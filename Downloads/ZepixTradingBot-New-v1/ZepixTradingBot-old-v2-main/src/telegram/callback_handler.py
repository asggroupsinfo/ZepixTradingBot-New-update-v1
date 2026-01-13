"""
Callback Handler - Button Click Mapping for Telegram Bots

Document 20: Telegram Unified Interface Addendum
Maps button clicks (callback queries) to specific actions.

Features:
- Menu navigation callbacks
- Action execution callbacks
- Wizard initiation callbacks
- Position management callbacks
- Plugin management callbacks
- Confirmation handling
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable, Tuple
from datetime import datetime
import asyncio
import logging
import re


class CallbackType(Enum):
    """Types of callback queries"""
    MENU = "menu"           # Navigate to menu
    ACTION = "action"       # Execute action
    WIZARD = "wizard"       # Start input wizard
    POSITION = "position"   # Position management
    PLUGIN = "plugin"       # Plugin management
    CONFIRM = "confirm"     # Confirmation
    CANCEL = "cancel"       # Cancel action
    PAGE = "page"           # Pagination
    CUSTOM = "custom"       # Custom callback


@dataclass
class CallbackData:
    """Parsed callback data"""
    callback_type: CallbackType
    action: str
    params: List[str] = field(default_factory=list)
    raw_data: str = ""
    
    @classmethod
    def parse(cls, data: str) -> 'CallbackData':
        """Parse callback data string"""
        parts = data.split(":")
        
        if not parts:
            return cls(
                callback_type=CallbackType.CUSTOM,
                action="unknown",
                raw_data=data
            )
        
        # Determine callback type
        type_str = parts[0].lower()
        callback_type = CallbackType.CUSTOM
        
        for ct in CallbackType:
            if ct.value == type_str:
                callback_type = ct
                break
        
        action = parts[1] if len(parts) > 1 else ""
        params = parts[2:] if len(parts) > 2 else []
        
        return cls(
            callback_type=callback_type,
            action=action,
            params=params,
            raw_data=data
        )
    
    def to_string(self) -> str:
        """Convert back to callback data string"""
        parts = [self.callback_type.value, self.action] + self.params
        return ":".join(parts)


@dataclass
class CallbackContext:
    """Context for callback execution"""
    user_id: int
    chat_id: int
    message_id: int
    callback_data: CallbackData
    timestamp: datetime = field(default_factory=datetime.utcnow)
    answered: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "message_id": self.message_id,
            "callback_type": self.callback_data.callback_type.value,
            "action": self.callback_data.action,
            "params": self.callback_data.params,
            "timestamp": self.timestamp.isoformat(),
            "answered": self.answered
        }


@dataclass
class CallbackResult:
    """Result of callback execution"""
    success: bool
    message: Optional[str] = None
    show_alert: bool = False
    edit_message: bool = True
    new_text: Optional[str] = None
    new_keyboard: Optional[List[List[Dict[str, str]]]] = None
    redirect_menu: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# Type alias for callback handlers
CallbackHandler = Callable[[CallbackContext], Awaitable[CallbackResult]]


class CallbackRegistry:
    """
    Registry for callback handlers
    
    Maps callback patterns to handler functions.
    """
    
    def __init__(self):
        self.handlers: Dict[str, CallbackHandler] = {}
        self.pattern_handlers: List[Tuple[re.Pattern, CallbackHandler]] = []
        self.default_handler: Optional[CallbackHandler] = None
        self.logger = logging.getLogger(__name__)
    
    def register(self, pattern: str, handler: CallbackHandler) -> None:
        """Register handler for exact pattern"""
        self.handlers[pattern] = handler
        self.logger.debug(f"Registered handler for pattern: {pattern}")
    
    def register_pattern(self, pattern: str, handler: CallbackHandler) -> None:
        """Register handler for regex pattern"""
        compiled = re.compile(pattern)
        self.pattern_handlers.append((compiled, handler))
        self.logger.debug(f"Registered pattern handler: {pattern}")
    
    def register_default(self, handler: CallbackHandler) -> None:
        """Register default handler for unmatched callbacks"""
        self.default_handler = handler
    
    def get_handler(self, callback_data: str) -> Optional[CallbackHandler]:
        """Get handler for callback data"""
        # Check exact match first
        if callback_data in self.handlers:
            return self.handlers[callback_data]
        
        # Check pattern matches
        for pattern, handler in self.pattern_handlers:
            if pattern.match(callback_data):
                return handler
        
        # Return default handler
        return self.default_handler
    
    def unregister(self, pattern: str) -> bool:
        """Unregister handler"""
        if pattern in self.handlers:
            del self.handlers[pattern]
            return True
        return False
    
    def list_handlers(self) -> List[str]:
        """List all registered patterns"""
        return list(self.handlers.keys())


class CallbackProcessor:
    """
    Callback Processor
    
    Processes callback queries and routes to appropriate handlers.
    Implements the zero-typing interface principle.
    """
    
    def __init__(self):
        self.registry = CallbackRegistry()
        self.pending_confirmations: Dict[int, Dict[str, Any]] = {}  # user_id -> pending action
        self.logger = logging.getLogger(__name__)
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default callback handlers"""
        # Menu navigation
        self.registry.register_pattern(r"^menu:", self._handle_menu)
        
        # Actions
        self.registry.register_pattern(r"^action:", self._handle_action)
        
        # Wizards
        self.registry.register_pattern(r"^wizard:", self._handle_wizard)
        
        # Position management
        self.registry.register_pattern(r"^position:", self._handle_position)
        
        # Plugin management
        self.registry.register_pattern(r"^plugin:", self._handle_plugin)
        
        # Confirmations
        self.registry.register_pattern(r"^confirm:", self._handle_confirm)
        self.registry.register("cancel", self._handle_cancel)
        
        # Pagination
        self.registry.register_pattern(r"^page:", self._handle_page)
        
        # Default handler
        self.registry.register_default(self._handle_unknown)
    
    async def process(self, context: CallbackContext) -> CallbackResult:
        """Process callback query"""
        callback_data = context.callback_data.raw_data
        
        self.logger.debug(f"Processing callback: {callback_data}")
        
        handler = self.registry.get_handler(callback_data)
        
        if handler:
            try:
                result = await handler(context)
                context.answered = True
                return result
            except Exception as e:
                self.logger.error(f"Error processing callback: {e}")
                return CallbackResult(
                    success=False,
                    message=f"Error: {str(e)}",
                    show_alert=True
                )
        
        return CallbackResult(
            success=False,
            message="Unknown action",
            show_alert=True
        )
    
    async def _handle_menu(self, context: CallbackContext) -> CallbackResult:
        """Handle menu navigation"""
        menu_name = context.callback_data.action
        
        return CallbackResult(
            success=True,
            redirect_menu=menu_name,
            data={"menu": menu_name}
        )
    
    async def _handle_action(self, context: CallbackContext) -> CallbackResult:
        """Handle action execution"""
        action = context.callback_data.action
        params = context.callback_data.params
        
        # Map actions to responses
        action_messages = {
            "status": "📊 Fetching bot status...",
            "history": "📜 Loading trade history...",
            "close_all": "⚠️ Are you sure you want to close all positions?",
            "book_profits": "💵 Booking profits...",
            "breakeven": "⚖️ Moving positions to breakeven...",
            "refresh_positions": "🔄 Refreshing positions...",
            "notification_settings": "🔔 Loading notification settings...",
            "voice_settings": "🔊 Loading voice alert settings...",
            "symbol_settings": "💱 Loading symbol settings...",
            "session_settings": "🕐 Loading session settings...",
            "active_plugins": "✅ Loading active plugins...",
            "all_plugins": "📋 Loading all plugins...",
            "reload_plugins": "🔄 Reloading plugins...",
            "risk_status": "📊 Loading risk status...",
            "daily_limits": "📅 Loading daily limits...",
            "emergency_stop": "🚨 EMERGENCY STOP triggered!",
            "daily_report": "📊 Generating daily report...",
            "weekly_report": "📈 Generating weekly report...",
            "win_rate": "🎯 Calculating win rate...",
            "pnl_chart": "📉 Generating P&L chart...",
            "plugin_stats": "🔌 Loading plugin statistics...",
            "symbol_stats": "💱 Loading symbol statistics...",
            "quick_start": "🚀 Quick Start Guide",
            "commands": "📋 Available Commands",
            "faq": "❓ Frequently Asked Questions",
            "support": "💬 Contact Support",
            "about": "ℹ️ About Zepix Trading Bot",
            "version": "🏷️ Version Information",
            "start_bot": "▶️ Starting bot...",
            "stop_bot": "⏹️ Stopping bot...",
            "system_status": "🖥️ Loading system status...",
            "mt5_status": "📡 Checking MT5 connection...",
            "view_logs": "📜 Loading logs...",
            "clear_logs": "🗑️ Clearing logs...",
            "restart_bot": "🔄 Restarting bot...",
            "backup": "💾 Creating backup..."
        }
        
        message = action_messages.get(action, f"Executing: {action}")
        
        # Check if action needs confirmation
        needs_confirmation = action in [
            "close_all", "emergency_stop", "clear_logs", "restart_bot"
        ]
        
        if needs_confirmation:
            self.pending_confirmations[context.user_id] = {
                "action": action,
                "params": params,
                "timestamp": datetime.utcnow()
            }
            
            return CallbackResult(
                success=True,
                message=message,
                new_keyboard=[
                    [
                        {"text": "✅ Confirm", "callback_data": f"confirm:{action}"},
                        {"text": "❌ Cancel", "callback_data": "cancel"}
                    ]
                ]
            )
        
        return CallbackResult(
            success=True,
            message=message,
            data={"action": action, "params": params}
        )
    
    async def _handle_wizard(self, context: CallbackContext) -> CallbackResult:
        """Handle wizard initiation"""
        wizard_name = context.callback_data.action
        
        wizard_prompts = {
            "lot_size": "📊 Enter lot size (e.g., 0.01, 0.1, 1.0):",
            "risk_percent": "📉 Enter risk percentage (e.g., 1, 2, 5):",
            "default_sl": "🛑 Enter default stop loss in pips:",
            "default_tp": "🎯 Enter default take profit in pips:",
            "modify_sl": "🎯 Enter new stop loss price:",
            "modify_tp": "🎯 Enter new take profit price:",
            "enable_plugin": "▶️ Select plugin to enable:",
            "disable_plugin": "⏹️ Select plugin to disable:",
            "plugin_config": "⚙️ Select plugin to configure:",
            "max_risk": "📉 Enter maximum risk percentage:",
            "max_trades": "🔢 Enter maximum concurrent trades:",
            "daily_loss_limit": "🛑 Enter daily loss limit in $:",
            "max_drawdown": "📉 Enter maximum drawdown percentage:"
        }
        
        prompt = wizard_prompts.get(wizard_name, f"Enter value for {wizard_name}:")
        
        return CallbackResult(
            success=True,
            message=prompt,
            data={"wizard": wizard_name, "awaiting_input": True}
        )
    
    async def _handle_position(self, context: CallbackContext) -> CallbackResult:
        """Handle position management"""
        action = context.callback_data.action
        ticket = context.callback_data.params[0] if context.callback_data.params else None
        
        if not ticket:
            return CallbackResult(
                success=False,
                message="Position ticket not specified",
                show_alert=True
            )
        
        action_messages = {
            "details": f"📊 Loading details for position #{ticket}...",
            "modify": f"🎯 Modify position #{ticket}",
            "book25": f"💵 Booking 25% profit on position #{ticket}...",
            "book50": f"💵 Booking 50% profit on position #{ticket}...",
            "breakeven": f"⚖️ Moving position #{ticket} to breakeven...",
            "close": f"🔴 Closing position #{ticket}..."
        }
        
        message = action_messages.get(action, f"Position action: {action}")
        
        # Close action needs confirmation
        if action == "close":
            self.pending_confirmations[context.user_id] = {
                "action": f"close_position:{ticket}",
                "params": [ticket],
                "timestamp": datetime.utcnow()
            }
            
            return CallbackResult(
                success=True,
                message=f"⚠️ Close position #{ticket}?",
                new_keyboard=[
                    [
                        {"text": "✅ Confirm", "callback_data": f"confirm:close_position:{ticket}"},
                        {"text": "❌ Cancel", "callback_data": "cancel"}
                    ]
                ]
            )
        
        return CallbackResult(
            success=True,
            message=message,
            data={"position_action": action, "ticket": ticket}
        )
    
    async def _handle_plugin(self, context: CallbackContext) -> CallbackResult:
        """Handle plugin management"""
        action = context.callback_data.action
        plugin_name = context.callback_data.params[0] if context.callback_data.params else None
        
        if not plugin_name:
            return CallbackResult(
                success=False,
                message="Plugin name not specified",
                show_alert=True
            )
        
        action_messages = {
            "stats": f"📊 Loading stats for {plugin_name}...",
            "config": f"⚙️ Loading config for {plugin_name}...",
            "enable": f"▶️ Enabling {plugin_name}...",
            "disable": f"⏹️ Disabling {plugin_name}..."
        }
        
        message = action_messages.get(action, f"Plugin action: {action}")
        
        return CallbackResult(
            success=True,
            message=message,
            data={"plugin_action": action, "plugin_name": plugin_name}
        )
    
    async def _handle_confirm(self, context: CallbackContext) -> CallbackResult:
        """Handle confirmation"""
        action = context.callback_data.action
        params = context.callback_data.params
        
        # Check if there's a pending confirmation
        pending = self.pending_confirmations.get(context.user_id)
        
        if pending:
            del self.pending_confirmations[context.user_id]
        
        return CallbackResult(
            success=True,
            message=f"✅ Confirmed: {action}",
            data={"confirmed_action": action, "params": params}
        )
    
    async def _handle_cancel(self, context: CallbackContext) -> CallbackResult:
        """Handle cancellation"""
        # Clear any pending confirmation
        if context.user_id in self.pending_confirmations:
            del self.pending_confirmations[context.user_id]
        
        return CallbackResult(
            success=True,
            message="❌ Action cancelled",
            redirect_menu="main"
        )
    
    async def _handle_page(self, context: CallbackContext) -> CallbackResult:
        """Handle pagination"""
        page_type = context.callback_data.action
        page_num = int(context.callback_data.params[0]) if context.callback_data.params else 1
        
        return CallbackResult(
            success=True,
            message=f"Loading page {page_num}...",
            data={"page_type": page_type, "page": page_num}
        )
    
    async def _handle_unknown(self, context: CallbackContext) -> CallbackResult:
        """Handle unknown callback"""
        return CallbackResult(
            success=False,
            message=f"Unknown action: {context.callback_data.raw_data}",
            show_alert=True
        )
    
    def register_handler(self, pattern: str, handler: CallbackHandler) -> None:
        """Register custom callback handler"""
        self.registry.register(pattern, handler)
    
    def register_pattern_handler(self, pattern: str, handler: CallbackHandler) -> None:
        """Register custom pattern handler"""
        self.registry.register_pattern(pattern, handler)
    
    def get_pending_confirmation(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get pending confirmation for user"""
        return self.pending_confirmations.get(user_id)
    
    def clear_pending_confirmation(self, user_id: int) -> bool:
        """Clear pending confirmation for user"""
        if user_id in self.pending_confirmations:
            del self.pending_confirmations[user_id]
            return True
        return False
