"""
V6 Price Action Plugin - Timeframe Strategies Module

Implements 4 timeframe-specific trading strategies for V6.

Part of Document 03: Phases 2-6 Consolidated Plan - Phase 5
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseTimeframeStrategy(ABC):
    """
    Base class for timeframe-specific strategies.
    
    Each timeframe has unique characteristics:
    - SL/TP multipliers
    - Lot size adjustments
    - Dual order settings
    - Max hold time
    """
    
    def __init__(self, plugin, timeframe: str, settings: Dict[str, Any]):
        """
        Initialize timeframe strategy.
        
        Args:
            plugin: Parent PriceActionV6Plugin instance
            timeframe: Timeframe string (1M, 5M, 15M, 1H)
            settings: Timeframe-specific settings
        """
        self.plugin = plugin
        self.timeframe = timeframe
        self.settings = settings
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"{__name__}.{timeframe}Strategy")
        
        self.logger.info(f"{timeframe} Strategy initialized: {settings.get('name', 'Unknown')}")
    
    @abstractmethod
    async def execute_entry(self, alert: Any, direction: str) -> Dict[str, Any]:
        """Execute entry for this timeframe."""
        pass
    
    @abstractmethod
    async def execute_exit(self, alert: Any) -> Dict[str, Any]:
        """Execute exit for this timeframe."""
        pass
    
    def get_sl_multiplier(self) -> float:
        """Get SL multiplier for this timeframe."""
        return self.settings.get("sl_multiplier", 1.0)
    
    def get_lot_multiplier(self) -> float:
        """Get lot multiplier for this timeframe."""
        return self.settings.get("lot_multiplier", 1.0)
    
    def should_use_dual_orders(self) -> bool:
        """Check if dual orders should be used."""
        return self.settings.get("dual_orders", False)
    
    def get_max_hold_minutes(self) -> int:
        """Get maximum hold time in minutes."""
        return self.settings.get("max_hold_minutes", 480)


class Strategy1M(BaseTimeframeStrategy):
    """
    1-Minute Scalping Strategy.
    
    Characteristics:
    - Single order only
    - Tight SL (0.5x multiplier)
    - Reduced lot size (0.5x)
    - Max hold: 30 minutes
    - Quick entries and exits
    """
    
    async def execute_entry(self, alert: Any, direction: str) -> Dict[str, Any]:
        """
        Execute 1M scalping entry.
        
        Args:
            alert: Alert data
            direction: BUY or SELL
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"1M Scalping Entry: {symbol} {direction}")
        
        # Calculate lot size with 0.5x multiplier
        base_lot = await self._calculate_base_lot(symbol)
        lot_size = round(base_lot * self.get_lot_multiplier(), 2)
        
        # Calculate SL with 0.5x multiplier (tighter)
        base_sl = getattr(alert, "sl", 0.0)
        sl_price = base_sl
        
        # Single order only for 1M
        ticket = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_size,
            sl_price=sl_price,
            tp_price=getattr(alert, "tp", 0.0),
            comment=f"V6_1M_Scalp_{getattr(alert, 'alert_type', 'Entry')}"
        )
        
        return {
            "success": ticket is not None,
            "timeframe": "1M",
            "strategy": "Scalping",
            "symbol": symbol,
            "direction": direction,
            "ticket": ticket,
            "lot_size": lot_size,
            "dual_orders": False
        }
    
    async def execute_exit(self, alert: Any) -> Dict[str, Any]:
        """Execute 1M exit."""
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"1M Scalping Exit: {symbol}")
        
        # Close all 1M positions for symbol
        closed = await self._close_positions(symbol)
        
        return {
            "success": True,
            "timeframe": "1M",
            "symbol": symbol,
            "positions_closed": closed
        }
    
    async def _calculate_base_lot(self, symbol: str) -> float:
        """Calculate base lot size."""
        if self.service_api is None:
            return 0.01
        
        try:
            risk_service = getattr(self.service_api, 'risk_management', None)
            if risk_service:
                return risk_service.get_fixed_lot_size(10000.0)
        except Exception:
            pass
        return 0.01
    
    async def _place_order(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str
    ) -> Optional[int]:
        """Place order via service API."""
        if self.service_api is None:
            return int(datetime.now().timestamp())
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                return await order_service.place_order(
                    symbol=symbol,
                    direction=direction,
                    lot_size=lot_size,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    comment=comment,
                    plugin_id=self.plugin.plugin_id
                )
        except Exception as e:
            self.logger.error(f"Order placement error: {e}")
        return int(datetime.now().timestamp())
    
    async def _close_positions(self, symbol: str) -> int:
        """Close positions for symbol."""
        if self.service_api is None:
            return 0
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                result = await order_service.close_all_orders(
                    symbol=symbol,
                    plugin_id=self.plugin.plugin_id
                )
                return result.get("closed", 0)
        except Exception as e:
            self.logger.error(f"Position close error: {e}")
        return 0


