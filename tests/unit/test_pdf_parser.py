from pathlib import Path

import pymupdf

from doc_processor.services.pdf_parser import extract_pdf


def test_extract_pdf(tmp_path: Path):
    pdf_path = tmp_path / "test.pdf"

    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Hello from page one",
    )

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Hello from page two",
    )

    document.save(pdf_path)
    document.close()

    result = extract_pdf(pdf_path)

    assert result.page_count == 2
    assert "Hello from page one" in result.text
    assert "Hello from page two" in result.text