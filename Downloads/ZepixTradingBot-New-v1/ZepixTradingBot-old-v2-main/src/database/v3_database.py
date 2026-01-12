"""
V3 Combined Logic Database Schema

Document 09: Database Schema Designs
Implements the V3 Combined Logic database schema with:
- combined_v3_trades: Main trades table with dual order support
- v3_profit_bookings: Profit booking records
- v3_signals_log: Signal logging
- v3_daily_stats: Daily statistics
"""

import sqlite3
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from .schemas import BaseSchema

logger = logging.getLogger(__name__)


class V3Schema(BaseSchema):
    """
    V3 Combined Logic Database Schema.
    
    Database: data/zepix_combined.db
    
    Tables:
    - combined_v3_trades: Main trades with dual order (A+B) support
    - v3_profit_bookings: Partial close and profit booking records
    - v3_signals_log: All received V3 signals
    - v3_daily_stats: Daily aggregated statistics
    """
    
    def get_schema_sql(self) -> List[str]:
        """Get V3 schema SQL statements."""
        return [
            # combined_v3_trades table
            """
            CREATE TABLE IF NOT EXISTS combined_v3_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Order Identification
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
                
                -- V3 Specific: Signal Details
                signal_type TEXT NOT NULL,
                signal_timeframe TEXT,
                consensus_score INTEGER CHECK(consensus_score BETWEEN 0 AND 9),
                position_multiplier REAL,
                
                -- V3 Specific: MTF 4-Pillar Trends
                mtf_15m INTEGER CHECK(mtf_15m IN (-1, 0, 1)),
                mtf_1h INTEGER CHECK(mtf_1h IN (-1, 0, 1)),
                mtf_4h INTEGER CHECK(mtf_4h IN (-1, 0, 1)),
                mtf_1d INTEGER CHECK(mtf_1d IN (-1, 0, 1)),
                mtf_raw_string TEXT,
                
                -- V3 Specific: Routing
                logic_route TEXT CHECK(logic_route IN ('LOGIC1', 'LOGIC2', 'LOGIC3')),
                logic_multiplier REAL,
                routing_reason TEXT,
                
                -- V3 Specific: Dual Order Details
                order_a_lot_size REAL,
                order_b_lot_size REAL,
                order_a_sl_price REAL,
                order_b_sl_price REAL,
                order_a_tp_price REAL,
                order_b_tp_price REAL,
                
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
                trend_bypass_used BOOLEAN DEFAULT 0,
                is_entry_v3_signal BOOLEAN DEFAULT 0,
                close_reason TEXT,
                notes TEXT
            )
            """,
            
            # v3_profit_bookings table
            """
            CREATE TABLE IF NOT EXISTS v3_profit_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL,
                order_type TEXT CHECK(order_type IN ('ORDER_A', 'ORDER_B')),
                booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_percentage REAL NOT NULL,
                closed_volume REAL NOT NULL,
                profit_pips REAL,
                profit_dollars REAL,
                reason TEXT,
                FOREIGN KEY (trade_id) REFERENCES combined_v3_trades(id)
            )
            """,
            
            # v3_signals_log table
            """
            CREATE TABLE IF NOT EXISTS v3_signals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                signal_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT,
                timeframe TEXT,
                consensus_score INTEGER,
                mtf_raw_string TEXT,
                signal_json TEXT,
                processed BOOLEAN DEFAULT 0,
                trade_placed BOOLEAN DEFAULT 0,
                trade_id INTEGER,
                skip_reason TEXT,
                FOREIGN KEY (trade_id) REFERENCES combined_v3_trades(id)
            )
            """,
            
            # v3_daily_stats table
            """
            CREATE TABLE IF NOT EXISTS v3_daily_stats (
                date TEXT PRIMARY KEY,
                total_dual_entries INTEGER DEFAULT 0,
                total_order_a_closed INTEGER DEFAULT 0,
                total_order_b_closed INTEGER DEFAULT 0,
                logic1_trades INTEGER DEFAULT 0,
                logic2_trades INTEGER DEFAULT 0,
                logic3_trades INTEGER DEFAULT 0,
                total_profit_dollars REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0
            )
            """
        ]
    
    def get_indexes_sql(self) -> List[str]:
        """Get V3 index SQL statements."""
        return [
            "CREATE INDEX IF NOT EXISTS idx_v3_trades_status ON combined_v3_trades(status)",
            "CREATE INDEX IF NOT EXISTS idx_v3_trades_symbol ON combined_v3_trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_v3_trades_signal_type ON combined_v3_trades(signal_type)",
            "CREATE INDEX IF NOT EXISTS idx_v3_trades_logic_route ON combined_v3_trades(logic_route)",
            "CREATE INDEX IF NOT EXISTS idx_v3_trades_entry_time ON combined_v3_trades(entry_time)",
            "CREATE INDEX IF NOT EXISTS idx_v3_signals_processed ON v3_signals_log(processed)",
            "CREATE INDEX IF NOT EXISTS idx_v3_signals_symbol ON v3_signals_log(symbol)"
        ]


