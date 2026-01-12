"""
Test Suite for Document 10: API Specifications

This test file verifies the complete implementation of Document 10:
- Service API Contracts (IOrderExecutionService, IRiskManagementService, etc.)
- Request/Response Models (DualOrderV3Request, etc.)
- Plugin Permissions (PermissionChecker, PluginIsolation)
- API Package Structure

Test Categories:
- TestAPIPackageStructure: Package imports and exports
- TestServiceAPIContracts: Interface definitions
- TestOrderExecutionModels: Order request/response models
- TestRiskManagementModels: Risk request/response models
- TestTrendManagementModels: Trend request/response models
- TestProfitBookingModels: Profit booking models
- TestMarketDataModels: Market data models
- TestPluginPermissions: Permission definitions
- TestPermissionChecker: Permission checking logic
- TestPluginIsolation: Plugin isolation enforcement
- TestDocument10Integration: All components working together
- TestDocument10Summary: Summary verification
"""

import unittest
import os
import sys
from abc import ABC

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestAPIPackageStructure(unittest.TestCase):
    """Test API package structure and imports."""
    
    def test_contracts_module_exists(self):
        """Test that contracts.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api', 'contracts.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_models_module_exists(self):
        """Test that models.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api', 'models.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_permissions_module_exists(self):
        """Test that permissions.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'api', 'permissions.py'
        )
        self.assertTrue(os.path.exists(module_path))
    
    def test_import_contracts(self):
        """Test importing contracts module."""
        from api import contracts
        self.assertIsNotNone(contracts)
    
    def test_import_models(self):
        """Test importing models module."""
        from api import models
        self.assertIsNotNone(models)
    
    def test_import_permissions(self):
        """Test importing permissions module."""
        from api import permissions
        self.assertIsNotNone(permissions)
    
    def test_import_service_api_contracts(self):
        """Test importing service API contracts."""
        from api import (
            IOrderExecutionService,
            IRiskManagementService,
            ITrendManagementService,
            IProfitBookingService,
            IMarketDataService,
            IServiceAPI
        )
        self.assertIsNotNone(IOrderExecutionService)
        self.assertIsNotNone(IRiskManagementService)
        self.assertIsNotNone(ITrendManagementService)
        self.assertIsNotNone(IProfitBookingService)
        self.assertIsNotNone(IMarketDataService)
        self.assertIsNotNone(IServiceAPI)
    
    def test_import_enums(self):
        """Test importing enumerations."""
        from api import OrderType, LogicRoute, MarketState
        self.assertIsNotNone(OrderType)
        self.assertIsNotNone(LogicRoute)
        self.assertIsNotNone(MarketState)
    
    def test_import_request_models(self):
        """Test importing request models."""
        from api import (
            DualOrderV3Request,
            SingleOrderRequest,
            DualOrderV6Request,
            ModifyOrderRequest,
            ClosePositionRequest,
            ClosePartialRequest
        )
        self.assertIsNotNone(DualOrderV3Request)
        self.assertIsNotNone(SingleOrderRequest)
        self.assertIsNotNone(DualOrderV6Request)
    
    def test_import_response_models(self):
        """Test importing response models."""
        from api import (
            DualOrderV3Response,
            SingleOrderResponse,
            DualOrderV6Response,
            ModifyOrderResponse,
            ClosePositionResponse,
            ClosePartialResponse
        )
        self.assertIsNotNone(DualOrderV3Response)
        self.assertIsNotNone(SingleOrderResponse)
        self.assertIsNotNone(DualOrderV6Response)
    
    def test_import_permission_classes(self):
        """Test importing permission classes."""
        from api import (
            Permission,
            PluginType,
            PluginPermissions,
            PermissionChecker,
            PluginIsolation
        )
        self.assertIsNotNone(Permission)
        self.assertIsNotNone(PluginType)
        self.assertIsNotNone(PluginPermissions)
        self.assertIsNotNone(PermissionChecker)
        self.assertIsNotNone(PluginIsolation)


class TestServiceAPIContracts(unittest.TestCase):
    """Test Service API contract definitions."""
    
    def test_order_execution_service_is_abstract(self):
        """Test IOrderExecutionService is abstract."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(issubclass(IOrderExecutionService, ABC))
    
    def test_order_execution_has_place_dual_orders_v3(self):
        """Test IOrderExecutionService has place_dual_orders_v3."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'place_dual_orders_v3'))
    
    def test_order_execution_has_place_single_order_a(self):
        """Test IOrderExecutionService has place_single_order_a."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'place_single_order_a'))
    
    def test_order_execution_has_place_single_order_b(self):
        """Test IOrderExecutionService has place_single_order_b."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'place_single_order_b'))
    
    def test_order_execution_has_place_dual_orders_v6(self):
        """Test IOrderExecutionService has place_dual_orders_v6."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'place_dual_orders_v6'))
    
    def test_order_execution_has_modify_order(self):
        """Test IOrderExecutionService has modify_order."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'modify_order'))
    
    def test_order_execution_has_close_position(self):
        """Test IOrderExecutionService has close_position."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'close_position'))
    
    def test_order_execution_has_close_position_partial(self):
        """Test IOrderExecutionService has close_position_partial."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'close_position_partial'))
    
    def test_order_execution_has_get_open_orders(self):
        """Test IOrderExecutionService has get_open_orders."""
        from api.contracts import IOrderExecutionService
        self.assertTrue(hasattr(IOrderExecutionService, 'get_open_orders'))
    
    def test_risk_management_service_is_abstract(self):
        """Test IRiskManagementService is abstract."""
        from api.contracts import IRiskManagementService
        self.assertTrue(issubclass(IRiskManagementService, ABC))
    
    def test_risk_management_has_calculate_lot_size(self):
        """Test IRiskManagementService has calculate_lot_size."""
        from api.contracts import IRiskManagementService
        self.assertTrue(hasattr(IRiskManagementService, 'calculate_lot_size'))
    
    def test_risk_management_has_check_daily_limit(self):
        """Test IRiskManagementService has check_daily_limit."""
        from api.contracts import IRiskManagementService
        self.assertTrue(hasattr(IRiskManagementService, 'check_daily_limit'))
    
    def test_trend_management_service_is_abstract(self):
        """Test ITrendManagementService is abstract."""
        from api.contracts import ITrendManagementService
        self.assertTrue(issubclass(ITrendManagementService, ABC))
    
    def test_trend_management_has_get_timeframe_trend(self):
        """Test ITrendManagementService has get_timeframe_trend."""
        from api.contracts import ITrendManagementService
        self.assertTrue(hasattr(ITrendManagementService, 'get_timeframe_trend'))
    
    def test_trend_management_has_get_mtf_trends(self):
        """Test ITrendManagementService has get_mtf_trends."""
        from api.contracts import ITrendManagementService
        self.assertTrue(hasattr(ITrendManagementService, 'get_mtf_trends'))
    
    def test_trend_management_has_validate_v3_trend_alignment(self):
        """Test ITrendManagementService has validate_v3_trend_alignment."""
        from api.contracts import ITrendManagementService
        self.assertTrue(hasattr(ITrendManagementService, 'validate_v3_trend_alignment'))
    
    def test_trend_management_has_update_trend_pulse(self):
        """Test ITrendManagementService has update_trend_pulse."""
        from api.contracts import ITrendManagementService
        self.assertTrue(hasattr(ITrendManagementService, 'update_trend_pulse'))
    
    def test_trend_management_has_get_market_state(self):
        """Test ITrendManagementService has get_market_state."""
        from api.contracts import ITrendManagementService
        self.assertTrue(hasattr(ITrendManagementService, 'get_market_state'))
    
    def test_trend_management_has_check_pulse_alignment(self):
        """Test ITrendManagementService has check_pulse_alignment."""
        from api.contracts import ITrendManagementService
        self.assertTrue(hasattr(ITrendManagementService, 'check_pulse_alignment'))
    
    def test_profit_booking_service_is_abstract(self):
        """Test IProfitBookingService is abstract."""
        from api.contracts import IProfitBookingService
        self.assertTrue(issubclass(IProfitBookingService, ABC))
    
    def test_profit_booking_has_book_profit(self):
        """Test IProfitBookingService has book_profit."""
        from api.contracts import IProfitBookingService
        self.assertTrue(hasattr(IProfitBookingService, 'book_profit'))
    
    def test_profit_booking_has_move_to_breakeven(self):
        """Test IProfitBookingService has move_to_breakeven."""
        from api.contracts import IProfitBookingService
        self.assertTrue(hasattr(IProfitBookingService, 'move_to_breakeven'))
    
    def test_market_data_service_is_abstract(self):
        """Test IMarketDataService is abstract."""
        from api.contracts import IMarketDataService
        self.assertTrue(issubclass(IMarketDataService, ABC))
    
    def test_market_data_has_get_current_spread(self):
        """Test IMarketDataService has get_current_spread."""
        from api.contracts import IMarketDataService
        self.assertTrue(hasattr(IMarketDataService, 'get_current_spread'))
    
    def test_market_data_has_get_current_price(self):
        """Test IMarketDataService has get_current_price."""
        from api.contracts import IMarketDataService
        self.assertTrue(hasattr(IMarketDataService, 'get_current_price'))
    
    def test_service_api_is_abstract(self):
        """Test IServiceAPI is abstract."""
        from api.contracts import IServiceAPI
        self.assertTrue(issubclass(IServiceAPI, ABC))
    
    def test_service_api_has_orders_property(self):
        """Test IServiceAPI has orders property."""
        from api.contracts import IServiceAPI
        self.assertTrue(hasattr(IServiceAPI, 'orders'))
    
    def test_service_api_has_risk_property(self):
        """Test IServiceAPI has risk property."""
        from api.contracts import IServiceAPI
        self.assertTrue(hasattr(IServiceAPI, 'risk'))
    
    def test_service_api_has_trend_property(self):
        """Test IServiceAPI has trend property."""
        from api.contracts import IServiceAPI
        self.assertTrue(hasattr(IServiceAPI, 'trend'))
    
    def test_service_api_has_profit_property(self):
        """Test IServiceAPI has profit property."""
        from api.contracts import IServiceAPI
        self.assertTrue(hasattr(IServiceAPI, 'profit'))
    
    def test_service_api_has_market_property(self):
        """Test IServiceAPI has market property."""
        from api.contracts import IServiceAPI
        self.assertTrue(hasattr(IServiceAPI, 'market'))


class TestOrderExecutionModels(unittest.TestCase):
    """Test order execution request/response models."""
    
    def test_dual_order_v3_request_creation(self):
        """Test DualOrderV3Request creation."""
        from api.models import DualOrderV3Request
        
        request = DualOrderV3Request(
            plugin_id='combined_v3',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            order_a_sl=2028.00,
            order_a_tp=2035.00,
            order_b_sl=2029.50,
            order_b_tp=2032.00,
            logic_route='LOGIC2'
        )
        
        self.assertEqual(request.plugin_id, 'combined_v3')
        self.assertEqual(request.symbol, 'XAUUSD')
        self.assertEqual(request.direction, 'BUY')
        self.assertEqual(request.lot_size_total, 0.10)
    
    def test_dual_order_v3_request_validation_valid(self):
        """Test DualOrderV3Request validation with valid data."""
        from api.models import DualOrderV3Request
        
        request = DualOrderV3Request(
            plugin_id='combined_v3',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            order_a_sl=2028.00,
            order_a_tp=2035.00,
            order_b_sl=2029.50,
            order_b_tp=2032.00,
            logic_route='LOGIC1'
        )
        
        self.assertTrue(request.validate())
    
    def test_dual_order_v3_request_validation_invalid_plugin(self):
        """Test DualOrderV3Request validation with invalid plugin."""
        from api.models import DualOrderV3Request
        
        request = DualOrderV3Request(
            plugin_id='wrong_plugin',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            order_a_sl=2028.00,
            order_a_tp=2035.00,
            order_b_sl=2029.50,
            order_b_tp=2032.00,
            logic_route='LOGIC1'
        )
        
        self.assertFalse(request.validate())
    
    def test_dual_order_v3_response_success(self):
        """Test DualOrderV3Response success creation."""
        from api.models import DualOrderV3Response
        
        response = DualOrderV3Response.success_response(12345, 12346)
        
        self.assertTrue(response.success)
        self.assertEqual(response.order_a_ticket, 12345)
        self.assertEqual(response.order_b_ticket, 12346)
    
    def test_dual_order_v3_response_error(self):
        """Test DualOrderV3Response error creation."""
        from api.models import DualOrderV3Response
        
        response = DualOrderV3Response.error_response("Order failed")
        
        self.assertFalse(response.success)
        self.assertEqual(response.error_message, "Order failed")
    
    def test_single_order_request_creation(self):
        """Test SingleOrderRequest creation."""
        from api.models import SingleOrderRequest
        
        request = SingleOrderRequest(
            plugin_id='price_action_1m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size=0.05,
            sl_price=2029.00,
            tp_price=2031.00
        )
        
        self.assertEqual(request.plugin_id, 'price_action_1m')
        self.assertEqual(request.lot_size, 0.05)
    
    def test_single_order_request_validation(self):
        """Test SingleOrderRequest validation."""
        from api.models import SingleOrderRequest
        
        request = SingleOrderRequest(
            plugin_id='price_action_1m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size=0.05,
            sl_price=2029.00,
            tp_price=2031.00
        )
        
        self.assertTrue(request.validate())
    
    def test_single_order_response_success(self):
        """Test SingleOrderResponse success creation."""
        from api.models import SingleOrderResponse
        
        response = SingleOrderResponse.success_response(12345)
        
        self.assertTrue(response.success)
        self.assertEqual(response.ticket, 12345)
    
    def test_dual_order_v6_request_creation(self):
        """Test DualOrderV6Request creation."""
        from api.models import DualOrderV6Request
        
        request = DualOrderV6Request(
            plugin_id='price_action_5m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            sl_price=2028.00,
            tp1_price=2032.00,
            tp2_price=2035.00
        )
        
        self.assertEqual(request.plugin_id, 'price_action_5m')
        self.assertTrue(request.validate())
    
    def test_close_position_response_success(self):
        """Test ClosePositionResponse success creation."""
        from api.models import ClosePositionResponse
        
        response = ClosePositionResponse.success_response(0.10, 15.5, 155.00)
        
        self.assertTrue(response.success)
        self.assertEqual(response.closed_volume, 0.10)
        self.assertEqual(response.profit_pips, 15.5)
        self.assertEqual(response.profit_dollars, 155.00)


class TestRiskManagementModels(unittest.TestCase):
    """Test risk management request/response models."""
    
    def test_lot_size_request_creation(self):
        """Test LotSizeRequest creation."""
        from api.models import LotSizeRequest
        
        request = LotSizeRequest(
            plugin_id='combined_v3',
            symbol='XAUUSD',
            risk_percentage=1.5,
            stop_loss_pips=10.0
        )
        
        self.assertEqual(request.plugin_id, 'combined_v3')
        self.assertEqual(request.risk_percentage, 1.5)
    
    def test_lot_size_request_validation_valid(self):
        """Test LotSizeRequest validation with valid data."""
        from api.models import LotSizeRequest
        
        request = LotSizeRequest(
            plugin_id='combined_v3',
            symbol='XAUUSD',
            risk_percentage=1.5,
            stop_loss_pips=10.0
        )
        
        self.assertTrue(request.validate())
    
    def test_lot_size_request_validation_invalid_risk(self):
        """Test LotSizeRequest validation with invalid risk."""
        from api.models import LotSizeRequest
        
        request = LotSizeRequest(
            plugin_id='combined_v3',
            symbol='XAUUSD',
            risk_percentage=15.0,  # Too high
            stop_loss_pips=10.0
        )
        
        self.assertFalse(request.validate())
    
    def test_daily_limit_response_creation(self):
        """Test DailyLimitResponse creation."""
        from api.models import DailyLimitResponse
        
        response = DailyLimitResponse(
            daily_loss=250.00,
            daily_limit=500.00,
            remaining=250.00,
            can_trade=True
        )
        
        self.assertEqual(response.daily_loss, 250.00)
        self.assertTrue(response.can_trade)
    
    def test_risk_tier_response_creation(self):
        """Test RiskTierResponse creation."""
        from api.models import RiskTierResponse
        
        response = RiskTierResponse(
            tier=2,
            tier_name='MODERATE',
            risk_percentage=1.5,
            max_trades=5,
            max_lot_size=0.50
        )
        
        self.assertEqual(response.tier, 2)
        self.assertEqual(response.tier_name, 'MODERATE')


class TestTrendManagementModels(unittest.TestCase):
    """Test trend management request/response models."""
    
    def test_timeframe_trend_response_creation(self):
        """Test TimeframeTrendResponse creation."""
        from api.models import TimeframeTrendResponse
        
        response = TimeframeTrendResponse(
            timeframe='15m',
            direction='bullish',
            value=1,
            last_updated='2026-01-12 10:30'
        )
        
        self.assertEqual(response.timeframe, '15m')
        self.assertEqual(response.direction, 'bullish')
        self.assertEqual(response.value, 1)
    
    def test_mtf_trends_response_creation(self):
        """Test MTFTrendsResponse creation."""
        from api.models import MTFTrendsResponse
        
        response = MTFTrendsResponse(
            m15=1,
            h1=1,
            h4=-1,
            d1=1
        )
        
        self.assertEqual(response.m15, 1)
        self.assertEqual(response.h4, -1)
    
    def test_mtf_trends_response_aligned_count_buy(self):
        """Test MTFTrendsResponse aligned count for BUY."""
        from api.models import MTFTrendsResponse
        
        response = MTFTrendsResponse(
            m15=1,
            h1=1,
            h4=-1,
            d1=1
        )
        
        self.assertEqual(response.get_aligned_count('BUY'), 3)
    
    def test_mtf_trends_response_aligned_count_sell(self):
        """Test MTFTrendsResponse aligned count for SELL."""
        from api.models import MTFTrendsResponse
        
        response = MTFTrendsResponse(
            m15=-1,
            h1=-1,
            h4=-1,
            d1=1
        )
        
        self.assertEqual(response.get_aligned_count('SELL'), 3)
    
    def test_trend_pulse_data_creation(self):
        """Test TrendPulseData creation."""
        from api.models import TrendPulseData
        
        data = TrendPulseData(
            timeframe='15',
            bull_count=5,
            bear_count=1,
            market_state='TRENDING_BULLISH',
            last_updated='2026-01-12 10:30'
        )
        
        self.assertEqual(data.bull_count, 5)
        self.assertEqual(data.bear_count, 1)
    
    def test_pulse_data_response_bullish_aligned(self):
        """Test PulseDataResponse bullish alignment."""
        from api.models import PulseDataResponse
        
        response = PulseDataResponse(
            symbol='XAUUSD',
            timeframes={
                '5': {'bull_count': 4, 'bear_count': 2},
                '15': {'bull_count': 5, 'bear_count': 1}
            }
        )
        
        self.assertTrue(response.is_bullish_aligned())
        self.assertFalse(response.is_bearish_aligned())


class TestProfitBookingModels(unittest.TestCase):
    """Test profit booking request/response models."""
    
    def test_book_profit_request_creation(self):
        """Test BookProfitRequest creation."""
        from api.models import BookProfitRequest
        
        request = BookProfitRequest(
            plugin_id='price_action_5m',
            order_id=12345,
            percentage=50.0,
            reason='TP1'
        )
        
        self.assertEqual(request.plugin_id, 'price_action_5m')
        self.assertEqual(request.percentage, 50.0)
    
    def test_book_profit_request_validation_valid(self):
        """Test BookProfitRequest validation with valid data."""
        from api.models import BookProfitRequest
        
        request = BookProfitRequest(
            plugin_id='price_action_5m',
            order_id=12345,
            percentage=50.0,
            reason='TP1'
        )
        
        self.assertTrue(request.validate())
    
    def test_book_profit_request_validation_invalid_percentage(self):
        """Test BookProfitRequest validation with invalid percentage."""
        from api.models import BookProfitRequest
        
        request = BookProfitRequest(
            plugin_id='price_action_5m',
            order_id=12345,
            percentage=150.0,  # Too high
            reason='TP1'
        )
        
        self.assertFalse(request.validate())
    
    def test_breakeven_request_creation(self):
        """Test BreakevenRequest creation."""
        from api.models import BreakevenRequest
        
        request = BreakevenRequest(
            plugin_id='price_action_5m',
            order_id=12345,
            buffer_pips=2.0
        )
        
        self.assertEqual(request.buffer_pips, 2.0)
        self.assertTrue(request.validate())


class TestMarketDataModels(unittest.TestCase):
    """Test market data request/response models."""
    
    def test_spread_response_creation(self):
        """Test SpreadResponse creation."""
        from api.models import SpreadResponse
        
        response = SpreadResponse(
            symbol='XAUUSD',
            spread_pips=1.5,
            timestamp='2026-01-12 10:30:00'
        )
        
        self.assertEqual(response.symbol, 'XAUUSD')
        self.assertEqual(response.spread_pips, 1.5)
    
    def test_price_response_creation(self):
        """Test PriceResponse creation."""
        from api.models import PriceResponse
        
        response = PriceResponse(
            symbol='XAUUSD',
            bid=2030.45,
            ask=2030.55,
            spread_pips=1.0,
            timestamp='2026-01-12 10:30:00'
        )
        
        self.assertEqual(response.bid, 2030.45)
        self.assertEqual(response.ask, 2030.55)
    
    def test_symbol_info_response_creation(self):
        """Test SymbolInfoResponse creation."""
        from api.models import SymbolInfoResponse
        
        response = SymbolInfoResponse(
            symbol='XAUUSD',
            pip_value=10.0,
            lot_step=0.01,
            min_lot=0.01,
            max_lot=100.0,
            contract_size=100,
            digits=2
        )
        
        self.assertEqual(response.pip_value, 10.0)
        self.assertEqual(response.min_lot, 0.01)


class TestErrorResponse(unittest.TestCase):
    """Test error response model."""
    
    def test_validation_error_creation(self):
        """Test validation error creation."""
        from api.models import ErrorResponse
        
        error = ErrorResponse.validation_error(
            "Invalid parameter",
            {"field": "lot_size", "reason": "must be positive"}
        )
        
        self.assertFalse(error.success)
        self.assertEqual(error.error_code, "VALIDATION_ERROR")
    
    def test_permission_error_creation(self):
        """Test permission error creation."""
        from api.models import ErrorResponse
        
        error = ErrorResponse.permission_error("Access denied")
        
        self.assertFalse(error.success)
        self.assertEqual(error.error_code, "PERMISSION_DENIED")
    
    def test_not_found_error_creation(self):
        """Test not found error creation."""
        from api.models import ErrorResponse
        
        error = ErrorResponse.not_found_error("Order not found")
        
        self.assertFalse(error.success)
        self.assertEqual(error.error_code, "NOT_FOUND")
    
    def test_execution_error_creation(self):
        """Test execution error creation."""
        from api.models import ErrorResponse
        
        error = ErrorResponse.execution_error("Order execution failed")
        
        self.assertFalse(error.success)
        self.assertEqual(error.error_code, "EXECUTION_ERROR")


class TestPluginPermissions(unittest.TestCase):
    """Test plugin permission definitions."""
    
    def test_permission_enum_values(self):
        """Test Permission enum has all required values."""
        from api.permissions import Permission
        
        self.assertEqual(Permission.PLACE_DUAL_ORDERS_V3.value, "place_dual_orders_v3")
        self.assertEqual(Permission.PLACE_SINGLE_ORDER_A.value, "place_single_order_a")
        self.assertEqual(Permission.PLACE_SINGLE_ORDER_B.value, "place_single_order_b")
        self.assertEqual(Permission.PLACE_DUAL_ORDERS_V6.value, "place_dual_orders_v6")
    
    def test_plugin_type_enum_values(self):
        """Test PluginType enum has all required values."""
        from api.permissions import PluginType
        
        self.assertEqual(PluginType.V3_COMBINED.value, "V3_COMBINED")
        self.assertEqual(PluginType.V6_PRICE_ACTION_1M.value, "V6_PRICE_ACTION_1M")
        self.assertEqual(PluginType.V6_PRICE_ACTION_5M.value, "V6_PRICE_ACTION_5M")
        self.assertEqual(PluginType.V6_PRICE_ACTION_15M.value, "V6_PRICE_ACTION_15M")
        self.assertEqual(PluginType.V6_PRICE_ACTION_1H.value, "V6_PRICE_ACTION_1H")
    
    def test_plugin_permissions_v3_combined(self):
        """Test V3 Combined plugin permissions."""
        from api.permissions import PluginPermissions
        
        perms = PluginPermissions()
        self.assertIn("place_dual_orders_v3", perms.V3_COMBINED)
        self.assertIn("validate_v3_trend_alignment", perms.V3_COMBINED)
    
    def test_plugin_permissions_v6_1m(self):
        """Test V6 1M plugin permissions (ORDER B ONLY)."""
        from api.permissions import PluginPermissions
        
        perms = PluginPermissions()
        self.assertIn("place_single_order_b", perms.V6_1M)
        self.assertNotIn("place_single_order_a", perms.V6_1M)
        self.assertNotIn("place_dual_orders_v3", perms.V6_1M)
    
    def test_plugin_permissions_v6_5m(self):
        """Test V6 5M plugin permissions (DUAL ORDERS)."""
        from api.permissions import PluginPermissions
        
        perms = PluginPermissions()
        self.assertIn("place_dual_orders_v6", perms.V6_5M)
        self.assertIn("move_to_breakeven", perms.V6_5M)
    
    def test_plugin_permissions_v6_15m(self):
        """Test V6 15M plugin permissions (ORDER A ONLY)."""
        from api.permissions import PluginPermissions
        
        perms = PluginPermissions()
        self.assertIn("place_single_order_a", perms.V6_15M)
        self.assertNotIn("place_single_order_b", perms.V6_15M)
    
    def test_plugin_permissions_v6_1h(self):
        """Test V6 1H plugin permissions (ORDER A ONLY)."""
        from api.permissions import PluginPermissions
        
        perms = PluginPermissions()
        self.assertIn("place_single_order_a", perms.V6_1H)
        self.assertNotIn("place_dual_orders_v6", perms.V6_1H)
    
    def test_plugin_permissions_mapping(self):
        """Test PLUGIN_PERMISSIONS mapping."""
        from api.permissions import PLUGIN_PERMISSIONS
        
        self.assertIn("combined_v3", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_1m", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_5m", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_15m", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_1h", PLUGIN_PERMISSIONS)


class TestPermissionChecker(unittest.TestCase):
    """Test PermissionChecker functionality."""
    
    def test_has_permission_v3_dual_orders(self):
        """Test V3 has permission for dual orders."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        self.assertTrue(checker.has_permission("combined_v3", "place_dual_orders_v3"))
    
    def test_has_permission_v6_1m_order_b(self):
        """Test V6 1M has permission for Order B."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        self.assertTrue(checker.has_permission("price_action_1m", "place_single_order_b"))
    
    def test_no_permission_v6_1m_order_a(self):
        """Test V6 1M does NOT have permission for Order A."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        self.assertFalse(checker.has_permission("price_action_1m", "place_single_order_a"))
    
    def test_no_permission_unknown_plugin(self):
        """Test unknown plugin has no permissions."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        self.assertFalse(checker.has_permission("unknown_plugin", "place_dual_orders_v3"))
    
    def test_get_permissions(self):
        """Test getting all permissions for a plugin."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        perms = checker.get_permissions("combined_v3")
        
        self.assertIsInstance(perms, list)
        self.assertGreater(len(perms), 0)
    
    def test_get_plugin_type(self):
        """Test getting plugin type."""
        from api.permissions import PermissionChecker, PluginType
        
        checker = PermissionChecker()
        
        self.assertEqual(checker.get_plugin_type("combined_v3"), PluginType.V3_COMBINED)
        self.assertEqual(checker.get_plugin_type("price_action_1m"), PluginType.V6_PRICE_ACTION_1M)
    
    def test_is_v3_plugin(self):
        """Test is_v3_plugin check."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        
        self.assertTrue(checker.is_v3_plugin("combined_v3"))
        self.assertFalse(checker.is_v3_plugin("price_action_1m"))
    
    def test_is_v6_plugin(self):
        """Test is_v6_plugin check."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        
        self.assertFalse(checker.is_v6_plugin("combined_v3"))
        self.assertTrue(checker.is_v6_plugin("price_action_1m"))
        self.assertTrue(checker.is_v6_plugin("price_action_5m"))
    
    def test_can_place_dual_orders_v3(self):
        """Test can_place_dual_orders_v3 check."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        
        self.assertTrue(checker.can_place_dual_orders_v3("combined_v3"))
        self.assertFalse(checker.can_place_dual_orders_v3("price_action_1m"))
    
    def test_can_place_single_order_a(self):
        """Test can_place_single_order_a check."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        
        self.assertTrue(checker.can_place_single_order_a("price_action_15m"))
        self.assertTrue(checker.can_place_single_order_a("price_action_1h"))
        self.assertFalse(checker.can_place_single_order_a("price_action_1m"))
    
    def test_can_place_single_order_b(self):
        """Test can_place_single_order_b check."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        
        self.assertTrue(checker.can_place_single_order_b("price_action_1m"))
        self.assertFalse(checker.can_place_single_order_b("price_action_15m"))
    
    def test_validate_plugin_access_allowed(self):
        """Test validate_plugin_access for allowed access."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        result = checker.validate_plugin_access("combined_v3", "place_dual_orders_v3")
        
        self.assertTrue(result["allowed"])
        self.assertIsNone(result["error_message"])
    
    def test_validate_plugin_access_denied(self):
        """Test validate_plugin_access for denied access."""
        from api.permissions import PermissionChecker
        
        checker = PermissionChecker()
        result = checker.validate_plugin_access("price_action_1m", "place_dual_orders_v3")
        
        self.assertFalse(result["allowed"])
        self.assertIsNotNone(result["error_message"])


