"""
Delivery Manager - Robust Notification Delivery

Document 19: Notification System Specification
Handles delivery with retry logic, rate limiting, and priority queuing.

Features:
- Priority-based queue processing
- Rate limiting (20 msg/min, 30 msg/sec)
- Retry with exponential backoff
- Delivery status tracking
- Failed notification recovery
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import asyncio
import logging
import time
from collections import deque


class DeliveryStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    RATE_LIMITED = "rate_limited"
    CANCELLED = "cancelled"


class DeliveryPriority(Enum):
    """Delivery priority levels"""
    CRITICAL = 5  # Immediate delivery, bypass queue
    HIGH = 4      # Front of queue
    NORMAL = 3    # Standard queue position
    LOW = 2       # Back of queue
    BATCH = 1     # Batch processing, lowest priority


@dataclass
class DeliveryResult:
    """Result of notification delivery attempt"""
    notification_id: str
    status: DeliveryStatus
    delivered_at: Optional[datetime] = None
    attempts: int = 1
    error: Optional[str] = None
    delivery_time_ms: float = 0.0
    target_bot: str = ""
    target_users: List[int] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if delivery was successful"""
        return self.status == DeliveryStatus.DELIVERED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "notification_id": self.notification_id,
            "status": self.status.value,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "attempts": self.attempts,
            "error": self.error,
            "delivery_time_ms": self.delivery_time_ms,
            "target_bot": self.target_bot,
            "target_users": self.target_users,
            "success": self.success
        }


@dataclass
class QueuedNotification:
    """Notification in delivery queue"""
    notification_id: str
    message: str
    target_bot: str
    target_users: List[int]
    priority: DeliveryPriority
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: 'QueuedNotification') -> bool:
        """Compare by priority for queue ordering"""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        return self.created_at < other.created_at


class RateLimiter:
    """
    Rate limiter for notification delivery
    
    Enforces Telegram API limits:
    - 30 messages per second to different chats
    - 20 messages per minute to same chat
    """
    
    def __init__(
        self,
        max_per_second: int = 30,
        max_per_minute: int = 20,
        max_per_minute_per_chat: int = 20
    ):
        self.max_per_second = max_per_second
        self.max_per_minute = max_per_minute
        self.max_per_minute_per_chat = max_per_minute_per_chat
        
        self.sent_timestamps: deque = deque()
        self.sent_per_chat: Dict[str, deque] = {}
        self._lock = asyncio.Lock()
    
    async def acquire(self, chat_id: Optional[str] = None) -> bool:
        """
        Acquire permission to send a message
        
        Args:
            chat_id: Optional chat ID for per-chat limiting
            
        Returns:
            True if allowed, False if rate limited
        """
        async with self._lock:
            now = time.time()
            
            # Clean old timestamps
            self._clean_old_timestamps(now)
            
            # Check global rate limits
            if len(self.sent_timestamps) >= self.max_per_second:
                # Check if oldest is within last second
                if self.sent_timestamps and now - self.sent_timestamps[0] < 1:
                    return False
            
            # Check per-minute limit
            minute_count = sum(1 for t in self.sent_timestamps if now - t < 60)
            if minute_count >= self.max_per_minute:
                return False
            
            # Check per-chat limit
            if chat_id:
                if chat_id not in self.sent_per_chat:
                    self.sent_per_chat[chat_id] = deque()
                
                chat_timestamps = self.sent_per_chat[chat_id]
                chat_minute_count = sum(1 for t in chat_timestamps if now - t < 60)
                
                if chat_minute_count >= self.max_per_minute_per_chat:
                    return False
                
                chat_timestamps.append(now)
            
            # Record timestamp
            self.sent_timestamps.append(now)
            return True
    
    def _clean_old_timestamps(self, now: float) -> None:
        """Remove timestamps older than 1 minute"""
        # Clean global timestamps
        while self.sent_timestamps and now - self.sent_timestamps[0] > 60:
            self.sent_timestamps.popleft()
        
        # Clean per-chat timestamps
        for chat_id in list(self.sent_per_chat.keys()):
            chat_timestamps = self.sent_per_chat[chat_id]
            while chat_timestamps and now - chat_timestamps[0] > 60:
                chat_timestamps.popleft()
            
            if not chat_timestamps:
                del self.sent_per_chat[chat_id]
    
    async def wait_for_slot(self, chat_id: Optional[str] = None, timeout: float = 30.0) -> bool:
        """
        Wait until a slot is available
        
        Args:
            chat_id: Optional chat ID for per-chat limiting
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if slot acquired, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.acquire(chat_id):
                return True
            await asyncio.sleep(0.1)
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        now = time.time()
        self._clean_old_timestamps(now)
        
        return {
            "messages_last_second": sum(1 for t in self.sent_timestamps if now - t < 1),
            "messages_last_minute": len(self.sent_timestamps),
            "active_chats": len(self.sent_per_chat),
            "max_per_second": self.max_per_second,
            "max_per_minute": self.max_per_minute
        }


class RetryPolicy:
    """
    Retry policy for failed deliveries
    
    Implements exponential backoff with jitter.
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: float = 0.1
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def should_retry(self, attempts: int, error: Optional[str] = None) -> bool:
        """Check if should retry based on attempts and error type"""
        if attempts >= self.max_attempts:
            return False
        
        # Don't retry certain errors
        if error:
            non_retryable = [
                "chat not found",
                "user blocked",
                "invalid token",
                "unauthorized",
                "forbidden"
            ]
            for err in non_retryable:
                if err.lower() in error.lower():
                    return False
        
        return True
    
    def get_delay(self, attempts: int) -> float:
        """Calculate delay before next retry"""
        import random
        
        delay = self.base_delay * (self.exponential_base ** (attempts - 1))
        delay = min(delay, self.max_delay)
        
        # Add jitter
        jitter_amount = delay * self.jitter
        delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, delay)


