from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.db.session import get_db_session
from doc_processor.repositories.user_repository import UserRepository
from doc_processor.services.auth_service import AuthService

DbSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


def get_user_repository(
    session: DbSession,
) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[
    UserRepository,
    Depends(get_user_repository),
]


def get_auth_service(
    user_repository: UserRepositoryDep,
) -> AuthService:
    return AuthService(user_repository)


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]