"""
Bot Orchestrator for Multi-Telegram System.

This module manages the lifecycle of all 3 Telegram bots:
- Controller Bot: System control & commands
- Notification Bot: Trade alerts & signals
- Analytics Bot: Reports & statistics

Based on Document 18: TELEGRAM_SYSTEM_ARCHITECTURE.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio


logger = logging.getLogger(__name__)


class BotType(Enum):
    """Bot type enumeration."""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"


class BotState(Enum):
    """Bot state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    PAUSED = "paused"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class BotConfig:
    """Configuration for a single bot."""
    bot_type: BotType
    token: str
    chat_id: str
    enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_per_minute: int = 20
    rate_limit_per_second: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bot_type": self.bot_type.value,
            "token": self.token[:10] + "..." if self.token else "",
            "chat_id": self.chat_id,
            "enabled": self.enabled,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "rate_limit_per_second": self.rate_limit_per_second
        }


@dataclass
class BotStatus:
    """Status of a single bot."""
    bot_type: BotType
    state: BotState
    last_message_time: Optional[datetime] = None
    messages_sent: int = 0
    errors_count: int = 0
    uptime_seconds: float = 0.0
    start_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bot_type": self.bot_type.value,
            "state": self.state.value,
            "last_message_time": self.last_message_time.isoformat() if self.last_message_time else None,
            "messages_sent": self.messages_sent,
            "errors_count": self.errors_count,
            "uptime_seconds": self.uptime_seconds,
            "start_time": self.start_time.isoformat() if self.start_time else None
        }


@dataclass
class QueuedMessage:
    """Message queued for sending."""
    bot_type: BotType
    chat_id: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    parse_mode: str = "HTML"
    reply_markup: Optional[Any] = None
    created_at: datetime = field(default_factory=datetime.now)
    retries: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bot_type": self.bot_type.value,
            "chat_id": self.chat_id,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "priority": self.priority.value,
            "parse_mode": self.parse_mode,
            "created_at": self.created_at.isoformat(),
            "retries": self.retries
        }


