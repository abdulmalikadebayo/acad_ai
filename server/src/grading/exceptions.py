class LLMGradingError(Exception):
    """
    Raised when LLM grading operations fail.

    This includes:
    - API connection failures
    - Invalid API responses
    - Parsing errors
    - Configuration errors
    """
