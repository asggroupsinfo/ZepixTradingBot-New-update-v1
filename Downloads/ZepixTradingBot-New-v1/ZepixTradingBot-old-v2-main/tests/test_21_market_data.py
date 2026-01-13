"""
Test Suite for Document 21: Market Data Service Specification

This test file verifies 100% implementation of Document 21 requirements:
- MarketDataService core functionality
- MT5 Integration (symbol_info_tick)
- Spread Monitor (real-time spread checking)
- Historical Data (candles/bars for plugins)
- Caching System (micro-caching)
- Symbol Normalization (broker mapping)
- Pip Value Calculator

Part of V5 Hybrid Plugin Architecture - ATOMIC PROTOCOL
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestMarketDataServiceStructure:
    """Test that all required modules and classes exist."""
    
    def test_market_data_module_exists(self):
        """Test that market_data module exists."""
        from services import market_data
        assert market_data is not None
    
    def test_market_data_service_class_exists(self):
        """Test that MarketDataService class exists."""
        from services.market_data import MarketDataService
        assert MarketDataService is not None
    
    def test_symbol_normalizer_class_exists(self):
        """Test that SymbolNormalizer class exists."""
        from services.market_data import SymbolNormalizer
        assert SymbolNormalizer is not None
    
    def test_pip_value_calculator_class_exists(self):
        """Test that PipValueCalculator class exists."""
        from services.market_data import PipValueCalculator
        assert PipValueCalculator is not None
    
    def test_spread_monitor_class_exists(self):
        """Test that SpreadMonitor class exists."""
        from services.market_data import SpreadMonitor
        assert SpreadMonitor is not None
    
    def test_historical_data_manager_class_exists(self):
        """Test that HistoricalDataManager class exists."""
        from services.market_data import HistoricalDataManager
        assert HistoricalDataManager is not None
    
    def test_factory_function_exists(self):
        """Test that factory function exists."""
        from services.market_data import create_market_data_service
        assert create_market_data_service is not None


class TestMarketDataServiceEnums:
    """Test all enum definitions."""
    
    def test_market_state_enum(self):
        """Test MarketState enum values."""
        from services.market_data import MarketState
        assert MarketState.OPEN.value == "OPEN"
        assert MarketState.CLOSED.value == "CLOSED"
        assert MarketState.PRE_MARKET.value == "PRE_MARKET"
        assert MarketState.POST_MARKET.value == "POST_MARKET"
        assert MarketState.WEEKEND.value == "WEEKEND"
        assert MarketState.HOLIDAY.value == "HOLIDAY"
    
    def test_volatility_state_enum(self):
        """Test VolatilityState enum values."""
        from services.market_data import VolatilityState
        assert VolatilityState.HIGH.value == "HIGH"
        assert VolatilityState.MODERATE.value == "MODERATE"
        assert VolatilityState.LOW.value == "LOW"
        assert VolatilityState.UNKNOWN.value == "UNKNOWN"
    
    def test_symbol_type_enum(self):
        """Test SymbolType enum values."""
        from services.market_data import SymbolType
        assert SymbolType.FOREX.value == "FOREX"
        assert SymbolType.METAL.value == "METAL"
        assert SymbolType.INDEX.value == "INDEX"
        assert SymbolType.CRYPTO.value == "CRYPTO"
        assert SymbolType.STOCK.value == "STOCK"
        assert SymbolType.COMMODITY.value == "COMMODITY"
        assert SymbolType.UNKNOWN.value == "UNKNOWN"


class TestMarketDataServiceDataclasses:
    """Test all dataclass definitions."""
    
    def test_tick_data_dataclass(self):
        """Test TickData dataclass."""
        from services.market_data import TickData
        tick = TickData(
            symbol="XAUUSD",
            bid=2030.45,
            ask=2030.55,
            last=2030.50,
            volume=1000,
            spread_points=10,
            timestamp=datetime.now()
        )
        assert tick.symbol == "XAUUSD"
        assert tick.bid == 2030.45
        assert tick.ask == 2030.55
        assert tick.mid_price == 2030.50
    
    def test_price_bar_dataclass(self):
        """Test PriceBar dataclass."""
        from services.market_data import PriceBar
        bar = PriceBar(
            symbol="XAUUSD",
            timeframe="15m",
            open=2030.00,
            high=2035.00,
            low=2028.00,
            close=2033.00,
            volume=5000,
            timestamp=datetime.now()
        )
        assert bar.symbol == "XAUUSD"
        assert bar.range == 7.0
        assert bar.body == 3.0
        assert bar.is_bullish is True
    
    def test_price_bar_bearish(self):
        """Test PriceBar bearish detection."""
        from services.market_data import PriceBar
        bar = PriceBar(
            symbol="XAUUSD",
            timeframe="15m",
            open=2035.00,
            high=2036.00,
            low=2028.00,
            close=2030.00,
            volume=5000,
            timestamp=datetime.now()
        )
        assert bar.is_bullish is False
    
    def test_symbol_info_dataclass(self):
        """Test SymbolInfo dataclass."""
        from services.market_data import SymbolInfo, SymbolType
        info = SymbolInfo(
            symbol="XAUUSD",
            symbol_type=SymbolType.METAL,
            digits=2,
            point=0.01,
            pip_value=1.0,
            min_lot=0.01,
            max_lot=50.0,
            lot_step=0.01,
            contract_size=100.0,
            trade_mode=0,
            currency_base="XAU",
            currency_profit="USD",
            currency_margin="USD",
            spread_float=True
        )
        assert info.symbol == "XAUUSD"
        assert info.pip_size == 0.1
    
    def test_cache_entry_dataclass(self):
        """Test CacheEntry dataclass."""
        from services.market_data import CacheEntry
        entry = CacheEntry(
            data={"test": "data"},
            timestamp=datetime.now(),
            ttl=1.0
        )
        assert entry.is_valid is True
        
        old_entry = CacheEntry(
            data={"test": "data"},
            timestamp=datetime.now() - timedelta(seconds=5),
            ttl=1.0
        )
        assert old_entry.is_valid is False


class TestSymbolNormalizer:
    """Test SymbolNormalizer functionality."""
    
    def test_normalizer_initialization(self):
        """Test SymbolNormalizer initialization."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        assert normalizer is not None
        assert len(normalizer.mappings) > 0
    
    def test_normalize_gold_to_xauusd(self):
        """Test normalizing GOLD to XAUUSD."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        assert normalizer.normalize("GOLD") == "XAUUSD"
    
    def test_normalize_silver_to_xagusd(self):
        """Test normalizing SILVER to XAGUSD."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        assert normalizer.normalize("SILVER") == "XAGUSD"
    
    def test_normalize_xauusd_pro(self):
        """Test normalizing XAUUSD.pro to XAUUSD."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        assert normalizer.normalize("XAUUSD.pro") == "XAUUSD"
    
    def test_normalize_standard_symbol(self):
        """Test that standard symbols remain unchanged."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        assert normalizer.normalize("XAUUSD") == "XAUUSD"
        assert normalizer.normalize("EURUSD") == "EURUSD"
    
    def test_get_broker_symbol(self):
        """Test getting broker-specific symbol."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        broker_symbols = ["GOLD", "EURUSD", "GBPUSD"]
        assert normalizer.get_broker_symbol("XAUUSD", broker_symbols) == "GOLD"
    
    def test_get_broker_symbol_standard(self):
        """Test getting broker symbol when standard is available."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        broker_symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
        assert normalizer.get_broker_symbol("XAUUSD", broker_symbols) == "XAUUSD"
    
    def test_get_symbol_type_metal(self):
        """Test symbol type detection for metals."""
        from services.market_data import SymbolNormalizer, SymbolType
        normalizer = SymbolNormalizer()
        assert normalizer.get_symbol_type("XAUUSD") == SymbolType.METAL
        assert normalizer.get_symbol_type("GOLD") == SymbolType.METAL
        assert normalizer.get_symbol_type("XAGUSD") == SymbolType.METAL
    
    def test_get_symbol_type_forex(self):
        """Test symbol type detection for forex."""
        from services.market_data import SymbolNormalizer, SymbolType
        normalizer = SymbolNormalizer()
        assert normalizer.get_symbol_type("EURUSD") == SymbolType.FOREX
        assert normalizer.get_symbol_type("GBPUSD") == SymbolType.FOREX
        assert normalizer.get_symbol_type("USDJPY") == SymbolType.FOREX
    
    def test_add_custom_mapping(self):
        """Test adding custom symbol mapping."""
        from services.market_data import SymbolNormalizer
        normalizer = SymbolNormalizer()
        normalizer.add_mapping("BTCUSD", ["BTC/USD", "BITCOIN"])
        assert normalizer.normalize("BITCOIN") == "BTCUSD"
    
    def test_custom_mappings_in_constructor(self):
        """Test custom mappings in constructor."""
        from services.market_data import SymbolNormalizer
        custom = {"CUSTOM": ["CUSTOM.pro", "CUSTOM."]}
        normalizer = SymbolNormalizer(custom_mappings=custom)
        assert normalizer.normalize("CUSTOM.pro") == "CUSTOM"


