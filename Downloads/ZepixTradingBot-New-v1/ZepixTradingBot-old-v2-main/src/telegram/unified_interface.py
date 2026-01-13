"""
Unified Interface for Multi-Telegram System.

This module provides standardized menus and keyboard layouts:
- Main Menu (Reply Keyboard)
- Status Submenu (Inline Keyboard)
- Trades Menu (Inline Keyboard)
- Settings Menu (Inline Keyboard)
- Emergency Menu (Inline Keyboard)

Based on Document 18: TELEGRAM_SYSTEM_ARCHITECTURE.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class MenuType(Enum):
    """Menu type enumeration."""
    MAIN = "main"
    STATUS = "status"
    TRADES = "trades"
    SETTINGS = "settings"
    ANALYTICS = "analytics"
    ALERTS = "alerts"
    EMERGENCY = "emergency"
    PLUGINS = "plugins"


class ButtonType(Enum):
    """Button type enumeration."""
    REPLY = "reply"
    INLINE = "inline"


@dataclass
class KeyboardButton:
    """Keyboard button definition."""
    text: str
    callback_data: Optional[str] = None
    button_type: ButtonType = ButtonType.REPLY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "callback_data": self.callback_data,
            "button_type": self.button_type.value
        }


@dataclass
class KeyboardRow:
    """Row of keyboard buttons."""
    buttons: List[KeyboardButton] = field(default_factory=list)
    
    def add_button(self, button: KeyboardButton) -> None:
        """Add button to row."""
        self.buttons.append(button)
    
    def to_list(self) -> List[str]:
        """Convert to list of button texts (for reply keyboard)."""
        return [b.text for b in self.buttons]
    
    def to_inline_list(self) -> List[Dict[str, str]]:
        """Convert to list of inline button dicts."""
        return [
            {"text": b.text, "callback_data": b.callback_data or b.text}
            for b in self.buttons
        ]


@dataclass
class Menu:
    """Menu definition."""
    menu_type: MenuType
    title: str
    rows: List[KeyboardRow] = field(default_factory=list)
    is_inline: bool = False
    resize_keyboard: bool = True
    
    def add_row(self, row: KeyboardRow) -> None:
        """Add row to menu."""
        self.rows.append(row)
    
    def to_reply_markup(self) -> Dict[str, Any]:
        """Convert to reply markup format."""
        if self.is_inline:
            return {
                "inline_keyboard": [row.to_inline_list() for row in self.rows]
            }
        else:
            return {
                "keyboard": [row.to_list() for row in self.rows],
                "resize_keyboard": self.resize_keyboard
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "menu_type": self.menu_type.value,
            "title": self.title,
            "is_inline": self.is_inline,
            "rows": [[b.to_dict() for b in row.buttons] for row in self.rows]
        }


class MenuBuilder:
    """Builder for creating menus."""
    
    @staticmethod
    def create_main_menu() -> Menu:
        """Create main menu (Reply Keyboard)."""
        menu = Menu(
            menu_type=MenuType.MAIN,
            title="ZEPIX TRADING BOT v3.0",
            is_inline=False
        )
        
        row1 = KeyboardRow()
        row1.add_button(KeyboardButton(text="📊 Status"))
        row1.add_button(KeyboardButton(text="💰 Trades"))
        menu.add_row(row1)
        
        row2 = KeyboardRow()
        row2.add_button(KeyboardButton(text="⚙️ Settings"))
        row2.add_button(KeyboardButton(text="📈 Analytics"))
        menu.add_row(row2)
        
        row3 = KeyboardRow()
        row3.add_button(KeyboardButton(text="🔔 Alerts"))
        row3.add_button(KeyboardButton(text="🛑 Emergency"))
        menu.add_row(row3)
        
        return menu
    
    @staticmethod
    def create_status_menu(bot_status: str = "🟢 Active", 
                          uptime: str = "0d 0h",
                          plugins_active: int = 0,
                          plugins_total: int = 0,
                          open_trades: int = 0) -> Tuple[str, Menu]:
        """Create status submenu (Inline Keyboard)."""
        text = f"""Status Information:
Bot: {bot_status} | Uptime: {uptime}
Plugins: {plugins_active}/{plugins_total} Active
Open Trades: {open_trades}

