# MCP Tools Reference - Phase 4

## Overview

Phase 4 exposes all Document QA Agent capabilities as Claude tools via the Model Context Protocol (MCP). Claude can invoke these tools to analyze German and Chinese technical documents with full formatting and language-specific validation.

## Available Tools

### 1. upload_document

**Description**: Upload and validate a document file (PDF or DOCX format)

**Parameters**:
- `file_path` (string, required): Path to the document file (PDF or DOCX)

**Returns**:
```json
{
  "status": "success",
  "filename": "document.docx",
  "file_type": "docx",
  "file_size": 25000,
  "message": "Document uploaded successfully: document.docx"
}
```

**Example Usage**:
```python
# Claude calling the tool
tool_use = {
  "type": "tool_use",
  "name": "upload_document",
  "input": {
    "file_path": "/path/to/german_document.docx"
  }
}
```

### 2. process_document

**Description**: Process document to extract content and detect language

**Parameters**:
- `file_path` (string, required): Path to the document file

**Returns**:
```json
{
  "status": "success",
  "file_type": "docx",
  "language": "de",
  "language_confidence": 0.95,
  "text_sample": "Sample text from document...",
  "message": "Document processed: docx detected as de"
}
```

**Detects**:
- German (de)
- Simplified Chinese (zh_CN)
- English (en) - no language-specific rules

### 3. analyze_formatting

**Description**: Analyze document formatting (Phase 2) - fonts, headings, tables, lists, images, cross-references

**Parameters**:
- `file_path` (string, required): Path to the document file

**Returns**:
```json
{
  "status": "success",
  "total_formatting_issues": 5,
  "critical": 0,
  "warning": 2,
  "info": 3,
  "by_type": {
    "font_variety": 1,
    "heading_hierarchy": 1,
    "table_structure": 3
  },
  "message": "Formatting analysis complete: 5 issues found"
}
```

**Checks**:
- Font consistency (max 3 recommended)
- Heading hierarchy (H1 → H2 → H3)
- Table structure validation
- List formatting
- Image captions
- Cross-references

### 4. analyze_language

**Description**: Analyze language-specific conventions (Phase 3) - German or Chinese rules

**Parameters**:
- `file_path` (string, required): Path to the document file

**Returns**:
```json
{
  "status": "success",
  "language": "de",
  "total_language_issues": 3,
  "message": "Language analysis complete for de: 3 issues found"
}
```

