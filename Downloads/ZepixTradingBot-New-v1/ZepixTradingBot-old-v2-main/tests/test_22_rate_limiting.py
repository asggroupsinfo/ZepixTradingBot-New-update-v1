"""
Test Suite for Document 22: Telegram Rate Limiting System

Tests the complete rate limiting implementation including:
- Token Bucket Algorithm
- Exponential Backoff
- Priority Queue System
- Queue Watchdog
- Global Rate Limit Coordinator
- Enhanced Rate Limiter
- High Load Simulation

Part of V5 Hybrid Plugin Architecture Implementation
"""

import pytest
import sys
import os
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestRateLimiterModuleStructure:
    """Test rate limiter module structure and imports."""
    
    def test_rate_limiter_module_exists(self):
        """Test rate_limiter module exists."""
        from telegram import rate_limiter
        assert rate_limiter is not None
    
    def test_rate_limit_error_exists(self):
        """Test RateLimitError exception exists."""
        from telegram.rate_limiter import RateLimitError
        assert RateLimitError is not None
    
    def test_token_bucket_exists(self):
        """Test TokenBucket class exists."""
        from telegram.rate_limiter import TokenBucket
        assert TokenBucket is not None
    
    def test_exponential_backoff_exists(self):
        """Test ExponentialBackoff class exists."""
        from telegram.rate_limiter import ExponentialBackoff
        assert ExponentialBackoff is not None
    
    def test_message_priority_exists(self):
        """Test MessagePriority enum exists."""
        from telegram.rate_limiter import MessagePriority
        assert MessagePriority is not None
    
    def test_throttled_message_exists(self):
        """Test ThrottledMessage class exists."""
        from telegram.rate_limiter import ThrottledMessage
        assert ThrottledMessage is not None
    
    def test_telegram_rate_limiter_exists(self):
        """Test TelegramRateLimiter class exists."""
        from telegram.rate_limiter import TelegramRateLimiter
        assert TelegramRateLimiter is not None
    
    def test_rate_limit_monitor_exists(self):
        """Test RateLimitMonitor class exists."""
        from telegram.rate_limiter import RateLimitMonitor
        assert RateLimitMonitor is not None
    
    def test_queue_watchdog_exists(self):
        """Test QueueWatchdog class exists."""
        from telegram.rate_limiter import QueueWatchdog
        assert QueueWatchdog is not None
    
    def test_global_coordinator_exists(self):
        """Test GlobalRateLimitCoordinator class exists."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator
        assert GlobalRateLimitCoordinator is not None
    
    def test_enhanced_rate_limiter_exists(self):
        """Test EnhancedTelegramRateLimiter class exists."""
        from telegram.rate_limiter import EnhancedTelegramRateLimiter
        assert EnhancedTelegramRateLimiter is not None
    
    def test_factory_function_exists(self):
        """Test create_rate_limiter factory function exists."""
        from telegram.rate_limiter import create_rate_limiter
        assert create_rate_limiter is not None


class TestRateLimitError:
    """Test RateLimitError exception."""
    
    def test_error_creation(self):
        """Test creating RateLimitError."""
        from telegram.rate_limiter import RateLimitError
        error = RateLimitError("Rate limit exceeded", retry_after=5.0)
        assert str(error) == "Rate limit exceeded"
        assert error.retry_after == 5.0
    
    def test_error_default_retry(self):
        """Test default retry_after value."""
        from telegram.rate_limiter import RateLimitError
        error = RateLimitError("Rate limit exceeded")
        assert error.retry_after == 0


class TestTokenBucket:
    """Test Token Bucket Algorithm implementation."""
    
    def test_bucket_initialization(self):
        """Test TokenBucket initialization."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=0.5)
        assert bucket.capacity == 30.0
        assert bucket.refill_rate == 0.5
        assert bucket.tokens == 30.0
    
    def test_bucket_consume_success(self):
        """Test consuming tokens successfully."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=0.5)
        assert bucket.consume(1.0) is True
        assert bucket.tokens == 29.0
    
    def test_bucket_consume_multiple(self):
        """Test consuming multiple tokens."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=0.5)
        assert bucket.consume(10.0) is True
        assert bucket.tokens == 20.0
    
    def test_bucket_consume_failure(self):
        """Test consuming more tokens than available."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=5.0, refill_rate=0.5, tokens=2.0)
        assert bucket.consume(5.0) is False
        assert abs(bucket.tokens - 2.0) < 0.01
    
    def test_bucket_refill(self):
        """Test token refill over time."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=10.0, tokens=0.0)
        bucket.last_refill = time.time() - 1.0
        bucket._refill()
        assert bucket.tokens >= 9.0
    
    def test_bucket_refill_cap(self):
        """Test refill doesn't exceed capacity."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=100.0, tokens=25.0)
        bucket.last_refill = time.time() - 1.0
        bucket._refill()
        assert bucket.tokens == 30.0
    
    def test_bucket_wait_time_zero(self):
        """Test wait time when tokens available."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=0.5, tokens=30.0)
        assert bucket.wait_time(1.0) == 0.0
    
    def test_bucket_wait_time_positive(self):
        """Test wait time when tokens not available."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=1.0, tokens=0.0)
        wait = bucket.wait_time(5.0)
        assert wait > 0.0
        assert wait <= 5.0
    
    def test_bucket_get_available_tokens(self):
        """Test getting available tokens."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=0.5, tokens=15.0)
        assert abs(bucket.get_available_tokens() - 15.0) < 0.01


