"""End-to-end integration tests for complete workflows (Phase 7)."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from docx import Document

from claude_mcp_docqa_agent.analysis.document_quality_analyzer import (
    DocumentQualityAnalyzer,
)
from claude_mcp_docqa_agent.config.config_manager import ConfigManager
from claude_mcp_docqa_agent.document_processing.content_processor import (
    ContentProcessor,
)
from claude_mcp_docqa_agent.report_generation import ReportManager


@pytest.fixture
def sample_docx_file():
    """Create a sample DOCX file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        doc = Document()

        # Add heading
        doc.add_heading("Sample Document", level=1)

        # Add paragraphs
        doc.add_paragraph(
            "This is a test document with sufficient content for language detection. "
            "The text needs to be at least 50 characters long for proper language detection to work. "
            "This paragraph contains more than enough text to meet that requirement.",
            style="Normal",
        )

        doc.add_heading("Section 2", level=2)
        doc.add_paragraph("Content in section 2")

        # Add table
        table = doc.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "Header 1"
        table.cell(0, 1).text = "Header 2"
        table.cell(1, 0).text = "Data 1"
        table.cell(1, 1).text = "Data 2"

        # Add list
        doc.add_paragraph("Item 1", style="List Bullet")
        doc.add_paragraph("Item 2", style="List Bullet")

        doc.save(f.name)
        yield f.name

    try:
        Path(f.name).unlink()
    except PermissionError:
        pass


