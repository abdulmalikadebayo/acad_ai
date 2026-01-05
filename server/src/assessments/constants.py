from django.db.models import TextChoices


class QuestionType(TextChoices):
    MCQ = "MCQ", "Multiple Choice"
    SHORT_TEXT = "SHORT_TEXT", "Short Text"


class SubmissionStatus(TextChoices):
    SUBMITTED = "SUBMITTED", "Submitted"
    GRADED = "GRADED", "Graded"
