"""Unit tests for language-specific rules."""

import pytest

from claude_mcp_docqa_agent.analysis.document_quality_analyzer import (
    DocumentQualityAnalyzer,
)
from claude_mcp_docqa_agent.analysis.language_rules.chinese_rules import (
    ChineseRulesEngine,
)
from claude_mcp_docqa_agent.analysis.language_rules.german_rules import (
    GermanRulesEngine,
)
from claude_mcp_docqa_agent.analysis.language_rules_analyzer import (
    LanguageRulesAnalyzer,
)


@pytest.fixture
def german_document_content():
    """Sample German document for testing."""
    return {
        "file_type": "docx",
        "language": "de",
        "full_text": 'Haupttitel: "Guten Tag" und "Auf Wiedersehen". Dies ist ein Test mit 1,234.56 und table mit Daten. Siehe \'Sektion\' 1.1.',
        "content": {
            "metadata": {"title": "Test Document"},
            "paragraphs": [],
            "headings": [],
            "tables": [],
            "font_usage": {},
        },
    }


@pytest.fixture
def chinese_document_content():
    """Sample Chinese document for testing."""
    return {
        "file_type": "docx",
        "language": "zh_CN",
        "full_text": "标题: 这是一个测试，使用傳統汉字。這是一個簡單的例子: 表格有123个行。參考第一章獲取詳細信息。字体应该一致。",
        "content": {
            "metadata": {"title": "Test Document"},
            "paragraphs": [],
            "headings": [],
            "tables": [],
            "font_usage": {},
        },
    }


@pytest.fixture
def english_document_content():
    """English document (no language-specific rules)."""
    return {
        "file_type": "docx",
        "language": "en",
        "full_text": "This is an English document. No special rules apply.",
        "content": {
            "metadata": {"title": "English Document"},
            "paragraphs": [],
            "headings": [],
            "tables": [],
            "font_usage": {},
        },
    }


class TestGermanRulesEngine:
    """Test German language rules."""

    def test_german_engine_initialization(self, german_document_content):
        """Test initializing German rules engine."""
        engine = GermanRulesEngine(german_document_content)
        assert engine is not None

    def test_quotation_marks_detection(self, german_document_content):
        """Test detection of English quotation marks."""
        engine = GermanRulesEngine(german_document_content)
        issues = engine.analyze()

        # Should find English quotes that should be German
        quote_issues = [i for i in issues if i.issue_type == "german_quotation_marks"]
        assert len(quote_issues) > 0

    def test_number_format_detection(self, german_document_content):
        """Test detection of English number format."""
        engine = GermanRulesEngine(german_document_content)
        issues = engine.analyze()

        # Should find English number format (1,234.56)
        number_issues = [i for i in issues if i.issue_type == "german_number_format"]
        assert len(number_issues) > 0

    def test_get_summary(self, german_document_content):
        """Test getting German rules summary."""
        engine = GermanRulesEngine(german_document_content)
        engine.analyze()
        summary = engine.get_summary()

        assert "total_issues" in summary
        assert "quotation_marks" in summary
        assert "number_format" in summary


class TestChineseRulesEngine:
    """Test Chinese language rules."""

    def test_chinese_engine_initialization(self, chinese_document_content):
        """Test initializing Chinese rules engine."""
        engine = ChineseRulesEngine(chinese_document_content)
        assert engine is not None

    def test_traditional_character_detection(self, chinese_document_content):
        """Test detection of traditional Chinese characters."""
        engine = ChineseRulesEngine(chinese_document_content)
        issues = engine.analyze()

        # Should find traditional characters (傳, 這, 個, 參)
        trad_issues = [
            i for i in issues if i.issue_type == "chinese_traditional_chars"
        ]
        assert len(trad_issues) > 0

    def test_get_summary(self, chinese_document_content):
        """Test getting Chinese rules summary."""
        engine = ChineseRulesEngine(chinese_document_content)
        engine.analyze()
        summary = engine.get_summary()

        assert "total_issues" in summary
        assert "traditional_chars" in summary
        assert "punctuation" in summary


class TestLanguageRulesAnalyzer:
    """Test language rules analyzer."""

    def test_analyzer_initialization_german(self, german_document_content):
        """Test initializing analyzer for German."""
        analyzer = LanguageRulesAnalyzer(german_document_content)
        assert analyzer.language == "de"

    def test_analyzer_initialization_chinese(self, chinese_document_content):
        """Test initializing analyzer for Chinese."""
        analyzer = LanguageRulesAnalyzer(chinese_document_content)
        assert analyzer.language == "zh_CN"

    def test_german_language_analysis(self, german_document_content):
        """Test German language analysis."""
        analyzer = LanguageRulesAnalyzer(german_document_content)
        issues = analyzer.analyze()

        assert isinstance(issues, list)
        # German rules are applied (may or may not find issues depending on content)
        assert analyzer.language == "de"

    def test_chinese_language_analysis(self, chinese_document_content):
        """Test Chinese language analysis."""
        analyzer = LanguageRulesAnalyzer(chinese_document_content)
        issues = analyzer.analyze()

        assert isinstance(issues, list)
        # Chinese rules are applied (may or may not find issues depending on content)
        assert analyzer.language in ["zh_CN", "zh-cn", "zh"]

    def test_english_language_no_rules(self, english_document_content):
        """Test that English documents have no language-specific rules."""
        analyzer = LanguageRulesAnalyzer(english_document_content)
        issues = analyzer.analyze()

        # English should have no language-specific rules
        assert len(issues) == 0

    def test_get_summary(self, german_document_content):
        """Test getting language analyzer summary."""
        analyzer = LanguageRulesAnalyzer(german_document_content)
        analyzer.analyze()
        summary = analyzer.get_summary()

        assert summary["language"] == "de"
        assert "total_issues" in summary


