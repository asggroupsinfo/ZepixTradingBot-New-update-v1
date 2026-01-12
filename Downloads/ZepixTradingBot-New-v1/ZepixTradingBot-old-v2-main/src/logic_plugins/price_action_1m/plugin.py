"""
Price Action 1M Plugin for V6 Integration.

1-Minute Scalping Logic:
- ADX > 20
- Confidence >= 80
- Spread < 2 pips
- ORDER B ONLY
- Risk multiplier: 0.5x

Based on Document 16: PHASE_7_V6_INTEGRATION_PLAN.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order type for 1M plugin."""
    ORDER_B_ONLY = "ORDER_B_ONLY"


@dataclass
class PriceAction1MConfig:
    """Configuration for 1M Price Action plugin."""
    plugin_id: str = "price_action_1m"
    version: str = "1.0.0"
    enabled: bool = True
    min_adx: float = 20.0
    min_confidence: int = 80
    max_spread_pips: float = 2.0
    risk_multiplier: float = 0.5
    order_type: OrderType = OrderType.ORDER_B_ONLY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "version": self.version,
            "enabled": self.enabled,
            "min_adx": self.min_adx,
            "min_confidence": self.min_confidence,
            "max_spread_pips": self.max_spread_pips,
            "risk_multiplier": self.risk_multiplier,
            "order_type": self.order_type.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceAction1MConfig':
        """Create from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", "price_action_1m"),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            min_adx=float(data.get("min_adx", 20.0)),
            min_confidence=int(data.get("min_confidence", 80)),
            max_spread_pips=float(data.get("max_spread_pips", 2.0)),
            risk_multiplier=float(data.get("risk_multiplier", 0.5))
        )


@dataclass
class TradeRecord:
    """Trade record for 1M plugin."""
    ticket: int
    symbol: str
    direction: str
    lot_size: float
    entry_price: float
    sl_price: Optional[float]
    tp_price: Optional[float]
    adx: Optional[float]
    confidence_score: int
    spread_pips: float
    order_b_ticket: int
    entry_time: datetime = field(default_factory=datetime.now)
    exit_time: Optional[datetime] = None
    profit: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ticket": self.ticket,
            "symbol": self.symbol,
            "direction": self.direction,
            "lot_size": self.lot_size,
            "entry_price": self.entry_price,
            "sl_price": self.sl_price,
            "tp_price": self.tp_price,
            "adx": self.adx,
            "confidence_score": self.confidence_score,
            "spread_pips": self.spread_pips,
            "order_b_ticket": self.order_b_ticket,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "profit": self.profit
        }


class MockServiceAPI:
    """Mock ServiceAPI for 1M plugin."""
    
    def __init__(self):
        """Initialize mock service API."""
        self._next_ticket = 1000
    
    async def get_current_spread(self, symbol: str) -> float:
        """Get current spread (mock)."""
        return 1.5
    
    async def calculate_lot_size(self, symbol: str, risk_percentage: float,
                                 stop_loss_pips: float) -> float:
        """Calculate lot size (mock)."""
        return 0.1 * (risk_percentage / 1.0)
    
    async def place_single_order_b(self, symbol: str, direction: str,
                                   lot_size: float, sl_price: Optional[float],
                                   tp_price: Optional[float], comment: str) -> int:
        """Place Order B only."""
        ticket = self._next_ticket
        self._next_ticket += 1
        logger.info(f"1M: ORDER B placed #{ticket} {symbol} {direction}")
        return ticket


class PriceAction1M:
    """
    1-Minute Scalping Logic Plugin.
    
    Features:
    - ADX > 20 filter (avoid choppy markets)
    - Confidence >= 80 filter
    - Spread < 2 pips filter
    - ORDER B ONLY (quick scalp)
    - 0.5x risk multiplier
    """
    
    PLUGIN_ID = "price_action_1m"
    PLUGIN_NAME = "Price Action 1M Scalping"
    VERSION = "1.0.0"
    TIMEFRAME = "1"
    
    def __init__(self, plugin_id: str, config: Dict[str, Any],
                 service_api: Optional[MockServiceAPI] = None):
        """Initialize 1M plugin."""
        self.plugin_id = plugin_id
        self.config = PriceAction1MConfig.from_dict(config) if config else PriceAction1MConfig()
        self.service_api = service_api or MockServiceAPI()
        self.is_enabled = self.config.enabled
        self._trades: list = []
    
    def enable(self) -> None:
        """Enable plugin."""
        self.is_enabled = True
        self.config.enabled = True
        logger.info(f"{self.PLUGIN_ID} enabled")
    
    def disable(self) -> None:
        """Disable plugin."""
        self.is_enabled = False
        self.config.enabled = False
        logger.info(f"{self.PLUGIN_ID} disabled")
    
    async def on_signal_received(self, signal: Dict[str, Any]) -> bool:
        """
        Process incoming signal.
        
        Args:
            signal: Signal data dictionary
        
        Returns:
            bool: True if trade executed, False otherwise
        """
        if not self.is_enabled:
            return False
        
        if not await self._validate_entry(signal):
            return False
        
        lot = await self.service_api.calculate_lot_size(
            symbol=signal.get('symbol', ''),
            risk_percentage=1.0,
            stop_loss_pips=self._calculate_sl_pips(signal)
        )
        lot = lot * self.config.risk_multiplier
        
        ticket = await self.service_api.place_single_order_b(
            symbol=signal.get('symbol', ''),
            direction=signal.get('direction', ''),
            lot_size=lot,
            sl_price=signal.get('sl_price'),
            tp_price=signal.get('tp1_price'),
            comment=f"{self.plugin_id}_entry"
        )
        
        spread = await self.service_api.get_current_spread(signal.get('symbol', ''))
        
        trade = TradeRecord(
            ticket=ticket,
            symbol=signal.get('symbol', ''),
            direction=signal.get('direction', ''),
            lot_size=lot,
            entry_price=signal.get('price', 0),
            sl_price=signal.get('sl_price'),
            tp_price=signal.get('tp1_price'),
            adx=signal.get('adx'),
            confidence_score=signal.get('conf_score', 0),
            spread_pips=spread,
            order_b_ticket=ticket
        )
        self._trades.append(trade)
        
        logger.info(f"1M Entry: {signal.get('symbol')} {signal.get('direction')} #{ticket}")
        return True
    
    async def _validate_entry(self, signal: Dict[str, Any]) -> bool:
        """Validate entry conditions."""
        adx = signal.get('adx', 0)
        if adx is not None and adx < self.config.min_adx:
            logger.info(f"1M Skip: ADX {adx} < {self.config.min_adx} (choppy)")
            return False
        
        conf_score = signal.get('conf_score', 0)
        if conf_score < self.config.min_confidence:
            logger.info(f"1M Skip: Confidence {conf_score} < {self.config.min_confidence}")
            return False
        
        spread = await self.service_api.get_current_spread(signal.get('symbol', ''))
        if spread > self.config.max_spread_pips:
            logger.info(f"1M Skip: Spread {spread} > {self.config.max_spread_pips} pips")
            return False
        
        return True
    
    def _calculate_sl_pips(self, signal: Dict[str, Any]) -> float:
        """Calculate SL in pips."""
        price = signal.get('price', 0)
        sl = signal.get('sl_price')
        if sl is None:
            return 15.0
        return abs(price - sl) * 10
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "plugin_id": self.plugin_id,
            "name": self.PLUGIN_NAME,
            "version": self.VERSION,
            "timeframe": self.TIMEFRAME,
            "enabled": self.is_enabled,
            "order_type": "ORDER_B_ONLY",
            "config": self.config.to_dict(),
            "trade_count": len(self._trades)
        }
    
    def get_trades(self) -> list:
        """Get trade history."""
        return [t.to_dict() for t in self._trades]


def create_price_action_1m(config: Optional[Dict[str, Any]] = None,
                           service_api: Optional[MockServiceAPI] = None) -> PriceAction1M:
    """Factory function to create 1M plugin."""
    return PriceAction1M("price_action_1m", config or {}, service_api)
