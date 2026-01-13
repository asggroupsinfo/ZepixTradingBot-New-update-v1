"""
Live Header Manager - Sticky Header for Telegram Bots

Document 20: Telegram Unified Interface Addendum
Creates live sticky headers that update every 60 seconds with:
- Current time, date, session duration
- Real-time bot status
- Key metrics (trades, P&L, plugins)

Each bot has its own header variant:
- Controller: Bot control & system status
- Notification: Alert activity
- Analytics: Performance stats
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import asyncio
import logging


class BotType(Enum):
    """Bot types for header variants"""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"


class HeaderStatus(Enum):
    """Header update status"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class HeaderMetrics:
    """Metrics displayed in header"""
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
        """Convert to dictionary"""
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
class HeaderConfig:
    """Configuration for live header"""
    update_interval: int = 60  # seconds
    show_clock: bool = True
    show_date: bool = True
    show_session: bool = True
    show_metrics: bool = True
    show_status: bool = True
    timezone: str = "UTC"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"


class HeaderFormatter:
    """
    Formats header content for different bot types
    """
    
    def __init__(self, bot_type: BotType, config: Optional[HeaderConfig] = None):
        self.bot_type = bot_type
        self.config = config or HeaderConfig()
        self.session_start: Optional[datetime] = None
    
    def set_session_start(self, start_time: datetime) -> None:
        """Set session start time"""
        self.session_start = start_time
    
    def format_header(self, metrics: HeaderMetrics) -> str:
        """Format complete header based on bot type"""
        lines = []
        
        # Title line
        lines.append(self._format_title())
        lines.append("─" * 30)
        
        # Clock/Date/Session line
        if self.config.show_clock or self.config.show_date or self.config.show_session:
            lines.append(self._format_time_line())
        
        # Status line
        if self.config.show_status:
            lines.append(self._format_status_line(metrics))
        
        # Metrics based on bot type
        if self.config.show_metrics:
            lines.append("─" * 30)
            lines.extend(self._format_metrics(metrics))
        
        lines.append("─" * 30)
        
        return "\n".join(lines)
    
    def _format_title(self) -> str:
        """Format title based on bot type"""
        titles = {
            BotType.CONTROLLER: "🤖 ZEPIX CONTROLLER",
            BotType.NOTIFICATION: "🔔 ZEPIX NOTIFICATIONS",
            BotType.ANALYTICS: "📊 ZEPIX ANALYTICS"
        }
        return titles.get(self.bot_type, "🤖 ZEPIX BOT")
    
    def _format_time_line(self) -> str:
        """Format time/date/session line"""
        now = datetime.utcnow()
        parts = []
        
        if self.config.show_clock:
            parts.append(f"🕐 {now.strftime(self.config.time_format)}")
        
        if self.config.show_date:
            parts.append(f"📅 {now.strftime(self.config.date_format)}")
        
        if self.config.show_session and self.session_start:
            duration = now - self.session_start
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            parts.append(f"⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        return " | ".join(parts)
    
    def _format_status_line(self, metrics: HeaderMetrics) -> str:
        """Format status line"""
        mt5_status = "🟢 MT5" if metrics.mt5_connected else "🔴 MT5"
        bot_status = "🟢 BOT" if metrics.bot_running else "🔴 BOT"
        return f"Status: {mt5_status} | {bot_status}"
    
    def _format_metrics(self, metrics: HeaderMetrics) -> List[str]:
        """Format metrics based on bot type"""
        if self.bot_type == BotType.CONTROLLER:
            return self._format_controller_metrics(metrics)
        elif self.bot_type == BotType.NOTIFICATION:
            return self._format_notification_metrics(metrics)
        elif self.bot_type == BotType.ANALYTICS:
            return self._format_analytics_metrics(metrics)
        return []
    
    def _format_controller_metrics(self, metrics: HeaderMetrics) -> List[str]:
        """Format controller bot metrics"""
        pnl_emoji = "📈" if metrics.daily_pnl >= 0 else "📉"
        pnl_sign = "+" if metrics.daily_pnl >= 0 else ""
        
        return [
            f"📋 Trades: {metrics.open_trades} open",
            f"{pnl_emoji} P&L: {pnl_sign}${metrics.daily_pnl:.2f}",
            f"🔌 Plugins: {metrics.active_plugins}/{metrics.total_plugins} active"
        ]
    
    def _format_notification_metrics(self, metrics: HeaderMetrics) -> List[str]:
        """Format notification bot metrics"""
        return [
            f"🔔 Alerts: {metrics.alerts_today} today",
            f"📥 Entries: {metrics.entries_today}",
            f"📤 Exits: {metrics.exits_today}"
        ]
    
    def _format_analytics_metrics(self, metrics: HeaderMetrics) -> List[str]:
        """Format analytics bot metrics"""
        pnl_emoji = "📈" if metrics.daily_pnl >= 0 else "📉"
        pnl_sign = "+" if metrics.daily_pnl >= 0 else ""
        
        return [
            f"🎯 Win Rate: {metrics.win_rate:.1f}%",
            f"{pnl_emoji} Daily P&L: {pnl_sign}${metrics.daily_pnl:.2f}",
            f"📊 Reports: {metrics.reports_sent} sent"
        ]


class LiveHeaderManager:
    """
    Live Header Manager
    
    Manages pinned header message that updates every 60 seconds.
    Each bot has its own header with relevant metrics.
    """
    
    def __init__(
        self,
        bot_type: BotType,
        chat_id: Optional[int] = None,
        config: Optional[HeaderConfig] = None,
        send_callback: Optional[Callable] = None,
        edit_callback: Optional[Callable] = None,
        pin_callback: Optional[Callable] = None
    ):
        self.bot_type = bot_type
        self.chat_id = chat_id
        self.config = config or HeaderConfig()
        self.formatter = HeaderFormatter(bot_type, self.config)
        
        # Callbacks for Telegram operations
        self._send_callback = send_callback
        self._edit_callback = edit_callback
        self._pin_callback = pin_callback
        
        # State
        self.status = HeaderStatus.STOPPED
        self.message_id: Optional[int] = None
        self.metrics = HeaderMetrics()
        self.session_start: Optional[datetime] = None
        self._update_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
    
    async def start(self) -> bool:
        """Start live header updates"""
        if self.status == HeaderStatus.ACTIVE:
            return True
        
        try:
            # Set session start
            self.session_start = datetime.utcnow()
            self.formatter.set_session_start(self.session_start)
            
            # Send initial header
            await self._send_initial_header()
            
            # Start update loop
            self.status = HeaderStatus.ACTIVE
            self._update_task = asyncio.create_task(self._update_loop())
            
            self.logger.info(f"LiveHeaderManager started for {self.bot_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start LiveHeaderManager: {e}")
            self.status = HeaderStatus.ERROR
            return False
    
    async def stop(self) -> None:
        """Stop live header updates"""
        self.status = HeaderStatus.STOPPED
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None
        
        self.logger.info(f"LiveHeaderManager stopped for {self.bot_type.value}")
    
    async def pause(self) -> None:
        """Pause header updates"""
        self.status = HeaderStatus.PAUSED
        self.logger.info(f"LiveHeaderManager paused for {self.bot_type.value}")
    
    async def resume(self) -> None:
        """Resume header updates"""
        if self.status == HeaderStatus.PAUSED:
            self.status = HeaderStatus.ACTIVE
            self.logger.info(f"LiveHeaderManager resumed for {self.bot_type.value}")
    
    def update_metrics(self, metrics: HeaderMetrics) -> None:
        """Update metrics (will be reflected in next update)"""
        self.metrics = metrics
    
    def update_metric(self, key: str, value: Any) -> None:
        """Update single metric"""
        if hasattr(self.metrics, key):
            setattr(self.metrics, key, value)
    
    async def force_update(self) -> bool:
        """Force immediate header update"""
        return await self._update_header()
    
    async def _send_initial_header(self) -> None:
        """Send initial header message and pin it"""
        header_text = self.formatter.format_header(self.metrics)
        
        if self._send_callback:
            result = await self._send_callback(
                chat_id=self.chat_id,
                text=header_text
            )
            if result and hasattr(result, 'message_id'):
                self.message_id = result.message_id
                
                # Pin the message
                if self._pin_callback:
                    await self._pin_callback(
                        chat_id=self.chat_id,
                        message_id=self.message_id
                    )
        else:
            # Mock mode - just set a fake message ID
            self.message_id = 1
    
    async def _update_header(self) -> bool:
        """Update header message"""
        if not self.message_id:
            return False
        
        try:
            header_text = self.formatter.format_header(self.metrics)
            
            if self._edit_callback:
                await self._edit_callback(
                    chat_id=self.chat_id,
                    message_id=self.message_id,
                    text=header_text
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update header: {e}")
            return False
    
    async def _update_loop(self) -> None:
        """Background update loop"""
        while self.status == HeaderStatus.ACTIVE:
            try:
                await asyncio.sleep(self.config.update_interval)
                
                if self.status == HeaderStatus.ACTIVE:
                    await self._update_header()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get header manager status"""
        return {
            "bot_type": self.bot_type.value,
            "status": self.status.value,
            "message_id": self.message_id,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "update_interval": self.config.update_interval,
            "metrics": self.metrics.to_dict()
        }


class HeaderSynchronizer:
    """
    Synchronizes headers across all 3 bots
    
    Ensures consistent metrics display and coordinated updates.
    """
    
    def __init__(self):
        self.headers: Dict[BotType, LiveHeaderManager] = {}
        self.shared_metrics = HeaderMetrics()
        self.logger = logging.getLogger(__name__)
    
    def register_header(self, header: LiveHeaderManager) -> None:
        """Register a header manager"""
        self.headers[header.bot_type] = header
    
    def unregister_header(self, bot_type: BotType) -> None:
        """Unregister a header manager"""
        if bot_type in self.headers:
            del self.headers[bot_type]
    
    async def start_all(self) -> Dict[BotType, bool]:
        """Start all registered headers"""
        results = {}
        for bot_type, header in self.headers.items():
            results[bot_type] = await header.start()
        return results
    
    async def stop_all(self) -> None:
        """Stop all registered headers"""
        for header in self.headers.values():
            await header.stop()
    
    def update_shared_metrics(self, metrics: HeaderMetrics) -> None:
        """Update metrics for all headers"""
        self.shared_metrics = metrics
        for header in self.headers.values():
            header.update_metrics(metrics)
    
    def update_shared_metric(self, key: str, value: Any) -> None:
        """Update single metric for all headers"""
        if hasattr(self.shared_metrics, key):
            setattr(self.shared_metrics, key, value)
        
        for header in self.headers.values():
            header.update_metric(key, value)
    
    async def force_update_all(self) -> Dict[BotType, bool]:
        """Force update all headers"""
        results = {}
        for bot_type, header in self.headers.items():
            results[bot_type] = await header.force_update()
        return results
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all headers"""
        return {
            bot_type.value: header.get_status()
            for bot_type, header in self.headers.items()
        }
