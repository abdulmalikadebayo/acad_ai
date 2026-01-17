"""OpenAI GPT-4o grading provider.

This provider sends text questions to OpenAI's API for evaluation.
MCQ questions are handled separately by the grading service.
"""
import json
import time
from typing import Any

from django.conf import settings

import requests

from grading.exceptions import LLMGradingError
from grading.prompt import build_grading_prompt


class OpenAIProvider:
    """Grades text answers using OpenAI's GPT-4o model.
    
    Implements exponential backoff retry logic for transient failures.
    Uses JSON mode to ensure structured responses.
    """

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise LLMGradingError("OPENAI_API_KEY is missing.")
        self.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o"
        self.timeout = 60
        self.max_retries = 3

    def grade(self, *, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = build_grading_prompt(payload)

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an academic grading assistant. Return only valid JSON with no markdown formatting.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(
                    url, headers=headers, json=body, timeout=self.timeout
                )
                if resp.status_code >= 400:
                    raise LLMGradingError(
                        f"OpenAI error {resp.status_code}: {resp.text}"
                    )

                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return self._parse_json(text)

            except Exception as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(0.8 * (attempt + 1))

        raise LLMGradingError(f"LLM grading failed: {last_error}")

    def _parse_json(self, text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMGradingError(
                f"LLM returned non-JSON output: {text[:500]}"
            ) from exc
