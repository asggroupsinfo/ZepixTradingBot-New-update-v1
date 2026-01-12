"""
Trend Monitor Service - V5 Hybrid Plugin Architecture

This service provides multi-timeframe trend monitoring for all plugins.
Tracks trend direction across multiple timeframes for confluence analysis.

Part of Document 01: Project Overview - Service Layer Architecture
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Trend direction enumeration."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class TrendMonitorService:
    """
    Centralized trend monitoring service for all trading plugins.
    
    Tracks Multi-Timeframe (MTF) Trends:
    - 1M (1 minute) - Scalping
    - 5M (5 minute) - Intraday
    - 15M (15 minute) - Swing
    - 1H (1 hour) - Position
    - 4H (4 hour) - Major trend
    - D1 (Daily) - Long-term trend
    
    Responsibilities:
    - Track trend direction per symbol/timeframe
    - Provide MTF alignment analysis
    - Lock/unlock trends for specific conditions
    - Notify on trend changes
    
    Benefits:
    - Consistent trend analysis across all plugins
    - Centralized trend state management
    - MTF confluence detection
    - Trend change notifications
    
    Usage:
        service = TrendMonitorService(config)
        service.update_trend("EURUSD", "15M", TrendDirection.BULLISH)
        alignment = service.get_mtf_alignment("EURUSD")
    """
    
    # Supported timeframes
    TIMEFRAMES = ["1M", "5M", "15M", "1H", "4H", "D1"]
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Trend Monitor Service.
        
        Args:
            config: Service configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.TrendMonitorService")
        
        # Trend state: {symbol: {timeframe: TrendDirection}}
        self.trends: Dict[str, Dict[str, TrendDirection]] = {}
        
        # Locked trends: {symbol: {timeframe: bool}}
        self.locked_trends: Dict[str, Dict[str, bool]] = {}
        
        # Trend history for analysis
        self.trend_history: List[Dict[str, Any]] = []
        
        self.logger.info("TrendMonitorService initialized")
    
    def get_trend(
        self,
        symbol: str,
        timeframe: str
    ) -> TrendDirection:
        """
        Get current trend for a symbol/timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (e.g., "15M", "1H")
            
        Returns:
            TrendDirection: Current trend direction
        """
        if symbol not in self.trends:
            return TrendDirection.UNKNOWN
        
        return self.trends[symbol].get(timeframe, TrendDirection.UNKNOWN)
    
    def update_trend(
        self,
        symbol: str,
        timeframe: str,
        direction: TrendDirection,
        source: str = ""
    ) -> bool:
        """
        Update trend for a symbol/timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            direction: New trend direction
            source: Source of the update (e.g., "V3_TrendPulse")
            
        Returns:
            bool: True if updated (False if locked)
        """
        # Check if trend is locked
        if self._is_locked(symbol, timeframe):
            self.logger.warning(
                f"Trend locked, ignoring update: {symbol} {timeframe}"
            )
            return False
        
        # Initialize symbol if needed
        if symbol not in self.trends:
            self.trends[symbol] = {}
        
        # Get previous trend
        previous = self.trends[symbol].get(timeframe, TrendDirection.UNKNOWN)
        
        # Update trend
        self.trends[symbol][timeframe] = direction
        
        # Log change if different
        if previous != direction:
            self.logger.info(
                f"Trend changed: {symbol} {timeframe} "
                f"{previous.value} -> {direction.value} [{source}]"
            )
            
            # Record in history
            self.trend_history.append({
                "symbol": symbol,
                "timeframe": timeframe,
                "previous": previous.value,
                "new": direction.value,
                "source": source,
                "timestamp": datetime.now().isoformat()
            })
        
        return True
    
    def get_mtf_alignment(self, symbol: str) -> Dict[str, Any]:
        """
        Get multi-timeframe alignment analysis for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: MTF alignment analysis
        """
        if symbol not in self.trends:
            return {
                "symbol": symbol,
                "aligned": False,
                "direction": TrendDirection.UNKNOWN.value,
                "alignment_score": 0,
                "timeframes": {}
            }
        
        symbol_trends = self.trends[symbol]
        
        # Count directions
        bullish_count = sum(
            1 for tf, d in symbol_trends.items() 
            if d == TrendDirection.BULLISH
        )
        bearish_count = sum(
            1 for tf, d in symbol_trends.items() 
            if d == TrendDirection.BEARISH
        )
        total_count = len(symbol_trends)
        
        # Determine alignment
        if total_count == 0:
            alignment_score = 0
            direction = TrendDirection.UNKNOWN
            aligned = False
        elif bullish_count == total_count:
            alignment_score = 100
            direction = TrendDirection.BULLISH
            aligned = True
        elif bearish_count == total_count:
            alignment_score = 100
            direction = TrendDirection.BEARISH
            aligned = True
        else:
            # Partial alignment
            max_count = max(bullish_count, bearish_count)
            alignment_score = int((max_count / total_count) * 100)
            direction = (
                TrendDirection.BULLISH if bullish_count > bearish_count
                else TrendDirection.BEARISH if bearish_count > bullish_count
                else TrendDirection.NEUTRAL
            )
            aligned = alignment_score >= 80  # 80% threshold for alignment
        
        return {
            "symbol": symbol,
            "aligned": aligned,
            "direction": direction.value,
            "alignment_score": alignment_score,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "total_timeframes": total_count,
            "timeframes": {
                tf: d.value for tf, d in symbol_trends.items()
            }
        }
    
    def lock_trend(self, symbol: str, timeframe: str):
        """
        Lock a trend to prevent updates.
        
        Used during critical trading conditions.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe to lock
        """
        if symbol not in self.locked_trends:
            self.locked_trends[symbol] = {}
        
        self.locked_trends[symbol][timeframe] = True
        self.logger.info(f"Trend locked: {symbol} {timeframe}")
    
    def unlock_trend(self, symbol: str, timeframe: str):
        """
        Unlock a trend to allow updates.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe to unlock
        """
        if symbol in self.locked_trends:
            self.locked_trends[symbol][timeframe] = False
            self.logger.info(f"Trend unlocked: {symbol} {timeframe}")
    
    def _is_locked(self, symbol: str, timeframe: str) -> bool:
        """Check if a trend is locked."""
        if symbol not in self.locked_trends:
            return False
        return self.locked_trends[symbol].get(timeframe, False)
    
    def get_all_trends(self, symbol: str) -> Dict[str, str]:
        """
        Get all trends for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: {timeframe: direction} mapping
        """
        if symbol not in self.trends:
            return {}
        
        return {
            tf: d.value for tf, d in self.trends[symbol].items()
        }
    
    def clear_trends(self, symbol: Optional[str] = None):
        """
        Clear trend data.
        
        Args:
            symbol: Specific symbol (None = all)
        """
        if symbol:
            if symbol in self.trends:
                del self.trends[symbol]
            if symbol in self.locked_trends:
                del self.locked_trends[symbol]
            self.logger.info(f"Cleared trends for {symbol}")
        else:
            self.trends = {}
            self.locked_trends = {}
            self.logger.info("Cleared all trends")
    
    def get_trend_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trend change history.
        
        Args:
            symbol: Filter by symbol (None = all)
            limit: Maximum entries to return
            
        Returns:
            List of trend change events
        """
        history = self.trend_history
        
        if symbol:
            history = [h for h in history if h["symbol"] == symbol]
        
        return history[-limit:]
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status summary.
        
        Returns:
            dict: Service status
        """
        return {
            "symbols_tracked": len(self.trends),
            "total_trends": sum(len(t) for t in self.trends.values()),
            "locked_trends": sum(
                sum(1 for v in l.values() if v)
                for l in self.locked_trends.values()
            ),
            "history_entries": len(self.trend_history)
        }