class TestPipValueCalculator:
    """Test PipValueCalculator functionality."""
    
    def test_calculator_initialization(self):
        """Test PipValueCalculator initialization."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        assert calc.account_currency == "USD"
    
    def test_calculator_custom_currency(self):
        """Test PipValueCalculator with custom currency."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator(account_currency="EUR")
        assert calc.account_currency == "EUR"
    
    def test_pip_value_xauusd(self):
        """Test pip value calculation for XAUUSD."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        pip_value = calc.calculate_pip_value("XAUUSD", 1.0)
        assert pip_value == 10.0
    
    def test_pip_value_xauusd_fractional_lot(self):
        """Test pip value for fractional lot XAUUSD."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        pip_value = calc.calculate_pip_value("XAUUSD", 0.1)
        assert pip_value == 1.0
    
    def test_pip_value_eurusd(self):
        """Test pip value calculation for EURUSD."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        pip_value = calc.calculate_pip_value("EURUSD", 1.0)
        assert pip_value == 10.0
    
    def test_pip_value_usdjpy(self):
        """Test pip value calculation for USDJPY."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        pip_value = calc.calculate_pip_value("USDJPY", 1.0, current_price=150.0)
        assert pip_value > 0
    
    def test_pips_from_price_xauusd(self):
        """Test converting price difference to pips for XAUUSD."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        pips = calc.calculate_pips_from_price("XAUUSD", 1.0)
        assert pips == 10.0
    
    def test_pips_from_price_eurusd(self):
        """Test converting price difference to pips for EURUSD."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        pips = calc.calculate_pips_from_price("EURUSD", 0.0010)
        assert pips == 10.0
    
    def test_pips_from_price_usdjpy(self):
        """Test converting price difference to pips for USDJPY."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        pips = calc.calculate_pips_from_price("USDJPY", 0.10)
        assert pips == 10.0
    
    def test_price_from_pips_xauusd(self):
        """Test converting pips to price difference for XAUUSD."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        price_diff = calc.calculate_price_from_pips("XAUUSD", 10.0)
        assert price_diff == 1.0
    
    def test_price_from_pips_eurusd(self):
        """Test converting pips to price difference for EURUSD."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        price_diff = calc.calculate_price_from_pips("EURUSD", 10.0)
        assert price_diff == 0.001
    
    def test_position_value_calculation(self):
        """Test position value calculation."""
        from services.market_data import PipValueCalculator
        calc = PipValueCalculator()
        value = calc.calculate_position_value("XAUUSD", 1.0, 2000.0)
        assert value == 200000.0


class TestSpreadMonitor:
    """Test SpreadMonitor functionality."""
    
    def test_monitor_initialization(self):
        """Test SpreadMonitor initialization."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor()
        assert monitor is not None
        assert len(monitor.max_spread_config) > 0
    
    def test_monitor_custom_config(self):
        """Test SpreadMonitor with custom config."""
        from services.market_data import SpreadMonitor
        config = {"XAUUSD": 3.0, "EURUSD": 2.0}
        monitor = SpreadMonitor(max_spread_config=config)
        assert monitor.get_max_spread("XAUUSD") == 3.0
        assert monitor.get_max_spread("EURUSD") == 2.0
    
    def test_record_spread(self):
        """Test recording spread."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor()
        monitor.record_spread("XAUUSD", 1.5)
        assert len(monitor.spread_history["XAUUSD"]) == 1
    
    def test_spread_acceptable(self):
        """Test spread acceptability check."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor({"XAUUSD": 2.0})
        assert monitor.is_spread_acceptable("XAUUSD", 1.5) is True
        assert monitor.is_spread_acceptable("XAUUSD", 2.5) is False
    
    def test_average_spread(self):
        """Test average spread calculation."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor()
        monitor.record_spread("XAUUSD", 1.0)
        monitor.record_spread("XAUUSD", 2.0)
        monitor.record_spread("XAUUSD", 3.0)
        avg = monitor.get_average_spread("XAUUSD", minutes=5)
        assert avg == 2.0
    
    def test_spread_stats(self):
        """Test spread statistics."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor()
        monitor.record_spread("XAUUSD", 1.0)
        monitor.record_spread("XAUUSD", 2.0)
        monitor.record_spread("XAUUSD", 3.0)
        stats = monitor.get_spread_stats("XAUUSD")
        assert stats["min"] == 1.0
        assert stats["max"] == 3.0
        assert stats["average"] == 2.0
        assert stats["samples"] == 3
    
    def test_set_max_spread(self):
        """Test setting max spread."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor()
        monitor.set_max_spread("XAUUSD", 5.0)
        assert monitor.get_max_spread("XAUUSD") == 5.0
    
    def test_default_max_spread(self):
        """Test default max spread for unknown symbol."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor()
        assert monitor.get_max_spread("UNKNOWN") == 3.0
    
    def test_spread_history_limit(self):
        """Test spread history size limit."""
        from services.market_data import SpreadMonitor
        monitor = SpreadMonitor()
        monitor.max_history_size = 5
        for i in range(10):
            monitor.record_spread("XAUUSD", float(i))
        assert len(monitor.spread_history["XAUUSD"]) == 5


