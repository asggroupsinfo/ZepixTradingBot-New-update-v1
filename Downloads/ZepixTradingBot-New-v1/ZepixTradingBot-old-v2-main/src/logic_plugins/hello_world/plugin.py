"""
Hello World Example Plugin.

This is a minimal example plugin demonstrating the V5 Hybrid Plugin Architecture.
Use this as a template for creating your own trading strategies.

Features demonstrated:
- Plugin initialization
- Signal processing
- ServiceAPI usage
- Database operations
- Logging

Based on Document 15: DEVELOPER_ONBOARDING.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Signal types for Hello World plugin."""
    ENTRY = "entry"
    EXIT = "exit"
    INFO = "info"


class Direction(Enum):
    """Trade direction."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class HelloWorldConfig:
    """Configuration for Hello World plugin."""
    plugin_id: str = "hello_world"
    version: str = "1.0.0"
    enabled: bool = True
    max_lot_size: float = 0.1
    risk_percentage: float = 1.0
    daily_loss_limit: float = 100.0
    supported_symbols: List[str] = field(default_factory=lambda: ["XAUUSD", "EURUSD"])
    entry_threshold: int = 7
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HelloWorldConfig':
        """Create config from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", "hello_world"),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            max_lot_size=data.get("max_lot_size", 0.1),
            risk_percentage=data.get("risk_percentage", 1.0),
            daily_loss_limit=data.get("daily_loss_limit", 100.0),
            supported_symbols=data.get("supported_symbols", ["XAUUSD", "EURUSD"]),
            entry_threshold=data.get("entry_threshold", 7)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "version": self.version,
            "enabled": self.enabled,
            "max_lot_size": self.max_lot_size,
            "risk_percentage": self.risk_percentage,
            "daily_loss_limit": self.daily_loss_limit,
            "supported_symbols": self.supported_symbols,
            "entry_threshold": self.entry_threshold
        }


@dataclass
class Signal:
    """Trading signal."""
    symbol: str
    signal_type: SignalType
    direction: Optional[Direction] = None
    consensus_score: int = 0
    entry_price: float = 0.0
    sl_price: float = 0.0
    tp_price: float = 0.0
    timeframe: str = "15m"
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Signal':
        """Create signal from dictionary."""
        signal_type = SignalType(data.get("signal_type", "entry"))
        direction = None
        if data.get("direction"):
            direction = Direction(data["direction"])
        
        return cls(
            symbol=data.get("symbol", ""),
            signal_type=signal_type,
            direction=direction,
            consensus_score=data.get("consensus_score", 0),
            entry_price=data.get("entry_price", 0.0),
            sl_price=data.get("sl_price", 0.0),
            tp_price=data.get("tp_price", 0.0),
            timeframe=data.get("timeframe", "15m")
        )


class MockServiceAPI:
    """Mock ServiceAPI for demonstration purposes."""
    
    def __init__(self):
        """Initialize mock service API."""
        self.orders = MockOrderService()
        self.risk = MockRiskService()
        self.trend = MockTrendService()
        self.notifications = MockNotificationService()
    
    
