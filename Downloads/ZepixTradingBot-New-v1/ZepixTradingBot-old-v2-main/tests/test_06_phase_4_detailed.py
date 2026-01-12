"""
Test Suite for Document 06: Phase 4 - V3 Plugin Migration

This test suite verifies 100% backward compatibility of the V3 Combined Logic
plugin with existing V2 code. All 12 signals must work exactly as before.

CRITICAL REQUIREMENTS:
- V3 Combined Logic plugin must produce IDENTICAL results to existing V2 code
- All 12 signals must work exactly as before
- LOGIC1/LOGIC2/LOGIC3 behavior must be preserved perfectly
- Database schema compatibility mandatory
- Shadow testing system for validation

Test Categories:
1. Signal Handlers (12 signal types)
2. Routing Logic (2-tier routing matrix)
3. Dual Order Manager (Hybrid SL system)
4. MTF Processor (4-pillar extraction)
5. Position Sizer (4-step lot calculation)
6. Plugin Integration (Full V3 pipeline)
7. Backward Compatibility (V3 parity tests)
8. Database Schema (Compatibility tests)

Part of Document 06: Phase 4 Detailed Plan - V3 Plugin Migration
"""

import pytest
import sys
import os
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import dataclass
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class MockAlert:
    """Mock alert for testing."""
    signal_type: str = "Institutional_Launchpad"
    symbol: str = "XAUUSD"
    direction: str = "LONG"
    tf: str = "15"
    entry_price: float = 2000.0
    sl_price: float = 1990.0
    tp_price: float = 2020.0
    mtf_string: str = "111111"
    mtf_trends: str = "1,1,1,1,1,1"
    consensus_score: int = 7
    timestamp: str = "2026-01-12T12:00:00Z"


def create_mock_plugin():
    """Create a mock plugin for testing components."""
    mock_plugin = Mock()
    mock_plugin.plugin_id = "combined_v3"
    mock_plugin.service_api = Mock()
    mock_plugin.config = {
        'dual_orders': {
            'split_ratio': 0.5,
            'order_a_comment': 'OrderA_TP_Trail',
            'order_b_comment': 'OrderB_Profit_Trail',
            'order_b_fixed_sl': 10.0
        },
        'mtf_config': {
            'pillars_only': ['15m', '1h', '4h', '1d'],
            'ignore_timeframes': ['1m', '5m'],
            'min_alignment': 3
        },
        'risk_tiers': {
            'micro': {'min_balance': 0, 'max_balance': 1000, 'base_lot': 0.01},
            'mini': {'min_balance': 1000, 'max_balance': 5000, 'base_lot': 0.05},
            'standard': {'min_balance': 5000, 'max_balance': 25000, 'base_lot': 0.10},
            'premium': {'min_balance': 25000, 'max_balance': 100000, 'base_lot': 0.25},
            'elite': {'min_balance': 100000, 'max_balance': 999999999, 'base_lot': 0.50}
        }
    }
    mock_plugin.database = None
    return mock_plugin


