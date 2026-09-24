from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(
        description="Stable machine-readable application error code."
    )
    message: str = Field(
        description="Human-readable error message."
    )
    request_id: str | None = Field(
        default=None,
        description="Request correlation ID.",
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional structured error information.",
    )


class ErrorEnvelope(BaseModel):
    error: ErrorResponse