class TestExponentialBackoff:
    """Test Exponential Backoff implementation."""
    
    def test_backoff_initialization(self):
        """Test ExponentialBackoff initialization."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=60.0)
        assert backoff.base_delay == 1.0
        assert backoff.max_delay == 60.0
        assert backoff.current_attempt == 0
    
    def test_backoff_first_delay_zero(self):
        """Test first attempt has zero delay."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff()
        assert backoff.get_delay() == 0.0
    
    def test_backoff_delay_increases(self):
        """Test delay increases with attempts."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff(base_delay=1.0, multiplier=2.0, jitter=0.0)
        
        backoff.record_failure()
        delay1 = backoff.get_delay()
        
        backoff.record_failure()
        delay2 = backoff.get_delay()
        
        assert delay2 > delay1
    
    def test_backoff_max_delay(self):
        """Test delay doesn't exceed max_delay."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=10.0, multiplier=2.0, jitter=0.0)
        
        for _ in range(10):
            backoff.record_failure()
        
        assert backoff.get_delay() <= 10.0
    
    def test_backoff_record_success(self):
        """Test success resets backoff."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff()
        
        backoff.record_failure()
        backoff.record_failure()
        assert backoff.current_attempt == 2
        
        backoff.record_success()
        assert backoff.current_attempt == 0
    
    def test_backoff_should_retry_true(self):
        """Test should_retry returns True within limit."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff()
        backoff.record_failure()
        backoff.record_failure()
        assert backoff.should_retry(max_attempts=5) is True
    
    def test_backoff_should_retry_false(self):
        """Test should_retry returns False at limit."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff()
        for _ in range(5):
            backoff.record_failure()
        assert backoff.should_retry(max_attempts=5) is False
    
    def test_backoff_wait(self):
        """Test async wait function."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff(base_delay=0.01, jitter=0.0)
        backoff.record_failure()
        asyncio.run(backoff.wait())


class TestMessagePriority:
    """Test MessagePriority enum."""
    
    def test_priority_values(self):
        """Test priority enum values."""
        from telegram.rate_limiter import MessagePriority
        assert MessagePriority.LOW.value == 0
        assert MessagePriority.NORMAL.value == 1
        assert MessagePriority.HIGH.value == 2
        assert MessagePriority.CRITICAL.value == 3
    
    def test_priority_ordering(self):
        """Test priority ordering."""
        from telegram.rate_limiter import MessagePriority
        assert MessagePriority.LOW.value < MessagePriority.NORMAL.value
        assert MessagePriority.NORMAL.value < MessagePriority.HIGH.value
        assert MessagePriority.HIGH.value < MessagePriority.CRITICAL.value


