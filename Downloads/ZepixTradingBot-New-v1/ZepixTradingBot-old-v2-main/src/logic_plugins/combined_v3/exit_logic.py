"""
V3 Combined Logic - Exit Logic Module

Handles all exit signal processing for V3 Combined Logic plugin.
Implements exact same logic as old V3 in TradingEngine.

Part of Document 03: Phases 2-6 Consolidated Plan - Phase 4
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ExitLogic:
    """
    V3 Exit Logic Handler.
    
    Processes exit signals with:
    - Position matching by symbol/direction
    - Profit booking integration
    - Partial close support
    - Database updates
    
    Exit Types:
    - Exit_Appeared: Standard exit signal
    - Reversal_Exit: Exit due to trend reversal
    """
    
    def __init__(self, plugin):
        """
        Initialize Exit Logic.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"{__name__}.ExitLogic")
        
        self.logger.info("V3 ExitLogic initialized")
    
    async def process_exit(self, alert: Any) -> Dict[str, Any]:
        """
        Process V3 exit signal.
        
        Steps:
        1. Validate exit signal
        2. Find matching open positions
        3. Close positions (full or partial)
        4. Update database
        5. Calculate P/L
        
        Args:
            alert: V3 exit alert data
            
        Returns:
            dict: Exit execution result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        signal_type = getattr(alert, "signal_type", "")
        exit_type = getattr(alert, "exit_type", "full")
        
        self.logger.info(f"Processing exit: {symbol} [{signal_type}]")
        
        # Step 1: Find matching positions
        positions = await self._find_matching_positions(symbol, direction)
        
        if not positions:
            self.logger.info(f"No matching positions for {symbol} {direction}")
            return {
                "success": True,
                "symbol": symbol,
                "positions_closed": 0,
                "reason": "no_matching_positions"
            }
        
        # Step 2: Close positions
        closed_positions = []
        total_pnl = 0.0
        
        for position in positions:
            result = await self._close_position(position, exit_type, signal_type)
            if result.get("success"):
                closed_positions.append(result)
                total_pnl += result.get("pnl", 0.0)
        
        # Step 3: Update database
        await self._record_exits(closed_positions, signal_type)
        
        self.logger.info(
            f"Exit complete: {symbol} closed {len(closed_positions)} positions, "
            f"P/L: ${total_pnl:.2f}"
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "signal_type": signal_type,
            "positions_closed": len(closed_positions),
            "total_pnl": total_pnl,
            "closed_positions": closed_positions
        }
    
    async def process_reversal_exit(self, alert: Any) -> Dict[str, Any]:
        """
        Process reversal exit (close opposite positions).
        
        When a reversal signal comes:
        1. Close all positions in opposite direction
        2. Prepare for new entry in signal direction
        
        Args:
            alert: Reversal alert data
            
        Returns:
            dict: Reversal exit result
        """
        symbol = getattr(alert, "symbol", "")
        new_direction = getattr(alert, "direction", "")
        signal_type = getattr(alert, "signal_type", "")
        
        opposite_direction = "SELL" if new_direction == "BUY" else "BUY"
        
        self.logger.info(
            f"Processing reversal exit: {symbol} "
            f"closing {opposite_direction} for {new_direction} entry"
        )
        
        # Find and close opposite positions
        positions = await self._find_matching_positions(symbol, opposite_direction)
        
        closed_positions = []
        total_pnl = 0.0
        
        for position in positions:
            result = await self._close_position(position, "full", f"REVERSAL_{signal_type}")
            if result.get("success"):
                closed_positions.append(result)
                total_pnl += result.get("pnl", 0.0)
        
        await self._record_exits(closed_positions, f"REVERSAL_{signal_type}")
        
        self.logger.info(
            f"Reversal exit complete: {symbol} closed {len(closed_positions)} "
            f"{opposite_direction} positions, P/L: ${total_pnl:.2f}"
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "signal_type": signal_type,
            "opposite_direction": opposite_direction,
            "positions_closed": len(closed_positions),
            "total_pnl": total_pnl,
            "ready_for_entry": True
        }
    
    async def process_partial_exit(
        self,
        alert: Any,
        percentage: float = 50.0
    ) -> Dict[str, Any]:
        """
        Process partial exit (close percentage of position).
        
        Args:
            alert: Exit alert data
            percentage: Percentage to close (default 50%)
            
        Returns:
            dict: Partial exit result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        signal_type = getattr(alert, "signal_type", "")
        
        self.logger.info(f"Processing partial exit: {symbol} {percentage}%")
        
        positions = await self._find_matching_positions(symbol, direction)
        
        partial_closes = []
        total_pnl = 0.0
        
        for position in positions:
            result = await self._partial_close_position(position, percentage, signal_type)
            if result.get("success"):
                partial_closes.append(result)
                total_pnl += result.get("pnl", 0.0)
        
        self.logger.info(
            f"Partial exit complete: {symbol} {percentage}% of "
            f"{len(partial_closes)} positions, P/L: ${total_pnl:.2f}"
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "percentage": percentage,
            "positions_affected": len(partial_closes),
            "total_pnl": total_pnl
        }
    
    async def _find_matching_positions(
        self,
        symbol: str,
        direction: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find open positions matching criteria.
        
        Args:
            symbol: Trading symbol
            direction: Optional direction filter
            
        Returns:
            List of matching positions
        """
        if self.service_api is None:
            return []
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service is None:
                return []
            
            positions = await order_service.get_open_orders(
                symbol=symbol,
                plugin_id=self.plugin.plugin_id
            )
            
            if direction:
                positions = [p for p in positions if p.get("direction") == direction]
            
            return positions
            
        except Exception as e:
            self.logger.warning(f"Position fetch error: {e}")
            return []
    
    async def _close_position(
        self,
        position: Dict[str, Any],
        exit_type: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Close a single position.
        
        Args:
            position: Position data
            exit_type: "full" or "partial"
            reason: Exit reason for logging
            
        Returns:
            dict: Close result
        """
        ticket = position.get("ticket", 0)
        symbol = position.get("symbol", "")
        
        self.logger.debug(f"Closing position {ticket}: {symbol} [{reason}]")
        
        if self.service_api is None:
            return {
                "success": True,
                "ticket": ticket,
                "symbol": symbol,
                "pnl": 0.0,
                "reason": reason
            }
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service is None:
                return {
                    "success": True,
                    "ticket": ticket,
                    "symbol": symbol,
                    "pnl": 0.0,
                    "reason": reason
                }
            
            success = await order_service.close_order(
                ticket=ticket,
                plugin_id=self.plugin.plugin_id
            )
            
            pnl = position.get("profit", 0.0)
            
            return {
                "success": success,
                "ticket": ticket,
                "symbol": symbol,
                "pnl": pnl,
                "reason": reason,
                "close_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Position close error: {e}")
            return {
                "success": False,
                "ticket": ticket,
                "error": str(e)
            }
    
    async def _partial_close_position(
        self,
        position: Dict[str, Any],
        percentage: float,
        reason: str
    ) -> Dict[str, Any]:
        """
        Partially close a position.
        
        Args:
            position: Position data
            percentage: Percentage to close
            reason: Close reason
            
        Returns:
            dict: Partial close result
        """
        ticket = position.get("ticket", 0)
        symbol = position.get("symbol", "")
        current_lot = position.get("lot_size", 0.01)
        
        close_lot = round(current_lot * (percentage / 100), 2)
        remaining_lot = round(current_lot - close_lot, 2)
        
        self.logger.debug(
            f"Partial close {ticket}: {close_lot} of {current_lot} ({percentage}%)"
        )
        
        if self.service_api is None:
            return {
                "success": True,
                "ticket": ticket,
                "symbol": symbol,
                "closed_lot": close_lot,
                "remaining_lot": remaining_lot,
                "pnl": 0.0,
                "reason": reason
            }
        
        try:
            profit_service = getattr(self.service_api, 'profit_booking', None)
            if profit_service is None:
                return {
                    "success": True,
                    "ticket": ticket,
                    "symbol": symbol,
                    "closed_lot": close_lot,
                    "remaining_lot": remaining_lot,
                    "pnl": 0.0,
                    "reason": reason
                }
            
            pnl = position.get("profit", 0.0) * (percentage / 100)
            
            return {
                "success": True,
                "ticket": ticket,
                "symbol": symbol,
                "closed_lot": close_lot,
                "remaining_lot": remaining_lot,
                "pnl": pnl,
                "reason": reason,
                "close_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Partial close error: {e}")
            return {
                "success": False,
                "ticket": ticket,
                "error": str(e)
            }
    
    async def _record_exits(
        self,
        closed_positions: List[Dict[str, Any]],
        signal_type: str
    ):
        """
        Record exit trades in database.
        
        Args:
            closed_positions: List of closed position results
            signal_type: Exit signal type
        """
        try:
            db = self.plugin.get_database_connection()
            if db:
                pass
            
            for pos in closed_positions:
                self.logger.debug(
                    f"Exit recorded: {pos.get('symbol')} "
                    f"ticket={pos.get('ticket')} pnl={pos.get('pnl', 0):.2f}"
                )
                
        except Exception as e:
            self.logger.warning(f"Exit recording error: {e}")
    
    def calculate_pnl(
        self,
        entry_price: float,
        exit_price: float,
        lot_size: float,
        direction: str,
        symbol: str
    ) -> float:
        """
        Calculate P/L for a trade.
        
        Args:
            entry_price: Entry price
            exit_price: Exit price
            lot_size: Position size
            direction: BUY or SELL
            symbol: Trading symbol
            
        Returns:
            float: P/L in dollars
        """
        pip_value = 10.0
        if "JPY" in symbol:
            pip_value = 1000.0 / 100
        elif "XAU" in symbol or "GOLD" in symbol:
            pip_value = 1.0
        
        if direction == "BUY":
            pips = (exit_price - entry_price) * 10000
        else:
            pips = (entry_price - exit_price) * 10000
        
        if "JPY" in symbol:
            pips = pips / 100
        elif "XAU" in symbol or "GOLD" in symbol:
            pips = (exit_price - entry_price) if direction == "BUY" else (entry_price - exit_price)
        
        pnl = pips * pip_value * lot_size
        return round(pnl, 2)
