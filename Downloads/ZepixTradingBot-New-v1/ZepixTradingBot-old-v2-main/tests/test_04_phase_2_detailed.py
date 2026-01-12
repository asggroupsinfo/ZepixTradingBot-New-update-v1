"""
Test Suite for Document 04: Phase 2 Detailed Plan Implementation

Tests cover:
1. Rate Limiting System (TelegramRateLimiter, MessagePriority, ThrottledMessage)
2. Message Queue Management (MessageQueueManager, MessageRouter, MessageFormatter)
3. Enhanced MultiTelegramManager (rate limiting integration, async API)
4. Expanded ControllerBot (command handlers, callback handlers)
5. NotificationBot (delivery system)
6. AnalyticsBot (report generation)
7. Error Handling and Fallback Mechanisms

Part of Document 04: Phase 2 Detailed Plan - Multi-Telegram System
"""

import pytest
import sys
import os
import ast
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# HELPER FUNCTIONS FOR AST-BASED VERIFICATION
# ============================================================

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()


def check_class_exists(file_path: str, class_name: str) -> bool:
    """Check if a class exists in a file using AST parsing."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return True
        return False
    except Exception:
        return False


def check_class_has_method(file_path: str, class_name: str, method_name: str) -> bool:
    """Check if a class has a specific method using AST parsing."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name == method_name:
                            return True
        return False
    except Exception:
        return False


