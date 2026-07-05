import magic
from typing import Tuple
import structlog

from app.core.exceptions import ValidationException

logger = structlog.get_logger()

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file_content: bytes, filename: str) -> Tuple[str, int]:
    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        raise ValidationException(f"File size exceeds 10MB limit (got {file_size / 1024 / 1024:.1f}MB)")

    mime_type = magic.from_buffer(file_content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValidationException(f"Invalid file type: {mime_type}. Only PDF and DOCX are accepted.")

    expected_ext = ALLOWED_MIME_TYPES[mime_type]
    if not filename.lower().endswith(expected_ext):
        raise ValidationException("File extension does not match content type")

    return mime_type, file_size
