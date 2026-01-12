
import logging
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
import os
from datetime import datetime

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the imports that might cause issues outside of full environment
sys.modules['telegram'] = MagicMock()
sys.modules['telegram.ext'] = MagicMock()

from src.menu.menu_manager import MenuManager
from src.menu.command_executor import CommandExecutor
from src.menu.menu_constants import MENU_CATEGORIES, DEFAULT_MENU_LAYOUT
from src.core.trading_engine import TradingEngine
from src.managers.risk_manager import RiskManager
from src.utils.pip_calculator import PipCalculator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestTimeframeImplementation(unittest.TestCase):
    def setUp(self):
        # Setup mock bot configuration
        self.config = {
            "account_size": 10000,
            "risk_per_trade": 1.0,
            "fixed_lot_sizes": {
                "5000": 0.05,
                "10000": 0.10
            },
            "timeframe_specific_config": {
                "enabled": True,
                "LOGIC1": {
                    "timeframe": "30m",
                    "lot_multiplier": 1.0, 
                    "sl_multiplier": 1.0,
                    "recovery_window_minutes": 30
                },
                "LOGIC2": {
                    "timeframe": "1h",
                    "lot_multiplier": 1.0, 
                    "sl_multiplier": 1.0, 
                    "recovery_window_minutes": 60
                },
                "LOGIC3": {
                    "timeframe": "scalp",
                    "lot_multiplier": 1.5, 
                    "sl_multiplier": 1.2, 
                    "recovery_window_minutes": 120
                }
            },
            "symbol_config": {
                "EURUSD": {
                    "pip_size": 0.0001, 
                    "volatility": "medium",
                    "pip_value_per_std_lot": 10.0
                }
            },
            "risk_by_account_tier": {
                "5000": {"medium": {"risk_dollars": 50}},
                "10000": {"medium": {"risk_dollars": 100}}
            }
        }
        
        # Mock Bot
        self.bot = MagicMock()
        self.bot.config = self.config
        
        # Initialize Managers with mocked dependencies
        self.bot.risk_manager = RiskManager(self.config)
        self.bot.pip_calculator = PipCalculator(self.config)
        
        # Menu System
        self.menu_manager = MenuManager(self.bot)
        self.bot.menu_manager = self.menu_manager
        
        # Command Executor
        self.executor = CommandExecutor(self.bot)

    def test_menu_structure(self):
        """Test if menu constants are correctly updated"""
        logger.info("Testing Menu Structure...")
        
        # Check Categories
        self.assertIn("timeframe", MENU_CATEGORIES)
        self.assertEqual(MENU_CATEGORIES["timeframe"]["title"], "⏱️ Timeframe Config")
        
        # Check Layout
        self.assertIn("timeframe", DEFAULT_MENU_LAYOUT)
        layout = DEFAULT_MENU_LAYOUT["timeframe"]
        self.assertTrue(any(btn["callback_data"] == "action_toggle_timeframe" for row in layout for btn in row))
        
        logger.info("✅ Menu Structure Verified")

    def test_command_wiring(self):
        """Test if commands are correctly wired in executor"""
        logger.info("Testing Command Wiring...")
        
        # Test command mapping access
        # Instead of accessing internal map, we check if execution methods are called
        self.bot.handle_toggle_timeframe = MagicMock()
        
        # Execute command
        result = self.executor.execute_command(123, "toggle_timeframe", {})
        
        # Verify the bot handler was called
        # Note: In real execution, execute_command calls handle_toggle_timeframe
        # But since we mocked bot, we verify the attribute access or method call if possible
        # For this unit test, we rely on the fact that result is True/False or it didn't crash
        
        # A clearer test might be to verify _execute_... methods exist if they were added,
        # or check the command_map logic inside execute_command.
        # Since execute_command builds a local command_map, we can verify via execution.
        
        self.assertTrue(result, "Command execution should return True")
        self.bot.handle_toggle_timeframe.assert_called_once()
        
        logger.info("✅ Command Wiring Verified")

    def test_fresh_order_logic(self):
        """Test fresh order calculation with timeframe logic"""
        logger.info("Testing Fresh Order Logic...")
        
        balance = 10000
        
        # LOGIC1 (1.0x)
        lot1 = self.bot.risk_manager.get_lot_size_for_logic(balance, "LOGIC1")
        self.assertEqual(lot1, 0.10) # Base 0.10 * 1.0
        
        # LOGIC3 (1.5x)
        lot3 = self.bot.risk_manager.get_lot_size_for_logic(balance, "LOGIC3")
        self.assertEqual(lot3, 0.15) # Base 0.10 * 1.5
        
        logger.info(f"✅ Lot Sizes Verified: LOGIC1={lot1}, LOGIC3={lot3}")

    def test_sl_calculation_logic(self):
        """Test SL calculation with logic multipliers"""
        logger.info("Testing SL Calculation Logic...")
        
        # Mock settings
        symbol = "EURUSD"
        entry = 1.1000
        signal = "BUY"
        lot = 0.1
        balance = 10000
        
        # Standard Calc (LOGIC1 - 1.0x)
        sl1, dist1 = self.bot.pip_calculator.calculate_sl_price(
            symbol, entry, signal, lot, balance, logic="LOGIC1"
        )
        
        # Multiplied Calc (LOGIC3 - 1.2x)
        sl3, dist3 = self.bot.pip_calculator.calculate_sl_price(
            symbol, entry, signal, lot, balance, logic="LOGIC3"
        )
        
        # Verify Distance Scaling
        self.assertAlmostEqual(dist3, dist1 * 1.2, places=4)
        
        logger.info(f"✅ SL Distances Verified: LOGIC1={dist1}, LOGIC3={dist3}")

if __name__ == '__main__':
    # Run tests
    unittest.main()