───────────────────────"""
        
        menu = Menu(
            menu_type=MenuType.STATUS,
            title="Status",
            is_inline=True
        )
        
        row1 = KeyboardRow()
        row1.add_button(KeyboardButton(
            text="🔄 Refresh",
            callback_data="status_refresh",
            button_type=ButtonType.INLINE
        ))
        row1.add_button(KeyboardButton(
            text="📋 Details",
            callback_data="status_details",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row1)
        
        row2 = KeyboardRow()
        row2.add_button(KeyboardButton(
            text="🏠 Main Menu",
            callback_data="main_menu",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row2)
        
        return text, menu
    
    @staticmethod
    def create_trades_menu(trades: List[Dict[str, Any]], 
                          page: int = 1,
                          per_page: int = 5) -> Tuple[str, Menu]:
        """Create trades menu (Inline Keyboard)."""
        total_trades = len(trades)
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_trades)
        page_trades = trades[start_idx:end_idx]
        
        lines = [f"Open Positions ({total_trades}):\n"]
        
        for i, trade in enumerate(page_trades, start=start_idx + 1):
            symbol = trade.get("symbol", "UNKNOWN")
            direction = trade.get("direction", "?")
            lot_size = trade.get("lot_size", 0)
            profit = trade.get("profit", 0)
            plugin = trade.get("plugin", "unknown")
            age = trade.get("age", "0m")
            
            profit_str = f"+${profit:.2f}" if profit >= 0 else f"-${abs(profit):.2f}"
            lines.append(f"{i}️⃣ {symbol} {direction} {lot_size} | {profit_str}")
            lines.append(f"   Plugin: {plugin} | Age: {age}")
        
        text = "\n".join(lines) + "\n\n───────────────────────"
        
        menu = Menu(
            menu_type=MenuType.TRADES,
            title="Trades",
            is_inline=True
        )
        
        nav_row = KeyboardRow()
        if page > 1:
            nav_row.add_button(KeyboardButton(
                text="◀️ Prev Page",
                callback_data=f"trades_page_{page - 1}",
                button_type=ButtonType.INLINE
            ))
        if end_idx < total_trades:
            nav_row.add_button(KeyboardButton(
                text="▶️ Next Page",
                callback_data=f"trades_page_{page + 1}",
                button_type=ButtonType.INLINE
            ))
        if nav_row.buttons:
            menu.add_row(nav_row)
        
        home_row = KeyboardRow()
        home_row.add_button(KeyboardButton(
            text="🏠 Main Menu",
            callback_data="main_menu",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(home_row)
        
        return text, menu
    
    @staticmethod
    def create_trade_actions_menu(trade_id: int) -> Menu:
        """Create trade actions menu."""
        menu = Menu(
            menu_type=MenuType.TRADES,
            title="Trade Actions",
            is_inline=True
        )
        
        row1 = KeyboardRow()
        row1.add_button(KeyboardButton(
            text="Close",
            callback_data=f"close_trade_{trade_id}",
            button_type=ButtonType.INLINE
        ))
        row1.add_button(KeyboardButton(
            text="Modify",
            callback_data=f"modify_trade_{trade_id}",
            button_type=ButtonType.INLINE
        ))
        row1.add_button(KeyboardButton(
            text="Book Profit",
            callback_data=f"profit_trade_{trade_id}_25",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row1)
        
        return menu
    
    @staticmethod
    def create_settings_menu(max_lot: float = 1.0,
                            daily_loss_limit: float = 500.0,
                            risk_per_trade: float = 1.5) -> Tuple[str, Menu]:
        """Create settings menu (Inline Keyboard)."""
        text = f"""⚙️ Bot Settings:

Current Configuration:
• Max Lot Size: {max_lot}
• Daily Loss Limit: ${daily_loss_limit:.0f}
• Risk per Trade: {risk_per_trade}%

───────────────────────"""
        
        menu = Menu(
            menu_type=MenuType.SETTINGS,
            title="Settings",
            is_inline=True
        )
        
        row1 = KeyboardRow()
        row1.add_button(KeyboardButton(
            text="🔌 Plugins",
            callback_data="settings_plugins",
            button_type=ButtonType.INLINE
        ))
        row1.add_button(KeyboardButton(
            text="⚡ Quick Settings",
            callback_data="settings_quick",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row1)
        
        row2 = KeyboardRow()
        row2.add_button(KeyboardButton(
            text="📝 Edit Config",
            callback_data="settings_edit",
            button_type=ButtonType.INLINE
        ))
        row2.add_button(KeyboardButton(
            text="🏠 Main Menu",
            callback_data="main_menu",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row2)
        
        return text, menu
    
    @staticmethod
    def create_emergency_menu() -> Tuple[str, Menu]:
        """Create emergency menu (Inline Keyboard)."""
        text = """🛑 EMERGENCY CONTROLS

