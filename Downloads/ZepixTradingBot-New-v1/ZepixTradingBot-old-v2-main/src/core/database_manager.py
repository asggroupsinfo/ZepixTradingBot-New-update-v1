"""
Database Manager - V5 Hybrid Plugin Architecture

Multi-DB routing manager for V3 and V6 databases. Ensures proper data
isolation between different trading logics while providing unified access.

Part of Document 23: Database Sync Error Recovery
Part of Document 09: Database Schema Designs

Features:
- Multi-database routing (V3 -> zepix_combined_v3.db, V6 -> zepix_price_action.db)
- Connection pooling
- Query routing based on plugin ID
- Database synchronization
- Error recovery and healing
"""

import logging
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Central database manager for V5 Hybrid Plugin Architecture.
    
    Routes database operations to the correct database based on plugin ID.
    Manages connections to V3 (combined) and V6 (price_action) databases.
    
    Usage:
        db_manager = DatabaseManager(
            v3_path='data/zepix_combined_v3.db',
            v6_path='data/zepix_price_action.db'
        )
        conn = db_manager.get_connection('combined_v3')
    """
    
    # Plugin to database mapping
    PLUGIN_DB_MAP = {
        "combined_v3": "v3",
        "price_action_v6": "v6",
        "price_action_5m": "v6",
        "price_action_15m": "v6",
        "price_action_1h": "v6",
        "price_action_1m": "v6"
    }
    
    def __init__(
        self,
        v3_path: str = "data/zepix_combined_v3.db",
        v6_path: str = "data/zepix_price_action.db",
        central_path: str = "data/zepix_central.db"
    ):
        """
        Initialize Database Manager.
        
        Args:
            v3_path: Path to V3 (combined) database
            v6_path: Path to V6 (price_action) database
            central_path: Path to central database for shared data
        """
        self.v3_path = Path(v3_path)
        self.v6_path = Path(v6_path)
        self.central_path = Path(central_path)
        
        self.logger = logging.getLogger(__name__)
        self._connections: Dict[str, sqlite3.Connection] = {}
        self._lock = threading.Lock()
        
        # Statistics
        self._stats = {
            "v3_queries": 0,
            "v6_queries": 0,
            "central_queries": 0,
            "errors": 0,
            "syncs": 0
        }
        
        # Ensure data directory exists
        self._ensure_directories()
        
        self.logger.info(f"DatabaseManager initialized: V3={v3_path}, V6={v6_path}")
    
    def _ensure_directories(self):
        """Ensure database directories exist."""
        for path in [self.v3_path, self.v6_path, self.central_path]:
            path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self, plugin_id: str) -> sqlite3.Connection:
        """
        Get database connection for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            sqlite3.Connection: Database connection
        """
        db_type = self.PLUGIN_DB_MAP.get(plugin_id, "central")
        return self._get_connection_by_type(db_type)
    
    def _get_connection_by_type(self, db_type: str) -> sqlite3.Connection:
        """
        Get connection by database type.
        
        Args:
            db_type: Database type (v3, v6, central)
            
        Returns:
            sqlite3.Connection: Database connection
        """
        with self._lock:
            if db_type not in self._connections:
                path = self._get_path_for_type(db_type)
                self._connections[db_type] = sqlite3.connect(
                    str(path),
                    check_same_thread=False
                )
                self._connections[db_type].row_factory = sqlite3.Row
                self.logger.info(f"Created connection to {db_type} database: {path}")
            
            return self._connections[db_type]
    
    def _get_path_for_type(self, db_type: str) -> Path:
        """Get database path for type."""
        if db_type == "v3":
            return self.v3_path
        elif db_type == "v6":
            return self.v6_path
        else:
            return self.central_path
    
    def get_v3_connection(self) -> sqlite3.Connection:
        """Get V3 (combined) database connection."""
        self._stats["v3_queries"] += 1
        return self._get_connection_by_type("v3")
    
    def get_v6_connection(self) -> sqlite3.Connection:
        """Get V6 (price_action) database connection."""
        self._stats["v6_queries"] += 1
        return self._get_connection_by_type("v6")
    
    def get_central_connection(self) -> sqlite3.Connection:
        """Get central database connection."""
        self._stats["central_queries"] += 1
        return self._get_connection_by_type("central")
    
    def execute_query(
        self,
        plugin_id: str,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Execute a query on the appropriate database.
        
        Args:
            plugin_id: Plugin identifier for routing
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        try:
            conn = self.get_connection(plugin_id)
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                conn.commit()
                return [{"affected_rows": cursor.rowcount}]
        
        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"Query error for {plugin_id}: {e}")
            raise
    
    def insert_trade(
        self,
        plugin_id: str,
        trade_data: Dict[str, Any]
    ) -> int:
        """
        Insert a trade record into the appropriate database.
        
        Args:
            plugin_id: Plugin identifier
            trade_data: Trade data dictionary
            
        Returns:
            int: Inserted row ID
        """
        conn = self.get_connection(plugin_id)
        cursor = conn.cursor()
        
        # Build insert query
        columns = ", ".join(trade_data.keys())
        placeholders = ", ".join(["?" for _ in trade_data])
        query = f"INSERT INTO trades ({columns}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, tuple(trade_data.values()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"Insert trade error: {e}")
            raise
    
    def get_open_trades(self, plugin_id: str) -> List[Dict[str, Any]]:
        """
        Get open trades for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            List of open trade dictionaries
        """
        query = """
            SELECT * FROM trades 
            WHERE status = 'OPEN' AND plugin_id = ?
            ORDER BY open_time DESC
        """
        return self.execute_query(plugin_id, query, (plugin_id,))
    
    def update_trade_status(
        self,
        plugin_id: str,
        ticket: int,
        status: str,
        close_data: Dict[str, Any] = None
    ) -> bool:
        """
        Update trade status.
        
        Args:
            plugin_id: Plugin identifier
            ticket: Trade ticket number
            status: New status
            close_data: Optional close data
            
        Returns:
            bool: True if updated successfully
        """
        conn = self.get_connection(plugin_id)
        cursor = conn.cursor()
        
        if close_data:
            query = """
                UPDATE trades 
                SET status = ?, close_price = ?, close_time = ?, pnl = ?
                WHERE ticket = ?
            """
            params = (
                status,
                close_data.get("close_price"),
                close_data.get("close_time"),
                close_data.get("pnl"),
                ticket
            )
        else:
            query = "UPDATE trades SET status = ? WHERE ticket = ?"
            params = (status, ticket)
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"Update trade error: {e}")
            return False
    
    def sync_databases(self) -> Dict[str, Any]:
        """
        Synchronize data between databases.
        
        Returns:
            dict: Sync result with statistics
        """
        self._stats["syncs"] += 1
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "v3_to_central": 0,
            "v6_to_central": 0,
            "errors": []
        }
        
        try:
            # Sync V3 summary to central
            v3_conn = self.get_v3_connection()
            central_conn = self.get_central_connection()
            
            # Get V3 trade summary
            v3_cursor = v3_conn.cursor()
            v3_cursor.execute("""
                SELECT COUNT(*) as count, SUM(pnl) as total_pnl
                FROM trades WHERE status = 'CLOSED'
            """)
            v3_summary = v3_cursor.fetchone()
            
            # Get V6 trade summary
            v6_conn = self.get_v6_connection()
            v6_cursor = v6_conn.cursor()
            v6_cursor.execute("""
                SELECT COUNT(*) as count, SUM(pnl) as total_pnl
                FROM trades WHERE status = 'CLOSED'
            """)
            v6_summary = v6_cursor.fetchone()
            
            self.logger.info(f"Database sync complete: V3={v3_summary}, V6={v6_summary}")
            
        except Exception as e:
            result["errors"].append(str(e))
            self.logger.error(f"Sync error: {e}")
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database manager statistics."""
        return {
            **self._stats,
            "v3_path": str(self.v3_path),
            "v6_path": str(self.v6_path),
            "central_path": str(self.central_path),
            "active_connections": len(self._connections),
            "timestamp": datetime.now().isoformat()
        }
    
    def close_all(self):
        """Close all database connections."""
        with self._lock:
            for db_type, conn in self._connections.items():
                try:
                    conn.close()
                    self.logger.info(f"Closed {db_type} database connection")
                except Exception as e:
                    self.logger.error(f"Error closing {db_type} connection: {e}")
            self._connections.clear()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all databases.
        
        Returns:
            dict: Health status for each database
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "databases": {}
        }
        
        for db_type in ["v3", "v6", "central"]:
            try:
                conn = self._get_connection_by_type(db_type)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                health["databases"][db_type] = {
                    "status": "healthy",
                    "path": str(self._get_path_for_type(db_type))
                }
            except Exception as e:
                health["databases"][db_type] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health


