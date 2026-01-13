"""
Voice Alert Service - V5 Hybrid Plugin Architecture

Service layer wrapper for VoiceAlertSystem. Provides clean API for plugins
to send voice alerts without direct dependency on the underlying implementation.

Part of Document 11: Voice Notification Implementation
Reference: DOCUMENTATION/VOICE_NOTIFICATION_SYSTEM_V3.md

Features:
- Trade announcement methods
- SL/TP hit alerts
- Session change alerts
- Priority-based routing
- Async execution
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class VoiceAlertService:
    """
    Service wrapper for VoiceAlertSystem.
    
    Provides a clean, plugin-friendly API for voice alerts.
    Wraps the underlying VoiceAlertSystem and WindowsAudioPlayer.
    
    Usage:
        voice_service = VoiceAlertService(voice_system)
        await voice_service.announce_trade("EURUSD", "BUY", 1.0850, 0.10)
    """
    
    def __init__(self, voice_system=None, windows_player=None):
        """
        Initialize Voice Alert Service.
        
        Args:
            voice_system: VoiceAlertSystem instance (optional)
            windows_player: WindowsAudioPlayer instance (optional)
        """
        self.voice_system = voice_system
        self.windows_player = windows_player
        self.logger = logging.getLogger(__name__)
        self.enabled = True
        self._stats = {
            "total_alerts": 0,
            "trade_alerts": 0,
            "sl_alerts": 0,
            "tp_alerts": 0,
            "session_alerts": 0,
            "failed_alerts": 0
        }
        
        self.logger.info("VoiceAlertService initialized")
    
    @property
    def is_available(self) -> bool:
        """Check if voice system is available."""
        return self.voice_system is not None or self.windows_player is not None
    
    async def announce_trade(
        self,
        symbol: str,
        direction: str,
        price: float,
        lot_size: float,
        order_type: str = "MARKET"
    ) -> bool:
        """
        Announce trade execution via voice.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            direction: Trade direction ("BUY" or "SELL")
            price: Entry price
            lot_size: Lot size
            order_type: Order type (default: "MARKET")
            
        Returns:
            bool: True if announcement successful
        """
        if not self.enabled:
            self.logger.debug("Voice alerts disabled, skipping trade announcement")
            return False
        
        message = f"Trade executed. {direction} {symbol} at {price:.5f}. Lot size {lot_size:.2f}."
        
        try:
            success = await self._send_alert(message, priority="HIGH")
            if success:
                self._stats["trade_alerts"] += 1
            return success
        except Exception as e:
            self.logger.error(f"Trade announcement failed: {e}")
            self._stats["failed_alerts"] += 1
            return False
    
    async def announce_sl_hit(
        self,
        symbol: str,
        loss_amount: float,
        direction: str = ""
    ) -> bool:
        """
        Announce stop loss hit via voice.
        
        Args:
            symbol: Trading symbol
            loss_amount: Loss amount in account currency
            direction: Original trade direction
            
        Returns:
            bool: True if announcement successful
        """
        if not self.enabled:
            return False
        
        message = f"Stop loss hit on {symbol}. Loss: {abs(loss_amount):.2f} dollars."
        
        try:
            success = await self._send_alert(message, priority="CRITICAL")
            if success:
                self._stats["sl_alerts"] += 1
            return success
        except Exception as e:
            self.logger.error(f"SL announcement failed: {e}")
            self._stats["failed_alerts"] += 1
            return False
    
    async def announce_tp_hit(
        self,
        symbol: str,
        profit_amount: float,
        direction: str = ""
    ) -> bool:
        """
        Announce take profit hit via voice.
        
        Args:
            symbol: Trading symbol
            profit_amount: Profit amount in account currency
            direction: Original trade direction
            
        Returns:
            bool: True if announcement successful
        """
        if not self.enabled:
            return False
        
        message = f"Take profit hit on {symbol}. Profit: {profit_amount:.2f} dollars."
        
        try:
            success = await self._send_alert(message, priority="HIGH")
            if success:
                self._stats["tp_alerts"] += 1
            return success
        except Exception as e:
            self.logger.error(f"TP announcement failed: {e}")
            self._stats["failed_alerts"] += 1
            return False
    
    async def announce_session_change(
        self,
        session_name: str,
        allowed_symbols: list = None
    ) -> bool:
        """
        Announce forex session change via voice.
        
        Args:
            session_name: Name of the new session (e.g., "London", "Asian")
            allowed_symbols: List of allowed symbols in this session
            
        Returns:
            bool: True if announcement successful
        """
        if not self.enabled:
            return False
        
        symbols_str = ", ".join(allowed_symbols[:3]) if allowed_symbols else "various pairs"
        message = f"{session_name} session started. Trading {symbols_str}."
        
        try:
            success = await self._send_alert(message, priority="MEDIUM")
            if success:
                self._stats["session_alerts"] += 1
            return success
        except Exception as e:
            self.logger.error(f"Session announcement failed: {e}")
            self._stats["failed_alerts"] += 1
            return False
    
    async def announce_reentry(
        self,
        symbol: str,
        direction: str,
        chain_level: int
    ) -> bool:
        """
        Announce re-entry trade via voice.
        
        Args:
            symbol: Trading symbol
            direction: Trade direction
            chain_level: Current chain level
            
        Returns:
            bool: True if announcement successful
        """
        if not self.enabled:
            return False
        
        message = f"Re-entry triggered. {direction} {symbol}. Chain level {chain_level}."
        
        try:
            return await self._send_alert(message, priority="HIGH")
        except Exception as e:
            self.logger.error(f"Re-entry announcement failed: {e}")
            return False
    
    async def announce_profit_chain_level(
        self,
        symbol: str,
        level: int,
        profit_booked: float
    ) -> bool:
        """
        Announce profit chain level advancement.
        
        Args:
            symbol: Trading symbol
            level: New chain level
            profit_booked: Profit booked at this level
            
        Returns:
            bool: True if announcement successful
        """
        if not self.enabled:
            return False
        
        message = f"Profit chain level {level} on {symbol}. Booked {profit_booked:.2f} dollars."
        
        try:
            return await self._send_alert(message, priority="MEDIUM")
        except Exception as e:
            self.logger.error(f"Profit chain announcement failed: {e}")
            return False
    
    async def send_alert(
        self,
        message: str,
        priority: str = "MEDIUM"
    ) -> bool:
        """
        Send a generic voice alert.
        
        Args:
            message: Alert message text
            priority: Alert priority (CRITICAL, HIGH, MEDIUM, LOW)
            
        Returns:
            bool: True if alert sent successfully
        """
        if not self.enabled:
            return False
        
        return await self._send_alert(message, priority)
    
    async def _send_alert(self, message: str, priority: str = "MEDIUM") -> bool:
        """
        Internal method to send alert via voice system.
        
        Args:
            message: Alert message
            priority: Alert priority
            
        Returns:
            bool: True if successful
        """
        self._stats["total_alerts"] += 1
        
        # Try VoiceAlertSystem first
        if self.voice_system:
            try:
                from src.modules.voice_alert_system import AlertPriority
                priority_enum = getattr(AlertPriority, priority.upper(), AlertPriority.MEDIUM)
                await self.voice_system.send_voice_alert(message, priority_enum)
                self.logger.info(f"Voice alert sent: {message[:50]}...")
                return True
            except Exception as e:
                self.logger.warning(f"VoiceAlertSystem failed: {e}")
        
        # Fallback to WindowsAudioPlayer
        if self.windows_player:
            try:
                success = self.windows_player.speak(message)
                if success:
                    self.logger.info(f"Windows audio played: {message[:50]}...")
                return success
            except Exception as e:
                self.logger.warning(f"WindowsAudioPlayer failed: {e}")
        
        # Log if no voice system available
        self.logger.warning(f"No voice system available. Message: {message}")
        return False
    
    def enable(self):
        """Enable voice alerts."""
        self.enabled = True
        self.logger.info("Voice alerts enabled")
    
    def disable(self):
        """Disable voice alerts."""
        self.enabled = False
        self.logger.info("Voice alerts disabled")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get voice alert statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        return {
            **self._stats,
            "enabled": self.enabled,
            "voice_system_available": self.voice_system is not None,
            "windows_player_available": self.windows_player is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self._stats = {
            "total_alerts": 0,
            "trade_alerts": 0,
            "sl_alerts": 0,
            "tp_alerts": 0,
            "session_alerts": 0,
            "failed_alerts": 0
        }
        self.logger.info("Voice alert statistics reset")


# Factory function for creating VoiceAlertService
def create_voice_alert_service(
    bot=None,
    chat_id: str = None,
    enable_windows_audio: bool = True
) -> VoiceAlertService:
    """
    Factory function to create VoiceAlertService with proper initialization.
    
    Args:
        bot: Telegram Bot instance
        chat_id: Telegram chat ID
        enable_windows_audio: Whether to enable Windows audio
        
    Returns:
        VoiceAlertService: Configured service instance
    """
    voice_system = None
    windows_player = None
    
    # Try to initialize VoiceAlertSystem
    if bot and chat_id:
        try:
            from src.modules.voice_alert_system import VoiceAlertSystem
            voice_system = VoiceAlertSystem(bot, chat_id)
            logger.info("VoiceAlertSystem initialized")
        except Exception as e:
            logger.warning(f"Could not initialize VoiceAlertSystem: {e}")
    
    # Try to initialize WindowsAudioPlayer
    if enable_windows_audio:
        try:
            from src.modules.windows_audio_player import WindowsAudioPlayer
            windows_player = WindowsAudioPlayer(rate=150, volume=1.0)
            logger.info("WindowsAudioPlayer initialized")
        except Exception as e:
            logger.warning(f"Could not initialize WindowsAudioPlayer: {e}")
    
    return VoiceAlertService(voice_system, windows_player)
