from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from doc_processor.api.dependencies import get_current_user
from doc_processor.exceptions.auth import UnauthorizedError
from doc_processor.models.user import User


@pytest.mark.asyncio
async def test_current_user_success():
    user_id = uuid4()

    user = User(
        id=user_id,
        email="test@example.com",
        password_hash="dummy-hash",
        is_active=True,
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = user

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="test-token",
    )

    with patch(
        "doc_processor.api.dependencies.decode_access_token",
        return_value=user_id,
    ):
        result = await get_current_user(
            credentials=credentials,
            user_repository=repository,
        )

    assert result is user
    repository.get_by_id.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_missing_credentials():
    repository = AsyncMock()

    with pytest.raises(UnauthorizedError):
        await get_current_user(
            credentials=None,
            user_repository=repository,
        )

    repository.get_by_id.assert_not_awaited()
