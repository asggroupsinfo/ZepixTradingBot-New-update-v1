# VOICE ALERT SYSTEM CONFIGURATION v2.0

## 1. Overview
The Voice Alert System converts trading signals and critical errors into speech, allowing you to monitor the bot without looking at the screen. 

**New in v2.0:**
- **Indian Accent (Hinglish):** Optimized for clear pronunciation.
- **All Priorities:** Voice alerts now active for Low, Medium, High, and Critical events.
- **Test Button:** Instant audio check via Telegram.

---

## 2. Configuration (`config.json`)

To enable voice alerts, ensure your `config.json` has:
```json
"voice_alerts": {
    "enabled": true,
    "language": "en",
    "tld": "co.in",  // "co.in" = Indian Accent
    "rate": 1.0,     // Speed (0.5 - 2.0)
    "priority_level": "LOW" // Minimum level to trigger voice
}
```

---

## 3. Usage & Testing

### 3.1 How to Test Voice
1.  Open Telegram Bot.
2.  Click **"🎙️ Voice Test"** button (Quick Actions).
3.  **Result:** You should receive a voice file saying: *"This is a test of the Zepix Voice Alert System..."*

### 3.2 Alert Priorities
| Level | Channels | Example Scenario |
| :--- | :--- | :--- |
| **CRITICAL** | Voice + Text + SMS | Crash, Stop Loss Failure |
| **HIGH** | Voice + Text | Trade Entry, TP Hit |
| **MEDIUM** | Voice + Text | Warning, Watchlist Alert |
| **LOW** | Voice + Text | General Info, System Start |

*Note: Critical alerts map to SMS only if `sms_enabled` is true in config.*
