"""Unit tests for language detection."""

import pytest

from claude_mcp_docqa_agent.analysis.language_detector import LanguageDetector
from claude_mcp_docqa_agent.errors.exceptions import LanguageDetectionError


@pytest.fixture
def detector():
    """Create a language detector instance."""
    return LanguageDetector()


class TestLanguageDetector:
    """Test language detection functionality."""

    def test_detector_initialization(self, detector):
        """Test detector initialization."""
        assert detector is not None
        assert hasattr(detector, "detect_language")

    def test_detect_german_text(self, detector):
        """Test detection of German text."""
        german_text = """
        Dies ist ein Test document für die Spracherkennung.
        Der Text enthält deutsche Wörter und Sätze.
        Dies sollte als Deutsch erkannt werden.
        """

        result = detector.detect_language(german_text)

        assert "language" in result
        assert "confidence" in result
        assert "method" in result
        assert result["language"] == "de"
        assert result["confidence"] > 0

    def test_detect_chinese_text(self, detector):
        """Test detection of Chinese text."""
        chinese_text = """
        这是一个测试文档用于语言检测。
        文本包含中文单词和句子。
        这应该被识别为中文。
        这是中文测试的另一部分。
        """

        result = detector.detect_language(chinese_text)

        assert "language" in result
        assert "confidence" in result
        assert result["language"] in ["zh", "zh_CN", "zh-cn"]

    def test_detect_english_text(self, detector):
        """Test detection of English text."""
        english_text = """
        This is a test document for language detection.
        The text contains English words and sentences.
        This should be recognized as English.
        """

        result = detector.detect_language(english_text)

        assert "language" in result
        assert result["language"] in ["en", "english"]

    def test_detect_language_too_short(self, detector):
        """Test detection fails with too short text."""
        short_text = "Hallo"

        with pytest.raises(LanguageDetectionError):
            detector.detect_language(short_text, min_length=100)

    def test_detect_language_empty(self, detector):
        """Test detection fails with empty text."""
        with pytest.raises(LanguageDetectionError):
            detector.detect_language("")

    def test_normalize_language_code(self, detector):
        """Test language code normalization."""
        assert detector.normalize_language_code("de") == "de"
        assert detector.normalize_language_code("german") == "de"
        assert detector.normalize_language_code("deu") == "de"

        assert detector.normalize_language_code("zh") == "zh_CN"
        assert detector.normalize_language_code("zh-cn") == "zh_CN"
        assert detector.normalize_language_code("zh_cn") == "zh_CN"

        assert detector.normalize_language_code("en") == "en"

    def test_is_german(self, detector):
        """Test German language check."""
        assert detector.is_german("de") is True
        assert detector.is_german("deu") is True
        assert detector.is_german("german") is True
        assert detector.is_german("en") is False

    def test_is_chinese(self, detector):
        """Test Chinese language check."""
        assert detector.is_chinese("zh_CN") is True
        assert detector.is_chinese("zh") is True
        assert detector.is_chinese("zh-cn") is True
        assert detector.is_chinese("de") is False

    def test_get_supported_languages(self, detector):
        """Test getting supported languages."""
        languages = detector.get_supported_languages()

        assert isinstance(languages, list)
        assert len(languages) > 0

    def test_validate_detection(self, detector):
        """Test detection validation."""
        high_confidence_result = {
            "language": "de",
            "confidence": 0.95,
            "method": "langdetect",
        }

        assert detector.validate_detection(high_confidence_result) is True

        low_confidence_result = {
            "language": "de",
            "confidence": 0.3,
            "method": "langdetect",
        }

        assert detector.validate_detection(low_confidence_result) is False

    def test_detection_alternatives(self, detector):
        """Test getting alternative language detections."""
        german_text = """
        Dies ist ein Test document für die Spracherkennung.
        Der Text enthält deutsche Wörter und Sätze.
        Dies sollte als Deutsch erkannt werden.
        """

        result = detector.detect_language(german_text)

        # Should have alternatives in result
        assert "alternatives" in result
