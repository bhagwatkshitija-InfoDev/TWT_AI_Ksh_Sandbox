"""MCP Server for Document QA Agent."""

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ToolResult

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


class DocumentQAServer:
    """MCP Server for Document QA Agent."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("document-qa-agent")
        self._setup_tools()
        logger.info("Initialized DocumentQA MCP Server")

    def _setup_tools(self) -> None:
        """Register all available tools."""
        self.server.set_tool_handler(self._handle_tool)

        # Register tools
        self.server.register_tool(self._get_upload_document_tool())
        self.server.register_tool(self._get_process_document_tool())
        self.server.register_tool(self._get_analyze_formatting_tool())
        self.server.register_tool(self._get_analyze_language_tool())
        self.server.register_tool(self._get_analyze_complete_tool())
        self.server.register_tool(self._get_get_document_summary_tool())

        logger.info("Registered 6 tools")

    async def _handle_tool(self, tool_name: str, tool_input: dict[str, Any]) -> ToolResult:
        """Handle tool invocation."""
        logger.info(f"Tool invoked: {tool_name}")

        try:
            if tool_name == "upload_document":
                result = self._upload_document(tool_input)
            elif tool_name == "process_document":
                result = self._process_document(tool_input)
            elif tool_name == "analyze_formatting":
                result = self._analyze_formatting(tool_input)
            elif tool_name == "analyze_language":
                result = self._analyze_language(tool_input)
            elif tool_name == "analyze_complete":
                result = self._analyze_complete(tool_input)
            elif tool_name == "get_document_summary":
                result = self._get_document_summary(tool_input)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return ToolResult(content=[TextContent(type="text", text=json.dumps(result))])

        except Exception as e:
            logger.error(f"Tool error: {e}")
            error_result = {"error": str(e), "tool": tool_name}
            return ToolResult(content=[TextContent(type="text", text=json.dumps(error_result))])

    def _get_upload_document_tool(self) -> Tool:
        """Get upload_document tool definition."""
        return Tool(
            name="upload_document",
            description="Upload and validate a document (PDF or DOCX)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file (PDF or DOCX)",
                    },
                },
                "required": ["file_path"],
            },
        )

    def _get_process_document_tool(self) -> Tool:
        """Get process_document tool definition."""
        return Tool(
            name="process_document",
            description="Process document to extract content and detect language",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file",
                    },
                },
                "required": ["file_path"],
            },
        )

    def _get_analyze_formatting_tool(self) -> Tool:
        """Get analyze_formatting tool definition."""
        return Tool(
            name="analyze_formatting",
            description="Analyze document formatting (Phase 2): fonts, headings, tables, lists",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file",
                    },
                },
                "required": ["file_path"],
            },
        )

    def _get_analyze_language_tool(self) -> Tool:
        """Get analyze_language tool definition."""
        return Tool(
            name="analyze_language",
            description="Analyze language-specific conventions (Phase 3): German or Chinese rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file",
                    },
                },
                "required": ["file_path"],
            },
        )

    def _get_analyze_complete_tool(self) -> Tool:
        """Get analyze_complete tool definition."""
        return Tool(
            name="analyze_complete",
            description="Complete document quality analysis (formatting + language rules)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file",
                    },
                },
                "required": ["file_path"],
            },
        )

    def _get_get_document_summary_tool(self) -> Tool:
        """Get get_document_summary tool definition."""
        return Tool(
            name="get_document_summary",
            description="Get document analysis summary with quality score",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file",
                    },
                },
                "required": ["file_path"],
            },
        )

    def _upload_document(self, params: dict[str, Any]) -> dict[str, Any]:
        """Upload and validate document."""
        file_path = params.get("file_path")

        if not file_path:
            return {"error": "file_path is required"}

        try:
            extractor = MetadataExtractor(file_path)
            metadata = extractor.extract_metadata()

            return {
                "status": "success",
                "document": metadata,
                "message": f"Document uploaded: {metadata['filename']}",
            }

        except Exception as e:
            return {"error": str(e)}

    def _process_document(self, params: dict[str, Any]) -> dict[str, Any]:
        """Process document."""
        file_path = params.get("file_path")

        if not file_path:
            return {"error": "file_path is required"}

        try:
            processor = ContentProcessor(file_path)
            result = processor.process_document()

            return {
                "status": "success",
                "file_type": result.get("file_type"),
                "language": result.get("language"),
                "text_sample": result.get("full_text", "")[:200],
                "message": f"Document processed successfully",
            }

        except Exception as e:
            return {"error": str(e)}

    def _analyze_formatting(self, params: dict[str, Any]) -> dict[str, Any]:
        """Analyze formatting."""
        file_path = params.get("file_path")

        if not file_path:
            return {"error": "file_path is required"}

        try:
            processor = ContentProcessor(file_path)
            doc_data = processor.process_document()

            analyzer = DocumentQualityAnalyzer(doc_data)
            formatting_issues = analyzer.analyze_formatting_only()

            summary = analyzer.get_summary()

            return {
                "status": "success",
                "total_issues": len(formatting_issues),
                "summary": summary,
                "critical": summary["critical"],
                "warning": summary["warning"],
                "info": summary["info"],
                "by_type": summary["by_type"],
            }

        except Exception as e:
            return {"error": str(e)}

    def _analyze_language(self, params: dict[str, Any]) -> dict[str, Any]:
        """Analyze language rules."""
        file_path = params.get("file_path")

        if not file_path:
            return {"error": "file_path is required"}

        try:
            processor = ContentProcessor(file_path)
            doc_data = processor.process_document()

            analyzer = DocumentQualityAnalyzer(doc_data)
            language_issues = analyzer.analyze_language_only()

            return {
                "status": "success",
                "language": analyzer.language,
                "total_issues": len(language_issues),
                "message": f"Language analysis complete for {analyzer.language}",
            }

        except Exception as e:
            return {"error": str(e)}

    def _analyze_complete(self, params: dict[str, Any]) -> dict[str, Any]:
        """Complete analysis."""
        file_path = params.get("file_path")

        if not file_path:
            return {"error": "file_path is required"}

        try:
            processor = ContentProcessor(file_path)
            doc_data = processor.process_document()

            analyzer = DocumentQualityAnalyzer(doc_data)
            result = analyzer.analyze_complete()

            return {
                "status": "success",
                "language": analyzer.language,
                "total_issues": len(result["all_issues"]),
                "formatting_issues": len(result["formatting_issues"]),
                "language_issues": len(result["language_issues"]),
                "quality_score": analyzer.get_quality_score(),
                "summary": result["summary"],
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_document_summary(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get document summary."""
        file_path = params.get("file_path")

        if not file_path:
            return {"error": "file_path is required"}

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
                "quality_score": analyzer.get_quality_score(),
                "total_issues": len(result["all_issues"]),
                "severity_distribution": result["summary"]["severity_distribution"],
                "priority_issues": [
                    {
                        "type": issue.issue_type,
                        "severity": issue.severity,
                        "description": issue.issue_description,
                        "fix": issue.recommended_fix,
                    }
                    for issue in priority_issues
                ],
            }

        except Exception as e:
            return {"error": str(e)}

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting DocumentQA MCP Server")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


def main():
    """Main entry point."""
    import asyncio

    server = DocumentQAServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
