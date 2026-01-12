"""
V6 Price Action Database Schema

Document 09: Database Schema Designs
Implements the V6 Price Action database schema with:
- price_action_1m_trades: 1M scalping trades (ORDER B only)
- price_action_5m_trades: 5M momentum trades (ORDER A + ORDER B)
- price_action_15m_trades: 15M intraday trades (ORDER A only)
- price_action_1h_trades: 1H swing trades (ORDER A only)
- market_trends: Trend Pulse market trends
- v6_signals_log: Signal logging
- v6_daily_stats: Daily statistics per plugin
"""

import sqlite3
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from .schemas import BaseSchema

logger = logging.getLogger(__name__)


class V6Schema(BaseSchema):
    """
    V6 Price Action Database Schema.
    
    Database: data/zepix_price_action.db
    
    Tables:
    - price_action_1m_trades: 1M scalping (ORDER B only, 0.5x SL, 60min max)
    - price_action_5m_trades: 5M momentum (ORDER A + ORDER B, 1.0x SL, 240min max)
    - price_action_15m_trades: 15M intraday (ORDER A only, 1.5x SL, 480min max)
    - price_action_1h_trades: 1H swing (ORDER A only, 2.0x SL, 1440min max)
    - market_trends: Trend Pulse data shared by all V6 plugins
    - v6_signals_log: All received V6 signals
    - v6_daily_stats: Daily aggregated statistics per plugin
    """
    
    def get_schema_sql(self) -> List[str]:
        """Get V6 schema SQL statements."""
        return [
            # price_action_1m_trades table (ORDER B only)
            """
            CREATE TABLE IF NOT EXISTS price_action_1m_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Order Identification (B only for 1M)
                order_b_ticket INTEGER UNIQUE,
                mt5_ticket INTEGER,
                
                -- Basic Trade Info
                symbol TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('BUY', 'SELL')),
                entry_price REAL NOT NULL,
                entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exit_time TIMESTAMP,
                status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
                
                -- V6 Specific: Signal Details
                signal_type TEXT NOT NULL,
                trend_pulse_bull INTEGER DEFAULT 0,
                trend_pulse_bear INTEGER DEFAULT 0,
                adx_value REAL,
                momentum_score REAL,
                
                -- V6 1M Specific: Order B Details
                lot_size REAL NOT NULL,
                sl_price REAL,
                tp_price REAL,
                sl_multiplier REAL DEFAULT 0.5,
                max_hold_minutes INTEGER DEFAULT 60,
                
                -- Results
                exit_price REAL,
                profit_pips REAL,
                profit_dollars REAL,
                commission REAL DEFAULT 0,
                swap REAL DEFAULT 0,
                
                -- Metadata
                close_reason TEXT,
                notes TEXT
            )
            """,
            
            # price_action_5m_trades table (ORDER A + ORDER B)
            """
            CREATE TABLE IF NOT EXISTS price_action_5m_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Order Identification (Dual orders for 5M)
                order_a_ticket INTEGER UNIQUE,
                order_b_ticket INTEGER UNIQUE,
                mt5_parent_ticket INTEGER,
                
                -- Basic Trade Info
                symbol TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('BUY', 'SELL')),
                entry_price REAL NOT NULL,
                entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exit_time TIMESTAMP,
                status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')) DEFAULT 'OPEN',
                
                -- V6 Specific: Signal Details
                signal_type TEXT NOT NULL,
                trend_pulse_bull INTEGER DEFAULT 0,
                trend_pulse_bear INTEGER DEFAULT 0,
                adx_value REAL,
                momentum_score REAL,
                
                -- V6 5M Specific: Dual Order Details
                order_a_lot_size REAL,
                order_b_lot_size REAL,
                order_a_sl_price REAL,
                order_b_sl_price REAL,
                order_a_tp_price REAL,
                order_b_tp_price REAL,
                sl_multiplier REAL DEFAULT 1.0,
                max_hold_minutes INTEGER DEFAULT 240,
                
                -- Order A Results
                order_a_exit_price REAL,
                order_a_exit_time TIMESTAMP,
                order_a_profit_pips REAL,
                order_a_profit_dollars REAL,
                order_a_status TEXT CHECK(order_a_status IN ('OPEN', 'CLOSED')),
                
                -- Order B Results
                order_b_exit_price REAL,
                order_b_exit_time TIMESTAMP,
                order_b_profit_pips REAL,
                order_b_profit_dollars REAL,
                order_b_status TEXT CHECK(order_b_status IN ('OPEN', 'CLOSED')),
                
                -- Combined P&L
                total_profit_pips REAL,
                total_profit_dollars REAL,
                commission REAL DEFAULT 0,
                swap REAL DEFAULT 0,
                
                -- Metadata
                close_reason TEXT,
                notes TEXT
            )
            """,
            
            # price_action_15m_trades table (ORDER A only)
            """
            CREATE TABLE IF NOT EXISTS price_action_15m_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Order Identification (A only for 15M)
                order_a_ticket INTEGER UNIQUE,
                mt5_ticket INTEGER,
                
                -- Basic Trade Info
                symbol TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('BUY', 'SELL')),
                entry_price REAL NOT NULL,
                entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exit_time TIMESTAMP,
                status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
                
                -- V6 Specific: Signal Details
                signal_type TEXT NOT NULL,
                trend_pulse_bull INTEGER DEFAULT 0,
                trend_pulse_bear INTEGER DEFAULT 0,
                adx_value REAL,
                momentum_score REAL,
                
                -- V6 15M Specific: Order A Details
                lot_size REAL NOT NULL,
                sl_price REAL,
                tp_price REAL,
                sl_multiplier REAL DEFAULT 1.5,
                max_hold_minutes INTEGER DEFAULT 480,
                
                -- Results
                exit_price REAL,
                profit_pips REAL,
                profit_dollars REAL,
                commission REAL DEFAULT 0,
                swap REAL DEFAULT 0,
                
                -- Metadata
                close_reason TEXT,
                notes TEXT
            )
            """,
            
            # price_action_1h_trades table (ORDER A only)
            """
            CREATE TABLE IF NOT EXISTS price_action_1h_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Order Identification (A only for 1H)
                order_a_ticket INTEGER UNIQUE,
                mt5_ticket INTEGER,
                
                -- Basic Trade Info
                symbol TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('BUY', 'SELL')),
                entry_price REAL NOT NULL,
                entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exit_time TIMESTAMP,
                status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
                
                -- V6 Specific: Signal Details
                signal_type TEXT NOT NULL,
                trend_pulse_bull INTEGER DEFAULT 0,
                trend_pulse_bear INTEGER DEFAULT 0,
                adx_value REAL,
                momentum_score REAL,
                
                -- V6 1H Specific: Order A Details
                lot_size REAL NOT NULL,
                sl_price REAL,
                tp_price REAL,
                sl_multiplier REAL DEFAULT 2.0,
                max_hold_minutes INTEGER DEFAULT 1440,
                
                -- Results
                exit_price REAL,
                profit_pips REAL,
                profit_dollars REAL,
                commission REAL DEFAULT 0,
                swap REAL DEFAULT 0,
                
                -- Metadata
                close_reason TEXT,
                notes TEXT
            )
            """,
            
            # market_trends table (shared by all V6 plugins)
            """
            CREATE TABLE IF NOT EXISTS market_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                bull_count INTEGER DEFAULT 0,
                bear_count INTEGER DEFAULT 0,
                last_trend_pulse TEXT,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe)
            )
            """,
            
            # v6_signals_log table
            """
            CREATE TABLE IF NOT EXISTS v6_signals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                plugin_id TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT,
                timeframe TEXT,
                trend_pulse_bull INTEGER,
                trend_pulse_bear INTEGER,
                adx_value REAL,
                momentum_score REAL,
                signal_json TEXT,
                processed BOOLEAN DEFAULT 0,
                trade_placed BOOLEAN DEFAULT 0,
                trade_id INTEGER,
                skip_reason TEXT
            )
            """,
            
            # v6_daily_stats table (per plugin)
            """
            CREATE TABLE IF NOT EXISTS v6_daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                plugin_id TEXT NOT NULL,
                total_entries INTEGER DEFAULT 0,
                total_exits INTEGER DEFAULT 0,
                bullish_entries INTEGER DEFAULT 0,
                bearish_entries INTEGER DEFAULT 0,
                total_profit_dollars REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                UNIQUE(date, plugin_id)
            )
            """
        ]
    
    def get_indexes_sql(self) -> List[str]:
        """Get V6 index SQL statements."""
        return [
            # 1M indexes
            "CREATE INDEX IF NOT EXISTS idx_v6_1m_status ON price_action_1m_trades(status)",
            "CREATE INDEX IF NOT EXISTS idx_v6_1m_symbol ON price_action_1m_trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_v6_1m_entry_time ON price_action_1m_trades(entry_time)",
            
            # 5M indexes
            "CREATE INDEX IF NOT EXISTS idx_v6_5m_status ON price_action_5m_trades(status)",
            "CREATE INDEX IF NOT EXISTS idx_v6_5m_symbol ON price_action_5m_trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_v6_5m_entry_time ON price_action_5m_trades(entry_time)",
            
            # 15M indexes
            "CREATE INDEX IF NOT EXISTS idx_v6_15m_status ON price_action_15m_trades(status)",
            "CREATE INDEX IF NOT EXISTS idx_v6_15m_symbol ON price_action_15m_trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_v6_15m_entry_time ON price_action_15m_trades(entry_time)",
            
            # 1H indexes
            "CREATE INDEX IF NOT EXISTS idx_v6_1h_status ON price_action_1h_trades(status)",
            "CREATE INDEX IF NOT EXISTS idx_v6_1h_symbol ON price_action_1h_trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_v6_1h_entry_time ON price_action_1h_trades(entry_time)",
            
            # Market trends indexes
            "CREATE INDEX IF NOT EXISTS idx_market_trends_symbol ON market_trends(symbol)",
            
            # Signals log indexes
            "CREATE INDEX IF NOT EXISTS idx_v6_signals_processed ON v6_signals_log(processed)",
            "CREATE INDEX IF NOT EXISTS idx_v6_signals_plugin ON v6_signals_log(plugin_id)"
        ]


