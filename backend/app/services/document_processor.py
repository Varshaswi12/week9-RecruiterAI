from pathlib import Path

import pymupdf
from docx import Document


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class DocumentProcessingError(Exception):
    """Raised when a document cannot be processed."""
    pass


def validate_file(file_path: str) -> None:
    """
    Validate that the uploaded file exists,
    has a supported extension, and is not empty.
    """

    path = Path(file_path)

    if not path.exists():
        raise DocumentProcessingError("File does not exist.")

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise DocumentProcessingError(
            "Unsupported file format. Only PDF and DOCX files are allowed."
        )

    if path.stat().st_size == 0:
        raise DocumentProcessingError("The uploaded file is empty.")


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""

    try:
        document = pymupdf.open(file_path)

        text = []

        for page in document:
            text.append(page.get_text())

        document.close()

        extracted_text = "\n".join(text).strip()

        if not extracted_text:
            raise DocumentProcessingError(
                "The PDF does not contain extractable text."
            )

        return extracted_text

    except DocumentProcessingError:
        raise

    except Exception as exc:
        raise DocumentProcessingError(
            f"Failed to process PDF: {str(exc)}"
        ) from exc


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""

    try:
        document = Document(file_path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        extracted_text = "\n".join(paragraphs).strip()

        if not extracted_text:
            raise DocumentProcessingError(
                "The DOCX document does not contain extractable text."
            )

        return extracted_text

    except DocumentProcessingError:
        raise

    except Exception as exc:
        raise DocumentProcessingError(
            f"Failed to process DOCX: {str(exc)}"
        ) from exc


def extract_text(file_path: str) -> str:
    """
    Extract text from a supported PDF or DOCX file.
    """

    validate_file(file_path)

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    raise DocumentProcessingError(
        "Unsupported document format."
    )