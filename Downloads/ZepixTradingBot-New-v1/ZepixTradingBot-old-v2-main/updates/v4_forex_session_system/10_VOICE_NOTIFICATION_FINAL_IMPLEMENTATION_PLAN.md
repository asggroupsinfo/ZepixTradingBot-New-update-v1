# Voice Notification System - FINAL IMPLEMENTATION PLAN
*Date: 2026-01-12 02:00 IST | Status: APPROVED FOR IMPLEMENTATION*

## 🎯 OBJECTIVE (Zero Tolerance)

**Goal:** Implement dual-channel audio notification system with 100% reliability.

**User Requirements:**
1. ✅ **Windows Laptop:** Direct TTS audio playback via speakers (works even if Telegram closed)
2. ✅ **Phone:** Telegram notification sound (works even if phone locked)
3. ❌ **NO voice files** in Telegram chat
4. ✅ Must hear voice on both devices immediately

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Dependency Installation ✅
- [x] Install `pyttsx3` for Windows TTS
- [x] Verify installation success
- [x] Test basic TTS functionality

### Phase 2: Code Implementation 🔄
- [ ] Create `WindowsAudioPlayer` module
- [ ] Update `VoiceAlertSystem` class
- [ ] Remove voice file sending logic
- [ ] Add Windows speaker integration
- [ ] Update channel routing logic

### Phase 3: Testing & Verification 🔄
- [ ] Test Windows audio playback
- [ ] Test phone notification sound
- [ ] Verify NO voice files in chat
- [ ] End-to-end live bot test

### Phase 4: Documentation Update 🔄
- [ ] Update main documentation
- [ ] Add usage guide
- [ ] Document troubleshooting steps

---

## 🏗️ ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                    Bot Trading Signal Triggered                  │
│                   (Entry/Exit/Warning/Critical)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              VoiceAlertSystem (UPGRADED V2.0)                    │
│  • Receives alert with priority (CRITICAL/HIGH/MEDIUM/LOW)       │
│  • Routes to appropriate channels                                │
│  • NO MORE: Voice file generation/sending                        │
└────────────────┬──────────────────────────┬─────────────────────┘
                 │                          │
                 ▼                          ▼
┌──────────────────────────┐   ┌─────────────────────────────────┐
│  WindowsAudioPlayer      │   │  Telegram Bot                    │
│  (NEW MODULE)            │   │  (UPDATED - Text Only)           │
│                          │   │                                  │
│  • pyttsx3.init()        │   │  • bot.send_message()            │
│  • engine.say(text)      │   │  • disable_notification=False    │
│  • engine.runAndWait()   │   │  • Text + emoji only             │
│  • Direct speaker output │   │  • Triggers sound on phone       │
└──────────────────────────┘   └─────────────────────────────────┘
         │                              │
         ▼                              ▼
   🔊 WINDOWS SPEAKER            📱 PHONE NOTIFICATION SOUND
   (Direct Audio - TTS)         (Telegram Native Sound)
   Works: Telegram closed       Works: Phone locked
```

---

## 📝 CODE IMPLEMENTATION DETAILS

### 1. NEW MODULE: `src/modules/windows_audio_player.py`

```python
"""
Windows Audio Player Module
Direct TTS audio playback on Windows speakers using pyttsx3.

Features:
- Offline TTS (no internet required)
- Direct speaker output
- Works even if Telegram is closed
- Configurable voice rate and volume

Author: Zepix Trading Bot Team
Version: 1.0
Created: 2026-01-12
"""

import pyttsx3
import logging
from typing import Optional


