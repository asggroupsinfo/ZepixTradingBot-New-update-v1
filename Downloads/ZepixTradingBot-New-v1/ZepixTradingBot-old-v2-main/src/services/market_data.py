"""
Market Data Service - V5 Hybrid Plugin Architecture

This service provides real-time market data access for all plugins with:
- Spread checks and filtering
- Price validation
- Market condition analysis
- Symbol normalization
- Pip value calculations
- Micro-caching for performance

Part of Document 21: Market Data Service Specification
Priority: HIGH (Required for V6 1M Plugin)
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
import time

logger = logging.getLogger(__name__)


class MarketState(Enum):
    """Market state enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    POST_MARKET = "POST_MARKET"
    WEEKEND = "WEEKEND"
    HOLIDAY = "HOLIDAY"


class VolatilityState(Enum):
    """Volatility state enumeration."""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class SymbolType(Enum):
    """Symbol type enumeration."""
    FOREX = "FOREX"
    METAL = "METAL"
    INDEX = "INDEX"
    CRYPTO = "CRYPTO"
    STOCK = "STOCK"
    COMMODITY = "COMMODITY"
    UNKNOWN = "UNKNOWN"


@dataclass
class TickData:
    """Represents a market tick."""
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    spread_points: int
    timestamp: datetime
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price."""
        return (self.bid + self.ask) / 2


@dataclass
class PriceBar:
    """Represents a price bar/candle."""
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime
    
    @property
    def range(self) -> float:
        """Calculate bar range."""
        return self.high - self.low
    
    @property
    def body(self) -> float:
        """Calculate bar body size."""
        return abs(self.close - self.open)
    
    @property
    def is_bullish(self) -> bool:
        """Check if bar is bullish."""
        return self.close > self.open


@dataclass
class SymbolInfo:
    """Comprehensive symbol information."""
    symbol: str
    symbol_type: SymbolType
    digits: int
    point: float
    pip_value: float
    min_lot: float
    max_lot: float
    lot_step: float
    contract_size: float
    trade_mode: int
    currency_base: str
    currency_profit: str
    currency_margin: str
    spread_float: bool
    
    @property
    def pip_size(self) -> float:
        """Calculate pip size based on symbol type."""
        if self.symbol_type == SymbolType.METAL:
            return self.point * 10
        elif self.digits == 5 or self.digits == 3:
            return self.point * 10
        return self.point


@dataclass
class CacheEntry:
    """Cache entry with timestamp."""
    data: Any
    timestamp: datetime
    ttl: float
    
    @property
    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age < self.ttl


class SymbolNormalizer:
    """
    Handles symbol normalization across different brokers.
    
    Different brokers use different symbol names:
    - XM: XAUUSD -> GOLD
    - IC Markets: XAUUSD -> XAUUSD.pro
    - Pepperstone: XAUUSD -> XAUUSD.
    """
    
    DEFAULT_MAPPINGS = {
        "XAUUSD": ["GOLD", "XAUUSD.pro", "XAUUSD.", "XAU/USD", "GOLD."],
        "XAGUSD": ["SILVER", "XAGUSD.pro", "XAGUSD.", "XAG/USD", "SILVER."],
        "EURUSD": ["EURUSD.pro", "EURUSD.", "EUR/USD"],
        "GBPUSD": ["GBPUSD.pro", "GBPUSD.", "GBP/USD"],
        "USDJPY": ["USDJPY.pro", "USDJPY.", "USD/JPY"],
        "USDCHF": ["USDCHF.pro", "USDCHF.", "USD/CHF"],
        "AUDUSD": ["AUDUSD.pro", "AUDUSD.", "AUD/USD"],
        "NZDUSD": ["NZDUSD.pro", "NZDUSD.", "NZD/USD"],
        "USDCAD": ["USDCAD.pro", "USDCAD.", "USD/CAD"],
        "EURJPY": ["EURJPY.pro", "EURJPY.", "EUR/JPY"],
    }
    
    def __init__(self, custom_mappings: Optional[Dict[str, List[str]]] = None):
        """
        Initialize symbol normalizer.
        
        Args:
            custom_mappings: Custom broker-specific mappings
        """
        self.mappings = dict(self.DEFAULT_MAPPINGS)
        if custom_mappings:
            self.mappings.update(custom_mappings)
        self._reverse_mappings: Dict[str, str] = {}
        self._build_reverse_mappings()
        self.logger = logging.getLogger(f"{__name__}.SymbolNormalizer")
    
    def _build_reverse_mappings(self):
        """Build reverse mappings for quick lookup."""
        for standard, variants in self.mappings.items():
            for variant in variants:
                self._reverse_mappings[variant.upper()] = standard
    
    def normalize(self, symbol: str) -> str:
        """
        Normalize a broker-specific symbol to standard format.
        
        Args:
            symbol: Broker-specific symbol name
            
        Returns:
            Standard symbol name (e.g., "GOLD" -> "XAUUSD")
        """
        upper_symbol = symbol.upper()
        if upper_symbol in self._reverse_mappings:
            return self._reverse_mappings[upper_symbol]
        return upper_symbol
    
    def get_broker_symbol(self, standard_symbol: str, broker_symbols: List[str]) -> str:
        """
        Find the broker-specific symbol from available symbols.
        
        Args:
            standard_symbol: Standard symbol name
            broker_symbols: List of available broker symbols
            
        Returns:
            Broker-specific symbol or standard symbol if not found
        """
        upper_standard = standard_symbol.upper()
        
        if upper_standard in broker_symbols:
            return upper_standard
        
        variants = self.mappings.get(upper_standard, [])
        for variant in variants:
            if variant.upper() in [s.upper() for s in broker_symbols]:
                for s in broker_symbols:
                    if s.upper() == variant.upper():
                        return s
        
        return standard_symbol
    
    def get_symbol_type(self, symbol: str) -> SymbolType:
        """
        Determine symbol type from symbol name.
        
        Args:
            symbol: Symbol name
            
        Returns:
            SymbolType enum value
        """
        normalized = self.normalize(symbol).upper()
        
        if normalized in ["XAUUSD", "XAGUSD"]:
            return SymbolType.METAL
        elif normalized.endswith("USD") or normalized.startswith("USD"):
            if len(normalized) == 6:
                return SymbolType.FOREX
        elif "BTC" in normalized or "ETH" in normalized:
            return SymbolType.CRYPTO
        elif normalized in ["US30", "US500", "NAS100", "GER40", "UK100"]:
            return SymbolType.INDEX
        
        return SymbolType.FOREX
    
    def add_mapping(self, standard: str, variants: List[str]):
        """Add custom symbol mapping."""
        self.mappings[standard.upper()] = [v.upper() for v in variants]
        self._build_reverse_mappings()


class PipValueCalculator:
    """
    Calculates accurate pip values for different symbols.
    
    Pip value depends on:
    - Symbol type (forex, metals, indices)
    - Account currency
    - Current exchange rate
    - Contract size
    """
    
    STANDARD_LOT_SIZE = 100000
    METAL_CONTRACT_SIZE = 100
    
    def __init__(self, account_currency: str = "USD"):
        """
        Initialize pip value calculator.
        
        Args:
            account_currency: Account base currency
        """
        self.account_currency = account_currency.upper()
        self.logger = logging.getLogger(f"{__name__}.PipValueCalculator")
    
    def calculate_pip_value(
        self,
        symbol: str,
        lot_size: float,
        symbol_info: Optional[SymbolInfo] = None,
        current_price: Optional[float] = None
    ) -> float:
        """
        Calculate pip value for a position.
        
        Args:
            symbol: Symbol name
            lot_size: Position size in lots
            symbol_info: Symbol information (optional)
            current_price: Current price (optional, for cross pairs)
            
        Returns:
            Pip value in account currency
        """
        symbol_upper = symbol.upper()
        
        if symbol_upper in ["XAUUSD", "GOLD"]:
            pip_size = 0.1
            contract_size = self.METAL_CONTRACT_SIZE
            pip_value = pip_size * contract_size * lot_size
            return round(pip_value, 2)
        
        elif symbol_upper in ["XAGUSD", "SILVER"]:
            pip_size = 0.01
            contract_size = 5000
            pip_value = pip_size * contract_size * lot_size
            return round(pip_value, 2)
        
        elif symbol_upper.endswith("USD"):
            pip_value = 10.0 * lot_size
            return round(pip_value, 2)
        
        elif symbol_upper.startswith("USD"):
            if current_price and current_price > 0:
                pip_value = (10.0 / current_price) * lot_size
            else:
                pip_value = 10.0 * lot_size
            return round(pip_value, 2)
        
        else:
            pip_value = 10.0 * lot_size
            return round(pip_value, 2)
    
    def calculate_position_value(
        self,
        symbol: str,
        lot_size: float,
        price: float,
        symbol_info: Optional[SymbolInfo] = None
    ) -> float:
        """
        Calculate total position value.
        
        Args:
            symbol: Symbol name
            lot_size: Position size in lots
            price: Entry price
            symbol_info: Symbol information (optional)
            
        Returns:
            Position value in account currency
        """
        symbol_upper = symbol.upper()
        
        if symbol_upper in ["XAUUSD", "GOLD"]:
            contract_size = self.METAL_CONTRACT_SIZE
        elif symbol_upper in ["XAGUSD", "SILVER"]:
            contract_size = 5000
        else:
            contract_size = self.STANDARD_LOT_SIZE
        
        if symbol_info:
            contract_size = symbol_info.contract_size
        
        return round(price * contract_size * lot_size, 2)
    
    def calculate_pips_from_price(
        self,
        symbol: str,
        price_diff: float
    ) -> float:
        """
        Convert price difference to pips.
        
        Args:
            symbol: Symbol name
            price_diff: Price difference
            
        Returns:
            Difference in pips
        """
        symbol_upper = symbol.upper()
        
        if symbol_upper in ["XAUUSD", "GOLD"]:
            return round(price_diff * 10, 1)
        elif symbol_upper in ["XAGUSD", "SILVER"]:
            return round(price_diff * 100, 1)
        elif symbol_upper.endswith("JPY"):
            return round(price_diff * 100, 1)
        else:
            return round(price_diff * 10000, 1)
    
    def calculate_price_from_pips(
        self,
        symbol: str,
        pips: float
    ) -> float:
        """
        Convert pips to price difference.
        
        Args:
            symbol: Symbol name
            pips: Number of pips
            
        Returns:
            Price difference
        """
        symbol_upper = symbol.upper()
        
        if symbol_upper in ["XAUUSD", "GOLD"]:
            return round(pips / 10, 5)
        elif symbol_upper in ["XAGUSD", "SILVER"]:
            return round(pips / 100, 5)
        elif symbol_upper.endswith("JPY"):
            return round(pips / 100, 3)
        else:
            return round(pips / 10000, 5)


class SpreadMonitor:
    """
    Real-time spread monitoring and filtering.
    
    Critical for V6 1M Plugin to prevent entries during high spread periods.
    """
    
    def __init__(self, max_spread_config: Optional[Dict[str, float]] = None):
        """
        Initialize spread monitor.
        
        Args:
            max_spread_config: Maximum spread per symbol in pips
        """
        self.max_spread_config = max_spread_config or {
            "XAUUSD": 2.0,
            "XAGUSD": 3.0,
            "EURUSD": 1.5,
            "GBPUSD": 2.0,
            "USDJPY": 1.5,
            "USDCHF": 2.0,
            "AUDUSD": 1.5,
            "NZDUSD": 2.0,
            "USDCAD": 2.0,
            "EURJPY": 2.5,
        }
        self.spread_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.max_history_size = 100
        self.logger = logging.getLogger(f"{__name__}.SpreadMonitor")
    
    def record_spread(self, symbol: str, spread_pips: float):
        """
        Record spread for historical analysis.
        
        Args:
            symbol: Symbol name
            spread_pips: Current spread in pips
        """
        if symbol not in self.spread_history:
            self.spread_history[symbol] = []
        
        self.spread_history[symbol].append((datetime.now(), spread_pips))
        
        if len(self.spread_history[symbol]) > self.max_history_size:
            self.spread_history[symbol] = self.spread_history[symbol][-self.max_history_size:]
    
    def is_spread_acceptable(self, symbol: str, current_spread: float) -> bool:
        """
        Check if current spread is acceptable for trading.
        
        Args:
            symbol: Symbol name
            current_spread: Current spread in pips
            
        Returns:
            True if spread is acceptable
        """
        max_spread = self.max_spread_config.get(symbol.upper(), 3.0)
        acceptable = current_spread <= max_spread
        
        if not acceptable:
            self.logger.info(
                f"Spread rejected for {symbol}: {current_spread} > {max_spread} pips"
            )
        
        return acceptable
    
    def get_average_spread(self, symbol: str, minutes: int = 5) -> Optional[float]:
        """
        Get average spread over recent period.
        
        Args:
            symbol: Symbol name
            minutes: Lookback period in minutes
            
        Returns:
            Average spread in pips or None if no data
        """
        if symbol not in self.spread_history:
            return None
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [s for t, s in self.spread_history[symbol] if t >= cutoff]
        
        if not recent:
            return None
        
        return round(sum(recent) / len(recent), 2)
    
    def get_spread_stats(self, symbol: str) -> Dict[str, Any]:
        """
        Get spread statistics for a symbol.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Dictionary with spread statistics
        """
        if symbol not in self.spread_history or not self.spread_history[symbol]:
            return {
                "symbol": symbol,
                "current": None,
                "average": None,
                "min": None,
                "max": None,
                "samples": 0
            }
        
        spreads = [s for _, s in self.spread_history[symbol]]
        
        return {
            "symbol": symbol,
            "current": spreads[-1] if spreads else None,
            "average": round(sum(spreads) / len(spreads), 2),
            "min": round(min(spreads), 2),
            "max": round(max(spreads), 2),
            "samples": len(spreads)
        }
    
    def set_max_spread(self, symbol: str, max_spread_pips: float):
        """Set maximum acceptable spread for a symbol."""
        self.max_spread_config[symbol.upper()] = max_spread_pips
    
    def get_max_spread(self, symbol: str) -> float:
        """Get maximum acceptable spread for a symbol."""
        return self.max_spread_config.get(symbol.upper(), 3.0)


class HistoricalDataManager:
    """
    Manages historical price data retrieval and caching.
    """
    
    TIMEFRAME_MAP = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "1d": 1440,
    }
    
    def __init__(self, mt5_engine=None, cache_ttl: float = 60.0):
        """
        Initialize historical data manager.
        
        Args:
            mt5_engine: MT5 engine instance
            cache_ttl: Cache time-to-live in seconds
        """
        self.mt5 = mt5_engine
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self.logger = logging.getLogger(f"{__name__}.HistoricalDataManager")
    
    def _get_cache_key(self, symbol: str, timeframe: str, bars: int) -> str:
        """Generate cache key."""
        return f"{symbol}_{timeframe}_{bars}"
    
    async def get_bars(
        self,
        symbol: str,
        timeframe: str,
        bars: int = 100
    ) -> List[PriceBar]:
        """
        Get historical price bars.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string (1m, 5m, 15m, 1h, etc.)
            bars: Number of bars to retrieve
            
        Returns:
            List of PriceBar objects
        """
        cache_key = self._get_cache_key(symbol, timeframe, bars)
        
        if cache_key in self._cache and self._cache[cache_key].is_valid:
            return self._cache[cache_key].data
        
        try:
            if self.mt5:
                tf_value = self.TIMEFRAME_MAP.get(timeframe, 15)
                rates = self.mt5.copy_rates_from_pos(symbol, tf_value, 0, bars)
                
                if rates is None or len(rates) == 0:
                    self.logger.warning(f"No data for {symbol} {timeframe}")
                    return []
                
                price_bars = []
                for rate in rates:
                    bar = PriceBar(
                        symbol=symbol,
                        timeframe=timeframe,
                        open=rate['open'],
                        high=rate['high'],
                        low=rate['low'],
                        close=rate['close'],
                        volume=rate.get('tick_volume', 0),
                        timestamp=datetime.fromtimestamp(rate['time'])
                    )
                    price_bars.append(bar)
                
                self._cache[cache_key] = CacheEntry(
                    data=price_bars,
                    timestamp=datetime.now(),
                    ttl=self.cache_ttl
                )
                
                return price_bars
            else:
                return self._generate_mock_bars(symbol, timeframe, bars)
                
        except Exception as e:
            self.logger.error(f"Failed to get bars for {symbol}: {e}")
            return []
    
    def _generate_mock_bars(
        self,
        symbol: str,
        timeframe: str,
        bars: int
    ) -> List[PriceBar]:
        """Generate mock bars for testing."""
        base_price = 2000.0 if "XAU" in symbol.upper() else 1.1000
        price_bars = []
        
        for i in range(bars):
            bar = PriceBar(
                symbol=symbol,
                timeframe=timeframe,
                open=base_price + (i * 0.01),
                high=base_price + (i * 0.01) + 0.5,
                low=base_price + (i * 0.01) - 0.3,
                close=base_price + (i * 0.01) + 0.2,
                volume=1000 + i * 10,
                timestamp=datetime.now() - timedelta(minutes=i * self.TIMEFRAME_MAP.get(timeframe, 15))
            )
            price_bars.append(bar)
        
        return list(reversed(price_bars))
    
    async def get_price_range(
        self,
        symbol: str,
        timeframe: str,
        bars: int = 20
    ) -> Dict[str, Any]:
        """
        Get price range for recent bars.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string
            bars: Number of bars to analyze
            
        Returns:
            Dictionary with high, low, range, and ATR estimate
        """
        price_bars = await self.get_bars(symbol, timeframe, bars)
        
        if not price_bars:
            return None
        
        high = max(bar.high for bar in price_bars)
        low = min(bar.low for bar in price_bars)
        
        pip_calc = PipValueCalculator()
        range_pips = pip_calc.calculate_pips_from_price(symbol, high - low)
        
        ranges = [bar.range for bar in price_bars]
        avg_range = sum(ranges) / len(ranges)
        atr_pips = pip_calc.calculate_pips_from_price(symbol, avg_range)
        
        return {
            "high": high,
            "low": low,
            "range_pips": round(range_pips, 1),
            "atr_estimate": round(atr_pips, 1),
            "bars_analyzed": len(price_bars)
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache = {}


class MarketDataService:
    """
    Centralized market data service for all trading plugins.
    
    Provides:
    - Real-time price data with micro-caching
    - Spread monitoring and filtering
    - Historical data access
    - Symbol normalization
    - Pip value calculations
    - Market condition analysis
    
    Thread-safe, async-compatible service.
    
    Usage:
        service = MarketDataService(mt5_engine)
        spread = await service.get_current_spread('XAUUSD')
        if spread > 2.0:
            logger.info("Spread too high, skipping entry")
    """
    
    VERSION = "1.0.0"
    
    def __init__(
        self,
        mt5_engine=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Market Data Service.
        
        Args:
            mt5_engine: MetaTrader 5 engine instance
            config: Service configuration
        """
        self.mt5 = mt5_engine
        self.config = config or {}
        
        self._cache: Dict[str, CacheEntry] = {}
        self._price_cache_ttl = self.config.get("price_cache_ttl", 0.1)
        self._symbol_cache_ttl = self.config.get("symbol_cache_ttl", 60.0)
        
        self.symbol_normalizer = SymbolNormalizer(
            self.config.get("symbol_mappings")
        )
        self.pip_calculator = PipValueCalculator(
            self.config.get("account_currency", "USD")
        )
        self.spread_monitor = SpreadMonitor(
            self.config.get("max_spread_config")
        )
        self.historical_data = HistoricalDataManager(
            mt5_engine,
            self.config.get("historical_cache_ttl", 60.0)
        )
        
        self.logger = logging.getLogger(f"{__name__}.MarketDataService")
        self.stats = {
            "price_requests": 0,
            "spread_checks": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        
        self.logger.info("MarketDataService initialized")
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if still valid."""
        if key in self._cache and self._cache[key].is_valid:
            self.stats["cache_hits"] += 1
            return self._cache[key].data
        self.stats["cache_misses"] += 1
        return None
    
    def _set_cached(self, key: str, data: Any, ttl: float):
        """Cache data with timestamp."""
        self._cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl=ttl
        )
    
    async def get_current_spread(self, symbol: str) -> float:
        """
        Get current spread in PIPS.
        
        Args:
            symbol: Symbol name (e.g., 'XAUUSD')
            
        Returns:
            Spread in pips (e.g., 1.5)
            Returns 999.9 on error to prevent trading
        """
        self.stats["spread_checks"] += 1
        
        cache_key = f"spread_{symbol}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.mt5:
                symbol_info = self.mt5.symbol_info(symbol)
                if symbol_info is None:
                    normalized = self.symbol_normalizer.normalize(symbol)
                    symbol_info = self.mt5.symbol_info(normalized)
                
                if symbol_info is None:
                    raise ValueError(f"Symbol {symbol} not found")
                
                spread_points = symbol_info.spread
                point_value = symbol_info.point
                
                symbol_type = self.symbol_normalizer.get_symbol_type(symbol)
                if symbol_type == SymbolType.METAL:
                    spread_pips = (spread_points * point_value) * 10
                else:
                    spread_pips = spread_points / 10.0
                
                spread_pips = round(spread_pips, 1)
            else:
                spread_pips = 1.5
            
            self._set_cached(cache_key, spread_pips, self._price_cache_ttl)
            self.spread_monitor.record_spread(symbol, spread_pips)
            
            return spread_pips
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Failed to get spread for {symbol}: {e}")
            return 999.9
    
    async def check_spread_acceptable(
        self,
        symbol: str,
        max_spread_pips: Optional[float] = None
    ) -> bool:
        """
        Check if spread is within acceptable range.
        
        Args:
            symbol: Symbol name
            max_spread_pips: Maximum acceptable spread (uses config if None)
            
        Returns:
            True if spread <= max_spread_pips
        """
        current_spread = await self.get_current_spread(symbol)
        
        if max_spread_pips is None:
            max_spread_pips = self.spread_monitor.get_max_spread(symbol)
        
        return current_spread <= max_spread_pips
    
    async def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current bid/ask prices.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Dictionary with bid, ask, spread, timestamp
            None on error
        """
        self.stats["price_requests"] += 1
        
        cache_key = f"price_{symbol}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.mt5:
                tick = self.mt5.symbol_info_tick(symbol)
                if tick is None:
                    normalized = self.symbol_normalizer.normalize(symbol)
                    tick = self.mt5.symbol_info_tick(normalized)
                
                if tick is None:
                    raise ValueError(f"No tick data for {symbol}")
                
                spread = await self.get_current_spread(symbol)
                
                price_data = {
                    "bid": tick.bid,
                    "ask": tick.ask,
                    "spread_pips": spread,
                    "last": tick.last,
                    "volume": tick.volume,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                base_price = 2000.0 if "XAU" in symbol.upper() else 1.1000
                spread = await self.get_current_spread(symbol)
                
                price_data = {
                    "bid": base_price,
                    "ask": base_price + 0.10,
                    "spread_pips": spread,
                    "last": base_price,
                    "volume": 0,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            self._set_cached(cache_key, price_data, self._price_cache_ttl)
            return price_data
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    async def get_price_range(
        self,
        symbol: str,
        timeframe: str,
        bars_back: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Get price range (high/low) for recent bars.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string (1m, 5m, 15m, 1h)
            bars_back: Number of bars to analyze
            
        Returns:
            Dictionary with high, low, range_pips, atr_estimate
        """
        return await self.historical_data.get_price_range(symbol, timeframe, bars_back)
    
    async def is_market_open(self, symbol: str) -> bool:
        """
        Check if market is currently open for trading.
        
        Args:
            symbol: Symbol name
            
        Returns:
            True if market is open
        """
        try:
            if self.mt5:
                symbol_info = self.mt5.symbol_info(symbol)
                if symbol_info is None:
                    return False
                
                TRADE_MODE_FULL = 0
                TRADE_MODE_LONGONLY = 1
                TRADE_MODE_SHORTONLY = 2
                
                return symbol_info.trade_mode in [
                    TRADE_MODE_FULL,
                    TRADE_MODE_LONGONLY,
                    TRADE_MODE_SHORTONLY
                ]
            else:
                now = datetime.now()
                if now.weekday() >= 5:
                    return False
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to check market status for {symbol}: {e}")
            return False
    
    async def get_trading_hours(self, symbol: str) -> Dict[str, Any]:
        """
        Get trading hours for symbol.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Dictionary with trading hours information
        """
        is_open = await self.is_market_open(symbol)
        
        return {
            "is_open": is_open,
            "session_start": "00:00",
            "session_end": "23:59",
            "next_session_start": "Monday 00:00" if not is_open else "N/A"
        }
    
    async def get_volatility_state(
        self,
        symbol: str,
        timeframe: str = "15m"
    ) -> Dict[str, Any]:
        """
        Analyze current volatility state.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe for analysis
            
        Returns:
            Dictionary with volatility state and metrics
        """
        try:
            range_data = await self.get_price_range(symbol, timeframe, 20)
            if not range_data:
                return {"state": VolatilityState.UNKNOWN.value}
            
            current_atr = range_data["atr_estimate"]
            
            long_term_data = await self.get_price_range(symbol, timeframe, 100)
            avg_atr = long_term_data["atr_estimate"] if long_term_data else current_atr
            
            vol_ratio = current_atr / avg_atr if avg_atr > 0 else 1.0
            
            if vol_ratio > 1.5:
                state = VolatilityState.HIGH
            elif vol_ratio > 0.8:
                state = VolatilityState.MODERATE
            else:
                state = VolatilityState.LOW
            
            return {
                "state": state.value,
                "atr_current": round(current_atr, 1),
                "atr_average": round(avg_atr, 1),
                "volatility_ratio": round(vol_ratio, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze volatility for {symbol}: {e}")
            return {"state": VolatilityState.UNKNOWN.value}
    
    async def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive symbol information.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Dictionary with symbol information
        """
        cache_key = f"symbol_info_{symbol}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.mt5:
                info = self.mt5.symbol_info(symbol)
                if info is None:
                    normalized = self.symbol_normalizer.normalize(symbol)
                    info = self.mt5.symbol_info(normalized)
                
                if info is None:
                    raise ValueError(f"Symbol {symbol} not found")
                
                symbol_data = {
                    "symbol": symbol,
                    "digits": info.digits,
                    "point": info.point,
                    "pip_value_per_std_lot": self.pip_calculator.calculate_pip_value(symbol, 1.0),
                    "min_lot": info.volume_min,
                    "max_lot": info.volume_max,
                    "lot_step": info.volume_step,
                    "contract_size": info.trade_contract_size,
                    "trade_mode": info.trade_mode
                }
            else:
                symbol_type = self.symbol_normalizer.get_symbol_type(symbol)
                
                if symbol_type == SymbolType.METAL:
                    digits = 2
                    point = 0.01
                    contract_size = 100.0
                else:
                    digits = 5
                    point = 0.00001
                    contract_size = 100000.0
                
                symbol_data = {
                    "symbol": symbol,
                    "digits": digits,
                    "point": point,
                    "pip_value_per_std_lot": self.pip_calculator.calculate_pip_value(symbol, 1.0),
                    "min_lot": 0.01,
                    "max_lot": 50.0,
                    "lot_step": 0.01,
                    "contract_size": contract_size,
                    "trade_mode": 0
                }
            
            self._set_cached(cache_key, symbol_data, self._symbol_cache_ttl)
            return symbol_data
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Failed to get symbol info for {symbol}: {e}")
            return None
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize a broker-specific symbol to standard format."""
        return self.symbol_normalizer.normalize(symbol)
    
    def get_broker_symbol(self, standard_symbol: str, available_symbols: List[str]) -> str:
        """Find the broker-specific symbol from available symbols."""
        return self.symbol_normalizer.get_broker_symbol(standard_symbol, available_symbols)
    
    def calculate_pip_value(
        self,
        symbol: str,
        lot_size: float,
        current_price: Optional[float] = None
    ) -> float:
        """Calculate pip value for a position."""
        return self.pip_calculator.calculate_pip_value(symbol, lot_size, current_price=current_price)
    
    def calculate_pips(self, symbol: str, price_diff: float) -> float:
        """Convert price difference to pips."""
        return self.pip_calculator.calculate_pips_from_price(symbol, price_diff)
    
    def calculate_price_diff(self, symbol: str, pips: float) -> float:
        """Convert pips to price difference."""
        return self.pip_calculator.calculate_price_from_pips(symbol, pips)
    
    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str,
        bars: int = 100
    ) -> List[PriceBar]:
        """Get historical price bars."""
        return await self.historical_data.get_bars(symbol, timeframe, bars)
    
    def get_spread_stats(self, symbol: str) -> Dict[str, Any]:
        """Get spread statistics for a symbol."""
        return self.spread_monitor.get_spread_stats(symbol)
    
    def set_max_spread(self, symbol: str, max_spread_pips: float):
        """Set maximum acceptable spread for a symbol."""
        self.spread_monitor.set_max_spread(symbol, max_spread_pips)
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache = {}
        self.historical_data.clear_cache()
        self.logger.info("Cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "version": self.VERSION,
            "price_requests": self.stats["price_requests"],
            "spread_checks": self.stats["spread_checks"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": round(
                self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"]) * 100,
                1
            ),
            "errors": self.stats["errors"]
        }


def create_market_data_service(
    mt5_engine=None,
    config: Optional[Dict[str, Any]] = None
) -> MarketDataService:
    """
    Factory function to create MarketDataService instance.
    
    Args:
        mt5_engine: MT5 engine instance
        config: Service configuration
        
    Returns:
        Configured MarketDataService instance
    """
    return MarketDataService(mt5_engine, config)
