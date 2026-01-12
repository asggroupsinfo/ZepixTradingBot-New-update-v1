"""
User Session Manager for Multi-Telegram System.

This module tracks user state across multiple bots:
- Session creation and management
- State persistence
- Cross-bot session synchronization
- Session timeout handling

Based on Document 18: TELEGRAM_SYSTEM_ARCHITECTURE.md

Version: 1.0
Date: 2026-01-12
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json


logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session state enumeration."""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    LOCKED = "locked"


class ConversationState(Enum):
    """Conversation state enumeration."""
    IDLE = "idle"
    AWAITING_INPUT = "awaiting_input"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    IN_MENU = "in_menu"
    PROCESSING = "processing"


@dataclass
class UserPreferences:
    """User preferences."""
    voice_alerts_enabled: bool = True
    notification_sound: bool = True
    daily_report_time: str = "18:00"
    timezone: str = "UTC"
    language: str = "en"
    theme: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "voice_alerts_enabled": self.voice_alerts_enabled,
            "notification_sound": self.notification_sound,
            "daily_report_time": self.daily_report_time,
            "timezone": self.timezone,
            "language": self.language,
            "theme": self.theme
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create from dictionary."""
        return cls(
            voice_alerts_enabled=data.get("voice_alerts_enabled", True),
            notification_sound=data.get("notification_sound", True),
            daily_report_time=data.get("daily_report_time", "18:00"),
            timezone=data.get("timezone", "UTC"),
            language=data.get("language", "en"),
            theme=data.get("theme", "default")
        )


@dataclass
class ConversationContext:
    """Context for ongoing conversation."""
    state: ConversationState = ConversationState.IDLE
    current_menu: Optional[str] = None
    pending_action: Optional[str] = None
    pending_params: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    max_history: int = 10
    
    def add_to_history(self, item: str) -> None:
        """Add item to history."""
        self.history.append(item)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def clear_pending(self) -> None:
        """Clear pending action."""
        self.pending_action = None
        self.pending_params = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "state": self.state.value,
            "current_menu": self.current_menu,
            "pending_action": self.pending_action,
            "pending_params": self.pending_params,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        """Create from dictionary."""
        return cls(
            state=ConversationState(data.get("state", "idle")),
            current_menu=data.get("current_menu"),
            pending_action=data.get("pending_action"),
            pending_params=data.get("pending_params", {}),
            history=data.get("history", [])
        )


@dataclass
class UserSession:
    """User session data."""
    user_id: str
    chat_id: str
    username: Optional[str] = None
    state: SessionState = SessionState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    preferences: UserPreferences = field(default_factory=UserPreferences)
    context: ConversationContext = field(default_factory=ConversationContext)
    data: Dict[str, Any] = field(default_factory=dict)
    is_admin: bool = False
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
        if self.state == SessionState.IDLE:
            self.state = SessionState.ACTIVE
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session is expired."""
        if self.state == SessionState.EXPIRED:
            return True
        elapsed = datetime.now() - self.last_activity
        return elapsed > timedelta(minutes=timeout_minutes)
    
    def expire(self) -> None:
        """Expire the session."""
        self.state = SessionState.EXPIRED
    
    def set_data(self, key: str, value: Any) -> None:
        """Set session data."""
        self.data[key] = value
        self.update_activity()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        return self.data.get(key, default)
    
    def clear_data(self, key: Optional[str] = None) -> None:
        """Clear session data."""
        if key:
            self.data.pop(key, None)
        else:
            self.data.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "username": self.username,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "preferences": self.preferences.to_dict(),
            "context": self.context.to_dict(),
            "data": self.data,
            "is_admin": self.is_admin
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            chat_id=data["chat_id"],
            username=data.get("username"),
            state=SessionState(data.get("state", "active")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            last_activity=datetime.fromisoformat(data["last_activity"]) if "last_activity" in data else datetime.now(),
            preferences=UserPreferences.from_dict(data.get("preferences", {})),
            context=ConversationContext.from_dict(data.get("context", {})),
            data=data.get("data", {}),
            is_admin=data.get("is_admin", False)
        )


