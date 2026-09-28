"""Unified document quality analysis combining formatting and language rules."""

from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import (
    FormattingAnalyzer,
    FormattingIssue,
)
from claude_mcp_docqa_agent.analysis.language_rules_analyzer import (
    LanguageRulesAnalyzer,
)
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentQualityAnalyzer:
    """Unified document quality analyzer combining formatting and language rules."""

    def __init__(self, document_data: dict[str, Any]) -> None:
        """Initialize document quality analyzer.

        Args:
            document_data: Structured document content from ContentProcessor
        """
        self.document_data = document_data
        self.language = document_data.get("language", "unknown")
        self.file_type = document_data.get("file_type", "unknown")

        self.formatting_issues: list[FormattingIssue] = []
        self.language_issues: list[FormattingIssue] = []
        self.all_issues: list[FormattingIssue] = []

        logger.info(
            f"Initialized DocumentQualityAnalyzer for {self.file_type} ({self.language})"
        )

    def analyze_complete(self) -> dict[str, Any]:
        """Run complete document quality analysis.

        Returns:
            Dictionary with formatting issues, language issues, and summary
        """
        logger.info("Starting complete document quality analysis")

        # Phase 2: Formatting analysis
        logger.debug("Running formatting analysis")
        formatting_analyzer = FormattingAnalyzer(self.document_data)
        self.formatting_issues = formatting_analyzer.analyze_all()

        # Phase 3: Language-specific analysis
        logger.debug("Running language-specific analysis")
        language_analyzer = LanguageRulesAnalyzer(self.document_data)
        self.language_issues = language_analyzer.analyze()

        # Combine all issues
        self.all_issues = self.formatting_issues + self.language_issues

        logger.info(
            f"Analysis complete: {len(self.formatting_issues)} formatting issues, "
            f"{len(self.language_issues)} language issues, "
            f"{len(self.all_issues)} total"
        )

        return {
            "formatting_issues": self.formatting_issues,
            "language_issues": self.language_issues,
            "all_issues": self.all_issues,
            "summary": self.get_summary(),
        }

    def analyze_formatting_only(self) -> list[FormattingIssue]:
        """Run formatting analysis only (Phase 2).

        Returns:
            List of formatting issues
        """
        logger.info("Running formatting analysis only")

        formatting_analyzer = FormattingAnalyzer(self.document_data)
        self.formatting_issues = formatting_analyzer.analyze_all()

        return self.formatting_issues

    def analyze_language_only(self) -> list[FormattingIssue]:
        """Run language analysis only (Phase 3).

        Returns:
            List of language issues
        """
        logger.info("Running language analysis only")

        language_analyzer = LanguageRulesAnalyzer(self.document_data)
        self.language_issues = language_analyzer.analyze()

        return self.language_issues

    def get_issues_by_severity(self, severity: str) -> list[FormattingIssue]:
        """Filter all issues by severity.

        Args:
            severity: 'critical', 'warning', or 'info'

        Returns:
            Filtered issues
        """
        return [issue for issue in self.all_issues if issue.severity == severity]

    def get_issues_by_type(self, issue_type: str) -> list[FormattingIssue]:
        """Filter all issues by type.

        Args:
            issue_type: Issue type to filter by

        Returns:
            Filtered issues
        """
        return [issue for issue in self.all_issues if issue.issue_type == issue_type]

    def get_issues_by_phase(self, phase: int) -> list[FormattingIssue]:
        """Filter issues by phase.

        Args:
            phase: 2 for formatting, 3 for language

        Returns:
            Issues from specified phase
        """
        if phase == 2:
            return self.formatting_issues
        elif phase == 3:
            return self.language_issues
        else:
            return []

    def get_issues_by_page(self, page_number: int) -> list[FormattingIssue]:
        """Filter issues by page number.

        Args:
            page_number: Page number (1-indexed)

        Returns:
            Issues on that page
        """
        return [issue for issue in self.all_issues if issue.page_number == page_number]

    def get_summary(self) -> dict[str, Any]:
        """Get comprehensive summary of all issues.

        Returns:
            Summary with statistics
        """
        critical = len(self.get_issues_by_severity("critical"))
        warnings = len(self.get_issues_by_severity("warning"))
        info = len(self.get_issues_by_severity("info"))

        summary = {
            "language": self.language,
            "file_type": self.file_type,
            "total_issues": len(self.all_issues),
            "critical": critical,
            "warning": warnings,
            "info": info,
            "severity_distribution": {
                "critical": critical,
                "warning": warnings,
                "info": info,
            },
            "by_phase": {
                "formatting": len(self.formatting_issues),
                "language": len(self.language_issues),
            },
            "by_type": {},
        }

        # Count by issue type
        for issue in self.all_issues:
            issue_type = issue.issue_type
            if issue_type not in summary["by_type"]:
                summary["by_type"][issue_type] = 0
            summary["by_type"][issue_type] += 1

        return summary

    def get_issues_for_export(self) -> list[dict[str, Any]]:
        """Get all issues in dictionary format for export.

        Returns:
            List of issue dictionaries
        """
        return [issue.to_dict() for issue in self.all_issues]

    def get_quality_score(self) -> float:
        """Calculate overall document quality score (0-100).

        Returns:
            Quality score with 100 being perfect
        """
        if len(self.all_issues) == 0:
            return 100.0

        # Scoring: critical = -10 points, warning = -5 points, info = -2 points
        points_deducted = (
            len(self.get_issues_by_severity("critical")) * 10
            + len(self.get_issues_by_severity("warning")) * 5
            + len(self.get_issues_by_severity("info")) * 2
        )

        # Cap at 0 minimum
        score = max(0, 100 - points_deducted)

        return score

    def get_priority_issues(self, top_n: int = 5) -> list[FormattingIssue]:
        """Get top priority issues (sorted by severity then type).

        Args:
            top_n: Number of issues to return

        Returns:
            Top N most critical issues
        """
        severity_order = {"critical": 0, "warning": 1, "info": 2}

        sorted_issues = sorted(
            self.all_issues, key=lambda x: severity_order.get(x.severity, 3)
        )

        return sorted_issues[:top_n]
