#!/usr/bin/env python3
"""Analyze documents from TWT_AI_Ksh_Sandbox repository using Document QA Agent."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load configuration for KSH Sandbox
load_dotenv(".env.ksh-sandbox")

from claude_mcp_docqa_agent.config import get_settings
from claude_mcp_docqa_agent.database.db_manager import get_db_manager
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for KSH Sandbox document analysis."""
    try:
        # Initialize settings with KSH Sandbox config
        settings = get_settings()
        logger.info(f"Document QA Agent configured for KSH Sandbox")
        logger.info(f"Source repository: {os.getenv('SOURCE_REPO_PATH')}")
        logger.info(f"Report directory: {settings.REPORT_DIR}")

        # Initialize database
        db_manager = get_db_manager()
        logger.info("Database initialized for KSH Sandbox analysis")

        # Get source repository path
        source_repo = Path(os.getenv("SOURCE_REPO_PATH", "D:/TWT_AI/TWT_AI_Ksh_Sandbox"))

        # Find documents in the repository
        docs_to_analyze = []
        supported_formats = tuple(settings.SUPPORTED_FORMATS)

        for file_path in source_repo.rglob("*"):
            if file_path.suffix.lower() in (f".{fmt}" for fmt in supported_formats):
                docs_to_analyze.append(file_path)

        if docs_to_analyze:
            logger.info(f"Found {len(docs_to_analyze)} documents to analyze:")
            for doc in docs_to_analyze:
                logger.info(f"  - {doc.relative_to(source_repo)}")
            print(f"\nFound {len(docs_to_analyze)} documents ready for analysis")
        else:
            logger.warning("No documents found in the repository")
            print("No documents found in the repository")

        print(f"\nDocument QA Agent is configured for: {source_repo}")
        print(f"Report output: {settings.REPORT_DIR}")
        print("\nAgent is ready to analyze documents from TWT_AI_Ksh_Sandbox")

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
