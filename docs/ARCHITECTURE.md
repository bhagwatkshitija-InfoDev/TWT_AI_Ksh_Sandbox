# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code + Claude API                      │
│              (User Interaction & Intelligence Layer)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ (Claude Messages API)
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              MCP Server (Document QA Agent)                       │
│                                                                   │
│   Tools Layer (Phase 4)                                           │
│   • upload_document()     • detect_language()                    │
│   • extract_content()     • analyze_formatting()                 │
│   • validate_compliance() • generate_report()                    │
│                                                                   │
│   ↓                                                               │
│                                                                   │
│   Document Processing Engine (Phase 1) ✅                        │
│   ├─ PDF Extractor → pdfplumber, pypdf                          │
│   ├─ DOCX Parser → python-docx                                  │
│   ├─ Content Processor → normalize & structure                  │
│   └─ Metadata Extractor → file properties                       │
│                                                                   │
│   ↓                                                               │
│                                                                   │
│   Analysis Engine (Phase 2-3)                                    │
│   ├─ Language Detector (Phase 1) ✅                              │
│   ├─ Formatting Analyzer (Phase 2)                              │
│   │  ├─ Font & Size Checker                                     │
│   │  ├─ Heading Hierarchy Validator                             │
│   │  ├─ Table Structure Analyzer                                │
│   │  ├─ Numbering & List Checker                                │
│   │  ├─ Caption & Cross-ref Validator                           │
│   │  └─ Image Analysis                                          │
│   └─ Language Rules Engine (Phase 3)                            │
│      ├─ German Rules → quotes, numbers, caps                    │
│      └─ Chinese Rules → punctuation, widths, fonts              │
│                                                                   │
│   ↓                                                               │
│                                                                   │
│   Storage & Configuration (Phase 1) ✅                           │
│   ├─ SQLite Database (documents, issues, rules)                │
│   ├─ YAML Config (style rules, preferences)                    │
│   └─ Cache (processing results)                                 │
│                                                                   │
│   ↓                                                               │
│                                                                   │
│   Report Generation Engine (Phase 5)                            │
│   ├─ JSON Serializer                                            │
│   ├─ HTML/CSS Template Renderer                                 │
│   └─ PDF Report Exporter                                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Document Processing Engine (Phase 1) ✅

#### PDF Extractor (`pdf_extractor.py`)
**Purpose**: Extract content from PDF files with coordinate tracking

**Key Methods**:
- `extract_full_text()` - All text from all pages
- `extract_page_content(page_number)` - Specific page with coordinates
- `extract_all_tables()` - Table structures
- `extract_structured_content()` - Complete page-by-page breakdown
- `extract_metadata()` - PDF properties

**Implementation**:
- Uses `pdfplumber` for coordinate-aware extraction
- Preserves character positions for visual markup
- Handles multi-page documents efficiently

#### DOCX Parser (`docx_parser.py`)
**Purpose**: Parse DOCX files with formatting preservation

**Key Methods**:
- `extract_full_text()` - Complete text
- `extract_paragraphs()` - With style and run-level formatting
- `extract_tables()` - With structure information
- `extract_headings()` - With hierarchy levels
- `extract_font_usage()` - Font statistics
- `extract_metadata()` - Document properties

**Implementation**:
- Uses `python-docx` for native DOCX support
- Preserves all formatting attributes
- Tracks font names and sizes

#### Content Processor (`content_processor.py`)
**Purpose**: Unified interface for processing both PDF and DOCX

**Key Methods**:
- `process_document()` - Detects type and processes
- `get_text_for_analysis()` - Extract text for analysis
- `get_page_count()` - Total pages/sections

**Implementation**:
- Auto-detects file type by extension
- Integrates language detection
- Returns normalized structure

#### Metadata Extractor (`metadata_extractor.py`)
**Purpose**: Extract and normalize document metadata

**Key Methods**:
- `extract_metadata()` - Type-specific metadata
- `get_text_sample()` - Sample for language detection

**Implementation**:
- Handles both PDF and DOCX
- Provides normalized output format

### 2. Analysis Engine (Phase 2-3)

#### Language Detector (`analysis/language_detector.py`) (Phase 1) ✅
**Purpose**: Detect document language with fallback mechanisms

**Key Methods**:
- `detect_language(text)` - Primary + fallback detection
- `normalize_language_code(code)` - Standardize codes
- `is_german()`, `is_chinese()` - Convenience checks
- `validate_detection()` - Check confidence threshold

