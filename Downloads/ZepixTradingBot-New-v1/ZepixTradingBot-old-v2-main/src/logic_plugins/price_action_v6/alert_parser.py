"""
V6 Alert Parser - Converts Pine V6 pipe-separated alerts to dict format.

Parses all 14 V6 signal types from Signals_and_Overlays_V6_Enhanced_Build.pine.

Signal Types:
Entry (6): BULLISH_ENTRY, BEARISH_ENTRY, SIDEWAYS_BREAKOUT, 
           TRENDLINE_BULLISH_BREAK, TRENDLINE_BEARISH_BREAK, BREAKOUT, BREAKDOWN
Exit (2): EXIT_BULLISH, EXIT_BEARISH
Info (6): TREND_PULSE, MOMENTUM_CHANGE, STATE_CHANGE, 
          SCREENER_FULL_BULLISH, SCREENER_FULL_BEARISH

Version: 1.0
Date: 2026-01-13
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class V6AlertParser:
    """
    Parses V6 Pine Script pipe-separated alerts to dict format.
    
    V6 Pine sends alerts in format: SIGNAL_TYPE|SYMBOL|TF|FIELD3|FIELD4|...
    This parser converts them to dict with proper field names for bot processing.
    """
    
    # Entry signal field definitions (15 fields)
    ENTRY_FIELDS = [
        "signal_type",      # 0: BULLISH_ENTRY, BEARISH_ENTRY
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "price",            # 3: 1.23456
        "direction",        # 4: BUY, SELL
        "confidence_level", # 5: HIGH, MEDIUM, LOW
        "conf_score",       # 6: 85
        "adx",              # 7: 25.5
        "adx_strength",     # 8: STRONG, MODERATE, WEAK
        "sl_price",         # 9: 1.23000
        "tp1_price",        # 10: 1.24000
        "tp2_price",        # 11: 1.24500
        "tp3_price",        # 12: 1.25000
        "tf_alignment",     # 13: 4/2
        "trendline_state"   # 14: TL_OK, TL_BREAK
    ]
    
    # Exit signal field definitions (5 fields)
    EXIT_FIELDS = [
        "signal_type",      # 0: EXIT_BULLISH, EXIT_BEARISH
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "price",            # 3: 1.24500
        "bars_held"         # 4: 15
    ]
    
    # Trend Pulse field definitions (7 fields)
    TREND_PULSE_FIELDS = [
        "signal_type",      # 0: TREND_PULSE
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "bullish_count",    # 3: 4
        "bearish_count",    # 4: 2
        "changed_tfs",      # 5: 15m,1H
        "market_state"      # 6: TRENDING_BULLISH
    ]
    
    # Sideways Breakout field definitions (8 fields)
    SIDEWAYS_BREAKOUT_FIELDS = [
        "signal_type",      # 0: SIDEWAYS_BREAKOUT
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "direction",        # 3: BUY, SELL
        "adx",              # 4: 25.5
        "adx_strength",     # 5: STRONG
        "prev_state",       # 6: SIDEWAYS
        "momentum"          # 7: INCREASING
    ]
    
    # Trendline Break field definitions (6 fields)
    TRENDLINE_BREAK_FIELDS = [
        "signal_type",      # 0: TRENDLINE_BULLISH_BREAK, TRENDLINE_BEARISH_BREAK
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "price",            # 3: 1.23456
        "trendline_price",  # 4: 1.23400
        "break_strength"    # 5: STRONG
    ]
    
    # Momentum Change field definitions (8 fields)
    MOMENTUM_CHANGE_FIELDS = [
        "signal_type",      # 0: MOMENTUM_CHANGE
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "current_adx",      # 3: 28.5
        "current_strength", # 4: STRONG
        "prev_adx",         # 5: 22.3
        "prev_strength",    # 6: MODERATE
        "change_type"       # 7: INCREASING, DECREASING
    ]
    
    # State Change field definitions (6 fields)
    STATE_CHANGE_FIELDS = [
        "signal_type",      # 0: STATE_CHANGE
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "prev_state",       # 3: SIDEWAYS
        "new_state",        # 4: TRENDING_BULLISH
        "trigger"           # 5: ADX_CROSS
    ]
    
    # Breakout/Breakdown field definitions (7 fields)
    BREAKOUT_FIELDS = [
        "signal_type",      # 0: BREAKOUT, BREAKDOWN
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "price",            # 3: 1.23456
        "level_price",      # 4: 1.23400
        "test_count",       # 5: 3
        "direction"         # 6: BUY, SELL
    ]
    
    # Screener Full field definitions (4 fields)
    SCREENER_FIELDS = [
        "signal_type",      # 0: SCREENER_FULL_BULLISH, SCREENER_FULL_BEARISH
        "symbol",           # 1: EURUSD
        "timeframe",        # 2: 15
        "alignment_score"   # 3: 6/6
    ]
    
    # Signal type to field mapping
    SIGNAL_FIELD_MAP = {
        "BULLISH_ENTRY": ENTRY_FIELDS,
        "BEARISH_ENTRY": ENTRY_FIELDS,
        "EXIT_BULLISH": EXIT_FIELDS,
        "EXIT_BEARISH": EXIT_FIELDS,
        "TREND_PULSE": TREND_PULSE_FIELDS,
        "SIDEWAYS_BREAKOUT": SIDEWAYS_BREAKOUT_FIELDS,
        "TRENDLINE_BULLISH_BREAK": TRENDLINE_BREAK_FIELDS,
        "TRENDLINE_BEARISH_BREAK": TRENDLINE_BREAK_FIELDS,
        "MOMENTUM_CHANGE": MOMENTUM_CHANGE_FIELDS,
        "STATE_CHANGE": STATE_CHANGE_FIELDS,
        "BREAKOUT": BREAKOUT_FIELDS,
        "BREAKDOWN": BREAKOUT_FIELDS,
        "SCREENER_FULL_BULLISH": SCREENER_FIELDS,
        "SCREENER_FULL_BEARISH": SCREENER_FIELDS
    }
    
    # Entry signal types
    ENTRY_SIGNALS = [
        "BULLISH_ENTRY",
        "BEARISH_ENTRY",
        "SIDEWAYS_BREAKOUT",
        "TRENDLINE_BULLISH_BREAK",
        "TRENDLINE_BEARISH_BREAK",
        "BREAKOUT",
        "BREAKDOWN"
    ]
    
    # Exit signal types
    EXIT_SIGNALS = [
        "EXIT_BULLISH",
        "EXIT_BEARISH"
    ]
    
    # Info signal types
    INFO_SIGNALS = [
        "TREND_PULSE",
        "MOMENTUM_CHANGE",
        "STATE_CHANGE",
        "SCREENER_FULL_BULLISH",
        "SCREENER_FULL_BEARISH"
    ]
    
    def __init__(self):
        """Initialize V6 Alert Parser."""
        self.logger = logging.getLogger(f"{__name__}.V6AlertParser")
        self.parse_count = 0
        self.error_count = 0
        self.logger.info("V6AlertParser initialized - 14 signal types supported")
    
    def parse(self, alert_string: str) -> Optional[Dict[str, Any]]:
        """
        Parse V6 pipe-separated alert string to dict.
        
        Args:
            alert_string: Raw alert string from Pine V6
            
        Returns:
            dict: Parsed alert data or None if parsing fails
        """
        if not alert_string or not isinstance(alert_string, str):
            self.logger.warning("Invalid alert string received")
            return None
        
        try:
            # Split by pipe delimiter
            fields = alert_string.strip().split("|")
            
            if not fields:
                self.logger.warning("Empty alert after split")
                return None
            
            # Get signal type from first field
            signal_type = fields[0].strip().upper()
            
            # Get field definitions for this signal type
            field_defs = self.SIGNAL_FIELD_MAP.get(signal_type)
            
            if not field_defs:
                self.logger.warning(f"Unknown V6 signal type: {signal_type}")
                return {"signal_type": signal_type, "raw": alert_string, "parsed": False}
            
            # Parse fields based on signal type
            result = self._parse_fields(fields, field_defs, signal_type)
            
            if result:
                self.parse_count += 1
                result["parsed"] = True
                result["category"] = self._get_signal_category(signal_type)
                self.logger.debug(f"Parsed V6 alert: {signal_type} -> {result.get('symbol', 'N/A')}")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"V6 alert parse error: {e}")
            return {"signal_type": "UNKNOWN", "raw": alert_string, "parsed": False, "error": str(e)}
    
    def _parse_fields(
        self,
        fields: List[str],
        field_defs: List[str],
        signal_type: str
    ) -> Dict[str, Any]:
        """
        Parse fields based on field definitions.
        
        Args:
            fields: List of field values from split
            field_defs: List of field names
            signal_type: Signal type string
            
        Returns:
            dict: Parsed field values
        """
        result = {}
        
        for i, field_name in enumerate(field_defs):
            if i < len(fields):
                value = fields[i].strip()
                result[field_name] = self._convert_field_value(field_name, value)
            else:
                result[field_name] = self._get_default_value(field_name)
        
        return result
    
    def _convert_field_value(self, field_name: str, value: str) -> Any:
        """
        Convert field value to appropriate type.
        
        Args:
            field_name: Name of the field
            value: String value from alert
            
        Returns:
            Converted value (int, float, or str)
        """
        if not value:
            return self._get_default_value(field_name)
        
        # Numeric fields
        numeric_fields = [
            "price", "sl_price", "tp1_price", "tp2_price", "tp3_price",
            "adx", "current_adx", "prev_adx", "trendline_price", "level_price"
        ]
        
        integer_fields = [
            "conf_score", "bullish_count", "bearish_count", "bars_held", "test_count"
        ]
        
        if field_name in numeric_fields:
            try:
                return float(value)
            except ValueError:
                return 0.0
        
        if field_name in integer_fields:
            try:
                return int(value)
            except ValueError:
                return 0
        
        # String fields - return as-is
        return value
    
    def _get_default_value(self, field_name: str) -> Any:
        """
        Get default value for a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Default value for the field type
        """
        numeric_fields = [
            "price", "sl_price", "tp1_price", "tp2_price", "tp3_price",
            "adx", "current_adx", "prev_adx", "trendline_price", "level_price"
        ]
        
        integer_fields = [
            "conf_score", "bullish_count", "bearish_count", "bars_held", "test_count"
        ]
        
        if field_name in numeric_fields:
            return 0.0
        if field_name in integer_fields:
            return 0
        return ""
    
    def _get_signal_category(self, signal_type: str) -> str:
        """
        Get signal category (entry, exit, info).
        
        Args:
            signal_type: Signal type string
            
        Returns:
            str: Category name
        """
        if signal_type in self.ENTRY_SIGNALS:
            return "entry"
        elif signal_type in self.EXIT_SIGNALS:
            return "exit"
        elif signal_type in self.INFO_SIGNALS:
            return "info"
        return "unknown"
    
    def is_entry_signal(self, signal_type: str) -> bool:
        """Check if signal type is an entry signal."""
        return signal_type in self.ENTRY_SIGNALS
    
    def is_exit_signal(self, signal_type: str) -> bool:
        """Check if signal type is an exit signal."""
        return signal_type in self.EXIT_SIGNALS
    
    def is_info_signal(self, signal_type: str) -> bool:
        """Check if signal type is an info signal."""
        return signal_type in self.INFO_SIGNALS
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parser statistics."""
        return {
            "parse_count": self.parse_count,
            "error_count": self.error_count,
            "supported_signals": len(self.SIGNAL_FIELD_MAP),
            "entry_signals": len(self.ENTRY_SIGNALS),
            "exit_signals": len(self.EXIT_SIGNALS),
            "info_signals": len(self.INFO_SIGNALS)
        }


# Singleton instance for easy import
_parser_instance = None


def get_v6_parser() -> V6AlertParser:
    """Get singleton V6 alert parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = V6AlertParser()
    return _parser_instance


def parse_v6_alert(alert_string: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to parse V6 alert.
    
    Args:
        alert_string: Raw alert string from Pine V6
        
    Returns:
        dict: Parsed alert data or None
    """
    return get_v6_parser().parse(alert_string)
