# Language-Specific Rules - Phase 3 Reference

## Overview

Phase 3 implements comprehensive language-specific rule checking for German and Chinese documents. These rules validate conventions, spelling, formatting, and language-specific requirements that the generic formatting analyzer cannot detect.

## Architecture

```
DocumentQualityAnalyzer (Phase 2 + Phase 3)
    ├─ FormattingAnalyzer (Phase 2)
    │   └─ 10+ formatting checks
    └─ LanguageRulesAnalyzer (Phase 3)
        ├─ GermanRulesEngine
        │   ├─ Quotation marks
        │   ├─ Number formatting
        │   ├─ Capitalization
        │   ├─ Umlaut usage
        │   └─ Spacing rules
        └─ ChineseRulesEngine
            ├─ Punctuation marks
            ├─ Character width
            ├─ Traditional characters
            └─ CJK spacing
```

## German Rules Engine

### GermanRulesEngine

Validates German language conventions.

```python
from claude_mcp_docqa_agent.analysis.language_rules.german_rules import GermanRulesEngine

engine = GermanRulesEngine(document_content)
issues = engine.analyze()
summary = engine.get_summary()
```

### Checks Implemented

#### 1. Quotation Marks (german_quotation_marks)
**Severity**: Warning

German documents should use „" (double-low-9 and double-high-reversed-9) for quotation marks, not "" (English quotes).

**Example**:
- ❌ Wrong: He said "Guten Morgen"
- ✅ Correct: He said „Guten Morgen"

#### 2. Number Formatting (german_number_format)
**Severity**: Warning

German uses period (.) for thousands separator and comma (,) for decimal separator, opposite of English.

**Example**:
- ❌ Wrong: The value is 1,234.56
- ✅ Correct: The value is 1.234,56

**Format**: `[1-3 digits].[3 digits].[3 digits],...,[2 digits]`

#### 3. Capitalization (german_capitalization)
**Severity**: Info

All German nouns must be capitalized. Common words in English text should follow German rules.

**Example**:
- ❌ Wrong: Das dokument enthält...
- ✅ Correct: Das Dokument enthält...

#### 4. Umlaut Usage (german_umlauts)
**Severity**: Info

German umlauts (ä, ö, ü) must be used instead of substitutes (ae, oe, ue).

**Example**:
- ❌ Wrong: Größe, Schätzen (incorrect if written as Groesse, Schaetzen)
- ✅ Correct: Größe, Schätzen

#### 5. Spacing Rules (german_spacing)
**Severity**: Info

German spacing: no space before punctuation, space after punctuation.

**Example**:
- ❌ Wrong: Das ist wichtig : sehr wichtig !
- ✅ Correct: Das ist wichtig: sehr wichtig!

### Usage Example

```python
from claude_mcp_docqa_agent.analysis.language_rules.german_rules import GermanRulesEngine

# Create engine with document content
engine = GermanRulesEngine(document_data["content"])

# Run analysis
issues = engine.analyze()

# Get summary
summary = engine.get_summary()
print(f"Quotation mark issues: {summary['quotation_marks']}")
print(f"Number format issues: {summary['number_format']}")
print(f"Capitalization issues: {summary['capitalization']}")
print(f"Umlaut issues: {summary['umlauts']}")
print(f"Spacing issues: {summary['spacing']}")
```

## Chinese Rules Engine

### ChineseRulesEngine

Validates Simplified Chinese (中文) language conventions.

```python
from claude_mcp_docqa_agent.analysis.language_rules.chinese_rules import ChineseRulesEngine

engine = ChineseRulesEngine(document_content)
issues = engine.analyze()
summary = engine.get_summary()
```

### Checks Implemented

#### 1. Punctuation Marks (chinese_punctuation)
**Severity**: Warning

Chinese documents should use Chinese punctuation marks (，。！？：；) instead of English equivalents.

**Character Mapping**:
| English | Chinese | Character |
|---------|---------|-----------|
| , | ， | U+FF0C |
| . | 。 | U+3002 |
| ! | ！ | U+FF01 |
| ? | ？ | U+FF1F |
| : | ： | U+FF1A |
| ; | ； | U+FF1B |

**Example**:
- ❌ Wrong: 这是中文文本, 但使用了英文标点。
- ✅ Correct: 这是中文文本，但使用了中文标点。

#### 2. Character Width (chinese_character_width)
**Severity**: Info

Numbers and punctuation should be full-width in Chinese text.

**Example**:
- ❌ Wrong: １２３个文件 (full-width) or １２３个文件 (mixed)
- ✅ Correct: 123个文件 (half-width within Chinese) or １２３個文件 (full-width for consistency)

#### 3. Traditional Characters (chinese_traditional_chars)
**Severity**: Warning

Simplified Chinese documents should use Simplified characters only (GB2312/GBK).

**Common Mappings**:
| Traditional | Simplified |
|-------------|-----------|
| 這 | 这 |
| 個 | 个 |
| 來 | 来 |
| 對 | 对 |
| 會 | 会 |
| 傳 | 传 |
| 參 | 参 |
| 詳 | 详 |

**Example**:
- ❌ Wrong: 這是繁體中文
- ✅ Correct: 这是简体中文

#### 4. CJK Spacing (chinese_spacing)
**Severity**: Info

