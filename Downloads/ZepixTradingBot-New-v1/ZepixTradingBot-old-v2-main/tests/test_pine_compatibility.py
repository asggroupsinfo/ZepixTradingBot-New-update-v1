"""
Pine Script Compatibility Tests

Tests for V3 and V6 Pine Script to Bot compatibility.
Verifies field mapping, signal aliases, alert parsing, and signal mapping.

Version: 1.0
Date: 2026-01-13
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestV3FieldMapping:
    """Test V3 field mapping compatibility."""
    
    def test_sl_price_field_mapping_dict(self):
        """Test SL price field mapping with dict alert."""
        from logic_plugins.combined_v3.entry_logic import EntryLogic
        
        # Create mock plugin
        class MockPlugin:
            service_api = None
            plugin_id = "test"
        
        entry_logic = EntryLogic(MockPlugin())
        
        # Test with Pine V3 field name (sl_price)
        alert_pine = {"sl_price": 1.23456, "direction": "BUY"}
        sl = entry_logic._calculate_sl_price(alert_pine, "LOGIC1", "ORDER_A")
        assert sl == 1.23456, "Should extract sl_price from Pine V3 alert"
        
        # Test with legacy field name (sl)
        alert_legacy = {"sl": 1.11111, "direction": "BUY"}
        sl = entry_logic._calculate_sl_price(alert_legacy, "LOGIC1", "ORDER_A")
        assert sl == 1.11111, "Should extract sl from legacy alert"
        
        # Test fallback when both present (sl_price takes priority)
        alert_both = {"sl_price": 1.23456, "sl": 1.11111}
        sl = entry_logic._calculate_sl_price(alert_both, "LOGIC1", "ORDER_A")
        assert sl == 1.23456, "sl_price should take priority over sl"
    
    def test_tp_price_field_mapping_dict(self):
        """Test TP price field mapping with dict alert."""
        from logic_plugins.combined_v3.entry_logic import EntryLogic
        
        class MockPlugin:
            service_api = None
            plugin_id = "test"
        
        entry_logic = EntryLogic(MockPlugin())
        
        # Test with Pine V3 field names (tp1_price, tp2_price)
        alert_pine = {"tp1_price": 1.24000, "tp2_price": 1.25000}
        
        tp_a = entry_logic._calculate_tp_price(alert_pine, "LOGIC1", "ORDER_A")
        assert tp_a == 1.24000, "ORDER_A should use tp1_price"
        
        tp_b = entry_logic._calculate_tp_price(alert_pine, "LOGIC1", "ORDER_B")
        assert tp_b == 1.25000, "ORDER_B should use tp2_price"
        
        # Test with legacy field name (tp)
        alert_legacy = {"tp": 1.22222}
        tp = entry_logic._calculate_tp_price(alert_legacy, "LOGIC1", "ORDER_A")
        assert tp == 1.22222, "Should extract tp from legacy alert"
    
    def test_sl_price_field_mapping_object(self):
        """Test SL price field mapping with object alert."""
        from logic_plugins.combined_v3.entry_logic import EntryLogic
        
        class MockPlugin:
            service_api = None
            plugin_id = "test"
        
        entry_logic = EntryLogic(MockPlugin())
        
        # Test with Pine V3 field name (sl_price)
        class AlertPine:
            sl_price = 1.23456
            direction = "BUY"
        
        sl = entry_logic._calculate_sl_price(AlertPine(), "LOGIC1", "ORDER_A")
        assert sl == 1.23456, "Should extract sl_price from Pine V3 object alert"
        
        # Test with legacy field name (sl)
        class AlertLegacy:
            sl = 1.11111
            direction = "BUY"
        
        sl = entry_logic._calculate_sl_price(AlertLegacy(), "LOGIC1", "ORDER_A")
        assert sl == 1.11111, "Should extract sl from legacy object alert"


class TestV3SignalAliases:
    """Test V3 signal aliases for Pine compatibility."""
    
    def test_signal_aliases_defined(self):
        """Test that signal aliases are defined."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        
        assert hasattr(V3SignalHandlers, 'SIGNAL_ALIASES'), "SIGNAL_ALIASES should be defined"
        
        aliases = V3SignalHandlers.SIGNAL_ALIASES
        assert 'Liquidity_Trap_Reversal' in aliases, "Liquidity_Trap_Reversal alias should exist"
        assert 'Mitigation_Test_Entry' in aliases, "Mitigation_Test_Entry alias should exist"
        
        assert aliases['Liquidity_Trap_Reversal'] == 'Liquidity_Trap'
        assert aliases['Mitigation_Test_Entry'] == 'Mitigation_Test'
    
    def test_signal_handlers_include_aliases(self):
        """Test that SIGNAL_HANDLERS includes aliased signal types."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        
        handlers = V3SignalHandlers.SIGNAL_HANDLERS
        
        # Check that aliased signals map to correct handlers
        assert 'Liquidity_Trap_Reversal' in handlers, "Liquidity_Trap_Reversal should be in handlers"
        assert 'Mitigation_Test_Entry' in handlers, "Mitigation_Test_Entry should be in handlers"
        
        # Check they map to same handler as canonical names
        assert handlers['Liquidity_Trap_Reversal'] == handlers['Liquidity_Trap']
        assert handlers['Mitigation_Test_Entry'] == handlers['Mitigation_Test']
    
    def test_all_v3_pine_signals_supported(self):
        """Test that all V3 Pine signal types are supported."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        
        # V3 Pine signal types from ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine
        v3_pine_signals = [
            "Institutional_Launchpad",
            "Liquidity_Trap_Reversal",  # Pine sends this
            "Momentum_Breakout",
            "Mitigation_Test_Entry",    # Pine sends this
            "Golden_Pocket_Flip",
            "Bullish_Exit",
            "Bearish_Exit",
            "Volatility_Squeeze",
            "Screener_Full_Bullish",
            "Screener_Full_Bearish",
            "Trend_Pulse",
            "Sideways_Breakout"
        ]
        
        handlers = V3SignalHandlers.SIGNAL_HANDLERS
        
        for signal in v3_pine_signals:
            assert signal in handlers, f"V3 Pine signal '{signal}' should be supported"


