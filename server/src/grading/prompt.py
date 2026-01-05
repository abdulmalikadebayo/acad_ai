def build_grading_prompt(payload: dict) -> str:
    """
    Build a robust grading prompt to send to the LLM.
    The prompt explicitly references rubrics, grading criteria, expected answer, and required output schema.
    It instructs the model to avoid any text outside the JSON object and to only use the rubric for scoring.
    """
    return f"""
You are an automated academic grading engine.

Below is a student's submission for an exam. You will grade each question against its rubric and provide precise scores and feedback.

DO NOT output any text outside a single strict JSON object. No markdown. No commentary outside the JSON.

GENERAL RULES:
1) You must only assign points between 0 and max_points for each question.
2) For MCQ questions:
   - If the selected_choice_id equals the correct_choice_id, award full points.
   - Otherwise award 0.
3) For SHORT_TEXT questions:
   - Compare the student's answer text with the expected_answer and rubric.
   - Award partial credit based on how well key concepts, terminology, and logic from the rubric are present.
   - If the answer is missing, incomplete, irrelevant, or contradicts the expected answer, award 0.
4) Only use the provided expected_answer as the grading rubric. Do NOT hallucinate additional content.
5) Always use evidence from the student's answer to justify the feedback.
6) If required fields are missing (e.g., no answer for a question), mark awarded_points = 0 and provide clear feedback in JSON.

OUTPUT SCHEMA (JSON ONLY):
{{
  "grading_version": "llm-v1",
  "total_score": <number>,
  "max_score": <number>,
  "feedback": {{
    "summary": "<overall summary that reflects student performance>"
  }},
  "per_question": [
    {{
      "question_id": <int>,
      "awarded_points": <number>,
      "is_correct": <true|false|null>,
      "feedback": "<concise evidence-based feedback>"
    }}
  ]
}}

EXAM STRUCTURE AND SUBMISSION:
{payload}
""".strip()
