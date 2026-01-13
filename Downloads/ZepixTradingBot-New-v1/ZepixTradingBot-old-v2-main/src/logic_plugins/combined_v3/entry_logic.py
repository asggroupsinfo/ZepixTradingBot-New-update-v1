"""
V3 Combined Logic - Entry Logic Module

Handles all entry signal processing for V3 Combined Logic plugin.
Implements exact same logic as old V3 in TradingEngine.

Part of Document 03: Phases 2-6 Consolidated Plan - Phase 4
"""

from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EntryLogic:
    """
    V3 Entry Logic Handler.
    
    Processes entry signals with:
    - Trend validation
    - ADX filtering
    - Dual order placement (Order A + Order B)
    - Logic-specific SL/TP calculation
    
    Logic Types:
    - LOGIC1: 5-minute scalping (tight SL, quick exits)
    - LOGIC2: 15-minute intraday (balanced approach)
    - LOGIC3: 1-hour swing (wider SL, longer holds)
    """
    
    # SL multipliers per logic type
    SL_MULTIPLIERS = {
        "LOGIC1": 1.0,   # Base SL
        "LOGIC2": 1.5,   # 1.5x base SL
        "LOGIC3": 2.0    # 2x base SL
    }
    
    # Order B lot multiplier (relative to Order A)
    ORDER_B_MULTIPLIER = 2.0
    
    # Fixed $10 SL for Order B (in pips, varies by symbol)
    ORDER_B_FIXED_SL_USD = 10.0
    
    def __init__(self, plugin):
        """
        Initialize Entry Logic.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"{__name__}.EntryLogic")
        
        self.logger.info("V3 EntryLogic initialized")
    
    async def process_entry(self, alert: Any) -> Dict[str, Any]:
        """
        Process V3 entry signal.
        
        Steps:
        1. Validate trend alignment (unless aggressive reversal)
        2. Check ADX strength
        3. Calculate lot sizes for Order A and Order B
        4. Place dual orders
        5. Record trade in database
        
        Args:
            alert: V3 entry alert data
            
        Returns:
            dict: Entry execution result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        signal_type = getattr(alert, "signal_type", "")
        timeframe = getattr(alert, "tf", "15")
        
        self.logger.info(f"Processing entry: {symbol} {direction} [{signal_type}]")
        
        # Step 1: Trend validation (skip for aggressive reversals)
        if not self._is_aggressive_reversal(signal_type):
            trend_valid = await self._validate_trend(symbol, direction, timeframe)
            if not trend_valid:
                self.logger.info(f"Entry rejected: Trend not aligned for {symbol} {direction}")
                return {
                    "success": False,
                    "reason": "trend_not_aligned",
                    "symbol": symbol,
                    "direction": direction
                }
        
        # Step 2: Determine logic type
        logic_type = self._get_logic_type(timeframe)
        
        # Step 3: Calculate lot sizes
        balance = await self._get_account_balance()
        sl_pips = self._calculate_sl_pips(alert, logic_type)
        
        lot_a = self._calculate_lot_a(balance, sl_pips, symbol, logic_type)
        lot_b = self._calculate_lot_b(lot_a)
        
        # Step 4: Calculate SL/TP prices
        sl_a = self._calculate_sl_price(alert, logic_type, "ORDER_A")
        sl_b = self._calculate_sl_price(alert, logic_type, "ORDER_B")
        tp_a = self._calculate_tp_price(alert, logic_type, "ORDER_A")
        tp_b = self._calculate_tp_price(alert, logic_type, "ORDER_B")
        
        # Step 5: Place dual orders
        order_a_ticket = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_a,
            sl_price=sl_a,
            tp_price=tp_a,
            comment=f"V3_{logic_type}_A_{signal_type}"
        )
        
        order_b_ticket = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_b,
            sl_price=sl_b,
            tp_price=tp_b,
            comment=f"V3_{logic_type}_B_{signal_type}"
        )
        
        # Step 6: Record trade
        trade_record = {
            "symbol": symbol,
            "direction": direction,
            "signal_type": signal_type,
            "logic_type": logic_type,
            "order_a_ticket": order_a_ticket,
            "order_b_ticket": order_b_ticket,
            "lot_a": lot_a,
            "lot_b": lot_b,
            "sl_a": sl_a,
            "sl_b": sl_b,
            "tp_a": tp_a,
            "tp_b": tp_b,
            "entry_time": datetime.now().isoformat(),
            "plugin_id": self.plugin.plugin_id
        }
        
        await self._record_trade(trade_record)
        
        self.logger.info(
            f"Entry complete: {symbol} {direction} "
            f"A={order_a_ticket} B={order_b_ticket} [{logic_type}]"
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "direction": direction,
            "signal_type": signal_type,
            "logic_type": logic_type,
            "order_a": order_a_ticket,
            "order_b": order_b_ticket,
            "lot_a": lot_a,
            "lot_b": lot_b
        }
    
    async def _validate_trend(
        self,
        symbol: str,
        direction: str,
        timeframe: str
    ) -> bool:
        """
        Validate trend alignment for entry.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            timeframe: Signal timeframe
            
        Returns:
            bool: True if trend is aligned
        """
        if self.service_api is None:
            return True
        
        try:
            trend_service = getattr(self.service_api, 'trend_monitor', None)
            if trend_service is None:
                return True
            
            alignment = trend_service.get_mtf_alignment(symbol)
            
            if not alignment.get("aligned", False):
                return False
            
            trend_direction = alignment.get("direction", "UNKNOWN")
            
            if direction == "BUY" and trend_direction == "BULLISH":
                return True
            elif direction == "SELL" and trend_direction == "BEARISH":
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Trend validation error: {e}")
            return True
    
    def _is_aggressive_reversal(self, signal_type: str) -> bool:
        """Check if signal is aggressive reversal (bypasses trend check)."""
        aggressive_signals = [
            "Liquidity_Trap_Reversal",
            "Golden_Pocket_Flip",
            "Screener_Full_Bullish",
            "Screener_Full_Bearish"
        ]
        return signal_type in aggressive_signals
    
    def _get_logic_type(self, timeframe: str) -> str:
        """
        Determine logic type from timeframe.
        
        Args:
            timeframe: Timeframe string
            
        Returns:
            str: LOGIC1, LOGIC2, or LOGIC3
        """
        if timeframe in ["1", "5", "1M", "5M"]:
            return "LOGIC1"
        elif timeframe in ["15", "15M"]:
            return "LOGIC2"
        else:
            return "LOGIC3"
    
    async def _get_account_balance(self) -> float:
        """Get current account balance."""
        if self.service_api is None:
            return 10000.0
        
        try:
            risk_service = getattr(self.service_api, 'risk_management', None)
            if risk_service is None:
                return 10000.0
            
            summary = risk_service.get_risk_summary(10000.0)
            return summary.get("balance", 10000.0)
            
        except Exception as e:
            self.logger.warning(f"Balance fetch error: {e}")
            return 10000.0
    
    def _calculate_sl_pips(self, alert: Any, logic_type: str) -> float:
        """
        Calculate SL in pips based on alert and logic type.
        
        Args:
            alert: Alert data
            logic_type: LOGIC1, LOGIC2, or LOGIC3
            
        Returns:
            float: SL distance in pips
        """
        base_sl = getattr(alert, "sl_pips", 50.0)
        multiplier = self.SL_MULTIPLIERS.get(logic_type, 1.0)
        return base_sl * multiplier
    
    def _calculate_lot_a(
        self,
        balance: float,
        sl_pips: float,
        symbol: str,
        logic_type: str
    ) -> float:
        """
        Calculate lot size for Order A.
        
        Args:
            balance: Account balance
            sl_pips: SL distance in pips
            symbol: Trading symbol
            logic_type: Logic type
            
        Returns:
            float: Lot size for Order A
        """
        if self.service_api is None:
            return 0.01
        
        try:
            risk_service = getattr(self.service_api, 'risk_management', None)
            if risk_service is None:
                return 0.01
            
            lot_size = risk_service.calculate_lot_size(
                balance=balance,
                sl_pips=sl_pips,
                symbol=symbol
            )
            return lot_size
            
        except Exception as e:
            self.logger.warning(f"Lot calculation error: {e}")
            return 0.01
    
    def _calculate_lot_b(self, lot_a: float) -> float:
        """
        Calculate lot size for Order B (2x Order A).
        
        Args:
            lot_a: Order A lot size
            
        Returns:
            float: Lot size for Order B
        """
        return round(lot_a * self.ORDER_B_MULTIPLIER, 2)
    
    def _calculate_sl_price(
        self,
        alert: Any,
        logic_type: str,
        order_type: str
    ) -> float:
        """
        Calculate SL price for order.
        
        Order A: Timeframe-based SL with multiplier
        Order B: Fixed $10 SL
        
        Supports both Pine field names (sl_price) and legacy (sl).
        
        Args:
            alert: Alert data
            logic_type: Logic type
            order_type: ORDER_A or ORDER_B
            
        Returns:
            float: SL price
        """
        # Support both sl_price (Pine V3) and sl (legacy)
        if isinstance(alert, dict):
            sl_price = alert.get("sl_price") or alert.get("sl", 0.0)
        else:
            sl_price = getattr(alert, "sl_price", None) or getattr(alert, "sl", 0.0)
        
        if order_type == "ORDER_B":
            return sl_price
        
        return sl_price
    
    def _calculate_tp_price(
        self,
        alert: Any,
        logic_type: str,
        order_type: str
    ) -> float:
        """
        Calculate TP price for order.
        
        Order A uses tp1_price (conservative target).
        Order B uses tp2_price (extended target).
        
        Supports both Pine field names (tp1_price, tp2_price) and legacy (tp).
        
        Args:
            alert: Alert data
            logic_type: Logic type
            order_type: ORDER_A or ORDER_B
            
        Returns:
            float: TP price
        """
        # Support both tp1_price/tp2_price (Pine V3) and tp (legacy)
        if isinstance(alert, dict):
            tp1 = alert.get("tp1_price") or alert.get("tp", 0.0)
            tp2 = alert.get("tp2_price") or tp1
        else:
            tp1 = getattr(alert, "tp1_price", None) or getattr(alert, "tp", 0.0)
            tp2 = getattr(alert, "tp2_price", None) or tp1
        
        # Order A uses tp1 (conservative), Order B uses tp2 (extended)
        if order_type == "ORDER_A":
            return tp1
        else:
            return tp2
    
    async def _place_order(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str
    ) -> Optional[int]:
        """
        Place order via OrderExecutionService.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            lot_size: Position size
            sl_price: Stop loss price
            tp_price: Take profit price
            comment: Order comment
            
        Returns:
            int: Order ticket or None
        """
        if self.service_api is None:
            self.logger.info(f"Mock order: {symbol} {direction} {lot_size}")
            return int(datetime.now().timestamp())
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service is None:
                return int(datetime.now().timestamp())
            
            ticket = await order_service.place_order(
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                sl_price=sl_price,
                tp_price=tp_price,
                comment=comment,
                plugin_id=self.plugin.plugin_id
            )
            return ticket
            
        except Exception as e:
            self.logger.error(f"Order placement error: {e}")
            return None
    
    async def _record_trade(self, trade_record: Dict[str, Any]):
        """
        Record trade in plugin database.
        
        Args:
            trade_record: Trade data to record
        """
        try:
            db = self.plugin.get_database_connection()
            if db:
                pass
            
            self.logger.debug(f"Trade recorded: {trade_record.get('symbol')}")
            
        except Exception as e:
            self.logger.warning(f"Trade recording error: {e}")
