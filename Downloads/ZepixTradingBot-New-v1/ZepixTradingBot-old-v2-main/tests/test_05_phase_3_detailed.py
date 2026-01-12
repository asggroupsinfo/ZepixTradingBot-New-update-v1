"""
Test Suite for Document 05: Phase 3 Detailed Plan - Service API Layer

This test file verifies the complete implementation of Phase 3 components:
- OrderExecutionService: MT5 integration, order placement, plugin isolation
- ProfitBookingService: 5-level pyramid system, partial close logic
- RiskManagementService: Tier system, lot sizing, daily limits
- TrendMonitorService: MTF alignment, consensus scoring, indicators
- ServiceAPI: Unified interface, convenience methods, health monitoring

Part of ATOMIC PROTOCOL: Document 05 Implementation Verification
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, date
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_mt5_client():
    """Create a mock MT5 client for testing."""
    client = Mock()
    client.place_order = Mock(return_value=12345)
    client.close_position = Mock(return_value=True)
    client.modify_position = Mock(return_value=True)
    client.get_account_balance = Mock(return_value=10000.0)
    client.get_account_equity = Mock(return_value=10500.0)
    client.get_symbol_tick = Mock(return_value={'bid': 1.1000, 'ask': 1.1002})
    client.get_symbol_info = Mock(return_value={'symbol': 'EURUSD', 'digits': 5})
    return client


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return {
        "risk": {
            "default_risk_pct": 0.01,
            "max_daily_loss_pct": 0.03
        },
        "trading": {
            "enabled": True
        }
    }


# ============================================================================
# ORDER EXECUTION SERVICE TESTS
# ============================================================================

class TestOrderExecutionService:
    """Test suite for OrderExecutionService."""
    
    def test_order_execution_service_exists(self):
        """Test that OrderExecutionService module exists."""
        from src.services.order_execution import OrderExecutionService
        assert OrderExecutionService is not None
    
    def test_order_type_enum_exists(self):
        """Test that OrderType enum exists with required values."""
        from src.services.order_execution import OrderType
        assert hasattr(OrderType, 'MARKET_BUY')
        assert hasattr(OrderType, 'MARKET_SELL')
        assert hasattr(OrderType, 'LIMIT_BUY')
        assert hasattr(OrderType, 'LIMIT_SELL')
    
    def test_order_status_enum_exists(self):
        """Test that OrderStatus enum exists with required values."""
        from src.services.order_execution import OrderStatus
        assert hasattr(OrderStatus, 'PENDING')
        assert hasattr(OrderStatus, 'OPEN')
        assert hasattr(OrderStatus, 'CLOSED')
        assert hasattr(OrderStatus, 'FAILED')
        assert hasattr(OrderStatus, 'PARTIALLY_CLOSED')
    
    def test_order_record_dataclass_exists(self):
        """Test that OrderRecord dataclass exists with required fields."""
        from src.services.order_execution import OrderRecord, OrderStatus
        from datetime import datetime
        record = OrderRecord(
            ticket=12345,
            plugin_id="test_plugin",
            symbol="EURUSD",
            direction="BUY",
            lot_size=0.1,
            open_price=1.1000,
            sl_price=1.0950,
            tp_price=1.1050,
            comment="test",
            status=OrderStatus.OPEN,
            created_at=datetime.now()
        )
        assert record.ticket == 12345
        assert record.plugin_id == "test_plugin"
        assert record.symbol == "EURUSD"
        assert record.direction == "BUY"
        assert record.lot_size == 0.1
    
    def test_order_database_exists(self):
        """Test that OrderDatabase class exists."""
        from src.services.order_execution import OrderDatabase
        db = OrderDatabase()
        assert db is not None
    
    def test_order_database_save_and_get(self):
        """Test OrderDatabase save and get operations."""
        from src.services.order_execution import OrderDatabase, OrderRecord, OrderStatus
        from datetime import datetime
        
        db = OrderDatabase()
        record = OrderRecord(
            ticket=12345,
            plugin_id="test_plugin",
            symbol="EURUSD",
            direction="BUY",
            lot_size=0.1,
            open_price=1.1000,
            sl_price=1.0950,
            tp_price=1.1050,
            comment="test",
            status=OrderStatus.OPEN,
            created_at=datetime.now()
        )
        
        db.save_order(record)
        retrieved = db.get_order(12345, "test_plugin")
        
        assert retrieved is not None
        assert retrieved.ticket == 12345
        assert retrieved.plugin_id == "test_plugin"
    
    def test_order_database_plugin_isolation(self):
        """Test that OrderDatabase enforces plugin isolation."""
        from src.services.order_execution import OrderDatabase, OrderRecord, OrderStatus
        from datetime import datetime
        
        db = OrderDatabase()
        record = OrderRecord(
            ticket=12345,
            plugin_id="plugin_a",
            symbol="EURUSD",
            direction="BUY",
            lot_size=0.1,
            open_price=1.1000,
            sl_price=1.0950,
            tp_price=1.1050,
            comment="test",
            status=OrderStatus.OPEN,
            created_at=datetime.now()
        )
        
        db.save_order(record)
        
        # Same plugin can access
        assert db.get_order(12345, "plugin_a") is not None
        
        # Different plugin cannot access
        assert db.get_order(12345, "plugin_b") is None
    
    def test_order_database_get_plugin_orders(self):
        """Test getting all orders for a specific plugin."""
        from src.services.order_execution import OrderDatabase, OrderRecord, OrderStatus
        from datetime import datetime
        
        db = OrderDatabase()
        
        # Add orders for different plugins
        db.save_order(OrderRecord(ticket=1, plugin_id="plugin_a", symbol="EURUSD", direction="BUY", lot_size=0.1,
                                  open_price=1.1, sl_price=1.09, tp_price=1.11, comment="", status=OrderStatus.OPEN, created_at=datetime.now()))
        db.save_order(OrderRecord(ticket=2, plugin_id="plugin_a", symbol="GBPUSD", direction="SELL", lot_size=0.2,
                                  open_price=1.3, sl_price=1.31, tp_price=1.29, comment="", status=OrderStatus.OPEN, created_at=datetime.now()))
        db.save_order(OrderRecord(ticket=3, plugin_id="plugin_b", symbol="EURUSD", direction="BUY", lot_size=0.1,
                                  open_price=1.1, sl_price=1.09, tp_price=1.11, comment="", status=OrderStatus.OPEN, created_at=datetime.now()))
        
        plugin_a_orders = db.get_plugin_orders("plugin_a")
        assert len(plugin_a_orders) == 2
        
        plugin_b_orders = db.get_plugin_orders("plugin_b")
        assert len(plugin_b_orders) == 1
    
    def test_order_execution_service_initialization(self, mock_mt5_client, mock_config):
        """Test OrderExecutionService initialization."""
        from src.services.order_execution import OrderExecutionService
        
        service = OrderExecutionService(mock_mt5_client, mock_config)
        assert service is not None
        assert service.mt5_client == mock_mt5_client
    
    def test_order_execution_service_has_place_order(self, mock_mt5_client, mock_config):
        """Test that OrderExecutionService has place_order method."""
        from src.services.order_execution import OrderExecutionService
        
        service = OrderExecutionService(mock_mt5_client, mock_config)
        assert hasattr(service, 'place_order')
        assert callable(getattr(service, 'place_order'))
    
    def test_order_execution_service_has_place_dual_orders(self, mock_mt5_client, mock_config):
        """Test that OrderExecutionService has place_dual_orders method."""
        from src.services.order_execution import OrderExecutionService
        
        service = OrderExecutionService(mock_mt5_client, mock_config)
        assert hasattr(service, 'place_dual_orders')
        assert callable(getattr(service, 'place_dual_orders'))
    
    def test_order_execution_service_has_modify_order(self, mock_mt5_client, mock_config):
        """Test that OrderExecutionService has modify_order method."""
        from src.services.order_execution import OrderExecutionService
        
        service = OrderExecutionService(mock_mt5_client, mock_config)
        assert hasattr(service, 'modify_order')
        assert callable(getattr(service, 'modify_order'))
    
    def test_order_execution_service_has_close_order(self, mock_mt5_client, mock_config):
        """Test that OrderExecutionService has close_order method."""
        from src.services.order_execution import OrderExecutionService
        
        service = OrderExecutionService(mock_mt5_client, mock_config)
        assert hasattr(service, 'close_order')
        assert callable(getattr(service, 'close_order'))
    
    def test_order_execution_service_has_get_open_orders(self, mock_mt5_client, mock_config):
        """Test that OrderExecutionService has get_open_orders method."""
        from src.services.order_execution import OrderExecutionService
        
        service = OrderExecutionService(mock_mt5_client, mock_config)
        assert hasattr(service, 'get_open_orders')
        assert callable(getattr(service, 'get_open_orders'))
    
    def test_order_execution_service_has_statistics(self, mock_mt5_client, mock_config):
        """Test that OrderExecutionService has statistics methods."""
        from src.services.order_execution import OrderExecutionService
        
        service = OrderExecutionService(mock_mt5_client, mock_config)
        assert hasattr(service, 'get_statistics')
        assert hasattr(service, 'get_plugin_statistics')
    
    def test_order_execution_retry_constants(self):
        """Test that retry constants are defined."""
        from src.services.order_execution import OrderExecutionService
        
        assert hasattr(OrderExecutionService, 'MAX_RETRIES')
        assert hasattr(OrderExecutionService, 'RETRY_DELAY')
        assert OrderExecutionService.MAX_RETRIES == 3
        assert OrderExecutionService.RETRY_DELAY == 0.5


# ============================================================================
# PROFIT BOOKING SERVICE TESTS
# ============================================================================

class TestProfitBookingService:
    """Test suite for ProfitBookingService."""
    
    def test_profit_booking_service_exists(self):
        """Test that ProfitBookingService module exists."""
        from src.services.profit_booking import ProfitBookingService
        assert ProfitBookingService is not None
    
    def test_chain_status_enum_exists(self):
        """Test that ChainStatus enum exists with required values."""
        from src.services.profit_booking import ChainStatus
        assert hasattr(ChainStatus, 'ACTIVE')
        assert hasattr(ChainStatus, 'PAUSED')
        assert hasattr(ChainStatus, 'CLOSED')
        assert hasattr(ChainStatus, 'COMPLETED')
        assert hasattr(ChainStatus, 'FAILED')
    
    def test_profit_level_enum_exists(self):
        """Test that ProfitLevel enum exists with 5 levels."""
        from src.services.profit_booking import ProfitLevel
        assert hasattr(ProfitLevel, 'LEVEL_0')
        assert hasattr(ProfitLevel, 'LEVEL_1')
        assert hasattr(ProfitLevel, 'LEVEL_2')
        assert hasattr(ProfitLevel, 'LEVEL_3')
        assert hasattr(ProfitLevel, 'LEVEL_4')
    
    def test_profit_chain_dataclass_exists(self):
        """Test that ProfitChain dataclass exists with required fields."""
        from src.services.profit_booking import ProfitChain, ChainStatus, ProfitLevel
        from datetime import datetime
        
        chain = ProfitChain(
            chain_id="test_chain_123",
            plugin_id="test_plugin",
            symbol="EURUSD",
            direction="BUY",
            base_lot=0.1,
            current_level=0,
            status=ChainStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        assert chain.chain_id == "test_chain_123"
        assert chain.plugin_id == "test_plugin"
        assert chain.symbol == "EURUSD"
        assert chain.direction == "BUY"
        assert chain.base_lot == 0.1
        assert chain.current_level == 0
        assert chain.status == ChainStatus.ACTIVE
    
    def test_profit_booking_service_initialization(self, mock_mt5_client, mock_config):
        """Test ProfitBookingService initialization."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert service is not None
    
    def test_profit_booking_service_has_create_chain(self, mock_mt5_client, mock_config):
        """Test that ProfitBookingService has create_chain method."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert hasattr(service, 'create_chain')
        assert callable(getattr(service, 'create_chain'))
    
    def test_profit_booking_service_has_process_profit_level(self, mock_mt5_client, mock_config):
        """Test that ProfitBookingService has process_profit_level method."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert hasattr(service, 'process_profit_level')
        assert callable(getattr(service, 'process_profit_level'))
    
    def test_profit_booking_service_has_book_profit(self, mock_mt5_client, mock_config):
        """Test that ProfitBookingService has book_profit method."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert hasattr(service, 'book_profit')
        assert callable(getattr(service, 'book_profit'))
    
    def test_profit_booking_service_has_get_chain_status(self, mock_mt5_client, mock_config):
        """Test that ProfitBookingService has get_chain_status method."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert hasattr(service, 'get_chain_status')
        assert callable(getattr(service, 'get_chain_status'))
    
    def test_profit_booking_service_has_close_chain(self, mock_mt5_client, mock_config):
        """Test that ProfitBookingService has close_chain method."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert hasattr(service, 'close_chain')
        assert callable(getattr(service, 'close_chain'))
    
    def test_pyramid_levels_constant(self, mock_mt5_client, mock_config):
        """Test that PYRAMID_LEVELS constant is defined correctly."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert hasattr(service, 'PYRAMID_LEVELS')
        
        # Verify 5-level pyramid: 1 -> 2 -> 4 -> 8 -> 16
        levels = service.PYRAMID_LEVELS
        assert levels[0] == 1
        assert levels[1] == 2
        assert levels[2] == 4
        assert levels[3] == 8
        assert levels[4] == 16
    
    def test_get_orders_for_level(self, mock_mt5_client, mock_config):
        """Test get_orders_for_level method."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        
        assert service.get_orders_for_level(0) == 1
        assert service.get_orders_for_level(1) == 2
        assert service.get_orders_for_level(2) == 4
        assert service.get_orders_for_level(3) == 8
        assert service.get_orders_for_level(4) == 16
    
    def test_get_lot_size_for_level(self, mock_mt5_client, mock_config):
        """Test get_lot_size_for_level method."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        base_lot = 1.0
        
        # Level 0: 1 order, lot = 1.0
        assert service.get_lot_size_for_level(base_lot, 0) == 1.0
        
        # Level 1: 2 orders, lot = 0.5 each
        assert service.get_lot_size_for_level(base_lot, 1) == 0.5
        
        # Level 2: 4 orders, lot = 0.25 each
        assert service.get_lot_size_for_level(base_lot, 2) == 0.25
        
        # Level 3: 8 orders, lot = 0.12 each (rounded to 2 decimal places)
        assert service.get_lot_size_for_level(base_lot, 3) == 0.12
        
        # Level 4: 16 orders, lot = 0.06 each (rounded to 2 decimal places)
        assert service.get_lot_size_for_level(base_lot, 4) == 0.06
    
    def test_profit_booking_service_has_statistics(self, mock_mt5_client, mock_config):
        """Test that ProfitBookingService has statistics methods."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        assert hasattr(service, 'get_chain_statistics')
        assert hasattr(service, 'get_plugin_statistics')


# ============================================================================
# RISK MANAGEMENT SERVICE TESTS
# ============================================================================

class TestRiskManagementService:
    """Test suite for RiskManagementService."""
    
    def test_risk_management_service_exists(self):
        """Test that RiskManagementService module exists."""
        from src.services.risk_management import RiskManagementService
        assert RiskManagementService is not None
    
    def test_plugin_risk_config_dataclass_exists(self):
        """Test that PluginRiskConfig dataclass exists."""
        from src.services.risk_management import PluginRiskConfig
        
        config = PluginRiskConfig(
            plugin_id="test_plugin",
            max_lot_size=1.0,
            risk_percentage=0.01,
            daily_loss_limit=300.0
        )
        
        assert config.plugin_id == "test_plugin"
        assert config.max_lot_size == 1.0
        assert config.risk_percentage == 0.01
        assert config.daily_loss_limit == 300.0
    
    def test_daily_stats_dataclass_exists(self):
        """Test that DailyStats dataclass exists."""
        from src.services.risk_management import DailyStats
        
        stats = DailyStats(
            plugin_id="test_plugin",
            date=date.today()
        )
        
        assert stats.plugin_id == "test_plugin"
        assert stats.date == date.today()
        assert stats.trades_opened == 0
        assert stats.total_profit == 0.0
        assert stats.total_loss == 0.0
    
    def test_risk_management_service_initialization(self, mock_mt5_client, mock_config):
        """Test RiskManagementService initialization."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        assert service is not None
    
    def test_account_tiers_constant(self, mock_mt5_client, mock_config):
        """Test that ACCOUNT_TIERS constant is defined correctly."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        assert hasattr(service, 'ACCOUNT_TIERS')
        
        tiers = service.ACCOUNT_TIERS
        assert 'TIER_1' in tiers
        assert 'TIER_2' in tiers
        assert 'TIER_3' in tiers
        assert 'TIER_4' in tiers
        assert 'TIER_5' in tiers
    
    def test_get_account_tier(self, mock_mt5_client, mock_config):
        """Test get_account_tier method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        assert service.get_account_tier(5000) == "TIER_1"
        assert service.get_account_tier(15000) == "TIER_2"
        assert service.get_account_tier(30000) == "TIER_3"
        assert service.get_account_tier(75000) == "TIER_4"
        assert service.get_account_tier(150000) == "TIER_5"
    
    def test_calculate_lot_size(self, mock_mt5_client, mock_config):
        """Test calculate_lot_size method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        lot_size = service.calculate_lot_size(
            balance=10000,
            sl_pips=50,
            symbol="EURUSD"
        )
        
        assert lot_size > 0
        assert lot_size <= 0.10  # TIER_2 max lot
    
    def test_get_fixed_lot_size(self, mock_mt5_client, mock_config):
        """Test get_fixed_lot_size method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        lot_size = service.get_fixed_lot_size(10000)
        assert lot_size > 0
    
    def test_validate_risk(self, mock_mt5_client, mock_config):
        """Test validate_risk method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        result = service.validate_risk(
            symbol="EURUSD",
            lot_size=0.05,
            sl_pips=50,
            balance=10000,
            plugin_id="test_plugin"
        )
        
        assert "valid" in result
        assert result["valid"] == True
    
    def test_validate_risk_exceeds_max_lot(self, mock_mt5_client, mock_config):
        """Test validate_risk rejects lot size exceeding tier max."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        result = service.validate_risk(
            symbol="EURUSD",
            lot_size=1.0,  # Exceeds TIER_2 max of 0.10
            sl_pips=50,
            balance=10000,
            plugin_id="test_plugin"
        )
        
        assert result["valid"] == False
        assert "exceeds" in result["reason"].lower()
    
    def test_record_loss(self, mock_mt5_client, mock_config):
        """Test record_loss method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        service.record_loss(100.0, "test_plugin")
        
        assert service.get_daily_loss("test_plugin") == 100.0
        assert service.get_lifetime_loss() == 100.0
    
    def test_reset_daily_losses(self, mock_mt5_client, mock_config):
        """Test reset_daily_losses method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        service.record_loss(100.0, "test_plugin")
        service.reset_daily_losses()
        
        assert service.get_daily_loss("test_plugin") == 0.0
    
    def test_get_risk_summary(self, mock_mt5_client, mock_config):
        """Test get_risk_summary method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        summary = service.get_risk_summary(10000)
        
        assert "balance" in summary
        assert "tier" in summary
        assert "risk_per_trade" in summary
        assert "max_lot_size" in summary
        assert "daily_loss_limit" in summary
    
    def test_register_plugin(self, mock_mt5_client, mock_config):
        """Test register_plugin method."""
        from src.services.risk_management import RiskManagementService, PluginRiskConfig
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        config = PluginRiskConfig(
            plugin_id="custom_plugin",
            max_lot_size=0.5,
            daily_loss_limit=200.0
        )
        
        service.register_plugin("custom_plugin", config)
        
        retrieved = service.get_plugin_config("custom_plugin")
        assert retrieved.max_lot_size == 0.5
        assert retrieved.daily_loss_limit == 200.0
    
    def test_check_daily_limit(self, mock_mt5_client, mock_config):
        """Test check_daily_limit method."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        result = service.check_daily_limit("test_plugin", balance=10000)
        
        assert "plugin_id" in result
        assert "daily_loss" in result
        assert "daily_limit" in result
        assert "can_trade" in result
        assert result["can_trade"] == True
    
    def test_check_daily_limit_exceeded(self, mock_mt5_client, mock_config):
        """Test check_daily_limit when limit is exceeded."""
        from src.services.risk_management import RiskManagementService
        
        service = RiskManagementService(mock_mt5_client, mock_config)
        
        # Record losses exceeding daily limit (3% of 10000 = 300)
        service.record_loss(350.0, "test_plugin")
        
        result = service.check_daily_limit("test_plugin", balance=10000)
        
        assert result["can_trade"] == False