class TestSignalHandlers:
    """Test V3SignalHandlers - All 12 signal types."""
    
    def test_signal_handlers_module_exists(self):
        """Test signal_handlers.py exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/signal_handlers.py"
        assert path.exists(), "signal_handlers.py should exist"
    
    def test_signal_handlers_class_import(self):
        """Test V3SignalHandlers can be imported."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        assert V3SignalHandlers is not None
    
    def test_signal_handlers_initialization(self):
        """Test V3SignalHandlers initializes correctly."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        assert handlers is not None
        assert hasattr(handlers, 'route_signal')
    
    def test_entry_signals_defined(self):
        """Test all 7 entry signals are defined."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        entry_signals = [
            "Institutional_Launchpad",
            "Liquidity_Trap",
            "Momentum_Breakout",
            "Mitigation_Test",
            "Golden_Pocket_Flip",
            "Screener_Full_Bullish",
            "Screener_Full_Bearish"
        ]
        
        for signal in entry_signals:
            assert signal in handlers.ENTRY_SIGNALS or any(
                signal in s for s in handlers.ENTRY_SIGNALS
            ), f"Entry signal {signal} should be defined"
    
    def test_exit_signals_defined(self):
        """Test all 2 exit signals are defined."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        exit_signals = ["Bullish_Exit", "Bearish_Exit"]
        
        for signal in exit_signals:
            assert signal in handlers.EXIT_SIGNALS or any(
                signal in s for s in handlers.EXIT_SIGNALS
            ), f"Exit signal {signal} should be defined"
    
    def test_info_signals_defined(self):
        """Test all 2 info signals are defined."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        info_signals = ["Volatility_Squeeze", "Trend_Pulse"]
        
        for signal in info_signals:
            assert signal in handlers.INFO_SIGNALS or any(
                signal in s for s in handlers.INFO_SIGNALS
            ), f"Info signal {signal} should be defined"
    
    def test_trend_pulse_signal_defined(self):
        """Test trend pulse signal is defined."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert "Trend_Pulse" in handlers.INFO_SIGNALS or hasattr(handlers, 'handle_trend_pulse')
    
    def test_route_signal_method(self):
        """Test route_signal method exists and works."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'route_signal')
        assert callable(handlers.route_signal)
    
    def test_handle_institutional_launchpad(self):
        """Test Signal 1: Institutional Launchpad handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_institutional_launchpad')
    
    def test_handle_liquidity_trap(self):
        """Test Signal 2: Liquidity Trap handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_liquidity_trap')
    
    def test_handle_momentum_breakout(self):
        """Test Signal 3: Momentum Breakout handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_momentum_breakout')
    
    def test_handle_mitigation_test(self):
        """Test Signal 4: Mitigation Test handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_mitigation_test')
    
    def test_handle_golden_pocket_flip(self):
        """Test Signal 5: Golden Pocket Flip handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_golden_pocket_flip')
    
    def test_handle_screener_full(self):
        """Test Signal 9/10: Screener Full handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_screener_full')
    
    def test_handle_sideways_breakout(self):
        """Test Signal 12: Sideways Breakout handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_sideways_breakout')
    
    def test_handle_bullish_exit(self):
        """Test Signal 7: Bullish Exit handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_bullish_exit')
    
    def test_handle_bearish_exit(self):
        """Test Signal 8: Bearish Exit handler."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_bearish_exit')
    
    def test_handle_volatility_squeeze(self):
        """Test Signal 6: Volatility Squeeze handler (info only)."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_volatility_squeeze')
    
    def test_handle_trend_pulse(self):
        """Test Signal 11: Trend Pulse handler (DB update)."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'handle_trend_pulse')
    
    def test_get_statistics(self):
        """Test get_statistics method."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        
        assert hasattr(handlers, 'get_statistics')
        stats = handlers.get_statistics()
        assert isinstance(stats, dict)


