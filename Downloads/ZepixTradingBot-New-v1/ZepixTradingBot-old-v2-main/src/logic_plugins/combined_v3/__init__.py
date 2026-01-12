"""
V3 Combined Logic Plugin - V5 Hybrid Plugin Architecture

This plugin implements the V3 Combined Logic trading strategy with 100% backward
compatibility to existing V2 code.

Features:
- 12 signal types (7 entry, 2 exit, 2 info, 1 trend pulse)
- 3 logic routes (LOGIC1: 5m scalp, LOGIC2: 15m intraday, LOGIC3: 1h swing)
- Dual order system (Order A + Order B)
- Hybrid SL system (Smart SL for Order A, Fixed $10 SL for Order B)
- SL multipliers (LOGIC1: 1.0x, LOGIC2: 1.5x, LOGIC3: 2.0x)
- Order B multiplier (2.0x Order A lot size)
- MTF 4-pillar trend validation
- 2-tier routing matrix (Signal Override -> Timeframe Routing)

Part of Document 01: Project Overview - Plugin System Architecture
Full implementation in Document 06: Phase 4 - V3 Plugin Migration
"""

from .plugin import CombinedV3Plugin
from .signal_handlers import V3SignalHandlers
from .routing_logic import V3RoutingLogic
from .dual_order_manager import V3DualOrderManager
from .mtf_processor import V3MTFProcessor
from .position_sizer import V3PositionSizer

__all__ = [
    "CombinedV3Plugin",
    "V3SignalHandlers",
    "V3RoutingLogic",
    "V3DualOrderManager",
    "V3MTFProcessor",
    "V3PositionSizer"
]
