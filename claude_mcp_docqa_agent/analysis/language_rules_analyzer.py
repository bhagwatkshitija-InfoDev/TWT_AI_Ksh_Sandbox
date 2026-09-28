"""Language-specific rules analyzer."""

from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.analysis.language_rules.chinese_rules import (
    ChineseRulesEngine,
)
from claude_mcp_docqa_agent.analysis.language_rules.german_rules import GermanRulesEngine
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class LanguageRulesAnalyzer:
    """Apply language-specific rules based on detected language."""

    def __init__(self, document_data: dict[str, Any]) -> None:
        """Initialize language rules analyzer.

        Args:
            document_data: Structured document content from ContentProcessor
        """
        self.document_data = document_data
        self.language = document_data.get("language", "unknown")
        self.content = document_data.get("content", {})
        self.issues: list[FormattingIssue] = []

        logger.info(f"Initialized LanguageRulesAnalyzer for language: {self.language}")

    def analyze(self) -> list[FormattingIssue]:
        """Run language-specific analysis based on detected language.

        Returns:
            List of language-specific issues
        """
        logger.info(f"Starting language-specific analysis for {self.language}")

        if self.language == "de":
            return self._analyze_german()
        elif self.language in ["zh_CN", "zh-cn", "zh"]:
            return self._analyze_chinese()
        else:
            logger.warning(f"No language-specific rules for language: {self.language}")
            return []

    def _analyze_german(self) -> list[FormattingIssue]:
        """Analyze German language conventions.

        Returns:
            List of German convention issues
        """
        logger.debug("Applying German language rules")

        engine = GermanRulesEngine(self.content)
        issues = engine.analyze()

        logger.info(f"Found {len(issues)} German language issues")
        return issues

    def _analyze_chinese(self) -> list[FormattingIssue]:
        """Analyze Chinese language conventions.

        Returns:
            List of Chinese convention issues
        """
        logger.debug("Applying Chinese language rules")

        engine = ChineseRulesEngine(self.content)
        issues = engine.analyze()

        logger.info(f"Found {len(issues)} Chinese language issues")
        return issues

    def get_issues_by_type(self, issue_type: str) -> list[FormattingIssue]:
        """Filter issues by type.

        Args:
            issue_type: Issue type to filter by

        Returns:
            Filtered issues
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]

    def get_issues_by_severity(self, severity: str) -> list[FormattingIssue]:
        """Filter issues by severity.

        Args:
            severity: 'critical', 'warning', or 'info'

        Returns:
            Filtered issues
        """
        return [issue for issue in self.issues if issue.severity == severity]

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics of language issues.

        Returns:
            Summary with counts by severity and type
        """
        summary = {
            "language": self.language,
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