class TestPluginIsolation(unittest.TestCase):
    """Test PluginIsolation functionality."""
    
    def test_validate_order_access_same_plugin(self):
        """Test order access for same plugin."""
        from api.permissions import PluginIsolation
        
        isolation = PluginIsolation()
        self.assertTrue(isolation.validate_order_access("combined_v3", "combined_v3"))
    
    def test_validate_order_access_different_plugin(self):
        """Test order access for different plugin."""
        from api.permissions import PluginIsolation
        
        isolation = PluginIsolation()
        self.assertFalse(isolation.validate_order_access("combined_v3", "price_action_1m"))
    
    def test_filter_orders_for_plugin(self):
        """Test filtering orders for a plugin."""
        from api.permissions import PluginIsolation
        
        isolation = PluginIsolation()
        
        orders = [
            {"plugin_id": "combined_v3", "ticket": 1},
            {"plugin_id": "price_action_1m", "ticket": 2},
            {"plugin_id": "combined_v3", "ticket": 3},
        ]
        
        filtered = isolation.filter_orders_for_plugin("combined_v3", orders)
        
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["ticket"], 1)
        self.assertEqual(filtered[1]["ticket"], 3)
    
    def test_get_isolation_context_v3(self):
        """Test getting isolation context for V3 plugin."""
        from api.permissions import PluginIsolation
        
        isolation = PluginIsolation()
        context = isolation.get_isolation_context("combined_v3")
        
        self.assertEqual(context["plugin_id"], "combined_v3")
        self.assertEqual(context["database"], "zepix_combined.db")
        self.assertTrue(context["is_v3"])
        self.assertFalse(context["is_v6"])
    
    def test_get_isolation_context_v6(self):
        """Test getting isolation context for V6 plugin."""
        from api.permissions import PluginIsolation
        
        isolation = PluginIsolation()
        context = isolation.get_isolation_context("price_action_1m")
        
        self.assertEqual(context["plugin_id"], "price_action_1m")
        self.assertEqual(context["database"], "zepix_price_action.db")
        self.assertFalse(context["is_v3"])
        self.assertTrue(context["is_v6"])


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def test_check_permission_function(self):
        """Test check_permission convenience function."""
        from api.permissions import check_permission
        
        self.assertTrue(check_permission("combined_v3", "place_dual_orders_v3"))
        self.assertFalse(check_permission("price_action_1m", "place_dual_orders_v3"))
    
    def test_get_plugin_permissions_function(self):
        """Test get_plugin_permissions convenience function."""
        from api.permissions import get_plugin_permissions
        
        perms = get_plugin_permissions("combined_v3")
        self.assertIsInstance(perms, list)
        self.assertIn("place_dual_orders_v3", perms)
    
    def test_validate_access_function(self):
        """Test validate_access convenience function."""
        from api.permissions import validate_access
        
        result = validate_access("combined_v3", "place_dual_orders_v3")
        self.assertTrue(result["allowed"])