class MockBot:
    """Mock Telegram Bot for testing."""
    
    def __init__(self, token: str, bot_type: BotType):
        """Initialize mock bot."""
        self.token = token
        self.bot_type = bot_type
        self._messages: List[Dict[str, Any]] = []
        self._running = False
    
    async def send_message(self, chat_id: str, text: str, 
                          parse_mode: str = "HTML",
                          reply_markup: Optional[Any] = None) -> Dict[str, Any]:
        """Send a message (mock)."""
        message = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "reply_markup": reply_markup,
            "timestamp": datetime.now().isoformat(),
            "bot_type": self.bot_type.value
        }
        self._messages.append(message)
        logger.info(f"{self.bot_type.value}: Message sent to {chat_id}")
        return {"message_id": len(self._messages), "ok": True}
    
    async def send_voice(self, chat_id: str, voice: Any) -> Dict[str, Any]:
        """Send a voice message (mock)."""
        message = {
            "chat_id": chat_id,
            "type": "voice",
            "timestamp": datetime.now().isoformat(),
            "bot_type": self.bot_type.value
        }
        self._messages.append(message)
        return {"message_id": len(self._messages), "ok": True}
    
    async def start(self) -> None:
        """Start the bot (mock)."""
        self._running = True
        logger.info(f"{self.bot_type.value}: Bot started")
    
    async def stop(self) -> None:
        """Stop the bot (mock)."""
        self._running = False
        logger.info(f"{self.bot_type.value}: Bot stopped")
    
    def is_running(self) -> bool:
        """Check if bot is running."""
        return self._running
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all sent messages."""
        return self._messages.copy()
    
    def clear_messages(self) -> None:
        """Clear message history."""
        self._messages.clear()


class BotOrchestrator:
    """
    Manages lifecycle of all 3 Telegram bots.
    
    Features:
    - Bot lifecycle management (start, stop, restart)
    - Health monitoring
    - Message queue management
    - Error recovery with retries
    - Graceful shutdown
    """
    
    def __init__(self, configs: Optional[Dict[BotType, BotConfig]] = None):
        """Initialize Bot Orchestrator."""
        self.configs = configs or {}
        self.bots: Dict[BotType, MockBot] = {}
        self.statuses: Dict[BotType, BotStatus] = {}
        self.message_queue: List[QueuedMessage] = []
        self._running = False
        self._queue_processor_task: Optional[asyncio.Task] = None
        
        self._init_default_configs()
        self._init_bots()
        self._init_statuses()
    
    def _init_default_configs(self) -> None:
        """Initialize default configurations."""
        if BotType.CONTROLLER not in self.configs:
            self.configs[BotType.CONTROLLER] = BotConfig(
                bot_type=BotType.CONTROLLER,
                token="CONTROLLER_TOKEN",
                chat_id="CHAT_ID"
            )
        if BotType.NOTIFICATION not in self.configs:
            self.configs[BotType.NOTIFICATION] = BotConfig(
                bot_type=BotType.NOTIFICATION,
                token="NOTIFICATION_TOKEN",
                chat_id="CHAT_ID"
            )
        if BotType.ANALYTICS not in self.configs:
            self.configs[BotType.ANALYTICS] = BotConfig(
                bot_type=BotType.ANALYTICS,
                token="ANALYTICS_TOKEN",
                chat_id="CHAT_ID"
            )
    
    def _init_bots(self) -> None:
        """Initialize bot instances."""
        for bot_type, config in self.configs.items():
            self.bots[bot_type] = MockBot(config.token, bot_type)
    
    def _init_statuses(self) -> None:
        """Initialize bot statuses."""
        for bot_type in self.configs.keys():
            self.statuses[bot_type] = BotStatus(
                bot_type=bot_type,
                state=BotState.STOPPED
            )
    
    async def start_all(self) -> Dict[BotType, bool]:
        """Start all bots."""
        results = {}
        for bot_type, bot in self.bots.items():
            try:
                await self.start_bot(bot_type)
                results[bot_type] = True
            except Exception as e:
                logger.error(f"Failed to start {bot_type.value}: {e}")
                results[bot_type] = False
        
        self._running = True
        self._queue_processor_task = asyncio.create_task(self._process_queue())
        
        return results
    
    async def stop_all(self) -> Dict[BotType, bool]:
        """Stop all bots gracefully."""
        self._running = False
        
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
            try:
                await self._queue_processor_task
            except asyncio.CancelledError:
                pass
        
        results = {}
        for bot_type in self.bots.keys():
            try:
                await self.stop_bot(bot_type)
                results[bot_type] = True
            except Exception as e:
                logger.error(f"Failed to stop {bot_type.value}: {e}")
                results[bot_type] = False
        
        return results
    
    async def start_bot(self, bot_type: BotType) -> bool:
        """Start a specific bot."""
        if bot_type not in self.bots:
            return False
        
        status = self.statuses[bot_type]
        status.state = BotState.STARTING
        
        try:
            await self.bots[bot_type].start()
            status.state = BotState.RUNNING
            status.start_time = datetime.now()
            logger.info(f"Bot {bot_type.value} started successfully")
            return True
        except Exception as e:
            status.state = BotState.ERROR
            status.errors_count += 1
            logger.error(f"Failed to start bot {bot_type.value}: {e}")
            return False
    
    async def stop_bot(self, bot_type: BotType) -> bool:
        """Stop a specific bot."""
        if bot_type not in self.bots:
            return False
        
        status = self.statuses[bot_type]
        status.state = BotState.STOPPING
        
        try:
            await self.bots[bot_type].stop()
            status.state = BotState.STOPPED
            if status.start_time:
                status.uptime_seconds = (datetime.now() - status.start_time).total_seconds()
            logger.info(f"Bot {bot_type.value} stopped successfully")
            return True
        except Exception as e:
            status.state = BotState.ERROR
            status.errors_count += 1
            logger.error(f"Failed to stop bot {bot_type.value}: {e}")
            return False
    
    async def restart_bot(self, bot_type: BotType) -> bool:
        """Restart a specific bot."""
        await self.stop_bot(bot_type)
        await asyncio.sleep(0.5)
        return await self.start_bot(bot_type)
    
    async def pause_bot(self, bot_type: BotType) -> bool:
        """Pause a specific bot."""
        if bot_type not in self.statuses:
            return False
        
        self.statuses[bot_type].state = BotState.PAUSED
        logger.info(f"Bot {bot_type.value} paused")
        return True
    
    async def resume_bot(self, bot_type: BotType) -> bool:
        """Resume a paused bot."""
        if bot_type not in self.statuses:
            return False
        
        if self.statuses[bot_type].state == BotState.PAUSED:
            self.statuses[bot_type].state = BotState.RUNNING
            logger.info(f"Bot {bot_type.value} resumed")
            return True
        return False
    
    def queue_message(self, message: QueuedMessage) -> None:
        """Add message to queue."""
        self.message_queue.append(message)
        self.message_queue.sort(key=lambda m: m.priority.value, reverse=True)
    
    async def _process_queue(self) -> None:
        """Process message queue."""
        while self._running:
            if self.message_queue:
                message = self.message_queue.pop(0)
                await self._send_message(message)
            await asyncio.sleep(0.1)
    
    async def _send_message(self, message: QueuedMessage) -> bool:
        """Send a queued message."""
        bot = self.bots.get(message.bot_type)
        status = self.statuses.get(message.bot_type)
        
        if not bot or not status:
            return False
        
        if status.state != BotState.RUNNING:
            if message.retries < self.configs[message.bot_type].max_retries:
                message.retries += 1
                self.queue_message(message)
            return False
        
        try:
            await bot.send_message(
                chat_id=message.chat_id,
                text=message.content,
                parse_mode=message.parse_mode,
                reply_markup=message.reply_markup
            )
            status.messages_sent += 1
            status.last_message_time = datetime.now()
            return True
        except Exception as e:
            status.errors_count += 1
            logger.error(f"Failed to send message via {message.bot_type.value}: {e}")
            
            if message.retries < self.configs[message.bot_type].max_retries:
                message.retries += 1
                self.queue_message(message)
            return False
    
    def get_bot_status(self, bot_type: BotType) -> Optional[BotStatus]:
        """Get status of a specific bot."""
        return self.statuses.get(bot_type)
    
    def get_all_statuses(self) -> Dict[BotType, BotStatus]:
        """Get status of all bots."""
        return self.statuses.copy()
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get health report for all bots."""
        healthy_count = sum(
            1 for s in self.statuses.values() 
            if s.state == BotState.RUNNING
        )
        total_count = len(self.statuses)
        
        return {
            "overall_health": "healthy" if healthy_count == total_count else "degraded",
            "healthy_bots": healthy_count,
            "total_bots": total_count,
            "queue_size": len(self.message_queue),
            "bots": {
                bt.value: status.to_dict() 
                for bt, status in self.statuses.items()
            }
        }
    
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running
    
    def get_bot(self, bot_type: BotType) -> Optional[MockBot]:
        """Get a specific bot instance."""
        return self.bots.get(bot_type)


def create_bot_orchestrator(configs: Optional[Dict[BotType, BotConfig]] = None) -> BotOrchestrator:
    """Factory function to create Bot Orchestrator."""
    return BotOrchestrator(configs)
