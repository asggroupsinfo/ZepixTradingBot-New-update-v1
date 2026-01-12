"""
Voice Alert System V3.0 (Final)
Dual-channel notification: Windows Speaker TTS + Text Notifications

Features:
- Windows Speaker TTS via pyttsx3 (offline, immediate laptop audio)
- Telegram text notifications (phone notification sound)
- Priority levels: CRITICAL, HIGH, MEDIUM, LOW
- Multi-channel delivery: Windows Audio → Text → SMS (fallback chain)
- Async alert queue processing
- Retry mechanism with exponential backoff (max 3 retries)
- Clean Telegram chat (NO voice files)
- Works even when Telegram closed (Windows audio)

Usage:
    alert_system = VoiceAlertSystem(bot, chat_id)
    await alert_system.send_voice_alert("Trade opened EURUSD", AlertPriority.HIGH)
    # Result: Windows audio + Text notification

Author: Zepix Trading Bot Development Team
Version: 3.0 (Final - Clean Chat)
Updated: 2026-01-12
"""

import asyncio
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
from enum import Enum
import logging
import uuid
import concurrent.futures
from telegram import Bot
from telegram.error import TelegramError

# V2.0: Import Windows Audio Player
from src.modules.windows_audio_player import WindowsAudioPlayer


class AlertPriority(Enum):
    """Alert priority levels determining delivery channels"""
    CRITICAL = "CRITICAL"  # Windows Audio + Text + SMS
    HIGH = "HIGH"          # Windows Audio + Text
    MEDIUM = "MEDIUM"      # Windows Audio + Text
    LOW = "LOW"            # Text only


class AlertChannel(Enum):
    """Available notification channels (V3.0: Windows audio + Text only)"""
    WINDOWS_AUDIO = "windows_audio"  # Direct speaker TTS
    TEXT = "text"
    SMS = "sms"