class NotificationQueueManager:
    """
    Notification Queue Manager
    
    Manages priority queue for notification delivery with rate limiting.
    """
    
    def __init__(
        self,
        max_per_minute: int = 20,
        max_queue_size: int = 1000
    ):
        self.max_per_minute = max_per_minute
        self.max_queue_size = max_queue_size
        
        self.queue: List[QueuedNotification] = []
        self.processing = False
        self.rate_limiter = RateLimiter(max_per_minute=max_per_minute)
        self.retry_policy = RetryPolicy()
        
        self._send_callback: Optional[Callable] = None
        self._process_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            "total_queued": 0,
            "total_sent": 0,
            "total_failed": 0,
            "total_retried": 0
        }
    
    def set_send_callback(self, callback: Callable) -> None:
        """Set callback for sending notifications"""
        self._send_callback = callback
    
    async def add(self, notification: QueuedNotification) -> bool:
        """
        Add notification to queue
        
        Args:
            notification: Notification to queue
            
        Returns:
            True if added, False if queue full
        """
        if len(self.queue) >= self.max_queue_size:
            self.logger.warning("Notification queue full, dropping notification")
            return False
        
        # Insert in priority order
        self.queue.append(notification)
        self.queue.sort()
        
        self.stats["total_queued"] += 1
        return True
    
    async def add_message(
        self,
        notification_id: str,
        message: str,
        target_bot: str,
        priority: DeliveryPriority = DeliveryPriority.NORMAL,
        target_users: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add message to queue
        
        Args:
            notification_id: Unique notification ID
            message: Message content
            target_bot: Target bot name
            priority: Delivery priority
            target_users: Optional list of user IDs
            metadata: Optional metadata
            
        Returns:
            True if added successfully
        """
        notification = QueuedNotification(
            notification_id=notification_id,
            message=message,
            target_bot=target_bot,
            target_users=target_users or [],
            priority=priority,
            metadata=metadata or {}
        )
        return await self.add(notification)
    
    async def process(self) -> None:
        """Process queue with rate limiting"""
        self.processing = True
        
        while self.processing:
            if not self.queue:
                await asyncio.sleep(0.1)
                continue
            
            # Get next notification
            notification = self.queue.pop(0)
            
            # Check scheduled time
            if notification.scheduled_at and notification.scheduled_at > datetime.now():
                # Re-queue for later
                self.queue.append(notification)
                self.queue.sort()
                await asyncio.sleep(0.1)
                continue
            
            # Wait for rate limit slot
            if not await self.rate_limiter.wait_for_slot(notification.target_bot, timeout=5.0):
                # Re-queue with delay
                notification.scheduled_at = datetime.now() + timedelta(seconds=1)
                self.queue.append(notification)
                self.queue.sort()
                continue
            
            # Send notification
            notification.attempts += 1
            
            try:
                if self._send_callback:
                    await self._send_callback(notification)
                self.stats["total_sent"] += 1
                
            except Exception as e:
                notification.last_error = str(e)
                self.logger.error(f"Notification send failed: {e}")
                
                # Check if should retry
                if self.retry_policy.should_retry(notification.attempts, str(e)):
                    delay = self.retry_policy.get_delay(notification.attempts)
                    notification.scheduled_at = datetime.now() + timedelta(seconds=delay)
                    self.queue.append(notification)
                    self.queue.sort()
                    self.stats["total_retried"] += 1
                else:
                    self.stats["total_failed"] += 1
    
    def start_processing(self) -> None:
        """Start queue processing in background"""
        if self._process_task is None or self._process_task.done():
            self._process_task = asyncio.create_task(self.process())
    
    def stop_processing(self) -> None:
        """Stop queue processing"""
        self.processing = False
        if self._process_task:
            self._process_task.cancel()
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return len(self.queue)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            **self.stats,
            "queue_size": len(self.queue),
            "processing": self.processing,
            "rate_limiter": self.rate_limiter.get_stats()
        }
    
    def clear_queue(self) -> int:
        """Clear all queued notifications"""
        count = len(self.queue)
        self.queue.clear()
        return count


class DeliveryManager:
    """
    Delivery Manager
    
    Manages notification delivery with retry, rate limiting, and tracking.
    """
    
    def __init__(self, telegram_manager=None):
        self.telegram = telegram_manager
        self.queue_manager = NotificationQueueManager()
        self.rate_limiter = RateLimiter()
        self.retry_policy = RetryPolicy()
        
        self.delivery_history: List[DeliveryResult] = []
        self.max_history_size = 1000
        
        self.logger = logging.getLogger(__name__)
        self._running = False
    
    async def deliver(
        self,
        notification_id: str,
        message: str,
        target_bot: str,
        target_users: Optional[List[int]] = None,
        priority: DeliveryPriority = DeliveryPriority.NORMAL,
        use_queue: bool = True
    ) -> DeliveryResult:
        """
        Deliver notification
        
        Args:
            notification_id: Unique notification ID
            message: Message content
            target_bot: Target bot name
            target_users: Optional list of user IDs
            priority: Delivery priority
            use_queue: Whether to use queue (False for immediate)
            
        Returns:
            DeliveryResult with status
        """
        start_time = datetime.now()
        
        # Critical priority bypasses queue
        if priority == DeliveryPriority.CRITICAL or not use_queue:
            return await self._deliver_immediate(
                notification_id, message, target_bot, target_users
            )
        
        # Queue for later delivery
        success = await self.queue_manager.add_message(
            notification_id=notification_id,
            message=message,
            target_bot=target_bot,
            priority=priority,
            target_users=target_users
        )
        
        result = DeliveryResult(
            notification_id=notification_id,
            status=DeliveryStatus.QUEUED if success else DeliveryStatus.FAILED,
            target_bot=target_bot,
            target_users=target_users or [],
            error="Queue full" if not success else None
        )
        
        self._record_delivery(result)
        return result
    
    async def _deliver_immediate(
        self,
        notification_id: str,
        message: str,
        target_bot: str,
        target_users: Optional[List[int]] = None
    ) -> DeliveryResult:
        """Deliver notification immediately with retry"""
        start_time = datetime.now()
        attempts = 0
        last_error = None
        
        while True:
            attempts += 1
            
            # Wait for rate limit
            if not await self.rate_limiter.wait_for_slot(target_bot, timeout=10.0):
                result = DeliveryResult(
                    notification_id=notification_id,
                    status=DeliveryStatus.RATE_LIMITED,
                    attempts=attempts,
                    target_bot=target_bot,
                    target_users=target_users or [],
                    error="Rate limit exceeded"
                )
                self._record_delivery(result)
                return result
            
            try:
                # Send to bot
                if self.telegram:
                    if target_bot == "broadcast":
                        await self.telegram.broadcast(message)
                    else:
                        await self.telegram.route_message(target_bot, message)
                    
                    # Send to specific users
                    if target_users:
                        await self.telegram.send_to_users(target_users, message)
                
                # Success
                delivery_time = (datetime.now() - start_time).total_seconds() * 1000
                
                result = DeliveryResult(
                    notification_id=notification_id,
                    status=DeliveryStatus.DELIVERED,
                    delivered_at=datetime.now(),
                    attempts=attempts,
                    delivery_time_ms=delivery_time,
                    target_bot=target_bot,
                    target_users=target_users or []
                )
                self._record_delivery(result)
                return result
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Delivery attempt {attempts} failed: {e}")
                
                if not self.retry_policy.should_retry(attempts, last_error):
                    break
                
                delay = self.retry_policy.get_delay(attempts)
                await asyncio.sleep(delay)
        
        # All retries failed
        delivery_time = (datetime.now() - start_time).total_seconds() * 1000
        
        result = DeliveryResult(
            notification_id=notification_id,
            status=DeliveryStatus.FAILED,
            attempts=attempts,
            error=last_error,
            delivery_time_ms=delivery_time,
            target_bot=target_bot,
            target_users=target_users or []
        )
        self._record_delivery(result)
        return result
    
    def _record_delivery(self, result: DeliveryResult) -> None:
        """Record delivery result in history"""
        self.delivery_history.append(result)
        
        # Trim history if needed
        if len(self.delivery_history) > self.max_history_size:
            self.delivery_history = self.delivery_history[-self.max_history_size:]
    
    def start(self) -> None:
        """Start delivery manager"""
        self._running = True
        self.queue_manager.start_processing()
    
    def stop(self) -> None:
        """Stop delivery manager"""
        self._running = False
        self.queue_manager.stop_processing()
    
    def get_delivery_history(self, limit: int = 100) -> List[DeliveryResult]:
        """Get recent delivery history"""
        return self.delivery_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        total = len(self.delivery_history)
        delivered = sum(1 for r in self.delivery_history if r.status == DeliveryStatus.DELIVERED)
        failed = sum(1 for r in self.delivery_history if r.status == DeliveryStatus.FAILED)
        
        avg_delivery_time = 0.0
        if delivered > 0:
            avg_delivery_time = sum(
                r.delivery_time_ms for r in self.delivery_history 
                if r.status == DeliveryStatus.DELIVERED
            ) / delivered
        
        return {
            "total_deliveries": total,
            "delivered": delivered,
            "failed": failed,
            "success_rate": (delivered / total * 100) if total > 0 else 0,
            "avg_delivery_time_ms": avg_delivery_time,
            "queue_stats": self.queue_manager.get_stats(),
            "rate_limiter_stats": self.rate_limiter.get_stats(),
            "running": self._running
        }
    
    def clear_history(self) -> None:
        """Clear delivery history"""
        self.delivery_history.clear()
