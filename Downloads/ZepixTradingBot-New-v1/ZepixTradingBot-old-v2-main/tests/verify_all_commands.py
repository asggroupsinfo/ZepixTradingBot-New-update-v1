import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config
from src.clients.telegram_bot import TelegramBot
from src.menu.command_executor import CommandExecutor
from src.menu.command_mapping import COMMAND_PARAM_MAP

class TestAllCommandsExecution(unittest.TestCase):
    def setUp(self):
        # Force UTF-8 for Windows console
        import sys
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
            
        # Mock Config
        self.config = MagicMock(spec=Config)
        # Setup config.get() to return appropriate values based on key
        def config_get_side_effect(key, default=None):
            config_values = {
                "default_risk_tier": "10000",
                "risk_tiers": {
                    "5000": {"daily_loss_limit": 100.0, "max_total_loss": 500.0, "lot_size": 0.01},
                    "10000": {"daily_loss_limit": 500.0, "max_total_loss": 5000.0, "lot_size": 0.05},
                    "25000": {"daily_loss_limit": 1000.0, "max_total_loss": 10000.0, "lot_size": 0.1},
                    "50000": {"daily_loss_limit": 2000.0, "max_total_loss": 20000.0, "lot_size": 0.2},
                    "100000": {"daily_loss_limit": 5000.0, "max_total_loss": 50000.0, "lot_size": 0.5}
                },
                "symbol_config": {},
                "reentry_enabled": True,
                "reentry_monitor_interval": 60,
                "reentry_max_levels": 3,
                "reentry_sl_reduction": 0.5
            }
            return config_values.get(key, default)
        
        self.config.get.side_effect = config_get_side_effect
        self.config.update = MagicMock()
        
        # Mock TelegramBot dependencies
        self.bot = MagicMock(spec=TelegramBot)
        self.bot.config = self.config
        self.bot.logger = MagicMock()
        
        # Mock all managers to prevent AttributeErrors
        self.bot.trading_engine = MagicMock()
        self.bot.trading_engine.monitor_error_count = 0
        self.bot.trading_engine.max_monitor_errors = 10
        self.bot.trading_engine.price_monitor = MagicMock()
        self.bot.trading_engine.price_monitor.monitor_error_count = 0
        self.bot.trading_engine.price_monitor.max_monitor_errors = 10
        self.bot.trading_engine.mt5_client = MagicMock()
        self.bot.trading_engine.mt5_client.connection_errors = 0
        self.bot.trading_engine.mt5_client.max_connection_errors = 5
        self.bot.trading_engine.mt5_client.initialized = True
        self.bot.trading_engine.is_paused = False
        self.bot.trading_engine.start_time = 1000.0
        
        # Mock time module for health status
        patcher = patch('time.time', return_value=4600.0) # 3600s = 1 hour uptime
        self.addCleanup(patcher.stop)
        self.mock_time = patcher.start()
        
        # Mock risk manager
        self.bot.risk_manager = MagicMock()
        self.bot.risk_manager.daily_loss = 0.0
        self.bot.risk_manager.lifetime_loss = 50.0
        self.bot.risk_manager.get_stats.return_value = {
            "current_lot_size": 0.05,
            "account_balance": 10000.0,
            "daily_loss": 0.0,
            "total_loss": 0.0,
            "daily_cap": 500.0,
            "lifetime_cap": 5000.0,
            "risk_tier": 10000,
            "total_trades": 10,
            "winning_trades": 6,
            "win_rate": 60.0,
            "daily_profit": 100.0,
            "lifetime_loss": 50.0,
            "risk_parameters": {
                "daily_loss_limit": 500.0,
                "max_total_loss": 5000.0
            }
        }
        
        self.bot.trend_manager = MagicMock()
        self.bot.trend_manager.get_all_trends.return_value = {
            "5m": "BULLISH", "15m": "BEARISH", "1h": "NEUTRAL", "4h": "BULLISH", "1d": "BULLISH"
        }
        self.bot.profit_booking_manager = MagicMock()
        self.bot.menu_manager = MagicMock()
        self.bot.reentry_manager = MagicMock()
        
        # Mock analytics engine inside trading engine
        self.bot.trading_engine.analytics_engine = MagicMock()
        self.bot.trading_engine.analytics_engine.get_performance_report.return_value = {
            'total_trades': 10,
            'winning_trades': 6,
            'losing_trades': 4,
            'total_pnl': 150.0,
            'win_rate': 60.0,
            'average_win': 50.0,
            'average_loss': 37.5
        }
        self.bot.trading_engine.analytics_engine.get_pair_performance.return_value = {
            'XAUUSD': {'trades': 5, 'pnl': 100.0, 'wins': 3},
            'EURUSD': {'trades': 5, 'pnl': 50.0, 'wins': 3}
        }
        self.bot.trading_engine.analytics_engine.get_strategy_performance.return_value = {
            'LOGIC1': {'trades': 5, 'pnl': 100.0, 'wins': 3},
            'LOGIC2': {'trades': 5, 'pnl': 50.0, 'wins': 3}
        }
        
        # Mock reentry manager inside trading engine
        self.bot.trading_engine.reentry_manager = MagicMock()
        self.bot.trading_engine.reentry_manager.active_chains = {}
        
        # Mock profit booking manager inside trading engine
        self.bot.trading_engine.profit_booking_manager = MagicMock()
        
        # Mock send_message to track calls
        self.bot.send_message = MagicMock()
        
        # Initialize CommandExecutor
        self.executor = CommandExecutor(self.bot)

    def test_all_commands_execution(self):
        """Simulate execution of ALL 81 commands to ensure no crashes"""
        print(f"\n🚀 STARTING EXECUTION TEST FOR {len(COMMAND_PARAM_MAP)} COMMANDS...\n")
        
        failed_commands = []
        passed_commands = []
        
        for command, details in COMMAND_PARAM_MAP.items():
            handler_name = details.get('handler')
            
            # Determine where the handler lives and get REAL code
            handler = None
            instance = None
            
            # Check TelegramBot class first
            if hasattr(TelegramBot, handler_name):
                handler = getattr(TelegramBot, handler_name)
                instance = self.bot
            # Check CommandExecutor class
            elif hasattr(CommandExecutor, handler_name):
                handler = getattr(CommandExecutor, handler_name)
                instance = self.executor
            
            if not handler:
                print(f"❌ {command}: Handler '{handler_name}' NOT FOUND")
                failed_commands.append(f"{command} (Missing Handler)")
                continue
                
            # Prepare dummy message/params based on command type
            # We provide a dict which simulates the 'message' or 'params' argument
            dummy_params = {
                'text': f'/{command}',
                'chat': {'id': 123},
                'from_user': {'id': 456},
                # Add common params to satisfy most handlers
                'mode': 'status',
                'symbol': 'XAUUSD',
                'timeframe': '1h',
                'trend': 'BULLISH',
                'amount': '100',
                'value': '10',
                'tier': '10000',
                'logic': 'LOGIC1',
                'system': 'sl-1',
                'percent': '10',
                'lines': '100',
                'date': '2025-01-01',
                'start_date': '2025-01-01',
                'end_date': '2025-01-02',
                'level': 'INFO',
                'profit_sl_mode': 'SL-2.1',
                'chain_id': 'test_chain',
                'targets': [10, 20, 30],
                'multipliers': [1, 2, 3]
            }
            
            try:
                # Reset mock before call
                self.bot.send_message.reset_mock()
                self.bot.send_document.reset_mock()
                
                # Call the handler with the instance (self)
                # This executes the REAL code using the MOCKED instance state
                handler(instance, dummy_params)
                
                # Check if send_message was called (success)
                if self.bot.send_message.called:
                    print(f"✅ {command}: Executed & Responded")
                    passed_commands.append(command)
                else:
                    # Some handlers might return True/False instead of sending message directly
                    # or use other methods like send_document
                    if hasattr(self.bot, 'send_document') and self.bot.send_document.called:
                         print(f"✅ {command}: Executed & Sent Document")
                         passed_commands.append(command)
                    else:
                        print(f"⚠️ {command}: Executed but NO RESPONSE sent")
                        # We count this as pass for now if no exception, but warn
                        passed_commands.append(command)
                        
            except Exception as e:
                print(f"❌ {command}: CRASHED - {str(e)}")
                failed_commands.append(f"{command} (Crash: {str(e)})")

        print("\n" + "="*50)
        print(f"TOTAL COMMANDS: {len(COMMAND_PARAM_MAP)}")
        print(f"PASSED: {len(passed_commands)}")
        print(f"FAILED: {len(failed_commands)}")
        print("="*50)
        
        if failed_commands:
            print("\n❌ FAILED COMMANDS:")
            for f in failed_commands:
                print(f"  - {f}")
            self.fail(f"{len(failed_commands)} commands failed execution test!")
        else:
            print("\n✅ ALL COMMANDS EXECUTED SUCCESSFULLY!")

if __name__ == '__main__':
    unittest.main()
