"""Chinese language-specific rules engine."""

import re
import unicodedata
import uuid
from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ChineseRulesEngine:
    """Check Chinese language conventions."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize Chinese rules engine.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.full_text = document_content.get("full_text", "")
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Run all Chinese language checks.

        Returns:
            List of Chinese convention issues
        """
        logger.info("Starting Chinese language analysis")

        self._check_punctuation_marks()
        self._check_character_width()
        self._check_traditional_characters()
        self._check_spacing()

        logger.info(f"Found {len(self.issues)} Chinese language issues")
        return self.issues

    def _check_punctuation_marks(self) -> None:
        """Check for proper Chinese punctuation marks."""
        # Common English punctuation that should be Chinese
        punctuation_pairs = [
            (r",", "，", "comma", "English comma"),
            (r"\.", "。", "period", "English period"),
            (r"!", "！", "exclamation", "English exclamation mark"),
            (r"\?", "？", "question", "English question mark"),
            (r":", "：", "colon", "English colon"),
            (r";", "；", "semicolon", "English semicolon"),
        ]

        for english, chinese, issue_id, description in punctuation_pairs:
            # Look for English punctuation in Chinese text context
            pattern = rf"[一-鿿]{english}|{english}[一-鿿]"
            matches = re.finditer(pattern, self.full_text)

            for match in matches:
                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="chinese_punctuation",
                    severity="warning",
                    location_description=f'Text: "{match.group(0)}"',
                    issue_description=f"{description} ({english}) should be Chinese punctuation ({chinese})",
                    recommended_fix=f'Replace "{english}" with "{chinese}"',
                    context=self.full_text[
                        max(0, match.start() - 20) : match.end() + 20
                    ],
                )
                self.issues.append(issue)
                logger.debug(f"Found {description} in Chinese text")

    def _check_character_width(self) -> None:
        """Check for full-width vs half-width character consistency."""
        # Look for half-width ASCII characters in predominantly Chinese text
        for i, char in enumerate(self.full_text):
            if ord(char) < 128 and char.isdigit():  # Half-width digits
                # Check if surrounded by Chinese characters
                has_chinese_nearby = False
                for j in range(max(0, i - 5), min(len(self.full_text), i + 5)):
                    if "一" <= self.full_text[j] <= "鿿":
                        has_chinese_nearby = True
                        break

                if has_chinese_nearby:
                    full_width_digit = chr(ord(char) + 0xFEE0)
                    context = self.full_text[max(0, i - 20) : i + 20]

                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=1,
                        issue_type="chinese_character_width",
                        severity="info",
                        location_description=f'Character: "{char}"',
                        issue_description=f'Half-width digit "{char}" in Chinese text should be full-width "{full_width_digit}"',
                        recommended_fix=f'Replace half-width "{char}" with full-width "{full_width_digit}"',
                        context=context,
                    )
                    self.issues.append(issue)
                    logger.debug(f"Found half-width digit in Chinese context: {char}")
                    break  # Only report once per document

    def _check_traditional_characters(self) -> None:
        """Check for traditional Chinese characters (should use simplified)."""
        # Common traditional characters that should be simplified
        traditional_simplified = {
            "這": "这",
            "個": "个",
            "來": "来",
            "對": "对",
            "會": "会",
            "點": "点",
            "國": "国",
            "時": "时",
        }

        for traditional, simplified in traditional_simplified.items():
            if traditional in self.full_text:
                matches = re.finditer(re.escape(traditional), self.full_text)

                for match in matches:
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=1,
                        issue_type="chinese_traditional_chars",
                        severity="warning",
                        location_description=f'Character: "{traditional}"',
                        issue_description=f'Traditional Chinese character "{traditional}" should use simplified form "{simplified}"',
                        recommended_fix=f'Replace "{traditional}" with "{simplified}"',
                        context=self.full_text[
                            max(0, match.start() - 20) : match.end() + 20
                        ],
                    )
                    self.issues.append(issue)
                    logger.debug(f"Found traditional character: {traditional}")

    def _check_spacing(self) -> None:
        """Check Chinese spacing rules."""
        # Check for proper spacing between CJK and Latin characters
        # Pattern: CJK followed directly by Latin or vice versa
        pattern = r"([一-鿿])([a-zA-Z0-9])|([a-zA-Z0-9])([一-鿿])"

        matches = re.finditer(pattern, self.full_text)
        found_spacing_issue = False

        for match in matches:
            if not found_spacing_issue:
                context_start = max(0, match.start() - 20)
                context_end = min(len(self.full_text), match.end() + 20)
                context = self.full_text[context_start:context_end]

                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="chinese_spacing",
                    severity="info",
                    location_description=f'Text: "{context.strip()}"',
                    issue_description="Missing space between Chinese and Latin characters",
                    recommended_fix="Add space between Chinese characters and Latin characters for readability",
                    context=context,
                )
                self.issues.append(issue)
                logger.debug("Found CJK-Latin spacing issue")
                found_spacing_issue = True  # Report once

    def get_summary(self) -> dict[str, Any]:
        """Get summary of Chinese language issues.

        Returns:
            Summary statistics
        """
        return {
            "total_issues": len(self.issues),
            "punctuation": len(
                [i for i in self.issues if i.issue_type == "chinese_punctuation"]
            ),
            "character_width": len(
                [i for i in self.issues if i.issue_type == "chinese_character_width"]
            ),
            "traditional_chars": len(
                [i for i in self.issues if i.issue_type == "chinese_traditional_chars"]
            ),
            "spacing": len([i for i in self.issues if i.issue_type == "chinese_spacing"]),
        }
