"""
Central System Database Schema

Document 09: Database Schema Designs
Implements the Central System database schema with:
- plugins_registry: Pre-populated plugin registry
- aggregated_trades: Auto-synced from per-plugin DBs
- system_config: Pre-populated system configuration
- system_events: System event logging
"""

import sqlite3
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .schemas import BaseSchema

logger = logging.getLogger(__name__)


class EventSeverity(Enum):
    """Event severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CentralSchema(BaseSchema):
    """
    Central System Database Schema.
    
    Database: data/zepix_bot.db
    
    Tables:
    - plugins_registry: Pre-populated with 5 plugins
    - aggregated_trades: Auto-synced from V3/V6 databases
    - system_config: Pre-populated system configuration
    - system_events: System event logging
    """
    
    def get_schema_sql(self) -> List[str]:
        """Get Central schema SQL statements."""
        return [
            # plugins_registry table
            """
            CREATE TABLE IF NOT EXISTS plugins_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT UNIQUE NOT NULL,
                plugin_type TEXT CHECK(plugin_type IN ('V3_COMBINED', 'V6_PRICE_ACTION')),
                display_name TEXT NOT NULL,
                description TEXT,
                version TEXT DEFAULT '1.0.0',
                enabled BOOLEAN DEFAULT 1,
                database_path TEXT,
                config_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # aggregated_trades table
            """
            CREATE TABLE IF NOT EXISTS aggregated_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                plugin_type TEXT CHECK(plugin_type IN ('V3_COMBINED', 'V6_PRICE_ACTION')),
                source_trade_id INTEGER NOT NULL,
                mt5_ticket INTEGER,
                symbol TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('BUY', 'SELL')),
                lot_size REAL,
                entry_price REAL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                exit_price REAL,
                profit_pips REAL,
                profit_dollars REAL,
                status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')),
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plugin_id) REFERENCES plugins_registry(plugin_id)
            )
            """,
            
            # system_config table
            """
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                config_type TEXT CHECK(config_type IN ('string', 'integer', 'float', 'boolean', 'json')),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # system_events table
            """
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                severity TEXT CHECK(severity IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
                source TEXT,
                message TEXT NOT NULL,
                details TEXT,
                acknowledged BOOLEAN DEFAULT 0
            )
            """
        ]
    
    def get_indexes_sql(self) -> List[str]:
        """Get Central index SQL statements."""
        return [
            "CREATE INDEX IF NOT EXISTS idx_plugins_enabled ON plugins_registry(enabled)",
            "CREATE INDEX IF NOT EXISTS idx_agg_trades_plugin ON aggregated_trades(plugin_id)",
            "CREATE INDEX IF NOT EXISTS idx_agg_trades_status ON aggregated_trades(status)",
            "CREATE INDEX IF NOT EXISTS idx_agg_trades_symbol ON aggregated_trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_agg_trades_synced ON aggregated_trades(synced_at)",
            "CREATE INDEX IF NOT EXISTS idx_events_severity ON system_events(severity)",
            "CREATE INDEX IF NOT EXISTS idx_events_time ON system_events(event_time)",
            "CREATE INDEX IF NOT EXISTS idx_events_type ON system_events(event_type)"
        ]
    
    def create_schema(self) -> bool:
        """
        Create the database schema with pre-populated data.
        
        Returns:
            True if schema created successfully
        """
        result = super().create_schema()
        
        if result:
            self._populate_plugins_registry()
            self._populate_system_config()
        
        return result
    
    def _populate_plugins_registry(self) -> None:
        """Pre-populate plugins registry with 5 plugins."""
        conn = self.connect()
        cursor = conn.cursor()
        
        plugins = [
            {
                "plugin_id": "combined_v3",
                "plugin_type": "V3_COMBINED",
                "display_name": "V3 Combined Logic",
                "description": "Combined V3 logic with 12 signal types and dual order support",
                "database_path": "data/zepix_combined.db",
                "config_path": "config/plugins/combined_v3.json"
            },
            {
                "plugin_id": "price_action_1m",
                "plugin_type": "V6_PRICE_ACTION",
                "display_name": "V6 Price Action 1M",
                "description": "1-minute scalping strategy (ORDER B only, 0.5x SL, 60min max)",
                "database_path": "data/zepix_price_action.db",
                "config_path": "config/plugins/price_action_1m.json"
            },
            {
                "plugin_id": "price_action_5m",
                "plugin_type": "V6_PRICE_ACTION",
                "display_name": "V6 Price Action 5M",
                "description": "5-minute momentum strategy (ORDER A + B, 1.0x SL, 240min max)",
                "database_path": "data/zepix_price_action.db",
                "config_path": "config/plugins/price_action_5m.json"
            },
            {
                "plugin_id": "price_action_15m",
                "plugin_type": "V6_PRICE_ACTION",
                "display_name": "V6 Price Action 15M",
                "description": "15-minute intraday strategy (ORDER A only, 1.5x SL, 480min max)",
                "database_path": "data/zepix_price_action.db",
                "config_path": "config/plugins/price_action_15m.json"
            },
            {
                "plugin_id": "price_action_1h",
                "plugin_type": "V6_PRICE_ACTION",
                "display_name": "V6 Price Action 1H",
                "description": "1-hour swing strategy (ORDER A only, 2.0x SL, 1440min max)",
                "database_path": "data/zepix_price_action.db",
                "config_path": "config/plugins/price_action_1h.json"
            }
        ]
        
        for plugin in plugins:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO plugins_registry 
                    (plugin_id, plugin_type, display_name, description, database_path, config_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    plugin["plugin_id"], plugin["plugin_type"], plugin["display_name"],
                    plugin["description"], plugin["database_path"], plugin["config_path"]
                ))
            except sqlite3.IntegrityError:
                pass  # Plugin already exists
        
        conn.commit()
        self.close()
        logger.info("Plugins registry pre-populated with 5 plugins")
    
    def _populate_system_config(self) -> None:
        """Pre-populate system configuration."""
        conn = self.connect()
        cursor = conn.cursor()
        
        configs = [
            {
                "key": "bot_version",
                "value": "5.0.0",
                "description": "Current bot version",
                "config_type": "string"
            },
            {
                "key": "architecture",
                "value": "V5_HYBRID_PLUGIN",
                "description": "System architecture type",
                "config_type": "string"
            },
            {
                "key": "v3_enabled",
                "value": "true",
                "description": "V3 Combined Logic plugin enabled",
                "config_type": "boolean"
            },
            {
                "key": "v6_enabled",
                "value": "true",
                "description": "V6 Price Action plugins enabled",
                "config_type": "boolean"
            },
            {
                "key": "sync_interval_minutes",
                "value": "5",
                "description": "Database sync interval in minutes",
                "config_type": "integer"
            },
            {
                "key": "max_open_trades_per_plugin",
                "value": "10",
                "description": "Maximum open trades per plugin",
                "config_type": "integer"
            },
            {
                "key": "telegram_rate_limit_per_minute",
                "value": "20",
                "description": "Telegram messages per minute limit",
                "config_type": "integer"
            },
            {
                "key": "last_sync_time",
                "value": "",
                "description": "Last database sync timestamp",
                "config_type": "string"
            }
        ]
        
        for config in configs:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO system_config 
                    (key, value, description, config_type)
                    VALUES (?, ?, ?, ?)
                """, (
                    config["key"], config["value"],
                    config["description"], config["config_type"]
                ))
            except sqlite3.IntegrityError:
                pass  # Config already exists
        
        conn.commit()
        self.close()
        logger.info("System config pre-populated")


