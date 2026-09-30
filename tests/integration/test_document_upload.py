
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from doc_processor.core.config import settings
from doc_processor.db.session import engine
from doc_processor.main import create_application

BASE_URL = "/api/v1"


@pytest.fixture
def client(tmp_path: Path, monkeypatch):
    # Isolate file storage for each test.
    assert make_url(settings.database_url).database == "doc_processor_test", (
        "Integration tests must use doc_processor_test"
    )
    monkeypatch.setattr(settings, "upload_dir", tmp_path)

    # Use the actual application and dependencies.
    app = create_application()

    with TestClient(app) as test_client:
        try:
            yield test_client, tmp_path
        finally:
            test_client.portal.call(engine.dispose)
        

def create_authenticated_user(client: TestClient) -> dict:
    # Generate a unique email to avoid conflicts.
    email = f"test-{uuid.uuid4().hex}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "user_id": register_response.json()["id"],
        "headers": {
            "Authorization": f"Bearer {token}",
        },
    }


def test_upload_and_retrieve_document(client):
    test_client, upload_dir = client
    user = create_authenticated_user(test_client)

    # Enough to test the current upload validation.
    pdf_content = b"%PDF-1.4\nIntegration test content"

    # 1. Upload the document.
    response = test_client.post(
        f"{BASE_URL}/documents/upload",
        headers=user["headers"],
        files={
            "file": (
                "report.pdf",
                pdf_content,
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 201

    document = response.json()
    document_id = document["id"]

    assert uuid.UUID(document_id)
    assert document["filename"] == "report.pdf"
    assert document["created_at"]

    # 2. Verify the saved physical file.
    saved_file = upload_dir / f"{document_id}.pdf"

    assert saved_file.is_file()
    assert saved_file.read_bytes() == pdf_content

    # 3. Retrieve the document through the API.
    get_response = test_client.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=user["headers"],
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == document_id
    assert get_response.json()["filename"] == "report.pdf"

    # 4. Verify the document appears in the user's list.
    list_response = test_client.get(
        f"{BASE_URL}/documents",
        headers=user["headers"],
    )

    assert list_response.status_code == 200

    document_ids = {
        item["id"]
        for item in list_response.json()
    }

    assert document_id in document_ids


def test_document_access_is_user_scoped(client):
    test_client, _ = client

    # Create two real users.
    owner = create_authenticated_user(test_client)
    other_user = create_authenticated_user(test_client)

    # The first user uploads a document.
    upload_response = test_client.post(
        f"{BASE_URL}/documents/upload",
        headers=owner["headers"],
        files={
            "file": (
                "private.pdf",
                b"%PDF-1.4\nPrivate content",
                "application/pdf",
            ),
        },
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["id"]

    # The owner should be able to retrieve it.
    owner_response = test_client.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=owner["headers"],
    )

    assert owner_response.status_code == 200

    # The second user must not be able to retrieve it.
    other_response = test_client.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=other_user["headers"],
    )

    assert other_response.status_code == 404

    # It must not appear in the second user's document list.
    list_response = test_client.get(
        f"{BASE_URL}/documents",
        headers=other_user["headers"],
    )

    assert list_response.status_code == 200

    assert all(
        document["id"] != document_id
        for document in list_response.json()
    )


def test_upload_boundaries(client):
    test_client, upload_dir = client
    user = create_authenticated_user(test_client)

    pdf_content = b"%PDF-1.4\nRepeated upload"

    def upload():
        return test_client.post(
            f"{BASE_URL}/documents/upload",
            headers=user["headers"],
            files={
                "file": (
                    "report.pdf",
                    pdf_content,
                    "application/pdf",
                ),
            },
        )

    # The same filename must produce different IDs.
    first = upload()
    second = upload()

    assert first.status_code == 201
    assert second.status_code == 201

    first_id = first.json()["id"]
    second_id = second.json()["id"]

    assert first_id != second_id
    assert (upload_dir / f"{first_id}.pdf").exists()
    assert (upload_dir / f"{second_id}.pdf").exists()

    # Invalid content must not create another file.
    files_before = set(upload_dir.iterdir())

    invalid = test_client.post(
        f"{BASE_URL}/documents/upload",
        headers=user["headers"],
        files={
            "file": (
                "invalid.pdf",
                b"Not a PDF",
                "application/pdf",
            ),
        },
    )

    assert invalid.status_code == 415
    assert set(upload_dir.iterdir()) == files_before

    # An unauthenticated request must be rejected.
    unauthorized = test_client.post(
        f"{BASE_URL}/documents/upload",
        files={
            "file": (
                "report.pdf",
                pdf_content,
                "application/pdf",
            ),
        },
    )

    assert unauthorized.status_code == 401
    assert set(upload_dir.iterdir()) == files_before
