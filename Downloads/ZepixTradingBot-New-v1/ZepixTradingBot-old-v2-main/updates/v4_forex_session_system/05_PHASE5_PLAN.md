# Phase 5 Implementation Plan: Voice Alert System

**Date:** 2026-01-11  
**Mode:** PLANNING → EXECUTION  
**Focus:** Multi-channel alert delivery with voice messages, retry queue, and failover

---

## Objective

Create a robust voice alert system that:
- Delivers voice messages via Telegram (even when phone is off/locked)
- Falls back to text/SMS on failure
- Implements priority-based routing
- Uses retry queue with exponential backoff
- Integrates with Session Manager for session transition alerts

---

## Proposed Changes

### 1. Create `src/modules/voice_alert_system.py` (NEW)
**Purpose:** Multi-channel notification delivery with retry mechanism

**Features:**
- Voice message generation (TTS via gTTS)
- Alert priority levels (CRITICAL, HIGH, MEDIUM, LOW)
- Multi-channel delivery (Voice → Text → SMS)
- Retry queue with exponential backoff
- Async processing

**Alert Channels by Priority:**
- CRITICAL: Voice + Text + SMS
- HIGH: Voice + Text
- MEDIUM: Voice
- LOW: Text only

---

## Dependencies

**New Libraries:**
- `gTTS` - Google Text-to-Speech for voice generation
- (Optional) `twilio` or `sns` - for SMS fallback

**Install Command:**
```bash
pip install gtts
```

---

## Implementation Details

### Alert Priority Enum
```python
CRITICAL - System crashes, major losses
HIGH - Order execution, trade opened/closed
MEDIUM - SL/TP hits, session alerts
LOW - Info messages, status updates
```

### Voice Message Flow
1. User action triggers alert
2. Alert queued with priority
3. TTS generates voice file (gTTS)
4. Telegram sends voice message
5. On failure → retry (max 3 attempts)
6. On final failure → fallback to text/SMS

---

## Success Criteria

- ✅ Voice messages deliver successfully
- ✅ TTS audio quality acceptable
- ✅ Queue processes in priority order
- ✅ Retry mechanism works (3 attempts max)
- ✅ Fallback to text on voice failure
- ✅ Works when phone is locked/off
- ✅ No memory leaks during extended operation
- ✅ 100% unit test coverage

---

**Ready for implementation.**
