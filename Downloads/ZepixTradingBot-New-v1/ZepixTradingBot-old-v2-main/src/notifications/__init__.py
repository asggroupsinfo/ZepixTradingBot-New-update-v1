"""
Notification System Package

Document 19: Notification System Specification
Centralized notification routing for all bot events with priority-based delivery.

Components:
- NotificationRouter: Central dispatch for all notifications
- NotificationFormatter: Template-based message formatting
- DeliveryManager: Robust delivery with retry and rate limiting
- UserPreferences: Granular notification settings per user
- AlertRouter: Route alerts to specific bots/chats
- VoiceAlertSystem: Voice alert generation and delivery
- NotificationStats: Tracking and analytics
"""

from src.notifications.notification_router import (
    NotificationPriority,
    NotificationType,
    NotificationRouter,
)
from src.notifications.notification_formatter import (
    NotificationFormatter,
    NotificationTemplate,
    TemplateManager,
)
from src.notifications.delivery_manager import (
    DeliveryStatus,
    DeliveryResult,
    DeliveryManager,
    NotificationQueueManager,
)
from src.notifications.user_preferences import (
    NotificationPreference,
    UserNotificationSettings,
    PreferencesManager,
)
from src.notifications.alert_router import (
    AlertType,
    RoutingRule,
    AlertRouter,
)
from src.notifications.voice_alerts import (
    VoiceAlertConfig,
    VoiceAlertSystem,
)
from src.notifications.notification_stats import (
    NotificationStats,
    StatsAggregator,
)

__all__ = [
    # Router
    'NotificationPriority',
    'NotificationType',
    'NotificationRouter',
    # Formatter
    'NotificationFormatter',
    'NotificationTemplate',
    'TemplateManager',
    # Delivery
    'DeliveryStatus',
    'DeliveryResult',
    'DeliveryManager',
    'NotificationQueueManager',
    # Preferences
    'NotificationPreference',
    'UserNotificationSettings',
    'PreferencesManager',
    # Alert Routing
    'AlertType',
    'RoutingRule',
    'AlertRouter',
    # Voice
    'VoiceAlertConfig',
    'VoiceAlertSystem',
    # Stats
    'NotificationStats',
    'StatsAggregator',
]

__version__ = '1.0.0'