class TestHistoricalDataManager:
    """Test HistoricalDataManager functionality."""
    
    def test_manager_initialization(self):
        """Test HistoricalDataManager initialization."""
        from services.market_data import HistoricalDataManager
        manager = HistoricalDataManager()
        assert manager is not None
    
    def test_timeframe_map(self):
        """Test timeframe mapping."""
        from services.market_data import HistoricalDataManager
        manager = HistoricalDataManager()
        assert manager.TIMEFRAME_MAP["1m"] == 1
        assert manager.TIMEFRAME_MAP["5m"] == 5
        assert manager.TIMEFRAME_MAP["15m"] == 15
        assert manager.TIMEFRAME_MAP["1h"] == 60
    
    def test_get_bars_mock(self):
        """Test getting bars with mock data."""
        from services.market_data import HistoricalDataManager
        manager = HistoricalDataManager()
        bars = asyncio.run(manager.get_bars("XAUUSD", "15m", 10))
        assert len(bars) == 10
        assert bars[0].symbol == "XAUUSD"
    
    def test_get_price_range(self):
        """Test getting price range."""
        from services.market_data import HistoricalDataManager
        manager = HistoricalDataManager()
        range_data = asyncio.run(manager.get_price_range("XAUUSD", "15m", 10))
        assert range_data is not None
        assert "high" in range_data
        assert "low" in range_data
        assert "range_pips" in range_data
        assert "atr_estimate" in range_data
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        from services.market_data import HistoricalDataManager
        manager = HistoricalDataManager()
        key = manager._get_cache_key("XAUUSD", "15m", 100)
        assert key == "XAUUSD_15m_100"
    
    def test_clear_cache(self):
        """Test clearing cache."""
        from services.market_data import HistoricalDataManager
        manager = HistoricalDataManager()
        manager._cache["test"] = "data"
        manager.clear_cache()
        assert len(manager._cache) == 0


