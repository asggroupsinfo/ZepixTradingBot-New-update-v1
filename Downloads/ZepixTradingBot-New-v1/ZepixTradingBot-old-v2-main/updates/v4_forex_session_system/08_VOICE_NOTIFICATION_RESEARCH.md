# Voice Notification System - Research Document
*Date: 2026-01-12 | Status: RESEARCH PHASE*

## 1. User Requirement (Actual)

**Problem Statement:**
Current system sends voice files to Telegram chat which requires opening the app to hear. User needs:
1. **Windows Laptop:** Audio plays directly from speakers (like alarm/ringtone) - works even if Telegram closed
2. **Phone:** Telegram notification sound (NOT voice file in chat) - works even if phone locked

**Use Case:**
> Bot generates alert → Laptop speakers immediately play TTS audio → Phone receives Telegram notification (with sound) → User hears both without opening any app

---

## 2. Windows Audio Libraries Comparison

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| **pyttsx3** | ✅ Offline TTS<br>✅ No internet needed<br>✅ Works on lock screen | ❌ Voice quality moderate | **RECOMMENDED** |
| **playsound** | ✅ Simple MP3 playback<br>✅ Lightweight | ❌ Requires pre-generated files | Backup option |
| **winsound** | ✅ Built-in (no install) | ❌ Only .wav files<br>❌ No TTS | Not suitable |
| **pygame.mixer** | ✅ Advanced audio control | ❌ Overkill for our use | Not needed |

**Selected:** `pyttsx3` for real-time TTS playback on Windows speakers.

---

## 3. Phone Notification Mechanism

**Current Issue:**
- `bot.send_voice()` sends voice file to chat (requires opening Telegram)

**Solution:**
- `bot.send_message()` with `disable_notification=False` (default)
- Telegram app on phone will:
  - Show notification banner
  - Play notification sound (even if locked)
  - User hears alert WITHOUT opening app

**Key:** Remove voice file sending, keep only text notifications.

---

## 4. Technical Architecture

### Current Flow (WRONG):
```
Bot Alert → VoiceAlertSystem → Generate TTS MP3 → Send to Telegram Chat
```
**Problem:** Voice only accessible in chat.

### New Flow (CORRECT):
```
Bot Alert → VoiceAlertSystem → Split into TWO channels:
  ├─ Channel 1 (Windows): pyttsx3.speak() → Laptop speakers
  └─ Channel 2 (Phone): bot.send_message() → Telegram notification sound
```

**Benefits:**
- ✅ Laptop: Direct audio (no Telegram needed)
- ✅ Phone: Notification sound (even if locked)
- ✅ No voice files cluttering chat

---

## 5. Implementation Strategy

### Step 1: Install Dependencies
```bash
pip install pyttsx3
```

### Step 2: Create `WindowsAudioPlayer` Module
- Location: `src/modules/windows_audio_player.py`
- Purpose: Play TTS audio directly on Windows speakers
- Method: `speak(text)` → Immediate audio playback

### Step 3: Update `VoiceAlertSystem`
- Remove: `send_via_telegram_voice()` logic
- Add: `send_via_windows_speaker()` logic
- Update: `send_via_telegram_text()` to ensure notifications enabled

### Step 4: Route Alerts
- **CRITICAL/HIGH Priority:** Windows speaker + Telegram text
- **MEDIUM/LOW Priority:** Telegram text only

---

## 6. Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| `pyttsx3` fails to initialize | High | Fallback to `playsound` with pre-generated MP3 |
| Windows speaker muted | Medium | Log warning, continue with Telegram |
| Phone notifications disabled | Low | User responsibility (Telegram settings) |

---

## 7. Testing Plan

1. **Windows Audio Test:**
   ```python
   python scripts/test_windows_audio.py
   ```
   - Expected: Hear TTS from laptop speakers

2. **Phone Notification Test:**
   - Lock phone
   - Trigger bot alert
   - Expected: Hear Telegram notification sound

3. **Chat Verification:**
   - Open Telegram chat
   - Expected: NO voice files, only text messages

---

## 8. Next Steps

1. Create implementation plan document
2. User review & approval
3. Implement `WindowsAudioPlayer`
4. Update `VoiceAlertSystem`
5. Test & verify

---
*End of Research Document*
