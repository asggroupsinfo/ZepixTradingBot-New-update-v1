"""
V6 Integration Package for V5 Hybrid Plugin Architecture.

This package provides V6 Price Action integration:
- Alert models (ZepixV6Alert, TrendPulseAlert)
- Trend Pulse Manager
- V6 Integration Engine
- Conflict Resolution
- Performance Optimization

Based on Document 16: PHASE_7_V6_INTEGRATION_PLAN.md

Version: 1.0
Date: 2026-01-12
"""

from .alert_models import (
    V6AlertType,
    V6Direction,
    V6ConfidenceLevel,
    V6ADXStrength,
    V6MarketState,
    V6TrendlineStatus,
    V6Timeframe,
    V6OrderRouting,
    ZepixV6Alert,
    TrendPulseAlert,
    V6AlertParser,
    parse_v6_payload,
    parse_trend_pulse
)

from .trend_pulse_manager import (
    MarketState,
    TrendPulseData,
    MockDatabase,
    TrendPulseManager
)

from .v6_engine import (
    V6PluginState,
    ConflictResolutionStrategy,
    V6PluginConfig,
    V6TradeResult,
    ConflictEvent,
    MockServiceAPI,
    V6ConflictResolver,
    V6PerformanceOptimizer,
    V6IntegrationEngine,
    create_v6_engine
)

__version__ = "1.0.0"

__all__ = [
    # Alert Models
    "V6AlertType",
    "V6Direction",
    "V6ConfidenceLevel",
    "V6ADXStrength",
    "V6MarketState",
    "V6TrendlineStatus",
    "V6Timeframe",
    "V6OrderRouting",
    "ZepixV6Alert",
    "TrendPulseAlert",
    "V6AlertParser",
    "parse_v6_payload",
    "parse_trend_pulse",
    
    # Trend Pulse Manager
    "MarketState",
    "TrendPulseData",
    "MockDatabase",
    "TrendPulseManager",
    
    # V6 Engine
    "V6PluginState",
    "ConflictResolutionStrategy",
    "V6PluginConfig",
    "V6TradeResult",
    "ConflictEvent",
    "MockServiceAPI",
    "V6ConflictResolver",
    "V6PerformanceOptimizer",
    "V6IntegrationEngine",
    "create_v6_engine"
]
