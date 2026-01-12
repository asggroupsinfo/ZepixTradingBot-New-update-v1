"""
Plugin Permissions - Access Control for Service APIs

Document 10: API Specifications
Defines plugin-specific permissions for API access.

Security Model:
- Each plugin can ONLY access its own orders
- Cross-plugin queries return empty results
- ServiceAPI enforces plugin_id checks on ALL methods
"""

from typing import List, Set, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


class Permission(Enum):
    """Available API permissions."""
    
    # Order Execution Permissions
    PLACE_DUAL_ORDERS_V3 = "place_dual_orders_v3"
    PLACE_SINGLE_ORDER_A = "place_single_order_a"
    PLACE_SINGLE_ORDER_B = "place_single_order_b"
    PLACE_DUAL_ORDERS_V6 = "place_dual_orders_v6"
    MODIFY_ORDERS = "modify_orders"
    CLOSE_POSITIONS = "close_positions"
    CLOSE_PARTIAL = "close_partial"
    GET_OPEN_ORDERS = "get_open_orders"
    
    # Risk Management Permissions
    CALCULATE_LOT_SIZE = "calculate_lot_size"
    CHECK_DAILY_LIMIT = "check_daily_limit"
    GET_RISK_TIER = "get_risk_tier"
    
    # Trend Management Permissions
    GET_TIMEFRAME_TREND = "get_timeframe_trend"
    GET_MTF_TRENDS = "get_mtf_trends"
    VALIDATE_V3_TREND_ALIGNMENT = "validate_v3_trend_alignment"
    UPDATE_TREND_PULSE = "update_trend_pulse"
    GET_MARKET_STATE = "get_market_state"
    CHECK_PULSE_ALIGNMENT = "check_pulse_alignment"
    GET_PULSE_DATA = "get_pulse_data"
    
    # Profit Booking Permissions
    BOOK_PROFIT = "book_profit"
    MOVE_TO_BREAKEVEN = "move_to_breakeven"
    GET_BOOKING_HISTORY = "get_booking_history"
    
    # Market Data Permissions
    GET_CURRENT_SPREAD = "get_current_spread"
    GET_CURRENT_PRICE = "get_current_price"
    GET_SYMBOL_INFO = "get_symbol_info"


class PluginType(Enum):
    """Plugin type enumeration."""
    V3_COMBINED = "V3_COMBINED"
    V6_PRICE_ACTION_1M = "V6_PRICE_ACTION_1M"
    V6_PRICE_ACTION_5M = "V6_PRICE_ACTION_5M"
    V6_PRICE_ACTION_15M = "V6_PRICE_ACTION_15M"
    V6_PRICE_ACTION_1H = "V6_PRICE_ACTION_1H"