class V3Database:
    """
    V3 Combined Logic Database Manager.
    
    Provides CRUD operations for V3 trades, signals, and statistics.
    """
    
    DB_PATH = "data/zepix_combined.db"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize V3 database.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or self.DB_PATH
        self.schema = V3Schema(self.db_path)
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
    # Trade Operations
    # =========================================================================
    
    def save_trade(self, trade_data: Dict[str, Any]) -> int:
        """
        Save a new V3 trade.
        
        Args:
            trade_data: Trade data dictionary
            
        Returns:
            Trade ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        columns = [
            "symbol", "direction", "entry_price", "signal_type",
            "signal_timeframe", "consensus_score", "position_multiplier",
            "mtf_15m", "mtf_1h", "mtf_4h", "mtf_1d", "mtf_raw_string",
            "logic_route", "logic_multiplier", "routing_reason",
            "order_a_ticket", "order_b_ticket", "order_a_lot_size", "order_b_lot_size",
            "order_a_sl_price", "order_b_sl_price", "order_a_tp_price", "order_b_tp_price",
            "order_a_status", "order_b_status", "trend_bypass_used", "is_entry_v3_signal"
        ]
        
        values = [trade_data.get(col) for col in columns]
        placeholders = ", ".join(["?" for _ in columns])
        columns_str = ", ".join(columns)
        
        cursor.execute(
            f"INSERT INTO combined_v3_trades ({columns_str}) VALUES ({placeholders})",
            values
        )
        conn.commit()
        
        trade_id = cursor.lastrowid
        self.logger.info(f"Saved V3 trade {trade_id}")
        return trade_id
    
    def get_trade(self, trade_id: int) -> Optional[Dict[str, Any]]:
        """
        Get trade by ID.
        
        Args:
            trade_id: Trade ID
            
        Returns:
            Trade data dictionary or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM combined_v3_trades WHERE id = ?", (trade_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_trade_by_ticket(self, ticket: int) -> Optional[Dict[str, Any]]:
        """
        Get trade by MT5 ticket (Order A or B).
        
        Args:
            ticket: MT5 ticket number
            
        Returns:
            Trade data dictionary or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM combined_v3_trades WHERE order_a_ticket = ? OR order_b_ticket = ?",
            (ticket, ticket)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_open_trades(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open trades.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of trade dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute(
                "SELECT * FROM combined_v3_trades WHERE status IN ('OPEN', 'PARTIAL') AND symbol = ?",
                (symbol,)
            )
        else:
            cursor.execute(
                "SELECT * FROM combined_v3_trades WHERE status IN ('OPEN', 'PARTIAL')"
            )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_trade(self, trade_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update trade fields.
        
        Args:
            trade_id: Trade ID
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [trade_id]
        
        cursor.execute(
            f"UPDATE combined_v3_trades SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def close_order_a(self, trade_id: int, exit_price: float, profit_pips: float,
                      profit_dollars: float) -> bool:
        """
        Close Order A for a trade.
        
        Args:
            trade_id: Trade ID
            exit_price: Exit price
            profit_pips: Profit in pips
            profit_dollars: Profit in dollars
            
        Returns:
            True if closed successfully
        """
        return self.update_trade(trade_id, {
            "order_a_exit_price": exit_price,
            "order_a_exit_time": datetime.now().isoformat(),
            "order_a_profit_pips": profit_pips,
            "order_a_profit_dollars": profit_dollars,
            "order_a_status": "CLOSED"
        })
    
    def close_order_b(self, trade_id: int, exit_price: float, profit_pips: float,
                      profit_dollars: float) -> bool:
        """
        Close Order B for a trade.
        
        Args:
            trade_id: Trade ID
            exit_price: Exit price
            profit_pips: Profit in pips
            profit_dollars: Profit in dollars
            
        Returns:
            True if closed successfully
        """
        return self.update_trade(trade_id, {
            "order_b_exit_price": exit_price,
            "order_b_exit_time": datetime.now().isoformat(),
            "order_b_profit_pips": profit_pips,
            "order_b_profit_dollars": profit_dollars,
            "order_b_status": "CLOSED"
        })
    
    def close_trade(self, trade_id: int, total_profit_pips: float,
                    total_profit_dollars: float, close_reason: str) -> bool:
        """
        Close entire trade (both orders).
        
        Args:
            trade_id: Trade ID
            total_profit_pips: Total profit in pips
            total_profit_dollars: Total profit in dollars
            close_reason: Reason for closing
            
        Returns:
            True if closed successfully
        """
        return self.update_trade(trade_id, {
            "status": "CLOSED",
            "exit_time": datetime.now().isoformat(),
            "total_profit_pips": total_profit_pips,
            "total_profit_dollars": total_profit_dollars,
            "close_reason": close_reason
        })
    
    # =========================================================================
    # Signal Operations
    # =========================================================================
    
    def log_signal(self, signal_data: Dict[str, Any]) -> int:
        """
        Log a received signal.
        
        Args:
            signal_data: Signal data dictionary
            
        Returns:
            Signal log ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO v3_signals_log 
            (signal_type, symbol, direction, timeframe, consensus_score, 
             mtf_raw_string, signal_json, processed, trade_placed, skip_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal_data.get("signal_type"),
            signal_data.get("symbol"),
            signal_data.get("direction"),
            signal_data.get("timeframe"),
            signal_data.get("consensus_score"),
            signal_data.get("mtf_raw_string"),
            signal_data.get("signal_json"),
            signal_data.get("processed", False),
            signal_data.get("trade_placed", False),
            signal_data.get("skip_reason")
        ))
        conn.commit()
        
        return cursor.lastrowid
    
    def update_signal_processed(self, signal_id: int, trade_id: Optional[int] = None,
                                 trade_placed: bool = False) -> bool:
        """
        Update signal as processed.
        
        Args:
            signal_id: Signal log ID
            trade_id: Associated trade ID (if trade was placed)
            trade_placed: Whether a trade was placed
            
        Returns:
            True if updated successfully
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE v3_signals_log 
            SET processed = 1, trade_placed = ?, trade_id = ?
            WHERE id = ?
        """, (trade_placed, trade_id, signal_id))
        conn.commit()
        
        return cursor.rowcount > 0
    
    # =========================================================================
    # Statistics Operations
    # =========================================================================
    
    def get_daily_stats(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Get daily statistics.
        
        Args:
            date_str: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Daily stats dictionary
        """
        if not date_str:
            date_str = date.today().isoformat()
        
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM v3_daily_stats WHERE date = ?", (date_str,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        
        # Return empty stats if not found
        return {
            "date": date_str,
            "total_dual_entries": 0,
            "total_order_a_closed": 0,
            "total_order_b_closed": 0,
            "logic1_trades": 0,
            "logic2_trades": 0,
            "logic3_trades": 0,
            "total_profit_dollars": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0
        }
    
    def update_daily_stats(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Recalculate and update daily statistics.
        
        Args:
            date_str: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Updated daily stats dictionary
        """
        if not date_str:
            date_str = date.today().isoformat()
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Calculate stats from trades
        cursor.execute("""
            SELECT 
                COUNT(*) as total_dual_entries,
                SUM(CASE WHEN order_a_status = 'CLOSED' THEN 1 ELSE 0 END) as total_order_a_closed,
                SUM(CASE WHEN order_b_status = 'CLOSED' THEN 1 ELSE 0 END) as total_order_b_closed,
                SUM(CASE WHEN logic_route = 'LOGIC1' THEN 1 ELSE 0 END) as logic1_trades,
                SUM(CASE WHEN logic_route = 'LOGIC2' THEN 1 ELSE 0 END) as logic2_trades,
                SUM(CASE WHEN logic_route = 'LOGIC3' THEN 1 ELSE 0 END) as logic3_trades,
                COALESCE(SUM(total_profit_dollars), 0) as total_profit_dollars
            FROM combined_v3_trades
            WHERE DATE(entry_time) = ?
        """, (date_str,))
        
        row = cursor.fetchone()
        stats = dict(row) if row else {}
        
        # Calculate win rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN total_profit_dollars > 0 THEN 1 ELSE 0 END) as wins
            FROM combined_v3_trades
            WHERE DATE(entry_time) = ? AND status = 'CLOSED'
        """, (date_str,))
        
        wr_row = cursor.fetchone()
        if wr_row and wr_row["total"] > 0:
            stats["win_rate"] = round(wr_row["wins"] / wr_row["total"] * 100, 2)
        else:
            stats["win_rate"] = 0.0
        
        stats["profit_factor"] = 0.0  # Would need more complex calculation
        stats["date"] = date_str
        
        # Upsert stats
        cursor.execute("""
            INSERT OR REPLACE INTO v3_daily_stats 
            (date, total_dual_entries, total_order_a_closed, total_order_b_closed,
             logic1_trades, logic2_trades, logic3_trades, total_profit_dollars, win_rate, profit_factor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_str, stats.get("total_dual_entries", 0), stats.get("total_order_a_closed", 0),
            stats.get("total_order_b_closed", 0), stats.get("logic1_trades", 0),
            stats.get("logic2_trades", 0), stats.get("logic3_trades", 0),
            stats.get("total_profit_dollars", 0), stats.get("win_rate", 0),
            stats.get("profit_factor", 0)
        ))
        conn.commit()
        
        return stats
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall V3 statistics.
        
        Returns:
            Statistics dictionary
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Total trades
        cursor.execute("SELECT COUNT(*) FROM combined_v3_trades")
        total_trades = cursor.fetchone()[0]
        
        # Open trades
        cursor.execute("SELECT COUNT(*) FROM combined_v3_trades WHERE status IN ('OPEN', 'PARTIAL')")
        open_trades = cursor.fetchone()[0]
        
        # Closed trades
        cursor.execute("SELECT COUNT(*) FROM combined_v3_trades WHERE status = 'CLOSED'")
        closed_trades = cursor.fetchone()[0]
        
        # Total profit
        cursor.execute("SELECT COALESCE(SUM(total_profit_dollars), 0) FROM combined_v3_trades WHERE status = 'CLOSED'")
        total_profit = cursor.fetchone()[0]
        
        # Win rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN total_profit_dollars > 0 THEN 1 ELSE 0 END) as wins
            FROM combined_v3_trades WHERE status = 'CLOSED'
        """)
        wr_row = cursor.fetchone()
        win_rate = round(wr_row["wins"] / wr_row["total"] * 100, 2) if wr_row["total"] > 0 else 0.0
        
        return {
            "total_trades": total_trades,
            "open_trades": open_trades,
            "closed_trades": closed_trades,
            "total_profit": round(total_profit, 2),
            "win_rate": win_rate
        }
