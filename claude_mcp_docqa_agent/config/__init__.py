"""Configuration management for the Document QA Agent."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """Application settings."""

    # Paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    STORAGE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "storage"
    )
    CONFIG_DIR: Path = Field(default_factory=lambda: Path(__file__).parent)
    DATABASE_PATH: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data" / "docqa.db"
    )

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'docqa.db'}"
    )

    # Processing
    SUPPORTED_FORMATS: list[str] = ["pdf", "docx"]
    SUPPORTED_LANGUAGES: list[str] = ["de", "zh_CN"]
    MAX_FILE_SIZE_MB: int = 100

    # Language Detection
    LANGUAGE_DETECTION_MIN_CONFIDENCE: float = 0.7

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")

    # Report
    REPORT_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "reports"
    )
    ENABLE_PDF_REPORTS: bool = True
    ENABLE_HTML_REPORTS: bool = True
    ENABLE_JSON_REPORTS: bool = True

    # MCP
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 8000

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs) -> None:
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)

        # Create required directories
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORT_DIR.mkdir(parents=True, exist_ok=True)

        logger.info(f"Settings initialized. Base directory: {self.BASE_DIR}")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings instance
    """
    global _settings

    if _settings is None:
        _settings = Settings()

    return _settings
