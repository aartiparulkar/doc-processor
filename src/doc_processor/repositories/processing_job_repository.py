import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from doc_processor.models.job_processing import (
    ProcessingJob,
    ProcessingJobStatus,
)


class ProcessingJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        document_id: uuid.UUID,
    ) -> ProcessingJob:
        processing_job = ProcessingJob(
            document_id=document_id,
            status=ProcessingJobStatus.QUEUED,
        )

        self.session.add(processing_job)

        await self.session.flush()
        await self.session.refresh(processing_job)

        return processing_job

    async def get_by_document_id(
        self,
        document_id: uuid.UUID,
    ) -> ProcessingJob | None:
        statement = select(ProcessingJob).where(
            ProcessingJob.document_id == document_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()