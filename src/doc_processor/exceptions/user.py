from doc_processor.core.error_codes import ErrorCode
from doc_processor.exceptions.base import AppException


class UserAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.AUTH_USER_ALREADY_EXISTS,
            message="User Already Exists.",
        )
        

class UserNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.AUTH_USER_NOT_FOUND,
            message="User Not Found.",
        )
            