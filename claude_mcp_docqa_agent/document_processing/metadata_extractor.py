"""Extract metadata from documents."""

from pathlib import Path
from typing import Any

from claude_mcp_docqa_agent.document_processing.docx_parser import DOCXParser
from claude_mcp_docqa_agent.document_processing.pdf_extractor import PDFExtractor
from claude_mcp_docqa_agent.errors.exceptions import DocumentProcessingError
from claude_mcp_docqa_agent.utils.logger import get_logger
from claude_mcp_docqa_agent.utils.validators import validate_document_path

logger = get_logger(__name__)


class MetadataExtractor:
    """Extract metadata from PDF and DOCX documents."""

    def __init__(self, file_path: str) -> None:
        """Initialize metadata extractor.

        Args:
            file_path: Path to document file

        Raises:
            DocumentProcessingError: If file is invalid
        """
        self.file_path = validate_document_path(file_path)

    def extract_metadata(self) -> dict[str, Any]:
        """Extract metadata based on file type.

        Returns:
            Dictionary with document metadata

        Raises:
            DocumentProcessingError: If extraction fails
        """
        file_type = self.file_path.suffix.lower()

        try:
            if file_type == ".pdf":
                return self._extract_pdf_metadata()
            elif file_type == ".docx":
                return self._extract_docx_metadata()
            else:
                raise DocumentProcessingError(f"Unsupported file type: {file_type}")

        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            raise DocumentProcessingError(f"Failed to extract metadata: {e}")

    def _extract_pdf_metadata(self) -> dict[str, Any]:
        """Extract PDF metadata.

        Returns:
            PDF metadata dictionary
        """
        extractor = PDFExtractor(str(self.file_path))
        pdf_meta = extractor.extract_metadata()

        return {
            "file_path": str(self.file_path),
            "file_type": "pdf",
            "filename": self.file_path.name,
            "file_size": self.file_path.stat().st_size,
            "total_pages": pdf_meta.get("total_pages", 0),
            "pdf_metadata": pdf_meta.get("metadata", {}),
        }

    def _extract_docx_metadata(self) -> dict[str, Any]:
        """Extract DOCX metadata.

        Returns:
            DOCX metadata dictionary
        """
        parser = DOCXParser(str(self.file_path))
        docx_meta = parser.extract_metadata()

        return {
            "file_path": str(self.file_path),
            "file_type": "docx",
            "filename": self.file_path.name,
            "file_size": self.file_path.stat().st_size,
            "properties": docx_meta,
        }

    def get_text_sample(self, length: int = 500) -> str:
        """Get a sample of text from the document.

        Args:
            length: Maximum length of sample

        Returns:
            Text sample from beginning of document
        """
        file_type = self.file_path.suffix.lower()

        try:
            if file_type == ".pdf":
                extractor = PDFExtractor(str(self.file_path))
                text = extractor.extract_full_text()
            elif file_type == ".docx":
                parser = DOCXParser(str(self.file_path))
                text = parser.extract_full_text()
            else:
                return ""

            return text[:length]

        except Exception as e:
            logger.warning(f"Failed to get text sample: {e}")
            return ""
