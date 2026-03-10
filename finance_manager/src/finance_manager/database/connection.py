"""Database connection management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator, Any

from ..core.config import get_config
from ..core.logging import get_logger
from ..core.errors import DatabaseError, ConnectionError

logger = get_logger()


class DatabaseManager:
    """Manages SQLite database connections."""
    
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or get_config().database.path
        self._connection: Optional[sqlite3.Connection] = None
    
    @property
    def db_path(self) -> Path:
        """Get database file path."""
        return Path(self._db_path).expanduser()
    
    def initialize(self) -> None:
        """Initialize database - create directory and file if needed."""
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database if it doesn't exist
        if not self.db_path.exists():
            logger.info(f"Creating new database at {self.db_path}")
            self._create_database()
    
    def _create_database(self) -> None:
        """Create new database with schema."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("PRAGMA foreign_keys = ON")
            conn.close()
            logger.info("Database created successfully")
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to create database: {e}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
                self._connection.execute("PRAGMA foreign_keys = ON")
                self._connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                raise ConnectionError(f"Failed to connect to database: {e}")
        return self._connection
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.debug("Database connection closed")
    
    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL query."""
        try:
            conn = self.get_connection()
            return conn.execute(query, parameters)
        except sqlite3.Error as e:
            raise DatabaseError(f"Query execution failed: {e}")
    
    def executemany(self, query: str, parameters: list) -> sqlite3.Cursor:
        """Execute SQL query with multiple parameter sets."""
        try:
            conn = self.get_connection()
            return conn.executemany(query, parameters)
        except sqlite3.Error as e:
            raise DatabaseError(f"Batch execution failed: {e}")
    
    def commit(self) -> None:
        """Commit current transaction."""
        if self._connection:
            self._connection.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        if self._connection:
            self._connection.rollback()
    
    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database transactions."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def fetch_one(self, query: str, parameters: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch single row."""
        cursor = self.execute(query, parameters)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, parameters: tuple = ()) -> list:
        """Fetch all rows."""
        cursor = self.execute(query, parameters)
        return cursor.fetchall()
    
    def last_row_id(self) -> int:
        """Get last inserted row ID."""
        return self.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.fetch_one(query, (table_name,))
        return result is not None
    
    def get_table_names(self) -> list:
        """Get list of all table names."""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        rows = self.fetch_all(query)
        return [row[0] for row in rows]


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_connection() -> sqlite3.Connection:
    """Get database connection."""
    return get_db_manager().get_connection()
