from doc_processor.core.security import hash_password
from doc_processor.exceptions.user import UserAlreadyExistsError
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

        user = await self.user_repository.create(
                email=normalized_email,
                password_hash=password_hash,
        )
            
        return user
    