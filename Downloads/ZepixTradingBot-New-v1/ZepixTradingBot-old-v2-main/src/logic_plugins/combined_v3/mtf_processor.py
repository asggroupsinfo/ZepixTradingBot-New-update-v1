"""
V3 Combined Logic - MTF Processor Module

Processes Multi-Timeframe 4-Pillar system for V3 signals.

Part of Document 06: Phase 4 - V3 Plugin Migration

Pine Script sends: [1m, 5m, 15m, 1H, 4H, 1D] (6 trends)
Bot extracts: Indices [2:6] = [15m, 1H, 4H, 1D] (4 pillars)
Bot ignores: Indices [0:2] = [1m, 5m] (too noisy)

Input: "1,1,-1,1,1,1" (6 values)
Output: {"15m": -1, "1h": 1, "4h": 1, "1d": 1}
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class V3MTFProcessor:
    """
    Processes Multi-Timeframe 4-Pillar system.
    
    Extracts 4-pillar trends from 6-value MTF string:
    - Ignores 1m, 5m (too noisy)
    - Uses 15m, 1H, 4H, 1D (4 pillars)
    
    Trend Values:
    - 1 = Bullish
    - -1 = Bearish
    - 0 = Neutral
    """
    
    # 4-pillar timeframes (indices 2-5 from 6-value array)
    PILLARS = ['15m', '1h', '4h', '1d']
    
    # Ignored timeframes (too noisy)
    IGNORED_TIMEFRAMES = ['1m', '5m']
    
    # All timeframes in order (as sent by Pine Script)
    ALL_TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']
    
    # Minimum alignment required for entry
    MIN_ALIGNMENT_COUNT = 3  # At least 3/4 pillars must align
    
    def __init__(self, plugin):
        """
        Initialize V3 MTF Processor.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
        """
        self.plugin = plugin
        self.logger = logging.getLogger(f"{__name__}.V3MTFProcessor")
        
        # Load configuration
        self.config = self._load_config()
        
        # Cache for trend data
        self._trend_cache: Dict[str, Dict[str, int]] = {}
        
        self.logger.info("V3MTFProcessor initialized - 4-pillar system ready")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load MTF configuration from plugin config."""
        default_config = {
            'pillars_only': self.PILLARS,
            'ignore_timeframes': self.IGNORED_TIMEFRAMES,
            'min_alignment': self.MIN_ALIGNMENT_COUNT
        }
        
        if hasattr(self.plugin, 'config') and self.plugin.config:
            mtf_config = self.plugin.config.get('mtf_config', {})
            default_config.update(mtf_config)
        
        return default_config
    
    def extract_4_pillar_trends(self, mtf_string: str) -> Dict[str, int]:
        """
        Extract only 4-pillar trends, ignore 1m/5m.
        
        Input: "1,1,-1,1,1,1" (6 values: 1m,5m,15m,1H,4H,1D)
        Output: {"15m": -1, "1h": 1, "4h": 1, "1d": 1}
        
        Args:
            mtf_string: Comma-separated trend values (6 values)
            
        Returns:
            dict: 4-pillar trend dictionary
            
        Raises:
            ValueError: If MTF string is invalid
        """
        if not mtf_string:
            raise ValueError("Empty MTF string")
        
        # Parse MTF string
        try:
            trends = [int(x.strip()) for x in mtf_string.split(',')]
        except ValueError as e:
            raise ValueError(f"Invalid MTF string format: {mtf_string}") from e
        
        if len(trends) != 6:
            raise ValueError(f"Invalid MTF string: expected 6 values, got {len(trends)}")
        
        # Extract 4 pillars (indices 2-5)
        return {
            "15m": trends[2],  # Index 2
            "1h": trends[3],   # Index 3
            "4h": trends[4],   # Index 4
            "1d": trends[5]    # Index 5
        }
    
    def extract_all_trends(self, mtf_string: str) -> Dict[str, int]:
        """
        Extract all 6 timeframe trends.
        
        Args:
            mtf_string: Comma-separated trend values (6 values)
            
        Returns:
            dict: All 6 timeframe trends
        """
        if not mtf_string:
            raise ValueError("Empty MTF string")
        
        trends = [int(x.strip()) for x in mtf_string.split(',')]
        
        if len(trends) != 6:
            raise ValueError(f"Invalid MTF string: expected 6 values, got {len(trends)}")
        
        return {
            "1m": trends[0],
            "5m": trends[1],
            "15m": trends[2],
            "1h": trends[3],
            "4h": trends[4],
            "1d": trends[5]
        }
    
    async def update_trend_database(self, alert: Any):
        """
        Update market_trends table with 4-pillar data.
        
        Args:
            alert: Trend pulse alert with mtf_trends field
        """
        symbol = self._get_attr(alert, 'symbol', '')
        mtf_string = self._get_attr(alert, 'mtf_trends', '')
        
        if not mtf_string:
            self.logger.warning(f"No MTF trends in alert for {symbol}")
            return
        
        try:
            pillars = self.extract_4_pillar_trends(mtf_string)
            
            # Update cache
            self._trend_cache[symbol] = pillars
            
            # Update database for each pillar
            for tf, direction in pillars.items():
                await self._update_trend_record(
                    symbol=symbol,
                    timeframe=tf,
                    direction='bullish' if direction == 1 else 'bearish' if direction == -1 else 'neutral'
                )
            
            self.logger.info(f"MTF 4-Pillar updated for {symbol}: {pillars}")
            
        except ValueError as e:
            self.logger.error(f"MTF update error: {e}")
    
    async def _update_trend_record(
        self,
        symbol: str,
        timeframe: str,
        direction: str
    ):
        """
        Update single trend record in database.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe string
            direction: 'bullish', 'bearish', or 'neutral'
        """
        try:
            if hasattr(self.plugin, 'database') and self.plugin.database:
                await self.plugin.database.update_trend(
                    symbol=symbol,
                    timeframe=timeframe,
                    direction=direction
                )
        except Exception as e:
            self.logger.warning(f"Trend record update error: {e}")
    
    async def validate_trend_alignment(self, alert: Any) -> bool:
        """
        Check if signal aligns with current trends.
        
        For BUY: majority should be bullish (at least 3/4)
        For SELL: majority should be bearish (at least 3/4)
        
        Args:
            alert: V3 alert data
            
        Returns:
            bool: True if trend is aligned
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        mtf_string = self._get_attr(alert, 'mtf_trends', '')
        
        if not mtf_string:
            # Try to get from cache
            if symbol in self._trend_cache:
                pillars = self._trend_cache[symbol]
            else:
                self.logger.warning(f"No MTF data for {symbol}, allowing entry")
                return True
        else:
            try:
                pillars = self.extract_4_pillar_trends(mtf_string)
            except ValueError:
                self.logger.warning(f"Invalid MTF string, allowing entry")
                return True
        
        # Count bullish and bearish pillars
        bullish_count = sum(1 for v in pillars.values() if v == 1)
        bearish_count = sum(1 for v in pillars.values() if v == -1)
        
        min_alignment = self.config.get('min_alignment', self.MIN_ALIGNMENT_COUNT)
        
        if direction == 'BUY':
            aligned = bullish_count >= min_alignment
            self.logger.debug(
                f"BUY alignment check: {bullish_count}/4 bullish "
                f"(need {min_alignment}) = {'PASS' if aligned else 'FAIL'}"
            )
            return aligned
        else:
            aligned = bearish_count >= min_alignment
            self.logger.debug(
                f"SELL alignment check: {bearish_count}/4 bearish "
                f"(need {min_alignment}) = {'PASS' if aligned else 'FAIL'}"
            )
            return aligned
    
    def get_alignment_score(self, pillars: Dict[str, int], direction: str) -> int:
        """
        Get alignment score for direction.
        
        Args:
            pillars: 4-pillar trend dictionary
            direction: 'BUY' or 'SELL'
            
        Returns:
            int: Number of aligned pillars (0-4)
        """
        if direction == 'BUY':
            return sum(1 for v in pillars.values() if v == 1)
        else:
            return sum(1 for v in pillars.values() if v == -1)
    
    def get_trend_summary(self, symbol: str) -> Dict[str, Any]:
        """
        Get trend summary for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: Trend summary
        """
        if symbol not in self._trend_cache:
            return {
                'symbol': symbol,
                'available': False,
                'pillars': None
            }
        
        pillars = self._trend_cache[symbol]
        bullish = sum(1 for v in pillars.values() if v == 1)
        bearish = sum(1 for v in pillars.values() if v == -1)
        
        if bullish >= 3:
            overall = 'BULLISH'
        elif bearish >= 3:
            overall = 'BEARISH'
        else:
            overall = 'MIXED'
        
        return {
            'symbol': symbol,
            'available': True,
            'pillars': pillars,
            'bullish_count': bullish,
            'bearish_count': bearish,
            'overall': overall
        }
    
    def get_cached_trends(self, symbol: str) -> Optional[Dict[str, int]]:
        """
        Get cached trend data for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: Cached pillars or None
        """
        return self._trend_cache.get(symbol)
    
    def clear_cache(self, symbol: str = None):
        """
        Clear trend cache.
        
        Args:
            symbol: Specific symbol to clear, or None for all
        """
        if symbol:
            self._trend_cache.pop(symbol, None)
        else:
            self._trend_cache.clear()
    
    def _get_attr(self, alert: Any, attr: str, default: Any = None) -> Any:
        """Get attribute from alert (supports dict and object)."""
        if isinstance(alert, dict):
            return alert.get(attr, default)
        return getattr(alert, attr, default)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get MTF processor statistics."""
        return {
            'cached_symbols': len(self._trend_cache),
            'pillars': self.PILLARS,
            'ignored_timeframes': self.IGNORED_TIMEFRAMES,
            'min_alignment': self.config.get('min_alignment', self.MIN_ALIGNMENT_COUNT)
        }
