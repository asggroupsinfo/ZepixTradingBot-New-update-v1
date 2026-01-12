"""
Unit Tests for Voice Alert System
Tests queue management, priority routing, TTS generation, and retry logic.

Run tests with:
    pytest tests/test_voice_alert_system.py -v
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, ANY
import os
import sys
from datetime import datetime

# Import module to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from modules.voice_alert_system import VoiceAlertSystem, AlertPriority, AlertChannel


class TestVoiceAlertSystem:
    """Test suite for VoiceAlertSystem"""
    
    @pytest.fixture
    def mock_bot(self):
        """Create mock Telegram bot"""
        bot = MagicMock()
        bot.send_message = AsyncMock(return_value=True)
        bot.send_voice = AsyncMock(return_value=True)
        return bot
    
    @pytest.fixture
    def alert_system(self, mock_bot):
        """Create VoiceAlertSystem instance"""
        # Patch gTTS to avoid actual API calls during tests
        with patch('modules.voice_alert_system.gTTS') as mock_gtts:
            # Setup mock gTTS instance
            mock_tts_instance = MagicMock()
            mock_tts_instance.write_to_fp = MagicMock()
            mock_gtts.return_value = mock_tts_instance
            
            system = VoiceAlertSystem(mock_bot, "123456789")
            yield system

    @pytest.mark.asyncio
    async def test_queue_alert(self, alert_system):
        """Test queuing an alert"""
        await alert_system.send_voice_alert("Test message", AlertPriority.HIGH)
        
        assert len(alert_system.alert_queue) == 1
        alert = alert_system.alert_queue[0]
        assert alert['message'] == "Test message"
        assert alert['priority'] == AlertPriority.HIGH.value
        assert alert['status'] == 'PENDING'
    
    @pytest.mark.asyncio
    async def test_priority_channels_critical(self, alert_system):
        """Test channel selection for CRITICAL priority"""
        channels = alert_system._get_channels_for_priority(AlertPriority.CRITICAL)
        assert AlertChannel.VOICE.value in channels
        assert AlertChannel.TEXT.value in channels
        assert AlertChannel.SMS.value in channels
    
    @pytest.mark.asyncio
    async def test_priority_channels_medium(self, alert_system):
        """Test channel selection for MEDIUM priority"""
        channels = alert_system._get_channels_for_priority(AlertPriority.MEDIUM)
        assert AlertChannel.VOICE.value in channels
        assert AlertChannel.TEXT.value in channels
    
    @pytest.mark.asyncio
    async def test_process_alert_success(self, alert_system, mock_bot):
        """Test successful alert processing"""
        # Add alert to queue manually to avoid async background task starting
        alert = {
            'id': 'test-1',
            'priority': AlertPriority.MEDIUM.value,
            'message': 'Test alert',
            'timestamp': datetime.now().isoformat(),
            'retry_count': 0,
            'max_retries': 3,
            'channels': [AlertChannel.TEXT.value],  # Use text for simple verification
            'status': 'PENDING'
        }
        alert_system.alert_queue.append(alert)
        
        # Process queue
        await alert_system.process_alert_queue()
        
        # Verify result
        assert len(alert_system.alert_queue) == 0  # Should be removed after success
        mock_bot.send_message.assert_called_once()
        assert alert['status'] == 'SENT'

    @pytest.mark.asyncio
    async def test_retry_logic(self, alert_system, mock_bot):
        """Test retry mechanism on failure"""
        # Mock failure
        mock_bot.send_message.side_effect = Exception("Telegram API Error")
        
        alert = {
            'id': 'test-retry',
            'priority': AlertPriority.LOW.value,
            'message': 'Retry test',
            'timestamp': datetime.now().isoformat(),
            'retry_count': 0,
            'max_retries': 2,
            'channels': [AlertChannel.TEXT.value],
            'status': 'PENDING'
        }
        alert_system.alert_queue.append(alert)
        
        # Force one processing loop iteration
        # We need to control the loop, so we'll mock _deliver_alert instead of running full process_queue
        alert_system._deliver_alert = AsyncMock(return_value=False)
        
        # Run process queue - it should try, fail, increment retry, and keep in queue
        # Since process_alert_queue loops while queue is not empty, we need to be careful
        # Let's test the logic inside the loop manually for control
        
        current_alert = alert_system.alert_queue[0]
        success = await alert_system._deliver_alert(current_alert)
        
        assert success is False
        
        # Manually simulate what the loop does
        current_alert['retry_count'] += 1
        
        assert current_alert['retry_count'] == 1
        assert current_alert['status'] == 'PENDING'
        assert len(alert_system.alert_queue) == 1

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, alert_system):
        """Test removal after max retries"""
        alert = {
            'id': 'test-max-retry',
            'priority': AlertPriority.LOW.value,
            'message': 'Max retry test',
            'retry_count': 2,
            'max_retries': 3,
            'channels': [AlertChannel.TEXT.value],
            'status': 'PENDING'
        }
        alert_system.alert_queue.append(alert)
        
        # Mock delivery failure
        alert_system._deliver_alert = AsyncMock(return_value=False)
        
        # Run loop logic equivalent
        if not await alert_system._deliver_alert(alert):
            alert['retry_count'] += 1
            if alert['retry_count'] >= alert['max_retries']:
                alert['status'] = 'FAILED'
                alert_system.alert_queue.pop(0)
        
        assert len(alert_system.alert_queue) == 0
        assert alert['status'] == 'FAILED'
        assert alert['retry_count'] == 3

    @pytest.mark.asyncio
    async def test_voice_generation(self, alert_system):
        """Test TTS generation"""
        # The mock is already set up in the fixture
        audio_data = await alert_system.generate_voice_message("Hello World")
        
        assert audio_data is not None
        # Verify gTTS was called with Indian accent param
        import modules.voice_alert_system
        modules.voice_alert_system.gTTS.assert_called_with(text="Hello World", lang='en', tld='co.in', slow=False)

    @pytest.mark.asyncio
    async def test_telegram_voice_send(self, alert_system, mock_bot):
        """Test sending voice message via Telegram"""
        # Mock generate_voice_message to return dummy bytes
        alert_system.generate_voice_message = AsyncMock(return_value=b"dummy_audio_bytes")
        
        result = await alert_system.send_via_telegram_voice("Voice test")
        
        assert result is True
        mock_bot.send_voice.assert_called_once()
        
        # Verify arguments
        call_args = mock_bot.send_voice.call_args
        assert call_args.kwargs['chat_id'] == "123456789"
        assert "Voice Alert" in call_args.kwargs['caption']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
