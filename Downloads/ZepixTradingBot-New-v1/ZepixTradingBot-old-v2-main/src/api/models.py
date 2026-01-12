"""
API Models - Request/Response Data Classes

Document 10: API Specifications
Defines request and response models for all API operations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# Enumerations
# =============================================================================

class Direction(Enum):
    """Trade direction."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order status."""
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    CLOSED = "CLOSED"


class LogicRoute(Enum):
    """V3 logic route."""
    LOGIC1 = "LOGIC1"
    LOGIC2 = "LOGIC2"
    LOGIC3 = "LOGIC3"


class MarketState(Enum):
    """V6 market state."""
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"


class Timeframe(Enum):
    """Trading timeframes."""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


# =============================================================================
# Order Execution Models
# =============================================================================

@dataclass
class DualOrderV3Request:
    """Request model for V3 dual order placement."""
    plugin_id: str
    symbol: str
    direction: str
    lot_size_total: float
    order_a_sl: float
    order_a_tp: float
    order_b_sl: float
    order_b_tp: float
    logic_route: str
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.plugin_id != "combined_v3":
            return False
        if self.direction not in ["BUY", "SELL"]:
            return False
        if self.logic_route not in ["LOGIC1", "LOGIC2", "LOGIC3"]:
            return False
        if self.lot_size_total <= 0:
            return False
        return True


@dataclass
class DualOrderV3Response:
    """Response model for V3 dual order placement."""
    success: bool
    order_a_ticket: int = 0
    order_b_ticket: int = 0
    error_message: str = ""
    
    @classmethod
    def success_response(cls, order_a: int, order_b: int) -> "DualOrderV3Response":
        """Create success response."""
        return cls(success=True, order_a_ticket=order_a, order_b_ticket=order_b)
    
    @classmethod
    def error_response(cls, message: str) -> "DualOrderV3Response":
        """Create error response."""
        return cls(success=False, error_message=message)


@dataclass
class SingleOrderRequest:
    """Request model for single order placement (V6)."""
    plugin_id: str
    symbol: str
    direction: str
    lot_size: float
    sl_price: float
    tp_price: float
    comment: str = ""
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.direction not in ["BUY", "SELL"]:
            return False
        if self.lot_size <= 0:
            return False
        return True


@dataclass
class SingleOrderResponse:
    """Response model for single order placement."""
    success: bool
    ticket: int = 0
    error_message: str = ""
    
    @classmethod
    def success_response(cls, ticket: int) -> "SingleOrderResponse":
        """Create success response."""
        return cls(success=True, ticket=ticket)
    
    @classmethod
    def error_response(cls, message: str) -> "SingleOrderResponse":
        """Create error response."""
        return cls(success=False, error_message=message)


@dataclass
class DualOrderV6Request:
    """Request model for V6 dual order placement."""
    plugin_id: str
    symbol: str
    direction: str
    lot_size_total: float
    sl_price: float
    tp1_price: float
    tp2_price: float
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.direction not in ["BUY", "SELL"]:
            return False
        if self.lot_size_total <= 0:
            return False
        return True


@dataclass
class DualOrderV6Response:
    """Response model for V6 dual order placement."""
    success: bool
    order_a_ticket: int = 0
    order_b_ticket: int = 0
    error_message: str = ""
    
    @classmethod
    def success_response(cls, order_a: int, order_b: int) -> "DualOrderV6Response":
        """Create success response."""
        return cls(success=True, order_a_ticket=order_a, order_b_ticket=order_b)
    
    @classmethod
    def error_response(cls, message: str) -> "DualOrderV6Response":
        """Create error response."""
        return cls(success=False, error_message=message)


@dataclass
class ModifyOrderRequest:
    """Request model for order modification."""
    plugin_id: str
    order_id: int
    new_sl: Optional[float] = None
    new_tp: Optional[float] = None
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.order_id <= 0:
            return False
        if self.new_sl is None and self.new_tp is None:
            return False
        return True


@dataclass
class ModifyOrderResponse:
    """Response model for order modification."""
    success: bool
    error_message: str = ""


@dataclass
class ClosePositionRequest:
    """Request model for position close."""
    plugin_id: str
    order_id: int
    reason: str = "Manual"
    
    def validate(self) -> bool:
        """Validate request parameters."""
        return self.order_id > 0


@dataclass
class ClosePositionResponse:
    """Response model for position close."""
    success: bool
    closed_volume: float = 0.0
    profit_pips: float = 0.0
    profit_dollars: float = 0.0
    error_message: str = ""
    
    @classmethod
    def success_response(cls, volume: float, pips: float, dollars: float) -> "ClosePositionResponse":
        """Create success response."""
        return cls(success=True, closed_volume=volume, profit_pips=pips, profit_dollars=dollars)
    
    @classmethod
    def error_response(cls, message: str) -> "ClosePositionResponse":
        """Create error response."""
        return cls(success=False, error_message=message)


@dataclass
class ClosePartialRequest:
    """Request model for partial position close."""
    plugin_id: str
    order_id: int
    percentage: float
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.order_id <= 0:
            return False
        if self.percentage <= 0 or self.percentage > 100:
            return False
        return True


@dataclass
class ClosePartialResponse:
    """Response model for partial position close."""
    success: bool
    closed_volume: float = 0.0
    remaining_volume: float = 0.0
    profit_pips: float = 0.0
    profit_dollars: float = 0.0
    error_message: str = ""


