import logging

from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.exceptions import (
    DatabaseError,
    DatabaseUnavailableError,
    UserAlreadyExistsError,
)
from doc_processor.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        try:
            statement = select(User).where(User.email == email)

            result = await self.session.execute(statement)

            return result.scalar_one_or_none()

        except OperationalError as exc:
            await self.session.rollback()

            logger.exception(
                "Database unavailable while fetching user."
            )

            raise DatabaseUnavailableError() from exc

        except SQLAlchemyError as exc:
            await self.session.rollback()

            logger.exception(
                "Database error while fetching user."
            )

            raise DatabaseError(
                message="Database error while fetching user.",
            ) from exc

    async def get_by_id(self, user_id: int) -> User | None:
        try:
            statement = select(User).where(User.id == user_id)

            result = await self.session.execute(statement)

            return result.scalar_one_or_none()

        except OperationalError as exc:
            await self.session.rollback()

            logger.exception(
                "Database unavailable while fetching user."
            )

            raise DatabaseUnavailableError() from exc

        except SQLAlchemyError as exc:
            await self.session.rollback()

            logger.exception(
                "Database error while fetching user."
            )

            raise DatabaseError(
                message="Database error while fetching user.",
            ) from exc

    async def create(
        self,
        email: str,
        password_hash: str,
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
        )

        self.session.add(user)

        try:
            await self.session.flush()
            await self.session.refresh(user)

            return user

        except IntegrityError as exc:
            await self.session.rollback()

            if self._is_unique_violation(exc):
                logger.warning(
                    "User creation failed because a unique constraint "
                    "was violated."
                )

                raise UserAlreadyExistsError() from exc

            logger.exception(
                "Database integrity error while creating user."
            )

            raise DatabaseError(
                message="Database integrity error while creating user.",
            ) from exc

        except OperationalError as exc:
            await self.session.rollback()

            logger.exception(
                "Database unavailable while creating user."
            )

            raise DatabaseUnavailableError() from exc

        except SQLAlchemyError as exc:
            await self.session.rollback()

            logger.exception(
                "Database error while creating user."
            )

            raise DatabaseError(
                message="Database error while creating user.",
            ) from exc

    @staticmethod
    def _is_unique_violation(
        exc: IntegrityError,
    ) -> bool:
        original_exception = exc.orig

        return getattr(
            original_exception,
            "sqlstate",
            None,
        ) == "23505"