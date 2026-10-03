import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from doc_processor.models.job_processing import (
    ProcessingJob,
    ProcessingJobStatus,
)
from doc_processor.repositories.processing_job_repository import (
    ProcessingJobRepository,
)


@pytest.mark.asyncio
async def test_create_processing_job():
    session = Mock()
    
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    repository = ProcessingJobRepository(session)

    document_id = uuid.uuid4()

    job = await repository.create(document_id)

    assert isinstance(job, ProcessingJob)
    assert job.document_id == document_id
    assert job.status == ProcessingJobStatus.QUEUED

    session.add.assert_called_once_with(job)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(job)