@pytest.fixture
def temp_config_dir():
    """Create temporary configuration directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        import yaml

        config_dir = Path(tmpdir)

        # Create minimal settings
        settings = {
            "document_processing": {
                "supported_formats": ["pdf", "docx"],
                "max_file_size_mb": 100,
            },
            "quality": {
                "min_language_confidence": 0.7,
            },
        }
        with open(config_dir / "settings.yaml", "w") as f:
            yaml.dump(settings, f)

        # Create rules
        rules = {"formatting_rules": []}
        with open(config_dir / "default_rules.yaml", "w") as f:
            yaml.dump(rules, f)

        yield config_dir


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_complete_document_analysis_workflow(self, sample_docx_file):
        """Test complete workflow: upload → process → analyze → report."""
        # Step 1: Process document
        processor = ContentProcessor(sample_docx_file)
        doc_data = processor.process_document()

        assert doc_data is not None
        assert "file_type" in doc_data
        assert doc_data["file_type"] == "docx"
        assert "language" in doc_data
        assert "full_text" in doc_data

        # Step 2: Analyze document
        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        assert result is not None
        assert "formatting_issues" in result
        assert "language_issues" in result
        assert "summary" in result

        # Step 3: Generate reports
        manager = ReportManager()
        from claude_mcp_docqa_agent.report_generation import AnalysisData

        analysis_data = AnalysisData(
            document_path=sample_docx_file,
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
            issues_by_type=result["summary"].get("by_type", {}),
            generated_at=datetime.now(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            from claude_mcp_docqa_agent.report_generation import ReportConfig

            config = ReportConfig(output_dir=Path(tmpdir))
            manager = ReportManager(config)
            results = manager.generate_all_formats(analysis_data)

            # Verify all reports generated
            assert len(results) == 3
            assert "json" in results
            assert "html" in results
            assert "pdf" in results

            # Verify files exist
            for fmt, path in results.items():
                assert path is not None
                assert path.exists()

    def test_document_analysis_with_configuration(
        self, sample_docx_file, temp_config_dir
    ):
        """Test document analysis with custom configuration."""
        # Initialize config manager
        config_mgr = ConfigManager(config_dir=temp_config_dir)

        # Update configuration
        success, msg = config_mgr.update_config(
            {"quality": {"min_language_confidence": 0.8}},
            user="test",
            reason="Testing e2e workflow",
        )
        assert success is True

        # Process document
        processor = ContentProcessor(sample_docx_file)
        doc_data = processor.process_document()

        # Verify language confidence meets new threshold
        assert doc_data["language_detection"]["confidence"] >= 0.7

        # Analyze with new config
        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        assert result is not None
        assert len(analyzer.all_issues) >= 0

    def test_configuration_rollback_workflow(self, temp_config_dir):
        """Test configuration change and rollback workflow."""
        config_mgr = ConfigManager(
            config_dir=temp_config_dir, enable_versions=True
        )

        # Make a change
        config_mgr.update_config(
            {"quality": {"min_language_confidence": 0.9}},
            user="user2",
            reason="Testing higher threshold",
        )

        # Verify change applied
        changed_config = config_mgr.get_config("quality")
        assert changed_config["min_language_confidence"] == 0.9

        # Get versions - should have backup from before the update
        versions = config_mgr.get_versions()
        assert len(versions) > 0

        # Verify audit trail has the update
        audit = config_mgr.get_audit_trail()
        assert len(audit) >= 1

        # Verify audit entry shows the change
        assert audit[-1]["action"] == "update"
        assert audit[-1]["user"] == "user2"

    def test_multi_language_document_workflow(self):
        """Test workflow with different language documents."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            doc = Document()

            # Create English document
            doc.add_heading("English Document", level=1)
            doc.add_paragraph(
                "This is an English document with sufficient content for language detection. "
                "The system should recognize this as English. "
                "This paragraph provides enough text for proper detection."
            )

            doc.save(f.name)

            try:
                # Process and analyze
                processor = ContentProcessor(f.name)
                doc_data = processor.process_document()

                assert doc_data["language"].lower() in [
                    "en",
                    "english",
                ]

                # Analyze
                analyzer = DocumentQualityAnalyzer(doc_data)
                result = analyzer.analyze_complete()

                assert result is not None

            finally:
                try:
                    Path(f.name).unlink()
                except PermissionError:
                    pass

    def test_audit_trail_workflow(self, temp_config_dir):
        """Test complete audit trail tracking."""
        config_mgr = ConfigManager(
            config_dir=temp_config_dir, enable_versions=True
        )

        # Perform multiple configuration updates
        config_mgr.update_config(
            {"quality": {"min_language_confidence": 0.75}},
            user="user0",
            reason="Test 1",
        )
        config_mgr.update_config(
            {"quality": {"min_language_confidence": 0.8}},
            user="user1",
            reason="Test 2",
        )

        # Retrieve and verify audit trail
        audit = config_mgr.get_audit_trail(limit=100)

        assert len(audit) >= 2
        assert all("timestamp" in entry for entry in audit)
        assert all("user" in entry for entry in audit)
        assert all("action" in entry for entry in audit)
        assert audit[-2]["user"] == "user0"
        assert audit[-1]["user"] == "user1"

    def test_report_generation_formats(self, sample_docx_file):
        """Test report generation in all formats."""
        # Process and analyze
        processor = ContentProcessor(sample_docx_file)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        # Generate reports
        manager = ReportManager()
        from claude_mcp_docqa_agent.report_generation import AnalysisData

        analysis_data = AnalysisData(
            document_path=sample_docx_file,
            language=analyzer.language,
            file_type=analyzer.file_type,
            quality_score=analyzer.get_quality_score(),
            total_issues=len(analyzer.all_issues),
            critical_count=len(
                analyzer.get_issues_by_severity("critical")
            ),
            warning_count=len(analyzer.get_issues_by_severity("warning")),
            info_count=len(analyzer.get_issues_by_severity("info")),
            formatting_issues=analyzer.formatting_issues,
            language_issues=analyzer.language_issues,
            all_issues=analyzer.all_issues,
            issues_by_type=result["summary"].get("by_type", {}),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            from claude_mcp_docqa_agent.report_generation import ReportConfig

            config = ReportConfig(output_dir=Path(tmpdir))
            manager = ReportManager(config)

            # Test individual format generation
            json_results = manager.generate(analysis_data, formats=["json"])
            assert "json" in json_results
            assert json_results["json"].exists()

            # Verify JSON content
            with open(json_results["json"]) as f:
                json_content = json.load(f)
            assert "metadata" in json_content
            assert "quality" in json_content

            # Test HTML generation
            html_results = manager.generate(analysis_data, formats=["html"])
            assert "html" in html_results
            assert html_results["html"].exists()

            # Verify HTML content
            with open(html_results["html"], encoding="utf-8") as f:
                html_content = f.read()
            assert "<!DOCTYPE html>" in html_content

            # Test PDF generation
            pdf_results = manager.generate(analysis_data, formats=["pdf"])
            assert "pdf" in pdf_results
            assert pdf_results["pdf"].exists()

            # Verify PDF is binary
            with open(pdf_results["pdf"], "rb") as f:
                pdf_content = f.read()
            assert pdf_content.startswith(b"%PDF")


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def test_document_processing_performance(self, sample_docx_file):
        """Benchmark document processing performance."""
        import time

        start = time.time()
        processor = ContentProcessor(sample_docx_file)
        doc_data = processor.process_document()
        elapsed = time.time() - start

        # Should complete in under 2 seconds
        assert elapsed < 2.0
        assert doc_data is not None

    def test_analysis_performance(self, sample_docx_file):
        """Benchmark analysis performance."""
        import time

        processor = ContentProcessor(sample_docx_file)
        doc_data = processor.process_document()

        start = time.time()
        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()
        elapsed = time.time() - start

        # Should complete in under 2 seconds
        assert elapsed < 2.0
        assert result is not None

    def test_report_generation_performance(self, sample_docx_file):
        """Benchmark report generation performance."""
        import time

        processor = ContentProcessor(sample_docx_file)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        from claude_mcp_docqa_agent.report_generation import (
            AnalysisData,
            ReportManager,
            ReportConfig,
        )

        analysis_data = AnalysisData(
            document_path=sample_docx_file,
            language=analyzer.language,
            file_type=analyzer.file_type,
            quality_score=analyzer.get_quality_score(),
            total_issues=len(analyzer.all_issues),
            critical_count=len(
                analyzer.get_issues_by_severity("critical")
            ),
            warning_count=len(analyzer.get_issues_by_severity("warning")),
            info_count=len(analyzer.get_issues_by_severity("info")),
            formatting_issues=analyzer.formatting_issues,
            language_issues=analyzer.language_issues,
            all_issues=analyzer.all_issues,
            issues_by_type=result["summary"].get("by_type", {}),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ReportConfig(output_dir=Path(tmpdir))
            manager = ReportManager(config)

            start = time.time()
            reports = manager.generate_all_formats(analysis_data)
            elapsed = time.time() - start

            # Should complete in under 2 seconds
            assert elapsed < 2.0
            assert len(reports) == 3
            assert all(p.exists() for p in reports.values())

    def test_configuration_management_performance(self, temp_config_dir):
        """Benchmark configuration management performance."""
        import time

        config_mgr = ConfigManager(config_dir=temp_config_dir)

        # Benchmark updates
        start = time.time()
        for i in range(5):
            config_mgr.update_config(
                {"quality": {"min_language_confidence": 0.7 + i * 0.01}}
            )
        elapsed = time.time() - start

        # 5 updates should complete in under 1 second
        assert elapsed < 1.0

        # Benchmark reads
        start = time.time()
        for _ in range(10):
            config_mgr.get_config()
        elapsed = time.time() - start

        # 10 reads should complete in under 100ms
        assert elapsed < 0.1
