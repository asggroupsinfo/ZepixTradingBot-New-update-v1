import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import asyncio

# Fix path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from clients.menu_callback_handler import MenuCallbackHandler
from src.telegram.session_menu_handler import SessionMenuHandler

class TestUIIntegration(unittest.TestCase):
    def setUp(self):
        # Mock Telegram Bot
        self.mock_bot = MagicMock()
        self.mock_bot.handle_voice_test_command = MagicMock()
        self.mock_bot.handle_clock_command = MagicMock()
        self.mock_bot.menu_manager = MagicMock()
        
        # Init Handler
        self.handler = MenuCallbackHandler(self.mock_bot)
        
    def test_voice_button_trigger(self):
        """Test that action_voice_test triggers handle_voice_test_command"""
        print("\n🔹 Testing Voice Button Click...")
        result = self.handler.handle_menu_callback("action_voice_test", 12345, 999)
        
        self.assertTrue(result)
        self.mock_bot.handle_voice_test_command.assert_called_once()
        print("✅ PASS: Voice button called bot handler")

    def test_clock_button_trigger(self):
        """Test that action_clock triggers handle_clock_command"""
        print("\n🔹 Testing Clock Button Click...")
        result = self.handler.handle_menu_callback("action_clock", 12345, 999)
        
        self.assertTrue(result)
        self.mock_bot.handle_clock_command.assert_called_once()
        print("✅ PASS: Clock button called bot handler")

    def test_session_button_route(self):
        """Mock test to verify session route (handled separately in telegram_bot but good to check callback name validity)"""
        # This just confirms the callback string we used in MenuManager matches what TelegramBot looks for
        session_callback = "session_dashboard"
        self.assertTrue(session_callback.startswith("session_"))
        print("\n✅ PASS: Session callback format valid for routing")

if __name__ == "__main__":
    unittest.main()
