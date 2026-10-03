import asyncio
import logging
import uuid

from doc_processor.db.session import AsyncSessionLocal
from doc_processor.models.job_processing import ProcessingJobStatus
from doc_processor.repositories.document_repository import DocumentRepository
from doc_processor.repositories.processing_job_repository import (
    ProcessingJobRepository,
)
from doc_processor.services.pdf_parser import extract_pdf
from doc_processor.storage.local import get_pdf_path

logger = logging.getLogger(__name__)


async def process_document(document_id: uuid.UUID) -> None:
    try:
        parsed = await asyncio.to_thread(
            extract_pdf,
            get_pdf_path(document_id),
        )

        async with AsyncSessionLocal() as session:
            job_repository = ProcessingJobRepository(session)
            processing_job = await job_repository.get_by_document_id(document_id)

            if (
                processing_job is None
                or processing_job.status != ProcessingJobStatus.PROCESSING
            ):
                return

            document_repository = DocumentRepository(session)
            await document_repository.save_processing_result(
                document_id=document_id,
                extracted_text=parsed.text,
                page_count=parsed.page_count,
            )
            await job_repository.update_status(
                processing_job,
                ProcessingJobStatus.COMPLETED,
            )
            await session.commit()

        logger.info("Processed document %s", document_id)

    except Exception:
        logger.exception("Failed to process document %s", document_id)

        async with AsyncSessionLocal() as session:
            job_repository = ProcessingJobRepository(session)
            job = await job_repository.get_by_document_id(document_id)

            if job is not None and job.status == ProcessingJobStatus.PROCESSING:
                await job_repository.update_status(
                    job,
                    ProcessingJobStatus.FAILED,
                )
                await session.commit()