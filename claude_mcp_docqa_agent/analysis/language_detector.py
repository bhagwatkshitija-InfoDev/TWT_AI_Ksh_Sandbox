"""Language detection for documents."""

from typing import Optional

import langdetect
import textblob
from langdetect import detect, detect_langs

from claude_mcp_docqa_agent.config import get_settings
from claude_mcp_docqa_agent.errors.exceptions import LanguageDetectionError
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class LanguageDetector:
    """Detect document language using multiple methods."""

    def __init__(self) -> None:
        """Initialize language detector."""
        self.settings = get_settings()
        logger.info("Initialized language detector")

    def detect_language(
        self, text: str, min_length: int = 50
    ) -> dict[str, Optional[str]]:
        """Detect language from text.

        Uses langdetect as primary method, falls back to textblob.

        Args:
            text: Text to analyze
            min_length: Minimum text length for detection

        Returns:
            Dictionary with detected language, confidence, and method

        Raises:
            LanguageDetectionError: If detection fails
        """
        if not text or len(text) < min_length:
            logger.warning(f"Text too short for language detection: {len(text)} chars")
            raise LanguageDetectionError(
                f"Text too short for language detection (minimum {min_length} chars)"
            )

        # Try langdetect
        try:
            probabilities = detect_langs(text)

            if probabilities:
                lang_code = probabilities[0].lang
                confidence = probabilities[0].prob

                logger.info(f"Detected language: {lang_code} (confidence: {confidence:.2f})")

                return {
                    "language": lang_code,
                    "confidence": confidence,
                    "method": "langdetect",
                    "alternatives": [
                        {"lang": p.lang, "prob": p.prob} for p in probabilities[1:3]
                    ],
                }

        except langdetect.LangDetectException as e:
            logger.warning(f"langdetect failed: {e}, trying textblob fallback")

        # Fallback to textblob
        try:
            blob = textblob.TextBlob(text)
            lang_code = blob.detect_language()

            logger.info(f"Detected language (textblob fallback): {lang_code}")

            return {
                "language": lang_code,
                "confidence": 0.5,  # textblob doesn't return confidence
                "method": "textblob",
                "alternatives": [],
            }

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            raise LanguageDetectionError(f"Failed to detect language: {e}")

    def normalize_language_code(self, lang_code: str) -> str:
        """Normalize language code to supported format.

        Args:
            lang_code: Language code (e.g., 'zh', 'zh-cn', 'zh_CN')

        Returns:
            Normalized language code (e.g., 'zh_CN')
        """
        code_map = {
            "de": "de",
            "german": "de",
            "deu": "de",
            "zh": "zh_CN",
            "zh-cn": "zh_CN",
            "zh_cn": "zh_CN",
            "zh_hans": "zh_CN",
            "zhs": "zh_CN",
            "chi": "zh_CN",
            "en": "en",
            "english": "en",
            "eng": "en",
        }

        normalized = code_map.get(lang_code.lower(), lang_code.lower())
        return normalized

    def is_german(self, lang_code: str) -> bool:
        """Check if language code represents German.

        Args:
            lang_code: Language code

        Returns:
            True if German, False otherwise
        """
        return self.normalize_language_code(lang_code) == "de"

    def is_chinese(self, lang_code: str) -> bool:
        """Check if language code represents Simplified Chinese.

        Args:
            lang_code: Language code

        Returns:
            True if Simplified Chinese, False otherwise
        """
        return self.normalize_language_code(lang_code) == "zh_CN"

    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages.

        Returns:
            List of supported language codes
        """
        return self.settings.SUPPORTED_LANGUAGES

    def validate_detection(self, detection_result: dict) -> bool:
        """Validate if detection confidence meets minimum threshold.

        Args:
            detection_result: Result from detect_language()

        Returns:
            True if confidence meets threshold, False otherwise
        """
        confidence = detection_result.get("confidence", 0)
        min_confidence = self.settings.LANGUAGE_DETECTION_MIN_CONFIDENCE

        is_valid = confidence >= min_confidence

        if not is_valid:
            logger.warning(
                f"Detection confidence below threshold: {confidence:.2f} < {min_confidence}"
            )

        return is_valid
