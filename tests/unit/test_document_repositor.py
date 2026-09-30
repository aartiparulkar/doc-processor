import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from doc_processor.models.documents import Document
from doc_processor.repositories.document_repository import DocumentRepository


@pytest.mark.asyncio
async def test_create_document():
    session = Mock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    
    repo = DocumentRepository(session)
    document_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    document = await repo.create(
        document_id=document_id,
        user_id=user_id,
        filename="report.pdf"
    )
    
    assert isinstance(document, Document)
    assert document.id == document_id
    assert document.user_id == user_id
    assert document.filename == "report.pdf"

    session.add.assert_called_once_with(document)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(document)

    # The repository must not commit the transaction.
    session.commit.assert_not_called()