from typing import Any

from doc_processor.core.error_codes import ErrorCode


class AppException(Exception):
    """
    Base exception for expected application errors.

    These exceptions are safe to translate into API responses.
    """
    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details

        super().__init__(code)
