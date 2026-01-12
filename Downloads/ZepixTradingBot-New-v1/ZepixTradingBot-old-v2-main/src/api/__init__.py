"""
API Package - FastAPI REST Endpoints and Service API Contracts

Document 08: Phase 6 - UI Dashboard (Optional)
Document 10: API Specifications

Provides:
- REST API endpoints for plugin management, metrics, and configuration
- Service API contracts for V3/V6 order routing
- Request/Response models for all API operations
- Plugin permissions and isolation

Modules:
- admin_routes: Plugin management endpoints (/admin/plugins, /admin/config)
- metrics_routes: System metrics endpoints (/metrics, /dashboard)
- health_routes: Health check endpoints (/health, /status)
- contracts: Service API interface definitions
- models: Request/Response data classes
- permissions: Plugin permission definitions
"""

from .admin_routes import router as admin_router
from .metrics_routes import router as metrics_router
from .health_routes import router as health_router

from .contracts import (
    IOrderExecutionService,
    IRiskManagementService,
    ITrendManagementService,
    IProfitBookingService,
    IMarketDataService,
    IServiceAPI,
    OrderType,
    LogicRoute,
    MarketState
)

from .models import (
    Direction,
    OrderStatus,
    Timeframe,
    DualOrderV3Request,
    DualOrderV3Response,
    SingleOrderRequest,
    SingleOrderResponse,
    DualOrderV6Request,
    DualOrderV6Response,
    ModifyOrderRequest,
    ModifyOrderResponse,
    ClosePositionRequest,
    ClosePositionResponse,
    ClosePartialRequest,
    ClosePartialResponse,
    OrderInfo,
    LotSizeRequest,
    LotSizeResponse,
    DailyLimitResponse,
    RiskTierResponse,
    TimeframeTrendResponse,
    MTFTrendsResponse,
    TrendPulseData,
    PulseDataResponse,
    BookProfitRequest,
    BookProfitResponse,
    BreakevenRequest,
    BreakevenResponse,
    BookingRecord,
    SpreadResponse,
    PriceResponse,
    SymbolInfoResponse,
    ErrorResponse
)

from .permissions import (
    Permission,
    PluginType,
    PluginPermissions,
    PermissionChecker,
    PluginIsolation,
    PLUGIN_PERMISSIONS,
    PLUGIN_TYPES,
    permission_checker,
    plugin_isolation,
    check_permission,
    get_plugin_permissions,
    validate_access
)

__all__ = [
    # REST API Routers
    'admin_router',
    'metrics_router', 
    'health_router',
    
    # Service API Contracts
    'IOrderExecutionService',
    'IRiskManagementService',
    'ITrendManagementService',
    'IProfitBookingService',
    'IMarketDataService',
    'IServiceAPI',
    'OrderType',
    'LogicRoute',
    'MarketState',
    
    # Request/Response Models
    'Direction',
    'OrderStatus',
    'Timeframe',
    'DualOrderV3Request',
    'DualOrderV3Response',
    'SingleOrderRequest',
    'SingleOrderResponse',
    'DualOrderV6Request',
    'DualOrderV6Response',
    'ModifyOrderRequest',
    'ModifyOrderResponse',
    'ClosePositionRequest',
    'ClosePositionResponse',
    'ClosePartialRequest',
    'ClosePartialResponse',
    'OrderInfo',
    'LotSizeRequest',
    'LotSizeResponse',
    'DailyLimitResponse',
    'RiskTierResponse',
    'TimeframeTrendResponse',
    'MTFTrendsResponse',
    'TrendPulseData',
    'PulseDataResponse',
    'BookProfitRequest',
    'BookProfitResponse',
    'BreakevenRequest',
    'BreakevenResponse',
    'BookingRecord',
    'SpreadResponse',
    'PriceResponse',
    'SymbolInfoResponse',
    'ErrorResponse',
    
    # Permissions
    'Permission',
    'PluginType',
    'PluginPermissions',
    'PermissionChecker',
    'PluginIsolation',
    'PLUGIN_PERMISSIONS',
    'PLUGIN_TYPES',
    'permission_checker',
    'plugin_isolation',
    'check_permission',
    'get_plugin_permissions',
    'validate_access'
]
