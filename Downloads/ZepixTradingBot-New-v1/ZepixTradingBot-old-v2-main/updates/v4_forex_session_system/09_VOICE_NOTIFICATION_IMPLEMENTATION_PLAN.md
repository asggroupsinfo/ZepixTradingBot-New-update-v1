# Voice Notification System - Implementation Plan
*Date: 2026-01-12 | Status: AWAITING APPROVAL*

## 1. Overview

**Goal:** Implement dual-channel audio notification system.

**Channels:**
1. **Windows Laptop:** Direct TTS playback via `pyttsx3`
2. **Phone:** Telegram text notifications (with sound)

**Constraints:**
- NO voice files in Telegram chat
- Must work with phone locked/Telegram closed
- Must work with laptop speakers (even if Telegram closed)

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Bot Alert Triggered                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────┐
│              VoiceAlertSystem (Updated)                    │
│  • Receives alert with priority (CRITICAL/HIGH/MEDIUM/LOW) │
│  • Routes to appropriate channels                          │
└────────────┬──────────────────────┬───────────────────────┘
             │                      │
             ▼                      ▼
┌─────────────────────┐   ┌──────────────────────┐
│ WindowsAudioPlayer  │   │  TelegramBot         │
│ (NEW MODULE)        │   │  (UPDATED)           │
│                     │   │                      │
│ • pyttsx3.speak()   │   │ • send_message()     │
│ • Laptop speakers   │   │ • Text only          │
│ • Immediate playback│   │ • Notification sound │
└─────────────────────┘   └──────────────────────┘
         │                         │
         ▼                         ▼
  🔊 Windows Speaker         📱 Phone Notification
  (Direct Audio)            (Telegram Sound)
```

---

## 3. Code Changes

### 3.1 NEW: `src/modules/windows_audio_player.py`

```python
import pyttsx3
import logging

class WindowsAudioPlayer:
    """Play TTS audio directly on Windows speakers"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed
        self.engine.setProperty('volume', 1.0)  # Max volume
        self.logger = logging.getLogger(__name__)
    
    def speak(self, text: str):
        """Play text as audio on Windows speakers"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            self.logger.info(f"Audio played: {text[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
```

### 3.2 MODIFY: `src/modules/voice_alert_system.py`

**Changes:**
1. Import `WindowsAudioPlayer`
2. Remove `send_via_telegram_voice()` method
3. Add `send_via_windows_speaker()` method
4. Update `_deliver_alert()` to route correctly

**Key Code:**
```python
from src.modules.windows_audio_player import WindowsAudioPlayer

class VoiceAlertSystem:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.windows_player = WindowsAudioPlayer()  # NEW
    
    def send_via_windows_speaker(self, message: str) -> bool:
        """Play audio on Windows laptop speakers"""
        try:
            self.windows_player.speak(message)
            return True
        except:
            return False
    
    async def _deliver_alert(self, alert: Dict) -> bool:
        channels = alert['channels']
        
        for channel in channels:
            if channel == "windows_audio":  # NEW
                success = self.send_via_windows_speaker(alert['message'])
            elif channel == "text":
                success = self.send_via_telegram_text(alert['message'])
            # REMOVED: voice channel (no more voice files)
```

### 3.3 UPDATE: Channel Routing Logic

```python
def _get_channels_for_priority(self, priority: AlertPriority):
    if priority == AlertPriority.CRITICAL:
        return ["windows_audio", "text"]  # Both
    elif priority == AlertPriority.HIGH:
        return ["windows_audio", "text"]  # Both
    else:
        return ["text"]  # Phone only
```

---

## 4. File Structure

```
src/modules/
├── voice_alert_system.py (MODIFIED)
├── windows_audio_player.py (NEW)
└── fixed_clock_system.py (NO CHANGE)

scripts/
└── test_windows_audio.py (NEW - for verification)
```

---

## 5. Testing Strategy

### Test 1: Windows Speaker Audio
**Script:** `scripts/test_windows_audio.py`
```python
from src.modules.windows_audio_player import WindowsAudioPlayer

player = WindowsAudioPlayer()
player.speak("This is a test of the Windows audio system")
```
**Expected:** Hear audio from laptop speakers immediately.

### Test 2: Phone Notification
**Action:** Lock phone, trigger CRITICAL alert
**Expected:** Hear Telegram notification sound (even with phone locked)

### Test 3: Chat Verification
**Action:** Open Telegram chat after alerts
**Expected:** See only text messages, NO voice files

---

## 6. Deployment Steps

1. Install `pyttsx3`:
   ```bash
   pip install pyttsx3
   ```

2. Create `WindowsAudioPlayer` module

3. Update `VoiceAlertSystem`

4. Run test script to verify Windows audio

5. Trigger live alert to verify phone notification

---

## 7. Rollback Plan

If Windows audio fails:
1. Comment out `windows_audio` channel
2. Revert to text-only notifications
3. Investigate `pyttsx3` initialization error

---

## 8. Success Criteria

- ✅ Alert triggers → Laptop speakers play TTS audio
- ✅ Alert triggers → Phone receives Telegram notification (with sound)
- ✅ Chat contains ONLY text messages (NO voice files)
- ✅ Works with phone locked
- ✅ Works with Telegram closed on laptop

---

**Awaiting User Approval to Proceed with Implementation.**

*End of Implementation Plan*
