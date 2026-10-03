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
    
    
    async def update_status(
        self,
        job: ProcessingJob,
        status: ProcessingJobStatus,
    ) -> ProcessingJob:
        job.status = status

        await self.session.flush()
        await self.session.refresh(job)

        return job
    
    async def claim_next_queued(self) -> ProcessingJob | None:
        statement = (
            select(ProcessingJob)
            .where(ProcessingJob.status == ProcessingJobStatus.QUEUED)
            .order_by(ProcessingJob.created_at, ProcessingJob.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )

        result = await self.session.execute(statement)
        job = result.scalar_one_or_none()

        if job is not None:
            job.status = ProcessingJobStatus.PROCESSING
            await self.session.flush()

        return job