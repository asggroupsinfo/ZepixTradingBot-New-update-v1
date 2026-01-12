"""
Test Data Generators for V5 Hybrid Plugin Architecture.

This module provides test data generators for:
- V3 Signal test data (12 signal types)
- V6 Alert test data (4 timeframes)
- Order test data (dual orders, single orders)
- MTF test data (4-pillar system)
- Shadow mode test data

Version: 1.0
Date: 2026-01-12
"""

import random
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta


class SignalType(Enum):
    """V3 Signal types."""
    INSTITUTIONAL_LAUNCHPAD = "Institutional_Launchpad"
    LIQUIDITY_TRAP = "Liquidity_Trap"
    MOMENTUM_IGNITION = "Momentum_Ignition"
    MITIGATION_BLOCK = "Mitigation_Block"
    GOLDEN_POCKET = "Golden_Pocket"
    SCREENER = "Screener"
    ENTRY_V3 = "entry_v3"
    EXIT_BULLISH = "Exit_Bullish"
    EXIT_BEARISH = "Exit_Bearish"
    VOLATILITY_SQUEEZE = "Volatility_Squeeze"
    SIDEWAYS_BREAKOUT = "Sideways_Breakout"
    TREND_PULSE = "Trend_Pulse"


class Direction(Enum):
    """Trade direction."""
    BUY = "BUY"
    SELL = "SELL"


class LogicRoute(Enum):
    """V3 Logic routes."""
    LOGIC1 = "LOGIC1"
    LOGIC2 = "LOGIC2"
    LOGIC3 = "LOGIC3"


class OrderRouting(Enum):
    """V6 Order routing types."""
    ORDER_A_ONLY = "ORDER_A_ONLY"
    ORDER_B_ONLY = "ORDER_B_ONLY"
    DUAL_ORDERS = "DUAL_ORDERS"


class ADXStrength(Enum):
    """ADX strength levels."""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


@dataclass
class V3SignalData:
    """V3 Signal test data."""
    signal_type: str
    tf: str
    consensus: int
    direction: str
    mtf: str
    symbol: str = "XAUUSD"
    entry_price: float = 2030.00
    sl_price: float = 2028.00
    tp1_price: float = 2032.00
    tp2_price: float = 2035.00
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    def get_expected_route(self) -> str:
        """Get expected logic route based on signal type and timeframe."""
        if self.signal_type == "Screener":
            return "LOGIC3"
        if self.signal_type == "Golden_Pocket" and self.tf in ["60", "240"]:
            return "LOGIC3"
        
        tf_routing = {
            "5": "LOGIC1",
            "15": "LOGIC2",
            "60": "LOGIC3",
            "240": "LOGIC3"
        }
        return tf_routing.get(self.tf, "LOGIC2")
    
    def get_mtf_pillars(self) -> Dict[str, int]:
        """Extract MTF 4-pillar values."""
        values = [int(x) for x in self.mtf.split(",")]
        if len(values) >= 6:
            return {
                "15m": values[2],
                "1h": values[3],
                "4h": values[4],
                "1d": values[5]
            }
        return {"15m": 0, "1h": 0, "4h": 0, "1d": 0}


@dataclass
class V6AlertData:
    """V6 Alert test data."""
    timeframe: str
    direction: str
    adx: float
    confidence_score: int
    spread_pips: float
    symbol: str = "XAUUSD"
    entry_price: float = 2030.00
    sl_price: float = 2028.00
    tp1_price: float = 2032.00
    tp2_price: float = 2035.00
    trend_15m_aligned: bool = True
    trend_4h_aligned: bool = True
    trend_1d_aligned: bool = True
    market_state: str = "TRENDING_BULLISH"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    def get_expected_routing(self) -> str:
        """Get expected order routing based on timeframe."""
        routing_map = {
            "1m": "ORDER_B_ONLY",
            "5m": "DUAL_ORDERS",
            "15m": "ORDER_A_ONLY",
            "1h": "ORDER_A_ONLY"
        }
        return routing_map.get(self.timeframe, "ORDER_A_ONLY")
    
    def should_allow_entry(self) -> bool:
        """Check if entry should be allowed based on conditions."""
        if self.timeframe == "1m":
            return self.adx >= 20 and self.confidence_score >= 80 and self.spread_pips <= 2.0
        elif self.timeframe == "5m":
            return self.adx >= 25 and self.confidence_score >= 70 and self.trend_15m_aligned
        elif self.timeframe == "15m":
            return self.confidence_score >= 65
        elif self.timeframe == "1h":
            return self.confidence_score >= 60 and self.trend_4h_aligned and self.trend_1d_aligned
        return False


