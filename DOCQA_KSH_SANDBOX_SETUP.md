# Document QA Agent Setup for TWT_AI_Ksh_Sandbox

## Overview
The Document QA Agent is now configured to analyze documents from the TWT_AI_Ksh_Sandbox repository.

## Quick Start

### 1. Run the Agent
```bash
python analyze_ksh_sandbox.py
```

This will:
- Initialize the Document QA Agent with KSH Sandbox configuration
- Scan the repository for documents (PDF, DOCX, Markdown)
- Prepare analysis reports in `reports/ksh_sandbox/`

### 2. Configuration
The agent uses `.env.ksh-sandbox` for configuration, which includes:
- **Source Repository**: `D:/TWT_AI/TWT_AI_Ksh_Sandbox`
- **Database**: `data/docqa_ksh_sandbox.db` (separate from main agent)
- **Reports**: `reports/ksh_sandbox/` (HTML, JSON, PDF)
- **Logs**: `logs/ksh_sandbox/`

### 3. Supported Document Formats
- **PDF** (.pdf)
- **Microsoft Word** (.docx)
- **Markdown** (.md)

### 4. Language Support
- German (de)
- Chinese (zh_CN)
- English (en)

### 5. Supported Analyses
The agent checks for:
- **Formatting**: Font consistency, heading hierarchy, table formatting, list formatting
- **Language Conventions**: German and Chinese-specific formatting rules
- **Cross-references**: Proper linking and numbering
- **Image captions**: Documentation completeness

## Repository Structure
```
D:\TWT_AI\TWT_AI_Ksh_Sandbox/     # Cloned repository
D:\TWT_AI\.env.ksh-sandbox        # Configuration file
D:\TWT_AI\analyze_ksh_sandbox.py  # Analysis script
D:\TWT_AI\reports/ksh_sandbox/    # Analysis reports (output)
```

## Available Reports
After analysis, the following reports are generated:
- **HTML Report** (`report.html`) - Interactive visualization
- **JSON Report** (`report.json`) - Machine-readable format
- **PDF Report** (`report.pdf`) - Printable document

## Configuration Options
Edit `.env.ksh-sandbox` to customize:
- Document sources (`SOURCE_REPO_PATH`)
- Report output location (`REPORT_DIR`)
- Database location (`DATABASE_URL`)
- Language settings (`SUPPORTED_LANGUAGES`)
- Analysis options (enable/disable specific checks)

## Database
Each analysis repository has its own database:
- **Main Agent**: `data/docqa.db`
- **KSH Sandbox**: `data/docqa_ksh_sandbox.db`

This allows independent tracking of analysis history.

## Logging
Logs are stored in `logs/ksh_sandbox/` with:
- **Level**: INFO (configurable in `.env.ksh-sandbox`)
- **Rotation**: 500 MB per file
- **Retention**: 7 days
- **Output**: Console + file

## Current Status
✅ Agent initialized
✅ Repository cloned
✅ Configuration complete
✅ Found 1 document ready for analysis

## Next Steps
1. Run `python analyze_ksh_sandbox.py` to generate analysis reports
2. View reports in `reports/ksh_sandbox/`
3. Use analysis results to improve document quality in the sandbox repository
4. Update `.env.ksh-sandbox` as needed for different analysis requirements
