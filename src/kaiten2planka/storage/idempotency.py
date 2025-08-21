"""Idempotency tracking with SQLite storage."""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@dataclass
class MigrationRecord:
    """Record of a migrated entity."""
    kaiten_id: str
    planka_id: str
    entity_type: str
    migrated_at: datetime
    checksum: str


@dataclass
class ErrorRecord:
    """Record of migration error."""
    kaiten_id: str
    entity_type: str
    error_message: str
    occurred_at: datetime


class IdempotencyStore:
    """SQLite-based storage for migration tracking."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS mapping (
                    kaiten_id TEXT NOT NULL,
                    planka_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    migrated_at TIMESTAMP NOT NULL,
                    checksum TEXT NOT NULL,
                    PRIMARY KEY (kaiten_id, entity_type)
                );
                
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kaiten_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    occurred_at TIMESTAMP NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_mapping_kaiten 
                ON mapping(kaiten_id, entity_type);
                
                CREATE INDEX IF NOT EXISTS idx_errors_kaiten 
                ON errors(kaiten_id, entity_type);
            """)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def is_migrated(self, kaiten_id: str, entity_type: str, checksum: str) -> Optional[str]:
        """
        Check if entity is already migrated.
        
        Args:
            kaiten_id: Kaiten entity ID
            entity_type: Type of entity
            checksum: Current entity checksum
            
        Returns:
            Planka ID if already migrated with same checksum, None otherwise
        """
        with self._get_connection() as conn:
            result = conn.execute(
                "SELECT planka_id, checksum FROM mapping WHERE kaiten_id = ? AND entity_type = ?",
                (kaiten_id, entity_type)
            ).fetchone()
            
            if result and result['checksum'] == checksum:
                return result['planka_id']
                
        return None
    
    def record_migration(
        self, 
        kaiten_id: str, 
        planka_id: str, 
        entity_type: str, 
        checksum: str
    ) -> None:
        """
        Record successful migration.
        
        Args:
            kaiten_id: Kaiten entity ID
            planka_id: Created Planka entity ID
            entity_type: Type of entity
            checksum: Entity checksum
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO mapping 
                (kaiten_id, planka_id, entity_type, migrated_at, checksum)
                VALUES (?, ?, ?, ?, ?)
                """,
                (kaiten_id, planka_id, entity_type, datetime.now(), checksum)
            )
            conn.commit()
            
        logger.debug(f"Recorded migration: {kaiten_id} -> {planka_id}")
    
    def record_error(self, kaiten_id: str, entity_type: str, error_message: str) -> None:
        """
        Record migration error.
        
        Args:
            kaiten_id: Kaiten entity ID that failed
            entity_type: Type of entity
            error_message: Error description
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO errors (kaiten_id, entity_type, error_message, occurred_at)
                VALUES (?, ?, ?, ?)
                """,
                (kaiten_id, entity_type, error_message, datetime.now())
            )
            conn.commit()
            
        logger.warning(f"Recorded error for {kaiten_id}: {error_message}")
    
    def get_migration_stats(self) -> Dict[str, int]:
        """Get migration statistics."""
        with self._get_connection() as conn:
            stats = {}
            
            # Count by entity type
            result = conn.execute(
                "SELECT entity_type, COUNT(*) as count FROM mapping GROUP BY entity_type"
            ).fetchall()
            
            for row in result:
                stats[f"migrated_{row['entity_type']}"] = row['count']
            
            # Count errors
            error_count = conn.execute("SELECT COUNT(*) as count FROM errors").fetchone()
            stats['errors'] = error_count['count']
            
        return stats
