from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class PerQuestionGrade:
    question_id: int
    awarded_points: Decimal
    is_correct: bool | None
    feedback: str


@dataclass(frozen=True)
class GradeResult:
    total_score: Decimal
    max_score: Decimal
    grading_version: str
    feedback: dict[str, Any]
    per_question: list[PerQuestionGrade]
