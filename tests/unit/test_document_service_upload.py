
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from doc_processor.exceptions.database import DatabaseError
from doc_processor.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_successful_upload(tmp_path):
    document_repository = AsyncMock()
    processing_job_repository = AsyncMock()
    session = AsyncMock()

    saved_path = tmp_path / "document.pdf"
    saved_path.write_bytes(b"%PDF-1.4 test")

    expected_document = document_repository.create.return_value

    service = DocumentService(
        document_repository=document_repository, 
        processing_job_repository=processing_job_repository,
        session=session
    )

    with patch(
        "doc_processor.services.document_service.save_pdf",
        return_value=saved_path,
    ) as mock_save:
        result = await service.upload_document(
            user_id=uuid.uuid4(),
            filename="report.pdf",
            content=b"%PDF-1.4 test",
        )

    # Storage and repository receive the same document ID.
    storage_id = mock_save.call_args.args[0]
    repository_id = document_repository.create.call_args.kwargs[
        "document_id"
    ]
    

    assert storage_id == repository_id
    assert result is expected_document

    document_repository.create.assert_awaited_once()
    processing_job_repository.create.assert_awaited_once_with(
        document_id=document_repository.create.call_args.kwargs["document_id"]
    )
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_database_failure_removes_pdf(tmp_path):
    document_repository = AsyncMock()
    processing_job_repository = AsyncMock()
    session = AsyncMock()

    document_repository.create.side_effect = RuntimeError(
        "Database insertion failed"
    )

    saved_path = tmp_path / "document.pdf"
    saved_path.write_bytes(b"%PDF-1.4 test")

    service = DocumentService(document_repository, processing_job_repository, session)

    with patch(
        "doc_processor.services.document_service.save_pdf",
        return_value=saved_path,
    ), pytest.raises(
        RuntimeError,
        match="Database insertion failed",
    ):
        await service.upload_document(
            user_id=uuid.uuid4(),
            filename="report.pdf",
            content=b"%PDF-1.4 test",
        )

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()

    # The previously saved PDF must be deleted.
    assert not saved_path.exists()


@pytest.mark.asyncio
async def test_storage_failure_skips_database():
    document_repository = AsyncMock()
    processing_job_repository = AsyncMock()
    session = AsyncMock()

    service = DocumentService(document_repository, processing_job_repository, session)

    with patch(
        "doc_processor.services.document_service.save_pdf",
        side_effect=PermissionError("Access denied"),
    ), pytest.raises(PermissionError):
        await service.upload_document(
            user_id=uuid.uuid4(),
            filename="report.pdf",
            content=b"%PDF-1.4 test",
        )

    document_repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()



@pytest.mark.asyncio
async def test_database_error_cleans_up_pdf(tmp_path):
    document_repository = AsyncMock()
    processing_job_repository = AsyncMock()
    session = AsyncMock()

    document_repository.create.side_effect = SQLAlchemyError(
        "Database insert failed"
    )

    saved_path = tmp_path / "document.pdf"
    saved_path.write_bytes(b"%PDF-1.4 test")

    service = DocumentService(document_repository, processing_job_repository, session)

    with patch(
        "doc_processor.services.document_service.save_pdf",
        return_value=saved_path,
    ), pytest.raises(DatabaseError):
        await service.upload_document(
            user_id=uuid.uuid4(),
            filename="report.pdf",
            content=b"%PDF-1.4 test",
        )

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
    assert not saved_path.exists()
    

@pytest.mark.asyncio
async def test_rollback_failure_still_removes_pdf(tmp_path):
    document_repository = AsyncMock()
    processing_job_repository = AsyncMock()
    session = AsyncMock()

    document_repository.create.side_effect = SQLAlchemyError(
        "Database insert failed"
    )
    session.rollback.side_effect = RuntimeError(
        "Rollback failed"
    )

    saved_path = tmp_path / "document.pdf"
    saved_path.write_bytes(b"%PDF-1.4 test")

    service = DocumentService(document_repository, processing_job_repository, session)

    with patch(
        "doc_processor.services.document_service.save_pdf",
        return_value=saved_path,
    ), pytest.raises(DatabaseError):
        await service.upload_document(
            user_id=uuid.uuid4(),
            filename="report.pdf",
            content=b"%PDF-1.4 test",
        )

    session.rollback.assert_awaited_once()
    assert not saved_path.exists()

    
@pytest.mark.asyncio
async def test_processing_job_failure_rolls_back_document(tmp_path):
    document_repository = AsyncMock()
    processing_job_repository = AsyncMock()
    session = AsyncMock()

    processing_job_repository.create.side_effect = RuntimeError(
        "Job creation failed"
    )

    saved_path = tmp_path / "document.pdf"
    saved_path.write_bytes(b"%PDF-1.4 test")

    service = DocumentService(
        document_repository=document_repository,
        processing_job_repository=processing_job_repository,
        session=session,
    )

    with patch(
        "doc_processor.services.document_service.save_pdf",
        return_value=saved_path,
    ), pytest.raises(
        RuntimeError,
        match="Job creation failed",
    ):
        await service.upload_document(
            user_id=uuid.uuid4(),
            filename="report.pdf",
            content=b"%PDF-1.4 test",
        )

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()

    assert not saved_path.exists()    

