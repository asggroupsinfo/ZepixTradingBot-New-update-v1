# ZEPIX BOT UI NAVIGATION GUIDE v2.0

## 1. Introduction
Zepix Bot v2.0 introduces a **Zero-Typing Interface**. You can control 100% of the bot's features using interactve buttons and menus.

---

## 2. The Two Menu Types

### 2.1 The Main Menu (Inline Buttons)
This appears visibly inside the chat message when you send `/start` or click **Refresh**.

| Row | Buttons | Function |
| :--- | :--- | :--- |
| **Quick Actions** | `📊 Dashboard` `⏸️ Pause` `🎙️ Voice` `⏰ Clock` | One-tap access to status & tools. |
| **Trading** | `💰 Trading` `🕒 Sessions` | Trade controls & Session Manager. |
| **Analysis** | `⏱️ Timeframe` `⚡ Performance` | TF settings & PnL reports. |
| **Management** | `🔄 Re-entry` `📍 Trends` | Auto-recovery & Trend Matrix. |
| **Risk** | `🛡️ Risk` `⚙️ SL System` | Risk settings & Stop-loss logic. |
| **Wallet** | `💎 Orders` `📈 Profit` | Active orders & Profit booking. |
| **System** | `🔧 Settings` `🔍 Diagnostics` | Config & Logs. |

### 2.2 The Persistent Menu (Dogal/Toggle)
This is the fixed keyboard at the bottom of your screen (where you usually type).

*   **Row 1:** `📊 Dashboard` | `⏸️ Pause/Resume` | `🕒 Sessions`
*   **Row 2:** `📈 Active Trades` | `🛡️ Risk` | `🎙️ Voice`
*   **Row 3:** `🔄 Re-entry` | `⚙️ SL System` | `📍 Trends`
*   **Row 4:** `📈 Profit` | `🆘 Help`
*   **Row 5:** `🚨 PANIC CLOSE` (Emergency Button)

---

## 3. Special Features

### 🕒 Session Manager Dashboard
*   **Access:** Click `🕒 Sessions` button.
*   **Use:** Toggle Master Switch, Edit Allowed Symbols per session, Change Times.
*   **Note:** Changes apply instantly to the trading engine.

### 📌 Live Pinned Header
*   Look at the **top of your Telegram chat**.
*   You will see a pinned message like:
    > 🕐 14:30:05 IST | 📅 12 Jan 2026
    > 🟢 Session: London | ✅ EURUSD, GBPUSD
*   This removes the need to constantly check `/status` for time/session info.

---

## 4. Troubleshooting
*   **Buttons not working?** Send `/start` to refresh the bot's internal state.
*   **Menu disappeared?** Click the small "grid" icon in your text input bar to toggle the persistent menu.