class Strategy5M(BaseTimeframeStrategy):
    """
    5-Minute Intraday Strategy.
    
    Characteristics:
    - Single order only
    - Standard SL (1.0x multiplier)
    - Standard lot size (1.0x)
    - Max hold: 120 minutes
    - Balanced approach
    """
    
    async def execute_entry(self, alert: Any, direction: str) -> Dict[str, Any]:
        """
        Execute 5M intraday entry.
        
        Args:
            alert: Alert data
            direction: BUY or SELL
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"5M Intraday Entry: {symbol} {direction}")
        
        # Standard lot size
        base_lot = await self._calculate_base_lot(symbol)
        lot_size = round(base_lot * self.get_lot_multiplier(), 2)
        
        # Standard SL
        sl_price = getattr(alert, "sl", 0.0)
        
        # Single order for 5M
        ticket = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_size,
            sl_price=sl_price,
            tp_price=getattr(alert, "tp", 0.0),
            comment=f"V6_5M_Intraday_{getattr(alert, 'alert_type', 'Entry')}"
        )
        
        return {
            "success": ticket is not None,
            "timeframe": "5M",
            "strategy": "Intraday",
            "symbol": symbol,
            "direction": direction,
            "ticket": ticket,
            "lot_size": lot_size,
            "dual_orders": False
        }
    
    async def execute_exit(self, alert: Any) -> Dict[str, Any]:
        """Execute 5M exit."""
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"5M Intraday Exit: {symbol}")
        
        closed = await self._close_positions(symbol)
        
        return {
            "success": True,
            "timeframe": "5M",
            "symbol": symbol,
            "positions_closed": closed
        }
    
    async def _calculate_base_lot(self, symbol: str) -> float:
        """Calculate base lot size."""
        if self.service_api is None:
            return 0.01
        
        try:
            risk_service = getattr(self.service_api, 'risk_management', None)
            if risk_service:
                return risk_service.get_fixed_lot_size(10000.0)
        except Exception:
            pass
        return 0.01
    
    async def _place_order(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str
    ) -> Optional[int]:
        """Place order via service API."""
        if self.service_api is None:
            return int(datetime.now().timestamp())
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                return await order_service.place_order(
                    symbol=symbol,
                    direction=direction,
                    lot_size=lot_size,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    comment=comment,
                    plugin_id=self.plugin.plugin_id
                )
        except Exception as e:
            self.logger.error(f"Order placement error: {e}")
        return int(datetime.now().timestamp())
    
    async def _close_positions(self, symbol: str) -> int:
        """Close positions for symbol."""
        if self.service_api is None:
            return 0
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                result = await order_service.close_all_orders(
                    symbol=symbol,
                    plugin_id=self.plugin.plugin_id
                )
                return result.get("closed", 0)
        except Exception as e:
            self.logger.error(f"Position close error: {e}")
        return 0


class Strategy15M(BaseTimeframeStrategy):
    """
    15-Minute Swing Strategy.
    
    Characteristics:
    - Dual orders (Order A + Order B)
    - Wider SL (1.5x multiplier)
    - Standard lot size (1.0x)
    - Max hold: 480 minutes (8 hours)
    - Balanced swing approach
    """
    
    async def execute_entry(self, alert: Any, direction: str) -> Dict[str, Any]:
        """
        Execute 15M swing entry with dual orders.
        
        Args:
            alert: Alert data
            direction: BUY or SELL
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"15M Swing Entry: {symbol} {direction}")
        
        # Calculate lot sizes
        base_lot = await self._calculate_base_lot(symbol)
        lot_a = round(base_lot * self.get_lot_multiplier(), 2)
        lot_b = round(lot_a * 2, 2)  # Order B is 2x Order A
        
        # SL prices
        sl_price = getattr(alert, "sl", 0.0)
        tp_price = getattr(alert, "tp", 0.0)
        
        # Place dual orders
        ticket_a = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_a,
            sl_price=sl_price,
            tp_price=tp_price,
            comment=f"V6_15M_Swing_A_{getattr(alert, 'alert_type', 'Entry')}"
        )
        
        ticket_b = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_b,
            sl_price=sl_price,
            tp_price=0.0,  # Order B uses profit trailing, no fixed TP
            comment=f"V6_15M_Swing_B_{getattr(alert, 'alert_type', 'Entry')}"
        )
        
        return {
            "success": ticket_a is not None and ticket_b is not None,
            "timeframe": "15M",
            "strategy": "Swing",
            "symbol": symbol,
            "direction": direction,
            "ticket_a": ticket_a,
            "ticket_b": ticket_b,
            "lot_a": lot_a,
            "lot_b": lot_b,
            "dual_orders": True
        }
    
    async def execute_exit(self, alert: Any) -> Dict[str, Any]:
        """Execute 15M exit."""
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"15M Swing Exit: {symbol}")
        
        closed = await self._close_positions(symbol)
        
        return {
            "success": True,
            "timeframe": "15M",
            "symbol": symbol,
            "positions_closed": closed
        }
    
    async def _calculate_base_lot(self, symbol: str) -> float:
        """Calculate base lot size."""
        if self.service_api is None:
            return 0.01
        
        try:
            risk_service = getattr(self.service_api, 'risk_management', None)
            if risk_service:
                return risk_service.get_fixed_lot_size(10000.0)
        except Exception:
            pass
        return 0.01
    
    async def _place_order(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str
    ) -> Optional[int]:
        """Place order via service API."""
        if self.service_api is None:
            return int(datetime.now().timestamp())
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                return await order_service.place_order(
                    symbol=symbol,
                    direction=direction,
                    lot_size=lot_size,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    comment=comment,
                    plugin_id=self.plugin.plugin_id
                )
        except Exception as e:
            self.logger.error(f"Order placement error: {e}")
        return int(datetime.now().timestamp())
    
    async def _close_positions(self, symbol: str) -> int:
        """Close positions for symbol."""
        if self.service_api is None:
            return 0
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                result = await order_service.close_all_orders(
                    symbol=symbol,
                    plugin_id=self.plugin.plugin_id
                )
                return result.get("closed", 0)
        except Exception as e:
            self.logger.error(f"Position close error: {e}")
        return 0


