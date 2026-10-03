import asyncio
import logging
import uuid

from doc_processor.db.session import AsyncSessionLocal, engine
from doc_processor.repositories.processing_job_repository import (
    ProcessingJobRepository,
)
from doc_processor.services.document_processing_service import process_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_one_job() -> bool:
    async with AsyncSessionLocal() as session:
        repository = ProcessingJobRepository(session)
        job = await repository.claim_next_queued()

        if job is None:
            return False

        document_id: uuid.UUID = job.document_id
        await session.commit()

    await process_document(document_id)
    return True


async def run_worker() -> None:
    try:
        while True:
            try:
                found_job = await process_one_job()
            except Exception:
                logger.exception("Worker failed while polling for a job")
                found_job = False

            if not found_job:
                await asyncio.sleep(2)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_worker())