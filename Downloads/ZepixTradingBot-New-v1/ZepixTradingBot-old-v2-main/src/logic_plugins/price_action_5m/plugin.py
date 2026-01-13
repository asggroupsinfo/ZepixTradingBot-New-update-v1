"""
Price Action 5M Plugin for V6 Integration.

5-Minute Swing Logic:
- ADX >= 25
- Confidence >= 70
- Require 15M alignment
- DUAL ORDERS (Order A + Order B)
- Risk multiplier: 1.0x

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
    """Order type for 5M plugin."""
    DUAL_ORDERS = "DUAL_ORDERS"


@dataclass
class PriceAction5MConfig:
    """Configuration for 5M Price Action plugin."""
    plugin_id: str = "price_action_5m"
    version: str = "1.0.0"
    enabled: bool = True
    min_adx: float = 25.0
    min_confidence: int = 70
    max_spread_pips: float = 3.0
    risk_multiplier: float = 1.0
    require_15m_alignment: bool = True
    order_type: OrderType = OrderType.DUAL_ORDERS
    
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
            "require_15m_alignment": self.require_15m_alignment,
            "order_type": self.order_type.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceAction5MConfig':
        """Create from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", "price_action_5m"),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            min_adx=float(data.get("min_adx", 25.0)),
            min_confidence=int(data.get("min_confidence", 70)),
            max_spread_pips=float(data.get("max_spread_pips", 3.0)),
            risk_multiplier=float(data.get("risk_multiplier", 1.0)),
            require_15m_alignment=data.get("require_15m_alignment", True)
        )


@dataclass
class TradeRecord:
    """Trade record for 5M plugin."""
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
    order_b_ticket: int
    alignment_15m: bool
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
            "order_b_ticket": self.order_b_ticket,
            "alignment_15m": self.alignment_15m,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "profit": self.profit
        }


class MockServiceAPI:
    """Mock ServiceAPI for 5M plugin."""
    
    def __init__(self):
        """Initialize mock service API."""
        self._next_ticket = 5000
    
    async def get_current_spread(self, symbol: str) -> float:
        """Get current spread (mock)."""
        return 1.8
    
    async def calculate_lot_size(self, symbol: str, risk_percentage: float,
                                 stop_loss_pips: float) -> float:
        """Calculate lot size (mock)."""
        return 0.1 * (risk_percentage / 1.0)
    
    async def place_dual_orders(self, symbol: str, direction: str, lot_size: float,
                                order_a_sl: Optional[float], order_a_tp: Optional[float],
                                order_b_sl: Optional[float], order_b_tp: Optional[float],
                                comment: str) -> Tuple[int, int]:
        """Place dual orders (Order A + Order B)."""
        ticket_a = self._next_ticket
        self._next_ticket += 1
        ticket_b = self._next_ticket
        self._next_ticket += 1
        logger.info(f"5M: DUAL ORDERS placed #{ticket_a}, #{ticket_b} {symbol} {direction}")
        return ticket_a, ticket_b
    
    async def check_15m_alignment(self, symbol: str, direction: str) -> bool:
        """Check 15M alignment (mock)."""
        return True


