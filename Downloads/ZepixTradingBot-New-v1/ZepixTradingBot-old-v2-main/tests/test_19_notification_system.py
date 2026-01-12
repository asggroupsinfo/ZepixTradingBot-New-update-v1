"""
Test Suite for Document 19: Notification System Specification

Tests all notification system components:
- NotificationRouter: Central dispatch with priority-based routing
- NotificationFormatter: Template-based message formatting
- DeliveryManager: Retry, rate limiting, priority queuing
- UserPreferences: Granular notification settings
- AlertRouter: Route alerts to specific bots/chats
- VoiceAlertSystem: Voice alert generation and delivery
- NotificationStats: Statistics and analytics

Total: 100+ test cases covering all Document 19 requirements
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, time, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# TEST: Module Structure
# =============================================================================

class TestNotificationModuleStructure:
    """Test that all notification modules exist"""
    
    def test_notifications_package_exists(self):
        """Test notifications package exists"""
        notifications_path = project_root / "src" / "notifications"
        assert notifications_path.exists(), "notifications package should exist"
    
    def test_notification_router_exists(self):
        """Test notification_router.py exists"""
        module_path = project_root / "src" / "notifications" / "notification_router.py"
        assert module_path.exists(), "notification_router.py should exist"
    
    def test_notification_formatter_exists(self):
        """Test notification_formatter.py exists"""
        module_path = project_root / "src" / "notifications" / "notification_formatter.py"
        assert module_path.exists(), "notification_formatter.py should exist"
    
    def test_delivery_manager_exists(self):
        """Test delivery_manager.py exists"""
        module_path = project_root / "src" / "notifications" / "delivery_manager.py"
        assert module_path.exists(), "delivery_manager.py should exist"
    
    def test_user_preferences_exists(self):
        """Test user_preferences.py exists"""
        module_path = project_root / "src" / "notifications" / "user_preferences.py"
        assert module_path.exists(), "user_preferences.py should exist"
    
    def test_alert_router_exists(self):
        """Test alert_router.py exists"""
        module_path = project_root / "src" / "notifications" / "alert_router.py"
        assert module_path.exists(), "alert_router.py should exist"
    
    def test_voice_alerts_exists(self):
        """Test voice_alerts.py exists"""
        module_path = project_root / "src" / "notifications" / "voice_alerts.py"
        assert module_path.exists(), "voice_alerts.py should exist"
    
    def test_notification_stats_exists(self):
        """Test notification_stats.py exists"""
        module_path = project_root / "src" / "notifications" / "notification_stats.py"
        assert module_path.exists(), "notification_stats.py should exist"


# =============================================================================
# TEST: Notification Router Imports
# =============================================================================

class TestNotificationRouterImports:
    """Test NotificationRouter imports"""
    
    def test_import_notification_priority(self):
        """Test NotificationPriority import"""
        from src.notifications.notification_router import NotificationPriority
        assert NotificationPriority is not None
        assert hasattr(NotificationPriority, 'CRITICAL')
        assert hasattr(NotificationPriority, 'HIGH')
        assert hasattr(NotificationPriority, 'MEDIUM')
        assert hasattr(NotificationPriority, 'LOW')
        assert hasattr(NotificationPriority, 'INFO')
    
    def test_import_notification_type(self):
        """Test NotificationType import"""
        from src.notifications.notification_router import NotificationType
        assert NotificationType is not None
        assert hasattr(NotificationType, 'ENTRY_V3_DUAL')
        assert hasattr(NotificationType, 'EXIT_PROFIT')
        assert hasattr(NotificationType, 'EMERGENCY_STOP')
    
    def test_import_notification(self):
        """Test Notification import"""
        from src.notifications.notification_router import Notification
        assert Notification is not None
    
    def test_import_notification_router(self):
        """Test NotificationRouter import"""
        from src.notifications.notification_router import NotificationRouter
        assert NotificationRouter is not None
    
    def test_import_mock_telegram_manager(self):
        """Test MockTelegramManager import"""
        from src.notifications.notification_router import MockTelegramManager
        assert MockTelegramManager is not None


# =============================================================================
# TEST: Notification Router Functionality
# =============================================================================

class TestNotificationRouter:
    """Test NotificationRouter functionality"""
    
    def test_router_creation(self):
        """Test router creation"""
        from src.notifications.notification_router import NotificationRouter
        router = NotificationRouter()
        assert router is not None
        assert router.voice_enabled is True
    
    def test_priority_properties(self):
        """Test priority properties"""
        from src.notifications.notification_router import NotificationPriority
        
        critical = NotificationPriority.CRITICAL
        assert critical.color == "RED"
        assert critical.emoji == "🔴"
        assert critical.requires_voice is True
        assert critical.target_bot == "broadcast"
        
        info = NotificationPriority.INFO
        assert info.color == "GREEN"
        assert info.target_bot == "controller"
    
    def test_notification_type_defaults(self):
        """Test notification type default priorities"""
        from src.notifications.notification_router import NotificationType, NotificationPriority
        
        assert NotificationType.EMERGENCY_STOP.default_priority == NotificationPriority.CRITICAL
        assert NotificationType.ENTRY_V3_DUAL.default_priority == NotificationPriority.HIGH
        assert NotificationType.DAILY_SUMMARY.default_priority == NotificationPriority.LOW
        assert NotificationType.BOT_STARTED.default_priority == NotificationPriority.INFO
    
    def test_send_notification(self):
        """Test sending notification"""
        import asyncio
        from src.notifications.notification_router import NotificationRouter, NotificationType
        
        router = NotificationRouter()
        notification = asyncio.get_event_loop().run_until_complete(
            router.send(
                NotificationType.ENTRY_V3_DUAL,
                {"symbol": "EURUSD", "direction": "BUY", "entry_price": 1.1000}
            )
        )
        
        assert notification is not None
        assert notification.notification_type == NotificationType.ENTRY_V3_DUAL
        assert notification.delivered is True
    
    def test_send_emergency_notification(self):
        """Test sending emergency notification"""
        import asyncio
        from src.notifications.notification_router import NotificationRouter
        
        router = NotificationRouter()
        notification = asyncio.get_event_loop().run_until_complete(
            router.send_emergency_notification("Test emergency")
        )
        
        assert notification is not None
        assert notification.delivered is True
    
    def test_voice_text_generation(self):
        """Test voice text generation"""
        from src.notifications.notification_router import NotificationRouter
        
        router = NotificationRouter()
        
        # Test entry voice text
        text = router._generate_voice_text("entry_v3_dual", {
            "direction": "BUY",
            "symbol": "EURUSD",
            "entry_price": 1.1000,
            "signal_type": "STRONG_BUY"
        })
        assert "BUY" in text
        assert "EURUSD" in text
    
    def test_stats_summary(self):
        """Test statistics summary"""
        from src.notifications.notification_router import NotificationRouter
        
        router = NotificationRouter()
        stats = router.get_stats_summary()
        
        assert "total_sent" in stats
        assert "by_type" in stats
        assert "by_priority" in stats


# =============================================================================
# TEST: Notification Formatter Imports
# =============================================================================

class TestNotificationFormatterImports:
    """Test NotificationFormatter imports"""
    
    def test_import_format_type(self):
        """Test FormatType import"""
        from src.notifications.notification_formatter import FormatType
        assert FormatType is not None
        assert hasattr(FormatType, 'PLAIN')
        assert hasattr(FormatType, 'HTML')
        assert hasattr(FormatType, 'MARKDOWN')
    
    def test_import_template_type(self):
        """Test TemplateType import"""
        from src.notifications.notification_formatter import TemplateType
        assert TemplateType is not None
        assert hasattr(TemplateType, 'ENTRY_V3_DUAL')
        assert hasattr(TemplateType, 'EXIT_PROFIT')
    
    def test_import_notification_template(self):
        """Test NotificationTemplate import"""
        from src.notifications.notification_formatter import NotificationTemplate
        assert NotificationTemplate is not None
    
    def test_import_template_manager(self):
        """Test TemplateManager import"""
        from src.notifications.notification_formatter import TemplateManager
        assert TemplateManager is not None
    
    def test_import_notification_formatter(self):
        """Test NotificationFormatter import"""
        from src.notifications.notification_formatter import NotificationFormatter
        assert NotificationFormatter is not None


# =============================================================================
# TEST: Notification Formatter Functionality
# =============================================================================

class TestNotificationFormatter:
    """Test NotificationFormatter functionality"""
    
    def test_template_manager_creation(self):
        """Test template manager creation"""
        from src.notifications.notification_formatter import TemplateManager
        
        manager = TemplateManager()
        assert manager is not None
        assert len(manager.templates) > 0
    
    def test_default_templates_loaded(self):
        """Test default templates are loaded"""
        from src.notifications.notification_formatter import TemplateManager
        
        manager = TemplateManager()
        templates = manager.list_templates()
        
        assert "entry_v3_dual" in templates
        assert "exit_profit" in templates
        assert "daily_summary" in templates
        assert "emergency_stop" in templates
    
    def test_formatter_creation(self):
        """Test formatter creation"""
        from src.notifications.notification_formatter import NotificationFormatter
        
        formatter = NotificationFormatter()
        assert formatter is not None
    
    def test_format_entry_v3_dual(self):
        """Test formatting V3 dual entry"""
        from src.notifications.notification_formatter import NotificationFormatter
        
        formatter = NotificationFormatter()
        result = formatter.format("entry_v3_dual", {
            "plugin_name": "Combined_V3",
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry_price": 1.1000,
            "signal_type": "STRONG_BUY"
        })
        
        assert "ENTRY" in result
        assert "EURUSD" in result
        assert "BUY" in result
    
    def test_format_exit_profit(self):
        """Test formatting exit profit"""
        from src.notifications.notification_formatter import NotificationFormatter
        
        formatter = NotificationFormatter()
        result = formatter.format("exit_profit", {
            "plugin_name": "Combined_V3",
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry_price": 1.1000,
            "exit_price": 1.1050,
            "profit": 50.0
        })
        
        assert "EXIT" in result
        assert "50.00" in result
    
    def test_format_daily_summary(self):
        """Test formatting daily summary"""
        from src.notifications.notification_formatter import NotificationFormatter
        
        formatter = NotificationFormatter()
        result = formatter.format("daily_summary", {
            "date": "2026-01-12",
            "total_trades": 10,
            "winners": 7,
            "losers": 3,
            "win_rate": 70.0,
            "gross_profit": 500.0,
            "gross_loss": 150.0,
            "net_pnl": 350.0
        })
        
        assert "DAILY SUMMARY" in result
        assert "10" in result
    
    def test_template_validation(self):
        """Test template validation"""
        from src.notifications.notification_formatter import TemplateManager
        
        manager = TemplateManager()
        template = manager.get_template("entry_v3_dual")
        
        assert template is not None
        assert template.validate_data({
            "plugin_name": "Test",
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry_price": 1.1000,
            "signal_type": "BUY"
        }) is True


# =============================================================================
# TEST: Delivery Manager Imports
# =============================================================================

class TestDeliveryManagerImports:
    """Test DeliveryManager imports"""
    
    def test_import_delivery_status(self):
        """Test DeliveryStatus import"""
        from src.notifications.delivery_manager import DeliveryStatus
        assert DeliveryStatus is not None
        assert hasattr(DeliveryStatus, 'PENDING')
        assert hasattr(DeliveryStatus, 'DELIVERED')
        assert hasattr(DeliveryStatus, 'FAILED')
    
    def test_import_delivery_priority(self):
        """Test DeliveryPriority import"""
        from src.notifications.delivery_manager import DeliveryPriority
        assert DeliveryPriority is not None
        assert hasattr(DeliveryPriority, 'CRITICAL')
        assert hasattr(DeliveryPriority, 'NORMAL')
    
    def test_import_delivery_result(self):
        """Test DeliveryResult import"""
        from src.notifications.delivery_manager import DeliveryResult
        assert DeliveryResult is not None
    
    def test_import_rate_limiter(self):
        """Test RateLimiter import"""
        from src.notifications.delivery_manager import RateLimiter
        assert RateLimiter is not None
    
    def test_import_delivery_manager(self):
        """Test DeliveryManager import"""
        from src.notifications.delivery_manager import DeliveryManager
        assert DeliveryManager is not None
    
    def test_import_notification_queue_manager(self):
        """Test NotificationQueueManager import"""
        from src.notifications.delivery_manager import NotificationQueueManager
        assert NotificationQueueManager is not None


# =============================================================================
# TEST: Delivery Manager Functionality
# =============================================================================

class TestDeliveryManager:
    """Test DeliveryManager functionality"""
    
    def test_rate_limiter_creation(self):
        """Test rate limiter creation"""
        from src.notifications.delivery_manager import RateLimiter
        
        limiter = RateLimiter(max_per_second=30, max_per_minute=20)
        assert limiter is not None
        assert limiter.max_per_second == 30
        assert limiter.max_per_minute == 20
    
    def test_rate_limiter_acquire(self):
        """Test rate limiter acquire"""
        import asyncio
        from src.notifications.delivery_manager import RateLimiter
        
        limiter = RateLimiter()
        result = asyncio.get_event_loop().run_until_complete(limiter.acquire())
        assert result is True
    
    def test_retry_policy(self):
        """Test retry policy"""
        from src.notifications.delivery_manager import RetryPolicy
        
        policy = RetryPolicy(max_attempts=3, base_delay=1.0)
        
        assert policy.should_retry(1) is True
        assert policy.should_retry(3) is False
        assert policy.get_delay(1) > 0
    
    def test_queue_manager_creation(self):
        """Test queue manager creation"""
        from src.notifications.delivery_manager import NotificationQueueManager
        
        manager = NotificationQueueManager(max_per_minute=20)
        assert manager is not None
        assert manager.max_per_minute == 20
    
    def test_queue_add_message(self):
        """Test adding message to queue"""
        import asyncio
        from src.notifications.delivery_manager import NotificationQueueManager, DeliveryPriority
        
        manager = NotificationQueueManager()
        result = asyncio.get_event_loop().run_until_complete(
            manager.add_message(
                notification_id="TEST-001",
                message="Test message",
                target_bot="notification",
                priority=DeliveryPriority.NORMAL
            )
        )
        
        assert result is True
        assert manager.get_queue_size() == 1
    
    def test_delivery_manager_creation(self):
        """Test delivery manager creation"""
        from src.notifications.delivery_manager import DeliveryManager
        
        manager = DeliveryManager()
        assert manager is not None
    
    def test_delivery_manager_stats(self):
        """Test delivery manager stats"""
        from src.notifications.delivery_manager import DeliveryManager
        
        manager = DeliveryManager()
        stats = manager.get_stats()
        
        assert "total_deliveries" in stats
        assert "queue_stats" in stats


# =============================================================================
# TEST: User Preferences Imports
# =============================================================================

class TestUserPreferencesImports:
    """Test UserPreferences imports"""
    
    def test_import_notification_preference(self):
        """Test NotificationPreference import"""
        from src.notifications.user_preferences import NotificationPreference
        assert NotificationPreference is not None
        assert hasattr(NotificationPreference, 'ALL')
        assert hasattr(NotificationPreference, 'NONE')
    
    def test_import_pnl_display_mode(self):
        """Test PnLDisplayMode import"""
        from src.notifications.user_preferences import PnLDisplayMode
        assert PnLDisplayMode is not None
        assert hasattr(PnLDisplayMode, 'FULL')
        assert hasattr(PnLDisplayMode, 'HIDDEN')
    
    def test_import_voice_preference(self):
        """Test VoicePreference import"""
        from src.notifications.user_preferences import VoicePreference
        assert VoicePreference is not None
    
    def test_import_user_notification_settings(self):
        """Test UserNotificationSettings import"""
        from src.notifications.user_preferences import UserNotificationSettings
        assert UserNotificationSettings is not None
    
    def test_import_preferences_manager(self):
        """Test PreferencesManager import"""
        from src.notifications.user_preferences import PreferencesManager
        assert PreferencesManager is not None


# =============================================================================
# TEST: User Preferences Functionality
# =============================================================================

class TestUserPreferences:
    """Test UserPreferences functionality"""
    
    def test_quiet_hours_creation(self):
        """Test quiet hours creation"""
        from src.notifications.user_preferences import QuietHours
        
        quiet = QuietHours(enabled=True, start_time=time(22, 0), end_time=time(7, 0))
        assert quiet is not None
        assert quiet.enabled is True
    
    def test_notification_filter(self):
        """Test notification filter"""
        from src.notifications.user_preferences import NotificationFilter
        
        filter_obj = NotificationFilter(min_priority=3)
        
        assert filter_obj.should_notify("entry", 4) is True
        assert filter_obj.should_notify("entry", 2) is False
    
    def test_user_settings_creation(self):
        """Test user settings creation"""
        from src.notifications.user_preferences import UserNotificationSettings
        
        settings = UserNotificationSettings(user_id=12345)
        assert settings is not None
        assert settings.user_id == 12345
    
    def test_user_settings_should_notify(self):
        """Test should_notify logic"""
        from src.notifications.user_preferences import UserNotificationSettings, NotificationPreference
        
        settings = UserNotificationSettings(user_id=12345)
        assert settings.should_notify("entry", 4) is True
        
        settings.preference = NotificationPreference.NONE
        assert settings.should_notify("entry", 4) is False
    
    def test_mute_type(self):
        """Test muting notification type"""
        from src.notifications.user_preferences import UserNotificationSettings
        
        settings = UserNotificationSettings(user_id=12345)
        settings.mute_type("daily_summary")
        
        assert settings.should_notify("daily_summary", 2) is False
        assert settings.should_notify("entry", 4) is True
    
    def test_preferences_manager_creation(self):
        """Test preferences manager creation"""
        from src.notifications.user_preferences import PreferencesManager
        
        manager = PreferencesManager()
        assert manager is not None
    
    def test_preferences_manager_get_preferences(self):
        """Test getting user preferences"""
        from src.notifications.user_preferences import PreferencesManager
        
        manager = PreferencesManager()
        prefs = manager.get_preferences(12345)
        
        assert prefs is not None
        assert prefs.user_id == 12345
    
    def test_pnl_format(self):
        """Test P&L formatting"""
        from src.notifications.user_preferences import UserNotificationSettings, PnLDisplayMode
        
        settings = UserNotificationSettings(user_id=12345)
        
        # Full mode
        result = settings.format_pnl(100.0, 5.0)
        assert "100.00" in result
        
        # Hidden mode
        settings.pnl_display = PnLDisplayMode.HIDDEN
        result = settings.format_pnl(100.0)
        assert "Hidden" in result


# =============================================================================
# TEST: Alert Router Imports
# =============================================================================

class TestAlertRouterImports:
    """Test AlertRouter imports"""
    
    def test_import_alert_type(self):
        """Test AlertType import"""
        from src.notifications.alert_router import AlertType
        assert AlertType is not None
        assert hasattr(AlertType, 'ENTRY')
        assert hasattr(AlertType, 'EXIT')
        assert hasattr(AlertType, 'EMERGENCY')
    
    def test_import_target_type(self):
        """Test TargetType import"""
        from src.notifications.alert_router import TargetType
        assert TargetType is not None
        assert hasattr(TargetType, 'BOT')
        assert hasattr(TargetType, 'BROADCAST')
    
    def test_import_routing_rule(self):
        """Test RoutingRule import"""
        from src.notifications.alert_router import RoutingRule
        assert RoutingRule is not None
    
    def test_import_alert_router(self):
        """Test AlertRouter import"""
        from src.notifications.alert_router import AlertRouter
        assert AlertRouter is not None


# =============================================================================
# TEST: Alert Router Functionality
# =============================================================================

class TestAlertRouter:
    """Test AlertRouter functionality"""
    
    def test_router_creation(self):
        """Test router creation"""
        from src.notifications.alert_router import AlertRouter
        
        router = AlertRouter()
        assert router is not None
        assert len(router.rules) > 0  # Default rules loaded
    
    def test_default_rules_loaded(self):
        """Test default rules are loaded"""
        from src.notifications.alert_router import AlertRouter
        
        router = AlertRouter()
        rules = router.list_rules()
        
        assert len(rules) >= 5  # At least 5 default rules
    
    def test_route_emergency(self):
        """Test routing emergency alert"""
        from src.notifications.alert_router import AlertRouter, AlertType
        
        router = AlertRouter()
        result = router.route(AlertType.EMERGENCY, {})
        
        assert result.routed is True
        assert len(result.targets) > 0
    
    def test_route_entry(self):
        """Test routing entry alert"""
        from src.notifications.alert_router import AlertRouter, AlertType
        
        router = AlertRouter()
        result = router.route(AlertType.ENTRY, {"symbol": "EURUSD"})
        
        assert result.routed is True
    
    def test_create_symbol_rule(self):
        """Test creating symbol-specific rule"""
        from src.notifications.alert_router import AlertRouter
        
        router = AlertRouter()
        rule_id = router.create_symbol_rule("XAUUSD", "analytics")
        
        assert rule_id is not None
        assert router.get_rule(rule_id) is not None
    
    def test_routing_condition(self):
        """Test routing condition evaluation"""
        from src.notifications.alert_router import RoutingCondition
        
        condition = RoutingCondition("symbol", "eq", "EURUSD")
        
        assert condition.evaluate({"symbol": "EURUSD"}) is True
        assert condition.evaluate({"symbol": "GBPUSD"}) is False
    
    def test_enable_disable_rule(self):
        """Test enabling/disabling rules"""
        from src.notifications.alert_router import AlertRouter
        
        router = AlertRouter()
        rule_id = list(router.rules.keys())[0]
        
        router.disable_rule(rule_id)
        assert router.rules[rule_id].enabled is False
        
        router.enable_rule(rule_id)
        assert router.rules[rule_id].enabled is True


# =============================================================================
# TEST: Voice Alerts Imports
# =============================================================================

class TestVoiceAlertsImports:
    """Test VoiceAlerts imports"""
    
    def test_import_voice_language(self):
        """Test VoiceLanguage import"""
        from src.notifications.voice_alerts import VoiceLanguage
        assert VoiceLanguage is not None
        assert hasattr(VoiceLanguage, 'ENGLISH')
        assert hasattr(VoiceLanguage, 'HINDI')
    
    def test_import_voice_speed(self):
        """Test VoiceSpeed import"""
        from src.notifications.voice_alerts import VoiceSpeed
        assert VoiceSpeed is not None
        assert hasattr(VoiceSpeed, 'NORMAL')
    
    def test_import_voice_alert_config(self):
        """Test VoiceAlertConfig import"""
        from src.notifications.voice_alerts import VoiceAlertConfig
        assert VoiceAlertConfig is not None
    
    def test_import_voice_alert_system(self):
        """Test VoiceAlertSystem import"""
        from src.notifications.voice_alerts import VoiceAlertSystem
        assert VoiceAlertSystem is not None


# =============================================================================
# TEST: Voice Alerts Functionality
# =============================================================================

class TestVoiceAlerts:
    """Test VoiceAlerts functionality"""
    
    def test_config_creation(self):
        """Test voice config creation"""
        from src.notifications.voice_alerts import VoiceAlertConfig
        
        config = VoiceAlertConfig()
        assert config is not None
        assert config.enabled is True
        assert config.volume == 100
    
    def test_trigger_enabled(self):
        """Test trigger enabled check"""
        from src.notifications.voice_alerts import VoiceAlertConfig, VoiceTrigger
        
        config = VoiceAlertConfig()
        
        assert config.is_trigger_enabled(VoiceTrigger.ENTRY) is True
        assert config.is_trigger_enabled(VoiceTrigger.DAILY_SUMMARY) is False
    
    def test_voice_system_creation(self):
        """Test voice system creation"""
        from src.notifications.voice_alerts import VoiceAlertSystem
        
        system = VoiceAlertSystem()
        assert system is not None
    
    def test_should_alert(self):
        """Test should_alert logic"""
        from src.notifications.voice_alerts import VoiceAlertSystem
        
        system = VoiceAlertSystem()
        
        assert system.should_alert("entry_v3_dual") is True
        assert system.should_alert("unknown_type") is False
    
    def test_generate_alert(self):
        """Test generating voice alert"""
        from src.notifications.voice_alerts import VoiceAlertSystem, VoiceTrigger
        
        system = VoiceAlertSystem()
        alert = system.generate_alert("entry_v3_dual", {
            "direction": "BUY",
            "symbol": "EURUSD",
            "entry_price": 1.1000,
            "signal_type": "STRONG_BUY"
        })
        
        assert alert is not None
        assert alert.trigger == VoiceTrigger.ENTRY
        assert len(alert.text) > 0
    
    def test_voice_text_generator(self):
        """Test voice text generator"""
        from src.notifications.voice_alerts import VoiceTextGenerator, VoiceLanguage
        
        generator = VoiceTextGenerator(VoiceLanguage.ENGLISH)
        text = generator.generate("entry", {
            "direction": "BUY",
            "symbol": "EURUSD",
            "entry_price": 1.1000,
            "signal_type": "BUY"
        })
        
        assert "BUY" in text
        assert "EURUSD" in text
    
    def test_enable_disable(self):
        """Test enable/disable voice alerts"""
        from src.notifications.voice_alerts import VoiceAlertSystem
        
        system = VoiceAlertSystem()
        
        system.disable()
        assert system.config.enabled is False
        
        system.enable()
        assert system.config.enabled is True


# =============================================================================
# TEST: Notification Stats Imports
# =============================================================================

class TestNotificationStatsImports:
    """Test NotificationStats imports"""
    
    def test_import_notification_metric(self):
        """Test NotificationMetric import"""
        from src.notifications.notification_stats import NotificationMetric
        assert NotificationMetric is not None
    
    def test_import_hourly_stats(self):
        """Test HourlyStats import"""
        from src.notifications.notification_stats import HourlyStats
        assert HourlyStats is not None
    
    def test_import_daily_stats(self):
        """Test DailyStats import"""
        from src.notifications.notification_stats import DailyStats
        assert DailyStats is not None
    
    def test_import_notification_stats(self):
        """Test NotificationStats import"""
        from src.notifications.notification_stats import NotificationStats
        assert NotificationStats is not None
    
    def test_import_stats_aggregator(self):
        """Test StatsAggregator import"""
        from src.notifications.notification_stats import StatsAggregator
        assert StatsAggregator is not None


# =============================================================================
# TEST: Notification Stats Functionality
# =============================================================================

class TestNotificationStats:
    """Test NotificationStats functionality"""
    
    def test_stats_creation(self):
        """Test stats creation"""
        from src.notifications.notification_stats import NotificationStats
        
        stats = NotificationStats()
        assert stats is not None
        assert stats.total_sent == 0
    
    def test_record_notification(self):
        """Test recording notification"""
        from src.notifications.notification_stats import NotificationStats
        
        stats = NotificationStats()
        stats.record(
            notification_type="entry_v3_dual",
            priority="HIGH",
            target_bot="notification",
            success=True
        )
        
        assert stats.total_sent == 1
        assert stats.total_successful == 1
    
    def test_record_failed_notification(self):
        """Test recording failed notification"""
        from src.notifications.notification_stats import NotificationStats
        
        stats = NotificationStats()
        stats.record(
            notification_type="entry_v3_dual",
            priority="HIGH",
            target_bot="notification",
            success=False
        )
        
        assert stats.total_sent == 1
        assert stats.total_failed == 1
    
    def test_get_summary(self):
        """Test getting summary"""
        from src.notifications.notification_stats import NotificationStats
        
        stats = NotificationStats()
        stats.record("entry", "HIGH", "notification", True)
        stats.record("exit", "HIGH", "notification", True)
        stats.record("error", "HIGH", "notification", False)
        
        summary = stats.get_summary()
        
        assert summary["total_sent"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
    
    def test_stats_aggregator_creation(self):
        """Test stats aggregator creation"""
        from src.notifications.notification_stats import StatsAggregator
        
        aggregator = StatsAggregator()
        assert aggregator is not None
    
    def test_aggregator_record(self):
        """Test aggregator recording"""
        from src.notifications.notification_stats import StatsAggregator
        
        aggregator = StatsAggregator()
        aggregator.record_notification("entry", "HIGH", "notification", True)
        
        summary = aggregator.notification_stats.get_summary()
        assert summary["total_sent"] == 1
    
    def test_dashboard_data(self):
        """Test getting dashboard data"""
        from src.notifications.notification_stats import StatsAggregator
        
        aggregator = StatsAggregator()
        aggregator.record_notification("entry", "HIGH", "notification", True)
        
        data = aggregator.get_dashboard_data()
        
        assert "summary" in data
        assert "hourly_chart" in data
        assert "last_updated" in data


# =============================================================================
# TEST: Document 19 Integration
# =============================================================================

class TestDocument19Integration:
    """Test Document 19 integration"""
    
    def test_all_modules_importable(self):
        """Test all modules can be imported"""
        from src.notifications import notification_router
        from src.notifications import notification_formatter
        from src.notifications import delivery_manager
        from src.notifications import user_preferences
        from src.notifications import alert_router
        from src.notifications import voice_alerts
        from src.notifications import notification_stats
        
        assert notification_router is not None
        assert notification_formatter is not None
        assert delivery_manager is not None
        assert user_preferences is not None
        assert alert_router is not None
        assert voice_alerts is not None
        assert notification_stats is not None
    
    def test_priority_based_routing(self):
        """Test priority-based routing works"""
        from src.notifications.notification_router import NotificationRouter, NotificationType, NotificationPriority
        
        router = NotificationRouter()
        
        # Critical should broadcast
        assert NotificationPriority.CRITICAL.target_bot == "broadcast"
        
        # High should go to notification
        assert NotificationPriority.HIGH.target_bot == "notification"
        
        # Low should go to analytics
        assert NotificationPriority.LOW.target_bot == "analytics"
    
    def test_template_system(self):
        """Test template system works"""
        from src.notifications.notification_formatter import NotificationFormatter, TemplateManager
        
        manager = TemplateManager()
        formatter = NotificationFormatter(manager)
        
        # Should have all required templates
        templates = manager.list_templates()
        required = ["entry_v3_dual", "exit_profit", "exit_loss", "daily_summary", "emergency_stop"]
        
        for req in required:
            assert req in templates, f"Missing template: {req}"
    
    def test_user_preferences_integration(self):
        """Test user preferences integration"""
        from src.notifications.user_preferences import PreferencesManager, NotificationPreference
        
        manager = PreferencesManager()
        
        # Create user with custom preferences
        prefs = manager.get_preferences(12345)
        manager.update_preference(12345, NotificationPreference.IMPORTANT_ONLY)
        
        # Should filter low priority
        assert manager.should_notify(12345, "entry", 4) is True
        assert manager.should_notify(12345, "info", 1) is False


# =============================================================================
# TEST: Document 19 Summary
# =============================================================================

class TestDocument19Summary:
    """Test Document 19 requirements summary"""
    
    def test_notification_router_complete(self):
        """Test NotificationRouter is complete"""
        from src.notifications.notification_router import (
            NotificationPriority, NotificationType, Notification,
            NotificationRouter, MockTelegramManager
        )
        
        # All priority levels
        assert len(NotificationPriority) == 5
        
        # All notification types
        assert len(NotificationType) >= 25
        
        # Router has required methods
        router = NotificationRouter()
        assert hasattr(router, 'send')
        assert hasattr(router, 'format_notification')
        assert hasattr(router, 'get_stats_summary')
    
    def test_notification_formatter_complete(self):
        """Test NotificationFormatter is complete"""
        from src.notifications.notification_formatter import (
            FormatType, TemplateType, NotificationTemplate,
            TemplateManager, NotificationFormatter
        )
        
        # Format types
        assert len(FormatType) == 3
        
        # Template types
        assert len(TemplateType) >= 20
        
        # Manager has templates
        manager = TemplateManager()
        assert len(manager.templates) >= 20
    
    def test_delivery_manager_complete(self):
        """Test DeliveryManager is complete"""
        from src.notifications.delivery_manager import (
            DeliveryStatus, DeliveryPriority, DeliveryResult,
            RateLimiter, RetryPolicy, NotificationQueueManager,
            DeliveryManager
        )
        
        # Delivery statuses
        assert len(DeliveryStatus) >= 6
        
        # Delivery priorities
        assert len(DeliveryPriority) == 5
        
        # Manager has required methods
        manager = DeliveryManager()
        assert hasattr(manager, 'deliver')
        assert hasattr(manager, 'get_stats')
    
    def test_user_preferences_complete(self):
        """Test UserPreferences is complete"""
        from src.notifications.user_preferences import (
            NotificationPreference, PnLDisplayMode, VoicePreference,
            GroupingMode, QuietHours, NotificationFilter,
            UserNotificationSettings, PreferencesManager
        )
        
        # Preference options
        assert len(NotificationPreference) >= 4
        assert len(PnLDisplayMode) >= 4
        assert len(VoicePreference) >= 4
        
        # Settings has required methods
        settings = UserNotificationSettings(user_id=1)
        assert hasattr(settings, 'should_notify')
        assert hasattr(settings, 'should_voice_alert')
        assert hasattr(settings, 'format_pnl')
    
    def test_alert_router_complete(self):
        """Test AlertRouter is complete"""
        from src.notifications.alert_router import (
            AlertType, TargetType, RouteTarget, RoutingCondition,
            RoutingRule, RoutingResult, AlertRouter
        )
        
        # Alert types
        assert len(AlertType) >= 15
        
        # Target types
        assert len(TargetType) >= 5
        
        # Router has required methods
        router = AlertRouter()
        assert hasattr(router, 'route')
        assert hasattr(router, 'add_rule')
        assert hasattr(router, 'create_symbol_rule')
    
    def test_voice_alerts_complete(self):
        """Test VoiceAlerts is complete"""
        from src.notifications.voice_alerts import (
            VoiceLanguage, VoiceSpeed, VoiceTrigger,
            VoiceAlertConfig, VoiceAlert, VoiceTextGenerator,
            VoiceAlertSystem
        )
        
        # Languages
        assert len(VoiceLanguage) >= 5
        
        # Triggers
        assert len(VoiceTrigger) >= 8
        
        # System has required methods
        system = VoiceAlertSystem()
        assert hasattr(system, 'should_alert')
        assert hasattr(system, 'generate_alert')
        assert hasattr(system, 'send_alert')
    
    def test_notification_stats_complete(self):
        """Test NotificationStats is complete"""
        from src.notifications.notification_stats import (
            NotificationMetric, HourlyStats, DailyStats,
            NotificationStats, StatsAggregator
        )
        
        # Stats has required methods
        stats = NotificationStats()
        assert hasattr(stats, 'record')
        assert hasattr(stats, 'get_summary')
        assert hasattr(stats, 'get_hourly_breakdown')
        assert hasattr(stats, 'get_daily_breakdown')
        
        # Aggregator has required methods
        aggregator = StatsAggregator()
        assert hasattr(aggregator, 'record_notification')
        assert hasattr(aggregator, 'get_dashboard_data')
    
    def test_document_19_requirements_met(self):
        """Test all Document 19 requirements are met"""
        # 1. NotificationRouter implemented
        from src.notifications.notification_router import NotificationRouter
        assert NotificationRouter is not None
        
        # 2. All event types mapped (NotificationType enum)
        from src.notifications.notification_router import NotificationType
        assert len(NotificationType) >= 25
        
        # 3. All formatters created (TemplateManager)
        from src.notifications.notification_formatter import TemplateManager
        manager = TemplateManager()
        assert len(manager.templates) >= 20
        
        # 4. Voice alert system working
        from src.notifications.voice_alerts import VoiceAlertSystem
        system = VoiceAlertSystem()
        assert system.should_alert("entry_v3_dual") is True
        
        # 5. Queue system implemented
        from src.notifications.delivery_manager import NotificationQueueManager
        queue = NotificationQueueManager()
        assert queue is not None
        
        # 6. Rate limiting configured
        from src.notifications.delivery_manager import RateLimiter
        limiter = RateLimiter()
        assert limiter.max_per_minute == 20
        
        # 7. Statistics tracking active
        from src.notifications.notification_stats import NotificationStats
        stats = NotificationStats()
        stats.record("test", "HIGH", "notification", True)
        assert stats.total_sent == 1
        
        # 8. User preferences implemented
        from src.notifications.user_preferences import PreferencesManager
        prefs = PreferencesManager()
        assert prefs is not None


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