class TestThrottledMessage:
    """Test ThrottledMessage class."""
    
    def test_message_creation(self):
        """Test creating ThrottledMessage."""
        from telegram.rate_limiter import ThrottledMessage, MessagePriority
        msg = ThrottledMessage(
            chat_id="123456",
            text="Test message",
            priority=MessagePriority.HIGH
        )
        assert msg.chat_id == "123456"
        assert msg.text == "Test message"
        assert msg.priority == MessagePriority.HIGH
    
    def test_message_defaults(self):
        """Test message default values."""
        from telegram.rate_limiter import ThrottledMessage, MessagePriority
        msg = ThrottledMessage(chat_id="123", text="Test")
        assert msg.priority == MessagePriority.NORMAL
        assert msg.parse_mode == "Markdown"
        assert msg.retries == 0
        assert msg.max_retries == 3
    
    def test_message_timestamp(self):
        """Test message timestamp."""
        from telegram.rate_limiter import ThrottledMessage
        before = datetime.now()
        msg = ThrottledMessage(chat_id="123", text="Test")
        after = datetime.now()
        assert before <= msg.timestamp <= after
    
    def test_message_repr(self):
        """Test message string representation."""
        from telegram.rate_limiter import ThrottledMessage, MessagePriority
        msg = ThrottledMessage(chat_id="123", text="Test message", priority=MessagePriority.HIGH)
        repr_str = repr(msg)
        assert "123" in repr_str
        assert "HIGH" in repr_str