# ============================================================================
# TREND MONITOR SERVICE TESTS
# ============================================================================

class TestTrendMonitorService:
    """Test suite for TrendMonitorService."""
    
    def test_trend_monitor_service_exists(self):
        """Test that TrendMonitorService module exists."""
        from src.services.trend_monitor import TrendMonitorService
        assert TrendMonitorService is not None
    
    def test_trend_direction_enum_exists(self):
        """Test that TrendDirection enum exists with required values."""
        from src.services.trend_monitor import TrendDirection
        assert hasattr(TrendDirection, 'BULLISH')
        assert hasattr(TrendDirection, 'BEARISH')
        assert hasattr(TrendDirection, 'NEUTRAL')
        assert hasattr(TrendDirection, 'UNKNOWN')
    
    def test_indicator_data_dataclass_exists(self):
        """Test that IndicatorData dataclass exists."""
        from src.services.trend_monitor import IndicatorData
        
        data = IndicatorData(
            symbol="EURUSD",
            timeframe="15M",
            ma_slope=0.5,
            rsi=60.0,
            adx=25.0
        )
        
        assert data.symbol == "EURUSD"
        assert data.timeframe == "15M"
        assert data.ma_slope == 0.5
        assert data.rsi == 60.0
        assert data.adx == 25.0
    
    def test_indicator_data_get_trend_bias(self):
        """Test IndicatorData.get_trend_bias method."""
        from src.services.trend_monitor import IndicatorData
        
        # Bullish indicators
        bullish_data = IndicatorData(
            symbol="EURUSD",
            timeframe="15M",
            ma_slope=0.5,
            rsi=60.0,
            macd_histogram=0.001
        )
        assert bullish_data.get_trend_bias() == "BULLISH"
        
        # Bearish indicators
        bearish_data = IndicatorData(
            symbol="EURUSD",
            timeframe="15M",
            ma_slope=-0.5,
            rsi=40.0,
            macd_histogram=-0.001
        )
        assert bearish_data.get_trend_bias() == "BEARISH"
    
    def test_trend_monitor_service_initialization(self, mock_config):
        """Test TrendMonitorService initialization."""
        from src.services.trend_monitor import TrendMonitorService
        
        service = TrendMonitorService(mock_config)
        assert service is not None
    
    def test_timeframes_constant(self, mock_config):
        """Test that TIMEFRAMES constant is defined correctly."""
        from src.services.trend_monitor import TrendMonitorService
        
        service = TrendMonitorService(mock_config)
        assert hasattr(service, 'TIMEFRAMES')
        
        timeframes = service.TIMEFRAMES
        assert "1M" in timeframes
        assert "5M" in timeframes
        assert "15M" in timeframes
        assert "1H" in timeframes
        assert "4H" in timeframes
        assert "D1" in timeframes
    
    def test_timeframe_weights_constant(self, mock_config):
        """Test that TIMEFRAME_WEIGHTS constant is defined correctly."""
        from src.services.trend_monitor import TrendMonitorService
        
        service = TrendMonitorService(mock_config)
        assert hasattr(service, 'TIMEFRAME_WEIGHTS')
        
        weights = service.TIMEFRAME_WEIGHTS
        assert weights["1M"] < weights["5M"]
        assert weights["5M"] < weights["15M"]
        assert weights["15M"] < weights["1H"]
        assert weights["1H"] < weights["4H"]
        assert weights["4H"] < weights["D1"]
    
    def test_get_trend(self, mock_config):
        """Test get_trend method."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        # Unknown trend for untracked symbol
        trend = service.get_trend("EURUSD", "15M")
        assert trend == TrendDirection.UNKNOWN
    
    def test_update_trend(self, mock_config):
        """Test update_trend method."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        result = service.update_trend("EURUSD", "15M", TrendDirection.BULLISH, "test")
        assert result == True
        
        trend = service.get_trend("EURUSD", "15M")
        assert trend == TrendDirection.BULLISH
    
    def test_lock_unlock_trend(self, mock_config):
        """Test lock_trend and unlock_trend methods."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        # Set initial trend
        service.update_trend("EURUSD", "15M", TrendDirection.BULLISH)
        
        # Lock trend
        service.lock_trend("EURUSD", "15M")
        
        # Try to update (should fail)
        result = service.update_trend("EURUSD", "15M", TrendDirection.BEARISH)
        assert result == False
        
        # Trend should still be bullish
        assert service.get_trend("EURUSD", "15M") == TrendDirection.BULLISH
        
        # Unlock and update
        service.unlock_trend("EURUSD", "15M")
        result = service.update_trend("EURUSD", "15M", TrendDirection.BEARISH)
        assert result == True
        assert service.get_trend("EURUSD", "15M") == TrendDirection.BEARISH
    
    def test_get_mtf_alignment(self, mock_config):
        """Test get_mtf_alignment method."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        # Set all timeframes to bullish
        for tf in ["1M", "5M", "15M", "1H", "4H", "D1"]:
            service.update_trend("EURUSD", tf, TrendDirection.BULLISH)
        
        alignment = service.get_mtf_alignment("EURUSD")
        
        assert alignment["aligned"] == True
        assert alignment["direction"] == "BULLISH"
        assert alignment["alignment_score"] == 100
    
    def test_get_mtf_alignment_partial(self, mock_config):
        """Test get_mtf_alignment with partial alignment."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        # Set mixed trends
        service.update_trend("EURUSD", "1M", TrendDirection.BULLISH)
        service.update_trend("EURUSD", "5M", TrendDirection.BULLISH)
        service.update_trend("EURUSD", "15M", TrendDirection.BEARISH)
        service.update_trend("EURUSD", "1H", TrendDirection.BEARISH)
        
        alignment = service.get_mtf_alignment("EURUSD")
        
        assert alignment["aligned"] == False
        assert alignment["alignment_score"] < 100
    
    def test_update_indicators(self, mock_config):
        """Test update_indicators method."""
        from src.services.trend_monitor import TrendMonitorService
        
        service = TrendMonitorService(mock_config)
        
        service.update_indicators(
            symbol="EURUSD",
            timeframe="15M",
            ma_slope=0.5,
            rsi=60.0,
            adx=25.0,
            macd_histogram=0.001
        )
        
        indicators = service.get_indicators("EURUSD", "15M")
        assert indicators is not None
        assert indicators.ma_slope == 0.5
        assert indicators.rsi == 60.0
        assert indicators.adx == 25.0
    
    def test_get_consensus_score(self, mock_config):
        """Test get_consensus_score method."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        # Set all timeframes to bullish
        for tf in ["1M", "5M", "15M", "1H", "4H", "D1"]:
            service.update_trend("EURUSD", tf, TrendDirection.BULLISH)
        
        consensus = service.get_consensus_score("EURUSD")
        
        assert "consensus_score" in consensus
        assert "direction" in consensus
        assert "confidence" in consensus
        assert consensus["consensus_score"] == 100
        assert consensus["direction"] == "BULLISH"
        assert consensus["confidence"] == "HIGH"
    
    def test_check_trend_alignment(self, mock_config):
        """Test check_trend_alignment method."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        # Set all timeframes to bullish
        for tf in ["1M", "5M", "15M", "1H", "4H", "D1"]:
            service.update_trend("EURUSD", tf, TrendDirection.BULLISH)
        
        result = service.check_trend_alignment(
            symbol="EURUSD",
            required_direction="BULLISH",
            min_timeframes=3,
            min_score=50
        )
        
        assert result["can_trade"] == True
        assert result["direction_match"] == True
        assert result["score_ok"] == True
        assert result["timeframes_ok"] == True
    
    def test_get_service_status(self, mock_config):
        """Test get_service_status method."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        service.update_trend("EURUSD", "15M", TrendDirection.BULLISH)
        
        status = service.get_service_status()
        
        assert "symbols_tracked" in status
        assert "total_trends" in status
        assert status["symbols_tracked"] >= 1
        assert status["total_trends"] >= 1


