"""
Price Action 1H Plugin for V6 Integration.

1-Hour Position Logic:
- ADX >= 20
- Confidence >= 60
- Require 4H/1D alignment
- ORDER A ONLY
- Risk multiplier: 0.625x

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
    """Order type for 1H plugin."""
    ORDER_A_ONLY = "ORDER_A_ONLY"


class MarketState(Enum):
    """Market state enumeration."""
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    UNKNOWN = "UNKNOWN"


@dataclass
class PriceAction1HConfig:
    """Configuration for 1H Price Action plugin."""
    plugin_id: str = "price_action_1h"
    version: str = "1.0.0"
    enabled: bool = True
    min_adx: float = 20.0
    min_confidence: int = 60
    max_spread_pips: float = 5.0
    # CRITICAL FIX: Changed from 0.625 to 0.6 per planning doc 05_PRICE_ACTION_LOGIC_1H.md
    risk_multiplier: float = 0.6
    require_4h_1d_alignment: bool = True
    check_market_state: bool = True
    order_type: OrderType = OrderType.ORDER_A_ONLY
    # ADX extreme threshold for warning (per planning compliance)
    adx_extreme_threshold: float = 50.0
    
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
            "require_4h_1d_alignment": self.require_4h_1d_alignment,
            "check_market_state": self.check_market_state,
            "order_type": self.order_type.value,
            "adx_extreme_threshold": self.adx_extreme_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceAction1HConfig':
        """Create from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", "price_action_1h"),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            min_adx=float(data.get("min_adx", 20.0)),
            min_confidence=int(data.get("min_confidence", 60)),
            max_spread_pips=float(data.get("max_spread_pips", 5.0)),
            # CRITICAL FIX: Default to 0.6 per planning doc
            risk_multiplier=float(data.get("risk_multiplier", 0.6)),
            require_4h_1d_alignment=data.get("require_4h_1d_alignment", True),
            check_market_state=data.get("check_market_state", True),
            adx_extreme_threshold=float(data.get("adx_extreme_threshold", 50.0))
        )


@dataclass
class TradeRecord:
    """Trade record for 1H plugin."""
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
    htf_alignment: str
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
            "htf_alignment": self.htf_alignment,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "profit": self.profit
        }


class MockServiceAPI:
    """Mock ServiceAPI for 1H plugin."""
    
    def __init__(self):
        """Initialize mock service API."""
        self._next_ticket = 60000
        self._market_state = MarketState.TRENDING_BULLISH
    
    async def get_current_spread(self, symbol: str) -> float:
        """Get current spread (mock)."""
        return 2.5
    
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
        logger.info(f"1H: ORDER A placed #{ticket} {symbol} {direction}")
        return ticket
    
    async def get_market_state(self, symbol: str) -> MarketState:
        """Get market state (mock)."""
        return self._market_state
    
    async def check_4h_1d_alignment(self, symbol: str, direction: str) -> bool:
        """Check 4H/1D alignment (mock)."""
        return True
    
    def set_market_state(self, state: MarketState) -> None:
        """Set market state for testing."""
        self._market_state = state


class PriceAction1H:
    """
    1-Hour Position Logic Plugin.
    
    Features:
    - ADX >= 20 filter
    - Confidence >= 60 filter
    - Require 4H/1D alignment
    - Market state check
    - ORDER A ONLY
    - 0.625x risk multiplier
    """
    
    PLUGIN_ID = "price_action_1h"
    PLUGIN_NAME = "Price Action 1H Position"
    VERSION = "1.0.0"
    TIMEFRAME = "60"
    
    def __init__(self, plugin_id: str, config: Dict[str, Any],
                 service_api: Optional[MockServiceAPI] = None):
        """Initialize 1H plugin."""
        self.plugin_id = plugin_id
        self.config = PriceAction1HConfig.from_dict(config) if config else PriceAction1HConfig()
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
        
        if self.config.check_market_state:
            market_state = await self.service_api.get_market_state(signal.get('symbol', ''))
            if not self._is_aligned(signal.get('direction', ''), market_state):
                logger.info(f"1H Skip: Direction {signal.get('direction')} not aligned with {market_state.value}")
                return False
        else:
            market_state = MarketState.UNKNOWN
        
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
            tp_price=signal.get('tp3_price'),
            comment=f"{self.plugin_id}_entry"
        )
        
        htf_aligned = await self.service_api.check_4h_1d_alignment(
            signal.get('symbol', ''), signal.get('direction', '')
        )
        
        trade = TradeRecord(
            ticket=ticket,
            symbol=signal.get('symbol', ''),
            direction=signal.get('direction', ''),
            lot_size=lot,
            entry_price=signal.get('price', 0),
            sl_price=signal.get('sl_price'),
            tp_price=signal.get('tp3_price'),
            adx=signal.get('adx'),
            confidence_score=signal.get('conf_score', 0),
            order_a_ticket=ticket,
            market_state=market_state.value,
            htf_alignment="ALIGNED" if htf_aligned else "NOT_ALIGNED"
        )
        self._trades.append(trade)
        
        logger.info(f"1H Entry: {signal.get('symbol')} {signal.get('direction')} #{ticket}")
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
            logger.info(f"1H Skip: ADX {adx} < {self.config.min_adx}")
            return False
        
        # CRITICAL FIX: Add ADX > 50 warning per planning doc 05_PRICE_ACTION_LOGIC_1H.md
        if adx is not None and adx > self.config.adx_extreme_threshold:
            logger.warning(
                f"1H CAUTION: Extreme Trend Detected - ADX {adx} > {self.config.adx_extreme_threshold}. "
                f"Symbol: {signal.get('symbol', '')} Direction: {signal.get('direction', '')}. "
                f"Trade will proceed but with elevated risk."
            )
        
        conf_score = signal.get('conf_score', 0)
        if conf_score < self.config.min_confidence:
            logger.info(f"1H Skip: Confidence {conf_score} < {self.config.min_confidence}")
            return False
        
        spread = await self.service_api.get_current_spread(signal.get('symbol', ''))
        if spread > self.config.max_spread_pips:
            logger.info(f"1H Skip: Spread {spread} > {self.config.max_spread_pips} pips")
            return False
        
        if self.config.require_4h_1d_alignment:
            aligned = await self.service_api.check_4h_1d_alignment(
                signal.get('symbol', ''), signal.get('direction', '')
            )
            if not aligned:
                logger.info("1H Skip: 4H/1D alignment not confirmed")
                return False
        
        return True
    
    def _calculate_sl_pips(self, signal: Dict[str, Any]) -> float:
        """Calculate SL in pips."""
        price = signal.get('price', 0)
        sl = signal.get('sl_price')
        if sl is None:
            return 40.0
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


def create_price_action_1h(config: Optional[Dict[str, Any]] = None,
                           service_api: Optional[MockServiceAPI] = None) -> PriceAction1H:
    """Factory function to create 1H plugin."""
    return PriceAction1H("price_action_1h", config or {}, service_api)
