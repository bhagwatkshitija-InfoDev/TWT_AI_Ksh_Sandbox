"""Logging configuration and utilities."""

import sys
from pathlib import Path

from loguru import logger as _logger

# Configure loguru
_logger.remove()  # Remove default handler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Console handler
_logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# File handler
_logger.add(
    LOG_DIR / "docqa_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="500 MB",
    retention="7 days",
)


def get_logger(name: str) -> "loguru.Logger":  # type: ignore
    """Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return _logger.bind(name=name)
