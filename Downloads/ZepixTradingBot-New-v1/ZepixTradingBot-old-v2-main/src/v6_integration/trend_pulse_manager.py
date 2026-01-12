"""
Trend Pulse Manager for V6 Price Action Integration.

This module manages V6 Trend Pulse alerts and market state:
- Update market_trends table with pulse data
- Get current market state for symbols
- Check pulse alignment for trading decisions
- Performance-optimized database access

Based on Document 16: PHASE_7_V6_INTEGRATION_PLAN.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class MarketState(Enum):
    """Market state enumeration."""
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    UNKNOWN = "UNKNOWN"


@dataclass
class TrendPulseData:
    """Trend pulse data for a symbol/timeframe."""
    symbol: str
    timeframe: str
    bull_count: int
    bear_count: int
    market_state: MarketState
    last_updated: datetime = field(default_factory=datetime.now)
    
    def is_bullish(self) -> bool:
        """Check if trend is bullish."""
        return self.bull_count > self.bear_count
    
    def is_bearish(self) -> bool:
        """Check if trend is bearish."""
        return self.bear_count > self.bull_count
    
    def get_strength(self) -> float:
        """Get trend strength (0.0 to 1.0)."""
        total = self.bull_count + self.bear_count
        if total == 0:
            return 0.0
        return abs(self.bull_count - self.bear_count) / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "bull_count": self.bull_count,
            "bear_count": self.bear_count,
            "market_state": self.market_state.value,
            "last_updated": self.last_updated.isoformat()
        }


class MockDatabase:
    """Mock database for trend pulse data."""
    
    def __init__(self):
        """Initialize mock database."""
        self._data: Dict[str, TrendPulseData] = {}
    
    def _key(self, symbol: str, timeframe: str) -> str:
        """Generate key for symbol/timeframe."""
        return f"{symbol}_{timeframe}"
    
    def execute(self, query: str, params: tuple = ()) -> None:
        """Execute a query (mock implementation)."""
        pass
    
    def query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results (mock implementation)."""
        return []
    
    def query_scalar(self, query: str, params: tuple = ()) -> Any:
        """Execute a query and return scalar result (mock implementation)."""
        return 0
    
    def insert_or_replace(self, symbol: str, timeframe: str, bull_count: int, 
                         bear_count: int, market_state: str) -> None:
        """Insert or replace trend pulse data."""
        key = self._key(symbol, timeframe)
        try:
            state = MarketState(market_state)
        except ValueError:
            state = MarketState.UNKNOWN
        
        self._data[key] = TrendPulseData(
            symbol=symbol,
            timeframe=timeframe,
            bull_count=bull_count,
            bear_count=bear_count,
            market_state=state,
            last_updated=datetime.now()
        )
    
    def get_trend_data(self, symbol: str, timeframe: str) -> Optional[TrendPulseData]:
        """Get trend data for symbol/timeframe."""
        key = self._key(symbol, timeframe)
        return self._data.get(key)
    
    def get_all_trends_for_symbol(self, symbol: str) -> List[TrendPulseData]:
        """Get all trend data for a symbol."""
        return [
            data for key, data in self._data.items()
            if data.symbol == symbol
        ]
    
    def get_total_counts(self, symbol: str) -> Tuple[int, int]:
        """Get total bull/bear counts for a symbol."""
        trends = self.get_all_trends_for_symbol(symbol)
        total_bulls = sum(t.bull_count for t in trends)
        total_bears = sum(t.bear_count for t in trends)
        return total_bulls, total_bears