@dataclass
class PluginPermissions:
    """
    Plugin permission definitions.
    
    Each plugin has specific permissions based on its type and requirements.
    """
    
    # V3 Combined Logic Plugin Permissions
    V3_COMBINED: List[str] = field(default_factory=lambda: [
        Permission.PLACE_DUAL_ORDERS_V3.value,
        Permission.MODIFY_ORDERS.value,
        Permission.CLOSE_POSITIONS.value,
        Permission.CLOSE_PARTIAL.value,
        Permission.GET_OPEN_ORDERS.value,
        Permission.CALCULATE_LOT_SIZE.value,
        Permission.CHECK_DAILY_LIMIT.value,
        Permission.GET_RISK_TIER.value,
        Permission.GET_TIMEFRAME_TREND.value,
        Permission.GET_MTF_TRENDS.value,
        Permission.VALIDATE_V3_TREND_ALIGNMENT.value,
        Permission.BOOK_PROFIT.value,
        Permission.MOVE_TO_BREAKEVEN.value,
        Permission.GET_BOOKING_HISTORY.value,
        Permission.GET_CURRENT_SPREAD.value,
        Permission.GET_CURRENT_PRICE.value,
        Permission.GET_SYMBOL_INFO.value,
    ])
    
    # V6 1M Plugin Permissions (ORDER B ONLY)
    V6_1M: List[str] = field(default_factory=lambda: [
        Permission.PLACE_SINGLE_ORDER_B.value,  # ORDER B ONLY
        Permission.MODIFY_ORDERS.value,
        Permission.CLOSE_POSITIONS.value,
        Permission.GET_OPEN_ORDERS.value,
        Permission.CALCULATE_LOT_SIZE.value,
        Permission.CHECK_DAILY_LIMIT.value,
        Permission.GET_MARKET_STATE.value,
        Permission.CHECK_PULSE_ALIGNMENT.value,
        Permission.GET_PULSE_DATA.value,
        Permission.GET_CURRENT_SPREAD.value,
        Permission.GET_CURRENT_PRICE.value,
        Permission.GET_SYMBOL_INFO.value,
    ])
    
    # V6 5M Plugin Permissions (DUAL ORDERS)
    V6_5M: List[str] = field(default_factory=lambda: [
        Permission.PLACE_DUAL_ORDERS_V6.value,  # DUAL ORDERS
        Permission.MODIFY_ORDERS.value,
        Permission.CLOSE_POSITIONS.value,
        Permission.CLOSE_PARTIAL.value,
        Permission.GET_OPEN_ORDERS.value,
        Permission.CALCULATE_LOT_SIZE.value,
        Permission.CHECK_DAILY_LIMIT.value,
        Permission.GET_MARKET_STATE.value,
        Permission.CHECK_PULSE_ALIGNMENT.value,
        Permission.GET_PULSE_DATA.value,
        Permission.BOOK_PROFIT.value,
        Permission.MOVE_TO_BREAKEVEN.value,
        Permission.GET_BOOKING_HISTORY.value,
        Permission.GET_CURRENT_SPREAD.value,
        Permission.GET_CURRENT_PRICE.value,
        Permission.GET_SYMBOL_INFO.value,
    ])
    
    # V6 15M Plugin Permissions (ORDER A ONLY)
    V6_15M: List[str] = field(default_factory=lambda: [
        Permission.PLACE_SINGLE_ORDER_A.value,  # ORDER A ONLY
        Permission.MODIFY_ORDERS.value,
        Permission.CLOSE_POSITIONS.value,
        Permission.GET_OPEN_ORDERS.value,
        Permission.CALCULATE_LOT_SIZE.value,
        Permission.CHECK_DAILY_LIMIT.value,
        Permission.GET_MARKET_STATE.value,
        Permission.CHECK_PULSE_ALIGNMENT.value,
        Permission.GET_PULSE_DATA.value,
        Permission.GET_CURRENT_SPREAD.value,
        Permission.GET_CURRENT_PRICE.value,
        Permission.GET_SYMBOL_INFO.value,
    ])
    
    # V6 1H Plugin Permissions (ORDER A ONLY)
    V6_1H: List[str] = field(default_factory=lambda: [
        Permission.PLACE_SINGLE_ORDER_A.value,  # ORDER A ONLY
        Permission.MODIFY_ORDERS.value,
        Permission.CLOSE_POSITIONS.value,
        Permission.GET_OPEN_ORDERS.value,
        Permission.CALCULATE_LOT_SIZE.value,
        Permission.CHECK_DAILY_LIMIT.value,
        Permission.GET_MARKET_STATE.value,
        Permission.GET_PULSE_DATA.value,
        Permission.GET_CURRENT_SPREAD.value,
        Permission.GET_CURRENT_PRICE.value,
        Permission.GET_SYMBOL_INFO.value,
    ])


# Plugin ID to Permission mapping
PLUGIN_PERMISSIONS: Dict[str, List[str]] = {
    "combined_v3": PluginPermissions().V3_COMBINED,
    "price_action_1m": PluginPermissions().V6_1M,
    "price_action_5m": PluginPermissions().V6_5M,
    "price_action_15m": PluginPermissions().V6_15M,
    "price_action_1h": PluginPermissions().V6_1H,
}


