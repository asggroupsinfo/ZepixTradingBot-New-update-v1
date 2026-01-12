"""
API Reference Generator for V5 Hybrid Plugin Architecture.

This module provides automated API documentation generation:
- Service API documentation
- Plugin API documentation
- REST API documentation
- Telegram Bot API documentation

Based on Document 14: USER_DOCUMENTATION.md

Version: 1.0
Date: 2026-01-12
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class APICategory(Enum):
    """API categories."""
    SERVICE_API = "service_api"
    PLUGIN_API = "plugin_api"
    REST_API = "rest_api"
    TELEGRAM_API = "telegram_api"
    DATABASE_API = "database_api"


@dataclass
class APIEndpoint:
    """An API endpoint."""
    name: str
    method: str
    path: str
    description: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown."""
        lines = [
            f"### `{self.method}` {self.path}",
            "",
            f"**{self.name}**",
            "",
            self.description,
            "",
        ]
        
        if self.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            lines.append("| Name | Type | Required | Description |")
            lines.append("|------|------|----------|-------------|")
            for param in self.parameters:
                required = "Yes" if param.get("required", False) else "No"
                lines.append(f"| `{param['name']}` | {param.get('type', 'Any')} | {required} | {param.get('description', '')} |")
            lines.append("")
        
        if self.request_body:
            lines.append("**Request Body:**")
            lines.append("")
            lines.append("```json")
            lines.append(str(self.request_body))
            lines.append("```")
            lines.append("")
        
        if self.response:
            lines.append("**Response:**")
            lines.append("")
            lines.append("```json")
            lines.append(str(self.response))
            lines.append("```")
            lines.append("")
        
        if self.examples:
            lines.append("**Examples:**")
            lines.append("")
            for example in self.examples:
                lines.append(f"*{example.get('title', 'Example')}*")
                lines.append("")
                lines.append("```python")
                lines.append(example.get("code", ""))
                lines.append("```")
                lines.append("")
        
        return "\n".join(lines)


