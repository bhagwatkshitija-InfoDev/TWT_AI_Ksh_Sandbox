"""Main entry point for Document QA Agent."""

import sys
from pathlib import Path

from claude_mcp_docqa_agent.config import get_settings
from claude_mcp_docqa_agent.database.db_manager import get_db_manager
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


def initialize_application() -> None:
    """Initialize application components."""
    logger.info("Initializing Document QA Agent")

    # Initialize settings
    settings = get_settings()
    logger.info(f"Settings loaded from {settings.CONFIG_DIR}")

    # Initialize database
    db_manager = get_db_manager()
    logger.info("Database initialized")

    logger.info("Application initialized successfully")


def cli() -> int:
    """Command-line interface entry point.

    Returns:
        Exit code
    """
    try:
        initialize_application()
        print("Document QA Agent initialized successfully")
        return 0

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli())
