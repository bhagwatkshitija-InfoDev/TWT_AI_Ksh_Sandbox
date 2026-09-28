"""German language-specific rules engine."""

import re
import uuid
from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class GermanRulesEngine:
    """Check German language conventions."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize German rules engine.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.full_text = document_content.get("full_text", "")
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Run all German language checks.

        Returns:
            List of German convention issues
        """
        logger.info("Starting German language analysis")

        self._check_quotation_marks()
        self._check_number_formatting()
        self._check_capitalization()
        self._check_umlaut_usage()
        self._check_spacing()

        logger.info(f"Found {len(self.issues)} German language issues")
        return self.issues

    def _check_quotation_marks(self) -> None:
        """Check for proper German quotation marks."""
        # English quotes that should be German
        english_quotes = [
            (r'"([^"]*)"', '"', '"', "English double quotes"),
            (r"'([^']*)'", "'", "'", "English single quotes"),
        ]

        for pattern, open_quote, close_quote, desc in english_quotes:
            matches = re.finditer(pattern, self.full_text)
            for match in matches:
                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="german_quotation_marks",
                    severity="warning",
                    location_description=f'Text: "{match.group(0)[:50]}"',
                    issue_description=f'{desc} ({open_quote}{close_quote}) used instead of German quotation marks („“)',
                    recommended_fix=f'Replace {open_quote}{match.group(1)}{close_quote} with „{match.group(1)}“',
                    context=match.group(0),
                )
                self.issues.append(issue)
                logger.debug(f"Found {desc}: {match.group(0)[:40]}")

    def _check_number_formatting(self) -> None:
        """Check for proper German number formatting."""
        # English-style thousands (1,234.56) should be German (1.234,56)
        english_numbers = re.finditer(r"\d+,\d{3}(\.\d+)?", self.full_text)

        for match in english_numbers:
            number = match.group(0)
            # Convert to German format
            german_number = number.replace(",", "_").replace(".", ",").replace("_", ".")

            issue = FormattingIssue(
                id=str(uuid.uuid4()),
                page_number=1,
                issue_type="german_number_format",
                severity="warning",
                location_description=f"Number: {number}",
                issue_description=f"Number uses English format ({number}) instead of German format",
                recommended_fix=f"Use German number format: {german_number}",
                context=number,
            )
            self.issues.append(issue)
            logger.debug(f"Found English number format: {number}")

    def _check_capitalization(self) -> None:
        """Check for German noun capitalization."""
        # Look for common nouns that should be capitalized
        common_nouns = [
            ("document", "Dokument"),
            ("table", "Tabelle"),
            ("chapter", "Kapitel"),
            ("section", "Abschnitt"),
            ("figure", "Abbildung"),
            ("example", "Beispiel"),
        ]

        for english, german in common_nouns:
            # Look for lowercase versions that should be capitalized
            pattern = rf"\b{english}\b"
            matches = re.finditer(pattern, self.full_text, re.IGNORECASE)

            for match in matches:
                if match.group(0).islower():
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=1,
                        issue_type="german_capitalization",
                        severity="info",
                        location_description=f'Word: "{match.group(0)}"',
                        issue_description=f'Word "{match.group(0)}" appears in German text and should follow German capitalization rules',
                        recommended_fix=f"Use German equivalent or capitalize: '{german}' or '{match.group(0).capitalize()}'",
                        context=self.full_text[max(0, match.start() - 20) : match.end() + 20],
                    )
                    self.issues.append(issue)
                    logger.debug(f"Found capitalization issue: {match.group(0)}")

    def _check_umlaut_usage(self) -> None:
        """Check for proper German umlaut usage."""
        # Look for umlaut substitutes (ae, oe, ue) that should use umlauts
        umlaut_patterns = [
            (r"\b[aA]e(?=\w)", "ä/Ä", "ae"),
            (r"\b[oO]e(?=\w)", "ö/Ö", "oe"),
            (r"\b[uU]e(?=\w)", "ü/Ü", "ue"),
        ]

        for pattern, proper, substitute in umlaut_patterns:
            matches = re.finditer(pattern, self.full_text)

            for match in matches:
                word_start = max(0, match.start() - 10)
                word_end = min(len(self.full_text), match.end() + 10)
                context = self.full_text[word_start:word_end]

                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="german_umlauts",
                    severity="info",
                    location_description=f'Text: "{context.strip()}"',
                    issue_description=f'Umlaut substitute "{substitute}" should use proper character: {proper}',
                    recommended_fix=f'Replace "{substitute}" with proper German umlaut: {proper}',
                    context=context,
                )
                self.issues.append(issue)
                logger.debug(f"Found umlaut issue: {match.group(0)}")

    def _check_spacing(self) -> None:
        """Check German spacing rules."""
        # German style: no space before punctuation, space after
        violations = [
            (r"\s+[,!?;:]", "Space before punctuation", "punctuation"),
            (r"[,!?;:](?=[^\s])", "No space after punctuation", "spacing"),
        ]

        for pattern, description, violation_type in violations:
            matches = re.finditer(pattern, self.full_text)

            for match in matches:
                word_start = max(0, match.start() - 10)
                word_end = min(len(self.full_text), match.end() + 10)
                context = self.full_text[word_start:word_end]

                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="german_spacing",
                    severity="info",
                    location_description=f'Text: "{context.strip()}"',
                    issue_description=f"German spacing rule violation: {description}",
                    recommended_fix="Ensure proper spacing: no space before punctuation, space after",
                    context=context,
                )
                self.issues.append(issue)
                logger.debug(f"Found spacing issue: {description}")

    def get_summary(self) -> dict[str, Any]:
        """Get summary of German language issues.

        Returns:
            Summary statistics
        """
        return {
            "total_issues": len(self.issues),
            "quotation_marks": len(
                [i for i in self.issues if i.issue_type == "german_quotation_marks"]
            ),
            "number_format": len(
                [i for i in self.issues if i.issue_type == "german_number_format"]
            ),
            "capitalization": len(
                [i for i in self.issues if i.issue_type == "german_capitalization"]
            ),
            "umlauts": len([i for i in self.issues if i.issue_type == "german_umlauts"]),
            "spacing": len([i for i in self.issues if i.issue_type == "german_spacing"]),
        }