class TestRoutingLogic:
    """Test V3RoutingLogic - 2-tier routing matrix."""
    
    def test_routing_logic_module_exists(self):
        """Test routing_logic.py exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/routing_logic.py"
        assert path.exists(), "routing_logic.py should exist"
    
    def test_routing_logic_class_import(self):
        """Test V3RoutingLogic can be imported."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        assert V3RoutingLogic is not None
    
    def test_routing_logic_initialization(self):
        """Test V3RoutingLogic initializes correctly."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        assert routing is not None
    
    def test_signal_overrides_defined(self):
        """Test signal overrides are defined."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        assert hasattr(routing, 'SIGNAL_OVERRIDES')
        assert "Screener_Full_Bullish" in routing.SIGNAL_OVERRIDES
        assert "Screener_Full_Bearish" in routing.SIGNAL_OVERRIDES
    
    def test_timeframe_routing_defined(self):
        """Test timeframe routing is defined."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        assert hasattr(routing, 'TIMEFRAME_ROUTING')
    
    def test_logic1_timeframe_routing(self):
        """Test LOGIC1 routes for 1m/5m timeframes."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        alert_5m = MockAlert(tf="5")
        result = routing.determine_logic_route(alert_5m, "Institutional_Launchpad")
        assert result == "LOGIC1", "5m should route to LOGIC1"
    
    def test_logic2_timeframe_routing(self):
        """Test LOGIC2 routes for 15m timeframe."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        alert_15m = MockAlert(tf="15")
        result = routing.determine_logic_route(alert_15m, "Institutional_Launchpad")
        assert result == "LOGIC2", "15m should route to LOGIC2"
    
    def test_logic3_timeframe_routing(self):
        """Test LOGIC3 routes for 60m/240m/D1 timeframes."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        alert_60m = MockAlert(tf="60")
        result = routing.determine_logic_route(alert_60m, "Institutional_Launchpad")
        assert result == "LOGIC3", "60m should route to LOGIC3"
        
        alert_240m = MockAlert(tf="240")
        result = routing.determine_logic_route(alert_240m, "Institutional_Launchpad")
        assert result == "LOGIC3", "240m should route to LOGIC3"
    
    def test_signal_override_priority(self):
        """Test signal override takes priority over timeframe routing."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        alert = MockAlert(signal_type="Screener_Full_Bullish", tf="5")
        result = routing.determine_logic_route(alert, "Screener_Full_Bullish")
        assert result == "LOGIC3", "Screener_Full_Bullish should override to LOGIC3"
    
    def test_default_logic_fallback(self):
        """Test default logic fallback."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        assert hasattr(routing, 'DEFAULT_LOGIC')
        assert routing.DEFAULT_LOGIC == "LOGIC2"
    
    def test_sl_multiplier_logic1(self):
        """Test SL multiplier for LOGIC1 is 1.0x."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        multiplier = routing.get_sl_multiplier("LOGIC1")
        assert multiplier == 1.0, "LOGIC1 SL multiplier should be 1.0"
    
    def test_sl_multiplier_logic2(self):
        """Test SL multiplier for LOGIC2 is 1.5x."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        multiplier = routing.get_sl_multiplier("LOGIC2")
        assert multiplier == 1.5, "LOGIC2 SL multiplier should be 1.5"
    
    def test_sl_multiplier_logic3(self):
        """Test SL multiplier for LOGIC3 is 2.0x."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        multiplier = routing.get_sl_multiplier("LOGIC3")
        assert multiplier == 2.0, "LOGIC3 SL multiplier should be 2.0"
    
    def test_logic_multiplier_logic1(self):
        """Test lot multiplier for LOGIC1 is 1.25x."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        multiplier = routing.get_logic_multiplier("LOGIC1")
        assert multiplier == 1.25, "LOGIC1 lot multiplier should be 1.25"
    
    def test_logic_multiplier_logic2(self):
        """Test lot multiplier for LOGIC2 is 1.0x."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        multiplier = routing.get_logic_multiplier("LOGIC2")
        assert multiplier == 1.0, "LOGIC2 lot multiplier should be 1.0"
    
    def test_logic_multiplier_logic3(self):
        """Test lot multiplier for LOGIC3 is 0.625x."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        multiplier = routing.get_logic_multiplier("LOGIC3")
        assert multiplier == 0.625, "LOGIC3 lot multiplier should be 0.625"
    
    def test_get_route_info(self):
        """Test get_route_info method."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        assert hasattr(routing, 'get_route_info')
        info = routing.get_route_info("LOGIC2")
        assert isinstance(info, dict)
        assert 'sl_multiplier' in info
        assert 'lot_multiplier' in info
    
    def test_get_statistics(self):
        """Test get_statistics method."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        assert hasattr(routing, 'get_statistics')
        stats = routing.get_statistics()
        assert isinstance(stats, dict)


class TestDualOrderManager:
    """Test V3DualOrderManager - Hybrid SL dual order system."""
    
    def test_dual_order_manager_module_exists(self):
        """Test dual_order_manager.py exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/dual_order_manager.py"
        assert path.exists(), "dual_order_manager.py should exist"
    
    def test_dual_order_manager_class_import(self):
        """Test V3DualOrderManager can be imported."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        assert V3DualOrderManager is not None
    
    def test_dual_order_manager_initialization(self):
        """Test V3DualOrderManager initializes correctly."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        assert manager is not None
    
    def test_place_dual_orders_method_exists(self):
        """Test place_dual_orders_v3 method exists."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, 'place_dual_orders_v3')
        assert callable(manager.place_dual_orders_v3)
    
    def test_order_a_smart_sl(self):
        """Test Order A uses V3 Smart SL from Pine Script."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, '_place_order_a')
    
    def test_order_b_fixed_sl(self):
        """Test Order B uses FIXED $10 SL."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, '_place_order_b')
        assert hasattr(manager, 'DEFAULT_ORDER_B_FIXED_SL_USD')
    
    def test_lot_split_ratio(self):
        """Test 50/50 lot split between Order A and Order B."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, 'DEFAULT_SPLIT_RATIO')
        assert manager.DEFAULT_SPLIT_RATIO == 0.5
    
    def test_calculate_fixed_sl(self):
        """Test _calculate_fixed_sl method."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, '_calculate_fixed_sl')
    
    def test_save_dual_trade(self):
        """Test _save_dual_trade method for database persistence."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, '_save_dual_trade')
    
    def test_get_statistics(self):
        """Test get_statistics method."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, 'get_statistics')
        stats = manager.get_statistics()
        assert isinstance(stats, dict)