class PriceAction5M:
    """
    5-Minute Swing Logic Plugin.
    
    Features:
    - ADX >= 25 filter
    - Confidence >= 70 filter
    - Require 15M alignment
    - DUAL ORDERS (Order A + Order B)
    - 1.0x risk multiplier
    """
    
    PLUGIN_ID = "price_action_5m"
    PLUGIN_NAME = "Price Action 5M Swing"
    VERSION = "1.0.0"
    TIMEFRAME = "5"
    
    def __init__(self, plugin_id: str, config: Dict[str, Any],
                 service_api: Optional[MockServiceAPI] = None):
        """Initialize 5M plugin."""
        self.plugin_id = plugin_id
        self.config = PriceAction5MConfig.from_dict(config) if config else PriceAction5MConfig()
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
        
        alignment_15m = await self._validate_with_trend_alignment(signal)
        if not alignment_15m:
            return False
        
        lot = await self.service_api.calculate_lot_size(
            symbol=signal.get('symbol', ''),
            risk_percentage=1.0,
            stop_loss_pips=self._calculate_sl_pips(signal)
        )
        lot = lot * self.config.risk_multiplier
        
        ticket_a, ticket_b = await self.service_api.place_dual_orders(
            symbol=signal.get('symbol', ''),
            direction=signal.get('direction', ''),
            lot_size=lot,
            order_a_sl=signal.get('sl_price'),
            order_a_tp=signal.get('tp2_price'),
            order_b_sl=signal.get('sl_price'),
            order_b_tp=signal.get('tp1_price'),
            comment=f"{self.plugin_id}_entry"
        )
        
        trade = TradeRecord(
            ticket=ticket_a,
            symbol=signal.get('symbol', ''),
            direction=signal.get('direction', ''),
            lot_size=lot,
            entry_price=signal.get('price', 0),
            sl_price=signal.get('sl_price'),
            tp_price=signal.get('tp2_price'),
            adx=signal.get('adx'),
            confidence_score=signal.get('conf_score', 0),
            order_a_ticket=ticket_a,
            order_b_ticket=ticket_b,
            alignment_15m=True
        )
        self._trades.append(trade)
        
        logger.info(f"5M Entry: {signal.get('symbol')} {signal.get('direction')} #{ticket_a}, #{ticket_b}")
        return True
    
    async def _validate_with_trend_alignment(self, signal: Dict[str, Any]) -> bool:
        """Validate entry with trend alignment."""
        adx = signal.get('adx', 0)
        adx_strength = signal.get('adx_strength', '').upper()
        
        # Planning doc 03_PRICE_ACTION_LOGIC_5M.md: ADX >= 25 AND not WEAK
        if adx is not None and adx < self.config.min_adx:
            logger.info(f"5M Skip: ADX {adx} < {self.config.min_adx}")
            return False
        
        # CRITICAL FIX: Check ADX strength is not WEAK (per planning compliance)
        if adx_strength == "WEAK":
            logger.info(f"5M Skip: ADX strength is WEAK (requires MODERATE or STRONG)")
            return False
        
        conf_score = signal.get('conf_score', 0)
        if conf_score < self.config.min_confidence:
            logger.info(f"5M Skip: Confidence {conf_score} < {self.config.min_confidence}")
            return False
        
        spread = await self.service_api.get_current_spread(signal.get('symbol', ''))
        if spread > self.config.max_spread_pips:
            logger.info(f"5M Skip: Spread {spread} > {self.config.max_spread_pips} pips")
            return False
        
        if self.config.require_15m_alignment:
            aligned = await self.service_api.check_15m_alignment(
                signal.get('symbol', ''), signal.get('direction', '')
            )
            if not aligned:
                logger.info("5M Skip: 15M alignment not confirmed")
                return False
        
        return True
    
    def _calculate_sl_pips(self, signal: Dict[str, Any]) -> float:
        """Calculate SL in pips."""
        price = signal.get('price', 0)
        sl = signal.get('sl_price')
        if sl is None:
            return 20.0
        return abs(price - sl) * 10
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "plugin_id": self.plugin_id,
            "name": self.PLUGIN_NAME,
            "version": self.VERSION,
            "timeframe": self.TIMEFRAME,
            "enabled": self.is_enabled,
            "order_type": "DUAL_ORDERS",
            "config": self.config.to_dict(),
            "trade_count": len(self._trades)
        }
    
    def get_trades(self) -> list:
        """Get trade history."""
        return [t.to_dict() for t in self._trades]


def create_price_action_5m(config: Optional[Dict[str, Any]] = None,
                           service_api: Optional[MockServiceAPI] = None) -> PriceAction5M:
    """Factory function to create 5M plugin."""
    return PriceAction5M("price_action_5m", config or {}, service_api)
