import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.models.documents import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        

    async def get_by_id_for_user(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Document | None:
        statement = select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()
    
    
    async def list_by_user(self, user_id: uuid.UUID) -> list[Document]:
        statement = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(
                Document.created_at.desc(),
                Document.id.desc(),
            )
        )
        
        # execute() returns a collection of row tuples: [(Row1), (Row2),...]
        result = await self.session.execute(statement)
        
        # .scalars() extracts the first element of each row.
        # .all() tells SQLAlchemy to immediately fetch all remaining matching rows from db driver to memory
        return list(result.scalars().all())
    
    
    async def create(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        filename: str
    ) -> Document:
        document = Document(
            id=document_id,
            user_id=user_id,
            filename=filename
        )
        
        
        # Track document with the current session
        self.session.add(document)
        
        await self.session.flush()                          # Sends pendind INSERT to PostgreSQL
        await self.session.refresh(document)                # Retrives the document's DB values
        
        return document

    async def delete_by_id_for_user(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Document | None:
        document = await self.get_by_id_for_user(document_id, user_id)

        if document is None:
            return None

        await self.session.delete(document)
        await self.session.flush()

        return document
    
    async def save_processing_result(
        self,
        document_id: uuid.UUID,
        extracted_text: str,
        page_count: int,
    ) -> Document:
        statement = select(Document).where(Document.id == document_id)
        result = await self.session.execute(statement)
        document = result.scalar_one_or_none()

        if document is None:
            raise LookupError(f"Document {document_id} does not exist")

        document.extracted_text = extracted_text
        document.page_count = page_count
        document.processed_at = datetime.now(UTC)

        await self.session.flush()
        return document