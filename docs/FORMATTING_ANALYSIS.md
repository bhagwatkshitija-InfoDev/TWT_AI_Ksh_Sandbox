# Formatting Analysis - Phase 2 Reference

## Overview

Phase 2 implements comprehensive formatting analysis for DOCX and PDF documents. The system checks font consistency, heading hierarchy, table structure, lists, images, captions, and cross-references.

## Core Components

### FormattingAnalyzer (Main Orchestrator)

The `FormattingAnalyzer` class is the main entry point for all formatting checks.

```python
from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingAnalyzer

analyzer = FormattingAnalyzer(document_data)
issues = analyzer.analyze_all()
```

**Key Methods**:
- `analyze_all()` - Run all checks and return list of issues
- `get_issues_by_severity(severity)` - Filter by 'critical', 'warning', 'info'
- `get_issues_by_page(page_number)` - Filter by page number
- `get_issues_by_type(issue_type)` - Filter by issue type
- `get_summary()` - Get statistics on issues found

### FormattingIssue Data Class

Represents a single formatting issue with full context:

```python
@dataclass
class FormattingIssue:
    id: str                          # Unique issue ID
    page_number: int                 # Page where issue occurs
    issue_type: str                  # 'font', 'heading', 'table', etc.
    severity: str                    # 'critical', 'warning', 'info'
    location_description: str        # Human-readable location
    issue_description: str           # What's wrong
    recommended_fix: str             # How to fix it
    coordinates: Optional[dict]      # {x, y, width, height}
    context: Optional[str]           # Example text
```

## DOCX-Specific Analyzers

### DOCXFontAnalyzer

Analyzes font consistency in DOCX documents.

```python
from claude_mcp_docqa_agent.analysis.docx_analyzers import DOCXFontAnalyzer

analyzer = DOCXFontAnalyzer(document_content)
issues = analyzer.analyze()
font_list = analyzer.get_font_list()  # Sorted by usage
```

**Checks**:
- Font variety (max 3 recommended)
- Font name consistency
- Font size variations

**Configuration**:
- `MAX_UNIQUE_FONTS = 3` - Maximum recommended fonts

### DOCXHeadingAnalyzer

Validates heading hierarchy and consistency.

```python
from claude_mcp_docqa_agent.analysis.docx_analyzers import DOCXHeadingAnalyzer

analyzer = DOCXHeadingAnalyzer(document_content)
issues = analyzer.analyze()
tree = analyzer.get_heading_tree()  # Heading hierarchy
```

**Checks**:
- Proper heading hierarchy (H1 → H2 → H3, not H1 → H3)
- Single H1 validation (typically should be one)
- Heading consistency

**Issues Detected**:
- `heading_hierarchy` - Skipped levels
- `heading_consistency` - Multiple H1 headings

### DOCXTableAnalyzer

Analyzes table structures and content.

```python
from claude_mcp_docqa_agent.analysis.docx_analyzers import DOCXTableAnalyzer

analyzer = DOCXTableAnalyzer(document_content)
issues = analyzer.analyze()
stats = analyzer.get_table_stats()
```

**Checks**:
- Consistent column counts per table
- Empty table detection
- Row-column structure validation

**Statistics**:
- Total tables
- Average rows
- Average columns

### DOCXListAnalyzer

Checks list and numbering formatting.

```python
from claude_mcp_docqa_agent.analysis.docx_analyzers import DOCXListAnalyzer

analyzer = DOCXListAnalyzer(document_content)
issues = analyzer.analyze()
```

**Checks**:
- Consistent indentation levels
- List formatting consistency
- Numbering scheme validation

## PDF-Specific Analyzers

### PDFFontAnalyzer

Analyzes font usage in PDF documents.

```python
from claude_mcp_docqa_agent.analysis.pdf_analyzers import PDFFontAnalyzer

analyzer = PDFFontAnalyzer(document_content)
issues = analyzer.analyze()
```

**Checks**:
- Font variety
- Font size consistency across pages
- Character density analysis

### PDFTableAnalyzer

Validates tables in PDF documents.

```python
from claude_mcp_docqa_agent.analysis.pdf_analyzers import PDFTableAnalyzer

analyzer = PDFTableAnalyzer(document_content)
issues = analyzer.analyze()
count = analyzer.get_table_count()
```

**Checks**:
- Empty table detection
- Table content extraction
- Table structure validation

### PDFStructureAnalyzer

Analyzes overall document structure.

```python
from claude_mcp_docqa_agent.analysis.pdf_analyzers import PDFStructureAnalyzer

analyzer = PDFStructureAnalyzer(document_content)
issues = analyzer.analyze()
```

**Checks**:
- Page consistency
- Content density analysis
- Blank page detection

## Cross-Document Analyzers

### ImageAnalyzer

Checks for images and their captions.

```python
from claude_mcp_docqa_agent.analysis.image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer(document_content)
issues = analyzer.analyze()
count = analyzer.get_image_count()
```