class SessionStorage:
    """Storage backend for sessions."""
    
    def __init__(self):
        """Initialize storage."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def save(self, session: UserSession) -> bool:
        """Save session to storage."""
        self._sessions[session.user_id] = session.to_dict()
        return True
    
    def load(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load session from storage."""
        return self._sessions.get(user_id)
    
    def delete(self, user_id: str) -> bool:
        """Delete session from storage."""
        if user_id in self._sessions:
            del self._sessions[user_id]
            return True
        return False
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all sessions."""
        return list(self._sessions.values())
    
    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()


class SessionManager:
    """
    Manages user sessions across multiple bots.
    
    Features:
    - Session creation and retrieval
    - State persistence
    - Session timeout handling
    - Cross-bot synchronization
    """
    
    def __init__(self, storage: Optional[SessionStorage] = None,
                 session_timeout_minutes: int = 30):
        """Initialize session manager."""
        self.storage = storage or SessionStorage()
        self.session_timeout = session_timeout_minutes
        self._active_sessions: Dict[str, UserSession] = {}
        self._admin_users: List[str] = []
    
    def create_session(self, user_id: str, chat_id: str,
                      username: Optional[str] = None) -> UserSession:
        """Create a new session."""
        session = UserSession(
            user_id=user_id,
            chat_id=chat_id,
            username=username,
            is_admin=user_id in self._admin_users
        )
        
        self._active_sessions[user_id] = session
        self.storage.save(session)
        
        logger.info(f"Created session for user {user_id}")
        return session
    
    def get_session(self, user_id: str) -> Optional[UserSession]:
        """Get existing session."""
        if user_id in self._active_sessions:
            session = self._active_sessions[user_id]
            if not session.is_expired(self.session_timeout):
                return session
            else:
                self._handle_expired_session(session)
                return None
        
        stored_data = self.storage.load(user_id)
        if stored_data:
            session = UserSession.from_dict(stored_data)
            if not session.is_expired(self.session_timeout):
                self._active_sessions[user_id] = session
                return session
            else:
                self._handle_expired_session(session)
        
        return None
    
    def get_or_create_session(self, user_id: str, chat_id: str,
                             username: Optional[str] = None) -> UserSession:
        """Get existing session or create new one."""
        session = self.get_session(user_id)
        if session:
            session.update_activity()
            return session
        return self.create_session(user_id, chat_id, username)
    
    def update_session(self, session: UserSession) -> bool:
        """Update session in storage."""
        session.update_activity()
        self._active_sessions[session.user_id] = session
        return self.storage.save(session)
    
    def end_session(self, user_id: str) -> bool:
        """End a session."""
        if user_id in self._active_sessions:
            session = self._active_sessions[user_id]
            session.expire()
            self.storage.save(session)
            del self._active_sessions[user_id]
            logger.info(f"Ended session for user {user_id}")
            return True
        return False
    
    def _handle_expired_session(self, session: UserSession) -> None:
        """Handle expired session."""
        session.expire()
        self.storage.save(session)
        self._active_sessions.pop(session.user_id, None)
        logger.info(f"Session expired for user {session.user_id}")
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        expired_count = 0
        for user_id in list(self._active_sessions.keys()):
            session = self._active_sessions[user_id]
            if session.is_expired(self.session_timeout):
                self._handle_expired_session(session)
                expired_count += 1
        return expired_count
    
    def set_conversation_state(self, user_id: str, 
                              state: ConversationState) -> bool:
        """Set conversation state for user."""
        session = self.get_session(user_id)
        if session:
            session.context.state = state
            return self.update_session(session)
        return False
    
    def set_current_menu(self, user_id: str, menu: str) -> bool:
        """Set current menu for user."""
        session = self.get_session(user_id)
        if session:
            session.context.current_menu = menu
            return self.update_session(session)
        return False
    
    def set_pending_action(self, user_id: str, action: str,
                          params: Optional[Dict[str, Any]] = None) -> bool:
        """Set pending action for user."""
        session = self.get_session(user_id)
        if session:
            session.context.pending_action = action
            session.context.pending_params = params or {}
            session.context.state = ConversationState.AWAITING_CONFIRMATION
            return self.update_session(session)
        return False
    
    def clear_pending_action(self, user_id: str) -> bool:
        """Clear pending action for user."""
        session = self.get_session(user_id)
        if session:
            session.context.clear_pending()
            session.context.state = ConversationState.IDLE
            return self.update_session(session)
        return False
    
    def get_pending_action(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get pending action for user."""
        session = self.get_session(user_id)
        if session and session.context.pending_action:
            return {
                "action": session.context.pending_action,
                "params": session.context.pending_params
            }
        return None
    
    def add_admin_user(self, user_id: str) -> None:
        """Add user to admin list."""
        if user_id not in self._admin_users:
            self._admin_users.append(user_id)
            session = self.get_session(user_id)
            if session:
                session.is_admin = True
                self.update_session(session)
    
    def remove_admin_user(self, user_id: str) -> None:
        """Remove user from admin list."""
        if user_id in self._admin_users:
            self._admin_users.remove(user_id)
            session = self.get_session(user_id)
            if session:
                session.is_admin = False
                self.update_session(session)
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin."""
        session = self.get_session(user_id)
        return session.is_admin if session else user_id in self._admin_users
    
    def get_active_sessions(self) -> List[UserSession]:
        """Get all active sessions."""
        return list(self._active_sessions.values())
    
    def get_session_count(self) -> int:
        """Get count of active sessions."""
        return len(self._active_sessions)
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences."""
        session = self.get_session(user_id)
        return session.preferences if session else None
    
    def update_user_preferences(self, user_id: str, 
                               preferences: UserPreferences) -> bool:
        """Update user preferences."""
        session = self.get_session(user_id)
        if session:
            session.preferences = preferences
            return self.update_session(session)
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        active_count = len(self._active_sessions)
        admin_count = sum(1 for s in self._active_sessions.values() if s.is_admin)
        
        return {
            "active_sessions": active_count,
            "admin_sessions": admin_count,
            "total_stored": len(self.storage.get_all()),
            "timeout_minutes": self.session_timeout
        }


def create_session_manager(session_timeout_minutes: int = 30) -> SessionManager:
    """Factory function to create Session Manager."""
    return SessionManager(session_timeout_minutes=session_timeout_minutes)
