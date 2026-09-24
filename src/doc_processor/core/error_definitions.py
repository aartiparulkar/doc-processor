from dataclasses import dataclass

from fastapi import status

from doc_processor.core.error_codes import ErrorCode


@dataclass(frozen=True)
class ErrorDefinition:
    status_code: int
    message: str


ERROR_DEFINITIONS: dict[ErrorCode, ErrorDefinition] = {
    ErrorCode.INTERNAL_ERROR: ErrorDefinition(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An Unexpected Error Occurred.",
    ),
    ErrorCode.VALIDATION_ERROR: ErrorDefinition(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        message="Request Validation Failed.",
    ),
    ErrorCode.BAD_REQUEST: ErrorDefinition(
        status_code=status.HTTP_400_BAD_REQUEST,
        message="The Request Is Invalid.",
    ),
    ErrorCode.AUTH_INVALID_CREDENTIALS: ErrorDefinition(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message="Invalid Email Or Password.",
    ),
    ErrorCode.AUTH_USER_ALREADY_EXISTS: ErrorDefinition(
        status_code=status.HTTP_409_CONFLICT,
        message="User Already Exists.",
    ),
    ErrorCode.AUTH_USER_NOT_FOUND: ErrorDefinition(
        status_code=status.HTTP_404_NOT_FOUND,
        message="User Not Found.",
    ),
    ErrorCode.AUTH_UNAUTHORIZED: ErrorDefinition(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message="Authentication Is Required.",
    ),
    ErrorCode.FORBIDDEN: ErrorDefinition(
        status_code=status.HTTP_403_FORBIDDEN,
        message="You Do Not Have Permission To Perform This Operation.",
    ),
    ErrorCode.DB_ERROR: ErrorDefinition(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="A Database Error Occurred.",
    ),
    ErrorCode.DB_INTEGRITY_ERROR: ErrorDefinition(
        status_code=status.HTTP_409_CONFLICT,
        message="The Requested Operation Violates A Database Constraint.",
    ),
    ErrorCode.DB_UNAVAILABLE: ErrorDefinition(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        message="The Database Is Temporarily Unavailable.",
    ),
    ErrorCode.EXTERNAL_SERVICE_ERROR: ErrorDefinition(
        status_code=status.HTTP_502_BAD_GATEWAY,
        message="An External Service Error Occurred.",
    ),
    ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE: ErrorDefinition(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        message="An External Service Is Temporarily Unavailable.",
    ),
    ErrorCode.EXTERNAL_SERVICE_TIMEOUT: ErrorDefinition(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        message="An External Service Request Timed Out.",
    ),
    ErrorCode.EXTERNAL_SERVICE_RATE_LIMITED: ErrorDefinition(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        message="The External Service Rate Limit Has Been Exceeded.",
    ),
}
