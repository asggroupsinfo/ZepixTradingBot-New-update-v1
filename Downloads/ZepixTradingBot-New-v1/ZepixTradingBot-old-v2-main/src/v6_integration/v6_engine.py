"""
V6 Integration Engine for V5 Hybrid Plugin Architecture.

This module provides the main V6 integration engine:
- V6 plugin management and routing
- Conflict resolution between plugins
- Performance optimization for high-frequency checks
- System-wide integration with V3

Based on Document 16: PHASE_7_V6_INTEGRATION_PLAN.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from .alert_models import ZepixV6Alert, TrendPulseAlert, V6OrderRouting, V6AlertParser
from .trend_pulse_manager import TrendPulseManager, MarketState


logger = logging.getLogger(__name__)


class V6PluginState(Enum):
    """V6 plugin state."""
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    SHADOW_MODE = "SHADOW_MODE"


class ConflictResolutionStrategy(Enum):
    """Strategy for resolving conflicts between plugins."""
    FIRST_WINS = "FIRST_WINS"
    HIGHEST_CONFIDENCE = "HIGHEST_CONFIDENCE"
    TIMEFRAME_PRIORITY = "TIMEFRAME_PRIORITY"
    QUEUE_ALL = "QUEUE_ALL"


@dataclass
class V6PluginConfig:
    """Configuration for a V6 plugin."""
    plugin_id: str
    timeframe: str
    enabled: bool = True
    min_adx: float = 20.0
    min_confidence: int = 70
    max_spread_pips: float = 3.0
    risk_multiplier: float = 1.0
    order_routing: V6OrderRouting = V6OrderRouting.DUAL_ORDERS
    require_pulse_alignment: bool = False
    require_market_state_check: bool = False
    state: V6PluginState = V6PluginState.ENABLED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "timeframe": self.timeframe,
            "enabled": self.enabled,
            "min_adx": self.min_adx,
            "min_confidence": self.min_confidence,
            "max_spread_pips": self.max_spread_pips,
            "risk_multiplier": self.risk_multiplier,
            "order_routing": self.order_routing.value,
            "require_pulse_alignment": self.require_pulse_alignment,
            "require_market_state_check": self.require_market_state_check,
            "state": self.state.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'V6PluginConfig':
        """Create from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", ""),
            timeframe=data.get("timeframe", ""),
            enabled=data.get("enabled", True),
            min_adx=float(data.get("min_adx", 20.0)),
            min_confidence=int(data.get("min_confidence", 70)),
            max_spread_pips=float(data.get("max_spread_pips", 3.0)),
            risk_multiplier=float(data.get("risk_multiplier", 1.0)),
            order_routing=V6OrderRouting(data.get("order_routing", "DUAL_ORDERS")),
            require_pulse_alignment=data.get("require_pulse_alignment", False),
            require_market_state_check=data.get("require_market_state_check", False),
            state=V6PluginState(data.get("state", "ENABLED"))
        )


@dataclass
class V6TradeResult:
    """Result of a V6 trade execution."""
    success: bool
    plugin_id: str
    symbol: str
    direction: str
    order_routing: V6OrderRouting
    ticket_a: Optional[int] = None
    ticket_b: Optional[int] = None
    lot_size: float = 0.0
    entry_price: float = 0.0
    sl_price: Optional[float] = None
    tp_price: Optional[float] = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "plugin_id": self.plugin_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "order_routing": self.order_routing.value,
            "ticket_a": self.ticket_a,
            "ticket_b": self.ticket_b,
            "lot_size": self.lot_size,
            "entry_price": self.entry_price,
            "sl_price": self.sl_price,
            "tp_price": self.tp_price,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ConflictEvent:
    """Record of a conflict between plugins."""
    timestamp: datetime
    symbol: str
    plugins_involved: List[str]
    resolution: str
    winning_plugin: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "plugins_involved": self.plugins_involved,
            "resolution": self.resolution,
            "winning_plugin": self.winning_plugin
        }