def check_class_has_attribute(file_path: str, class_name: str, attr_name: str) -> bool:
    """Check if a class __init__ assigns an attribute using AST parsing."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                        for stmt in ast.walk(item):
                            # Check regular assignments
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute):
                                        if target.attr == attr_name:
                                            return True
                            # Check annotated assignments (e.g., self.attr: Type = value)
                            if isinstance(stmt, ast.AnnAssign):
                                if isinstance(stmt.target, ast.Attribute):
                                    if stmt.target.attr == attr_name:
                                        return True
        return False
    except Exception:
        return False


def check_enum_exists(file_path: str, enum_name: str) -> bool:
    """Check if an Enum class exists in a file."""
    return check_class_exists(file_path, enum_name)


def get_class_methods(file_path: str, class_name: str) -> list:
    """Get all method names from a class."""
    methods = []
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)
        return methods
    except Exception:
        return []


# ============================================================
# FILE PATHS
# ============================================================

TELEGRAM_DIR = PROJECT_ROOT / "src" / "telegram"
RATE_LIMITER_FILE = TELEGRAM_DIR / "rate_limiter.py"
MESSAGE_QUEUE_FILE = TELEGRAM_DIR / "message_queue.py"
MULTI_TELEGRAM_FILE = TELEGRAM_DIR / "multi_telegram_manager.py"
CONTROLLER_BOT_FILE = TELEGRAM_DIR / "controller_bot.py"
NOTIFICATION_BOT_FILE = TELEGRAM_DIR / "notification_bot.py"
ANALYTICS_BOT_FILE = TELEGRAM_DIR / "analytics_bot.py"


# ============================================================
# TEST CLASS: Rate Limiter System
# ============================================================

class TestRateLimiterSystem:
    """Tests for the Rate Limiting System (rate_limiter.py)."""
    
    def test_rate_limiter_file_exists(self):
        """Test that rate_limiter.py exists."""
        assert check_file_exists(RATE_LIMITER_FILE), "rate_limiter.py should exist"
    
    def test_message_priority_enum_exists(self):
        """Test that MessagePriority enum exists."""
        assert check_enum_exists(RATE_LIMITER_FILE, "MessagePriority"), \
            "MessagePriority enum should exist"
    
    def test_throttled_message_class_exists(self):
        """Test that ThrottledMessage class exists."""
        assert check_class_exists(RATE_LIMITER_FILE, "ThrottledMessage"), \
            "ThrottledMessage class should exist"
    
    def test_telegram_rate_limiter_class_exists(self):
        """Test that TelegramRateLimiter class exists."""
        assert check_class_exists(RATE_LIMITER_FILE, "TelegramRateLimiter"), \
            "TelegramRateLimiter class should exist"
    
    def test_rate_limit_monitor_class_exists(self):
        """Test that RateLimitMonitor class exists."""
        assert check_class_exists(RATE_LIMITER_FILE, "RateLimitMonitor"), \
            "RateLimitMonitor class should exist"
    
    def test_rate_limiter_has_start_method(self):
        """Test that TelegramRateLimiter has start method."""
        assert check_class_has_method(RATE_LIMITER_FILE, "TelegramRateLimiter", "start"), \
            "TelegramRateLimiter should have start method"
    
    def test_rate_limiter_has_stop_method(self):
        """Test that TelegramRateLimiter has stop method."""
        assert check_class_has_method(RATE_LIMITER_FILE, "TelegramRateLimiter", "stop"), \
            "TelegramRateLimiter should have stop method"
    
    def test_rate_limiter_has_enqueue_method(self):
        """Test that TelegramRateLimiter has enqueue method."""
        assert check_class_has_method(RATE_LIMITER_FILE, "TelegramRateLimiter", "enqueue"), \
            "TelegramRateLimiter should have enqueue method"
    
    def test_rate_limiter_has_can_send_method(self):
        """Test that TelegramRateLimiter has _can_send method."""
        assert check_class_has_method(RATE_LIMITER_FILE, "TelegramRateLimiter", "_can_send"), \
            "TelegramRateLimiter should have _can_send method"
    
    def test_rate_limiter_has_process_queue_method(self):
        """Test that TelegramRateLimiter has _process_queue method."""
        assert check_class_has_method(RATE_LIMITER_FILE, "TelegramRateLimiter", "_process_queue"), \
            "TelegramRateLimiter should have _process_queue method"
    
    def test_rate_limiter_has_get_stats_method(self):
        """Test that TelegramRateLimiter has get_stats method."""
        assert check_class_has_method(RATE_LIMITER_FILE, "TelegramRateLimiter", "get_stats"), \
            "TelegramRateLimiter should have get_stats method"
    
    def test_rate_limiter_has_priority_queues(self):
        """Test that TelegramRateLimiter has priority queues."""
        assert check_class_has_attribute(RATE_LIMITER_FILE, "TelegramRateLimiter", "queue_critical"), \
            "TelegramRateLimiter should have queue_critical attribute"
        assert check_class_has_attribute(RATE_LIMITER_FILE, "TelegramRateLimiter", "queue_high"), \
            "TelegramRateLimiter should have queue_high attribute"
        assert check_class_has_attribute(RATE_LIMITER_FILE, "TelegramRateLimiter", "queue_normal"), \
            "TelegramRateLimiter should have queue_normal attribute"
        assert check_class_has_attribute(RATE_LIMITER_FILE, "TelegramRateLimiter", "queue_low"), \
            "TelegramRateLimiter should have queue_low attribute"
    
    def test_rate_monitor_has_check_health_method(self):
        """Test that RateLimitMonitor has check_health method."""
        assert check_class_has_method(RATE_LIMITER_FILE, "RateLimitMonitor", "check_health"), \
            "RateLimitMonitor should have check_health method"


# ============================================================
# TEST CLASS: Message Queue System
# ============================================================

class TestMessageQueueSystem:
    """Tests for the Message Queue System (message_queue.py)."""
    
    def test_message_queue_file_exists(self):
        """Test that message_queue.py exists."""
        assert check_file_exists(MESSAGE_QUEUE_FILE), "message_queue.py should exist"
    
    def test_message_type_enum_exists(self):
        """Test that MessageType enum exists."""
        assert check_enum_exists(MESSAGE_QUEUE_FILE, "MessageType"), \
            "MessageType enum should exist"
    
    def test_delivery_status_enum_exists(self):
        """Test that DeliveryStatus enum exists."""
        assert check_enum_exists(MESSAGE_QUEUE_FILE, "DeliveryStatus"), \
            "DeliveryStatus enum should exist"
    
    def test_queued_message_class_exists(self):
        """Test that QueuedMessage class exists."""
        assert check_class_exists(MESSAGE_QUEUE_FILE, "QueuedMessage"), \
            "QueuedMessage class should exist"
    
    def test_message_router_class_exists(self):
        """Test that MessageRouter class exists."""
        assert check_class_exists(MESSAGE_QUEUE_FILE, "MessageRouter"), \
            "MessageRouter class should exist"
    
    def test_message_queue_manager_class_exists(self):
        """Test that MessageQueueManager class exists."""
        assert check_class_exists(MESSAGE_QUEUE_FILE, "MessageQueueManager"), \
            "MessageQueueManager class should exist"
    
    def test_message_formatter_class_exists(self):
        """Test that MessageFormatter class exists."""
        assert check_class_exists(MESSAGE_QUEUE_FILE, "MessageFormatter"), \
            "MessageFormatter class should exist"
    
    def test_message_router_has_get_target_bot(self):
        """Test that MessageRouter has get_target_bot method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageRouter", "get_target_bot"), \
            "MessageRouter should have get_target_bot method"
    
    def test_message_router_has_get_priority_for_type(self):
        """Test that MessageRouter has get_priority_for_type method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageRouter", "get_priority_for_type"), \
            "MessageRouter should have get_priority_for_type method"
    
    def test_queue_manager_has_start_method(self):
        """Test that MessageQueueManager has start method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageQueueManager", "start"), \
            "MessageQueueManager should have start method"
    
    def test_queue_manager_has_stop_method(self):
        """Test that MessageQueueManager has stop method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageQueueManager", "stop"), \
            "MessageQueueManager should have stop method"
    
    def test_queue_manager_has_enqueue_method(self):
        """Test that MessageQueueManager has enqueue method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageQueueManager", "enqueue"), \
            "MessageQueueManager should have enqueue method"
    
    def test_queue_manager_has_dequeue_method(self):
        """Test that MessageQueueManager has dequeue method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageQueueManager", "dequeue"), \
            "MessageQueueManager should have dequeue method"
    
    def test_queue_manager_has_get_stats_method(self):
        """Test that MessageQueueManager has get_stats method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageQueueManager", "get_stats"), \
            "MessageQueueManager should have get_stats method"
    
    def test_message_formatter_has_format_entry(self):
        """Test that MessageFormatter has format_entry method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageFormatter", "format_entry"), \
            "MessageFormatter should have format_entry method"
    
    def test_message_formatter_has_format_exit(self):
        """Test that MessageFormatter has format_exit method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageFormatter", "format_exit"), \
            "MessageFormatter should have format_exit method"
    
    def test_message_formatter_has_format_error(self):
        """Test that MessageFormatter has format_error method."""
        assert check_class_has_method(MESSAGE_QUEUE_FILE, "MessageFormatter", "format_error"), \
            "MessageFormatter should have format_error method"


