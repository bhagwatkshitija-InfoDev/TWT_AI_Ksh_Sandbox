#!/usr/bin/env python3
"""Generate comprehensive analysis reports for TWT_AI_Ksh_Sandbox repository."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load configuration for KSH Sandbox
load_dotenv(".env.ksh-sandbox")

from claude_mcp_docqa_agent.config import get_settings
from claude_mcp_docqa_agent.database.db_manager import get_db_manager
from claude_mcp_docqa_agent.utils.logger import get_logger
from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.document_quality_analyzer import DocumentQualityAnalyzer
from claude_mcp_docqa_agent.report_generation.manager import ReportManager
from claude_mcp_docqa_agent.analysis.language_detector import LanguageDetector

logger = get_logger(__name__)


def analyze_document(file_path: Path, settings) -> dict:
    """Analyze a single document and return results.

    Args:
        file_path: Path to the document to analyze
        settings: Application settings

    Returns:
        Dictionary with analysis results
    """
    try:
        logger.info(f"Analyzing document: {file_path}")

        # Handle different file types
        document_data = None

        if file_path.suffix.lower() == ".md":
            # Handle Markdown files
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            detector = LanguageDetector()
            try:
                lang_detection = detector.detect_language(content[:1000])
                language = lang_detection.get("language", "en")
            except Exception as e:
                logger.warning(f"Language detection failed, using default: {e}")
                lang_detection = {"language": "en", "confidence": 0.0}
                language = "en"

            document_data = {
                "file_path": str(file_path),
                "file_type": "markdown",
                "language": language,
                "language_detection": lang_detection,
                "content": {"text": content},
                "full_text": content,
            }
        else:
            # Handle PDF and DOCX files
            processor = ContentProcessor(str(file_path))
            document_data = processor.process_document()

        if not document_data:
            logger.warning(f"Could not process document: {file_path}")
            return None

        # Run quality analysis
        analyzer = DocumentQualityAnalyzer(document_data)
        analysis_result = analyzer.analyze_complete()

        logger.info(f"Analysis complete for {file_path.name}: "
                   f"{len(analysis_result.get('all_issues', []))} issues found")

        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "document_data": document_data,
            "analysis_result": analysis_result
        }

    except Exception as e:
        logger.error(f"Error analyzing document {file_path}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def generate_reports(analysis_results: list[dict], settings) -> None:
    """Generate analysis reports.

    Args:
        analysis_results: List of analysis results
        settings: Application settings
    """
    if not analysis_results:
        logger.warning("No analysis results to generate reports from")
        return

    try:
        # Ensure report directory exists
        settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)

        report_manager = ReportManager(str(settings.REPORT_DIR))

        # Generate consolidated report
        logger.info("Generating consolidated analysis report")

        # Prepare summary data
        total_issues = sum(
            len(r["analysis_result"].get("all_issues", []))
            for r in analysis_results if r
        )
        total_documents = len([r for r in analysis_results if r])

        logger.info(f"Report Summary: {total_documents} documents, {total_issues} total issues")

        # Generate reports for each document
        for result in analysis_results:
            if not result:
                continue

            doc_name = result["file_name"]
            logger.info(f"Generating report for {doc_name}")

            # Generate HTML report
            try:
                html_path = settings.REPORT_DIR / f"{Path(doc_name).stem}_analysis.html"
                logger.debug(f"Creating HTML report: {html_path}")
            except Exception as e:
                logger.error(f"Error generating HTML report: {e}")

            # Generate JSON report
            try:
                import json
                json_path = settings.REPORT_DIR / f"{Path(doc_name).stem}_analysis.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "file": doc_name,
                        "language": result["document_data"].get("language", "unknown"),
                        "file_type": result["document_data"].get("file_type", "unknown"),
                        "issues": [
                            {
                                "type": issue.get("type", "unknown"),
                                "severity": issue.get("severity", "info"),
                                "message": issue.get("message", ""),
                                "location": issue.get("location", "")
                            }
                            for issue in result["analysis_result"].get("all_issues", [])
                        ]
                    }, f, indent=2, ensure_ascii=False)
                logger.info(f"JSON report created: {json_path}")
            except Exception as e:
                logger.error(f"Error generating JSON report: {e}")

        # Generate index report
        index_path = settings.REPORT_DIR / "index.html"
        try:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Document QA Analysis Report - TWT_AI_Ksh_Sandbox</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .document {{ margin: 20px 0; padding: 10px; border-left: 4px solid #007bff; }}
        .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
        .stat {{ background: #e9ecef; padding: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>Document QA Analysis Report</h1>
    <h2>TWT_AI_Ksh_Sandbox Repository</h2>

    <div class="summary">
        <h3>Analysis Summary</h3>
        <div class="stats">
            <div class="stat"><strong>Documents Analyzed:</strong> {total_documents}</div>
            <div class="stat"><strong>Total Issues:</strong> {total_issues}</div>
        </div>
    </div>

    <h3>Analyzed Documents</h3>
    <ul>
""")
                for result in analysis_results:
                    if result:
                        doc_name = result["file_name"]
                        issues_count = len(result["analysis_result"].get("all_issues", []))
                        json_report = f"{Path(doc_name).stem}_analysis.json"
                        f.write(f'        <li><a href="{json_report}">{doc_name}</a> ({issues_count} issues)</li>\n')

                f.write("""
    </ul>
</body>
</html>
""")
            logger.info(f"Index report created: {index_path}")
        except Exception as e:
            logger.error(f"Error generating index report: {e}")

        print(f"\n✅ Reports generated in: {settings.REPORT_DIR}")
        print(f"   - Total documents: {total_documents}")
        print(f"   - Total issues: {total_issues}")
        print(f"   - Index: {index_path}")

    except Exception as e:
        logger.error(f"Error generating reports: {e}")


def main():
    """Main entry point for KSH Sandbox report generation."""
    try:
        # Initialize settings with KSH Sandbox config
        settings = get_settings()
        logger.info("Document QA Agent configured for KSH Sandbox report generation")

        # Initialize database
        db_manager = get_db_manager()
        logger.info("Database initialized")

        # Get source repository path
        source_repo = Path(os.getenv("SOURCE_REPO_PATH", "D:/TWT_AI/TWT_AI_Ksh_Sandbox"))

        # Find documents in the repository
        docs_to_analyze = []
        supported_formats = tuple(f".{fmt}" for fmt in settings.SUPPORTED_FORMATS)

        for file_path in source_repo.rglob("*"):
            if file_path.suffix.lower() in supported_formats:
                docs_to_analyze.append(file_path)

        if not docs_to_analyze:
            logger.warning("No documents found in repository")
            print("No documents found in the repository")
            return 1

        logger.info(f"Found {len(docs_to_analyze)} documents to analyze")
        print(f"\nAnalyzing {len(docs_to_analyze)} documents from {source_repo}...\n")

        # Analyze each document
        analysis_results = []
        for doc_path in docs_to_analyze:
            result = analyze_document(doc_path, settings)
            if result:
                analysis_results.append(result)
                print(f"  ✓ {doc_path.name}")

        # Generate reports
        print("\nGenerating reports...")
        generate_reports(analysis_results, settings)

        return 0

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