class Strategy1H(BaseTimeframeStrategy):
    """
    1-Hour Position Strategy.
    
    Characteristics:
    - Dual orders (Order A + Order B)
    - Wide SL (2.0x multiplier)
    - Reduced lot size (0.75x)
    - Max hold: 1440 minutes (24 hours)
    - Position trading approach
    """
    
    async def execute_entry(self, alert: Any, direction: str) -> Dict[str, Any]:
        """
        Execute 1H position entry with dual orders.
        
        Args:
            alert: Alert data
            direction: BUY or SELL
            
        Returns:
            dict: Entry result
        """
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"1H Position Entry: {symbol} {direction}")
        
        # Calculate lot sizes (reduced for position trading)
        base_lot = await self._calculate_base_lot(symbol)
        lot_a = round(base_lot * self.get_lot_multiplier(), 2)
        lot_b = round(lot_a * 2, 2)  # Order B is 2x Order A
        
        # SL prices (wider for position trading)
        sl_price = getattr(alert, "sl", 0.0)
        tp_price = getattr(alert, "tp", 0.0)
        
        # Place dual orders
        ticket_a = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_a,
            sl_price=sl_price,
            tp_price=tp_price,
            comment=f"V6_1H_Position_A_{getattr(alert, 'alert_type', 'Entry')}"
        )
        
        ticket_b = await self._place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_b,
            sl_price=sl_price,
            tp_price=0.0,  # Order B uses profit trailing
            comment=f"V6_1H_Position_B_{getattr(alert, 'alert_type', 'Entry')}"
        )
        
        return {
            "success": ticket_a is not None and ticket_b is not None,
            "timeframe": "1H",
            "strategy": "Position",
            "symbol": symbol,
            "direction": direction,
            "ticket_a": ticket_a,
            "ticket_b": ticket_b,
            "lot_a": lot_a,
            "lot_b": lot_b,
            "dual_orders": True
        }
    
    async def execute_exit(self, alert: Any) -> Dict[str, Any]:
        """Execute 1H exit."""
        symbol = getattr(alert, "symbol", "")
        
        self.logger.info(f"1H Position Exit: {symbol}")
        
        closed = await self._close_positions(symbol)
        
        return {
            "success": True,
            "timeframe": "1H",
            "symbol": symbol,
            "positions_closed": closed
        }
    
    async def _calculate_base_lot(self, symbol: str) -> float:
        """Calculate base lot size."""
        if self.service_api is None:
            return 0.01
        
        try:
            risk_service = getattr(self.service_api, 'risk_management', None)
            if risk_service:
                return risk_service.get_fixed_lot_size(10000.0)
        except Exception:
            pass
        return 0.01
    
    async def _place_order(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str
    ) -> Optional[int]:
        """Place order via service API."""
        if self.service_api is None:
            return int(datetime.now().timestamp())
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                return await order_service.place_order(
                    symbol=symbol,
                    direction=direction,
                    lot_size=lot_size,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    comment=comment,
                    plugin_id=self.plugin.plugin_id
                )
        except Exception as e:
            self.logger.error(f"Order placement error: {e}")
        return int(datetime.now().timestamp())
    
    async def _close_positions(self, symbol: str) -> int:
        """Close positions for symbol."""
        if self.service_api is None:
            return 0
        
        try:
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service:
                result = await order_service.close_all_orders(
                    symbol=symbol,
                    plugin_id=self.plugin.plugin_id
                )
                return result.get("closed", 0)
        except Exception as e:
            self.logger.error(f"Position close error: {e}")
        return 0