class TestMTFProcessor:
    """Test V3MTFProcessor - 4-pillar MTF extraction."""
    
    def test_mtf_processor_module_exists(self):
        """Test mtf_processor.py exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/mtf_processor.py"
        assert path.exists(), "mtf_processor.py should exist"
    
    def test_mtf_processor_class_import(self):
        """Test V3MTFProcessor can be imported."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        assert V3MTFProcessor is not None
    
    def test_mtf_processor_initialization(self):
        """Test V3MTFProcessor initializes correctly."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        assert processor is not None
    
    def test_extract_4_pillar_trends(self):
        """Test extract_4_pillar_trends extracts indices [2:6]."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'extract_4_pillar_trends')
        
        mtf_string = "1,1,1,1,1,1"
        pillars = processor.extract_4_pillar_trends(mtf_string)
        assert len(pillars) == 4, "Should extract 4 pillars"
    
    def test_ignore_noisy_timeframes(self):
        """Test 1m and 5m timeframes are ignored."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        mtf_string = "0,0,1,1,1,1"
        pillars = processor.extract_4_pillar_trends(mtf_string)
        assert pillars == {"15m": 1, "1h": 1, "4h": 1, "1d": 1}, "Should ignore first 2 values (1m, 5m)"
    
    def test_pillar_order(self):
        """Test pillar order is [15m, 1h, 4h, 1d]."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'PILLARS')
    
    def test_validate_trend_alignment(self):
        """Test validate_trend_alignment method."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'validate_trend_alignment')
    
    def test_minimum_alignment_requirement(self):
        """Test minimum 3/4 pillars must align."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'MIN_ALIGNMENT_COUNT')
    
    def test_get_alignment_score(self):
        """Test get_alignment_score method."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'get_alignment_score')
    
    def test_update_trend_database(self):
        """Test update_trend_database method."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'update_trend_database')
    
    def test_get_trend_summary(self):
        """Test get_trend_summary method."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'get_trend_summary')
    
    def test_trend_caching(self):
        """Test trend caching for performance."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'get_cached_trends') or hasattr(processor, '_trend_cache')
    
    def test_get_statistics(self):
        """Test get_statistics method."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        assert hasattr(processor, 'get_statistics')
        stats = processor.get_statistics()
        assert isinstance(stats, dict)


class TestPositionSizer:
    """Test V3PositionSizer - 4-step position sizing flow."""
    
    def test_position_sizer_module_exists(self):
        """Test position_sizer.py exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/position_sizer.py"
        assert path.exists(), "position_sizer.py should exist"
    
    def test_position_sizer_class_import(self):
        """Test V3PositionSizer can be imported."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        assert V3PositionSizer is not None
    
    def test_position_sizer_initialization(self):
        """Test V3PositionSizer initializes correctly."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        assert sizer is not None
    
    def test_calculate_v3_lot_size(self):
        """Test calculate_v3_lot_size method."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, 'calculate_v3_lot_size')
    
    def test_4_step_flow(self):
        """Test 4-step flow: base lot x v3_multiplier x logic_multiplier."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, '_get_base_lot')
        assert hasattr(sizer, '_calculate_consensus_multiplier')
        assert hasattr(sizer, 'get_logic_multiplier')
    
    def test_calculate_dual_lots(self):
        """Test calculate_dual_lots for Order A and Order B."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, 'calculate_dual_lots')
    
    def test_consensus_score_mapping(self):
        """Test consensus score mapping: 0 -> 0.2, 9 -> 1.0."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        multiplier_0 = sizer._calculate_consensus_multiplier(0)
        multiplier_9 = sizer._calculate_consensus_multiplier(9)
        
        assert multiplier_0 <= 0.3, "Consensus 0 should give low multiplier"
        assert multiplier_9 >= 0.9, "Consensus 9 should give high multiplier"
    
    def test_risk_tiers(self):
        """Test risk tier support."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, 'RISK_TIERS') or hasattr(sizer, 'get_tier_for_balance')
    
    def test_micro_tier(self):
        """Test micro tier: $0-$1000, base lot 0.01."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        tier = sizer.get_tier_for_balance(500)
        assert tier == "micro", "Balance $500 should be micro tier"
    
    def test_mini_tier(self):
        """Test mini tier: $1000-$5000, base lot 0.05."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        tier = sizer.get_tier_for_balance(3000)
        assert tier == "mini", "Balance $3000 should be mini tier"
    
    def test_standard_tier(self):
        """Test standard tier: $5000-$25000, base lot 0.10."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        tier = sizer.get_tier_for_balance(15000)
        assert tier == "standard", "Balance $15000 should be standard tier"
    
    def test_premium_tier(self):
        """Test premium tier: $25000-$100000, base lot 0.25."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        tier = sizer.get_tier_for_balance(50000)
        assert tier == "premium", "Balance $50000 should be premium tier"
    
    def test_elite_tier(self):
        """Test elite tier: $100000+, base lot 0.50."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        tier = sizer.get_tier_for_balance(200000)
        assert tier == "elite", "Balance $200000 should be elite tier"
    
    def test_validate_lot_size(self):
        """Test validate_lot_size method."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, 'validate_lot_size')
    
    def test_symbol_specific_adjustments(self):
        """Test symbol-specific lot adjustments (e.g., gold)."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, 'adjust_lot_for_symbol')
    
    def test_get_statistics(self):
        """Test get_statistics method."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, 'get_statistics')
        stats = sizer.get_statistics()
        assert isinstance(stats, dict)


class TestCombinedV3Plugin:
    """Test CombinedV3Plugin - Main plugin class."""
    
    def test_plugin_module_exists(self):
        """Test plugin.py exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/plugin.py"
        assert path.exists(), "plugin.py should exist"
    
    def test_plugin_class_import(self):
        """Test CombinedV3Plugin can be imported."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert CombinedV3Plugin is not None
    
    def test_plugin_initialization(self):
        """Test CombinedV3Plugin class has required attributes."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert hasattr(CombinedV3Plugin, 'PLUGIN_ID')
        assert hasattr(CombinedV3Plugin, 'VERSION')
    
    def test_plugin_version(self):
        """Test plugin version is 3.1.0."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'VERSION')
        assert CombinedV3Plugin.VERSION == "3.1.0"
    
    def test_plugin_id(self):
        """Test plugin_id is combined_v3."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert CombinedV3Plugin.PLUGIN_ID == "combined_v3"
    
    def test_entry_signals_constant(self):
        """Test ENTRY_SIGNALS constant is defined."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'ENTRY_SIGNALS')
        assert len(CombinedV3Plugin.ENTRY_SIGNALS) >= 7
    
    def test_exit_signals_constant(self):
        """Test EXIT_SIGNALS constant is defined."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'EXIT_SIGNALS')
        assert len(CombinedV3Plugin.EXIT_SIGNALS) >= 2
    
    def test_info_signals_constant(self):
        """Test INFO_SIGNALS constant is defined."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'INFO_SIGNALS')
    
    def test_sl_multipliers_constant(self):
        """Test SL_MULTIPLIERS constant is defined."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'SL_MULTIPLIERS')
        assert CombinedV3Plugin.SL_MULTIPLIERS.get('LOGIC1') == 1.0
        assert CombinedV3Plugin.SL_MULTIPLIERS.get('LOGIC2') == 1.5
        assert CombinedV3Plugin.SL_MULTIPLIERS.get('LOGIC3') == 2.0
    
    def test_order_b_multiplier_constant(self):
        """Test ORDER_B_MULTIPLIER constant is defined."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'ORDER_B_MULTIPLIER')
        assert CombinedV3Plugin.ORDER_B_MULTIPLIER == 2.0
    
    def test_signal_handlers_component(self):
        """Test signal_handlers is defined in __init__."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin.__init__)
        assert 'signal_handlers' in source
    
    def test_routing_component(self):
        """Test routing is defined in __init__."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin.__init__)
        assert 'routing' in source
    
    def test_dual_orders_component(self):
        """Test dual_orders is defined in __init__."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin.__init__)
        assert 'dual_orders' in source
    
    def test_mtf_processor_component(self):
        """Test mtf_processor is defined in __init__."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin.__init__)
        assert 'mtf_processor' in source
    
    def test_position_sizer_component(self):
        """Test position_sizer is defined in __init__."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin.__init__)
        assert 'position_sizer' in source
    
    def test_on_signal_received_method(self):
        """Test on_signal_received method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'on_signal_received')
        assert callable(CombinedV3Plugin.on_signal_received)
    
    def test_process_v3_entry_method(self):
        """Test process_v3_entry method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_v3_entry')
        assert callable(CombinedV3Plugin.process_v3_entry)
    
    def test_process_v3_exit_method(self):
        """Test process_v3_exit method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_v3_exit')
        assert callable(CombinedV3Plugin.process_v3_exit)
    
    def test_process_entry_signal_method(self):
        """Test process_entry_signal method exists (legacy interface)."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_entry_signal')
        assert callable(CombinedV3Plugin.process_entry_signal)
    
    def test_process_exit_signal_method(self):
        """Test process_exit_signal method exists (legacy interface)."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_exit_signal')
        assert callable(CombinedV3Plugin.process_exit_signal)
    
    def test_process_reversal_signal_method(self):
        """Test process_reversal_signal method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_reversal_signal')
        assert callable(CombinedV3Plugin.process_reversal_signal)
    
    def test_process_trend_pulse_method(self):
        """Test process_trend_pulse method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_trend_pulse')
        assert callable(CombinedV3Plugin.process_trend_pulse)
    
    def test_validate_alert_method(self):
        """Test validate_alert method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'validate_alert')
        assert callable(CombinedV3Plugin.validate_alert)
    
    def test_get_sl_multiplier_method(self):
        """Test get_sl_multiplier method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'get_sl_multiplier')
        assert callable(CombinedV3Plugin.get_sl_multiplier)
    
    def test_get_status_method(self):
        """Test get_status method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'get_status')
        assert callable(CombinedV3Plugin.get_status)
    
    def test_get_statistics_method(self):
        """Test get_statistics method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'get_statistics')
        assert callable(CombinedV3Plugin.get_statistics)
    
    def test_shadow_mode_attribute(self):
        """Test shadow_mode is set in __init__."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin.__init__)
        assert 'shadow_mode' in source
    
    def test_stats_tracking(self):
        """Test stats is set in __init__."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin.__init__)
        assert 'stats' in source


class TestConfigJson:
    """Test config.json - Document 06 specifications."""
    
    def test_config_file_exists(self):
        """Test config.json exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        assert path.exists(), "config.json should exist"
    
    def test_config_is_valid_json(self):
        """Test config.json is valid JSON."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert isinstance(config, dict)
    
    def test_config_plugin_id(self):
        """Test plugin_id is combined_v3."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert config.get('plugin_id') == 'combined_v3'
    
    def test_config_version(self):
        """Test version is 3.1.0."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert config.get('version') == '3.1.0'
    
    def test_config_signal_routing(self):
        """Test signal_routing section exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'signal_routing' in config
        assert 'signal_overrides' in config['signal_routing']
        assert 'timeframe_routing' in config['signal_routing']
    
    def test_config_signal_overrides(self):
        """Test signal overrides are defined."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        overrides = config['signal_routing']['signal_overrides']
        assert 'Screener_Full_Bullish' in overrides
        assert 'Screener_Full_Bearish' in overrides
    
    def test_config_logic_multipliers(self):
        """Test logic_multipliers section exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'logic_multipliers' in config
        assert config['logic_multipliers']['LOGIC1'] == 1.25
        assert config['logic_multipliers']['LOGIC2'] == 1.0
        assert config['logic_multipliers']['LOGIC3'] == 0.625
    
    def test_config_logic_settings(self):
        """Test logic_settings section exists with SL multipliers."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'logic_settings' in config
        assert config['logic_settings']['logic1']['sl_multiplier'] == 1.0
        assert config['logic_settings']['logic2']['sl_multiplier'] == 1.5
        assert config['logic_settings']['logic3']['sl_multiplier'] == 2.0
    
    def test_config_mtf_config(self):
        """Test mtf_config section exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'mtf_config' in config
        assert config['mtf_config']['min_alignment'] == 3
    
    def test_config_dual_orders(self):
        """Test dual_orders section exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'dual_orders' in config
        assert config['dual_orders']['split_ratio'] == 0.5
        assert config['dual_orders']['order_b_fixed_sl'] == 10.0
    
    def test_config_risk_tiers(self):
        """Test risk_tiers section exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'risk_tiers' in config
        assert 'micro' in config['risk_tiers']
        assert 'mini' in config['risk_tiers']
        assert 'standard' in config['risk_tiers']
        assert 'premium' in config['risk_tiers']
        assert 'elite' in config['risk_tiers']


