"""Grading orchestration service.

This module coordinates the grading flow: building payloads, invoking
the configured provider, normalizing results, and merging MCQ grades.
MCQ questions are always graded deterministically regardless of provider.
"""
from decimal import Decimal
from typing import Any

from assessments.models import Question, QuestionType, Submission, SubmissionAnswer
from grading.dto import GradeResult, PerQuestionGrade
from grading.exceptions import LLMGradingError
from grading.providers.openai_provider import OpenAIProvider


def _build_payload(submission: Submission) -> dict[str, Any]:
    # Re-fetch with prefetching only if caller didn't optimize the query
    if not hasattr(submission, "_prefetched_objects_cache"):
        submission = (
            Submission.objects.select_related("exam", "exam__course")
            .prefetch_related(
                "answers__question",
                "answers__selected_choice",
                "exam__questions__choices",
            )
            .get(id=submission.id)
        )

    questions = []
    max_score = Decimal("0")

    # Pre-compute correct choices to grade MCQs without LLM involvement
    correct_choice_by_qid: dict[int, int] = {}
    for q in submission.exam.questions.all():
        max_score += q.points
        if q.type == QuestionType.MCQ:
            correct = q.choices.filter(is_correct=True).first()
            if correct:
                correct_choice_by_qid[q.id] = correct.id

    answers_by_qid = {a.question_id: a for a in submission.answers.all()}

    for q in submission.exam.questions.all().order_by("order"):
        a = answers_by_qid.get(q.id)
        questions.append(
            {
                "question_id": q.id,
                "type": q.type,
                "prompt": q.prompt,
                "expected_answer": q.expected_answer,
                "max_points": float(q.points),
                "student_answer_text": (a.answer_text if a else ""),
                "selected_choice_id": (a.selected_choice_id if a else None),
                "correct_choice_id": correct_choice_by_qid.get(q.id),
                "choices": [{"id": c.id, "text": c.text} for c in q.choices.all()],
            }
        )

    return {
        "exam": {
            "id": submission.exam_id,
            "title": submission.exam.title,
            "course": {
                "code": submission.exam.course.code,
                "name": submission.exam.course.name,
            },
        },
        "submission": {"id": submission.id, "student_id": submission.student_id},
        "questions": questions,
        "max_score": float(max_score),
        "policy": {
            "grade_only_text": True,
        },
    }


def grade_submission_with_provider(*, submission_id: int) -> GradeResult:
    submission = Submission.objects.get(id=submission_id)
    payload = _build_payload(submission)

    # Send only text questions to LLM, grade MCQ deterministically
    payload = _payload_text_only(payload)

    provider = OpenAIProvider()
    resp = provider.grade(payload=payload)

    return _normalize_grade_result(resp, submission_id=submission_id)


def _payload_text_only(payload: dict[str, Any]) -> dict[str, Any]:
    filtered = []
    for q in payload["questions"]:
        if q["type"] == QuestionType.SHORT_TEXT:
            filtered.append(q)
    payload["questions"] = filtered
    return payload


def _normalize_grade_result(resp: dict[str, Any], *, submission_id: int) -> GradeResult:
    """
    Validate shape and coerce to Decimals.
    """
    grading_version = str(resp.get("grading_version", "llm-v1"))
    feedback = (
        resp.get("feedback", {})
        if isinstance(resp.get("feedback", {}), dict)
        else {"summary": ""}
    )

    per_question_raw = resp.get("per_question", [])
    if not isinstance(per_question_raw, list):
        raise LLMGradingError("per_question must be a list")

    # Compute max_score from DB for correctness, not trusting LLM.
    answers = SubmissionAnswer.objects.select_related("question").filter(
        submission_id=submission_id
    )
    max_score = sum((a.question.points for a in answers), Decimal("0"))

    per_question: list[PerQuestionGrade] = []
    total_score = Decimal("0")

    for item in per_question_raw:
        qid = int(item["question_id"])
        awarded = Decimal(str(item.get("awarded_points", 0)))
        is_correct = item.get("is_correct", None)
        fb = str(item.get("feedback", "")).strip()

        # Clamp awarded_points to [0, question.points]
        q_points = answers.get(question_id=qid).question.points
        if awarded < 0:
            awarded = Decimal("0")
        if awarded > q_points:
            awarded = q_points

        total_score += awarded
        per_question.append(
            PerQuestionGrade(
                question_id=qid,
                awarded_points=awarded,
                is_correct=(
                    is_correct
                    if isinstance(is_correct, bool) or is_correct is None
                    else None
                ),
                feedback=fb,
            )
        )

    # Always merge with deterministic MCQ grading
    total_score, per_question = _merge_with_deterministic_mcq(
        submission_id, total_score, per_question
    )

    # Enhance feedback to include MCQ performance
    feedback = _enhance_feedback_with_mcq(
        feedback, per_question, total_score, max_score
    )

    return GradeResult(
        total_score=total_score,
        max_score=max_score,
        grading_version=grading_version,
        feedback=feedback,
        per_question=per_question,
    )


