from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def grade(self, *, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Must return a dict with:
        - grading_version: str
        - total_score: number
        - max_score: number
        - per_question: [{question_id, awarded_points, is_correct, feedback}]
        - feedback: dict
        """
        raise NotImplementedError
