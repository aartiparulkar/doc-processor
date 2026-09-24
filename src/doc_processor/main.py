from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from doc_processor.api.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from doc_processor.api.v1.router import api_router
from doc_processor.core.logging import configure_logging
from doc_processor.exceptions.base import AppException
from doc_processor.middleware.request_id import RequestIDMiddleware


def create_application() -> FastAPI:
    app = FastAPI(
        title="Document Processor API",
    )

    app.add_middleware(RequestIDMiddleware)

    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    app.add_exception_handler(
        HTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )

    app.include_router(api_router)
    return app


configure_logging()
app = create_application()