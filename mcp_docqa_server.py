#!/usr/bin/env python3
"""Document QA Agent MCP Server using current MCP SDK."""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.document_quality_analyzer import DocumentQualityAnalyzer
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize server
server = Server("document-qa-agent")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="analyze_document",
            description="Complete document quality analysis (formatting + language rules)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file (PDF, DOCX, or Markdown)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="process_document",
            description="Process document to extract content and detect language",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_document_summary",
            description="Get comprehensive document analysis summary with priority issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file"
                    }
                },
                "required": ["file_path"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name}")

    try:
        if name == "analyze_document":
            return await analyze_document(arguments)
        elif name == "process_document":
            return await process_document(arguments)
        elif name == "get_document_summary":
            return await get_document_summary(arguments)
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e), "tool": name}))]


async def analyze_document(args: dict[str, Any]) -> list[TextContent]:
    """Analyze document."""
    file_path = args.get("file_path")
    if not file_path:
        return [TextContent(type="text", text=json.dumps({"error": "file_path is required"}))]

    try:
        processor = ContentProcessor(file_path)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "language": analyzer.language,
                "file_type": analyzer.file_type,
                "total_issues": len(result["all_issues"]),
                "formatting_issues": len(result["formatting_issues"]),
                "language_issues": len(result["language_issues"]),
                "summary": result["summary"]
            })
        )]
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def process_document(args: dict[str, Any]) -> list[TextContent]:
    """Process document."""
    file_path = args.get("file_path")
    if not file_path:
        return [TextContent(type="text", text=json.dumps({"error": "file_path is required"}))]

    try:
        processor = ContentProcessor(file_path)
        result = processor.process_document()

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "file_type": result.get("file_type"),
                "language": result.get("language"),
                "text_sample": result.get("full_text", "")[:200],
            })
        )]
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def get_document_summary(args: dict[str, Any]) -> list[TextContent]:
    """Get document summary."""
    file_path = args.get("file_path")
    if not file_path:
        return [TextContent(type="text", text=json.dumps({"error": "file_path is required"}))]

    try:
        processor = ContentProcessor(file_path)
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        result = analyzer.analyze_complete()

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "language": analyzer.language,
                "file_type": analyzer.file_type,
                "total_issues": len(result["all_issues"]),
                "summary": result["summary"]
            })
        )]
    except Exception as e:
        logger.error(f"Error getting document summary: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Run the MCP server."""
    logger.info("Starting Document QA Agent MCP Server")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, None)


if __name__ == "__main__":
    asyncio.run(main())