class TestDocument10Integration(unittest.TestCase):
    """Test all Document 10 components working together."""
    
    def test_v3_plugin_workflow(self):
        """Test V3 plugin workflow with permissions and models."""
        from api.permissions import check_permission, validate_access
        from api.models import DualOrderV3Request, DualOrderV3Response
        
        # Check permission
        self.assertTrue(check_permission("combined_v3", "place_dual_orders_v3"))
        
        # Create request
        request = DualOrderV3Request(
            plugin_id='combined_v3',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            order_a_sl=2028.00,
            order_a_tp=2035.00,
            order_b_sl=2029.50,
            order_b_tp=2032.00,
            logic_route='LOGIC2'
        )
        
        # Validate request
        self.assertTrue(request.validate())
        
        # Create response
        response = DualOrderV3Response.success_response(12345, 12346)
        self.assertTrue(response.success)
    
    def test_v6_1m_plugin_workflow(self):
        """Test V6 1M plugin workflow (ORDER B ONLY)."""
        from api.permissions import check_permission
        from api.models import SingleOrderRequest, SingleOrderResponse
        
        # Check permission - should have ORDER B
        self.assertTrue(check_permission("price_action_1m", "place_single_order_b"))
        
        # Check permission - should NOT have ORDER A
        self.assertFalse(check_permission("price_action_1m", "place_single_order_a"))
        
        # Create request
        request = SingleOrderRequest(
            plugin_id='price_action_1m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size=0.05,
            sl_price=2029.00,
            tp_price=2031.00,
            comment='ORDER_B'
        )
        
        self.assertTrue(request.validate())
    
    def test_v6_5m_plugin_workflow(self):
        """Test V6 5M plugin workflow (DUAL ORDERS)."""
        from api.permissions import check_permission
        from api.models import DualOrderV6Request, DualOrderV6Response
        
        # Check permission
        self.assertTrue(check_permission("price_action_5m", "place_dual_orders_v6"))
        self.assertTrue(check_permission("price_action_5m", "move_to_breakeven"))
        
        # Create request
        request = DualOrderV6Request(
            plugin_id='price_action_5m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            sl_price=2028.00,
            tp1_price=2032.00,
            tp2_price=2035.00
        )
        
        self.assertTrue(request.validate())
    
    def test_plugin_isolation_enforcement(self):
        """Test plugin isolation is enforced."""
        from api.permissions import PluginIsolation
        
        isolation = PluginIsolation()
        
        # V3 can only access V3 orders
        self.assertTrue(isolation.validate_order_access("combined_v3", "combined_v3"))
        self.assertFalse(isolation.validate_order_access("combined_v3", "price_action_1m"))
        
        # V6 can only access V6 orders
        self.assertTrue(isolation.validate_order_access("price_action_1m", "price_action_1m"))
        self.assertFalse(isolation.validate_order_access("price_action_1m", "combined_v3"))


