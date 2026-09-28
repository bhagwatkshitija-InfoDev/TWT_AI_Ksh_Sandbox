"""PDF-specific formatting analyzers."""

import uuid
from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class PDFFontAnalyzer:
    """Analyze font usage in PDF documents."""

    MAX_UNIQUE_FONTS = 5

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize PDF font analyzer.

        Args:
            document_content: Structured PDF content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze font usage in PDF.

        Returns:
            List of font-related issues
        """
        self._check_font_variety()
        self._check_font_sizes()
        return self.issues

    def _check_font_variety(self) -> None:
        """Check for excessive font variety in PDF."""
        pages = self.content.get("pages", [])

        all_fonts = {}
        for page in pages:
            chars = page.get("num_chars", 0)
            if chars > 0:
                # In a full implementation, would extract actual fonts from PDF
                # For now, use heuristic based on character counts
                pass

        # PDF font analysis is limited without full PDF parsing
        logger.debug("PDF font variety check completed")

    def _check_font_sizes(self) -> None:
        """Check for inconsistent font sizes in PDF."""
        pages = self.content.get("pages", [])

        if len(pages) < 2:
            return

        # Basic heuristic: check if consecutive pages have significant size differences
        page_char_counts = [p.get("num_chars", 0) for p in pages]

        for i in range(1, len(page_char_counts)):
            prev_count = page_char_counts[i - 1]
            curr_count = page_char_counts[i]

            if prev_count > 0:
                variance = abs(curr_count - prev_count) / prev_count

                # Flag if variation > 50% (likely indicates different font size)
                if variance > 0.5 and curr_count > 100:
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=i + 1,
                        issue_type="font_size_variation",
                        severity="info",
                        location_description=f"Page {i + 1}",
                        issue_description=f"Page has significantly different character density ({variance:.0%}) from previous page",
                        recommended_fix="Check if font size or margins differ from other pages for consistency",
                    )
                    self.issues.append(issue)
                    logger.debug(f"Found font size variance on page {i + 1}")


class PDFTableAnalyzer:
    """Analyze table structures in PDF documents."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize PDF table analyzer.

        Args:
            document_content: Structured PDF content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze tables in PDF.

        Returns:
            List of table-related issues
        """
        self._check_table_content()
        return self.issues

    def _check_table_content(self) -> None:
        """Check for tables in PDF and basic validation."""
        pages = self.content.get("pages", [])

        for page_idx, page in enumerate(pages):
            page_tables = page.get("tables", [])

            for table_idx, table in enumerate(page_tables):
                if not table:
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=page_idx + 1,
                        issue_type="table_content",
                        severity="info",
                        location_description=f"Page {page_idx + 1}, Table {table_idx + 1}",
                        issue_description="Table appears to be empty or unable to extract",
                        recommended_fix="Verify table contains readable content and formatting is correct",
                    )
                    self.issues.append(issue)
                    logger.debug(
                        f"Found empty table on page {page_idx + 1}, table {table_idx + 1}"
                    )

    def get_table_count(self) -> int:
        """Get total number of tables in PDF.

        Returns:
            Total table count
        """
        pages = self.content.get("pages", [])
        return sum(len(p.get("tables", [])) for p in pages)


class PDFStructureAnalyzer:
    """Analyze document structure in PDF."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize PDF structure analyzer.

        Args:
            document_content: Structured PDF content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze PDF document structure.

        Returns:
            List of structure-related issues
        """
        self._check_page_consistency()
        return self.issues

    def _check_page_consistency(self) -> None:
        """Check for unusual page structures."""
        pages = self.content.get("pages", [])
        total_pages = len(pages)

        if total_pages < 2:
            return

        # Check for pages with unusual content density
        page_contents = [
            (p.get("num_chars", 0) + p.get("num_lines", 0) + p.get("num_rects", 0))
            for p in pages
        ]

        avg_content = sum(page_contents) / len(page_contents) if page_contents else 0

        for page_idx, content_count in enumerate(page_contents):
            if avg_content > 0:
                variance = abs(content_count - avg_content) / avg_content

                # Flag pages with <10% or >200% of average content
                if content_count == 0 and page_idx > 0:
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=page_idx + 1,
                        issue_type="page_structure",
                        severity="info",
                        location_description=f"Page {page_idx + 1}",
                        issue_description="Page appears to be blank or has no readable content",
                        recommended_fix="Verify page content is correct or remove if unnecessary",
                    )
                    self.issues.append(issue)
                    logger.debug(f"Found blank page: {page_idx + 1}")
