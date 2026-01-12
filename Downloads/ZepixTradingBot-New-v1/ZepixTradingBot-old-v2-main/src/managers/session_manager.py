"""
Session Manager - Tracks trading sessions from entry to exit
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages trading sessions - from entry signal to complete exit"""
    
    def __init__(self, config, db, mt5_client):
        self.config = config
        self.db = db
        self.mt5_client = mt5_client
        self.active_session_id: Optional[str] = None
        
        # Try to recover active session on startup
        active = self.db.get_active_session()
        if active:
            self.active_session_id = active.get('session_id')
            logger.info(f"✅ Recovered active session: {self.active_session_id}")
    
    def create_session(self, symbol: str, direction: str, signal: str, logic: str = "combinedlogic-1") -> str:
        """
        Create new trading session
        
        Args:
            symbol: Trading symbol (e.g. XAUUSD)
            direction: buy or sell
            signal: Entry signal name (e.g. BEARISH, BULLISH)
            logic: Trading logic type (combinedlogic-1, combinedlogic-2, combinedlogic-3) - Phase 6 tracking
            
        Returns:
            session_id
        """
        try:
            # Check if session already active
            if self.active_session_id:
                logger.warning(f"Session already active: {self.active_session_id}")
                return self.active_session_id
            
            # Generate unique session ID
            session_id = f"SES_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            # Create session in database
            self.db.create_session(session_id, symbol, direction, signal)
            
            # Store logic-specific metadata (Phase 6)
            import json
            metadata = {
                "logic_type": logic,
                "logic_stats": {
                    logic: {
                        "trades": 0,
                        "wins": 0,
                        "losses": 0,
                        "pnl": 0.0,
                        "avg_lot_multiplier": 0.0,
                        "avg_sl_multiplier": 0.0
                    }
                }
            }
            cursor = self.db.conn.cursor()
            cursor.execute(
                "UPDATE trading_sessions SET metadata = ? WHERE session_id = ?",
                (json.dumps(metadata), session_id)
            )
            self.db.conn.commit()
            
            self.active_session_id = session_id
            
            logger.info(
                f"📊 SESSION STARTED: {session_id}\n"
                f"   Symbol: {symbol}\n"
                f"   Direction: {direction}\n"
                f"   Signal: {signal}\n"
                f"   Logic: {logic}"
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return None
    
    def close_session(self, reason: str = "COMPLETE_EXIT"):
        """
        Close active session
        
        Args:
            reason: Exit reason (REVERSAL, EXIT_SIGNAL, LOSS_LIMIT, MANUAL, etc.)
        """
        try:
            if not self.active_session_id:
                logger.warning("No active session to close")
                return
            
            # Update final stats
            self.db.update_session_stats(self.active_session_id)
            
            # Close session
            self.db.close_session(self.active_session_id, reason)
            
            # Get final stats for logging
            details = self.db.get_session_details(self.active_session_id)
            
            logger.info(
                f"🏁 SESSION CLOSED: {self.active_session_id}\n"
                f"   Exit Reason: {reason}\n"
                f"   Total PnL: ${details.get('total_pnl', 0):.2f}\n"
                f"   Win Rate: {details.get('breakdown', {}).get('win_rate', 0):.1f}%"
            )
            
            self.active_session_id = None
            return details
            
        except Exception as e:
            logger.error(f"Error closing session: {str(e)}")
            return None
    
    def get_active_session(self) -> Optional[str]:
        """Get current active session ID"""
        return self.active_session_id
    
    def update_session(self):
        """Update session stats (call after trades close)"""
        if self.active_session_id:
            self.db.update_session_stats(self.active_session_id)
            
    def update_logic_stats(self, trade):
        """
        Update logic-specific statistics in session metadata
        
        Args:
            trade: Trade object with logic_type and outcome
        """
        if not self.active_session_id:
            return
        
        try:
            import json
            
            # Get current session
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT metadata FROM trading_sessions WHERE session_id = ?",
                (self.active_session_id,)
            )
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return
            
            metadata = json.loads(result[0])
            logic_stats = metadata.get("logic_stats", {})
            logic_type = getattr(trade, 'logic_type', getattr(trade, 'strategy', 'combinedlogic-1'))
            
            # Initialize logic stats if not exists
            if logic_type not in logic_stats:
                logic_stats[logic_type] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "pnl": 0.0,
                    "avg_lot_multiplier": 0.0,
                    "avg_sl_multiplier": 0.0
                }
            
            stats = logic_stats[logic_type]
            
            # Update stats
            stats["trades"] += 1
            stats["pnl"] += getattr(trade, 'pnl', 0.0) or 0.0
            
            if getattr(trade, 'pnl', 0) > 0:
                stats["wins"] += 1
            else:
                stats["losses"] += 1
            
            # Update multiplier averages
            lot_mult = getattr(trade, 'lot_multiplier', 1.0)
            sl_mult = getattr(trade, 'sl_multiplier', 1.0)
            
            # Calculate running average
            n = stats["trades"]
            stats["avg_lot_multiplier"] = ((stats["avg_lot_multiplier"] * (n-1)) + lot_mult) / n
            stats["avg_sl_multiplier"] = ((stats["avg_sl_multiplier"] * (n-1)) + sl_mult) / n
            
            # Save updated metadata
            metadata["logic_stats"] = logic_stats
            cursor.execute(
                "UPDATE trading_sessions SET metadata = ? WHERE session_id = ?",
                (json.dumps(metadata), self.active_session_id)
            )
            self.db.conn.commit()
            
            logger.info(
                f"📈 Logic Stats Updated: {logic_type}\n"
                f"   Trades: {stats['trades']} | Wins: {stats['wins']} | Losses: {stats['losses']}\n"
                f"   PnL: ${stats['pnl']:.2f} | Avg Lot Mult: {stats['avg_lot_multiplier']:.2f}x"
            )
            
        except Exception as e:
            logger.error(f"Error updating logic stats: {str(e)}")
    
    def check_session_end(self, open_trades: list):
        """
        Check if session should end (all positions closed)
        
        Args:
            open_trades: List of currently open trades
        """
        if not self.active_session_id:
            return
        
        # Get session
        session = self.db.get_active_session(self.active_session_id)
        if not session:
            return
        
        # Check if any trades for this session are still open
        session_has_open_trades = any(
            t.session_id == self.active_session_id and t.status == 'open'
            for t in open_trades
        )
        
        if not session_has_open_trades:
            total_trades = session.get('total_trades', 0)
            if total_trades > 0:  # Only close if trades were actually made
                logger.info(f"All positions closed for session {self.active_session_id}")
                return self.close_session("AUTO_COMPLETE")
            return None
    
    def get_today_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions for today"""
        from datetime import date
        return self.db.get_sessions_by_date(date.today())
    
    def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session report"""
        return self.db.get_session_details(session_id)
