"""
V6 Price Action Plugin - ADX Integration Module

Provides ADX (Average Directional Index) filtering for V6 entries.
ADX measures trend strength regardless of direction.

Part of Document 03: Phases 2-6 Consolidated Plan - Phase 5
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ADXIntegration:
    """
    ADX Integration for V6 Plugin.
    
    ADX (Average Directional Index) measures trend strength:
    - ADX < 20: Weak/No trend (ranging market)
    - ADX 20-25: Emerging trend
    - ADX 25-50: Strong trend
    - ADX 50-75: Very strong trend
    - ADX > 75: Extremely strong trend (rare)
    
    Used to filter entries:
    - Breakout entries: ADX > 25 (need trend strength)
    - Momentum entries: ADX > 30 (need strong trend)
    - Reversal entries: ADX < 40 (trend exhaustion)
    """
    
    # ADX thresholds
    WEAK_TREND = 20
    EMERGING_TREND = 25
    STRONG_TREND = 30
    VERY_STRONG_TREND = 50
    EXTREME_TREND = 75
    
    # Default thresholds for different entry types
    ENTRY_THRESHOLDS = {
        "breakout": 25,
        "pullback": 20,
        "reversal": 40,  # Max ADX for reversals
        "momentum": 30,
        "support_bounce": 20,
        "resistance_rejection": 20,
        "trend_continuation": 25
    }
    
    def __init__(self, plugin):
        """
        Initialize ADX Integration.
        
        Args:
            plugin: Parent PriceActionV6Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"{__name__}.ADXIntegration")
        
        # Cache ADX values per symbol
        self.adx_cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache expiry in seconds
        self.cache_expiry = 60
        
        self.logger.info("ADXIntegration initialized")
    
    def get_current_adx(self, symbol: str, timeframe: str = "15M") -> float:
        """
        Get current ADX value for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe for ADX calculation
            
        Returns:
            float: ADX value (0-100)
        """
        cache_key = f"{symbol}_{timeframe}"
        
        # Check cache
        if cache_key in self.adx_cache:
            cached = self.adx_cache[cache_key]
            age = (datetime.now() - cached["timestamp"]).total_seconds()
            if age < self.cache_expiry:
                return cached["value"]
        
        # Fetch new ADX value
        adx_value = self._fetch_adx(symbol, timeframe)
        
        # Update cache
        self.adx_cache[cache_key] = {
            "value": adx_value,
            "timestamp": datetime.now()
        }
        
        return adx_value
    
    def _fetch_adx(self, symbol: str, timeframe: str) -> float:
        """
        Fetch ADX value from market data service.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            float: ADX value
        """
        if self.service_api is None:
            return 25.0
        
        try:
            market_data = getattr(self.service_api, 'market_data', None)
            if market_data:
                adx = market_data.get_indicator(symbol, "ADX", timeframe)
                if adx is not None:
                    return adx
        except Exception as e:
            self.logger.warning(f"ADX fetch error: {e}")
        
        return 25.0
    
    def check_adx_filter(
        self,
        symbol: str,
        entry_type: str,
        timeframe: str = "15M"
    ) -> Dict[str, Any]:
        """
        Check if ADX filter passes for an entry type.
        
        Args:
            symbol: Trading symbol
            entry_type: Type of entry (breakout, pullback, etc.)
            timeframe: Timeframe
            
        Returns:
            dict: Filter result with details
        """
        adx_value = self.get_current_adx(symbol, timeframe)
        threshold = self.ENTRY_THRESHOLDS.get(entry_type, 25)
        
        # Reversal entries have max threshold (trend exhaustion)
        if entry_type == "reversal":
            passed = adx_value <= threshold
            reason = "trend_exhaustion" if passed else "trend_too_strong"
        else:
            passed = adx_value >= threshold
            reason = "trend_confirmed" if passed else "trend_too_weak"
        
        result = {
            "passed": passed,
            "adx_value": adx_value,
            "threshold": threshold,
            "entry_type": entry_type,
            "reason": reason,
            "trend_strength": self._get_trend_strength(adx_value)
        }
        
        self.logger.debug(
            f"ADX filter for {symbol} {entry_type}: "
            f"ADX={adx_value:.1f} threshold={threshold} passed={passed}"
        )
        
        return result
    
    def _get_trend_strength(self, adx_value: float) -> str:
        """
        Get trend strength description from ADX value.
        
        Args:
            adx_value: ADX value
            
        Returns:
            str: Trend strength description
        """
        if adx_value < self.WEAK_TREND:
            return "WEAK"
        elif adx_value < self.EMERGING_TREND:
            return "EMERGING"
        elif adx_value < self.STRONG_TREND:
            return "MODERATE"
        elif adx_value < self.VERY_STRONG_TREND:
            return "STRONG"
        elif adx_value < self.EXTREME_TREND:
            return "VERY_STRONG"
        else:
            return "EXTREME"
    
    def get_di_values(self, symbol: str, timeframe: str = "15M") -> Dict[str, float]:
        """
        Get +DI and -DI values for directional analysis.
        
        +DI > -DI: Bullish trend
        -DI > +DI: Bearish trend
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            dict: DI values
        """
        if self.service_api is None:
            return {"plus_di": 25.0, "minus_di": 25.0}
        
        try:
            market_data = getattr(self.service_api, 'market_data', None)
            if market_data:
                plus_di = market_data.get_indicator(symbol, "PLUS_DI", timeframe)
                minus_di = market_data.get_indicator(symbol, "MINUS_DI", timeframe)
                
                if plus_di is not None and minus_di is not None:
                    return {
                        "plus_di": plus_di,
                        "minus_di": minus_di
                    }
        except Exception as e:
            self.logger.warning(f"DI fetch error: {e}")
        
        return {"plus_di": 25.0, "minus_di": 25.0}
    
    def get_trend_direction(self, symbol: str, timeframe: str = "15M") -> str:
        """
        Get trend direction from DI values.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            str: BULLISH, BEARISH, or NEUTRAL
        """
        di_values = self.get_di_values(symbol, timeframe)
        plus_di = di_values["plus_di"]
        minus_di = di_values["minus_di"]
        
        if plus_di > minus_di + 5:  # 5 point buffer
            return "BULLISH"
        elif minus_di > plus_di + 5:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def get_full_analysis(self, symbol: str, timeframe: str = "15M") -> Dict[str, Any]:
        """
        Get full ADX analysis for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            dict: Complete ADX analysis
        """
        adx_value = self.get_current_adx(symbol, timeframe)
        di_values = self.get_di_values(symbol, timeframe)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "adx": adx_value,
            "trend_strength": self._get_trend_strength(adx_value),
            "plus_di": di_values["plus_di"],
            "minus_di": di_values["minus_di"],
            "trend_direction": self.get_trend_direction(symbol, timeframe),
            "entry_recommendations": self._get_entry_recommendations(adx_value),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_entry_recommendations(self, adx_value: float) -> Dict[str, bool]:
        """
        Get entry type recommendations based on ADX.
        
        Args:
            adx_value: Current ADX value
            
        Returns:
            dict: Recommended entry types
        """
        return {
            "breakout": adx_value >= self.ENTRY_THRESHOLDS["breakout"],
            "pullback": adx_value >= self.ENTRY_THRESHOLDS["pullback"],
            "reversal": adx_value <= self.ENTRY_THRESHOLDS["reversal"],
            "momentum": adx_value >= self.ENTRY_THRESHOLDS["momentum"],
            "support_bounce": adx_value >= self.ENTRY_THRESHOLDS["support_bounce"],
            "resistance_rejection": adx_value >= self.ENTRY_THRESHOLDS["resistance_rejection"],
            "trend_continuation": adx_value >= self.ENTRY_THRESHOLDS["trend_continuation"]
        }
    
    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear ADX cache.
        
        Args:
            symbol: Specific symbol (None = all)
        """
        if symbol:
            keys_to_remove = [k for k in self.adx_cache if k.startswith(symbol)]
            for key in keys_to_remove:
                del self.adx_cache[key]
            self.logger.debug(f"Cleared ADX cache for {symbol}")
        else:
            self.adx_cache = {}
            self.logger.debug("Cleared all ADX cache")
    
    def update_adx(self, symbol: str, timeframe: str, value: float):
        """
        Manually update ADX value (from external source).
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            value: ADX value
        """
        cache_key = f"{symbol}_{timeframe}"
        self.adx_cache[cache_key] = {
            "value": value,
            "timestamp": datetime.now()
        }
        self.logger.debug(f"Updated ADX for {symbol} {timeframe}: {value}")