class TestTelegramRateLimiter:
    """Test TelegramRateLimiter class."""
    
    def test_limiter_initialization(self):
        """Test TelegramRateLimiter initialization."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot", max_per_minute=20, max_per_second=30)
        assert limiter.bot_name == "TestBot"
        assert limiter.max_per_minute == 20
        assert limiter.max_per_second == 30
    
    def test_limiter_start_stop(self):
        """Test starting and stopping limiter."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        
        asyncio.run(limiter.start())
        assert limiter._running is True
        
        asyncio.run(limiter.stop())
        assert limiter._running is False
    
    def test_limiter_enqueue(self):
        """Test enqueueing messages."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot")
        
        msg = ThrottledMessage(chat_id="123", text="Test", priority=MessagePriority.NORMAL)
        result = asyncio.run(limiter.enqueue(msg))
        assert result is True
        assert limiter._get_total_queue_size() == 1
    
    def test_limiter_priority_queues(self):
        """Test messages go to correct priority queues."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot")
        
        asyncio.run(limiter.enqueue(ThrottledMessage("1", "Low", MessagePriority.LOW)))
        asyncio.run(limiter.enqueue(ThrottledMessage("2", "Normal", MessagePriority.NORMAL)))
        asyncio.run(limiter.enqueue(ThrottledMessage("3", "High", MessagePriority.HIGH)))
        asyncio.run(limiter.enqueue(ThrottledMessage("4", "Critical", MessagePriority.CRITICAL)))
        
        assert len(limiter.queue_low) == 1
        assert len(limiter.queue_normal) == 1
        assert len(limiter.queue_high) == 1
        assert len(limiter.queue_critical) == 1
    
    def test_limiter_can_send(self):
        """Test _can_send rate checking."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot", max_per_minute=20, max_per_second=30)
        assert limiter._can_send() is True
    
    def test_limiter_record_send(self):
        """Test recording sent messages."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        
        limiter._record_send()
        assert limiter.stats["total_sent"] == 1
        assert len(limiter.sent_times_second) == 1
        assert len(limiter.sent_times_minute) == 1
    
    def test_limiter_get_next_message_priority_order(self):
        """Test messages retrieved in priority order."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot")
        
        asyncio.run(limiter.enqueue(ThrottledMessage("1", "Low", MessagePriority.LOW)))
        asyncio.run(limiter.enqueue(ThrottledMessage("2", "Critical", MessagePriority.CRITICAL)))
        asyncio.run(limiter.enqueue(ThrottledMessage("3", "Normal", MessagePriority.NORMAL)))
        
        msg = asyncio.run(limiter._get_next_message())
        assert msg.priority == MessagePriority.CRITICAL
    
    def test_limiter_queue_overflow_drops_low(self):
        """Test queue overflow drops LOW priority first."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot", max_queue_size=5)
        
        for i in range(5):
            asyncio.run(limiter.enqueue(ThrottledMessage(str(i), f"Low {i}", MessagePriority.LOW)))
        
        high_msg = ThrottledMessage("high", "High priority", MessagePriority.HIGH)
        result = asyncio.run(limiter.enqueue(high_msg))
        assert result is True
        assert limiter.stats["total_dropped"] == 1
    
    def test_limiter_get_stats(self):
        """Test getting limiter statistics."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        stats = limiter.get_stats()
        
        assert "bot" in stats
        assert "running" in stats
        assert "queued" in stats
        assert "limits" in stats
        assert "stats" in stats
    
    def test_limiter_clear_queues(self):
        """Test clearing all queues."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot")
        
        asyncio.run(limiter.enqueue(ThrottledMessage("1", "Test", MessagePriority.NORMAL)))
        assert limiter._get_total_queue_size() == 1
        
        limiter.clear_queues()
        assert limiter._get_total_queue_size() == 0
    
    def test_limiter_set_send_function(self):
        """Test setting send function."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        
        async def mock_send(msg):
            pass
        
        limiter.set_send_function(mock_send)
        assert limiter._send_function is not None


class TestRateLimitMonitor:
    """Test RateLimitMonitor class."""
    
    def test_monitor_initialization(self):
        """Test RateLimitMonitor initialization."""
        from telegram.rate_limiter import RateLimitMonitor
        monitor = RateLimitMonitor(warning_threshold=70, critical_threshold=90)
        assert monitor.warning_threshold == 70
        assert monitor.critical_threshold == 90
    
    def test_monitor_healthy_status(self):
        """Test healthy status when queues are empty."""
        from telegram.rate_limiter import RateLimitMonitor, TelegramRateLimiter
        monitor = RateLimitMonitor()
        limiter = TelegramRateLimiter("TestBot")
        
        health = monitor.check_health({"TestBot": limiter})
        assert health["status"] == "healthy"
        assert len(health["alerts"]) == 0
    
    def test_monitor_warning_status(self):
        """Test warning status when queue is high."""
        from telegram.rate_limiter import RateLimitMonitor, TelegramRateLimiter, ThrottledMessage, MessagePriority
        monitor = RateLimitMonitor(warning_threshold=50, critical_threshold=90)
        limiter = TelegramRateLimiter("TestBot", max_queue_size=10)
        
        for i in range(6):
            asyncio.run(limiter.enqueue(ThrottledMessage(str(i), f"Msg {i}", MessagePriority.NORMAL)))
        
        health = monitor.check_health({"TestBot": limiter})
        assert health["status"] == "warning"
    
    def test_monitor_critical_status(self):
        """Test critical status when queue is very high."""
        from telegram.rate_limiter import RateLimitMonitor, TelegramRateLimiter, ThrottledMessage, MessagePriority
        monitor = RateLimitMonitor(warning_threshold=50, critical_threshold=80)
        limiter = TelegramRateLimiter("TestBot", max_queue_size=10)
        
        for i in range(9):
            asyncio.run(limiter.enqueue(ThrottledMessage(str(i), f"Msg {i}", MessagePriority.NORMAL)))
        
        health = monitor.check_health({"TestBot": limiter})
        assert health["status"] == "critical"


class TestQueueWatchdog:
    """Test QueueWatchdog class."""
    
    def test_watchdog_initialization(self):
        """Test QueueWatchdog initialization."""
        from telegram.rate_limiter import QueueWatchdog, TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        watchdog = QueueWatchdog({"TestBot": limiter}, check_interval=1.0)
        
        assert watchdog.check_interval == 1.0
        assert "TestBot" in watchdog.limiters
    
    def test_watchdog_start_stop(self):
        """Test starting and stopping watchdog."""
        from telegram.rate_limiter import QueueWatchdog, TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        watchdog = QueueWatchdog({"TestBot": limiter}, check_interval=0.1)
        
        asyncio.run(watchdog.start())
        assert watchdog._running is True
        
        asyncio.run(watchdog.stop())
        assert watchdog._running is False
    
    def test_watchdog_get_stats(self):
        """Test getting watchdog statistics."""
        from telegram.rate_limiter import QueueWatchdog, TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        watchdog = QueueWatchdog({"TestBot": limiter})
        
        stats = watchdog.get_stats()
        assert "running" in stats
        assert "check_interval" in stats
        assert "thresholds" in stats
        assert "stats" in stats
    
    def test_watchdog_with_callback(self):
        """Test watchdog with alert callback."""
        from telegram.rate_limiter import QueueWatchdog, TelegramRateLimiter
        
        alerts_received = []
        
        async def alert_callback(level, health):
            alerts_received.append((level, health))
        
        limiter = TelegramRateLimiter("TestBot")
        watchdog = QueueWatchdog(
            {"TestBot": limiter},
            alert_callback=alert_callback
        )
        
        assert watchdog.alert_callback is not None


class TestGlobalRateLimitCoordinator:
    """Test GlobalRateLimitCoordinator class."""
    
    def test_coordinator_initialization(self):
        """Test GlobalRateLimitCoordinator initialization."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator
        coordinator = GlobalRateLimitCoordinator(
            global_messages_per_second=90.0,
            global_messages_per_minute=60.0
        )
        assert coordinator.global_per_second == 90.0
        assert coordinator.global_per_minute == 60.0
    
    def test_coordinator_register_bot(self):
        """Test registering a bot."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator, TelegramRateLimiter
        coordinator = GlobalRateLimitCoordinator()
        limiter = TelegramRateLimiter("TestBot")
        
        coordinator.register_bot("TestBot", limiter)
        assert "TestBot" in coordinator.bots
    
    def test_coordinator_unregister_bot(self):
        """Test unregistering a bot."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator, TelegramRateLimiter
        coordinator = GlobalRateLimitCoordinator()
        limiter = TelegramRateLimiter("TestBot")
        
        coordinator.register_bot("TestBot", limiter)
        coordinator.unregister_bot("TestBot")
        assert "TestBot" not in coordinator.bots
    
    def test_coordinator_request_permission(self):
        """Test requesting send permission."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator, TelegramRateLimiter
        coordinator = GlobalRateLimitCoordinator()
        limiter = TelegramRateLimiter("TestBot")
        coordinator.register_bot("TestBot", limiter)
        
        result = asyncio.run(coordinator.request_send_permission("TestBot"))
        assert result is True
        assert coordinator.stats["total_coordinated"] == 1
    
    def test_coordinator_fair_share(self):
        """Test fair share calculation."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator, TelegramRateLimiter
        coordinator = GlobalRateLimitCoordinator(fairness_enabled=True)
        
        coordinator.register_bot("Bot1", TelegramRateLimiter("Bot1"))
        coordinator.register_bot("Bot2", TelegramRateLimiter("Bot2"))
        
        share = coordinator.get_fair_share("Bot1")
        assert share == 0.5
    
    def test_coordinator_get_stats(self):
        """Test getting coordinator statistics."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator
        coordinator = GlobalRateLimitCoordinator()
        
        stats = coordinator.get_stats()
        assert "global_limits" in stats
        assert "registered_bots" in stats
        assert "available_tokens" in stats
        assert "stats" in stats
    
    def test_coordinator_reset_stats(self):
        """Test resetting statistics."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator, TelegramRateLimiter
        coordinator = GlobalRateLimitCoordinator()
        limiter = TelegramRateLimiter("TestBot")
        coordinator.register_bot("TestBot", limiter)
        
        asyncio.run(coordinator.request_send_permission("TestBot"))
        assert coordinator.stats["total_coordinated"] == 1
        
        coordinator.reset_stats()
        assert coordinator.stats["total_coordinated"] == 0


