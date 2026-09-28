# Claude MCP Document QA Agent

A sophisticated Claude-based document quality assurance system for German and Chinese technical documentation in DOCX and PDF formats.

## Overview

This project implements a comprehensive document analysis system that:

- **Accepts** DOCX and PDF documents
- **Detects** language automatically (German/Simplified Chinese)
- **Validates** formatting compliance (fonts, sizes, heading hierarchy, tables, lists, captions, cross-references)
- **Checks** language-specific conventions (German quotes, Chinese punctuation, full-width characters, etc.)
- **Generates** detailed reports in JSON, HTML, and PDF formats
- **Integrates** with Claude via Model Context Protocol (MCP)
- **Runs** locally on Windows with zero external dependencies

## Project Structure

```
claude_mcp_docqa_agent/
├── mcp_server/              # MCP server and tool definitions
├── document_processing/     # PDF/DOCX extraction
├── analysis/                # Formatting and language analysis
│   └── language_rules/      # Language-specific rule engines
├── database/                # SQLAlchemy models and managers
├── config/                  # Configuration and style rules (YAML)
├── report_generation/       # Report builders and exporters
├── storage/                 # File and cache management
├── errors/                  # Custom exceptions
└── utils/                   # Logging, validation, helpers
```

## Installation

### Prerequisites

- Python 3.11+
- Windows, macOS, or Linux
- ~2GB disk space for dependencies

### Setup

1. **Clone or navigate to the project**:
   ```bash
   cd D:\TWT_AI
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**:
   ```bash
   python -m claude_mcp_docqa_agent.main
   ```

## Usage

### Phase 1: Core Features (Implemented)

#### Document Processing
```python
from claude_mcp_docqa_agent.document_processing.pdf_extractor import PDFExtractor
from claude_mcp_docqa_agent.document_processing.docx_parser import DOCXParser

# Extract PDF content
pdf = PDFExtractor("document.pdf")
text = pdf.extract_full_text()
tables = pdf.extract_all_tables()
metadata = pdf.extract_metadata()

# Parse DOCX content
docx = DOCXParser("document.docx")
paragraphs = docx.extract_paragraphs()
headings = docx.extract_headings()
fonts = docx.extract_font_usage()
```

#### Language Detection
```python
from claude_mcp_docqa_agent.analysis.language_detector import LanguageDetector

detector = LanguageDetector()
result = detector.detect_language(text)
# Returns: {"language": "de", "confidence": 0.95, "method": "langdetect", ...}

is_german = detector.is_german(result["language"])
is_chinese = detector.is_chinese(result["language"])
```

#### Content Processing
```python
from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor

processor = ContentProcessor("document.docx")
result = processor.process_document()
# Returns: complete structured document with language detection

text = processor.get_text_for_analysis()
page_count = processor.get_page_count()
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_document_processing.py