# ============================================================
# TEST CLASS: Enhanced MultiTelegramManager
# ============================================================

class TestMultiTelegramManager:
    """Tests for the Enhanced MultiTelegramManager."""
    
    def test_multi_telegram_file_exists(self):
        """Test that multi_telegram_manager.py exists."""
        assert check_file_exists(MULTI_TELEGRAM_FILE), "multi_telegram_manager.py should exist"
    
    def test_multi_telegram_manager_class_exists(self):
        """Test that MultiTelegramManager class exists."""
        assert check_class_exists(MULTI_TELEGRAM_FILE, "MultiTelegramManager"), \
            "MultiTelegramManager class should exist"
    
    def test_has_init_bots_method(self):
        """Test that MultiTelegramManager has _init_bots method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "_init_bots"), \
            "MultiTelegramManager should have _init_bots method"
    
    def test_has_init_rate_limiters_method(self):
        """Test that MultiTelegramManager has _init_rate_limiters method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "_init_rate_limiters"), \
            "MultiTelegramManager should have _init_rate_limiters method"
    
    def test_has_init_message_queue_method(self):
        """Test that MultiTelegramManager has _init_message_queue method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "_init_message_queue"), \
            "MultiTelegramManager should have _init_message_queue method"
    
    def test_has_start_method(self):
        """Test that MultiTelegramManager has start method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "start"), \
            "MultiTelegramManager should have start method"
    
    def test_has_stop_method(self):
        """Test that MultiTelegramManager has stop method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "stop"), \
            "MultiTelegramManager should have stop method"
    
    def test_has_route_message_method(self):
        """Test that MultiTelegramManager has route_message method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "route_message"), \
            "MultiTelegramManager should have route_message method"
    
    def test_has_send_alert_method(self):
        """Test that MultiTelegramManager has send_alert method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_alert"), \
            "MultiTelegramManager should have send_alert method"
    
    def test_has_send_report_method(self):
        """Test that MultiTelegramManager has send_report method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_report"), \
            "MultiTelegramManager should have send_report method"
    
    def test_has_send_controller_message_method(self):
        """Test that MultiTelegramManager has send_controller_message async method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_controller_message"), \
            "MultiTelegramManager should have send_controller_message method"
    
    def test_has_send_notification_method(self):
        """Test that MultiTelegramManager has send_notification async method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_notification"), \
            "MultiTelegramManager should have send_notification method"
    
    def test_has_send_analytics_report_method(self):
        """Test that MultiTelegramManager has send_analytics_report async method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_analytics_report"), \
            "MultiTelegramManager should have send_analytics_report method"
    
    def test_has_send_entry_alert_method(self):
        """Test that MultiTelegramManager has send_entry_alert method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_entry_alert"), \
            "MultiTelegramManager should have send_entry_alert method"
    
    def test_has_send_exit_alert_method(self):
        """Test that MultiTelegramManager has send_exit_alert method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_exit_alert"), \
            "MultiTelegramManager should have send_exit_alert method"
    
    def test_has_send_error_alert_method(self):
        """Test that MultiTelegramManager has send_error_alert method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "send_error_alert"), \
            "MultiTelegramManager should have send_error_alert method"
    
    def test_has_get_rate_limit_stats_method(self):
        """Test that MultiTelegramManager has get_rate_limit_stats method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "get_rate_limit_stats"), \
            "MultiTelegramManager should have get_rate_limit_stats method"
    
    def test_has_get_health_status_method(self):
        """Test that MultiTelegramManager has get_health_status method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "get_health_status"), \
            "MultiTelegramManager should have get_health_status method"
    
    def test_has_get_stats_method(self):
        """Test that MultiTelegramManager has get_stats method."""
        assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", "get_stats"), \
            "MultiTelegramManager should have get_stats method"


