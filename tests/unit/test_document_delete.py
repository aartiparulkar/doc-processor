import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from doc_processor.api.dependencies import get_current_user, get_document_service
from doc_processor.core.config import settings
from doc_processor.exceptions.database import DatabaseError
from doc_processor.main import create_application
from doc_processor.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_delete_owned_document_removes_record_and_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", tmp_path)
    document_id, user_id = uuid.uuid4(), uuid.uuid4()
    pdf = tmp_path / f"{document_id}.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    document = SimpleNamespace(id=document_id)
    repository, jobs, session = AsyncMock(), AsyncMock(), AsyncMock()
    repository.get_by_id_for_user.return_value = document

    result = await DocumentService(repository, jobs, session).delete_owned_document(
        document_id, user_id
    )

    assert result is document
    repository.get_by_id_for_user.assert_awaited_once_with(document_id, user_id)
    repository.delete.assert_awaited_once_with(document)
    session.commit.assert_awaited_once()
    assert not pdf.exists()


@pytest.mark.asyncio
async def test_delete_missing_or_unowned_document_changes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", tmp_path)
    repository, jobs, session = AsyncMock(), AsyncMock(), AsyncMock()
    repository.get_by_id_for_user.return_value = None

    assert await DocumentService(repository, jobs, session).delete_owned_document(
        uuid.uuid4(), uuid.uuid4()
    ) is None
    repository.delete.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_database_failure_preserves_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", tmp_path)
    document_id = uuid.uuid4()
    pdf = tmp_path / f"{document_id}.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    repository, jobs, session = AsyncMock(), AsyncMock(), AsyncMock()
    repository.get_by_id_for_user.return_value = SimpleNamespace(id=document_id)
    session.commit.side_effect = SQLAlchemyError("commit failed")

    with pytest.raises(DatabaseError):
        await DocumentService(repository, jobs, session).delete_owned_document(
            document_id, uuid.uuid4()
        )

    session.rollback.assert_awaited_once()
    assert pdf.exists()


def test_delete_route_returns_deleted_document_and_404_for_missing():
    app = create_application()
    user_id, document_id = uuid.uuid4(), uuid.uuid4()
    service = SimpleNamespace(delete_document=AsyncMock())
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user_id)
    app.dependency_overrides[get_document_service] = lambda: service

    with TestClient(app) as client:
        service.delete_document.return_value = SimpleNamespace(
            id=document_id,
            filename="report.pdf",
            created_at=datetime.now(timezone.utc),
        )
        response = client.delete(f"/api/v1/documents/{document_id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(document_id)
        service.delete_document.assert_awaited_once_with(
            document_id=document_id, user_id=user_id
        )

        service.delete_document.return_value = None
        assert client.delete(f"/api/v1/documents/{document_id}").status_code == 404

    app.dependency_overrides.clear()
