
import uuid
from pathlib import Path

from doc_processor.core.config import settings


def save_pdf(
    document_id: uuid.UUID,
    content: bytes,
) -> Path:
    """Save a validated PDF using its document ID."""

    upload_dir = settings.upload_dir

    # Create the upload directory if it does not exist.
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Never use the user-supplied filename as a storage path.
    file_path = upload_dir / f"{document_id}.pdf"

    with file_path.open("xb") as destination:
        try:
            destination.write(content)

        except OSError:
        # Remove a partially written file if writing failed.
            destination.close()
            file_path.unlink(missing_ok=True)
            raise

    return file_path


def delete_pdf(document_id: uuid.UUID) -> None:
    """Remove a stored PDF, if it is present."""
    upload_dir = settings.upload_dir
    filepath = upload_dir / f"{document_id}.pdf"

    filepath.unlink(missing_ok=True)


def get_pdf_path(document_id: uuid.UUID) -> Path:
    return settings.upload_dir / f"{document_id}.pdf"
