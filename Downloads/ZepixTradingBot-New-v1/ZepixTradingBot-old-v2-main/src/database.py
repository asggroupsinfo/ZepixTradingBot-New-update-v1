import sqlite3
from datetime import datetime, date
from src.models import Trade, ReEntryChain
from typing import List, Dict, Any

class TradeDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('data/trading_bot.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Main trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                trade_id TEXT,
                symbol TEXT,
                entry_price REAL,
                exit_price REAL,
                sl_price REAL,
                tp_price REAL,
                lot_size REAL,
                direction TEXT,
                strategy TEXT,
                pnl REAL,
                commission REAL,
                swap REAL,
                comment TEXT,
                status TEXT,
                open_time DATETIME,
                close_time DATETIME,
                chain_id TEXT,
                chain_level INTEGER,
                is_re_entry BOOLEAN,
                order_type TEXT,
                profit_chain_id TEXT,
                profit_level INTEGER DEFAULT 0,
                session_id TEXT,
                sl_adjusted INTEGER DEFAULT 0,
                original_sl_distance REAL DEFAULT 0.0,
                logic_type TEXT,
                base_lot_size REAL DEFAULT 0.0,
                final_lot_size REAL DEFAULT 0.0,
                base_sl_pips REAL DEFAULT 0.0,
                final_sl_pips REAL DEFAULT 0.0,
                lot_multiplier REAL DEFAULT 1.0,
                sl_multiplier REAL DEFAULT 1.0
            )
        ''')
        
        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE trades ADD COLUMN order_type TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE trades ADD COLUMN profit_chain_id TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE trades ADD COLUMN profit_level INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE trades ADD COLUMN session_id TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Add new columns for timeframe logic if they don't exist
        db_columns_to_add = [
            ("commission", "REAL"),
            ("swap", "REAL"),
            ("comment", "TEXT"),
            ("sl_adjusted", "INTEGER DEFAULT 0"),
            ("original_sl_distance", "REAL DEFAULT 0.0"),
            ("logic_type", "TEXT"),
            ("base_lot_size", "REAL DEFAULT 0.0"),
            ("final_lot_size", "REAL DEFAULT 0.0"),
            ("base_sl_pips", "REAL DEFAULT 0.0"),
            ("final_sl_pips", "REAL DEFAULT 0.0"),
            ("lot_multiplier", "REAL DEFAULT 1.0"),
            ("sl_multiplier", "REAL DEFAULT 1.0")
        ]
        
        cursor.execute("PRAGMA table_info(trades)")
        existing_columns = [info[1] for info in cursor.fetchall()]

        for col_name, col_type in db_columns_to_add:
            if col_name not in existing_columns:
                print(f"Migrating database: Adding {col_name} to trades table...")
                try:
                    cursor.execute(f"ALTER TABLE trades ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"Error adding column {col_name}: {e}")
        
        # Re-entry chains table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reentry_chains (
                chain_id TEXT PRIMARY KEY,
                symbol TEXT,
                direction TEXT,
                original_entry REAL,
                original_sl_distance REAL,
                max_level_reached INTEGER,
                total_profit REAL,
                status TEXT,
                created_at DATETIME,
                completed_at DATETIME
            )
        ''')
        
        # SL hunting events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sl_events (
                id INTEGER PRIMARY KEY,
                trade_id TEXT,
                symbol TEXT,
                sl_price REAL,
                original_entry REAL,
                hit_time DATETIME,
                recovery_attempted BOOLEAN,
                recovery_successful BOOLEAN
            )
        ''')
        
        # TP re-entry tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tp_reentry_events (
                id INTEGER PRIMARY KEY,
                chain_id TEXT,
                symbol TEXT,
                tp_level INTEGER,
                tp_price REAL,
                reentry_price REAL,
                sl_reduction_percent REAL,
                pnl REAL,
                timestamp DATETIME
            )
        ''')
        
        # Reversal exit events table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reversal_exit_events (
                id INTEGER PRIMARY KEY,
                trade_id TEXT,
                symbol TEXT,
                exit_price REAL,
                exit_signal TEXT,
                pnl REAL,
                timestamp DATETIME
            )
        ''')
        
        # System state table for pause/resume control
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME
            )
        ''')
        
        # Profit booking chains table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profit_booking_chains (
                chain_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                base_lot REAL NOT NULL,
                current_level INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0,
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Profit booking orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profit_booking_orders (
                order_id TEXT PRIMARY KEY,
                chain_id TEXT,
                level INTEGER,
                profit_target REAL,
                sl_reduction INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chain_id) REFERENCES profit_booking_chains(chain_id)
            )
        ''')
        
        # Profit booking events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profit_booking_events (
                id INTEGER PRIMARY KEY,
                chain_id TEXT,
                level INTEGER,
                profit_booked REAL,
                orders_closed INTEGER,
                orders_placed INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trading sessions table - NEW
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_sessions (
                session_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_signal TEXT,
                exit_reason TEXT,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                total_pnl REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ACTIVE',
                metadata TEXT
            )
        ''')
        
        self.conn.commit()

    def save_trade(self, trade: Trade):
        try:
            cursor = self.conn.cursor()
            
            # Extract timeframe logic details if available
            logic_type = getattr(trade, 'logic_type', None)
            # Default to current values if base values not available
            base_lot = getattr(trade, 'base_lot_size', trade.lot_size)
            final_lot = trade.lot_size
            
            # Calculate SL pips if possible
            base_sl_pips = getattr(trade, 'base_sl_pips', 0.0)
            final_sl_pips = 0.0
            if trade.entry and trade.sl:
                final_sl_pips = abs(trade.entry - trade.sl)
                # Normalize if we have pip size info, otherwise store raw price diff
                if hasattr(trade, 'symbol') and "JPY" in trade.symbol:
                     final_sl_pips *= 100
                else:
                     final_sl_pips *= 10000
            
            lot_mult = getattr(trade, 'lot_multiplier', 1.0)
            sl_mult = getattr(trade, 'sl_multiplier', 1.0)
            
            # Get close_price if exists
            close_price = getattr(trade, 'close_price', None)
            
            cursor.execute("""
                INSERT OR REPLACE INTO trades (
                    trade_id, symbol, entry_price, exit_price, sl_price, tp_price, lot_size, direction, 
                    strategy, pnl, commission, swap, comment, status, open_time, close_time, 
                    chain_id, chain_level, is_re_entry, order_type, profit_chain_id, profit_level, 
                    session_id, sl_adjusted, original_sl_distance,
                    logic_type, base_lot_size, final_lot_size, base_sl_pips, final_sl_pips,
                    lot_multiplier, sl_multiplier
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.trade_id, trade.symbol, trade.entry, close_price, trade.sl, 
                trade.tp, trade.lot_size, trade.direction, trade.strategy, trade.pnl, 
                getattr(trade, 'commission', 0.0), getattr(trade, 'swap', 0.0), getattr(trade, 'comment', None),
                trade.status, trade.open_time, trade.close_time, getattr(trade, 'chain_id', None), 
                getattr(trade, 'chain_level', 1), getattr(trade, 'is_re_entry', False), getattr(trade, 'order_type', None), 
                getattr(trade, 'profit_chain_id', None), getattr(trade, 'profit_level', 0), getattr(trade, 'session_id', None),
                getattr(trade, 'sl_adjusted', 0), getattr(trade, 'original_sl_distance', 0.0),
                logic_type, base_lot, final_lot, base_sl_pips, final_sl_pips, lot_mult, sl_mult
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving trade: {e}")

    def save_chain(self, chain: ReEntryChain):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO reentry_chains VALUES (?,?,?,?,?,?,?,?,?,?)
        ''', (chain.chain_id, chain.symbol, chain.direction, 
              chain.original_entry, chain.original_sl_distance,
              chain.current_level, chain.total_profit, chain.status,
              chain.created_at, datetime.now().isoformat() if chain.status == "completed" else None))
        self.conn.commit()

    def save_sl_event(self, trade_id: str, symbol: str, sl_price: float, 
                     original_entry: float, recovery_attempted: bool = False,
                     recovery_successful: bool = False):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sl_events VALUES (?,?,?,?,?,?,?,?)
        ''', (None, trade_id, symbol, sl_price, original_entry, 
              datetime.now().isoformat(), recovery_attempted, recovery_successful))
        self.conn.commit()

    def get_trade_history(self, days=30) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trades 
            WHERE close_time >= datetime('now', ?)
            ORDER BY close_time DESC
        ''', (f'-{days} days',))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_chain_statistics(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        
        # Get chain performance
        cursor.execute('''
            SELECT 
                COUNT(*) as total_chains,
                AVG(max_level_reached) as avg_max_level,
                SUM(total_profit) as total_chain_profit,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_chains,
                COUNT(CASE WHEN total_profit > 0 THEN 1 END) as profitable_chains
            FROM reentry_chains
        ''')
        
        result = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        
        return dict(zip(columns, result))

    def get_sl_recovery_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sl_hits,
                COUNT(CASE WHEN recovery_attempted THEN 1 END) as recovery_attempts,
                COUNT(CASE WHEN recovery_successful THEN 1 END) as successful_recoveries
            FROM sl_events
            WHERE hit_time >= datetime('now', '-30 days')
        ''')
        
        result = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        
        return dict(zip(columns, result))
    
    def clear_lifetime_losses(self):
        """Reset lifetime loss counter (database side)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE system_state SET value = '0', updated_at = ? WHERE key = 'lifetime_loss'
        ''', (datetime.now().isoformat(),))
        self.conn.commit()
        
    def get_tp_reentry_stats(self) -> Dict[str, Any]:
        """Get TP re-entry statistics"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_tp_reentries,
                SUM(pnl) as total_tp_reentry_pnl,
                AVG(pnl) as avg_tp_reentry_pnl,
                COUNT(CASE WHEN pnl > 0 THEN 1 END) as profitable_tp_reentries
            FROM tp_reentry_events
            WHERE timestamp >= datetime('now', '-30 days')
        ''')
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result)) if result else {}
    
    def get_sl_hunt_reentry_stats(self) -> Dict[str, Any]:
        """Get SL hunt re-entry statistics (from sl_events where recovery_successful=1)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN recovery_successful THEN 1 END) as total_sl_hunt_reentries,
                COUNT(CASE WHEN recovery_attempted THEN 1 END) as sl_hunt_attempts
            FROM sl_events
            WHERE hit_time >= datetime('now', '-30 days')
        ''')
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result)) if result else {}
    
    def get_trades_by_date(self, target_date: date) -> List[Dict[str, Any]]:
        """
        Get trades closed on a specific date
        Returns: List of trade dictionaries with PnL
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM trades 
                WHERE DATE(close_time) = DATE(?) AND status = 'closed'
                ORDER BY close_time DESC
            ''', (target_date.isoformat(),))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting trades by date: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test database connection
        Returns: True if connection is working, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def save_profit_chain(self, chain):
        """Save profit booking chain to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO profit_booking_chains 
            (chain_id, symbol, direction, base_lot, current_level, total_profit, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chain.chain_id,
            chain.symbol,
            chain.direction,
            chain.base_lot,
            chain.current_level,
            chain.total_profit,
            chain.status,
            chain.created_at,
            chain.updated_at
        ))
        self.conn.commit()
    
    def get_active_profit_chains(self) -> List[Dict[str, Any]]:
        """Get all active profit booking chains from database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM profit_booking_chains
            WHERE status = 'ACTIVE'
        ''')
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def save_profit_booking_order(self, order_id: str, chain_id: str, level: int, 
                                  profit_target: float, sl_reduction: int, status: str):
        """Save profit booking order to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO profit_booking_orders
            (order_id, chain_id, level, profit_target, sl_reduction, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, chain_id, level, profit_target, sl_reduction, status, datetime.now().isoformat()))
        self.conn.commit()
    
    def save_profit_booking_event(self, chain_id: str, level: int, profit_booked: float,
                                  orders_closed: int, orders_placed: int):
        """Save profit booking event to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO profit_booking_events
            (chain_id, level, profit_booked, orders_closed, orders_placed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (chain_id, level, profit_booked, orders_closed, orders_placed, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_profit_chain_stats(self) -> Dict[str, Any]:
        """Get profit booking chain statistics"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_chains,
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_chains,
                COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_chains,
                AVG(current_level) as avg_level,
                SUM(total_profit) as total_profit,
                AVG(total_profit) as avg_profit_per_chain
            FROM profit_booking_chains
        ''')
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result)) if result else {}
    
    # ==================== SESSION TRACKING METHODS ====================
    
    def create_session(self, session_id: str, symbol: str, direction: str, entry_signal: str):
        """Create new trading session"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trading_sessions 
            (session_id, symbol, direction, entry_signal, start_time, status)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE')
        ''', (session_id, symbol, direction, entry_signal, datetime.now().isoformat()))
        self.conn.commit()
    
    def close_session(self, session_id: str, exit_reason: str):
        """Close trading session"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE trading_sessions
            SET status = 'COMPLETED', end_time = ?, exit_reason = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), exit_reason, session_id))
        self.conn.commit()
    
    def update_session_stats(self, session_id: str):
        """Recalculate session total_pnl and total_trades from trades table"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(pnl), 0)
            FROM trades
            WHERE session_id = ? AND status = 'closed'
        ''', (session_id,))
        
        total_trades, total_pnl = cursor.fetchone()
        
        cursor.execute('''
            UPDATE trading_sessions
            SET total_pnl = ?, total_trades = ?
            WHERE session_id = ?
        ''', (total_pnl, total_trades, session_id))
        self.conn.commit()
    
    def get_active_session(self, symbol: str = None) -> Dict[str, Any]:
        """Get active session for symbol (or any active session if symbol is None)"""
        cursor = self.conn.cursor()
        if symbol:
            cursor.execute('''
                SELECT * FROM trading_sessions
                WHERE symbol = ? AND status = 'ACTIVE'
                ORDER BY start_time DESC LIMIT 1
            ''', (symbol,))
        else:
            cursor.execute('''
                SELECT * FROM trading_sessions
                WHERE status = 'ACTIVE'
                ORDER BY start_time DESC LIMIT 1
            ''')
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return {}
    
    def get_sessions_by_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get all sessions for a specific date"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trading_sessions
            WHERE DATE(start_time) = DATE(?)
            ORDER BY start_time DESC
        ''', (target_date.isoformat(),))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session report including breakdown"""
        cursor = self.conn.cursor()
        
        # Get session info
        cursor.execute('SELECT * FROM trading_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        if not row:
            return {}
        
        columns = [desc[0] for desc in cursor.description]
        session = dict(zip(columns, row))
        
        # Get win/loss breakdown
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN pnl > 0 THEN 1 END) as wins,
                COUNT(CASE WHEN pnl < 0 THEN 1 END) as losses,
                COALESCE(SUM(CASE WHEN pnl > 0 THEN pnl END), 0) as total_profit,
                COALESCE(SUM(CASE WHEN pnl < 0 THEN pnl END), 0) as total_loss,
                COUNT(DISTINCT CASE WHEN order_type = 'DUAL_A' OR order_type = 'DUAL_B' THEN 1 END) as dual_orders,
                COUNT(DISTINCT profit_chain_id) as profit_chains,
                COUNT(CASE WHEN is_re_entry THEN 1 END) as reentries
            FROM trades
            WHERE session_id = ? AND status = 'closed'
        ''', (session_id,))
        
        breakdown = cursor.fetchone()
        if breakdown:
            cols = [desc[0] for desc in cursor.description]
            session['breakdown'] = dict(zip(cols, breakdown))
        
        return session