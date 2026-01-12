"""
V3 Combined Logic Plugin - V5 Hybrid Plugin Architecture

This plugin implements the V3 Combined Logic trading strategy.

Features:
- 12 signal types (7 entry, 2 exit, 2 info, 1 trend pulse)
- 3 logic routes (LOGIC1: 5m scalp, LOGIC2: 15m intraday, LOGIC3: 1h swing)
- Dual order system (Order A + Order B)
- Hybrid SL system (Smart SL for Order A, Fixed $10 SL for Order B)

Part of Document 01: Project Overview - Plugin System Architecture
Full implementation in Document 06: Phase 4 - V3 Plugin Migration
"""

from .plugin import CombinedV3Plugin

__all__ = ["CombinedV3Plugin"]