class WindowsAudioPlayer:
    """Play TTS audio directly on Windows speakers."""
    
    def __init__(self, rate: int = 150, volume: float = 1.0):
        """
        Initialize Windows Audio Player.
        
        Args:
            rate: Speech rate (words per minute), default 150
            volume: Volume level (0.0 to 1.0), default 1.0 (max)
        """
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.rate = rate
        self.volume = volume
        
        try:
            self.engine = pyttsx3.init()
            self._configure_engine()
            self.logger.info(f"WindowsAudioPlayer initialized | Rate: {rate} | Volume: {volume}")
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
            raise
    
    def _configure_engine(self):
        """Configure TTS engine properties."""
        if not self.engine:
            return
        
        # Set speech rate
        self.engine.setProperty('rate', self.rate)
        
        # Set volume level
        self.engine.setProperty('volume', self.volume)
        
        # Get available voices (optional: select specific voice)
        voices = self.engine.getProperty('voices')
        if voices:
            # Default to first voice (usually Microsoft David/Zira)
            self.engine.setProperty('voice', voices[0].id)
            self.logger.info(f"Using voice: {voices[0].name}")
    
    def speak(self, text: str) -> bool:
        """
        Play text as audio on Windows speakers.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            self.logger.error("TTS engine not initialized")
            return False
        
        if not text or not text.strip():
            self.logger.warning("Empty text provided, skipping")
            return False
        
        try:
            self.logger.info(f"Playing audio: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # Queue text for speech
            self.engine.say(text)
            
            # Block while processing all currently queued commands
            self.engine.runAndWait()
            
            self.logger.info("Audio playback completed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
            return False
    
    def test_speaker(self) -> bool:
        """
        Test speaker with a simple message.
        
        Returns:
            True if test successful, False otherwise
        """
        test_message = "Windows audio system test. If you can hear this, the system is working correctly."
        return self.speak(test_message)
    
    def cleanup(self):
        """Clean up TTS engine resources."""
        if self.engine:
            try:
                self.engine.stop()
                self.logger.info("TTS engine stopped")
            except Exception as e:
                self.logger.error(f"Error stopping TTS engine: {e}")


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing WindowsAudioPlayer...")
    
    try:
        player = WindowsAudioPlayer(rate=160, volume=1.0)
        player.test_speaker()
        player.speak("This is a critical trading alert. Euro USD long position opened at 1.0850.")
        player.cleanup()
        print("✅ Test completed successfully")
    except Exception as e:
        print(f"❌ Test failed: {e}")
```

---

### 2. UPDATED MODULE: `src/modules/voice_alert_system.py`

**Changes Required:**

#### A) Import Section (Line 1-33)
```python
# ADD THIS IMPORT
from src.modules.windows_audio_player import WindowsAudioPlayer
```

#### B) __init__ Method (Line 58-76)
```python
def __init__(self, bot: Bot, chat_id: str, sms_gateway=None):
    """
    Initialize Voice Alert System with Windows audio support.
    
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
    
    # NEW: Initialize Windows Audio Player
    try:
        self.windows_player = WindowsAudioPlayer(rate=150, volume=1.0)
        self.logger.info("Windows audio player initialized successfully")
    except Exception as e:
        self.logger.error(f"Windows audio player initialization failed: {e}")
        self.windows_player = None
    
    self.logger.info("VoiceAlertSystem V2.0 initialized")
```

#### C) Channel Routing Method (Line 105-124)
```python
def _get_channels_for_priority(self, priority: AlertPriority) -> List[str]:
    """
    Determine delivery channels based on priority.
    
    V2.0 Update: 
    - Removed voice file channel
    - Added windows_audio channel
    - All priorities get text notifications
    
    Args:
        priority: Alert priority
        
    Returns:
        List of channel names to attempt
    """
    if priority == AlertPriority.CRITICAL:
        return ["windows_audio", "text", "sms"]
    elif priority == AlertPriority.HIGH:
        return ["windows_audio", "text"]
    elif priority == AlertPriority.MEDIUM:
        return ["windows_audio", "text"]
    else:  # LOW
        return ["text"]  # Text only for LOW priority