# Run with coverage
pytest tests/ --cov=claude_mcp_docqa_agent
```

## Configuration

### Style Rules

Configuration is managed through YAML files in `claude_mcp_docqa_agent/config/`:

- **default_rules.yaml** - Generic formatting rules
- **german_conventions.yaml** - German language rules
- **chinese_conventions.yaml** - Chinese language rules
- **settings.yaml** - Application settings

### Example Rule Customization

Edit `german_conventions.yaml` to modify German quotation mark detection:

```yaml
quotation_marks:
  - id: german_quotation_marks
    primary_open: "„"
    primary_close: """
    severity: warning
    enabled: true
```

## Database

The system uses **SQLite** for local storage:

- **Location**: `data/docqa.db`
- **Auto-initialization**: Database and tables created automatically
- **Models**: Document, ProcessingResult, FormattingIssue, LanguageIssue, StyleRule, Report

## Phase Progress

### ✅ Phase 1: Foundation (Complete)
- [x] Project structure and dependencies
- [x] PDF extraction (pdfplumber)
- [x] DOCX parsing (python-docx)
- [x] Language detection (langdetect + textblob)
- [x] Database schema and manager
- [x] Logging and error handling
- [x] Unit tests (40+ tests)
- [x] Configuration system

### ✅ Phase 2: Formatting Analysis (Complete)
- [x] Font analyzer
- [x] Heading hierarchy validator
- [x] Table structure checker
- [x] List and numbering checker
- [x] Image caption validator
- [x] Cross-reference checker
- [x] Integration tests (30 tests)
- [x] All analyzers working (62 tests passing)

### ✅ Phase 3: Language-Specific Rules (Complete)
- [x] German rules engine (5 checks)
- [x] Chinese rules engine (4 checks)
- [x] Rule application system
- [x] Unified quality analyzer
- [x] Integration tests (28 tests)
- [x] 90 total tests passing

### ✅ Phase 4: MCP Integration (Complete)
- [x] MCP server implementation
- [x] Tool definitions (6 tools)
- [x] Claude integration ready
- [x] Quality scoring
- [x] Integration tests (26 tests)
- [x] 116 total tests passing

### ⏳ Phase 5: Report Generation (Upcoming)
- [ ] JSON exporter
- [ ] HTML template and exporter
- [ ] PDF exporter

### ⏳ Phase 6: Configuration UI (Upcoming)
- [ ] Rule editor
- [ ] Hot-loading support

### ⏳ Phase 7: Testing & Documentation (Upcoming)
- [ ] Comprehensive test suite
- [ ] User documentation
- [ ] API reference

### ⏳ Phase 8: Deployment (Upcoming)
- [ ] Windows installer
- [ ] CI/CD pipeline
- [ ] Deployment guide

## Dependencies

### Core
- **mcp**: Anthropic MCP SDK for Claude integration
- **anthropic**: Claude API client

### Document Processing
- **python-docx**: DOCX parsing and manipulation
- **pdfplumber**: PDF extraction with coordinate tracking
- **pypdf**: PDF utilities
- **Pillow**: Image processing

### Language Analysis
- **langdetect**: Language detection (primary)
- **textblob**: NLP fallback
- **regex**: Enhanced pattern matching
- **python-pinyin**: Chinese phonetic analysis

### Database
- **sqlalchemy**: ORM and schema management
- **alembic**: Database migrations

### Reporting
- **reportlab**: PDF generation
- **Jinja2**: HTML template rendering

### Utilities
- **pydantic**: Data validation
- **pyyaml**: Configuration management
- **loguru**: Structured logging

## Architecture

```
Claude Code
    ↓
MCP Server (Phase 4)
    ↓
Tools Layer
    ├─ upload_document()
    ├─ extract_content()
    ├─ detect_language()
    ├─ analyze_formatting()
    ├─ validate_compliance()
    └─ generate_report()
    ↓
Analysis Engine (Phase 2-3)
    ├─ Document Processing
    ├─ Formatting Analysis
    └─ Language Rules
    ↓
Storage Layer
    ├─ SQLite Database
    ├─ File Storage
    └─ Cache
```

## Error Handling

Custom exception hierarchy for robust error management:

- `DocumentQAException` - Base exception
- `DocumentProcessingError` - Processing failures
- `PDFExtractionError` - PDF-specific errors
- `DOCXParsingError` - DOCX-specific errors
- `LanguageDetectionError` - Detection failures
- `FormattingAnalysisError` - Analysis failures
- `DatabaseError` - Database operations
- `ConfigurationError` - Configuration issues

## Logging

Logging is configured via `utils/logger.py`:

- **Console output**: Colorized, formatted logs
- **File output**: Rotating logs in `logs/` directory
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Modules**: Each module uses `get_logger(__name__)`

## Next Steps

1. **Phase 2**: Implement formatting analysis modules
2. **Phase 3**: Build language-specific rule engines
3. **Phase 4**: Create MCP server and integrate with Claude
4. **Phase 5**: Develop report generation system

## Contributing

- Follow PEP 8 style guide
- Write unit tests for new features
- Update configuration files for new rules
- Document all public methods

## Testing

Unit tests are comprehensive with fixtures for:
- Temporary DOCX files
- Language detection samples
- Processing validation

```bash
pytest tests/ -v              # Verbose output
pytest tests/ --cov           # Coverage report
pytest tests/test_*.py -k "test_" # Specific tests
```

## License

Proprietary - Internal Use Only

## Status

🚀 **Phase 1 Complete** - Document processing and language detection implemented and tested.

Next phase begins implementation of formatting analysis components.