⚠️ WARNING: These actions are immediate!

───────────────────────"""
        
        menu = Menu(
            menu_type=MenuType.EMERGENCY,
            title="Emergency",
            is_inline=True
        )
        
        row1 = KeyboardRow()
        row1.add_button(KeyboardButton(
            text="🔴 CLOSE ALL TRADES",
            callback_data="emergency_close_all",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row1)
        
        row2 = KeyboardRow()
        row2.add_button(KeyboardButton(
            text="⏸️ PAUSE BOT",
            callback_data="emergency_pause",
            button_type=ButtonType.INLINE
        ))
        row2.add_button(KeyboardButton(
            text="▶️ RESUME BOT",
            callback_data="emergency_resume",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row2)
        
        row3 = KeyboardRow()
        row3.add_button(KeyboardButton(
            text="🔄 RESTART PLUGINS",
            callback_data="emergency_restart_plugins",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row3)
        
        row4 = KeyboardRow()
        row4.add_button(KeyboardButton(
            text="❌ Cancel",
            callback_data="emergency_cancel",
            button_type=ButtonType.INLINE
        ))
        row4.add_button(KeyboardButton(
            text="🏠 Main Menu",
            callback_data="main_menu",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row4)
        
        return text, menu
    
    @staticmethod
    def create_confirmation_menu(action: str, 
                                 details: str,
                                 confirm_callback: str,
                                 cancel_callback: str = "cancel") -> Tuple[str, Menu]:
        """Create confirmation menu."""
        text = f"""⚠️ {action}

{details}

───────────────────────"""
        
        menu = Menu(
            menu_type=MenuType.EMERGENCY,
            title="Confirmation",
            is_inline=True
        )
        
        row = KeyboardRow()
        row.add_button(KeyboardButton(
            text="✅ YES, CONFIRM",
            callback_data=confirm_callback,
            button_type=ButtonType.INLINE
        ))
        row.add_button(KeyboardButton(
            text="❌ CANCEL",
            callback_data=cancel_callback,
            button_type=ButtonType.INLINE
        ))
        menu.add_row(row)
        
        return text, menu
    
    @staticmethod
    def create_plugins_menu(plugins: List[Dict[str, Any]]) -> Tuple[str, Menu]:
        """Create plugins menu."""
        lines = ["🔌 Plugin Status:\n"]
        
        for plugin in plugins:
            name = plugin.get("name", "Unknown")
            enabled = plugin.get("enabled", False)
            status_icon = "🟢" if enabled else "🔴"
            lines.append(f"{status_icon} {name}")
        
        text = "\n".join(lines) + "\n\n───────────────────────"
        
        menu = Menu(
            menu_type=MenuType.PLUGINS,
            title="Plugins",
            is_inline=True
        )
        
        for plugin in plugins:
            plugin_id = plugin.get("id", "unknown")
            enabled = plugin.get("enabled", False)
            action = "disable" if enabled else "enable"
            
            row = KeyboardRow()
            row.add_button(KeyboardButton(
                text=f"{'🔴 Disable' if enabled else '🟢 Enable'} {plugin.get('name', plugin_id)}",
                callback_data=f"plugin_{action}_{plugin_id}",
                button_type=ButtonType.INLINE
            ))
            menu.add_row(row)
        
        home_row = KeyboardRow()
        home_row.add_button(KeyboardButton(
            text="🏠 Main Menu",
            callback_data="main_menu",
            button_type=ButtonType.INLINE
        ))
        menu.add_row(home_row)
        
        return text, menu


class UnifiedInterface:
    """
    Unified interface for all Telegram menus.
    
    Provides standardized menu creation and navigation.
    """
    
    def __init__(self):
        """Initialize unified interface."""
        self.builder = MenuBuilder()
        self.current_menu: Dict[str, MenuType] = {}
    
    def get_main_menu(self) -> Menu:
        """Get main menu."""
        return self.builder.create_main_menu()
    
    def get_status_menu(self, **kwargs) -> Tuple[str, Menu]:
        """Get status menu."""
        return self.builder.create_status_menu(**kwargs)
    
    def get_trades_menu(self, trades: List[Dict[str, Any]], 
                       page: int = 1) -> Tuple[str, Menu]:
        """Get trades menu."""
        return self.builder.create_trades_menu(trades, page)
    
    def get_settings_menu(self, **kwargs) -> Tuple[str, Menu]:
        """Get settings menu."""
        return self.builder.create_settings_menu(**kwargs)
    
    def get_emergency_menu(self) -> Tuple[str, Menu]:
        """Get emergency menu."""
        return self.builder.create_emergency_menu()
    
    def get_confirmation_menu(self, action: str, details: str,
                             confirm_callback: str) -> Tuple[str, Menu]:
        """Get confirmation menu."""
        return self.builder.create_confirmation_menu(
            action, details, confirm_callback
        )
    
    def get_plugins_menu(self, plugins: List[Dict[str, Any]]) -> Tuple[str, Menu]:
        """Get plugins menu."""
        return self.builder.create_plugins_menu(plugins)
    
    def set_user_menu(self, user_id: str, menu_type: MenuType) -> None:
        """Set current menu for user."""
        self.current_menu[user_id] = menu_type
    
    def get_user_menu(self, user_id: str) -> Optional[MenuType]:
        """Get current menu for user."""
        return self.current_menu.get(user_id)
    
    def clear_user_menu(self, user_id: str) -> None:
        """Clear current menu for user."""
        self.current_menu.pop(user_id, None)


def create_unified_interface() -> UnifiedInterface:
    """Factory function to create Unified Interface."""
    return UnifiedInterface()


# =============================================================================
# DOCUMENT 20 ADDITIONS: Unified Interface Manager
# =============================================================================

class InterfaceState(Enum):
    """Interface state for unified management."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class BotType(Enum):
    """Bot types for header variants."""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"