class MockServiceAPI:
    """Mock ServiceAPI for V6 integration."""
    
    def __init__(self):
        """Initialize mock service API."""
        self._next_ticket = 10000
        self._orders: Dict[int, Dict[str, Any]] = {}
    
    def _get_next_ticket(self) -> int:
        """Get next ticket number."""
        ticket = self._next_ticket
        self._next_ticket += 1
        return ticket
    
    async def place_single_order_a(self, plugin_id: str, symbol: str, direction: str,
                                   lot_size: float, sl_price: Optional[float],
                                   tp_price: Optional[float], comment: str = "") -> int:
        """Place Order A only (for 15M/1H plugins)."""
        ticket = self._get_next_ticket()
        self._orders[ticket] = {
            "ticket": ticket,
            "plugin_id": plugin_id,
            "symbol": symbol,
            "direction": direction,
            "lot_size": lot_size,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "order_type": "ORDER_A",
            "comment": comment
        }
        logger.info(f"{plugin_id}: ORDER A placed #{ticket}")
        return ticket
    
    async def place_single_order_b(self, plugin_id: str, symbol: str, direction: str,
                                   lot_size: float, sl_price: Optional[float],
                                   tp_price: Optional[float], comment: str = "") -> int:
        """Place Order B only (for 1M plugin)."""
        ticket = self._get_next_ticket()
        self._orders[ticket] = {
            "ticket": ticket,
            "plugin_id": plugin_id,
            "symbol": symbol,
            "direction": direction,
            "lot_size": lot_size,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "order_type": "ORDER_B",
            "comment": comment
        }
        logger.info(f"{plugin_id}: ORDER B placed #{ticket}")
        return ticket
    
    async def place_dual_orders(self, plugin_id: str, symbol: str, direction: str,
                                lot_size: float, order_a_sl: Optional[float],
                                order_a_tp: Optional[float], order_b_sl: Optional[float],
                                order_b_tp: Optional[float]) -> Tuple[int, int]:
        """Place both Order A and Order B (for 5M plugin)."""
        lot_a = lot_size * 0.5
        lot_b = lot_size * 0.5
        
        ticket_a = await self.place_single_order_a(
            plugin_id, symbol, direction, lot_a, order_a_sl, order_a_tp,
            f"{plugin_id}_dual_a"
        )
        ticket_b = await self.place_single_order_b(
            plugin_id, symbol, direction, lot_b, order_b_sl, order_b_tp,
            f"{plugin_id}_dual_b"
        )
        
        return ticket_a, ticket_b
    
    async def get_current_spread(self, symbol: str) -> float:
        """Get current spread for symbol (mock)."""
        spreads = {
            "XAUUSD": 1.5,
            "EURUSD": 0.8,
            "GBPUSD": 1.2,
            "USDJPY": 0.9
        }
        return spreads.get(symbol, 2.0)
    
    async def calculate_lot_size(self, symbol: str, risk_percentage: float,
                                 stop_loss_pips: float) -> float:
        """Calculate lot size based on risk (mock)."""
        base_lot = 0.1
        return base_lot * (risk_percentage / 1.0)
    
    def get_orders(self) -> Dict[int, Dict[str, Any]]:
        """Get all orders."""
        return self._orders.copy()