class TestMarketDataServiceCore:
    """Test MarketDataService core functionality."""
    
    def test_service_initialization(self):
        """Test MarketDataService initialization."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert service is not None
        assert service.VERSION == "1.0.0"
    
    def test_service_with_config(self):
        """Test MarketDataService with config."""
        from services.market_data import MarketDataService
        config = {
            "price_cache_ttl": 0.5,
            "symbol_cache_ttl": 120.0,
            "account_currency": "EUR"
        }
        service = MarketDataService(config=config)
        assert service._price_cache_ttl == 0.5
        assert service._symbol_cache_ttl == 120.0
    
    def test_factory_function(self):
        """Test factory function."""
        from services.market_data import create_market_data_service
        service = create_market_data_service()
        assert service is not None
    
    def test_service_has_components(self):
        """Test service has all components."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert service.symbol_normalizer is not None
        assert service.pip_calculator is not None
        assert service.spread_monitor is not None
        assert service.historical_data is not None


class TestMarketDataServiceSpread:
    """Test MarketDataService spread functionality."""
    
    def test_get_current_spread(self):
        """Test getting current spread."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        spread = asyncio.run(service.get_current_spread("XAUUSD"))
        assert spread == 1.5
    
    def test_check_spread_acceptable_true(self):
        """Test spread acceptability when acceptable."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        acceptable = asyncio.run(service.check_spread_acceptable("XAUUSD", 2.0))
        assert acceptable is True
    
    def test_check_spread_acceptable_false(self):
        """Test spread acceptability when not acceptable."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        acceptable = asyncio.run(service.check_spread_acceptable("XAUUSD", 1.0))
        assert acceptable is False


class TestMarketDataServicePrice:
    """Test MarketDataService price functionality."""
    
    def test_get_current_price(self):
        """Test getting current price."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        price = asyncio.run(service.get_current_price("XAUUSD"))
        assert price is not None
        assert "bid" in price
        assert "ask" in price
        assert "spread_pips" in price
        assert "timestamp" in price
    
    def test_get_price_range(self):
        """Test getting price range."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        range_data = asyncio.run(service.get_price_range("XAUUSD", "15m", 20))
        assert range_data is not None
        assert "high" in range_data
        assert "low" in range_data


class TestMarketDataServiceMarketStatus:
    """Test MarketDataService market status functionality."""
    
    def test_is_market_open(self):
        """Test market open check."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        is_open = asyncio.run(service.is_market_open("XAUUSD"))
        assert isinstance(is_open, bool)
    
    def test_get_trading_hours(self):
        """Test getting trading hours."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        hours = asyncio.run(service.get_trading_hours("XAUUSD"))
        assert hours is not None
        assert "is_open" in hours
        assert "session_start" in hours
        assert "session_end" in hours


class TestMarketDataServiceVolatility:
    """Test MarketDataService volatility functionality."""
    
    def test_get_volatility_state(self):
        """Test getting volatility state."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        vol = asyncio.run(service.get_volatility_state("XAUUSD", "15m"))
        assert vol is not None
        assert "state" in vol