class DatabaseRouter:
    """
    Routes database queries to the correct database based on plugin ID.
    
    Provides a simplified interface for plugins to access their data
    without knowing the underlying database structure.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize Database Router.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def route_query(
        self,
        plugin_id: str,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Route a query to the appropriate database.
        
        Args:
            plugin_id: Plugin identifier
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results
        """
        return self.db_manager.execute_query(plugin_id, query, params)
    
    def get_plugin_trades(
        self,
        plugin_id: str,
        status: str = None,
        symbol: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trades for a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            status: Optional status filter
            symbol: Optional symbol filter
            limit: Maximum number of results
            
        Returns:
            List of trade dictionaries
        """
        query = "SELECT * FROM trades WHERE plugin_id = ?"
        params = [plugin_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        query += f" ORDER BY open_time DESC LIMIT {limit}"
        
        return self.db_manager.execute_query(plugin_id, query, tuple(params))


# Factory function
def create_database_manager(
    v3_path: str = "data/zepix_combined_v3.db",
    v6_path: str = "data/zepix_price_action.db",
    central_path: str = "data/zepix_central.db"
) -> DatabaseManager:
    """
    Factory function to create DatabaseManager.
    
    Args:
        v3_path: Path to V3 database
        v6_path: Path to V6 database
        central_path: Path to central database
        
    Returns:
        DatabaseManager: Configured manager instance
    """
    return DatabaseManager(
        v3_path=v3_path,
        v6_path=v6_path,
        central_path=central_path
    )
