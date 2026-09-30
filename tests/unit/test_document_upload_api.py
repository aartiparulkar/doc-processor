
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from doc_processor.api.dependencies import (
    get_current_user,
    get_document_service,
)
from doc_processor.main import create_application

UPLOAD_URL = "/api/v1/documents/upload"


@pytest.fixture
def upload_client():
    app = create_application()

    user_id = uuid.uuid4()

    # A predictable authenticated user.
    fake_user = SimpleNamespace(id=user_id)

    # A mock service instead of real storage and PostgreSQL.
    mock_service = SimpleNamespace(
        upload_document=AsyncMock()
    )

    # Replace only the dependencies needed for this test.
    app.dependency_overrides[get_current_user] = (
        lambda: fake_user
    )
    app.dependency_overrides[get_document_service] = (
        lambda: mock_service
    )

    with TestClient(app) as client:
        yield client, mock_service, user_id

    app.dependency_overrides.clear()



def test_upload_valid_pdf(upload_client):
    client, mock_service, user_id = upload_client

    document_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)
    pdf_content = b"%PDF-1.4\nTest PDF content"

    # Simulate the document returned by the service.
    mock_service.upload_document.return_value = (
        SimpleNamespace(
            id=document_id,
            filename="report.pdf",
            created_at=created_at,
        )
    )

    response = client.post(
        UPLOAD_URL,
        files={
            "file": (
                "report.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == str(document_id)
    assert data["filename"] == "report.pdf"
    assert datetime.fromisoformat(
        data["created_at"]
    ) == created_at

    mock_service.upload_document.assert_awaited_once_with(
        user_id=user_id,
        filename="report.pdf",
        content=pdf_content,
    )



@pytest.mark.parametrize(
    "filename, content, mime_type, expected_status",
    [
        (
            "report.txt",
            b"Not a PDF",
            "text/plain",
            415,
        ),
        (
            "empty.pdf",
            b"",
            "application/pdf",
            400,
        ),
        (
            "fake.pdf",
            b"This is not a PDF",
            "application/pdf",
            415,
        ),
        (
            "oversized.pdf",
            b"%PDF-" + b"x" * (10 * 1024 * 1024),
            "application/pdf",
            413,
        ),
        (
            " ",
            b"%PDF-1.4\nTest",
            "application/pdf",
            400,
        ),
        (
            "a" * 252 + ".pdf",
            b"%PDF-1.4\nTest",
            "application/pdf",
            400,
        ),
    ],
    ids=[
        "unsupported-file-type",
        "empty-pdf",
        "invalid-pdf-content",
        "oversized-pdf",
        "blank-filename",
        "filename-too-long",
    ],
)
def test_invalid_upload(
    upload_client,
    filename,
    content,
    mime_type,
    expected_status,
):
    client, mock_service, _ = upload_client

    response = client.post(
        UPLOAD_URL,
        files={
            "file": (
                filename,
                content,
                mime_type,
            )
        },
    )

    assert response.status_code == expected_status

    # Invalid uploads must never reach the service.
    mock_service.upload_document.assert_not_awaited()



def test_upload_without_file(upload_client):
    client, mock_service, _ = upload_client

    response = client.post(UPLOAD_URL)

    assert response.status_code == 422
    mock_service.upload_document.assert_not_awaited()
