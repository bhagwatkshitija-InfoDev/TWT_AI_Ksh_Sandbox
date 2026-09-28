# Phase 2: Quick Start Guide

## Quick Reference

### 1. Basic Formatting Analysis

```python
from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingAnalyzer

# Step 1: Process document
processor = ContentProcessor("your_document.docx")
doc_data = processor.process_document()

# Step 2: Analyze formatting
analyzer = FormattingAnalyzer(doc_data)
issues = analyzer.analyze_all()

# Step 3: Review results
print(f"Found {len(issues)} formatting issues")
for issue in issues:
    print(f"  [{issue.severity}] Page {issue.page_number}: {issue.issue_description}")
```

### 2. Filter Results

```python
# By severity
critical_issues = analyzer.get_issues_by_severity("critical")
warnings = analyzer.get_issues_by_severity("warning")
info = analyzer.get_issues_by_severity("info")

# By page
page_1_issues = analyzer.get_issues_by_page(1)

# By type
font_issues = analyzer.get_issues_by_type("font_variety")
heading_issues = analyzer.get_issues_by_type("heading_hierarchy")
```

### 3. Get Summary

```python
summary = analyzer.get_summary()

print(f"Total: {summary['total_issues']}")
print(f"Critical: {summary['critical']}")
print(f"Warnings: {summary['warning']}")
print(f"Info: {summary['info']}")
print(f"By type: {summary['by_type']}")
```

## Supported Issue Types

| Issue Type | Description | Severity |
|------------|-------------|----------|
| `font_variety` | Too many different fonts | warning |
| `heading_hierarchy` | Skipped heading levels | warning |
| `heading_consistency` | Multiple H1 headings | info |
| `table_structure` | Inconsistent table columns | warning |
| `list_formatting` | Inconsistent list indentation | info |
| `image_caption` | Missing or short captions | warning |
| `cross_reference` | Broken references | warning |
| `font_size_variation` | Inconsistent font sizes | info |
| `table_content` | Empty tables | info |
| `page_structure` | Blank pages | info |

## Common Tasks

### Task: Check Font Consistency

```python
from claude_mcp_docqa_agent.analysis.docx_analyzers import DOCXFontAnalyzer

analyzer = DOCXFontAnalyzer(doc_data["content"])
issues = analyzer.analyze()
font_list = analyzer.get_font_list()

print(f"Fonts used: {[f[0] for f in font_list]}")
print(f"Font issues: {len(issues)}")
```

### Task: Validate Heading Structure

```python
from claude_mcp_docqa_agent.analysis.docx_analyzers import DOCXHeadingAnalyzer

analyzer = DOCXHeadingAnalyzer(doc_data["content"])
issues = analyzer.analyze()
tree = analyzer.get_heading_tree()

print("Heading structure:")
for heading in tree:
    indent = "  " * (heading["level"] - 1)
    print(f"{indent}H{heading['level']}: {heading['text']}")
```

### Task: Check Tables

```python
from claude_mcp_docqa_agent.analysis.docx_analyzers import DOCXTableAnalyzer

analyzer = DOCXTableAnalyzer(doc_data["content"])
issues = analyzer.analyze()
stats = analyzer.get_table_stats()

print(f"Total tables: {stats['total_tables']}")
print(f"Avg rows: {stats['avg_rows']:.1f}")
print(f"Avg cols: {stats['avg_cols']:.1f}")
print(f"Issues: {len(issues)}")
```

### Task: Validate Cross-References

```python
from claude_mcp_docqa_agent.analysis.cross_ref_checker import CrossReferenceChecker

checker = CrossReferenceChecker(doc_data["content"])
issues = checker.analyze()
summary = checker.get_reference_summary()

print(f"Headings: {summary['total_headings']}")
print(f"Tables: {summary['total_tables']}")
print(f"Broken refs: {summary['broken_references']}")
```

### Task: Check Image Captions

```python
from claude_mcp_docqa_agent.analysis.image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer(doc_data["content"])
issues = analyzer.analyze()
count = analyzer.get_image_count()

print(f"Estimated images: {count}")
print(f"Caption issues: {len(issues)}")
```

## Working with FormattingIssue

Each issue is a structured object:

```python
issue = issues[0]

print(f"ID: {issue.id}")
print(f"Page: {issue.page_number}")
print(f"Type: {issue.issue_type}")
print(f"Severity: {issue.severity}")
print(f"Location: {issue.location_description}")
print(f"Problem: {issue.issue_description}")
print(f"Fix: {issue.recommended_fix}")
```

Convert to dict for JSON export:

```python
issue_dict = issue.to_dict()
import json
json.dumps(issue_dict)
```

## File Type Support

### DOCX (Microsoft Word)
All analyzers supported:
- ✅ Font analysis
- ✅ Heading analysis
- ✅ Table analysis
- ✅ List analysis
- ✅ Image/caption analysis
- ✅ Cross-references

### PDF
Limited support:
- ✅ Font analysis (heuristic)
- ✅ Table analysis (basic)
- ✅ Structure analysis
- ✅ Image captions (pattern-based)
- ✅ Cross-references (pattern-based)

## Integration with Phase 1

Phase 2 works with Phase 1 output:

```python
# Phase 1: Document Processing
from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
processor = ContentProcessor("document.pdf")  # or .docx
document_data = processor.process_document()

# document_data contains:
# - file_type: 'pdf' or 'docx'
# - language: detected language
# - full_text: complete text
# - content: structured content
#   - metadata
#   - paragraphs
#   - headings
#   - tables
#   - font_usage

# Phase 2: Formatting Analysis
from claude_mcp_docqa_agent.analysis.formatting_analyzer import FormattingAnalyzer
analyzer = FormattingAnalyzer(document_data)
issues = analyzer.analyze_all()

# Returns: list of FormattingIssue objects
# Ready for Phase 3: Language-specific rules
```

## Running Tests

```bash
# Run all Phase 2 tests
pytest tests/test_formatting_analysis.py -v

# Run specific analyzer tests
pytest tests/test_formatting_analysis.py::TestDOCXFontAnalyzer -v

# Run integration tests
pytest tests/test_formatting_analysis.py::TestFormattingAnalysisIntegration -v
```

## Performance Tips

1. **For Large Documents**
   - Analysis is done page-by-page
   - Memory usage stays under 10MB
   - Typical document: <500ms

2. **For Batch Processing**
   - Use in-memory caching
   - Database persistence for results
   - Can process multiple documents

3. **For Memory-Constrained Environments**
   - PDF analysis uses less memory
   - Stream processing on demand
   - Cache results if needed

## Troubleshooting

### Issue: "outline_level" attribute error
- **Status**: Fixed in Phase 2 update
- **Cause**: DOCX parser incompatibility
- **Solution**: Uses heading style parsing instead

### Issue: No issues found
- **Cause**: Document might be well-formatted
- **Check**: Manual review or test with sample document

### Issue: PDF font analysis limited
- **Cause**: Full PDF font extraction not implemented
- **Note**: Will be improved in future phases

## Next Steps

1. **Phase 3**: Language-specific rules (German, Chinese)
2. **Phase 4**: MCP server integration with Claude
3. **Phase 5**: Report generation (JSON, HTML, PDF)
4. **Phase 6**: Configuration UI
5. **Phase 7**: Complete testing and documentation
6. **Phase 8**: Windows deployment

## Reference Links

- **Full API**: See `docs/FORMATTING_ANALYSIS.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Deployment**: See `docs/DEPLOYMENT.md`
- **Phase 2 Summary**: See `PHASE2_SUMMARY.md`
