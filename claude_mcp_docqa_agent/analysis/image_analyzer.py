"""Image and caption analysis."""

import uuid
from typing import Any

from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingIssue
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ImageAnalyzer:
    """Analyze images and captions in documents."""

    MIN_CAPTION_LENGTH = 10

    def __init__(self, document_content: dict[str, Any]) -> None:
        """Initialize image analyzer.

        Args:
            document_content: Structured document content
        """
        self.content = document_content
        self.issues: list[FormattingIssue] = []

    def analyze(self) -> list[FormattingIssue]:
        """Analyze images and their captions.

        Returns:
            List of image-related issues
        """
        self._check_image_captions()
        return self.issues

    def _check_image_captions(self) -> None:
        """Check for missing or inadequate image captions.

        In a full implementation, would:
        - Extract image references from document
        - Check for adjacent caption paragraphs
        - Validate caption content length and quality
        """
        # Note: Actual image extraction requires specialized libraries
        # For now, provide framework for when image support is added

        paragraphs = self.content.get("paragraphs", [])
        if not paragraphs:
            return

        # Look for patterns suggesting images
        image_keywords = ["image", "figure", "fig.", "illustration", "picture"]
        potential_images = []

        for idx, para in enumerate(paragraphs):
            text_lower = para.get("text", "").lower()
            if any(keyword in text_lower for keyword in image_keywords):
                potential_images.append((idx, para))

        # Check if these have captions
        for idx, para in potential_images:
            next_para = paragraphs[idx + 1] if idx + 1 < len(paragraphs) else None

            if not next_para:
                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="image_caption",
                    severity="warning",
                    location_description=f"After: '{para['text'][:40]}'",
                    issue_description="Image reference found but no caption text follows",
                    recommended_fix="Add a descriptive caption after the image reference",
                )
                self.issues.append(issue)
                logger.debug("Found image without caption")

            elif len(next_para.get("text", "")) < self.MIN_CAPTION_LENGTH:
                issue = FormattingIssue(
                    id=str(uuid.uuid4()),
                    page_number=1,
                    issue_type="image_caption",
                    severity="info",
                    location_description=f"Caption: '{next_para['text'][:40]}'",
                    issue_description=f"Image caption is too short ({len(next_para['text'])} chars, minimum recommended: {self.MIN_CAPTION_LENGTH})",
                    recommended_fix=f"Expand caption to at least {self.MIN_CAPTION_LENGTH} characters with descriptive text",
                )
                self.issues.append(issue)
                logger.debug("Found short image caption")

    def get_image_count(self) -> int:
        """Estimate number of images in document.

        Returns:
            Estimated image count
        """
        paragraphs = self.content.get("paragraphs", [])
        image_keywords = ["image", "figure", "fig.", "illustration"]

        count = 0
        for para in paragraphs:
            text_lower = para.get("text", "").lower()
            if any(keyword in text_lower for keyword in image_keywords):
                count += 1

        return count