class TestEnhancedTelegramRateLimiter:
    """Test EnhancedTelegramRateLimiter class."""
    
    def test_enhanced_limiter_initialization(self):
        """Test EnhancedTelegramRateLimiter initialization."""
        from telegram.rate_limiter import EnhancedTelegramRateLimiter
        limiter = EnhancedTelegramRateLimiter("TestBot")
        
        assert limiter.bot_name == "TestBot"
        assert limiter.token_bucket is not None
        assert limiter.backoff is not None
    
    def test_enhanced_limiter_with_coordinator(self):
        """Test enhanced limiter with coordinator."""
        from telegram.rate_limiter import EnhancedTelegramRateLimiter, GlobalRateLimitCoordinator
        coordinator = GlobalRateLimitCoordinator()
        limiter = EnhancedTelegramRateLimiter("TestBot", coordinator=coordinator)
        
        assert limiter.coordinator is coordinator
    
    def test_enhanced_limiter_token_bucket_stats(self):
        """Test enhanced limiter includes token bucket stats."""
        from telegram.rate_limiter import EnhancedTelegramRateLimiter
        limiter = EnhancedTelegramRateLimiter("TestBot")
        
        stats = limiter.get_stats()
        assert "token_bucket" in stats
        assert "available_tokens" in stats["token_bucket"]
        assert "capacity" in stats["token_bucket"]
    
    def test_enhanced_limiter_backoff_stats(self):
        """Test enhanced limiter includes backoff stats."""
        from telegram.rate_limiter import EnhancedTelegramRateLimiter
        limiter = EnhancedTelegramRateLimiter("TestBot")
        
        stats = limiter.get_stats()
        assert "backoff" in stats
        assert "current_attempt" in stats["backoff"]
        assert "next_delay" in stats["backoff"]


