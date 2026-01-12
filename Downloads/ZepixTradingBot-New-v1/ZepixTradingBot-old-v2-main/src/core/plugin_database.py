"""
PluginDatabase - Per-Plugin Database Management System

Document 07: Phase 5 - Dynamic Config & Per-Plugin Databases
Implements isolated database for each plugin with complete schema management.

Features:
- Isolated database per plugin (data/zepix_{plugin_id}.db)
- Standard schema for trades, daily stats, plugin info
- CRUD operations for trade management
- Statistics and reporting queries
- Database migration support
"""

import sqlite3
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PluginDatabase:
    """
    Manages isolated database for each plugin.
    
    Each plugin gets its own SQLite database file at data/zepix_{plugin_id}.db
    with a standard schema for trades, daily stats, and plugin info.
    
    Features:
    - Complete database isolation between plugins
    - Standard schema with trades, daily_stats, plugin_info tables
    - Thread-safe connection management
    - Automatic schema creation and migration
    
    Usage:
        db = PluginDatabase("combined_v3")
        db.save_trade({
            "ticket": 12345,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.0850,
            "sl_price": 1.0800,
            "tp_price": 1.0900
        })
        
        trades = db.get_open_trades()
        stats = db.get_daily_stats(date.today())
    """
    
    # Database directory
    DB_DIR = "data"
    
    # Schema version for migrations
    SCHEMA_VERSION = 1
    
    def __init__(self, plugin_id: str):
        """
        Initialize PluginDatabase.
        
        Args:
            plugin_id: Unique identifier for the plugin
        """
        self.plugin_id = plugin_id
        self.db_path = os.path.join(self.DB_DIR, f"zepix_{plugin_id}.db")
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Creates database and schema if needed."""
        # Ensure data directory exists
        os.makedirs(self.DB_DIR, exist_ok=True)
        
        is_new_db = not os.path.exists(self.db_path)
        
        if is_new_db:
            logger.info(f"Creating new database for {self.plugin_id}")
        
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        if is_new_db:
            self._create_schema()
        else:
            self._check_schema_version()
    
    def _create_schema(self) -> None:
        """Creates plugin database schema."""
        cursor = self.connection.cursor()
        
        # Schema version table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Plugin info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_info (
                plugin_id TEXT PRIMARY KEY,
                version TEXT,
                last_started TIMESTAMP,
                total_runtime_hours REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mt5_ticket INTEGER UNIQUE,
                symbol TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('BUY', 'SELL')),
                lot_size REAL NOT NULL,
                entry_price REAL NOT NULL,
                sl_price REAL,
                tp_price REAL,
                entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exit_time TIMESTAMP,
                exit_price REAL,
                profit_pips REAL,
                profit_dollars REAL,
                commission REAL DEFAULT 0,
                swap REAL DEFAULT 0,
                status TEXT CHECK(status IN ('OPEN', 'CLOSED', 'PARTIAL')) DEFAULT 'OPEN',
                close_reason TEXT,
                signal_type TEXT,
                logic_route TEXT,
                order_type TEXT,
                signal_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Daily stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                breakeven_trades INTEGER DEFAULT 0,
                total_profit_pips REAL DEFAULT 0,
                total_profit_dollars REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Trade events table (for audit trail)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                event_type TEXT NOT NULL,
                event_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_mt5_ticket ON trades(mt5_ticket)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trade_events_trade_id ON trade_events(trade_id)")
        
        # Insert schema version
        cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))
        
        # Insert plugin info
        cursor.execute("""
            INSERT INTO plugin_info (plugin_id, version, last_started)
            VALUES (?, '1.0.0', CURRENT_TIMESTAMP)
        """, (self.plugin_id,))
        
        self.connection.commit()
        logger.info(f"Schema created for {self.plugin_id}")
    
    def _check_schema_version(self) -> None:
        """Check and migrate schema if needed."""
        cursor = self.connection.cursor()
        
        try:
            result = cursor.execute("SELECT MAX(version) FROM schema_version").fetchone()
            current_version = result[0] if result else 0
            
            if current_version < self.SCHEMA_VERSION:
                logger.info(f"Migrating {self.plugin_id} database from v{current_version} to v{self.SCHEMA_VERSION}")
                self._migrate_schema(current_version)
        except sqlite3.OperationalError:
            # schema_version table doesn't exist, create full schema
            self._create_schema()
    
    def _migrate_schema(self, from_version: int) -> None:
        """Migrate schema from older version."""
        cursor = self.connection.cursor()
        
        # Add migration logic here as schema evolves
        # Example:
        # if from_version < 2:
        #     cursor.execute("ALTER TABLE trades ADD COLUMN new_field TEXT")
        
        cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))
        self.connection.commit()
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.connection.cursor()
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
    
    def save_trade(self, trade_data: Dict[str, Any]) -> int:
        """
        Saves trade to plugin database.
        
        Args:
            trade_data: Dictionary with trade information
                Required: ticket, symbol, direction, lot_size, entry_price
                Optional: sl_price, tp_price, signal_type, logic_route, order_type, signal_data
        
        Returns:
            The database ID of the inserted trade
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO trades 
            (mt5_ticket, symbol, direction, lot_size, entry_price, sl_price, tp_price,
             signal_type, logic_route, order_type, signal_data, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
        """, (
            trade_data.get("ticket"),
            trade_data["symbol"],
            trade_data["direction"],
            trade_data["lot_size"],
            trade_data["entry_price"],
            trade_data.get("sl_price"),
            trade_data.get("tp_price"),
            trade_data.get("signal_type"),
            trade_data.get("logic_route"),
            trade_data.get("order_type"),
            json.dumps(trade_data.get("signal_data", {}))
        ))
        
        trade_id = cursor.lastrowid
        self.connection.commit()
        
        # Log trade event
        self._log_event(trade_id, "TRADE_OPENED", trade_data)
        
        logger.info(f"Trade saved: {trade_data.get('ticket')} for {self.plugin_id}")
        return trade_id
    
    def update_trade(self, ticket: int, updates: Dict[str, Any]) -> bool:
        """
        Update an existing trade.
        
        Args:
            ticket: MT5 ticket number
            updates: Dictionary of fields to update
            
        Returns:
            True if trade was updated, False if not found
        """
        cursor = self.connection.cursor()
        
        # Build update query dynamically
        allowed_fields = ['sl_price', 'tp_price', 'exit_time', 'exit_price', 
                         'profit_pips', 'profit_dollars', 'status', 'close_reason',
                         'commission', 'swap']
        
        set_clauses = []
        values = []
        
        for field in allowed_fields:
            if field in updates:
                set_clauses.append(f"{field} = ?")
                values.append(updates[field])
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(ticket)
        
        query = f"UPDATE trades SET {', '.join(set_clauses)} WHERE mt5_ticket = ?"
        cursor.execute(query, values)
        self.connection.commit()
        
        if cursor.rowcount > 0:
            # Log trade event
            trade = self.get_trade_by_ticket(ticket)
            if trade:
                self._log_event(trade['id'], "TRADE_UPDATED", updates)
            return True
        
        return False
    
    def close_trade(self, ticket: int, exit_price: float, profit_pips: float, 
                    profit_dollars: float, close_reason: str = "MANUAL") -> bool:
        """
        Close a trade.
        
        Args:
            ticket: MT5 ticket number
            exit_price: Exit price
            profit_pips: Profit in pips
            profit_dollars: Profit in dollars
            close_reason: Reason for closing (TP, SL, MANUAL, REVERSAL, etc.)
            
        Returns:
            True if trade was closed, False if not found
        """
        return self.update_trade(ticket, {
            'exit_time': datetime.now().isoformat(),
            'exit_price': exit_price,
            'profit_pips': profit_pips,
            'profit_dollars': profit_dollars,
            'status': 'CLOSED',
            'close_reason': close_reason
        })
    
    def get_trade_by_ticket(self, ticket: int) -> Optional[Dict[str, Any]]:
        """
        Get trade by MT5 ticket number.
        
        Args:
            ticket: MT5 ticket number
            
        Returns:
            Trade dictionary or None if not found
        """
        cursor = self.connection.cursor()
        result = cursor.execute(
            "SELECT * FROM trades WHERE mt5_ticket = ?", (ticket,)
        ).fetchone()
        
        return dict(result) if result else None
    
    def get_open_trades(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open trades.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open trade dictionaries
        """
        cursor = self.connection.cursor()
        
        if symbol:
            result = cursor.execute(
                "SELECT * FROM trades WHERE status = 'OPEN' AND symbol = ? ORDER BY entry_time DESC",
                (symbol,)
            ).fetchall()
        else:
            result = cursor.execute(
                "SELECT * FROM trades WHERE status = 'OPEN' ORDER BY entry_time DESC"
            ).fetchall()
        
        return [dict(row) for row in result]
    
    def get_closed_trades(self, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get closed trades within date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of closed trade dictionaries
        """
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM trades WHERE status = 'CLOSED'"
        params = []
        
        if start_date:
            query += " AND exit_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND exit_time <= ?"
            params.append(end_date + " 23:59:59")
        
        query += " ORDER BY exit_time DESC"
        
        result = cursor.execute(query, params).fetchall()
        return [dict(row) for row in result]
    
    def get_all_trades(self) -> List[Dict[str, Any]]:
        """
        Get all trades.
        
        Returns:
            List of all trade dictionaries
        """
        cursor = self.connection.cursor()
        result = cursor.execute("SELECT * FROM trades ORDER BY entry_time DESC").fetchall()
        return [dict(row) for row in result]
    
    def get_daily_stats(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get daily statistics.
        
        Args:
            target_date: Date to get stats for (defaults to today)
            
        Returns:
            Daily stats dictionary
        """
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.isoformat()
        
        cursor = self.connection.cursor()
        result = cursor.execute(
            "SELECT * FROM daily_stats WHERE date = ?", (date_str,)
        ).fetchone()
        
        if result:
            return dict(result)
        
        # Calculate stats from trades if not cached
        return self._calculate_daily_stats(date_str)
    
    def _calculate_daily_stats(self, date_str: str) -> Dict[str, Any]:
        """Calculate daily stats from trades."""
        cursor = self.connection.cursor()
        
        # Get trades closed on this date
        trades = cursor.execute("""
            SELECT * FROM trades 
            WHERE status = 'CLOSED' 
            AND date(exit_time) = ?
        """, (date_str,)).fetchall()
        
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t['profit_dollars'] and t['profit_dollars'] > 0)
        losing_trades = sum(1 for t in trades if t['profit_dollars'] and t['profit_dollars'] < 0)
        breakeven_trades = total_trades - winning_trades - losing_trades
        
        total_profit_pips = sum(t['profit_pips'] or 0 for t in trades)
        total_profit_dollars = sum(t['profit_dollars'] or 0 for t in trades)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        stats = {
            'date': date_str,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'breakeven_trades': breakeven_trades,
            'total_profit_pips': total_profit_pips,
            'total_profit_dollars': total_profit_dollars,
            'win_rate': win_rate
        }
        
        # Cache the stats
        self._save_daily_stats(stats)
        
        return stats
    
    def _save_daily_stats(self, stats: Dict[str, Any]) -> None:
        """Save or update daily stats."""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO daily_stats 
            (date, total_trades, winning_trades, losing_trades, breakeven_trades,
             total_profit_pips, total_profit_dollars, win_rate, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            stats['date'],
            stats['total_trades'],
            stats['winning_trades'],
            stats['losing_trades'],
            stats.get('breakeven_trades', 0),
            stats['total_profit_pips'],
            stats['total_profit_dollars'],
            stats.get('win_rate', 0)
        ))
        
        self.connection.commit()
    
    def update_plugin_info(self, version: Optional[str] = None, 
                           runtime_hours: Optional[float] = None) -> None:
        """
        Update plugin info.
        
        Args:
            version: Plugin version string
            runtime_hours: Additional runtime hours to add
        """
        cursor = self.connection.cursor()
        
        updates = ["last_started = CURRENT_TIMESTAMP", "updated_at = CURRENT_TIMESTAMP"]
        params = []
        
        if version:
            updates.append("version = ?")
            params.append(version)
        
        if runtime_hours:
            updates.append("total_runtime_hours = total_runtime_hours + ?")
            params.append(runtime_hours)
        
        params.append(self.plugin_id)
        
        query = f"UPDATE plugin_info SET {', '.join(updates)} WHERE plugin_id = ?"
        cursor.execute(query, params)
        self.connection.commit()
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """
        Get plugin info.
        
        Returns:
            Plugin info dictionary
        """
        cursor = self.connection.cursor()
        result = cursor.execute(
            "SELECT * FROM plugin_info WHERE plugin_id = ?", (self.plugin_id,)
        ).fetchone()
        
        return dict(result) if result else {}
    
    def _log_event(self, trade_id: int, event_type: str, event_data: Any) -> None:
        """Log a trade event for audit trail."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO trade_events (trade_id, event_type, event_data)
            VALUES (?, ?, ?)
        """, (trade_id, event_type, json.dumps(event_data, default=str)))
        self.connection.commit()
    
    def get_trade_events(self, trade_id: int) -> List[Dict[str, Any]]:
        """
        Get all events for a trade.
        
        Args:
            trade_id: Database trade ID
            
        Returns:
            List of event dictionaries
        """
        cursor = self.connection.cursor()
        result = cursor.execute(
            "SELECT * FROM trade_events WHERE trade_id = ? ORDER BY created_at",
            (trade_id,)
        ).fetchall()
        
        return [dict(row) for row in result]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall plugin statistics.
        
        Returns:
            Statistics dictionary
        """
        cursor = self.connection.cursor()
        
        # Total trades
        total = cursor.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        
        # Open trades
        open_trades = cursor.execute(
            "SELECT COUNT(*) FROM trades WHERE status = 'OPEN'"
        ).fetchone()[0]
        
        # Closed trades stats
        closed_stats = cursor.execute("""
            SELECT 
                COUNT(*) as total_closed,
                SUM(CASE WHEN profit_dollars > 0 THEN 1 ELSE 0 END) as winners,
                SUM(CASE WHEN profit_dollars < 0 THEN 1 ELSE 0 END) as losers,
                SUM(profit_dollars) as total_profit,
                SUM(profit_pips) as total_pips
            FROM trades WHERE status = 'CLOSED'
        """).fetchone()
        
        total_closed = closed_stats[0] or 0
        winners = closed_stats[1] or 0
        losers = closed_stats[2] or 0
        total_profit = closed_stats[3] or 0
        total_pips = closed_stats[4] or 0
        
        win_rate = (winners / total_closed * 100) if total_closed > 0 else 0
        
        return {
            'plugin_id': self.plugin_id,
            'total_trades': total,
            'open_trades': open_trades,
            'closed_trades': total_closed,
            'winning_trades': winners,
            'losing_trades': losers,
            'win_rate': round(win_rate, 2),
            'total_profit_dollars': round(total_profit, 2),
            'total_profit_pips': round(total_pips, 1)
        }
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info(f"Database closed for {self.plugin_id}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __repr__(self) -> str:
        return f"PluginDatabase(plugin_id={self.plugin_id}, path={self.db_path})"
