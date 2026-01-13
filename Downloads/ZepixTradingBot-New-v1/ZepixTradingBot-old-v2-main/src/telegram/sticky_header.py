"""
Sticky Header Implementation for V5 Hybrid Plugin Architecture

Provides persistent menu headers in Telegram with:
- Live Clock & Session Panel (IST time, date, active session)
- Metrics Display (PnL, Active Trades, API Latency, Uptime)
- Smart Updates (60s interval, rate limit compliance)
- Anti-Scroll Logic (resend & pin if scrolled out of view)
- Multi-Bot Support (Controller, Notification, Analytics)

Integrates V4 Forex Session Logic for session-aware trading display.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field
import logging
import time


class HeaderType(Enum):
    """Types of sticky headers for different bots."""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    UNIFIED = "unified"


class HeaderStatus(Enum):
    """Status of the sticky header."""
    ACTIVE = "active"
    UPDATING = "updating"
    STALE = "stale"
    ERROR = "error"


@dataclass
class HeaderMetrics:
    """Real-time metrics for header display."""
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    active_trades: int = 0
    pending_orders: int = 0
    api_latency_ms: int = 0
    bot_uptime_seconds: int = 0
    v3_status: str = "Unknown"
    v6_status: str = "Unknown"
    last_trade_time: Optional[datetime] = None
    win_rate: float = 0.0
    total_trades_today: int = 0


@dataclass
class HeaderConfig:
    """Configuration for sticky header."""
    update_interval_seconds: int = 60
    anti_scroll_check_interval: int = 300
    max_message_age_seconds: int = 600
    enable_metrics: bool = True
    enable_session_panel: bool = True
    enable_quick_buttons: bool = True
    pin_message: bool = True
    use_code_blocks: bool = True


@dataclass
class PinnedMessage:
    """Represents a pinned header message."""
    message_id: int
    chat_id: int
    header_type: HeaderType
    created_at: datetime
    last_updated: datetime
    update_count: int = 0
    is_pinned: bool = True


class StickyHeaderManager:
    """
    Manages sticky headers for the 3-bot Telegram system.
    
    Features:
    - Unified Header Manager: Single pinned message per chat
    - Live Clock & Session Panel: IST time, date, active session
    - Smart Updates: 60s interval with rate limit compliance
    - Metrics Display: PnL, Active Trades, API Latency, Uptime
    - Anti-Scroll Logic: Resend & pin if scrolled out of view
    - Multi-Bot Support: Different styles for each bot type
    """
    
    IST_OFFSET_HOURS = 5
    IST_OFFSET_MINUTES = 30
    
    def __init__(
        self,
        config: Optional[HeaderConfig] = None,
        session_manager: Optional[Any] = None
    ):
        """
        Initialize the Sticky Header Manager.
        
        Args:
            config: Header configuration
            session_manager: ForexSessionManager instance for session data
        """
        self.config = config or HeaderConfig()
        self.session_manager = session_manager
        
        self.pinned_messages: Dict[int, PinnedMessage] = {}
        self.metrics: HeaderMetrics = HeaderMetrics()
        self._running: bool = False
        self._update_task: Optional[asyncio.Task] = None
        self._anti_scroll_task: Optional[asyncio.Task] = None
        self._bot_start_time: datetime = datetime.now(timezone.utc)
        
        self._send_message_callback: Optional[Callable] = None
        self._edit_message_callback: Optional[Callable] = None
        self._pin_message_callback: Optional[Callable] = None
        self._get_message_callback: Optional[Callable] = None
        
        self.logger = logging.getLogger(__name__)
        
        self.stats = {
            'updates_sent': 0,
            'updates_failed': 0,
            'repins_triggered': 0,
            'anti_scroll_checks': 0,
            'rate_limit_delays': 0
        }
    
    def get_current_ist_time(self) -> datetime:
        """Get current time in IST timezone."""
        utc_now = datetime.now(timezone.utc)
        ist_offset = timedelta(hours=self.IST_OFFSET_HOURS, minutes=self.IST_OFFSET_MINUTES)
        return utc_now + ist_offset
    
    def format_uptime(self, seconds: int) -> str:
        """Format uptime in human-readable format."""
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def get_bot_uptime(self) -> int:
        """Get bot uptime in seconds."""
        now = datetime.now(timezone.utc)
        uptime = now - self._bot_start_time
        return int(uptime.total_seconds())
    
    def update_metrics(
        self,
        total_pnl: Optional[float] = None,
        daily_pnl: Optional[float] = None,
        active_trades: Optional[int] = None,
        pending_orders: Optional[int] = None,
        api_latency_ms: Optional[int] = None,
        v3_status: Optional[str] = None,
        v6_status: Optional[str] = None,
        last_trade_time: Optional[datetime] = None,
        win_rate: Optional[float] = None,
        total_trades_today: Optional[int] = None
    ) -> None:
        """Update header metrics."""
        if total_pnl is not None:
            self.metrics.total_pnl = total_pnl
        if daily_pnl is not None:
            self.metrics.daily_pnl = daily_pnl
        if active_trades is not None:
            self.metrics.active_trades = active_trades
        if pending_orders is not None:
            self.metrics.pending_orders = pending_orders
        if api_latency_ms is not None:
            self.metrics.api_latency_ms = api_latency_ms
        if v3_status is not None:
            self.metrics.v3_status = v3_status
        if v6_status is not None:
            self.metrics.v6_status = v6_status
        if last_trade_time is not None:
            self.metrics.last_trade_time = last_trade_time
        if win_rate is not None:
            self.metrics.win_rate = win_rate
        if total_trades_today is not None:
            self.metrics.total_trades_today = total_trades_today
        
        self.metrics.bot_uptime_seconds = self.get_bot_uptime()
    
    def _get_session_panel(self) -> Dict[str, str]:
        """Get session panel data from session manager or generate default."""
        if self.session_manager:
            try:
                return self.session_manager.get_header_session_panel()
            except Exception as e:
                self.logger.error(f"Failed to get session panel: {e}")
        
        current_time = self.get_current_ist_time()
        return {
            'time': current_time.strftime("%H:%M:%S"),
            'date': current_time.strftime("%d %b %Y"),
            'session': " Session Data Unavailable",
            'status_color': "yellow",
            'active_pairs': "N/A",
            'time_remaining': "N/A",
            'is_trading_allowed': False,
            'next_session': "Unknown"
        }
    
    def generate_controller_header(self) -> str:
        """Generate header text for Controller Bot."""
        session_panel = self._get_session_panel()
        uptime_str = self.format_uptime(self.get_bot_uptime())
        
        pnl_emoji = "" if self.metrics.daily_pnl >= 0 else ""
        pnl_sign = "+" if self.metrics.daily_pnl >= 0 else ""
        
        v3_emoji = "" if self.metrics.v3_status == "Active" else ""
        v6_emoji = "" if self.metrics.v6_status == "Active" else ""
        
        header = (
            f"<b> Zepix Trading Bot - Live Dashboard</b>\n"
            f"\n"
            f"<code>"
            f" {session_panel['time']} IST |  {session_panel['date']}\n"
            f"{session_panel['session']}\n"
            f" Active Pairs: {session_panel['active_pairs']}\n"
            f"</code>\n"
            f"\n"
            f"<b> System Status</b>\n"
            f"<code>"
            f" Bot Uptime: {uptime_str}\n"
            f" API Latency: {self.metrics.api_latency_ms}ms\n"
            f"{v3_emoji} V3 Combined: {self.metrics.v3_status}\n"
            f"{v6_emoji} V6 Price Action: {self.metrics.v6_status}\n"
            f"</code>\n"
            f"\n"
            f"<b> Trading Stats</b>\n"
            f"<code>"
            f" Active Trades: {self.metrics.active_trades}\n"
            f" Pending Orders: {self.metrics.pending_orders}\n"
            f"{pnl_emoji} Daily P&L: {pnl_sign}${self.metrics.daily_pnl:.2f}\n"
            f" Total P&L: ${self.metrics.total_pnl:.2f}\n"
            f" Win Rate: {self.metrics.win_rate:.1f}%\n"
            f"</code>\n"
            f"\n"
            f"<i>Last Update: {session_panel['time']} IST</i>"
        )
        
        return header
    
    def generate_notification_header(self) -> str:
        """Generate header text for Notification Bot."""
        session_panel = self._get_session_panel()
        
        header = (
            f"<b> Zepix Notifications</b>\n"
            f"\n"
            f"<code>"
            f" {session_panel['time']} IST |  {session_panel['date']}\n"
            f"{session_panel['session']}\n"
            f"</code>\n"
            f"\n"
            f"<b> Alert Status</b>\n"
            f"<code>"
            f" Active Trades: {self.metrics.active_trades}\n"
            f" Today's Trades: {self.metrics.total_trades_today}\n"
            f"</code>\n"
            f"\n"
            f"<i>Trade alerts appear below </i>"
        )
        
        return header
    
    def generate_analytics_header(self) -> str:
        """Generate header text for Analytics Bot."""
        session_panel = self._get_session_panel()
        uptime_str = self.format_uptime(self.get_bot_uptime())
        
        pnl_emoji = "" if self.metrics.total_pnl >= 0 else ""
        
        header = (
            f"<b> Zepix Analytics Dashboard</b>\n"
            f"\n"
            f"<code>"
            f" {session_panel['time']} IST |  {session_panel['date']}\n"
            f"{session_panel['session']}\n"
            f"</code>\n"
            f"\n"
            f"<b> Performance Metrics</b>\n"
            f"<code>"
            f"{pnl_emoji} Total P&L: ${self.metrics.total_pnl:.2f}\n"
            f" Daily P&L: ${self.metrics.daily_pnl:.2f}\n"
            f" Win Rate: {self.metrics.win_rate:.1f}%\n"
            f" Total Trades: {self.metrics.total_trades_today}\n"
            f" Uptime: {uptime_str}\n"
            f"</code>\n"
            f"\n"
            f"<i>Reports and analytics below </i>"
        )
        
        return header
    
    def generate_unified_header(self) -> str:
        """Generate unified header text combining all information."""
        session_panel = self._get_session_panel()
        uptime_str = self.format_uptime(self.get_bot_uptime())
        
        pnl_emoji = "" if self.metrics.daily_pnl >= 0 else ""
        pnl_sign = "+" if self.metrics.daily_pnl >= 0 else ""
        
        v3_emoji = "" if self.metrics.v3_status == "Active" else ""
        v6_emoji = "" if self.metrics.v6_status == "Active" else ""
        
        trading_status = "" if session_panel['is_trading_allowed'] else ""
        
        header = (
            f"<b> ZEPIX TRADING BOT - COMMAND CENTER</b>\n"
            f"\n"
            f"<code>"
            f" {session_panel['time']} IST |  {session_panel['date']}\n"
            f"{session_panel['session']}\n"
            f" Active Pairs: {session_panel['active_pairs']}\n"
            f" Time Remaining: {session_panel['time_remaining']}\n"
            f"</code>\n"
            f"\n"
            f"<b>{trading_status} Trading Status</b>\n"
            f"<code>"
            f"{v3_emoji} V3 Combined Logic: {self.metrics.v3_status}\n"
            f"{v6_emoji} V6 Price Action: {self.metrics.v6_status}\n"
            f" Active Trades: {self.metrics.active_trades}\n"
            f" Pending Orders: {self.metrics.pending_orders}\n"
            f"</code>\n"
            f"\n"
            f"<b> Performance</b>\n"
            f"<code>"
            f"{pnl_emoji} Daily P&L: {pnl_sign}${self.metrics.daily_pnl:.2f}\n"
            f" Total P&L: ${self.metrics.total_pnl:.2f}\n"
            f" Win Rate: {self.metrics.win_rate:.1f}% ({self.metrics.total_trades_today} trades)\n"
            f"</code>\n"
            f"\n"
            f"<b> System Health</b>\n"
            f"<code>"
            f" Uptime: {uptime_str}\n"
            f" API Latency: {self.metrics.api_latency_ms}ms\n"
            f"</code>\n"
            f"\n"
            f"<i> Last Update: {session_panel['time']} IST | Next: {session_panel['next_session']}</i>"
        )
        
        return header
    
    def generate_header(self, header_type: HeaderType = HeaderType.UNIFIED) -> str:
        """
        Generate header text based on type.
        
        Args:
            header_type: Type of header to generate
            
        Returns:
            Formatted header text
        """
        if header_type == HeaderType.CONTROLLER:
            return self.generate_controller_header()
        elif header_type == HeaderType.NOTIFICATION:
            return self.generate_notification_header()
        elif header_type == HeaderType.ANALYTICS:
            return self.generate_analytics_header()
        else:
            return self.generate_unified_header()
    
    def generate_quick_buttons(self, header_type: HeaderType = HeaderType.UNIFIED) -> List[List[Dict[str, str]]]:
        """
        Generate inline keyboard buttons for header.
        
        Args:
            header_type: Type of header
            
        Returns:
            List of button rows for InlineKeyboardMarkup
        """
        if header_type == HeaderType.CONTROLLER:
            return [
                [
                    {"text": " Dashboard", "callback_data": "dash_home"},
                    {"text": " Live Stats", "callback_data": "dash_stats"}
                ],
                [
                    {"text": " V3 Status", "callback_data": "plugin_v3"},
                    {"text": " V6 Status", "callback_data": "plugin_v6"}
                ],
                [
                    {"text": " Settings", "callback_data": "settings"},
                    {"text": " Reports", "callback_data": "reports"}
                ],
                [
                    {"text": " Refresh", "callback_data": "refresh"},
                    {"text": " Emergency Stop", "callback_data": "emergency_stop"}
                ]
            ]
        elif header_type == HeaderType.NOTIFICATION:
            return [
                [
                    {"text": " Mute 1h", "callback_data": "mute_1h"},
                    {"text": " Mute All", "callback_data": "mute_all"}
                ],
                [
                    {"text": " Settings", "callback_data": "notif_settings"},
                    {"text": " History", "callback_data": "notif_history"}
                ]
            ]
        elif header_type == HeaderType.ANALYTICS:
            return [
                [
                    {"text": " Daily Report", "callback_data": "report_daily"},
                    {"text": " Weekly Report", "callback_data": "report_weekly"}
                ],
                [
                    {"text": " Performance", "callback_data": "analytics_perf"},
                    {"text": " Export", "callback_data": "analytics_export"}
                ]
            ]
        else:
            return [
                [
                    {"text": " Menu", "callback_data": "menu_home"},
                    {"text": " Status", "callback_data": "menu_status"},
                    {"text": " Settings", "callback_data": "menu_settings"}
                ],
                [
                    {"text": " V3", "callback_data": "plugin_v3"},
                    {"text": " V6", "callback_data": "plugin_v6"},
                    {"text": " Reports", "callback_data": "reports"}
                ],
                [
                    {"text": " Refresh", "callback_data": "refresh"},
                    {"text": " Stop", "callback_data": "emergency_stop"}
                ]
            ]
    
    def generate_reply_keyboard(self) -> List[List[str]]:
        """
        Generate persistent reply keyboard buttons.
        
        Returns:
            List of button rows for ReplyKeyboardMarkup
        """
        return [
            [" Menu", " Status"],
            [" Settings", " Analytics"]
        ]
    
    def set_callbacks(
        self,
        send_message: Optional[Callable] = None,
        edit_message: Optional[Callable] = None,
        pin_message: Optional[Callable] = None,
        get_message: Optional[Callable] = None
    ) -> None:
        """
        Set callback functions for Telegram operations.
        
        Args:
            send_message: Async function to send a message
            edit_message: Async function to edit a message
            pin_message: Async function to pin a message
            get_message: Async function to get message info
        """
        self._send_message_callback = send_message
        self._edit_message_callback = edit_message
        self._pin_message_callback = pin_message
        self._get_message_callback = get_message
    
    async def create_header(
        self,
        chat_id: int,
        header_type: HeaderType = HeaderType.UNIFIED,
        pin: bool = True
    ) -> Optional[PinnedMessage]:
        """
        Create and optionally pin a new header message.
        
        Args:
            chat_id: Telegram chat ID
            header_type: Type of header to create
            pin: Whether to pin the message
            
        Returns:
            PinnedMessage if successful, None otherwise
        """
        if not self._send_message_callback:
            self.logger.error("Send message callback not set")
            return None
        
        try:
            header_text = self.generate_header(header_type)
            buttons = self.generate_quick_buttons(header_type) if self.config.enable_quick_buttons else None
            
            message_id = await self._send_message_callback(
                chat_id=chat_id,
                text=header_text,
                buttons=buttons
            )
            
            if message_id and pin and self._pin_message_callback:
                await self._pin_message_callback(chat_id=chat_id, message_id=message_id)
            
            now = datetime.now(timezone.utc)
            pinned_message = PinnedMessage(
                message_id=message_id or 0,
                chat_id=chat_id,
                header_type=header_type,
                created_at=now,
                last_updated=now,
                is_pinned=pin
            )
            
            self.pinned_messages[chat_id] = pinned_message
            self.stats['updates_sent'] += 1
            
            self.logger.info(f"Created header for chat {chat_id}, message_id: {message_id}")
            return pinned_message
            
        except Exception as e:
            self.logger.error(f"Failed to create header: {e}")
            self.stats['updates_failed'] += 1
            return None
    
    async def update_header(
        self,
        chat_id: int,
        force_recreate: bool = False
    ) -> bool:
        """
        Update an existing header message.
        
        Args:
            chat_id: Telegram chat ID
            force_recreate: Force recreate if update fails
            
        Returns:
            True if successful
        """
        if chat_id not in self.pinned_messages:
            if force_recreate:
                await self.create_header(chat_id)
                return True
            return False
        
        pinned = self.pinned_messages[chat_id]
        
        if not self._edit_message_callback:
            self.logger.error("Edit message callback not set")
            return False
        
        try:
            header_text = self.generate_header(pinned.header_type)
            buttons = self.generate_quick_buttons(pinned.header_type) if self.config.enable_quick_buttons else None
            
            success = await self._edit_message_callback(
                chat_id=chat_id,
                message_id=pinned.message_id,
                text=header_text,
                buttons=buttons
            )
            
            if success:
                pinned.last_updated = datetime.now(timezone.utc)
                pinned.update_count += 1
                self.stats['updates_sent'] += 1
                return True
            else:
                self.stats['updates_failed'] += 1
                if force_recreate:
                    await self.create_header(chat_id, pinned.header_type, pinned.is_pinned)
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update header: {e}")
            self.stats['updates_failed'] += 1
            
            if force_recreate:
                await self.create_header(chat_id, pinned.header_type, pinned.is_pinned)
            
            return False
    
    async def check_and_repin(self, chat_id: int) -> bool:
        """
        Check if header is still pinned and repin if necessary.
        
        Anti-scroll logic: Detects if header scrolled out of view and repins.
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            True if repin was needed and successful
        """
        self.stats['anti_scroll_checks'] += 1
        
        if chat_id not in self.pinned_messages:
            return False
        
        pinned = self.pinned_messages[chat_id]
        now = datetime.now(timezone.utc)
        
        message_age = (now - pinned.last_updated).total_seconds()
        if message_age > self.config.max_message_age_seconds:
            self.logger.info(f"Header too old ({message_age}s), recreating for chat {chat_id}")
            await self.create_header(chat_id, pinned.header_type, pinned.is_pinned)
            self.stats['repins_triggered'] += 1
            return True
        
        return False
    
    async def remove_header(self, chat_id: int) -> bool:
        """
        Remove header from tracking (does not delete message).
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            True if removed
        """
        if chat_id in self.pinned_messages:
            del self.pinned_messages[chat_id]
            return True
        return False
    
    async def _update_loop(self) -> None:
        """Background task to update headers periodically."""
        while self._running:
            try:
                for chat_id in list(self.pinned_messages.keys()):
                    await self.update_header(chat_id)
                    await asyncio.sleep(1)
                
                await asyncio.sleep(self.config.update_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Update loop error: {e}")
                await asyncio.sleep(self.config.update_interval_seconds)
    
    async def _anti_scroll_loop(self) -> None:
        """Background task to check and repin headers."""
        while self._running:
            try:
                await asyncio.sleep(self.config.anti_scroll_check_interval)
                
                for chat_id in list(self.pinned_messages.keys()):
                    await self.check_and_repin(chat_id)
                    await asyncio.sleep(1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Anti-scroll loop error: {e}")
                await asyncio.sleep(self.config.anti_scroll_check_interval)
    
    async def start(self) -> None:
        """Start the sticky header manager."""
        if self._running:
            return
        
        self._running = True
        self._bot_start_time = datetime.now(timezone.utc)
        
        self._update_task = asyncio.create_task(self._update_loop())
        self._anti_scroll_task = asyncio.create_task(self._anti_scroll_loop())
        
        self.logger.info("Sticky header manager started")
    
    async def stop(self) -> None:
        """Stop the sticky header manager."""
        self._running = False
        
        if self._update_task and not self._update_task.done():
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        
        if self._anti_scroll_task and not self._anti_scroll_task.done():
            self._anti_scroll_task.cancel()
            try:
                await self._anti_scroll_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Sticky header manager stopped")
    
    def get_header_status(self, chat_id: int) -> Dict[str, Any]:
        """Get status of header for a chat."""
        if chat_id not in self.pinned_messages:
            return {
                'exists': False,
                'status': HeaderStatus.ERROR.value
            }
        
        pinned = self.pinned_messages[chat_id]
        now = datetime.now(timezone.utc)
        age_seconds = (now - pinned.last_updated).total_seconds()
        
        if age_seconds > self.config.max_message_age_seconds:
            status = HeaderStatus.STALE
        elif age_seconds > self.config.update_interval_seconds * 2:
            status = HeaderStatus.UPDATING
        else:
            status = HeaderStatus.ACTIVE
        
        return {
            'exists': True,
            'status': status.value,
            'message_id': pinned.message_id,
            'header_type': pinned.header_type.value,
            'is_pinned': pinned.is_pinned,
            'update_count': pinned.update_count,
            'age_seconds': int(age_seconds),
            'created_at': pinned.created_at.isoformat(),
            'last_updated': pinned.last_updated.isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sticky header manager statistics."""
        return {
            **self.stats,
            'active_headers': len(self.pinned_messages),
            'is_running': self._running,
            'uptime_seconds': self.get_bot_uptime(),
            'config': {
                'update_interval': self.config.update_interval_seconds,
                'anti_scroll_interval': self.config.anti_scroll_check_interval,
                'max_message_age': self.config.max_message_age_seconds
            }
        }