class TestMarketDataServiceSymbolInfo:
    """Test MarketDataService symbol info functionality."""
    
    def test_get_symbol_info(self):
        """Test getting symbol info."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        info = asyncio.run(service.get_symbol_info("XAUUSD"))
        assert info is not None
        assert "digits" in info
        assert "point" in info
        assert "min_lot" in info
        assert "max_lot" in info
    
    def test_normalize_symbol(self):
        """Test symbol normalization."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert service.normalize_symbol("GOLD") == "XAUUSD"
    
    def test_get_broker_symbol(self):
        """Test getting broker symbol."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        broker_symbols = ["GOLD", "EURUSD"]
        assert service.get_broker_symbol("XAUUSD", broker_symbols) == "GOLD"


class TestMarketDataServicePipCalculations:
    """Test MarketDataService pip calculation functionality."""
    
    def test_calculate_pip_value(self):
        """Test pip value calculation."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        pip_value = service.calculate_pip_value("XAUUSD", 1.0)
        assert pip_value == 10.0
    
    def test_calculate_pips(self):
        """Test pips calculation."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        pips = service.calculate_pips("XAUUSD", 1.0)
        assert pips == 10.0
    
    def test_calculate_price_diff(self):
        """Test price difference calculation."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        price_diff = service.calculate_price_diff("XAUUSD", 10.0)
        assert price_diff == 1.0


