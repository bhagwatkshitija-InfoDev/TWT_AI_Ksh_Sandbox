"""Unit tests for report generation module (Phase 5)."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.report_generation.base import (
    AnalysisData,
    BaseReportGenerator,
    ReportConfig,
)
from claude_mcp_docqa_agent.report_generation.exporters.json_exporter import (
    JSONReporter,
)
from claude_mcp_docqa_agent.report_generation.exporters.html_exporter import (
    HTMLReporter,
)
from claude_mcp_docqa_agent.report_generation.exporters.pdf_exporter import (
    PDFReporter,
)
from claude_mcp_docqa_agent.report_generation.manager import ReportManager


@pytest.fixture
def sample_issues():
    """Create sample FormattingIssue objects."""
    issues = [
        FormattingIssue(
            id="issue_001",
            page_number=1,
            issue_type="Font Consistency",
            severity="critical",
            location_description="Header in section 1",
            issue_description="Font size inconsistent with style guide",
            recommended_fix="Change font size to 14pt",
            coordinates={"x0": 10, "y0": 20, "x1": 100, "y1": 30},
            context="Arial 12pt found instead of Arial 14pt",
        ),
        FormattingIssue(
            id="issue_002",
            page_number=2,
            issue_type="Heading Hierarchy",
            severity="warning",
            location_description="Section 2.1",
            issue_description="Missing intermediate heading level",
            recommended_fix="Add Heading 2 between Heading 1 and Heading 3",
            context="H1 followed directly by H3",
        ),
        FormattingIssue(
            id="issue_003",
            page_number=3,
            issue_type="Table Formatting",
            severity="info",
            location_description="Table 1",
            issue_description="Table missing header row emphasis",
            recommended_fix="Apply bold formatting to header row",
            context="Header row not formatted distinctly",
        ),
    ]
    return issues


@pytest.fixture
def sample_analysis_data(sample_issues):
    """Create sample AnalysisData."""
    return AnalysisData(
        document_path="/path/to/document.docx",
        language="de",
        file_type="docx",
        quality_score=75.5,
        total_issues=len(sample_issues),
        critical_count=1,
        warning_count=1,
        info_count=1,
        formatting_issues=sample_issues[:2],
        language_issues=sample_issues[2:],
        all_issues=sample_issues,
        issues_by_type={
            "Font Consistency": 1,
            "Heading Hierarchy": 1,
            "Table Formatting": 1,
        },
        generated_at=datetime(2026, 9, 28, 10, 30, 0),
    )


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestReportConfig:
    """Test ReportConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ReportConfig()
        assert config.title == "Document Quality Report"
        assert config.author == "Claude Document QA Agent"
        assert config.include_toc is True
        assert config.include_statistics is True
        assert config.theme == "light"

    def test_custom_config(self, temp_output_dir):
        """Test custom configuration."""
        config = ReportConfig(
            title="Custom Report",
            author="Test Author",
            theme="dark",
            output_dir=temp_output_dir,
        )
        assert config.title == "Custom Report"
        assert config.author == "Test Author"
        assert config.theme == "dark"
        assert config.output_dir == temp_output_dir


class TestAnalysisData:
    """Test AnalysisData."""

    def test_analysis_data_creation(self, sample_analysis_data):
        """Test creating AnalysisData."""
        assert sample_analysis_data.language == "de"
        assert sample_analysis_data.file_type == "docx"
        assert sample_analysis_data.quality_score == 75.5
        assert sample_analysis_data.total_issues == 3

    def test_analysis_data_to_dict(self, sample_analysis_data):
        """Test converting AnalysisData to dictionary."""
        data_dict = sample_analysis_data.to_dict()
        assert data_dict["language"] == "de"
        assert data_dict["file_type"] == "docx"
        assert data_dict["quality_score"] == 75.5
        assert data_dict["total_issues"] == 3
        assert "generated_at" in data_dict

    def test_analysis_data_auto_generated_at(self, sample_issues):
        """Test that generated_at is auto-set."""
        data = AnalysisData(
            document_path="test.docx",
            language="en",
            file_type="docx",
            quality_score=80.0,
            total_issues=0,
            critical_count=0,
            warning_count=0,
            info_count=0,
            formatting_issues=[],
            language_issues=[],
            all_issues=[],
            issues_by_type={},
        )
        assert data.generated_at is not None
        assert isinstance(data.generated_at, datetime)


