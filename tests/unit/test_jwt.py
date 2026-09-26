from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from doc_processor.core.config import settings
from doc_processor.core.jwt import (
    create_access_token,
    decode_access_token,
)
from doc_processor.exceptions.auth import UnauthorizedError


def test_valid_token():
    user_id = uuid4()
    token = create_access_token(user_id)
    assert decode_access_token(token) == user_id


def test_invalid_signature():
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        "deliberately-wrong-test-secrettttttttttttttttttttt",
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(UnauthorizedError):
        decode_access_token(token)


def test_expired_token():
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "exp": datetime.now(UTC) - timedelta(hours=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(UnauthorizedError):
        decode_access_token(token)


def test_missing_subject():
    token = jwt.encode(
        {
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(UnauthorizedError):
        decode_access_token(token)


def test_invalid_subject():
    token = jwt.encode(
        {
            "sub": "not-a-uuid",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(UnauthorizedError):
        decode_access_token(token)