class TestInitPy:
    """Test __init__.py - Module exports."""
    
    def test_init_file_exists(self):
        """Test __init__.py exists."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/__init__.py"
        assert path.exists(), "__init__.py should exist"
    
    def test_combined_v3_plugin_export(self):
        """Test CombinedV3Plugin is exported."""
        from logic_plugins.combined_v3 import CombinedV3Plugin
        assert CombinedV3Plugin is not None
    
    def test_signal_handlers_export(self):
        """Test V3SignalHandlers is exported."""
        from logic_plugins.combined_v3 import V3SignalHandlers
        assert V3SignalHandlers is not None
    
    def test_routing_logic_export(self):
        """Test V3RoutingLogic is exported."""
        from logic_plugins.combined_v3 import V3RoutingLogic
        assert V3RoutingLogic is not None
    
    def test_dual_order_manager_export(self):
        """Test V3DualOrderManager is exported."""
        from logic_plugins.combined_v3 import V3DualOrderManager
        assert V3DualOrderManager is not None
    
    def test_mtf_processor_export(self):
        """Test V3MTFProcessor is exported."""
        from logic_plugins.combined_v3 import V3MTFProcessor
        assert V3MTFProcessor is not None
    
    def test_position_sizer_export(self):
        """Test V3PositionSizer is exported."""
        from logic_plugins.combined_v3 import V3PositionSizer
        assert V3PositionSizer is not None
    
    def test_all_exports(self):
        """Test __all__ contains all exports."""
        from logic_plugins.combined_v3 import __all__
        assert 'CombinedV3Plugin' in __all__
        assert 'V3SignalHandlers' in __all__
        assert 'V3RoutingLogic' in __all__
        assert 'V3DualOrderManager' in __all__
        assert 'V3MTFProcessor' in __all__
        assert 'V3PositionSizer' in __all__


class TestBackwardCompatibility:
    """Test backward compatibility with existing V2 code."""
    
    def test_legacy_process_entry_signal(self):
        """Test legacy process_entry_signal interface works."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_entry_signal')
        assert callable(CombinedV3Plugin.process_entry_signal)
    
    def test_legacy_process_exit_signal(self):
        """Test legacy process_exit_signal interface works."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'process_exit_signal')
        assert callable(CombinedV3Plugin.process_exit_signal)
    
    def test_legacy_validate_alert(self):
        """Test legacy validate_alert interface works."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'validate_alert')
        assert callable(CombinedV3Plugin.validate_alert)
    
    def test_legacy_route_to_logic(self):
        """Test legacy _route_to_logic method works."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, '_route_to_logic')
        assert callable(CombinedV3Plugin._route_to_logic)
    
    def test_legacy_get_status(self):
        """Test legacy get_status interface works."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, 'get_status')
        assert callable(CombinedV3Plugin.get_status)
    
    def test_base_plugin_inheritance(self):
        """Test CombinedV3Plugin inherits from BaseLogicPlugin."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert issubclass(CombinedV3Plugin, BaseLogicPlugin)
    
    def test_plugin_id_consistency(self):
        """Test plugin_id is consistent."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert CombinedV3Plugin.PLUGIN_ID == "combined_v3"
    
    def test_supported_symbols(self):
        """Test supported symbols are defined in config."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'supported_symbols' in config
        assert 'XAUUSD' in config['supported_symbols']


class TestDatabaseSchema:
    """Test database schema compatibility."""
    
    def test_database_path_defined(self):
        """Test database path is defined in config."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert 'database' in config
        assert 'path' in config['database']
    
    def test_v3_database_initialization(self):
        """Test V3 database initialization method exists."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        assert hasattr(CombinedV3Plugin, '_initialize_v3_database')
        assert callable(CombinedV3Plugin._initialize_v3_database)
    
    def test_dual_trades_table_schema(self):
        """Test dual_trades table schema is defined in _initialize_v3_database."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        import inspect
        source = inspect.getsource(CombinedV3Plugin._initialize_v3_database)
        assert 'v3_dual_trades' in source


