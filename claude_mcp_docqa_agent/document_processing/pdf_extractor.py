"""PDF extraction using pdfplumber."""

import json
from pathlib import Path
from typing import Any, Optional

import pdfplumber

from claude_mcp_docqa_agent.errors.exceptions import PDFExtractionError
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class PDFExtractor:
    """Extract content and metadata from PDF files."""

    def __init__(self, file_path: str) -> None:
        """Initialize PDF extractor.

        Args:
            file_path: Path to PDF file

        Raises:
            PDFExtractionError: If file is not a valid PDF
        """
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise PDFExtractionError(f"PDF file not found: {file_path}")

        if self.file_path.suffix.lower() != ".pdf":
            raise PDFExtractionError(f"File is not a PDF: {file_path}")

        logger.info(f"Initialized PDF extractor for: {self.file_path}")

    def extract_full_text(self) -> str:
        """Extract all text from PDF.

        Returns:
            Combined text from all pages

        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                full_text = "\n".join(text_parts)
                logger.info(f"Extracted text from {len(pdf.pages)} pages")
                return full_text

        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            raise PDFExtractionError(f"Failed to extract text: {e}")

    def extract_page_content(self, page_number: int) -> dict[str, Any]:
        """Extract content from a specific page.

        Args:
            page_number: 0-indexed page number

        Returns:
            Dictionary containing page text, tables, and metadata

        Raises:
            PDFExtractionError: If page extraction fails
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                if page_number >= len(pdf.pages):
                    raise PDFExtractionError(f"Page {page_number} not found")

                page = pdf.pages[page_number]

                return {
                    "page_number": page_number + 1,
                    "text": page.extract_text() or "",
                    "tables": page.extract_tables() or [],
                    "lines": page.lines,
                    "rects": page.rects,
                    "chars": page.chars,
                    "width": page.width,
                    "height": page.height,
                }

        except Exception as e:
            logger.error(f"Page {page_number} extraction failed: {e}")
            raise PDFExtractionError(f"Failed to extract page {page_number}: {e}")

    def extract_metadata(self) -> dict[str, Any]:
        """Extract PDF metadata.

        Returns:
            Dictionary with PDF metadata
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                return {
                    "total_pages": len(pdf.pages),
                    "metadata": pdf.metadata,
                    "file_size": self.file_path.stat().st_size,
                }

        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {"error": str(e)}

    def extract_all_tables(self) -> list[list[list[Optional[str]]]]:
        """Extract all tables from PDF.

        Returns:
            List of tables (each table is a list of rows)
        """
        tables = []

        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            tables.append({"page": page_idx + 1, "table": table})

                logger.info(f"Extracted {len(tables)} tables from PDF")
                return tables

        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            raise PDFExtractionError(f"Failed to extract tables: {e}")

    def extract_structured_content(self) -> dict[str, Any]:
        """Extract structured content from entire PDF.

        Returns:
            Dictionary with pages, metadata, and statistics
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                pages_content = []

                for idx, page in enumerate(pdf.pages):
                    page_data = {
                        "page_number": idx + 1,
                        "text": page.extract_text() or "",
                        "tables": page.extract_tables() or [],
                        "num_chars": len(page.chars),
                        "num_lines": len(page.lines),
                        "num_rects": len(page.rects),
                    }
                    pages_content.append(page_data)

                result = {
                    "file_path": str(self.file_path),
                    "total_pages": len(pdf.pages),
                    "metadata": pdf.metadata or {},
                    "pages": pages_content,
                }

                logger.info(f"Extracted structured content from {len(pdf.pages)} pages")
                return result

        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            raise PDFExtractionError(f"Failed to extract structured content: {e}")
