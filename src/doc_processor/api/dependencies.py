from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.core.jwt import decode_access_token
from doc_processor.db.session import get_db_session
from doc_processor.exceptions.auth import UnauthorizedError
from doc_processor.models.user import User
from doc_processor.repositories.document_repository import DocumentRepository
from doc_processor.repositories.processing_job_repository import (
    ProcessingJobRepository,
)
from doc_processor.repositories.user_repository import UserRepository
from doc_processor.services.auth_service import AuthService
from doc_processor.services.document_service import DocumentService

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
    session: DbSession,
    user_repository: UserRepositoryDep,
) -> AuthService:
    return AuthService(user_repository, session)


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]


bearer_scheme = HTTPBearer(auto_error=False)

BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


async def get_current_user(
    credentials: BearerCredentials,
    user_repository: UserRepositoryDep,
) -> User:

    if credentials is None:
        raise UnauthorizedError()

    user_id = decode_access_token(credentials.credentials)

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError()

    if not user.is_active:
        raise UnauthorizedError()

    return user


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]


def get_document_repository(session: DbSession) -> DocumentRepository:
    return DocumentRepository(session)


DocumentRepositoryDep = Annotated[
    DocumentRepository,
    Depends(get_document_repository),
]


def get_document_service(
    document_repository: DocumentRepositoryDep,
    processing_job_repository: ProcessingJobRepository,
    session: DbSession
) -> DocumentService:
    return DocumentService(
        document_repository=document_repository,
        processing_job_repository=processing_job_repository,
        session=session,
    )


DocumentServiceDep = Annotated[
    DocumentService,
    Depends(get_document_service)
]

def get_processing_job_repository(
    session: DbSession,
) -> ProcessingJobRepository:
    return ProcessingJobRepository(session)


ProcessingJobRepositoryDep = Annotated[
    ProcessingJobRepository,
    Depends(get_processing_job_repository),
]