**Checks**:
- Missing image captions
- Short or inadequate captions
- Image reference validation

**Configuration**:
- `MIN_CAPTION_LENGTH = 10` - Minimum caption length

### CrossReferenceChecker

Validates cross-references and section numbering.

```python
from claude_mcp_docqa_agent.analysis.cross_ref_checker import CrossReferenceChecker

checker = CrossReferenceChecker(document_content)
issues = checker.analyze()
summary = checker.get_reference_summary()
```

**Checks**:
- Valid section references
- Table references
- Figure references
- Broken cross-references

**Reference Patterns Detected**:
- "See Section X"
- "See Chapter Y"
- "Refer to Heading Title"
- "Table X"
- "Figure X"

## Usage Example

### Complete Analysis Workflow

```python
from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingAnalyzer

# 1. Process document (Phase 1)
processor = ContentProcessor("document.docx")
document_data = processor.process_document()

# 2. Analyze formatting (Phase 2)
analyzer = FormattingAnalyzer(document_data)
issues = analyzer.analyze_all()

# 3. Filter and prioritize
critical_issues = analyzer.get_issues_by_severity("critical")
page_1_issues = analyzer.get_issues_by_page(1)
font_issues = analyzer.get_issues_by_type("font")

# 4. Get summary
summary = analyzer.get_summary()
print(f"Total issues: {summary['total_issues']}")
print(f"Critical: {summary['critical']}, Warning: {summary['warning']}")
print(f"By type: {summary['by_type']}")
```

## Issue Types Reference

### Formatting Issues

| Type | Severity | Description |
|------|----------|-------------|
| `font_variety` | warning | Too many different fonts |
| `font_size_variation` | info | Inconsistent font sizes |
| `heading_hierarchy` | warning | Skipped heading levels |
| `heading_consistency` | info | Multiple H1 headings |
| `table_structure` | warning | Inconsistent columns |
| `table_content` | info | Empty or missing tables |
| `list_formatting` | info | Inconsistent list indentation |
| `image_caption` | warning | Missing or short captions |
| `cross_reference` | warning | Broken references |
| `page_structure` | info | Blank or unusual pages |

## Configuration

### Font Analysis Settings

```yaml
formatting_rules:
  - id: font_consistency
    scope: formatting
    severity: warning
    rule_definition:
      max_unique_fonts: 3
      required_fonts: []
```

### Heading Settings

```yaml
  - id: heading_hierarchy
    scope: structure
    severity: warning
    rule_definition:
      require_single_h1: true
      require_sequence: true
```

## Integration with Phase 1

The formatting analyzer works seamlessly with Phase 1 components:

```
Document File (PDF/DOCX)
        ↓
ContentProcessor (Phase 1)
        ↓
FormattingAnalyzer (Phase 2)
        ↓
FormattingIssues List
        ↓
[Phase 3 Language Rules]
        ↓
Complete Analysis Results
```

## Testing

### Running Formatting Analysis Tests

```bash
# Run all formatting tests
pytest tests/test_formatting_analysis.py -v

# Run specific analyzer tests
pytest tests/test_formatting_analysis.py::TestDOCXFontAnalyzer -v

# Run integration tests
pytest tests/test_formatting_analysis.py::TestFormattingAnalysisIntegration -v
```

### Test Coverage

- 30+ unit tests for all analyzers
- Integration tests with real DOCX files
- Fixture-based testing with sample documents
- Edge case coverage

## Performance Notes

- **Memory**: ~1-5MB per document analysis
- **Speed**: <500ms for typical 10-page document
- **Scalability**: Processes page-by-page to minimize memory usage
- **Caching**: Results can be cached in database

## Extension Points

### Adding a New Analyzer

1. Create analyzer class inheriting from base structure:
```python
class MyAnalyzer:
    def __init__(self, document_content: dict[str, Any]):
        self.content = document_content
        self.issues: list[FormattingIssue] = []
    
    def analyze(self) -> list[FormattingIssue]:
        # Your analysis logic
        return self.issues
```

2. Register in `FormattingAnalyzer.analyze_all()`:
```python
analyzer = MyAnalyzer(self.content)
self.issues.extend(analyzer.analyze())
```

3. Add configuration to YAML rules

4. Create unit tests

### Adding a New Check Type

1. Define new `issue_type` constant
2. Create FormattingIssue with that type
3. Add to configuration rules
4. Update documentation

## Known Limitations

- PDF font analysis is limited (requires full PDF parsing)
- Image extraction requires specialized libraries (not in Phase 2)
- List numbering validation is heuristic-based
- Cross-references are pattern-based (not semantic)

## Next Steps (Phase 3)

Phase 3 will add language-specific rule engines that work with these formatting issues to provide comprehensive quality assurance for German and Chinese technical documentation.

## Related Documentation

- **ARCHITECTURE.md** - System design
- **README.md** - Project overview
- **Phase 1 Summary** - Foundation components
- **Phase 3** - Language-specific rules (coming)
