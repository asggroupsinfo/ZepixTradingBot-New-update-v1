"""
V6 Price Action Plugin - Momentum Integration Module

Provides momentum filtering for V6 entries.
Uses multiple momentum indicators for directional confirmation.

Part of Document 03: Phases 2-6 Consolidated Plan - Phase 5
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MomentumStrength(Enum):
    """Momentum strength levels."""
    STRONG_BEARISH = -2
    BEARISH = -1
    NEUTRAL = 0
    BULLISH = 1
    STRONG_BULLISH = 2


class MomentumIntegration:
    """
    Momentum Integration for V6 Plugin.
    
    Uses multiple momentum indicators:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Stochastic
    - CCI (Commodity Channel Index)
    
    Provides:
    - Directional momentum confirmation
    - Overbought/Oversold detection
    - Momentum divergence detection
    - Entry filtering based on momentum
    """
    
    # RSI thresholds
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    RSI_NEUTRAL_LOW = 45
    RSI_NEUTRAL_HIGH = 55
    
    # Stochastic thresholds
    STOCH_OVERSOLD = 20
    STOCH_OVERBOUGHT = 80
    
    # CCI thresholds
    CCI_OVERSOLD = -100
    CCI_OVERBOUGHT = 100
    
    def __init__(self, plugin):
        """
        Initialize Momentum Integration.
        
        Args:
            plugin: Parent PriceActionV6Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"{__name__}.MomentumIntegration")
        
        # Cache momentum values per symbol
        self.momentum_cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache expiry in seconds
        self.cache_expiry = 30
        
        self.logger.info("MomentumIntegration initialized")
    
    def get_momentum(self, symbol: str, timeframe: str = "15M") -> float:
        """
        Get composite momentum score for a symbol.
        
        Score ranges from -100 to +100:
        - Positive: Bullish momentum
        - Negative: Bearish momentum
        - Near zero: Neutral/No momentum
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            float: Momentum score (-100 to +100)
        """
        cache_key = f"{symbol}_{timeframe}"
        
        # Check cache
        if cache_key in self.momentum_cache:
            cached = self.momentum_cache[cache_key]
            age = (datetime.now() - cached["timestamp"]).total_seconds()
            if age < self.cache_expiry:
                return cached["score"]
        
        # Calculate composite momentum
        rsi = self._get_rsi(symbol, timeframe)
        macd = self._get_macd_histogram(symbol, timeframe)
        stoch = self._get_stochastic(symbol, timeframe)
        
        # Normalize and combine
        rsi_score = self._normalize_rsi(rsi)
        macd_score = self._normalize_macd(macd)
        stoch_score = self._normalize_stochastic(stoch)
        
        # Weighted average (RSI: 40%, MACD: 35%, Stochastic: 25%)
        composite = (rsi_score * 0.40) + (macd_score * 0.35) + (stoch_score * 0.25)
        
        # Update cache
        self.momentum_cache[cache_key] = {
            "score": composite,
            "rsi": rsi,
            "macd": macd,
            "stochastic": stoch,
            "timestamp": datetime.now()
        }
        
        return composite
    
    def _get_rsi(self, symbol: str, timeframe: str) -> float:
        """Get RSI value."""
        if self.service_api is None:
            return 50.0
        
        try:
            market_data = getattr(self.service_api, 'market_data', None)
            if market_data:
                rsi = market_data.get_indicator(symbol, "RSI", timeframe)
                if rsi is not None:
                    return rsi
        except Exception as e:
            self.logger.warning(f"RSI fetch error: {e}")
        
        return 50.0
    
    def _get_macd_histogram(self, symbol: str, timeframe: str) -> float:
        """Get MACD histogram value."""
        if self.service_api is None:
            return 0.0
        
        try:
            market_data = getattr(self.service_api, 'market_data', None)
            if market_data:
                macd_hist = market_data.get_indicator(symbol, "MACD_HIST", timeframe)
                if macd_hist is not None:
                    return macd_hist
        except Exception as e:
            self.logger.warning(f"MACD fetch error: {e}")
        
        return 0.0
    
    def _get_stochastic(self, symbol: str, timeframe: str) -> float:
        """Get Stochastic %K value."""
        if self.service_api is None:
            return 50.0
        
        try:
            market_data = getattr(self.service_api, 'market_data', None)
            if market_data:
                stoch = market_data.get_indicator(symbol, "STOCH_K", timeframe)
                if stoch is not None:
                    return stoch
        except Exception as e:
            self.logger.warning(f"Stochastic fetch error: {e}")
        
        return 50.0
    
    def _normalize_rsi(self, rsi: float) -> float:
        """
        Normalize RSI to -100 to +100 scale.
        
        RSI 0-30: -100 to -33 (oversold/bearish)
        RSI 30-50: -33 to 0 (weak bearish)
        RSI 50-70: 0 to +33 (weak bullish)
        RSI 70-100: +33 to +100 (overbought/bullish)
        """
        if rsi <= 30:
            return -100 + ((rsi / 30) * 67)
        elif rsi <= 50:
            return -33 + (((rsi - 30) / 20) * 33)
        elif rsi <= 70:
            return ((rsi - 50) / 20) * 33
        else:
            return 33 + (((rsi - 70) / 30) * 67)
    
    def _normalize_macd(self, macd_hist: float) -> float:
        """
        Normalize MACD histogram to -100 to +100 scale.
        
        Assumes typical MACD histogram range of -0.01 to +0.01
        """
        # Clamp to reasonable range
        clamped = max(-0.01, min(0.01, macd_hist))
        return (clamped / 0.01) * 100
    
    def _normalize_stochastic(self, stoch: float) -> float:
        """
        Normalize Stochastic to -100 to +100 scale.
        
        Stochastic 0-20: -100 to -60 (oversold)
        Stochastic 20-50: -60 to 0 (bearish)
        Stochastic 50-80: 0 to +60 (bullish)
        Stochastic 80-100: +60 to +100 (overbought)
        """
        if stoch <= 20:
            return -100 + ((stoch / 20) * 40)
        elif stoch <= 50:
            return -60 + (((stoch - 20) / 30) * 60)
        elif stoch <= 80:
            return ((stoch - 50) / 30) * 60
        else:
            return 60 + (((stoch - 80) / 20) * 40)
    
    def check_momentum_filter(
        self,
        symbol: str,
        direction: str,
        timeframe: str = "15M",
        threshold: float = 20.0
    ) -> Dict[str, Any]:
        """
        Check if momentum confirms entry direction.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            timeframe: Timeframe
            threshold: Minimum momentum score required
            
        Returns:
            dict: Filter result with details
        """
        momentum = self.get_momentum(symbol, timeframe)
        
        if direction == "BUY":
            passed = momentum >= threshold
            reason = "bullish_momentum" if passed else "momentum_not_bullish"
        else:  # SELL
            passed = momentum <= -threshold
            reason = "bearish_momentum" if passed else "momentum_not_bearish"
        
        result = {
            "passed": passed,
            "momentum_score": momentum,
            "direction": direction,
            "threshold": threshold,
            "reason": reason,
            "strength": self._get_momentum_strength(momentum)
        }
        
        self.logger.debug(
            f"Momentum filter for {symbol} {direction}: "
            f"score={momentum:.1f} threshold={threshold} passed={passed}"
        )
        
        return result
    
    def _get_momentum_strength(self, score: float) -> MomentumStrength:
        """
        Get momentum strength from score.
        
        Args:
            score: Momentum score
            
        Returns:
            MomentumStrength enum
        """
        if score <= -50:
            return MomentumStrength.STRONG_BEARISH
        elif score <= -20:
            return MomentumStrength.BEARISH
        elif score >= 50:
            return MomentumStrength.STRONG_BULLISH
        elif score >= 20:
            return MomentumStrength.BULLISH
        else:
            return MomentumStrength.NEUTRAL
    
    def is_overbought(self, symbol: str, timeframe: str = "15M") -> bool:
        """
        Check if symbol is in overbought condition.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            bool: True if overbought
        """
        rsi = self._get_rsi(symbol, timeframe)
        stoch = self._get_stochastic(symbol, timeframe)
        
        # Both RSI and Stochastic must be overbought
        return rsi >= self.RSI_OVERBOUGHT and stoch >= self.STOCH_OVERBOUGHT
    
    def is_oversold(self, symbol: str, timeframe: str = "15M") -> bool:
        """
        Check if symbol is in oversold condition.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            bool: True if oversold
        """
        rsi = self._get_rsi(symbol, timeframe)
        stoch = self._get_stochastic(symbol, timeframe)
        
        # Both RSI and Stochastic must be oversold
        return rsi <= self.RSI_OVERSOLD and stoch <= self.STOCH_OVERSOLD
    
    def get_full_analysis(self, symbol: str, timeframe: str = "15M") -> Dict[str, Any]:
        """
        Get full momentum analysis for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            dict: Complete momentum analysis
        """
        momentum = self.get_momentum(symbol, timeframe)
        rsi = self._get_rsi(symbol, timeframe)
        macd = self._get_macd_histogram(symbol, timeframe)
        stoch = self._get_stochastic(symbol, timeframe)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "composite_score": momentum,
            "strength": self._get_momentum_strength(momentum).name,
            "indicators": {
                "rsi": {
                    "value": rsi,
                    "normalized": self._normalize_rsi(rsi),
                    "overbought": rsi >= self.RSI_OVERBOUGHT,
                    "oversold": rsi <= self.RSI_OVERSOLD
                },
                "macd_histogram": {
                    "value": macd,
                    "normalized": self._normalize_macd(macd),
                    "bullish": macd > 0,
                    "bearish": macd < 0
                },
                "stochastic": {
                    "value": stoch,
                    "normalized": self._normalize_stochastic(stoch),
                    "overbought": stoch >= self.STOCH_OVERBOUGHT,
                    "oversold": stoch <= self.STOCH_OVERSOLD
                }
            },
            "conditions": {
                "overbought": self.is_overbought(symbol, timeframe),
                "oversold": self.is_oversold(symbol, timeframe)
            },
            "recommendations": {
                "buy_favorable": momentum > 20 and not self.is_overbought(symbol, timeframe),
                "sell_favorable": momentum < -20 and not self.is_oversold(symbol, timeframe)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_divergence(
        self,
        symbol: str,
        price_direction: str,
        timeframe: str = "15M"
    ) -> Dict[str, Any]:
        """
        Detect momentum divergence.
        
        Bullish divergence: Price making lower lows, momentum making higher lows
        Bearish divergence: Price making higher highs, momentum making lower highs
        
        Args:
            symbol: Trading symbol
            price_direction: Current price direction (UP or DOWN)
            timeframe: Timeframe
            
        Returns:
            dict: Divergence analysis
        """
        momentum = self.get_momentum(symbol, timeframe)
        
        # Simplified divergence detection
        # In production, would compare multiple price/momentum points
        
        bullish_divergence = False
        bearish_divergence = False
        
        if price_direction == "DOWN" and momentum > 0:
            bullish_divergence = True
        elif price_direction == "UP" and momentum < 0:
            bearish_divergence = True
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "bullish_divergence": bullish_divergence,
            "bearish_divergence": bearish_divergence,
            "price_direction": price_direction,
            "momentum_score": momentum,
            "signal": "BULLISH" if bullish_divergence else "BEARISH" if bearish_divergence else "NONE"
        }
    
    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear momentum cache.
        
        Args:
            symbol: Specific symbol (None = all)
        """
        if symbol:
            keys_to_remove = [k for k in self.momentum_cache if k.startswith(symbol)]
            for key in keys_to_remove:
                del self.momentum_cache[key]
            self.logger.debug(f"Cleared momentum cache for {symbol}")
        else:
            self.momentum_cache = {}
            self.logger.debug("Cleared all momentum cache")
    
    def update_momentum(
        self,
        symbol: str,
        timeframe: str,
        rsi: Optional[float] = None,
        macd: Optional[float] = None,
        stochastic: Optional[float] = None
    ):
        """
        Manually update momentum indicators (from external source).
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            rsi: RSI value
            macd: MACD histogram value
            stochastic: Stochastic value
        """
        cache_key = f"{symbol}_{timeframe}"
        
        # Get existing or create new
        if cache_key in self.momentum_cache:
            cached = self.momentum_cache[cache_key]
        else:
            cached = {
                "rsi": 50.0,
                "macd": 0.0,
                "stochastic": 50.0
            }
        
        # Update provided values
        if rsi is not None:
            cached["rsi"] = rsi
        if macd is not None:
            cached["macd"] = macd
        if stochastic is not None:
            cached["stochastic"] = stochastic
        
        # Recalculate composite score
        rsi_score = self._normalize_rsi(cached["rsi"])
        macd_score = self._normalize_macd(cached["macd"])
        stoch_score = self._normalize_stochastic(cached["stochastic"])
        
        cached["score"] = (rsi_score * 0.40) + (macd_score * 0.35) + (stoch_score * 0.25)
        cached["timestamp"] = datetime.now()
        
        self.momentum_cache[cache_key] = cached
        
        self.logger.debug(
            f"Updated momentum for {symbol} {timeframe}: "
            f"RSI={cached['rsi']}, MACD={cached['macd']}, Stoch={cached['stochastic']}"
        )
