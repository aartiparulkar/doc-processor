from doc_processor.exceptions.base import AppException


class UserAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="USER_ALREADY_EXISTS",
            message="A user with this email already exists.",
            status_code=409,
        )
