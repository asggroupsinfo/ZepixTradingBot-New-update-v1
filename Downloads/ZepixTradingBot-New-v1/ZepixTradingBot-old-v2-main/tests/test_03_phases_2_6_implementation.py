"""
Document 03: Phases 2-6 Implementation Tests

Comprehensive test suite verifying all Phase 2-6 components:
- Phase 2: Multi-Telegram System (3 bots)
- Phase 3: Service API Layer (4 services)
- Phase 4: V3 Plugin Migration (entry/exit logic)
- Phase 5: V6 Plugin Implementation (4 timeframes, 14 alerts)
- Phase 6: Integration and Documentation

Part of ATOMIC PROTOCOL - Document 03 verification
"""

import pytest
import sys
import os
import json
import asyncio
import ast
import re
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_class_has_method(file_path: Path, class_name: str, method_name: str) -> bool:
    """Check if a class in a file has a specific method using AST parsing."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name == method_name:
                            return True
        return False
    except Exception:
        return False


def check_class_exists(file_path: Path, class_name: str) -> bool:
    """Check if a class exists in a file using AST parsing."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return True
        return False
    except Exception:
        return False


def check_class_has_attribute(file_path: Path, class_name: str, attr_name: str) -> bool:
    """Check if a class has a class-level attribute using AST parsing."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == attr_name:
                                return True
        return False
    except Exception:
        return False


# ============================================================================
# PHASE 2: Multi-Telegram System Tests
# ============================================================================

class TestPhase2MultiTelegramSystem:
    """Tests for Phase 2: Multi-Telegram System (3 bots).
    
    Note: Uses AST-based checking to avoid import chain issues with
    src.modules.telegram_bot dependency that exists in production but
    not in test environment.
    """
    
    # File existence tests
    
    def test_multi_telegram_manager_exists(self):
        """Verify MultiTelegramManager file exists."""
        path = PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py"
        assert path.exists(), f"MultiTelegramManager not found at {path}"
    
    def test_controller_bot_exists(self):
        """Verify ControllerBot file exists."""
        path = PROJECT_ROOT / "src" / "telegram" / "controller_bot.py"
        assert path.exists(), f"ControllerBot not found at {path}"
    
    def test_notification_bot_exists(self):
        """Verify NotificationBot file exists."""
        path = PROJECT_ROOT / "src" / "telegram" / "notification_bot.py"
        assert path.exists(), f"NotificationBot not found at {path}"
    
    def test_analytics_bot_exists(self):
        """Verify AnalyticsBot file exists."""
        path = PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py"
        assert path.exists(), f"AnalyticsBot not found at {path}"
    
    def test_telegram_init_exists(self):
        """Verify telegram __init__.py exists."""
        path = PROJECT_ROOT / "src" / "telegram" / "__init__.py"
        assert path.exists(), f"Telegram __init__.py not found at {path}"
    
    # Class existence tests (using AST to avoid import issues)
    
    def test_multi_telegram_manager_class_exists(self):
        """Verify MultiTelegramManager class exists in file."""
        path = PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py"
        assert check_class_exists(path, "MultiTelegramManager")
    
    def test_controller_bot_class_exists(self):
        """Verify ControllerBot class exists in file."""
        path = PROJECT_ROOT / "src" / "telegram" / "controller_bot.py"
        assert check_class_exists(path, "ControllerBot")
    
    def test_notification_bot_class_exists(self):
        """Verify NotificationBot class exists in file."""
        path = PROJECT_ROOT / "src" / "telegram" / "notification_bot.py"
        assert check_class_exists(path, "NotificationBot")
    
    def test_analytics_bot_class_exists(self):
        """Verify AnalyticsBot class exists in file."""
        path = PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py"
        assert check_class_exists(path, "AnalyticsBot")
    
    # Structure tests (using AST)
    
    def test_multi_telegram_manager_has_route_message(self):
        """Verify MultiTelegramManager has route_message method."""
        path = PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py"
        assert check_class_has_method(path, "MultiTelegramManager", "route_message")
    
    def test_multi_telegram_manager_has_send_alert(self):
        """Verify MultiTelegramManager has send_alert method."""
        path = PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py"
        assert check_class_has_method(path, "MultiTelegramManager", "send_alert")
    
    def test_multi_telegram_manager_has_send_report(self):
        """Verify MultiTelegramManager has send_report method."""
        path = PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py"
        assert check_class_has_method(path, "MultiTelegramManager", "send_report")
    
    def test_controller_bot_has_process_command(self):
        """Verify ControllerBot has process_command method."""
        path = PROJECT_ROOT / "src" / "telegram" / "controller_bot.py"
        assert check_class_has_method(path, "ControllerBot", "process_command")
    
    def test_notification_bot_has_send_entry_notification(self):
        """Verify NotificationBot has send_entry_notification method."""
        path = PROJECT_ROOT / "src" / "telegram" / "notification_bot.py"
        assert check_class_has_method(path, "NotificationBot", "send_entry_notification")
    
    def test_notification_bot_has_send_exit_notification(self):
        """Verify NotificationBot has send_exit_notification method."""
        path = PROJECT_ROOT / "src" / "telegram" / "notification_bot.py"
        assert check_class_has_method(path, "NotificationBot", "send_exit_notification")
    
    def test_analytics_bot_has_send_daily_report(self):
        """Verify AnalyticsBot has send_daily_report method."""
        path = PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py"
        assert check_class_has_method(path, "AnalyticsBot", "send_daily_report")
    
    def test_analytics_bot_has_send_plugin_report(self):
        """Verify AnalyticsBot has send_plugin_report method."""
        path = PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py"
        assert check_class_has_method(path, "AnalyticsBot", "send_plugin_report")
    
    # Additional structure tests
    
    def test_controller_bot_has_start_method(self):
        """Verify ControllerBot has start method."""
        path = PROJECT_ROOT / "src" / "telegram" / "controller_bot.py"
        assert check_class_has_method(path, "ControllerBot", "start")
    
    def test_notification_bot_has_send_message(self):
        """Verify NotificationBot has send_message method."""
        path = PROJECT_ROOT / "src" / "telegram" / "notification_bot.py"
        assert check_class_has_method(path, "NotificationBot", "send_message")
    
    def test_analytics_bot_has_send_weekly_report(self):
        """Verify AnalyticsBot has send_weekly_report method."""
        path = PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py"
        assert check_class_has_method(path, "AnalyticsBot", "send_weekly_report")


# ============================================================================
# PHASE 3: Service API Layer Tests
# ============================================================================

class TestPhase3ServiceAPILayer:
    """Tests for Phase 3: Service API Layer (4 services)."""
    
    # File existence tests
    
    def test_order_execution_service_exists(self):
        """Verify OrderExecutionService file exists."""
        path = PROJECT_ROOT / "src" / "services" / "order_execution.py"
        assert path.exists(), f"OrderExecutionService not found at {path}"
    
    def test_profit_booking_service_exists(self):
        """Verify ProfitBookingService file exists."""
        path = PROJECT_ROOT / "src" / "services" / "profit_booking.py"
        assert path.exists(), f"ProfitBookingService not found at {path}"
    
    def test_risk_management_service_exists(self):
        """Verify RiskManagementService file exists."""
        path = PROJECT_ROOT / "src" / "services" / "risk_management.py"
        assert path.exists(), f"RiskManagementService not found at {path}"
    
    def test_trend_monitor_service_exists(self):
        """Verify TrendMonitorService file exists."""
        path = PROJECT_ROOT / "src" / "services" / "trend_monitor.py"
        assert path.exists(), f"TrendMonitorService not found at {path}"
    
    # Import tests
    
    def test_order_execution_service_imports(self):
        """Verify OrderExecutionService can be imported."""
        from src.services.order_execution import OrderExecutionService
        assert OrderExecutionService is not None
    
    def test_profit_booking_service_imports(self):
        """Verify ProfitBookingService can be imported."""
        from src.services.profit_booking import ProfitBookingService
        assert ProfitBookingService is not None
    
    def test_risk_management_service_imports(self):
        """Verify RiskManagementService can be imported."""
        from src.services.risk_management import RiskManagementService
        assert RiskManagementService is not None
    
    def test_trend_monitor_service_imports(self):
        """Verify TrendMonitorService can be imported."""
        from src.services.trend_monitor import TrendMonitorService
        assert TrendMonitorService is not None
    
    # Structure tests - OrderExecutionService
    
    def test_order_execution_has_place_order(self):
        """Verify OrderExecutionService has place_order method."""
        from src.services.order_execution import OrderExecutionService
        assert hasattr(OrderExecutionService, 'place_order')
    
    def test_order_execution_has_place_dual_orders(self):
        """Verify OrderExecutionService has place_dual_orders method."""
        from src.services.order_execution import OrderExecutionService
        assert hasattr(OrderExecutionService, 'place_dual_orders')
    
    def test_order_execution_has_modify_order(self):
        """Verify OrderExecutionService has modify_order method."""
        from src.services.order_execution import OrderExecutionService
        assert hasattr(OrderExecutionService, 'modify_order')
    
    def test_order_execution_has_close_order(self):
        """Verify OrderExecutionService has close_order method."""
        from src.services.order_execution import OrderExecutionService
        assert hasattr(OrderExecutionService, 'close_order')
    
    def test_order_execution_has_close_all_orders(self):
        """Verify OrderExecutionService has close_all_orders method."""
        from src.services.order_execution import OrderExecutionService
        assert hasattr(OrderExecutionService, 'close_all_orders')
    
    def test_order_execution_has_get_open_orders(self):
        """Verify OrderExecutionService has get_open_orders method."""
        from src.services.order_execution import OrderExecutionService
        assert hasattr(OrderExecutionService, 'get_open_orders')
    
    # Structure tests - ProfitBookingService
    
    def test_profit_booking_has_create_chain(self):
        """Verify ProfitBookingService has create_chain method."""
        from src.services.profit_booking import ProfitBookingService
        assert hasattr(ProfitBookingService, 'create_chain')
    
    def test_profit_booking_has_process_profit_level(self):
        """Verify ProfitBookingService has process_profit_level method."""
        from src.services.profit_booking import ProfitBookingService
        assert hasattr(ProfitBookingService, 'process_profit_level')
    
    def test_profit_booking_has_close_chain(self):
        """Verify ProfitBookingService has close_chain method."""
        from src.services.profit_booking import ProfitBookingService
        assert hasattr(ProfitBookingService, 'close_chain')
    
    def test_profit_booking_has_pyramid_levels(self):
        """Verify ProfitBookingService has PYRAMID_LEVELS constant."""
        from src.services.profit_booking import ProfitBookingService
        assert hasattr(ProfitBookingService, 'PYRAMID_LEVELS')
        assert ProfitBookingService.PYRAMID_LEVELS[0] == 1
        assert ProfitBookingService.PYRAMID_LEVELS[4] == 16
    
    # Structure tests - RiskManagementService
    
    def test_risk_management_has_calculate_lot_size(self):
        """Verify RiskManagementService has calculate_lot_size method."""
        from src.services.risk_management import RiskManagementService
        assert hasattr(RiskManagementService, 'calculate_lot_size')
    
    def test_risk_management_has_get_account_tier(self):
        """Verify RiskManagementService has get_account_tier method."""
        from src.services.risk_management import RiskManagementService
        assert hasattr(RiskManagementService, 'get_account_tier')
    
    def test_risk_management_has_validate_risk(self):
        """Verify RiskManagementService has validate_risk method."""
        from src.services.risk_management import RiskManagementService
        assert hasattr(RiskManagementService, 'validate_risk')
    
    def test_risk_management_has_account_tiers(self):
        """Verify RiskManagementService has ACCOUNT_TIERS constant."""
        from src.services.risk_management import RiskManagementService
        assert hasattr(RiskManagementService, 'ACCOUNT_TIERS')
        assert "TIER_1" in RiskManagementService.ACCOUNT_TIERS
        assert "TIER_5" in RiskManagementService.ACCOUNT_TIERS
    
    # Structure tests - TrendMonitorService
    
    def test_trend_monitor_has_get_trend(self):
        """Verify TrendMonitorService has get_trend method."""
        from src.services.trend_monitor import TrendMonitorService
        assert hasattr(TrendMonitorService, 'get_trend')
    
    def test_trend_monitor_has_update_trend(self):
        """Verify TrendMonitorService has update_trend method."""
        from src.services.trend_monitor import TrendMonitorService
        assert hasattr(TrendMonitorService, 'update_trend')
    
    def test_trend_monitor_has_get_mtf_alignment(self):
        """Verify TrendMonitorService has get_mtf_alignment method."""
        from src.services.trend_monitor import TrendMonitorService
        assert hasattr(TrendMonitorService, 'get_mtf_alignment')
    
    def test_trend_monitor_has_lock_trend(self):
        """Verify TrendMonitorService has lock_trend method."""
        from src.services.trend_monitor import TrendMonitorService
        assert hasattr(TrendMonitorService, 'lock_trend')
    
    # Instantiation and functionality tests
    
    def test_risk_management_instantiation(self):
        """Verify RiskManagementService can be instantiated."""
        from src.services.risk_management import RiskManagementService
        mt5_client = Mock()
        config = {}
        service = RiskManagementService(mt5_client, config)
        assert service is not None
    
    def test_risk_management_tier_calculation(self):
        """Verify tier calculation works correctly."""
        from src.services.risk_management import RiskManagementService
        mt5_client = Mock()
        config = {}
        service = RiskManagementService(mt5_client, config)
        
        assert service.get_account_tier(5000) == "TIER_1"
        assert service.get_account_tier(15000) == "TIER_2"
        assert service.get_account_tier(30000) == "TIER_3"
        assert service.get_account_tier(75000) == "TIER_4"
        assert service.get_account_tier(150000) == "TIER_5"
    
    def test_risk_management_lot_calculation(self):
        """Verify lot size calculation works correctly."""
        from src.services.risk_management import RiskManagementService
        mt5_client = Mock()
        config = {}
        service = RiskManagementService(mt5_client, config)
        
        lot = service.calculate_lot_size(10000, 50, "EURUSD")
        assert lot >= 0.01
        assert lot <= 0.10  # TIER_2 max
    
    def test_trend_monitor_instantiation(self):
        """Verify TrendMonitorService can be instantiated."""
        from src.services.trend_monitor import TrendMonitorService
        config = {}
        service = TrendMonitorService(config)
        assert service is not None
    
    def test_trend_monitor_update_and_get(self):
        """Verify trend update and retrieval works."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        config = {}
        service = TrendMonitorService(config)
        
        service.update_trend("EURUSD", "15M", TrendDirection.BULLISH, "test")
        trend = service.get_trend("EURUSD", "15M")
        assert trend == TrendDirection.BULLISH
    
    def test_trend_monitor_mtf_alignment(self):
        """Verify MTF alignment calculation works."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        config = {}
        service = TrendMonitorService(config)
        
        # Set all timeframes to bullish
        for tf in ["1M", "5M", "15M", "1H"]:
            service.update_trend("EURUSD", tf, TrendDirection.BULLISH, "test")
        
        alignment = service.get_mtf_alignment("EURUSD")
        assert alignment["aligned"] == True
        assert alignment["direction"] == "BULLISH"
        assert alignment["alignment_score"] == 100


# ============================================================================
# PHASE 4: V3 Plugin Migration Tests
# ============================================================================

class TestPhase4V3PluginMigration:
    """Tests for Phase 4: V3 Plugin Migration."""
    
    # File existence tests
    
    def test_v3_plugin_exists(self):
        """Verify V3 plugin.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "plugin.py"
        assert path.exists(), f"V3 plugin.py not found at {path}"
    
    def test_v3_config_exists(self):
        """Verify V3 config.json exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "config.json"
        assert path.exists(), f"V3 config.json not found at {path}"
    
    def test_v3_entry_logic_exists(self):
        """Verify V3 entry_logic.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "entry_logic.py"
        assert path.exists(), f"V3 entry_logic.py not found at {path}"
    
    def test_v3_exit_logic_exists(self):
        """Verify V3 exit_logic.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "exit_logic.py"
        assert path.exists(), f"V3 exit_logic.py not found at {path}"
    
    def test_v3_init_exists(self):
        """Verify V3 __init__.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "__init__.py"
        assert path.exists(), f"V3 __init__.py not found at {path}"
    
    # Import tests
    
    def test_v3_plugin_imports(self):
        """Verify CombinedV3Plugin can be imported."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert CombinedV3Plugin is not None
    
    def test_v3_entry_logic_imports(self):
        """Verify EntryLogic can be imported."""
        from src.logic_plugins.combined_v3.entry_logic import EntryLogic
        assert EntryLogic is not None
    
    def test_v3_exit_logic_imports(self):
        """Verify ExitLogic can be imported."""
        from src.logic_plugins.combined_v3.exit_logic import ExitLogic
        assert ExitLogic is not None
    
    # Structure tests - CombinedV3Plugin
    
    def test_v3_plugin_has_entry_signals(self):
        """Verify CombinedV3Plugin has ENTRY_SIGNALS."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert hasattr(CombinedV3Plugin, 'ENTRY_SIGNALS')
        assert len(CombinedV3Plugin.ENTRY_SIGNALS) == 7
    
    def test_v3_plugin_has_exit_signals(self):
        """Verify CombinedV3Plugin has EXIT_SIGNALS."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert hasattr(CombinedV3Plugin, 'EXIT_SIGNALS')
        assert len(CombinedV3Plugin.EXIT_SIGNALS) == 2
    
    def test_v3_plugin_has_logic_types(self):
        """Verify CombinedV3Plugin has LOGIC_TYPES."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert hasattr(CombinedV3Plugin, 'LOGIC_TYPES')
        assert "LOGIC1" in CombinedV3Plugin.LOGIC_TYPES
        assert "LOGIC2" in CombinedV3Plugin.LOGIC_TYPES
        assert "LOGIC3" in CombinedV3Plugin.LOGIC_TYPES
    
    def test_v3_plugin_has_process_entry_signal(self):
        """Verify CombinedV3Plugin has process_entry_signal method."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert hasattr(CombinedV3Plugin, 'process_entry_signal')
    
    def test_v3_plugin_has_process_exit_signal(self):
        """Verify CombinedV3Plugin has process_exit_signal method."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert hasattr(CombinedV3Plugin, 'process_exit_signal')
    
    def test_v3_plugin_has_validate_alert(self):
        """Verify CombinedV3Plugin has validate_alert method."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        assert hasattr(CombinedV3Plugin, 'validate_alert')
    
    # Structure tests - EntryLogic
    
    def test_entry_logic_has_process_entry(self):
        """Verify EntryLogic has process_entry method."""
        from src.logic_plugins.combined_v3.entry_logic import EntryLogic
        assert hasattr(EntryLogic, 'process_entry')
    
    def test_entry_logic_has_sl_multipliers(self):
        """Verify EntryLogic has SL_MULTIPLIERS."""
        from src.logic_plugins.combined_v3.entry_logic import EntryLogic
        assert hasattr(EntryLogic, 'SL_MULTIPLIERS')
        assert EntryLogic.SL_MULTIPLIERS["LOGIC1"] == 1.0
        assert EntryLogic.SL_MULTIPLIERS["LOGIC2"] == 1.5
        assert EntryLogic.SL_MULTIPLIERS["LOGIC3"] == 2.0
    
    def test_entry_logic_has_order_b_multiplier(self):
        """Verify EntryLogic has ORDER_B_MULTIPLIER."""
        from src.logic_plugins.combined_v3.entry_logic import EntryLogic
        assert hasattr(EntryLogic, 'ORDER_B_MULTIPLIER')
        assert EntryLogic.ORDER_B_MULTIPLIER == 2.0
    
    # Structure tests - ExitLogic
    
    def test_exit_logic_has_process_exit(self):
        """Verify ExitLogic has process_exit method."""
        from src.logic_plugins.combined_v3.exit_logic import ExitLogic
        assert hasattr(ExitLogic, 'process_exit')
    
    def test_exit_logic_has_process_reversal_exit(self):
        """Verify ExitLogic has process_reversal_exit method."""
        from src.logic_plugins.combined_v3.exit_logic import ExitLogic
        assert hasattr(ExitLogic, 'process_reversal_exit')
    
    def test_exit_logic_has_process_partial_exit(self):
        """Verify ExitLogic has process_partial_exit method."""
        from src.logic_plugins.combined_v3.exit_logic import ExitLogic
        assert hasattr(ExitLogic, 'process_partial_exit')
    
    def test_exit_logic_has_calculate_pnl(self):
        """Verify ExitLogic has calculate_pnl method."""
        from src.logic_plugins.combined_v3.exit_logic import ExitLogic
        assert hasattr(ExitLogic, 'calculate_pnl')
    
    # Config validation
    
    def test_v3_config_valid_json(self):
        """Verify V3 config.json is valid JSON."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "config.json"
        with open(path) as f:
            config = json.load(f)
        assert "plugin_id" in config
        assert config["plugin_id"] == "combined_v3"
    
    # Logic routing tests
    
    def test_v3_logic_routing(self):
        """Verify V3 logic routing works correctly."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        # Create mock plugin
        mock_service_api = Mock()
        plugin = CombinedV3Plugin("combined_v3", {}, mock_service_api)
        
        # Test routing
        class MockAlert:
            tf = "5"
        
        assert plugin._route_to_logic(MockAlert()) == "LOGIC1"
        
        MockAlert.tf = "15"
        assert plugin._route_to_logic(MockAlert()) == "LOGIC2"
        
        MockAlert.tf = "1H"
        assert plugin._route_to_logic(MockAlert()) == "LOGIC3"


# ============================================================================
# PHASE 5: V6 Plugin Implementation Tests
# ============================================================================

class TestPhase5V6PluginImplementation:
    """Tests for Phase 5: V6 Plugin Implementation."""
    
    # File existence tests
    
    def test_v6_plugin_exists(self):
        """Verify V6 plugin.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "plugin.py"
        assert path.exists(), f"V6 plugin.py not found at {path}"
    
    def test_v6_config_exists(self):
        """Verify V6 config.json exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "config.json"
        assert path.exists(), f"V6 config.json not found at {path}"
    
    def test_v6_alert_handlers_exists(self):
        """Verify V6 alert_handlers.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "alert_handlers.py"
        assert path.exists(), f"V6 alert_handlers.py not found at {path}"
    
    def test_v6_timeframe_strategies_exists(self):
        """Verify V6 timeframe_strategies.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "timeframe_strategies.py"
        assert path.exists(), f"V6 timeframe_strategies.py not found at {path}"
    
    def test_v6_adx_integration_exists(self):
        """Verify V6 adx_integration.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "adx_integration.py"
        assert path.exists(), f"V6 adx_integration.py not found at {path}"
    
    def test_v6_momentum_integration_exists(self):
        """Verify V6 momentum_integration.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "momentum_integration.py"
        assert path.exists(), f"V6 momentum_integration.py not found at {path}"
    
    def test_v6_init_exists(self):
        """Verify V6 __init__.py exists."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "__init__.py"
        assert path.exists(), f"V6 __init__.py not found at {path}"
    
    # Import tests
    
    def test_v6_plugin_imports(self):
        """Verify PriceActionV6Plugin can be imported."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        assert PriceActionV6Plugin is not None
    
    def test_v6_alert_handlers_imports(self):
        """Verify V6AlertHandlers can be imported."""
        from src.logic_plugins.price_action_v6.alert_handlers import V6AlertHandlers
        assert V6AlertHandlers is not None
    
    def test_v6_timeframe_strategies_imports(self):
        """Verify TimeframeStrategies can be imported."""
        from src.logic_plugins.price_action_v6.timeframe_strategies import TimeframeStrategies
        assert TimeframeStrategies is not None
    
    def test_v6_adx_integration_imports(self):
        """Verify ADXIntegration can be imported."""
        from src.logic_plugins.price_action_v6.adx_integration import ADXIntegration
        assert ADXIntegration is not None
    
    def test_v6_momentum_integration_imports(self):
        """Verify MomentumIntegration can be imported."""
        from src.logic_plugins.price_action_v6.momentum_integration import MomentumIntegration
        assert MomentumIntegration is not None
    
    # Structure tests - PriceActionV6Plugin
    
    def test_v6_plugin_has_timeframes(self):
        """Verify PriceActionV6Plugin has TIMEFRAMES."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        assert hasattr(PriceActionV6Plugin, 'TIMEFRAMES')
        assert "1M" in PriceActionV6Plugin.TIMEFRAMES
        assert "5M" in PriceActionV6Plugin.TIMEFRAMES
        assert "15M" in PriceActionV6Plugin.TIMEFRAMES
        assert "1H" in PriceActionV6Plugin.TIMEFRAMES
    
    def test_v6_plugin_has_entry_alerts(self):
        """Verify PriceActionV6Plugin has ENTRY_ALERTS."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        assert hasattr(PriceActionV6Plugin, 'ENTRY_ALERTS')
        assert len(PriceActionV6Plugin.ENTRY_ALERTS) == 7
    
    def test_v6_plugin_has_exit_alerts(self):
        """Verify PriceActionV6Plugin has EXIT_ALERTS."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        assert hasattr(PriceActionV6Plugin, 'EXIT_ALERTS')
        assert len(PriceActionV6Plugin.EXIT_ALERTS) == 3
    
    def test_v6_plugin_has_info_alerts(self):
        """Verify PriceActionV6Plugin has INFO_ALERTS."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        assert hasattr(PriceActionV6Plugin, 'INFO_ALERTS')
        assert len(PriceActionV6Plugin.INFO_ALERTS) == 4
    
    def test_v6_plugin_total_14_alerts(self):
        """Verify V6 plugin has exactly 14 alert types."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        total = len(PriceActionV6Plugin.ENTRY_ALERTS) + \
                len(PriceActionV6Plugin.EXIT_ALERTS) + \
                len(PriceActionV6Plugin.INFO_ALERTS)
        assert total == 14, f"Expected 14 alerts, got {total}"
    
    def test_v6_plugin_has_timeframe_settings(self):
        """Verify PriceActionV6Plugin has TIMEFRAME_SETTINGS."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        assert hasattr(PriceActionV6Plugin, 'TIMEFRAME_SETTINGS')
        assert "1M" in PriceActionV6Plugin.TIMEFRAME_SETTINGS
        assert "5M" in PriceActionV6Plugin.TIMEFRAME_SETTINGS
        assert "15M" in PriceActionV6Plugin.TIMEFRAME_SETTINGS
        assert "1H" in PriceActionV6Plugin.TIMEFRAME_SETTINGS
    
    # Structure tests - V6AlertHandlers
    
    def test_alert_handlers_has_14_handlers(self):
        """Verify V6AlertHandlers has 14 handlers."""
        from src.logic_plugins.price_action_v6.alert_handlers import V6AlertHandlers
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        handlers = V6AlertHandlers(mock_plugin)
        
        assert len(handlers.handlers) == 14
    
    def test_alert_handlers_has_route_alert(self):
        """Verify V6AlertHandlers has route_alert method."""
        from src.logic_plugins.price_action_v6.alert_handlers import V6AlertHandlers
        assert hasattr(V6AlertHandlers, 'route_alert')
    
    def test_alert_handlers_entry_handlers(self):
        """Verify V6AlertHandlers has all entry handlers."""
        from src.logic_plugins.price_action_v6.alert_handlers import V6AlertHandlers
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        handlers = V6AlertHandlers(mock_plugin)
        
        entry_handlers = [
            "PA_Breakout_Entry",
            "PA_Pullback_Entry",
            "PA_Reversal_Entry",
            "PA_Momentum_Entry",
            "PA_Support_Bounce",
            "PA_Resistance_Rejection",
            "PA_Trend_Continuation"
        ]
        
        for handler_name in entry_handlers:
            assert handler_name in handlers.handlers, f"Missing handler: {handler_name}"
    
    def test_alert_handlers_exit_handlers(self):
        """Verify V6AlertHandlers has all exit handlers."""
        from src.logic_plugins.price_action_v6.alert_handlers import V6AlertHandlers
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        handlers = V6AlertHandlers(mock_plugin)
        
        exit_handlers = [
            "PA_Exit_Signal",
            "PA_Reversal_Exit",
            "PA_Target_Hit"
        ]
        
        for handler_name in exit_handlers:
            assert handler_name in handlers.handlers, f"Missing handler: {handler_name}"
    
    def test_alert_handlers_info_handlers(self):
        """Verify V6AlertHandlers has all info handlers."""
        from src.logic_plugins.price_action_v6.alert_handlers import V6AlertHandlers
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        handlers = V6AlertHandlers(mock_plugin)
        
        info_handlers = [
            "PA_Trend_Pulse",
            "PA_Volatility_Alert",
            "PA_Session_Open",
            "PA_Session_Close"
        ]
        
        for handler_name in info_handlers:
            assert handler_name in handlers.handlers, f"Missing handler: {handler_name}"
    
    # Structure tests - TimeframeStrategies
    
    def test_timeframe_strategies_has_4_strategies(self):
        """Verify TimeframeStrategies has 4 strategies."""
        from src.logic_plugins.price_action_v6.timeframe_strategies import TimeframeStrategies
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        strategies = TimeframeStrategies(mock_plugin)
        
        assert len(strategies.strategies) == 4
    
    def test_timeframe_strategies_1m(self):
        """Verify 1M strategy exists and has correct settings."""
        from src.logic_plugins.price_action_v6.timeframe_strategies import TimeframeStrategies
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        strategies = TimeframeStrategies(mock_plugin)
        
        strategy = strategies.get_strategy("1M")
        assert strategy is not None
        assert strategy.settings["name"] == "Scalping"
        assert strategy.settings["dual_orders"] == False
        assert strategy.settings["sl_multiplier"] == 0.5
    
    def test_timeframe_strategies_5m(self):
        """Verify 5M strategy exists and has correct settings."""
        from src.logic_plugins.price_action_v6.timeframe_strategies import TimeframeStrategies
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        strategies = TimeframeStrategies(mock_plugin)
        
        strategy = strategies.get_strategy("5M")
        assert strategy is not None
        assert strategy.settings["name"] == "Intraday"
        assert strategy.settings["dual_orders"] == False
        assert strategy.settings["sl_multiplier"] == 1.0
    
    def test_timeframe_strategies_15m(self):
        """Verify 15M strategy exists and has correct settings."""
        from src.logic_plugins.price_action_v6.timeframe_strategies import TimeframeStrategies
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        strategies = TimeframeStrategies(mock_plugin)
        
        strategy = strategies.get_strategy("15M")
        assert strategy is not None
        assert strategy.settings["name"] == "Swing"
        assert strategy.settings["dual_orders"] == True
        assert strategy.settings["sl_multiplier"] == 1.5
    
    def test_timeframe_strategies_1h(self):
        """Verify 1H strategy exists and has correct settings."""
        from src.logic_plugins.price_action_v6.timeframe_strategies import TimeframeStrategies
        
        mock_plugin = Mock()
        mock_plugin.service_api = None
        strategies = TimeframeStrategies(mock_plugin)
        
        strategy = strategies.get_strategy("1H")
        assert strategy is not None
        assert strategy.settings["name"] == "Position"
        assert strategy.settings["dual_orders"] == True
        assert strategy.settings["sl_multiplier"] == 2.0
    
    # Structure tests - ADXIntegration
    
    def test_adx_integration_has_get_current_adx(self):
        """Verify ADXIntegration has get_current_adx method."""
        from src.logic_plugins.price_action_v6.adx_integration import ADXIntegration
        assert hasattr(ADXIntegration, 'get_current_adx')
    
    def test_adx_integration_has_check_adx_filter(self):
        """Verify ADXIntegration has check_adx_filter method."""
        from src.logic_plugins.price_action_v6.adx_integration import ADXIntegration
        assert hasattr(ADXIntegration, 'check_adx_filter')
    
    def test_adx_integration_has_thresholds(self):
        """Verify ADXIntegration has threshold constants."""
        from src.logic_plugins.price_action_v6.adx_integration import ADXIntegration
        assert hasattr(ADXIntegration, 'WEAK_TREND')
        assert hasattr(ADXIntegration, 'STRONG_TREND')
        assert ADXIntegration.WEAK_TREND == 20
        assert ADXIntegration.STRONG_TREND == 30
    
    def test_adx_integration_has_entry_thresholds(self):
        """Verify ADXIntegration has ENTRY_THRESHOLDS."""
        from src.logic_plugins.price_action_v6.adx_integration import ADXIntegration
        assert hasattr(ADXIntegration, 'ENTRY_THRESHOLDS')
        assert "breakout" in ADXIntegration.ENTRY_THRESHOLDS
        assert "momentum" in ADXIntegration.ENTRY_THRESHOLDS
    
    # Structure tests - MomentumIntegration
    
    def test_momentum_integration_has_get_momentum(self):
        """Verify MomentumIntegration has get_momentum method."""
        from src.logic_plugins.price_action_v6.momentum_integration import MomentumIntegration
        assert hasattr(MomentumIntegration, 'get_momentum')
    
    def test_momentum_integration_has_check_momentum_filter(self):
        """Verify MomentumIntegration has check_momentum_filter method."""
        from src.logic_plugins.price_action_v6.momentum_integration import MomentumIntegration
        assert hasattr(MomentumIntegration, 'check_momentum_filter')
    
    def test_momentum_integration_has_is_overbought(self):
        """Verify MomentumIntegration has is_overbought method."""
        from src.logic_plugins.price_action_v6.momentum_integration import MomentumIntegration
        assert hasattr(MomentumIntegration, 'is_overbought')
    
    def test_momentum_integration_has_is_oversold(self):
        """Verify MomentumIntegration has is_oversold method."""
        from src.logic_plugins.price_action_v6.momentum_integration import MomentumIntegration
        assert hasattr(MomentumIntegration, 'is_oversold')
    
    def test_momentum_integration_has_rsi_thresholds(self):
        """Verify MomentumIntegration has RSI thresholds."""
        from src.logic_plugins.price_action_v6.momentum_integration import MomentumIntegration
        assert hasattr(MomentumIntegration, 'RSI_OVERSOLD')
        assert hasattr(MomentumIntegration, 'RSI_OVERBOUGHT')
        assert MomentumIntegration.RSI_OVERSOLD == 30
        assert MomentumIntegration.RSI_OVERBOUGHT == 70
    
    # Config validation
    
    def test_v6_config_valid_json(self):
        """Verify V6 config.json is valid JSON."""
        path = PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "config.json"
        with open(path) as f:
            config = json.load(f)
        assert "plugin_id" in config
        assert config["plugin_id"] == "price_action_v6"


# ============================================================================
# PHASE 6: Integration Tests
# ============================================================================

class TestPhase6Integration:
    """Tests for Phase 6: Integration and Documentation."""
    
    def test_all_telegram_bots_exist(self):
        """Verify all 3 Telegram bot files exist and have correct classes."""
        # Using AST-based checking to avoid import chain issues
        telegram_files = [
            (PROJECT_ROOT / "src" / "telegram" / "controller_bot.py", "ControllerBot"),
            (PROJECT_ROOT / "src" / "telegram" / "notification_bot.py", "NotificationBot"),
            (PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py", "AnalyticsBot"),
            (PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py", "MultiTelegramManager")
        ]
        
        for path, class_name in telegram_files:
            assert path.exists(), f"File not found: {path}"
            assert check_class_exists(path, class_name), f"Class {class_name} not found in {path}"
    
    def test_all_services_importable(self):
        """Verify all 4 services can be imported together."""
        from src.services.order_execution import OrderExecutionService
        from src.services.profit_booking import ProfitBookingService
        from src.services.risk_management import RiskManagementService
        from src.services.trend_monitor import TrendMonitorService
        
        assert OrderExecutionService is not None
        assert ProfitBookingService is not None
        assert RiskManagementService is not None
        assert TrendMonitorService is not None
    
    def test_v3_plugin_complete(self):
        """Verify V3 plugin is complete with all modules."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        from src.logic_plugins.combined_v3.entry_logic import EntryLogic
        from src.logic_plugins.combined_v3.exit_logic import ExitLogic
        
        assert CombinedV3Plugin is not None
        assert EntryLogic is not None
        assert ExitLogic is not None
    
    def test_v6_plugin_complete(self):
        """Verify V6 plugin is complete with all modules."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        from src.logic_plugins.price_action_v6.alert_handlers import V6AlertHandlers
        from src.logic_plugins.price_action_v6.timeframe_strategies import TimeframeStrategies
        from src.logic_plugins.price_action_v6.adx_integration import ADXIntegration
        from src.logic_plugins.price_action_v6.momentum_integration import MomentumIntegration
        
        assert PriceActionV6Plugin is not None
        assert V6AlertHandlers is not None
        assert TimeframeStrategies is not None
        assert ADXIntegration is not None
        assert MomentumIntegration is not None
    
    def test_plugin_system_integration(self):
        """Verify plugin system can load both V3 and V6 plugins."""
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        # Both plugins should inherit from BaseLogicPlugin
        assert issubclass(CombinedV3Plugin, BaseLogicPlugin)
        assert issubclass(PriceActionV6Plugin, BaseLogicPlugin)
    
    def test_v3_plugin_instantiation_with_services(self):
        """Verify V3 plugin can be instantiated with mock services."""
        from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin
        
        mock_service_api = Mock()
        mock_service_api.order_execution = Mock()
        mock_service_api.profit_booking = Mock()
        mock_service_api.risk_management = Mock()
        mock_service_api.trend_monitor = Mock()
        
        plugin = CombinedV3Plugin("combined_v3", {}, mock_service_api)
        assert plugin is not None
        assert plugin.plugin_id == "combined_v3"
    
    def test_v6_plugin_instantiation_with_services(self):
        """Verify V6 plugin can be instantiated with mock services."""
        from src.logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        mock_service_api = Mock()
        mock_service_api.order_execution = Mock()
        mock_service_api.profit_booking = Mock()
        mock_service_api.risk_management = Mock()
        mock_service_api.trend_monitor = Mock()
        
        plugin = PriceActionV6Plugin("price_action_v6", {}, mock_service_api)
        assert plugin is not None
        assert plugin.plugin_id == "price_action_v6"
    
    def test_directory_structure_complete(self):
        """Verify complete directory structure exists."""
        required_dirs = [
            PROJECT_ROOT / "src" / "telegram",
            PROJECT_ROOT / "src" / "services",
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6",
            PROJECT_ROOT / "src" / "core" / "plugin_system"
        ]
        
        for dir_path in required_dirs:
            assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_all_configs_valid(self):
        """Verify all config files are valid JSON."""
        config_files = [
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "config.json",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "config.json"
        ]
        
        for config_path in config_files:
            assert config_path.exists(), f"Config not found: {config_path}"
            with open(config_path) as f:
                config = json.load(f)
            assert "plugin_id" in config


# ============================================================================
# Summary Test
# ============================================================================

class TestDocument03Summary:
    """Summary tests for Document 03 implementation."""
    
    def test_phase_2_complete(self):
        """Verify Phase 2 (Multi-Telegram) is complete."""
        files = [
            PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py",
            PROJECT_ROOT / "src" / "telegram" / "controller_bot.py",
            PROJECT_ROOT / "src" / "telegram" / "notification_bot.py",
            PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py"
        ]
        for f in files:
            assert f.exists(), f"Phase 2 file missing: {f}"
    
    def test_phase_3_complete(self):
        """Verify Phase 3 (Service API) is complete."""
        files = [
            PROJECT_ROOT / "src" / "services" / "order_execution.py",
            PROJECT_ROOT / "src" / "services" / "profit_booking.py",
            PROJECT_ROOT / "src" / "services" / "risk_management.py",
            PROJECT_ROOT / "src" / "services" / "trend_monitor.py"
        ]
        for f in files:
            assert f.exists(), f"Phase 3 file missing: {f}"
    
    def test_phase_4_complete(self):
        """Verify Phase 4 (V3 Migration) is complete."""
        files = [
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "plugin.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "config.json",
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "entry_logic.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "exit_logic.py"
        ]
        for f in files:
            assert f.exists(), f"Phase 4 file missing: {f}"
    
    def test_phase_5_complete(self):
        """Verify Phase 5 (V6 Implementation) is complete."""
        files = [
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "plugin.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "config.json",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "alert_handlers.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "timeframe_strategies.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "adx_integration.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "momentum_integration.py"
        ]
        for f in files:
            assert f.exists(), f"Phase 5 file missing: {f}"
    
    def test_total_component_count(self):
        """Verify total component count matches Document 03 requirements."""
        # Phase 2: 4 files (manager + 3 bots)
        # Phase 3: 4 files (4 services)
        # Phase 4: 4 files (plugin, config, entry, exit)
        # Phase 5: 6 files (plugin, config, handlers, strategies, adx, momentum)
        # Total: 18 core files
        
        core_files = [
            # Phase 2
            PROJECT_ROOT / "src" / "telegram" / "multi_telegram_manager.py",
            PROJECT_ROOT / "src" / "telegram" / "controller_bot.py",
            PROJECT_ROOT / "src" / "telegram" / "notification_bot.py",
            PROJECT_ROOT / "src" / "telegram" / "analytics_bot.py",
            # Phase 3
            PROJECT_ROOT / "src" / "services" / "order_execution.py",
            PROJECT_ROOT / "src" / "services" / "profit_booking.py",
            PROJECT_ROOT / "src" / "services" / "risk_management.py",
            PROJECT_ROOT / "src" / "services" / "trend_monitor.py",
            # Phase 4
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "plugin.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "config.json",
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "entry_logic.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "combined_v3" / "exit_logic.py",
            # Phase 5
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "plugin.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "config.json",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "alert_handlers.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "timeframe_strategies.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "adx_integration.py",
            PROJECT_ROOT / "src" / "logic_plugins" / "price_action_v6" / "momentum_integration.py"
        ]
        
        existing_count = sum(1 for f in core_files if f.exists())
        assert existing_count == 18, f"Expected 18 core files, found {existing_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
