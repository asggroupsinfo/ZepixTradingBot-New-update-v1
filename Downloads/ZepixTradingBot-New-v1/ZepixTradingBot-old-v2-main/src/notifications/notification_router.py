"""
Notification Router - Central Notification Dispatch

Document 19: Notification System Specification
Centralized notification routing for all bot events with priority-based delivery.

Priority Levels:
- CRITICAL (5): Emergency stop, daily loss limit, MT5 disconnect - Broadcast to ALL bots + Voice
- HIGH (4): Trade entry/exit, SL/TP hit, plugin error - Notification Bot + Voice
- MEDIUM (3): Partial profit, SL modification - Notification Bot only
- LOW (2): Daily summary, config reload - Analytics Bot
- INFO (1): Bot started, plugin loaded - Controller Bot
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import logging
import asyncio


class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = 5  # RED - Emergency, broadcast to ALL + voice
    HIGH = 4      # ORANGE - Trade events, notification bot + voice
    MEDIUM = 3    # YELLOW - Partial actions, notification bot only
    LOW = 2       # BLUE - Summaries, analytics bot
    INFO = 1      # GREEN - Status updates, controller bot
    
    @property
    def color(self) -> str:
        """Get color indicator for priority"""
        colors = {
            NotificationPriority.CRITICAL: "RED",
            NotificationPriority.HIGH: "ORANGE",
            NotificationPriority.MEDIUM: "YELLOW",
            NotificationPriority.LOW: "BLUE",
            NotificationPriority.INFO: "GREEN"
        }
        return colors.get(self, "WHITE")
    
    @property
    def emoji(self) -> str:
        """Get emoji indicator for priority"""
        emojis = {
            NotificationPriority.CRITICAL: "🔴",
            NotificationPriority.HIGH: "🟠",
            NotificationPriority.MEDIUM: "🟡",
            NotificationPriority.LOW: "🔵",
            NotificationPriority.INFO: "🟢"
        }
        return emojis.get(self, "⚪")
    
    @property
    def requires_voice(self) -> bool:
        """Check if priority requires voice alert"""
        return self in (NotificationPriority.CRITICAL, NotificationPriority.HIGH)
    
    @property
    def target_bot(self) -> str:
        """Get default target bot for priority"""
        targets = {
            NotificationPriority.CRITICAL: "broadcast",
            NotificationPriority.HIGH: "notification",
            NotificationPriority.MEDIUM: "notification",
            NotificationPriority.LOW: "analytics",
            NotificationPriority.INFO: "controller"
        }
        return targets.get(self, "notification")


class NotificationType(Enum):
    """All notification types supported by the system"""
    # Trade Events
    ENTRY_V3_DUAL = "entry_v3_dual"
    ENTRY_V6_SINGLE = "entry_v6_single"
    ENTRY_V6_SINGLE_A = "entry_v6_single_a"
    ENTRY_V6_SINGLE_B = "entry_v6_single_b"
    EXIT_PROFIT = "exit_profit"
    EXIT_LOSS = "exit_loss"
    TP1_HIT = "tp1_hit"
    TP2_HIT = "tp2_hit"
    SL_HIT = "sl_hit"
    PROFIT_PARTIAL = "profit_partial"
    SL_MODIFIED = "sl_modified"
    BREAKEVEN_MOVED = "breakeven_moved"
    
    # System Events
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    EMERGENCY_STOP = "emergency_stop"
    MT5_DISCONNECT = "mt5_disconnect"
    MT5_RECONNECT = "mt5_reconnect"
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_ERROR = "plugin_error"
    CONFIG_RELOAD = "config_reload"
    
    # Alert Events
    ALERT_RECEIVED = "alert_received"
    ALERT_PROCESSED = "alert_processed"
    ALERT_SHADOW = "alert_shadow"
    ALERT_ERROR = "alert_error"
    ALERT_INVALID = "alert_invalid"
    
    # Analytics Events
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    PERFORMANCE_REPORT = "performance_report"
    RISK_ALERT = "risk_alert"
    
    @property
    def default_priority(self) -> NotificationPriority:
        """Get default priority for notification type"""
        priority_map = {
            # Critical
            NotificationType.EMERGENCY_STOP: NotificationPriority.CRITICAL,
            NotificationType.BOT_STOPPED: NotificationPriority.CRITICAL,
            NotificationType.MT5_DISCONNECT: NotificationPriority.CRITICAL,
            NotificationType.DAILY_LOSS_LIMIT: NotificationPriority.CRITICAL,
            # High
            NotificationType.ENTRY_V3_DUAL: NotificationPriority.HIGH,
            NotificationType.ENTRY_V6_SINGLE: NotificationPriority.HIGH,
            NotificationType.ENTRY_V6_SINGLE_A: NotificationPriority.HIGH,
            NotificationType.ENTRY_V6_SINGLE_B: NotificationPriority.HIGH,
            NotificationType.EXIT_PROFIT: NotificationPriority.HIGH,
            NotificationType.EXIT_LOSS: NotificationPriority.HIGH,
            NotificationType.TP1_HIT: NotificationPriority.HIGH,
            NotificationType.TP2_HIT: NotificationPriority.HIGH,
            NotificationType.SL_HIT: NotificationPriority.HIGH,
            NotificationType.MT5_RECONNECT: NotificationPriority.HIGH,
            NotificationType.PLUGIN_ERROR: NotificationPriority.HIGH,
            NotificationType.ALERT_ERROR: NotificationPriority.HIGH,
            NotificationType.RISK_ALERT: NotificationPriority.HIGH,
            # Medium
            NotificationType.PROFIT_PARTIAL: NotificationPriority.MEDIUM,
            NotificationType.SL_MODIFIED: NotificationPriority.MEDIUM,
            NotificationType.BREAKEVEN_MOVED: NotificationPriority.MEDIUM,
            NotificationType.ALERT_PROCESSED: NotificationPriority.MEDIUM,
            NotificationType.ALERT_INVALID: NotificationPriority.MEDIUM,
            # Low
            NotificationType.DAILY_SUMMARY: NotificationPriority.LOW,
            NotificationType.WEEKLY_SUMMARY: NotificationPriority.LOW,
            NotificationType.PERFORMANCE_REPORT: NotificationPriority.LOW,
            NotificationType.CONFIG_RELOAD: NotificationPriority.LOW,
            NotificationType.ALERT_SHADOW: NotificationPriority.LOW,
            # Info
            NotificationType.BOT_STARTED: NotificationPriority.INFO,
            NotificationType.PLUGIN_LOADED: NotificationPriority.INFO,
            NotificationType.ALERT_RECEIVED: NotificationPriority.INFO,
        }
        return priority_map.get(self, NotificationPriority.MEDIUM)
    
    @property
    def requires_voice(self) -> bool:
        """Check if notification type requires voice alert"""
        voice_types = {
            NotificationType.ENTRY_V3_DUAL,
            NotificationType.ENTRY_V6_SINGLE,
            NotificationType.ENTRY_V6_SINGLE_A,
            NotificationType.EXIT_PROFIT,
            NotificationType.EXIT_LOSS,
            NotificationType.TP1_HIT,
            NotificationType.TP2_HIT,
            NotificationType.SL_HIT,
            NotificationType.EMERGENCY_STOP,
            NotificationType.MT5_DISCONNECT,
            NotificationType.DAILY_LOSS_LIMIT,
            NotificationType.RISK_ALERT,
        }
        return self in voice_types


@dataclass
class Notification:
    """Notification data structure"""
    notification_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    data: Dict[str, Any]
    formatted_message: str = ""
    voice_text: str = ""
    target_bot: str = ""
    target_users: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    delivered: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "notification_id": self.notification_id,
            "notification_type": self.notification_type.value,
            "priority": self.priority.name,
            "data": self.data,
            "formatted_message": self.formatted_message,
            "voice_text": self.voice_text,
            "target_bot": self.target_bot,
            "target_users": self.target_users,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered": self.delivered,
            "error": self.error,
        }


@dataclass
class NotificationLog:
    """Log entry for sent notifications"""
    notification_id: str
    notification_type: str
    priority: str
    target_bot: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    delivery_time_ms: float = 0.0


class MockTelegramManager:
    """Mock Telegram Manager for testing"""
    
    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []
        self.broadcast_messages: List[str] = []
    
    async def route_message(self, bot: str, message: str) -> bool:
        """Route message to specific bot"""
        self.sent_messages.append({
            "bot": bot,
            "message": message,
            "timestamp": datetime.now()
        })
        return True
    
    async def broadcast(self, message: str) -> bool:
        """Broadcast message to all bots"""
        self.broadcast_messages.append(message)
        return True
    
    async def send_to_users(self, user_ids: List[int], message: str) -> Dict[int, bool]:
        """Send message to specific users"""
        results = {}
        for user_id in user_ids:
            self.sent_messages.append({
                "user_id": user_id,
                "message": message,
                "timestamp": datetime.now()
            })
            results[user_id] = True
        return results


class NotificationRouter:
    """
    Central Notification Router
    
    Routes notifications to appropriate bots based on priority and type.
    Supports voice alerts, message formatting, and delivery tracking.
    """
    
    def __init__(self, telegram_manager=None):
        self.telegram = telegram_manager or MockTelegramManager()
        self.voice_enabled = True
        self.handlers: Dict[str, Callable] = {}
        self.notification_log: List[NotificationLog] = []
        self.logger = logging.getLogger(__name__)
        self._notification_counter = 0
        self._voice_callback: Optional[Callable] = None
        self._formatter = None
        self._stats = None
    
    def set_formatter(self, formatter) -> None:
        """Set notification formatter"""
        self._formatter = formatter
    
    def set_stats(self, stats) -> None:
        """Set notification stats tracker"""
        self._stats = stats
    
    def set_voice_callback(self, callback: Callable) -> None:
        """Set voice alert callback"""
        self._voice_callback = callback
    
    def register_handler(self, notification_type: str, handler: Callable) -> None:
        """Register custom handler for notification type"""
        self.handlers[notification_type] = handler
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        self._notification_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"NOTIF-{timestamp}-{self._notification_counter:06d}"
    
    async def send(
        self,
        notification_type: NotificationType,
        data: Dict[str, Any],
        priority: Optional[NotificationPriority] = None,
        target_users: Optional[List[int]] = None
    ) -> Notification:
        """
        Central notification dispatch
        
        Args:
            notification_type: Type of notification
            data: Notification payload
            priority: Override priority (uses default if None)
            target_users: Specific users to notify (optional)
            
        Returns:
            Notification object with delivery status
        """
        # Use default priority if not specified
        if priority is None:
            priority = notification_type.default_priority
        
        # Create notification
        notification = Notification(
            notification_id=self._generate_notification_id(),
            notification_type=notification_type,
            priority=priority,
            data=data,
            target_bot=priority.target_bot,
            target_users=target_users or []
        )
        
        # Format message
        notification.formatted_message = await self.format_notification(
            notification_type.value, data
        )
        
        # Generate voice text if needed
        if priority.requires_voice or notification_type.requires_voice:
            notification.voice_text = self._generate_voice_text(
                notification_type.value, data
            )
        
        start_time = datetime.now()
        success = False
        error = None
        
        try:
            # Route based on priority
            if priority == NotificationPriority.CRITICAL:
                # Broadcast to ALL bots
                await self.telegram.broadcast(notification.formatted_message)
                # Always send voice for critical
                await self._send_voice_alert(notification.voice_text, data)
                success = True
                
            elif priority == NotificationPriority.HIGH:
                # Send to Notification Bot
                await self.telegram.route_message('notification', notification.formatted_message)
                # Voice if enabled
                if self.voice_enabled:
                    await self._send_voice_alert(notification.voice_text, data)
                success = True
                
            elif priority == NotificationPriority.MEDIUM:
                # Notification Bot only
                await self.telegram.route_message('notification', notification.formatted_message)
                success = True
                
            elif priority == NotificationPriority.LOW:
                # Analytics Bot
                await self.telegram.route_message('analytics', notification.formatted_message)
                success = True
                
            else:  # INFO
                # Controller Bot
                await self.telegram.route_message('controller', notification.formatted_message)
                success = True
            
            # Send to specific users if provided
            if target_users:
                await self.telegram.send_to_users(target_users, notification.formatted_message)
            
            notification.sent_at = datetime.now()
            notification.delivered = True
            
        except Exception as e:
            error = str(e)
            notification.error = error
            self.logger.error(f"Notification send failed: {e}")
        
        # Calculate delivery time
        delivery_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log notification
        log_entry = NotificationLog(
            notification_id=notification.notification_id,
            notification_type=notification_type.value,
            priority=priority.name,
            target_bot=notification.target_bot,
            success=success,
            error=error,
            delivery_time_ms=delivery_time
        )
        self.notification_log.append(log_entry)
        
        # Update stats if available
        if self._stats:
            self._stats.record(
                notification_type.value,
                priority,
                notification.target_bot,
                success
            )
        
        return notification
    
    async def format_notification(self, notification_type: str, data: Dict[str, Any]) -> str:
        """Format notification based on type"""
        # Check for custom handler
        handler = self.handlers.get(notification_type)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                return await handler(data)
            return handler(data)
        
        # Use formatter if available
        if self._formatter:
            return self._formatter.format(notification_type, data)
        
        # Default formatter
        return f"{notification_type.upper()}: {data}"
    
    def _generate_voice_text(self, notification_type: str, data: Dict[str, Any]) -> str:
        """Generate short voice alert text"""
        if notification_type in ('entry_v3_dual', 'entry_v6_single', 'entry_v6_single_a'):
            direction = data.get('direction', 'unknown')
            symbol = data.get('symbol', 'unknown')
            entry_price = data.get('entry_price', 0)
            signal_type = data.get('signal_type', 'unknown')
            return f"New {direction} trade on {symbol} at {entry_price}. Signal: {signal_type}."
        
        elif notification_type == 'exit_profit':
            direction = data.get('direction', 'unknown')
            profit = data.get('profit', 0)
            return f"{direction} trade closed with profit of {profit} dollars."
        
        elif notification_type == 'exit_loss':
            direction = data.get('direction', 'unknown')
            profit = data.get('profit', 0)
            return f"{direction} trade closed with loss of {abs(profit)} dollars."
        
        elif notification_type in ('tp1_hit', 'tp2_hit'):
            tp_level = data.get('tp_level', 1)
            profit = data.get('profit', 0)
            return f"TP{tp_level} hit. Profit: {profit} dollars."
        
        elif notification_type == 'sl_hit':
            profit = data.get('profit', 0)
            return f"Stop loss hit. Loss: {abs(profit)} dollars."
        
        elif notification_type == 'emergency_stop':
            message = data.get('message', 'Emergency stop activated')
            return f"Emergency alert. {message}"
        
        elif notification_type == 'mt5_disconnect':
            return "Warning. MT5 connection lost. Please check your connection."
        
        elif notification_type == 'daily_loss_limit':
            return "Daily loss limit reached. Trading has been paused."
        
        elif notification_type == 'risk_alert':
            message = data.get('message', 'Risk threshold exceeded')
            return f"Risk alert. {message}"
        
        else:
            return f"Notification: {notification_type}"
    
    async def _send_voice_alert(self, voice_text: str, data: Dict[str, Any]) -> None:
        """Send voice alert"""
        if self._voice_callback and voice_text:
            try:
                if asyncio.iscoroutinefunction(self._voice_callback):
                    await self._voice_callback(voice_text, data)
                else:
                    self._voice_callback(voice_text, data)
            except Exception as e:
                self.logger.error(f"Voice alert failed: {e}")
    
    def get_notification_log(self, limit: int = 100) -> List[NotificationLog]:
        """Get recent notification log entries"""
        return self.notification_log[-limit:]
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get notification statistics summary"""
        total = len(self.notification_log)
        successful = sum(1 for log in self.notification_log if log.success)
        failed = total - successful
        
        by_type: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}
        by_bot: Dict[str, int] = {}
        
        for log in self.notification_log:
            by_type[log.notification_type] = by_type.get(log.notification_type, 0) + 1
            by_priority[log.priority] = by_priority.get(log.priority, 0) + 1
            by_bot[log.target_bot] = by_bot.get(log.target_bot, 0) + 1
        
        avg_delivery_time = 0.0
        if total > 0:
            avg_delivery_time = sum(log.delivery_time_ms for log in self.notification_log) / total
        
        return {
            "total_sent": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "by_type": by_type,
            "by_priority": by_priority,
            "by_bot": by_bot,
            "avg_delivery_time_ms": avg_delivery_time
        }
    
    def clear_log(self) -> None:
        """Clear notification log"""
        self.notification_log.clear()
    
    # Convenience methods for common notification types
    async def send_entry_notification(
        self,
        plugin_name: str,
        symbol: str,
        direction: str,
        entry_price: float,
        signal_type: str,
        is_v3_dual: bool = True,
        **kwargs
    ) -> Notification:
        """Send trade entry notification"""
        data = {
            "plugin_name": plugin_name,
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "signal_type": signal_type,
            **kwargs
        }
        notification_type = NotificationType.ENTRY_V3_DUAL if is_v3_dual else NotificationType.ENTRY_V6_SINGLE
        return await self.send(notification_type, data)
    
    async def send_exit_notification(
        self,
        plugin_name: str,
        symbol: str,
        direction: str,
        entry_price: float,
        exit_price: float,
        profit: float,
        close_reason: str,
        **kwargs
    ) -> Notification:
        """Send trade exit notification"""
        data = {
            "plugin_name": plugin_name,
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "profit": profit,
            "close_reason": close_reason,
            **kwargs
        }
        notification_type = NotificationType.EXIT_PROFIT if profit > 0 else NotificationType.EXIT_LOSS
        return await self.send(notification_type, data)
    
    async def send_emergency_notification(self, message: str, **kwargs) -> Notification:
        """Send emergency notification"""
        data = {"message": message, **kwargs}
        return await self.send(
            NotificationType.EMERGENCY_STOP,
            data,
            priority=NotificationPriority.CRITICAL
        )
    
    async def send_daily_summary(self, summary_data: Dict[str, Any]) -> Notification:
        """Send daily summary notification"""
        return await self.send(NotificationType.DAILY_SUMMARY, summary_data)
    
    async def send_system_notification(
        self,
        notification_type: NotificationType,
        message: str,
        **kwargs
    ) -> Notification:
        """Send system notification"""
        data = {"message": message, **kwargs}
        return await self.send(notification_type, data)