class CentralDatabase:
    """
    Central System Database Manager.
    
    Provides operations for plugin registry, aggregated trades,
    system configuration, and event logging.
    """
    
    DB_PATH = "data/zepix_bot.db"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Central database.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or self.DB_PATH
        self.schema = CentralSchema(self.db_path)
        self.logger = logging.getLogger(__name__)
        
        # Ensure schema exists
        if not os.path.exists(self.db_path):
            self.schema.create_schema()
    
    def connect(self) -> sqlite3.Connection:
        """Get database connection."""
        return self.schema.connect()
    
    def close(self) -> None:
        """Close database connection."""
        self.schema.close()
    
    # =========================================================================
    # Plugin Registry Operations
    # =========================================================================
    
    def get_all_plugins(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all registered plugins.
        
        Args:
            enabled_only: If True, return only enabled plugins
            
        Returns:
            List of plugin dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if enabled_only:
            cursor.execute("SELECT * FROM plugins_registry WHERE enabled = 1")
        else:
            cursor.execute("SELECT * FROM plugins_registry")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin dictionary or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM plugins_registry WHERE plugin_id = ?", (plugin_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if enabled successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE plugins_registry SET enabled = 1, updated_at = ? WHERE plugin_id = ?",
            (datetime.now().isoformat(), plugin_id)
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if disabled successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE plugins_registry SET enabled = 0, updated_at = ? WHERE plugin_id = ?",
            (datetime.now().isoformat(), plugin_id)
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def register_plugin(self, plugin_data: Dict[str, Any]) -> bool:
        """
        Register a new plugin.
        
        Args:
            plugin_data: Plugin data dictionary
            
        Returns:
            True if registered successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO plugins_registry 
                (plugin_id, plugin_type, display_name, description, database_path, config_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                plugin_data.get("plugin_id"),
                plugin_data.get("plugin_type"),
                plugin_data.get("display_name"),
                plugin_data.get("description"),
                plugin_data.get("database_path"),
                plugin_data.get("config_path")
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    # =========================================================================
    # Aggregated Trades Operations
    # =========================================================================
    
    def add_aggregated_trade(self, trade_data: Dict[str, Any]) -> int:
        """
        Add an aggregated trade.
        
        Args:
            trade_data: Trade data dictionary
            
        Returns:
            Trade ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO aggregated_trades 
            (plugin_id, plugin_type, source_trade_id, mt5_ticket, symbol, direction,
             lot_size, entry_price, entry_time, exit_time, exit_price,
             profit_pips, profit_dollars, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_data.get("plugin_id"),
            trade_data.get("plugin_type"),
            trade_data.get("source_trade_id"),
            trade_data.get("mt5_ticket"),
            trade_data.get("symbol"),
            trade_data.get("direction"),
            trade_data.get("lot_size"),
            trade_data.get("entry_price"),
            trade_data.get("entry_time"),
            trade_data.get("exit_time"),
            trade_data.get("exit_price"),
            trade_data.get("profit_pips"),
            trade_data.get("profit_dollars"),
            trade_data.get("status", "OPEN")
        ))
        conn.commit()
        
        return cursor.lastrowid
    
    def get_aggregated_trades(self, plugin_id: Optional[str] = None,
                               status: Optional[str] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get aggregated trades.
        
        Args:
            plugin_id: Optional plugin filter
            status: Optional status filter
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM aggregated_trades WHERE 1=1"
        params = []
        
        if plugin_id:
            query += " AND plugin_id = ?"
            params.append(plugin_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY synced_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_aggregated_trade(self, trade_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update an aggregated trade.
        
        Args:
            trade_id: Trade ID
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        updates["synced_at"] = datetime.now().isoformat()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [trade_id]
        
        cursor.execute(
            f"UPDATE aggregated_trades SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def get_last_synced_trade_id(self, plugin_id: str) -> int:
        """
        Get the last synced trade ID for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Last synced trade ID or 0
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COALESCE(MAX(source_trade_id), 0) FROM aggregated_trades WHERE plugin_id = ?",
            (plugin_id,)
        )
        return cursor.fetchone()[0]
    
    # =========================================================================
    # System Config Operations
    # =========================================================================
    
    def get_config(self, key: str) -> Optional[str]:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        return None
    
    def set_config(self, key: str, value: str, description: Optional[str] = None,
                   config_type: str = "string") -> bool:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            description: Optional description
            config_type: Value type (string, integer, float, boolean, json)
            
        Returns:
            True if set successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO system_config 
            (key, value, description, config_type, updated_at)
            VALUES (?, ?, COALESCE(?, (SELECT description FROM system_config WHERE key = ?)), ?, ?)
        """, (key, value, description, key, config_type, datetime.now().isoformat()))
        conn.commit()
        
        return True
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all config key-value pairs
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value, config_type FROM system_config")
        
        config = {}
        for row in cursor.fetchall():
            key, value, config_type = row
            
            # Convert value based on type
            if config_type == "integer":
                config[key] = int(value) if value else 0
            elif config_type == "float":
                config[key] = float(value) if value else 0.0
            elif config_type == "boolean":
                config[key] = value.lower() in ("true", "1", "yes")
            else:
                config[key] = value
        
        return config
    
    # =========================================================================
    # System Events Operations
    # =========================================================================
    
    def log_event(self, event_type: str, message: str,
                  severity: str = "INFO", source: Optional[str] = None,
                  details: Optional[str] = None) -> int:
        """
        Log a system event.
        
        Args:
            event_type: Type of event
            message: Event message
            severity: Event severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            source: Event source
            details: Additional details
            
        Returns:
            Event ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO system_events 
            (event_type, severity, source, message, details)
            VALUES (?, ?, ?, ?, ?)
        """, (event_type, severity, source, message, details))
        conn.commit()
        
        return cursor.lastrowid
    
    def get_events(self, severity: Optional[str] = None,
                   event_type: Optional[str] = None,
                   limit: int = 100,
                   unacknowledged_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get system events.
        
        Args:
            severity: Optional severity filter
            event_type: Optional event type filter
            limit: Maximum number of events to return
            unacknowledged_only: If True, return only unacknowledged events
            
        Returns:
            List of event dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM system_events WHERE 1=1"
        params = []
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if unacknowledged_only:
            query += " AND acknowledged = 0"
        
        query += " ORDER BY event_time DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def acknowledge_event(self, event_id: int) -> bool:
        """
        Acknowledge an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            True if acknowledged successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE system_events SET acknowledged = 1 WHERE id = ?",
            (event_id,)
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def acknowledge_all_events(self, severity: Optional[str] = None) -> int:
        """
        Acknowledge all events.
        
        Args:
            severity: Optional severity filter
            
        Returns:
            Number of events acknowledged
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if severity:
            cursor.execute(
                "UPDATE system_events SET acknowledged = 1 WHERE severity = ? AND acknowledged = 0",
                (severity,)
            )
        else:
            cursor.execute(
                "UPDATE system_events SET acknowledged = 1 WHERE acknowledged = 0"
            )
        conn.commit()
        
        return cursor.rowcount
    
    # =========================================================================
    # Statistics Operations
    # =========================================================================
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """
        Get overall system statistics.
        
        Returns:
            Statistics dictionary
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Plugin counts
        cursor.execute("SELECT COUNT(*) FROM plugins_registry")
        total_plugins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM plugins_registry WHERE enabled = 1")
        enabled_plugins = cursor.fetchone()[0]
        
        # Trade counts
        cursor.execute("SELECT COUNT(*) FROM aggregated_trades")
        total_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aggregated_trades WHERE status IN ('OPEN', 'PARTIAL')")
        open_trades = cursor.fetchone()[0]
        
        # Total profit
        cursor.execute("SELECT COALESCE(SUM(profit_dollars), 0) FROM aggregated_trades WHERE status = 'CLOSED'")
        total_profit = cursor.fetchone()[0]
        
        # Event counts
        cursor.execute("SELECT COUNT(*) FROM system_events WHERE acknowledged = 0")
        unacknowledged_events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM system_events WHERE severity IN ('ERROR', 'CRITICAL') AND acknowledged = 0")
        critical_events = cursor.fetchone()[0]
        
        return {
            "total_plugins": total_plugins,
            "enabled_plugins": enabled_plugins,
            "total_trades": total_trades,
            "open_trades": open_trades,
            "total_profit": round(total_profit, 2),
            "unacknowledged_events": unacknowledged_events,
            "critical_events": critical_events
        }
