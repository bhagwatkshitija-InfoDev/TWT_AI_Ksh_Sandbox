"""Report manager orchestrates report generation across formats."""

from datetime import datetime
from pathlib import Path
from typing import Any

from claude_mcp_docqa_agent.analysis.document_quality_analyzer import (
    DocumentQualityAnalyzer,
)
from claude_mcp_docqa_agent.report_generation.base import AnalysisData, ReportConfig
from claude_mcp_docqa_agent.report_generation.exporters.json_exporter import (
    JSONReporter,
)
from claude_mcp_docqa_agent.report_generation.exporters.html_exporter import (
    HTMLReporter,
)
from claude_mcp_docqa_agent.report_generation.exporters.pdf_exporter import (
    PDFReporter,
)
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ReportManager:
    """Manages report generation across multiple formats."""

    EXPORTERS = {
        "json": JSONReporter,
        "html": HTMLReporter,
        "pdf": PDFReporter,
    }

    def __init__(self, config: ReportConfig = None):
        """Initialize report manager.

        Args:
            config: Report configuration
        """
        self.config = config or ReportConfig()
        logger.info("Initialized ReportManager")

    def generate_from_analyzer(
        self,
        analyzer: DocumentQualityAnalyzer,
        document_path: str,
        formats: list[str] = None,
    ) -> dict[str, Path]:
        """Generate reports from a DocumentQualityAnalyzer instance.

        Args:
            analyzer: DocumentQualityAnalyzer instance
            document_path: Path to the analyzed document
            formats: List of formats to generate (['json', 'html', 'pdf'])

        Returns:
            Dictionary mapping format names to output file paths
        """
        if formats is None:
            formats = ["json", "html"]

        # Convert analyzer data to AnalysisData
        analysis_data = self._analyzer_to_analysis_data(
            analyzer, document_path
        )

        return self.generate(analysis_data, formats)

    def generate(
        self,
        analysis_data: AnalysisData,
        formats: list[str] = None,
    ) -> dict[str, Path]:
        """Generate reports in specified formats.

        Args:
            analysis_data: Analysis data to export
            formats: List of formats to generate (['json', 'html', 'pdf'])

        Returns:
            Dictionary mapping format names to output file paths
        """
        if formats is None:
            formats = ["json", "html"]

        logger.info(f"Generating reports in formats: {formats}")

        results = {}

        for format_name in formats:
            if format_name not in self.EXPORTERS:
                logger.warning(f"Unknown format: {format_name}")
                continue

            try:
                exporter_class = self.EXPORTERS[format_name]
                exporter = exporter_class(self.config)
                output_path = exporter.write(analysis_data)
                results[format_name] = output_path
                logger.info(f"Generated {format_name} report: {output_path}")

            except Exception as e:
                logger.error(
                    f"Error generating {format_name} report: {e}"
                )
                results[format_name] = None

        return results

    def generate_all_formats(
        self, analysis_data: AnalysisData
    ) -> dict[str, Path]:
        """Generate reports in all available formats.

        Args:
            analysis_data: Analysis data to export

        Returns:
            Dictionary mapping format names to output file paths
        """
        return self.generate(
            analysis_data, list(self.EXPORTERS.keys())
        )

    @staticmethod
    def _analyzer_to_analysis_data(
        analyzer: DocumentQualityAnalyzer,
        document_path: str,
    ) -> AnalysisData:
        """Convert DocumentQualityAnalyzer to AnalysisData.

        Args:
            analyzer: DocumentQualityAnalyzer instance
            document_path: Path to the analyzed document

        Returns:
            AnalysisData instance
        """
        # Get summary information
        summary = analyzer.get_summary()

        # Create AnalysisData instance
        analysis_data = AnalysisData(
            document_path=document_path,
            language=analyzer.language,
            file_type=analyzer.file_type,
            quality_score=analyzer.get_quality_score(),
            total_issues=len(analyzer.all_issues),
            critical_count=len(analyzer.get_issues_by_severity("critical")),
            warning_count=len(analyzer.get_issues_by_severity("warning")),
            info_count=len(analyzer.get_issues_by_severity("info")),
            formatting_issues=analyzer.formatting_issues,
            language_issues=analyzer.language_issues,
            all_issues=analyzer.all_issues,
            issues_by_type=summary.get("by_type", {}),
            generated_at=datetime.now(),
        )

        return analysis_data

    def get_supported_formats(self) -> list[str]:
        """Get list of supported export formats.

        Returns:
            List of format names
        """
        return list(self.EXPORTERS.keys())

    def set_output_directory(self, output_dir: Path) -> None:
        """Set output directory for reports.

        Args:
            output_dir: Path to output directory
        """
        self.config.output_dir = Path(output_dir)
        logger.info(f"Set output directory to: {output_dir}")

    def set_config(self, config: ReportConfig) -> None:
        """Set report configuration.

        Args:
            config: ReportConfig instance
        """
        self.config = config
        logger.info("Updated report configuration")
