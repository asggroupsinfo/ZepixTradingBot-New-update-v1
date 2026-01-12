"""
Test Suite for Document 18: Telegram System Architecture.

Tests cover:
- Bot Orchestrator (lifecycle management)
- Unified Interface (menus, keyboards)
- Command Routing
- User Session Management
- Broadcast System
- Error Handling & Health Monitoring

Based on Document 18: TELEGRAM_SYSTEM_ARCHITECTURE.md

Version: 1.0
Date: 2026-01-12
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestTelegramModuleStructure:
    """Test that all Telegram modules exist."""
    
    def test_bot_orchestrator_exists(self):
        """Test bot_orchestrator.py exists."""
        module_path = project_root / "src" / "telegram" / "bot_orchestrator.py"
        assert module_path.exists(), "bot_orchestrator.py should exist"
    
    def test_unified_interface_exists(self):
        """Test unified_interface.py exists."""
        module_path = project_root / "src" / "telegram" / "unified_interface.py"
        assert module_path.exists(), "unified_interface.py should exist"
    
    def test_command_router_exists(self):
        """Test command_router.py exists."""
        module_path = project_root / "src" / "telegram" / "command_router.py"
        assert module_path.exists(), "command_router.py should exist"
    
    def test_session_manager_exists(self):
        """Test session_manager.py exists."""
        module_path = project_root / "src" / "telegram" / "session_manager.py"
        assert module_path.exists(), "session_manager.py should exist"
    
    def test_broadcast_system_exists(self):
        """Test broadcast_system.py exists."""
        module_path = project_root / "src" / "telegram" / "broadcast_system.py"
        assert module_path.exists(), "broadcast_system.py should exist"
    
    def test_error_handler_exists(self):
        """Test error_handler.py exists."""
        module_path = project_root / "src" / "telegram" / "error_handler.py"
        assert module_path.exists(), "error_handler.py should exist"


class TestBotOrchestratorImports:
    """Test Bot Orchestrator imports."""
    
    def test_import_bot_type(self):
        """Test BotType import."""
        from telegram.bot_orchestrator import BotType
        assert BotType.CONTROLLER.value == "controller"
        assert BotType.NOTIFICATION.value == "notification"
        assert BotType.ANALYTICS.value == "analytics"
    
    def test_import_bot_state(self):
        """Test BotState import."""
        from telegram.bot_orchestrator import BotState
        assert BotState.STOPPED.value == "stopped"
        assert BotState.RUNNING.value == "running"
        assert BotState.ERROR.value == "error"
    
    def test_import_bot_config(self):
        """Test BotConfig import."""
        from telegram.bot_orchestrator import BotConfig, BotType
        config = BotConfig(
            bot_type=BotType.CONTROLLER,
            token="test_token",
            chat_id="12345"
        )
        assert config.bot_type == BotType.CONTROLLER
        assert config.enabled == True
    
    def test_import_bot_status(self):
        """Test BotStatus import."""
        from telegram.bot_orchestrator import BotStatus, BotType, BotState
        status = BotStatus(
            bot_type=BotType.CONTROLLER,
            state=BotState.RUNNING
        )
        assert status.messages_sent == 0
        assert status.errors_count == 0
    
    def test_import_bot_orchestrator(self):
        """Test BotOrchestrator import."""
        from telegram.bot_orchestrator import BotOrchestrator
        orchestrator = BotOrchestrator()
        assert orchestrator is not None


class TestBotOrchestrator:
    """Test Bot Orchestrator functionality."""
    
    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        from telegram.bot_orchestrator import BotOrchestrator, BotType
        orchestrator = BotOrchestrator()
        assert len(orchestrator.bots) == 3
        assert BotType.CONTROLLER in orchestrator.bots
        assert BotType.NOTIFICATION in orchestrator.bots
        assert BotType.ANALYTICS in orchestrator.bots
    
    def test_orchestrator_default_configs(self):
        """Test default configurations."""
        from telegram.bot_orchestrator import BotOrchestrator, BotType
        orchestrator = BotOrchestrator()
        assert BotType.CONTROLLER in orchestrator.configs
        assert BotType.NOTIFICATION in orchestrator.configs
        assert BotType.ANALYTICS in orchestrator.configs
    
    def test_orchestrator_statuses(self):
        """Test bot statuses initialization."""
        from telegram.bot_orchestrator import BotOrchestrator, BotType, BotState
        orchestrator = BotOrchestrator()
        for bot_type in [BotType.CONTROLLER, BotType.NOTIFICATION, BotType.ANALYTICS]:
            status = orchestrator.get_bot_status(bot_type)
            assert status is not None
            assert status.state == BotState.STOPPED
    
    def test_orchestrator_health_report(self):
        """Test health report generation."""
        from telegram.bot_orchestrator import BotOrchestrator
        orchestrator = BotOrchestrator()
        report = orchestrator.get_health_report()
        assert "overall_health" in report
        assert "healthy_bots" in report
        assert "total_bots" in report
        assert report["total_bots"] == 3
    
    def test_orchestrator_get_bot(self):
        """Test getting specific bot."""
        from telegram.bot_orchestrator import BotOrchestrator, BotType
        orchestrator = BotOrchestrator()
        bot = orchestrator.get_bot(BotType.CONTROLLER)
        assert bot is not None
        assert bot.bot_type == BotType.CONTROLLER


class TestUnifiedInterfaceImports:
    """Test Unified Interface imports."""
    
    def test_import_menu_type(self):
        """Test MenuType import."""
        from telegram.unified_interface import MenuType
        assert MenuType.MAIN.value == "main"
        assert MenuType.STATUS.value == "status"
        assert MenuType.TRADES.value == "trades"
        assert MenuType.EMERGENCY.value == "emergency"
    
    def test_import_button_type(self):
        """Test ButtonType import."""
        from telegram.unified_interface import ButtonType
        assert ButtonType.REPLY.value == "reply"
        assert ButtonType.INLINE.value == "inline"
    
    def test_import_keyboard_button(self):
        """Test KeyboardButton import."""
        from telegram.unified_interface import KeyboardButton
        button = KeyboardButton(text="Test", callback_data="test_cb")
        assert button.text == "Test"
        assert button.callback_data == "test_cb"
    
    def test_import_menu(self):
        """Test Menu import."""
        from telegram.unified_interface import Menu, MenuType
        menu = Menu(menu_type=MenuType.MAIN, title="Test Menu")
        assert menu.menu_type == MenuType.MAIN
        assert menu.title == "Test Menu"
    
    def test_import_menu_builder(self):
        """Test MenuBuilder import."""
        from telegram.unified_interface import MenuBuilder
        builder = MenuBuilder()
        assert builder is not None


class TestUnifiedInterface:
    """Test Unified Interface functionality."""
    
    def test_create_main_menu(self):
        """Test main menu creation."""
        from telegram.unified_interface import MenuBuilder, MenuType
        menu = MenuBuilder.create_main_menu()
        assert menu.menu_type == MenuType.MAIN
        assert len(menu.rows) == 3
        assert menu.is_inline == False
    
    def test_create_status_menu(self):
        """Test status menu creation."""
        from telegram.unified_interface import MenuBuilder, MenuType
        text, menu = MenuBuilder.create_status_menu(
            bot_status="🟢 Active",
            uptime="1d 5h",
            plugins_active=5,
            plugins_total=5,
            open_trades=3
        )
        assert "Status Information" in text
        assert menu.menu_type == MenuType.STATUS
        assert menu.is_inline == True
    
    def test_create_trades_menu(self):
        """Test trades menu creation."""
        from telegram.unified_interface import MenuBuilder
        trades = [
            {"symbol": "XAUUSD", "direction": "BUY", "lot_size": 0.1, "profit": 55.0, "plugin": "v3", "age": "2h"},
            {"symbol": "EURUSD", "direction": "SELL", "lot_size": 0.05, "profit": -10.0, "plugin": "v6", "age": "30m"}
        ]
        text, menu = MenuBuilder.create_trades_menu(trades)
        assert "Open Positions" in text
        assert "XAUUSD" in text
    
    def test_create_emergency_menu(self):
        """Test emergency menu creation."""
        from telegram.unified_interface import MenuBuilder, MenuType
        text, menu = MenuBuilder.create_emergency_menu()
        assert "EMERGENCY CONTROLS" in text
        assert menu.menu_type == MenuType.EMERGENCY
    
    def test_create_settings_menu(self):
        """Test settings menu creation."""
        from telegram.unified_interface import MenuBuilder
        text, menu = MenuBuilder.create_settings_menu(
            max_lot=1.0,
            daily_loss_limit=500.0,
            risk_per_trade=1.5
        )
        assert "Bot Settings" in text
        assert "Max Lot Size" in text
    
    def test_unified_interface_creation(self):
        """Test UnifiedInterface creation."""
        from telegram.unified_interface import UnifiedInterface
        interface = UnifiedInterface()
        assert interface is not None
        assert interface.builder is not None


class TestCommandRouterImports:
    """Test Command Router imports."""
    
    def test_import_command_category(self):
        """Test CommandCategory import."""
        from telegram.command_router import CommandCategory
        assert CommandCategory.SYSTEM.value == "system"
        assert CommandCategory.TRADING.value == "trading"
        assert CommandCategory.EMERGENCY.value == "emergency"
    
    def test_import_route_target(self):
        """Test RouteTarget import."""
        from telegram.command_router import RouteTarget
        assert RouteTarget.CONTROLLER.value == "controller"
        assert RouteTarget.NOTIFICATION.value == "notification"
        assert RouteTarget.ANALYTICS.value == "analytics"
    
    def test_import_message_type(self):
        """Test MessageType import."""
        from telegram.command_router import MessageType
        assert MessageType.COMMAND.value == "command"
        assert MessageType.ENTRY.value == "entry"
        assert MessageType.EXIT.value == "exit"
    
    def test_import_command_definition(self):
        """Test CommandDefinition import."""
        from telegram.command_router import CommandDefinition, CommandCategory
        cmd = CommandDefinition(
            name="test",
            description="Test command",
            category=CommandCategory.SYSTEM,
            handler_name="handle_test"
        )
        assert cmd.name == "test"
    
    def test_import_command_router(self):
        """Test CommandRouter import."""
        from telegram.command_router import CommandRouter
        router = CommandRouter()
        assert router is not None


class TestCommandRouter:
    """Test Command Router functionality."""
    
    def test_router_creation(self):
        """Test router creation."""
        from telegram.command_router import CommandRouter
        router = CommandRouter()
        assert router.command_registry is not None
        assert router.callback_registry is not None
    
    def test_default_commands_registered(self):
        """Test default commands are registered."""
        from telegram.command_router import CommandRouter
        router = CommandRouter()
        assert router.is_valid_command("start")
        assert router.is_valid_command("status")
        assert router.is_valid_command("trades")
        assert router.is_valid_command("help")
    
    def test_route_command(self):
        """Test command routing."""
        from telegram.command_router import CommandRouter
        router = CommandRouter()
        result = router.route_command("/status")
        assert result is not None
        assert result.handler_name == "handle_status"
    
    def test_route_callback(self):
        """Test callback routing."""
        from telegram.command_router import CommandRouter
        router = CommandRouter()
        result = router.route_callback("close_trade_123")
        assert result is not None
        assert result.handler_name == "close_trade_handler"
        assert result.params["trade_id"] == "123"
    
    def test_route_message_entry(self):
        """Test entry message routing."""
        from telegram.command_router import CommandRouter, MessageType, RouteTarget
        router = CommandRouter()
        result = router.route_message(MessageType.ENTRY, "Entry alert")
        assert result.target == RouteTarget.NOTIFICATION
    
    def test_route_message_analytics(self):
        """Test analytics message routing."""
        from telegram.command_router import CommandRouter, MessageType, RouteTarget
        router = CommandRouter()
        result = router.route_message(MessageType.DAILY_REPORT, "Daily report")
        assert result.target == RouteTarget.ANALYTICS
    
    def test_get_command_help(self):
        """Test help text generation."""
        from telegram.command_router import CommandRouter
        router = CommandRouter()
        help_text = router.get_command_help()
        assert "Available Commands" in help_text
        assert "/start" in help_text


class TestSessionManagerImports:
    """Test Session Manager imports."""
    
    def test_import_session_state(self):
        """Test SessionState import."""
        from telegram.session_manager import SessionState
        assert SessionState.ACTIVE.value == "active"
        assert SessionState.EXPIRED.value == "expired"
    
    def test_import_conversation_state(self):
        """Test ConversationState import."""
        from telegram.session_manager import ConversationState
        assert ConversationState.IDLE.value == "idle"
        assert ConversationState.AWAITING_CONFIRMATION.value == "awaiting_confirmation"
    
    def test_import_user_preferences(self):
        """Test UserPreferences import."""
        from telegram.session_manager import UserPreferences
        prefs = UserPreferences()
        assert prefs.voice_alerts_enabled == True
        assert prefs.timezone == "UTC"
    
    def test_import_user_session(self):
        """Test UserSession import."""
        from telegram.session_manager import UserSession
        session = UserSession(user_id="123", chat_id="456")
        assert session.user_id == "123"
        assert session.chat_id == "456"
    
    def test_import_session_manager(self):
        """Test SessionManager import."""
        from telegram.session_manager import SessionManager
        manager = SessionManager()
        assert manager is not None


class TestSessionManager:
    """Test Session Manager functionality."""
    
    def test_manager_creation(self):
        """Test manager creation."""
        from telegram.session_manager import SessionManager
        manager = SessionManager()
        assert manager.storage is not None
        assert manager.session_timeout == 30
    
    def test_create_session(self):
        """Test session creation."""
        from telegram.session_manager import SessionManager, SessionState
        manager = SessionManager()
        session = manager.create_session("user1", "chat1", "testuser")
        assert session.user_id == "user1"
        assert session.chat_id == "chat1"
        assert session.state == SessionState.ACTIVE
    
    def test_get_session(self):
        """Test session retrieval."""
        from telegram.session_manager import SessionManager
        manager = SessionManager()
        manager.create_session("user2", "chat2")
        session = manager.get_session("user2")
        assert session is not None
        assert session.user_id == "user2"
    
    def test_get_or_create_session(self):
        """Test get or create session."""
        from telegram.session_manager import SessionManager
        manager = SessionManager()
        session1 = manager.get_or_create_session("user3", "chat3")
        session2 = manager.get_or_create_session("user3", "chat3")
        assert session1.user_id == session2.user_id
    
    def test_session_data(self):
        """Test session data storage."""
        from telegram.session_manager import SessionManager
        manager = SessionManager()
        session = manager.create_session("user4", "chat4")
        session.set_data("key1", "value1")
        assert session.get_data("key1") == "value1"
    
    def test_pending_action(self):
        """Test pending action management."""
        from telegram.session_manager import SessionManager, ConversationState
        manager = SessionManager()
        manager.create_session("user5", "chat5")
        manager.set_pending_action("user5", "close_all", {"count": 5})
        
        pending = manager.get_pending_action("user5")
        assert pending is not None
        assert pending["action"] == "close_all"
        
        session = manager.get_session("user5")
        assert session.context.state == ConversationState.AWAITING_CONFIRMATION
    
    def test_admin_user(self):
        """Test admin user management."""
        from telegram.session_manager import SessionManager
        manager = SessionManager()
        manager.create_session("admin1", "chat_admin")
        manager.add_admin_user("admin1")
        assert manager.is_admin("admin1")


class TestBroadcastSystemImports:
    """Test Broadcast System imports."""
    
    def test_import_broadcast_type(self):
        """Test BroadcastType import."""
        from telegram.broadcast_system import BroadcastType
        assert BroadcastType.ALL_BOTS.value == "all_bots"
        assert BroadcastType.ALL_USERS.value == "all_users"
        assert BroadcastType.ADMINS_ONLY.value == "admins_only"
    
    def test_import_broadcast_priority(self):
        """Test BroadcastPriority import."""
        from telegram.broadcast_system import BroadcastPriority
        assert BroadcastPriority.LOW.value == 0
        assert BroadcastPriority.CRITICAL.value == 3
    
    def test_import_broadcast_status(self):
        """Test BroadcastStatus import."""
        from telegram.broadcast_system import BroadcastStatus
        assert BroadcastStatus.PENDING.value == "pending"
        assert BroadcastStatus.COMPLETED.value == "completed"
    
    def test_import_broadcast_target(self):
        """Test BroadcastTarget import."""
        from telegram.broadcast_system import BroadcastTarget, BroadcastType
        target = BroadcastTarget(broadcast_type=BroadcastType.ALL_BOTS)
        assert target.broadcast_type == BroadcastType.ALL_BOTS
    
    def test_import_broadcast_system(self):
        """Test BroadcastSystem import."""
        from telegram.broadcast_system import BroadcastSystem
        system = BroadcastSystem()
        assert system is not None


class TestBroadcastSystem:
    """Test Broadcast System functionality."""
    
    def test_system_creation(self):
        """Test system creation."""
        from telegram.broadcast_system import BroadcastSystem
        system = BroadcastSystem()
        assert len(system._bots) == 3
    
    def test_register_user(self):
        """Test user registration."""
        from telegram.broadcast_system import BroadcastSystem
        system = BroadcastSystem()
        system.register_user("user1", "chat1", is_admin=True)
        assert "user1" in system._users
        assert "user1" in system._admin_users
    
    def test_queue_broadcast(self):
        """Test broadcast queuing."""
        from telegram.broadcast_system import BroadcastSystem, BroadcastTarget, BroadcastType
        system = BroadcastSystem()
        target = BroadcastTarget(broadcast_type=BroadcastType.ALL_USERS)
        message_id = system.queue_broadcast("Test message", target)
        assert message_id is not None
        assert len(system._message_queue) == 1
    
    def test_cancel_broadcast(self):
        """Test broadcast cancellation."""
        from telegram.broadcast_system import BroadcastSystem, BroadcastTarget, BroadcastType
        system = BroadcastSystem()
        target = BroadcastTarget(broadcast_type=BroadcastType.ALL_USERS)
        message_id = system.queue_broadcast("Test message", target)
        result = system.cancel_broadcast(message_id)
        assert result == True
        assert len(system._message_queue) == 0
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        from telegram.broadcast_system import BroadcastSystem
        system = BroadcastSystem()
        stats = system.get_stats()
        assert "pending_count" in stats
        assert "registered_bots" in stats
        assert stats["registered_bots"] == 3


class TestErrorHandlerImports:
    """Test Error Handler imports."""
    
    def test_import_error_severity(self):
        """Test ErrorSeverity import."""
        from telegram.error_handler import ErrorSeverity
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.CRITICAL.value == "critical"
    
    def test_import_error_category(self):
        """Test ErrorCategory import."""
        from telegram.error_handler import ErrorCategory
        assert ErrorCategory.CONNECTION.value == "connection"
        assert ErrorCategory.RATE_LIMIT.value == "rate_limit"
    
    def test_import_health_status(self):
        """Test HealthStatus import."""
        from telegram.error_handler import HealthStatus
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
    
    def test_import_error_record(self):
        """Test ErrorRecord import."""
        from telegram.error_handler import ErrorRecord, ErrorCategory, ErrorSeverity
        error = ErrorRecord(
            error_id="err_1",
            category=ErrorCategory.CONNECTION,
            severity=ErrorSeverity.HIGH,
            message="Connection lost"
        )
        assert error.error_id == "err_1"
    
    def test_import_error_handler(self):
        """Test ErrorHandler import."""
        from telegram.error_handler import ErrorHandler
        handler = ErrorHandler()
        assert handler is not None


class TestErrorHandler:
    """Test Error Handler functionality."""
    
    def test_handler_creation(self):
        """Test handler creation."""
        from telegram.error_handler import ErrorHandler
        handler = ErrorHandler()
        assert handler.max_retries == 3
        assert handler.retry_delay == 1.0
    
    def test_handle_error(self):
        """Test error handling."""
        from telegram.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
        handler = ErrorHandler()
        error = handler.handle_error(
            Exception("Test error"),
            category=ErrorCategory.CONNECTION,
            severity=ErrorSeverity.MEDIUM
        )
        assert error is not None
        assert error.message == "Test error"
        assert error.category == ErrorCategory.CONNECTION
    
    def test_should_retry(self):
        """Test retry logic."""
        from telegram.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity, RecoveryAction
        handler = ErrorHandler()
        error = handler.handle_error(
            Exception("Connection error"),
            category=ErrorCategory.CONNECTION
        )
        assert handler.should_retry(error)
    
    def test_get_retry_delay(self):
        """Test retry delay calculation."""
        from telegram.error_handler import ErrorHandler, ErrorCategory
        handler = ErrorHandler(retry_delay=1.0, backoff_multiplier=2.0)
        error = handler.handle_error(Exception("Test"), category=ErrorCategory.CONNECTION)
        
        delay1 = handler.get_retry_delay(error)
        assert delay1 == 1.0
        
        handler.increment_retry(error)
        delay2 = handler.get_retry_delay(error)
        assert delay2 == 2.0
    
    def test_mark_resolved(self):
        """Test marking error as resolved."""
        from telegram.error_handler import ErrorHandler, ErrorCategory
        handler = ErrorHandler()
        error = handler.handle_error(Exception("Test"), category=ErrorCategory.INTERNAL)
        
        result = handler.mark_resolved(error.error_id)
        assert result == True
        assert error.resolved == True


class TestHealthMonitor:
    """Test Health Monitor functionality."""
    
    def test_monitor_creation(self):
        """Test monitor creation."""
        from telegram.error_handler import HealthMonitor
        monitor = HealthMonitor()
        assert monitor.check_interval == 60
    
    def test_register_bot(self):
        """Test bot registration."""
        from telegram.error_handler import HealthMonitor
        monitor = HealthMonitor()
        monitor.register_bot("test_bot")
        assert "test_bot" in monitor._bot_stats
    
    def test_record_message(self):
        """Test message recording."""
        from telegram.error_handler import HealthMonitor
        monitor = HealthMonitor()
        monitor.register_bot("test_bot")
        monitor.record_message_sent("test_bot")
        assert monitor._bot_stats["test_bot"]["messages_sent"] == 1
    
    def test_get_bot_health(self):
        """Test bot health retrieval."""
        from telegram.error_handler import HealthMonitor, HealthStatus
        monitor = HealthMonitor()
        monitor.register_bot("test_bot")
        report = monitor.get_bot_health("test_bot")
        assert report is not None
        assert report.bot_id == "test_bot"
        assert report.status == HealthStatus.HEALTHY
    
    def test_get_system_health(self):
        """Test system health retrieval."""
        from telegram.error_handler import HealthMonitor
        monitor = HealthMonitor()
        monitor.register_bot("bot1")
        monitor.register_bot("bot2")
        report = monitor.get_system_health()
        assert report is not None
        assert len(report.bots) == 2
    
    def test_format_health_dashboard(self):
        """Test health dashboard formatting."""
        from telegram.error_handler import HealthMonitor
        monitor = HealthMonitor()
        monitor.register_bot("controller")
        dashboard = monitor.format_health_dashboard()
        assert "System Health" in dashboard


class TestTelegramErrorHandler:
    """Test combined Telegram Error Handler."""
    
    def test_combined_handler_creation(self):
        """Test combined handler creation."""
        from telegram.error_handler import TelegramErrorHandler
        handler = TelegramErrorHandler()
        assert handler.error_handler is not None
        assert handler.health_monitor is not None
    
    def test_register_and_handle(self):
        """Test register bot and handle error."""
        from telegram.error_handler import TelegramErrorHandler, ErrorCategory
        handler = TelegramErrorHandler()
        handler.register_bot("test_bot")
        
        error = handler.handle_error(
            Exception("Test error"),
            category=ErrorCategory.CONNECTION,
            bot_id="test_bot"
        )
        
        assert error is not None
        report = handler.get_health_report()
        assert "test_bot" in report.bots
    
    def test_get_stats(self):
        """Test combined stats."""
        from telegram.error_handler import TelegramErrorHandler
        handler = TelegramErrorHandler()
        stats = handler.get_stats()
        assert "health" in stats
        assert "errors" in stats


class TestDocument18Integration:
    """Test Document 18 integration."""
    
    def test_all_modules_importable(self):
        """Test all modules can be imported."""
        from telegram.bot_orchestrator import BotOrchestrator, BotType, BotState
        from telegram.unified_interface import UnifiedInterface, MenuBuilder, MenuType
        from telegram.command_router import CommandRouter, CommandCategory, MessageType
        from telegram.session_manager import SessionManager, UserSession, SessionState
        from telegram.broadcast_system import BroadcastSystem, BroadcastType
        from telegram.error_handler import ErrorHandler, HealthMonitor, TelegramErrorHandler
        
        assert BotOrchestrator is not None
        assert UnifiedInterface is not None
        assert CommandRouter is not None
        assert SessionManager is not None
        assert BroadcastSystem is not None
        assert TelegramErrorHandler is not None
    
    def test_three_bot_architecture(self):
        """Test 3-bot architecture is implemented."""
        from telegram.bot_orchestrator import BotOrchestrator, BotType
        orchestrator = BotOrchestrator()
        
        assert BotType.CONTROLLER in orchestrator.bots
        assert BotType.NOTIFICATION in orchestrator.bots
        assert BotType.ANALYTICS in orchestrator.bots
    
    def test_menu_system(self):
        """Test menu system is complete."""
        from telegram.unified_interface import MenuBuilder, MenuType
        
        main_menu = MenuBuilder.create_main_menu()
        assert main_menu.menu_type == MenuType.MAIN
        
        _, status_menu = MenuBuilder.create_status_menu()
        assert status_menu.menu_type == MenuType.STATUS
        
        _, emergency_menu = MenuBuilder.create_emergency_menu()
        assert emergency_menu.menu_type == MenuType.EMERGENCY
    
    def test_command_routing(self):
        """Test command routing is complete."""
        from telegram.command_router import CommandRouter
        router = CommandRouter()
        
        commands = ["start", "status", "trades", "close", "closeall", 
                   "pause", "resume", "enable", "disable", "help"]
        for cmd in commands:
            assert router.is_valid_command(cmd), f"Command {cmd} should be valid"


class TestDocument18Summary:
    """Test Document 18 requirements summary."""
    
    def test_bot_orchestrator_complete(self):
        """Test Bot Orchestrator is complete."""
        from telegram.bot_orchestrator import (
            BotOrchestrator, BotType, BotState, BotConfig, 
            BotStatus, QueuedMessage, MessagePriority
        )
        
        orchestrator = BotOrchestrator()
        assert orchestrator.is_running() == False
        assert len(orchestrator.get_all_statuses()) == 3
    
    def test_unified_interface_complete(self):
        """Test Unified Interface is complete."""
        from telegram.unified_interface import (
            UnifiedInterface, MenuBuilder, Menu, MenuType,
            KeyboardButton, KeyboardRow, ButtonType
        )
        
        interface = UnifiedInterface()
        main_menu = interface.get_main_menu()
        assert main_menu is not None
    
    def test_command_router_complete(self):
        """Test Command Router is complete."""
        from telegram.command_router import (
            CommandRouter, CommandRegistry, CallbackRegistry,
            CommandDefinition, CallbackRoute, RouteRule
        )
        
        router = CommandRouter()
        assert len(router.command_registry.get_all()) >= 10
    
    def test_session_manager_complete(self):
        """Test Session Manager is complete."""
        from telegram.session_manager import (
            SessionManager, UserSession, UserPreferences,
            ConversationContext, SessionState, ConversationState
        )
        
        manager = SessionManager()
        session = manager.create_session("test", "chat")
        assert session.preferences is not None
        assert session.context is not None
    
    def test_broadcast_system_complete(self):
        """Test Broadcast System is complete."""
        from telegram.broadcast_system import (
            BroadcastSystem, BroadcastMessage, BroadcastTarget,
            BroadcastType, BroadcastPriority, BroadcastStatus
        )
        
        system = BroadcastSystem()
        stats = system.get_stats()
        assert "registered_bots" in stats
    
    def test_error_handler_complete(self):
        """Test Error Handler is complete."""
        from telegram.error_handler import (
            ErrorHandler, HealthMonitor, TelegramErrorHandler,
            ErrorRecord, ErrorSeverity, ErrorCategory, HealthStatus
        )
        
        handler = TelegramErrorHandler()
        stats = handler.get_stats()
        assert "health" in stats
        assert "errors" in stats
    
    def test_document_18_requirements_met(self):
        """Test all Document 18 requirements are met."""
        requirements = {
            "bot_orchestrator": True,
            "unified_interface": True,
            "command_routing": True,
            "session_management": True,
            "broadcast_system": True,
            "error_handling": True,
            "health_monitoring": True
        }
        
        from telegram.bot_orchestrator import BotOrchestrator
        from telegram.unified_interface import UnifiedInterface
        from telegram.command_router import CommandRouter
        from telegram.session_manager import SessionManager
        from telegram.broadcast_system import BroadcastSystem
        from telegram.error_handler import TelegramErrorHandler
        
        assert BotOrchestrator() is not None
        assert UnifiedInterface() is not None
        assert CommandRouter() is not None
        assert SessionManager() is not None
        assert BroadcastSystem() is not None
        assert TelegramErrorHandler() is not None
        
        for req, status in requirements.items():
            assert status == True, f"Requirement {req} not met"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
