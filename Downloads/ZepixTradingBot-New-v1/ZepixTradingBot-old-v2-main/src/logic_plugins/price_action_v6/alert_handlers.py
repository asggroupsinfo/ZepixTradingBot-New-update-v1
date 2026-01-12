"""
V6 Price Action Plugin - Alert Handlers Module

Handles all 14 V6 alert types with appropriate routing and processing.

Part of Document 03: Phases 2-6 Consolidated Plan - Phase 5
"""

from typing import Dict, Any, Optional, Callable
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class V6AlertHandlers:
    """
    V6 Alert Handlers.
    
    Routes and processes all 14 V6 alert types:
    
    Entry Alerts (7):
    - PA_Breakout_Entry
    - PA_Pullback_Entry
    - PA_Reversal_Entry
    - PA_Momentum_Entry
    - PA_Support_Bounce
    - PA_Resistance_Rejection
    - PA_Trend_Continuation
    
    Exit Alerts (3):
    - PA_Exit_Signal
    - PA_Reversal_Exit
    - PA_Target_Hit
    
    Info Alerts (4):
    - PA_Trend_Pulse
    - PA_Volatility_Alert
    - PA_Session_Open
    - PA_Session_Close
    """
    
    def __init__(self, plugin):
        """
        Initialize V6 Alert Handlers.
        
        Args:
            plugin: Parent PriceActionV6Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"{__name__}.V6AlertHandlers")
        
        # Alert routing map
        self.handlers: Dict[str, Callable] = {
            # Entry alerts
            "PA_Breakout_Entry": self.handle_breakout_entry,
            "PA_Pullback_Entry": self.handle_pullback_entry,
            "PA_Reversal_Entry": self.handle_reversal_entry,
            "PA_Momentum_Entry": self.handle_momentum_entry,
            "PA_Support_Bounce": self.handle_support_bounce,
            "PA_Resistance_Rejection": self.handle_resistance_rejection,
            "PA_Trend_Continuation": self.handle_trend_continuation,
            # Exit alerts
            "PA_Exit_Signal": self.handle_exit_signal,
            "PA_Reversal_Exit": self.handle_reversal_exit,
            "PA_Target_Hit": self.handle_target_hit,
            # Info alerts
            "PA_Trend_Pulse": self.handle_trend_pulse,
            "PA_Volatility_Alert": self.handle_volatility_alert,
            "PA_Session_Open": self.handle_session_open,
            "PA_Session_Close": self.handle_session_close,
        }
        
        self.logger.info("V6AlertHandlers initialized with 14 handlers")
    
    async def route_alert(self, alert: Any) -> Dict[str, Any]:
        """
        Route alert to appropriate handler.
        
        Args:
            alert: V6 alert data
            
        Returns:
            dict: Handler result
        """
        alert_type = getattr(alert, "alert_type", "")
        
        handler = self.handlers.get(alert_type)
        
        if handler:
            self.logger.debug(f"Routing alert to handler: {alert_type}")
            return await handler(alert)
        else:
            self.logger.warning(f"Unknown alert type: {alert_type}")
            return {
                "success": False,
                "error": f"unknown_alert_type: {alert_type}"
            }
    
    # Entry Alert Handlers
    
    async def handle_breakout_entry(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Breakout_Entry alert.
        
        Breakout entries occur when price breaks through key levels.
        Uses ADX and momentum confirmation.
        
        Args:
            alert: Breakout entry alert
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Breakout Entry: {symbol} {direction} TF={timeframe}")
        
        # Check ADX for trend strength
        if not await self._check_adx_filter(symbol):
            return {
                "success": False,
                "reason": "adx_filter_failed",
                "symbol": symbol
            }
        
        # Check momentum
        if not await self._check_momentum_filter(symbol, direction):
            return {
                "success": False,
                "reason": "momentum_filter_failed",
                "symbol": symbol
            }
        
        # Execute entry via timeframe strategy
        return await self._execute_entry(alert, "breakout")
    
    async def handle_pullback_entry(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Pullback_Entry alert.
        
        Pullback entries occur during trend retracements.
        
        Args:
            alert: Pullback entry alert
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Pullback Entry: {symbol} {direction} TF={timeframe}")
        
        # Pullbacks require trend confirmation
        if not await self._check_trend_alignment(symbol, direction):
            return {
                "success": False,
                "reason": "trend_not_aligned",
                "symbol": symbol
            }
        
        return await self._execute_entry(alert, "pullback")
    
    async def handle_reversal_entry(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Reversal_Entry alert.
        
        Reversal entries occur at trend exhaustion points.
        
        Args:
            alert: Reversal entry alert
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Reversal Entry: {symbol} {direction} TF={timeframe}")
        
        # Reversals bypass trend check but need momentum confirmation
        if not await self._check_momentum_filter(symbol, direction):
            return {
                "success": False,
                "reason": "momentum_filter_failed",
                "symbol": symbol
            }
        
        return await self._execute_entry(alert, "reversal")
    
    async def handle_momentum_entry(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Momentum_Entry alert.
        
        Momentum entries occur during strong directional moves.
        
        Args:
            alert: Momentum entry alert
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Momentum Entry: {symbol} {direction} TF={timeframe}")
        
        # Strong ADX required for momentum entries
        if not await self._check_adx_filter(symbol, threshold=30):
            return {
                "success": False,
                "reason": "adx_too_weak",
                "symbol": symbol
            }
        
        return await self._execute_entry(alert, "momentum")
    
    async def handle_support_bounce(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Support_Bounce alert.
        
        Support bounce entries occur at key support levels.
        
        Args:
            alert: Support bounce alert
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Support Bounce: {symbol} TF={timeframe}")
        
        # Support bounces are always BUY
        alert.direction = "BUY"
        
        return await self._execute_entry(alert, "support_bounce")
    
    async def handle_resistance_rejection(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Resistance_Rejection alert.
        
        Resistance rejection entries occur at key resistance levels.
        
        Args:
            alert: Resistance rejection alert
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Resistance Rejection: {symbol} TF={timeframe}")
        
        # Resistance rejections are always SELL
        alert.direction = "SELL"
        
        return await self._execute_entry(alert, "resistance_rejection")
    
    async def handle_trend_continuation(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Trend_Continuation alert.
        
        Trend continuation entries occur during established trends.
        
        Args:
            alert: Trend continuation alert
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Trend Continuation: {symbol} {direction} TF={timeframe}")
        
        # Must have trend alignment
        if not await self._check_trend_alignment(symbol, direction):
            return {
                "success": False,
                "reason": "trend_not_aligned",
                "symbol": symbol
            }
        
        return await self._execute_entry(alert, "trend_continuation")
    
    # Exit Alert Handlers
    
    async def handle_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Exit_Signal alert.
        
        Standard exit signal for closing positions.
        
        Args:
            alert: Exit signal alert
            
        Returns:
            dict: Exit result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Exit Signal: {symbol} TF={timeframe}")
        
        return await self._execute_exit(alert, "signal")
    
    async def handle_reversal_exit(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Reversal_Exit alert.
        
        Exit due to trend reversal detection.
        
        Args:
            alert: Reversal exit alert
            
        Returns:
            dict: Exit result
        """
        symbol = getattr(alert, "symbol", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Reversal Exit: {symbol} TF={timeframe}")
        
        return await self._execute_exit(alert, "reversal")
    
    async def handle_target_hit(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Target_Hit alert.
        
        Exit due to take profit target being hit.
        
        Args:
            alert: Target hit alert
            
        Returns:
            dict: Exit result
        """
        symbol = getattr(alert, "symbol", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Target Hit: {symbol} TF={timeframe}")
        
        return await self._execute_exit(alert, "target_hit")
    
    # Info Alert Handlers
    
    async def handle_trend_pulse(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Trend_Pulse alert.
        
        Updates trend tracking for the symbol/timeframe.
        
        Args:
            alert: Trend pulse alert
            
        Returns:
            dict: Processing result
        """
        symbol = getattr(alert, "symbol", "")
        direction = getattr(alert, "direction", "")
        timeframe = getattr(alert, "timeframe", "15M")
        
        self.logger.info(f"Processing Trend Pulse: {symbol} {direction} TF={timeframe}")
        
        # Update trend service
        if self.service_api:
            trend_service = getattr(self.service_api, 'trend_monitor', None)
            if trend_service:
                from src.services.trend_monitor import TrendDirection
                trend_dir = TrendDirection.BULLISH if direction == "BUY" else TrendDirection.BEARISH
                trend_service.update_trend(symbol, timeframe, trend_dir, "V6_TrendPulse")
        
        return {
            "success": True,
            "alert_type": "PA_Trend_Pulse",
            "symbol": symbol,
            "direction": direction,
            "timeframe": timeframe
        }
    
    async def handle_volatility_alert(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Volatility_Alert alert.
        
        Notifies of increased volatility conditions.
        
        Args:
            alert: Volatility alert
            
        Returns:
            dict: Processing result
        """
        symbol = getattr(alert, "symbol", "")
        volatility_level = getattr(alert, "volatility", "HIGH")
        
        self.logger.info(f"Processing Volatility Alert: {symbol} level={volatility_level}")
        
        return {
            "success": True,
            "alert_type": "PA_Volatility_Alert",
            "symbol": symbol,
            "volatility_level": volatility_level
        }
    
    async def handle_session_open(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Session_Open alert.
        
        Notifies of trading session opening.
        
        Args:
            alert: Session open alert
            
        Returns:
            dict: Processing result
        """
        session = getattr(alert, "session", "UNKNOWN")
        
        self.logger.info(f"Processing Session Open: {session}")
        
        return {
            "success": True,
            "alert_type": "PA_Session_Open",
            "session": session
        }
    
    async def handle_session_close(self, alert: Any) -> Dict[str, Any]:
        """
        Handle PA_Session_Close alert.
        
        Notifies of trading session closing.
        
        Args:
            alert: Session close alert
            
        Returns:
            dict: Processing result
        """
        session = getattr(alert, "session", "UNKNOWN")
        
        self.logger.info(f"Processing Session Close: {session}")
        
        return {
            "success": True,
            "alert_type": "PA_Session_Close",
            "session": session
        }
    
    # Helper Methods
    
    async def _check_adx_filter(self, symbol: str, threshold: int = 25) -> bool:
        """
        Check ADX filter for trend strength.
        
        Args:
            symbol: Trading symbol
            threshold: ADX threshold (default 25)
            
        Returns:
            bool: True if ADX is above threshold
        """
        if not hasattr(self.plugin, 'adx_integration') or self.plugin.adx_integration is None:
            return True
        
        try:
            adx_value = self.plugin.adx_integration.get_current_adx(symbol)
            return adx_value >= threshold
        except Exception as e:
            self.logger.warning(f"ADX check error: {e}")
            return True
    
    async def _check_momentum_filter(self, symbol: str, direction: str) -> bool:
        """
        Check momentum filter for directional strength.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            
        Returns:
            bool: True if momentum confirms direction
        """
        if not hasattr(self.plugin, 'momentum_integration') or self.plugin.momentum_integration is None:
            return True
        
        try:
            momentum = self.plugin.momentum_integration.get_momentum(symbol)
            
            if direction == "BUY":
                return momentum > 0
            else:
                return momentum < 0
        except Exception as e:
            self.logger.warning(f"Momentum check error: {e}")
            return True
    
    async def _check_trend_alignment(self, symbol: str, direction: str) -> bool:
        """
        Check if trend is aligned with direction.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            
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
            self.logger.warning(f"Trend alignment check error: {e}")
            return True
    
    async def _execute_entry(self, alert: Any, entry_type: str) -> Dict[str, Any]:
        """
        Execute entry via timeframe strategy.
        
        Args:
            alert: Alert data
            entry_type: Type of entry
            
        Returns:
            dict: Entry result
        """
        timeframe = getattr(alert, "timeframe", "15M")
        
        if hasattr(self.plugin, 'timeframe_strategies') and self.plugin.timeframe_strategies:
            strategy = self.plugin.timeframe_strategies.get_strategy(timeframe)
            if strategy:
                return await strategy.execute_entry(alert, getattr(alert, "direction", "BUY"))
        
        # Fallback to plugin's process_entry_signal
        return await self.plugin.process_entry_signal(alert)
    
    async def _execute_exit(self, alert: Any, exit_type: str) -> Dict[str, Any]:
        """
        Execute exit.
        
        Args:
            alert: Alert data
            exit_type: Type of exit
            
        Returns:
            dict: Exit result
        """
        return await self.plugin.process_exit_signal(alert)
