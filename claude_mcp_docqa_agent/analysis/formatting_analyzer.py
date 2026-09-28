"""Main formatting analysis module."""

from dataclasses import dataclass, asdict
from typing import Any, Optional

from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FormattingIssue:
    """Represents a single formatting issue."""

    id: str
    page_number: int
    issue_type: str
    severity: str  # 'critical', 'warning', 'info'
    location_description: str
    issue_description: str
    recommended_fix: str
    coordinates: Optional[dict[str, float]] = None
    context: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class FormattingAnalyzer:
    """Main formatting analysis orchestrator."""

    def __init__(self, document_data: dict[str, Any]) -> None:
        """Initialize formatter with document data.

        Args:
            document_data: Structured document content from ContentProcessor
        """
        self.document_data = document_data
        self.file_type = document_data.get("file_type")
        self.language = document_data.get("language")
        self.full_text = document_data.get("full_text", "")
        self.content = document_data.get("content", {})
        self.issues: list[FormattingIssue] = []

        logger.info(f"Initialized FormattingAnalyzer for {self.file_type} document")

    def analyze_all(self) -> list[FormattingIssue]:
        """Run all formatting analysis checks.

        Returns:
            List of formatting issues found
        """
        logger.info("Starting comprehensive formatting analysis")

        # Delegate to specific analyzers based on file type
        if self.file_type == "docx":
            self._analyze_docx_formatting()
        elif self.file_type == "pdf":
            self._analyze_pdf_formatting()

        logger.info(f"Found {len(self.issues)} formatting issues")
        return self.issues

    def _analyze_docx_formatting(self) -> None:
        """Analyze DOCX-specific formatting."""
        from claude_mcp_docqa_agent.analysis.docx_analyzers import (
            DOCXFontAnalyzer,
            DOCXHeadingAnalyzer,
            DOCXTableAnalyzer,
            DOCXListAnalyzer,
        )

        content = self.content

        # Font consistency
        logger.debug("Analyzing font consistency")
        font_analyzer = DOCXFontAnalyzer(content)
        self.issues.extend(font_analyzer.analyze())

        # Heading hierarchy
        logger.debug("Analyzing heading hierarchy")
        heading_analyzer = DOCXHeadingAnalyzer(content)
        self.issues.extend(heading_analyzer.analyze())

        # Table formatting
        logger.debug("Analyzing table formatting")
        table_analyzer = DOCXTableAnalyzer(content)
        self.issues.extend(table_analyzer.analyze())

        # List formatting
        logger.debug("Analyzing list formatting")
        list_analyzer = DOCXListAnalyzer(content)
        self.issues.extend(list_analyzer.analyze())

    def _analyze_pdf_formatting(self) -> None:
        """Analyze PDF-specific formatting."""
        from claude_mcp_docqa_agent.analysis.pdf_analyzers import (
            PDFFontAnalyzer,
            PDFTableAnalyzer,
        )

        content = self.content

        # Font consistency in PDF
        logger.debug("Analyzing font consistency in PDF")
        font_analyzer = PDFFontAnalyzer(content)
        self.issues.extend(font_analyzer.analyze())

        # Tables in PDF
        logger.debug("Analyzing PDF tables")
        table_analyzer = PDFTableAnalyzer(content)
        self.issues.extend(table_analyzer.analyze())

    def get_issues_by_severity(self, severity: str) -> list[FormattingIssue]:
        """Get issues filtered by severity.

        Args:
            severity: 'critical', 'warning', or 'info'

        Returns:
            Filtered list of issues
        """
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_page(self, page_number: int) -> list[FormattingIssue]:
        """Get issues filtered by page number.

        Args:
            page_number: Page number (1-indexed)

        Returns:
            Issues on that page
        """
        return [issue for issue in self.issues if issue.page_number == page_number]

    def get_issues_by_type(self, issue_type: str) -> list[FormattingIssue]:
        """Get issues filtered by type.

        Args:
            issue_type: Issue type (e.g., 'font', 'heading', 'table')

        Returns:
            Issues of that type
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics of formatting issues.

        Returns:
            Summary with counts by severity and type
        """
        summary = {
            "total_issues": len(self.issues),
            "critical": len(self.get_issues_by_severity("critical")),
            "warning": len(self.get_issues_by_severity("warning")),
            "info": len(self.get_issues_by_severity("info")),
            "by_type": {},
        }

        # Count by issue type
        for issue in self.issues:
            issue_type = issue.issue_type
            if issue_type not in summary["by_type"]:
                summary["by_type"][issue_type] = 0
            summary["by_type"][issue_type] += 1

        return summary
