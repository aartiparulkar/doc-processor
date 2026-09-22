from doc_processor.core.security import hash_password

from doc_processor.exceptions.user_already_exists_error import UserAlreadyExistsError
from doc_processor.exceptions.user_email_conflict_error import UserEmailConflictError

from doc_processor.models.user import User

from doc_processor.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
        
    async def register(
        self,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()

        existing_user = await self.user_repository.get_by_email(
            normalized_email
        )

        if existing_user is not None:
            raise UserAlreadyExistsError()

        password_hash = hash_password(password)

        try:
            user = await self.user_repository.create(
                email=normalized_email,
                password_hash=password_hash,
            )
        except UserEmailConflictError as exc:
            raise UserEmailConflictError() from exc

        return user
    