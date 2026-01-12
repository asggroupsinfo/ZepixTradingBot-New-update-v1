"""
V6 Alert Models for V5 Hybrid Plugin Architecture.

This module provides data models for V6 Price Action alerts:
- ZepixV6Alert: Enhanced alert payload with 15 fields
- TrendPulseAlert: Trend Pulse update alerts
- V6AlertParser: Parser for V6 alert payloads

Based on Document 16: PHASE_7_V6_INTEGRATION_PLAN.md

Version: 1.0
Date: 2026-01-12
"""

import re
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, List
from enum import Enum
from datetime import datetime


class V6AlertType(Enum):
    """V6 alert types."""
    BULLISH_ENTRY = "BULLISH_ENTRY"
    BEARISH_ENTRY = "BEARISH_ENTRY"
    EXIT_BULLISH = "EXIT_BULLISH"
    EXIT_BEARISH = "EXIT_BEARISH"
    TREND_PULSE = "TREND_PULSE"
    INFO = "INFO"


class V6Direction(Enum):
    """V6 trade direction."""
    BUY = "BUY"
    SELL = "SELL"


class V6ConfidenceLevel(Enum):
    """V6 confidence level."""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class V6ADXStrength(Enum):
    """V6 ADX strength."""
    STRONG = "STRONG"
    WEAK = "WEAK"
    NONE = "NONE"


class V6MarketState(Enum):
    """V6 market state."""
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    UNKNOWN = "UNKNOWN"


class V6TrendlineStatus(Enum):
    """V6 trendline status."""
    TL_OK = "TL_OK"
    TL_BROKEN = "TL_BROKEN"


class V6Timeframe(Enum):
    """V6 timeframes."""
    M1 = "1"
    M5 = "5"
    M15 = "15"
    H1 = "60"


class V6OrderRouting(Enum):
    """V6 order routing types."""
    ORDER_A_ONLY = "ORDER_A_ONLY"
    ORDER_B_ONLY = "ORDER_B_ONLY"
    DUAL_ORDERS = "DUAL_ORDERS"


