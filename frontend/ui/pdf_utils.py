from io import BytesIO

from pypdf import PdfReader

from .settings import MAX_FILE_BYTES, MAX_DOCUMENT_CHARS


class PDFValidationError(Exception):
    """An error identified by a translation key."""


def extract_pdf_text(raw):
    if not raw:
        raise PDFValidationError("empty_file")

    if len(raw) > MAX_FILE_BYTES:
        raise PDFValidationError("large_file")

    reader = PdfReader(BytesIO(raw))

    if reader.is_encrypted:
        raise PDFValidationError("encrypted")

    if len(reader.pages) > 30:
        raise PDFValidationError("many_pages")

    parts = []
    total_chars = 0

    for page in reader.pages:
        page_text = page.extract_text() or ""
        total_chars += len(page_text) + 2

        if total_chars > MAX_DOCUMENT_CHARS:
            raise PDFValidationError("long_text")

        parts.append(page_text)

    text = "\n\n".join(parts).strip()

    if not text:
        raise PDFValidationError("no_text")

    return text