class V6ConflictResolver:
    """Resolver for conflicts between V6 plugins."""
    
    TIMEFRAME_PRIORITY = ["60", "15", "5", "1"]
    
    def __init__(self, strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.TIMEFRAME_PRIORITY):
        """Initialize conflict resolver."""
        self.strategy = strategy
        self.conflict_history: List[ConflictEvent] = []
    
    def resolve(self, alerts: List[ZepixV6Alert], configs: Dict[str, V6PluginConfig]) -> Optional[ZepixV6Alert]:
        """
        Resolve conflict between multiple alerts.
        
        Args:
            alerts: List of conflicting alerts
            configs: Plugin configurations
        
        Returns:
            Winning alert or None
        """
        if not alerts:
            return None
        
        if len(alerts) == 1:
            return alerts[0]
        
        plugins_involved = [f"price_action_{a.tf}m" for a in alerts]
        
        if self.strategy == ConflictResolutionStrategy.FIRST_WINS:
            winner = alerts[0]
        elif self.strategy == ConflictResolutionStrategy.HIGHEST_CONFIDENCE:
            winner = max(alerts, key=lambda a: a.conf_score)
        elif self.strategy == ConflictResolutionStrategy.TIMEFRAME_PRIORITY:
            winner = self._resolve_by_timeframe(alerts)
        else:
            winner = alerts[0]
        
        self.conflict_history.append(ConflictEvent(
            timestamp=datetime.now(),
            symbol=winner.ticker,
            plugins_involved=plugins_involved,
            resolution=self.strategy.value,
            winning_plugin=f"price_action_{winner.tf}m"
        ))
        
        logger.info(f"Conflict resolved: {plugins_involved} -> price_action_{winner.tf}m")
        
        return winner
    
    def _resolve_by_timeframe(self, alerts: List[ZepixV6Alert]) -> ZepixV6Alert:
        """Resolve by timeframe priority (higher TF wins)."""
        def get_priority(alert: ZepixV6Alert) -> int:
            try:
                return self.TIMEFRAME_PRIORITY.index(alert.tf)
            except ValueError:
                return len(self.TIMEFRAME_PRIORITY)
        
        return min(alerts, key=get_priority)
    
    def get_conflict_history(self) -> List[Dict[str, Any]]:
        """Get conflict history."""
        return [c.to_dict() for c in self.conflict_history]
    
    def clear_history(self) -> None:
        """Clear conflict history."""
        self.conflict_history.clear()