@dataclass
class HeaderMetrics:
    """Metrics displayed in live header."""
    open_trades: int = 0
    daily_pnl: float = 0.0
    win_rate: float = 0.0
    active_plugins: int = 0
    total_plugins: int = 0
    alerts_today: int = 0
    entries_today: int = 0
    exits_today: int = 0
    reports_sent: int = 0
    mt5_connected: bool = True
    bot_running: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "open_trades": self.open_trades,
            "daily_pnl": self.daily_pnl,
            "win_rate": self.win_rate,
            "active_plugins": self.active_plugins,
            "total_plugins": self.total_plugins,
            "alerts_today": self.alerts_today,
            "entries_today": self.entries_today,
            "exits_today": self.exits_today,
            "reports_sent": self.reports_sent,
            "mt5_connected": self.mt5_connected,
            "bot_running": self.bot_running
        }


@dataclass
class BotInterface:
    """Interface for a single bot in unified system."""
    bot_type: BotType
    chat_id: int
    menu_message_id: Optional[int] = None
    current_menu: MenuType = MenuType.MAIN
    state: InterfaceState = InterfaceState.INITIALIZING
    last_activity: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bot_type": self.bot_type.value,
            "chat_id": self.chat_id,
            "menu_message_id": self.menu_message_id,
            "current_menu": self.current_menu.value,
            "state": self.state.value,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }


