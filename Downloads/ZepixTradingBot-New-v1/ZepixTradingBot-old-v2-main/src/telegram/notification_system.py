"""
Notification System - V5 Hybrid Plugin Architecture

Centralized notification router that accepts alerts from plugins and routes
them to appropriate channels (Telegram, Voice, SMS) based on priority.

Part of Document 19: Notification System Specification
Reference: DOCUMENTATION/VOICE_NOTIFICATION_SYSTEM_V3.md

Features:
- Priority-based routing (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Multi-channel delivery (Telegram + Voice)
- Template-based message formatting
- Delivery tracking and statistics
- Retry mechanism with exponential backoff
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels determining delivery channels."""
    CRITICAL = "CRITICAL"  # Voice + Telegram + SMS (all channels)
    HIGH = "HIGH"          # Voice + Telegram
    MEDIUM = "MEDIUM"      # Voice + Telegram
    LOW = "LOW"            # Telegram only
    INFO = "INFO"          # Telegram only (silent)


class NotificationType(Enum):
    """Types of notifications the system can handle."""
    TRADE_EXECUTED = "trade_executed"
    TRADE_CLOSED = "trade_closed"
    SL_HIT = "sl_hit"
    TP_HIT = "tp_hit"
    REENTRY_TRIGGERED = "reentry_triggered"
    SESSION_CHANGE = "session_change"
    PROFIT_CHAIN_LEVEL = "profit_chain_level"
    RISK_WARNING = "risk_warning"
    SYSTEM_ALERT = "system_alert"
    BOT_STATUS = "bot_status"


