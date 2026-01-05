from django.db.models import Prefetch

from .models import Exam, Submission, SubmissionAnswer


def get_exam_with_questions(exam_id: int) -> Exam:
    return (
        Exam.objects.select_related("course")
        .prefetch_related("questions__choices")
        .get(id=exam_id)
    )


def get_submission_for_owner(submission_id: int, user_id: int) -> Submission:
    return (
        Submission.objects.select_related("exam", "exam__course")
        .prefetch_related(
            Prefetch(
                "answers",
                queryset=SubmissionAnswer.objects.select_related(
                    "question", "selected_choice"
                ).order_by("question__order"),
            ),
            "exam__questions__choices",
        )
        .get(id=submission_id, student_id=user_id)
    )