class TestV6AlertParser:
    """Test V6 alert parser functionality."""
    
    def test_parser_initialization(self):
        """Test V6 alert parser initializes correctly."""
        from logic_plugins.price_action_v6.alert_parser import V6AlertParser
        
        parser = V6AlertParser()
        assert parser is not None
        assert parser.parse_count == 0
        assert parser.error_count == 0
    
    def test_parse_bullish_entry(self):
        """Test parsing BULLISH_ENTRY alert."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        alert = "BULLISH_ENTRY|EURUSD|15|1.23456|BUY|HIGH|85|25.5|STRONG|1.23000|1.24000|1.24500|1.25000|4/2|TL_OK"
        
        result = parse_v6_alert(alert)
        
        assert result is not None
        assert result.get("parsed") == True
        assert result.get("signal_type") == "BULLISH_ENTRY"
        assert result.get("symbol") == "EURUSD"
        assert result.get("timeframe") == "15"
        assert result.get("price") == 1.23456
        assert result.get("direction") == "BUY"
        assert result.get("conf_score") == 85
        assert result.get("adx") == 25.5
        assert result.get("sl_price") == 1.23000
        assert result.get("tp1_price") == 1.24000
        assert result.get("category") == "entry"
    
    def test_parse_bearish_entry(self):
        """Test parsing BEARISH_ENTRY alert."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        alert = "BEARISH_ENTRY|GBPUSD|5|1.34567|SELL|MEDIUM|70|22.0|MODERATE|1.35000|1.34000|1.33500|1.33000|3/3|TL_BREAK"
        
        result = parse_v6_alert(alert)
        
        assert result is not None
        assert result.get("parsed") == True
        assert result.get("signal_type") == "BEARISH_ENTRY"
        assert result.get("direction") == "SELL"
        assert result.get("category") == "entry"
    
    def test_parse_exit_bullish(self):
        """Test parsing EXIT_BULLISH alert."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        alert = "EXIT_BULLISH|EURUSD|15|1.24500|15"
        
        result = parse_v6_alert(alert)
        
        assert result is not None
        assert result.get("parsed") == True
        assert result.get("signal_type") == "EXIT_BULLISH"
        assert result.get("symbol") == "EURUSD"
        assert result.get("bars_held") == 15
        assert result.get("category") == "exit"
    
    def test_parse_trend_pulse(self):
        """Test parsing TREND_PULSE alert."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        alert = "TREND_PULSE|EURUSD|15|4|2|15m,1H|TRENDING_BULLISH"
        
        result = parse_v6_alert(alert)
        
        assert result is not None
        assert result.get("parsed") == True
        assert result.get("signal_type") == "TREND_PULSE"
        assert result.get("bullish_count") == 4
        assert result.get("bearish_count") == 2
        assert result.get("category") == "info"
    
    def test_parse_sideways_breakout(self):
        """Test parsing SIDEWAYS_BREAKOUT alert."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        alert = "SIDEWAYS_BREAKOUT|XAUUSD|15|BUY|28.5|STRONG|SIDEWAYS|INCREASING"
        
        result = parse_v6_alert(alert)
        
        assert result is not None
        assert result.get("parsed") == True
        assert result.get("signal_type") == "SIDEWAYS_BREAKOUT"
        assert result.get("direction") == "BUY"
        assert result.get("adx") == 28.5
        assert result.get("category") == "entry"
    
    def test_parse_unknown_signal(self):
        """Test parsing unknown signal type."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        alert = "UNKNOWN_SIGNAL|EURUSD|15|1.23456"
        
        result = parse_v6_alert(alert)
        
        assert result is not None
        assert result.get("parsed") == False
        assert result.get("signal_type") == "UNKNOWN_SIGNAL"
    
    def test_parse_empty_alert(self):
        """Test parsing empty alert."""
        from logic_plugins.price_action_v6.alert_parser import parse_v6_alert
        
        result = parse_v6_alert("")
        assert result is None
        
        result = parse_v6_alert(None)
        assert result is None
    
    def test_all_v6_signal_types_supported(self):
        """Test that all V6 Pine signal types are supported."""
        from logic_plugins.price_action_v6.alert_parser import V6AlertParser
        
        # V6 Pine signal types from Signals_and_Overlays_V6_Enhanced_Build.pine
        v6_pine_signals = [
            "BULLISH_ENTRY",
            "BEARISH_ENTRY",
            "EXIT_BULLISH",
            "EXIT_BEARISH",
            "TREND_PULSE",
            "SIDEWAYS_BREAKOUT",
            "TRENDLINE_BULLISH_BREAK",
            "TRENDLINE_BEARISH_BREAK",
            "MOMENTUM_CHANGE",
            "STATE_CHANGE",
            "BREAKOUT",
            "BREAKDOWN",
            "SCREENER_FULL_BULLISH",
            "SCREENER_FULL_BEARISH"
        ]
        
        parser = V6AlertParser()
        
        for signal in v6_pine_signals:
            assert signal in parser.SIGNAL_FIELD_MAP, f"V6 Pine signal '{signal}' should be supported"