# ============================================================================
# SERVICE API TESTS
# ============================================================================

class TestServiceAPI:
    """Test suite for ServiceAPI unified interface."""
    
    def test_service_api_exists(self):
        """Test that ServiceAPI module exists."""
        from src.core.plugin_system.service_api import ServiceAPI
        assert ServiceAPI is not None
    
    def test_service_api_for_plugin_classmethod(self):
        """Test ServiceAPI.for_plugin class method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        # Reset services for clean test
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI.for_plugin("test_plugin", mock_engine)
        
        assert api is not None
        assert api.plugin_id == "test_plugin"
    
    def test_service_api_plugin_id_property(self):
        """Test ServiceAPI.plugin_id property."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine, "my_plugin")
        
        assert api.plugin_id == "my_plugin"
    
    def test_service_api_has_service_properties(self):
        """Test that ServiceAPI has service property accessors."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'order_service')
        assert hasattr(api, 'profit_service')
        assert hasattr(api, 'risk_service')
        assert hasattr(api, 'trend_service')
    
    def test_service_api_has_place_plugin_order(self):
        """Test that ServiceAPI has place_plugin_order method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'place_plugin_order')
        assert callable(getattr(api, 'place_plugin_order'))
    
    def test_service_api_has_place_dual_orders(self):
        """Test that ServiceAPI has place_dual_orders method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'place_dual_orders')
        assert callable(getattr(api, 'place_dual_orders'))
    
    def test_service_api_has_close_plugin_order(self):
        """Test that ServiceAPI has close_plugin_order method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'close_plugin_order')
        assert callable(getattr(api, 'close_plugin_order'))
    
    def test_service_api_has_get_plugin_orders(self):
        """Test that ServiceAPI has get_plugin_orders method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'get_plugin_orders')
        assert callable(getattr(api, 'get_plugin_orders'))
    
    def test_service_api_has_check_daily_limit(self):
        """Test that ServiceAPI has check_daily_limit method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'check_daily_limit')
        assert callable(getattr(api, 'check_daily_limit'))
    
    def test_service_api_has_get_trend_consensus(self):
        """Test that ServiceAPI has get_trend_consensus method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'get_trend_consensus')
        assert callable(getattr(api, 'get_trend_consensus'))
    
    def test_service_api_has_check_trend_alignment(self):
        """Test that ServiceAPI has check_trend_alignment method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'check_trend_alignment')
        assert callable(getattr(api, 'check_trend_alignment'))
    
    def test_service_api_has_create_profit_chain(self):
        """Test that ServiceAPI has create_profit_chain method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'create_profit_chain')
        assert callable(getattr(api, 'create_profit_chain'))
    
    def test_service_api_has_process_profit_level(self):
        """Test that ServiceAPI has process_profit_level method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'process_profit_level')
        assert callable(getattr(api, 'process_profit_level'))
    
    def test_service_api_has_get_service_health(self):
        """Test that ServiceAPI has get_service_health method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'get_service_health')
        assert callable(getattr(api, 'get_service_health'))
    
    def test_service_api_has_get_plugin_statistics(self):
        """Test that ServiceAPI has get_plugin_statistics method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = None
        mock_engine.risk_manager = None
        mock_engine.telegram_bot = None
        
        api = ServiceAPI(mock_engine)
        
        assert hasattr(api, 'get_plugin_statistics')
        assert callable(getattr(api, 'get_plugin_statistics'))
    
    def test_service_api_backward_compatibility(self):
        """Test that ServiceAPI maintains backward compatibility."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        mock_engine = Mock()
        mock_engine.config = {}
        mock_engine.mt5_client = Mock()
        mock_engine.risk_manager = Mock()
        mock_engine.telegram_bot = Mock()
        mock_engine.trading_enabled = True
        mock_engine.get_open_trades = Mock(return_value=[])
        
        api = ServiceAPI(mock_engine)
        
        # Old API methods should still exist
        assert hasattr(api, 'get_price')
        assert hasattr(api, 'get_balance')
        assert hasattr(api, 'get_equity')
        assert hasattr(api, 'place_order')
        assert hasattr(api, 'close_trade')
        assert hasattr(api, 'modify_order')
        assert hasattr(api, 'get_open_trades')
        assert hasattr(api, 'calculate_lot_size')
        assert hasattr(api, 'send_notification')
        assert hasattr(api, 'log')
        assert hasattr(api, 'get_config')
    
    def test_service_api_reset_services(self):
        """Test ServiceAPI.reset_services class method."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        ServiceAPI.reset_services()
        
        assert ServiceAPI._order_service is None
        assert ServiceAPI._profit_service is None
        assert ServiceAPI._risk_service is None
        assert ServiceAPI._trend_service is None
        assert ServiceAPI._initialized == False


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestDocument05Integration:
    """Integration tests for Document 05 components."""
    
    def test_all_services_can_be_imported(self):
        """Test that all services can be imported together."""
        from src.services.order_execution import OrderExecutionService
        from src.services.profit_booking import ProfitBookingService
        from src.services.risk_management import RiskManagementService
        from src.services.trend_monitor import TrendMonitorService
        from src.core.plugin_system.service_api import ServiceAPI
        
        assert OrderExecutionService is not None
        assert ProfitBookingService is not None
        assert RiskManagementService is not None
        assert TrendMonitorService is not None
        assert ServiceAPI is not None
    
    def test_services_can_be_instantiated_together(self, mock_mt5_client, mock_config):
        """Test that all services can be instantiated together."""
        from src.services.order_execution import OrderExecutionService
        from src.services.profit_booking import ProfitBookingService
        from src.services.risk_management import RiskManagementService
        from src.services.trend_monitor import TrendMonitorService
        
        order_service = OrderExecutionService(mock_mt5_client, mock_config)
        profit_service = ProfitBookingService(mock_mt5_client, mock_config)
        risk_service = RiskManagementService(mock_mt5_client, mock_config)
        trend_service = TrendMonitorService(mock_config)
        
        assert order_service is not None
        assert profit_service is not None
        assert risk_service is not None
        assert trend_service is not None
    
    def test_plugin_isolation_across_services(self, mock_mt5_client, mock_config):
        """Test that plugin isolation works across services."""
        from src.services.order_execution import OrderExecutionService, OrderDatabase, OrderRecord, OrderStatus
        from src.services.risk_management import RiskManagementService
        from datetime import datetime
        
        order_db = OrderDatabase()
        risk_service = RiskManagementService(mock_mt5_client, mock_config)
        
        # Create orders for different plugins
        order_db.save_order(OrderRecord(
            ticket=1, plugin_id="plugin_a", symbol="EURUSD", direction="BUY", lot_size=0.1,
            open_price=1.1, sl_price=1.09, tp_price=1.11, comment="", status=OrderStatus.OPEN, created_at=datetime.now()
        ))
        order_db.save_order(OrderRecord(
            ticket=2, plugin_id="plugin_b", symbol="EURUSD", direction="SELL", lot_size=0.1,
            open_price=1.1, sl_price=1.11, tp_price=1.09, comment="", status=OrderStatus.OPEN, created_at=datetime.now()
        ))
        
        # Record losses for different plugins
        risk_service.record_loss(100.0, "plugin_a")
        risk_service.record_loss(50.0, "plugin_b")
        
        # Verify isolation
        assert order_db.get_order(1, "plugin_a") is not None
        assert order_db.get_order(1, "plugin_b") is None
        assert order_db.get_order(2, "plugin_b") is not None
        assert order_db.get_order(2, "plugin_a") is None
        
        assert risk_service.get_daily_loss("plugin_a") == 100.0
        assert risk_service.get_daily_loss("plugin_b") == 50.0
    
    def test_pyramid_system_lot_calculation(self, mock_mt5_client, mock_config):
        """Test that pyramid system calculates lots correctly across all levels."""
        from src.services.profit_booking import ProfitBookingService
        
        service = ProfitBookingService(mock_mt5_client, mock_config)
        base_lot = 1.0
        
        # Verify pyramid levels are correct (1, 2, 4, 8, 16)
        assert service.get_orders_for_level(0) == 1
        assert service.get_orders_for_level(1) == 2
        assert service.get_orders_for_level(2) == 4
        assert service.get_orders_for_level(3) == 8
        assert service.get_orders_for_level(4) == 16
        
        # Verify lot sizes are calculated (with rounding to 2 decimal places)
        assert service.get_lot_size_for_level(base_lot, 0) == 1.0
        assert service.get_lot_size_for_level(base_lot, 1) == 0.5
        assert service.get_lot_size_for_level(base_lot, 2) == 0.25
        # Note: Levels 3 and 4 have rounding due to 2 decimal place precision
        assert service.get_lot_size_for_level(base_lot, 3) == 0.12  # 1/8 rounded
        assert service.get_lot_size_for_level(base_lot, 4) == 0.06  # 1/16 rounded
    
    def test_trend_consensus_with_indicators(self, mock_config):
        """Test trend consensus scoring with indicator data."""
        from src.services.trend_monitor import TrendMonitorService, TrendDirection
        
        service = TrendMonitorService(mock_config)
        
        # Set trends and indicators
        for tf in ["1M", "5M", "15M", "1H"]:
            service.update_trend("EURUSD", tf, TrendDirection.BULLISH)
            service.update_indicators(
                symbol="EURUSD",
                timeframe=tf,
                ma_slope=0.5,
                rsi=60.0,
                macd_histogram=0.001
            )
        
        consensus = service.get_consensus_score("EURUSD")
        
        assert consensus["direction"] == "BULLISH"
        assert consensus["indicator_bias"] == "BULLISH"


