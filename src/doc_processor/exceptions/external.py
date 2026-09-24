from doc_processor.core.error_codes import ErrorCode
from doc_processor.exceptions.base import AppException


class ExternalServiceError(AppException):
    def __init__(
        self,
        message: str = "An External Service Error Occurred.",
    ) -> None:
        super().__init__(
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            message=message,
        )


class ExternalServiceUnavailableError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            message="An External Service Is Temporarily Unavailable.",
        )


class ExternalServiceTimeoutError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.EXTERNAL_SERVICE_TIMEOUT,
            message="An External Service Request Timed Out.",
        )


class ExternalServiceRateLimitedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.EXTERNAL_SERVICE_RATE_LIMITED,
            message="The External Service Rate Limit Has Been Exceeded.",
        )
