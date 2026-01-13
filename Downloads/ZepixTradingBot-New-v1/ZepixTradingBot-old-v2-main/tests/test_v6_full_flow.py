"""
V6 Full Flow Test Suite - Proof of Life Test

Tests the complete V6 signal processing flow:
1. Raw pipe alert from Pine Script
2. Alert parsing via V6AlertParser
3. Signal routing to timeframe-specific plugins
4. ADX and Confidence validation
5. Order placement (mocked)
6. Database storage in zepix_price_action.db

Per PM directive: This test MUST pass 100% to prove V6 is as robust as V3.

Version: 1.0
Date: 2026-01-13
"""

import pytest
import asyncio
import sqlite3
import os
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_async(coro):
    """Helper to run async functions in sync tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestV6AlertParser:
    """Test V6 Alert Parser - Pipe format parsing."""
    
    def test_parse_bullish_entry_signal(self):
        """Test parsing BULLISH_ENTRY signal from Pine V6."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        # Simulate raw pipe alert from Pine V6
        raw_alert = "BULLISH_ENTRY|EURUSD|5|1.08500|BUY|HIGH|85|28.5|STRONG|1.08400|1.08600|1.08700|1.08800|4/2|TL_OK"
        
        result = parse_v6_alert(raw_alert)
        
        assert result is not None
        assert result.get("parsed") is True
        assert result.get("signal_type") == "BULLISH_ENTRY"
        assert result.get("symbol") == "EURUSD"
        assert result.get("timeframe") == "5"
        assert result.get("direction") == "BUY"
        assert result.get("conf_score") == 85
        assert result.get("adx") == 28.5
        assert result.get("adx_strength") == "STRONG"
        assert result.get("category") == "entry"
    
    def test_parse_bearish_entry_signal(self):
        """Test parsing BEARISH_ENTRY signal from Pine V6."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        raw_alert = "BEARISH_ENTRY|GBPUSD|15|1.26500|SELL|MEDIUM|72|22.0|MODERATE|1.26600|1.26400|1.26300|1.26200|3/3|TL_BREAK"
        
        result = parse_v6_alert(raw_alert)
        
        assert result is not None
        assert result.get("parsed") is True
        assert result.get("signal_type") == "BEARISH_ENTRY"
        assert result.get("symbol") == "GBPUSD"
        assert result.get("direction") == "SELL"
        assert result.get("category") == "entry"
    
    def test_parse_exit_signal(self):
        """Test parsing EXIT_BULLISH signal from Pine V6."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        raw_alert = "EXIT_BULLISH|EURUSD|5|1.08700|15"
        
        result = parse_v6_alert(raw_alert)
        
        assert result is not None
        assert result.get("parsed") is True
        assert result.get("signal_type") == "EXIT_BULLISH"
        assert result.get("symbol") == "EURUSD"
        assert result.get("bars_held") == 15
        assert result.get("category") == "exit"
    
    def test_parse_trend_pulse_signal(self):
        """Test parsing TREND_PULSE signal from Pine V6."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        raw_alert = "TREND_PULSE|EURUSD|15|4|2|15m,1H|TRENDING_BULLISH"
        
        result = parse_v6_alert(raw_alert)
        
        assert result is not None
        assert result.get("parsed") is True
        assert result.get("signal_type") == "TREND_PULSE"
        assert result.get("bullish_count") == 4
        assert result.get("bearish_count") == 2
        assert result.get("market_state") == "TRENDING_BULLISH"
        assert result.get("category") == "info"
    
    def test_parse_momentum_change_signal(self):
        """Test parsing MOMENTUM_CHANGE signal from Pine V6."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        raw_alert = "MOMENTUM_CHANGE|EURUSD|5|28.5|STRONG|22.3|MODERATE|INCREASING"
        
        result = parse_v6_alert(raw_alert)
        
        assert result is not None
        assert result.get("parsed") is True
        assert result.get("signal_type") == "MOMENTUM_CHANGE"
        assert result.get("current_adx") == 28.5
        assert result.get("current_strength") == "STRONG"
        assert result.get("change_type") == "INCREASING"
        assert result.get("category") == "info"
    
    def test_parse_unknown_signal_returns_unparsed(self):
        """Test that unknown signal types return unparsed result."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        raw_alert = "UNKNOWN_SIGNAL|EURUSD|5|1.08500"
        
        result = parse_v6_alert(raw_alert)
        
        assert result is not None
        assert result.get("parsed") is False
        assert result.get("signal_type") == "UNKNOWN_SIGNAL"


class TestV6SignalRouting:
    """Test V6 Signal Routing to Timeframe Plugins."""
    
    def test_timeframe_normalization(self):
        """Test timeframe normalization from Pine format to bot format."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        # Create mock plugin
        mock_service_api = Mock()
        plugin = PriceActionV6Plugin("price_action_v6", {}, mock_service_api)
        
        # Test normalization
        assert plugin._normalize_timeframe("1") == "1M"
        assert plugin._normalize_timeframe("5") == "5M"
        assert plugin._normalize_timeframe("15") == "15M"
        assert plugin._normalize_timeframe("60") == "1H"
        assert plugin._normalize_timeframe("1M") == "1M"
        assert plugin._normalize_timeframe("5M") == "5M"
        assert plugin._normalize_timeframe("15M") == "15M"
        assert plugin._normalize_timeframe("1H") == "1H"
    
    def test_signal_mapping(self):
        """Test Pine V6 signal to bot handler mapping."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        mock_service_api = Mock()
        plugin = PriceActionV6Plugin("price_action_v6", {}, mock_service_api)
        
        # Test signal mapping
        assert plugin.map_pine_signal("BULLISH_ENTRY") == "PA_Breakout_Entry"
        assert plugin.map_pine_signal("BEARISH_ENTRY") == "PA_Breakout_Entry"
        assert plugin.map_pine_signal("EXIT_BULLISH") == "PA_Exit_Signal"
        assert plugin.map_pine_signal("EXIT_BEARISH") == "PA_Exit_Signal"
        assert plugin.map_pine_signal("TREND_PULSE") == "PA_Trend_Pulse"
        assert plugin.map_pine_signal("MOMENTUM_CHANGE") == "PA_Volatility_Alert"


class TestV6TimeframePlugins:
    """Test V6 Timeframe-Specific Plugins."""
    
    def test_5m_plugin_adx_weak_rejection(self):
        """Test 5M plugin rejects signals with WEAK ADX strength."""
        from logic_plugins.price_action_5m.plugin import create_price_action_5m
        
        plugin = create_price_action_5m()
        
        # Signal with ADX >= 25 but WEAK strength should be rejected
        signal = {
            "symbol": "EURUSD",
            "direction": "BUY",
            "price": 1.08500,
            "adx": 26.0,  # Above threshold
            "adx_strength": "WEAK",  # But WEAK strength
            "conf_score": 75,
            "sl_price": 1.08400,
            "tp1_price": 1.08600,
            "tp2_price": 1.08700
        }
        
        result = run_async(plugin.on_signal_received(signal))
        
        # Should be rejected due to WEAK ADX strength
        assert result is False
    
    def test_5m_plugin_accepts_strong_adx(self):
        """Test 5M plugin accepts signals with STRONG ADX strength."""
        from logic_plugins.price_action_5m.plugin import create_price_action_5m
        
        plugin = create_price_action_5m()
        
        # Signal with ADX >= 25 and STRONG strength should be accepted
        signal = {
            "symbol": "EURUSD",
            "direction": "BUY",
            "price": 1.08500,
            "adx": 28.0,
            "adx_strength": "STRONG",
            "conf_score": 75,
            "sl_price": 1.08400,
            "tp1_price": 1.08600,
            "tp2_price": 1.08700
        }
        
        result = run_async(plugin.on_signal_received(signal))
        
        # Should be accepted
        assert result is True
    
    def test_5m_plugin_dual_orders(self):
        """Test 5M plugin places DUAL ORDERS."""
        from logic_plugins.price_action_5m.plugin import create_price_action_5m
        
        plugin = create_price_action_5m()
        
        # Check order type is DUAL_ORDERS
        status = plugin.get_status()
        assert status["order_type"] == "DUAL_ORDERS"
    
    def test_1h_plugin_risk_multiplier(self):
        """Test 1H plugin uses 0.6x risk multiplier (per planning doc)."""
        from logic_plugins.price_action_1h.plugin import create_price_action_1h
        
        plugin = create_price_action_1h()
        
        # Check risk multiplier is 0.6 (not 0.625)
        assert plugin.config.risk_multiplier == 0.6
    
    def test_1h_plugin_adx_extreme_threshold(self):
        """Test 1H plugin has ADX extreme threshold of 50."""
        from logic_plugins.price_action_1h.plugin import create_price_action_1h
        
        plugin = create_price_action_1h()
        
        # Check ADX extreme threshold
        assert plugin.config.adx_extreme_threshold == 50.0
    
    def test_1h_plugin_order_a_only(self):
        """Test 1H plugin uses ORDER A ONLY."""
        from logic_plugins.price_action_1h.plugin import create_price_action_1h
        
        plugin = create_price_action_1h()
        
        # Check order type is ORDER_A_ONLY
        status = plugin.get_status()
        assert status["order_type"] == "ORDER_A_ONLY"


class TestV6DatabaseIsolation:
    """Test V6 Database Isolation from V3."""
    
    def test_v6_database_path(self):
        """Test V6 uses separate database path."""
        from logic_plugins.price_action_v6.plugin import V6_DATABASE_PATH
        
        # V6 should use zepix_price_action.db
        assert "zepix_price_action.db" in str(V6_DATABASE_PATH)
        assert "zepix_combined" not in str(V6_DATABASE_PATH)
    
    def test_v6_database_tables_created(self):
        """Test V6 database tables are created correctly."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin, V6_DATABASE_PATH
        
        mock_service_api = Mock()
        plugin = PriceActionV6Plugin("price_action_v6", {}, mock_service_api)
        
        # Check database file exists
        if V6_DATABASE_PATH.exists():
            conn = sqlite3.connect(str(V6_DATABASE_PATH))
            cursor = conn.cursor()
            
            # Check v6_trades table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='v6_trades'")
            assert cursor.fetchone() is not None
            
            # Check v6_trend_pulse table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='v6_trend_pulse'")
            assert cursor.fetchone() is not None
            
            # Check v6_momentum_state table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='v6_momentum_state'")
            assert cursor.fetchone() is not None
            
            conn.close()