class UnifiedInterfaceManager:
    """
    Unified Interface Manager (Document 20)
    
    Manages consistent interface across all 3 Telegram bots.
    Implements zero-typing interface with button-based navigation.
    
    Features:
    - Same menu system for all bots
    - Live sticky headers per bot
    - Unified callback handling
    - Message editing (sticky interface)
    """
    
    def __init__(
        self,
        controller_chat_id: Optional[int] = None,
        notification_chat_id: Optional[int] = None,
        analytics_chat_id: Optional[int] = None
    ):
        """Initialize unified interface manager."""
        self.interfaces: Dict[BotType, BotInterface] = {}
        self.builder = MenuBuilder()
        self.shared_metrics = HeaderMetrics()
        self.state = InterfaceState.INITIALIZING
        
        # Initialize interfaces if chat IDs provided
        if controller_chat_id:
            self.interfaces[BotType.CONTROLLER] = BotInterface(
                bot_type=BotType.CONTROLLER,
                chat_id=controller_chat_id
            )
        if notification_chat_id:
            self.interfaces[BotType.NOTIFICATION] = BotInterface(
                bot_type=BotType.NOTIFICATION,
                chat_id=notification_chat_id
            )
        if analytics_chat_id:
            self.interfaces[BotType.ANALYTICS] = BotInterface(
                bot_type=BotType.ANALYTICS,
                chat_id=analytics_chat_id
            )
        
        logger.info("UnifiedInterfaceManager initialized")
    
    def add_bot(self, bot_type: BotType, chat_id: int) -> BotInterface:
        """Add a bot to the unified interface."""
        interface = BotInterface(
            bot_type=bot_type,
            chat_id=chat_id
        )
        self.interfaces[bot_type] = interface
        logger.info(f"Added bot to unified interface: {bot_type.value}")
        return interface
    
    def get_interface(self, bot_type: BotType) -> Optional[BotInterface]:
        """Get interface for bot."""
        return self.interfaces.get(bot_type)
    
    def update_metrics(self, metrics: HeaderMetrics) -> None:
        """Update shared metrics for all headers."""
        self.shared_metrics = metrics
    
    def update_metric(self, key: str, value: Any) -> None:
        """Update single metric for all headers."""
        if hasattr(self.shared_metrics, key):
            setattr(self.shared_metrics, key, value)
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all interfaces."""
        return {
            "state": self.state.value,
            "interfaces": {
                bot_type.value: interface.to_dict()
                for bot_type, interface in self.interfaces.items()
            },
            "metrics": self.shared_metrics.to_dict()
        }
    
    def list_bots(self) -> List[str]:
        """List all registered bots."""
        return [bt.value for bt in self.interfaces.keys()]


class MessageEditor:
    """
    Message Editor (Document 20)
    
    Handles message editing to reduce clutter (sticky interface behavior).
    Updates existing messages instead of sending new ones.
    """
    
    def __init__(self):
        """Initialize message editor."""
        self.tracked_messages: Dict[str, int] = {}
    
    def track_message(self, key: str, message_id: int) -> None:
        """Track a message for future editing."""
        self.tracked_messages[key] = message_id
    
    def get_message_id(self, key: str) -> Optional[int]:
        """Get tracked message ID."""
        return self.tracked_messages.get(key)
    
    def untrack_message(self, key: str) -> bool:
        """Stop tracking a message."""
        if key in self.tracked_messages:
            del self.tracked_messages[key]
            return True
        return False
    
    def should_edit(self, key: str) -> bool:
        """Check if message should be edited vs sent new."""
        return key in self.tracked_messages
    
    def get_tracked_count(self) -> int:
        """Get count of tracked messages."""
        return len(self.tracked_messages)
    
    def clear_all(self) -> None:
        """Clear all tracked messages."""
        self.tracked_messages.clear()


class NavigationManager:
    """
    Navigation Manager (Document 20)
    
    Manages navigation state and history for seamless transitions.
    Supports Back/Home buttons and breadcrumb navigation.
    """
    
    def __init__(self, max_history: int = 10):
        """Initialize navigation manager."""
        self.history: Dict[int, List[MenuType]] = {}
        self.max_history = max_history
    
    def push(self, user_id: int, menu: MenuType) -> None:
        """Push menu to history."""
        if user_id not in self.history:
            self.history[user_id] = []
        
        self.history[user_id].append(menu)
        
        # Limit history size
        if len(self.history[user_id]) > self.max_history:
            self.history[user_id] = self.history[user_id][-self.max_history:]
    
    def pop(self, user_id: int) -> Optional[MenuType]:
        """Pop last menu from history."""
        if user_id in self.history and self.history[user_id]:
            return self.history[user_id].pop()
        return None
    
    def peek(self, user_id: int) -> Optional[MenuType]:
        """Peek at last menu without removing."""
        if user_id in self.history and self.history[user_id]:
            return self.history[user_id][-1]
        return None
    
    def get_previous(self, user_id: int) -> MenuType:
        """Get previous menu (for back button)."""
        if user_id in self.history and len(self.history[user_id]) > 1:
            return self.history[user_id][-2]
        return MenuType.MAIN
    
    def clear(self, user_id: int) -> None:
        """Clear history for user."""
        if user_id in self.history:
            del self.history[user_id]
    
    def get_breadcrumb(self, user_id: int) -> List[str]:
        """Get navigation breadcrumb."""
        if user_id not in self.history:
            return ["Main"]
        return [m.value.title() for m in self.history[user_id]]


def create_unified_interface_manager(
    controller_chat_id: Optional[int] = None,
    notification_chat_id: Optional[int] = None,
    analytics_chat_id: Optional[int] = None
) -> UnifiedInterfaceManager:
    """Factory function to create Unified Interface Manager."""
    return UnifiedInterfaceManager(
        controller_chat_id=controller_chat_id,
        notification_chat_id=notification_chat_id,
        analytics_chat_id=analytics_chat_id
    )