def _merge_with_deterministic_mcq(
    submission_id: int, total_score: Decimal, per_question: list[PerQuestionGrade]
):
    existing_qids = {p.question_id for p in per_question}
    answers = SubmissionAnswer.objects.select_related(
        "question", "selected_choice"
    ).filter(submission_id=submission_id)

    for a in answers:
        if a.question.type != QuestionType.MCQ:
            continue
        if a.question_id in existing_qids:
            continue

        correct = a.question.choices.filter(is_correct=True).first()
        is_correct = bool(correct and a.selected_choice_id == correct.id)
        awarded = a.question.points if is_correct else Decimal("0")
        total_score += awarded

        per_question.append(
            PerQuestionGrade(
                question_id=a.question_id,
                awarded_points=awarded,
                is_correct=is_correct,
                feedback="Correct." if is_correct else "Incorrect.",
            )
        )

    # Keep stable ordering
    per_question.sort(key=lambda x: x.question_id)
    return total_score, per_question


def _enhance_feedback_with_mcq(
    feedback: dict,
    per_question: list[PerQuestionGrade],
    total_score: Decimal,
    max_score: Decimal,
) -> dict:
    """
    Generate a smart, concise summary combining MCQ and text question performance with topic context.
    """
    # Fetch actual question types from database
    question_ids = [q.question_id for q in per_question]
    questions_data = Question.objects.filter(id__in=question_ids).values(
        "id", "type", "prompt", "metadata"
    )
    questions_by_id = {q["id"]: q for q in questions_data}

    # Separate by actual question type
    mcq_results = []
    text_results = []

    for q in per_question:
        q_data = questions_by_id.get(q.question_id)
        if q_data and q_data["type"] == QuestionType.MCQ:
            mcq_results.append((q, q_data))
        else:
            text_results.append((q, q_data))

    # Calculate overall stats
    percentage = (float(total_score) / float(max_score) * 100) if max_score > 0 else 0

    # Build smart summary
    summary_parts = []

    # Overall score
    summary_parts.append(
        f"Overall Performance: {total_score}/{max_score} ({percentage:.1f}%)."
    )

    # MCQ summary with topics
    if mcq_results:
        mcq_correct = sum(1 for q, _ in mcq_results if q.is_correct)
        mcq_total = len(mcq_results)
        mcq_score = sum(q.awarded_points for q, _ in mcq_results)

        # Extract topics from MCQ metadata
        topics = []
        for q, q_data in mcq_results:
            if q_data and q_data.get("metadata"):
                topic = q_data["metadata"].get("topic") or q_data["metadata"].get(
                    "subtopic"
                )
                if topic and topic not in topics:
                    topics.append(topic)

        topic_context = f" covering {', '.join(topics[:3])}" if topics else ""

        if mcq_correct == mcq_total:
            summary_parts.append(
                f"Strong performance on multiple choice{topic_context} (all {mcq_total} correct, {mcq_score} points)."
            )
        elif mcq_correct > mcq_total / 2:
            summary_parts.append(
                f"Good understanding of multiple choice concepts{topic_context} ({mcq_correct}/{mcq_total} correct, {mcq_score} points)."
            )
        else:
            summary_parts.append(
                f"Multiple choice questions need improvement{topic_context} ({mcq_correct}/{mcq_total} correct, {mcq_score} points)."
            )

    # Text question summary
    original_summary = feedback.get("summary", "").strip()
    if text_results:
        text_score = sum(q.awarded_points for q, _ in text_results)
        text_answered = sum(1 for q, _ in text_results if q.awarded_points > 0)
        text_total = len(text_results)

        if original_summary:
            # Use LLM summary if available
            summary_parts.append(original_summary)
        else:
            # Fallback summary
            if text_answered == 0:
                summary_parts.append(
                    f"No answers provided for {text_total} essay question(s)."
                )
            elif text_answered < text_total:
                summary_parts.append(
                    f"Partial completion: {text_answered}/{text_total} essay question(s) answered ({text_score} points)."
                )
            else:
                summary_parts.append(
                    f"Completed all {text_total} essay question(s) ({text_score} points)."
                )

    feedback["summary"] = " ".join(summary_parts)
    return feedback
