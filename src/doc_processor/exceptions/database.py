from doc_processor.core.error_codes import ErrorCode
from doc_processor.exceptions.base import AppException


class DatabaseError(AppException):
    def __init__(
        self, 
        message: str = "A Database Error Occurred."
    ):
        super().__init__(
            code=ErrorCode.DB_ERROR,
            message=message,
        )
        

class DatabaseIntegrityError(AppException):
    def __init__(
        self, 
        message: str = "The Requested Operation Violates A Database Constraint."
    ):
        super().__init__(
            code=ErrorCode.DB_INTEGRITY_ERROR,
            message=message,
        )
        

class DatabaseUnavailableError(AppException):
    def __init__(self):
        super().__init__(
            code=ErrorCode.DB_ERROR,
            message="The Database Is Temorarily Unavailable",
        )