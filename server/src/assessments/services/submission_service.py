"""Business logic for exam submissions.

This service handles the complete submission flow: validation, persistence,
and grading orchestration. All operations run within a database transaction
to ensure consistency.
"""
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import ValidationError

from assessments.constants import QuestionType, SubmissionStatus
from assessments.models import Choice, Exam, Question, Submission, SubmissionAnswer
from grading.service import grade_submission_with_provider


@dataclass(frozen=True)
class CreateSubmissionResult:
    submission: Submission


def _validate_exam_open(exam: Exam) -> None:
    if not exam.is_open():
        raise ValidationError({"exam": "Exam is not open for submissions."})


def _validate_questions_belong_to_exam(
    exam: Exam, question_ids: list[int]
) -> dict[int, Question]:
    qs = Question.objects.filter(exam=exam, id__in=question_ids).prefetch_related(
        "choices"
    )
    found = {q.id: q for q in qs}
    missing = [qid for qid in question_ids if qid not in found]
    if missing:
        raise ValidationError(
            {"answers": f"Invalid question_id(s) for this exam: {missing}"}
        )
    return found


def _validate_choice(question: Question, selected_choice_id: int) -> Choice:
    try:
        return question.choices.get(id=selected_choice_id)
    except Choice.DoesNotExist as exc:
        raise ValidationError(
            {"selected_choice_id": "Choice does not belong to the question."}
        ) from exc


@transaction.atomic
def create_and_grade_submission(
    *, user_id: int, exam_id: int, answers_payload: list[dict]
) -> CreateSubmissionResult:
    exam = Exam.objects.select_related("course").get(id=exam_id)
    _validate_exam_open(exam)

    if Submission.objects.filter(student_id=user_id, exam_id=exam_id).exists():
        raise ValidationError({"submission": "You have already submitted this exam."})

    question_ids = [a["question_id"] for a in answers_payload]
    questions_by_id = _validate_questions_belong_to_exam(exam, question_ids)

    submission = Submission.objects.create(
        student_id=user_id,
        exam=exam,
        status=SubmissionStatus.SUBMITTED,
        submitted_at=timezone.now(),
    )

    answer_rows: list[SubmissionAnswer] = []
    for item in answers_payload:
        q = questions_by_id[item["question_id"]]
        selected_choice = None
        answer_text = ""

        if q.type == QuestionType.MCQ:
            choice_id = item.get("selected_choice_id")
            if choice_id:
                selected_choice = _validate_choice(q, choice_id)
        else:
            answer_text = (item.get("answer_text") or "").strip()

        answer_rows.append(
            SubmissionAnswer(
                submission=submission,
                question=q,
                answer_text=answer_text,
                selected_choice=selected_choice,
            )
        )

    SubmissionAnswer.objects.bulk_create(answer_rows)

    # Grade it using the configured provider
    grade_result = grade_submission_with_provider(submission_id=submission.id)

    # Persist grade
    submission.score = grade_result.total_score
    submission.max_score = grade_result.max_score
    submission.feedback = grade_result.feedback
    submission.grading_version = grade_result.grading_version
    submission.status = SubmissionStatus.GRADED
    submission.graded_at = timezone.now()
    submission.save(
        update_fields=[
            "score",
            "max_score",
            "feedback",
            "grading_version",
            "status",
            "graded_at",
        ]
    )

    # Persist per-question results using bulk update for efficiency
    answer_objects = list(
        SubmissionAnswer.objects.filter(submission_id=submission.id).select_for_update()
    )
    answer_by_qid = {a.question_id: a for a in answer_objects}

    answers_to_update = []
    for r in grade_result.per_question:
        if answer := answer_by_qid.get(r.question_id):
            answer.is_correct = r.is_correct
            answer.awarded_points = r.awarded_points
            answer.feedback = r.feedback
            answers_to_update.append(answer)

    if answers_to_update:
        SubmissionAnswer.objects.bulk_update(
            answers_to_update, ["is_correct", "awarded_points", "feedback"]
        )

    return CreateSubmissionResult(submission=submission)