class V6PerformanceOptimizer:
    """Performance optimizer for V6 high-frequency checks."""
    
    def __init__(self):
        """Initialize performance optimizer."""
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl_ms: int = 100
        self._metrics: Dict[str, int] = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_checks": 0
        }
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if still valid."""
        self._metrics["total_checks"] += 1
        
        if key not in self._cache:
            self._metrics["cache_misses"] += 1
            return None
        
        timestamp = self._cache_timestamps.get(key)
        if timestamp:
            elapsed_ms = (datetime.now() - timestamp).total_seconds() * 1000
            if elapsed_ms < self._cache_ttl_ms:
                self._metrics["cache_hits"] += 1
                return self._cache[key]
        
        self._metrics["cache_misses"] += 1
        return None
    
    def set_cached(self, key: str, value: Any) -> None:
        """Set cached value."""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def invalidate(self, key: str) -> None:
        """Invalidate cache entry."""
        self._cache.pop(key, None)
        self._cache_timestamps.pop(key, None)
    
    def clear_cache(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        total = self._metrics["total_checks"]
        hit_rate = self._metrics["cache_hits"] / total if total > 0 else 0
        
        return {
            **self._metrics,
            "hit_rate": hit_rate,
            "cache_size": len(self._cache)
        }


class V6IntegrationEngine:
    """
    Main V6 Integration Engine.
    Manages V6 plugins and coordinates with V3 system.
    """
    
    DEFAULT_CONFIGS = {
        "1": V6PluginConfig(
            plugin_id="price_action_1m",
            timeframe="1",
            min_adx=20.0,
            min_confidence=80,
            max_spread_pips=2.0,
            risk_multiplier=0.5,
            order_routing=V6OrderRouting.ORDER_B_ONLY
        ),
        "5": V6PluginConfig(
            plugin_id="price_action_5m",
            timeframe="5",
            min_adx=25.0,
            min_confidence=70,
            max_spread_pips=3.0,
            risk_multiplier=1.0,
            order_routing=V6OrderRouting.DUAL_ORDERS,
            require_pulse_alignment=True
        ),
        "15": V6PluginConfig(
            plugin_id="price_action_15m",
            timeframe="15",
            min_adx=20.0,
            min_confidence=70,
            max_spread_pips=4.0,
            risk_multiplier=1.0,
            order_routing=V6OrderRouting.ORDER_A_ONLY,
            require_market_state_check=True,
            require_pulse_alignment=True
        ),
        "60": V6PluginConfig(
            plugin_id="price_action_1h",
            timeframe="60",
            min_adx=20.0,
            min_confidence=60,
            max_spread_pips=5.0,
            risk_multiplier=0.625,
            order_routing=V6OrderRouting.ORDER_A_ONLY,
            require_market_state_check=True
        )
    }
    
    def __init__(self, service_api: Optional[MockServiceAPI] = None,
                 trend_pulse_manager: Optional[TrendPulseManager] = None):
        """Initialize V6 Integration Engine."""
        self.service_api = service_api or MockServiceAPI()
        self.trend_pulse = trend_pulse_manager or TrendPulseManager()
        self.conflict_resolver = V6ConflictResolver()
        self.performance_optimizer = V6PerformanceOptimizer()
        
        self.plugin_configs: Dict[str, V6PluginConfig] = self.DEFAULT_CONFIGS.copy()
        self.enabled = True
        self.shadow_mode = False
        
        self._trade_history: List[V6TradeResult] = []
        self._pending_alerts: Dict[str, List[ZepixV6Alert]] = {}
    
    def configure_plugin(self, timeframe: str, config: V6PluginConfig) -> None:
        """Configure a V6 plugin."""
        self.plugin_configs[timeframe] = config
        logger.info(f"V6 Plugin configured: {config.plugin_id}")
    
    def enable_plugin(self, timeframe: str) -> None:
        """Enable a V6 plugin."""
        if timeframe in self.plugin_configs:
            self.plugin_configs[timeframe].enabled = True
            self.plugin_configs[timeframe].state = V6PluginState.ENABLED
            logger.info(f"V6 Plugin enabled: price_action_{timeframe}m")
    
    def disable_plugin(self, timeframe: str) -> None:
        """Disable a V6 plugin."""
        if timeframe in self.plugin_configs:
            self.plugin_configs[timeframe].enabled = False
            self.plugin_configs[timeframe].state = V6PluginState.DISABLED
            logger.info(f"V6 Plugin disabled: price_action_{timeframe}m")
    
    def set_shadow_mode(self, timeframe: str, enabled: bool = True) -> None:
        """Set shadow mode for a plugin."""
        if timeframe in self.plugin_configs:
            if enabled:
                self.plugin_configs[timeframe].state = V6PluginState.SHADOW_MODE
            else:
                self.plugin_configs[timeframe].state = V6PluginState.ENABLED
            logger.info(f"V6 Plugin shadow mode: price_action_{timeframe}m = {enabled}")
    
    async def process_alert(self, payload: str) -> Optional[V6TradeResult]:
        """
        Process a V6 alert payload.
        
        Args:
            payload: Raw alert payload string
        
        Returns:
            V6TradeResult or None
        """
        if V6AlertParser.is_trend_pulse(payload):
            pulse = V6AlertParser.parse_trend_pulse(payload)
            self.trend_pulse.update_pulse_from_alert(pulse)
            return None
        
        if V6AlertParser.is_entry_signal(payload):
            alert = V6AlertParser.parse_v6_payload(payload)
            return await self.execute_entry(alert)
        
        return None
    
    async def execute_entry(self, alert: ZepixV6Alert) -> V6TradeResult:
        """
        Execute V6 entry based on alert.
        
        Args:
            alert: ZepixV6Alert object
        
        Returns:
            V6TradeResult
        """
        config = self.plugin_configs.get(alert.tf)
        
        if not config or not config.enabled:
            return V6TradeResult(
                success=False,
                plugin_id=f"price_action_{alert.tf}m",
                symbol=alert.ticker,
                direction=alert.direction,
                order_routing=alert.get_order_routing(),
                message=f"Plugin for {alert.tf}m not enabled"
            )
        
        if config.state == V6PluginState.SHADOW_MODE:
            logger.info(f"SHADOW MODE: Would execute {alert.ticker} {alert.direction} on {alert.tf}m")
            return V6TradeResult(
                success=True,
                plugin_id=config.plugin_id,
                symbol=alert.ticker,
                direction=alert.direction,
                order_routing=config.order_routing,
                message="Shadow mode - no actual trade"
            )
        
        validation_result = await self._validate_entry(alert, config)
        if not validation_result[0]:
            return V6TradeResult(
                success=False,
                plugin_id=config.plugin_id,
                symbol=alert.ticker,
                direction=alert.direction,
                order_routing=config.order_routing,
                message=validation_result[1]
            )
        
        return await self._execute_order(alert, config)
    
    async def _validate_entry(self, alert: ZepixV6Alert, config: V6PluginConfig) -> Tuple[bool, str]:
        """Validate entry conditions."""
        if alert.adx is not None and alert.adx < config.min_adx:
            return False, f"ADX {alert.adx} < {config.min_adx}"
        
        if alert.conf_score < config.min_confidence:
            return False, f"Confidence {alert.conf_score} < {config.min_confidence}"
        
        spread = await self.service_api.get_current_spread(alert.ticker)
        if spread > config.max_spread_pips:
            return False, f"Spread {spread} > {config.max_spread_pips}"
        
        if config.require_pulse_alignment:
            if not self.trend_pulse.check_pulse_alignment(alert.ticker, alert.direction):
                return False, "Pulse alignment check failed"
        
        if config.require_market_state_check:
            market_state = self.trend_pulse.get_market_state(alert.ticker)
            if market_state == MarketState.SIDEWAYS:
                return False, "Market is sideways"
            if alert.direction == "BUY" and market_state == MarketState.TRENDING_BEARISH:
                return False, "BUY signal in bearish market"
            if alert.direction == "SELL" and market_state == MarketState.TRENDING_BULLISH:
                return False, "SELL signal in bullish market"
        
        return True, "Validation passed"
    
    async def _execute_order(self, alert: ZepixV6Alert, config: V6PluginConfig) -> V6TradeResult:
        """Execute order based on routing type."""
        lot_size = await self.service_api.calculate_lot_size(
            alert.ticker, 1.0, self._calculate_sl_pips(alert)
        )
        lot_size *= config.risk_multiplier
        
        result = V6TradeResult(
            success=True,
            plugin_id=config.plugin_id,
            symbol=alert.ticker,
            direction=alert.direction,
            order_routing=config.order_routing,
            lot_size=lot_size,
            entry_price=alert.price,
            sl_price=alert.sl
        )
        
        if config.order_routing == V6OrderRouting.ORDER_A_ONLY:
            ticket = await self.service_api.place_single_order_a(
                config.plugin_id, alert.ticker, alert.direction,
                lot_size, alert.sl, alert.tp2, f"{config.plugin_id}_entry"
            )
            result.ticket_a = ticket
            result.tp_price = alert.tp2
            result.message = f"ORDER A placed #{ticket}"
        
        elif config.order_routing == V6OrderRouting.ORDER_B_ONLY:
            ticket = await self.service_api.place_single_order_b(
                config.plugin_id, alert.ticker, alert.direction,
                lot_size, alert.sl, alert.tp1, f"{config.plugin_id}_entry"
            )
            result.ticket_b = ticket
            result.tp_price = alert.tp1
            result.message = f"ORDER B placed #{ticket}"
        
        elif config.order_routing == V6OrderRouting.DUAL_ORDERS:
            ticket_a, ticket_b = await self.service_api.place_dual_orders(
                config.plugin_id, alert.ticker, alert.direction,
                lot_size, alert.sl, alert.tp2, alert.sl, alert.tp1
            )
            result.ticket_a = ticket_a
            result.ticket_b = ticket_b
            result.message = f"DUAL ORDERS placed #{ticket_a}, #{ticket_b}"
        
        self._trade_history.append(result)
        logger.info(f"V6 {alert.tf}m Entry: {alert.ticker} {alert.direction} - {result.message}")
        
        return result
    
    def _calculate_sl_pips(self, alert: ZepixV6Alert) -> float:
        """Calculate SL in pips."""
        if alert.sl is None:
            return 25.0
        return abs(alert.price - alert.sl) * 10
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history."""
        return [t.to_dict() for t in self._trade_history]
    
    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all plugins."""
        return {
            tf: config.to_dict()
            for tf, config in self.plugin_configs.items()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        return {
            "enabled": self.enabled,
            "shadow_mode": self.shadow_mode,
            "plugins": self.get_plugin_status(),
            "trade_count": len(self._trade_history),
            "conflict_count": len(self.conflict_resolver.conflict_history),
            "performance": self.performance_optimizer.get_metrics()
        }


def create_v6_engine(service_api: Optional[MockServiceAPI] = None) -> V6IntegrationEngine:
    """Factory function to create V6 Integration Engine."""
    return V6IntegrationEngine(service_api=service_api)
