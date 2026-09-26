from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.core.jwt import create_access_token
from doc_processor.core.security import hash_password, verify_password
from doc_processor.exceptions.auth import InvalidCredentialsError
from doc_processor.exceptions.user import UserAlreadyExistsError
from doc_processor.models.user import User
from doc_processor.repositories.user_repository import UserRepository


class AuthService:
    def __init__(
        self, 
        user_repository: UserRepository, 
        session: AsyncSession
    ):
        self.user_repository = user_repository
        self.session = session
        
        
    async def register(
        self,
        email: str,
        password: str,
    ) -> User:
        async with self.session.begin():
            normalized_email = email.strip().lower()

            existing_user = await self.user_repository.get_by_email(normalized_email)

            if existing_user is not None:
                raise UserAlreadyExistsError()

            password_hash = hash_password(password)

            user = await self.user_repository.create(
                email=normalized_email,
                password_hash=password_hash,
                    )        
                
        return user
    
    
    async def login(
        self,
        email: str,
        password: str,
    ) -> str:
        
        normalized_email = email.strip().lower()
        user = await self.user_repository.get_by_email(normalized_email)

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        access_token = create_access_token(user.id)

        return access_token
        