"""
Base Schema Definitions and Utilities

Document 09: Database Schema Designs
Provides base classes and utilities for database schema management.
"""

import sqlite3
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseSchema(ABC):
    """
    Abstract base class for database schemas.
    
    All database schema classes should inherit from this class
    and implement the required methods.
    """
    
    DB_DIR = "data"
    
    def __init__(self, db_path: str):
        """
        Initialize schema with database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    @abstractmethod
    def get_schema_sql(self) -> List[str]:
        """
        Get list of SQL statements to create the schema.
        
        Returns:
            List of SQL CREATE TABLE statements
        """
        pass
    
    @abstractmethod
    def get_indexes_sql(self) -> List[str]:
        """
        Get list of SQL statements to create indexes.
        
        Returns:
            List of SQL CREATE INDEX statements
        """
        pass
    
    def create_schema(self) -> bool:
        """
        Create the database schema.
        
        Returns:
            True if schema created successfully
        """
        try:
            os.makedirs(self.DB_DIR, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            for sql in self.get_schema_sql():
                cursor.execute(sql)
            
            # Create indexes
            for sql in self.get_indexes_sql():
                try:
                    cursor.execute(sql)
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        raise
            
            conn.commit()
            conn.close()
            
            logger.info(f"Schema created for {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating schema for {self.db_path}: {e}")
            return False
    
    def connect(self) -> sqlite3.Connection:
        """
        Get database connection.
        
        Returns:
            SQLite connection object
        """
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_tables(self) -> List[str]:
        """
        Get list of tables in the database.
        
        Returns:
            List of table names
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table
            
        Returns:
            True if table exists
        """
        return table_name in self.get_tables()
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column info dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "default": row[4],
                "pk": row[5]
            })
        return columns
    
    def get_row_count(self, table_name: str) -> int:
        """
        Get row count for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]


class SchemaManager:
    """
    Manages all database schemas.
    
    Provides utilities for creating, validating, and managing
    all databases in the system.
    """
    
    DB_DIR = "data"
    
    # Database paths
    V3_DB_PATH = "data/zepix_combined.db"
    V6_DB_PATH = "data/zepix_price_action.db"
    CENTRAL_DB_PATH = "data/zepix_bot.db"
    
    def __init__(self):
        """Initialize schema manager."""
        self.logger = logging.getLogger(__name__)
    
    def create_all_databases(self) -> Dict[str, bool]:
        """
        Create all databases with their schemas.
        
        Returns:
            Dictionary of database names and creation status
        """
        from .v3_database import V3Schema
        from .v6_database import V6Schema
        from .central_database import CentralSchema
        
        results = {}
        
        # Create V3 database
        v3_schema = V3Schema(self.V3_DB_PATH)
        results["v3_combined"] = v3_schema.create_schema()
        
        # Create V6 database
        v6_schema = V6Schema(self.V6_DB_PATH)
        results["v6_price_action"] = v6_schema.create_schema()
        
        # Create Central database
        central_schema = CentralSchema(self.CENTRAL_DB_PATH)
        results["central"] = central_schema.create_schema()
        
        return results
    
    def validate_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all database schemas.
        
        Returns:
            Dictionary of validation results
        """
        from .v3_database import V3Schema
        from .v6_database import V6Schema
        from .central_database import CentralSchema
        
        results = {}
        
        # Validate V3
        if os.path.exists(self.V3_DB_PATH):
            v3_schema = V3Schema(self.V3_DB_PATH)
            results["v3_combined"] = {
                "exists": True,
                "tables": v3_schema.get_tables(),
                "valid": len(v3_schema.get_tables()) >= 4
            }
        else:
            results["v3_combined"] = {"exists": False, "tables": [], "valid": False}
        
        # Validate V6
        if os.path.exists(self.V6_DB_PATH):
            v6_schema = V6Schema(self.V6_DB_PATH)
            results["v6_price_action"] = {
                "exists": True,
                "tables": v6_schema.get_tables(),
                "valid": len(v6_schema.get_tables()) >= 6
            }
        else:
            results["v6_price_action"] = {"exists": False, "tables": [], "valid": False}
        
        # Validate Central
        if os.path.exists(self.CENTRAL_DB_PATH):
            central_schema = CentralSchema(self.CENTRAL_DB_PATH)
            results["central"] = {
                "exists": True,
                "tables": central_schema.get_tables(),
                "valid": len(central_schema.get_tables()) >= 4
            }
        else:
            results["central"] = {"exists": False, "tables": [], "valid": False}
        
        return results
    
    def get_database_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all databases.
        
        Returns:
            Dictionary of database statistics
        """
        from .v3_database import V3Schema
        from .v6_database import V6Schema
        from .central_database import CentralSchema
        
        stats = {}
        
        # V3 stats
        if os.path.exists(self.V3_DB_PATH):
            v3_schema = V3Schema(self.V3_DB_PATH)
            stats["v3_combined"] = {
                "path": self.V3_DB_PATH,
                "size_bytes": os.path.getsize(self.V3_DB_PATH),
                "tables": len(v3_schema.get_tables())
            }
        
        # V6 stats
        if os.path.exists(self.V6_DB_PATH):
            v6_schema = V6Schema(self.V6_DB_PATH)
            stats["v6_price_action"] = {
                "path": self.V6_DB_PATH,
                "size_bytes": os.path.getsize(self.V6_DB_PATH),
                "tables": len(v6_schema.get_tables())
            }
        
        # Central stats
        if os.path.exists(self.CENTRAL_DB_PATH):
            central_schema = CentralSchema(self.CENTRAL_DB_PATH)
            stats["central"] = {
                "path": self.CENTRAL_DB_PATH,
                "size_bytes": os.path.getsize(self.CENTRAL_DB_PATH),
                "tables": len(central_schema.get_tables())
            }
        
        return stats


def create_all_databases() -> Dict[str, bool]:
    """
    Convenience function to create all databases.
    
    Returns:
        Dictionary of database names and creation status
    """
    manager = SchemaManager()
    return manager.create_all_databases()


def get_database_info() -> Dict[str, Any]:
    """
    Get information about all databases.
    
    Returns:
        Dictionary with database information
    """
    manager = SchemaManager()
    return {
        "validation": manager.validate_all_schemas(),
        "stats": manager.get_database_stats()
    }
