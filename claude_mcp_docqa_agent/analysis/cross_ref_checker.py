"""Cross-reference validation."""

import re
import uuid
from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class CrossReferenceChecker:
    """Check cross-references in documents."""

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize cross-reference checker.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []
        self._build_reference_map()

    def _build_reference_map(self) -> None:
        """Build map of referenceable elements (headings, tables, figures)."""
        self.headings_map = {}
        self.tables_map = {}
        self.figures_map = {}

        # Map heading texts for reference checking
        headings = self.content.get("headings", [])
        for idx, heading in enumerate(headings):
            self.headings_map[heading["text"]] = idx + 1

        # Map table positions
        tables = self.content.get("tables", [])
        for idx, table in enumerate(tables):
            self.tables_map[f"Table {idx + 1}"] = idx + 1

        logger.debug(
            f"Built reference map: {len(self.headings_map)} headings, {len(self.tables_map)} tables"
        )

    def analyze(self) -> list[FormattingIssue]:
        """Analyze cross-references in document.

        Returns:
            List of cross-reference issues
        """
        self._check_reference_patterns()
        self._check_forward_references()
        return self.issues

    def _check_reference_patterns(self) -> None:
        """Check for common reference patterns."""
        full_text = self.content.get("full_text", "")

        # Look for "See Section X", "Refer to Chapter Y" patterns
        patterns = [
            r"see section (\d+\.?[a-z]*)",  # See Section 1, Section 1.1, etc
            r"see chapter (\d+)",  # See Chapter 2
            r"refer to (?:section|chapter|heading) ['\"]?([^'\"]+)['\"]?",  # Refer to "Heading Title"
            r"table (\d+)",  # Table 1, Table 2, etc
            r"figure (\d+)",  # Figure 1, Figure 2, etc
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                self._validate_reference(match.group(0), match.group(1))

    def _check_forward_references(self) -> None:
        """Check for forward references that may not be correct."""
        paragraphs = self.content.get("paragraphs", [])
        headings = self.content.get("headings", [])

        # Build list of valid heading numbers
        valid_section_numbers = set()
        for heading in headings:
            # Extract section numbers like "1", "2.1", etc
            text = heading["text"]
            match = re.match(r"^(\d+(?:\.\d+)*)", text)
            if match:
                valid_section_numbers.add(match.group(1))

        # Check for invalid section references in text
        for para in paragraphs:
            text = para.get("text", "")
            # Look for "Section X.Y" patterns
            matches = re.finditer(r"Section (\d+(?:\.\d+)?)", text, re.IGNORECASE)
            for match in matches:
                section_num = match.group(1)
                if section_num not in valid_section_numbers:
                    issue = FormattingIssue(
                        id=str(uuid.uuid4()),
                        page_number=1,
                        issue_type="cross_reference",
                        severity="warning",
                        location_description=f"Text: '{text[:60]}'",
                        issue_description=f"Reference to 'Section {section_num}' but this section does not exist",
                        recommended_fix=f"Verify section number or update reference to valid section",
                        context=text[:100],
                    )
                    self.issues.append(issue)
                    logger.debug(f"Found broken cross-reference: Section {section_num}")

    def _validate_reference(self, full_match: str, reference: str) -> None:
        """Validate a single reference.

        Args:
            full_match: Full matched text
            reference: Extracted reference string
        """
        # Check if reference exists in our maps
        if reference in self.headings_map:
            return  # Valid reference

        if f"Table {reference}" in self.tables_map:
            return  # Valid table reference

        # Check if it's a numeric pattern that might be valid
        if re.match(r"^\d+$", reference):
            return  # Assume numeric references might be valid

        # Otherwise, flag as potentially invalid
        issue = FormattingIssue(
            id=str(uuid.uuid4()),
            page_number=1,
            issue_type="cross_reference",
            severity="info",
            location_description=f"Reference in text",
            issue_description=f"Reference '{full_match}' may not resolve correctly",
            recommended_fix="Verify the referenced element exists or update the reference",
        )
        self.issues.append(issue)

    def get_reference_summary(self) -> dict[str, Any]:
        """Get summary of references found.

        Returns:
            Summary of reference usage
        """
        return {
            "total_headings": len(self.headings_map),
            "total_tables": len(self.tables_map),
            "total_issues": len(self.issues),
            "broken_references": len(
                [i for i in self.issues if i.issue_type == "cross_reference"]
            ),
        }
