"""
Unit Tests for Fixed Clock System
Tests IST timezone handling, message formatting, and clock update logic.

Run tests with:
    pytest tests/test_fixed_clock_system.py -v
    pytest tests/test_fixed_clock_system.py::test_ist_timezone -v  # Single test
"""

import pytest
import asyncio
from datetime import datetime
import pytz
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from telegram import Bot, Message
from telegram.error import TelegramError

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from modules.fixed_clock_system import FixedClockSystem


class TestFixedClockSystem:
    """Test suite for FixedClockSystem class"""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock Telegram bot"""
        bot = AsyncMock(spec=Bot)
        bot.send_message = AsyncMock()
        bot.edit_message_text = AsyncMock()
        bot.pin_chat_message = AsyncMock()
        bot.unpin_chat_message = AsyncMock()
        bot.delete_message = AsyncMock()
        return bot
    
    @pytest.fixture
    def clock_system(self, mock_bot):
        """Create a FixedClockSystem instance with mock bot"""
        return FixedClockSystem(bot=mock_bot, chat_id="12345")
    
    def test_initialization(self, clock_system):
        """Test that clock system initializes correctly"""
        assert clock_system.chat_id == "12345"
        assert clock_system.timezone.zone == 'Asia/Kolkata'
        assert clock_system.message_id is None
        assert clock_system.is_running is False
    
    def test_ist_timezone(self, clock_system):
        """Test IST timezone conversion"""
        current_time = clock_system.get_current_ist_time()
        
        # Verify timezone is IST
        assert current_time.tzinfo.zone == 'Asia/Kolkata'
        
        # Verify time is reasonable (not in future, not too old)
        now_utc = datetime.now(pytz.UTC)
        time_diff = abs((current_time - now_utc).total_seconds())
        assert time_diff < 3600  # Within 1 hour (accounting for timezone differences)
    
    def test_message_formatting(self, clock_system):
        """Test clock message formatting"""
        with patch.object(clock_system, 'get_current_ist_time') as mock_time:
            # Mock a specific time: 2026-01-11 23:07:30 IST (Saturday)
            mock_time.return_value = datetime(
                2026, 1, 11, 23, 7, 30,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
            
            message = clock_system.format_clock_message()
            
            # Verify time format
            assert "23:07:30 IST" in message
            
            # Verify date format
            assert "11 Jan 2026" in message
            assert "Sunday" in message  # Jan 11, 2026 is Sunday
            
            # Verify emojis and structure
            assert "🕐" in message
            assert "📅" in message
            assert "**Current Time:**" in message
            assert "**Date:**" in message
    
    @pytest.mark.asyncio
    async def test_create_and_pin_message(self, clock_system, mock_bot):
        """Test creating and pinning a new clock message"""
        # Mock sent message
        mock_message = Mock(spec=Message)
        mock_message.message_id = 999
        mock_bot.send_message.return_value = mock_message
        
        await clock_system.update_clock_display()
        
        # Verify message was sent
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        assert call_args.kwargs['chat_id'] == "12345"
        assert call_args.kwargs['parse_mode'] == 'Markdown'
        
        # Verify message was pinned
        mock_bot.pin_chat_message.assert_called_once_with(
            chat_id="12345",
            message_id=999,
            disable_notification=True
        )
        
        # Verify message_id was stored
        assert clock_system.message_id == 999
    
    @pytest.mark.asyncio
    async def test_edit_existing_message(self, clock_system, mock_bot):
        """Test editing an existing clock message"""
        # Set existing message_id
        clock_system.message_id = 888
        
        await clock_system.update_clock_display()
        
        # Verify message was edited (not sent)
        mock_bot.edit_message_text.assert_called_once()
        mock_bot.send_message.assert_not_called()
        
        call_args = mock_bot.edit_message_text.call_args
        assert call_args.kwargs['chat_id'] == "12345"
        assert call_args.kwargs['message_id'] == 888
        assert call_args.kwargs['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_telegram_error_recovery(self, clock_system, mock_bot):
        """Test recovery when message edit fails"""
        clock_system.message_id = 777
        
        # Simulate "message not found" error
        mock_bot.edit_message_text.side_effect = TelegramError("Message to edit not found")
        
        await clock_system.update_clock_display()
        
        # Verify message_id was reset (will recreate on next update)
        assert clock_system.message_id is None  # Reset on error
    
    def test_date_change_detection(self, clock_system):
        """Test midnight crossing detection"""
        with patch.object(clock_system, 'get_current_ist_time') as mock_time:
            # First call: Jan 11
            mock_time.return_value = datetime(2026, 1, 11, 23, 59, 59, tzinfo=pytz.timezone('Asia/Kolkata'))
            result1 = clock_system._check_date_change()
            assert result1 is False  # First check, no change
            
            # Second call: Still Jan 11
            mock_time.return_value = datetime(2026, 1, 11, 23, 59, 58, tzinfo=pytz.timezone('Asia/Kolkata'))
            result2 = clock_system._check_date_change()
            assert result2 is False  # Same date, no change
            
            # Third call: Midnight crossed to Jan 12
            mock_time.return_value = datetime(2026, 1, 12, 0, 0, 1, tzinfo=pytz.timezone('Asia/Kolkata'))
            result3 = clock_system._check_date_change()
            assert result3 is True  # Date changed!
    
    @pytest.mark.asyncio
    async def test_stop_clock(self, clock_system):
        """Test stopping the clock loop"""
        clock_system.is_running = True
        
        clock_system.stop_clock()
        
        assert clock_system.is_running is False
    
    @pytest.mark.asyncio
    async def test_unpin_clock(self, clock_system, mock_bot):
        """Test unpinning clock message"""
        clock_system.message_id = 666
        
        await clock_system.unpin_clock()
        
        mock_bot.unpin_chat_message.assert_called_once_with(
            chat_id="12345",
            message_id=666
        )
    
    @pytest.mark.asyncio
    async def test_delete_clock(self, clock_system, mock_bot):
        """Test deleting clock message"""
        clock_system.message_id = 555
        
        await clock_system.delete_clock()
        
        mock_bot.delete_message.assert_called_once_with(
            chat_id="12345",
            message_id=555
        )
        
        # Verify message_id was cleared
        assert clock_system.message_id is None
    
    def test_get_status(self, clock_system):
        """Test status reporting"""
        clock_system.is_running = True
        clock_system.message_id = 444
        
        status = clock_system.get_status()
        
        assert status['is_running'] is True
        assert status['message_id'] == 444
        assert status['chat_id'] == "12345"
        assert status['timezone'] == 'Asia/Kolkata'
        assert 'current_time' in status
        assert 'last_date' in status
    
    @pytest.mark.asyncio
    async def test_clock_loop_single_iteration(self, clock_system, mock_bot):
        """Test one iteration of the clock loop"""
        # Mock send_message to avoid actual Telegram calls
        mock_message = Mock(spec=Message)
        mock_message.message_id = 111
        mock_bot.send_message.return_value = mock_message
        
        # Start clock in background
        loop_task = asyncio.create_task(clock_system.start_clock_loop())
        
        # Let it run for 2 seconds
        await asyncio.sleep(2)
        
        # Stop the clock
        clock_system.stop_clock()
        
        # Wait for loop to exit
        await asyncio.sleep(0.5)
        
        # Verify loop is no longer running
        assert clock_system.is_running is False
        
        # Verify message was created at least once
        assert mock_bot.send_message.call_count >= 1


class TestClockMessageFormat:
    """Test specific formatting scenarios"""
    
    @pytest.fixture
    def clock_system(self):
        mock_bot = AsyncMock(spec=Bot)
        return FixedClockSystem(bot=mock_bot, chat_id="test")
    
    @pytest.mark.parametrize("hour,minute,second,expected_time", [
        (0, 0, 0, "00:00:00 IST"),
        (12, 30, 45, "12:30:45 IST"),
        (23, 59, 59, "23:59:59 IST"),
        (9, 5, 1, "09:05:01 IST"),
    ])
    def test_time_format_variations(self, clock_system, hour, minute, second, expected_time):
        """Test various time formats"""
        with patch.object(clock_system, 'get_current_ist_time') as mock_time:
            mock_time.return_value = datetime(
                2026, 1, 11, hour, minute, second,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
            
            message = clock_system.format_clock_message()
            assert expected_time in message
    
    @pytest.mark.parametrize("month,day,dow,expected_date", [
        (1, 1, "Thursday", "01 Jan 2026 (Thursday)"),       # 2026-01-01 is Thursday
        (12, 31, "Thursday", "31 Dec 2026 (Thursday)"),     # 2026-12-31 is Thursday
        (7, 15, "Wednesday", "15 Jul 2026 (Wednesday)"),    # 2026-07-15 is Wednesday
    ])
    def test_date_format_variations(self, clock_system, month, day, dow, expected_date):
        """Test various date formats"""
        with patch.object(clock_system, 'get_current_ist_time') as mock_time:
            mock_time.return_value = datetime(
                2026, month, day, 12, 0, 0,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
            
            message = clock_system.format_clock_message()
            assert expected_date in message


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_fixed_clock_system.py -v
    pytest.main([__file__, "-v", "--tb=short"])