@dataclass
class APISection:
    """A section of API documentation."""
    title: str
    description: str
    category: APICategory
    endpoints: List[APIEndpoint] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown."""
        lines = [
            f"## {self.title}",
            "",
            self.description,
            "",
        ]
        
        for endpoint in self.endpoints:
            lines.append(endpoint.to_markdown())
        
        return "\n".join(lines)


class ServiceAPIReference:
    """Service API reference documentation."""
    
    ORDER_EXECUTION_ENDPOINTS = [
        APIEndpoint(
            name="Place Dual Orders (V3)",
            method="async",
            path="service_api.place_dual_orders_v3()",
            description="Place dual orders (Order A + Order B) for V3 Combined Logic plugin.",
            parameters=[
                {"name": "symbol", "type": "str", "required": True, "description": "Trading symbol (e.g., 'XAUUSD')"},
                {"name": "direction", "type": "str", "required": True, "description": "Trade direction ('BUY' or 'SELL')"},
                {"name": "lot_size_a", "type": "float", "required": True, "description": "Lot size for Order A"},
                {"name": "lot_size_b", "type": "float", "required": True, "description": "Lot size for Order B"},
                {"name": "stop_loss", "type": "float", "required": True, "description": "Stop loss price"},
                {"name": "take_profit", "type": "float", "required": False, "description": "Take profit price"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Place BUY dual orders",
                "code": """result = await service_api.place_dual_orders_v3(
    symbol="XAUUSD",
    direction="BUY",
    lot_size_a=0.1,
    lot_size_b=0.2,
    stop_loss=2025.00,
    take_profit=2035.00,
    plugin_id="combined_v3"
)"""
            }]
        ),
        APIEndpoint(
            name="Place Single Order",
            method="async",
            path="service_api.place_order()",
            description="Place a single order for any plugin.",
            parameters=[
                {"name": "symbol", "type": "str", "required": True, "description": "Trading symbol"},
                {"name": "direction", "type": "str", "required": True, "description": "Trade direction"},
                {"name": "lot_size", "type": "float", "required": True, "description": "Lot size"},
                {"name": "stop_loss", "type": "float", "required": False, "description": "Stop loss price"},
                {"name": "take_profit", "type": "float", "required": False, "description": "Take profit price"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Place single order",
                "code": """result = await service_api.place_order(
    symbol="EURUSD",
    direction="SELL",
    lot_size=0.1,
    stop_loss=1.0850,
    plugin_id="price_action_5m"
)"""
            }]
        ),
        APIEndpoint(
            name="Modify Order",
            method="async",
            path="service_api.modify_order()",
            description="Modify an existing order's stop loss or take profit.",
            parameters=[
                {"name": "ticket", "type": "int", "required": True, "description": "Order ticket number"},
                {"name": "stop_loss", "type": "float", "required": False, "description": "New stop loss price"},
                {"name": "take_profit", "type": "float", "required": False, "description": "New take profit price"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Modify stop loss",
                "code": """result = await service_api.modify_order(
    ticket=12345,
    stop_loss=2027.00,
    plugin_id="combined_v3"
)"""
            }]
        ),
        APIEndpoint(
            name="Close Position",
            method="async",
            path="service_api.close_position()",
            description="Close an open position.",
            parameters=[
                {"name": "ticket", "type": "int", "required": True, "description": "Position ticket number"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Close position",
                "code": """result = await service_api.close_position(
    ticket=12345,
    plugin_id="combined_v3"
)"""
            }]
        ),
        APIEndpoint(
            name="Close Position Partial",
            method="async",
            path="service_api.close_position_partial()",
            description="Partially close an open position.",
            parameters=[
                {"name": "ticket", "type": "int", "required": True, "description": "Position ticket number"},
                {"name": "lot_size", "type": "float", "required": True, "description": "Lot size to close"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Partial close",
                "code": """result = await service_api.close_position_partial(
    ticket=12345,
    lot_size=0.05,
    plugin_id="combined_v3"
)"""
            }]
        ),
    ]
    
    RISK_MANAGEMENT_ENDPOINTS = [
        APIEndpoint(
            name="Calculate Lot Size",
            method="async",
            path="service_api.calculate_lot_size()",
            description="Calculate lot size based on risk percentage and stop loss.",
            parameters=[
                {"name": "symbol", "type": "str", "required": True, "description": "Trading symbol"},
                {"name": "risk_percentage", "type": "float", "required": True, "description": "Risk percentage (e.g., 1.5)"},
                {"name": "stop_loss_pips", "type": "float", "required": True, "description": "Stop loss in pips"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Calculate lot size",
                "code": """lot_size = await service_api.calculate_lot_size(
    symbol="XAUUSD",
    risk_percentage=1.5,
    stop_loss_pips=25,
    plugin_id="combined_v3"
)"""
            }]
        ),
        APIEndpoint(
            name="Check Daily Limit",
            method="async",
            path="service_api.check_daily_limit()",
            description="Check if plugin has reached daily loss limit.",
            parameters=[
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Check daily limit",
                "code": """can_trade = await service_api.check_daily_limit(
    plugin_id="combined_v3"
)
if not can_trade:
    logger.warning("Daily limit reached")"""
            }]
        ),
        APIEndpoint(
            name="Get Risk Status",
            method="async",
            path="service_api.get_risk_status()",
            description="Get current risk status for a plugin.",
            parameters=[
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Get risk status",
                "code": """status = await service_api.get_risk_status(
    plugin_id="combined_v3"
)
print(f"Daily P&L: {status['daily_pnl']}")
print(f"Open risk: {status['open_risk']}")"""
            }]
        ),
    ]
    
    NOTIFICATION_ENDPOINTS = [
        APIEndpoint(
            name="Send Notification",
            method="async",
            path="service_api.send_notification()",
            description="Send a notification via Telegram.",
            parameters=[
                {"name": "message", "type": "str", "required": True, "description": "Notification message"},
                {"name": "priority", "type": "str", "required": False, "description": "Priority level ('low', 'normal', 'high', 'critical')"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Send notification",
                "code": """await service_api.send_notification(
    message="Trade opened: XAUUSD BUY 0.1 lot",
    priority="high",
    plugin_id="combined_v3"
)"""
            }]
        ),
        APIEndpoint(
            name="Send Trade Alert",
            method="async",
            path="service_api.send_trade_alert()",
            description="Send a formatted trade alert.",
            parameters=[
                {"name": "trade_data", "type": "dict", "required": True, "description": "Trade data dictionary"},
                {"name": "alert_type", "type": "str", "required": True, "description": "Alert type ('entry', 'exit', 'modify')"},
                {"name": "plugin_id", "type": "str", "required": True, "description": "Plugin identifier"},
            ],
            examples=[{
                "title": "Send trade alert",
                "code": """await service_api.send_trade_alert(
    trade_data={
        "symbol": "XAUUSD",
        "direction": "BUY",
        "lot": 0.1,
        "entry": 2030.50,
        "sl": 2025.00,
        "tp": 2040.00
    },
    alert_type="entry",
    plugin_id="combined_v3"
)"""
            }]
        ),
    ]
    
    TREND_MANAGEMENT_ENDPOINTS = [
        APIEndpoint(
            name="Get Trend Status",
            method="async",
            path="service_api.get_trend_status()",
            description="Get current trend status for a symbol.",
            parameters=[
                {"name": "symbol", "type": "str", "required": True, "description": "Trading symbol"},
                {"name": "timeframe", "type": "str", "required": False, "description": "Timeframe (e.g., '1H', '4H')"},
            ],
            examples=[{
                "title": "Get trend status",
                "code": """trend = await service_api.get_trend_status(
    symbol="XAUUSD",
    timeframe="1H"
)
print(f"Trend: {trend['direction']}")
print(f"Strength: {trend['strength']}")"""
            }]
        ),
        APIEndpoint(
            name="Update Trend",
            method="async",
            path="service_api.update_trend()",
            description="Update trend status for a symbol.",
            parameters=[
                {"name": "symbol", "type": "str", "required": True, "description": "Trading symbol"},
                {"name": "direction", "type": "str", "required": True, "description": "Trend direction ('BULLISH', 'BEARISH', 'NEUTRAL')"},
                {"name": "strength", "type": "float", "required": False, "description": "Trend strength (0-100)"},
                {"name": "timeframe", "type": "str", "required": False, "description": "Timeframe"},
            ],
            examples=[{
                "title": "Update trend",
                "code": """await service_api.update_trend(
    symbol="XAUUSD",
    direction="BULLISH",
    strength=75.5,
    timeframe="1H"
)"""
            }]
        ),
    ]
    
    @classmethod
    def get_all_sections(cls) -> List[APISection]:
        """Get all API sections."""
        return [
            APISection(
                title="Order Execution Service",
                description="APIs for placing, modifying, and closing orders.",
                category=APICategory.SERVICE_API,
                endpoints=cls.ORDER_EXECUTION_ENDPOINTS
            ),
            APISection(
                title="Risk Management Service",
                description="APIs for risk calculation and daily limit management.",
                category=APICategory.SERVICE_API,
                endpoints=cls.RISK_MANAGEMENT_ENDPOINTS
            ),
            APISection(
                title="Notification Service",
                description="APIs for sending notifications and trade alerts.",
                category=APICategory.SERVICE_API,
                endpoints=cls.NOTIFICATION_ENDPOINTS
            ),
            APISection(
                title="Trend Management Service",
                description="APIs for trend tracking and management.",
                category=APICategory.SERVICE_API,
                endpoints=cls.TREND_MANAGEMENT_ENDPOINTS
            ),
        ]


class TelegramAPIReference:
    """Telegram Bot API reference documentation."""
    
    CONTROLLER_COMMANDS = [
        APIEndpoint(
            name="Status",
            method="command",
            path="/status",
            description="View bot health and active plugins.",
            parameters=[],
            examples=[{
                "title": "Check status",
                "code": "/status"
            }]
        ),
        APIEndpoint(
            name="Enable Plugin",
            method="command",
            path="/enable_plugin <name>",
            description="Enable a plugin.",
            parameters=[
                {"name": "name", "type": "str", "required": True, "description": "Plugin name to enable"},
            ],
            examples=[{
                "title": "Enable combined_v3",
                "code": "/enable_plugin combined_v3"
            }]
        ),
        APIEndpoint(
            name="Disable Plugin",
            method="command",
            path="/disable_plugin <name>",
            description="Disable a plugin.",
            parameters=[
                {"name": "name", "type": "str", "required": True, "description": "Plugin name to disable"},
            ],
            examples=[{
                "title": "Disable combined_v3",
                "code": "/disable_plugin combined_v3"
            }]
        ),
        APIEndpoint(
            name="Emergency Stop",
            method="command",
            path="/emergency_stop",
            description="Stop all trading immediately. Closes all positions and disables all plugins.",
            parameters=[],
            examples=[{
                "title": "Emergency stop",
                "code": "/emergency_stop"
            }]
        ),
        APIEndpoint(
            name="Config Reload",
            method="command",
            path="/config_reload <plugin>",
            description="Reload configuration for a plugin.",
            parameters=[
                {"name": "plugin", "type": "str", "required": True, "description": "Plugin name to reload config"},
            ],
            examples=[{
                "title": "Reload config",
                "code": "/config_reload combined_v3"
            }]
        ),
        APIEndpoint(
            name="Daily Limit",
            method="command",
            path="/daily_limit <plugin>",
            description="Check daily loss limit status for a plugin.",
            parameters=[
                {"name": "plugin", "type": "str", "required": True, "description": "Plugin name"},
            ],
            examples=[{
                "title": "Check daily limit",
                "code": "/daily_limit combined_v3"
            }]
        ),
    ]
    
    ANALYTICS_COMMANDS = [
        APIEndpoint(
            name="Daily Report",
            method="command",
            path="/daily_report",
            description="Get today's P&L summary.",
            parameters=[],
            examples=[{
                "title": "Get daily report",
                "code": "/daily_report"
            }]
        ),
        APIEndpoint(
            name="Weekly Report",
            method="command",
            path="/weekly_report",
            description="Get weekly performance report.",
            parameters=[],
            examples=[{
                "title": "Get weekly report",
                "code": "/weekly_report"
            }]
        ),
        APIEndpoint(
            name="Plugin Stats",
            method="command",
            path="/plugin_stats",
            description="Get per-plugin performance breakdown.",
            parameters=[],
            examples=[{
                "title": "Get plugin stats",
                "code": "/plugin_stats"
            }]
        ),
        APIEndpoint(
            name="Export Trades",
            method="command",
            path="/export_trades",
            description="Download trade history as CSV.",
            parameters=[],
            examples=[{
                "title": "Export trades",
                "code": "/export_trades"
            }]
        ),
    ]
    
    @classmethod
    def get_all_sections(cls) -> List[APISection]:
        """Get all Telegram API sections."""
        return [
            APISection(
                title="Controller Bot Commands",
                description="Commands for managing the trading bot.",
                category=APICategory.TELEGRAM_API,
                endpoints=cls.CONTROLLER_COMMANDS
            ),
            APISection(
                title="Analytics Bot Commands",
                description="Commands for viewing performance reports.",
                category=APICategory.TELEGRAM_API,
                endpoints=cls.ANALYTICS_COMMANDS
            ),
        ]


class APIReferenceGenerator:
    """Generator for API reference documentation."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize API reference generator."""
        self.output_dir = output_dir or os.path.join(os.getcwd(), "docs")
    
    def generate(self) -> str:
        """Generate API reference documentation."""
        lines = [
            "# API Reference",
            "",
            f"**Version:** 1.0",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
            f"**Type:** API Reference",
            "",
            "---",
            "",
            "This document provides a complete reference for all APIs in the V5 Hybrid Plugin Architecture.",
            "",
        ]
        
        lines.append("# Service API")
        lines.append("")
        lines.append("The Service API provides access to core trading services for plugins.")
        lines.append("")
        
        for section in ServiceAPIReference.get_all_sections():
            lines.append(section.to_markdown())
        
        lines.append("# Telegram Bot API")
        lines.append("")
        lines.append("Commands available in the Telegram bots.")
        lines.append("")
        
        for section in TelegramAPIReference.get_all_sections():
            lines.append(section.to_markdown())
        
        return "\n".join(lines)
    
    def save(self, filename: str = "API_REFERENCE.md") -> str:
        """Save API reference to file."""
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        
        content = self.generate()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath


def generate_api_reference(output_dir: Optional[str] = None) -> str:
    """Generate API reference documentation."""
    generator = APIReferenceGenerator(output_dir)
    return generator.save()
