from dataclasses import dataclass
from pathlib import Path

# Legacy import name for PyMuPDF
import pymupdf


@dataclass(slots=True)
class ParsedPDF:
    text: str
    page_count: int


def extract_pdf(path: Path) -> ParsedPDF:
    text_parts: list[str] = []

    with pymupdf.open(path) as document:
        page_count = document.page_count

        for page in document:
            text_parts.append(page.get_text())

    return ParsedPDF(
        text="\n".join(text_parts).strip(),
        page_count=page_count,
    )