from doc_processor.core.error_codes import ErrorCode
from doc_processor.exceptions.base import AppException


class UnauthorizedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.AUTH_UNAUTHORIZED,
            message="Authentication is required.",
        )


class InvalidCredentialsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            message="Invalid email or password.",
        )