Proper spacing between Chinese/Japanese/Korean (CJK) characters and Latin characters.

**Example**:
- ❌ Wrong: 这是HTML标记 (no space)
- ✅ Correct: 这是 HTML 标记 (with spaces)

### Usage Example

```python
from claude_mcp_docqa_agent.analysis.language_rules.chinese_rules import ChineseRulesEngine

# Create engine with document content
engine = ChineseRulesEngine(document_data["content"])

# Run analysis
issues = engine.analyze()

# Get summary
summary = engine.get_summary()
print(f"Punctuation issues: {summary['punctuation']}")
print(f"Character width issues: {summary['character_width']}")
print(f"Traditional character issues: {summary['traditional_chars']}")
print(f"Spacing issues: {summary['spacing']}")
```

## Unified Analyzers

### LanguageRulesAnalyzer

Automatically applies language-specific rules based on detected language.

```python
from claude_mcp_docqa_agent.analysis.language_rules_analyzer import LanguageRulesAnalyzer

analyzer = LanguageRulesAnalyzer(document_data)
issues = analyzer.analyze()  # Applies German or Chinese rules

summary = analyzer.get_summary()
```

### DocumentQualityAnalyzer

Combines formatting (Phase 2) and language rules (Phase 3) analysis.

```python
from claude_mcp_docqa_agent.analysis.document_quality_analyzer import DocumentQualityAnalyzer

analyzer = DocumentQualityAnalyzer(document_data)

# Complete analysis (formatting + language rules)
result = analyzer.analyze_complete()

# Access results
formatting_issues = result["formatting_issues"]
language_issues = result["language_issues"]
all_issues = result["all_issues"]
summary = result["summary"]

# Filter and analyze
critical = analyzer.get_issues_by_severity("critical")
page_1 = analyzer.get_issues_by_page(1)
german_quotes = analyzer.get_issues_by_type("german_quotation_marks")

# Quality scoring
score = analyzer.get_quality_score()  # 0-100, 100 = perfect
priority = analyzer.get_priority_issues(top_n=5)
```

## Issue Types Summary

### German Issues

| Issue Type | Severity | Description |
|-----------|----------|-------------|
| `german_quotation_marks` | warning | English quotes instead of „" |
| `german_number_format` | warning | English number format instead of German |
| `german_capitalization` | info | Lowercase nouns or improper capitalization |
| `german_umlauts` | info | Umlaut substitutes (ae, oe, ue) |
| `german_spacing` | info | Improper spacing around punctuation |

### Chinese Issues

| Issue Type | Severity | Description |
|-----------|----------|-------------|
| `chinese_punctuation` | warning | English punctuation in Chinese text |
| `chinese_character_width` | info | Half-width where full-width expected |
| `chinese_traditional_chars` | warning | Traditional characters (should be simplified) |
| `chinese_spacing` | info | Missing spaces between CJK and Latin |

## Complete Workflow

```python
from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.document_quality_analyzer import DocumentQualityAnalyzer

# Step 1: Process document (Phase 1)
processor = ContentProcessor("document.docx")
document_data = processor.process_document()

# Step 2: Comprehensive quality analysis (Phase 2 + 3)
analyzer = DocumentQualityAnalyzer(document_data)
result = analyzer.analyze_complete()

# Step 3: Review results
print(f"Language: {result['summary']['language']}")
print(f"Total issues: {result['summary']['total_issues']}")
print(f"Quality score: {analyzer.get_quality_score():.1f}/100")

# Step 4: Get details
for issue in analyzer.get_priority_issues(top_n=5):
    print(f"\n[{issue.severity}] {issue.issue_type}")
    print(f"  Location: {issue.location_description}")
    print(f"  Problem: {issue.issue_description}")
    print(f"  Fix: {issue.recommended_fix}")
```

## Configuration

Language rules are configured in YAML files:

- `config/german_conventions.yaml` - German rules
- `config/chinese_conventions.yaml` - Chinese rules

Rules can be:
- Enabled/disabled individually
- Customized severity levels
- Modified with regex patterns
- Extended with new rules

## Performance

- **Analysis Time**: <500ms for typical document
- **Memory**: ~1-5MB per document
- **Scalability**: Parallel processing capable
- **Database**: Results can be persisted

## Testing

```bash
# Run Phase 3 tests only
pytest tests/test_language_rules.py -v

# Run specific test class
pytest tests/test_language_rules.py::TestGermanRulesEngine -v

# Run integration tests
pytest tests/test_language_rules.py::TestLanguageRulesIntegration -v

# Run all tests (Phases 1-3)
pytest tests/ -v
```

## Known Limitations

1. **Pattern-based Detection**: Rules use regex patterns, not full NLP
2. **Context-Unaware**: May not understand context-specific exceptions
3. **No Auto-Fix**: Only identifies issues, does not auto-correct
4. **Language Mixing**: Assumes single language per document

## Future Enhancements

- Machine learning for context-aware detection
- Multi-language document support
- Automatic issue fixing
- Custom rule creation UI
- Advanced NLP-based analysis

## Related Documentation

- **ARCHITECTURE.md** - System design
- **FORMATTING_ANALYSIS.md** - Phase 2 formatting checks
- **QUICK_START_PHASE2.md** - Usage examples
- **Phase 3 Summary** - Implementation details
