import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.clients.telegram_bot import TelegramBot
from src.core.trading_engine import TradingEngine
from src.models import Alert

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Simulation")

class SimulationRunner:
    def __init__(self):
        self.config = MagicMock()
        def config_get_side_effect(key, default=None):
            if key == "telegram_token": return "123:test"
            if key == "telegram_chat_id": return "123456"
            if key.endswith("_config") or key in ["risk_parameters", "timeframe_specific_config"]:
                return default or {}
            if key == "simulate_orders": return True
            if key == "manual_lot_overrides": return {}
            if key == "fixed_lot_sizes": return {}
            return default or "dummy"
        
        self.config.get.side_effect = config_get_side_effect
        self.config.__getitem__.side_effect = lambda k: config_get_side_effect(k)
        self.mock_risk = MagicMock()
        self.mock_risk.can_trade.return_value = True
        self.mock_mt5 = MagicMock()
        
        # Setup Bot with SessionManager
        with patch('src.clients.telegram_bot.FixedClockSystem'), \
             patch('src.clients.telegram_bot.VoiceAlertSystem'):
            self.bot = TelegramBot(self.config)
            
        # Manually set session manager check result
        self.bot.session_manager = MagicMock()
        
        # Setup Trading Engine
        with patch('src.core.trading_engine.TradeDatabase'), \
             patch('src.core.trading_engine.PipCalculator'), \
             patch('src.core.trading_engine.AutonomousSystemManager'), \
             patch('src.core.trading_engine.PriceMonitorService'), \
             patch('src.core.trading_engine.ReversalExitHandler'), \
             patch('src.core.trading_engine.ReEntryManager'), \
             patch('src.core.trading_engine.ProfitBookingManager'), \
             patch('src.core.trading_engine.ProfitBookingReEntryManager'), \
             patch('src.core.trading_engine.DualOrderManager'), \
             patch('src.core.trading_engine.logger'):
            self.engine = TradingEngine(self.config, self.mock_risk, self.mock_mt5, self.bot, MagicMock())
            # Mock internal managers to isolate session logic check
            self.engine.trend_manager = MagicMock()
            self.engine.trend_manager.check_logic_alignment.return_value = {'aligned': True}

    async def run_scenario(self, symbol, session_allowed, reason):
        print(f"\n--- Running Scenario: {symbol} | Session Allowed: {session_allowed} ---")
        
        # Reset Mock Call History
        self.engine.trend_manager.reset_mock()
        self.engine.trend_manager.check_logic_alignment.return_value = {
            'aligned': True,
            'direction': 'BULLISH'
        }
        
        # Setup Mock Behavior
        self.bot.session_manager.check_trade_allowed.return_value = {
            'allowed': session_allowed, 
            'reason': reason
        }
        
        # Create Alert
        alert = MagicMock(spec=Alert)
        alert.symbol = symbol
        alert.tf = "5m"
        alert.type = "entry"
        alert.signal = "buy"
        alert.strategy = "TestStrategy"
        alert.price = 1.1000
        
        print(f"[1] Signal Received: {symbol} (5m) @ 1.1000")
        
        # Execute (Wait for async)
        await self.engine.execute_trades(alert)
        
        # Verification
        self.bot.session_manager.check_trade_allowed.assert_called_with(symbol)
        print(f"[2] Session Check: Performed for {symbol}")
        
        if session_allowed:
            if self.engine.trend_manager.check_logic_alignment.called:
                print(f"[3] Result: [PASS] Trade Proceeded to Trend Check (PASSED)")
                return True
            else:
                print(f"[3] Result: [FAIL] Trade Blocked Unexpectedly (FAILED)")
                return False
        else:
            if not self.engine.trend_manager.check_logic_alignment.called:
                print(f"[3] Result: [PASS] Trade Blocked as Expected (Reason: {reason})")
                return True
            else:
                print(f"[3] Result: [FAIL] Trade Leaked Through Session Block (FAILED)")
                return False

async def main():
    print("Starting End-to-End Session logic Simulation\n")
    sim = SimulationRunner()
    
    # Scenario 1: Open Session (EURUSD)
    success1 = await sim.run_scenario("EURUSD", True, "London Session Open")
    
    # Scenario 2: Closed Session (EURUSD)
    success2 = await sim.run_scenario("EURUSD", False, "Session Closed (Outside Asian/London/NY)")
    
    # Scenario 3: Crypto (Should pass filter usually, but here we explicitly model passing/blocking)
    # If we assume crypto is always open in session manager config
    success3 = await sim.run_scenario("BTCUSD", True, "Crypto Always Open")
    
    if success1 and success2 and success3:
        print("\n[DONE] ALL SCENARIOS PASSED. Session Logic Verification Complete.")
        sys.exit(0)
    else:
        print("\n[FAIL] SIMULATION FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
