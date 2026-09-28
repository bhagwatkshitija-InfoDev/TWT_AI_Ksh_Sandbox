# Claude MCP Document QA Agent - User Guide

Complete guide to using the Document QA Agent for analyzing documents in German and Chinese.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Workflows](#core-workflows)
4. [Configuration](#configuration)
5. [Report Generation](#report-generation)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Overview

The Claude MCP Document QA Agent is a sophisticated document analysis system that:

- **Accepts** DOCX and PDF documents
- **Detects** language automatically (German, Simplified Chinese, English)
- **Validates** formatting compliance (fonts, sizes, headings, tables, lists)
- **Checks** language-specific conventions (German quotes, Chinese punctuation)
- **Generates** reports in JSON, HTML, and PDF formats
- **Manages** configuration via MCP tools with full audit trail
- **Integrates** seamlessly with Claude via the Model Context Protocol

### Key Features

✨ **Multi-Language Support**
- Automatic language detection
- German-specific formatting rules
- Chinese-specific formatting rules
- English as fallback

✨ **Comprehensive Analysis**
- 10+ formatting checks
- Language convention validation
- Quality scoring (0-100)
- Issue severity levels (critical, warning, info)

✨ **Professional Reports**
- Structured JSON export
- Interactive HTML with styling
- Multi-page PDF with formatting
- Audit trail with user attribution

✨ **Dynamic Configuration**
- Update rules without restart
- Version history and rollback
- Configuration validation
- Complete audit trail

## Quick Start

### 1. Upload and Analyze a Document

```python
from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.document_quality_analyzer import DocumentQualityAnalyzer

# Process document
processor = ContentProcessor("path/to/document.docx")
doc_data = processor.process_document()

# Analyze document
analyzer = DocumentQualityAnalyzer(doc_data)
result = analyzer.analyze_complete()

# View results
print(f"Language: {analyzer.language}")
print(f"Quality Score: {analyzer.get_quality_score():.1f}/100")
print(f"Total Issues: {len(analyzer.all_issues)}")
```

### 2. Generate Reports

```python
from claude_mcp_docqa_agent.report_generation import ReportManager, AnalysisData

# Create analysis data from analyzer
analysis_data = AnalysisData(
    document_path="path/to/document.docx",
    language=analyzer.language,
    file_type=analyzer.file_type,
    quality_score=analyzer.get_quality_score(),
    total_issues=len(analyzer.all_issues),
    critical_count=len(analyzer.get_issues_by_severity("critical")),
    warning_count=len(analyzer.get_issues_by_severity("warning")),
    info_count=len(analyzer.get_issues_by_severity("info")),
    formatting_issues=analyzer.formatting_issues,
    language_issues=analyzer.language_issues,
    all_issues=analyzer.all_issues,
    issues_by_type=result["summary"].get("by_type", {}),
)

# Generate reports
manager = ReportManager()
reports = manager.generate_all_formats(analysis_data)

print(f"JSON: {reports['json']}")
print(f"HTML: {reports['html']}")
print(f"PDF: {reports['pdf']}")
```

### 3. Via Claude MCP Tools

All analysis and configuration can be done via MCP tools when using Claude:

```python
# Analysis tools (Phase 4)
- upload_document(file_path)
- process_document(file_path)
- analyze_formatting(file_path)
- analyze_language(file_path)
- analyze_complete(file_path)
- get_document_summary(file_path)

# Configuration tools (Phase 6)
- get_config(section)
- get_rules(rule_file)
- validate_config(proposed_changes)
- update_config(changes, reason)
- create_rule(rule_file, rule_definition, reason)
- get_audit_trail(limit)
- get_versions()
- rollback_config(version_id, reason)
- reload_config()
```

## Core Workflows

### Workflow 1: Single Document Analysis

**Goal**: Analyze a document and get quality feedback

**Steps**:
1. Upload document via `upload_document` tool
2. Process with `process_document` tool
3. Analyze with `analyze_complete` tool
4. Get summary with `get_document_summary` tool
5. Review priority issues in response

**Time**: ~2 seconds per document
**Output**: Quality score, issue list, recommendations

### Workflow 2: Batch Document Analysis

**Goal**: Analyze multiple documents and generate reports

**Steps**:
1. For each document:
   - Call `analyze_complete(file_path)`
   - Generate reports with ReportManager
   - Store results
2. Compare quality scores across documents
3. Identify common issues

### Workflow 3: Configuration Adjustment

**Goal**: Update analysis rules based on findings

**Steps**:
1. View current config: `get_config()`
2. Validate changes: `validate_config(proposed_changes)`
3. Apply changes: `update_config(changes, reason)`
4. Verify via audit trail: `get_audit_trail()`

### Workflow 4: Rule Customization

**Goal**: Create custom analysis rules for specific needs

**Steps**:
1. View existing rules: `get_rules("default_rules.yaml")`
2. Design new rule matching the structure
3. Create rule: `create_rule("default_rules.yaml", rule_definition, reason)`
4. Re-analyze documents with new rule

### Workflow 5: Troubleshooting with Rollback

**Goal**: Revert configuration if issues arise

**Steps**:
1. View versions: `get_versions()`
2. Review audit trail: `get_audit_trail()`
3. Rollback if needed: `rollback_config(version_id, reason)`
4. Verify with re-analysis

## Configuration

### Configuration Structure

Configuration is stored in YAML files:

```yaml
# settings.yaml - Main settings
document_processing:
  supported_formats: ["pdf", "docx"]
  max_file_size_mb: 100

language_detection:
  min_confidence: 0.7

analysis:
  check_font_consistency: true
  check_heading_hierarchy: true
  check_german_conventions: true
  check_chinese_conventions: true

reporting:
  generate_json: true
  generate_html: true
  generate_pdf: true

quality:
  min_language_confidence: 0.7
  max_critical_issues: 10
  max_warning_issues: 50
```

### Common Configuration Changes

**Increase Language Confidence Threshold**
```python
await claude_tool("update_config", {
    "changes": {
        "quality": {
            "min_language_confidence": 0.85
        }
    },
    "reason": "Require higher confidence for language detection"
})
```

**Disable German Checks**
```python
await claude_tool("update_config", {
    "changes": {
        "analysis": {
            "check_german_conventions": false
        }
    },
    "reason": "Document is not in German"
})
```

**Update Quality Thresholds**
```python
await claude_tool("update_config", {
    "changes": {
        "quality": {
            "max_critical_issues": 5,
            "max_warning_issues": 25
        }
    },
    "reason": "Stricter quality requirements"
})
```

### Creating Custom Rules

Rule structure:
```yaml
- id: unique_rule_id
  name: "Human Readable Name"
  severity: warning  # critical, warning, info
  enabled: true
  scope: formatting  # or structure, language, etc.
  description: "What this rule checks"
  rule_definition:
    # Rule-specific parameters
    max_value: 10
    required_pattern: "some regex"
  examples:
    - violation: "What a violation looks like"
      correction: "How to fix it"
```

Example: Create a rule for maximum table columns
```python
new_rule = {
    "id": "max_table_columns",
    "name": "Maximum Table Columns",
    "severity": "warning",
    "enabled": True,
    "scope": "formatting",
    "description": "Ensure tables don't exceed maximum columns",
    "rule_definition": {
        "max_columns": 6
    }
}

await claude_tool("create_rule", {
    "rule_file": "default_rules.yaml",
    "rule_definition": new_rule,
    "reason": "Enforce maximum table width for readability"
})
```

## Report Generation

### Report Formats

**JSON** - Structured data export
- Complete analysis data
- Machine-readable format
- Ideal for programmatic processing
- File size: ~5-10 KB per document

**HTML** - Interactive web report
- Professional styling
- Responsive design
- Sortable issue tables
- Print-friendly CSS
- Light/dark mode support
- File size: ~20-50 KB per document

**PDF** - Professional document
- Multi-page formatted report
- Cover page with quality score
- Table of contents
- Styled issue listings
- Print-ready format
- File size: ~50-100 KB per document

### Report Contents

All reports include:
- Document metadata (path, language, file type)
- Quality score (0-100) with grade (A-F)
- Issue statistics (total, by severity, by type)
- Severity distribution (critical, warning, info)
- Issue details (description, location, recommended fix)
- Audit trail (in admin panel)

### Customizing Reports

Configure report generation:
```python
from claude_mcp_docqa_agent.report_generation import ReportManager, ReportConfig
from pathlib import Path

config = ReportConfig(
    title="Company Document Review",
    author="QA Team",
    theme="dark",
    include_toc=True,
    include_statistics=True,
    output_dir=Path("reports")
)

manager = ReportManager(config)
reports = manager.generate_all_formats(analysis_data)
```

## Advanced Usage

### Analyzing Specific Languages

**German Documents**
- Automatic detection
- German quotation marks („ and ")
- German naming conventions
- Umlaut handling

**Chinese Documents**
- Automatic detection (Simplified Chinese)
- Full-width punctuation checks
- Proper character spacing
- Traditional vs. Simplified awareness

**English Documents**
- Fallback language
- Standard quotation marks
- English conventions

### Filtering Issues

```python
# Get issues by severity
critical = analyzer.get_issues_by_severity("critical")
warnings = analyzer.get_issues_by_severity("warning")

# Get issues by type
font_issues = analyzer.get_issues_by_type("Font Consistency")
heading_issues = analyzer.get_issues_by_type("Heading Hierarchy")

# Get issues by page
page1_issues = analyzer.get_issues_by_page(1)

# Get issues by phase
formatting = analyzer.get_issues_by_phase(2)
language = analyzer.get_issues_by_phase(3)
```

### Performance Optimization

**For Large Documents**:
- Process in chunks
- Cache results
- Use parallel processing

**For Batch Operations**:
- Use configuration for defaults
- Batch report generation
- Archive old reports

### Integration with External Tools

**Export to CSV**
```python
import csv

with open("issues.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Page", "Type", "Severity", "Description", "Fix"])
    for issue in analyzer.all_issues:
        writer.writerow([
            issue.page_number,
            issue.issue_type,
            issue.severity,
            issue.issue_description,
            issue.recommended_fix
        ])
```

**Send to Slack**
```python
import json

summary = analyzer.get_summary()
message = f"""
📄 Document Analysis Complete
Quality Score: {analyzer.get_quality_score():.1f}/100
Critical Issues: {summary['critical']}
Warnings: {summary['warning']}
"""

# Send to Slack webhook
```

## Troubleshooting

### Document Not Detected Correctly

**Problem**: Language detected as wrong language

**Solutions**:
1. Add more text to document (minimum 50 characters)
2. Increase `min_language_confidence` threshold
3. Manually override language in config

### Missing Expected Issues

**Problem**: Analyzer didn't find issues you expect

**Solutions**:
1. Check if rule is enabled: `get_config("analysis")`
2. Review rule definition: `get_rules("default_rules.yaml")`
3. Create custom rule if needed
4. Check severity level (critical vs. warning vs. info)

### Configuration Changes Not Applied

**Problem**: Updated config but old behavior persists

**Solutions**:
1. Verify update was successful: `get_audit_trail()`
2. Check current config: `get_config()`
3. Reload configuration: `reload_config()`
4. Restart application if changes still not applied

### Report Generation Failed

**Problem**: Reports not generating or incomplete

**Solutions**:
1. Check output directory has write permissions
2. Verify analysis completed successfully
3. Check available disk space
4. Try generating single format instead of all

### Performance Issues

**Problem**: Analysis taking longer than expected

**Solutions**:
1. Check document file size
2. Reduce number of enabled checks
3. Disable PDF generation (slowest)
4. Use HTML or JSON only
5. Check system resources

## Support and Documentation

- **API Reference**: See `docs/API_REFERENCE.md`
- **Configuration Guide**: See `docs/CONFIGURATION.md`
- **MCP Tools**: See `docs/MCP_TOOLS.md`
- **Architecture**: See `docs/ARCHITECTURE.md`

---

**Version**: 6.0  
**Last Updated**: 2026-09-28  
**Status**: Production Ready
