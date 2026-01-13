"""
Menu Builder - Visual Menu Layouts for Telegram Bots

Document 20: Telegram Unified Interface Addendum
Creates consistent menu layouts for all 3 bots with zero-typing interface.

Features:
- Main Menu with all primary actions
- Trading Menu with position management
- Settings Menu with configuration options
- Navigation buttons (Back, Home)
- Inline keyboards for confirmations
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
import logging


class MenuType(Enum):
    """Menu types for navigation"""
    MAIN = "main"
    TRADING = "trading"
    POSITIONS = "positions"
    SETTINGS = "settings"
    PLUGINS = "plugins"
    RISK = "risk"
    ANALYTICS = "analytics"
    HELP = "help"
    ADMIN = "admin"


class ButtonType(Enum):
    """Button types for styling"""
    PRIMARY = "primary"      # Main action buttons
    SECONDARY = "secondary"  # Secondary actions
    DANGER = "danger"        # Destructive actions (close, stop)
    SUCCESS = "success"      # Positive actions (profit, start)
    INFO = "info"            # Information buttons
    NAVIGATION = "navigation"  # Back, Home buttons


@dataclass
class MenuButton:
    """Single menu button"""
    text: str
    callback_data: str
    button_type: ButtonType = ButtonType.PRIMARY
    emoji: str = ""
    row: int = 0  # Row position (0-indexed)
    
    @property
    def display_text(self) -> str:
        """Get button text with emoji"""
        if self.emoji:
            return f"{self.emoji} {self.text}"
        return self.text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Telegram API"""
        return {
            "text": self.display_text,
            "callback_data": self.callback_data
        }


@dataclass
class MenuLayout:
    """Menu layout with buttons organized in rows"""
    menu_type: MenuType
    title: str
    description: str = ""
    buttons: List[MenuButton] = field(default_factory=list)
    show_back: bool = True
    show_home: bool = True
    parent_menu: Optional[MenuType] = None
    
    def add_button(self, button: MenuButton) -> None:
        """Add button to menu"""
        self.buttons.append(button)
    
    def get_rows(self) -> List[List[MenuButton]]:
        """Get buttons organized by rows"""
        rows: Dict[int, List[MenuButton]] = {}
        
        for button in self.buttons:
            if button.row not in rows:
                rows[button.row] = []
            rows[button.row].append(button)
        
        # Add navigation row
        nav_row = max(rows.keys()) + 1 if rows else 0
        nav_buttons = []
        
        if self.show_back and self.parent_menu:
            nav_buttons.append(MenuButton(
                text="Back",
                callback_data=f"menu:{self.parent_menu.value}",
                button_type=ButtonType.NAVIGATION,
                emoji="◀️",
                row=nav_row
            ))
        
        if self.show_home and self.menu_type != MenuType.MAIN:
            nav_buttons.append(MenuButton(
                text="Home",
                callback_data="menu:main",
                button_type=ButtonType.NAVIGATION,
                emoji="🏠",
                row=nav_row
            ))
        
        if nav_buttons:
            rows[nav_row] = nav_buttons
        
        return [rows[i] for i in sorted(rows.keys())]
    
    def to_inline_keyboard(self) -> List[List[Dict[str, str]]]:
        """Convert to Telegram InlineKeyboardMarkup format"""
        return [
            [button.to_dict() for button in row]
            for row in self.get_rows()
        ]
    
    def to_reply_keyboard(self) -> List[List[str]]:
        """Convert to Telegram ReplyKeyboardMarkup format"""
        return [
            [button.display_text for button in row]
            for row in self.get_rows()
        ]