class TestV6FullFlow:
    """Test Complete V6 Signal Processing Flow."""
    
    def test_full_flow_5m_entry(self):
        """Test full flow: Raw alert -> Parse -> Route to 5M -> Validate -> Execute."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        # Step 1: Simulate raw pipe alert from Pine V6
        raw_alert = "BULLISH_ENTRY|EURUSD|5|1.08500|BUY|HIGH|85|28.5|STRONG|1.08400|1.08600|1.08700|1.08800|4/2|TL_OK"
        
        # Step 2: Parse alert
        parsed = parse_v6_alert(raw_alert)
        assert parsed is not None
        assert parsed.get("parsed") is True
        assert parsed.get("signal_type") == "BULLISH_ENTRY"
        
        # Step 3: Create V6 plugin and process
        mock_service_api = Mock()
        plugin = PriceActionV6Plugin("price_action_v6", {}, mock_service_api)
        
        # Step 4: Process raw alert through V6 plugin
        result = run_async(plugin.process_raw_v6_alert(raw_alert))
        
        # Step 5: Verify routing
        assert result is not None
        assert result.get("routed_to") == "price_action_5m"
        assert result.get("timeframe") == "5M"
    
    def test_full_flow_trend_pulse(self):
        """Test full flow for Trend Pulse signal."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        # Step 1: Simulate raw pipe alert
        raw_alert = "TREND_PULSE|EURUSD|15|4|2|15m,1H|TRENDING_BULLISH"
        
        # Step 2: Parse alert
        parsed = parse_v6_alert(raw_alert)
        assert parsed is not None
        assert parsed.get("signal_type") == "TREND_PULSE"
        
        # Step 3: Create V6 plugin and process
        mock_service_api = Mock()
        plugin = PriceActionV6Plugin("price_action_v6", {}, mock_service_api)
        
        # Step 4: Process raw alert
        result = run_async(plugin.process_raw_v6_alert(raw_alert))
        
        # Step 5: Verify trend pulse processing
        assert result is not None
        assert result.get("success") is True
        assert result.get("bullish_count") == 4
        assert result.get("bearish_count") == 2
        assert result.get("market_state") == "TRENDING_BULLISH"
    
    def test_full_flow_exit_signal(self):
        """Test full flow for Exit signal."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        # Step 1: Simulate raw pipe alert
        raw_alert = "EXIT_BULLISH|EURUSD|5|1.08700|15"
        
        # Step 2: Parse alert
        parsed = parse_v6_alert(raw_alert)
        assert parsed is not None
        assert parsed.get("signal_type") == "EXIT_BULLISH"
        assert parsed.get("category") == "exit"
        
        # Step 3: Create V6 plugin and process
        mock_service_api = Mock()
        plugin = PriceActionV6Plugin("price_action_v6", {}, mock_service_api)
        
        # Step 4: Process raw alert
        result = run_async(plugin.process_raw_v6_alert(raw_alert))
        
        # Step 5: Verify exit processing
        assert result is not None
        assert result.get("success") is True


class TestV6PlanningCompliance:
    """Test V6 Implementation Matches Planning Documents."""
    
    def test_1m_order_b_only(self):
        """Test 1M uses ORDER B ONLY per planning doc 02_PRICE_ACTION_LOGIC_1M.md."""
        from logic_plugins.price_action_1m.plugin import create_price_action_1m
        
        plugin = create_price_action_1m()
        status = plugin.get_status()
        
        assert status["order_type"] == "ORDER_B_ONLY"
    
    def test_5m_dual_orders(self):
        """Test 5M uses DUAL ORDERS per planning doc 03_PRICE_ACTION_LOGIC_5M.md."""
        from logic_plugins.price_action_5m.plugin import create_price_action_5m
        
        plugin = create_price_action_5m()
        status = plugin.get_status()
        
        assert status["order_type"] == "DUAL_ORDERS"
    
    def test_15m_order_a_only(self):
        """Test 15M uses ORDER A ONLY per planning doc 04_PRICE_ACTION_LOGIC_15M.md."""
        from logic_plugins.price_action_15m.plugin import create_price_action_15m
        
        plugin = create_price_action_15m()
        status = plugin.get_status()
        
        assert status["order_type"] == "ORDER_A_ONLY"
    
    def test_1h_order_a_only(self):
        """Test 1H uses ORDER A ONLY per planning doc 05_PRICE_ACTION_LOGIC_1H.md."""
        from logic_plugins.price_action_1h.plugin import create_price_action_1h
        
        plugin = create_price_action_1h()
        status = plugin.get_status()
        
        assert status["order_type"] == "ORDER_A_ONLY"
    
    def test_1m_adx_threshold(self):
        """Test 1M ADX threshold is 20 per planning doc."""
        from logic_plugins.price_action_1m.plugin import create_price_action_1m
        
        plugin = create_price_action_1m()
        assert plugin.config.min_adx == 20.0
    
    def test_5m_adx_threshold(self):
        """Test 5M ADX threshold is 25 per planning doc."""
        from logic_plugins.price_action_5m.plugin import create_price_action_5m
        
        plugin = create_price_action_5m()
        assert plugin.config.min_adx == 25.0
    
    def test_15m_adx_threshold(self):
        """Test 15M ADX threshold is 20 per planning doc."""
        from logic_plugins.price_action_15m.plugin import create_price_action_15m
        
        plugin = create_price_action_15m()
        assert plugin.config.min_adx == 20.0
    
    def test_1h_adx_threshold(self):
        """Test 1H ADX threshold is 20 per planning doc."""
        from logic_plugins.price_action_1h.plugin import create_price_action_1h
        
        plugin = create_price_action_1h()
        assert plugin.config.min_adx == 20.0
    
    def test_1m_confidence_threshold(self):
        """Test 1M confidence threshold is 80 per planning doc."""
        from logic_plugins.price_action_1m.plugin import create_price_action_1m
        
        plugin = create_price_action_1m()
        assert plugin.config.min_confidence == 80
    
    def test_5m_confidence_threshold(self):
        """Test 5M confidence threshold is 70 per planning doc."""
        from logic_plugins.price_action_5m.plugin import create_price_action_5m
        
        plugin = create_price_action_5m()
        assert plugin.config.min_confidence == 70
    
    def test_15m_confidence_threshold(self):
        """Test 15M confidence threshold is 70 per planning doc."""
        from logic_plugins.price_action_15m.plugin import create_price_action_15m
        
        plugin = create_price_action_15m()
        assert plugin.config.min_confidence == 70
    
    def test_1h_confidence_threshold(self):
        """Test 1H confidence threshold is 60 per planning doc."""
        from logic_plugins.price_action_1h.plugin import create_price_action_1h
        
        plugin = create_price_action_1h()
        assert plugin.config.min_confidence == 60
    
    def test_1m_risk_multiplier(self):
        """Test 1M risk multiplier is 0.5 per planning doc."""
        from logic_plugins.price_action_1m.plugin import create_price_action_1m
        
        plugin = create_price_action_1m()
        assert plugin.config.risk_multiplier == 0.5
    
    def test_5m_risk_multiplier(self):
        """Test 5M risk multiplier is 1.0 per planning doc."""
        from logic_plugins.price_action_5m.plugin import create_price_action_5m
        
        plugin = create_price_action_5m()
        assert plugin.config.risk_multiplier == 1.0
    
    def test_15m_risk_multiplier(self):
        """Test 15M risk multiplier is 1.0 per planning doc."""
        from logic_plugins.price_action_15m.plugin import create_price_action_15m
        
        plugin = create_price_action_15m()
        assert plugin.config.risk_multiplier == 1.0
    
    def test_1h_risk_multiplier(self):
        """Test 1H risk multiplier is 0.6 per planning doc."""
        from logic_plugins.price_action_1h.plugin import create_price_action_1h
        
        plugin = create_price_action_1h()
        assert plugin.config.risk_multiplier == 0.6


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
