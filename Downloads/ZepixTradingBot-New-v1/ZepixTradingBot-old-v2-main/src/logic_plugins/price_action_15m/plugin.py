"""
Price Action 15M Plugin for V6 Integration.

15-Minute Position Logic:
- ADX >= 20
- Confidence >= 70
- Check market state
- Check pulse alignment
- ORDER A ONLY
- Risk multiplier: 1.0x

Based on Document 16: PHASE_7_V6_INTEGRATION_PLAN.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order type for 15M plugin."""
    ORDER_A_ONLY = "ORDER_A_ONLY"


class MarketState(Enum):
    """Market state enumeration."""
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    UNKNOWN = "UNKNOWN"


@dataclass
class PriceAction15MConfig:
    """Configuration for 15M Price Action plugin."""
    plugin_id: str = "price_action_15m"
    version: str = "1.0.0"
    enabled: bool = True
    min_adx: float = 20.0
    min_confidence: int = 70
    max_spread_pips: float = 4.0
    risk_multiplier: float = 1.0
    check_market_state: bool = True
    check_pulse_alignment: bool = True
    order_type: OrderType = OrderType.ORDER_A_ONLY
    
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
            "check_market_state": self.check_market_state,
            "check_pulse_alignment": self.check_pulse_alignment,
            "order_type": self.order_type.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceAction15MConfig':
        """Create from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", "price_action_15m"),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            min_adx=float(data.get("min_adx", 20.0)),
            min_confidence=int(data.get("min_confidence", 70)),
            max_spread_pips=float(data.get("max_spread_pips", 4.0)),
            risk_multiplier=float(data.get("risk_multiplier", 1.0)),
            check_market_state=data.get("check_market_state", True),
            check_pulse_alignment=data.get("check_pulse_alignment", True)
        )


@dataclass
class TradeRecord:
    """Trade record for 15M plugin."""
    ticket: int
    symbol: str
    direction: str
    lot_size: float
    entry_price: float
    sl_price: Optional[float]
    tp_price: Optional[float]
    adx: Optional[float]
    confidence_score: int
    order_a_ticket: int
    market_state: str
    pulse_alignment: str
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
            "order_a_ticket": self.order_a_ticket,
            "market_state": self.market_state,
            "pulse_alignment": self.pulse_alignment,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "profit": self.profit
        }


class MockServiceAPI:
    """Mock ServiceAPI for 15M plugin."""
    
    def __init__(self):
        """Initialize mock service API."""
        self._next_ticket = 15000
        self._market_state = MarketState.TRENDING_BULLISH
    
    async def get_current_spread(self, symbol: str) -> float:
        """Get current spread (mock)."""
        return 2.0
    
    async def calculate_lot_size(self, symbol: str, risk_percentage: float,
                                 stop_loss_pips: float) -> float:
        """Calculate lot size (mock)."""
        return 0.1 * (risk_percentage / 1.0)
    
    async def place_single_order_a(self, symbol: str, direction: str,
                                   lot_size: float, sl_price: Optional[float],
                                   tp_price: Optional[float], comment: str) -> int:
        """Place Order A only."""
        ticket = self._next_ticket
        self._next_ticket += 1
        logger.info(f"15M: ORDER A placed #{ticket} {symbol} {direction}")
        return ticket
    
    async def get_market_state(self, symbol: str) -> MarketState:
        """Get market state (mock)."""
        return self._market_state
    
    async def check_pulse_alignment(self, symbol: str, direction: str) -> bool:
        """Check pulse alignment (mock)."""
        return True
    
    def set_market_state(self, state: MarketState) -> None:
        """Set market state for testing."""
        self._market_state = state


class PriceAction15M:
    """
    15-Minute Position Logic Plugin.
    
    Features:
    - ADX >= 20 filter
    - Confidence >= 70 filter
    - Market state check
    - Pulse alignment check
    - ORDER A ONLY
    - 1.0x risk multiplier
    """
    
    PLUGIN_ID = "price_action_15m"
    PLUGIN_NAME = "Price Action 15M Position"
    VERSION = "1.0.0"
    TIMEFRAME = "15"
    
    def __init__(self, plugin_id: str, config: Dict[str, Any],
                 service_api: Optional[MockServiceAPI] = None):
        """Initialize 15M plugin."""
        self.plugin_id = plugin_id
        self.config = PriceAction15MConfig.from_dict(config) if config else PriceAction15MConfig()
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
        
        market_state = await self.service_api.get_market_state(signal.get('symbol', ''))
        if not self._is_aligned(signal.get('direction', ''), market_state):
            logger.info(f"15M Skip: Direction {signal.get('direction')} not aligned with {market_state.value}")
            return False
        
        if not await self._validate_entry(signal):
            return False
        
        lot = await self.service_api.calculate_lot_size(
            symbol=signal.get('symbol', ''),
            risk_percentage=1.0,
            stop_loss_pips=self._calculate_sl_pips(signal)
        )
        lot = lot * self.config.risk_multiplier
        
        ticket = await self.service_api.place_single_order_a(
            symbol=signal.get('symbol', ''),
            direction=signal.get('direction', ''),
            lot_size=lot,
            sl_price=signal.get('sl_price'),
            tp_price=signal.get('tp2_price'),
            comment=f"{self.plugin_id}_entry"
        )
        
        pulse_aligned = await self.service_api.check_pulse_alignment(
            signal.get('symbol', ''), signal.get('direction', '')
        )
        
        trade = TradeRecord(
            ticket=ticket,
            symbol=signal.get('symbol', ''),
            direction=signal.get('direction', ''),
            lot_size=lot,
            entry_price=signal.get('price', 0),
            sl_price=signal.get('sl_price'),
            tp_price=signal.get('tp2_price'),
            adx=signal.get('adx'),
            confidence_score=signal.get('conf_score', 0),
            order_a_ticket=ticket,
            market_state=market_state.value,
            pulse_alignment="ALIGNED" if pulse_aligned else "NOT_ALIGNED"
        )
        self._trades.append(trade)
        
        logger.info(f"15M Entry: {signal.get('symbol')} {signal.get('direction')} #{ticket}")
        return True
    
    def _is_aligned(self, direction: str, market_state: MarketState) -> bool:
        """Check if direction is aligned with market state."""
        if market_state == MarketState.SIDEWAYS:
            return False
        if direction == "BUY" and market_state == MarketState.TRENDING_BEARISH:
            return False
        if direction == "SELL" and market_state == MarketState.TRENDING_BULLISH:
            return False
        return True
    
    async def _validate_entry(self, signal: Dict[str, Any]) -> bool:
        """Validate entry conditions."""
        adx = signal.get('adx', 0)
        if adx is not None and adx < self.config.min_adx:
            logger.info(f"15M Skip: ADX {adx} < {self.config.min_adx}")
            return False
        
        conf_score = signal.get('conf_score', 0)
        if conf_score < self.config.min_confidence:
            logger.info(f"15M Skip: Confidence {conf_score} < {self.config.min_confidence}")
            return False
        
        spread = await self.service_api.get_current_spread(signal.get('symbol', ''))
        if spread > self.config.max_spread_pips:
            logger.info(f"15M Skip: Spread {spread} > {self.config.max_spread_pips} pips")
            return False
        
        if self.config.check_pulse_alignment:
            aligned = await self.service_api.check_pulse_alignment(
                signal.get('symbol', ''), signal.get('direction', '')
            )
            if not aligned:
                logger.info("15M Skip: Pulse alignment not confirmed")
                return False
        
        return True
    
    def _calculate_sl_pips(self, signal: Dict[str, Any]) -> float:
        """Calculate SL in pips."""
        price = signal.get('price', 0)
        sl = signal.get('sl_price')
        if sl is None:
            return 25.0
        return abs(price - sl) * 10
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "plugin_id": self.plugin_id,
            "name": self.PLUGIN_NAME,
            "version": self.VERSION,
            "timeframe": self.TIMEFRAME,
            "enabled": self.is_enabled,
            "order_type": "ORDER_A_ONLY",
            "config": self.config.to_dict(),
            "trade_count": len(self._trades)
        }
    
    def get_trades(self) -> list:
        """Get trade history."""
        return [t.to_dict() for t in self._trades]


def create_price_action_15m(config: Optional[Dict[str, Any]] = None,
                            service_api: Optional[MockServiceAPI] = None) -> PriceAction15M:
    """Factory function to create 15M plugin."""
    return PriceAction15M("price_action_15m", config or {}, service_api)