class TestMarketDataServiceHistorical:
    """Test MarketDataService historical data functionality."""
    
    def test_get_historical_bars(self):
        """Test getting historical bars."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        bars = asyncio.run(service.get_historical_bars("XAUUSD", "15m", 50))
        assert len(bars) == 50


class TestMarketDataServiceCaching:
    """Test MarketDataService caching functionality."""
    
    def test_cache_set_and_get(self):
        """Test cache set and get."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        service._set_cached("test_key", {"data": "value"}, 10.0)
        cached = service._get_cached("test_key")
        assert cached == {"data": "value"}
    
    def test_cache_expiry(self):
        """Test cache expiry."""
        from services.market_data import MarketDataService, CacheEntry
        service = MarketDataService()
        service._cache["expired"] = CacheEntry(
            data="old_data",
            timestamp=datetime.now() - timedelta(seconds=10),
            ttl=1.0
        )
        cached = service._get_cached("expired")
        assert cached is None
    
    def test_clear_cache(self):
        """Test clearing cache."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        service._set_cached("test", "data", 10.0)
        service.clear_cache()
        assert len(service._cache) == 0


class TestMarketDataServiceStatistics:
    """Test MarketDataService statistics functionality."""
    
    def test_get_statistics(self):
        """Test getting statistics."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        stats = service.get_statistics()
        assert "version" in stats
        assert "price_requests" in stats
        assert "spread_checks" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "cache_hit_rate" in stats
        assert "errors" in stats
    
    def test_statistics_increment(self):
        """Test statistics increment on operations."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        asyncio.run(service.get_current_spread("XAUUSD"))
        asyncio.run(service.get_current_price("XAUUSD"))
        stats = service.get_statistics()
        assert stats["spread_checks"] >= 1
        assert stats["price_requests"] >= 1
    
    def test_get_spread_stats(self):
        """Test getting spread stats."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        service.spread_monitor.record_spread("XAUUSD", 1.5)
        stats = service.get_spread_stats("XAUUSD")
        assert stats["current"] == 1.5
    
    def test_set_max_spread(self):
        """Test setting max spread."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        service.set_max_spread("XAUUSD", 5.0)
        assert service.spread_monitor.get_max_spread("XAUUSD") == 5.0


class TestDocument21Integration:
    """Test Document 21 integration requirements."""
    
    def test_all_modules_importable(self):
        """Test all modules are importable."""
        from services.market_data import (
            MarketDataService,
            SymbolNormalizer,
            PipValueCalculator,
            SpreadMonitor,
            HistoricalDataManager,
            MarketState,
            VolatilityState,
            SymbolType,
            TickData,
            PriceBar,
            SymbolInfo,
            CacheEntry,
            create_market_data_service
        )
        assert all([
            MarketDataService,
            SymbolNormalizer,
            PipValueCalculator,
            SpreadMonitor,
            HistoricalDataManager,
            MarketState,
            VolatilityState,
            SymbolType,
            TickData,
            PriceBar,
            SymbolInfo,
            CacheEntry,
            create_market_data_service
        ])
    
    def test_service_version(self):
        """Test service version."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert service.VERSION == "1.0.0"
    
    def test_v6_1m_plugin_integration(self):
        """Test V6 1M plugin integration scenario."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        
        spread = asyncio.run(service.get_current_spread("XAUUSD"))
        max_spread = 2.0
        
        if spread <= max_spread:
            price = asyncio.run(service.get_current_price("XAUUSD"))
            assert price is not None
            
            vol = asyncio.run(service.get_volatility_state("XAUUSD", "1m"))
            assert vol is not None
    
    def test_complete_workflow(self):
        """Test complete market data workflow."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        
        normalized = service.normalize_symbol("GOLD")
        assert normalized == "XAUUSD"
        
        spread = asyncio.run(service.get_current_spread("XAUUSD"))
        assert spread < 999.9
        
        price = asyncio.run(service.get_current_price("XAUUSD"))
        assert price is not None
        
        info = asyncio.run(service.get_symbol_info("XAUUSD"))
        assert info is not None
        
        pip_value = service.calculate_pip_value("XAUUSD", 0.1)
        assert pip_value > 0
        
        bars = asyncio.run(service.get_historical_bars("XAUUSD", "15m", 20))
        assert len(bars) > 0
        
        vol = asyncio.run(service.get_volatility_state("XAUUSD", "15m"))
        assert "state" in vol


