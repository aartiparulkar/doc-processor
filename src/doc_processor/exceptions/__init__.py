from doc_processor.exceptions.auth import (
    InvalidCredentialsError,
    UnauthorizedError,
)
from doc_processor.exceptions.base import AppException
from doc_processor.exceptions.database import (
    DatabaseError,
    DatabaseIntegrityError,
    DatabaseUnavailableError,
)
from doc_processor.exceptions.external import (
    ExternalServiceError,
    ExternalServiceRateLimitedError,
    ExternalServiceTimeoutError,
    ExternalServiceUnavailableError,
)
from doc_processor.exceptions.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
)

__all__ = [
    "AppException",
    "DatabaseError",
    "DatabaseIntegrityError",
    "DatabaseUnavailableError",
    "ExternalServiceError",
    "ExternalServiceRateLimitedError",
    "ExternalServiceTimeoutError",
    "ExternalServiceUnavailableError",
    "InvalidCredentialsError",
    "UnauthorizedError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
]
