"""
User Preferences - Granular Notification Settings

Document 19: Notification System Specification
Manages per-user notification preferences including muting, filtering, and delivery options.

Features:
- Per-user notification settings
- Mute specific notification types
- PnL display preferences
- Voice alert preferences
- Quiet hours configuration
- Notification grouping
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, time
import json


class NotificationPreference(Enum):
    """Notification preference options"""
    ALL = "all"              # Receive all notifications
    IMPORTANT_ONLY = "important_only"  # Only HIGH and CRITICAL
    CRITICAL_ONLY = "critical_only"    # Only CRITICAL
    NONE = "none"            # Muted
    CUSTOM = "custom"        # Custom filter


class PnLDisplayMode(Enum):
    """P&L display preferences"""
    FULL = "full"            # Show full P&L details
    SUMMARY = "summary"      # Show only net P&L
    PERCENTAGE = "percentage"  # Show as percentage
    HIDDEN = "hidden"        # Hide P&L completely


class VoicePreference(Enum):
    """Voice alert preferences"""
    ALL = "all"              # Voice for all eligible notifications
    CRITICAL_ONLY = "critical_only"  # Voice only for critical
    TRADES_ONLY = "trades_only"      # Voice only for trade events
    NONE = "none"            # No voice alerts


class GroupingMode(Enum):
    """Notification grouping mode"""
    NONE = "none"            # No grouping, send immediately
    BY_SYMBOL = "by_symbol"  # Group by trading symbol
    BY_TYPE = "by_type"      # Group by notification type
    TIMED = "timed"          # Group notifications within time window


@dataclass
class QuietHours:
    """Quiet hours configuration"""
    enabled: bool = False
    start_time: time = field(default_factory=lambda: time(22, 0))  # 10 PM
    end_time: time = field(default_factory=lambda: time(7, 0))     # 7 AM
    allow_critical: bool = True  # Allow critical notifications during quiet hours
    timezone: str = "UTC"
    
    def is_quiet_time(self, check_time: Optional[time] = None) -> bool:
        """Check if current time is within quiet hours"""
        if not self.enabled:
            return False
        
        current = check_time or datetime.now().time()
        
        # Handle overnight quiet hours (e.g., 22:00 to 07:00)
        if self.start_time > self.end_time:
            return current >= self.start_time or current <= self.end_time
        else:
            return self.start_time <= current <= self.end_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enabled": self.enabled,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "allow_critical": self.allow_critical,
            "timezone": self.timezone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuietHours':
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", False),
            start_time=time.fromisoformat(data.get("start_time", "22:00:00")),
            end_time=time.fromisoformat(data.get("end_time", "07:00:00")),
            allow_critical=data.get("allow_critical", True),
            timezone=data.get("timezone", "UTC")
        )


@dataclass
class NotificationFilter:
    """Custom notification filter"""
    include_types: Set[str] = field(default_factory=set)  # Types to include
    exclude_types: Set[str] = field(default_factory=set)  # Types to exclude
    min_priority: int = 1  # Minimum priority level (1-5)
    include_symbols: Set[str] = field(default_factory=set)  # Symbols to include (empty = all)
    exclude_symbols: Set[str] = field(default_factory=set)  # Symbols to exclude
    min_profit_threshold: Optional[float] = None  # Min profit for exit notifications
    
    def should_notify(
        self,
        notification_type: str,
        priority: int,
        symbol: Optional[str] = None,
        profit: Optional[float] = None
    ) -> bool:
        """Check if notification passes filter"""
        # Check type filters
        if self.include_types and notification_type not in self.include_types:
            return False
        if notification_type in self.exclude_types:
            return False
        
        # Check priority
        if priority < self.min_priority:
            return False
        
        # Check symbol filters
        if symbol:
            if self.include_symbols and symbol not in self.include_symbols:
                return False
            if symbol in self.exclude_symbols:
                return False
        
        # Check profit threshold
        if self.min_profit_threshold is not None and profit is not None:
            if abs(profit) < self.min_profit_threshold:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "include_types": list(self.include_types),
            "exclude_types": list(self.exclude_types),
            "min_priority": self.min_priority,
            "include_symbols": list(self.include_symbols),
            "exclude_symbols": list(self.exclude_symbols),
            "min_profit_threshold": self.min_profit_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationFilter':
        """Create from dictionary"""
        return cls(
            include_types=set(data.get("include_types", [])),
            exclude_types=set(data.get("exclude_types", [])),
            min_priority=data.get("min_priority", 1),
            include_symbols=set(data.get("include_symbols", [])),
            exclude_symbols=set(data.get("exclude_symbols", [])),
            min_profit_threshold=data.get("min_profit_threshold")
        )


@dataclass
class UserNotificationSettings:
    """Complete notification settings for a user"""
    user_id: int
    preference: NotificationPreference = NotificationPreference.ALL
    pnl_display: PnLDisplayMode = PnLDisplayMode.FULL
    voice_preference: VoicePreference = VoicePreference.ALL
    grouping_mode: GroupingMode = GroupingMode.NONE
    grouping_window_seconds: int = 60  # For TIMED grouping
    quiet_hours: QuietHours = field(default_factory=QuietHours)
    custom_filter: NotificationFilter = field(default_factory=NotificationFilter)
    
    # Specific mutes
    muted_types: Set[str] = field(default_factory=set)
    muted_symbols: Set[str] = field(default_factory=set)
    muted_plugins: Set[str] = field(default_factory=set)
    
    # Display preferences
    show_ticket_numbers: bool = True
    show_timestamps: bool = True
    show_commission: bool = True
    compact_mode: bool = False
    
    # Language and format
    language: str = "en"
    timezone: str = "UTC"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def should_notify(
        self,
        notification_type: str,
        priority: int,
        symbol: Optional[str] = None,
        plugin: Optional[str] = None,
        profit: Optional[float] = None
    ) -> bool:
        """Check if user should receive this notification"""
        # Check if completely muted
        if self.preference == NotificationPreference.NONE:
            return False
        
        # Check quiet hours
        if self.quiet_hours.is_quiet_time():
            if not self.quiet_hours.allow_critical or priority < 5:
                return False
        
        # Check preference level
        if self.preference == NotificationPreference.CRITICAL_ONLY and priority < 5:
            return False
        if self.preference == NotificationPreference.IMPORTANT_ONLY and priority < 4:
            return False
        
        # Check specific mutes
        if notification_type in self.muted_types:
            return False
        if symbol and symbol in self.muted_symbols:
            return False
        if plugin and plugin in self.muted_plugins:
            return False
        
        # Check custom filter
        if self.preference == NotificationPreference.CUSTOM:
            return self.custom_filter.should_notify(
                notification_type, priority, symbol, profit
            )
        
        return True
    
    def should_voice_alert(self, notification_type: str, priority: int) -> bool:
        """Check if voice alert should be sent"""
        if self.voice_preference == VoicePreference.NONE:
            return False
        
        if self.voice_preference == VoicePreference.CRITICAL_ONLY:
            return priority >= 5
        
        if self.voice_preference == VoicePreference.TRADES_ONLY:
            trade_types = {
                "entry_v3_dual", "entry_v6_single", "entry_v6_single_a",
                "exit_profit", "exit_loss", "tp1_hit", "tp2_hit", "sl_hit"
            }
            return notification_type in trade_types
        
        # VoicePreference.ALL
        return True
    
    def format_pnl(self, profit: float, commission: float = 0.0) -> str:
        """Format P&L according to user preferences"""
        if self.pnl_display == PnLDisplayMode.HIDDEN:
            return "[Hidden]"
        
        net = profit - commission
        
        if self.pnl_display == PnLDisplayMode.SUMMARY:
            sign = "+" if net >= 0 else ""
            return f"{sign}{net:.2f} USD"
        
        if self.pnl_display == PnLDisplayMode.PERCENTAGE:
            # Would need account balance for percentage
            sign = "+" if net >= 0 else ""
            return f"{sign}{net:.2f} USD"
        
        # FULL mode
        result = []
        if profit >= 0:
            result.append(f"Profit: +{profit:.2f} USD")
        else:
            result.append(f"Loss: {profit:.2f} USD")
        
        if self.show_commission and commission > 0:
            result.append(f"Commission: -{commission:.2f} USD")
        
        sign = "+" if net >= 0 else ""
        result.append(f"Net: {sign}{net:.2f} USD")
        
        return "\n".join(result)
    
    def mute_type(self, notification_type: str) -> None:
        """Mute a notification type"""
        self.muted_types.add(notification_type)
        self.updated_at = datetime.now()
    
    def unmute_type(self, notification_type: str) -> None:
        """Unmute a notification type"""
        self.muted_types.discard(notification_type)
        self.updated_at = datetime.now()
    
    def mute_symbol(self, symbol: str) -> None:
        """Mute notifications for a symbol"""
        self.muted_symbols.add(symbol)
        self.updated_at = datetime.now()
    
    def unmute_symbol(self, symbol: str) -> None:
        """Unmute notifications for a symbol"""
        self.muted_symbols.discard(symbol)
        self.updated_at = datetime.now()
    
    def mute_plugin(self, plugin: str) -> None:
        """Mute notifications from a plugin"""
        self.muted_plugins.add(plugin)
        self.updated_at = datetime.now()
    
    def unmute_plugin(self, plugin: str) -> None:
        """Unmute notifications from a plugin"""
        self.muted_plugins.discard(plugin)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "preference": self.preference.value,
            "pnl_display": self.pnl_display.value,
            "voice_preference": self.voice_preference.value,
            "grouping_mode": self.grouping_mode.value,
            "grouping_window_seconds": self.grouping_window_seconds,
            "quiet_hours": self.quiet_hours.to_dict(),
            "custom_filter": self.custom_filter.to_dict(),
            "muted_types": list(self.muted_types),
            "muted_symbols": list(self.muted_symbols),
            "muted_plugins": list(self.muted_plugins),
            "show_ticket_numbers": self.show_ticket_numbers,
            "show_timestamps": self.show_timestamps,
            "show_commission": self.show_commission,
            "compact_mode": self.compact_mode,
            "language": self.language,
            "timezone": self.timezone,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserNotificationSettings':
        """Create from dictionary"""
        return cls(
            user_id=data["user_id"],
            preference=NotificationPreference(data.get("preference", "all")),
            pnl_display=PnLDisplayMode(data.get("pnl_display", "full")),
            voice_preference=VoicePreference(data.get("voice_preference", "all")),
            grouping_mode=GroupingMode(data.get("grouping_mode", "none")),
            grouping_window_seconds=data.get("grouping_window_seconds", 60),
            quiet_hours=QuietHours.from_dict(data.get("quiet_hours", {})),
            custom_filter=NotificationFilter.from_dict(data.get("custom_filter", {})),
            muted_types=set(data.get("muted_types", [])),
            muted_symbols=set(data.get("muted_symbols", [])),
            muted_plugins=set(data.get("muted_plugins", [])),
            show_ticket_numbers=data.get("show_ticket_numbers", True),
            show_timestamps=data.get("show_timestamps", True),
            show_commission=data.get("show_commission", True),
            compact_mode=data.get("compact_mode", False),
            language=data.get("language", "en"),
            timezone=data.get("timezone", "UTC"),
            date_format=data.get("date_format", "%Y-%m-%d"),
            time_format=data.get("time_format", "%H:%M:%S"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


class PreferencesManager:
    """
    Preferences Manager
    
    Manages user notification preferences with persistence.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.preferences: Dict[int, UserNotificationSettings] = {}
        self._default_settings: Optional[UserNotificationSettings] = None
    
    def get_preferences(self, user_id: int) -> UserNotificationSettings:
        """Get preferences for user, creating default if not exists"""
        if user_id not in self.preferences:
            self.preferences[user_id] = UserNotificationSettings(user_id=user_id)
        return self.preferences[user_id]
    
    def set_preferences(self, settings: UserNotificationSettings) -> None:
        """Set preferences for user"""
        settings.updated_at = datetime.now()
        self.preferences[settings.user_id] = settings
    
    def update_preference(
        self,
        user_id: int,
        preference: NotificationPreference
    ) -> UserNotificationSettings:
        """Update notification preference level"""
        settings = self.get_preferences(user_id)
        settings.preference = preference
        settings.updated_at = datetime.now()
        return settings
    
    def update_voice_preference(
        self,
        user_id: int,
        voice_preference: VoicePreference
    ) -> UserNotificationSettings:
        """Update voice alert preference"""
        settings = self.get_preferences(user_id)
        settings.voice_preference = voice_preference
        settings.updated_at = datetime.now()
        return settings
    
    def update_pnl_display(
        self,
        user_id: int,
        pnl_display: PnLDisplayMode
    ) -> UserNotificationSettings:
        """Update P&L display mode"""
        settings = self.get_preferences(user_id)
        settings.pnl_display = pnl_display
        settings.updated_at = datetime.now()
        return settings
    
    def set_quiet_hours(
        self,
        user_id: int,
        enabled: bool,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        allow_critical: bool = True
    ) -> UserNotificationSettings:
        """Configure quiet hours"""
        settings = self.get_preferences(user_id)
        settings.quiet_hours.enabled = enabled
        if start_time:
            settings.quiet_hours.start_time = start_time
        if end_time:
            settings.quiet_hours.end_time = end_time
        settings.quiet_hours.allow_critical = allow_critical
        settings.updated_at = datetime.now()
        return settings
    
    def mute_type(self, user_id: int, notification_type: str) -> None:
        """Mute notification type for user"""
        settings = self.get_preferences(user_id)
        settings.mute_type(notification_type)
    
    def unmute_type(self, user_id: int, notification_type: str) -> None:
        """Unmute notification type for user"""
        settings = self.get_preferences(user_id)
        settings.unmute_type(notification_type)
    
    def mute_symbol(self, user_id: int, symbol: str) -> None:
        """Mute symbol for user"""
        settings = self.get_preferences(user_id)
        settings.mute_symbol(symbol)
    
    def unmute_symbol(self, user_id: int, symbol: str) -> None:
        """Unmute symbol for user"""
        settings = self.get_preferences(user_id)
        settings.unmute_symbol(symbol)
    
    def should_notify(
        self,
        user_id: int,
        notification_type: str,
        priority: int,
        symbol: Optional[str] = None,
        plugin: Optional[str] = None,
        profit: Optional[float] = None
    ) -> bool:
        """Check if user should receive notification"""
        settings = self.get_preferences(user_id)
        return settings.should_notify(
            notification_type, priority, symbol, plugin, profit
        )
    
    def should_voice_alert(
        self,
        user_id: int,
        notification_type: str,
        priority: int
    ) -> bool:
        """Check if user should receive voice alert"""
        settings = self.get_preferences(user_id)
        return settings.should_voice_alert(notification_type, priority)
    
    def get_all_users(self) -> List[int]:
        """Get all user IDs with preferences"""
        return list(self.preferences.keys())
    
    def delete_preferences(self, user_id: int) -> bool:
        """Delete user preferences"""
        if user_id in self.preferences:
            del self.preferences[user_id]
            return True
        return False
    
    def save(self) -> bool:
        """Save preferences to storage"""
        if not self.storage_path:
            return False
        
        try:
            data = {
                str(user_id): settings.to_dict()
                for user_id, settings in self.preferences.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def load(self) -> bool:
        """Load preferences from storage"""
        if not self.storage_path:
            return False
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.preferences = {
                int(user_id): UserNotificationSettings.from_dict(settings)
                for user_id, settings in data.items()
            }
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get preferences statistics"""
        total_users = len(self.preferences)
        
        by_preference = {}
        by_voice = {}
        by_pnl = {}
        muted_count = 0
        quiet_hours_enabled = 0
        
        for settings in self.preferences.values():
            pref = settings.preference.value
            by_preference[pref] = by_preference.get(pref, 0) + 1
            
            voice = settings.voice_preference.value
            by_voice[voice] = by_voice.get(voice, 0) + 1
            
            pnl = settings.pnl_display.value
            by_pnl[pnl] = by_pnl.get(pnl, 0) + 1
            
            if settings.preference == NotificationPreference.NONE:
                muted_count += 1
            
            if settings.quiet_hours.enabled:
                quiet_hours_enabled += 1
        
        return {
            "total_users": total_users,
            "by_preference": by_preference,
            "by_voice_preference": by_voice,
            "by_pnl_display": by_pnl,
            "muted_users": muted_count,
            "quiet_hours_enabled": quiet_hours_enabled
        }
