"""
Command Router for Multi-Telegram System.

This module provides intelligent routing of commands between bots:
- Slash command routing
- Button callback routing
- Message type routing
- Priority-based routing

Based on Document 18: TELEGRAM_SYSTEM_ARCHITECTURE.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
from enum import Enum
import re


logger = logging.getLogger(__name__)


class CommandCategory(Enum):
    """Command category enumeration."""
    SYSTEM = "system"
    TRADING = "trading"
    PLUGINS = "plugins"
    ANALYTICS = "analytics"
    SETTINGS = "settings"
    EMERGENCY = "emergency"


class RouteTarget(Enum):
    """Route target enumeration."""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    BROADCAST = "broadcast"


class MessageType(Enum):
    """Message type enumeration."""
    COMMAND = "command"
    CALLBACK = "callback"
    TEXT = "text"
    ENTRY = "entry"
    EXIT = "exit"
    PROFIT_BOOKING = "profit_booking"
    ERROR = "error"
    DAILY_REPORT = "daily_report"
    WEEKLY_SUMMARY = "weekly_summary"
    COMMAND_RESPONSE = "command_response"


@dataclass
class CommandDefinition:
    """Definition of a command."""
    name: str
    description: str
    category: CommandCategory
    handler_name: str
    requires_confirmation: bool = False
    admin_only: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "handler_name": self.handler_name,
            "requires_confirmation": self.requires_confirmation,
            "admin_only": self.admin_only
        }


@dataclass
class RouteRule:
    """Routing rule definition."""
    message_type: MessageType
    target: RouteTarget
    priority: int = 0
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    
    def matches(self, message_data: Dict[str, Any]) -> bool:
        """Check if rule matches message."""
        if self.condition:
            return self.condition(message_data)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_type": self.message_type.value,
            "target": self.target.value,
            "priority": self.priority
        }


@dataclass
class CallbackRoute:
    """Callback routing definition."""
    pattern: str
    handler_name: str
    category: CommandCategory
    requires_confirmation: bool = False
    
    def matches(self, callback_data: str) -> bool:
        """Check if callback data matches pattern."""
        return bool(re.match(self.pattern, callback_data))
    
    def extract_params(self, callback_data: str) -> Dict[str, Any]:
        """Extract parameters from callback data."""
        match = re.match(self.pattern, callback_data)
        if match:
            return match.groupdict()
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern": self.pattern,
            "handler_name": self.handler_name,
            "category": self.category.value,
            "requires_confirmation": self.requires_confirmation
        }


@dataclass
class RoutedMessage:
    """Message after routing."""
    original_type: MessageType
    target: RouteTarget
    content: Any
    handler_name: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_type": self.original_type.value,
            "target": self.target.value,
            "handler_name": self.handler_name,
            "params": self.params,
            "timestamp": self.timestamp.isoformat()
        }


class CommandRegistry:
    """Registry of all available commands."""
    
    def __init__(self):
        """Initialize command registry."""
        self.commands: Dict[str, CommandDefinition] = {}
        self._register_default_commands()
    
    def _register_default_commands(self) -> None:
        """Register default commands."""
        default_commands = [
            CommandDefinition(
                name="start",
                description="Initialize bot",
                category=CommandCategory.SYSTEM,
                handler_name="handle_start"
            ),
            CommandDefinition(
                name="status",
                description="Show current status",
                category=CommandCategory.SYSTEM,
                handler_name="handle_status"
            ),
            CommandDefinition(
                name="trades",
                description="List open positions",
                category=CommandCategory.TRADING,
                handler_name="handle_trades"
            ),
            CommandDefinition(
                name="close",
                description="Close specific trade",
                category=CommandCategory.TRADING,
                handler_name="handle_close",
                requires_confirmation=True
            ),
            CommandDefinition(
                name="closeall",
                description="Close all positions",
                category=CommandCategory.EMERGENCY,
                handler_name="handle_close_all",
                requires_confirmation=True,
                admin_only=True
            ),
            CommandDefinition(
                name="pause",
                description="Pause bot",
                category=CommandCategory.SYSTEM,
                handler_name="handle_pause",
                admin_only=True
            ),
            CommandDefinition(
                name="resume",
                description="Resume bot",
                category=CommandCategory.SYSTEM,
                handler_name="handle_resume",
                admin_only=True
            ),
            CommandDefinition(
                name="enable",
                description="Enable plugin",
                category=CommandCategory.PLUGINS,
                handler_name="handle_enable_plugin"
            ),
            CommandDefinition(
                name="disable",
                description="Disable plugin",
                category=CommandCategory.PLUGINS,
                handler_name="handle_disable_plugin"
            ),
            CommandDefinition(
                name="config",
                description="View plugin config",
                category=CommandCategory.SETTINGS,
                handler_name="handle_config"
            ),
            CommandDefinition(
                name="daily",
                description="Daily summary",
                category=CommandCategory.ANALYTICS,
                handler_name="handle_daily"
            ),
            CommandDefinition(
                name="weekly",
                description="Weekly summary",
                category=CommandCategory.ANALYTICS,
                handler_name="handle_weekly"
            ),
            CommandDefinition(
                name="help",
                description="Show all commands",
                category=CommandCategory.SYSTEM,
                handler_name="handle_help"
            ),
            CommandDefinition(
                name="menu",
                description="Show main menu",
                category=CommandCategory.SYSTEM,
                handler_name="handle_menu"
            ),
            CommandDefinition(
                name="health",
                description="Show health status",
                category=CommandCategory.SYSTEM,
                handler_name="handle_health"
            ),
            CommandDefinition(
                name="uptime",
                description="Show uptime",
                category=CommandCategory.SYSTEM,
                handler_name="handle_uptime"
            ),
            CommandDefinition(
                name="plugins",
                description="List all plugins",
                category=CommandCategory.PLUGINS,
                handler_name="handle_plugins"
            ),
            CommandDefinition(
                name="positions",
                description="Show open positions",
                category=CommandCategory.TRADING,
                handler_name="handle_positions"
            )
        ]
        
        for cmd in default_commands:
            self.register(cmd)
    
    def register(self, command: CommandDefinition) -> None:
        """Register a command."""
        self.commands[command.name] = command
        logger.debug(f"Registered command: /{command.name}")
    
    def unregister(self, name: str) -> bool:
        """Unregister a command."""
        if name in self.commands:
            del self.commands[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[CommandDefinition]:
        """Get command by name."""
        return self.commands.get(name)
    
    def get_by_category(self, category: CommandCategory) -> List[CommandDefinition]:
        """Get commands by category."""
        return [cmd for cmd in self.commands.values() if cmd.category == category]
    
    def get_all(self) -> List[CommandDefinition]:
        """Get all commands."""
        return list(self.commands.values())
    
    def get_help_text(self) -> str:
        """Generate help text for all commands."""
        lines = ["Available Commands:\n"]
        
        for category in CommandCategory:
            cmds = self.get_by_category(category)
            if cmds:
                lines.append(f"\n{category.value.upper()}:")
                for cmd in cmds:
                    lines.append(f"  /{cmd.name} - {cmd.description}")
        
        return "\n".join(lines)


class CallbackRegistry:
    """Registry of callback routes."""
    
    def __init__(self):
        """Initialize callback registry."""
        self.routes: List[CallbackRoute] = []
        self._register_default_routes()
    
    def _register_default_routes(self) -> None:
        """Register default callback routes."""
        default_routes = [
            CallbackRoute(
                pattern=r"close_trade_(?P<trade_id>\d+)",
                handler_name="close_trade_handler",
                category=CommandCategory.TRADING,
                requires_confirmation=True
            ),
            CallbackRoute(
                pattern=r"modify_trade_(?P<trade_id>\d+)",
                handler_name="modify_trade_handler",
                category=CommandCategory.TRADING
            ),
            CallbackRoute(
                pattern=r"profit_trade_(?P<trade_id>\d+)_(?P<percentage>\d+)",
                handler_name="book_profit_handler",
                category=CommandCategory.TRADING
            ),
            CallbackRoute(
                pattern=r"trades_page_(?P<page>\d+)",
                handler_name="trades_page_handler",
                category=CommandCategory.TRADING
            ),
            CallbackRoute(
                pattern=r"status_refresh",
                handler_name="refresh_status_handler",
                category=CommandCategory.SYSTEM
            ),
            CallbackRoute(
                pattern=r"status_details",
                handler_name="status_details_handler",
                category=CommandCategory.SYSTEM
            ),
            CallbackRoute(
                pattern=r"main_menu",
                handler_name="main_menu_handler",
                category=CommandCategory.SYSTEM
            ),
            CallbackRoute(
                pattern=r"settings_plugins",
                handler_name="settings_plugins_handler",
                category=CommandCategory.SETTINGS
            ),
            CallbackRoute(
                pattern=r"settings_quick",
                handler_name="settings_quick_handler",
                category=CommandCategory.SETTINGS
            ),
            CallbackRoute(
                pattern=r"settings_edit",
                handler_name="settings_edit_handler",
                category=CommandCategory.SETTINGS
            ),
            CallbackRoute(
                pattern=r"emergency_close_all",
                handler_name="emergency_close_all_handler",
                category=CommandCategory.EMERGENCY,
                requires_confirmation=True
            ),
            CallbackRoute(
                pattern=r"emergency_pause",
                handler_name="emergency_pause_handler",
                category=CommandCategory.EMERGENCY
            ),
            CallbackRoute(
                pattern=r"emergency_resume",
                handler_name="emergency_resume_handler",
                category=CommandCategory.EMERGENCY
            ),
            CallbackRoute(
                pattern=r"emergency_restart_plugins",
                handler_name="emergency_restart_plugins_handler",
                category=CommandCategory.EMERGENCY
            ),
            CallbackRoute(
                pattern=r"emergency_cancel",
                handler_name="emergency_cancel_handler",
                category=CommandCategory.EMERGENCY
            ),
            CallbackRoute(
                pattern=r"plugin_enable_(?P<plugin_id>\w+)",
                handler_name="plugin_enable_handler",
                category=CommandCategory.PLUGINS
            ),
            CallbackRoute(
                pattern=r"plugin_disable_(?P<plugin_id>\w+)",
                handler_name="plugin_disable_handler",
                category=CommandCategory.PLUGINS
            ),
            CallbackRoute(
                pattern=r"confirm_(?P<action>\w+)",
                handler_name="confirm_action_handler",
                category=CommandCategory.SYSTEM
            ),
            CallbackRoute(
                pattern=r"cancel",
                handler_name="cancel_handler",
                category=CommandCategory.SYSTEM
            )
        ]
        
        for route in default_routes:
            self.register(route)
    
    def register(self, route: CallbackRoute) -> None:
        """Register a callback route."""
        self.routes.append(route)
        logger.debug(f"Registered callback route: {route.pattern}")
    
    def find_route(self, callback_data: str) -> Optional[CallbackRoute]:
        """Find matching route for callback data."""
        for route in self.routes:
            if route.matches(callback_data):
                return route
        return None
    
    def get_all(self) -> List[CallbackRoute]:
        """Get all routes."""
        return self.routes.copy()


class CommandRouter:
    """
    Intelligent command and message router.
    
    Routes messages to appropriate bots based on:
    - Message type
    - Command category
    - Callback patterns
    - Custom rules
    """
    
    def __init__(self):
        """Initialize command router."""
        self.command_registry = CommandRegistry()
        self.callback_registry = CallbackRegistry()
        self.route_rules: List[RouteRule] = []
        self._init_default_rules()
    
    def _init_default_rules(self) -> None:
        """Initialize default routing rules."""
        self.route_rules = [
            RouteRule(
                message_type=MessageType.COMMAND,
                target=RouteTarget.CONTROLLER,
                priority=10
            ),
            RouteRule(
                message_type=MessageType.CALLBACK,
                target=RouteTarget.CONTROLLER,
                priority=10
            ),
            RouteRule(
                message_type=MessageType.ENTRY,
                target=RouteTarget.NOTIFICATION,
                priority=10
            ),
            RouteRule(
                message_type=MessageType.EXIT,
                target=RouteTarget.NOTIFICATION,
                priority=10
            ),
            RouteRule(
                message_type=MessageType.PROFIT_BOOKING,
                target=RouteTarget.NOTIFICATION,
                priority=10
            ),
            RouteRule(
                message_type=MessageType.ERROR,
                target=RouteTarget.NOTIFICATION,
                priority=20
            ),
            RouteRule(
                message_type=MessageType.DAILY_REPORT,
                target=RouteTarget.ANALYTICS,
                priority=10
            ),
            RouteRule(
                message_type=MessageType.WEEKLY_SUMMARY,
                target=RouteTarget.ANALYTICS,
                priority=10
            ),
            RouteRule(
                message_type=MessageType.COMMAND_RESPONSE,
                target=RouteTarget.CONTROLLER,
                priority=10
            )
        ]
    
    def add_rule(self, rule: RouteRule) -> None:
        """Add a routing rule."""
        self.route_rules.append(rule)
        self.route_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def route_command(self, command_text: str) -> Optional[RoutedMessage]:
        """Route a slash command."""
        parts = command_text.strip().split()
        if not parts:
            return None
        
        cmd_name = parts[0].lstrip("/")
        args = parts[1:] if len(parts) > 1 else []
        
        cmd_def = self.command_registry.get(cmd_name)
        if not cmd_def:
            return None
        
        return RoutedMessage(
            original_type=MessageType.COMMAND,
            target=RouteTarget.CONTROLLER,
            content=command_text,
            handler_name=cmd_def.handler_name,
            params={"command": cmd_name, "args": args}
        )
    
    def route_callback(self, callback_data: str) -> Optional[RoutedMessage]:
        """Route a callback query."""
        route = self.callback_registry.find_route(callback_data)
        if not route:
            return None
        
        params = route.extract_params(callback_data)
        
        return RoutedMessage(
            original_type=MessageType.CALLBACK,
            target=RouteTarget.CONTROLLER,
            content=callback_data,
            handler_name=route.handler_name,
            params=params
        )
    
    def route_message(self, message_type: MessageType, 
                     content: Any,
                     message_data: Optional[Dict[str, Any]] = None) -> RoutedMessage:
        """Route a message based on type."""
        message_data = message_data or {}
        
        for rule in self.route_rules:
            if rule.message_type == message_type and rule.matches(message_data):
                return RoutedMessage(
                    original_type=message_type,
                    target=rule.target,
                    content=content,
                    params=message_data
                )
        
        return RoutedMessage(
            original_type=message_type,
            target=RouteTarget.CONTROLLER,
            content=content,
            params=message_data
        )
    
    def get_target_for_type(self, message_type: MessageType) -> RouteTarget:
        """Get target bot for message type."""
        for rule in self.route_rules:
            if rule.message_type == message_type:
                return rule.target
        return RouteTarget.CONTROLLER
    
    def get_command_help(self) -> str:
        """Get help text for all commands."""
        return self.command_registry.get_help_text()
    
    def get_commands_by_category(self, category: CommandCategory) -> List[CommandDefinition]:
        """Get commands by category."""
        return self.command_registry.get_by_category(category)
    
    def is_valid_command(self, command_name: str) -> bool:
        """Check if command is valid."""
        return self.command_registry.get(command_name) is not None
    
    def requires_confirmation(self, command_name: str) -> bool:
        """Check if command requires confirmation."""
        cmd = self.command_registry.get(command_name)
        return cmd.requires_confirmation if cmd else False
    
    def is_admin_only(self, command_name: str) -> bool:
        """Check if command is admin only."""
        cmd = self.command_registry.get(command_name)
        return cmd.admin_only if cmd else False


def create_command_router() -> CommandRouter:
    """Factory function to create Command Router."""
    return CommandRouter()