class LiveClockManager:
    """
    Manages live clock display in Telegram headers.
    
    Provides real-time IST clock and calendar with configurable update frequency.
    """
    
    IST_OFFSET_HOURS = 5
    IST_OFFSET_MINUTES = 30
    
    def __init__(self, update_interval_seconds: int = 60):
        """
        Initialize the Live Clock Manager.
        
        Args:
            update_interval_seconds: How often to update the clock display
        """
        self.update_interval = update_interval_seconds
        self._running: bool = False
        self._update_task: Optional[asyncio.Task] = None
        self._clock_callback: Optional[Callable] = None
        self.logger = logging.getLogger(__name__)
    
    def get_current_ist_time(self) -> datetime:
        """Get current time in IST timezone."""
        utc_now = datetime.now(timezone.utc)
        ist_offset = timedelta(hours=self.IST_OFFSET_HOURS, minutes=self.IST_OFFSET_MINUTES)
        return utc_now + ist_offset
    
    def format_clock_display(self) -> Dict[str, str]:
        """
        Format clock display data.
        
        Returns:
            Dictionary with formatted time and date strings
        """
        current_time = self.get_current_ist_time()
        
        return {
            'time': current_time.strftime("%H:%M:%S"),
            'time_short': current_time.strftime("%H:%M"),
            'date': current_time.strftime("%d %b %Y"),
            'date_full': current_time.strftime("%d %B %Y (%A)"),
            'day': current_time.strftime("%A"),
            'timestamp': current_time.isoformat(),
            'timezone': 'IST'
        }
    
    def format_clock_message(self) -> str:
        """Format combined clock and calendar message."""
        clock_data = self.format_clock_display()
        
        return (
            f" <b>Current Time:</b> {clock_data['time']} IST\n"
            f" <b>Date:</b> {clock_data['date_full']}\n"
            f""
        )
    
    def set_clock_callback(self, callback: Callable) -> None:
        """Set callback function for clock updates."""
        self._clock_callback = callback
    
    async def _clock_loop(self) -> None:
        """Background task to update clock."""
        while self._running:
            try:
                if self._clock_callback:
                    clock_data = self.format_clock_display()
                    await self._clock_callback(clock_data)
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Clock loop error: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def start(self) -> None:
        """Start the live clock manager."""
        if self._running:
            return
        
        self._running = True
        self._update_task = asyncio.create_task(self._clock_loop())
        self.logger.info("Live clock manager started")
    
    async def stop(self) -> None:
        """Stop the live clock manager."""
        self._running = False
        
        if self._update_task and not self._update_task.done():
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Live clock manager stopped")


def create_sticky_header_manager(
    config: Optional[HeaderConfig] = None,
    session_manager: Optional[Any] = None
) -> StickyHeaderManager:
    """Factory function to create a StickyHeaderManager instance."""
    return StickyHeaderManager(config=config, session_manager=session_manager)


def create_live_clock_manager(update_interval: int = 60) -> LiveClockManager:
    """Factory function to create a LiveClockManager instance."""
    return LiveClockManager(update_interval_seconds=update_interval)
