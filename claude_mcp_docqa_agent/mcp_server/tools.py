"""MCP Tool definitions and handlers for Document QA Agent."""

import json
from typing import Any

from claude_mcp_docqa_agent.analysis.document_quality_analyzer import (
    DocumentQualityAnalyzer,
)
from claude_mcp_docqa_agent.document_processing.content_processor import (
    ContentProcessor,
)
from claude_mcp_docqa_agent.document_processing.metadata_extractor import (
    MetadataExtractor,
)
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


# Tool Definitions
TOOLS = [
    {
        "name": "upload_document",
        "description": "Upload and validate a document file (PDF or DOCX format)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file (PDF or DOCX)",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "process_document",
        "description": "Process document to extract content and detect language",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "analyze_formatting",
        "description": "Analyze document formatting (Phase 2): fonts, headings, tables, lists, images, cross-references",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "analyze_language",
        "description": "Analyze language-specific conventions (Phase 3): German or Chinese language rules",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "analyze_complete",
        "description": "Complete document quality analysis: formatting + language rules with quality score",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "get_document_summary",
        "description": "Get comprehensive document analysis summary with priority issues and quality score",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file",
                }
            },
            "required": ["file_path"],
        },
    },
]


# Tool Handlers
def upload_document(file_path: str) -> dict[str, Any]:
    """Upload and validate document."""
    logger.info(f"Uploading document: {file_path}")

    try:
        extractor = MetadataExtractor(file_path)
        metadata = extractor.extract_metadata()

        return {
            "status": "success",
            "filename": metadata["filename"],
            "file_type": metadata["file_type"],
            "file_size": metadata["file_size"],
            "message": f"Document uploaded successfully: {metadata['filename']}",
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return {"status": "error", "error": str(e)}


def process_document(file_path: str) -> dict[str, Any]:
    """Process document."""
    logger.info(f"Processing document: {file_path}")

    try:
        processor = ContentProcessor(file_path)
        result = processor.process_document()

        return {
            "status": "success",
            "file_type": result.get("file_type"),
            "language": result.get("language"),
            "language_confidence": result.get("language_detection", {}).get("confidence", 0),
            "text_sample": result.get("full_text", "")[:300],
            "message": f"Document processed: {result.get('file_type')} detected as {result.get('language')}",
        }

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return {"status": "error", "error": str(e)}


def analyze_formatting(file_path: str) -> dict[str, Any]:
    """Analyze formatting."""
    logger.info(f"Analyzing formatting: {file_path}")

    try:
        processor = ContentProcessor(file_path)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        analyzer.analyze_formatting_only()

        summary = analyzer.get_summary()

        return {
            "status": "success",
            "total_formatting_issues": len(analyzer.formatting_issues),
            "critical": summary["critical"],
            "warning": summary["warning"],
            "info": summary["info"],
            "by_type": summary["by_type"],
            "message": f"Formatting analysis complete: {len(analyzer.formatting_issues)} issues found",
        }

    except Exception as e:
        logger.error(f"Formatting analysis failed: {e}")
        return {"status": "error", "error": str(e)}


def analyze_language(file_path: str) -> dict[str, Any]:
    """Analyze language rules."""
    logger.info(f"Analyzing language: {file_path}")

    try:
        processor = ContentProcessor(file_path)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        analyzer.analyze_language_only()

        return {
            "status": "success",
            "language": analyzer.language,
            "total_language_issues": len(analyzer.language_issues),
            "message": f"Language analysis complete for {analyzer.language}: {len(analyzer.language_issues)} issues found",
        }

    except Exception as e:
        logger.error(f"Language analysis failed: {e}")
        return {"status": "error", "error": str(e)}


def analyze_complete(file_path: str) -> dict[str, Any]:
    """Complete analysis."""
    logger.info(f"Analyzing complete: {file_path}")

    try:
        processor = ContentProcessor(file_path)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        return {
            "status": "success",
            "language": analyzer.language,
            "file_type": analyzer.file_type,
            "total_issues": len(result["all_issues"]),
            "formatting_issues": len(result["formatting_issues"]),
            "language_issues": len(result["language_issues"]),
            "quality_score": round(analyzer.get_quality_score(), 1),
            "severity_distribution": result["summary"]["severity_distribution"],
            "message": f"Complete analysis: {len(result['all_issues'])} total issues, quality score {analyzer.get_quality_score():.1f}/100",
        }

    except Exception as e:
        logger.error(f"Complete analysis failed: {e}")
        return {"status": "error", "error": str(e)}


def get_document_summary(file_path: str) -> dict[str, Any]:
    """Get document summary."""
    logger.info(f"Getting summary: {file_path}")

    try:
        processor = ContentProcessor(file_path)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        priority_issues = analyzer.get_priority_issues(top_n=5)

        return {
            "status": "success",
            "language": analyzer.language,
            "file_type": analyzer.file_type,
            "quality_score": round(analyzer.get_quality_score(), 1),
            "total_issues": len(result["all_issues"]),
            "severity_distribution": result["summary"]["severity_distribution"],
            "issues_by_type": result["summary"]["by_type"],
            "priority_issues": [
                {
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.issue_description,
                    "fix": issue.recommended_fix,
                }
                for issue in priority_issues
            ],
            "message": f"Summary: {analyzer.language} document, quality {analyzer.get_quality_score():.1f}/100",
        }

    except Exception as e:
        logger.error(f"Summary failed: {e}")
        return {"status": "error", "error": str(e)}


# Tool dispatcher
TOOL_HANDLERS = {
    "upload_document": upload_document,
    "process_document": process_document,
    "analyze_formatting": analyze_formatting,
    "analyze_language": analyze_language,
    "analyze_complete": analyze_complete,
    "get_document_summary": get_document_summary,
}


def handle_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Handle a tool call and return JSON result."""
    logger.info(f"Handling tool: {tool_name}")

    if tool_name not in TOOL_HANDLERS:
        return json.dumps({"status": "error", "error": f"Unknown tool: {tool_name}"})

    try:
        handler = TOOL_HANDLERS[tool_name]
        result = handler(**tool_input)
        return json.dumps(result)

    except Exception as e:
        logger.error(f"Tool handler error: {e}")
        return json.dumps({"status": "error", "error": str(e)})
