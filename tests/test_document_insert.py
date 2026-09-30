import uuid
from datetime import UTC, datetime

from doc_processor.models.documents import Document
from doc_processor.schemas.documents import DocumentResponse

document = Document(
    id=uuid.uuid4(),
    user_id=uuid.uuid4(),
    filename="report.pdf",
    created_at=datetime.now(UTC),
)

response = DocumentResponse.model_validate(document)

assert response.id == document.id
assert response.filename == "report.pdf"
assert response.created_at == document.created_at
assert "user_id" not in response.model_dump()

print("DocumentResponse validation passed")