"""
Test Suite for Document 11: Configuration Templates.

Tests configuration validation schemas, defaults management,
environment variable support, and all plugin configuration templates.

Author: Devin AI
Date: 2026-01-12
"""

import os
import sys
import json
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestConfigPackageStructure(unittest.TestCase):
    """Test config package structure and imports."""
    
    def test_config_package_exists(self):
        """Test that config package exists."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'config')
        self.assertTrue(os.path.exists(config_path))
    
    def test_schemas_module_exists(self):
        """Test that schemas module exists."""
        schemas_path = os.path.join(PROJECT_ROOT, 'src', 'config', 'schemas.py')
        self.assertTrue(os.path.exists(schemas_path))
    
    def test_defaults_module_exists(self):
        """Test that defaults module exists."""
        defaults_path = os.path.join(PROJECT_ROOT, 'src', 'config', 'defaults.py')
        self.assertTrue(os.path.exists(defaults_path))
    
    def test_init_module_exists(self):
        """Test that __init__.py exists."""
        init_path = os.path.join(PROJECT_ROOT, 'src', 'config', '__init__.py')
        self.assertTrue(os.path.exists(init_path))
    
    def test_import_schemas(self):
        """Test that schemas module can be imported."""
        from config import schemas
        self.assertIsNotNone(schemas)
    
    def test_import_defaults(self):
        """Test that defaults module can be imported."""
        from config import defaults
        self.assertIsNotNone(defaults)
    
    def test_import_config_package(self):
        """Test that config package can be imported."""
        import config
        self.assertIsNotNone(config)


class TestConfigValidationSchemas(unittest.TestCase):
    """Test configuration validation schemas."""
    
    def test_config_validation_error_exists(self):
        """Test ConfigValidationError exception exists."""
        from config.schemas import ConfigValidationError
        self.assertTrue(issubclass(ConfigValidationError, Exception))
    
    def test_plugin_type_enum(self):
        """Test PluginType enum values."""
        from config.schemas import PluginType
        self.assertEqual(PluginType.V3_COMBINED.value, "V3_COMBINED")
        self.assertEqual(PluginType.V6_PRICE_ACTION.value, "V6_PRICE_ACTION")
    
    def test_logic_route_enum(self):
        """Test LogicRoute enum values."""
        from config.schemas import LogicRoute
        self.assertEqual(LogicRoute.LOGIC1.value, "LOGIC1")
        self.assertEqual(LogicRoute.LOGIC2.value, "LOGIC2")
        self.assertEqual(LogicRoute.LOGIC3.value, "LOGIC3")
    
    def test_order_routing_enum(self):
        """Test OrderRouting enum values."""
        from config.schemas import OrderRouting
        self.assertEqual(OrderRouting.ORDER_A_ONLY.value, "ORDER_A_ONLY")
        self.assertEqual(OrderRouting.ORDER_B_ONLY.value, "ORDER_B_ONLY")
        self.assertEqual(OrderRouting.DUAL_ORDERS.value, "DUAL_ORDERS")
    
    def test_adx_strength_enum(self):
        """Test ADXStrength enum values."""
        from config.schemas import ADXStrength
        self.assertEqual(ADXStrength.WEAK.value, "WEAK")
        self.assertEqual(ADXStrength.MODERATE.value, "MODERATE")
        self.assertEqual(ADXStrength.STRONG.value, "STRONG")
        self.assertEqual(ADXStrength.VERY_STRONG.value, "VERY_STRONG")


class TestPluginSystemConfig(unittest.TestCase):
    """Test PluginSystemConfig dataclass."""
    
    def test_plugin_system_config_creation(self):
        """Test PluginSystemConfig creation with defaults."""
        from config.schemas import PluginSystemConfig
        config = PluginSystemConfig()
        self.assertTrue(config.enabled)
        self.assertEqual(config.plugin_directory, "src/logic_plugins")
        self.assertTrue(config.auto_discover)
        self.assertEqual(config.max_plugin_execution_time, 5.0)
        self.assertTrue(config.dual_core_mode)
    
    def test_plugin_system_config_validation_valid(self):
        """Test PluginSystemConfig validation with valid data."""
        from config.schemas import PluginSystemConfig
        config = PluginSystemConfig(max_plugin_execution_time=10.0)
        self.assertTrue(config.validate())
    
    def test_plugin_system_config_validation_invalid(self):
        """Test PluginSystemConfig validation with invalid data."""
        from config.schemas import PluginSystemConfig, ConfigValidationError
        config = PluginSystemConfig(max_plugin_execution_time=-1.0)
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestSymbolConfig(unittest.TestCase):
    """Test SymbolConfig dataclass."""
    
    def test_symbol_config_creation(self):
        """Test SymbolConfig creation with defaults."""
        from config.schemas import SymbolConfig
        config = SymbolConfig()
        self.assertEqual(config.symbol_name, "XAUUSD")
        self.assertEqual(config.digits, 2)
        self.assertEqual(config.min_lot, 0.01)
        self.assertEqual(config.max_lot, 50.0)
    
    def test_symbol_config_validation_valid(self):
        """Test SymbolConfig validation with valid data."""
        from config.schemas import SymbolConfig
        config = SymbolConfig(symbol_name="EURUSD", digits=5)
        self.assertTrue(config.validate())
    
    def test_symbol_config_validation_invalid_digits(self):
        """Test SymbolConfig validation with invalid digits."""
        from config.schemas import SymbolConfig, ConfigValidationError
        config = SymbolConfig(digits=10)
        with self.assertRaises(ConfigValidationError):
            config.validate()
    
    def test_symbol_config_validation_invalid_lot(self):
        """Test SymbolConfig validation with invalid lot sizes."""
        from config.schemas import SymbolConfig, ConfigValidationError
        config = SymbolConfig(min_lot=0.0)
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestBotConfig(unittest.TestCase):
    """Test BotConfig dataclass."""
    
    def test_bot_config_creation(self):
        """Test BotConfig creation with defaults."""
        from config.schemas import BotConfig
        config = BotConfig()
        self.assertTrue(config.enabled)
        self.assertEqual(config.lot_multiplier, 1.0)
        self.assertEqual(config.risk_per_trade, 1.5)
        self.assertEqual(config.logic_route, "LOGIC1")
    
    def test_bot_config_validation_valid(self):
        """Test BotConfig validation with valid data."""
        from config.schemas import BotConfig
        config = BotConfig(logic_route="LOGIC2", lot_multiplier=1.25)
        self.assertTrue(config.validate())
    
    def test_bot_config_validation_invalid_route(self):
        """Test BotConfig validation with invalid logic route."""
        from config.schemas import BotConfig, ConfigValidationError
        config = BotConfig(logic_route="LOGIC4")
        with self.assertRaises(ConfigValidationError):
            config.validate()
    
    def test_bot_config_validation_invalid_risk(self):
        """Test BotConfig validation with invalid risk."""
        from config.schemas import BotConfig, ConfigValidationError
        config = BotConfig(risk_per_trade=15.0)
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestMainConfig(unittest.TestCase):
    """Test MainConfig dataclass."""
    
    def test_main_config_creation(self):
        """Test MainConfig creation."""
        from config.schemas import MainConfig
        config = MainConfig(telegram_chat_id="123456")
        self.assertEqual(config.telegram_chat_id, "123456")
        self.assertEqual(config.mt5_server, "MetaQuotesDemo-MT5")
    
    def test_main_config_from_dict(self):
        """Test MainConfig creation from dictionary."""
        from config.schemas import MainConfig
        data = {
            "telegram_chat_id": "789012",
            "mt5_server": "CustomServer",
            "plugins": {"test": {"enabled": True}}
        }
        config = MainConfig.from_dict(data)
        self.assertEqual(config.telegram_chat_id, "789012")
        self.assertEqual(config.mt5_server, "CustomServer")
        self.assertIn("test", config.plugins)
    
    def test_main_config_validation_valid(self):
        """Test MainConfig validation with valid data."""
        from config.schemas import MainConfig
        config = MainConfig(telegram_chat_id="123456")
        self.assertTrue(config.validate())
    
    def test_main_config_validation_invalid(self):
        """Test MainConfig validation with missing chat_id."""
        from config.schemas import MainConfig, ConfigValidationError
        config = MainConfig()
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestV3PluginConfig(unittest.TestCase):
    """Test V3 plugin configuration schemas."""
    
    def test_v3_plugin_config_creation(self):
        """Test V3PluginConfig creation."""
        from config.schemas import V3PluginConfig
        config = V3PluginConfig()
        self.assertEqual(config.plugin_id, "combined_v3")
        self.assertEqual(config.version, "1.0.0")
        self.assertTrue(config.enabled)
        self.assertFalse(config.shadow_mode)
    
    def test_v3_plugin_config_from_dict(self):
        """Test V3PluginConfig creation from dictionary."""
        from config.schemas import V3PluginConfig
        data = {
            "plugin_id": "combined_v3",
            "version": "2.0.0",
            "enabled": False,
            "metadata": {"name": "Test Plugin"}
        }
        config = V3PluginConfig.from_dict(data)
        self.assertEqual(config.version, "2.0.0")
        self.assertFalse(config.enabled)
        self.assertEqual(config.metadata["name"], "Test Plugin")
    
    def test_v3_plugin_config_validation(self):
        """Test V3PluginConfig validation."""
        from config.schemas import V3PluginConfig
        config = V3PluginConfig(plugin_id="combined_v3")
        self.assertTrue(config.validate())
    
    def test_signal_handling_config(self):
        """Test SignalHandlingConfig defaults."""
        from config.schemas import SignalHandlingConfig
        config = SignalHandlingConfig()
        self.assertIn("Institutional_Launchpad", config.entry_signals)
        self.assertIn("Exit_Bullish", config.exit_signals)
        self.assertTrue(config.signal_12_enabled)
        self.assertEqual(config.signal_12_name, "Sideways_Breakout")
    
    def test_routing_matrix_config(self):
        """Test RoutingMatrixConfig defaults."""
        from config.schemas import RoutingMatrixConfig
        config = RoutingMatrixConfig()
        self.assertEqual(config.priority_1_overrides["Screener"], "LOGIC3")
        self.assertEqual(config.priority_2_timeframe_routing["5"], "LOGIC1")
        self.assertEqual(config.logic_multipliers["LOGIC1"], 1.25)
        self.assertEqual(config.logic_multipliers["LOGIC2"], 1.0)
        self.assertEqual(config.logic_multipliers["LOGIC3"], 0.625)
    
    def test_dual_order_system_config(self):
        """Test DualOrderSystemConfig defaults."""
        from config.schemas import DualOrderSystemConfig
        config = DualOrderSystemConfig()
        self.assertTrue(config.enabled)
        self.assertEqual(config.order_split_ratio, 0.5)
    
    def test_mtf_4_pillar_config(self):
        """Test MTF4PillarConfig defaults."""
        from config.schemas import MTF4PillarConfig
        config = MTF4PillarConfig()
        self.assertEqual(len(config.pillars), 4)
        self.assertIn("15m", config.pillars)
        self.assertIn("1h", config.pillars)
        self.assertIn("4h", config.pillars)
        self.assertIn("1d", config.pillars)
        self.assertEqual(config.min_aligned_for_entry, 3)
    
    def test_mtf_4_pillar_validation_invalid(self):
        """Test MTF4PillarConfig validation with invalid pillars."""
        from config.schemas import MTF4PillarConfig, ConfigValidationError
        config = MTF4PillarConfig(pillars=["15m", "1h"])
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestV6PluginConfig(unittest.TestCase):
    """Test V6 plugin configuration schemas."""
    
    def test_v6_plugin_config_creation(self):
        """Test V6PluginConfig creation."""
        from config.schemas import V6PluginConfig
        config = V6PluginConfig(plugin_id="price_action_1m")
        self.assertEqual(config.plugin_id, "price_action_1m")
        self.assertTrue(config.enabled)
    
    def test_v6_plugin_config_from_dict(self):
        """Test V6PluginConfig creation from dictionary."""
        from config.schemas import V6PluginConfig
        data = {
            "plugin_id": "price_action_5m",
            "metadata": {"timeframe": "5m"},
            "settings": {"order_routing": "DUAL_ORDERS"}
        }
        config = V6PluginConfig.from_dict(data)
        self.assertEqual(config.plugin_id, "price_action_5m")
        self.assertEqual(config.settings["order_routing"], "DUAL_ORDERS")
    
    def test_v6_entry_conditions(self):
        """Test V6EntryConditions defaults."""
        from config.schemas import V6EntryConditions
        config = V6EntryConditions()
        self.assertEqual(config.adx_threshold, 20)
        self.assertEqual(config.adx_strength_required, "MODERATE")
        self.assertEqual(config.confidence_threshold, 70)
    
    def test_v6_entry_conditions_validation_invalid_adx(self):
        """Test V6EntryConditions validation with invalid ADX."""
        from config.schemas import V6EntryConditions, ConfigValidationError
        config = V6EntryConditions(adx_threshold=150)
        with self.assertRaises(ConfigValidationError):
            config.validate()
    
    def test_v6_order_configuration(self):
        """Test V6OrderConfiguration defaults."""
        from config.schemas import V6OrderConfiguration
        config = V6OrderConfiguration()
        self.assertTrue(config.use_order_a)
        self.assertFalse(config.use_order_b)
        self.assertEqual(config.target_level, "TP2")
    
    def test_trend_pulse_integration(self):
        """Test TrendPulseIntegration defaults."""
        from config.schemas import TrendPulseIntegration
        config = TrendPulseIntegration()
        self.assertTrue(config.enabled)
        self.assertTrue(config.require_pulse_alignment)
        self.assertEqual(config.min_bull_count_for_buy, 3)
        self.assertEqual(config.min_bear_count_for_sell, 3)
    
    def test_v6_exit_rules(self):
        """Test V6ExitRules defaults."""
        from config.schemas import V6ExitRules
        config = V6ExitRules()
        self.assertEqual(config.tp1_pips, 10)
        self.assertEqual(config.sl_pips, 15)
        self.assertFalse(config.use_trailing_stop)


class TestRiskManagementConfig(unittest.TestCase):
    """Test RiskManagementConfig dataclass."""
    
    def test_risk_management_config_creation(self):
        """Test RiskManagementConfig creation."""
        from config.schemas import RiskManagementConfig
        config = RiskManagementConfig()
        self.assertEqual(config.max_open_trades, 5)
        self.assertEqual(config.max_daily_trades, 10)
        self.assertEqual(config.daily_loss_limit, 500.0)
    
    def test_risk_management_validation_valid(self):
        """Test RiskManagementConfig validation with valid data."""
        from config.schemas import RiskManagementConfig
        config = RiskManagementConfig(max_open_trades=3, daily_loss_limit=300.0)
        self.assertTrue(config.validate())
    
    def test_risk_management_validation_invalid(self):
        """Test RiskManagementConfig validation with invalid data."""
        from config.schemas import RiskManagementConfig, ConfigValidationError
        config = RiskManagementConfig(max_open_trades=0)
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestNotificationsConfig(unittest.TestCase):
    """Test NotificationsConfig dataclass."""
    
    def test_notifications_config_creation(self):
        """Test NotificationsConfig creation."""
        from config.schemas import NotificationsConfig
        config = NotificationsConfig()
        self.assertTrue(config.notify_on_entry)
        self.assertTrue(config.notify_on_exit)
        self.assertEqual(config.telegram_bot, "controller")
    
    def test_notifications_config_validation_valid(self):
        """Test NotificationsConfig validation with valid bot."""
        from config.schemas import NotificationsConfig
        config = NotificationsConfig(telegram_bot="notification")
        self.assertTrue(config.validate())
    
    def test_notifications_config_validation_invalid(self):
        """Test NotificationsConfig validation with invalid bot."""
        from config.schemas import NotificationsConfig, ConfigValidationError
        config = NotificationsConfig(telegram_bot="invalid_bot")
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestDatabaseConfig(unittest.TestCase):
    """Test DatabaseConfig dataclass."""
    
    def test_database_config_creation(self):
        """Test DatabaseConfig creation."""
        from config.schemas import DatabaseConfig
        config = DatabaseConfig(path="data/test.db")
        self.assertEqual(config.path, "data/test.db")
        self.assertTrue(config.backup_enabled)
        self.assertTrue(config.sync_to_central)
    
    def test_database_config_validation_valid(self):
        """Test DatabaseConfig validation with valid data."""
        from config.schemas import DatabaseConfig
        config = DatabaseConfig(path="data/test.db", sync_interval_minutes=10)
        self.assertTrue(config.validate())
    
    def test_database_config_validation_invalid_path(self):
        """Test DatabaseConfig validation with missing path."""
        from config.schemas import DatabaseConfig, ConfigValidationError
        config = DatabaseConfig()
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestShadowModeSettings(unittest.TestCase):
    """Test ShadowModeSettings dataclass."""
    
    def test_shadow_mode_settings_creation(self):
        """Test ShadowModeSettings creation."""
        from config.schemas import ShadowModeSettings
        config = ShadowModeSettings()
        self.assertTrue(config.log_all_signals)
        self.assertTrue(config.simulate_order_placement)
        self.assertTrue(config.track_hypothetical_pnl)
        self.assertEqual(config.shadow_duration_hours, 72)
    
    def test_shadow_mode_validation_valid(self):
        """Test ShadowModeSettings validation with valid data."""
        from config.schemas import ShadowModeSettings
        config = ShadowModeSettings(shadow_duration_hours=48)
        self.assertTrue(config.validate())
    
    def test_shadow_mode_validation_invalid(self):
        """Test ShadowModeSettings validation with invalid duration."""
        from config.schemas import ShadowModeSettings, ConfigValidationError
        config = ShadowModeSettings(shadow_duration_hours=0)
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestEnvironmentConfig(unittest.TestCase):
    """Test EnvironmentConfig dataclass."""
    
    def test_environment_config_creation(self):
        """Test EnvironmentConfig creation."""
        from config.schemas import EnvironmentConfig
        config = EnvironmentConfig()
        self.assertEqual(config.environment, "development")
        self.assertFalse(config.debug_mode)
        self.assertEqual(config.log_level, "INFO")
    
    def test_environment_config_from_env(self):
        """Test EnvironmentConfig loading from environment."""
        from config.schemas import EnvironmentConfig
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "DEBUG_MODE": "true",
            "LOG_LEVEL": "DEBUG"
        }):
            config = EnvironmentConfig.from_env()
            self.assertEqual(config.environment, "production")
            self.assertTrue(config.debug_mode)
            self.assertEqual(config.log_level, "DEBUG")
    
    def test_environment_config_validation_valid(self):
        """Test EnvironmentConfig validation with valid data."""
        from config.schemas import EnvironmentConfig
        config = EnvironmentConfig(environment="production", log_level="WARNING")
        self.assertTrue(config.validate())
    
    def test_environment_config_validation_invalid_env(self):
        """Test EnvironmentConfig validation with invalid environment."""
        from config.schemas import EnvironmentConfig, ConfigValidationError
        config = EnvironmentConfig(environment="invalid")
        with self.assertRaises(ConfigValidationError):
            config.validate()


class TestConfigValidator(unittest.TestCase):
    """Test ConfigValidator utility class."""
    
    def test_validate_main_config(self):
        """Test main config validation."""
        from config.schemas import ConfigValidator
        config = {
            "telegram_chat_id": "123456",
            "plugin_system": {"enabled": True, "max_plugin_execution_time": 5.0},
            "plugins": {"test": {"enabled": True, "type": "V3_COMBINED"}},
            "symbol_config": {"XAUUSD": {"symbol_name": "XAUUSD", "digits": 2, "min_lot": 0.01, "max_lot": 50.0}},
            "bot_config": {"logic1": {"enabled": True, "lot_multiplier": 1.0, "risk_per_trade": 1.5, "logic_route": "LOGIC1"}}
        }
        self.assertTrue(ConfigValidator.validate_main_config(config))
    
    def test_validate_v3_config(self):
        """Test V3 config validation."""
        from config.schemas import ConfigValidator
        config = {
            "plugin_id": "combined_v3",
            "settings": {
                "signal_handling": {"entry_signals": ["test"]},
                "routing_matrix": {"logic_multipliers": {"LOGIC1": 1.25}},
                "dual_order_system": {"enabled": True, "order_split_ratio": 0.5},
                "mtf_4_pillar_system": {"pillars": ["15m", "1h", "4h", "1d"], "min_aligned_for_entry": 3},
                "position_sizing": {"base_risk_percentage": 1.5, "min_lot_size": 0.01, "max_lot_size": 1.0},
                "risk_management": {"max_open_trades": 5, "max_daily_trades": 10, "daily_loss_limit": 500.0, "max_symbol_exposure": 0.3}
            },
            "notifications": {"telegram_bot": "controller"},
            "database": {"path": "data/test.db", "sync_interval_minutes": 5}
        }
        self.assertTrue(ConfigValidator.validate_v3_config(config))
    
    def test_validate_v6_config(self):
        """Test V6 config validation."""
        from config.schemas import ConfigValidator
        config = {
            "plugin_id": "price_action_1m",
            "settings": {
                "order_routing": "ORDER_B_ONLY",
                "entry_conditions": {"adx_threshold": 20, "confidence_threshold": 80, "adx_strength_required": "MODERATE"},
                "order_configuration": {"use_order_a": False, "use_order_b": True, "target_level": "TP1", "split_ratio": 0.5},
                "risk_management": {"max_open_trades": 3, "max_daily_trades": 20, "daily_loss_limit": 200.0, "max_symbol_exposure": 0.3},
                "trend_pulse_integration": {"enabled": True, "min_bull_count_for_buy": 3, "min_bear_count_for_sell": 3},
                "exit_rules": {"tp1_pips": 10, "sl_pips": 15, "max_hold_time_minutes": 15}
            },
            "database": {"path": "data/test.db", "sync_interval_minutes": 5}
        }
        self.assertTrue(ConfigValidator.validate_v6_config(config))


class TestDefaultsManager(unittest.TestCase):
    """Test DefaultsManager class."""
    
    def test_get_main_config_defaults(self):
        """Test getting main config defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_main_config_defaults()
        self.assertIn("plugin_system", defaults)
        self.assertIn("plugins", defaults)
        self.assertIn("symbol_config", defaults)
        self.assertIn("bot_config", defaults)
    
    def test_get_v3_plugin_defaults(self):
        """Test getting V3 plugin defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v3_plugin_defaults()
        self.assertEqual(defaults["plugin_id"], "combined_v3")
        self.assertIn("metadata", defaults)
        self.assertIn("settings", defaults)
        self.assertIn("signal_handling", defaults["settings"])
        self.assertIn("routing_matrix", defaults["settings"])
        self.assertIn("dual_order_system", defaults["settings"])
        self.assertIn("mtf_4_pillar_system", defaults["settings"])
    
    def test_get_v6_1m_defaults(self):
        """Test getting V6 1M plugin defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_1m_defaults()
        self.assertEqual(defaults["plugin_id"], "price_action_1m")
        self.assertEqual(defaults["settings"]["order_routing"], "ORDER_B_ONLY")
        self.assertFalse(defaults["settings"]["order_configuration"]["use_order_a"])
        self.assertTrue(defaults["settings"]["order_configuration"]["use_order_b"])
    
    def test_get_v6_5m_defaults(self):
        """Test getting V6 5M plugin defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_5m_defaults()
        self.assertEqual(defaults["plugin_id"], "price_action_5m")
        self.assertEqual(defaults["settings"]["order_routing"], "DUAL_ORDERS")
        self.assertTrue(defaults["settings"]["order_configuration"]["use_order_a"])
        self.assertTrue(defaults["settings"]["order_configuration"]["use_order_b"])
    
    def test_get_v6_15m_defaults(self):
        """Test getting V6 15M plugin defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_15m_defaults()
        self.assertEqual(defaults["plugin_id"], "price_action_15m")
        self.assertEqual(defaults["settings"]["order_routing"], "ORDER_A_ONLY")
        self.assertTrue(defaults["settings"]["order_configuration"]["use_order_a"])
        self.assertFalse(defaults["settings"]["order_configuration"]["use_order_b"])
    
    def test_get_v6_1h_defaults(self):
        """Test getting V6 1H plugin defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_1h_defaults()
        self.assertEqual(defaults["plugin_id"], "price_action_1h")
        self.assertEqual(defaults["settings"]["order_routing"], "ORDER_A_ONLY")
        self.assertFalse(defaults["settings"]["trend_pulse_integration"]["enabled"])
    
    def test_get_v6_defaults_by_timeframe(self):
        """Test getting V6 defaults by timeframe."""
        from config.defaults import DefaultsManager
        defaults_1m = DefaultsManager.get_v6_defaults_by_timeframe("1m")
        self.assertEqual(defaults_1m["plugin_id"], "price_action_1m")
        
        defaults_5m = DefaultsManager.get_v6_defaults_by_timeframe("5m")
        self.assertEqual(defaults_5m["plugin_id"], "price_action_5m")
    
    def test_deep_merge(self):
        """Test deep merge functionality."""
        from config.defaults import DefaultsManager
        base = {"a": 1, "b": {"c": 2, "d": 3}}
        override = {"b": {"c": 10, "e": 5}}
        result = DefaultsManager.deep_merge(base, override)
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b"]["c"], 10)
        self.assertEqual(result["b"]["d"], 3)
        self.assertEqual(result["b"]["e"], 5)
    
    def test_apply_defaults(self):
        """Test applying defaults to partial config."""
        from config.defaults import DefaultsManager
        partial = {"plugin_id": "custom_v3", "enabled": False}
        result = DefaultsManager.apply_defaults(partial, "v3")
        self.assertEqual(result["plugin_id"], "custom_v3")
        self.assertFalse(result["enabled"])
        self.assertIn("metadata", result)
        self.assertIn("settings", result)
    
    def test_get_shadow_mode_defaults(self):
        """Test getting shadow mode defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_shadow_mode_defaults()
        self.assertTrue(defaults["log_all_signals"])
        self.assertTrue(defaults["simulate_order_placement"])
        self.assertEqual(defaults["shadow_duration_hours"], 72)
    
    def test_get_env_defaults(self):
        """Test getting environment defaults."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_env_defaults()
        self.assertEqual(defaults["ENVIRONMENT"], "development")
        self.assertEqual(defaults["DEBUG_MODE"], "false")
        self.assertEqual(defaults["LOG_LEVEL"], "INFO")


class TestEnvironmentVariableResolver(unittest.TestCase):
    """Test EnvironmentVariableResolver class."""
    
    def test_resolve_string_with_env_var(self):
        """Test resolving string with environment variable."""
        from config.defaults import EnvironmentVariableResolver
        with patch.dict(os.environ, {"TEST_TOKEN": "abc123"}):
            result = EnvironmentVariableResolver.resolve("${TEST_TOKEN}")
            self.assertEqual(result, "abc123")
    
    def test_resolve_string_without_env_var(self):
        """Test resolving string without environment variable."""
        from config.defaults import EnvironmentVariableResolver
        result = EnvironmentVariableResolver.resolve("plain_string")
        self.assertEqual(result, "plain_string")
    
    def test_resolve_dict(self):
        """Test resolving dictionary with environment variables."""
        from config.defaults import EnvironmentVariableResolver
        with patch.dict(os.environ, {"TOKEN": "secret123"}):
            config = {"token": "${TOKEN}", "name": "test"}
            result = EnvironmentVariableResolver.resolve(config)
            self.assertEqual(result["token"], "secret123")
            self.assertEqual(result["name"], "test")
    
    def test_resolve_nested_dict(self):
        """Test resolving nested dictionary."""
        from config.defaults import EnvironmentVariableResolver
        with patch.dict(os.environ, {"NESTED_VAR": "nested_value"}):
            config = {"outer": {"inner": "${NESTED_VAR}"}}
            result = EnvironmentVariableResolver.resolve(config)
            self.assertEqual(result["outer"]["inner"], "nested_value")
    
    def test_resolve_list(self):
        """Test resolving list with environment variables."""
        from config.defaults import EnvironmentVariableResolver
        with patch.dict(os.environ, {"LIST_VAR": "item1"}):
            config = ["${LIST_VAR}", "item2"]
            result = EnvironmentVariableResolver.resolve(config)
            self.assertEqual(result[0], "item1")
            self.assertEqual(result[1], "item2")
    
    def test_has_unresolved_vars(self):
        """Test checking for unresolved variables."""
        from config.defaults import EnvironmentVariableResolver
        config = {"token": "${MISSING_VAR}", "name": "test"}
        unresolved = EnvironmentVariableResolver.has_unresolved_vars(config)
        self.assertEqual(len(unresolved), 1)
        self.assertIn("MISSING_VAR", unresolved[0])


class TestConfigLoader(unittest.TestCase):
    """Test ConfigLoader class."""
    
    def test_config_loader_creation(self):
        """Test ConfigLoader creation."""
        from config.defaults import ConfigLoader
        loader = ConfigLoader(base_path="/test/path")
        self.assertEqual(loader.base_path, "/test/path")
    
    def test_generate_template_main(self):
        """Test generating main config template."""
        from config.defaults import ConfigLoader
        loader = ConfigLoader()
        template = loader.generate_template("main")
        self.assertIn("plugin_system", template)
        self.assertIn("plugins", template)
    
    def test_generate_template_v3(self):
        """Test generating V3 config template."""
        from config.defaults import ConfigLoader
        loader = ConfigLoader()
        template = loader.generate_template("v3")
        self.assertEqual(template["plugin_id"], "combined_v3")
    
    def test_generate_template_v6_1m(self):
        """Test generating V6 1M config template."""
        from config.defaults import ConfigLoader
        loader = ConfigLoader()
        template = loader.generate_template("v6_1m")
        self.assertEqual(template["plugin_id"], "price_action_1m")
        self.assertEqual(template["settings"]["order_routing"], "ORDER_B_ONLY")
    
    def test_generate_template_v6_5m(self):
        """Test generating V6 5M config template."""
        from config.defaults import ConfigLoader
        loader = ConfigLoader()
        template = loader.generate_template("v6_5m")
        self.assertEqual(template["plugin_id"], "price_action_5m")
        self.assertEqual(template["settings"]["order_routing"], "DUAL_ORDERS")
    
    def test_generate_template_v6_15m(self):
        """Test generating V6 15M config template."""
        from config.defaults import ConfigLoader
        loader = ConfigLoader()
        template = loader.generate_template("v6_15m")
        self.assertEqual(template["plugin_id"], "price_action_15m")
        self.assertEqual(template["settings"]["order_routing"], "ORDER_A_ONLY")
    
    def test_generate_template_v6_1h(self):
        """Test generating V6 1H config template."""
        from config.defaults import ConfigLoader
        loader = ConfigLoader()
        template = loader.generate_template("v6_1h")
        self.assertEqual(template["plugin_id"], "price_action_1h")
        self.assertEqual(template["settings"]["order_routing"], "ORDER_A_ONLY")


class TestEnvTemplateGeneration(unittest.TestCase):
    """Test environment template generation."""
    
    def test_generate_env_template(self):
        """Test generating .env template."""
        from config.defaults import generate_env_template
        template = generate_env_template()
        self.assertIn("TELEGRAM_CONTROLLER_TOKEN", template)
        self.assertIn("TELEGRAM_NOTIFICATION_TOKEN", template)
        self.assertIn("TELEGRAM_ANALYTICS_TOKEN", template)
        self.assertIn("MT5_PASSWORD", template)
        self.assertIn("DB_ENCRYPTION_KEY", template)
        self.assertIn("ENVIRONMENT", template)
        self.assertIn("DEBUG_MODE", template)
        self.assertIn("LOG_LEVEL", template)
    
    def test_generate_gitignore_additions(self):
        """Test generating .gitignore additions."""
        from config.defaults import generate_gitignore_additions
        additions = generate_gitignore_additions()
        self.assertIn(".env", additions)
        self.assertIn("*.db", additions)
        self.assertIn("*.log", additions)


class TestConfigTemplateFiles(unittest.TestCase):
    """Test configuration template files exist."""
    
    def test_main_config_template_exists(self):
        """Test main config template file exists."""
        template_path = os.path.join(PROJECT_ROOT, 'config', 'config.json.template')
        self.assertTrue(os.path.exists(template_path))
    
    def test_main_config_template_valid_json(self):
        """Test main config template is valid JSON."""
        template_path = os.path.join(PROJECT_ROOT, 'config', 'config.json.template')
        with open(template_path, 'r') as f:
            config = json.load(f)
        self.assertIn("plugin_system", config)
        self.assertIn("plugins", config)
    
    def test_v3_config_template_exists(self):
        """Test V3 config template file exists."""
        template_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'combined_v3', 'config.json.template')
        self.assertTrue(os.path.exists(template_path))
    
    def test_v3_config_template_valid_json(self):
        """Test V3 config template is valid JSON."""
        template_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'combined_v3', 'config.json.template')
        with open(template_path, 'r') as f:
            config = json.load(f)
        self.assertEqual(config["plugin_id"], "combined_v3")
        self.assertIn("settings", config)
    
    def test_v6_1m_config_exists(self):
        """Test V6 1M config file exists."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_1m', 'config.json')
        self.assertTrue(os.path.exists(config_path))
    
    def test_v6_1m_config_valid_json(self):
        """Test V6 1M config is valid JSON with ORDER_B_ONLY."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_1m', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.assertEqual(config["plugin_id"], "price_action_1m")
        self.assertEqual(config["settings"]["order_routing"], "ORDER_B_ONLY")
    
    def test_v6_5m_config_exists(self):
        """Test V6 5M config file exists."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_5m', 'config.json')
        self.assertTrue(os.path.exists(config_path))
    
    def test_v6_5m_config_valid_json(self):
        """Test V6 5M config is valid JSON with DUAL_ORDERS."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_5m', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.assertEqual(config["plugin_id"], "price_action_5m")
        self.assertEqual(config["settings"]["order_routing"], "DUAL_ORDERS")
    
    def test_v6_15m_config_exists(self):
        """Test V6 15M config file exists."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_15m', 'config.json')
        self.assertTrue(os.path.exists(config_path))
    
    def test_v6_15m_config_valid_json(self):
        """Test V6 15M config is valid JSON with ORDER_A_ONLY."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_15m', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.assertEqual(config["plugin_id"], "price_action_15m")
        self.assertEqual(config["settings"]["order_routing"], "ORDER_A_ONLY")
    
    def test_v6_1h_config_exists(self):
        """Test V6 1H config file exists."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_1h', 'config.json')
        self.assertTrue(os.path.exists(config_path))
    
    def test_v6_1h_config_valid_json(self):
        """Test V6 1H config is valid JSON with ORDER_A_ONLY."""
        config_path = os.path.join(PROJECT_ROOT, 'src', 'logic_plugins', 'price_action_1h', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.assertEqual(config["plugin_id"], "price_action_1h")
        self.assertEqual(config["settings"]["order_routing"], "ORDER_A_ONLY")
    
    def test_env_template_exists(self):
        """Test .env.template file exists."""
        template_path = os.path.join(PROJECT_ROOT, '.env.template')
        self.assertTrue(os.path.exists(template_path))
    
    def test_env_template_content(self):
        """Test .env.template has required variables."""
        template_path = os.path.join(PROJECT_ROOT, '.env.template')
        with open(template_path, 'r') as f:
            content = f.read()
        self.assertIn("TELEGRAM_CONTROLLER_TOKEN", content)
        self.assertIn("MT5_PASSWORD", content)
        self.assertIn("ENVIRONMENT", content)


class TestDocument11Integration(unittest.TestCase):
    """Test Document 11 integration scenarios."""
    
    def test_v6_order_routing_consistency(self):
        """Test V6 order routing is consistent across configs."""
        from config.defaults import DefaultsManager
        
        v6_1m = DefaultsManager.get_v6_1m_defaults()
        self.assertEqual(v6_1m["settings"]["order_routing"], "ORDER_B_ONLY")
        
        v6_5m = DefaultsManager.get_v6_5m_defaults()
        self.assertEqual(v6_5m["settings"]["order_routing"], "DUAL_ORDERS")
        
        v6_15m = DefaultsManager.get_v6_15m_defaults()
        self.assertEqual(v6_15m["settings"]["order_routing"], "ORDER_A_ONLY")
        
        v6_1h = DefaultsManager.get_v6_1h_defaults()
        self.assertEqual(v6_1h["settings"]["order_routing"], "ORDER_A_ONLY")
    
    def test_v3_logic_multipliers_consistency(self):
        """Test V3 logic multipliers are consistent."""
        from config.defaults import DefaultsManager
        
        v3 = DefaultsManager.get_v3_plugin_defaults()
        multipliers = v3["settings"]["routing_matrix"]["logic_multipliers"]
        
        self.assertEqual(multipliers["LOGIC1"], 1.25)
        self.assertEqual(multipliers["LOGIC2"], 1.0)
        self.assertEqual(multipliers["LOGIC3"], 0.625)
    
    def test_mtf_4_pillar_system(self):
        """Test MTF 4-pillar system configuration."""
        from config.defaults import DefaultsManager
        
        v3 = DefaultsManager.get_v3_plugin_defaults()
        mtf = v3["settings"]["mtf_4_pillar_system"]
        
        self.assertEqual(len(mtf["pillars"]), 4)
        self.assertEqual(mtf["pillars"], ["15m", "1h", "4h", "1d"])
        self.assertEqual(mtf["min_aligned_for_entry"], 3)
    
    def test_config_with_env_vars_and_defaults(self):
        """Test config loading with env vars and defaults."""
        from config.defaults import DefaultsManager, EnvironmentVariableResolver
        
        partial_config = {
            "telegram_token": "${TELEGRAM_MAIN_TOKEN}",
            "telegram_chat_id": "123456"
        }
        
        with patch.dict(os.environ, {"TELEGRAM_MAIN_TOKEN": "test_token_123"}):
            config = DefaultsManager.apply_defaults(partial_config, "main")
            config = EnvironmentVariableResolver.resolve_config(config)
            
            self.assertEqual(config["telegram_token"], "test_token_123")
            self.assertEqual(config["telegram_chat_id"], "123456")
            self.assertIn("plugin_system", config)


class TestDocument11Summary(unittest.TestCase):
    """Test Document 11 summary verification."""
    
    def test_all_config_modules_importable(self):
        """Test all config modules can be imported."""
        from config import schemas
        from config import defaults
        self.assertIsNotNone(schemas)
        self.assertIsNotNone(defaults)
    
    def test_all_schema_classes_exist(self):
        """Test all schema classes exist."""
        from config.schemas import (
            ConfigValidationError,
            PluginType,
            LogicRoute,
            OrderRouting,
            MainConfig,
            V3PluginConfig,
            V6PluginConfig,
            EnvironmentConfig
        )
        self.assertIsNotNone(ConfigValidationError)
        self.assertIsNotNone(PluginType)
        self.assertIsNotNone(LogicRoute)
        self.assertIsNotNone(OrderRouting)
        self.assertIsNotNone(MainConfig)
        self.assertIsNotNone(V3PluginConfig)
        self.assertIsNotNone(V6PluginConfig)
        self.assertIsNotNone(EnvironmentConfig)
    
    def test_all_defaults_classes_exist(self):
        """Test all defaults classes exist."""
        from config.defaults import (
            DefaultsManager,
            EnvironmentVariableResolver,
            ConfigLoader,
            generate_env_template,
            generate_gitignore_additions
        )
        self.assertIsNotNone(DefaultsManager)
        self.assertIsNotNone(EnvironmentVariableResolver)
        self.assertIsNotNone(ConfigLoader)
        self.assertIsNotNone(generate_env_template)
        self.assertIsNotNone(generate_gitignore_additions)
    
    def test_v6_1m_order_b_only(self):
        """Test V6 1M uses ORDER_B_ONLY."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_1m_defaults()
        self.assertEqual(defaults["settings"]["order_routing"], "ORDER_B_ONLY")
    
    def test_v6_5m_dual_orders(self):
        """Test V6 5M uses DUAL_ORDERS."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_5m_defaults()
        self.assertEqual(defaults["settings"]["order_routing"], "DUAL_ORDERS")
    
    def test_v6_15m_order_a_only(self):
        """Test V6 15M uses ORDER_A_ONLY."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_15m_defaults()
        self.assertEqual(defaults["settings"]["order_routing"], "ORDER_A_ONLY")
    
    def test_v6_1h_order_a_only(self):
        """Test V6 1H uses ORDER_A_ONLY."""
        from config.defaults import DefaultsManager
        defaults = DefaultsManager.get_v6_1h_defaults()
        self.assertEqual(defaults["settings"]["order_routing"], "ORDER_A_ONLY")
    
    def test_all_5_plugins_have_configs(self):
        """Test all 5 plugins have configuration templates."""
        from config.defaults import DefaultsManager
        
        v3 = DefaultsManager.get_v3_plugin_defaults()
        self.assertEqual(v3["plugin_id"], "combined_v3")
        
        v6_1m = DefaultsManager.get_v6_1m_defaults()
        self.assertEqual(v6_1m["plugin_id"], "price_action_1m")
        
        v6_5m = DefaultsManager.get_v6_5m_defaults()
        self.assertEqual(v6_5m["plugin_id"], "price_action_5m")
        
        v6_15m = DefaultsManager.get_v6_15m_defaults()
        self.assertEqual(v6_15m["plugin_id"], "price_action_15m")
        
        v6_1h = DefaultsManager.get_v6_1h_defaults()
        self.assertEqual(v6_1h["plugin_id"], "price_action_1h")


if __name__ == '__main__':
    unittest.main()
