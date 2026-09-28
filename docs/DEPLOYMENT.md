# Deployment Guide

## Prerequisites

- **Operating System**: Windows 11, 10, or later / macOS / Linux
- **Python**: 3.11 or higher
- **Disk Space**: 2GB for dependencies and database
- **Memory**: 4GB RAM recommended
- **Internet**: Required for initial dependency installation

## Windows Installation

### Step 1: Verify Python Installation

```powershell
python --version
# Should show Python 3.11 or higher
```

If Python is not installed, download from https://www.python.org/downloads/

### Step 2: Clone or Navigate to Project

```powershell
cd D:\TWT_AI
```

### Step 3: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install all required packages including:
- Document processing (pdfplumber, python-docx)
- Language detection (langdetect, textblob)
- Database (sqlalchemy)
- MCP and Claude integration

### Step 5: Initialize Application

```powershell
python -m claude_mcp_docqa_agent.main
```

You should see:
```
INFO     | claude_mcp_docqa_agent.config:__init__:70 - Settings initialized. Base directory: D:\TWT_AI
INFO     | claude_mcp_docqa_agent.database.db_manager:initialize:45 - Database initialized: sqlite:///D:\TWT_AI\data\docqa.db
INFO     | claude_mcp_docqa_agent.main:initialize_application:13 - Initializing Document QA Agent
INFO     | claude_mcp_docqa_agent.main:initialize_application:20 - Application initialized successfully
Document QA Agent initialized successfully
```

### Step 6: Run Tests (Optional)

```powershell
pytest tests/ -v
```

All tests should pass with green checkmarks.

## macOS/Linux Installation

### Step 1: Verify Python

```bash
python3 --version
# Should show Python 3.11 or higher
```

### Step 2: Navigate to Project

```bash
cd /path/to/TWT_AI
```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Initialize Application

```bash
python -m claude_mcp_docqa_agent.main
```

### Step 6: Run Tests

```bash
pytest tests/ -v
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` for your environment (optional):

```
DATABASE_URL=sqlite:///./data/docqa.db
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=100
LANGUAGE_DETECTION_MIN_CONFIDENCE=0.7
```

### Style Rules

Customize style rules in `claude_mcp_docqa_agent/config/`:

- **default_rules.yaml** - Generic rules
- **german_conventions.yaml** - German language rules
- **chinese_conventions.yaml** - Chinese language rules
- **settings.yaml** - Application settings

No restart needed - rules are loaded at runtime.

## Directory Structure After Installation

```
D:\TWT_AI\
├── venv/                    # Virtual environment
├── claude_mcp_docqa_agent/  # Application code
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── logs/                    # Log files (created at runtime)
├── data/                    # Database (created at runtime)
│   └── docqa.db            # SQLite database
├── reports/                 # Generated reports (created at runtime)
├── storage/                 # File storage
│   └── cache/              # Cache directory
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project metadata
├── README.md               # Overview
└── .env                    # Environment variables (optional)
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pdfplumber'"

**Solution**: Activate virtual environment and reinstall dependencies

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Database file is locked"

**Solution**: Ensure no other instances are running, then:

```powershell
python -c "from claude_mcp_docqa_agent.database.db_manager import get_db_manager; get_db_manager().close()"
```

### Issue: "Language detection not working"

**Solution**: Provide longer text sample (minimum 50 characters)

```python
from claude_mcp_docqa_agent.analysis.language_detector import LanguageDetector

detector = LanguageDetector()
# Use text longer than 50 characters
result = detector.detect_language(long_text_here)
```

### Issue: PDF extraction returns empty text

**Solution**: Some PDFs are image-based and require OCR (not yet implemented)

Workaround: Check PDF.metadata for information about PDF type

### Issue: "Permission denied" on Windows

**Solution**: Run PowerShell as Administrator

```powershell
# Right-click PowerShell and select "Run as administrator"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Updating

To update to the latest version:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests to verify
pytest tests/ -v
```

## Uninstalling

To completely remove the application:

```powershell
# Deactivate virtual environment
deactivate

# Remove virtual environment directory
Remove-Item -Recurse -Force venv

# Remove data directory (optional, keeps database)
Remove-Item -Recurse -Force data

# Remove logs (optional)
Remove-Item -Recurse -Force logs

# Remove reports (optional)
Remove-Item -Recurse -Force reports
```

## Performance Tuning

### For Large Documents (500+ pages)

Edit `claude_mcp_docqa_agent/config/settings.yaml`:

```yaml
performance:
  cache_results: true
  parallel_processing: true
  max_parallel_pages: 2  # Reduce if memory constrained
```

### For Limited Memory (<4GB)

```yaml
performance:
  parallel_processing: false
  cache_results: true
```

### Database Optimization

For large document collections, periodically vacuum the database:

```python
from claude_mcp_docqa_agent.database.db_manager import get_db_manager

db = get_db_manager()
db.engine.execute("VACUUM")
```

## MCP Server Deployment (Phase 4)

### Running as MCP Server

```powershell
python -m claude_mcp_docqa_agent.mcp_server
```

Server will start on `127.0.0.1:8000` (configurable in `.env`)

### Integration with Claude Code

Configure in Claude Code settings:

```json
{
  "mcp_servers": {
    "doc-qa": {
      "command": "python",
      "args": ["-m", "claude_mcp_docqa_agent.mcp_server"],
      "type": "stdio"
    }
  }
}
```

## Logging

Logs are written to `logs/docqa_YYYY-MM-DD.log`

### View Recent Logs

```powershell
Get-Content logs/docqa_*.log | Select-Object -Last 100
```

### Change Log Level

Edit `.env`:

```
LOG_LEVEL=DEBUG  # More verbose
LOG_LEVEL=ERROR  # Less verbose
```

## Backup

### Backup Database

```powershell
Copy-Item data/docqa.db backup/docqa_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

### Backup Configuration

```powershell
Copy-Item -Recurse claude_mcp_docqa_agent/config backup/config_$(Get-Date -Format 'yyyyMMdd')
```

## System Requirements

### Minimum
- Python 3.11
- 2GB RAM
- 2GB disk space
- Windows 7+, macOS 10.13+, Linux (any modern distro)

### Recommended
- Python 3.11+
- 4GB+ RAM
- 5GB+ disk space
- Windows 11, macOS 12+, Linux (recent kernel)

### For Large-Scale Processing
- 8GB+ RAM
- 10GB+ disk space (for document cache)
- SSD recommended for database performance

## Support

For issues, check:

1. **README.md** - Overview and basic usage
2. **ARCHITECTURE.md** - System design and components
3. **Test output** - `pytest tests/ -v`
4. **Log files** - `logs/docqa_*.log`

## Next Steps After Installation

1. **Phase 2**: Wait for formatting analysis implementation
2. **Phase 3**: Use German/Chinese rule engines when available
3. **Phase 4**: Connect to Claude via MCP server
4. **Phase 5**: Generate formatted reports

See README.md for current implementation status.