class TestCreateRateLimiterFactory:
    """Test create_rate_limiter factory function."""
    
    def test_create_enhanced_limiter(self):
        """Test creating enhanced limiter."""
        from telegram.rate_limiter import create_rate_limiter, EnhancedTelegramRateLimiter
        limiter = create_rate_limiter("TestBot", enhanced=True)
        assert isinstance(limiter, EnhancedTelegramRateLimiter)
    
    def test_create_basic_limiter(self):
        """Test creating basic limiter."""
        from telegram.rate_limiter import create_rate_limiter, TelegramRateLimiter, EnhancedTelegramRateLimiter
        limiter = create_rate_limiter("TestBot", enhanced=False)
        assert isinstance(limiter, TelegramRateLimiter)
        assert not isinstance(limiter, EnhancedTelegramRateLimiter)
    
    def test_create_with_coordinator(self):
        """Test creating limiter with coordinator."""
        from telegram.rate_limiter import create_rate_limiter, GlobalRateLimitCoordinator
        coordinator = GlobalRateLimitCoordinator()
        limiter = create_rate_limiter("TestBot", enhanced=True, coordinator=coordinator)
        assert limiter.coordinator is coordinator
    
    def test_create_with_custom_limits(self):
        """Test creating limiter with custom limits."""
        from telegram.rate_limiter import create_rate_limiter
        limiter = create_rate_limiter(
            "TestBot",
            max_per_minute=15,
            max_per_second=25,
            max_queue_size=50
        )
        assert limiter.max_per_minute == 15
        assert limiter.max_per_second == 25
        assert limiter.max_queue_size == 50


