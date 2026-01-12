"""
Message Queue Manager - V5 Hybrid Plugin Architecture

Centralized message queue management for the Multi-Telegram system.
Handles message routing, priority management, and delivery tracking.

Part of Document 04: Phase 2 Detailed Plan - Multi-Telegram System
"""

import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable, Deque
from enum import Enum
from dataclasses import dataclass, field
import logging
import uuid

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages for routing."""
    COMMAND = "command"           # User commands (Controller bot)
    ALERT = "alert"               # Trade alerts (Notification bot)
    ENTRY = "entry"               # Entry notifications (Notification bot)
    EXIT = "exit"                 # Exit notifications (Notification bot)
    REPORT = "report"             # Analytics reports (Analytics bot)
    STATS = "stats"               # Statistics (Analytics bot)
    BROADCAST = "broadcast"       # Send to all bots
    SYSTEM = "system"             # System messages (Controller bot)
    ERROR = "error"               # Error notifications (Controller bot)


class DeliveryStatus(Enum):
    """Message delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DROPPED = "dropped"


@dataclass
class QueuedMessage:
    """
    Represents a message in the queue with full metadata.
    
    Attributes:
        id: Unique message identifier
        chat_id: Target chat ID
        text: Message content
        message_type: Type for routing
        priority: Priority level (0-3, higher = more urgent)
        parse_mode: Telegram parse mode
        reply_markup: Optional keyboard markup
        created_at: When message was created
        queued_at: When message was queued
        delivered_at: When message was delivered
        status: Current delivery status
        retries: Number of retry attempts
        max_retries: Maximum retry attempts
        metadata: Additional metadata
    """
    chat_id: str
    text: str
    message_type: MessageType = MessageType.ALERT
    priority: int = 1
    parse_mode: str = "Markdown"
    reply_markup: Optional[Dict] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)
    queued_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    status: DeliveryStatus = DeliveryStatus.PENDING
    retries: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.queued_at is None:
            self.queued_at = datetime.now()
            self.status = DeliveryStatus.QUEUED


class MessageRouter:
    """
    Routes messages to appropriate bots based on message type.
    
    Routing Rules:
    - COMMAND, SYSTEM, ERROR -> Controller Bot
    - ALERT, ENTRY, EXIT -> Notification Bot
    - REPORT, STATS -> Analytics Bot
    - BROADCAST -> All Bots
    """
    
    # Routing map: message_type -> target_bot
    ROUTING_MAP = {
        MessageType.COMMAND: "controller",
        MessageType.SYSTEM: "controller",
        MessageType.ERROR: "controller",
        MessageType.ALERT: "notification",
        MessageType.ENTRY: "notification",
        MessageType.EXIT: "notification",
        MessageType.REPORT: "analytics",
        MessageType.STATS: "analytics",
        MessageType.BROADCAST: "all"
    }
    
    # Content-based routing keywords
    CONTENT_KEYWORDS = {
        "notification": ["buy", "sell", "entry", "exit", "trade", "order", "sl", "tp"],
        "analytics": ["report", "profit", "stats", "daily", "weekly", "performance"],
        "controller": ["status", "error", "warning", "system", "plugin"]
    }
    
    @classmethod
    def get_target_bot(cls, message: QueuedMessage) -> str:
        """
        Determine target bot for a message.
        
        Args:
            message: QueuedMessage to route
            
        Returns:
            Target bot name: "controller", "notification", "analytics", or "all"
        """
        # First check explicit message type
        if message.message_type in cls.ROUTING_MAP:
            return cls.ROUTING_MAP[message.message_type]
        
        # Fall back to content-based routing
        text_lower = message.text.lower()
        
        for bot, keywords in cls.CONTENT_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return bot
        
        # Default to controller
        return "controller"
    
    @classmethod
    def get_priority_for_type(cls, message_type: MessageType) -> int:
        """
        Get default priority for a message type.
        
        Args:
            message_type: Type of message
            
        Returns:
            Priority level (0=LOW, 1=NORMAL, 2=HIGH, 3=CRITICAL)
        """
        priority_map = {
            MessageType.ERROR: 3,      # CRITICAL
            MessageType.ENTRY: 2,      # HIGH
            MessageType.EXIT: 2,       # HIGH
            MessageType.ALERT: 2,      # HIGH
            MessageType.COMMAND: 1,    # NORMAL
            MessageType.SYSTEM: 1,     # NORMAL
            MessageType.BROADCAST: 1,  # NORMAL
            MessageType.REPORT: 0,     # LOW
            MessageType.STATS: 0       # LOW
        }
        return priority_map.get(message_type, 1)