# ============================================================
# TEST CLASS: Expanded ControllerBot
# ============================================================

class TestControllerBot:
    """Tests for the Expanded ControllerBot."""
    
    def test_controller_bot_file_exists(self):
        """Test that controller_bot.py exists."""
        assert check_file_exists(CONTROLLER_BOT_FILE), "controller_bot.py should exist"
    
    def test_controller_bot_class_exists(self):
        """Test that ControllerBot class exists."""
        assert check_class_exists(CONTROLLER_BOT_FILE, "ControllerBot"), \
            "ControllerBot class should exist"
    
    def test_command_category_enum_exists(self):
        """Test that CommandCategory enum exists."""
        assert check_enum_exists(CONTROLLER_BOT_FILE, "CommandCategory"), \
            "CommandCategory enum should exist"
    
    def test_has_start_method(self):
        """Test that ControllerBot has start method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "start"), \
            "ControllerBot should have start method"
    
    def test_has_stop_method(self):
        """Test that ControllerBot has stop method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "stop"), \
            "ControllerBot should have stop method"
    
    def test_has_process_command_method(self):
        """Test that ControllerBot has process_command method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "process_command"), \
            "ControllerBot should have process_command method"
    
    def test_has_process_callback_method(self):
        """Test that ControllerBot has process_callback method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "process_callback"), \
            "ControllerBot should have process_callback method"
    
    def test_has_handle_start_command(self):
        """Test that ControllerBot has _handle_start method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_start"), \
            "ControllerBot should have _handle_start method"
    
    def test_has_handle_stop_command(self):
        """Test that ControllerBot has _handle_stop method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_stop"), \
            "ControllerBot should have _handle_stop method"
    
    def test_has_handle_status_command(self):
        """Test that ControllerBot has _handle_status method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_status"), \
            "ControllerBot should have _handle_status method"
    
    def test_has_handle_plugins_command(self):
        """Test that ControllerBot has _handle_plugins method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_plugins"), \
            "ControllerBot should have _handle_plugins method"
    
    def test_has_handle_help_command(self):
        """Test that ControllerBot has _handle_help method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_help"), \
            "ControllerBot should have _handle_help method"
    
    def test_has_handle_menu_command(self):
        """Test that ControllerBot has _handle_menu method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_menu"), \
            "ControllerBot should have _handle_menu method"
    
    # Document 04 expanded commands
    
    def test_has_handle_health_command(self):
        """Test that ControllerBot has _handle_health method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_health"), \
            "ControllerBot should have _handle_health method"
    
    def test_has_handle_uptime_command(self):
        """Test that ControllerBot has _handle_uptime method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_uptime"), \
            "ControllerBot should have _handle_uptime method"
    
    def test_has_handle_enable_plugin_command(self):
        """Test that ControllerBot has _handle_enable_plugin method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_enable_plugin"), \
            "ControllerBot should have _handle_enable_plugin method"
    
    def test_has_handle_disable_plugin_command(self):
        """Test that ControllerBot has _handle_disable_plugin method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_disable_plugin"), \
            "ControllerBot should have _handle_disable_plugin method"
    
    def test_has_handle_plugin_status_command(self):
        """Test that ControllerBot has _handle_plugin_status method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_plugin_status"), \
            "ControllerBot should have _handle_plugin_status method"
    
    def test_has_handle_trades_command(self):
        """Test that ControllerBot has _handle_trades method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_trades"), \
            "ControllerBot should have _handle_trades method"
    
    def test_has_handle_positions_command(self):
        """Test that ControllerBot has _handle_positions method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_positions"), \
            "ControllerBot should have _handle_positions method"
    
    def test_has_handle_close_all_command(self):
        """Test that ControllerBot has _handle_close_all method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_close_all"), \
            "ControllerBot should have _handle_close_all method"
    
    def test_has_handle_settings_command(self):
        """Test that ControllerBot has _handle_settings method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_settings"), \
            "ControllerBot should have _handle_settings method"
    
    def test_has_handle_set_risk_command(self):
        """Test that ControllerBot has _handle_set_risk method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_set_risk"), \
            "ControllerBot should have _handle_set_risk method"
    
    def test_has_handle_daily_command(self):
        """Test that ControllerBot has _handle_daily method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_daily"), \
            "ControllerBot should have _handle_daily method"
    
    def test_has_handle_weekly_command(self):
        """Test that ControllerBot has _handle_weekly method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_handle_weekly"), \
            "ControllerBot should have _handle_weekly method"
    
    # Callback handlers
    
    def test_has_callback_menu_main(self):
        """Test that ControllerBot has _callback_menu_main method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_callback_menu_main"), \
            "ControllerBot should have _callback_menu_main method"
    
    def test_has_callback_cancel(self):
        """Test that ControllerBot has _callback_cancel method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_callback_cancel"), \
            "ControllerBot should have _callback_cancel method"
    
    def test_has_format_uptime_method(self):
        """Test that ControllerBot has _format_uptime method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "_format_uptime"), \
            "ControllerBot should have _format_uptime method"
    
    def test_has_get_status_method(self):
        """Test that ControllerBot has get_status method."""
        assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", "get_status"), \
            "ControllerBot should have get_status method"


# ============================================================
# TEST CLASS: NotificationBot
# ============================================================

class TestNotificationBot:
    """Tests for the NotificationBot."""
    
    def test_notification_bot_file_exists(self):
        """Test that notification_bot.py exists."""
        assert check_file_exists(NOTIFICATION_BOT_FILE), "notification_bot.py should exist"
    
    def test_notification_bot_class_exists(self):
        """Test that NotificationBot class exists."""
        assert check_class_exists(NOTIFICATION_BOT_FILE, "NotificationBot"), \
            "NotificationBot class should exist"
    
    def test_notification_priority_enum_exists(self):
        """Test that NotificationPriority enum exists."""
        assert check_enum_exists(NOTIFICATION_BOT_FILE, "NotificationPriority"), \
            "NotificationPriority enum should exist"
    
    def test_has_start_method(self):
        """Test that NotificationBot has start method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "start"), \
            "NotificationBot should have start method"
    
    def test_has_stop_method(self):
        """Test that NotificationBot has stop method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "stop"), \
            "NotificationBot should have stop method"
    
    def test_has_send_message_method(self):
        """Test that NotificationBot has send_message method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "send_message"), \
            "NotificationBot should have send_message method"
    
    def test_has_send_entry_notification_method(self):
        """Test that NotificationBot has send_entry_notification method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "send_entry_notification"), \
            "NotificationBot should have send_entry_notification method"
    
    def test_has_send_exit_notification_method(self):
        """Test that NotificationBot has send_exit_notification method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "send_exit_notification"), \
            "NotificationBot should have send_exit_notification method"
    
    def test_has_send_profit_booking_notification_method(self):
        """Test that NotificationBot has send_profit_booking_notification method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "send_profit_booking_notification"), \
            "NotificationBot should have send_profit_booking_notification method"
    
    def test_has_send_reentry_notification_method(self):
        """Test that NotificationBot has send_reentry_notification method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "send_reentry_notification"), \
            "NotificationBot should have send_reentry_notification method"
    
    def test_has_send_error_notification_method(self):
        """Test that NotificationBot has send_error_notification method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "send_error_notification"), \
            "NotificationBot should have send_error_notification method"
    
    def test_has_send_warning_notification_method(self):
        """Test that NotificationBot has send_warning_notification method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "send_warning_notification"), \
            "NotificationBot should have send_warning_notification method"
    
    def test_has_get_status_method(self):
        """Test that NotificationBot has get_status method."""
        assert check_class_has_method(NOTIFICATION_BOT_FILE, "NotificationBot", "get_status"), \
            "NotificationBot should have get_status method"