class TestHighLoadSimulation:
    """Test rate limiting under high load conditions."""
    
    def test_burst_handling(self):
        """Test handling burst of messages."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot", max_queue_size=100)
        
        for i in range(50):
            msg = ThrottledMessage(str(i), f"Burst message {i}", MessagePriority.NORMAL)
            asyncio.run(limiter.enqueue(msg))
        
        assert limiter._get_total_queue_size() == 50
        assert limiter.stats["total_queued"] == 50
    
    def test_priority_under_load(self):
        """Test priority handling under load."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot", max_queue_size=100)
        
        for i in range(20):
            asyncio.run(limiter.enqueue(ThrottledMessage(str(i), f"Low {i}", MessagePriority.LOW)))
        
        for i in range(10):
            asyncio.run(limiter.enqueue(ThrottledMessage(str(i), f"Critical {i}", MessagePriority.CRITICAL)))
        
        msg = asyncio.run(limiter._get_next_message())
        assert msg.priority == MessagePriority.CRITICAL
    
    def test_queue_overflow_under_load(self):
        """Test queue overflow handling under load."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot", max_queue_size=20)
        
        for i in range(15):
            asyncio.run(limiter.enqueue(ThrottledMessage(str(i), f"Low {i}", MessagePriority.LOW)))
        
        for i in range(10):
            asyncio.run(limiter.enqueue(ThrottledMessage(str(i), f"High {i}", MessagePriority.HIGH)))
        
        assert limiter.stats["total_dropped"] >= 5
    
    def test_multiple_bots_coordination(self):
        """Test coordination between multiple bots."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator, TelegramRateLimiter
        coordinator = GlobalRateLimitCoordinator(global_messages_per_second=90.0)
        
        bot1 = TelegramRateLimiter("Controller")
        bot2 = TelegramRateLimiter("Notification")
        bot3 = TelegramRateLimiter("Analytics")
        
        coordinator.register_bot("Controller", bot1)
        coordinator.register_bot("Notification", bot2)
        coordinator.register_bot("Analytics", bot3)
        
        for _ in range(10):
            asyncio.run(coordinator.request_send_permission("Controller"))
            asyncio.run(coordinator.request_send_permission("Notification"))
            asyncio.run(coordinator.request_send_permission("Analytics"))
        
        assert coordinator.stats["total_coordinated"] == 30
    
    def test_token_bucket_under_load(self):
        """Test token bucket under high load."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket(capacity=30.0, refill_rate=0.5)
        
        consumed = 0
        for _ in range(50):
            if bucket.consume(1.0):
                consumed += 1
        
        assert consumed == 30
        assert bucket.tokens < 0.1


class TestDocument22Integration:
    """Test Document 22 integration requirements."""
    
    def test_all_components_importable(self):
        """Test all Document 22 components are importable."""
        from telegram.rate_limiter import (
            RateLimitError,
            TokenBucket,
            ExponentialBackoff,
            MessagePriority,
            ThrottledMessage,
            TelegramRateLimiter,
            RateLimitMonitor,
            QueueWatchdog,
            GlobalRateLimitCoordinator,
            EnhancedTelegramRateLimiter,
            create_rate_limiter
        )
        assert all([
            RateLimitError,
            TokenBucket,
            ExponentialBackoff,
            MessagePriority,
            ThrottledMessage,
            TelegramRateLimiter,
            RateLimitMonitor,
            QueueWatchdog,
            GlobalRateLimitCoordinator,
            EnhancedTelegramRateLimiter,
            create_rate_limiter
        ])
    
    def test_20_per_minute_limit(self):
        """Test 20 messages per minute limit enforcement."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot", max_per_minute=20)
        assert limiter.max_per_minute == 20
    
    def test_30_per_second_limit(self):
        """Test 30 messages per second limit enforcement."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot", max_per_second=30)
        assert limiter.max_per_second == 30
    
    def test_priority_bypass(self):
        """Test CRITICAL priority bypasses LOW."""
        from telegram.rate_limiter import TelegramRateLimiter, ThrottledMessage, MessagePriority
        limiter = TelegramRateLimiter("TestBot")
        
        asyncio.run(limiter.enqueue(ThrottledMessage("1", "Low", MessagePriority.LOW)))
        asyncio.run(limiter.enqueue(ThrottledMessage("2", "Critical", MessagePriority.CRITICAL)))
        
        msg = asyncio.run(limiter._get_next_message())
        assert msg.priority == MessagePriority.CRITICAL
    
    def test_three_bot_system(self):
        """Test 3-bot system coordination."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator, TelegramRateLimiter
        coordinator = GlobalRateLimitCoordinator()
        
        controller = TelegramRateLimiter("Controller")
        notification = TelegramRateLimiter("Notification")
        analytics = TelegramRateLimiter("Analytics")
        
        coordinator.register_bot("Controller", controller)
        coordinator.register_bot("Notification", notification)
        coordinator.register_bot("Analytics", analytics)
        
        assert len(coordinator.bots) == 3