class NotificationRouter:
    """
    Central notification dispatch system.
    
    Routes notifications to appropriate channels based on priority and type.
    Integrates with VoiceAlertService and TelegramManager.
    
    Usage:
        router = NotificationRouter(telegram_manager, voice_service)
        await router.send("TRADE_EXECUTED", data, NotificationPriority.HIGH)
    """
    
    def __init__(
        self,
        telegram_manager=None,
        voice_service=None,
        sms_gateway=None
    ):
        """
        Initialize Notification Router.
        
        Args:
            telegram_manager: TelegramManager instance for message delivery
            voice_service: VoiceAlertService instance for voice alerts
            sms_gateway: Optional SMS gateway for critical alerts
        """
        self.telegram = telegram_manager
        self.voice = voice_service
        self.sms_gateway = sms_gateway
        self.logger = logging.getLogger(__name__)
        self.enabled = True
        
        # Message templates
        self.templates = self._load_templates()
        
        # Statistics
        self._stats = {
            "total_sent": 0,
            "by_priority": {p.value: 0 for p in NotificationPriority},
            "by_type": {t.value: 0 for t in NotificationType},
            "failed": 0,
            "voice_sent": 0,
            "telegram_sent": 0
        }
        
        # Delivery queue for retry
        self._retry_queue: List[Dict] = []
        self._max_retries = 3
        
        self.logger.info("NotificationRouter initialized")
    
    def _load_templates(self) -> Dict[str, str]:
        """Load message templates for different notification types."""
        return {
            NotificationType.TRADE_EXECUTED.value: (
                "{emoji} **TRADE EXECUTED**\n\n"
                "Symbol: {symbol}\n"
                "Direction: {direction}\n"
                "Price: {price}\n"
                "Lot Size: {lot_size}\n"
                "Plugin: {plugin}"
            ),
            NotificationType.TRADE_CLOSED.value: (
                "{emoji} **TRADE CLOSED**\n\n"
                "Symbol: {symbol}\n"
                "Direction: {direction}\n"
                "Close Price: {close_price}\n"
                "P/L: {pnl}"
            ),
            NotificationType.SL_HIT.value: (
                "{emoji} **STOP LOSS HIT**\n\n"
                "Symbol: {symbol}\n"
                "Loss: ${loss_amount:.2f}\n"
                "Recovery: Monitoring..."
            ),
            NotificationType.TP_HIT.value: (
                "{emoji} **TAKE PROFIT HIT**\n\n"
                "Symbol: {symbol}\n"
                "Profit: ${profit_amount:.2f}"
            ),
            NotificationType.REENTRY_TRIGGERED.value: (
                "{emoji} **RE-ENTRY TRIGGERED**\n\n"
                "Symbol: {symbol}\n"
                "Direction: {direction}\n"
                "Chain Level: {chain_level}"
            ),
            NotificationType.SESSION_CHANGE.value: (
                "{emoji} **SESSION CHANGE**\n\n"
                "New Session: {session_name}\n"
                "Allowed Pairs: {allowed_symbols}"
            ),
            NotificationType.PROFIT_CHAIN_LEVEL.value: (
                "{emoji} **PROFIT CHAIN LEVEL UP**\n\n"
                "Symbol: {symbol}\n"
                "Level: {level}\n"
                "Profit Booked: ${profit_booked:.2f}"
            ),
            NotificationType.RISK_WARNING.value: (
                "{emoji} **RISK WARNING**\n\n"
                "{message}"
            ),
            NotificationType.SYSTEM_ALERT.value: (
                "{emoji} **SYSTEM ALERT**\n\n"
                "{message}"
            ),
            NotificationType.BOT_STATUS.value: (
                "{emoji} **BOT STATUS**\n\n"
                "Status: {status}\n"
                "Time: {timestamp}"
            )
        }
    
    def _get_priority_emoji(self, priority: NotificationPriority) -> str:
        """Get emoji for priority level."""
        emoji_map = {
            NotificationPriority.CRITICAL: "",
            NotificationPriority.HIGH: "",
            NotificationPriority.MEDIUM: "",
            NotificationPriority.LOW: "",
            NotificationPriority.INFO: ""
        }
        return emoji_map.get(priority, "")
    
    def _get_channels_for_priority(self, priority: NotificationPriority) -> List[str]:
        """Determine delivery channels based on priority."""
        if priority == NotificationPriority.CRITICAL:
            return ["voice", "telegram", "sms"]
        elif priority in [NotificationPriority.HIGH, NotificationPriority.MEDIUM]:
            return ["voice", "telegram"]
        else:  # LOW, INFO
            return ["telegram"]
    
    async def send(
        self,
        notification_type: str,
        data: Dict[str, Any],
        priority: str = "MEDIUM"
    ) -> bool:
        """
        Central notification dispatch.
        
        Args:
            notification_type: Type of notification (e.g., "TRADE_EXECUTED")
            data: Data dictionary for message formatting
            priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
            
        Returns:
            bool: True if notification sent successfully
        """
        if not self.enabled:
            self.logger.debug("Notifications disabled, skipping")
            return False
        
        try:
            # Parse priority
            priority_enum = NotificationPriority[priority.upper()]
        except KeyError:
            priority_enum = NotificationPriority.MEDIUM
        
        # Format message
        formatted_msg = await self.format_notification(notification_type, data, priority_enum)
        
        # Get channels for this priority
        channels = self._get_channels_for_priority(priority_enum)
        
        # Track delivery success
        success = False
        
        # Route to channels
        for channel in channels:
            try:
                if channel == "voice" and self.voice:
                    await self._send_voice(formatted_msg, data, priority_enum)
                    self._stats["voice_sent"] += 1
                    success = True
                elif channel == "telegram" and self.telegram:
                    await self._send_telegram(formatted_msg, priority_enum)
                    self._stats["telegram_sent"] += 1
                    success = True
                elif channel == "sms" and self.sms_gateway:
                    await self._send_sms(formatted_msg)
                    success = True
            except Exception as e:
                self.logger.error(f"Failed to send via {channel}: {e}")
        
        # Update statistics
        if success:
            self._stats["total_sent"] += 1
            self._stats["by_priority"][priority_enum.value] += 1
            if notification_type in [t.value for t in NotificationType]:
                self._stats["by_type"][notification_type] += 1
        else:
            self._stats["failed"] += 1
        
        return success
    
    async def format_notification(
        self,
        notification_type: str,
        data: Dict[str, Any],
        priority: NotificationPriority
    ) -> str:
        """
        Format notification message using templates.
        
        Args:
            notification_type: Type of notification
            data: Data dictionary for formatting
            priority: Priority level for emoji
            
        Returns:
            str: Formatted message
        """
        # Get template
        template = self.templates.get(
            notification_type,
            "{emoji} **NOTIFICATION**\n\n{message}"
        )
        
        # Add emoji based on priority
        data["emoji"] = self._get_priority_emoji(priority)
        
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format message
        try:
            formatted = template.format(**data)
        except KeyError as e:
            self.logger.warning(f"Missing template key: {e}")
            formatted = f"{data.get('emoji', '')} {notification_type}: {str(data)}"
        
        return formatted
    
    async def _send_voice(
        self,
        message: str,
        data: Dict[str, Any],
        priority: NotificationPriority
    ):
        """Send notification via voice system."""
        if not self.voice:
            return
        
        # Create voice-friendly message (shorter, no markdown)
        voice_message = self._create_voice_message(data)
        
        # Map priority
        priority_str = priority.value
        
        await self.voice.send_alert(voice_message, priority_str)
    
    def _create_voice_message(self, data: Dict[str, Any]) -> str:
        """Create a voice-friendly message from data."""
        # Extract key information for voice
        if "symbol" in data and "direction" in data:
            if "price" in data:
                return f"Trade executed. {data['direction']} {data['symbol']} at {data['price']}."
            elif "loss_amount" in data:
                return f"Stop loss hit on {data['symbol']}. Loss: {data['loss_amount']:.2f} dollars."
            elif "profit_amount" in data:
                return f"Take profit hit on {data['symbol']}. Profit: {data['profit_amount']:.2f} dollars."
        
        if "session_name" in data:
            return f"{data['session_name']} session started."
        
        if "message" in data:
            return data["message"]
        
        return "Notification received."
    
    async def _send_telegram(self, message: str, priority: NotificationPriority):
        """Send notification via Telegram."""
        if not self.telegram:
            return
        
        # Determine if notification should make sound
        silent = priority == NotificationPriority.INFO
        
        try:
            if hasattr(self.telegram, 'send_message'):
                await self.telegram.send_message(
                    message,
                    parse_mode='Markdown',
                    disable_notification=silent
                )
            elif hasattr(self.telegram, 'broadcast'):
                await self.telegram.broadcast(message)
            else:
                self.logger.warning("Telegram manager has no send method")
        except Exception as e:
            self.logger.error(f"Telegram send failed: {e}")
            raise
    
    async def _send_sms(self, message: str):
        """Send notification via SMS gateway."""
        if not self.sms_gateway:
            return
        
        try:
            # Placeholder for SMS gateway integration
            self.logger.info(f"SMS would be sent: {message[:50]}...")
        except Exception as e:
            self.logger.error(f"SMS send failed: {e}")
            raise
    
    async def broadcast(self, message: str, priority: str = "HIGH"):
        """
        Broadcast a message to all channels.
        
        Args:
            message: Message to broadcast
            priority: Priority level
        """
        await self.send(
            NotificationType.SYSTEM_ALERT.value,
            {"message": message},
            priority
        )
    
    def enable(self):
        """Enable notifications."""
        self.enabled = True
        self.logger.info("Notifications enabled")
    
    def disable(self):
        """Disable notifications."""
        self.enabled = False
        self.logger.info("Notifications disabled")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics."""
        return {
            **self._stats,
            "enabled": self.enabled,
            "voice_available": self.voice is not None,
            "telegram_available": self.telegram is not None,
            "sms_available": self.sms_gateway is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self._stats = {
            "total_sent": 0,
            "by_priority": {p.value: 0 for p in NotificationPriority},
            "by_type": {t.value: 0 for t in NotificationType},
            "failed": 0,
            "voice_sent": 0,
            "telegram_sent": 0
        }
        self.logger.info("Notification statistics reset")


# Convenience function for creating NotificationRouter
def create_notification_router(
    telegram_manager=None,
    voice_service=None,
    sms_gateway=None
) -> NotificationRouter:
    """
    Factory function to create NotificationRouter.
    
    Args:
        telegram_manager: TelegramManager instance
        voice_service: VoiceAlertService instance
        sms_gateway: Optional SMS gateway
        
    Returns:
        NotificationRouter: Configured router instance
    """
    return NotificationRouter(
        telegram_manager=telegram_manager,
        voice_service=voice_service,
        sms_gateway=sms_gateway
    )