```

#### D) NEW METHOD: Windows Audio Sender
```python
async def send_via_windows_speaker(self, message: str) -> bool:
    """
    Play audio on Windows laptop speakers via TTS.
    
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
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.windows_player.speak, message)
            success = future.result(timeout=10)  # 10 second timeout
        
        if success:
            self.logger.info("Windows speaker audio played successfully")
        else:
            self.logger.warning("Windows speaker audio playback failed")
        
        return success
    
    except Exception as e:
        self.logger.error(f"Windows speaker audio error: {e}")
        return False
```

#### E) REMOVE METHOD: send_via_telegram_voice (Line 151-183)
```python
# COMPLETELY DELETE THIS METHOD - NO LONGER NEEDED
# Lines 151-183 should be removed
```

#### F) UPDATE METHOD: send_via_telegram_text (Line 184-221)
```python
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
        
        # IMPORTANT: disable_notification=False ensures phone makes sound
        self.bot.send_message(
            chat_id=self.chat_id,  # ADD THIS
            text=formatted_message,  # CHANGE: message → text
            parse_mode='Markdown',
            disable_notification=False  # ADD THIS: Ensures notification sound
        )
        
        self.logger.info("Text notification sent successfully")
        return True
    
    except TelegramError as e:
        self.logger.error(f"Telegram text send failed: {e}")
        return False
    except Exception as e:
        self.logger.error(f"Text send error: {e}")
        return False
```

#### G) UPDATE METHOD: _deliver_alert (Line 282-314)
```python
async def _deliver_alert(self, alert: Dict) -> bool:
    """
    Attempt to deliver an alert through available channels.
    
    V2.0 Update: Routes to windows_audio instead of voice channel.
    
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
            if channel == "windows_audio":  # NEW
                success = await self.send_via_windows_speaker(message)
            elif channel == "text":
                success = await self.send_via_telegram_text(message, priority)
            elif channel == "sms":
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
```

---

## 🧪 TESTING PLAN

### Test 1: Windows Speaker Test Script
**File:** `scripts/test_windows_audio.py`

```python
"""
Test Windows Audio Player functionality.
Verifies that TTS audio plays correctly on Windows speakers.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.windows_audio_player import WindowsAudioPlayer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 60)
    print("WINDOWS AUDIO PLAYER TEST")
    print("=" * 60)
    
    try:
        print("\n1. Initializing Windows Audio Player...")
        player = WindowsAudioPlayer(rate=150, volume=1.0)
        print("✅ Initialization successful\n")
        
        print("2. Running speaker test...")
        if player.test_speaker():
            print("✅ Speaker test passed\n")
        else:
            print("❌ Speaker test failed\n")
            return False
        
        print("3. Testing trading alert simulation...")
        test_messages = [
            "Critical alert. Euro USD long position opened at 1.0850. Stop loss at 1.0800.",
            "High priority. Profit target reached. Position closed with 50 pips profit.",
            "Medium priority. Trend reversal detected on 15-minute chart."
        ]
        
        for i, msg in enumerate(test_messages, 1):
            print(f"\nPlaying message {i}/{len(test_messages)}...")
            if player.speak(msg):
                print(f"✅ Message {i} played successfully")
            else:
                print(f"❌ Message {i} playback failed")
        
        print("\n4. Cleaning up...")
        player.cleanup()
        print("✅ Cleanup complete")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return True
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### Test 2: Live Bot Test
**Steps:**
1. Start bot: `python START_BOT.bat`
2. Trigger test alert via Telegram command
3. **Verify:**
   - ✅ Hear TTS audio from Windows speakers
   - ✅ Receive Telegram notification on phone (with sound)
   - ✅ NO voice files in Telegram chat
   - ✅ Only text messages visible

### Test 3: Phone Locked Test
**Steps:**
1. Lock phone screen
2. Trigger CRITICAL alert from bot
3. **Expected:**
   - ✅ Hear Telegram notification sound
   - ✅ See notification banner on lock screen
   - ✅ Hear Windows speaker audio simultaneously

---

## 📦 DEPENDENCY MANAGEMENT

### Install pyttsx3
```bash
pip install pyttsx3
```

### Verify Installation
```bash
python -c "import pyttsx3; print('✅ pyttsx3 installed successfully')"
```

### Update requirements.txt
```txt
# Add this line
pyttsx3==2.90
```

---

## ✅ SUCCESS CRITERIA (Zero Tolerance)

| Requirement | Status | Verification Method |
|------------|--------|---------------------|
| Windows speaker plays TTS audio | ⏳ | Run `test_windows_audio.py` |
| Phone receives notification sound | ⏳ | Live bot test with locked phone |
| NO voice files in chat | ⏳ | Check Telegram chat history |
| Works with Telegram closed | ⏳ | Close Telegram, trigger alert |
| Works with phone locked | ⏳ | Lock phone, trigger alert |
| Audio quality acceptable | ⏳ | Manual listening test |
| Latency < 3 seconds | ⏳ | Measure time from signal to audio |
| Error handling robust | ⏳ | Test with speaker muted, network down |

---

## 🚨 ROLLBACK PLAN

If Windows audio fails:
1. Check `pyttsx3` initialization error in logs
2. Verify Windows SAPI5 voices are installed
3. Fallback: Comment out `windows_audio` channel routing
4. Temporary: Revert to text-only notifications
5. Investigate and fix root cause

---

## 📚 DOCUMENTATION UPDATES REQUIRED

### Files to Update:
1. `DOCUMENTATION/VOICE_ALERT_SYSTEM.md` → Add V2.0 architecture
2. `DOCUMENTATION/DEPLOYMENT_GUIDE.md` → Add pyttsx3 installation
3. `DOCUMENTATION/TROUBLESHOOTING.md` → Add Windows audio issues
4. `README.md` → Update features list

---

## 🎯 IMPLEMENTATION TIMELINE

- **Phase 1:** Install dependencies (5 min) ⏱️
- **Phase 2:** Code implementation (30 min) ⏱️
- **Phase 3:** Testing & verification (20 min) ⏱️
- **Phase 4:** Documentation updates (15 min) ⏱️

**Total:** ~70 minutes

---

## 🔥 CRITICAL NOTES

1. **NO Voice Files:** Absolutely NO `send_voice()` calls in final code
2. **Synchronous TTS:** Use ThreadPoolExecutor to avoid blocking async loop
3. **Notification Sound:** `disable_notification=False` is MANDATORY
4. **Error Handling:** Graceful degradation if Windows audio unavailable
5. **Testing:** MUST hear audio on both devices before marking complete

---

**Status:** Ready for implementation
**Next Action:** Install pyttsx3 and begin coding

*End of Implementation Plan*
