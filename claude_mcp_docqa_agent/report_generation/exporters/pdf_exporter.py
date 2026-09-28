"""PDF report exporter using reportlab."""

from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from claude_mcp_docqa_agent.report_generation.base import (
    AnalysisData,
    BaseReportGenerator,
    ReportConfig,
)
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class PDFReporter(BaseReportGenerator):
    """Generate PDF format reports with professional formatting."""

    def __init__(self, config: ReportConfig = None):
        """Initialize PDF reporter.

        Args:
            config: Report configuration
        """
        super().__init__(config)
        self.page_size = A4
        self.left_margin = 0.5 * inch
        self.right_margin = 0.5 * inch
        self.top_margin = 0.75 * inch
        self.bottom_margin = 0.75 * inch

    def generate(self, data: AnalysisData) -> bytes:
        """Generate PDF report.

        Args:
            data: Analysis data

        Returns:
            PDF as bytes
        """
        logger.info("Generating PDF report")

        # Create PDF in memory
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.right_margin,
            leftMargin=self.left_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            title=self.config.title,
            author=self.config.author,
        )

        # Build story (content)
        story = []

        # Add cover page
        story.extend(self._build_cover_page(data))
        story.append(PageBreak())

        # Add table of contents
        if self.config.include_toc:
            story.extend(self._build_toc(data))
            story.append(PageBreak())

        # Add summary section
        story.extend(self._build_summary(data))

        # Add critical issues section
        if data.critical_count > 0:
            story.append(PageBreak())
            story.extend(self._build_critical_issues(data))

        # Add detailed issues section
        if data.total_issues > 0:
            story.append(PageBreak())
            story.extend(self._build_detailed_issues(data))

        # Add statistics section
        if self.config.include_statistics:
            story.append(PageBreak())
            story.extend(self._build_statistics(data))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        logger.info(f"PDF report generated: {len(pdf_bytes)} bytes")

        return pdf_bytes

    def _get_styles(self) -> dict[str, Any]:
        """Get custom paragraph styles.

        Returns:
            Dictionary of styles
        """
        styles = getSampleStyleSheet()

        # Define custom styles
        styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=styles["Heading1"],
                fontSize=28,
                textColor=colors.HexColor("#007bff"),
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        styles.add(
            ParagraphStyle(
                name="CustomSubtitle",
                parent=styles["Normal"],
                fontSize=14,
                textColor=colors.HexColor("#666666"),
                spaceAfter=12,
                alignment=TA_CENTER,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#007bff"),
                spaceAfter=12,
                spaceBefore=12,
                fontName="Helvetica-Bold",
            )
        )

        styles.add(
            ParagraphStyle(
                name="IssueDescription",
                parent=styles["Normal"],
                fontSize=10,
                spaceAfter=6,
                textColor=colors.HexColor("#333333"),
            )
        )

        styles.add(
            ParagraphStyle(
                name="IssueRecommendation",
                parent=styles["Normal"],
                fontSize=9,
                spaceAfter=6,
                textColor=colors.HexColor("#28a745"),
                fontName="Helvetica-Oblique",
            )
        )

        return styles

    def _build_cover_page(self, data: AnalysisData) -> list[Any]:
        """Build cover page content.

        Args:
            data: Analysis data

        Returns:
            List of reportlab elements
        """
        styles = self._get_styles()
        elements = []

        # Spacer
        elements.append(Spacer(1, 2 * inch))

        # Title
        elements.append(
            Paragraph(self.config.title, styles["CustomTitle"])
        )

        # Subtitle
        elements.append(
            Paragraph(data.document_path.split("/")[-1], styles["CustomSubtitle"])
        )

        # Spacer
        elements.append(Spacer(1, 0.5 * inch))

        # Quality score box
        quality_grade = self._get_grade(data.quality_score)
        quality_text = (
            f"Quality Score: {data.quality_score:.1f}/100 ({quality_grade})"
        )
        elements.append(
            Paragraph(quality_text, styles["SectionHeading"])
        )

        # Spacer
        elements.append(Spacer(1, 0.3 * inch))

        # Summary information
        summary_data = [
            ["Metric", "Value"],
            ["Language", data.language.upper()],
            ["File Type", data.file_type.upper()],
            ["Total Issues", str(data.total_issues)],
            ["Critical", str(data.critical_count)],
            ["Warnings", str(data.warning_count)],
            ["Info", str(data.info_count)],
            ["Generated", data.generated_at.strftime("%Y-%m-%d %H:%M:%S")],
        ]

        summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )

        elements.append(summary_table)
        elements.append(Spacer(1, 1 * inch))

        # Footer
        elements.append(
            Paragraph(
                f"Report generated on {data.generated_at.strftime('%Y-%m-%d at %H:%M:%S')}",
                styles["Normal"],
            )
        )

        return elements

    def _build_toc(self, data: AnalysisData) -> list[Any]:
        """Build table of contents.

        Args:
            data: Analysis data

        Returns:
            List of reportlab elements
        """
        styles = self._get_styles()
        elements = []

        elements.append(
            Paragraph("Table of Contents", styles["SectionHeading"])
        )
        elements.append(Spacer(1, 0.2 * inch))

        toc_items = [
            "1. Summary",
        ]

        if data.critical_count > 0:
            toc_items.append(f"2. Critical Issues ({data.critical_count})")
        if data.total_issues > 0:
            toc_items.append("3. Detailed Issues")
        if self.config.include_statistics:
            toc_items.append("4. Statistics")

        for item in toc_items:
            elements.append(Paragraph(item, styles["Normal"]))

        return elements

    def _build_summary(self, data: AnalysisData) -> list[Any]:
        """Build summary section.

        Args:
            data: Analysis data

        Returns:
            List of reportlab elements
        """
        styles = self._get_styles()
        elements = []

        elements.append(Paragraph("Summary", styles["SectionHeading"]))
        elements.append(Spacer(1, 0.15 * inch))

        # Summary table
        summary_data = [
            ["Metric", "Count"],
            ["Total Issues", str(data.total_issues)],
            ["Critical", str(data.critical_count)],
            ["Warnings", str(data.warning_count)],
            ["Info", str(data.info_count)],
            ["Quality Score", f"{data.quality_score:.1f}/100"],
        ]

        summary_table = Table(
            summary_data, colWidths=[3 * inch, 1.5 * inch]
        )
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#f0f0f0")]),
                ]
            )
        )

        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _build_critical_issues(self, data: AnalysisData) -> list[Any]:
        """Build critical issues section.

        Args:
            data: Analysis data

        Returns:
            List of reportlab elements
        """
        styles = self._get_styles()
        elements = []

        elements.append(
            Paragraph("Critical Issues", styles["SectionHeading"])
        )
        elements.append(Spacer(1, 0.15 * inch))

        critical_issues = [
            issue for issue in data.all_issues
            if issue.severity == "critical"
        ]

        for idx, issue in enumerate(critical_issues[:10], 1):
            # Issue header
            header_text = (
                f"{idx}. {issue.issue_type} "
                f"(Page {issue.page_number}) - {issue.location_description}"
            )
            elements.append(Paragraph(header_text, styles["Heading3"]))

            # Issue description
            elements.append(
                Paragraph(
                    issue.issue_description,
                    styles["IssueDescription"]
                )
            )

            # Recommended fix
            fix_text = f"<b>Fix:</b> {issue.recommended_fix}"
            elements.append(
                Paragraph(fix_text, styles["IssueRecommendation"])
            )

            elements.append(Spacer(1, 0.1 * inch))

        return elements

    def _build_detailed_issues(self, data: AnalysisData) -> list[Any]:
        """Build detailed issues section.

        Args:
            data: Analysis data

        Returns:
            List of reportlab elements
        """
        styles = self._get_styles()
        elements = []

        elements.append(
            Paragraph("Detailed Issues", styles["SectionHeading"])
        )
        elements.append(Spacer(1, 0.15 * inch))

        # Create issues summary table
        issues_by_type = {}
        for issue in data.all_issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = {
                    "critical": 0,
                    "warning": 0,
                    "info": 0,
                }
            issues_by_type[issue.issue_type][issue.severity] += 1

        table_data = [["Issue Type", "Critical", "Warning", "Info", "Total"]]
        for issue_type, counts in sorted(issues_by_type.items()):
            total = sum(counts.values())
            table_data.append([
                issue_type,
                str(counts["critical"]),
                str(counts["warning"]),
                str(counts["info"]),
                str(total),
            ])

        issues_table = Table(
            table_data,
            colWidths=[2.5 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch],
        )
        issues_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#f0f0f0")]),
                ]
            )
        )

        elements.append(issues_table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _build_statistics(self, data: AnalysisData) -> list[Any]:
        """Build statistics section.

        Args:
            data: Analysis data

        Returns:
            List of reportlab elements
        """
        styles = self._get_styles()
        elements = []

        elements.append(
            Paragraph("Statistics", styles["SectionHeading"])
        )
        elements.append(Spacer(1, 0.15 * inch))

        # Statistics info
        stats_text = (
            f"<b>Document Analysis Summary:</b><br/>"
            f"Language: {data.language.upper()}<br/>"
            f"File Type: {data.file_type.upper()}<br/>"
            f"Total Issues: {data.total_issues}<br/>"
            f"Quality Score: {data.quality_score:.1f}/100<br/>"
            f"Report Generated: {data.generated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        elements.append(Paragraph(stats_text, styles["Normal"]))

        return elements

    @staticmethod
    def _get_grade(score: float) -> str:
        """Get letter grade for quality score.

        Args:
            score: Quality score (0-100)

        Returns:
            Letter grade
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _get_format_ext(self) -> str:
        """Get file extension for PDF format.

        Returns:
            'pdf'
        """
        return "pdf"