**German Rules**:
- Quotation marks („" vs "")
- Number formatting (1.234,56 vs 1,234.56)
- Capitalization (noun rules)
- Umlaut usage (ä, ö, ü)
- Spacing rules

**Chinese Rules**:
- Punctuation marks (，。！？)
- Character width (full-width vs half-width)
- Traditional characters (should be simplified)
- CJK-Latin spacing

### 5. analyze_complete

**Description**: Complete document quality analysis - formatting + language rules with quality score

**Parameters**:
- `file_path` (string, required): Path to the document file

**Returns**:
```json
{
  "status": "success",
  "language": "de",
  "file_type": "docx",
  "total_issues": 8,
  "formatting_issues": 5,
  "language_issues": 3,
  "quality_score": 75.5,
  "severity_distribution": {
    "critical": 0,
    "warning": 2,
    "info": 6
  },
  "message": "Complete analysis: 8 total issues, quality score 75.5/100"
}
```

**Quality Score** (0-100):
- 100: No issues
- 90-99: Excellent (only info-level issues)
- 80-89: Good (few warnings)
- 70-79: Fair (multiple issues)
- 60-69: Poor (significant issues)
- <60: Critical (many issues)

### 6. get_document_summary

**Description**: Get comprehensive document analysis summary with priority issues and quality score

**Parameters**:
- `file_path` (string, required): Path to the document file

**Returns**:
```json
{
  "status": "success",
  "language": "de",
  "file_type": "docx",
  "quality_score": 75.5,
  "total_issues": 8,
  "severity_distribution": {
    "critical": 0,
    "warning": 2,
    "info": 6
  },
  "issues_by_type": {
    "font_variety": 1,
    "heading_hierarchy": 1,
    "german_quotation_marks": 2,
    "german_number_format": 1
  },
  "priority_issues": [
    {
      "type": "heading_hierarchy",
      "severity": "warning",
      "description": "Heading level skipped from H1 to H3",
      "fix": "Use H2 instead of H3, or use H2 for the previous heading"
    },
    {
      "type": "german_quotation_marks",
      "severity": "warning",
      "description": "English quotes (\") used instead of German quotation marks („")",
      "fix": "Replace \"text\" with „text\""
    }
  ],
  "message": "Summary: de document, quality 75.5/100"
}
```

## Tool Categories

### Document Intake (Phase 1)
- `upload_document` - Validate and register document
- `process_document` - Extract content and detect language

### Analysis (Phases 2-3)
- `analyze_formatting` - Formatting validation only
- `analyze_language` - Language rules only
- `analyze_complete` - Complete analysis
- `get_document_summary` - Full summary with recommendations

## Severity Levels

**Critical** (5 points deducted):
- Major issues affecting document usability
- Broken references
- Invalid structure

**Warning** (3 points deducted):
- Formatting inconsistencies
- Language convention violations
- Structure issues

**Info** (1 point deducted):
- Minor improvements
- Suggestions for consistency
- Optional enhancements

## Usage Patterns

### Pattern 1: Quick Validation
```python
# Upload and get quick summary
analyzer.upload_document(file_path)
summary = analyzer.get_document_summary(file_path)
print(f"Quality: {summary['quality_score']}/100")
```

### Pattern 2: Detailed Formatting Review
```python
# Focus on formatting issues
formatting = analyzer.analyze_formatting(file_path)
if formatting['warning'] > 0:
    print(f"Warning: {formatting['warning']} formatting issues")
```

### Pattern 3: Language Compliance Check
```python
# Check language-specific rules
language = analyzer.analyze_language(file_path)
if language['total_language_issues'] > 0:
    print(f"Fix {language['total_language_issues']} language issues")
```

### Pattern 4: Complete Quality Assessment
```python
# Full analysis with priority issues
result = analyzer.analyze_complete(file_path)
summary = analyzer.get_document_summary(file_path)

for issue in summary['priority_issues'][:3]:
    print(f"[{issue['severity']}] {issue['description']}")
    print(f"  Fix: {issue['fix']}\n")
```

## Error Handling

All tools return consistent error format:

```json
{
  "status": "error",
  "error": "Description of the error"
}
```

**Common Errors**:
- `file_path is required` - Missing required parameter
- `Document file not found` - File doesn't exist
- `Invalid document format` - Not a PDF or DOCX file
- `Failed to process document` - Processing error
- `Text too short for language detection` - Document has <50 characters

## Integration with Claude

### MCP Server Configuration

Tools are exposed via MCP server for Claude integration:

```json
{
  "tools": [
    {
      "name": "upload_document",
      "description": "Upload and validate a document",
      "inputSchema": { ... }
    },
    {
      "name": "process_document",
      "description": "Process document and detect language",
      "inputSchema": { ... }
    },
    // ... other tools
  ]
}
```

### Claude Invocation Example

Claude can invoke tools naturally:

> User: "Analyze this German technical document for quality issues"
> 
> Claude: I'll analyze the document for you. Let me first upload and process it.
> [calls upload_document]
> [calls analyze_complete]
> [calls get_document_summary]
>
> The document has a quality score of 75/100 with 8 total issues:
> - 2 German quotation mark issues
> - 1 heading hierarchy problem
> - 5 other formatting issues
>
> Top priority fixes:
> 1. Replace English quotes with German „"
> 2. Fix heading hierarchy from H1→H3 to H1→H2→H3

## Performance Characteristics

- **upload_document**: <100ms
- **process_document**: <1 second
- **analyze_formatting**: <500ms
- **analyze_language**: <200ms
- **analyze_complete**: <2 seconds
- **get_document_summary**: <2 seconds

## Supported File Types

- **PDF** - Text-based PDFs (not image-based)
- **DOCX** - Microsoft Word documents

## Supported Languages

- **German** (de) - Full formatting + language validation
- **Simplified Chinese** (zh_CN) - Full formatting + language validation
- **English** (en) - Formatting only, no language-specific rules

## Tool Availability

All 6 tools are registered and available:

1. ✅ upload_document
2. ✅ process_document
3. ✅ analyze_formatting
4. ✅ analyze_language
5. ✅ analyze_complete
6. ✅ get_document_summary

## Known Limitations

1. **Text Requirement**: Minimum 50 characters needed for language detection
2. **PDF Limitations**: Image-based PDFs not fully supported
3. **Single Language**: One language per document
4. **No Auto-Fix**: Tools identify issues, don't auto-correct
5. **Pattern-Based**: Uses regex, not full NLP

## Testing

All tools are tested with 26 test cases covering:
- Valid document uploads
- Content extraction
- Formatting analysis
- Language detection
- Complete workflows
- Error handling
- JSON serialization

Test pass rate: 100% (26/26 tests)

## Related Documentation

- **LANGUAGE_RULES.md** - Language-specific rules reference
- **FORMATTING_ANALYSIS.md** - Formatting checks reference
- **ARCHITECTURE.md** - System design
- **DEPLOYMENT.md** - Setup and configuration