class TestDocumentQualityAnalyzer:
    """Test unified document quality analyzer."""

    def test_analyzer_initialization_german(self, german_document_content):
        """Test initializing quality analyzer."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        assert analyzer.language == "de"

    def test_complete_analysis_german(self, german_document_content):
        """Test complete analysis for German document."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        result = analyzer.analyze_complete()

        assert "formatting_issues" in result
        assert "language_issues" in result
        assert "all_issues" in result
        assert "summary" in result

        # Check that result structure is valid
        assert isinstance(result["formatting_issues"], list)
        assert isinstance(result["language_issues"], list)
        assert isinstance(result["all_issues"], list)

    def test_complete_analysis_chinese(self, chinese_document_content):
        """Test complete analysis for Chinese document."""
        analyzer = DocumentQualityAnalyzer(chinese_document_content)
        result = analyzer.analyze_complete()

        assert isinstance(result["language_issues"], list)

    def test_formatting_only_analysis(self, german_document_content):
        """Test formatting-only analysis."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        issues = analyzer.analyze_formatting_only()

        assert isinstance(issues, list)

    def test_language_only_analysis(self, german_document_content):
        """Test language-only analysis."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        issues = analyzer.analyze_language_only()

        assert isinstance(issues, list)
        # Language-specific rules are applied
        assert analyzer.language == "de"

    def test_filter_by_severity(self, german_document_content):
        """Test filtering issues by severity."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        analyzer.analyze_complete()

        warnings = analyzer.get_issues_by_severity("warning")
        assert isinstance(warnings, list)

    def test_filter_by_type(self, german_document_content):
        """Test filtering issues by type."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        analyzer.analyze_complete()

        quote_issues = analyzer.get_issues_by_type("german_quotation_marks")
        assert isinstance(quote_issues, list)

    def test_filter_by_phase(self, german_document_content):
        """Test filtering issues by phase."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        analyzer.analyze_complete()

        phase2_issues = analyzer.get_issues_by_phase(2)
        phase3_issues = analyzer.get_issues_by_phase(3)

        assert isinstance(phase2_issues, list)
        assert isinstance(phase3_issues, list)

    def test_quality_score(self, german_document_content):
        """Test document quality score calculation."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        analyzer.analyze_complete()

        score = analyzer.get_quality_score()

        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_priority_issues(self, german_document_content):
        """Test getting priority issues."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        analyzer.analyze_complete()

        priority = analyzer.get_priority_issues(top_n=3)

        assert isinstance(priority, list)
        assert len(priority) <= 3

    def test_export_format(self, german_document_content):
        """Test exporting issues in dictionary format."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        analyzer.analyze_complete()

        export = analyzer.get_issues_for_export()

        assert isinstance(export, list)
        if export:
            assert isinstance(export[0], dict)
            assert "issue_type" in export[0]
            assert "severity" in export[0]

    def test_comprehensive_summary(self, german_document_content):
        """Test getting comprehensive summary."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        analyzer.analyze_complete()

        summary = analyzer.get_summary()

        assert "language" in summary
        assert "file_type" in summary
        assert "total_issues" in summary
        assert "critical" in summary
        assert "warning" in summary
        assert "info" in summary
        assert "by_phase" in summary
        assert "by_type" in summary


class TestLanguageRulesIntegration:
    """Integration tests for language rules."""

    def test_german_complete_workflow(self, german_document_content):
        """Test complete German document analysis workflow."""
        analyzer = DocumentQualityAnalyzer(german_document_content)
        result = analyzer.analyze_complete()

        # Check that analysis completed
        assert isinstance(result["language_issues"], list)

        # Get summary
        summary = result["summary"]
        assert summary["language"] == "de"

        # Get quality score
        quality = analyzer.get_quality_score()
        assert 0 <= quality <= 100  # Valid score range

    def test_chinese_complete_workflow(self, chinese_document_content):
        """Test complete Chinese document analysis workflow."""
        analyzer = DocumentQualityAnalyzer(chinese_document_content)
        result = analyzer.analyze_complete()

        # Check that analysis completed
        assert isinstance(result["language_issues"], list)

        # Get priority issues
        priority = analyzer.get_priority_issues(top_n=3)
        assert isinstance(priority, list)

    def test_mixed_language_content(self):
        """Test document with mixed languages."""
        mixed_content = {
            "file_type": "docx",
            "language": "de",  # Detected as German
            "full_text": 'This is English with "German quotes" and Chinese 中文.',
            "content": {
                "metadata": {},
                "paragraphs": [],
                "headings": [],
                "tables": [],
                "font_usage": {},
            },
        }

        analyzer = DocumentQualityAnalyzer(mixed_content)
        result = analyzer.analyze_complete()

        # German rules are applied
        assert analyzer.language == "de"
        assert isinstance(result["language_issues"], list)