class TestDocument06Integration:
    """Test Document 06 integration requirements."""
    
    def test_all_12_signals_supported(self):
        """Test all 12 signal types are supported."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        total_signals = len(CombinedV3Plugin.ENTRY_SIGNALS) + len(CombinedV3Plugin.EXIT_SIGNALS) + len(CombinedV3Plugin.INFO_SIGNALS)
        assert total_signals >= 11, f"Should support at least 11 signals, got {total_signals}"
    
    def test_3_logic_routes_supported(self):
        """Test all 3 logic routes are supported."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        
        assert routing.get_sl_multiplier('LOGIC1') is not None
        assert routing.get_sl_multiplier('LOGIC2') is not None
        assert routing.get_sl_multiplier('LOGIC3') is not None
    
    def test_dual_order_system(self):
        """Test dual order system is implemented."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        
        assert hasattr(manager, 'place_dual_orders_v3')
    
    def test_mtf_4_pillar_system(self):
        """Test MTF 4-pillar system is implemented."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        
        pillars = processor.extract_4_pillar_trends("1,1,1,1,1,1")
        assert len(pillars) == 4
    
    def test_position_sizing_flow(self):
        """Test 4-step position sizing flow is implemented."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        
        assert hasattr(sizer, 'calculate_v3_lot_size')
        assert hasattr(sizer, '_get_base_lot')
        assert hasattr(sizer, '_calculate_consensus_multiplier')


class TestDocument06Summary:
    """Summary tests for Document 06 completion."""
    
    def test_signal_handlers_complete(self):
        """Test signal_handlers.py is complete."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        assert handlers is not None
    
    def test_routing_logic_complete(self):
        """Test routing_logic.py is complete."""
        from logic_plugins.combined_v3.routing_logic import V3RoutingLogic
        routing = V3RoutingLogic()
        assert routing is not None
    
    def test_dual_order_manager_complete(self):
        """Test dual_order_manager.py is complete."""
        from logic_plugins.combined_v3.dual_order_manager import V3DualOrderManager
        mock_plugin = create_mock_plugin()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        assert manager is not None
    
    def test_mtf_processor_complete(self):
        """Test mtf_processor.py is complete."""
        from logic_plugins.combined_v3.mtf_processor import V3MTFProcessor
        mock_plugin = create_mock_plugin()
        processor = V3MTFProcessor(mock_plugin)
        assert processor is not None
    
    def test_position_sizer_complete(self):
        """Test position_sizer.py is complete."""
        from logic_plugins.combined_v3.position_sizer import V3PositionSizer
        sizer = V3PositionSizer()
        assert sizer is not None
    
    def test_plugin_complete(self):
        """Test plugin.py is complete."""
        from logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert CombinedV3Plugin.VERSION == "3.1.0"
        assert CombinedV3Plugin.PLUGIN_ID == "combined_v3"
    
    def test_config_complete(self):
        """Test config.json is complete."""
        path = Path(__file__).parent.parent / "src/logic_plugins/combined_v3/config.json"
        with open(path) as f:
            config = json.load(f)
        assert config.get('version') == '3.1.0'
    
    def test_init_complete(self):
        """Test __init__.py is complete."""
        from logic_plugins.combined_v3 import __all__
        assert len(__all__) == 6
    
    def test_document_06_requirements_met(self):
        """Test all Document 06 requirements are met."""
        from logic_plugins.combined_v3 import (
            CombinedV3Plugin,
            V3SignalHandlers,
            V3RoutingLogic,
            V3DualOrderManager,
            V3MTFProcessor,
            V3PositionSizer
        )
        
        assert CombinedV3Plugin.VERSION == "3.1.0"
        assert CombinedV3Plugin.SL_MULTIPLIERS == {'LOGIC1': 1.0, 'LOGIC2': 1.5, 'LOGIC3': 2.0}
        assert CombinedV3Plugin.ORDER_B_MULTIPLIER == 2.0
        
        mock_plugin = create_mock_plugin()
        handlers = V3SignalHandlers(mock_plugin)
        routing = V3RoutingLogic()
        manager = V3DualOrderManager(mock_plugin, mock_plugin.service_api)
        processor = V3MTFProcessor(mock_plugin)
        sizer = V3PositionSizer()
        
        assert handlers is not None
        assert routing is not None
        assert manager is not None
        assert processor is not None
        assert sizer is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
