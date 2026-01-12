"""
Voice Alerts - Voice Alert Generation and Delivery

Document 19: Notification System Specification
Generates and delivers voice alerts for critical notifications.

Features:
- Voice text generation
- Language support
- Speed and volume control
- Trigger configuration
- Voice alert queue
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import logging
import asyncio


class VoiceLanguage(Enum):
    """Supported voice languages"""
    ENGLISH = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"


class VoiceSpeed(Enum):
    """Voice speed options"""
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


class VoiceTrigger(Enum):
    """Voice alert triggers"""
    ENTRY = "entry"
    EXIT_PROFIT = "exit_profit"
    EXIT_LOSS = "exit_loss"
    TP_HIT = "tp_hit"
    SL_HIT = "sl_hit"
    EMERGENCY = "emergency"
    DAILY_SUMMARY = "daily_summary"
    RISK_ALERT = "risk_alert"
    MT5_DISCONNECT = "mt5_disconnect"
    DAILY_LOSS_LIMIT = "daily_loss_limit"


@dataclass
class VoiceAlertConfig:
    """Voice alert configuration"""
    enabled: bool = True
    language: VoiceLanguage = VoiceLanguage.ENGLISH
    speed: VoiceSpeed = VoiceSpeed.NORMAL
    volume: int = 100  # 0-100
    
    # Trigger settings
    triggers: Dict[VoiceTrigger, bool] = field(default_factory=lambda: {
        VoiceTrigger.ENTRY: True,
        VoiceTrigger.EXIT_PROFIT: True,
        VoiceTrigger.EXIT_LOSS: True,
        VoiceTrigger.TP_HIT: True,
        VoiceTrigger.SL_HIT: True,
        VoiceTrigger.EMERGENCY: True,
        VoiceTrigger.DAILY_SUMMARY: False,
        VoiceTrigger.RISK_ALERT: True,
        VoiceTrigger.MT5_DISCONNECT: True,
        VoiceTrigger.DAILY_LOSS_LIMIT: True,
    })
    
    # Advanced settings
    max_text_length: int = 200  # Max characters for voice text
    queue_enabled: bool = True
    max_queue_size: int = 10
    cooldown_seconds: float = 2.0  # Min time between alerts
    
    def is_trigger_enabled(self, trigger: VoiceTrigger) -> bool:
        """Check if trigger is enabled"""
        return self.enabled and self.triggers.get(trigger, False)
    
    def enable_trigger(self, trigger: VoiceTrigger) -> None:
        """Enable a trigger"""
        self.triggers[trigger] = True
    
    def disable_trigger(self, trigger: VoiceTrigger) -> None:
        """Disable a trigger"""
        self.triggers[trigger] = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enabled": self.enabled,
            "language": self.language.value,
            "speed": self.speed.value,
            "volume": self.volume,
            "triggers": {t.value: v for t, v in self.triggers.items()},
            "max_text_length": self.max_text_length,
            "queue_enabled": self.queue_enabled,
            "max_queue_size": self.max_queue_size,
            "cooldown_seconds": self.cooldown_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceAlertConfig':
        """Create from dictionary"""
        triggers = {}
        for trigger in VoiceTrigger:
            triggers[trigger] = data.get("triggers", {}).get(trigger.value, True)
        
        return cls(
            enabled=data.get("enabled", True),
            language=VoiceLanguage(data.get("language", "en")),
            speed=VoiceSpeed(data.get("speed", "normal")),
            volume=data.get("volume", 100),
            triggers=triggers,
            max_text_length=data.get("max_text_length", 200),
            queue_enabled=data.get("queue_enabled", True),
            max_queue_size=data.get("max_queue_size", 10),
            cooldown_seconds=data.get("cooldown_seconds", 2.0)
        )


@dataclass
class VoiceAlert:
    """Voice alert data"""
    alert_id: str
    text: str
    trigger: VoiceTrigger
    language: VoiceLanguage
    speed: VoiceSpeed
    volume: int
    created_at: datetime = field(default_factory=datetime.now)
    played_at: Optional[datetime] = None
    success: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "text": self.text,
            "trigger": self.trigger.value,
            "language": self.language.value,
            "speed": self.speed.value,
            "volume": self.volume,
            "created_at": self.created_at.isoformat(),
            "played_at": self.played_at.isoformat() if self.played_at else None,
            "success": self.success,
            "error": self.error
        }


class VoiceTextGenerator:
    """
    Voice Text Generator
    
    Generates short, clear voice text for different notification types.
    """
    
    def __init__(self, language: VoiceLanguage = VoiceLanguage.ENGLISH):
        self.language = language
        self._templates: Dict[str, Dict[str, str]] = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load voice text templates for all languages"""
        return {
            "en": {
                "entry": "New {direction} trade on {symbol} at {entry_price}. Signal: {signal_type}.",
                "exit_profit": "{direction} trade closed with profit of {profit} dollars.",
                "exit_loss": "{direction} trade closed with loss of {loss} dollars.",
                "tp_hit": "Take profit {tp_level} hit. Profit: {profit} dollars.",
                "sl_hit": "Stop loss hit. Loss: {loss} dollars.",
                "emergency": "Emergency alert. {message}",
                "daily_summary": "Daily summary. {trades} trades. Net profit: {net_pnl} dollars.",
                "risk_alert": "Risk alert. {message}",
                "mt5_disconnect": "Warning. MT5 connection lost. Please check your connection.",
                "daily_loss_limit": "Daily loss limit reached. Trading has been paused.",
                "partial_profit": "Partial profit booked. {profit} dollars secured.",
                "breakeven": "Stop loss moved to breakeven.",
                "bot_started": "Trading bot started successfully.",
                "bot_stopped": "Trading bot stopped. Reason: {reason}.",
            },
            "hi": {
                "entry": "Naya {direction} trade {symbol} par {entry_price} par. Signal: {signal_type}.",
                "exit_profit": "{direction} trade {profit} dollar profit ke saath band hua.",
                "exit_loss": "{direction} trade {loss} dollar loss ke saath band hua.",
                "tp_hit": "Take profit {tp_level} hit. Profit: {profit} dollar.",
                "sl_hit": "Stop loss hit. Loss: {loss} dollar.",
                "emergency": "Emergency alert. {message}",
                "daily_summary": "Daily summary. {trades} trades. Net profit: {net_pnl} dollar.",
                "risk_alert": "Risk alert. {message}",
                "mt5_disconnect": "Warning. MT5 connection lost.",
                "daily_loss_limit": "Daily loss limit reached. Trading paused.",
            }
        }
    
    def generate(
        self,
        notification_type: str,
        data: Dict[str, Any],
        language: Optional[VoiceLanguage] = None
    ) -> str:
        """
        Generate voice text for notification
        
        Args:
            notification_type: Type of notification
            data: Notification data
            language: Override language
            
        Returns:
            Voice text string
        """
        lang = (language or self.language).value
        templates = self._templates.get(lang, self._templates["en"])
        
        template = templates.get(notification_type)
        if not template:
            # Fallback to generic
            return f"Notification: {notification_type}"
        
        # Prepare data with defaults
        formatted_data = self._prepare_data(notification_type, data)
        
        try:
            return template.format(**formatted_data)
        except KeyError:
            return template
    
    def _prepare_data(self, notification_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data with defaults for template"""
        result = data.copy()
        
        # Add common defaults
        defaults = {
            "direction": data.get("direction", "unknown"),
            "symbol": data.get("symbol", "unknown"),
            "entry_price": data.get("entry_price", 0),
            "signal_type": data.get("signal_type", "unknown"),
            "profit": abs(data.get("profit", 0)),
            "loss": abs(data.get("profit", 0)),
            "tp_level": data.get("tp_level", 1),
            "message": data.get("message", ""),
            "trades": data.get("total_trades", 0),
            "net_pnl": data.get("net_pnl", 0),
            "reason": data.get("reason", "unknown"),
        }
        
        for key, value in defaults.items():
            if key not in result:
                result[key] = value
        
        return result
    
    def set_language(self, language: VoiceLanguage) -> None:
        """Set default language"""
        self.language = language
    
    def add_template(self, notification_type: str, template: str, language: str = "en") -> None:
        """Add or update template"""
        if language not in self._templates:
            self._templates[language] = {}
        self._templates[language][notification_type] = template


class VoiceAlertSystem:
    """
    Voice Alert System
    
    Manages voice alert generation, queuing, and delivery.
    """
    
    def __init__(self, config: Optional[VoiceAlertConfig] = None):
        self.config = config or VoiceAlertConfig()
        self.text_generator = VoiceTextGenerator(self.config.language)
        self.logger = logging.getLogger(__name__)
        
        # Alert queue
        self.queue: List[VoiceAlert] = []
        self.history: List[VoiceAlert] = []
        self.max_history_size = 100
        
        # Callbacks
        self._play_callback: Optional[Callable] = None
        self._alert_counter = 0
        
        # Cooldown tracking
        self._last_alert_time: Optional[datetime] = None
        
        # Statistics
        self.stats = {
            "total_generated": 0,
            "total_played": 0,
            "total_failed": 0,
            "by_trigger": {}
        }
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        self._alert_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"VOICE-{timestamp}-{self._alert_counter:04d}"
    
    def set_play_callback(self, callback: Callable) -> None:
        """Set callback for playing voice alerts"""
        self._play_callback = callback
    
    def set_config(self, config: VoiceAlertConfig) -> None:
        """Update configuration"""
        self.config = config
        self.text_generator.set_language(config.language)
    
    def get_trigger_from_type(self, notification_type: str) -> Optional[VoiceTrigger]:
        """Map notification type to voice trigger"""
        mapping = {
            "entry_v3_dual": VoiceTrigger.ENTRY,
            "entry_v6_single": VoiceTrigger.ENTRY,
            "entry_v6_single_a": VoiceTrigger.ENTRY,
            "entry_v6_single_b": VoiceTrigger.ENTRY,
            "exit_profit": VoiceTrigger.EXIT_PROFIT,
            "exit_loss": VoiceTrigger.EXIT_LOSS,
            "tp1_hit": VoiceTrigger.TP_HIT,
            "tp2_hit": VoiceTrigger.TP_HIT,
            "sl_hit": VoiceTrigger.SL_HIT,
            "emergency_stop": VoiceTrigger.EMERGENCY,
            "daily_summary": VoiceTrigger.DAILY_SUMMARY,
            "risk_alert": VoiceTrigger.RISK_ALERT,
            "mt5_disconnect": VoiceTrigger.MT5_DISCONNECT,
            "daily_loss_limit": VoiceTrigger.DAILY_LOSS_LIMIT,
        }
        return mapping.get(notification_type)
    
    def should_alert(self, notification_type: str) -> bool:
        """Check if voice alert should be generated"""
        if not self.config.enabled:
            return False
        
        trigger = self.get_trigger_from_type(notification_type)
        if not trigger:
            return False
        
        return self.config.is_trigger_enabled(trigger)
    
    def generate_alert(
        self,
        notification_type: str,
        data: Dict[str, Any]
    ) -> Optional[VoiceAlert]:
        """
        Generate voice alert
        
        Args:
            notification_type: Type of notification
            data: Notification data
            
        Returns:
            VoiceAlert if generated, None if skipped
        """
        if not self.should_alert(notification_type):
            return None
        
        trigger = self.get_trigger_from_type(notification_type)
        if not trigger:
            return None
        
        # Generate voice text
        text = self.text_generator.generate(notification_type, data)
        
        # Truncate if too long
        if len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length - 3] + "..."
        
        # Create alert
        alert = VoiceAlert(
            alert_id=self._generate_alert_id(),
            text=text,
            trigger=trigger,
            language=self.config.language,
            speed=self.config.speed,
            volume=self.config.volume
        )
        
        self.stats["total_generated"] += 1
        trigger_name = trigger.value
        self.stats["by_trigger"][trigger_name] = self.stats["by_trigger"].get(trigger_name, 0) + 1
        
        return alert
    
    async def send_alert(
        self,
        notification_type: str,
        data: Dict[str, Any]
    ) -> Optional[VoiceAlert]:
        """
        Generate and send voice alert
        
        Args:
            notification_type: Type of notification
            data: Notification data
            
        Returns:
            VoiceAlert with result
        """
        alert = self.generate_alert(notification_type, data)
        if not alert:
            return None
        
        # Check cooldown
        if self._last_alert_time:
            elapsed = (datetime.now() - self._last_alert_time).total_seconds()
            if elapsed < self.config.cooldown_seconds:
                # Queue for later
                if self.config.queue_enabled:
                    return await self.queue_alert(alert)
                return None
        
        # Play alert
        return await self.play_alert(alert)
    
    async def queue_alert(self, alert: VoiceAlert) -> VoiceAlert:
        """Add alert to queue"""
        if len(self.queue) >= self.config.max_queue_size:
            # Remove oldest
            self.queue.pop(0)
        
        self.queue.append(alert)
        return alert
    
    async def play_alert(self, alert: VoiceAlert) -> VoiceAlert:
        """Play voice alert"""
        try:
            if self._play_callback:
                if asyncio.iscoroutinefunction(self._play_callback):
                    await self._play_callback(alert.text, alert.language.value, alert.speed.value, alert.volume)
                else:
                    self._play_callback(alert.text, alert.language.value, alert.speed.value, alert.volume)
            
            alert.played_at = datetime.now()
            alert.success = True
            self.stats["total_played"] += 1
            self._last_alert_time = datetime.now()
            
        except Exception as e:
            alert.error = str(e)
            alert.success = False
            self.stats["total_failed"] += 1
            self.logger.error(f"Voice alert failed: {e}")
        
        # Add to history
        self.history.append(alert)
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
        
        return alert
    
    async def process_queue(self) -> List[VoiceAlert]:
        """Process queued alerts"""
        results = []
        
        while self.queue:
            # Check cooldown
            if self._last_alert_time:
                elapsed = (datetime.now() - self._last_alert_time).total_seconds()
                if elapsed < self.config.cooldown_seconds:
                    break
            
            alert = self.queue.pop(0)
            result = await self.play_alert(alert)
            results.append(result)
        
        return results
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return len(self.queue)
    
    def clear_queue(self) -> int:
        """Clear alert queue"""
        count = len(self.queue)
        self.queue.clear()
        return count
    
    def get_history(self, limit: int = 50) -> List[VoiceAlert]:
        """Get recent alert history"""
        return self.history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get voice alert statistics"""
        return {
            **self.stats,
            "queue_size": len(self.queue),
            "config": self.config.to_dict()
        }
    
    def enable(self) -> None:
        """Enable voice alerts"""
        self.config.enabled = True
    
    def disable(self) -> None:
        """Disable voice alerts"""
        self.config.enabled = False
    
    def enable_trigger(self, trigger: VoiceTrigger) -> None:
        """Enable specific trigger"""
        self.config.enable_trigger(trigger)
    
    def disable_trigger(self, trigger: VoiceTrigger) -> None:
        """Disable specific trigger"""
        self.config.disable_trigger(trigger)
    
    def set_volume(self, volume: int) -> None:
        """Set volume (0-100)"""
        self.config.volume = max(0, min(100, volume))
    
    def set_speed(self, speed: VoiceSpeed) -> None:
        """Set voice speed"""
        self.config.speed = speed
    
    def set_language(self, language: VoiceLanguage) -> None:
        """Set voice language"""
        self.config.language = language
        self.text_generator.set_language(language)