class TrendPulseManager:
    """
    Manages V6 Trend Pulse alerts.
    Separate from V3 Traditional Trend Manager.
    """
    
    def __init__(self, database: Optional[MockDatabase] = None):
        """Initialize Trend Pulse Manager."""
        self.db = database or MockDatabase()
        self._cache: Dict[str, TrendPulseData] = {}
        self._cache_ttl_seconds = 5
        self._last_cache_update: Dict[str, datetime] = {}
    
    def _cache_key(self, symbol: str, timeframe: str = "") -> str:
        """Generate cache key."""
        return f"{symbol}_{timeframe}" if timeframe else symbol
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        if key not in self._last_cache_update:
            return False
        elapsed = (datetime.now() - self._last_cache_update[key]).total_seconds()
        return elapsed < self._cache_ttl_seconds
    
    def update_pulse(self, symbol: str, timeframe: str, bull_count: int,
                    bear_count: int, state: str) -> None:
        """
        Update market_trends table with pulse data.
        
        Args:
            symbol: Trading symbol (e.g., "XAUUSD")
            timeframe: Timeframe (e.g., "15")
            bull_count: Number of bullish indicators
            bear_count: Number of bearish indicators
            state: Market state string
        """
        self.db.insert_or_replace(symbol, timeframe, bull_count, bear_count, state)
        
        key = self._cache_key(symbol, timeframe)
        try:
            market_state = MarketState(state)
        except ValueError:
            market_state = MarketState.UNKNOWN
        
        self._cache[key] = TrendPulseData(
            symbol=symbol,
            timeframe=timeframe,
            bull_count=bull_count,
            bear_count=bear_count,
            market_state=market_state,
            last_updated=datetime.now()
        )
        self._last_cache_update[key] = datetime.now()
        
        logger.info(f"Trend Pulse: {symbol} {timeframe} -> {state} (B:{bull_count}/S:{bear_count})")
    
    def update_pulse_from_alert(self, alert: Any) -> None:
        """
        Update pulse from TrendPulseAlert object.
        
        Args:
            alert: TrendPulseAlert object
        """
        self.update_pulse(
            symbol=alert.symbol,
            timeframe=alert.tf,
            bull_count=alert.bull_count,
            bear_count=alert.bear_count,
            state=alert.state
        )
    
    def get_market_state(self, symbol: str) -> MarketState:
        """
        Get current market state for symbol.
        Aggregates across all timeframes.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            MarketState: TRENDING_BULLISH, TRENDING_BEARISH, SIDEWAYS, or UNKNOWN
        """
        trends = self.db.get_all_trends_for_symbol(symbol)
        
        if not trends:
            return MarketState.UNKNOWN
        
        state_counts: Dict[MarketState, int] = {}
        for trend in trends:
            state = trend.market_state
            state_counts[state] = state_counts.get(state, 0) + 1
        
        if not state_counts:
            return MarketState.UNKNOWN
        
        return max(state_counts.keys(), key=lambda s: state_counts[s])
    
    def get_market_state_string(self, symbol: str) -> str:
        """Get market state as string."""
        return self.get_market_state(symbol).value
    
    def check_pulse_alignment(self, symbol: str, direction: str) -> bool:
        """
        Check if pulse alignment supports the trade direction.
        
        For BUY: bull_count should be > bear_count
        For SELL: bear_count should be > bull_count
        
        Args:
            symbol: Trading symbol
            direction: Trade direction ("BUY" or "SELL")
        
        Returns:
            bool: True if aligned, False otherwise
        """
        total_bulls, total_bears = self.db.get_total_counts(symbol)
        
        if direction.upper() == "BUY":
            return total_bulls > total_bears
        elif direction.upper() == "SELL":
            return total_bears > total_bulls
        
        return False
    
    def get_trend_strength(self, symbol: str) -> float:
        """
        Get overall trend strength for a symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            float: Strength from 0.0 (no trend) to 1.0 (strong trend)
        """
        total_bulls, total_bears = self.db.get_total_counts(symbol)
        total = total_bulls + total_bears
        
        if total == 0:
            return 0.0
        
        return abs(total_bulls - total_bears) / total
    
    def get_trend_data(self, symbol: str, timeframe: str) -> Optional[TrendPulseData]:
        """
        Get trend data for specific symbol/timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
        
        Returns:
            TrendPulseData or None
        """
        key = self._cache_key(symbol, timeframe)
        
        if key in self._cache and self._is_cache_valid(key):
            return self._cache[key]
        
        return self.db.get_trend_data(symbol, timeframe)
    
    def is_trending(self, symbol: str) -> bool:
        """Check if symbol is in a trending state."""
        state = self.get_market_state(symbol)
        return state in [MarketState.TRENDING_BULLISH, MarketState.TRENDING_BEARISH]
    
    def is_sideways(self, symbol: str) -> bool:
        """Check if symbol is in sideways state."""
        state = self.get_market_state(symbol)
        return state == MarketState.SIDEWAYS
    
    def get_all_symbols(self) -> List[str]:
        """Get all symbols with trend data."""
        symbols = set()
        for key in self.db._data.keys():
            symbol = key.split("_")[0]
            symbols.add(symbol)
        return list(symbols)
    
    def clear_cache(self) -> None:
        """Clear the trend pulse cache."""
        self._cache.clear()
        self._last_cache_update.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        return {
            "cached_entries": len(self._cache),
            "symbols": self.get_all_symbols(),
            "cache_ttl_seconds": self._cache_ttl_seconds
        }
