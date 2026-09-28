"""Base report generator abstract class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ReportConfig(BaseModel):
    """Configuration for report generation."""

    title: str = Field(default="Document Quality Report")
    author: str = Field(default="Claude Document QA Agent")
    include_toc: bool = Field(default=True)
    include_statistics: bool = Field(default=True)
    theme: str = Field(default="light")  # 'light' or 'dark'
    output_dir: Path = Field(default=Path("reports"))

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


@dataclass
class AnalysisData:
    """Container for analysis data to be exported."""

    document_path: str
    language: str
    file_type: str
    quality_score: float  # 0-100
    total_issues: int
    critical_count: int
    warning_count: int
    info_count: int
    formatting_issues: list[Any]  # List[FormattingIssue]
    language_issues: list[Any]  # List[FormattingIssue]
    all_issues: list[Any]  # List[FormattingIssue]
    issues_by_type: dict[str, int]
    generated_at: datetime = None

    def __post_init__(self):
        """Set generated_at if not provided."""
        if self.generated_at is None:
            self.generated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "document_path": self.document_path,
            "language": self.language,
            "file_type": self.file_type,
            "quality_score": self.quality_score,
            "total_issues": self.total_issues,
            "severity_distribution": {
                "critical": self.critical_count,
                "warning": self.warning_count,
                "info": self.info_count,
            },
            "issues_by_type": self.issues_by_type,
            "generated_at": self.generated_at.isoformat(),
        }


class BaseReportGenerator(ABC):
    """Abstract base class for report generators."""

    def __init__(self, config: ReportConfig = None):
        """Initialize report generator.

        Args:
            config: Report configuration
        """
        self.config = config or ReportConfig()
        self._ensure_output_dir()
        logger.info(f"Initialized {self.__class__.__name__}")

    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(
        self, document_name: str, format_ext: str
    ) -> str:
        """Generate a filename for the report.

        Args:
            document_name: Original document name
            format_ext: File extension (e.g., 'html', 'pdf', 'json')

        Returns:
            Generated filename with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = Path(document_name).stem
        return f"{timestamp}_{base_name}_report.{format_ext}"

    def _get_output_path(
        self, document_name: str, format_ext: str
    ) -> Path:
        """Get full output path for report.

        Args:
            document_name: Original document name
            format_ext: File extension

        Returns:
            Full path to output file
        """
        filename = self._generate_filename(document_name, format_ext)
        return self.config.output_dir / filename

    @abstractmethod
    def generate(self, data: AnalysisData) -> str:
        """Generate report content.

        Args:
            data: Analysis data to include in report

        Returns:
            Generated report content (format-specific)
        """
        pass

    def write(self, data: AnalysisData, output_path: Path = None) -> Path:
        """Generate and write report to file.

        Args:
            data: Analysis data
            output_path: Output file path (uses default if not provided)

        Returns:
            Path to generated report file
        """
        if output_path is None:
            output_path = self._get_output_path(
                data.document_path, self._get_format_ext()
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate(data)

        if isinstance(content, bytes):
            with open(output_path, "wb") as f:
                f.write(content)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        logger.info(f"Report written to {output_path}")
        return output_path

    @abstractmethod
    def _get_format_ext(self) -> str:
        """Get file extension for this report format.

        Returns:
            File extension without dot (e.g., 'html', 'pdf')
        """
        pass
