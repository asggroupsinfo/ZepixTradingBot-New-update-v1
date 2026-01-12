# Telegram Integration & Enhanced Notification Plan

This document outlines the extracted specifications for the Telegram integration, strictly based on the "ZepixTradingBot - Enhanced Autonomous System Plan". It focuses on the "Zero-Typing" interface, enhanced notifications, and menu systems.

---

## 1️⃣ Zero-Typing Menu System (Button-Based)

The goal is to eliminate manual command typing by using a comprehensive button-based menu structure.

### 🏠 Main Menu Structure
The root menu providing access to all major subsystems.

| Button Label | Action/Description |
| :--- | :--- |
| **📊 Dashboard** | View live bot status and P&L. |
| **⏸ Pause/Resume** | Toggle global trading activity. |
| **🔄 Re-entry System ➡** | Access Re-entry & Autonomous settings. |
| **📈 Profit Booking ➡** | Access Profit Booking & Pyramid settings. |
| **⚙ SL System Control ➡** | Manage Stop Loss configurations. |
| **⚡ Fine-Tune Settings ➡** | **(NEW)** Access advanced tuning (Protection, Reduction, etc.). |

---

### 🔄 Re-entry System Submenu
Controls for the new Autonomous and Recovery logic.

*   **🤖 Autonomous Mode**: `[ON✅/OFF]` - Toggles fully autonomous decision making.
*   **🎯 TP Continuation**: `[ON✅/OFF]` - Toggles auto-scaling after TP hit.
*   **🛡 SL Hunt**: `[ON✅/OFF]` - Toggles SL Hunt Re-entry logic.
*   **🔄 Exit Continuation**: `[ON✅/OFF]` - Toggles re-entry after manual/reversal exit.
*   **📊 View Status**: Dispay current chains and levels.
*   **⚙ Advanced Settings ➡**: Deep dive settings.
*   **🏠 Back to Main Menu**

---

### 📈 Profit Booking Submenu
Controls for the Pyramid/Order B system.

*   **🛡 Profit Protection**: `[ON✅/OFF]` - Toggles profit protection logic.
*   **📊 Active Chains**: View current order B chains.
*   **💎 SL Hunt Status**: View recovery status for profit orders.
*   **⚙ SL Mode**: `[SL-1.1]` / `[SL-2.1]` - Toggle Logic-based vs Fixed SL.
*   **📈 View Config**: Show current schema settings.
*   **🏠 Back to Main Menu**

---

### ⚡ Fine-Tune Settings Submenu (New)
Central hub for advanced parameter optimization.

*   **💰 Profit Protection ➡**: Configure protection multipliers.
*   **📉 SL Reduction ➡**: Configure SL stepping strategies.
*   **🔍 Recovery Windows ➡**: Configure symbol-specific recovery timeouts.
*   **📊 View All Settings**: Summary of all fine-tune (FT) knobs.
*   **🏠 Back to Main Menu**

#### A. 💰 Profit Protection Menu
Configure how the bot protects accumulated profits.

**Modes:**
1.  **⚡ Aggressive (3.5x)**: Frequent recoveries, higher risk.
2.  **⚖ Balanced (6.0x)**: (Default) Recommended balance.
3.  **🛡 Conservative (9.0x)**: Protect functionality over recovery.
4.  **🔒 Very Conservative (15.0x)**: Maximum safety.

**Switches:**
*   **📝 Order A Protection**: `[ON✅/OFF]`
*   **📝 Order B Protection**: `[ON✅/OFF]`

**Actions:**
*   **📊 View Current Stats**
*   **📖 Detailed Guide**

#### B. 📉 SL Reduction Optimizer Menu
Configure how SL tightens on subsequent levels.

**Strategies:**
1.  **⚡ Aggressive (40%)**: Tight stops, good for trending markets.
2.  **⚖ Balanced (30%)**: (Default) Standard reduction.
3.  **🛡 Conservative (20%)**: Wide stops, choppy markets.
4.  **🎯 Adaptive**: Symbol-specific optimization.

**Adaptive Settings (Symbol Specific):**
*   Interface to adjust reduction % per symbol (e.g., `XAUUSD: 35%`, `EURUSD: 25%`).
*   Controls: `⬇` (Decrease 1%), `⬆` (Increase 1%).
*   Range: 10% - 50%.

#### C. 🔍 Recovery Windows
*   View/Edit symbol specific recovery timeout windows (e.g., `XAUUSD: 15m`, `EURUSD: 30m`).

---

## 2️⃣ SL Systems Control (Dual Mode)

Quick switches for defining SL behavior.

