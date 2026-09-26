from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from doc_processor.core.security import hash_password
from doc_processor.exceptions.auth import InvalidCredentialsError
from doc_processor.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_login_success():
    user_id = uuid4()

    user = SimpleNamespace(
        id=user_id,
        password_hash=hash_password("correctpassword"),
        is_active=True,
    )

    repository = AsyncMock()
    repository.get_by_email.return_value = user

    service = AuthService(
        user_repository=repository,
        session=AsyncMock(),
    )

    with patch(
        "doc_processor.services.auth_service.create_access_token",
        return_value="test-token",
    ) as create_token:
        token = await service.login(
            "  USER@example.com  ",
            "correctpassword",
        )

    assert token == "test-token"

    repository.get_by_email.assert_awaited_once_with(
        "user@example.com"
    )

    create_token.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_login_unknown_user():
    repository = AsyncMock()
    repository.get_by_email.return_value = None

    service = AuthService(
        user_repository=repository,
        session=AsyncMock(),
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login(
            "unknown@example.com",
            "anypassword",
        )