class TestDocument21Summary:
    """Test Document 21 summary requirements."""
    
    def test_spread_management_implemented(self):
        """Test spread management is implemented."""
        from services.market_data import MarketDataService, SpreadMonitor
        service = MarketDataService()
        assert hasattr(service, 'get_current_spread')
        assert hasattr(service, 'check_spread_acceptable')
        assert isinstance(service.spread_monitor, SpreadMonitor)
    
    def test_price_data_implemented(self):
        """Test price data is implemented."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert hasattr(service, 'get_current_price')
        assert hasattr(service, 'get_price_range')
    
    def test_market_hours_implemented(self):
        """Test market hours is implemented."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert hasattr(service, 'is_market_open')
        assert hasattr(service, 'get_trading_hours')
    
    def test_volatility_analysis_implemented(self):
        """Test volatility analysis is implemented."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert hasattr(service, 'get_volatility_state')
    
    def test_symbol_info_implemented(self):
        """Test symbol info is implemented."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert hasattr(service, 'get_symbol_info')
    
    def test_caching_implemented(self):
        """Test caching is implemented."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert hasattr(service, '_get_cached')
        assert hasattr(service, '_set_cached')
        assert hasattr(service, 'clear_cache')
    
    def test_symbol_normalization_implemented(self):
        """Test symbol normalization is implemented."""
        from services.market_data import MarketDataService, SymbolNormalizer
        service = MarketDataService()
        assert hasattr(service, 'normalize_symbol')
        assert hasattr(service, 'get_broker_symbol')
        assert isinstance(service.symbol_normalizer, SymbolNormalizer)
    
    def test_pip_value_calculator_implemented(self):
        """Test pip value calculator is implemented."""
        from services.market_data import MarketDataService, PipValueCalculator
        service = MarketDataService()
        assert hasattr(service, 'calculate_pip_value')
        assert hasattr(service, 'calculate_pips')
        assert hasattr(service, 'calculate_price_diff')
        assert isinstance(service.pip_calculator, PipValueCalculator)
    
    def test_historical_data_implemented(self):
        """Test historical data is implemented."""
        from services.market_data import MarketDataService, HistoricalDataManager
        service = MarketDataService()
        assert hasattr(service, 'get_historical_bars')
        assert isinstance(service.historical_data, HistoricalDataManager)
    
    def test_statistics_implemented(self):
        """Test statistics is implemented."""
        from services.market_data import MarketDataService
        service = MarketDataService()
        assert hasattr(service, 'get_statistics')
        assert hasattr(service, 'get_spread_stats')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
