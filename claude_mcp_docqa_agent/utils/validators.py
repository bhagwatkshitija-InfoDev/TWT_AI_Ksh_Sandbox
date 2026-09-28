"""Input validation utilities."""

from pathlib import Path

from claude_mcp_docqa_agent.errors.exceptions import InvalidDocumentError
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


def validate_document_path(file_path: str) -> Path:
    """Validate that the document file exists and has correct extension.

    Args:
        file_path: Path to the document file

    Returns:
        Validated Path object

    Raises:
        InvalidDocumentError: If file doesn't exist or has invalid format
    """
    path = Path(file_path)

    if not path.exists():
        logger.error(f"Document file not found: {file_path}")
        raise InvalidDocumentError(f"Document file not found: {file_path}")

    if path.suffix.lower() not in [".pdf", ".docx"]:
        logger.error(f"Invalid document format: {path.suffix}")
        raise InvalidDocumentError(
            f"Invalid document format: {path.suffix}. Supported: .pdf, .docx"
        )

    return path


def validate_language_code(language_code: str) -> str:
    """Validate language code.

    Args:
        language_code: Language code (e.g., 'de', 'zh_CN')

    Returns:
        Validated language code

    Raises:
        InvalidDocumentError: If language code is not supported
    """
    supported = ["de", "zh_CN", "zh", "en"]

    if language_code not in supported:
        logger.warning(f"Unsupported language code: {language_code}")
        raise InvalidDocumentError(
            f"Unsupported language: {language_code}. Supported: {', '.join(supported)}"
        )

    return language_code
