# V4 Forex Session Enhancement - Implementation Plan

**Version:** 1.0  
**Created:** 2026-01-11  
**Implementation Order:** Sequential by module dependency

---

## Table of Contents

1. [Module 1: Fixed Clock System](#module-1-fixed-clock-system)
2. [Module 2: Session Manager](#module-2-session-manager)
3. [Module 3: Voice Alert System](#module-3-voice-alert-system)
4. [Module 4: Telegram UI Integration](#module-4-telegram-ui-integration)
5. [Module 5: Main Bot Integration](#module-5-main-bot-integration)
6. [Testing Strategy](#testing-strategy)
7. [Deployment Plan](#deployment-plan)

---

## Module 1: Fixed Clock System

### File: `src/modules/fixed_clock_system.py`

#### Purpose
Display real-time IST clock and calendar in Telegram with fixed positioning (pinned message).

#### Implementation Details

```python
"""
Fixed Clock & Calendar Display System
Provides real-time IST time and date in Telegram
"""

import asyncio
from datetime import datetime
import pytz
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
import logging

class FixedClockSystem:
    def __init__(self, bot: Bot, chat_id: str):
        self.bot = bot
        self.chat_id = chat_id
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.message_id: Optional[int] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)
    
    def get_current_ist_time(self) -> datetime:
        """Get current time in IST timezone"""
        return datetime.now(self.timezone)
    
    def format_clock_message(self) -> str:
        """Format combined clock and calendar message"""
        current_time = self.get_current_ist_time()
        
        # Time format: 22:15:30 IST
        time_str = current_time.strftime("%H:%M:%S IST")
        
        # Date format: 11 Jan 2026 (Saturday)
        date_str = current_time.strftime("%d %b %Y (%A)")
        
        # Combined message with emoji
        message = (
            f"🕐 **Current Time:** {time_str}\n"
            f"📅 **Date:** {date_str}\n"
            f"━━━━━━━━━━━━━━━━"
        )
        
        return message
    
    async def update_clock_display(self):
        """Update or create clock message"""
        try:
            message_text = self.format_clock_message()
            
            if self.message_id:
                # Edit existing message
                await self.bot.edit_message_text(
                    chat_id=self.chat_id,
                    message_id=self.message_id,
                    text=message_text,
                    parse_mode='Markdown'
                )
            else:
                # Create new message and pin it
                sent_message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message_text,
                    parse_mode='Markdown'
                )
                self.message_id = sent_message.message_id
                
                # Pin the message
                await self.bot.pin_chat_message(
                    chat_id=self.chat_id,
                    message_id=self.message_id,
                    disable_notification=True
                )
                
                self.logger.info(f"Clock message created and pinned: {self.message_id}")
        
        except TelegramError as e:
            self.logger.error(f"Failed to update clock display: {e}")
    
    async def start_clock_loop(self):
        """Start the clock update loop"""
        self.is_running = True
        self.logger.info("Starting fixed clock loop...")
        
        while self.is_running:
            try:
                await self.update_clock_display()
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                self.logger.error(f"Clock loop error: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    def stop_clock(self):
        """Stop the clock loop"""
        self.is_running = False
        self.logger.info("Clock loop stopped")
```

#### Integration Steps
1. Import in `main.py`
2. Initialize with Telegram bot and chat ID
3. Start async loop with `asyncio.create_task(clock.start_clock_loop())`
4. Ensure bot has permissions to pin messages

#### Testing Checklist
- [ ] IST timezone accuracy verified
- [ ] Message updates every second without lag
- [ ] Pinned message doesn't create notification spam
- [ ] Handles Telegram API errors gracefully
- [ ] Memory usage stable over 24-hour run

---

## Module 2: Session Manager

### File: `src/modules/session_manager.py`

#### Purpose
Manage Forex session timings, symbol filtering, and trade permissions based on dynamic JSON configuration.

#### Data Structure: `data/session_settings.json`

```json
{
  "version": "1.0",
  "master_switch": true,
  "timezone": "Asia/Kolkata",
  "sessions": {
    "asian": {
      "name": "Asian Session",
      "start_time": "05:30",
      "end_time": "14:30",
      "allowed_symbols": ["USDJPY", "AUDUSD", "EURJPY"],
      "advance_alert_enabled": true,
      "advance_alert_minutes": 30,
      "force_close_enabled": false,
      "description": "Tokyo & Sydney overlap, low volatility"
    },
    "london": {
      "name": "London Session",
      "start_time": "13:00",
      "end_time": "22:00",
      "allowed_symbols": ["GBPUSD", "EURUSD", "GBPJPY"],
      "advance_alert_enabled": true,
      "advance_alert_minutes": 30,
      "force_close_enabled": false,
      "description": "European session, high liquidity"
    },
    "overlap": {
      "name": "London-NY Overlap",
      "start_time": "18:00",
      "end_time": "20:30",
      "allowed_symbols": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "GBPJPY", "USDCAD"],
      "advance_alert_enabled": true,
      "advance_alert_minutes": 30,
      "force_close_enabled": false,
      "description": "Highest volume period, maximum volatility"
    },
    "ny_late": {
      "name": "New York Late Session",
      "start_time": "22:00",
      "end_time": "02:00",
      "allowed_symbols": ["USDCAD", "EURUSD"],
      "advance_alert_enabled": true,
      "advance_alert_minutes": 30,
      "force_close_enabled": false,
      "description": "Late US session, consolidation phase"
    },
    "dead_zone": {
      "name": "Dead Zone",
      "start_time": "02:00",
      "end_time": "05:30",
      "allowed_symbols": [],
      "advance_alert_enabled": false,
      "advance_alert_minutes": 0,
      "force_close_enabled": true,
      "description": "Low liquidity, trading not recommended"
    }
  },
  "all_symbols": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "GBPJPY", "USDCAD"],
  "alert_history": []
}
```

#### Implementation: `session_manager.py`

```python
"""
Forex Session Manager
Handles session-based trading restrictions and time management
"""

import json
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import logging

class SessionManager:
    def __init__(self, config_path: str = "data/session_settings.json"):
        self.config_path = config_path
        self.config = self.load_session_config()
        self.timezone = pytz.timezone(self.config.get('timezone', 'Asia/Kolkata'))
        self.logger = logging.getLogger(__name__)
        self.last_session = None
    
    def load_session_config(self) -> dict:
        """Load session configuration from JSON file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            self.logger.warning(f"Config not found: {self.config_path}, using defaults")
            return self._get_default_config()
    
    def save_session_config(self):
        """Save session configuration to JSON file"""
        try:
            # Atomic write: write to temp file first
            temp_path = self.config_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Rename temp to actual (atomic on most systems)
            os.replace(temp_path, self.config_path)
            self.logger.info("Session config saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save session config: {e}")
            raise
    
    def _get_default_config(self) -> dict:
        """Return default session configuration"""
        # (Use the JSON structure defined above)
        pass
    
    def get_current_time(self) -> datetime:
        """Get current time in configured timezone"""
        return datetime.now(self.timezone)
    
    def time_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM string to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def get_current_session(self, current_time: Optional[datetime] = None) -> str:
        """Get the name of the current active session"""
        if current_time is None:
            current_time = self.get_current_time()
        
        current_minutes = current_time.hour * 60 + current_time.minute
        
        for session_id, session_data in self.config['sessions'].items():
            start_mins = self.time_to_minutes(session_data['start_time'])
            end_mins = self.time_to_minutes(session_data['end_time'])
            
            # Handle sessions that cross midnight
            if start_mins > end_mins:
                if current_minutes >= start_mins or current_minutes < end_mins:
                    return session_id
            else:
                if start_mins <= current_minutes < end_mins:
                    return session_id
        
        return "none"
    
    def check_trade_allowed(self, symbol: str, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Check if trading the symbol is allowed based on current session
        Returns: (allowed: bool, reason: str)
        """
        # Master switch check
        if not self.config.get('master_switch', True):
            return True, "Master switch OFF - all trades allowed"
        
        if current_time is None:
            current_time = self.get_current_time()
        
        current_session = self.get_current_session(current_time)
        
        if current_session == "none":
            return False, "No active session"
        
        session_data = self.config['sessions'][current_session]
        allowed_symbols = session_data.get('allowed_symbols', [])
        
        if symbol in allowed_symbols:
            return True, f"Allowed in {session_data['name']}"
        else:
            return False, f"{symbol} not allowed in {session_data['name']}"
    
    def adjust_session_time(self, session_id: str, field: str, delta_minutes: int):
        """
        Adjust session start or end time
        field: 'start_time' or 'end_time'
        delta_minutes: +30 or -30 (in multiples of 30)
        """
        if session_id not in self.config['sessions']:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.config['sessions'][session_id]
        current_time_str = session[field]
        
        # Parse current time
        hours, minutes = map(int, current_time_str.split(':'))
        total_minutes = hours * 60 + minutes
        
        # Apply delta
        new_total_minutes = (total_minutes + delta_minutes) % (24 * 60)
        
        # Convert back to HH:MM
        new_hours = new_total_minutes // 60
        new_minutes = new_total_minutes % 60
        new_time_str = f"{new_hours:02d}:{new_minutes:02d}"
        
        # Update config
        self.config['sessions'][session_id][field] = new_time_str
        self.save_session_config()
        
        self.logger.info(f"Adjusted {session_id}.{field}: {current_time_str} → {new_time_str}")
    
    def toggle_symbol(self, session_id: str, symbol: str):
        """Toggle symbol ON/OFF for a session"""
        if session_id not in self.config['sessions']:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.config['sessions'][session_id]
        allowed_symbols = session.get('allowed_symbols', [])
        
        if symbol in allowed_symbols:
            allowed_symbols.remove(symbol)
            action = "removed"
        else:
            allowed_symbols.append(symbol)
            action = "added"
        
        session['allowed_symbols'] = allowed_symbols
        self.save_session_config()
        
        self.logger.info(f"{symbol} {action} for {session_id}")
    
    def toggle_master_switch(self) -> bool:
        """Toggle master switch and return new state"""
        current_state = self.config.get('master_switch', True)
        new_state = not current_state
        self.config['master_switch'] = new_state
        self.save_session_config()
        
        self.logger.info(f"Master switch: {current_state} → {new_state}")
        return new_state
    
    def toggle_force_close(self, session_id: str) -> bool:
        """Toggle force close for a session and return new state"""
        if session_id not in self.config['sessions']:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.config['sessions'][session_id]
        current_state = session.get('force_close_enabled', False)
        new_state = not current_state
        session['force_close_enabled'] = new_state
        self.save_session_config()
        
        return new_state
    
    def check_session_transitions(self) -> Dict[str, any]:
        """
        Check for session transitions and return alerts
        Should be called periodically (e.g., every minute)
        """
        current_time = self.get_current_time()
        current_session = self.get_current_session(current_time)
        
        alerts = {
            'session_started': None,
            'session_ending': None,
            'force_close_required': False
        }
        
        # Check if session just started
        if self.last_session != current_session:
            alerts['session_started'] = current_session
            self.last_session = current_session
        
        # Check for advance alerts (30 minutes before session starts)
        for session_id, session_data in self.config['sessions'].items():
            if not session_data.get('advance_alert_enabled', False):
                continue
            
            start_minutes = self.time_to_minutes(session_data['start_time'])
            alert_minutes = session_data.get('advance_alert_minutes', 30)
            
            # Calculate alert trigger time
            alert_trigger_minutes = (start_minutes - alert_minutes) % (24 * 60)
            current_minutes = current_time.hour * 60 + current_time.minute
            
            # Check if we're at the alert trigger point (within 1-minute window)
            if abs(current_minutes - alert_trigger_minutes) < 1:
                if session_id not in self.config.get('alert_history', []):
                    alerts['session_ending'] = {
                        'session': session_id,
                        'starts_in_minutes': alert_minutes
                    }
                    # Add to alert history to prevent duplicates
                    self.config.setdefault('alert_history', []).append(session_id)
        
        # Check if current session requires force close at end
        if current_session != "none":
            current_session_data = self.config['sessions'][current_session]
            if current_session_data.get('force_close_enabled', False):
                end_minutes = self.time_to_minutes(current_session_data['end_time'])
                current_minutes = current_time.hour * 60 + current_time.minute
                
                # Trigger force close 1 minute before session ends
                if abs(current_minutes - (end_minutes - 1)) < 1:
                    alerts['force_close_required'] = True
        
        return alerts
    
    def get_session_status_text(self) -> str:
        """Generate status text for Telegram display"""
        current_time = self.get_current_time()
        current_session = self.get_current_session(current_time)
        master_switch = self.config.get('master_switch', True)
        
        status = f"🔴 **Master Switch:** {'ON' if master_switch else 'OFF'}\n"
        
        if current_session == "none":
            status += "🕐 **Current Session:** None (Dead Zone)\n"
            status += "✅ **Allowed Symbols:** All (0 restrictions)\n"
        else:
            session_data = self.config['sessions'][current_session]
            allowed_symbols = session_data.get('allowed_symbols', [])
            status += f"🕐 **Current Session:** {session_data['name']}\n"
            status += f"✅ **Allowed Symbols:** {', '.join(allowed_symbols)} ({len(allowed_symbols)}/{len(self.config['all_symbols'])})\n"
        
        return status
```

#### Integration Steps
1. Create `data/session_settings.json` with default Forex sessions
2. Initialize `SessionManager` in `main.py`
3. Call `check_trade_allowed()` before every trade execution
4. Schedule `check_session_transitions()` every minute with async task
5. Integrate transition alerts with Voice Alert System

#### Testing Checklist
- [ ] JSON config loads correctly
- [ ] Session detection accurate across midnight boundary
- [ ] Symbol filtering works for all sessions
- [ ] Time adjustment logic handles edge cases (midnight, negative values)
- [ ] Master switch globally disables all filtering
- [ ] Force close triggers at correct time
- [ ] Advance alerts fire 30 minutes before session
- [ ] Config saves atomically without corruption

---

## Module 3: Voice Alert System

### File: `src/modules/voice_alert_system.py`

#### Purpose
Multi-channel alert delivery with retry mechanism, supporting Voice, Text, and SMS.

#### Implementation

```python
"""
Voice Alert System
Multi-channel notification delivery with retry and queueing
"""

import asyncio
from datetime import datetime
import pytz
from typing import Dict, List, Optional
from enum import Enum
import logging
import uuid
from gtts import gTTS
import io
from telegram import Bot
from telegram.error import TelegramError

class AlertPriority(Enum):
    CRITICAL = "CRITICAL"  # System crashes, major losses
    HIGH = "HIGH"          # Order execution
    MEDIUM = "MEDIUM"      # SL/TP hits
    LOW = "LOW"            # Session alerts

class AlertChannel(Enum):
    VOICE = "voice"
    TEXT = "text"
    SMS = "sms"

class VoiceAlertSystem:
    def __init__(self, bot: Bot, chat_id: str, sms_gateway=None):
        self.bot = bot
        self.chat_id = chat_id
        self.sms_gateway = sms_gateway
        self.alert_queue: List[Dict] = []
        self.is_processing = False
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.logger = logging.getLogger(__name__)
    
    async def send_voice_alert(self, message: str, priority: AlertPriority = AlertPriority.MEDIUM):
        """
        Queue a voice alert for delivery
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
        """Determine delivery channels based on priority"""
        if priority == AlertPriority.CRITICAL:
            return [AlertChannel.VOICE.value, AlertChannel.TEXT.value, AlertChannel.SMS.value]
        elif priority == AlertPriority.HIGH:
            return [AlertChannel.VOICE.value, AlertChannel.TEXT.value]
        elif priority == AlertPriority.MEDIUM:
            return [AlertChannel.VOICE.value]
        else:  # LOW
            return [AlertChannel.TEXT.value]
    
    async def generate_voice_message(self, text: str) -> Optional[bytes]:
        """Generate TTS voice message"""
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
        except Exception as e:
            self.logger.error(f"TTS generation failed: {e}")
            return None
    
    async def send_via_telegram_voice(self, message: str) -> bool:
        """Send voice message via Telegram"""
        try:
            audio_data = await self.generate_voice_message(message)
            if not audio_data:
                return False
            
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "alert.mp3"
            
            await self.bot.send_voice(
                chat_id=self.chat_id,
                voice=audio_file,
                caption=f"🔊 Voice Alert: {message[:50]}..."
            )
            
            self.logger.info("Voice message sent successfully")
            return True
        
        except TelegramError as e:
            self.logger.error(f"Telegram voice send failed: {e}")
            return False
    
    async def send_via_telegram_text(self, message: str, priority: AlertPriority) -> bool:
        """Send text message with sound via Telegram"""
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
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=formatted_message,
                parse_mode='Markdown',
                disable_notification=False  # Ensure sound plays
            )
            
            self.logger.info("Text message sent successfully")
            return True
        
        except TelegramError as e:
            self.logger.error(f"Telegram text send failed: {e}")
            return False
    
    async def send_via_sms(self, message: str) -> bool:
        """Send SMS via gateway (fallback)"""
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
        """Process alerts in the queue"""
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
        """Attempt to deliver an alert through available channels"""
        message = alert['message']
        priority = AlertPriority(alert['priority'])
        channels = alert['channels']
        
        for channel in channels:
            try:
                if channel == AlertChannel.VOICE.value:
                    success = await self.send_via_telegram_voice(message)
                elif channel == AlertChannel.TEXT.value:
                    success = await self.send_via_telegram_text(message, priority)
                elif channel == AlertChannel.SMS.value:
                    success = await self.send_via_sms(message)
                else:
                    continue
                
                if success:
                    return True
            
            except Exception as e:
                self.logger.error(f"Channel {channel} delivery failed: {e}")
                continue
        
        return False
```

#### Integration Steps
1. Install `gTTS` library: `pip install gTTS`
2. Initialize `VoiceAlertSystem` in `main.py`
3. Replace all existing alert calls with `voice_alerts.send_voice_alert()`
4. Configure SMS gateway (optional) for critical alerts
5. Test with phone locked to verify delivery

#### Testing Checklist
- [ ] Voice messages generate correctly
- [ ] TTS audio quality acceptable
- [ ] Telegram delivers voice when phone locked
- [ ] Text fallback works when voice fails
- [ ] SMS fallback works (if configured)
- [ ] Retry mechanism works with exponential backoff
- [ ] Queue processes alerts in priority order
- [ ] No memory leaks during extended operation

---

## Module 4: Telegram UI Integration

### File: `src/telegram/session_menu_handler.py`

#### Purpose
Handle Session Manager menu interactions and dynamic UI updates.

#### Implementation

```python
"""
Session Manager Telegram Menu Handler
Zero-typing button-based UI for session configuration
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from modules.session_manager import SessionManager
import logging

class SessionMenuHandler:
    def __init__(self, session_manager: SessionManager):
        self.session_mgr = session_manager
        self.logger = logging.getLogger(__name__)
    
    async def show_session_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display Session Manager dashboard"""
        query = update.callback_query
        await query.answer()
        
        # Get current status
        status_text = self.session_mgr.get_session_status_text()
        master_switch = self.session_mgr.config.get('master_switch', True)
        
        # Build keyboard
        keyboard = [
            [InlineKeyboardButton(
                f"{'🟢 Master: ON' if master_switch else '🔴 Master: OFF'}",
                callback_data="session_toggle_master"
            )],
            [InlineKeyboardButton("📝 Edit Sessions", callback_data="session_edit_menu")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="session_settings")],
            [InlineKeyboardButton("« Back", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"**📊 Session Manager Dashboard**\n\n{status_text}"
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_session_edit_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show list of sessions to edit"""
        query = update.callback_query
        await query.answer()
        
        keyboard = []
        
        for session_id, session_data in self.session_mgr.config['sessions'].items():
            button_text = f"{session_data['name']}"
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"session_edit_{session_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back", callback_data="session_dashboard")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="**Select Session to Edit:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_session_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: str):
        """Show detailed edit menu for a specific session"""
        query = update.callback_query
        await query.answer()
        
        session_data = self.session_mgr.config['sessions'][session_id]
        all_symbols = self.session_mgr.config['all_symbols']
        allowed_symbols = session_data.get('allowed_symbols', [])
        
        # Build symbol toggle buttons (2 per row)
        symbol_keyboard = []
        for i in range(0, len(all_symbols), 2):
            row = []
            for j in range(2):
                if i + j < len(all_symbols):
                    symbol = all_symbols[i + j]
                    is_allowed = symbol in allowed_symbols
                    button_text = f"{'✅' if is_allowed else '❌'} {symbol}"
                    row.append(InlineKeyboardButton(
                        button_text,
                        callback_data=f"session_toggle_{session_id}_{symbol}"
                    ))
            symbol_keyboard.append(row)
        
        # Time adjustment buttons
        time_keyboard = [
            [
                InlineKeyboardButton("Start:", callback_data="noop"),
                InlineKeyboardButton(session_data['start_time'], callback_data="noop"),
                InlineKeyboardButton("−30m", callback_data=f"session_time_{session_id}_start_-30"),
                InlineKeyboardButton("+30m", callback_data=f"session_time_{session_id}_start_+30")
            ],
            [
                InlineKeyboardButton("End:", callback_data="noop"),
                InlineKeyboardButton(session_data['end_time'], callback_data="noop"),
                InlineKeyboardButton("−30m", callback_data=f"session_time_{session_id}_end_-30"),
                InlineKeyboardButton("+30m", callback_data=f"session_time_{session_id}_end_+30")
            ]
        ]
        
        # Toggle buttons
        force_close = session_data.get('force_close_enabled', False)
        toggle_keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if force_close else '❌'} Force Close at End",
                callback_data=f"session_force_{session_id}"
            )]
        ]
        
        # Combine all keyboards
        keyboard = symbol_keyboard + time_keyboard + toggle_keyboard
        keyboard.append([InlineKeyboardButton("« Back", callback_data="session_edit_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"**Editing: {session_data['name']}**\n\n"
            f"📝 Description: {session_data.get('description', 'N/A')}\n"
            f"⏰ Active: {session_data['start_time']} - {session_data['end_time']}\n"
            f"📊 Allowed Symbols: {len(allowed_symbols)}/{len(all_symbols)}\n\n"
            f"**Toggle symbols, adjust times, or configure options below:**"
        )
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_symbol_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle symbol ON/OFF toggle"""
        query = update.callback_query
        await query.answer()
        
        # Parse callback data: session_toggle_{session_id}_{symbol}
        _, _, session_id, symbol = query.data.split('_', 3)
        
        self.session_mgr.toggle_symbol(session_id, symbol)
        
        # Refresh the edit menu
        await self.show_session_details(update, context, session_id)
    
    async def handle_time_adjustment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle session time adjustment"""
        query = update.callback_query
        await query.answer()
        
        # Parse callback data: session_time_{session_id}_{field}_{delta}
        _, _, session_id, field, delta_str = query.data.split('_', 4)
        delta_minutes = int(delta_str)
        
        self.session_mgr.adjust_session_time(session_id, f"{field}_time", delta_minutes)
        
        # Refresh the edit menu
        await self.show_session_details(update, context, session_id)
    
    async def handle_master_switch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle master switch"""
        query = update.callback_query
        await query.answer()
        
        new_state = self.session_mgr.toggle_master_switch()
        
        # Refresh dashboard
        await self.show_session_dashboard(update, context)
    
    async def handle_force_close_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle force close for a session"""
        query = update.callback_query
        await query.answer()
        
        # Parse callback data: session_force_{session_id}
        _, _, session_id = query.data.split('_', 2)
        
        new_state = self.session_mgr.toggle_force_close(session_id)
        
        # Refresh the edit menu
        await self.show_session_details(update, context, session_id)
```

#### Integration Steps
1. Import `SessionMenuHandler` in `telegram_bot.py`
2. Initialize with `SessionManager` instance
3. Add "Session Manager" button to main menu
4. Register callback handlers for all `session_*` patterns
5. Test all button interactions

#### Testing Checklist
- [ ] Dashboard displays correct current session
- [ ] Master switch toggles correctly
- [ ] Symbol buttons toggle ON/OFF states
- [ ] Time adjustment updates visible immediately
- [ ] Force close toggle works
- [ ] All buttons respond within 1 second
- [ ] UI doesn't break with concurrent users

---

## Module 5: Main Bot Integration

### File: `src/main.py` (Updates)

#### Integration Points

```python
# Add imports
from modules.fixed_clock_system import FixedClockSystem
from modules.session_manager import SessionManager
from modules.voice_alert_system import VoiceAlertSystem, AlertPriority
from telegram.session_menu_handler import SessionMenuHandler

# In main() function
async def main():
    # ... existing initialization ...
    
    # Initialize new systems
    clock_system = FixedClockSystem(bot, TELEGRAM_CHAT_ID)
    session_mgr = SessionManager()
    voice_alerts = VoiceAlertSystem(bot, TELEGRAM_CHAT_ID)
    session_menu = SessionMenuHandler(session_mgr)
    
    # Start background tasks
    asyncio.create_task(clock_system.start_clock_loop())
    asyncio.create_task(monitor_session_transitions(session_mgr, voice_alerts))
    
    # ... rest of initialization ...

async def monitor_session_transitions(session_mgr, voice_alerts):
    """Background task to monitor session changes"""
    while True:
        try:
            alerts = session_mgr.check_session_transitions()
            
            if alerts['session_started']:
                session_data = session_mgr.config['sessions'][alerts['session_started']]
                await voice_alerts.send_voice_alert(
                    f"Session started: {session_data['name']}",
                    AlertPriority.LOW
                )
            
            if alerts['session_ending']:
                info = alerts['session_ending']
                session_data = session_mgr.config['sessions'][info['session']]
                await voice_alerts.send_voice_alert(
                    f"Advance alert: {session_data['name']} starts in {info['starts_in_minutes']} minutes",
                    AlertPriority.MEDIUM
                )
            
            if alerts['force_close_required']:
                # Trigger force close logic
                # (Implementation depends on existing trade closing mechanism)
                pass
        
        except Exception as e:
            logging.error(f"Session transition monitoring error: {e}")
        
        await asyncio.sleep(60)  # Check every minute
```

### File: `src/trading_engine.py` (Updates)

```python
# Add session check before trade execution
async def execute_trade(symbol, action, lot_size, ...):
    # Session filtering
    allowed, reason = session_mgr.check_trade_allowed(symbol)
    
    if not allowed:
        logger.warning(f"Trade rejected: {reason}")
        await voice_alerts.send_voice_alert(
            f"❌ Trade rejected: {symbol} {action} - {reason}",
            AlertPriority.MEDIUM
        )
        return False
    
    # ... existing trade execution logic ...
    
    # Send voice alert on successful execution
    await voice_alerts.send_voice_alert(
        f"✅ Trade opened: {action} {symbol} {lot_size} lots @ {entry_price}",
        AlertPriority.HIGH
    )
```

---

## Testing Strategy

### Unit Tests

#### Test: `test_session_manager.py`
```python
import pytest
from modules.session_manager import SessionManager
from datetime import datetime
import pytz

def test_session_detection():
    mgr = SessionManager()
    
    # Test Asian session (05:30 - 14:30 IST)
    test_time = datetime(2026, 1, 11, 10, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
    assert mgr.get_current_session(test_time) == "asian"
    
    # Test London session (13:00 - 22:00 IST)
    test_time = datetime(2026, 1, 11, 15, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
    assert mgr.get_current_session(test_time) == "london"

def test_trade_allowed():
    mgr = SessionManager()
    
    # Asian session allows USDJPY
    test_time = datetime(2026, 1, 11, 10, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
    allowed, reason = mgr.check_trade_allowed("USDJPY", test_time)
    assert allowed == True
    
    # Asian session does NOT allow GBPUSD
    allowed, reason = mgr.check_trade_allowed("GBPUSD", test_time)
    assert allowed == False

def test_time_adjustment():
    mgr = SessionManager()
    
    original_start = mgr.config['sessions']['asian']['start_time']
    mgr.adjust_session_time('asian', 'start_time', 30)
    new_start = mgr.config['sessions']['asian']['start_time']
    
    assert original_start != new_start
```

### Integration Tests

#### Test: Live Session Transition
1. Set current time to 5 minutes before session start
2. Wait and verify 30-min advance alert fires
3. Wait and verify session start alert fires
4. Verify allowed symbols updated

#### Test: Force Close
1. Enable force close for a session
2. Open a test trade during session
3. Wait until session end time
4. Verify trade closes automatically

### End-to-End Tests

#### Test: Full Trading Workflow
1. Enable master switch
2. Attempt trade during allowed session with allowed symbol → Success
3. Attempt trade during allowed session with disallowed symbol → Rejection
4. Attempt trade during dead zone → Rejection
5. Disable master switch
6. Attempt trade during dead zone → Success (bypass enabled)

---

## Deployment Plan

### Pre-Deployment Checklist
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Documentation updated
- [ ] `requirements.txt` updated with new dependencies
- [ ] Environment variables configured
- [ ] SMS gateway tested (if used)
- [ ] Backup of existing database created

### Deployment Steps

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Create Data Directory
```bash
mkdir -p data
cp updates/v4_forex_session_system/session_settings.json data/
```

#### 3. Update Environment Variables
```bash
# .env file
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
SMS_GATEWAY_API_KEY=optional_sms_key  # If using SMS
```

#### 4. Run Initial Tests
```bash
python -m pytest tests/test_session_manager.py -v
python -m pytest tests/test_voice_alerts.py -v
```

#### 5. Start Bot
```bash
python src/main.py
```

#### 6. Verify Deployment
- [ ] Clock displays in Telegram
- [ ] Session Manager menu accessible
- [ ] Voice alert test successful
- [ ] Session transition detected
- [ ] Trade filtering works

### Rollback Plan
1. Stop bot: `Ctrl+C`
2. Restore previous version: `git checkout <previous-commit>`
3. Restore data: `cp data/session_settings.json.backup data/session_settings.json`
4. Restart bot: `python src/main.py`

---

## Monitoring & Maintenance

### Key Metrics
- Clock update latency (target: <100ms)
- Session detection accuracy (target: 100%)
- Voice alert delivery rate (target: >95%)
- Telegram API response time (target: <1s)
- JSON config integrity (no corruption)

### Logging
```python
# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/forex_sessions.log'),
        logging.StreamHandler()
    ]
)
```

### Regular Maintenance
- **Daily:** Check alert delivery logs
- **Weekly:** Review session transition accuracy
- **Monthly:** Backup `session_settings.json`
- **Quarterly:** Update TradingView Forex session timings if market hours change

---

**End of Implementation Plan**  
**Next:** Begin Phase 2 (Clock & Calendar Implementation)