# Plugin ID to Plugin Type mapping
PLUGIN_TYPES: Dict[str, PluginType] = {
    "combined_v3": PluginType.V3_COMBINED,
    "price_action_1m": PluginType.V6_PRICE_ACTION_1M,
    "price_action_5m": PluginType.V6_PRICE_ACTION_5M,
    "price_action_15m": PluginType.V6_PRICE_ACTION_15M,
    "price_action_1h": PluginType.V6_PRICE_ACTION_1H,
}


class PermissionChecker:
    """
    Permission checker for API access control.
    
    Enforces plugin isolation and permission-based access.
    """
    
    def __init__(self):
        """Initialize permission checker."""
        self.plugin_permissions = PLUGIN_PERMISSIONS
        self.plugin_types = PLUGIN_TYPES
    
    def has_permission(self, plugin_id: str, permission: str) -> bool:
        """
        Check if plugin has specific permission.
        
        Args:
            plugin_id: Plugin identifier
            permission: Permission to check
            
        Returns:
            True if plugin has permission
        """
        if plugin_id not in self.plugin_permissions:
            return False
        
        return permission in self.plugin_permissions[plugin_id]
    
    def get_permissions(self, plugin_id: str) -> List[str]:
        """
        Get all permissions for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            List of permission strings
        """
        return self.plugin_permissions.get(plugin_id, [])
    
    def get_plugin_type(self, plugin_id: str) -> PluginType:
        """
        Get plugin type.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            PluginType enum value
        """
        return self.plugin_types.get(plugin_id)
    
    def is_v3_plugin(self, plugin_id: str) -> bool:
        """Check if plugin is V3 type."""
        return self.get_plugin_type(plugin_id) == PluginType.V3_COMBINED
    
    def is_v6_plugin(self, plugin_id: str) -> bool:
        """Check if plugin is V6 type."""
        plugin_type = self.get_plugin_type(plugin_id)
        return plugin_type in [
            PluginType.V6_PRICE_ACTION_1M,
            PluginType.V6_PRICE_ACTION_5M,
            PluginType.V6_PRICE_ACTION_15M,
            PluginType.V6_PRICE_ACTION_1H,
        ]
    
    def can_place_dual_orders_v3(self, plugin_id: str) -> bool:
        """Check if plugin can place V3 dual orders."""
        return self.has_permission(plugin_id, Permission.PLACE_DUAL_ORDERS_V3.value)
    
    def can_place_single_order_a(self, plugin_id: str) -> bool:
        """Check if plugin can place single Order A."""
        return self.has_permission(plugin_id, Permission.PLACE_SINGLE_ORDER_A.value)
    
    def can_place_single_order_b(self, plugin_id: str) -> bool:
        """Check if plugin can place single Order B."""
        return self.has_permission(plugin_id, Permission.PLACE_SINGLE_ORDER_B.value)
    
    def can_place_dual_orders_v6(self, plugin_id: str) -> bool:
        """Check if plugin can place V6 dual orders."""
        return self.has_permission(plugin_id, Permission.PLACE_DUAL_ORDERS_V6.value)
    
    def can_use_v3_trend_system(self, plugin_id: str) -> bool:
        """Check if plugin can use V3 trend system."""
        return self.has_permission(plugin_id, Permission.VALIDATE_V3_TREND_ALIGNMENT.value)
    
    def can_use_v6_pulse_system(self, plugin_id: str) -> bool:
        """Check if plugin can use V6 Trend Pulse system."""
        return self.has_permission(plugin_id, Permission.CHECK_PULSE_ALIGNMENT.value)
    
    def can_book_profit(self, plugin_id: str) -> bool:
        """Check if plugin can book profit."""
        return self.has_permission(plugin_id, Permission.BOOK_PROFIT.value)
    
    def can_move_to_breakeven(self, plugin_id: str) -> bool:
        """Check if plugin can move to breakeven."""
        return self.has_permission(plugin_id, Permission.MOVE_TO_BREAKEVEN.value)
    
    def validate_plugin_access(self, plugin_id: str, permission: str) -> Dict[str, Any]:
        """
        Validate plugin access and return result.
        
        Args:
            plugin_id: Plugin identifier
            permission: Permission to check
            
        Returns:
            Dict with allowed, plugin_type, and error_message
        """
        if plugin_id not in self.plugin_permissions:
            return {
                "allowed": False,
                "plugin_type": None,
                "error_message": f"Unknown plugin: {plugin_id}"
            }
        
        if not self.has_permission(plugin_id, permission):
            return {
                "allowed": False,
                "plugin_type": self.get_plugin_type(plugin_id).value,
                "error_message": f"Plugin '{plugin_id}' does not have permission: {permission}"
            }
        
        return {
            "allowed": True,
            "plugin_type": self.get_plugin_type(plugin_id).value,
            "error_message": None
        }


