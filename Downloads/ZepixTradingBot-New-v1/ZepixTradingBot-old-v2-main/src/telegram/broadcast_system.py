"""
Broadcast System for Multi-Telegram System.

This module provides message broadcasting capabilities:
- Send messages to all users/bots
- Priority-based broadcasting
- Scheduled broadcasts
- Broadcast history tracking

Based on Document 18: TELEGRAM_SYSTEM_ARCHITECTURE.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
import asyncio


logger = logging.getLogger(__name__)


class BroadcastType(Enum):
    """Broadcast type enumeration."""
    ALL_BOTS = "all_bots"
    ALL_USERS = "all_users"
    SPECIFIC_BOT = "specific_bot"
    SPECIFIC_USERS = "specific_users"
    ADMINS_ONLY = "admins_only"


class BroadcastPriority(Enum):
    """Broadcast priority enumeration."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class BroadcastStatus(Enum):
    """Broadcast status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


@dataclass
class BroadcastTarget:
    """Target for broadcast."""
    broadcast_type: BroadcastType
    bot_ids: List[str] = field(default_factory=list)
    user_ids: List[str] = field(default_factory=list)
    exclude_users: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "broadcast_type": self.broadcast_type.value,
            "bot_ids": self.bot_ids,
            "user_ids": self.user_ids,
            "exclude_users": self.exclude_users
        }


@dataclass
class BroadcastMessage:
    """Broadcast message definition."""
    message_id: str
    content: str
    target: BroadcastTarget
    priority: BroadcastPriority = BroadcastPriority.NORMAL
    status: BroadcastStatus = BroadcastStatus.PENDING
    parse_mode: str = "HTML"
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "target": self.target.to_dict(),
            "priority": self.priority.value,
            "status": self.status.value,
            "parse_mode": self.parse_mode,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "error_message": self.error_message
        }


@dataclass
class BroadcastResult:
    """Result of a broadcast operation."""
    message_id: str
    success: bool
    total_targets: int
    successful_sends: int
    failed_sends: int
    duration_seconds: float
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "success": self.success,
            "total_targets": self.total_targets,
            "successful_sends": self.successful_sends,
            "failed_sends": self.failed_sends,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors
        }


class MockBroadcastBot:
    """Mock bot for broadcasting."""
    
    def __init__(self, bot_id: str):
        """Initialize mock bot."""
        self.bot_id = bot_id
        self._sent_messages: List[Dict[str, Any]] = []
    
    async def send_message(self, chat_id: str, text: str,
                          parse_mode: str = "HTML") -> bool:
        """Send message (mock)."""
        self._sent_messages.append({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """Get sent messages."""
        return self._sent_messages.copy()


class BroadcastSystem:
    """
    System for broadcasting messages to multiple bots/users.
    
    Features:
    - Multi-target broadcasting
    - Priority-based queue
    - Scheduled broadcasts
    - History tracking
    - Error handling
    """
    
    def __init__(self):
        """Initialize broadcast system."""
        self._bots: Dict[str, MockBroadcastBot] = {}
        self._users: Dict[str, str] = {}
        self._admin_users: Set[str] = set()
        self._message_queue: List[BroadcastMessage] = []
        self._history: List[BroadcastMessage] = []
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._message_counter = 0
        
        self._init_default_bots()
    
    def _init_default_bots(self) -> None:
        """Initialize default bots."""
        self._bots["controller"] = MockBroadcastBot("controller")
        self._bots["notification"] = MockBroadcastBot("notification")
        self._bots["analytics"] = MockBroadcastBot("analytics")
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        self._message_counter += 1
        return f"broadcast_{self._message_counter}_{int(datetime.now().timestamp())}"
    
    def register_bot(self, bot_id: str, bot: MockBroadcastBot) -> None:
        """Register a bot for broadcasting."""
        self._bots[bot_id] = bot
        logger.info(f"Registered bot: {bot_id}")
    
    def register_user(self, user_id: str, chat_id: str, 
                     is_admin: bool = False) -> None:
        """Register a user for broadcasting."""
        self._users[user_id] = chat_id
        if is_admin:
            self._admin_users.add(user_id)
        logger.info(f"Registered user: {user_id}")
    
    def unregister_user(self, user_id: str) -> None:
        """Unregister a user."""
        self._users.pop(user_id, None)
        self._admin_users.discard(user_id)
    
    async def start(self) -> None:
        """Start broadcast processor."""
        self._running = True
        self._processor_task = asyncio.create_task(self._process_queue())
        logger.info("Broadcast system started")
    
    async def stop(self) -> None:
        """Stop broadcast processor."""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Broadcast system stopped")
    
    async def _process_queue(self) -> None:
        """Process broadcast queue."""
        while self._running:
            now = datetime.now()
            
            for message in list(self._message_queue):
                if message.status == BroadcastStatus.SCHEDULED:
                    if message.scheduled_at and message.scheduled_at <= now:
                        message.status = BroadcastStatus.PENDING
                
                if message.status == BroadcastStatus.PENDING:
                    await self._send_broadcast(message)
            
            await asyncio.sleep(1)
    
    async def _send_broadcast(self, message: BroadcastMessage) -> BroadcastResult:
        """Send a broadcast message."""
        start_time = datetime.now()
        message.status = BroadcastStatus.IN_PROGRESS
        message.sent_at = start_time
        
        targets = self._resolve_targets(message.target)
        errors = []
        success_count = 0
        failure_count = 0
        
        for bot_id, chat_id in targets:
            try:
                bot = self._bots.get(bot_id)
                if bot:
                    await bot.send_message(chat_id, message.content, message.parse_mode)
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append(f"Bot not found: {bot_id}")
            except Exception as e:
                failure_count += 1
                errors.append(f"Failed to send to {chat_id}: {str(e)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        message.success_count = success_count
        message.failure_count = failure_count
        message.completed_at = end_time
        message.status = BroadcastStatus.COMPLETED if failure_count == 0 else BroadcastStatus.FAILED
        
        if errors:
            message.error_message = "; ".join(errors[:5])
        
        self._message_queue.remove(message)
        self._history.append(message)
        
        return BroadcastResult(
            message_id=message.message_id,
            success=failure_count == 0,
            total_targets=len(targets),
            successful_sends=success_count,
            failed_sends=failure_count,
            duration_seconds=duration,
            errors=errors
        )
    
    def _resolve_targets(self, target: BroadcastTarget) -> List[tuple]:
        """Resolve broadcast targets to (bot_id, chat_id) pairs."""
        targets = []
        
        if target.broadcast_type == BroadcastType.ALL_BOTS:
            for bot_id in self._bots.keys():
                for user_id, chat_id in self._users.items():
                    if user_id not in target.exclude_users:
                        targets.append((bot_id, chat_id))
        
        elif target.broadcast_type == BroadcastType.ALL_USERS:
            default_bot = "notification"
            for user_id, chat_id in self._users.items():
                if user_id not in target.exclude_users:
                    targets.append((default_bot, chat_id))
        
        elif target.broadcast_type == BroadcastType.SPECIFIC_BOT:
            for bot_id in target.bot_ids:
                for user_id, chat_id in self._users.items():
                    if user_id not in target.exclude_users:
                        targets.append((bot_id, chat_id))
        
        elif target.broadcast_type == BroadcastType.SPECIFIC_USERS:
            default_bot = "notification"
            for user_id in target.user_ids:
                if user_id in self._users and user_id not in target.exclude_users:
                    targets.append((default_bot, self._users[user_id]))
        
        elif target.broadcast_type == BroadcastType.ADMINS_ONLY:
            default_bot = "controller"
            for user_id in self._admin_users:
                if user_id in self._users and user_id not in target.exclude_users:
                    targets.append((default_bot, self._users[user_id]))
        
        return targets
    
    def queue_broadcast(self, content: str, target: BroadcastTarget,
                       priority: BroadcastPriority = BroadcastPriority.NORMAL,
                       scheduled_at: Optional[datetime] = None) -> str:
        """Queue a broadcast message."""
        message = BroadcastMessage(
            message_id=self._generate_message_id(),
            content=content,
            target=target,
            priority=priority,
            status=BroadcastStatus.SCHEDULED if scheduled_at else BroadcastStatus.PENDING,
            scheduled_at=scheduled_at
        )
        
        self._message_queue.append(message)
        self._message_queue.sort(key=lambda m: m.priority.value, reverse=True)
        
        logger.info(f"Queued broadcast: {message.message_id}")
        return message.message_id
    
    async def broadcast_to_all_bots(self, content: str,
                                   priority: BroadcastPriority = BroadcastPriority.NORMAL) -> str:
        """Broadcast to all bots."""
        target = BroadcastTarget(broadcast_type=BroadcastType.ALL_BOTS)
        return self.queue_broadcast(content, target, priority)
    
    async def broadcast_to_all_users(self, content: str,
                                    priority: BroadcastPriority = BroadcastPriority.NORMAL) -> str:
        """Broadcast to all users."""
        target = BroadcastTarget(broadcast_type=BroadcastType.ALL_USERS)
        return self.queue_broadcast(content, target, priority)
    
    async def broadcast_to_admins(self, content: str,
                                 priority: BroadcastPriority = BroadcastPriority.HIGH) -> str:
        """Broadcast to admin users only."""
        target = BroadcastTarget(broadcast_type=BroadcastType.ADMINS_ONLY)
        return self.queue_broadcast(content, target, priority)
    
    async def broadcast_critical(self, content: str) -> str:
        """Broadcast critical message to all bots."""
        target = BroadcastTarget(broadcast_type=BroadcastType.ALL_BOTS)
        return self.queue_broadcast(content, target, BroadcastPriority.CRITICAL)
    
    def cancel_broadcast(self, message_id: str) -> bool:
        """Cancel a pending broadcast."""
        for message in self._message_queue:
            if message.message_id == message_id:
                if message.status in [BroadcastStatus.PENDING, BroadcastStatus.SCHEDULED]:
                    message.status = BroadcastStatus.CANCELLED
                    self._message_queue.remove(message)
                    self._history.append(message)
                    return True
        return False
    
    def get_pending_broadcasts(self) -> List[BroadcastMessage]:
        """Get pending broadcasts."""
        return [m for m in self._message_queue 
                if m.status in [BroadcastStatus.PENDING, BroadcastStatus.SCHEDULED]]
    
    def get_broadcast_history(self, limit: int = 50) -> List[BroadcastMessage]:
        """Get broadcast history."""
        return self._history[-limit:]
    
    def get_broadcast_status(self, message_id: str) -> Optional[BroadcastMessage]:
        """Get status of a broadcast."""
        for message in self._message_queue + self._history:
            if message.message_id == message_id:
                return message
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get broadcast statistics."""
        completed = [m for m in self._history if m.status == BroadcastStatus.COMPLETED]
        failed = [m for m in self._history if m.status == BroadcastStatus.FAILED]
        
        total_success = sum(m.success_count for m in completed)
        total_failure = sum(m.failure_count for m in self._history)
        
        return {
            "pending_count": len(self._message_queue),
            "completed_count": len(completed),
            "failed_count": len(failed),
            "total_messages_sent": total_success,
            "total_failures": total_failure,
            "registered_bots": len(self._bots),
            "registered_users": len(self._users),
            "admin_users": len(self._admin_users)
        }
    
    def is_running(self) -> bool:
        """Check if broadcast system is running."""
        return self._running


def create_broadcast_system() -> BroadcastSystem:
    """Factory function to create Broadcast System."""
    return BroadcastSystem()
