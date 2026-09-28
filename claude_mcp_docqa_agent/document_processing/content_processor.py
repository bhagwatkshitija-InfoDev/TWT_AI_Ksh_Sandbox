"""Process and normalize document content."""

from typing import Any

from claude_mcp_docqa_agent.analysis.language_detector import LanguageDetector
from claude_mcp_docqa_agent.document_processing.docx_parser import DOCXParser
from claude_mcp_docqa_agent.document_processing.pdf_extractor import PDFExtractor
from claude_mcp_docqa_agent.errors.exceptions import DocumentProcessingError
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ContentProcessor:
    """Process document content into standard format."""

    def __init__(self, file_path: str) -> None:
        """Initialize content processor.

        Args:
            file_path: Path to document file
        """
        self.file_path = file_path
        self.detector = LanguageDetector()

    def process_document(self) -> dict[str, Any]:
        """Process entire document and return structured content.

        Returns:
            Dictionary with processed content and metadata

        Raises:
            DocumentProcessingError: If processing fails
        """
        try:
            # Determine file type
            if self.file_path.endswith(".pdf"):
                return self._process_pdf()
            elif self.file_path.endswith(".docx"):
                return self._process_docx()
            else:
                raise DocumentProcessingError(f"Unsupported file type: {self.file_path}")

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise DocumentProcessingError(f"Failed to process document: {e}")

    def _process_pdf(self) -> dict[str, Any]:
        """Process PDF document.

        Returns:
            Processed PDF content
        """
        extractor = PDFExtractor(self.file_path)

        # Extract text for language detection
        full_text = extractor.extract_full_text()
        text_sample = full_text[:1000]

        # Detect language
        lang_detection = self.detector.detect_language(text_sample)
        language = lang_detection["language"]

        structured = extractor.extract_structured_content()

        return {
            "file_path": self.file_path,
            "file_type": "pdf",
            "language": language,
            "language_detection": lang_detection,
            "content": structured,
            "full_text": full_text,
        }

    def _process_docx(self) -> dict[str, Any]:
        """Process DOCX document.

        Returns:
            Processed DOCX content
        """
        parser = DOCXParser(self.file_path)

        # Extract text for language detection
        full_text = parser.extract_full_text()
        text_sample = full_text[:1000]

        # Detect language
        lang_detection = self.detector.detect_language(text_sample)
        language = lang_detection["language"]

        structured = parser.extract_structured_content()

        return {
            "file_path": self.file_path,
            "file_type": "docx",
            "language": language,
            "language_detection": lang_detection,
            "content": structured,
            "full_text": full_text,
        }

    def get_text_for_analysis(self) -> str:
        """Get full text from document for analysis.

        Returns:
            Full text content
        """
        try:
            if self.file_path.endswith(".pdf"):
                extractor = PDFExtractor(self.file_path)
                return extractor.extract_full_text()
            elif self.file_path.endswith(".docx"):
                parser = DOCXParser(self.file_path)
                return parser.extract_full_text()
            else:
                return ""

        except Exception as e:
            logger.warning(f"Failed to extract text: {e}")
            return ""

    def get_page_count(self) -> int:
        """Get total page count.

        Returns:
            Number of pages in document
        """
        try:
            if self.file_path.endswith(".pdf"):
                extractor = PDFExtractor(self.file_path)
                return extractor.extract_metadata().get("total_pages", 0)
            elif self.file_path.endswith(".docx"):
                # DOCX doesn't have pages, count sections
                parser = DOCXParser(self.file_path)
                metadata = parser.extract_metadata()
                return metadata.get("num_sections", 0) or 1
            else:
                return 0

        except Exception as e:
            logger.warning(f"Failed to get page count: {e}")
            return 0