class PluginIsolation:
    """
    Plugin isolation enforcer.
    
    Ensures plugins can only access their own data.
    """
    
    def __init__(self):
        """Initialize plugin isolation."""
        self.permission_checker = PermissionChecker()
    
    def validate_order_access(
        self,
        requesting_plugin: str,
        order_plugin: str
    ) -> bool:
        """
        Validate if plugin can access an order.
        
        Args:
            requesting_plugin: Plugin making the request
            order_plugin: Plugin that owns the order
            
        Returns:
            True if access allowed
        """
        # Plugin can only access its own orders
        return requesting_plugin == order_plugin
    
    def filter_orders_for_plugin(
        self,
        plugin_id: str,
        orders: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter orders to only include those belonging to the plugin.
        
        Args:
            plugin_id: Plugin identifier
            orders: List of order dictionaries
            
        Returns:
            Filtered list of orders
        """
        return [
            order for order in orders
            if order.get("plugin_id") == plugin_id
        ]
    
    def validate_trade_access(
        self,
        requesting_plugin: str,
        trade_plugin: str
    ) -> bool:
        """
        Validate if plugin can access a trade.
        
        Args:
            requesting_plugin: Plugin making the request
            trade_plugin: Plugin that owns the trade
            
        Returns:
            True if access allowed
        """
        return requesting_plugin == trade_plugin
    
    def get_isolation_context(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get isolation context for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Dict with isolation settings
        """
        plugin_type = self.permission_checker.get_plugin_type(plugin_id)
        
        if plugin_type == PluginType.V3_COMBINED:
            database = "zepix_combined.db"
        elif plugin_type in [
            PluginType.V6_PRICE_ACTION_1M,
            PluginType.V6_PRICE_ACTION_5M,
            PluginType.V6_PRICE_ACTION_15M,
            PluginType.V6_PRICE_ACTION_1H,
        ]:
            database = "zepix_price_action.db"
        else:
            database = None
        
        return {
            "plugin_id": plugin_id,
            "plugin_type": plugin_type.value if plugin_type else None,
            "database": database,
            "permissions": self.permission_checker.get_permissions(plugin_id),
            "is_v3": self.permission_checker.is_v3_plugin(plugin_id),
            "is_v6": self.permission_checker.is_v6_plugin(plugin_id),
        }


# Global instances
permission_checker = PermissionChecker()
plugin_isolation = PluginIsolation()


def check_permission(plugin_id: str, permission: str) -> bool:
    """
    Convenience function to check permission.
    
    Args:
        plugin_id: Plugin identifier
        permission: Permission to check
        
    Returns:
        True if plugin has permission
    """
    return permission_checker.has_permission(plugin_id, permission)


def get_plugin_permissions(plugin_id: str) -> List[str]:
    """
    Convenience function to get plugin permissions.
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        List of permission strings
    """
    return permission_checker.get_permissions(plugin_id)


def validate_access(plugin_id: str, permission: str) -> Dict[str, Any]:
    """
    Convenience function to validate access.
    
    Args:
        plugin_id: Plugin identifier
        permission: Permission to check
        
    Returns:
        Dict with validation result
    """
    return permission_checker.validate_plugin_access(plugin_id, permission)