@dataclass
class OrderInfo:
    """Order information model."""
    ticket: int
    symbol: str
    direction: str
    lot_size: float
    entry_price: float
    current_price: float
    sl_price: float
    tp_price: float
    profit_pips: float
    profit_dollars: float
    status: str
    open_time: str
    comment: str = ""


# =============================================================================
# Risk Management Models
# =============================================================================

@dataclass
class LotSizeRequest:
    """Request model for lot size calculation."""
    plugin_id: str
    symbol: str
    risk_percentage: float
    stop_loss_pips: float
    account_balance: Optional[float] = None
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.risk_percentage <= 0 or self.risk_percentage > 10:
            return False
        if self.stop_loss_pips <= 0:
            return False
        return True


@dataclass
class LotSizeResponse:
    """Response model for lot size calculation."""
    success: bool
    lot_size: float = 0.0
    risk_amount: float = 0.0
    error_message: str = ""


@dataclass
class DailyLimitResponse:
    """Response model for daily limit check."""
    daily_loss: float
    daily_limit: float
    remaining: float
    can_trade: bool


@dataclass
class RiskTierResponse:
    """Response model for risk tier."""
    tier: int
    tier_name: str
    risk_percentage: float
    max_trades: int
    max_lot_size: float


# =============================================================================
# Trend Management Models
# =============================================================================

@dataclass
class TimeframeTrendResponse:
    """Response model for timeframe trend."""
    timeframe: str
    direction: str
    value: int
    last_updated: str


@dataclass
class MTFTrendsResponse:
    """Response model for MTF trends."""
    m15: int
    h1: int
    h4: int
    d1: int
    
    def get_aligned_count(self, direction: str) -> int:
        """Get count of aligned trends."""
        target = 1 if direction == "BUY" else -1
        count = 0
        if self.m15 == target:
            count += 1
        if self.h1 == target:
            count += 1
        if self.h4 == target:
            count += 1
        if self.d1 == target:
            count += 1
        return count


@dataclass
class TrendPulseData:
    """Trend Pulse data model."""
    timeframe: str
    bull_count: int
    bear_count: int
    market_state: str
    last_updated: str


@dataclass
class PulseDataResponse:
    """Response model for pulse data."""
    symbol: str
    timeframes: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    def is_bullish_aligned(self) -> bool:
        """Check if overall bullish aligned."""
        total_bull = sum(tf.get("bull_count", 0) for tf in self.timeframes.values())
        total_bear = sum(tf.get("bear_count", 0) for tf in self.timeframes.values())
        return total_bull > total_bear
    
    def is_bearish_aligned(self) -> bool:
        """Check if overall bearish aligned."""
        total_bull = sum(tf.get("bull_count", 0) for tf in self.timeframes.values())
        total_bear = sum(tf.get("bear_count", 0) for tf in self.timeframes.values())
        return total_bear > total_bull


# =============================================================================
# Profit Booking Models
# =============================================================================

@dataclass
class BookProfitRequest:
    """Request model for profit booking."""
    plugin_id: str
    order_id: int
    percentage: float
    reason: str = "TP1"
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.order_id <= 0:
            return False
        if self.percentage <= 0 or self.percentage > 100:
            return False
        return True


@dataclass
class BookProfitResponse:
    """Response model for profit booking."""
    success: bool
    closed_volume: float = 0.0
    remaining_volume: float = 0.0
    profit_pips: float = 0.0
    profit_dollars: float = 0.0
    error_message: str = ""


@dataclass
class BreakevenRequest:
    """Request model for breakeven move."""
    plugin_id: str
    order_id: int
    buffer_pips: float = 2.0
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if self.order_id <= 0:
            return False
        if self.buffer_pips < 0:
            return False
        return True


@dataclass
class BreakevenResponse:
    """Response model for breakeven move."""
    success: bool
    new_sl_price: float = 0.0
    error_message: str = ""


@dataclass
class BookingRecord:
    """Profit booking record model."""
    id: int
    order_id: int
    booking_time: str
    percentage: float
    closed_volume: float
    profit_pips: float
    profit_dollars: float
    reason: str


# =============================================================================
# Market Data Models
# =============================================================================

@dataclass
class SpreadResponse:
    """Response model for spread."""
    symbol: str
    spread_pips: float
    timestamp: str


@dataclass
class PriceResponse:
    """Response model for price."""
    symbol: str
    bid: float
    ask: float
    spread_pips: float
    timestamp: str


@dataclass
class SymbolInfoResponse:
    """Response model for symbol info."""
    symbol: str
    pip_value: float
    lot_step: float
    min_lot: float
    max_lot: float
    contract_size: float
    digits: int


# =============================================================================
# Error Response Model
# =============================================================================

@dataclass
class ErrorResponse:
    """Standard error response model."""
    success: bool = False
    error_code: str = ""
    error_message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def validation_error(cls, message: str, details: Dict[str, Any] = None) -> "ErrorResponse":
        """Create validation error response."""
        return cls(
            error_code="VALIDATION_ERROR",
            error_message=message,
            details=details or {}
        )
    
    @classmethod
    def permission_error(cls, message: str) -> "ErrorResponse":
        """Create permission error response."""
        return cls(
            error_code="PERMISSION_DENIED",
            error_message=message
        )
    
    @classmethod
    def not_found_error(cls, message: str) -> "ErrorResponse":
        """Create not found error response."""
        return cls(
            error_code="NOT_FOUND",
            error_message=message
        )
    
    @classmethod
    def execution_error(cls, message: str) -> "ErrorResponse":
        """Create execution error response."""
        return cls(
            error_code="EXECUTION_ERROR",
            error_message=message
        )