class TestV6SignalMapper:
    """Test V6 signal mapper functionality."""
    
    def test_signal_map_defined(self):
        """Test that V6_SIGNAL_MAP is defined."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        assert hasattr(PriceActionV6Plugin, 'V6_SIGNAL_MAP'), "V6_SIGNAL_MAP should be defined"
        
        signal_map = PriceActionV6Plugin.V6_SIGNAL_MAP
        assert len(signal_map) == 14, "Should have 14 signal mappings"
    
    def test_entry_signal_mappings(self):
        """Test entry signal mappings."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        signal_map = PriceActionV6Plugin.V6_SIGNAL_MAP
        
        # Entry signals should map to PA_* handlers
        assert signal_map["BULLISH_ENTRY"] == "PA_Breakout_Entry"
        assert signal_map["BEARISH_ENTRY"] == "PA_Breakout_Entry"
        assert signal_map["SIDEWAYS_BREAKOUT"] == "PA_Momentum_Entry"
        assert signal_map["TRENDLINE_BULLISH_BREAK"] == "PA_Support_Bounce"
        assert signal_map["TRENDLINE_BEARISH_BREAK"] == "PA_Resistance_Rejection"
        assert signal_map["BREAKOUT"] == "PA_Breakout_Entry"
        assert signal_map["BREAKDOWN"] == "PA_Breakout_Entry"
    
    def test_exit_signal_mappings(self):
        """Test exit signal mappings."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        signal_map = PriceActionV6Plugin.V6_SIGNAL_MAP
        
        assert signal_map["EXIT_BULLISH"] == "PA_Exit_Signal"
        assert signal_map["EXIT_BEARISH"] == "PA_Exit_Signal"
    
    def test_info_signal_mappings(self):
        """Test info signal mappings."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        signal_map = PriceActionV6Plugin.V6_SIGNAL_MAP
        
        assert signal_map["TREND_PULSE"] == "PA_Trend_Pulse"
        assert signal_map["MOMENTUM_CHANGE"] == "PA_Volatility_Alert"
        assert signal_map["STATE_CHANGE"] == "PA_Volatility_Alert"
        assert signal_map["SCREENER_FULL_BULLISH"] == "PA_Trend_Pulse"
        assert signal_map["SCREENER_FULL_BEARISH"] == "PA_Trend_Pulse"
    
    def test_all_v6_pine_signals_mapped(self):
        """Test that all V6 Pine signals are mapped."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        
        # V6 Pine signal types
        v6_pine_signals = [
            "BULLISH_ENTRY",
            "BEARISH_ENTRY",
            "EXIT_BULLISH",
            "EXIT_BEARISH",
            "TREND_PULSE",
            "SIDEWAYS_BREAKOUT",
            "TRENDLINE_BULLISH_BREAK",
            "TRENDLINE_BEARISH_BREAK",
            "MOMENTUM_CHANGE",
            "STATE_CHANGE",
            "BREAKOUT",
            "BREAKDOWN",
            "SCREENER_FULL_BULLISH",
            "SCREENER_FULL_BEARISH"
        ]
        
        signal_map = PriceActionV6Plugin.V6_SIGNAL_MAP
        
        for signal in v6_pine_signals:
            assert signal in signal_map, f"V6 Pine signal '{signal}' should be mapped"


class TestPineCompatibilitySummary:
    """Summary tests for Pine compatibility."""
    
    def test_v3_compatibility_100_percent(self):
        """Test V3 Pine to Bot compatibility is 100%."""
        from logic_plugins.combined_v3.signal_handlers import V3SignalHandlers
        
        # All V3 Pine signals
        v3_pine_signals = [
            "Institutional_Launchpad",
            "Liquidity_Trap_Reversal",
            "Momentum_Breakout",
            "Mitigation_Test_Entry",
            "Golden_Pocket_Flip",
            "Bullish_Exit",
            "Bearish_Exit",
            "Volatility_Squeeze",
            "Screener_Full_Bullish",
            "Screener_Full_Bearish",
            "Trend_Pulse",
            "Sideways_Breakout"
        ]
        
        handlers = V3SignalHandlers.SIGNAL_HANDLERS
        supported = sum(1 for s in v3_pine_signals if s in handlers)
        
        assert supported == len(v3_pine_signals), f"V3 compatibility: {supported}/{len(v3_pine_signals)}"
        print(f"V3 Pine Compatibility: {supported}/{len(v3_pine_signals)} = 100%")
    
    def test_v6_compatibility_100_percent(self):
        """Test V6 Pine to Bot compatibility is 100%."""
        from logic_plugins.price_action_v6.plugin import PriceActionV6Plugin
        from logic_plugins.price_action_v6.alert_parser import V6AlertParser
        
        # All V6 Pine signals
        v6_pine_signals = [
            "BULLISH_ENTRY",
            "BEARISH_ENTRY",
            "EXIT_BULLISH",
            "EXIT_BEARISH",
            "TREND_PULSE",
            "SIDEWAYS_BREAKOUT",
            "TRENDLINE_BULLISH_BREAK",
            "TRENDLINE_BEARISH_BREAK",
            "MOMENTUM_CHANGE",
            "STATE_CHANGE",
            "BREAKOUT",
            "BREAKDOWN",
            "SCREENER_FULL_BULLISH",
            "SCREENER_FULL_BEARISH"
        ]
        
        signal_map = PriceActionV6Plugin.V6_SIGNAL_MAP
        parser = V6AlertParser()
        
        # Check signal mapping
        mapped = sum(1 for s in v6_pine_signals if s in signal_map)
        assert mapped == len(v6_pine_signals), f"V6 mapping: {mapped}/{len(v6_pine_signals)}"
        
        # Check parser support
        parsed = sum(1 for s in v6_pine_signals if s in parser.SIGNAL_FIELD_MAP)
        assert parsed == len(v6_pine_signals), f"V6 parsing: {parsed}/{len(v6_pine_signals)}"
        
        print(f"V6 Pine Compatibility: {mapped}/{len(v6_pine_signals)} = 100%")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
