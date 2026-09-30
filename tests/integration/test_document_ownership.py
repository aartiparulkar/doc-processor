import os

import httpx

BASE_URL = os.getenv(
    "TEST_BASE_URL",
    "http://127.0.0.1.8000",
)


def test_cross_document_access():
    token_a = os.environ["TEST_USER_A_TOKEN"]
    document_a = os.environ["TEST_DOCUMENT_A_ID"]
    document_b = os.environ["TEST_DOCUMENT_B_ID"]

    headers = {
        "Authorization": f"Bearer {token_a}",
    }

    with httpx.Client(
        base_url=BASE_URL,
        timeout=10.0,
    ) as client:

        # User A retrieves their own document.
        response = client.get(
            f"/api/v1/documents/{document_a}",
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == document_a

        # User A attempts to retrieve User B's document.
        response = client.get(
            f"/api/v1/documents/{document_b}",
            headers=headers,
        )

        assert response.status_code == 404