class VoiceAlertSystem:
    """
    Manages voice alert delivery with retry and multi-channel fallback.
    
    Processes alerts in a queue, generates TTS voice messages,
    and handles delivery failures with automatic retries.
    """
    
    def __init__(self, bot: Bot, chat_id: str, sms_gateway=None):
        """
        Initialize Voice Alert System V2.0 with Windows audio support.
        
        Args:
            bot: Telegram Bot instance
            chat_id: Target Telegram chat ID
            sms_gateway: Optional SMS gateway for critical alerts
        """
        self.bot = bot
        self.chat_id = chat_id
        self.sms_gateway = sms_gateway
        self.alert_queue: List[Dict] = []
        self.is_processing = False
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.logger = logging.getLogger(__name__)
        
        # V2.0: Initialize Windows Audio Player
        try:
            self.windows_player = WindowsAudioPlayer(rate=150, volume=1.0)
            self.logger.info("Windows audio player initialized successfully")
        except Exception as e:
            self.logger.error(f"Windows audio player initialization failed: {e}")
            self.windows_player = None
        
        self.logger.info("VoiceAlertSystem V2.0 initialized")
    
    async def send_voice_alert(self, message: str, priority: AlertPriority = AlertPriority.MEDIUM):
        """
        Queue a voice alert for delivery.
        
        Args:
            message: Alert message text
            priority: Alert priority level
        """
        alert_id = str(uuid.uuid4())
        
        alert = {
            'id': alert_id,
            'priority': priority.value,
            'message': message,
            'timestamp': datetime.now(self.timezone).isoformat(),
            'retry_count': 0,
            'max_retries': 3,
            'channels': self._get_channels_for_priority(priority),
            'status': 'PENDING'
        }
        
        self.alert_queue.append(alert)
        self.logger.info(f"Alert queued: {alert_id} | {priority.value} | {message[:50]}...")
        
        # Start processing if not already running
        if not self.is_processing:
            asyncio.create_task(self.process_alert_queue())
    
    def _get_channels_for_priority(self, priority: AlertPriority) -> List[str]:
        """
        Determine delivery channels based on priority.
        
        V3.0 Final Update: 
        - Windows audio for immediate laptop alerts (all priorities)
        - Text notifications for phone (all priorities)
        - NO voice files (clean chat)
        
        Args:
            priority: Alert priority
            
        Returns:
            List of channel names to attempt
        """
        if priority == AlertPriority.CRITICAL:
            return [AlertChannel.WINDOWS_AUDIO.value, AlertChannel.TEXT.value, AlertChannel.SMS.value]
        elif priority == AlertPriority.HIGH:
            return [AlertChannel.WINDOWS_AUDIO.value, AlertChannel.TEXT.value]
        elif priority == AlertPriority.MEDIUM:
            return [AlertChannel.WINDOWS_AUDIO.value, AlertChannel.TEXT.value]
        else:  # LOW
            # V3.1: Enable Windows Audio for LOW priority too (Bot Start/End)
            return [AlertChannel.WINDOWS_AUDIO.value, AlertChannel.TEXT.value]
    
    
    async def send_via_windows_speaker(self, message: str) -> bool:
        """
        Play audio on Windows laptop speakers via TTS.
        
        V2.0: Uses pyttsx3 for direct speaker output.
        Runs in thread to avoid blocking async event loop.
        
        Args:
            message: Alert message text
            
        Returns:
            True if successful, False otherwise
        """
        if not self.windows_player:
            self.logger.warning("Windows audio player not available, skipping")
            return False
        
        try:
            # Run TTS in a thread to avoid blocking async event loop
            loop = asyncio.get_event_loop()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = loop.run_in_executor(
                    executor,
                    self.windows_player.speak,
                    message
                )
                success = await asyncio.wait_for(future, timeout=10.0)
            
            if success:
                self.logger.info("Windows speaker audio played successfully")
            else:
                self.logger.warning("Windows speaker audio playback failed")
            
            return success
        
        except asyncio.TimeoutError:
            self.logger.error("Windows speaker audio timeout (>10s)")
            return False
        except Exception as e:
            self.logger.error(f"Windows speaker audio error: {e}")
            return False
    
    async def send_via_telegram_voice(self, message: str) -> bool:
        """
        Send voice message via Telegram for phone notification.
        
        V2.5: Uses pyttsx3 to generate voice file, then sends to Telegram.
        Ensures phone receives notification sound + playable audio.
        
        Args:
            message: Alert message text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import tempfile
            import os
            
            # Generate voice file using pyttsx3
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                voice_file_path = tmp_file.name
            
            # Generate TTS audio
            engine = None
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)
                engine.save_to_file(message, voice_file_path)
                engine.runAndWait()
                
                self.logger.info(f"Voice file generated: {voice_file_path}")
            except Exception as e:
                self.logger.error(f"TTS generation failed: {e}")
                return False
            finally:
                if engine:
                    try:
                        engine.stop()
                    except:
                        pass
            
            # Send voice message to Telegram
            try:
                with open(voice_file_path, 'rb') as audio_file:
                    self.bot.send_voice(
                        chat_id=self.chat_id,
                        voice=audio_file,
                        caption=f"🔊 Voice Alert: {message[:50]}{'...' if len(message) > 50 else ''}"
                    )
                
                self.logger.info("Voice message sent successfully to Telegram")
                return True
            
            except Exception as e:
                self.logger.error(f"Telegram voice send failed: {e}")
                return False
            
            finally:
                # Cleanup temporary file
                try:
                    if os.path.exists(voice_file_path):
                        os.remove(voice_file_path)
                except:
                    pass
        
        except Exception as e:
            self.logger.error(f"Voice message error: {e}")
            return False
    
    async def send_via_telegram_text(self, message: str, priority: AlertPriority) -> bool:
        """
        Send text message with notification sound via Telegram.
        
        V2.0 Update: Ensures notifications are enabled for phone sound.
        
        Args:
            message: Message text
            priority: Alert priority for emoji selection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Priority emoji mapping
            emoji_map = {
                'CRITICAL': '🚨',
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            
            emoji = emoji_map.get(priority.value, '📢')
            formatted_message = f"{emoji} **{priority.value} ALERT**\n\n{message}"
            
            # V2.0: IMPORTANT - disable_notification=False ensures phone makes sound
            self.bot.send_message(
                chat_id=self.chat_id,
                text=formatted_message,
                parse_mode='Markdown',
                disable_notification=False  # Ensures notification sound on phone
            )
            
            self.logger.info("Text notification sent successfully")
            return True
        
        except TelegramError as e:
            self.logger.error(f"Telegram text send failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Text send error: {e}")
            return False
    
    async def send_via_sms(self, message: str) -> bool:
        """
        Send SMS via gateway (fallback for critical alerts).
        
        Args:
            message: Message text
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sms_gateway:
            self.logger.warning("SMS gateway not configured")
            return False
        
        try:
            # Placeholder for SMS gateway integration
            # Example: Twilio, AWS SNS, etc.
            # result = await self.sms_gateway.send(message)
            self.logger.info("SMS sent successfully (placeholder)")
            return True
        
        except Exception as e:
            self.logger.error(f"SMS send failed: {e}")
            return False
    
    async def process_alert_queue(self):
        """Process alerts in the queue with retry logic."""
        self.is_processing = True
        self.logger.info("Starting alert queue processing...")
        
        while self.alert_queue:
            alert = self.alert_queue[0]
            
            try:
                success = await self._deliver_alert(alert)
                
                if success:
                    alert['status'] = 'SENT'
                    self.alert_queue.pop(0)
                    self.logger.info(f"Alert delivered: {alert['id']}")
                else:
                    alert['retry_count'] += 1
                    
                    if alert['retry_count'] >= alert['max_retries']:
                        alert['status'] = 'FAILED'
                        self.alert_queue.pop(0)
                        self.logger.error(f"Alert failed after {alert['max_retries']} retries: {alert['id']}")
                    else:
                        # Exponential backoff
                        wait_time = 10 * (2 ** alert['retry_count'])
                        self.logger.warning(f"Retrying alert {alert['id']} in {wait_time}s...")
                        await asyncio.sleep(wait_time)
            
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")
                await asyncio.sleep(5)
        
        self.is_processing = False
        self.logger.info("Alert queue processing complete")
    
    async def _deliver_alert(self, alert: Dict) -> bool:
        """
        Attempt to deliver an alert through available channels.
        
        V3.0 Final: 
        - Windows audio for immediate laptop alerts
        - Text notifications for phone (clean chat)
        - NO voice files
        
        Args:
            alert: Alert dictionary
            
        Returns:
            True if delivered via any channel, False otherwise
        """
        message = alert['message']
        priority = AlertPriority(alert['priority'])
        channels = alert['channels']
        
        delivery_success = False
        
        for channel in channels:
            try:
                if channel == AlertChannel.WINDOWS_AUDIO.value:
                    success = await self.send_via_windows_speaker(message)
                elif channel == AlertChannel.TEXT.value:
                    success = await self.send_via_telegram_text(message, priority)
                elif channel == AlertChannel.SMS.value:
                    success = await self.send_via_sms(message)
                else:
                    self.logger.warning(f"Unknown channel: {channel}")
                    continue
                
                if success:
                    delivery_success = True
                    self.logger.info(f"Alert delivered via {channel}")
            
            except Exception as e:
                self.logger.error(f"Channel {channel} delivery failed: {e}")
                continue
        
        return delivery_success
    
    def get_queue_status(self) -> Dict:
        """
        Get current queue status.
        
        Returns:
            Dictionary with queue statistics
        """
        return {
            'total_queued': len(self.alert_queue),
            'is_processing': self.is_processing,
            'pending': [a for a in self.alert_queue if a['status'] == 'PENDING'],
            'retrying': [a for a in self.alert_queue if a['retry_count'] > 0]
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("VoiceAlertSystem module loaded successfully")
    print("Priority levels:", [p.value for p in AlertPriority])
    print("Channels:", [c.value for c in AlertChannel])
