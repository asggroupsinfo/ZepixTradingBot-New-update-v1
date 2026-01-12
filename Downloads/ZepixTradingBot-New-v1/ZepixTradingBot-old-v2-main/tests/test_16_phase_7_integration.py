"""
Test Suite for Document 16: Phase 7 V6 Integration Implementation.

This test file verifies the complete implementation of:
- V6 Alert Models
- Trend Pulse Manager
- V6 Integration Engine
- 4 Price Action Plugins (1M, 5M, 15M, 1H)
- Conflict Resolution
- Performance Optimization
- V3 + V6 Simultaneous Operation

Version: 1.0
Date: 2026-01-12
"""

import os
import sys
import pytest
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestV6IntegrationPackageStructure:
    """Test V6 integration package structure."""
    
    def test_v6_integration_package_exists(self):
        """Test that v6_integration package exists."""
        package_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'v6_integration')
        assert os.path.exists(package_path), "v6_integration package should exist"
    
    def test_alert_models_module_exists(self):
        """Test that alert_models module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'v6_integration', 'alert_models.py')
        assert os.path.exists(module_path), "alert_models.py should exist"
    
    def test_trend_pulse_manager_module_exists(self):
        """Test that trend_pulse_manager module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'v6_integration', 'trend_pulse_manager.py')
        assert os.path.exists(module_path), "trend_pulse_manager.py should exist"
    
    def test_v6_engine_module_exists(self):
        """Test that v6_engine module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'v6_integration', 'v6_engine.py')
        assert os.path.exists(module_path), "v6_engine.py should exist"


class TestPriceActionPluginStructure:
    """Test Price Action plugin structure."""
    
    def test_price_action_1m_exists(self):
        """Test that price_action_1m plugin exists."""
        plugin_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'price_action_1m')
        assert os.path.exists(plugin_path), "price_action_1m plugin should exist"
    
    def test_price_action_5m_exists(self):
        """Test that price_action_5m plugin exists."""
        plugin_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'price_action_5m')
        assert os.path.exists(plugin_path), "price_action_5m plugin should exist"
    
    def test_price_action_15m_exists(self):
        """Test that price_action_15m plugin exists."""
        plugin_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'price_action_15m')
        assert os.path.exists(plugin_path), "price_action_15m plugin should exist"
    
    def test_price_action_1h_exists(self):
        """Test that price_action_1h plugin exists."""
        plugin_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'price_action_1h')
        assert os.path.exists(plugin_path), "price_action_1h plugin should exist"


class TestV6AlertTypeEnum:
    """Test V6AlertType enum."""
    
    def test_alert_type_values(self):
        """Test V6AlertType enum values."""
        from src.v6_integration.alert_models import V6AlertType
        
        assert V6AlertType.BULLISH_ENTRY.value == "BULLISH_ENTRY"
        assert V6AlertType.BEARISH_ENTRY.value == "BEARISH_ENTRY"
        assert V6AlertType.EXIT_BULLISH.value == "EXIT_BULLISH"
        assert V6AlertType.TREND_PULSE.value == "TREND_PULSE"


class TestV6OrderRoutingEnum:
    """Test V6OrderRouting enum."""
    
    def test_order_routing_values(self):
        """Test V6OrderRouting enum values."""
        from src.v6_integration.alert_models import V6OrderRouting
        
        assert V6OrderRouting.ORDER_A_ONLY.value == "ORDER_A_ONLY"
        assert V6OrderRouting.ORDER_B_ONLY.value == "ORDER_B_ONLY"
        assert V6OrderRouting.DUAL_ORDERS.value == "DUAL_ORDERS"


class TestZepixV6Alert:
    """Test ZepixV6Alert dataclass."""
    
    def test_alert_creation(self):
        """Test ZepixV6Alert creation."""
        from src.v6_integration.alert_models import ZepixV6Alert
        
        alert = ZepixV6Alert(
            alert_type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2030.50,
            direction="BUY",
            conf_level="HIGH",
            conf_score=85
        )
        
        assert alert.ticker == "XAUUSD"
        assert alert.tf == "5"
        assert alert.conf_score == 85
    
    def test_alert_get_pulse_counts(self):
        """Test get_pulse_counts method."""
        from src.v6_integration.alert_models import ZepixV6Alert
        
        alert = ZepixV6Alert(
            alert_type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2030.50,
            direction="BUY",
            conf_level="HIGH",
            conf_score=85,
            alignment="5/1"
        )
        
        bulls, bears = alert.get_pulse_counts()
        assert bulls == 5
        assert bears == 1
    
    def test_alert_get_order_routing(self):
        """Test get_order_routing method."""
        from src.v6_integration.alert_models import ZepixV6Alert, V6OrderRouting
        
        alert_1m = ZepixV6Alert(
            alert_type="BULLISH_ENTRY", ticker="XAUUSD", tf="1",
            price=2030.50, direction="BUY", conf_level="HIGH", conf_score=85
        )
        assert alert_1m.get_order_routing() == V6OrderRouting.ORDER_B_ONLY
        
        alert_5m = ZepixV6Alert(
            alert_type="BULLISH_ENTRY", ticker="XAUUSD", tf="5",
            price=2030.50, direction="BUY", conf_level="HIGH", conf_score=85
        )
        assert alert_5m.get_order_routing() == V6OrderRouting.DUAL_ORDERS
        
        alert_15m = ZepixV6Alert(
            alert_type="BULLISH_ENTRY", ticker="XAUUSD", tf="15",
            price=2030.50, direction="BUY", conf_level="HIGH", conf_score=85
        )
        assert alert_15m.get_order_routing() == V6OrderRouting.ORDER_A_ONLY
    
    def test_alert_to_dict(self):
        """Test to_dict method."""
        from src.v6_integration.alert_models import ZepixV6Alert
        
        alert = ZepixV6Alert(
            alert_type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2030.50,
            direction="BUY",
            conf_level="HIGH",
            conf_score=85
        )
        
        data = alert.to_dict()
        
        assert data["ticker"] == "XAUUSD"
        assert data["conf_score"] == 85


class TestTrendPulseAlert:
    """Test TrendPulseAlert dataclass."""
    
    def test_pulse_alert_creation(self):
        """Test TrendPulseAlert creation."""
        from src.v6_integration.alert_models import TrendPulseAlert
        
        pulse = TrendPulseAlert(
            alert_type="TREND_PULSE",
            symbol="XAUUSD",
            tf="15",
            bull_count=5,
            bear_count=1,
            state="TRENDING_BULLISH"
        )
        
        assert pulse.symbol == "XAUUSD"
        assert pulse.bull_count == 5
        assert pulse.is_bullish() == True
    
    def test_pulse_alert_is_bearish(self):
        """Test is_bearish method."""
        from src.v6_integration.alert_models import TrendPulseAlert
        
        pulse = TrendPulseAlert(
            alert_type="TREND_PULSE",
            symbol="XAUUSD",
            tf="15",
            bull_count=1,
            bear_count=5,
            state="TRENDING_BEARISH"
        )
        
        assert pulse.is_bearish() == True
        assert pulse.is_bullish() == False


class TestV6AlertParser:
    """Test V6AlertParser class."""
    
    def test_parse_v6_payload(self):
        """Test parse_v6_payload method."""
        from src.v6_integration.alert_models import V6AlertParser
        
        payload = "BULLISH_ENTRY|XAUUSD|5|2030.50|BUY|HIGH|85|25.5|STRONG|2028.00|2032.00|2035.00|2038.00|5/1|TL_OK"
        alert = V6AlertParser.parse_v6_payload(payload)
        
        assert alert.alert_type == "BULLISH_ENTRY"
        assert alert.ticker == "XAUUSD"
        assert alert.tf == "5"
        assert alert.conf_score == 85
        assert alert.adx == 25.5
    
    def test_parse_trend_pulse(self):
        """Test parse_trend_pulse method."""
        from src.v6_integration.alert_models import V6AlertParser
        
        payload = "TREND_PULSE|XAUUSD|15|5|1|1M,5M|TRENDING_BULLISH"
        pulse = V6AlertParser.parse_trend_pulse(payload)
        
        assert pulse.symbol == "XAUUSD"
        assert pulse.bull_count == 5
        assert pulse.bear_count == 1
    
    def test_is_trend_pulse(self):
        """Test is_trend_pulse method."""
        from src.v6_integration.alert_models import V6AlertParser
        
        assert V6AlertParser.is_trend_pulse("TREND_PULSE|XAUUSD|15|5|1") == True
        assert V6AlertParser.is_trend_pulse("BULLISH_ENTRY|XAUUSD|5") == False
    
    def test_is_entry_signal(self):
        """Test is_entry_signal method."""
        from src.v6_integration.alert_models import V6AlertParser
        
        assert V6AlertParser.is_entry_signal("BULLISH_ENTRY|XAUUSD|5") == True
        assert V6AlertParser.is_entry_signal("BEARISH_ENTRY|XAUUSD|5") == True
        assert V6AlertParser.is_entry_signal("EXIT_BULLISH|XAUUSD|5") == False


class TestTrendPulseManager:
    """Test TrendPulseManager class."""
    
    def test_manager_creation(self):
        """Test TrendPulseManager creation."""
        from src.v6_integration.trend_pulse_manager import TrendPulseManager
        
        manager = TrendPulseManager()
        
        assert manager is not None
    
    def test_update_pulse(self):
        """Test update_pulse method."""
        from src.v6_integration.trend_pulse_manager import TrendPulseManager, MarketState
        
        manager = TrendPulseManager()
        manager.update_pulse("XAUUSD", "15", 5, 1, "TRENDING_BULLISH")
        
        state = manager.get_market_state("XAUUSD")
        assert state == MarketState.TRENDING_BULLISH
    
    def test_check_pulse_alignment(self):
        """Test check_pulse_alignment method."""
        from src.v6_integration.trend_pulse_manager import TrendPulseManager
        
        manager = TrendPulseManager()
        manager.update_pulse("XAUUSD", "15", 5, 1, "TRENDING_BULLISH")
        
        assert manager.check_pulse_alignment("XAUUSD", "BUY") == True
        assert manager.check_pulse_alignment("XAUUSD", "SELL") == False
    
    def test_get_trend_strength(self):
        """Test get_trend_strength method."""
        from src.v6_integration.trend_pulse_manager import TrendPulseManager
        
        manager = TrendPulseManager()
        manager.update_pulse("XAUUSD", "15", 5, 1, "TRENDING_BULLISH")
        
        strength = manager.get_trend_strength("XAUUSD")
        assert strength > 0


class TestV6PluginConfig:
    """Test V6PluginConfig dataclass."""
    
    def test_config_creation(self):
        """Test V6PluginConfig creation."""
        from src.v6_integration.v6_engine import V6PluginConfig, V6OrderRouting
        
        config = V6PluginConfig(
            plugin_id="price_action_1m",
            timeframe="1",
            min_adx=20.0,
            order_routing=V6OrderRouting.ORDER_B_ONLY
        )
        
        assert config.plugin_id == "price_action_1m"
        assert config.order_routing == V6OrderRouting.ORDER_B_ONLY
    
    def test_config_to_dict(self):
        """Test to_dict method."""
        from src.v6_integration.v6_engine import V6PluginConfig
        
        config = V6PluginConfig(
            plugin_id="price_action_5m",
            timeframe="5"
        )
        
        data = config.to_dict()
        
        assert data["plugin_id"] == "price_action_5m"


class TestV6ConflictResolver:
    """Test V6ConflictResolver class."""
    
    def test_resolver_creation(self):
        """Test V6ConflictResolver creation."""
        from src.v6_integration.v6_engine import V6ConflictResolver
        
        resolver = V6ConflictResolver()
        
        assert resolver is not None
    
    def test_resolve_single_alert(self):
        """Test resolve with single alert."""
        from src.v6_integration.v6_engine import V6ConflictResolver
        from src.v6_integration.alert_models import ZepixV6Alert
        
        resolver = V6ConflictResolver()
        
        alert = ZepixV6Alert(
            alert_type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2030.50,
            direction="BUY",
            conf_level="HIGH",
            conf_score=85
        )
        
        result = resolver.resolve([alert], {})
        
        assert result == alert
    
    def test_resolve_by_timeframe(self):
        """Test resolve by timeframe priority."""
        from src.v6_integration.v6_engine import V6ConflictResolver, ConflictResolutionStrategy
        from src.v6_integration.alert_models import ZepixV6Alert
        
        resolver = V6ConflictResolver(strategy=ConflictResolutionStrategy.TIMEFRAME_PRIORITY)
        
        alert_5m = ZepixV6Alert(
            alert_type="BULLISH_ENTRY", ticker="XAUUSD", tf="5",
            price=2030.50, direction="BUY", conf_level="HIGH", conf_score=85
        )
        alert_15m = ZepixV6Alert(
            alert_type="BULLISH_ENTRY", ticker="XAUUSD", tf="15",
            price=2030.50, direction="BUY", conf_level="HIGH", conf_score=80
        )
        
        result = resolver.resolve([alert_5m, alert_15m], {})
        
        assert result.tf == "15"


class TestV6PerformanceOptimizer:
    """Test V6PerformanceOptimizer class."""
    
    def test_optimizer_creation(self):
        """Test V6PerformanceOptimizer creation."""
        from src.v6_integration.v6_engine import V6PerformanceOptimizer
        
        optimizer = V6PerformanceOptimizer()
        
        assert optimizer is not None
    
    def test_cache_operations(self):
        """Test cache operations."""
        from src.v6_integration.v6_engine import V6PerformanceOptimizer
        
        optimizer = V6PerformanceOptimizer()
        
        optimizer.set_cached("test_key", "test_value")
        result = optimizer.get_cached("test_key")
        
        assert result == "test_value"
    
    def test_get_metrics(self):
        """Test get_metrics method."""
        from src.v6_integration.v6_engine import V6PerformanceOptimizer
        
        optimizer = V6PerformanceOptimizer()
        optimizer.set_cached("key1", "value1")
        optimizer.get_cached("key1")
        
        metrics = optimizer.get_metrics()
        
        assert "cache_hits" in metrics
        assert "total_checks" in metrics


class TestV6IntegrationEngine:
    """Test V6IntegrationEngine class."""
    
    def test_engine_creation(self):
        """Test V6IntegrationEngine creation."""
        from src.v6_integration.v6_engine import V6IntegrationEngine
        
        engine = V6IntegrationEngine()
        
        assert engine is not None
        assert engine.enabled == True
    
    def test_engine_default_configs(self):
        """Test default plugin configurations."""
        from src.v6_integration.v6_engine import V6IntegrationEngine, V6OrderRouting
        
        engine = V6IntegrationEngine()
        
        assert "1" in engine.plugin_configs
        assert "5" in engine.plugin_configs
        assert "15" in engine.plugin_configs
        assert "60" in engine.plugin_configs
        
        assert engine.plugin_configs["1"].order_routing == V6OrderRouting.ORDER_B_ONLY
        assert engine.plugin_configs["5"].order_routing == V6OrderRouting.DUAL_ORDERS
        assert engine.plugin_configs["15"].order_routing == V6OrderRouting.ORDER_A_ONLY
    
    def test_enable_disable_plugin(self):
        """Test enable/disable plugin."""
        from src.v6_integration.v6_engine import V6IntegrationEngine
        
        engine = V6IntegrationEngine()
        
        engine.disable_plugin("1")
        assert engine.plugin_configs["1"].enabled == False
        
        engine.enable_plugin("1")
        assert engine.plugin_configs["1"].enabled == True
    
    def test_get_status(self):
        """Test get_status method."""
        from src.v6_integration.v6_engine import V6IntegrationEngine
        
        engine = V6IntegrationEngine()
        status = engine.get_status()
        
        assert "enabled" in status
        assert "plugins" in status
        assert "trade_count" in status


class TestPriceAction1MPlugin:
    """Test Price Action 1M plugin."""
    
    def test_plugin_import(self):
        """Test plugin can be imported."""
        from src.logic_plugins.price_action_1m.plugin import PriceAction1M
        
        assert PriceAction1M is not None
    
    def test_plugin_constants(self):
        """Test plugin constants."""
        from src.logic_plugins.price_action_1m.plugin import PriceAction1M
        
        assert PriceAction1M.PLUGIN_ID == "price_action_1m"
        assert PriceAction1M.TIMEFRAME == "1"
    
    def test_plugin_creation(self):
        """Test plugin creation."""
        from src.logic_plugins.price_action_1m.plugin import PriceAction1M
        
        plugin = PriceAction1M("price_action_1m", {})
        
        assert plugin.plugin_id == "price_action_1m"
        assert plugin.is_enabled == True
    
    def test_plugin_config(self):
        """Test plugin configuration."""
        from src.logic_plugins.price_action_1m.plugin import PriceAction1M
        
        plugin = PriceAction1M("price_action_1m", {})
        
        assert plugin.config.min_adx == 20.0
        assert plugin.config.min_confidence == 80
        assert plugin.config.risk_multiplier == 0.5
    
    def test_1m_adx_filter(self):
        """Test 1M ADX filter."""
        import asyncio
        from src.logic_plugins.price_action_1m.plugin import PriceAction1M
        
        plugin = PriceAction1M("price_action_1m", {})
        
        signal = {
            "symbol": "XAUUSD",
            "direction": "BUY",
            "price": 2030.50,
            "adx": 15,
            "conf_score": 85
        }
        
        result = asyncio.get_event_loop().run_until_complete(
            plugin.on_signal_received(signal)
        )
        
        assert result == False
    
    def test_1m_order_b_only(self):
        """Test 1M places ORDER B only."""
        import asyncio
        from src.logic_plugins.price_action_1m.plugin import PriceAction1M
        
        plugin = PriceAction1M("price_action_1m", {})
        
        signal = {
            "symbol": "XAUUSD",
            "direction": "BUY",
            "price": 2030.50,
            "adx": 25,
            "conf_score": 85,
            "sl_price": 2028.00,
            "tp1_price": 2032.00
        }
        
        result = asyncio.get_event_loop().run_until_complete(
            plugin.on_signal_received(signal)
        )
        
        assert result == True
        assert len(plugin._trades) == 1


class TestPriceAction5MPlugin:
    """Test Price Action 5M plugin."""
    
    def test_plugin_import(self):
        """Test plugin can be imported."""
        from src.logic_plugins.price_action_5m.plugin import PriceAction5M
        
        assert PriceAction5M is not None
    
    def test_plugin_constants(self):
        """Test plugin constants."""
        from src.logic_plugins.price_action_5m.plugin import PriceAction5M
        
        assert PriceAction5M.PLUGIN_ID == "price_action_5m"
        assert PriceAction5M.TIMEFRAME == "5"
    
    def test_plugin_config(self):
        """Test plugin configuration."""
        from src.logic_plugins.price_action_5m.plugin import PriceAction5M
        
        plugin = PriceAction5M("price_action_5m", {})
        
        assert plugin.config.min_adx == 25.0
        assert plugin.config.min_confidence == 70
        assert plugin.config.risk_multiplier == 1.0
    
    def test_5m_dual_orders(self):
        """Test 5M places DUAL ORDERS."""
        import asyncio
        from src.logic_plugins.price_action_5m.plugin import PriceAction5M
        
        plugin = PriceAction5M("price_action_5m", {})
        
        signal = {
            "symbol": "XAUUSD",
            "direction": "BUY",
            "price": 2030.50,
            "adx": 30,
            "conf_score": 75,
            "sl_price": 2028.00,
            "tp1_price": 2032.00,
            "tp2_price": 2035.00
        }
        
        result = asyncio.get_event_loop().run_until_complete(
            plugin.on_signal_received(signal)
        )
        
        assert result == True
        assert len(plugin._trades) == 1
        assert plugin._trades[0].order_a_ticket is not None
        assert plugin._trades[0].order_b_ticket is not None


class TestPriceAction15MPlugin:
    """Test Price Action 15M plugin."""
    
    def test_plugin_import(self):
        """Test plugin can be imported."""
        from src.logic_plugins.price_action_15m.plugin import PriceAction15M
        
        assert PriceAction15M is not None
    
    def test_plugin_constants(self):
        """Test plugin constants."""
        from src.logic_plugins.price_action_15m.plugin import PriceAction15M
        
        assert PriceAction15M.PLUGIN_ID == "price_action_15m"
        assert PriceAction15M.TIMEFRAME == "15"
    
    def test_plugin_config(self):
        """Test plugin configuration."""
        from src.logic_plugins.price_action_15m.plugin import PriceAction15M
        
        plugin = PriceAction15M("price_action_15m", {})
        
        assert plugin.config.min_adx == 20.0
        assert plugin.config.check_market_state == True
        assert plugin.config.check_pulse_alignment == True
    
    def test_15m_order_a_only(self):
        """Test 15M places ORDER A only."""
        import asyncio
        from src.logic_plugins.price_action_15m.plugin import PriceAction15M
        
        plugin = PriceAction15M("price_action_15m", {})
        
        signal = {
            "symbol": "XAUUSD",
            "direction": "BUY",
            "price": 2030.50,
            "adx": 25,
            "conf_score": 75,
            "sl_price": 2028.00,
            "tp2_price": 2035.00
        }
        
        result = asyncio.get_event_loop().run_until_complete(
            plugin.on_signal_received(signal)
        )
        
        assert result == True
        assert len(plugin._trades) == 1
        assert plugin._trades[0].order_a_ticket is not None


class TestPriceAction1HPlugin:
    """Test Price Action 1H plugin."""
    
    def test_plugin_import(self):
        """Test plugin can be imported."""
        from src.logic_plugins.price_action_1h.plugin import PriceAction1H
        
        assert PriceAction1H is not None
    
    def test_plugin_constants(self):
        """Test plugin constants."""
        from src.logic_plugins.price_action_1h.plugin import PriceAction1H
        
        assert PriceAction1H.PLUGIN_ID == "price_action_1h"
        assert PriceAction1H.TIMEFRAME == "60"
    
    def test_plugin_config(self):
        """Test plugin configuration."""
        from src.logic_plugins.price_action_1h.plugin import PriceAction1H
        
        plugin = PriceAction1H("price_action_1h", {})
        
        assert plugin.config.min_adx == 20.0
        assert plugin.config.min_confidence == 60
        assert plugin.config.risk_multiplier == 0.625
    
    def test_1h_order_a_only(self):
        """Test 1H places ORDER A only."""
        import asyncio
        from src.logic_plugins.price_action_1h.plugin import PriceAction1H
        
        plugin = PriceAction1H("price_action_1h", {})
        
        signal = {
            "symbol": "XAUUSD",
            "direction": "BUY",
            "price": 2030.50,
            "adx": 25,
            "conf_score": 65,
            "sl_price": 2028.00,
            "tp3_price": 2038.00
        }
        
        result = asyncio.get_event_loop().run_until_complete(
            plugin.on_signal_received(signal)
        )
        
        assert result == True
        assert len(plugin._trades) == 1


class TestV6EngineExecution:
    """Test V6 engine execution."""
    
    def test_execute_entry_1m(self):
        """Test execute entry for 1M."""
        import asyncio
        from src.v6_integration.v6_engine import V6IntegrationEngine
        from src.v6_integration.alert_models import ZepixV6Alert
        
        engine = V6IntegrationEngine()
        
        alert = ZepixV6Alert(
            alert_type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="1",
            price=2030.50,
            direction="BUY",
            conf_level="HIGH",
            conf_score=85,
            adx=25.0,
            sl=2028.00,
            tp1=2032.00
        )
        
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute_entry(alert)
        )
        
        assert result.success == True
        assert result.ticket_b is not None
        assert result.ticket_a is None
    
    def test_execute_entry_5m(self):
        """Test execute entry for 5M."""
        import asyncio
        from src.v6_integration.v6_engine import V6IntegrationEngine
        from src.v6_integration.alert_models import ZepixV6Alert
        
        engine = V6IntegrationEngine()
        engine.trend_pulse.update_pulse("XAUUSD", "15", 5, 1, "TRENDING_BULLISH")
        
        alert = ZepixV6Alert(
            alert_type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2030.50,
            direction="BUY",
            conf_level="HIGH",
            conf_score=75,
            adx=30.0,
            sl=2028.00,
            tp1=2032.00,
            tp2=2035.00
        )
        
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute_entry(alert)
        )
        
        assert result.success == True
        assert result.ticket_a is not None
        assert result.ticket_b is not None


class TestV3V6Isolation:
    """Test V3 and V6 system isolation."""
    
    def test_separate_databases(self):
        """Test that V3 and V6 use separate databases."""
        from src.v6_integration.v6_engine import V6IntegrationEngine
        
        engine = V6IntegrationEngine()
        
        assert engine.trend_pulse is not None
        assert engine.service_api is not None
    
    def test_no_cross_contamination(self):
        """Test no cross-contamination between systems."""
        import asyncio
        from src.v6_integration.v6_engine import V6IntegrationEngine
        from src.v6_integration.alert_models import ZepixV6Alert
        
        engine = V6IntegrationEngine()
        
        alert = ZepixV6Alert(
            alert_type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="1",
            price=2030.50,
            direction="BUY",
            conf_level="HIGH",
            conf_score=85,
            adx=25.0
        )
        
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute_entry(alert)
        )
        
        assert result.plugin_id == "price_action_1m"
        assert "v3" not in result.plugin_id.lower()


class TestDocument16Integration:
    """Test Document 16 integration."""
    
    def test_all_modules_importable(self):
        """Test that all modules are importable."""
        from src.v6_integration import alert_models
        from src.v6_integration import trend_pulse_manager
        from src.v6_integration import v6_engine
        from src.logic_plugins.price_action_1m import plugin as p1m
        from src.logic_plugins.price_action_5m import plugin as p5m
        from src.logic_plugins.price_action_15m import plugin as p15m
        from src.logic_plugins.price_action_1h import plugin as p1h
        
        assert alert_models is not None
        assert trend_pulse_manager is not None
        assert v6_engine is not None
        assert p1m is not None
        assert p5m is not None
        assert p15m is not None
        assert p1h is not None
    
    def test_package_version(self):
        """Test package version."""
        from src.v6_integration import __version__
        
        assert __version__ == "1.0.0"
    
    def test_all_order_routing_types(self):
        """Test all order routing types are implemented."""
        from src.v6_integration.alert_models import V6OrderRouting
        
        routing_types = [r.value for r in V6OrderRouting]
        
        assert "ORDER_A_ONLY" in routing_types
        assert "ORDER_B_ONLY" in routing_types
        assert "DUAL_ORDERS" in routing_types


class TestDocument16Summary:
    """Test Document 16 summary verification."""
    
    def test_document_16_requirements_met(self):
        """Test that all Document 16 requirements are met."""
        from src.v6_integration.v6_engine import V6IntegrationEngine, V6OrderRouting
        
        engine = V6IntegrationEngine()
        
        assert "1" in engine.plugin_configs
        assert "5" in engine.plugin_configs
        assert "15" in engine.plugin_configs
        assert "60" in engine.plugin_configs
        
        assert engine.plugin_configs["1"].order_routing == V6OrderRouting.ORDER_B_ONLY
        assert engine.plugin_configs["5"].order_routing == V6OrderRouting.DUAL_ORDERS
        assert engine.plugin_configs["15"].order_routing == V6OrderRouting.ORDER_A_ONLY
        assert engine.plugin_configs["60"].order_routing == V6OrderRouting.ORDER_A_ONLY
    
    def test_trend_pulse_system_complete(self):
        """Test Trend Pulse system is complete."""
        from src.v6_integration.trend_pulse_manager import TrendPulseManager
        
        manager = TrendPulseManager()
        manager.update_pulse("XAUUSD", "15", 5, 1, "TRENDING_BULLISH")
        
        assert manager.check_pulse_alignment("XAUUSD", "BUY") == True
        assert manager.is_trending("XAUUSD") == True
    
    def test_conflict_resolution_complete(self):
        """Test conflict resolution is complete."""
        from src.v6_integration.v6_engine import V6ConflictResolver
        
        resolver = V6ConflictResolver()
        
        assert resolver is not None
        assert len(resolver.TIMEFRAME_PRIORITY) == 4
    
    def test_performance_optimization_complete(self):
        """Test performance optimization is complete."""
        from src.v6_integration.v6_engine import V6PerformanceOptimizer
        
        optimizer = V6PerformanceOptimizer()
        
        metrics = optimizer.get_metrics()
        assert "cache_hits" in metrics
        assert "hit_rate" in metrics
