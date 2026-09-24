import logging

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from doc_processor.core.error_codes import ErrorCode
from doc_processor.core.error_definitions import ERROR_DEFINITIONS
from doc_processor.exceptions.base import AppException

logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)
    
    
async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    
    definition = ERROR_DEFINITIONS.get(exc.code)
    
    if definition is None:
        logger.error(
            "Missing Error Definition",
            extra={
                "error_code": exc.code,
                "request_id": _get_request_id(request)
            }
        )
        
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "An unexpected error occurred."
    
    else:
        status_code = definition.status_code
        message = exc.message
    
    request_id = _get_request_id(request)
    
    logger.warning(
        "Application Error",
        extra={
            "error_code": exc.code,
            "status_code": status_code,
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
        
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": message,
                "request_id": request_id,
                "details": exc.details,
            }
        },
    )
    

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    request_id = _get_request_id(request)
    
    details = {
        "fields": [
            {
                "field": ".".join(
                    str(part) for part in error["loc"]
                ),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
    }
    
    logger.info(
        "Request Validation Failed",
        extra={
            "error_code": ErrorCode.VALIDATION_ERROR,
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Request validation failed.",
                "request_id": request_id,
                "details": details,
            }
        },
    )
    
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    request_id = _get_request_id(request)

    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "request_id": request_id,
                "details": None,
            }
        },
    )
    

async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = _get_request_id(request)

    logger.exception(
        "Unhandled application exception",
        extra={
            "error_code": ErrorCode.INTERNAL_ERROR,
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "An unexpected error occurred.",
                "request_id": request_id,
                "details": None,
            }
        },
    )
