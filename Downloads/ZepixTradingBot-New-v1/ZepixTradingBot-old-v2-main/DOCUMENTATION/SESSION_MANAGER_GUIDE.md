# SESSION MANAGER GUIDE v2.0

## 1. Overview
The Session Manager is a strict enforcement system that ensures the bot only trades during specific Forex sessions and only with authorized currency pairs.

**Key Features:**
- **Zero Tolerance Timing:** Trades are blocked the second a session ends.
- **Symbol Whitelisting:** Specific pairs allowed per session.
- **Auto-Close:** Positions force-closed at session end (Optional).
- **Telegram UI:** Full control via buttons (No typing).

---

## 2. Session Rules (Strict)

| Session | Time (IST) | Allowed Symbols (Strict) |
| :--- | :--- | :--- |
| **Asian** | 06:00 - 13:30 | USDJPY, AUDJPY, AUDUSD, NZDUSD |
| **London** | 13:30 - 22:30 | EURUSD, GBPUSD, EURGBP, GBPJPY, EURJPY, XAUUSD |
| **Overlap** | 18:30 - 22:30 | EURUSD, GBPUSD, XAUUSD, USDJPY |
| **NY Late** | 22:30 - 02:30 | USDJPY, XAUUSD, USDCAD |
| **Dead Zone** | 02:30 - 06:00 | **NO TRADING** (All Blocked) |

---

## 3. How to Use (No Typing Required)

### 3.1 Accessing the Menu
1.  Open Telegram Bot.
2.  Click **"🕒 Sessions"** button (Main Menu or Bottom Menu).
3.  The **Session Dashboard** will appear.

### 3.2 Dashboard Features
*   **Status View:** Shows Current Session, Time, and Active/Blocked Symbols.
*   **Master Switch:** Toggle ALL trading ON/OFF with one click.
*   **Edit Sessions:** Click to modify specific session rules.

### 3.3 Editing a Session
1.  Select a Session (e.g., "London").
2.  **Toggle Symbols:** Click buttons like `✅ EURUSD` to allowed/block pairs.
3.  **Adjust Time:** Use `-30m` / `+30m` buttons to tweak Start/End times.
4.  **Force Close:** Toggle `✅ Force Close` to auto-exit trades when session ends.

---

## 4. Live Pinned Header 📌
The bot pins a message to the top of your chat that updates every second:
> 🕐 **Current Time:** 14:15:00 IST
> 🟢 **Session:** London (13:30 - 22:30) | ✅ EURUSD, GBPUSD...

This lets you know exactly which session is active without checking commands.