class TestJSONReporter:
    """Test JSON report generation."""

    def test_json_reporter_creation(self, temp_output_dir):
        """Test creating JSONReporter."""
        config = ReportConfig(output_dir=temp_output_dir)
        reporter = JSONReporter(config)
        assert reporter is not None
        assert reporter.config.output_dir == temp_output_dir

    def test_json_generation(self, sample_analysis_data):
        """Test JSON report generation."""
        reporter = JSONReporter()
        json_str = reporter.generate(sample_analysis_data)

        # Parse and validate JSON
        data = json.loads(json_str)
        assert "metadata" in data
        assert "quality" in data
        assert "formatting_issues" in data
        assert "language_issues" in data
        assert data["quality"]["score"] == 75.5
        assert data["quality"]["total_issues"] == 3

    def test_json_metadata(self, sample_analysis_data):
        """Test JSON report metadata."""
        reporter = JSONReporter()
        json_str = reporter.generate(sample_analysis_data)
        data = json.loads(json_str)

        assert data["metadata"]["title"] == "Document Quality Report"
        assert data["metadata"]["document"]["language"] == "de"
        assert data["metadata"]["document"]["file_type"] == "docx"

    def test_json_write(self, sample_analysis_data, temp_output_dir):
        """Test writing JSON report to file."""
        config = ReportConfig(output_dir=temp_output_dir)
        reporter = JSONReporter(config)
        output_path = reporter.write(sample_analysis_data)

        assert output_path.exists()
        assert output_path.suffix == ".json"

        # Validate written JSON
        with open(output_path) as f:
            data = json.load(f)
        assert "metadata" in data
        assert "quality" in data

    def test_json_issues_format(self, sample_analysis_data):
        """Test JSON issue formatting."""
        reporter = JSONReporter()
        json_str = reporter.generate(sample_analysis_data)
        data = json.loads(json_str)

        # Check formatting issues
        assert len(data["formatting_issues"]) == 2
        assert data["formatting_issues"][0]["id"] == "issue_001"
        assert data["formatting_issues"][0]["severity"] == "critical"
        assert "coordinates" in data["formatting_issues"][0]

        # Check language issues
        assert len(data["language_issues"]) == 1
        assert data["language_issues"][0]["id"] == "issue_003"


class TestHTMLReporter:
    """Test HTML report generation."""

    def test_html_reporter_creation(self, temp_output_dir):
        """Test creating HTMLReporter."""
        config = ReportConfig(output_dir=temp_output_dir)
        reporter = HTMLReporter(config)
        assert reporter is not None

    def test_html_generation(self, sample_analysis_data):
        """Test HTML report generation."""
        reporter = HTMLReporter()
        html_str = reporter.generate(sample_analysis_data)

        assert isinstance(html_str, str)
        assert "<!DOCTYPE html>" in html_str
        assert "<title>" in html_str
        assert "Document Quality Report" in html_str

    def test_html_content_includes_quality_score(self, sample_analysis_data):
        """Test HTML includes quality score."""
        reporter = HTMLReporter()
        html_str = reporter.generate(sample_analysis_data)

        assert "75.5" in html_str
        assert "C" in html_str  # Grade for 75.5
        assert "3" in html_str  # Total issues

    def test_html_write(self, sample_analysis_data, temp_output_dir):
        """Test writing HTML report to file."""
        config = ReportConfig(output_dir=temp_output_dir)
        reporter = HTMLReporter(config)
        output_path = reporter.write(sample_analysis_data)

        assert output_path.exists()
        assert output_path.suffix == ".html"

        # Validate written HTML
        with open(output_path, encoding="utf-8") as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content

    def test_html_grade_calculation(self):
        """Test grade calculation for different scores."""
        reporter = HTMLReporter()

        assert reporter._get_grade(95) == "A"
        assert reporter._get_grade(85) == "B"
        assert reporter._get_grade(75) == "C"
        assert reporter._get_grade(65) == "D"
        assert reporter._get_grade(55) == "F"

    def test_html_color_mapping(self):
        """Test color mapping for quality scores."""
        reporter = HTMLReporter()

        assert "#28a745" in reporter._get_score_color(95)  # Green
        assert "#5cb85c" in reporter._get_score_color(85)  # Light green
        assert "#ffc107" in reporter._get_score_color(75)  # Yellow
        assert "#fd7e14" in reporter._get_score_color(65)  # Orange
        assert "#dc3545" in reporter._get_score_color(55)  # Red

    def test_html_issue_grouping(self, sample_analysis_data):
        """Test issue grouping by type and severity."""
        reporter = HTMLReporter()
        context = reporter._prepare_context(sample_analysis_data)

        assert "issues" in context
        assert "by_type" in context["issues"]
        assert "by_severity" in context["issues"]