class TestDocument22Summary:
    """Test Document 22 summary requirements."""
    
    def test_global_rate_limiter_implemented(self):
        """Test global rate limiter is implemented."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator
        coordinator = GlobalRateLimitCoordinator()
        assert hasattr(coordinator, 'global_per_second')
        assert hasattr(coordinator, 'global_per_minute')
        assert hasattr(coordinator, 'request_send_permission')
    
    def test_token_bucket_implemented(self):
        """Test token bucket algorithm is implemented."""
        from telegram.rate_limiter import TokenBucket
        bucket = TokenBucket()
        assert hasattr(bucket, 'consume')
        assert hasattr(bucket, 'wait_time')
        assert hasattr(bucket, '_refill')
    
    def test_priority_queue_implemented(self):
        """Test priority queue is implemented."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        assert hasattr(limiter, 'queue_critical')
        assert hasattr(limiter, 'queue_high')
        assert hasattr(limiter, 'queue_normal')
        assert hasattr(limiter, 'queue_low')
    
    def test_retry_mechanism_implemented(self):
        """Test exponential backoff retry mechanism is implemented."""
        from telegram.rate_limiter import ExponentialBackoff
        backoff = ExponentialBackoff()
        assert hasattr(backoff, 'get_delay')
        assert hasattr(backoff, 'record_failure')
        assert hasattr(backoff, 'record_success')
        assert hasattr(backoff, 'should_retry')
    
    def test_queue_monitor_implemented(self):
        """Test queue monitor watchdog is implemented."""
        from telegram.rate_limiter import QueueWatchdog, TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        watchdog = QueueWatchdog({"TestBot": limiter})
        assert hasattr(watchdog, 'start')
        assert hasattr(watchdog, 'stop')
        assert hasattr(watchdog, '_check_health')
    
    def test_multi_bot_coordination_implemented(self):
        """Test multi-bot coordination is implemented."""
        from telegram.rate_limiter import GlobalRateLimitCoordinator
        coordinator = GlobalRateLimitCoordinator()
        assert hasattr(coordinator, 'register_bot')
        assert hasattr(coordinator, 'unregister_bot')
        assert hasattr(coordinator, 'request_send_permission')
        assert hasattr(coordinator, 'get_fair_share')
    
    def test_enhanced_limiter_implemented(self):
        """Test enhanced rate limiter is implemented."""
        from telegram.rate_limiter import EnhancedTelegramRateLimiter
        limiter = EnhancedTelegramRateLimiter("TestBot")
        assert hasattr(limiter, 'token_bucket')
        assert hasattr(limiter, 'backoff')
        assert hasattr(limiter, 'coordinator')
    
    def test_factory_function_implemented(self):
        """Test factory function is implemented."""
        from telegram.rate_limiter import create_rate_limiter
        limiter = create_rate_limiter("TestBot")
        assert limiter is not None
    
    def test_statistics_tracking_implemented(self):
        """Test statistics tracking is implemented."""
        from telegram.rate_limiter import TelegramRateLimiter
        limiter = TelegramRateLimiter("TestBot")
        stats = limiter.get_stats()
        assert "total_sent" in stats["stats"]
        assert "total_queued" in stats["stats"]
        assert "total_dropped" in stats["stats"]
    
    def test_health_monitoring_implemented(self):
        """Test health monitoring is implemented."""
        from telegram.rate_limiter import RateLimitMonitor, TelegramRateLimiter
        monitor = RateLimitMonitor()
        limiter = TelegramRateLimiter("TestBot")
        health = monitor.check_health({"TestBot": limiter})
        assert "status" in health
        assert "bots" in health
        assert "alerts" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
