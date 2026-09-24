import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.exceptions.database import (
    DatabaseError,
    DatabaseIntegrityError,
    DatabaseUnavailableError,
)
from doc_processor.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    
    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()
    
    
    async def get_by_id(self, id: uuid) -> User | None:
        statement = select(User).where(User.id == id)
        
        result = await self.session.execute(statement)
        
        return result.scalar_one_or_none()
    
    
    async def create(self, email: str, password_hash: str) -> User:
        user = User(
            email=email,
            password_hash=password_hash
        )
        
        try:
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
            return user
            
        except IntegrityError as exc:
            await self.session.rollback()
            raise DatabaseIntegrityError() from exc
        
        except OperationalError as exc:
            await self.session.rollback()
            raise DatabaseUnavailableError() from exc
        
        except SQLAlchemyError as exc:
            self.session.rollback()
            
            raise DatabaseError() from exc
        