import asyncio
import logging
import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.exceptions.database import DatabaseError
from doc_processor.models.documents import Document
from doc_processor.repositories.document_repository import DocumentRepository
from doc_processor.repositories.processing_job_repository import ProcessingJobRepository
from doc_processor.storage.local import save_pdf

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self, 
        document_repository: DocumentRepository,
        processing_job_repository: ProcessingJobRepository,
        session: AsyncSession,
    ) -> None:
        self.document_repository = document_repository
        self.processing_job_repository = processing_job_repository
        self.session = session
        
    
    async def get_owned_document(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Document | None:
        return await self.document_repository.get_by_id_for_user(document_id, user_id)


    async def list_owned_document(
        self,
        user_id: uuid.UUID,
    ) -> list[Document]:
        return await self.document_repository.list_by_user(user_id)

    
    async def upload_document(
        self,
        user_id: uuid.UUID,
        filename: str,
        content: bytes,
    ) -> Document:
        document_id = uuid.uuid4()
        
        # Try to save the PDF before attempting database INSERT
        try:
            filepath = await asyncio.to_thread(
                save_pdf,
                document_id,
                content,
            )
        
        except OSError:
            logger.exception(
                "Failed to save PDF for document %s",
                document_id
            )
            raise
        
        try:
            document = await self.document_repository.create(
                document_id=document_id,
                user_id=user_id,
                filename=filename
            )
            
            await self.processing_job_repository.create(
                document_id=document_id,
            )

            await self.session.commit()
            return document
        
        except Exception as exc:
            # Undo uncommitted database changes
            try:
                await self.session.rollback()
            except Exception:
                logger.exception(
                    "Database rollback failed for document %s",
                    document_id
                )
                
            # Remove the PDF if database persistence fails.
            try:
                await asyncio.to_thread(
                    filepath.unlink,
                    missing_ok=True
                )
            except OSError:
                logger.exception(
                    "Failed to clean up PDF for document %s",
                    document_id
                )
                
            if isinstance(exc, SQLAlchemyError):
                logger.exception(
                    "Database error while uploading document %s",
                    document_id
                )
                raise DatabaseError() from exc
            
            raise