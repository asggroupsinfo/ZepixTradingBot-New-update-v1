import pytest
from unittest.mock import MagicMock, patch
import json
import os
from src.clients.telegram_bot import TelegramBot
from src.core.trading_engine import TradingEngine
from src.modules.session_manager import SessionManager
from src.modules.voice_alert_system import VoiceAlertSystem
from src.modules.fixed_clock_system import FixedClockSystem

class TestPhase6Integration:
    
    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.return_value = "dummy"
        return config
        
    @pytest.fixture
    def mock_telegram_bot(self, mock_config):
        # Patching cleanup_webhook to avoid network calls
        with patch.object(TelegramBot, '_cleanup_webhook_before_polling'), \
             patch('src.clients.telegram_bot.SessionManager'), \
             patch('src.clients.telegram_bot.VoiceAlertSystem'), \
             patch('src.clients.telegram_bot.FixedClockSystem'), \
             patch('src.clients.telegram_bot.SessionMenuHandler'):
            
            bot = TelegramBot(mock_config)
            bot.session_manager = MagicMock()
            bot.session_manager.check_trade_allowed.return_value = {'allowed': True, 'reason': ''}
            return bot

    def test_telegram_bot_initializes_modules(self, mock_config):
        """Test that TelegramBot initializes the new modules in its __init__"""
        with patch.object(TelegramBot, '_cleanup_webhook_before_polling'), \
             patch('src.clients.telegram_bot.SessionManager') as MockSessionManager, \
             patch('src.clients.telegram_bot.VoiceAlertSystem') as MockVoiceSystem, \
             patch('src.clients.telegram_bot.FixedClockSystem') as MockClockSystem, \
             patch('src.clients.telegram_bot.SessionMenuHandler') as MockMenuHandler:
            
            bot = TelegramBot(mock_config)
            
            # Verify initializations
            assert MockSessionManager.called
            assert MockVoiceSystem.called
            assert MockClockSystem.called
            assert MockMenuHandler.called
            
            # Verify clock start
            assert bot.clock_system.start.called
            
            # Verify command handlers
            assert "/session" in bot.command_handlers
            assert "/clock" in bot.command_handlers
            assert "/voice_test" in bot.command_handlers

    @pytest.mark.asyncio
    async def test_trading_engine_session_filter_passed(self, mock_config, mock_telegram_bot):
        """Test that TradingEngine proceeds when session check allows trade"""
        # Setup mocks
        mock_risk = MagicMock()
        mock_risk.can_trade.return_value = True
        
        mock_mt5 = MagicMock()
        
        # We need to construct TradingEngine with mocks
        # But modify check logic is inside execute_trades
        
        # We'll use a real TradingEngine but mock everything around it
        # We need to bypass __init__ complexity
        with patch('src.core.trading_engine.TradeDatabase'), \
             patch('src.core.trading_engine.PipCalculator'), \
             patch('src.core.trading_engine.TimeframeTrendManager'), \
             patch('src.core.trading_engine.ReEntryManager'), \
             patch('src.core.trading_engine.ProfitBookingManager'), \
             patch('src.core.trading_engine.DualOrderManager'), \
             patch('src.core.trading_engine.ProfitBookingReEntryManager'), \
             patch('src.core.trading_engine.AutonomousSystemManager'), \
             patch('src.core.trading_engine.PriceMonitorService'), \
             patch('src.core.trading_engine.ReversalExitHandler'), \
             patch('src.core.trading_engine.logger'):
             
            engine = TradingEngine(mock_config, mock_risk, mock_mt5, mock_telegram_bot, MagicMock())
            
            # Set up session manager allow
            mock_telegram_bot.session_manager.check_trade_allowed.return_value = {'allowed': True}
            
            # Create a dummy alert
            alert = MagicMock()
            alert.symbol = "EURUSD"
            alert.tf = "5m"
            alert.type = "entry"
            
            # To test if it proceeded past the check, we can check if it calls trend_manager
            # trend_manager is initialized in __init__, let's mock it on the instance
            engine.trend_manager = MagicMock()
            engine.trend_manager.check_logic_alignment.return_value = {'aligned': False} # Stop here
            
            # Run execute_trades
            await engine.execute_trades(alert)
            
            # Verify check_trade_allowed was called
            mock_telegram_bot.session_manager.check_trade_allowed.assert_called_with("EURUSD")
            
            # Verify it proceeded to trend check
            engine.trend_manager.check_logic_alignment.assert_called()

    @pytest.mark.asyncio
    async def test_trading_engine_session_filter_blocked(self, mock_config, mock_telegram_bot):
        """Test that TradingEngine stops when session check blocks trade"""
        mock_risk = MagicMock()
        mock_risk.can_trade.return_value = True
        mock_mt5 = MagicMock()
        
        with patch('src.core.trading_engine.TradeDatabase'), \
             patch('src.core.trading_engine.PipCalculator'), \
             patch('src.core.trading_engine.TimeframeTrendManager'), \
             patch('src.core.trading_engine.ReEntryManager'), \
             patch('src.core.trading_engine.ProfitBookingManager'), \
             patch('src.core.trading_engine.DualOrderManager'), \
             patch('src.core.trading_engine.ProfitBookingReEntryManager'), \
             patch('src.core.trading_engine.AutonomousSystemManager'), \
             patch('src.core.trading_engine.PriceMonitorService'), \
             patch('src.core.trading_engine.ReversalExitHandler'), \
             patch('src.core.trading_engine.logger'):
             
            engine = TradingEngine(mock_config, mock_risk, mock_mt5, mock_telegram_bot, MagicMock())
            
            # Set up session manager BLOCK
            mock_telegram_bot.session_manager.check_trade_allowed.return_value = {'allowed': False, 'reason': 'Session closed'}
            
            alert = MagicMock()
            alert.symbol = "EURUSD"
            alert.tf = "5m"
            alert.type = "entry"
            
            engine.trend_manager = MagicMock()
            
            # Run execute_trades
            await engine.execute_trades(alert)
            
            # Verify check_trade_allowed was called
            mock_telegram_bot.session_manager.check_trade_allowed.assert_called_with("EURUSD")
            
            # Verify it DID NOT proceed to trend check
            engine.trend_manager.check_logic_alignment.assert_not_called()
