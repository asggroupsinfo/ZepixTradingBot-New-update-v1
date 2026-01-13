"""
Telegram Rate Limiter - V5 Hybrid Plugin Architecture

Rate limiting system to prevent Telegram API violations when using 3 simultaneous bots.

Telegram API Limits:
- 30 messages/second per bot (hard limit)
- 20 messages/minute to same chat (recommended)
- 429 Too Many Requests error on violation

Part of Document 04: Phase 2 Detailed Plan - Multi-Telegram System
Enhanced by Document 22: Telegram Rate Limiting System
- Token Bucket Algorithm for burst handling
- Exponential Backoff for 429 errors
- Queue Monitor Watchdog
- Multi-Bot Coordination
"""

import asyncio
import time
import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, Deque, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: float = 0):
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class TokenBucket:
    """
    Token Bucket Algorithm for precise rate limiting with burst handling.
    
    The bucket fills with tokens at a constant rate (refill_rate tokens/second).
    Each message consumes one token. If no tokens available, message must wait.
    Allows bursts up to bucket capacity while maintaining average rate.
    
    Attributes:
        capacity: Maximum tokens the bucket can hold (burst size)
        refill_rate: Tokens added per second
        tokens: Current token count
        last_refill: Timestamp of last refill
    """
    capacity: float = 30.0
    refill_rate: float = 0.5
    tokens: float = field(default=30.0)
    last_refill: float = field(default_factory=time.time)
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: float = 1.0) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens consumed, False if not enough tokens
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def wait_time(self, tokens: float = 1.0) -> float:
        """
        Calculate time to wait for tokens to be available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Seconds to wait (0 if tokens available now)
        """
        self._refill()
        if self.tokens >= tokens:
            return 0.0
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate
    
    def get_available_tokens(self) -> float:
        """Get current available tokens."""
        self._refill()
        return self.tokens


@dataclass
class ExponentialBackoff:
    """
    Exponential Backoff for handling 429 Too Many Requests errors.
    
    Implements exponential backoff with jitter for retry logic.
    Each consecutive failure doubles the wait time up to max_delay.
    
    Attributes:
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Delay multiplier per attempt
        jitter: Random jitter factor (0-1)
        current_attempt: Current attempt number
        last_attempt_time: Timestamp of last attempt
    """
    base_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    jitter: float = 0.1
    current_attempt: int = 0
    last_attempt_time: float = field(default_factory=time.time)
    
    def get_delay(self) -> float:
        """
        Calculate delay for current attempt with jitter.
        
        Returns:
            Delay in seconds
        """
        if self.current_attempt == 0:
            return 0.0
        
        delay = self.base_delay * (self.multiplier ** (self.current_attempt - 1))
        delay = min(delay, self.max_delay)
        
        jitter_range = delay * self.jitter
        delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0.0, delay)
    
    def record_failure(self):
        """Record a failed attempt."""
        self.current_attempt += 1
        self.last_attempt_time = time.time()
    
    def record_success(self):
        """Record a successful attempt, reset backoff."""
        self.current_attempt = 0
        self.last_attempt_time = time.time()
    
    def should_retry(self, max_attempts: int = 5) -> bool:
        """
        Check if should retry based on attempt count.
        
        Args:
            max_attempts: Maximum retry attempts
            
        Returns:
            True if should retry
        """
        return self.current_attempt < max_attempts
    
    async def wait(self):
        """Wait for the calculated delay."""
        delay = self.get_delay()
        if delay > 0:
            await asyncio.sleep(delay)


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