class MenuBuilder:
    """
    Menu Builder
    
    Creates consistent menu layouts for all 3 Telegram bots.
    Implements zero-typing interface with button-based navigation.
    """
    
    def __init__(self):
        self.menus: Dict[MenuType, MenuLayout] = {}
        self.logger = logging.getLogger(__name__)
        self._build_default_menus()
    
    def _build_default_menus(self) -> None:
        """Build all default menus"""
        self._build_main_menu()
        self._build_trading_menu()
        self._build_positions_menu()
        self._build_settings_menu()
        self._build_plugins_menu()
        self._build_risk_menu()
        self._build_analytics_menu()
        self._build_help_menu()
        self._build_admin_menu()
    
    def _build_main_menu(self) -> None:
        """Build main menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.MAIN,
            title="🤖 ZEPIX TRADING BOT",
            description="Main Control Panel",
            show_back=False,
            show_home=False
        )
        
        # Row 0: Status and Trades
        menu.add_button(MenuButton(
            text="Status",
            callback_data="action:status",
            emoji="📊",
            row=0
        ))
        menu.add_button(MenuButton(
            text="Trades",
            callback_data="menu:trading",
            emoji="💰",
            row=0
        ))
        
        # Row 1: Plugins and Settings
        menu.add_button(MenuButton(
            text="Plugins",
            callback_data="menu:plugins",
            emoji="🔌",
            row=1
        ))
        menu.add_button(MenuButton(
            text="Settings",
            callback_data="menu:settings",
            emoji="⚙️",
            row=1
        ))
        
        # Row 2: Analytics and Risk
        menu.add_button(MenuButton(
            text="Analytics",
            callback_data="menu:analytics",
            emoji="📈",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Risk",
            callback_data="menu:risk",
            emoji="🛡️",
            row=2
        ))
        
        # Row 3: Help and Admin
        menu.add_button(MenuButton(
            text="Help",
            callback_data="menu:help",
            emoji="❓",
            row=3
        ))
        menu.add_button(MenuButton(
            text="Admin",
            callback_data="menu:admin",
            emoji="👤",
            row=3
        ))
        
        self.menus[MenuType.MAIN] = menu
    
    def _build_trading_menu(self) -> None:
        """Build trading menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.TRADING,
            title="💰 TRADING MENU",
            description="Manage your trades",
            parent_menu=MenuType.MAIN
        )
        
        # Row 0: Open Positions
        menu.add_button(MenuButton(
            text="Open Positions",
            callback_data="menu:positions",
            emoji="📋",
            row=0
        ))
        menu.add_button(MenuButton(
            text="Trade History",
            callback_data="action:history",
            emoji="📜",
            row=0
        ))
        
        # Row 1: Quick Actions
        menu.add_button(MenuButton(
            text="Close All",
            callback_data="action:close_all",
            button_type=ButtonType.DANGER,
            emoji="🔴",
            row=1
        ))
        menu.add_button(MenuButton(
            text="Book Profits",
            callback_data="action:book_profits",
            button_type=ButtonType.SUCCESS,
            emoji="💵",
            row=1
        ))
        
        # Row 2: Position Management
        menu.add_button(MenuButton(
            text="Modify SL",
            callback_data="wizard:modify_sl",
            emoji="🎯",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Modify TP",
            callback_data="wizard:modify_tp",
            emoji="🎯",
            row=2
        ))
        
        # Row 3: Breakeven
        menu.add_button(MenuButton(
            text="Move to Breakeven",
            callback_data="action:breakeven",
            emoji="⚖️",
            row=3
        ))
        
        self.menus[MenuType.TRADING] = menu
    
    def _build_positions_menu(self) -> None:
        """Build positions menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.POSITIONS,
            title="📋 OPEN POSITIONS",
            description="Manage individual positions",
            parent_menu=MenuType.TRADING
        )
        
        # Dynamic positions will be added at runtime
        # Row 0: Refresh
        menu.add_button(MenuButton(
            text="Refresh",
            callback_data="action:refresh_positions",
            emoji="🔄",
            row=0
        ))
        
        self.menus[MenuType.POSITIONS] = menu
    
    def _build_settings_menu(self) -> None:
        """Build settings menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.SETTINGS,
            title="⚙️ SETTINGS",
            description="Configure bot settings",
            parent_menu=MenuType.MAIN
        )
        
        # Row 0: Trading Settings
        menu.add_button(MenuButton(
            text="Lot Size",
            callback_data="wizard:lot_size",
            emoji="📊",
            row=0
        ))
        menu.add_button(MenuButton(
            text="Risk %",
            callback_data="wizard:risk_percent",
            emoji="📉",
            row=0
        ))
        
        # Row 1: SL/TP Settings
        menu.add_button(MenuButton(
            text="Default SL",
            callback_data="wizard:default_sl",
            emoji="🛑",
            row=1
        ))
        menu.add_button(MenuButton(
            text="Default TP",
            callback_data="wizard:default_tp",
            emoji="🎯",
            row=1
        ))
        
        # Row 2: Notification Settings
        menu.add_button(MenuButton(
            text="Notifications",
            callback_data="action:notification_settings",
            emoji="🔔",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Voice Alerts",
            callback_data="action:voice_settings",
            emoji="🔊",
            row=2
        ))
        
        # Row 3: Symbol Settings
        menu.add_button(MenuButton(
            text="Symbols",
            callback_data="action:symbol_settings",
            emoji="💱",
            row=3
        ))
        menu.add_button(MenuButton(
            text="Sessions",
            callback_data="action:session_settings",
            emoji="🕐",
            row=3
        ))
        
        self.menus[MenuType.SETTINGS] = menu
    
    def _build_plugins_menu(self) -> None:
        """Build plugins menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.PLUGINS,
            title="🔌 PLUGINS",
            description="Manage trading plugins",
            parent_menu=MenuType.MAIN
        )
        
        # Row 0: Plugin Status
        menu.add_button(MenuButton(
            text="Active Plugins",
            callback_data="action:active_plugins",
            emoji="✅",
            row=0
        ))
        menu.add_button(MenuButton(
            text="All Plugins",
            callback_data="action:all_plugins",
            emoji="📋",
            row=0
        ))
        
        # Row 1: Plugin Actions
        menu.add_button(MenuButton(
            text="Enable Plugin",
            callback_data="wizard:enable_plugin",
            button_type=ButtonType.SUCCESS,
            emoji="▶️",
            row=1
        ))
        menu.add_button(MenuButton(
            text="Disable Plugin",
            callback_data="wizard:disable_plugin",
            button_type=ButtonType.DANGER,
            emoji="⏹️",
            row=1
        ))
        
        # Row 2: Plugin Config
        menu.add_button(MenuButton(
            text="Plugin Config",
            callback_data="wizard:plugin_config",
            emoji="⚙️",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Reload Plugins",
            callback_data="action:reload_plugins",
            emoji="🔄",
            row=2
        ))
        
        self.menus[MenuType.PLUGINS] = menu
    
    def _build_risk_menu(self) -> None:
        """Build risk menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.RISK,
            title="🛡️ RISK MANAGEMENT",
            description="Configure risk settings",
            parent_menu=MenuType.MAIN
        )
        
        # Row 0: Risk Status
        menu.add_button(MenuButton(
            text="Risk Status",
            callback_data="action:risk_status",
            emoji="📊",
            row=0
        ))
        menu.add_button(MenuButton(
            text="Daily Limits",
            callback_data="action:daily_limits",
            emoji="📅",
            row=0
        ))
        
        # Row 1: Risk Settings
        menu.add_button(MenuButton(
            text="Max Risk %",
            callback_data="wizard:max_risk",
            emoji="📉",
            row=1
        ))
        menu.add_button(MenuButton(
            text="Max Trades",
            callback_data="wizard:max_trades",
            emoji="🔢",
            row=1
        ))
        
        # Row 2: Loss Limits
        menu.add_button(MenuButton(
            text="Daily Loss Limit",
            callback_data="wizard:daily_loss_limit",
            emoji="🛑",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Max Drawdown",
            callback_data="wizard:max_drawdown",
            emoji="📉",
            row=2
        ))
        
        # Row 3: Emergency
        menu.add_button(MenuButton(
            text="Emergency Stop",
            callback_data="action:emergency_stop",
            button_type=ButtonType.DANGER,
            emoji="🚨",
            row=3
        ))
        
        self.menus[MenuType.RISK] = menu
    
    def _build_analytics_menu(self) -> None:
        """Build analytics menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.ANALYTICS,
            title="📈 ANALYTICS",
            description="View trading analytics",
            parent_menu=MenuType.MAIN
        )
        
        # Row 0: Reports
        menu.add_button(MenuButton(
            text="Daily Report",
            callback_data="action:daily_report",
            emoji="📊",
            row=0
        ))
        menu.add_button(MenuButton(
            text="Weekly Report",
            callback_data="action:weekly_report",
            emoji="📈",
            row=0
        ))
        
        # Row 1: Performance
        menu.add_button(MenuButton(
            text="Win Rate",
            callback_data="action:win_rate",
            emoji="🎯",
            row=1
        ))
        menu.add_button(MenuButton(
            text="P&L Chart",
            callback_data="action:pnl_chart",
            emoji="📉",
            row=1
        ))
        
        # Row 2: Plugin Analytics
        menu.add_button(MenuButton(
            text="Plugin Stats",
            callback_data="action:plugin_stats",
            emoji="🔌",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Symbol Stats",
            callback_data="action:symbol_stats",
            emoji="💱",
            row=2
        ))
        
        self.menus[MenuType.ANALYTICS] = menu
    
    def _build_help_menu(self) -> None:
        """Build help menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.HELP,
            title="❓ HELP",
            description="Get help and support",
            parent_menu=MenuType.MAIN
        )
        
        # Row 0: Documentation
        menu.add_button(MenuButton(
            text="Quick Start",
            callback_data="action:quick_start",
            emoji="🚀",
            row=0
        ))
        menu.add_button(MenuButton(
            text="Commands",
            callback_data="action:commands",
            emoji="📋",
            row=0
        ))
        
        # Row 1: Support
        menu.add_button(MenuButton(
            text="FAQ",
            callback_data="action:faq",
            emoji="❓",
            row=1
        ))
        menu.add_button(MenuButton(
            text="Support",
            callback_data="action:support",
            emoji="💬",
            row=1
        ))
        
        # Row 2: About
        menu.add_button(MenuButton(
            text="About",
            callback_data="action:about",
            emoji="ℹ️",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Version",
            callback_data="action:version",
            emoji="🏷️",
            row=2
        ))
        
        self.menus[MenuType.HELP] = menu
    
    def _build_admin_menu(self) -> None:
        """Build admin menu layout"""
        menu = MenuLayout(
            menu_type=MenuType.ADMIN,
            title="👤 ADMIN",
            description="Administrative functions",
            parent_menu=MenuType.MAIN
        )
        
        # Row 0: Bot Control
        menu.add_button(MenuButton(
            text="Start Bot",
            callback_data="action:start_bot",
            button_type=ButtonType.SUCCESS,
            emoji="▶️",
            row=0
        ))
        menu.add_button(MenuButton(
            text="Stop Bot",
            callback_data="action:stop_bot",
            button_type=ButtonType.DANGER,
            emoji="⏹️",
            row=0
        ))
        
        # Row 1: System
        menu.add_button(MenuButton(
            text="System Status",
            callback_data="action:system_status",
            emoji="🖥️",
            row=1
        ))
        menu.add_button(MenuButton(
            text="MT5 Status",
            callback_data="action:mt5_status",
            emoji="📡",
            row=1
        ))
        
        # Row 2: Logs
        menu.add_button(MenuButton(
            text="View Logs",
            callback_data="action:view_logs",
            emoji="📜",
            row=2
        ))
        menu.add_button(MenuButton(
            text="Clear Logs",
            callback_data="action:clear_logs",
            button_type=ButtonType.DANGER,
            emoji="🗑️",
            row=2
        ))
        
        # Row 3: Maintenance
        menu.add_button(MenuButton(
            text="Restart Bot",
            callback_data="action:restart_bot",
            button_type=ButtonType.DANGER,
            emoji="🔄",
            row=3
        ))
        menu.add_button(MenuButton(
            text="Backup",
            callback_data="action:backup",
            emoji="💾",
            row=3
        ))
        
        self.menus[MenuType.ADMIN] = menu
    
    def get_menu(self, menu_type: MenuType) -> MenuLayout:
        """Get menu by type"""
        return self.menus.get(menu_type, self.menus[MenuType.MAIN])
    
    def get_main_menu(self) -> MenuLayout:
        """Get main menu"""
        return self.menus[MenuType.MAIN]
    
    def get_inline_keyboard(self, menu_type: MenuType) -> List[List[Dict[str, str]]]:
        """Get inline keyboard for menu"""
        menu = self.get_menu(menu_type)
        return menu.to_inline_keyboard()
    
    def get_reply_keyboard(self, menu_type: MenuType) -> List[List[str]]:
        """Get reply keyboard for menu"""
        menu = self.get_menu(menu_type)
        return menu.to_reply_keyboard()
    
    def create_confirmation_keyboard(
        self,
        action: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel"
    ) -> List[List[Dict[str, str]]]:
        """Create confirmation inline keyboard"""
        return [
            [
                {"text": f"✅ {confirm_text}", "callback_data": f"confirm:{action}"},
                {"text": f"❌ {cancel_text}", "callback_data": "cancel"}
            ]
        ]
    
    def create_position_keyboard(
        self,
        ticket: int,
        symbol: str
    ) -> List[List[Dict[str, str]]]:
        """Create keyboard for position management"""
        return [
            [
                {"text": "📊 Details", "callback_data": f"position:details:{ticket}"},
                {"text": "🎯 Modify", "callback_data": f"position:modify:{ticket}"}
            ],
            [
                {"text": "💵 Book 25%", "callback_data": f"position:book25:{ticket}"},
                {"text": "💵 Book 50%", "callback_data": f"position:book50:{ticket}"}
            ],
            [
                {"text": "⚖️ Breakeven", "callback_data": f"position:breakeven:{ticket}"},
                {"text": "🔴 Close", "callback_data": f"position:close:{ticket}"}
            ],
            [
                {"text": "◀️ Back", "callback_data": "menu:positions"}
            ]
        ]
    
    def create_plugin_keyboard(
        self,
        plugin_name: str,
        is_active: bool
    ) -> List[List[Dict[str, str]]]:
        """Create keyboard for plugin management"""
        toggle_text = "⏹️ Disable" if is_active else "▶️ Enable"
        toggle_action = "disable" if is_active else "enable"
        
        return [
            [
                {"text": "📊 Stats", "callback_data": f"plugin:stats:{plugin_name}"},
                {"text": "⚙️ Config", "callback_data": f"plugin:config:{plugin_name}"}
            ],
            [
                {"text": toggle_text, "callback_data": f"plugin:{toggle_action}:{plugin_name}"}
            ],
            [
                {"text": "◀️ Back", "callback_data": "menu:plugins"}
            ]
        ]
    
    def list_menus(self) -> List[MenuType]:
        """List all available menus"""
        return list(self.menus.keys())