class MockOrderService:
    """Mock order service."""
    
    async def place_order(self, symbol: str, direction: str, lot_size: float,
                         sl_price: float = 0.0, tp_price: float = 0.0,
                         comment: str = "") -> int:
        """Place a mock order."""
        logger.info(f"[MOCK] Placing order: {symbol} {direction} {lot_size} lots")
        return 12345
    
    async def close_position(self, ticket: int) -> bool:
        """Close a mock position."""
        logger.info(f"[MOCK] Closing position: {ticket}")
        return True
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get mock open orders."""
        return []


class MockRiskService:
    """Mock risk service."""
    
    async def calculate_lot_size(self, symbol: str, risk_percentage: float,
                                stop_loss_pips: float) -> float:
        """Calculate mock lot size."""
        return min(0.1, risk_percentage * 0.1)
    
    async def check_daily_limit(self, plugin_id: str = "") -> Dict[str, Any]:
        """Check mock daily limit."""
        return {"can_trade": True, "remaining": 100.0}


class MockTrendService:
    """Mock trend service."""
    
    async def get_current_trend(self, symbol: str, timeframe: str = "15m") -> Dict[str, Any]:
        """Get mock current trend."""
        return {"direction": "BULLISH", "strength": 0.75}


class MockNotificationService:
    """Mock notification service."""
    
    async def send(self, message: str, priority: str = "normal") -> bool:
        """Send mock notification."""
        logger.info(f"[MOCK] Notification: {message}")
        return True


class HelloWorldPlugin:
    """
    Hello World Example Plugin.
    
    This is a minimal example plugin demonstrating the V5 Hybrid Plugin Architecture.
    It shows how to:
    - Initialize a plugin with configuration
    - Process incoming signals
    - Use the ServiceAPI for trading operations
    - Log meaningful messages
    - Handle errors gracefully
    
    Usage:
        config = HelloWorldConfig()
        service_api = MockServiceAPI()
        plugin = HelloWorldPlugin("hello_world", config, service_api)
        
        signal = {"symbol": "XAUUSD", "direction": "BUY", "consensus_score": 8}
        result = await plugin.on_signal_received(signal)
    """
    
    PLUGIN_ID = "hello_world"
    PLUGIN_NAME = "Hello World Example"
    VERSION = "1.0.0"
    DESCRIPTION = "A minimal example plugin for learning the V5 architecture"
    AUTHOR = "Zepix Team"
    
    def __init__(self, plugin_id: str, config: Any, service_api: Any):
        """
        Initialize the Hello World plugin.
        
        Args:
            plugin_id: Unique identifier for this plugin instance
            config: Plugin configuration (dict or HelloWorldConfig)
            service_api: ServiceAPI instance for accessing core services
        """
        self.plugin_id = plugin_id
        
        if isinstance(config, dict):
            self.config = HelloWorldConfig.from_dict(config)
        elif isinstance(config, HelloWorldConfig):
            self.config = config
        else:
            self.config = HelloWorldConfig()
        
        self.service_api = service_api
        self.enabled = self.config.enabled
        self.trades_today = 0
        self.daily_pnl = 0.0
        
        logger.info(f"[{self.plugin_id}] Plugin initialized - v{self.VERSION}")
    
    @property
    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True
        logger.info(f"[{self.plugin_id}] Plugin enabled")
    
    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False
        logger.info(f"[{self.plugin_id}] Plugin disabled")
    
    async def on_signal_received(self, signal_data: Dict[str, Any]) -> bool:
        """
        Main entry point for processing TradingView alerts.
        
        This method is called whenever a new signal is received from TradingView.
        It validates the signal, checks trend alignment, calculates lot size,
        and places the order if all conditions are met.
        
        Args:
            signal_data: Dictionary containing signal information:
                - symbol: Trading symbol (e.g., "XAUUSD")
                - signal_type: Type of signal ("entry", "exit", "info")
                - direction: Trade direction ("BUY" or "SELL")
                - consensus_score: Signal strength (0-10)
                - sl_price: Stop loss price
                - tp_price: Take profit price
                - timeframe: Signal timeframe (e.g., "15m")
        
        Returns:
            bool: True if trade was placed, False if skipped
        """
        try:
            signal = Signal.from_dict(signal_data)
            
            logger.info(f"[{self.plugin_id}] Processing signal: {signal.symbol} {signal.signal_type.value}")
            
            if not self._should_process(signal):
                logger.info(f"[{self.plugin_id}] Signal skipped (validation failed)")
                return False
            
            if signal.signal_type == SignalType.EXIT:
                return await self._handle_exit_signal(signal)
            
            if signal.signal_type == SignalType.INFO:
                logger.info(f"[{self.plugin_id}] Info signal received: {signal_data}")
                return False
            
            trend = await self.service_api.trend.get_current_trend(
                symbol=signal.symbol,
                timeframe=signal.timeframe
            )
            
            if not self._is_aligned(signal.direction, trend):
                logger.info(f"[{self.plugin_id}] Signal skipped (against trend)")
                return False
            
            risk_status = await self.service_api.risk.check_daily_limit(self.plugin_id)
            if not risk_status.get("can_trade", True):
                logger.warning(f"[{self.plugin_id}] Daily limit reached, skipping trade")
                return False
            
            sl_pips = self._calculate_sl_pips(signal)
            lot_size = await self.service_api.risk.calculate_lot_size(
                symbol=signal.symbol,
                risk_percentage=self.config.risk_percentage,
                stop_loss_pips=sl_pips
            )
            
            lot_size = min(lot_size, self.config.max_lot_size)
            
            ticket = await self.service_api.orders.place_order(
                symbol=signal.symbol,
                direction=signal.direction.value if signal.direction else "BUY",
                lot_size=lot_size,
                sl_price=signal.sl_price,
                tp_price=signal.tp_price,
                comment=f"{self.plugin_id}_entry"
            )
            
            self.trades_today += 1
            
            logger.info(f"[{self.plugin_id}] Trade placed: ticket={ticket}, lot={lot_size}")
            
            await self.service_api.notifications.send(
                f"[{self.plugin_id}] Trade opened: {signal.symbol} {signal.direction.value if signal.direction else 'BUY'} {lot_size} lots",
                priority="high"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[{self.plugin_id}] Error processing signal: {e}")
            return False
    
    async def _handle_exit_signal(self, signal: Signal) -> bool:
        """Handle exit signal."""
        logger.info(f"[{self.plugin_id}] Processing exit signal for {signal.symbol}")
        return True
    
    def _should_process(self, signal: Signal) -> bool:
        """
        Validate if signal should be processed.
        
        Args:
            signal: Signal to validate
        
        Returns:
            bool: True if signal should be processed
        """
        if not self.enabled:
            return False
        
        if signal.symbol not in self.config.supported_symbols:
            return False
        
        if signal.signal_type == SignalType.ENTRY:
            if signal.consensus_score < self.config.entry_threshold:
                return False
        
        return True
    
    def _is_aligned(self, direction: Optional[Direction], trend: Dict[str, Any]) -> bool:
        """
        Check if signal direction aligns with current trend.
        
        Args:
            direction: Signal direction
            trend: Current trend data
        
        Returns:
            bool: True if aligned with trend
        """
        if direction is None:
            return True
        
        trend_direction = trend.get("direction", "NEUTRAL")
        
        if direction == Direction.BUY and trend_direction == "BEARISH":
            return False
        if direction == Direction.SELL and trend_direction == "BULLISH":
            return False
        
        return True
    
    def _calculate_sl_pips(self, signal: Signal) -> float:
        """
        Calculate stop loss in pips.
        
        Args:
            signal: Signal with entry and SL prices
        
        Returns:
            float: Stop loss in pips
        """
        if signal.entry_price == 0 or signal.sl_price == 0:
            return 25.0
        
        pip_value = 0.01 if "JPY" in signal.symbol else 0.0001
        if "XAU" in signal.symbol:
            pip_value = 0.1
        
        return abs(signal.entry_price - signal.sl_price) / pip_value
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get plugin status.
        
        Returns:
            dict: Plugin status information
        """
        return {
            "plugin_id": self.plugin_id,
            "name": self.PLUGIN_NAME,
            "version": self.VERSION,
            "enabled": self.enabled,
            "trades_today": self.trades_today,
            "daily_pnl": self.daily_pnl,
            "config": self.config.to_dict()
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"HelloWorldPlugin(id={self.plugin_id}, enabled={self.enabled})"


def create_hello_world_plugin(config: Optional[Dict[str, Any]] = None) -> HelloWorldPlugin:
    """
    Factory function to create a Hello World plugin instance.
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        HelloWorldPlugin: Configured plugin instance
    """
    config = config or {}
    service_api = MockServiceAPI()
    return HelloWorldPlugin("hello_world", config, service_api)