@dataclass
class ZepixV6Alert:
    """
    V6 Enhanced Alert Payload - 15 Fields.
    Source: Pine Script Signals & Overlays V6
    """
    alert_type: str
    ticker: str
    tf: str
    price: float
    direction: str
    conf_level: str
    conf_score: int
    adx: Optional[float] = None
    adx_strength: str = "NONE"
    sl: Optional[float] = None
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    alignment: str = "0/0"
    tl_status: str = "TL_OK"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_pulse_counts(self) -> Tuple[int, int]:
        """Parse alignment '5/1' -> (5, 1)."""
        try:
            parts = self.alignment.split('/')
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            return 0, 0
    
    def get_order_routing(self) -> V6OrderRouting:
        """Get order routing based on timeframe."""
        if self.tf == "1":
            return V6OrderRouting.ORDER_B_ONLY
        elif self.tf == "5":
            return V6OrderRouting.DUAL_ORDERS
        else:
            return V6OrderRouting.ORDER_A_ONLY
    
    def is_entry_signal(self) -> bool:
        """Check if this is an entry signal."""
        return self.alert_type in ["BULLISH_ENTRY", "BEARISH_ENTRY"]
    
    def is_exit_signal(self) -> bool:
        """Check if this is an exit signal."""
        return self.alert_type in ["EXIT_BULLISH", "EXIT_BEARISH"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_type": self.alert_type,
            "ticker": self.ticker,
            "tf": self.tf,
            "price": self.price,
            "direction": self.direction,
            "conf_level": self.conf_level,
            "conf_score": self.conf_score,
            "adx": self.adx,
            "adx_strength": self.adx_strength,
            "sl": self.sl,
            "tp1": self.tp1,
            "tp2": self.tp2,
            "tp3": self.tp3,
            "alignment": self.alignment,
            "tl_status": self.tl_status,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZepixV6Alert':
        """Create from dictionary."""
        return cls(
            alert_type=data.get("alert_type", ""),
            ticker=data.get("ticker", ""),
            tf=data.get("tf", ""),
            price=float(data.get("price", 0)),
            direction=data.get("direction", ""),
            conf_level=data.get("conf_level", "MODERATE"),
            conf_score=int(data.get("conf_score", 0)),
            adx=float(data["adx"]) if data.get("adx") and data["adx"] != "NA" else None,
            adx_strength=data.get("adx_strength", "NONE"),
            sl=float(data["sl"]) if data.get("sl") else None,
            tp1=float(data["tp1"]) if data.get("tp1") else None,
            tp2=float(data["tp2"]) if data.get("tp2") else None,
            tp3=float(data["tp3"]) if data.get("tp3") else None,
            alignment=data.get("alignment", "0/0"),
            tl_status=data.get("tl_status", "TL_OK")
        )


@dataclass
class TrendPulseAlert:
    """
    Separate alert type for Trend Pulse updates.
    """
    alert_type: str
    symbol: str
    tf: str
    bull_count: int
    bear_count: int
    changes: str = ""
    state: str = "UNKNOWN"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_market_state(self) -> V6MarketState:
        """Get market state enum."""
        try:
            return V6MarketState(self.state)
        except ValueError:
            return V6MarketState.UNKNOWN
    
    def is_bullish(self) -> bool:
        """Check if trend is bullish."""
        return self.bull_count > self.bear_count
    
    def is_bearish(self) -> bool:
        """Check if trend is bearish."""
        return self.bear_count > self.bull_count
    
    def is_sideways(self) -> bool:
        """Check if market is sideways."""
        return self.bull_count == self.bear_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_type": self.alert_type,
            "symbol": self.symbol,
            "tf": self.tf,
            "bull_count": self.bull_count,
            "bear_count": self.bear_count,
            "changes": self.changes,
            "state": self.state,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrendPulseAlert':
        """Create from dictionary."""
        return cls(
            alert_type=data.get("alert_type", "TREND_PULSE"),
            symbol=data.get("symbol", ""),
            tf=data.get("tf", ""),
            bull_count=int(data.get("bull_count", 0)),
            bear_count=int(data.get("bear_count", 0)),
            changes=data.get("changes", ""),
            state=data.get("state", "UNKNOWN")
        )


class V6AlertParser:
    """Parser for V6 alert payloads."""
    
    DELIMITER = "|"
    
    @classmethod
    def parse_v6_payload(cls, payload: str) -> ZepixV6Alert:
        """
        Parse V6 alert payload string.
        
        Format: TYPE|TICKER|TF|PRICE|DIRECTION|CONF_LEVEL|CONF_SCORE|ADX|ADX_STRENGTH|SL|TP1|TP2|TP3|ALIGNMENT|TL_STATUS
        Example: BULLISH_ENTRY|XAUUSD|5|2030.50|BUY|HIGH|85|25.5|STRONG|2028.00|2032.00|2035.00|2038.00|5/1|TL_OK
        """
        parts = payload.split(cls.DELIMITER)
        
        if len(parts) < 7:
            raise ValueError(f"Invalid V6 payload: expected at least 7 fields, got {len(parts)}")
        
        def safe_float(value: str) -> Optional[float]:
            if not value or value == "NA" or value == "":
                return None
            try:
                return float(value)
            except ValueError:
                return None
        
        return ZepixV6Alert(
            alert_type=parts[0] if len(parts) > 0 else "",
            ticker=parts[1] if len(parts) > 1 else "",
            tf=parts[2] if len(parts) > 2 else "",
            price=safe_float(parts[3]) or 0.0,
            direction=parts[4] if len(parts) > 4 else "",
            conf_level=parts[5] if len(parts) > 5 else "MODERATE",
            conf_score=int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 0,
            adx=safe_float(parts[7]) if len(parts) > 7 else None,
            adx_strength=parts[8] if len(parts) > 8 else "NONE",
            sl=safe_float(parts[9]) if len(parts) > 9 else None,
            tp1=safe_float(parts[10]) if len(parts) > 10 else None,
            tp2=safe_float(parts[11]) if len(parts) > 11 else None,
            tp3=safe_float(parts[12]) if len(parts) > 12 else None,
            alignment=parts[13] if len(parts) > 13 else "0/0",
            tl_status=parts[14] if len(parts) > 14 else "TL_OK"
        )
    
    @classmethod
    def parse_trend_pulse(cls, payload: str) -> TrendPulseAlert:
        """
        Parse Trend Pulse alert payload.
        
        Format: TREND_PULSE|SYMBOL|TF|BULL_COUNT|BEAR_COUNT|CHANGES|STATE
        Example: TREND_PULSE|XAUUSD|15|5|1|1M,5M|TRENDING_BULLISH
        """
        parts = payload.split(cls.DELIMITER)
        
        if len(parts) < 5:
            raise ValueError(f"Invalid Trend Pulse payload: expected at least 5 fields, got {len(parts)}")
        
        return TrendPulseAlert(
            alert_type=parts[0] if len(parts) > 0 else "TREND_PULSE",
            symbol=parts[1] if len(parts) > 1 else "",
            tf=parts[2] if len(parts) > 2 else "",
            bull_count=int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0,
            bear_count=int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0,
            changes=parts[5] if len(parts) > 5 else "",
            state=parts[6] if len(parts) > 6 else "UNKNOWN"
        )
    
    @classmethod
    def is_trend_pulse(cls, payload: str) -> bool:
        """Check if payload is a Trend Pulse alert."""
        return payload.startswith("TREND_PULSE")
    
    @classmethod
    def is_entry_signal(cls, payload: str) -> bool:
        """Check if payload is an entry signal."""
        return payload.startswith("BULLISH_ENTRY") or payload.startswith("BEARISH_ENTRY")
    
    @classmethod
    def is_exit_signal(cls, payload: str) -> bool:
        """Check if payload is an exit signal."""
        return payload.startswith("EXIT_")


def parse_v6_payload(payload: str) -> ZepixV6Alert:
    """Convenience function to parse V6 payload."""
    return V6AlertParser.parse_v6_payload(payload)


def parse_trend_pulse(payload: str) -> TrendPulseAlert:
    """Convenience function to parse Trend Pulse payload."""
    return V6AlertParser.parse_trend_pulse(payload)