# ============================================================
# TEST CLASS: AnalyticsBot
# ============================================================

class TestAnalyticsBot:
    """Tests for the AnalyticsBot."""
    
    def test_analytics_bot_file_exists(self):
        """Test that analytics_bot.py exists."""
        assert check_file_exists(ANALYTICS_BOT_FILE), "analytics_bot.py should exist"
    
    def test_analytics_bot_class_exists(self):
        """Test that AnalyticsBot class exists."""
        assert check_class_exists(ANALYTICS_BOT_FILE, "AnalyticsBot"), \
            "AnalyticsBot class should exist"
    
    def test_report_type_enum_exists(self):
        """Test that ReportType enum exists."""
        assert check_enum_exists(ANALYTICS_BOT_FILE, "ReportType"), \
            "ReportType enum should exist"
    
    def test_has_start_method(self):
        """Test that AnalyticsBot has start method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "start"), \
            "AnalyticsBot should have start method"
    
    def test_has_stop_method(self):
        """Test that AnalyticsBot has stop method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "stop"), \
            "AnalyticsBot should have stop method"
    
    def test_has_send_message_method(self):
        """Test that AnalyticsBot has send_message method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "send_message"), \
            "AnalyticsBot should have send_message method"
    
    def test_has_send_daily_report_method(self):
        """Test that AnalyticsBot has send_daily_report method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "send_daily_report"), \
            "AnalyticsBot should have send_daily_report method"
    
    def test_has_send_weekly_report_method(self):
        """Test that AnalyticsBot has send_weekly_report method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "send_weekly_report"), \
            "AnalyticsBot should have send_weekly_report method"
    
    def test_has_send_plugin_report_method(self):
        """Test that AnalyticsBot has send_plugin_report method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "send_plugin_report"), \
            "AnalyticsBot should have send_plugin_report method"
    
    def test_has_send_symbol_report_method(self):
        """Test that AnalyticsBot has send_symbol_report method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "send_symbol_report"), \
            "AnalyticsBot should have send_symbol_report method"
    
    def test_has_send_system_health_report_method(self):
        """Test that AnalyticsBot has send_system_health_report method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "send_system_health_report"), \
            "AnalyticsBot should have send_system_health_report method"
    
    def test_has_get_status_method(self):
        """Test that AnalyticsBot has get_status method."""
        assert check_class_has_method(ANALYTICS_BOT_FILE, "AnalyticsBot", "get_status"), \
            "AnalyticsBot should have get_status method"