class TestDocument10Summary(unittest.TestCase):
    """Summary tests for Document 10 implementation."""
    
    def test_all_service_contracts_defined(self):
        """Test all service contracts are defined."""
        from api.contracts import (
            IOrderExecutionService,
            IRiskManagementService,
            ITrendManagementService,
            IProfitBookingService,
            IMarketDataService,
            IServiceAPI
        )
        
        self.assertTrue(issubclass(IOrderExecutionService, ABC))
        self.assertTrue(issubclass(IRiskManagementService, ABC))
        self.assertTrue(issubclass(ITrendManagementService, ABC))
        self.assertTrue(issubclass(IProfitBookingService, ABC))
        self.assertTrue(issubclass(IMarketDataService, ABC))
        self.assertTrue(issubclass(IServiceAPI, ABC))
    
    def test_all_5_plugins_have_permissions(self):
        """Test all 5 plugins have permissions defined."""
        from api.permissions import PLUGIN_PERMISSIONS
        
        self.assertEqual(len(PLUGIN_PERMISSIONS), 5)
        self.assertIn("combined_v3", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_1m", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_5m", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_15m", PLUGIN_PERMISSIONS)
        self.assertIn("price_action_1h", PLUGIN_PERMISSIONS)
    
    def test_v3_has_dual_order_v3_permission(self):
        """Test V3 has dual order V3 permission."""
        from api.permissions import check_permission
        
        self.assertTrue(check_permission("combined_v3", "place_dual_orders_v3"))
    
    def test_v6_1m_has_order_b_only(self):
        """Test V6 1M has ORDER B ONLY."""
        from api.permissions import check_permission
        
        self.assertTrue(check_permission("price_action_1m", "place_single_order_b"))
        self.assertFalse(check_permission("price_action_1m", "place_single_order_a"))
        self.assertFalse(check_permission("price_action_1m", "place_dual_orders_v6"))
    
    def test_v6_5m_has_dual_orders(self):
        """Test V6 5M has DUAL ORDERS."""
        from api.permissions import check_permission
        
        self.assertTrue(check_permission("price_action_5m", "place_dual_orders_v6"))
    
    def test_v6_15m_has_order_a_only(self):
        """Test V6 15M has ORDER A ONLY."""
        from api.permissions import check_permission
        
        self.assertTrue(check_permission("price_action_15m", "place_single_order_a"))
        self.assertFalse(check_permission("price_action_15m", "place_single_order_b"))
    
    def test_v6_1h_has_order_a_only(self):
        """Test V6 1H has ORDER A ONLY."""
        from api.permissions import check_permission
        
        self.assertTrue(check_permission("price_action_1h", "place_single_order_a"))
        self.assertFalse(check_permission("price_action_1h", "place_single_order_b"))
    
    def test_all_modules_importable(self):
        """Test all API modules are importable."""
        from api import (
            IOrderExecutionService,
            IRiskManagementService,
            ITrendManagementService,
            IProfitBookingService,
            IMarketDataService,
            IServiceAPI,
            DualOrderV3Request,
            DualOrderV3Response,
            Permission,
            PluginType,
            PermissionChecker,
            PluginIsolation
        )
        
        self.assertIsNotNone(IOrderExecutionService)
        self.assertIsNotNone(DualOrderV3Request)
        self.assertIsNotNone(Permission)
        self.assertIsNotNone(PermissionChecker)


if __name__ == '__main__':
    unittest.main(verbosity=2)
