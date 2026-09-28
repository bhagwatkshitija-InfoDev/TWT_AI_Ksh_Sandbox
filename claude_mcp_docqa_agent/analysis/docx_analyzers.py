"""DOCX-specific formatting analyzers."""

import uuid
from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class DOCXFontAnalyzer:
    """Analyze font consistency in DOCX documents."""

    MAX_UNIQUE_FONTS = 3
    MIN_FONT_VARIATION_PT = 1

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize font analyzer.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze font usage across document.

        Returns:
            List of font-related issues
        """
        self._check_font_consistency()
        return self.issues

    def _check_font_consistency(self) -> None:
        """Check for excessive font variety."""
        font_usage = self.content.get("font_usage", {})

        if not font_usage:
            return

        num_fonts = len(font_usage)

        if num_fonts > self.MAX_UNIQUE_FONTS:
            issue = FormattingIssue(
                id=str(uuid.uuid4()),
                page_number=1,
                issue_type="font_variety",
                severity="warning",
                location_description=f"Entire document",
                issue_description=f"Document uses {num_fonts} different fonts (recommended: {self.MAX_UNIQUE_FONTS} maximum)",
                recommended_fix=f"Limit font usage to {self.MAX_UNIQUE_FONTS} or fewer fonts. Current fonts: {', '.join(list(font_usage.keys())[:5])}",
            )
            self.issues.append(issue)
            logger.debug(f"Found font consistency issue: {num_fonts} fonts")

    def get_font_list(self) -> list[tuple[str, int]]:
        """Get sorted list of fonts by usage frequency.

        Returns:
            List of (font_name, count) tuples sorted by count
        """
        font_usage = self.content.get("font_usage", {})
        return sorted(font_usage.items(), key=lambda x: x[1], reverse=True)


class DOCXHeadingAnalyzer:
    """Analyze heading hierarchy in DOCX documents."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize heading analyzer.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze heading structure and hierarchy.

        Returns:
            List of heading-related issues
        """
        self._check_heading_hierarchy()
        self._check_heading_consistency()
        return self.issues

    def _check_heading_hierarchy(self) -> None:
        """Check for proper heading hierarchy (H1 -> H2 -> H3, not H1 -> H3)."""
        headings = self.content.get("headings", [])

        if len(headings) < 2:
            return

        seen_levels = set()
        for idx, heading in enumerate(headings):
            level = heading.get("level", 1)
            seen_levels.add(level)

            # Check for skipped levels (except first heading)
            if idx > 0:
                prev_level = headings[idx - 1].get("level", 1)
                if level > prev_level + 1:
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=1,
                        issue_type="heading_hierarchy",
                        severity="warning",
                        location_description=f"Heading: '{heading['text'][:50]}'",
                        issue_description=f"Heading level skipped from H{prev_level} to H{level}",
                        recommended_fix=f"Use H{prev_level + 1} instead of H{level}, or use H{prev_level} for the previous heading",
                    )
                    self.issues.append(issue)
                    logger.debug(f"Found heading hierarchy issue: H{prev_level} -> H{level}")

    def _check_heading_consistency(self) -> None:
        """Check for multiple H1 headings (should typically be one)."""
        headings = self.content.get("headings", [])

        h1_count = sum(1 for h in headings if h.get("level") == 1)

        if h1_count > 1:
            issue = FormattingIssue(
                id=str(uuid.uuid4()),
                page_number=1,
                issue_type="heading_consistency",
                severity="info",
                location_description="Document structure",
                issue_description=f"Document has {h1_count} H1 headings (typically should have 1)",
                recommended_fix="Consider using only one H1 as the main document title",
            )
            self.issues.append(issue)

    def get_heading_tree(self) -> list[dict[str, Any]]:
        """Get heading hierarchy as tree structure.

        Returns:
            List of headings with their hierarchy level
        """
        headings = self.content.get("headings", [])
        return [
            {"text": h["text"], "level": h.get("level", 1)} for h in headings
        ]


class DOCXTableAnalyzer:
    """Analyze table formatting in DOCX documents."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize table analyzer.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze table structures and formatting.

        Returns:
            List of table-related issues
        """
        self._check_table_consistency()
        self._check_table_structure()
        return self.issues

    def _check_table_consistency(self) -> None:
        """Check for tables with inconsistent column counts."""
        tables = self.content.get("tables", [])

        for table_idx, table in enumerate(tables):
            num_cols = table.get("num_cols", 0)
            rows = table.get("rows", [])

            for row_idx, row in enumerate(rows):
                if len(row) != num_cols:
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=1,
                        issue_type="table_structure",
                        severity="warning",
                        location_description=f"Table {table_idx + 1}, Row {row_idx + 1}",
                        issue_description=f"Row has {len(row)} cells but table header shows {num_cols} columns",
                        recommended_fix="Ensure all rows have the same number of cells as the header row",
                    )
                    self.issues.append(issue)
                    logger.debug(
                        f"Found table inconsistency: Table {table_idx}, Row {row_idx}"
                    )

    def _check_table_structure(self) -> None:
        """Check for empty tables or tables with missing content."""
        tables = self.content.get("tables", [])

        for table_idx, table in enumerate(tables):
            num_rows = table.get("num_rows", 0)
            rows = table.get("rows", [])

            if num_rows == 0 or not rows:
                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="table_structure",
                    severity="info",
                    location_description=f"Table {table_idx + 1}",
                    issue_description="Table appears to be empty or has no content",
                    recommended_fix="Ensure table has content or remove if unnecessary",
                )
                self.issues.append(issue)

    def get_table_stats(self) -> dict[str, Any]:
        """Get statistics about tables in document.

        Returns:
            Table statistics
        """
        tables = self.content.get("tables", [])
        return {
            "total_tables": len(tables),
            "avg_rows": (
                sum(t.get("num_rows", 0) for t in tables) / len(tables)
                if tables
                else 0
            ),
            "avg_cols": (
                sum(t.get("num_cols", 0) for t in tables) / len(tables)
                if tables
                else 0
            ),
        }


class DOCXListAnalyzer:
    """Analyze list and numbering formatting in DOCX documents."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize list analyzer.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze list structures and numbering.

        Returns:
            List of list-related issues
        """
        self._check_list_formatting()
        return self.issues

    def _check_list_formatting(self) -> None:
        """Check for list formatting issues.

        This is a basic implementation. Full implementation would
        parse list markers and indentation from paragraph styles.
        """
        paragraphs = self.content.get("paragraphs", [])

        list_items = [p for p in paragraphs if p.get("level", 0) > 0]

        if len(list_items) < 3:
            return

        # Check for inconsistent indentation levels
        levels = [p.get("level", 0) for p in list_items]

        max_jump = 0
        for i in range(1, len(levels)):
            jump = abs(levels[i] - levels[i - 1])
            max_jump = max(max_jump, jump)

        if max_jump > 1:
            issue = FormattingIssue(
                id=str(uuid.uuid4()),
                page_number=1,
                issue_type="list_formatting",
                severity="info",
                location_description="List structures in document",
                issue_description=f"Lists have inconsistent indentation levels (max jump: {max_jump})",
                recommended_fix="Use consistent list indentation hierarchy (H1 -> H2 -> H3, etc.)",
            )
            self.issues.append(issue)
            logger.debug("Found list formatting inconsistency")
