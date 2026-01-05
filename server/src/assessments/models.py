# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone

from .constants import QuestionType, SubmissionStatus


class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return f"{self.code}: {self.name}"


class Exam(models.Model):
    title = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField()
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="exams")
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_open(self) -> bool:
        if not self.is_active:
            return False
        now = timezone.now()
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    type = models.CharField(max_length=32, choices=QuestionType.choices)
    prompt = models.TextField()
    expected_answer = models.TextField(blank=True, default="")
    points = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    order = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["exam", "order"]),
        ]

    def __str__(self) -> str:
        return f"Q{self.id} ({self.type})"


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["question"]),
        ]

    def __str__(self) -> str:
        return self.text[:60]


class Submission(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="submissions")

    status = models.CharField(
        max_length=16,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.SUBMITTED,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    feedback = models.JSONField(default=dict, blank=True)
    grading_version = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "exam"], name="uniq_student_exam_submission"
            ),
        ]
        indexes = [
            models.Index(fields=["student", "submitted_at"]),
            models.Index(fields=["exam", "student"]),
        ]

    def __str__(self) -> str:
        return f"Submission {self.id} by {self.student_id} for exam {self.exam_id}"


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        Question, on_delete=models.PROTECT, related_name="submission_answers"
    )

    answer_text = models.TextField(blank=True, default="")
    selected_choice = models.ForeignKey(
        Choice, on_delete=models.PROTECT, null=True, blank=True
    )

    is_correct = models.BooleanField(null=True, blank=True)
    awarded_points = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    feedback = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "question"], name="uniq_submission_question"
            ),
        ]
        indexes = [
            models.Index(fields=["submission", "question"]),
        ]
