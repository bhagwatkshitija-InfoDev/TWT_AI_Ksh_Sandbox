# API Reference - Document QA Agent

Complete API reference for all MCP tools and configuration options.

## Table of Contents

1. [Analysis Tools](#analysis-tools)
2. [Configuration Tools](#configuration-tools)
3. [Data Types](#data-types)
4. [Error Handling](#error-handling)
5. [Examples](#examples)

## Analysis Tools

These tools are available via MCP protocol for document analysis.

### upload_document

Upload and validate a document file.

**Endpoint**: `upload_document`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | Yes | Path to document (PDF or DOCX) |

**Response**:
```json
{
  "status": "success|error",
  "filename": "document.docx",
  "file_type": "docx",
  "file_size": 45230,
  "message": "Document uploaded successfully: document.docx"
}
```

**Errors**:
- File not found
- Unsupported file type
- File too large (>100MB default)

### process_document

Extract content and detect language from document.

**Endpoint**: `process_document`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | Yes | Path to document |

**Response**:
```json
{
  "status": "success|error",
  "file_type": "docx",
  "language": "de",
  "language_confidence": 0.95,
  "text_sample": "First 300 characters of document...",
  "message": "Document processed: docx detected as de"
}
```

**Errors**:
- File access error
- Document parsing error
- Language detection failed

### analyze_formatting

Analyze document formatting compliance (Phase 2).

**Endpoint**: `analyze_formatting`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | Yes | Path to document |

**Response**:
```json
{
  "status": "success|error",
  "total_formatting_issues": 5,
  "critical": 1,
  "warning": 3,
  "info": 1,
  "by_type": {
    "Font Consistency": 2,
    "Heading Hierarchy": 2,
    "Table Formatting": 1
  },
  "message": "Formatting analysis complete: 5 issues found"
}
```

**Checks**:
- Font consistency
- Heading hierarchy
- Font sizes
- Table formatting
- List formatting
- Image captions
- Cross-references
- Numbering

### analyze_language

Analyze language-specific conventions (Phase 3).

**Endpoint**: `analyze_language`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | Yes | Path to document |

**Response**:
```json
{
  "status": "success|error",
  "language": "de",
  "total_language_issues": 2,
  "message": "Language analysis complete for de: 2 issues found"
}
```

**Language Checks**:

German (de):
- Quotation marks („ and ")
- Umlaut consistency
- German naming conventions
- Dash usage

Chinese (zh_CN):
- Full-width punctuation
- Character spacing
- Traditional vs. Simplified
- Proper spacing rules

### analyze_complete

Complete quality analysis (formatting + language).

**Endpoint**: `analyze_complete`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | Yes | Path to document |

**Response**:
```json
{
  "status": "success|error",
  "language": "de",
  "file_type": "docx",
  "total_issues": 7,
  "formatting_issues": 5,
  "language_issues": 2,
  "quality_score": 78.5,
  "severity_distribution": {
    "critical": 1,
    "warning": 4,
    "info": 2
  },
  "message": "Complete analysis: 7 total issues, quality score 78.5/100"
}
```

### get_document_summary

Get comprehensive analysis summary with priority issues.

**Endpoint**: `get_document_summary`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | Yes | Path to document |

**Response**:
```json
{
  "status": "success|error",
  "language": "de",
  "file_type": "docx",
  "quality_score": 78.5,
  "total_issues": 7,
  "severity_distribution": {
    "critical": 1,
    "warning": 4,
    "info": 2
  },
  "issues_by_type": {
    "Font Consistency": 2,
    "Heading Hierarchy": 2,
    "Table Formatting": 1,
    "Quotation Marks": 2
  },
  "priority_issues": [
    {
      "type": "Font Consistency",
      "severity": "critical",
      "description": "Document uses 8 different fonts",
      "fix": "Limit to 3 fonts maximum"
    }
  ],
  "message": "Summary: de document, quality 78.5/100"
}
```

## Configuration Tools

These tools manage system configuration with full audit trail.

### get_config

Retrieve configuration settings.

**Endpoint**: `get_config`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `section` | string | No | Config section (e.g., 'quality'). Omit for full config |

**Response**:
```json
{
  "status": "success|error",
  "section": "quality",
  "config": {
    "min_language_confidence": 0.7,
    "max_critical_issues": 10,
    "max_warning_issues": 50
  }
}
```

**Available Sections**:
- `document_processing`
- `language_detection`
- `analysis`
- `reporting`
- `quality`
- `mcp`
- `logging`
- `performance`

### get_rules

Retrieve rule definitions.

**Endpoint**: `get_rules`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `rule_file` | string | No | Rule file to retrieve. Omit for all |

**Response**:
```json
{
  "status": "success|error",
  "rule_file": "default_rules.yaml",
  "rules": {
    "formatting_rules": [
      {
        "id": "font_consistency",
        "name": "Font Consistency",
        "severity": "warning",
        "enabled": true,
        "rule_definition": {
          "max_unique_fonts": 3
        }
      }
    ]
  }
}
```

**Available Files**:
- `default_rules.yaml` - Default formatting rules
- `german_conventions.yaml` - German language rules
- `chinese_conventions.yaml` - Chinese language rules

### validate_config

Validate proposed configuration changes.

**Endpoint**: `validate_config`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `proposed_changes` | object | Yes | Configuration changes to validate |

**Response**:
```json
{
  "status": "success|error",
  "is_valid": true,
  "message": "Configuration is valid",
  "changes": {
    "quality": {
      "min_language_confidence": 0.85
    }
  }
}
```

**Validation Rules**:
- Language confidence: 0-1 range
- Severity levels: critical, warning, info only
- File sizes: positive integers
- Rule IDs: must be unique

### update_config

Update configuration with audit trail.

**Endpoint**: `update_config`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `changes` | object | Yes | Configuration changes to apply |
| `reason` | string | No | Reason for change |

**Response**:
```json
{
  "status": "success|error",
  "success": true,
  "message": "Configuration updated successfully",
  "changes": {
    "quality": {
      "min_language_confidence": 0.85
    }
  }
}
```

**Side Effects**:
- Version backup created
- Audit entry logged
- Change callbacks triggered
- Hot-reload activated

### create_rule

Create a new analysis rule.

**Endpoint**: `create_rule`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `rule_file` | string | Yes | Rule file to add to |
| `rule_definition` | object | Yes | Rule definition (see structure) |
| `reason` | string | No | Reason for creating rule |

**Rule Definition Structure**:
```json
{
  "id": "unique_identifier",
  "name": "Human Readable Name",
  "severity": "critical|warning|info",
  "enabled": true,
  "scope": "formatting|structure|language",
  "description": "What this rule checks",
  "rule_definition": {
    "param1": "value1",
    "param2": 10
  },
  "examples": [
    {
      "violation": "Example of violation",
      "correction": "How to fix it"
    }
  ]
}
```

**Response**:
```json
{
  "status": "success|error",
  "success": true,
  "message": "Rule 'custom_check' created successfully",
  "rule_id": "custom_check"
}
```

### get_audit_trail

Retrieve configuration change history.

**Endpoint**: `get_audit_trail`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit` | integer | No | Maximum entries (default: 50) |

**Response**:
```json
{
  "status": "success|error",
  "entries": [
    {
      "timestamp": "2026-09-28T10:30:00.123456",
      "user": "claude",
      "action": "update|create_rule|rollback|reload",
      "changes": { "key": "value" },
      "reason": "optional reason",
      "version": "20260928_103000"
    }
  ],
  "total": 42
}
```

### get_versions

List available configuration versions.

**Endpoint**: `get_versions`

**Parameters**: None

**Response**:
```json
{
  "status": "success|error",
  "versions": [
    "20260928_143000",
    "20260928_140500",
    "20260928_135200"
  ],
  "total": 3
}
```

### rollback_config

Rollback configuration to previous version.

**Endpoint**: `rollback_config`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `version_id` | string | Yes | Version ID (format: YYYYMMDD_HHMMSS) |
| `reason` | string | No | Reason for rollback |

**Response**:
```json
{
  "status": "success|error",
  "success": true,
  "message": "Rolled back to version 20260928_143000",
  "version_id": "20260928_143000"
}
```

**Side Effects**:
- Backup created before rollback
- Configuration restored
- Audit entry logged
- Hot-reload triggered

### reload_config

Reload configuration from disk.

**Endpoint**: `reload_config`

**Parameters**: None

**Response**:
```json
{
  "status": "success|error",
  "success": true,
  "message": "Configuration reloaded from disk"
}
```

**Use Case**: Manual YAML file edits that need to be loaded

## Data Types

### Issue Object

```json
{
  "id": "unique_issue_id",
  "type": "Font Consistency",
  "severity": "critical|warning|info",
  "page": 1,
  "location": "Header in section 1",
  "description": "Font size inconsistent",
  "fix": "Change font size to 14pt",
  "context": "Found Arial 12pt instead of Arial 14pt",
  "coordinates": {
    "x0": 72.0,
    "y0": 100.5,
    "x1": 200.0,
    "y1": 115.0
  }
}
```

### Quality Score

Score ranges from 0-100:
- 90-100: A (Excellent)
- 80-89: B (Good)
- 70-79: C (Acceptable)
- 60-69: D (Poor)
- 0-59: F (Critical Issues)

### Severity Levels

- **critical**: Must fix before publishing
- **warning**: Should fix for quality
- **info**: Nice to fix, informational

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": "Description of error"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "File not found" | Invalid file path | Verify file exists |
| "Unsupported file type" | Not PDF or DOCX | Use supported format |
| "File too large" | Exceeds 100MB | Split into smaller files |
| "Invalid configuration" | Bad config values | Use validate_config first |
| "Rule ID already exists" | Duplicate rule | Use unique ID |
| "Version not found" | Invalid version ID | Check get_versions |

### Error Handling Best Practices

1. Always validate configuration before updating
2. Check file path before processing
3. Handle timeout errors (>30 seconds)
4. Use audit trail to understand failures
5. Verify rollback succeeded

## Examples

### Complete Workflow Example

```python
# 1. Upload and process
upload_result = await analyze_tool("upload_document", {
    "file_path": "document.docx"
})

# 2. Get quick summary
summary = await analyze_tool("get_document_summary", {
    "file_path": "document.docx"
})

# 3. If issues found, get detailed analysis
if summary["total_issues"] > 0:
    details = await analyze_tool("analyze_complete", {
        "file_path": "document.docx"
    })
    
    # 4. Generate reports
    reports = generate_reports(details)

# 5. Update configuration if needed
validation = await config_tool("validate_config", {
    "proposed_changes": {
        "quality": {"min_language_confidence": 0.8}
    }
})

if validation["is_valid"]:
    await config_tool("update_config", {
        "changes": {...},
        "reason": "Improving detection sensitivity"
    })
```

### Configuration Management Example

```python
# View current config
config = await config_tool("get_config", {"section": "quality"})

# Create custom rule
await config_tool("create_rule", {
    "rule_file": "default_rules.yaml",
    "rule_definition": {
        "id": "max_font_size",
        "name": "Maximum Font Size",
        "severity": "warning",
        "enabled": True,
        "rule_definition": {"max_size": 24}
    },
    "reason": "Enforce readable font sizes"
})

# Track changes
audit = await config_tool("get_audit_trail", {"limit": 10})

# Rollback if needed
await config_tool("rollback_config", {
    "version_id": "20260928_143000",
    "reason": "Configuration caused too many false positives"
})
```

---

**Version**: 2.0  
**Last Updated**: 2026-09-28  
**Status**: Production Ready