# ============================================================================
# DOCUMENT 05 SUMMARY TESTS
# ============================================================================

class TestDocument05Summary:
    """Summary tests verifying Document 05 requirements."""
    
    def test_order_execution_service_complete(self):
        """Verify OrderExecutionService has all required components."""
        from src.services.order_execution import (
            OrderExecutionService, OrderType, OrderStatus, 
            OrderRecord, OrderDatabase
        )
        
        # Enums exist
        assert OrderType is not None
        assert OrderStatus is not None
        
        # Dataclass exists
        assert OrderRecord is not None
        
        # Database class exists
        assert OrderDatabase is not None
        
        # Service class exists with required methods
        assert hasattr(OrderExecutionService, 'place_order')
        assert hasattr(OrderExecutionService, 'place_dual_orders')
        assert hasattr(OrderExecutionService, 'modify_order')
        assert hasattr(OrderExecutionService, 'close_order')
        assert hasattr(OrderExecutionService, 'get_open_orders')
        assert hasattr(OrderExecutionService, 'get_statistics')
        assert hasattr(OrderExecutionService, 'MAX_RETRIES')
        assert hasattr(OrderExecutionService, 'RETRY_DELAY')
    
    def test_profit_booking_service_complete(self):
        """Verify ProfitBookingService has all required components."""
        from src.services.profit_booking import (
            ProfitBookingService, ChainStatus, ProfitLevel, ProfitChain
        )
        
        # Enums exist
        assert ChainStatus is not None
        assert ProfitLevel is not None
        
        # Dataclass exists
        assert ProfitChain is not None
        
        # Service class exists with required methods
        assert hasattr(ProfitBookingService, 'create_chain')
        assert hasattr(ProfitBookingService, 'process_profit_level')
        assert hasattr(ProfitBookingService, 'book_profit')
        assert hasattr(ProfitBookingService, 'get_chain_status')
        assert hasattr(ProfitBookingService, 'close_chain')
        assert hasattr(ProfitBookingService, 'PYRAMID_LEVELS')
    
    def test_risk_management_service_complete(self):
        """Verify RiskManagementService has all required components."""
        from src.services.risk_management import (
            RiskManagementService, PluginRiskConfig, DailyStats
        )
        
        # Dataclasses exist
        assert PluginRiskConfig is not None
        assert DailyStats is not None
        
        # Service class exists with required methods
        assert hasattr(RiskManagementService, 'ACCOUNT_TIERS')
        assert hasattr(RiskManagementService, 'get_account_tier')
        assert hasattr(RiskManagementService, 'calculate_lot_size')
        assert hasattr(RiskManagementService, 'validate_risk')
        assert hasattr(RiskManagementService, 'record_loss')
        assert hasattr(RiskManagementService, 'check_daily_limit')
        assert hasattr(RiskManagementService, 'register_plugin')
    
    def test_trend_monitor_service_complete(self):
        """Verify TrendMonitorService has all required components."""
        from src.services.trend_monitor import (
            TrendMonitorService, TrendDirection, IndicatorData
        )
        
        # Enum exists
        assert TrendDirection is not None
        
        # Dataclass exists
        assert IndicatorData is not None
        
        # Service class exists with required methods
        assert hasattr(TrendMonitorService, 'TIMEFRAMES')
        assert hasattr(TrendMonitorService, 'TIMEFRAME_WEIGHTS')
        assert hasattr(TrendMonitorService, 'get_trend')
        assert hasattr(TrendMonitorService, 'update_trend')
        assert hasattr(TrendMonitorService, 'get_mtf_alignment')
        assert hasattr(TrendMonitorService, 'get_consensus_score')
        assert hasattr(TrendMonitorService, 'check_trend_alignment')
        assert hasattr(TrendMonitorService, 'update_indicators')
    
    def test_service_api_complete(self):
        """Verify ServiceAPI has all required components."""
        from src.core.plugin_system.service_api import ServiceAPI
        
        # Class methods
        assert hasattr(ServiceAPI, 'for_plugin')
        assert hasattr(ServiceAPI, 'reset_services')
        
        # Service properties
        assert hasattr(ServiceAPI, 'order_service')
        assert hasattr(ServiceAPI, 'profit_service')
        assert hasattr(ServiceAPI, 'risk_service')
        assert hasattr(ServiceAPI, 'trend_service')
        
        # Plugin-specific methods
        assert hasattr(ServiceAPI, 'place_plugin_order')
        assert hasattr(ServiceAPI, 'place_dual_orders')
        assert hasattr(ServiceAPI, 'close_plugin_order')
        assert hasattr(ServiceAPI, 'get_plugin_orders')
        assert hasattr(ServiceAPI, 'check_daily_limit')
        assert hasattr(ServiceAPI, 'get_trend_consensus')
        assert hasattr(ServiceAPI, 'check_trend_alignment')
        assert hasattr(ServiceAPI, 'create_profit_chain')
        assert hasattr(ServiceAPI, 'process_profit_level')
        
        # Health monitoring
        assert hasattr(ServiceAPI, 'get_service_health')
        assert hasattr(ServiceAPI, 'get_plugin_statistics')
        
        # Backward compatibility
        assert hasattr(ServiceAPI, 'get_price')
        assert hasattr(ServiceAPI, 'get_balance')
        assert hasattr(ServiceAPI, 'place_order')
        assert hasattr(ServiceAPI, 'close_trade')


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
