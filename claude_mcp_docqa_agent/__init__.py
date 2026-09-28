"""Claude MCP Document QA Agent for German and Chinese technical documentation."""

__version__ = "0.1.0"
__author__ = "AI Engineer"
__email__ = "dev@example.com"

# Lazy imports to avoid circular dependencies
def __getattr__(name: str):
    """Lazy load modules on demand."""
    if name == "PDFExtractor":
        from claude_mcp_docqa_agent.document_processing.pdf_extractor import PDFExtractor
        return PDFExtractor
    elif name == "DOCXParser":
        from claude_mcp_docqa_agent.document_processing.docx_parser import DOCXParser
        return DOCXParser
    elif name == "LanguageDetector":
        from claude_mcp_docqa_agent.analysis.language_detector import LanguageDetector
        return LanguageDetector
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "PDFExtractor",
    "DOCXParser",
    "LanguageDetector",
]