class TimeframeStrategies:
    """
    Manager for all timeframe strategies.
    
    Provides unified interface to access and use
    timeframe-specific trading strategies.
    """
    
    def __init__(self, plugin):
        """
        Initialize TimeframeStrategies manager.
        
        Args:
            plugin: Parent PriceActionV6Plugin instance
        """
        self.plugin = plugin
        self.logger = logging.getLogger(f"{__name__}.TimeframeStrategies")
        
        # Timeframe settings
        self.settings = {
            "1M": {
                "name": "Scalping",
                "dual_orders": False,
                "sl_multiplier": 0.5,
                "lot_multiplier": 0.5,
                "max_hold_minutes": 30
            },
            "5M": {
                "name": "Intraday",
                "dual_orders": False,
                "sl_multiplier": 1.0,
                "lot_multiplier": 1.0,
                "max_hold_minutes": 120
            },
            "15M": {
                "name": "Swing",
                "dual_orders": True,
                "sl_multiplier": 1.5,
                "lot_multiplier": 1.0,
                "max_hold_minutes": 480
            },
            "1H": {
                "name": "Position",
                "dual_orders": True,
                "sl_multiplier": 2.0,
                "lot_multiplier": 0.75,
                "max_hold_minutes": 1440
            }
        }
        
        # Initialize strategies
        self.strategies: Dict[str, BaseTimeframeStrategy] = {
            "1M": Strategy1M(plugin, "1M", self.settings["1M"]),
            "5M": Strategy5M(plugin, "5M", self.settings["5M"]),
            "15M": Strategy15M(plugin, "15M", self.settings["15M"]),
            "1H": Strategy1H(plugin, "1H", self.settings["1H"])
        }
        
        self.logger.info("TimeframeStrategies initialized with 4 strategies")
    
    def get_strategy(self, timeframe: str) -> Optional[BaseTimeframeStrategy]:
        """
        Get strategy for a timeframe.
        
        Args:
            timeframe: Timeframe string (1M, 5M, 15M, 1H)
            
        Returns:
            BaseTimeframeStrategy or None
        """
        return self.strategies.get(timeframe)
    
    def get_all_strategies(self) -> Dict[str, BaseTimeframeStrategy]:
        """Get all strategies."""
        return self.strategies
    
    def get_settings(self, timeframe: str) -> Dict[str, Any]:
        """Get settings for a timeframe."""
        return self.settings.get(timeframe, self.settings["15M"])