class QueueWatchdog:
    """
    Async watchdog to monitor queue health and alert on issues.
    
    Features:
    - Periodic health checks
    - Automatic alerts when queues back up
    - Callback support for custom alert handling
    
    Usage:
        watchdog = QueueWatchdog(limiters, alert_callback=my_alert_func)
        await watchdog.start()
        # ... later ...
        await watchdog.stop()
    """
    
    def __init__(
        self,
        limiters: Dict[str, "TelegramRateLimiter"],
        check_interval: float = 5.0,
        warning_threshold: int = 70,
        critical_threshold: int = 90,
        alert_callback: Optional[Callable] = None
    ):
        """
        Initialize watchdog.
        
        Args:
            limiters: Dictionary of bot_name -> TelegramRateLimiter
            check_interval: Seconds between health checks
            warning_threshold: Queue % to trigger warning
            critical_threshold: Queue % to trigger critical alert
            alert_callback: Async function to call on alerts
        """
        self.limiters = limiters
        self.check_interval = check_interval
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.alert_callback = alert_callback
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._monitor = RateLimitMonitor(warning_threshold, critical_threshold)
        
        self.stats = {
            "checks_performed": 0,
            "warnings_issued": 0,
            "critical_alerts": 0,
            "last_check_time": None,
            "last_status": "unknown"
        }
        
        self.logger = logging.getLogger(f"{__name__}.QueueWatchdog")
    
    async def start(self):
        """Start the watchdog monitoring loop."""
        if self._running:
            self.logger.warning("QueueWatchdog already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        self.logger.info(f"QueueWatchdog started (interval: {self.check_interval}s)")
    
    async def stop(self):
        """Stop the watchdog monitoring loop."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        self.logger.info("QueueWatchdog stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_health()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in watchdog loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_health(self):
        """Perform health check and issue alerts if needed."""
        self.stats["checks_performed"] += 1
        self.stats["last_check_time"] = datetime.now().isoformat()
        
        health = self._monitor.check_health(self.limiters)
        self.stats["last_status"] = health["status"]
        
        if health["status"] == "warning":
            self.stats["warnings_issued"] += 1
            await self._issue_alert("warning", health)
        elif health["status"] == "critical":
            self.stats["critical_alerts"] += 1
            await self._issue_alert("critical", health)
    
    async def _issue_alert(self, level: str, health: Dict[str, Any]):
        """Issue an alert via callback or logging."""
        alert_message = f"Queue Health {level.upper()}: {', '.join(health['alerts'])}"
        
        if level == "critical":
            self.logger.error(alert_message)
        else:
            self.logger.warning(alert_message)
        
        if self.alert_callback:
            try:
                await self.alert_callback(level, health)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get watchdog statistics."""
        return {
            "running": self._running,
            "check_interval": self.check_interval,
            "thresholds": {
                "warning": self.warning_threshold,
                "critical": self.critical_threshold
            },
            "stats": self.stats.copy()
        }


class GlobalRateLimitCoordinator:
    """
    Coordinates rate limiting across multiple bots to respect global API limits.
    
    When multiple bots share resources or need to coordinate their sending,
    this coordinator ensures they don't collectively exceed limits.
    
    Features:
    - Global token bucket for shared limits
    - Per-bot tracking
    - Fairness scheduling
    
    Usage:
        coordinator = GlobalRateLimitCoordinator(global_limit=90)
        coordinator.register_bot("controller", controller_limiter)
        coordinator.register_bot("notification", notification_limiter)
        await coordinator.start()
    """
    
    def __init__(
        self,
        global_messages_per_second: float = 90.0,
        global_messages_per_minute: float = 60.0,
        fairness_enabled: bool = True
    ):
        """
        Initialize coordinator.
        
        Args:
            global_messages_per_second: Combined limit across all bots
            global_messages_per_minute: Combined per-minute limit
            fairness_enabled: Enable fair scheduling between bots
        """
        self.global_per_second = global_messages_per_second
        self.global_per_minute = global_messages_per_minute
        self.fairness_enabled = fairness_enabled
        
        self.global_bucket = TokenBucket(
            capacity=global_messages_per_second,
            refill_rate=global_messages_per_second / 60.0
        )
        
        self.bots: Dict[str, "TelegramRateLimiter"] = {}
        self.bot_send_counts: Dict[str, int] = {}
        self.last_bot_index = 0
        
        self._running = False
        self._lock = asyncio.Lock()
        
        self.stats = {
            "total_coordinated": 0,
            "total_throttled": 0,
            "fairness_adjustments": 0
        }
        
        self.logger = logging.getLogger(f"{__name__}.GlobalRateLimitCoordinator")
    
    def register_bot(self, name: str, limiter: "TelegramRateLimiter"):
        """
        Register a bot with the coordinator.
        
        Args:
            name: Bot identifier
            limiter: The bot's rate limiter
        """
        self.bots[name] = limiter
        self.bot_send_counts[name] = 0
        self.logger.info(f"Registered bot: {name}")
    
    def unregister_bot(self, name: str):
        """
        Unregister a bot from the coordinator.
        
        Args:
            name: Bot identifier
        """
        if name in self.bots:
            del self.bots[name]
            del self.bot_send_counts[name]
            self.logger.info(f"Unregistered bot: {name}")
    
    async def request_send_permission(self, bot_name: str) -> bool:
        """
        Request permission to send a message.
        
        Args:
            bot_name: Name of the requesting bot
            
        Returns:
            True if permission granted, False if should wait
        """
        async with self._lock:
            if bot_name not in self.bots:
                self.logger.warning(f"Unknown bot requesting permission: {bot_name}")
                return True
            
            if self.global_bucket.consume(1.0):
                self.stats["total_coordinated"] += 1
                self.bot_send_counts[bot_name] += 1
                return True
            else:
                self.stats["total_throttled"] += 1
                return False
    
    async def wait_for_permission(self, bot_name: str, timeout: float = 5.0) -> bool:
        """
        Wait for permission to send a message.
        
        Args:
            bot_name: Name of the requesting bot
            timeout: Maximum time to wait
            
        Returns:
            True if permission granted within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.request_send_permission(bot_name):
                return True
            
            wait_time = self.global_bucket.wait_time(1.0)
            await asyncio.sleep(min(wait_time, 0.1))
        
        return False
    
    def get_fair_share(self, bot_name: str) -> float:
        """
        Calculate fair share of global limit for a bot.
        
        Args:
            bot_name: Bot identifier
            
        Returns:
            Percentage of global limit (0.0 to 1.0)
        """
        if not self.fairness_enabled or len(self.bots) == 0:
            return 1.0
        
        return 1.0 / len(self.bots)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        return {
            "global_limits": {
                "per_second": self.global_per_second,
                "per_minute": self.global_per_minute
            },
            "registered_bots": list(self.bots.keys()),
            "bot_send_counts": self.bot_send_counts.copy(),
            "available_tokens": self.global_bucket.get_available_tokens(),
            "fairness_enabled": self.fairness_enabled,
            "stats": self.stats.copy()
        }
    
    def reset_stats(self):
        """Reset all statistics."""
        self.stats = {
            "total_coordinated": 0,
            "total_throttled": 0,
            "fairness_adjustments": 0
        }
        for bot_name in self.bot_send_counts:
            self.bot_send_counts[bot_name] = 0


class EnhancedTelegramRateLimiter(TelegramRateLimiter):
    """
    Enhanced rate limiter with Token Bucket and Exponential Backoff.
    
    Extends TelegramRateLimiter with:
    - Token Bucket algorithm for precise burst handling
    - Exponential backoff for 429 error recovery
    - Integration with GlobalRateLimitCoordinator
    
    Usage:
        limiter = EnhancedTelegramRateLimiter("ControllerBot")
        await limiter.start()
        await limiter.enqueue(message)
    """
    
    def __init__(
        self,
        bot_name: str,
        max_per_minute: int = 20,
        max_per_second: int = 30,
        max_queue_size: int = 100,
        coordinator: Optional[GlobalRateLimitCoordinator] = None
    ):
        """
        Initialize enhanced rate limiter.
        
        Args:
            bot_name: Name of the bot
            max_per_minute: Maximum messages per minute
            max_per_second: Maximum messages per second
            max_queue_size: Maximum queue size
            coordinator: Optional global coordinator
        """
        super().__init__(bot_name, max_per_minute, max_per_second, max_queue_size)
        
        self.token_bucket = TokenBucket(
            capacity=float(max_per_second),
            refill_rate=float(max_per_minute) / 60.0
        )
        
        self.backoff = ExponentialBackoff(
            base_delay=1.0,
            max_delay=60.0,
            multiplier=2.0
        )
        
        self.coordinator = coordinator
        
        self.stats["token_bucket_waits"] = 0
        self.stats["backoff_waits"] = 0
        self.stats["coordinator_throttles"] = 0
    
    def _can_send(self) -> bool:
        """
        Check if we can send using Token Bucket algorithm.
        
        Returns:
            True if token available, False otherwise
        """
        if not self.token_bucket.consume(1.0):
            self.stats["token_bucket_waits"] += 1
            return False
        
        return super()._can_send()
    
    async def _send_message(self, message: ThrottledMessage) -> bool:
        """
        Send message with exponential backoff on failure.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if self.coordinator:
            if not await self.coordinator.request_send_permission(self.bot_name):
                self.stats["coordinator_throttles"] += 1
                return False
        
        if self.backoff.current_attempt > 0:
            self.stats["backoff_waits"] += 1
            await self.backoff.wait()
        
        try:
            success = await super()._send_message(message)
            
            if success:
                self.backoff.record_success()
            else:
                self.backoff.record_failure()
            
            return success
            
        except RateLimitError as e:
            self.backoff.record_failure()
            self.logger.warning(
                f"{self.bot_name}: Rate limit hit, backing off "
                f"(attempt {self.backoff.current_attempt}, "
                f"retry_after={e.retry_after}s)"
            )
            return False
        except Exception as e:
            self.backoff.record_failure()
            self.logger.error(f"{self.bot_name}: Send error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics."""
        stats = super().get_stats()
        stats["token_bucket"] = {
            "available_tokens": self.token_bucket.get_available_tokens(),
            "capacity": self.token_bucket.capacity,
            "refill_rate": self.token_bucket.refill_rate
        }
        stats["backoff"] = {
            "current_attempt": self.backoff.current_attempt,
            "next_delay": self.backoff.get_delay()
        }
        stats["has_coordinator"] = self.coordinator is not None
        return stats


def create_rate_limiter(
    bot_name: str,
    max_per_minute: int = 20,
    max_per_second: int = 30,
    max_queue_size: int = 100,
    enhanced: bool = True,
    coordinator: Optional[GlobalRateLimitCoordinator] = None
) -> TelegramRateLimiter:
    """
    Factory function to create rate limiter.
    
    Args:
        bot_name: Name of the bot
        max_per_minute: Maximum messages per minute
        max_per_second: Maximum messages per second
        max_queue_size: Maximum queue size
        enhanced: Use enhanced limiter with Token Bucket
        coordinator: Optional global coordinator
        
    Returns:
        TelegramRateLimiter or EnhancedTelegramRateLimiter
    """
    if enhanced:
        return EnhancedTelegramRateLimiter(
            bot_name=bot_name,
            max_per_minute=max_per_minute,
            max_per_second=max_per_second,
            max_queue_size=max_queue_size,
            coordinator=coordinator
        )
    else:
        return TelegramRateLimiter(
            bot_name=bot_name,
            max_per_minute=max_per_minute,
            max_per_second=max_per_second,
            max_queue_size=max_queue_size
        )
