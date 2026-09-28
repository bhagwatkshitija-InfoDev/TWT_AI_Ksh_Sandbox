"""Database manager for SQLAlchemy operations."""

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from claude_mcp_docqa_agent.config import get_settings
from claude_mcp_docqa_agent.database.models import Base
from claude_mcp_docqa_agent.errors.exceptions import DatabaseError
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, database_url: Optional[str] = None) -> None:
        """Initialize the database manager.

        Args:
            database_url: Optional SQLAlchemy database URL. Uses settings if not provided.
        """
        settings = get_settings()
        self.database_url = database_url or settings.DATABASE_URL
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

    def initialize(self) -> None:
        """Initialize database connection and create tables."""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Database initialized: {self.database_url}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy Session

        Raises:
            DatabaseError: If SessionLocal is not initialized
        """
        if self.SessionLocal is None:
            raise DatabaseError("Database not initialized. Call initialize() first.")

        return self.SessionLocal()

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance.

    Returns:
        DatabaseManager instance
    """
    global _db_manager

    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.initialize()

    return _db_manager