class TestPDFReporter:
    """Test PDF report generation."""

    def test_pdf_reporter_creation(self, temp_output_dir):
        """Test creating PDFReporter."""
        config = ReportConfig(output_dir=temp_output_dir)
        reporter = PDFReporter(config)
        assert reporter is not None

    def test_pdf_generation(self, sample_analysis_data):
        """Test PDF report generation."""
        reporter = PDFReporter()
        pdf_bytes = reporter.generate(sample_analysis_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")  # PDF magic number

    def test_pdf_write(self, sample_analysis_data, temp_output_dir):
        """Test writing PDF report to file."""
        config = ReportConfig(output_dir=temp_output_dir)
        reporter = PDFReporter(config)
        output_path = reporter.write(sample_analysis_data)

        assert output_path.exists()
        assert output_path.suffix == ".pdf"

        # Validate PDF content
        with open(output_path, "rb") as f:
            content = f.read()
        assert content.startswith(b"%PDF")

    def test_pdf_grade_calculation(self):
        """Test PDF grade calculation."""
        reporter = PDFReporter()

        assert reporter._get_grade(95) == "A"
        assert reporter._get_grade(75) == "C"
        assert reporter._get_grade(55) == "F"


class TestReportManager:
    """Test ReportManager."""

    def test_manager_creation(self, temp_output_dir):
        """Test creating ReportManager."""
        config = ReportConfig(output_dir=temp_output_dir)
        manager = ReportManager(config)
        assert manager is not None

    def test_supported_formats(self):
        """Test supported formats."""
        manager = ReportManager()
        formats = manager.get_supported_formats()

        assert "json" in formats
        assert "html" in formats
        assert "pdf" in formats

    def test_generate_single_format(self, sample_analysis_data, temp_output_dir):
        """Test generating single format."""
        config = ReportConfig(output_dir=temp_output_dir)
        manager = ReportManager(config)
        results = manager.generate(sample_analysis_data, formats=["json"])

        assert "json" in results
        assert results["json"].exists()

    def test_generate_multiple_formats(
        self, sample_analysis_data, temp_output_dir
    ):
        """Test generating multiple formats."""
        config = ReportConfig(output_dir=temp_output_dir)
        manager = ReportManager(config)
        results = manager.generate(
            sample_analysis_data, formats=["json", "html"]
        )

        assert "json" in results
        assert "html" in results
        assert results["json"].exists()
        assert results["html"].exists()

    def test_generate_all_formats(self, sample_analysis_data, temp_output_dir):
        """Test generating all formats."""
        config = ReportConfig(output_dir=temp_output_dir)
        manager = ReportManager(config)
        results = manager.generate_all_formats(sample_analysis_data)

        assert len(results) == 3
        assert all(path.exists() for path in results.values())

    def test_set_output_directory(self, temp_output_dir):
        """Test setting output directory."""
        manager = ReportManager()
        manager.set_output_directory(temp_output_dir)

        assert manager.config.output_dir == temp_output_dir

    def test_set_config(self, temp_output_dir):
        """Test setting configuration."""
        config = ReportConfig(
            title="Custom Report", output_dir=temp_output_dir
        )
        manager = ReportManager()
        manager.set_config(config)

        assert manager.config.title == "Custom Report"

    def test_generate_with_invalid_format(
        self, sample_analysis_data, temp_output_dir
    ):
        """Test generating with invalid format."""
        config = ReportConfig(output_dir=temp_output_dir)
        manager = ReportManager(config)
        results = manager.generate(
            sample_analysis_data, formats=["json", "invalid_format"]
        )

        assert "json" in results
        assert results["json"].exists()
        # Invalid formats are logged but not included in results
        # This is by design - we don't include None values in the results


class TestReportFilenaming:
    """Test report filename generation."""

    def test_filename_pattern(self, temp_output_dir, sample_analysis_data):
        """Test report filename pattern."""
        config = ReportConfig(output_dir=temp_output_dir)
        reporter = JSONReporter(config)
        output_path = reporter.write(sample_analysis_data)

        filename = output_path.name
        # Format: YYYYMMDD_HHMMSS_document_name_report.ext
        assert "_report.json" in filename
        assert filename.startswith("2026")

    def test_output_directory_creation(self, sample_analysis_data):
        """Test output directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "report" / "path"
            config = ReportConfig(output_dir=output_dir)
            reporter = JSONReporter(config)
            output_path = reporter.write(sample_analysis_data)

            assert output_path.parent.exists()
            assert output_path.exists()