### Order A (TP Trail)
*   **Switch**: Change between **SL-1 (Safe/Wide)** and **SL-2 (Tight/Aggressive)**.

### Order B (Profit Booking)
*   **Switch**: Change between **SL-1.1 (Logic-Specific)** and **SL-2.1 (Fixed Universal)**.

---

## 3️⃣ Enhanced Notifications

Rich, emoji-driven notifications for key autonomous events.

### 🚀 TP Continuation Notification
Triggered when a chain progresses to the next level after a TP hit.

```text
🚀 *AUTONOMOUS RE-ENTRY* 🚀
━━━━━━━━━━━━━━━━━━━━━━━━
Symbol: XAUUSD (BUY)
Type: TP Continuation
Progress: Level 1 ➡ Level 2
📍 ENTRY DETAILS
Entry: 2650.50
SL: 2645.00 (55 pips - 30% reduced)
TP: 2660.00 (RR 1.5:1)
✅ CHECKS PASSED
• Trend: BULLISH 🟢
• Alignment: 98% ✅
• Cooldown: 5s Complete ✅
• Momentum: Strong ⬆
⏱ TIMING
Placed: 14:32:15 UTC
Prev TP Hit: 14:32:10 UTC
🎯 CHAIN STATUS
Level: 2/5
Total Profit: +$45.00
Status: ACTIVE 🟢
━━━━━━━━━━━━━━━━━━━━━━━━
```

### 🛡 SL Hunt Re-Entry Notification
Triggered when an SL Hunt recovery order is placed.

```text
🛡 *SL HUNT ACTIVATED* 🛡
━━━━━━━━━━━━━━━━━━━━━━━━
Symbol: GBPUSD (SELL)
Type: Recovery Entry
Attempt: 1/1
⚠ ORIGINAL LOSS
SL Hit: 1.2750
Loss: -$25.00
Time: 14:30:05 UTC
📍 RECOVERY ENTRY
Entry: 1.2748 (2 pips recovery)
SL: 1.2753 (5 pips - Tight)
TP: 1.2730 (RR 3.6:1)
✅ SAFETY CHECKS
• Price Recovery: ✅ Confirmed
• Trend: Still BEARISH 🔴
• ATR: Low (Stable) ✅
• Alignment: 95% ✅
⏱ RECOVERY TIME
SL Hit → Recovery: 45 seconds
Status: RECOVERING LOSS 🔄
💪 CHAIN CONTINUATION
If Success: Resume → Level 2
If Fail: Chain STOP ❌
━━━━━━━━━━━━━━━━━━━━━━━━
```

### 💎 Order B Profit Protection Notification
Triggered when a Profit Booking order (Order B) enters recovery mode.

```text
💎 *PROFIT ORDER PROTECTION* 💎
━━━━━━━━━━━━━━━━━━━━━━━━
Chain: #EURUSD_a7b3
Level: 2/4 (Order 3/4)
⚠ SL HIT DETECTED
Order ID: #453621
Loss: -$10.00
SL Price: 1.1045
🔄 MONITORING ACTIVE
Current Price: 1.1046
Recovery Gap: +1 pip
Trend: BULLISH 🟢
━━━━━━━━━━━━━━━━━━━━━━━━
```

### ✅ Recovery Success Notification
Triggered when an SL Hunt trade hits TP.

```text
✅ PRICE RECOVERED - IMMEDIATE ACTION!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order: #12345
Symbol: XAUUSD
Recovery Price: 2642.00
Current Price: 2642.10
Recovery Time: 4.5 seconds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Placing Recovery Order NOW...
```

### ⏰ Recovery Timeout Notification
Triggered when the recovery window expires without price recovery.

```text
⏰ RECOVERY WINDOW TIMEOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order: #12345
Elapsed: 15.0 minutes
Max Window: 15.0 minutes
Status: FAILED - No recovery detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4️⃣ Configuration Switches & Guides

### Profit Protection Guide (In-App)
Pop-up message explaining the feature.
> **Current Mode**: ⚖ BALANCED
> **Multiplier**: 6.0x
> **Rule**: Chain Profit > (Loss × 6.0)

### Toggle logic
*   All boolean toggles (ON/OFF) must update the config in real-time without restart.
*   Mode switches (Aggressive/Balanced/etc.) must persist to JSON.

---

## Implementation Requirements
1.  **Menu Handler**: Extensions to `MenuManager` to handle new callback queries (`ft_`, `pp_`, `slr_`).
2.  **Notification Service**: New templates in `TelegramNotifier`.
3.  **Config Manager**: Updates to support `profit_protection` and `sl_reduction` keys.