**Implementation**:
- Primary: `langdetect` (fast, accurate)
- Fallback: `textblob` (if primary fails)
- Returns confidence scores and alternatives

#### Formatting Analyzer (Phase 2) - *To Be Implemented*
**Purpose**: Check formatting compliance

**Planned Methods**:
- `analyze_fonts()` - Font consistency
- `analyze_heading_hierarchy()` - Structure validation
- `analyze_tables()` - Table formatting
- `analyze_lists()` - Numbering and formatting
- `analyze_images()` - Captions and references

#### German Rules Engine (Phase 3) - *To Be Implemented*
**Purpose**: Check German-specific conventions

**Planned Checks**:
- Quotation marks („" vs "")
- Number formatting (1.000,00)
- Capitalization (all nouns)
- Umlauts (ä, ö, ü not ae, oe, ue)
- Hyphenation rules

#### Chinese Rules Engine (Phase 3) - *To Be Implemented*
**Purpose**: Check Chinese-specific conventions

**Planned Checks**:
- Punctuation marks (，。！？)
- Full-width vs half-width characters
- Font consistency (SimSun, SimHei)
- Spacing rules (CJK vs Latin)
- Proper Chinese characters only

### 3. Storage & Configuration (Phase 1) ✅

#### Database Schema (`database/models.py`)
**Core Tables**:
- `documents` - Document metadata and status
- `processing_results` - Cached extraction results
- `formatting_issues` - Formatting violations
- `language_issues` - Language convention violations
- `style_rules` - Configurable rules
- `reports` - Generated reports

#### Database Manager (`database/db_manager.py`)
**Purpose**: SQLAlchemy session and initialization management

**Key Methods**:
- `initialize()` - Create tables and engine
- `get_session()` - New database session
- `close()` - Cleanup

#### Configuration System (`config.py`)
**Purpose**: Centralized settings management

**Settings**:
- Paths (storage, database, config)
- Database URL
- Supported formats and languages
- Processing limits
- Report generation options
- MCP server settings
- Logging configuration

**Implementation**:
- Pydantic for validation
- Environment variable support
- Auto-creates directories on init

### 4. Configuration Files (Phase 1) ✅

#### `config/default_rules.yaml`
Generic formatting rules for all documents

#### `config/german_conventions.yaml`
German-specific conventions:
- Quotation marks
- Number formatting
- Capitalization
- Spacing rules
- Terminology

#### `config/chinese_conventions.yaml`
Chinese-specific conventions:
- Punctuation marks
- Character widths
- Font selection
- Spacing and line breaking
- Number formatting

#### `config/settings.yaml`
Application configuration:
- Processing options
- Analysis settings
- Report generation
- MCP server settings
- Performance tuning

### 5. Report Generation Engine (Phase 5) - *To Be Implemented*

#### Report Builder
**Purpose**: Aggregate findings and create reports

**Planned Features**:
- Deduplicate issues
- Severity stratification
- Page number tracking
- Recommendations

#### Exporters
- JSON exporter - Machine-readable format
- HTML exporter - Interactive, visual
- PDF exporter - Printable format

### 6. Utilities (Phase 1) ✅

#### Logger (`utils/logger.py`)
- Loguru-based logging
- Console + file output
- Rotating files
- Structured logs

#### Validators (`utils/validators.py`)
- File existence checking
- Format validation
- Language code validation

#### Helpers (`utils/helpers.py`)
- Document ID generation
- JSON save/load
- Text normalization

#### Error Handling (`errors/exceptions.py`)
Custom exception hierarchy for specific error types

## Data Flow

```
User Document
      ↓
validate_document_path()
      ↓
Determine File Type (.pdf or .docx)
      ↓
Extract Content
  ├─ PDFExtractor or DOCXParser
  └─ Returns: pages, text, tables, formatting
      ↓
Detect Language
  └─ LanguageDetector.detect_language()
      ├─ langdetect (primary)
      └─ textblob (fallback)
      ↓
Store in Database
  └─ ProcessingResult, Document metadata
      ↓
Analyze Content (Phase 2-3)
  ├─ Formatting Analysis
  ├─ German Rules Check
  └─ Chinese Rules Check
      ↓
Generate Report
  ├─ Deduplicate findings
  ├─ Severity scoring
  └─ Export (JSON, HTML, PDF)
      ↓
Return to Claude Agent
```

## Database Schema Details

### documents table
```sql
id (PK)              - Unique document ID
filename             - Original filename
file_type            - 'pdf' or 'docx'
language             - Detected language
language_confidence  - Detection confidence
total_pages          - Page count
upload_date          - Timestamp
processing_status    - pending|processing|complete|error
error_message        - Error details if failed
hash                 - Content hash for deduplication
```

### formatting_issues table
```sql
id (PK)              - Issue ID
document_id (FK)     - Document reference
page_number          - Where issue occurs
issue_type           - font|size|heading|table|list|etc
severity             - critical|warning|info
location_description - Text description of location
issue_description    - Detailed issue text
recommended_fix      - Suggested correction
coordinates          - JSON: {x, y, width, height} for visual markup
detected_date        - Timestamp
```

### language_issues table
```sql
id (PK)              - Issue ID
document_id (FK)     - Document reference
page_number          - Where issue occurs
language             - 'de' or 'zh_CN'
rule_violated        - german_quotes|chinese_punctuation|etc
severity             - critical|warning|info
context              - Example text showing violation
suggested_replacement - How to fix it
issue_description    - Detailed description
detected_date        - Timestamp
```

## Phase Implementation Roadmap

| Phase | Component | Status | Effort |
|-------|-----------|--------|--------|
| 1 | Project Setup | ✅ | - |
| 1 | PDF Extractor | ✅ | 4h |
| 1 | DOCX Parser | ✅ | 4h |
| 1 | Language Detector | ✅ | 3h |
| 1 | Database Schema | ✅ | 3h |
| 1 | Configuration System | ✅ | 2h |
| 1 | Unit Tests | ✅ | 4h |
| 2 | Formatting Analyzer | 🚧 | 8h |
| 3 | German Rules Engine | 🚧 | 6h |
| 3 | Chinese Rules Engine | 🚧 | 6h |
| 4 | MCP Server | 🚧 | 8h |
| 5 | Report Generation | 🚧 | 8h |
| 6 | Configuration UI | 🚧 | 4h |
| 7 | Testing & Docs | 🚧 | 6h |
| 8 | Deployment | 🚧 | 4h |

## Key Design Decisions

1. **SQLite for Local Storage**
   - Rationale: Zero setup, file-based, sufficient for typical volumes
   - Alternative: PostgreSQL (overkill for this use case)

2. **MCP for Claude Integration**
   - Rationale: Native integration, no custom API needed
   - Alternative: REST API (more work, same functionality)

3. **Pydantic for Configuration**
   - Rationale: Type-safe, validation, environment support
   - Alternative: ConfigParser (less powerful)

4. **YAML for Style Rules**
   - Rationale: Human-readable, hot-reloadable, version-controllable
   - Alternative: JSON (less readable)

5. **Coordinate Tracking in PDFs**
   - Rationale: Enables visual markup and navigation
   - Alternative: None - important for UX

6. **Dual Language Detection**
   - Rationale: Redundancy, handles edge cases
   - Alternative: Single method (unreliable)

## Extension Points

### Adding a New Language
1. Create `config/{language}_conventions.yaml`
2. Create `analysis/language_rules/{language}_rules.py`
3. Update `LanguageDetector.normalize_language_code()`
4. Update `Settings.SUPPORTED_LANGUAGES`

### Adding a New Formatting Check
1. Create method in `FormattingAnalyzer` (Phase 2)
2. Add rule to `config/default_rules.yaml`
3. Create database table if needed
4. Create corresponding test

### Adding a New Report Format
1. Create exporter class in `report_generation/`
2. Implement export logic
3. Update `generate_report()` tool
4. Update settings

## Testing Strategy

- **Unit Tests**: Isolated component testing with fixtures
- **Integration Tests**: End-to-end document processing
- **Fixture Files**: Sample DOCX/PDF for testing
- **Coverage Target**: >80% for core modules

## Performance Considerations

- **Caching**: Processed documents cached in SQLite
- **Parallel Processing**: Page-by-page analysis (Phase 2)
- **Memory**: Stream processing for large PDFs
- **Database Indexes**: On frequently queried columns

## Security Considerations

- **Local Processing**: No cloud storage or transmission
- **File Validation**: Strict format checking
- **Error Messages**: No sensitive data in logs
- **Database**: Local SQLite, no network access