class V6Database:
    """
    V6 Price Action Database Manager.
    
    Provides CRUD operations for V6 trades across all 4 timeframes.
    """
    
    DB_PATH = "data/zepix_price_action.db"
    
    # Plugin to table mapping
    PLUGIN_TABLES = {
        "price_action_1m": "price_action_1m_trades",
        "price_action_5m": "price_action_5m_trades",
        "price_action_15m": "price_action_15m_trades",
        "price_action_1h": "price_action_1h_trades"
    }
    
    # Plugin configurations
    PLUGIN_CONFIGS = {
        "price_action_1m": {
            "order_type": "B_ONLY",
            "sl_multiplier": 0.5,
            "max_hold_minutes": 60
        },
        "price_action_5m": {
            "order_type": "DUAL",
            "sl_multiplier": 1.0,
            "max_hold_minutes": 240
        },
        "price_action_15m": {
            "order_type": "A_ONLY",
            "sl_multiplier": 1.5,
            "max_hold_minutes": 480
        },
        "price_action_1h": {
            "order_type": "A_ONLY",
            "sl_multiplier": 2.0,
            "max_hold_minutes": 1440
        }
    }
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize V6 database.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or self.DB_PATH
        self.schema = V6Schema(self.db_path)
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
    
    def get_table_for_plugin(self, plugin_id: str) -> str:
        """
        Get table name for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Table name
        """
        return self.PLUGIN_TABLES.get(plugin_id, "price_action_1m_trades")
    
    # =========================================================================
    # Trade Operations (Generic for all timeframes)
    # =========================================================================
    
    def save_trade(self, plugin_id: str, trade_data: Dict[str, Any]) -> int:
        """
        Save a new V6 trade.
        
        Args:
            plugin_id: Plugin identifier (price_action_1m/5m/15m/1h)
            trade_data: Trade data dictionary
            
        Returns:
            Trade ID
        """
        table = self.get_table_for_plugin(plugin_id)
        config = self.PLUGIN_CONFIGS.get(plugin_id, {})
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Build columns based on order type
        if config.get("order_type") == "DUAL":
            columns = [
                "symbol", "direction", "entry_price", "signal_type",
                "trend_pulse_bull", "trend_pulse_bear", "adx_value", "momentum_score",
                "order_a_lot_size", "order_b_lot_size",
                "order_a_sl_price", "order_b_sl_price",
                "order_a_tp_price", "order_b_tp_price",
                "order_a_ticket", "order_b_ticket",
                "order_a_status", "order_b_status",
                "sl_multiplier", "max_hold_minutes"
            ]
        elif config.get("order_type") == "B_ONLY":
            columns = [
                "symbol", "direction", "entry_price", "signal_type",
                "trend_pulse_bull", "trend_pulse_bear", "adx_value", "momentum_score",
                "lot_size", "sl_price", "tp_price",
                "order_b_ticket", "sl_multiplier", "max_hold_minutes"
            ]
        else:  # A_ONLY
            columns = [
                "symbol", "direction", "entry_price", "signal_type",
                "trend_pulse_bull", "trend_pulse_bear", "adx_value", "momentum_score",
                "lot_size", "sl_price", "tp_price",
                "order_a_ticket", "sl_multiplier", "max_hold_minutes"
            ]
        
        # Set defaults from config
        trade_data.setdefault("sl_multiplier", config.get("sl_multiplier", 1.0))
        trade_data.setdefault("max_hold_minutes", config.get("max_hold_minutes", 240))
        
        values = [trade_data.get(col) for col in columns]
        placeholders = ", ".join(["?" for _ in columns])
        columns_str = ", ".join(columns)
        
        cursor.execute(
            f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})",
            values
        )
        conn.commit()
        
        trade_id = cursor.lastrowid
        self.logger.info(f"Saved V6 {plugin_id} trade {trade_id}")
        return trade_id
    
    def get_trade(self, plugin_id: str, trade_id: int) -> Optional[Dict[str, Any]]:
        """
        Get trade by ID.
        
        Args:
            plugin_id: Plugin identifier
            trade_id: Trade ID
            
        Returns:
            Trade data dictionary or None
        """
        table = self.get_table_for_plugin(plugin_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (trade_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_open_trades(self, plugin_id: str, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open trades for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            symbol: Optional symbol filter
            
        Returns:
            List of trade dictionaries
        """
        table = self.get_table_for_plugin(plugin_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute(
                f"SELECT * FROM {table} WHERE status IN ('OPEN', 'PARTIAL') AND symbol = ?",
                (symbol,)
            )
        else:
            cursor.execute(
                f"SELECT * FROM {table} WHERE status IN ('OPEN', 'PARTIAL')"
            )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_trade(self, plugin_id: str, trade_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update trade fields.
        
        Args:
            plugin_id: Plugin identifier
            trade_id: Trade ID
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully
        """
        table = self.get_table_for_plugin(plugin_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [trade_id]
        
        cursor.execute(
            f"UPDATE {table} SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def close_trade(self, plugin_id: str, trade_id: int, exit_price: float,
                    profit_pips: float, profit_dollars: float, close_reason: str) -> bool:
        """
        Close a trade.
        
        Args:
            plugin_id: Plugin identifier
            trade_id: Trade ID
            exit_price: Exit price
            profit_pips: Profit in pips
            profit_dollars: Profit in dollars
            close_reason: Reason for closing
            
        Returns:
            True if closed successfully
        """
        config = self.PLUGIN_CONFIGS.get(plugin_id, {})
        
        if config.get("order_type") == "DUAL":
            return self.update_trade(plugin_id, trade_id, {
                "status": "CLOSED",
                "exit_time": datetime.now().isoformat(),
                "total_profit_pips": profit_pips,
                "total_profit_dollars": profit_dollars,
                "close_reason": close_reason
            })
        else:
            return self.update_trade(plugin_id, trade_id, {
                "status": "CLOSED",
                "exit_time": datetime.now().isoformat(),
                "exit_price": exit_price,
                "profit_pips": profit_pips,
                "profit_dollars": profit_dollars,
                "close_reason": close_reason
            })
    
    # =========================================================================
    # Market Trends Operations
    # =========================================================================
    
    def update_market_trend(self, symbol: str, timeframe: str,
                            bull_count: int, bear_count: int,
                            trend_pulse: str) -> bool:
        """
        Update market trend data.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1M, 5M, 15M, 1H)
            bull_count: Bullish count
            bear_count: Bearish count
            trend_pulse: Trend pulse string
            
        Returns:
            True if updated successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO market_trends 
            (symbol, timeframe, bull_count, bear_count, last_trend_pulse, last_update)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, timeframe, bull_count, bear_count, trend_pulse, datetime.now().isoformat()))
        conn.commit()
        
        return True
    
    def get_market_trend(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """
        Get market trend data.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            Market trend dictionary or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM market_trends WHERE symbol = ? AND timeframe = ?",
            (symbol, timeframe)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_market_trends(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all market trends.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of market trend dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute("SELECT * FROM market_trends WHERE symbol = ?", (symbol,))
        else:
            cursor.execute("SELECT * FROM market_trends")
        
        return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # Signal Operations
    # =========================================================================
    
    def log_signal(self, plugin_id: str, signal_data: Dict[str, Any]) -> int:
        """
        Log a received signal.
        
        Args:
            plugin_id: Plugin identifier
            signal_data: Signal data dictionary
            
        Returns:
            Signal log ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO v6_signals_log 
            (plugin_id, signal_type, symbol, direction, timeframe,
             trend_pulse_bull, trend_pulse_bear, adx_value, momentum_score,
             signal_json, processed, trade_placed, skip_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plugin_id,
            signal_data.get("signal_type"),
            signal_data.get("symbol"),
            signal_data.get("direction"),
            signal_data.get("timeframe"),
            signal_data.get("trend_pulse_bull"),
            signal_data.get("trend_pulse_bear"),
            signal_data.get("adx_value"),
            signal_data.get("momentum_score"),
            signal_data.get("signal_json"),
            signal_data.get("processed", False),
            signal_data.get("trade_placed", False),
            signal_data.get("skip_reason")
        ))
        conn.commit()
        
        return cursor.lastrowid
    
    # =========================================================================
    # Statistics Operations
    # =========================================================================
    
    def get_daily_stats(self, plugin_id: str, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Get daily statistics for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            date_str: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Daily stats dictionary
        """
        if not date_str:
            date_str = date.today().isoformat()
        
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM v6_daily_stats WHERE date = ? AND plugin_id = ?",
            (date_str, plugin_id)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        
        return {
            "date": date_str,
            "plugin_id": plugin_id,
            "total_entries": 0,
            "total_exits": 0,
            "bullish_entries": 0,
            "bearish_entries": 0,
            "total_profit_dollars": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0
        }
    
    def update_daily_stats(self, plugin_id: str, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Recalculate and update daily statistics for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            date_str: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Updated daily stats dictionary
        """
        if not date_str:
            date_str = date.today().isoformat()
        
        table = self.get_table_for_plugin(plugin_id)
        config = self.PLUGIN_CONFIGS.get(plugin_id, {})
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Calculate stats from trades
        profit_col = "total_profit_dollars" if config.get("order_type") == "DUAL" else "profit_dollars"
        
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_entries,
                SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as total_exits,
                SUM(CASE WHEN direction = 'BUY' THEN 1 ELSE 0 END) as bullish_entries,
                SUM(CASE WHEN direction = 'SELL' THEN 1 ELSE 0 END) as bearish_entries,
                COALESCE(SUM({profit_col}), 0) as total_profit_dollars
            FROM {table}
            WHERE DATE(entry_time) = ?
        """, (date_str,))
        
        row = cursor.fetchone()
        stats = dict(row) if row else {}
        
        # Calculate win rate
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN {profit_col} > 0 THEN 1 ELSE 0 END) as wins
            FROM {table}
            WHERE DATE(entry_time) = ? AND status = 'CLOSED'
        """, (date_str,))
        
        wr_row = cursor.fetchone()
        if wr_row and wr_row["total"] > 0:
            stats["win_rate"] = round(wr_row["wins"] / wr_row["total"] * 100, 2)
        else:
            stats["win_rate"] = 0.0
        
        stats["profit_factor"] = 0.0
        stats["date"] = date_str
        stats["plugin_id"] = plugin_id
        
        # Upsert stats
        cursor.execute("""
            INSERT OR REPLACE INTO v6_daily_stats 
            (date, plugin_id, total_entries, total_exits, bullish_entries,
             bearish_entries, total_profit_dollars, win_rate, profit_factor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_str, plugin_id, stats.get("total_entries", 0),
            stats.get("total_exits", 0), stats.get("bullish_entries", 0),
            stats.get("bearish_entries", 0), stats.get("total_profit_dollars", 0),
            stats.get("win_rate", 0), stats.get("profit_factor", 0)
        ))
        conn.commit()
        
        return stats
    
    def get_statistics(self, plugin_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get overall V6 statistics.
        
        Args:
            plugin_id: Optional plugin filter
            
        Returns:
            Statistics dictionary
        """
        stats = {}
        
        plugins = [plugin_id] if plugin_id else list(self.PLUGIN_TABLES.keys())
        
        for pid in plugins:
            table = self.get_table_for_plugin(pid)
            config = self.PLUGIN_CONFIGS.get(pid, {})
            profit_col = "total_profit_dollars" if config.get("order_type") == "DUAL" else "profit_dollars"
            
            conn = self.connect()
            cursor = conn.cursor()
            
            # Total trades
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_trades = cursor.fetchone()[0]
            
            # Open trades
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE status IN ('OPEN', 'PARTIAL')")
            open_trades = cursor.fetchone()[0]
            
            # Total profit
            cursor.execute(f"SELECT COALESCE(SUM({profit_col}), 0) FROM {table} WHERE status = 'CLOSED'")
            total_profit = cursor.fetchone()[0]
            
            stats[pid] = {
                "total_trades": total_trades,
                "open_trades": open_trades,
                "total_profit": round(total_profit, 2)
            }
        
        return stats