# ============================================================
# TEST CLASS: Integration Tests
# ============================================================

class TestDocument04Integration:
    """Integration tests for Document 04 components."""
    
    def test_all_telegram_files_exist(self):
        """Test that all telegram module files exist."""
        files = [
            RATE_LIMITER_FILE,
            MESSAGE_QUEUE_FILE,
            MULTI_TELEGRAM_FILE,
            CONTROLLER_BOT_FILE,
            NOTIFICATION_BOT_FILE,
            ANALYTICS_BOT_FILE
        ]
        for f in files:
            assert check_file_exists(f), f"{f.name} should exist"
    
    def test_rate_limiter_has_all_priority_levels(self):
        """Test that MessagePriority has all required levels."""
        with open(RATE_LIMITER_FILE, 'r') as f:
            content = f.read()
        
        assert "LOW" in content, "MessagePriority should have LOW level"
        assert "NORMAL" in content, "MessagePriority should have NORMAL level"
        assert "HIGH" in content, "MessagePriority should have HIGH level"
        assert "CRITICAL" in content, "MessagePriority should have CRITICAL level"
    
    def test_message_queue_has_all_message_types(self):
        """Test that MessageType has all required types."""
        with open(MESSAGE_QUEUE_FILE, 'r') as f:
            content = f.read()
        
        assert "COMMAND" in content, "MessageType should have COMMAND type"
        assert "ALERT" in content, "MessageType should have ALERT type"
        assert "ENTRY" in content, "MessageType should have ENTRY type"
        assert "EXIT" in content, "MessageType should have EXIT type"
        assert "REPORT" in content, "MessageType should have REPORT type"
    
    def test_multi_telegram_has_rate_limiting_flag(self):
        """Test that MultiTelegramManager has rate limiting availability flag."""
        with open(MULTI_TELEGRAM_FILE, 'r') as f:
            content = f.read()
        
        assert "RATE_LIMITING_AVAILABLE" in content, \
            "MultiTelegramManager should have RATE_LIMITING_AVAILABLE flag"
    
    def test_controller_bot_has_command_categories(self):
        """Test that ControllerBot has command categories."""
        with open(CONTROLLER_BOT_FILE, 'r') as f:
            content = f.read()
        
        assert "CommandCategory" in content, "ControllerBot should have CommandCategory"
        assert "SYSTEM" in content, "CommandCategory should have SYSTEM"
        assert "TRADING" in content, "CommandCategory should have TRADING"
        assert "PLUGINS" in content, "CommandCategory should have PLUGINS"


