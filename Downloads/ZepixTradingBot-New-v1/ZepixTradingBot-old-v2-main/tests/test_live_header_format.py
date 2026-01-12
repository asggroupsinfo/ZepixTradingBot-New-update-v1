import sys
import os
import unittest
from unittest.mock import MagicMock
from datetime import datetime
import pytz

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.fixed_clock_system import FixedClockSystem
from src.modules.session_manager import SessionManager

class TestLiveHeaderFormat(unittest.TestCase):
    def setUp(self):
        self.mock_bot = MagicMock()
        self.session_manager = MagicMock()
        
        # Configure Mock Session Manager
        self.session_manager.config = {
            'sessions': {
                'london': {'start_time': '12:30', 'end_time': '21:30'} # Mock times
            }
        }
        self.session_manager.get_current_status.return_value = {
            'current_session': 'London',
            'allowed_symbols': ['EURUSD', 'GBPUSD', 'XAUUSD', 'GBPJPY']
        }
        
        self.clock = FixedClockSystem(self.mock_bot, "12345", self.session_manager)

    def test_header_content(self):
        """Verify the header contains Time, Date, and Session Info correctly formatted"""
        message = self.clock.format_clock_message()
        print("\n\n=== 🖥️  SIMULATED LIVE HEADER DISPLAY ===")
        print(message)
        print("========================================\n")
        
        # Validation
        self.assertIn("🕐 **Current Time:**", message)
        self.assertIn("📅 **Date:**", message)
        self.assertIn("🟢 **Session:** London", message)
        self.assertIn("✅ EURUSD, GBPUSD, XAUUSD...", message)
        self.assertIn("━━━━━━━━━━━━━━━━", message)

if __name__ == "__main__":
    unittest.main()
