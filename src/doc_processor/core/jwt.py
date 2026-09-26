from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError

from doc_processor.core.config import settings
from doc_processor.exceptions.auth import UnauthorizedError


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(UTC)

    expires_at = now + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    

def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={
                "require": ["sub", "iat", "exp"],
            },
        )

        user_id = UUID(payload["sub"])

        return user_id

    except (InvalidTokenError, ValueError, TypeError, AttributeError):
        raise UnauthorizedError() from None