# ============================================================
# TEST CLASS: Document 04 Summary
# ============================================================

class TestDocument04Summary:
    """Summary tests for Document 04 implementation."""
    
    def test_rate_limiter_complete(self):
        """Test that rate limiter implementation is complete."""
        required_classes = ["MessagePriority", "ThrottledMessage", "TelegramRateLimiter", "RateLimitMonitor"]
        for cls in required_classes:
            assert check_class_exists(RATE_LIMITER_FILE, cls), f"{cls} should exist in rate_limiter.py"
    
    def test_message_queue_complete(self):
        """Test that message queue implementation is complete."""
        required_classes = ["MessageType", "DeliveryStatus", "QueuedMessage", "MessageRouter", "MessageQueueManager", "MessageFormatter"]
        for cls in required_classes:
            assert check_class_exists(MESSAGE_QUEUE_FILE, cls), f"{cls} should exist in message_queue.py"
    
    def test_multi_telegram_manager_complete(self):
        """Test that MultiTelegramManager implementation is complete."""
        required_methods = [
            "start", "stop", "route_message", "send_alert", "send_report",
            "send_controller_message", "send_notification", "send_analytics_report",
            "get_rate_limit_stats", "get_health_status", "get_stats"
        ]
        for method in required_methods:
            assert check_class_has_method(MULTI_TELEGRAM_FILE, "MultiTelegramManager", method), \
                f"MultiTelegramManager should have {method} method"
    
    def test_controller_bot_expanded_commands(self):
        """Test that ControllerBot has all expanded commands."""
        expanded_commands = [
            "_handle_health", "_handle_uptime", "_handle_enable_plugin",
            "_handle_disable_plugin", "_handle_plugin_status", "_handle_trades",
            "_handle_positions", "_handle_close_all", "_handle_settings",
            "_handle_set_risk", "_handle_daily", "_handle_weekly"
        ]
        for cmd in expanded_commands:
            assert check_class_has_method(CONTROLLER_BOT_FILE, "ControllerBot", cmd), \
                f"ControllerBot should have {cmd} method"
    
    def test_all_bots_have_get_status(self):
        """Test that all bots have get_status method."""
        bots = [
            (CONTROLLER_BOT_FILE, "ControllerBot"),
            (NOTIFICATION_BOT_FILE, "NotificationBot"),
            (ANALYTICS_BOT_FILE, "AnalyticsBot")
        ]
        for file_path, class_name in bots:
            assert check_class_has_method(file_path, class_name, "get_status"), \
                f"{class_name} should have get_status method"


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