class MessageQueueManager:
    """
    Central message queue manager for Multi-Telegram system.
    
    Features:
    - Centralized queue management
    - Priority-based ordering
    - Message routing
    - Delivery tracking
    - Statistics and monitoring
    
    Usage:
        manager = MessageQueueManager()
        await manager.start()
        await manager.enqueue(message)
        await manager.stop()
    """
    
    def __init__(
        self,
        max_queue_size: int = 500,
        message_ttl_seconds: int = 300,
        cleanup_interval_seconds: int = 60
    ):
        """
        Initialize message queue manager.
        
        Args:
            max_queue_size: Maximum total messages in queue
            message_ttl_seconds: Time-to-live for messages
            cleanup_interval_seconds: Interval for cleanup task
        """
        self.max_queue_size = max_queue_size
        self.message_ttl = timedelta(seconds=message_ttl_seconds)
        self.cleanup_interval = cleanup_interval_seconds
        
        # Priority queues (index = priority level)
        self.queues: List[Deque[QueuedMessage]] = [
            deque() for _ in range(4)  # 0=LOW, 1=NORMAL, 2=HIGH, 3=CRITICAL
        ]
        
        # Delivery tracking
        self.delivered_messages: Dict[str, QueuedMessage] = {}
        self.failed_messages: Dict[str, QueuedMessage] = {}
        
        # Statistics
        self.stats = {
            "total_enqueued": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "total_dropped": 0,
            "total_expired": 0,
            "by_type": {t.value: 0 for t in MessageType},
            "by_bot": {"controller": 0, "notification": 0, "analytics": 0}
        }
        
        # Control
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
        # Callbacks for message delivery
        self._delivery_callbacks: Dict[str, Callable] = {}
        
        logger.info(
            f"MessageQueueManager initialized "
            f"(max_size={max_queue_size}, ttl={message_ttl_seconds}s)"
        )
    
    async def start(self):
        """Start the message queue manager."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("MessageQueueManager started")
    
    async def stop(self):
        """Stop the message queue manager."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("MessageQueueManager stopped")
    
    def register_delivery_callback(self, bot_name: str, callback: Callable):
        """
        Register a callback for message delivery.
        
        Args:
            bot_name: Name of the bot
            callback: Async function to call for delivery
        """
        self._delivery_callbacks[bot_name] = callback
        logger.debug(f"Registered delivery callback for {bot_name}")
    
    async def enqueue(
        self,
        chat_id: str,
        text: str,
        message_type: MessageType = MessageType.ALERT,
        priority: Optional[int] = None,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[QueuedMessage]:
        """
        Add a message to the queue.
        
        Args:
            chat_id: Target chat ID
            text: Message text
            message_type: Type for routing
            priority: Priority level (None = auto from type)
            parse_mode: Telegram parse mode
            reply_markup: Optional keyboard
            metadata: Additional metadata
            
        Returns:
            QueuedMessage if queued, None if dropped
        """
        # Auto-determine priority if not specified
        if priority is None:
            priority = MessageRouter.get_priority_for_type(message_type)
        
        # Clamp priority to valid range
        priority = max(0, min(3, priority))
        
        # Create message
        message = QueuedMessage(
            chat_id=chat_id,
            text=text,
            message_type=message_type,
            priority=priority,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            metadata=metadata or {}
        )
        
        async with self._lock:
            # Check queue size
            total_size = sum(len(q) for q in self.queues)
            
            if total_size >= self.max_queue_size:
                # Try to drop LOW priority messages
                if len(self.queues[0]) > 0:
                    dropped = self.queues[0].popleft()
                    dropped.status = DeliveryStatus.DROPPED
                    self.stats["total_dropped"] += 1
                    logger.warning(f"Dropped LOW priority message: {dropped.id}")
                elif priority == 0:
                    # Don't queue new LOW if full
                    message.status = DeliveryStatus.DROPPED
                    self.stats["total_dropped"] += 1
                    logger.warning(f"Queue full, dropping LOW: {message.id}")
                    return None
            
            # Add to appropriate queue
            self.queues[priority].append(message)
            self.stats["total_enqueued"] += 1
            self.stats["by_type"][message_type.value] += 1
            
            logger.debug(
                f"Enqueued message {message.id} "
                f"(type={message_type.value}, priority={priority})"
            )
            
            return message
    
    async def dequeue(self) -> Optional[QueuedMessage]:
        """
        Get the next message from the queue (highest priority first).
        
        Returns:
            Next message or None if empty
        """
        async with self._lock:
            # Check queues in priority order (3=CRITICAL first)
            for priority in range(3, -1, -1):
                if len(self.queues[priority]) > 0:
                    message = self.queues[priority].popleft()
                    message.status = DeliveryStatus.SENDING
                    return message
            
            return None
    
    async def mark_delivered(self, message: QueuedMessage):
        """Mark a message as delivered."""
        message.status = DeliveryStatus.DELIVERED
        message.delivered_at = datetime.now()
        
        self.delivered_messages[message.id] = message
        self.stats["total_delivered"] += 1
        
        # Track by bot
        target_bot = MessageRouter.get_target_bot(message)
        if target_bot in self.stats["by_bot"]:
            self.stats["by_bot"][target_bot] += 1
        
        logger.debug(f"Message {message.id} delivered")
    
    async def mark_failed(self, message: QueuedMessage, error: str = ""):
        """Mark a message as failed."""
        message.status = DeliveryStatus.FAILED
        message.metadata["error"] = error
        
        self.failed_messages[message.id] = message
        self.stats["total_failed"] += 1
        
        logger.warning(f"Message {message.id} failed: {error}")
    
    async def retry_message(self, message: QueuedMessage) -> bool:
        """
        Retry a failed message.
        
        Args:
            message: Message to retry
            
        Returns:
            True if re-queued, False if max retries exceeded
        """
        message.retries += 1
        
        if message.retries >= message.max_retries:
            await self.mark_failed(message, "Max retries exceeded")
            return False
        
        # Re-queue with same priority
        message.status = DeliveryStatus.QUEUED
        message.queued_at = datetime.now()
        
        async with self._lock:
            self.queues[message.priority].appendleft(message)
        
        logger.debug(
            f"Message {message.id} re-queued "
            f"(retry {message.retries}/{message.max_retries})"
        )
        
        return True
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired messages."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    async def _cleanup_expired(self):
        """Remove expired messages from queues."""
        now = datetime.now()
        expired_count = 0
        
        async with self._lock:
            for priority in range(4):
                # Create new deque without expired messages
                valid_messages = deque()
                
                while len(self.queues[priority]) > 0:
                    message = self.queues[priority].popleft()
                    
                    if now - message.created_at > self.message_ttl:
                        message.status = DeliveryStatus.DROPPED
                        expired_count += 1
                    else:
                        valid_messages.append(message)
                
                self.queues[priority] = valid_messages
        
        if expired_count > 0:
            self.stats["total_expired"] += expired_count
            logger.info(f"Cleaned up {expired_count} expired messages")
    
    def get_queue_size(self) -> Dict[str, int]:
        """Get current queue sizes by priority."""
        return {
            "critical": len(self.queues[3]),
            "high": len(self.queues[2]),
            "normal": len(self.queues[1]),
            "low": len(self.queues[0]),
            "total": sum(len(q) for q in self.queues)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queue_size": self.get_queue_size(),
            "stats": self.stats.copy(),
            "delivered_count": len(self.delivered_messages),
            "failed_count": len(self.failed_messages),
            "running": self._running
        }
    
    def clear_all(self):
        """Clear all queues and tracking."""
        for q in self.queues:
            q.clear()
        self.delivered_messages.clear()
        self.failed_messages.clear()
        logger.info("All queues cleared")


class MessageFormatter:
    """
    Formats messages for different notification types.
    
    Provides consistent formatting for:
    - Trade entries
    - Trade exits
    - Profit booking
    - Re-entries
    - Errors and warnings
    - Reports
    """
    
    @staticmethod
    def format_entry(
        symbol: str,
        direction: str,
        lot_size: float,
        entry_price: float,
        sl_price: float,
        tp_price: float,
        plugin_id: str,
        logic_type: str = "",
        order_type: str = ""
    ) -> str:
        """Format trade entry notification."""
        emoji = "🟢" if direction.upper() == "BUY" else "🔴"
        
        message = (
            f"{emoji} *NEW ENTRY*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Direction:* {direction}\n"
            f"*Lot Size:* {lot_size}\n"
            f"*Entry:* {entry_price}\n"
            f"*SL:* {sl_price}\n"
            f"*TP:* {tp_price}\n"
            f"*Plugin:* {plugin_id}\n"
        )
        
        if logic_type:
            message += f"*Logic:* {logic_type}\n"
        if order_type:
            message += f"*Order:* {order_type}\n"
        
        return message
    
    @staticmethod
    def format_exit(
        symbol: str,
        direction: str,
        lot_size: float,
        entry_price: float,
        exit_price: float,
        pnl: float,
        exit_reason: str,
        plugin_id: str
    ) -> str:
        """Format trade exit notification."""
        emoji = "💰" if pnl >= 0 else "💸"
        pnl_text = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
        
        return (
            f"{emoji} *TRADE CLOSED*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Direction:* {direction}\n"
            f"*Lot Size:* {lot_size}\n"
            f"*Entry:* {entry_price}\n"
            f"*Exit:* {exit_price}\n"
            f"*P/L:* {pnl_text}\n"
            f"*Reason:* {exit_reason}\n"
            f"*Plugin:* {plugin_id}\n"
        )
    
    @staticmethod
    def format_profit_booking(
        symbol: str,
        level: int,
        profit_booked: float,
        orders_closed: int,
        orders_placed: int,
        plugin_id: str
    ) -> str:
        """Format profit booking notification."""
        return (
            f"📈 *PROFIT BOOKED*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Level:* {level}\n"
            f"*Profit:* +${profit_booked:.2f}\n"
            f"*Closed:* {orders_closed} orders\n"
            f"*Placed:* {orders_placed} new orders\n"
            f"*Plugin:* {plugin_id}\n"
        )
    
    @staticmethod
    def format_reentry(
        symbol: str,
        direction: str,
        reentry_type: str,
        level: int,
        plugin_id: str
    ) -> str:
        """Format re-entry notification."""
        return (
            f"🔄 *RE-ENTRY*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Direction:* {direction}\n"
            f"*Type:* {reentry_type}\n"
            f"*Level:* {level}\n"
            f"*Plugin:* {plugin_id}\n"
        )
    
    @staticmethod
    def format_error(
        error_type: str,
        message: str,
        plugin_id: str = "",
        details: str = ""
    ) -> str:
        """Format error notification."""
        error_msg = (
            f"🚨 *ERROR*\n\n"
            f"*Type:* {error_type}\n"
            f"*Message:* {message}\n"
        )
        
        if plugin_id:
            error_msg += f"*Plugin:* {plugin_id}\n"
        if details:
            error_msg += f"*Details:* {details}\n"
        
        return error_msg
    
    @staticmethod
    def format_warning(
        warning_type: str,
        message: str,
        plugin_id: str = ""
    ) -> str:
        """Format warning notification."""
        warning_msg = (
            f"⚠️ *WARNING*\n\n"
            f"*Type:* {warning_type}\n"
            f"*Message:* {message}\n"
        )
        
        if plugin_id:
            warning_msg += f"*Plugin:* {plugin_id}\n"
        
        return warning_msg
    
    @staticmethod
    def format_system_status(
        bot_running: bool,
        uptime_hours: float,
        plugins_active: int,
        plugins_total: int,
        open_trades: int
    ) -> str:
        """Format system status message."""
        status_emoji = "🟢" if bot_running else "🔴"
        
        return (
            f"{status_emoji} *SYSTEM STATUS*\n\n"
            f"*Running:* {'Yes' if bot_running else 'No'}\n"
            f"*Uptime:* {uptime_hours:.1f} hours\n"
            f"*Plugins:* {plugins_active}/{plugins_total} active\n"
            f"*Open Trades:* {open_trades}\n"
        )
