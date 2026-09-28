"""JSON report exporter."""

import json
from typing import Any

from claude_mcp_docqa_agent.report_generation.base import (
    AnalysisData,
    BaseReportGenerator,
    ReportConfig,
)
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class JSONReporter(BaseReportGenerator):
    """Generate JSON format reports."""

    def __init__(self, config: ReportConfig = None):
        """Initialize JSON reporter.

        Args:
            config: Report configuration
        """
        super().__init__(config)

    def generate(self, data: AnalysisData) -> str:
        """Generate JSON report.

        Args:
            data: Analysis data

        Returns:
            JSON string
        """
        logger.info("Generating JSON report")

        report = {
            "metadata": {
                "title": self.config.title,
                "author": self.config.author,
                "generated_at": data.generated_at.isoformat(),
                "document": {
                    "path": data.document_path,
                    "language": data.language,
                    "file_type": data.file_type,
                },
            },
            "quality": {
                "score": round(data.quality_score, 1),
                "total_issues": data.total_issues,
                "severity_distribution": {
                    "critical": data.critical_count,
                    "warning": data.warning_count,
                    "info": data.info_count,
                },
            },
            "issues_by_type": data.issues_by_type,
            "formatting_issues": [
                self._issue_to_dict(issue) for issue in data.formatting_issues
            ],
            "language_issues": [
                self._issue_to_dict(issue) for issue in data.language_issues
            ],
            "summary": {
                "critical_issues": [
                    self._issue_to_dict(issue)
                    for issue in data.all_issues
                    if issue.severity == "critical"
                ],
                "top_issues": [
                    self._issue_to_dict(issue)
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
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    @staticmethod
    def _issue_to_dict(issue: Any) -> dict[str, Any]:
        """Convert FormattingIssue to dictionary.

        Args:
            issue: FormattingIssue object

        Returns:
            Dictionary representation
        """
        result = {
            "id": issue.id,
            "type": issue.issue_type,
            "severity": issue.severity,
            "page": issue.page_number,
            "location": issue.location_description,
            "description": issue.issue_description,
            "fix": issue.recommended_fix,
        }

        if issue.context:
            result["context"] = issue.context

        if issue.coordinates:
            result["coordinates"] = {
                "x0": round(issue.coordinates.get("x0", 0), 2),
                "y0": round(issue.coordinates.get("y0", 0), 2),
                "x1": round(issue.coordinates.get("x1", 0), 2),
                "y1": round(issue.coordinates.get("y1", 0), 2),
            }

        return result

    def _get_format_ext(self) -> str:
        """Get file extension for JSON format.

        Returns:
            'json'
        """
        return "json"
