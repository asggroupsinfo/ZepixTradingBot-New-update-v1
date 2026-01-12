"""
Telegram Rate Limiter - V5 Hybrid Plugin Architecture

Rate limiting system to prevent Telegram API violations when using 3 simultaneous bots.

Telegram API Limits:
- 30 messages/second per bot (hard limit)
- 20 messages/minute to same chat (recommended)
- 429 Too Many Requests error on violation

Part of Document 04: Phase 2 Detailed Plan - Multi-Telegram System
"""

import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, Deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels for queue ordering."""
    LOW = 0       # Daily stats, non-urgent info
    NORMAL = 1    # Regular trade notifications
    HIGH = 2      # Entry/Exit alerts
    CRITICAL = 3  # Errors, stop-loss hits, system alerts


class ThrottledMessage:
    """
    Represents a queued message with priority and metadata.
    
    Attributes:
        chat_id: Target chat ID
        text: Message text content
        priority: Message priority level
        parse_mode: Telegram parse mode (HTML/Markdown)
        reply_markup: Optional keyboard markup
        timestamp: When the message was queued
        retries: Number of send attempts
        max_retries: Maximum retry attempts
    """
    
    def __init__(
        self,
        chat_id: str,
        text: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Dict] = None,
        timestamp: Optional[datetime] = None
    ):
        self.chat_id = chat_id
        self.text = text
        self.priority = priority
        self.parse_mode = parse_mode
        self.reply_markup = reply_markup
        self.timestamp = timestamp or datetime.now()
        self.retries = 0
        self.max_retries = 3
    
    def __repr__(self) -> str:
        return (
            f"ThrottledMessage(chat_id={self.chat_id}, "
            f"priority={self.priority.name}, "
            f"text={self.text[:30]}...)"
        )


class TelegramRateLimiter:
    """
    Rate limiter for a single Telegram bot.
    
    Enforces Telegram API limits:
    - max_per_minute: Messages per minute (default 20)
    - max_per_second: Messages per second (default 30)
    
    Features:
    - Priority-based queue (CRITICAL > HIGH > NORMAL > LOW)
    - Automatic overflow handling (drops LOW priority first)
    - Statistics tracking
    - Async queue processor
    
    Usage:
        limiter = TelegramRateLimiter("ControllerBot")
        await limiter.start()
        await limiter.enqueue(message)
        await limiter.stop()
    """
    
    def __init__(
        self,
        bot_name: str,
        max_per_minute: int = 20,
        max_per_second: int = 30,
        max_queue_size: int = 100
    ):
        """
        Initialize rate limiter.
        
        Args:
            bot_name: Name of the bot (for logging)
            max_per_minute: Maximum messages per minute
            max_per_second: Maximum messages per second
            max_queue_size: Maximum total queue size
        """
        self.bot_name = bot_name
        self.max_per_minute = max_per_minute
        self.max_per_second = max_per_second
        self.max_queue_size = max_queue_size
        
        # Priority-based message queues
        self.queue_critical: Deque[ThrottledMessage] = deque()
        self.queue_high: Deque[ThrottledMessage] = deque()
        self.queue_normal: Deque[ThrottledMessage] = deque()
        self.queue_low: Deque[ThrottledMessage] = deque()
        
        # Rate tracking (timestamps of sent messages)
        self.sent_times_minute: Deque[datetime] = deque()
        self.sent_times_second: Deque[datetime] = deque()
        
        # Statistics
        self.stats = {
            "total_sent": 0,
            "total_queued": 0,
            "total_dropped": 0,
            "total_rate_limited": 0,
            "total_retries": 0,
            "total_failures": 0
        }
        
        # Control flags
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
        # Send function (to be hooked by MultiTelegramManager)
        self._send_function: Optional[Callable] = None
        
        logger.info(
            f"TelegramRateLimiter initialized for {bot_name} "
            f"(max {max_per_minute}/min, {max_per_second}/sec)"
        )
    
    async def start(self):
        """Start the rate limiter queue processor."""
        if self._running:
            logger.warning(f"{self.bot_name} rate limiter already running")
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_queue())
        logger.info(f"{self.bot_name} rate limiter started")
    
    async def stop(self):
        """Stop the rate limiter queue processor."""
        self._running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
            self._processor_task = None
        
        logger.info(f"{self.bot_name} rate limiter stopped")
    
    def set_send_function(self, func: Callable):
        """
        Set the function to use for sending messages.
        
        Args:
            func: Async function that takes ThrottledMessage and sends it
        """
        self._send_function = func
    
    async def enqueue(self, message: ThrottledMessage) -> bool:
        """
        Add a message to the queue.
        
        Args:
            message: ThrottledMessage to queue
            
        Returns:
            True if queued successfully, False if dropped
        """
        async with self._lock:
            # Select queue based on priority
            queue = self._get_queue_for_priority(message.priority)
            
            # Check total queue size
            total_queued = self._get_total_queue_size()
            
            if total_queued >= self.max_queue_size:
                # Try to drop LOW priority messages first
                if len(self.queue_low) > 0:
                    dropped = self.queue_low.popleft()
                    self.stats["total_dropped"] += 1
                    logger.warning(
                        f"{self.bot_name}: Dropped LOW priority message to make room: "
                        f"{dropped.text[:50]}..."
                    )
                elif message.priority == MessagePriority.LOW:
                    # Don't queue new LOW priority if queue is full
                    self.stats["total_dropped"] += 1
                    logger.warning(
                        f"{self.bot_name}: Queue full, dropping LOW priority: "
                        f"{message.text[:50]}..."
                    )
                    return False
                # For higher priorities, we still queue (may exceed max temporarily)
            
            # Enqueue the message
            queue.append(message)
            self.stats["total_queued"] += 1
            
            logger.debug(
                f"{self.bot_name}: Queued {message.priority.name} message "
                f"(queue size: {self._get_total_queue_size()})"
            )
            
            return True
    
    def _get_queue_for_priority(self, priority: MessagePriority) -> Deque[ThrottledMessage]:
        """Get the appropriate queue for a priority level."""
        if priority == MessagePriority.CRITICAL:
            return self.queue_critical
        elif priority == MessagePriority.HIGH:
            return self.queue_high
        elif priority == MessagePriority.NORMAL:
            return self.queue_normal
        else:
            return self.queue_low
    
    def _get_total_queue_size(self) -> int:
        """Get total number of messages across all queues."""
        return (
            len(self.queue_critical) +
            len(self.queue_high) +
            len(self.queue_normal) +
            len(self.queue_low)
        )
    
    def _can_send(self) -> bool:
        """
        Check if we can send a message now based on rate limits.
        
        Returns:
            True if within rate limits, False otherwise
        """
        now = datetime.now()
        
        # Clean old timestamps
        cutoff_second = now - timedelta(seconds=1)
        cutoff_minute = now - timedelta(seconds=60)
        
        while self.sent_times_second and self.sent_times_second[0] < cutoff_second:
            self.sent_times_second.popleft()
        
        while self.sent_times_minute and self.sent_times_minute[0] < cutoff_minute:
            self.sent_times_minute.popleft()
        
        # Check per-second limit
        if len(self.sent_times_second) >= self.max_per_second:
            return False
        
        # Check per-minute limit
        if len(self.sent_times_minute) >= self.max_per_minute:
            return False
        
        return True
    
    def _record_send(self):
        """Record that a message was sent."""
        now = datetime.now()
        self.sent_times_second.append(now)
        self.sent_times_minute.append(now)
        self.stats["total_sent"] += 1
    
    async def _get_next_message(self) -> Optional[ThrottledMessage]:
        """
        Get the next message from queues in priority order.
        
        Returns:
            Next message or None if all queues empty
        """
        async with self._lock:
            # Priority order: CRITICAL > HIGH > NORMAL > LOW
            if len(self.queue_critical) > 0:
                return self.queue_critical.popleft()
            elif len(self.queue_high) > 0:
                return self.queue_high.popleft()
            elif len(self.queue_normal) > 0:
                return self.queue_normal.popleft()
            elif len(self.queue_low) > 0:
                return self.queue_low.popleft()
            
            return None
    
    async def _process_queue(self):
        """Main queue processor loop."""
        while self._running:
            try:
                # Check if we can send
                if not self._can_send():
                    self.stats["total_rate_limited"] += 1
                    await asyncio.sleep(0.1)
                    continue
                
                # Get next message
                message = await self._get_next_message()
                if message is None:
                    # Queue empty, wait
                    await asyncio.sleep(0.1)
                    continue
                
                # Send the message
                success = await self._send_message(message)
                
                if success:
                    # Record successful send
                    self._record_send()
                else:
                    # Handle retry
                    message.retries += 1
                    self.stats["total_retries"] += 1
                    
                    if message.retries < message.max_retries:
                        # Re-queue with same priority
                        queue = self._get_queue_for_priority(message.priority)
                        async with self._lock:
                            queue.appendleft(message)  # Add to front
                        logger.warning(
                            f"{self.bot_name}: Retry {message.retries}/{message.max_retries} "
                            f"for message: {message.text[:30]}..."
                        )
                    else:
                        self.stats["total_failures"] += 1
                        logger.error(
                            f"{self.bot_name}: Failed to send after {message.max_retries} retries: "
                            f"{message.text[:50]}..."
                        )
                
                # Small delay to spread out messages
                await asyncio.sleep(0.05)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"{self.bot_name}: Error in queue processor: {e}")
                await asyncio.sleep(1)
    
    async def _send_message(self, message: ThrottledMessage) -> bool:
        """
        Send a message using the configured send function.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if self._send_function is None:
            logger.warning(f"{self.bot_name}: No send function configured")
            return True  # Return True to avoid infinite retries
        
        try:
            await self._send_function(message)
            return True
        except Exception as e:
            logger.error(f"{self.bot_name}: Send failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with queue sizes and stats
        """
        return {
            "bot": self.bot_name,
            "running": self._running,
            "queued": {
                "critical": len(self.queue_critical),
                "high": len(self.queue_high),
                "normal": len(self.queue_normal),
                "low": len(self.queue_low),
                "total": self._get_total_queue_size()
            },
            "limits": {
                "max_per_minute": self.max_per_minute,
                "max_per_second": self.max_per_second,
                "max_queue_size": self.max_queue_size
            },
            "stats": self.stats.copy()
        }
    
    def clear_queues(self):
        """Clear all message queues."""
        self.queue_critical.clear()
        self.queue_high.clear()
        self.queue_normal.clear()
        self.queue_low.clear()
        logger.info(f"{self.bot_name}: All queues cleared")


class RateLimitMonitor:
    """
    Monitor rate limiter health across all bots.
    
    Features:
    - Queue health checks
    - Alert on high queue usage
    - Track dropped messages
    """
    
    def __init__(
        self,
        warning_threshold: int = 70,
        critical_threshold: int = 90
    ):
        """
        Initialize monitor.
        
        Args:
            warning_threshold: Queue % to trigger warning
            critical_threshold: Queue % to trigger critical alert
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.logger = logging.getLogger(f"{__name__}.RateLimitMonitor")
    
    def check_health(self, limiters: Dict[str, TelegramRateLimiter]) -> Dict[str, Any]:
        """
        Check health of all rate limiters.
        
        Args:
            limiters: Dictionary of bot_name -> TelegramRateLimiter
            
        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "bots": {},
            "alerts": []
        }
        
        for bot_name, limiter in limiters.items():
            stats = limiter.get_stats()
            total_queued = stats["queued"]["total"]
            max_size = stats["limits"]["max_queue_size"]
            queue_percent = (total_queued / max_size * 100) if max_size > 0 else 0
            
            bot_health = {
                "queue_percent": queue_percent,
                "total_queued": total_queued,
                "dropped": stats["stats"]["total_dropped"],
                "status": "healthy"
            }
            
            # Check thresholds
            if queue_percent >= self.critical_threshold:
                bot_health["status"] = "critical"
                health["status"] = "critical"
                health["alerts"].append(
                    f"{bot_name}: Queue CRITICAL at {queue_percent:.1f}%"
                )
            elif queue_percent >= self.warning_threshold:
                bot_health["status"] = "warning"
                if health["status"] != "critical":
                    health["status"] = "warning"
                health["alerts"].append(
                    f"{bot_name}: Queue WARNING at {queue_percent:.1f}%"
                )
            
            # Check for dropped messages
            if stats["stats"]["total_dropped"] > 0:
                health["alerts"].append(
                    f"{bot_name}: {stats['stats']['total_dropped']} messages dropped"
                )
            
            health["bots"][bot_name] = bot_health
        
        return health