@dataclass
class DualOrderData:
    """Dual order test data."""
    symbol: str
    direction: str
    entry_price: float
    sl_price_v3: float
    tp1_price: float
    tp2_price: float
    total_lot: float
    order_a_lot: float = 0.0
    order_b_lot: float = 0.0
    order_a_sl: float = 0.0
    order_b_sl: float = 0.0
    order_a_tp: float = 0.0
    order_b_tp: float = 0.0
    
    def __post_init__(self):
        """Calculate derived values."""
        self.order_a_lot = self.total_lot / 2
        self.order_b_lot = self.total_lot / 2
        self.order_a_sl = self.sl_price_v3
        self.order_b_sl = self._calculate_fixed_sl()
        self.order_a_tp = self.tp2_price
        self.order_b_tp = self.tp1_price
    
    def _calculate_fixed_sl(self) -> float:
        """Calculate fixed $10 SL for Order B."""
        if self.direction == "BUY":
            return self.entry_price - (10.0 / self.entry_price * 100)
        else:
            return self.entry_price + (10.0 / self.entry_price * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TrendPulseData:
    """Trend Pulse test data."""
    bull_count: int
    bear_count: int
    market_state: str
    changes: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def is_aligned_for_direction(self, direction: str) -> bool:
        """Check if pulse is aligned for given direction."""
        if direction == "BUY":
            return self.bull_count > self.bear_count
        else:
            return self.bear_count > self.bull_count


class V3SignalGenerator:
    """Generator for V3 signal test data."""
    
    SIGNAL_TYPES = [e.value for e in SignalType]
    TIMEFRAMES = ["5", "15", "60", "240"]
    
    @classmethod
    def generate_signal(
        cls,
        signal_type: Optional[str] = None,
        timeframe: Optional[str] = None,
        direction: Optional[str] = None,
        consensus: Optional[int] = None,
        mtf_bullish: bool = True
    ) -> V3SignalData:
        """Generate a V3 signal with specified or random values."""
        signal_type = signal_type or random.choice(cls.SIGNAL_TYPES)
        timeframe = timeframe or random.choice(cls.TIMEFRAMES)
        direction = direction or random.choice(["BUY", "SELL"])
        consensus = consensus if consensus is not None else random.randint(0, 9)
        
        if mtf_bullish:
            mtf = "1,1,1,1,1,-1"
        else:
            mtf = "-1,-1,-1,-1,-1,1"
        
        base_price = 2030.00
        if direction == "BUY":
            entry = base_price
            sl = base_price - 2.0
            tp1 = base_price + 2.0
            tp2 = base_price + 5.0
        else:
            entry = base_price
            sl = base_price + 2.0
            tp1 = base_price - 2.0
            tp2 = base_price - 5.0
        
        return V3SignalData(
            signal_type=signal_type,
            tf=timeframe,
            consensus=consensus,
            direction=direction,
            mtf=mtf,
            entry_price=entry,
            sl_price=sl,
            tp1_price=tp1,
            tp2_price=tp2
        )
    
    @classmethod
    def generate_all_signal_types(cls, direction: str = "BUY") -> List[V3SignalData]:
        """Generate one signal for each signal type."""
        return [
            cls.generate_signal(signal_type=st, direction=direction)
            for st in cls.SIGNAL_TYPES
        ]
    
    @classmethod
    def generate_routing_test_data(cls) -> List[Tuple[V3SignalData, str]]:
        """Generate test data for routing matrix tests."""
        test_cases = []
        
        test_cases.append((
            cls.generate_signal(signal_type="Screener", timeframe="5"),
            "LOGIC3"
        ))
        
        test_cases.append((
            cls.generate_signal(signal_type="Golden_Pocket", timeframe="60"),
            "LOGIC3"
        ))
        
        test_cases.append((
            cls.generate_signal(signal_type="Golden_Pocket", timeframe="240"),
            "LOGIC3"
        ))
        
        test_cases.append((
            cls.generate_signal(signal_type="Institutional_Launchpad", timeframe="5"),
            "LOGIC1"
        ))
        
        test_cases.append((
            cls.generate_signal(signal_type="Institutional_Launchpad", timeframe="15"),
            "LOGIC2"
        ))
        
        test_cases.append((
            cls.generate_signal(signal_type="Institutional_Launchpad", timeframe="60"),
            "LOGIC3"
        ))
        
        return test_cases
    
    @classmethod
    def generate_mtf_test_data(cls) -> List[Tuple[str, Dict[str, int]]]:
        """Generate MTF extraction test data."""
        return [
            ("1,1,1,1,1,-1", {"15m": 1, "1h": 1, "4h": 1, "1d": -1}),
            ("-1,-1,-1,-1,-1,1", {"15m": -1, "1h": -1, "4h": -1, "1d": 1}),
            ("1,-1,1,1,-1,1", {"15m": 1, "1h": 1, "4h": -1, "1d": 1}),
            ("0,0,0,0,0,0", {"15m": 0, "1h": 0, "4h": 0, "1d": 0}),
        ]
    
    @classmethod
    def generate_consensus_test_data(cls) -> List[Tuple[int, float]]:
        """Generate consensus to multiplier mapping test data."""
        return [
            (0, 0.2), (1, 0.3), (2, 0.4), (3, 0.5),
            (4, 0.6), (5, 0.7), (6, 0.8),
            (7, 0.9), (8, 0.95), (9, 1.0),
        ]
    
    @classmethod
    def generate_trend_bypass_test_data(cls) -> List[Tuple[V3SignalData, bool, bool]]:
        """Generate trend bypass test data: (signal, mtf_aligned, should_enter)."""
        return [
            (cls.generate_signal(signal_type="entry_v3"), False, True),
            (cls.generate_signal(signal_type="entry_v3"), True, True),
            (cls.generate_signal(signal_type="Institutional_Launchpad"), False, False),
            (cls.generate_signal(signal_type="Institutional_Launchpad"), True, True),
        ]


class V6AlertGenerator:
    """Generator for V6 alert test data."""
    
    TIMEFRAMES = ["1m", "5m", "15m", "1h"]
    
    @classmethod
    def generate_alert(
        cls,
        timeframe: Optional[str] = None,
        direction: Optional[str] = None,
        adx: Optional[float] = None,
        confidence: Optional[int] = None,
        spread: Optional[float] = None
    ) -> V6AlertData:
        """Generate a V6 alert with specified or random values."""
        timeframe = timeframe or random.choice(cls.TIMEFRAMES)
        direction = direction or random.choice(["BUY", "SELL"])
        
        adx_defaults = {"1m": 22, "5m": 28, "15m": 24, "1h": 26}
        confidence_defaults = {"1m": 85, "5m": 75, "15m": 70, "1h": 65}
        
        adx = adx if adx is not None else adx_defaults.get(timeframe, 25)
        confidence = confidence if confidence is not None else confidence_defaults.get(timeframe, 70)
        spread = spread if spread is not None else 1.5
        
        base_price = 2030.00
        if direction == "BUY":
            entry = base_price
            sl = base_price - 2.0
            tp1 = base_price + 2.0
            tp2 = base_price + 5.0
            market_state = "TRENDING_BULLISH"
        else:
            entry = base_price
            sl = base_price + 2.0
            tp1 = base_price - 2.0
            tp2 = base_price - 5.0
            market_state = "TRENDING_BEARISH"
        
        return V6AlertData(
            timeframe=timeframe,
            direction=direction,
            adx=adx,
            confidence_score=confidence,
            spread_pips=spread,
            entry_price=entry,
            sl_price=sl,
            tp1_price=tp1,
            tp2_price=tp2,
            market_state=market_state
        )
    
    @classmethod
    def generate_1m_test_data(cls) -> List[Tuple[V6AlertData, bool, bool]]:
        """Generate 1M test data: (alert, order_a_expected, order_b_expected)."""
        return [
            (cls.generate_alert(timeframe="1m", adx=22, confidence=85, spread=1.5), False, True),
            (cls.generate_alert(timeframe="1m", adx=18, confidence=85, spread=1.5), False, False),
            (cls.generate_alert(timeframe="1m", adx=22, confidence=75, spread=1.5), False, False),
            (cls.generate_alert(timeframe="1m", adx=22, confidence=85, spread=2.5), False, False),
        ]
    
    @classmethod
    def generate_5m_test_data(cls) -> List[Tuple[V6AlertData, bool, bool]]:
        """Generate 5M test data: (alert, order_a_expected, order_b_expected)."""
        alert_valid = cls.generate_alert(timeframe="5m", adx=28, confidence=75)
        alert_valid.trend_15m_aligned = True
        
        alert_low_adx = cls.generate_alert(timeframe="5m", adx=22, confidence=75)
        alert_low_adx.trend_15m_aligned = True
        
        alert_no_trend = cls.generate_alert(timeframe="5m", adx=28, confidence=75)
        alert_no_trend.trend_15m_aligned = False
        
        return [
            (alert_valid, True, True),
            (alert_low_adx, False, False),
            (alert_no_trend, False, False),
        ]
    
    @classmethod
    def generate_15m_test_data(cls) -> List[Tuple[V6AlertData, bool, bool]]:
        """Generate 15M test data: (alert, order_a_expected, order_b_expected)."""
        return [
            (cls.generate_alert(timeframe="15m", confidence=70), True, False),
            (cls.generate_alert(timeframe="15m", confidence=60), False, False),
        ]
    
    @classmethod
    def generate_1h_test_data(cls) -> List[Tuple[V6AlertData, bool, bool]]:
        """Generate 1H test data: (alert, order_a_expected, order_b_expected)."""
        alert_valid = cls.generate_alert(timeframe="1h", confidence=65)
        alert_valid.trend_4h_aligned = True
        alert_valid.trend_1d_aligned = True
        
        alert_no_4h = cls.generate_alert(timeframe="1h", confidence=65)
        alert_no_4h.trend_4h_aligned = False
        alert_no_4h.trend_1d_aligned = True
        
        alert_no_1d = cls.generate_alert(timeframe="1h", confidence=65)
        alert_no_1d.trend_4h_aligned = True
        alert_no_1d.trend_1d_aligned = False
        
        return [
            (alert_valid, True, False),
            (alert_no_4h, False, False),
            (alert_no_1d, False, False),
        ]
    
    @classmethod
    def generate_all_timeframes(cls, direction: str = "BUY") -> List[V6AlertData]:
        """Generate one alert for each timeframe."""
        return [
            cls.generate_alert(timeframe=tf, direction=direction)
            for tf in cls.TIMEFRAMES
        ]


class DualOrderGenerator:
    """Generator for dual order test data."""
    
    @classmethod
    def generate_v3_dual_order(
        cls,
        direction: str = "BUY",
        total_lot: float = 0.10
    ) -> DualOrderData:
        """Generate V3 dual order test data."""
        base_price = 2030.00
        
        if direction == "BUY":
            entry = base_price
            sl = base_price - 2.0
            tp1 = base_price + 2.0
            tp2 = base_price + 5.0
        else:
            entry = base_price
            sl = base_price + 2.0
            tp1 = base_price - 2.0
            tp2 = base_price - 5.0
        
        return DualOrderData(
            symbol="XAUUSD",
            direction=direction,
            entry_price=entry,
            sl_price_v3=sl,
            tp1_price=tp1,
            tp2_price=tp2,
            total_lot=total_lot
        )
    
    @classmethod
    def generate_position_sizing_test_data(cls) -> List[Tuple[float, int, str, float]]:
        """Generate position sizing test data: (base_lot, consensus, logic_route, expected_lot)."""
        return [
            (0.10, 8, "LOGIC1", 0.10 * 0.95 * 1.25),
            (0.10, 5, "LOGIC2", 0.10 * 0.7 * 1.0),
            (0.10, 3, "LOGIC3", 0.10 * 0.5 * 0.625),
        ]


class TrendPulseGenerator:
    """Generator for Trend Pulse test data."""
    
    MARKET_STATES = [
        "TRENDING_BULLISH",
        "TRENDING_BEARISH",
        "SIDEWAYS",
        "VOLATILE"
    ]
    
    @classmethod
    def generate_pulse(
        cls,
        bull_count: Optional[int] = None,
        bear_count: Optional[int] = None,
        market_state: Optional[str] = None
    ) -> TrendPulseData:
        """Generate Trend Pulse test data."""
        bull_count = bull_count if bull_count is not None else random.randint(0, 7)
        bear_count = bear_count if bear_count is not None else random.randint(0, 7)
        
        if market_state is None:
            if bull_count > bear_count:
                market_state = "TRENDING_BULLISH"
            elif bear_count > bull_count:
                market_state = "TRENDING_BEARISH"
            else:
                market_state = "SIDEWAYS"
        
        return TrendPulseData(
            bull_count=bull_count,
            bear_count=bear_count,
            market_state=market_state
        )
    
    @classmethod
    def generate_alignment_test_data(cls) -> List[Tuple[TrendPulseData, str, bool]]:
        """Generate pulse alignment test data: (pulse, direction, expected_aligned)."""
        return [
            (cls.generate_pulse(bull_count=5, bear_count=2), "BUY", True),
            (cls.generate_pulse(bull_count=5, bear_count=2), "SELL", False),
            (cls.generate_pulse(bull_count=2, bear_count=5), "BUY", False),
            (cls.generate_pulse(bull_count=2, bear_count=5), "SELL", True),
            (cls.generate_pulse(bull_count=3, bear_count=3), "BUY", False),
            (cls.generate_pulse(bull_count=3, bear_count=3), "SELL", False),
        ]


class ShadowModeDataGenerator:
    """Generator for shadow mode test data."""
    
    @classmethod
    def generate_shadow_session(
        cls,
        duration_hours: int = 72,
        plugin_type: str = "v3"
    ) -> Dict[str, Any]:
        """Generate shadow mode session data."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        return {
            "session_id": f"shadow_{plugin_type}_{int(start_time.timestamp())}",
            "plugin_type": plugin_type,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_hours": duration_hours,
            "signals_logged": 0,
            "hypothetical_orders": [],
            "hypothetical_pnl": 0.0,
            "real_orders_placed": 0
        }
    
    @classmethod
    def generate_hypothetical_order(
        cls,
        signal_data: V3SignalData,
        order_type: str = "A"
    ) -> Dict[str, Any]:
        """Generate hypothetical order for shadow mode."""
        return {
            "order_id": f"shadow_{int(datetime.now().timestamp())}",
            "order_type": order_type,
            "symbol": signal_data.symbol,
            "direction": signal_data.direction,
            "entry_price": signal_data.entry_price,
            "sl_price": signal_data.sl_price,
            "tp_price": signal_data.tp1_price if order_type == "B" else signal_data.tp2_price,
            "lot_size": 0.05,
            "status": "HYPOTHETICAL",
            "timestamp": datetime.now().isoformat()
        }


class IntegrationTestDataGenerator:
    """Generator for integration test data."""
    
    @classmethod
    def generate_v3_v6_simultaneous_data(cls) -> Dict[str, Any]:
        """Generate data for V3 + V6 simultaneous execution test."""
        v3_signal = V3SignalGenerator.generate_signal(
            signal_type="Institutional_Launchpad",
            timeframe="5",
            direction="BUY"
        )
        
        v6_alert = V6AlertGenerator.generate_alert(
            timeframe="1m",
            direction="BUY"
        )
        
        return {
            "v3_signal": v3_signal.to_dict(),
            "v6_alert": v6_alert.to_dict(),
            "expected_v3_plugin": "combined_v3",
            "expected_v6_plugin": "price_action_1m",
            "expected_isolation": True
        }
    
    @classmethod
    def generate_service_api_test_data(cls) -> Dict[str, Any]:
        """Generate data for ServiceAPI integration tests."""
        return {
            "order_execution": {
                "place_dual_orders_v3": V3SignalGenerator.generate_signal().to_dict(),
                "place_single_order_a": V6AlertGenerator.generate_alert(timeframe="15m").to_dict(),
                "place_single_order_b": V6AlertGenerator.generate_alert(timeframe="1m").to_dict(),
            },
            "risk_management": {
                "calculate_lot_size": {"balance": 10000, "risk_percent": 1.0},
                "check_daily_limit": {"plugin_id": "combined_v3"},
            },
            "trend_monitor": {
                "get_mtf_trends": {"symbol": "XAUUSD"},
                "validate_v3_trend_alignment": {"direction": "BUY", "pillars": {"15m": 1, "1h": 1, "4h": 1, "1d": -1}},
            }
        }
