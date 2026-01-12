"""
Multi-Telegram Manager - V5 Hybrid Plugin Architecture

Enhanced manager for 3 specialized Telegram bots with rate limiting,
message queue management, and priority routing.

Bots:
1. Controller Bot: Commands and Admin
2. Notification Bot: Trade Alerts
3. Analytics Bot: Reports

Part of Document 04: Phase 2 Detailed Plan - Multi-Telegram System
"""

from typing import Dict, Any, Optional, List, Callable
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Import rate limiter and message queue (lazy import to avoid circular deps)
try:
    from src.telegram.rate_limiter import (
        TelegramRateLimiter,
        ThrottledMessage,
        MessagePriority,
        RateLimitMonitor
    )
    from src.telegram.message_queue import (
        MessageQueueManager,
        MessageType,
        MessageRouter,
        MessageFormatter,
        QueuedMessage
    )
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    logger.warning("Rate limiting modules not available, using basic mode")

# Try to import TelegramBot from modules
try:
    from src.modules.telegram_bot import TelegramBot
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False
    TelegramBot = None
    logger.warning("TelegramBot module not available")


class MultiTelegramManager:
    """
    Enhanced Multi-Telegram Manager with rate limiting and message queue.
    
    Manages 3 specialized Telegram bots:
    1. Controller Bot: Commands, admin, system messages
    2. Notification Bot: Trade alerts, entries, exits
    3. Analytics Bot: Reports, statistics
    
    Features:
    - Rate limiting per bot (20 msg/min, 30 msg/sec)
    - Priority-based message queue
    - Automatic routing based on message type
    - Fallback to main bot if specialized bot unavailable
    - Error handling and retry logic
    - Statistics tracking
    
    Usage:
        manager = MultiTelegramManager(config)
        await manager.start()
        await manager.send_notification("Trade opened", priority=MessagePriority.HIGH)
        await manager.stop()
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Multi-Telegram Manager.
        
        Args:
            config: Configuration dictionary with tokens and settings
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MultiTelegramManager")
        
        # Load tokens
        self.main_token = config.get("telegram_token")
        self.controller_token = config.get("telegram_controller_token")
        self.notification_token = config.get("telegram_notification_token")
        self.analytics_token = config.get("telegram_analytics_token")
        
        self.chat_id = config.get("telegram_chat_id")
        
        # Initialize bots (with fallback to main bot)
        self._init_bots()
        
        # Initialize rate limiters (if available)
        self._init_rate_limiters()
        
        # Initialize message queue manager
        self._init_message_queue()
        
        # State tracking
        self.is_running = False
        self.started_at: Optional[datetime] = None
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_failed": 0,
            "fallbacks_used": 0,
            "by_bot": {
                "controller": 0,
                "notification": 0,
                "analytics": 0
            }
        }
        
        self.logger.info("MultiTelegramManager initialized")
        self._log_bot_status()
    
    def _init_bots(self):
        """Initialize Telegram bot instances."""
        if TELEGRAM_BOT_AVAILABLE and TelegramBot:
            self.main_bot = TelegramBot(self.main_token) if self.main_token else None
            self.controller_bot = TelegramBot(self.controller_token) if self.controller_token else self.main_bot
            self.notification_bot = TelegramBot(self.notification_token) if self.notification_token else self.main_bot
            self.analytics_bot = TelegramBot(self.analytics_token) if self.analytics_token else self.main_bot
        else:
            # Placeholder for testing without actual Telegram
            self.main_bot = None
            self.controller_bot = None
            self.notification_bot = None
            self.analytics_bot = None
    
    def _init_rate_limiters(self):
        """Initialize rate limiters for each bot."""
        if RATE_LIMITING_AVAILABLE:
            self.controller_limiter = TelegramRateLimiter(
                bot_name="Controller",
                max_per_minute=20,
                max_per_second=30,
                max_queue_size=100
            )
            
            self.notification_limiter = TelegramRateLimiter(
                bot_name="Notification",
                max_per_minute=20,
                max_per_second=30,
                max_queue_size=100
            )
            
            self.analytics_limiter = TelegramRateLimiter(
                bot_name="Analytics",
                max_per_minute=15,  # Lower for reports
                max_per_second=20,
                max_queue_size=50
            )
            
            # Hook send functions
            self._hook_rate_limiters()
            
            # Initialize monitor
            self.rate_monitor = RateLimitMonitor()
            
            self.logger.info("Rate limiters initialized")
        else:
            self.controller_limiter = None
            self.notification_limiter = None
            self.analytics_limiter = None
            self.rate_monitor = None
    
    def _init_message_queue(self):
        """Initialize message queue manager."""
        if RATE_LIMITING_AVAILABLE:
            self.message_queue = MessageQueueManager(
                max_queue_size=500,
                message_ttl_seconds=300
            )
            self.logger.info("Message queue manager initialized")
        else:
            self.message_queue = None
    
    def _hook_rate_limiters(self):
        """Connect rate limiters to actual bot send methods."""
        if not RATE_LIMITING_AVAILABLE:
            return
        
        async def controller_send(msg: ThrottledMessage):
            if self.controller_bot:
                self.controller_bot.send_message(msg.text)
                self.stats["by_bot"]["controller"] += 1
        
        async def notification_send(msg: ThrottledMessage):
            if self.notification_bot:
                self.notification_bot.send_message(msg.text)
                self.stats["by_bot"]["notification"] += 1
        
        async def analytics_send(msg: ThrottledMessage):
            if self.analytics_bot:
                self.analytics_bot.send_message(msg.text)
                self.stats["by_bot"]["analytics"] += 1
        
        self.controller_limiter.set_send_function(controller_send)
        self.notification_limiter.set_send_function(notification_send)
        self.analytics_limiter.set_send_function(analytics_send)
    
    def _log_bot_status(self):
        """Log the status of each bot."""
        if self.controller_token:
            self.logger.info("Controller Bot: Active (dedicated token)")
        else:
            self.logger.info("Controller Bot: Using main token (fallback)")
        
        if self.notification_token:
            self.logger.info("Notification Bot: Active (dedicated token)")
        else:
            self.logger.info("Notification Bot: Using main token (fallback)")
        
        if self.analytics_token:
            self.logger.info("Analytics Bot: Active (dedicated token)")
        else:
            self.logger.info("Analytics Bot: Using main token (fallback)")
    
    async def start(self):
        """Start the Multi-Telegram Manager and all rate limiters."""
        if self.is_running:
            self.logger.warning("MultiTelegramManager already running")
            return
        
        self.is_running = True
        self.started_at = datetime.now()
        
        # Start rate limiters
        if RATE_LIMITING_AVAILABLE:
            await self.controller_limiter.start()
            await self.notification_limiter.start()
            await self.analytics_limiter.start()
            await self.message_queue.start()
        
        self.logger.info("MultiTelegramManager started")
    
    async def stop(self):
        """Stop the Multi-Telegram Manager and all rate limiters."""
        self.is_running = False
        
        # Stop rate limiters
        if RATE_LIMITING_AVAILABLE:
            await self.controller_limiter.stop()
            await self.notification_limiter.stop()
            await self.analytics_limiter.stop()
            await self.message_queue.stop()
        
        self.logger.info("MultiTelegramManager stopped")
    
    # ==========================================
    # SYNCHRONOUS API (Backward Compatible)
    # ==========================================
    
    def route_message(self, message_type: str, content: str, parse_mode: str = "Markdown"):
        """
        Routes message to appropriate bot based on type (synchronous).
        
        Args:
            message_type: 'command', 'alert', 'report', 'broadcast'
            content: Message text
            parse_mode: Telegram parse mode
        """
        if not content:
            return
        
        try:
            if message_type == "command":
                self._send_to_controller(content)
            elif message_type == "alert":
                self._send_to_notification(content)
            elif message_type == "report":
                self._send_to_analytics(content)
            elif message_type == "broadcast":
                self._broadcast(content)
            else:
                self._send_to_controller(content)
                
            self.stats["messages_sent"] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to route message ({message_type}): {e}")
            self.stats["messages_failed"] += 1
            self._fallback_send(content)
    
    def _send_to_controller(self, content: str):
        """Send message via Controller bot."""
        if self.controller_bot:
            self.controller_bot.send_message(content)
            self.stats["by_bot"]["controller"] += 1
    
    def _send_to_notification(self, content: str):
        """Send message via Notification bot."""
        if self.notification_bot:
            self.notification_bot.send_message(content)
            self.stats["by_bot"]["notification"] += 1
    
    def _send_to_analytics(self, content: str):
        """Send message via Analytics bot."""
        if self.analytics_bot:
            self.analytics_bot.send_message(content)
            self.stats["by_bot"]["analytics"] += 1
    
    def _broadcast(self, content: str):
        """Send message to all bots."""
        bots = [self.controller_bot, self.notification_bot, self.analytics_bot]
        unique_bots = list(set([b for b in bots if b]))
        
        for bot in unique_bots:
            try:
                bot.send_message(content)
            except Exception as e:
                self.logger.error(f"Broadcast failed for a bot: {e}")
    
    def _fallback_send(self, content: str):
        """Emergency fallback to main bot."""
        if self.main_bot and self.main_bot != self.controller_bot:
            try:
                self.main_bot.send_message(f"⚠️ ROUTING ERROR: {content}")
                self.stats["fallbacks_used"] += 1
            except Exception:
                pass
    
    def send_alert(self, message: str):
        """Helper for trade alerts (synchronous)."""
        self.route_message("alert", message)
    
    def send_report(self, message: str):
        """Helper for reports (synchronous)."""
        self.route_message("report", message)
    
    def send_admin_message(self, message: str):
        """Helper for admin/system messages (synchronous)."""
        self.route_message("command", message)
    
    # ==========================================
    # ASYNCHRONOUS API (Rate-Limited)
    # ==========================================
    
    async def send_controller_message(
        self,
        text: str,
        priority: Optional[int] = None,
        parse_mode: str = "Markdown"
    ):
        """
        Send message via Controller bot (rate-limited).
        
        Args:
            text: Message text
            priority: Priority level (0-3, None=auto)
            parse_mode: Telegram parse mode
        """
        if not RATE_LIMITING_AVAILABLE or not self.controller_limiter:
            self._send_to_controller(text)
            return
        
        if priority is None:
            priority = 1  # NORMAL
        
        msg_priority = self._int_to_priority(priority)
        
        message = ThrottledMessage(
            chat_id=str(self.chat_id),
            text=text,
            priority=msg_priority,
            parse_mode=parse_mode
        )
        
        await self.controller_limiter.enqueue(message)
    
    async def send_notification(
        self,
        text: str,
        priority: Optional[int] = None,
        parse_mode: str = "Markdown"
    ):
        """
        Send notification via Notification bot (rate-limited).
        
        Args:
            text: Message text
            priority: Priority level (0-3, None=HIGH for alerts)
            parse_mode: Telegram parse mode
        """
        if not RATE_LIMITING_AVAILABLE or not self.notification_limiter:
            self._send_to_notification(text)
            return
        
        if priority is None:
            priority = 2  # HIGH for alerts
        
        msg_priority = self._int_to_priority(priority)
        
        message = ThrottledMessage(
            chat_id=str(self.chat_id),
            text=text,
            priority=msg_priority,
            parse_mode=parse_mode
        )
        
        await self.notification_limiter.enqueue(message)
    
    async def send_analytics_report(
        self,
        text: str,
        priority: Optional[int] = None,
        parse_mode: str = "Markdown"
    ):
        """
        Send report via Analytics bot (rate-limited).
        
        Args:
            text: Message text
            priority: Priority level (0-3, None=LOW for reports)
            parse_mode: Telegram parse mode
        """
        if not RATE_LIMITING_AVAILABLE or not self.analytics_limiter:
            self._send_to_analytics(text)
            return
        
        if priority is None:
            priority = 0  # LOW for reports
        
        msg_priority = self._int_to_priority(priority)
        
        message = ThrottledMessage(
            chat_id=str(self.chat_id),
            text=text,
            priority=msg_priority,
            parse_mode=parse_mode
        )
        
        await self.analytics_limiter.enqueue(message)
    
    async def send_entry_alert(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        entry_price: float,
        sl_price: float,
        tp_price: float,
        plugin_id: str,
        logic_type: str = "",
        order_type: str = ""
    ):
        """
        Send formatted trade entry alert.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            lot_size: Position size
            entry_price: Entry price
            sl_price: Stop loss price
            tp_price: Take profit price
            plugin_id: Plugin identifier
            logic_type: Logic type (optional)
            order_type: Order type (optional)
        """
        if RATE_LIMITING_AVAILABLE:
            text = MessageFormatter.format_entry(
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_price=tp_price,
                plugin_id=plugin_id,
                logic_type=logic_type,
                order_type=order_type
            )
        else:
            emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            text = (
                f"{emoji} *NEW ENTRY*\n\n"
                f"*Symbol:* {symbol}\n"
                f"*Direction:* {direction}\n"
                f"*Lot Size:* {lot_size}\n"
                f"*Entry:* {entry_price}\n"
                f"*SL:* {sl_price}\n"
                f"*TP:* {tp_price}\n"
                f"*Plugin:* {plugin_id}\n"
            )
        
        await self.send_notification(text, priority=2)  # HIGH
    
    async def send_exit_alert(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        entry_price: float,
        exit_price: float,
        pnl: float,
        exit_reason: str,
        plugin_id: str
    ):
        """
        Send formatted trade exit alert.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            lot_size: Position size
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/Loss
            exit_reason: Reason for exit
            plugin_id: Plugin identifier
        """
        if RATE_LIMITING_AVAILABLE:
            text = MessageFormatter.format_exit(
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                entry_price=entry_price,
                exit_price=exit_price,
                pnl=pnl,
                exit_reason=exit_reason,
                plugin_id=plugin_id
            )
        else:
            emoji = "💰" if pnl >= 0 else "💸"
            pnl_text = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            text = (
                f"{emoji} *TRADE CLOSED*\n\n"
                f"*Symbol:* {symbol}\n"
                f"*Direction:* {direction}\n"
                f"*P/L:* {pnl_text}\n"
                f"*Plugin:* {plugin_id}\n"
            )
        
        priority = 3 if pnl < 0 else 2  # CRITICAL for losses, HIGH for wins
        await self.send_notification(text, priority=priority)
    
    async def send_error_alert(
        self,
        error_type: str,
        message: str,
        plugin_id: str = "",
        details: str = ""
    ):
        """
        Send error notification.
        
        Args:
            error_type: Type of error
            message: Error message
            plugin_id: Related plugin (optional)
            details: Additional details (optional)
        """
        if RATE_LIMITING_AVAILABLE:
            text = MessageFormatter.format_error(
                error_type=error_type,
                message=message,
                plugin_id=plugin_id,
                details=details
            )
        else:
            text = (
                f"🚨 *ERROR*\n\n"
                f"*Type:* {error_type}\n"
                f"*Message:* {message}\n"
            )
            if plugin_id:
                text += f"*Plugin:* {plugin_id}\n"
        
        await self.send_controller_message(text, priority=3)  # CRITICAL
    
    def _int_to_priority(self, priority: int) -> 'MessagePriority':
        """Convert integer priority to MessagePriority enum."""
        if not RATE_LIMITING_AVAILABLE:
            return None
        
        priority = max(0, min(3, priority))
        priority_map = {
            0: MessagePriority.LOW,
            1: MessagePriority.NORMAL,
            2: MessagePriority.HIGH,
            3: MessagePriority.CRITICAL
        }
        return priority_map[priority]
    
    # ==========================================
    # MONITORING & STATISTICS
    # ==========================================
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get statistics from all rate limiters."""
        if not RATE_LIMITING_AVAILABLE:
            return {"error": "Rate limiting not available"}
        
        return {
            "controller": self.controller_limiter.get_stats(),
            "notification": self.notification_limiter.get_stats(),
            "analytics": self.analytics_limiter.get_stats()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all bots and rate limiters."""
        health = {
            "is_running": self.is_running,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "bots": {
                "controller": self.controller_bot is not None,
                "notification": self.notification_bot is not None,
                "analytics": self.analytics_bot is not None,
                "main": self.main_bot is not None
            },
            "stats": self.stats.copy()
        }
        
        if RATE_LIMITING_AVAILABLE and self.rate_monitor:
            limiters = {
                "controller": self.controller_limiter,
                "notification": self.notification_limiter,
                "analytics": self.analytics_limiter
            }
            health["rate_limit_health"] = self.rate_monitor.check_health(limiters)
        
        return health
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all statistics."""
        return {
            "manager_stats": self.stats.copy(),
            "rate_limit_stats": self.get_rate_limit_stats() if RATE_LIMITING_AVAILABLE else {},
            "queue_stats": self.message_queue.get_stats() if self.message_queue else {}
        }
