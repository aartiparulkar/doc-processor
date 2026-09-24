from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from doc_processor.core.config import settings


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