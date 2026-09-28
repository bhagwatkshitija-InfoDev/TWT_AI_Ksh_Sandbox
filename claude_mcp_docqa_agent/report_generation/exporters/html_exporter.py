"""HTML report exporter with Jinja2 templating."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from claude_mcp_docqa_agent.report_generation.base import (
    AnalysisData,
    BaseReportGenerator,
    ReportConfig,
)
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class HTMLReporter(BaseReportGenerator):
    """Generate HTML format reports with professional styling."""

    def __init__(self, config: ReportConfig = None):
        """Initialize HTML reporter.

        Args:
            config: Report configuration
        """
        super().__init__(config)
        self.jinja_env = self._setup_jinja()

    def _setup_jinja(self) -> Environment:
        """Set up Jinja2 environment.

        Returns:
            Configured Jinja2 environment
        """
        try:
            env = Environment(
                loader=PackageLoader(
                    "claude_mcp_docqa_agent.report_generation", "templates"
                ),
                autoescape=select_autoescape(),
            )
        except Exception as e:
            logger.warning(
                f"Could not load templates from package: {e}. Using fallback."
            )
            # Fallback to file system loader
            template_dir = Path(__file__).parent.parent / "templates"
            from jinja2 import FileSystemLoader
            env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(),
            )

        return env

    def generate(self, data: AnalysisData) -> str:
        """Generate HTML report.

        Args:
            data: Analysis data

        Returns:
            HTML string
        """
        logger.info("Generating HTML report")

        template = self.jinja_env.get_template("report_base.html")

        # Prepare context for template
        context = self._prepare_context(data)

        return template.render(**context)

    def _prepare_context(self, data: AnalysisData) -> dict[str, Any]:
        """Prepare template context from analysis data.

        Args:
            data: Analysis data

        Returns:
            Dictionary ready for template rendering
        """
        # Group issues by type
        issues_by_type = self._group_issues_by_type(data.all_issues)

        # Group issues by severity
        issues_by_severity = self._group_issues_by_severity(data.all_issues)

        # Get severity color mapping
        severity_colors = {
            "critical": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
        }

        return {
            "title": self.config.title,
            "author": self.config.author,
            "theme": self.config.theme,
            "generated_at": data.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "document": {
                "path": data.document_path,
                "name": Path(data.document_path).name,
                "language": data.language.upper(),
                "file_type": data.file_type.upper(),
            },
            "quality": {
                "score": round(data.quality_score, 1),
                "grade": self._get_grade(data.quality_score),
                "color": self._get_score_color(data.quality_score),
            },
            "summary": {
                "total_issues": data.total_issues,
                "critical": data.critical_count,
                "warning": data.warning_count,
                "info": data.info_count,
                "severity_colors": severity_colors,
            },
            "issues": {
                "by_type": issues_by_type,
                "by_severity": issues_by_severity,
                "critical_issues": [
                    self._format_issue(issue)
                    for issue in data.all_issues
                    if issue.severity == "critical"
                ],
                "top_10": [
                    self._format_issue(issue)
                    for issue in sorted(
                        data.all_issues,
                        key=lambda x: (
                            {"critical": 0, "warning": 1, "info": 2}[
                                x.severity
                            ],
                            x.page_number,
                        ),
                    )[:10]
                ],
            },
            "issues_by_type_names": list(data.issues_by_type.keys()),
            "include_toc": self.config.include_toc,
            "include_statistics": self.config.include_statistics,
        }

    @staticmethod
    def _group_issues_by_type(
        issues: list[Any],
    ) -> dict[str, list[Any]]:
        """Group issues by type.

        Args:
            issues: List of issues

        Returns:
            Dictionary mapping issue type to list of issues
        """
        result = {}
        for issue in issues:
            issue_type = issue.issue_type
            if issue_type not in result:
                result[issue_type] = []
            result[issue_type].append(issue)
        return result

    @staticmethod
    def _group_issues_by_severity(
        issues: list[Any],
    ) -> dict[str, list[Any]]:
        """Group issues by severity.

        Args:
            issues: List of issues

        Returns:
            Dictionary mapping severity to list of issues
        """
        result = {"critical": [], "warning": [], "info": []}
        for issue in issues:
            severity = issue.severity
            if severity in result:
                result[severity].append(issue)
        return result

    @staticmethod
    def _format_issue(issue: Any) -> dict[str, Any]:
        """Format an issue for display.

        Args:
            issue: FormattingIssue object

        Returns:
            Formatted issue dictionary
        """
        return {
            "id": issue.id,
            "type": issue.issue_type,
            "severity": issue.severity,
            "page": issue.page_number,
            "location": issue.location_description,
            "description": issue.issue_description,
            "fix": issue.recommended_fix,
            "context": issue.context or "",
        }

    @staticmethod
    def _get_grade(score: float) -> str:
        """Get letter grade for quality score.

        Args:
            score: Quality score (0-100)

        Returns:
            Letter grade
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    @staticmethod
    def _get_score_color(score: float) -> str:
        """Get color for quality score.

        Args:
            score: Quality score (0-100)

        Returns:
            Hex color code
        """
        if score >= 90:
            return "#28a745"  # Green
        elif score >= 80:
            return "#5cb85c"  # Light green
        elif score >= 70:
            return "#ffc107"  # Yellow
        elif score >= 60:
            return "#fd7e14"  # Orange
        else:
            return "#dc3545"  # Red

    def _get_format_ext(self) -> str:
        """Get file extension for HTML format.

        Returns:
            'html'
        """
        return "html"
