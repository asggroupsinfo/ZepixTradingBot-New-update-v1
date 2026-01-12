"""
V6 Price Action Plugin - V5 Hybrid Plugin Architecture

This plugin implements the V6 Price Action trading strategy.

Features:
- 4 timeframe-specific plugins (1M, 5M, 15M, 1H)
- 14 alert types with conditional order routing
- Trend Pulse integration for MTF alignment
- Timeframe-specific order management

Part of Document 01: Project Overview - Plugin System Architecture
Full implementation in Document 07: Phase 5 - V6 Plugin Implementation
"""

from .plugin import PriceActionV6Plugin

__all__ = ["PriceActionV6Plugin"]
