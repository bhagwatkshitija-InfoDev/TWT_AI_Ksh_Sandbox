"""Helper utilities."""

import hashlib
import json
from pathlib import Path
from typing import Any

from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


def generate_document_id(file_path: str) -> str:
    """Generate unique document ID from file path and content hash.

    Args:
        file_path: Path to the document

    Returns:
        Unique document ID
    """
    path = Path(file_path)
    file_hash = hashlib.md5(path.read_bytes()).hexdigest()[:8]
    timestamp = path.stat().st_mtime_ns
    doc_id = f"{path.stem}_{file_hash}_{timestamp}"
    return doc_id


def save_json(data: Any, output_path: str) -> str:
    """Save data as JSON file.

    Args:
        data: Data to serialize
        output_path: Output file path

    Returns:
        Path to saved file
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved JSON to {path}")
    return str(path)


def load_json(file_path: str) -> Any:
    """Load JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    path = Path(file_path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded JSON from {path}")
    return data


def normalize_text(text: str) -> str:
    """Normalize text for consistent comparison.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    import unicodedata

    nfkd_form = unicodedata.normalize("NFKD", text)
    return nfkd_form.encode("ascii", "ignore").decode("ascii")
