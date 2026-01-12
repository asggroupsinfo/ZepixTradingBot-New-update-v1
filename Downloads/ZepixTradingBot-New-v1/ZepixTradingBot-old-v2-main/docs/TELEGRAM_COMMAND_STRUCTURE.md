# 🤖 ZEPIX TRADING BOT - COMPLETE TELEGRAM COMMAND STRUCTURE

**Total Commands: 81 Commands across 10 Categories**  
**Generated: 25-Nov-2025 23:42 IST**

---

## 📋 TABLE OF CONTENTS

1. [💰 Trading Control (6 Commands)](#1--trading-control-6-commands)
2. [⚡ Performance & Analytics (6 Commands)](#2--performance--analytics-6-commands)
3. [⚙️ Strategy Control (7 Commands)](#3-️-strategy-control-7-commands)
4. [🔄 Re-entry System (12 Commands)](#4--re-entry-system-12-commands)
5. [📍 Trend Management (5 Commands)](#5--trend-management-5-commands)
6. [🛡️ Risk & Lot Management (11 Commands)](#6-️-risk--lot-management-11-commands)
7. [⚙️ SL System Control (8 Commands)](#7-️-sl-system-control-8-commands)
8. [💎 Dual Orders (2 Commands)](#8--dual-orders-2-commands)
9. [📈 Profit Booking (15 Commands)](#9--profit-booking-15-commands)
10. [🔍 Diagnostics & Health (15 Commands)](#10--diagnostics--health-15-commands)

---

## 🎯 QUICK ACCESS BUTTONS (Always Available)

### Main Menu → Quick Actions
```
┌─────────────────────────────────────┐
│  🏠 MAIN MENU                       │
├─────────────────────────────────────┤
│  📊 Dashboard      (Direct Action)  │
│  ⏸️ Pause/Resume   (Direct Toggle)  │
│  📈 Trades         (Direct View)    │
│  💰 Performance    (Direct View)    │
└─────────────────────────────────────┘
```

---

## 1. 💰 TRADING CONTROL (6 Commands)

### Command Flow Structure:

#### 1.1 `/pause` - Pause Trading
```
Main Menu → Trading Control → Pause
└─ Button: "⏸️ Pause Trading"
   └─ Confirmation: "Confirm Pause?"
      └─ Execute: handle_pause()
         └─ Result: "Trading PAUSED ⏸️"
```
**Steps to Execute:** MAIN MENU → TRADING → PAUSE → CONFIRM (3 clicks)  
**Type:** Direct (No Parameters)  
**Handler:** `handle_pause()`

---

#### 1.2 `/resume` - Resume Trading
```
Main Menu → Trading Control → Resume
└─ Button: "▶️ Resume Trading"
   └─ Confirmation: "Confirm Resume?"
      └─ Execute: handle_resume()
         └─ Result: "Trading RESUMED ✅"
```
**Steps to Execute:** MAIN MENU → TRADING → RESUME → CONFIRM (3 clicks)  
**Type:** Direct (No Parameters)  
**Handler:** `handle_resume()`

---

#### 1.3 `/status` - Bot Status
```
Main Menu → Trading Control → Status
└─ Button: "📊 Status"
   └─ Execute: handle_status()
      └─ Result: Shows full bot status
```
**Steps to Execute:** MAIN MENU → TRADING → STATUS (2 clicks)  
**Type:** Direct (No Parameters)  
**Handler:** `handle_status()`

---

#### 1.4 `/trades` - View Open Trades
```
Main Menu → Trading Control → Trades
└─ Button: "📈 Trades"
   └─ Execute: handle_trades()
      └─ Result: List of open trades
```
**Steps to Execute:** MAIN MENU → TRADING → TRADES (2 clicks)  
**Type:** Direct (No Parameters)  
**Handler:** `handle_trades()`

---

#### 1.5 `/signal_status` - Current Signals
```
Main Menu → Trading Control → Signal Status
└─ Button: "📡 Signal Status"
   └─ Execute: handle_signal_status()
      └─ Result: Shows all symbol signals (5m, 15m, 1h, 1d)
```
**Steps to Execute:** MAIN MENU → TRADING → SIGNAL STATUS (2 clicks)  
**Type:** Direct (No Parameters)  
**Handler:** `handle_signal_status()`

---

#### 1.6 `/simulation_mode` - Toggle Simulation
```
Main Menu → Trading Control → Simulation Mode
└─ Button: "🔄 Simulation Mode"
   ├─ Select Mode:
   │  ├─ "status" → Show current mode
   │  ├─ "on"     → Enable simulation
   │  └─ "off"    → Disable simulation
   └─ Confirmation Screen
      └─ Execute: handle_simulation_mode(mode)
         └─ Result: "Simulation Mode: [ON/OFF]"
```
**Steps to Execute:** MAIN MENU → TRADING → SIMULATION → SELECT MODE → CONFIRM (4 clicks)  
**Type:** Single Parameter  
**Parameters:** mode (status/on/off)  
**Handler:** `handle_simulation_mode()`

---

## 2. ⚡ PERFORMANCE & ANALYTICS (6 Commands)

#### 2.1 `/performance` - Performance Summary
```
Main Menu → Performance → Performance
└─ Button: "📈 Performance"
   └─ Execute: handle_performance()
      └─ Result: Win rate, PnL, daily/lifetime stats
```
**Steps:** MAIN MENU → PERFORMANCE → PERFORMANCE (2 clicks)  
**Type:** Direct  
**Handler:** `handle_performance()`

---

#### 2.2 `/stats` - Risk Stats
```
Main Menu → Performance → Stats
└─ Button: "📊 Stats"
   └─ Execute: handle_stats()
      └─ Result: Risk tier, loss limits, lot size
```
**Steps:** MAIN MENU → PERFORMANCE → STATS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_stats()`

---

#### 2.3 `/performance_report` - 30-Day Report
```
Main Menu → Performance → Performance Report
└─ Button: "📊 Performance Report"
   └─ Execute: handle_performance_report()
      └─ Result: 30-day analytics
```
**Steps:** MAIN MENU → PERFORMANCE → PERFORMANCE REPORT (2 clicks)  
**Type:** Direct  
**Handler:** `handle_performance_report()`

---

#### 2.4 `/pair_report` - Symbol Performance
```
Main Menu → Performance → Pair Report
└─ Button: "📈 Pair Report"
   └─ Execute: handle_pair_report()
      └─ Result: Per-symbol statistics
```
**Steps:** MAIN MENU → PERFORMANCE → PAIR REPORT (2 clicks)  
**Type:** Direct  
**Handler:** `handle_pair_report()`

---

#### 2.5 `/strategy_report` - Strategy Analytics
```
Main Menu → Performance → Strategy Report
└─ Button: "🤖 Strategy Report"
   └─ Execute: handle_strategy_report()
      └─ Result: Per-logic performance
```
**Steps:** MAIN MENU → PERFORMANCE → STRATEGY REPORT (2 clicks)  
**Type:** Direct  
**Handler:** `handle_strategy_report()`

---

#### 2.6 `/chains` - Re-entry Chains Status
```
Main Menu → Performance → Chains
└─ Button: "🔗 Chains"
   └─ Execute: handle_chains_status()
      └─ Result: Active re-entry chains
```
**Steps:** MAIN MENU → PERFORMANCE → CHAINS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_chains_status()`

---

## 3. ⚙️ STRATEGY CONTROL (7 Commands)

#### 3.1 `/logic_status` - All Logics Status
```
Main Menu → Strategy → Logic Status
└─ Button: "📊 Logic Status"
   └─ Execute: handle_logic_status()
      └─ Result: LOGIC1/2/3 enabled/disabled status
```
**Steps:** MAIN MENU → STRATEGY → LOGIC STATUS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_logic_status()`

---

#### 3.2-3.7 Logic Control Commands
```
Main Menu → Strategy → Logic Control
└─ Submenu:
   ├─ LOGIC1
   │  ├─ "✅ Enable LOGIC1"  → handle_logic1_on()
   │  │  └─ Result: "✅ LOGIC 1 TRADING ENABLED"
   │  └─ "⛔ Disable LOGIC1" → handle_logic1_off()
   │     └─ Result: "⛔ LOGIC 1 TRADING DISABLED"
   ├─ LOGIC2
   │  ├─ "✅ Enable LOGIC2"  → handle_logic2_on()
   │  │  └─ Result: "✅ LOGIC 2 TRADING ENABLED"
   │  └─ "⛔ Disable LOGIC2" → handle_logic2_off()
   │     └─ Result: "⛔ LOGIC 2 TRADING DISABLED"
   └─ LOGIC3
      ├─ "✅ Enable LOGIC3"  → handle_logic3_on()
      │  └─ Result: "✅ LOGIC 3 TRADING ENABLED"
      └─ "⛔ Disable LOGIC3" → handle_logic3_off()
         └─ Result: "⛔ LOGIC 3 TRADING DISABLED"
```

**All Commands:**
- `/logic1_on` - Steps: MAIN MENU → STRATEGY → LOGIC CONTROL → ENABLE LOGIC1 (3 clicks)
- `/logic1_off` - Steps: MAIN MENU → STRATEGY → LOGIC CONTROL → DISABLE LOGIC1 (3 clicks)
- `/logic2_on` - Steps: MAIN MENU → STRATEGY → LOGIC CONTROL → ENABLE LOGIC2 (3 clicks)
- `/logic2_off` - Steps: MAIN MENU → STRATEGY → LOGIC CONTROL → DISABLE LOGIC2 (3 clicks)
- `/logic3_on` - Steps: MAIN MENU → STRATEGY → LOGIC CONTROL → ENABLE LOGIC3 (3 clicks)
- `/logic3_off` - Steps: MAIN MENU → STRATEGY → LOGIC CONTROL → DISABLE LOGIC3 (3 clicks)

**Type:** All Direct (No Parameters)
**Status:** ✅ **FIXED** - Commands now display proper confirmation messages and don't show generic success screen
**Handler Response:** Commands send their own status messages, then auto-return to main menu after 3 seconds

---

## 4. 🔄 RE-ENTRY SYSTEM (12 Commands)

#### 4.1 `/tp_system` - TP Re-entry Control
```
Main Menu → Re-entry → TP System
└─ Button: "🎯 TP System"
   ├─ Select Mode:
   │  ├─ "status" → Show current status
   │  ├─ "on"     → Enable TP re-entry
   │  └─ "off"    → Disable TP re-entry
   └─ Confirmation
      └─ Execute: handle_tp_system(mode)
```
**Steps:** MAIN MENU → RE-ENTRY → TP SYSTEM → MODE → CONFIRM (4 clicks)  
**Parameters:** mode (status/on/off)  
**Handler:** `handle_tp_system()`

---

#### 4.2 `/sl_hunt` - SL Hunt Re-entry
```
Main Menu → Re-entry → SL Hunt
└─ Button: "🎯 SL Hunt"
   ├─ Select Mode:
   │  ├─ "status" → Show current status
   │  ├─ "on"     → Enable SL hunt
   │  └─ "off"    → Disable SL hunt
   └─ Confirmation
      └─ Execute: handle_sl_hunt(mode)
```
**Steps:** MAIN MENU → RE-ENTRY → SL HUNT → MODE → CONFIRM (4 clicks)  
**Parameters:** mode (status/on/off)  
**Handler:** `handle_sl_hunt()`

---

#### 4.3 `/exit_continuation` - Exit Continuation
```
Main Menu → Re-entry → Exit Continuation
└─ Button: "🔄 Exit Continuation"
   ├─ Select Mode:
   │  ├─ "status" → Show current status
   │  ├─ "on"     → Enable continuation
   │  └─ "off"    → Disable continuation
   └─ Confirmation
      └─ Execute: handle_exit_continuation(mode)
```
**Steps:** MAIN MENU → RE-ENTRY → EXIT CONTINUATION → MODE → CONFIRM (4 clicks)  
**Parameters:** mode (status/on/off)  
**Handler:** `handle_exit_continuation()`

---

#### 4.4 `/tp_report` - TP Re-entry Report
```
Main Menu → Re-entry → TP Report
└─ Button: "📊 TP Report"
   └─ Execute: handle_tp_report()
      └─ Result: TP re-entry statistics
```
**Steps:** MAIN MENU → RE-ENTRY → TP REPORT (2 clicks)  
**Type:** Direct  
**Handler:** `handle_tp_report()`

---

#### 4.5 `/reentry_config` - View Config
```
Main Menu → Re-entry → Config
└─ Button: "⚙️ Config"
   └─ Execute: handle_reentry_config()
      └─ Result: All re-entry settings
```
**Steps:** MAIN MENU → RE-ENTRY → CONFIG (2 clicks)  
**Type:** Direct  
**Handler:** `handle_reentry_config()`

---

#### 4.6 `/set_monitor_interval` - Set Monitor Interval
```
Main Menu → Re-entry → Set Monitor Interval
└─ Button: "⏱️ Monitor Interval"
   ├─ Select Preset:
   │  ├─ "30s"
   │  ├─ "60s"
   │  ├─ "120s"
   │  ├─ "300s"
   │  ├─ "600s"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_monitor_interval(value)
```
**Steps:** MAIN MENU → RE-ENTRY → INTERVAL → VALUE → CONFIRM (4 clicks)  
**Parameters:** value (30-600 seconds)  
**Presets:** 30, 60, 120, 300, 600  
**Handler:** `handle_set_monitor_interval()`

---

#### 4.7 `/set_sl_offset` - Set SL Hunt Offset
```
Main Menu → Re-entry → Set SL Offset
└─ Button: "📏 SL Offset"
   ├─ Select Preset:
   │  ├─ "1 pip"
   │  ├─ "2 pips"
   │  ├─ "3 pips"
   │  ├─ "4 pips"
   │  ├─ "5 pips"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_sl_offset(value)
```
**Steps:** MAIN MENU → RE-ENTRY → SL OFFSET → VALUE → CONFIRM (4 clicks)  
**Parameters:** value (1-5 pips)  
**Handler:** `handle_set_sl_offset()`

---

#### 4.8 `/set_cooldown` - Set Cooldown Time
```
Main Menu → Re-entry → Set Cooldown
└─ Button: "⏱️ Cooldown"
   ├─ Select Preset:
   │  ├─ "30s"
   │  ├─ "60s"
   │  ├─ "120s"
   │  ├─ "300s"
   │  ├─ "600s"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_cooldown(value)
```
**Steps:** MAIN MENU → RE-ENTRY → COOLDOWN → VALUE → CONFIRM (4 clicks)  
**Parameters:** value (30-600 seconds)  
**Handler:** `handle_set_cooldown()`

---

#### 4.9 `/set_recovery_time` - Set Recovery Window
```
Main Menu → Re-entry → Set Recovery Time
└─ Button: "⏱️ Recovery Time"
   ├─ Select Preset:
   │  ├─ "1 min"
   │  ├─ "2 min"
   │  ├─ "5 min"
   │  ├─ "10 min"
   │  ├─ "15 min"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_recovery_time(value)
```
**Steps:** MAIN MENU → RE-ENTRY → RECOVERY → VALUE → CONFIRM (4 clicks)  
**Parameters:** value (1-15 minutes)  
**Handler:** `handle_set_recovery_time()`

---

#### 4.10 `/set_max_levels` - Set Max Chain Levels
```
Main Menu → Re-entry → Set Max Levels
└─ Button: "🔢 Max Levels"
   ├─ Select Preset:
   │  ├─ "1"
   │  ├─ "2"
   │  ├─ "3"
   │  ├─ "4"
   │  ├─ "5"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_max_levels(value)
```
**Steps:** MAIN MENU → RE-ENTRY → MAX LEVELS → VALUE → CONFIRM (4 clicks)  
**Parameters:** value (1-5)  
**Handler:** `handle_set_max_levels()`

---

#### 4.11 `/set_sl_reduction` - Set SL Reduction %
```
Main Menu → Re-entry → Set SL Reduction
└─ Button: "📉 SL Reduction"
   ├─ Select Preset:
   │  ├─ "0.3 (30%)"
   │  ├─ "0.4 (40%)"
   │  ├─ "0.5 (50%)"
   │  ├─ "0.6 (60%)"
   │  ├─ "0.7 (70%)"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_sl_reduction(value)
```
**Steps:** MAIN MENU → RE-ENTRY → SL REDUCTION → VALUE → CONFIRM (4 clicks)  
**Parameters:** value (0.3-0.7)  
**Handler:** `handle_set_sl_reduction()`

---

#### 4.12 `/reset_reentry_config` - Reset to Defaults
```
Main Menu → Re-entry → Reset Config
└─ Button: "🔄 Reset Config"
   └─ Confirmation: "Reset all re-entry settings?"
      └─ Execute: handle_reset_reentry_config()
```
**Steps:** MAIN MENU → RE-ENTRY → RESET → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_reset_reentry_config()`

---

## 5. 📍 TREND MANAGEMENT (5 Commands)

#### 5.1 `/show_trends` - Show Current Trends
```
Main Menu → Trends → Show Trends
└─ Button: "📊 Show Trends"
   └─ Execute: handle_show_trends()
      └─ Result: All symbols with trends
```
**Steps:** MAIN MENU → TRENDS → SHOW (2 clicks)  
**Type:** Direct  
**Handler:** `handle_show_trends()`

---

#### 5.2 `/trend_matrix` - Complete Matrix
```
Main Menu → Trends → Trend Matrix
└─ Button: "🎯 Trend Matrix"
   └─ Execute: handle_trend_matrix()
      └─ Result: Full trend matrix with logic alignments
```
**Steps:** MAIN MENU → TRENDS → MATRIX (2 clicks)  
**Type:** Direct  
**Handler:** `handle_trend_matrix()`

---

#### 5.3 `/set_trend` - Manually Set Trend
```
Main Menu → Trends → Set Trend
└─ Button: "🔒 Set Trend"
   ├─ Select Symbol:
   │  └─ [XAUUSD, EURUSD, GBPUSD, USDJPY, USDCAD, etc.]
   ├─ Select Timeframe:
   │  └─ [1m, 5m, 15m, 1h, 4h, 1d]
   ├─ Select Trend:
   │  └─ [BULLISH, BEARISH, NEUTRAL]
   └─ Confirmation
      └─ Execute: handle_set_trend(symbol, timeframe, trend)
```
**Steps:** MAIN MENU → TRENDS → SET → SYMBOL → TIMEFRAME → TREND → CONFIRM (6 clicks)  
**Parameters:** symbol, timeframe, trend  
**Handler:** `handle_set_trend()`

---

#### 5.4 `/set_auto` - Enable Auto Mode
```
Main Menu → Trends → Set Auto
└─ Button: "🔄 Set Auto"
   ├─ Select Symbol:
   │  └─ [XAUUSD, EURUSD, GBPUSD, etc.]
   ├─ Select Timeframe:
   │  └─ [1m, 5m, 15m, 1h, 4h, 1d]
   └─ Confirmation
      └─ Execute: handle_set_auto(symbol, timeframe)
```
**Steps:** MAIN MENU → TRENDS → AUTO → SYMBOL → TIMEFRAME → CONFIRM (5 clicks)  
**Parameters:** symbol, timeframe  
**Handler:** `handle_set_auto()`

---

#### 5.5 `/trend_mode` - Check Trend Mode
```
Main Menu → Trends → Trend Mode
└─ Button: "❓ Trend Mode"
   ├─ Select Symbol:
   │  └─ [XAUUSD, EURUSD, etc.]
   ├─ Select Timeframe:
   │  └─ [1m, 5m, 15m, 1h, 4h, 1d]
   └─ Execute: handle_trend_mode(symbol, timeframe)
      └─ Result: Shows if MANUAL or AUTO
```
**Steps:** MAIN MENU → TRENDS → MODE → SYMBOL → TIMEFRAME (4 clicks)  
**Parameters:** symbol, timeframe  
**Handler:** `handle_trend_mode()`

---

## 6. 🛡️ RISK & LOT MANAGEMENT (11 Commands)

#### 6.1 `/view_risk_caps` - View Risk Limits
```
Main Menu → Risk → View Risk Caps
└─ Button: "💰 Risk Caps"
   └─ Execute: handle_view_risk_caps()
      └─ Result: Daily/lifetime caps for all tiers
```
**Steps:** MAIN MENU → RISK → CAPS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_view_risk_caps()`

---

#### 6.2 `/view_risk_status` - Complete Risk Status
```
Main Menu → Risk → Risk Status
└─ Button: "📊 Risk Status"
   └─ Execute: handle_view_risk_status()
      └─ Result: Shows all tier configurations with active tier highlighted,
                 current loss status, preset settings for each tier
```
**Steps:** MAIN MENU → RISK → RISK STATUS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_view_risk_status()`  
**Output:** 
- Active tier marker (✅)
- All 5 tier configurations (daily/lifetime caps, lot sizes)
- Current daily and lifetime loss totals

---

#### 6.4 `/set_daily_cap` - Set Daily Loss Limit
```
Main Menu → Risk → Set Daily Cap
└─ Button: "📉 Daily Cap"
   ├─ Select Amount:
   │  ├─ "$10"
   │  ├─ "$20"
   │  ├─ "$50"
   │  ├─ "$100"
   │  ├─ "$200"
   │  ├─ "$500"
   │  ├─ "$1000"
   │  ├─ "$2000"
   │  ├─ "$5000"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_daily_cap(amount)
```
**Steps:** MAIN MENU → RISK → DAILY CAP → AMOUNT → CONFIRM (4 clicks)  
**Parameters:** amount ($10-$5000)  
**Handler:** `handle_set_daily_cap()`

---

#### 6.5 `/set_lifetime_cap` - Set Lifetime Loss Limit
```
Main Menu → Risk → Set Lifetime Cap
└─ Button: "📉 Lifetime Cap"
   ├─ Select Amount:
   │  └─ [Same presets as daily cap]
   └─ Confirmation
      └─ Execute: handle_set_lifetime_cap(amount)
```
**Steps:** MAIN MENU → RISK → LIFETIME CAP → AMOUNT → CONFIRM (4 clicks)  
**Parameters:** amount  
**Handler:** `handle_set_lifetime_cap()`

---

#### 6.6 `/set_risk_tier` - Configure Risk Tier
```
Main Menu → Risk → Set Risk Tier
└─ Button: "⚙️ Risk Tier"
   ├─ Enter Balance Tier (Type):
   │  └─ "Type balance (e.g., 10000)"
   ├─ Enter Daily Limit (Type):
   │  └─ "Type daily limit (e.g., 500)"
   ├─ Enter Lifetime Limit (Type):
   │  └─ "Type lifetime limit (e.g., 2000)"
   └─ Confirmation
      └─ Execute: handle_set_risk_tier(balance, daily, lifetime)
```
**Steps:** TYPE BALANCE → TYPE DAILY → TYPE LIFETIME → CONFIRM (4 inputs)  
**Parameters:** balance, daily, lifetime  
**Handler:** `handle_set_risk_tier()`

---

#### 6.7 `/switch_tier` - Switch Active Risk Tier
```
Main Menu → Risk → Switch Tier
└─ Button: "🔄 Switch Tier"
   ├─ Select Tier (Dynamic):
   │  ├─ "$5000"
   │  ├─ "$10000"
   │  ├─ "$25000"
   │  ├─ "$50000"
   │  └─ "$100000"
   └─ Confirmation
      └─ Execute: handle_switch_tier(tier)
```
**Steps:** MAIN MENU → RISK → SWITCH TIER → SELECT TIER → CONFIRM (4 clicks)  
**Parameters:** tier (5000/10000/25000/50000/100000)  
**Handler:** `handle_switch_tier()`  
**Type:** Single Parameter (Dynamic Tiers)  
**Result:** 
- Switches active tier immediately
- Applies preset daily/lifetime caps for selected tier
- Updates lot size to tier's preset value
- Shows warning if tier exceeds account balance
- All future trades use new tier settings

---

#### 6.8 `/clear_loss_data` - Clear Lifetime Loss
```
Main Menu → Risk → Clear Loss Data
└─ Button: "🗑️ Clear Loss Data"
   └─ Confirmation: "Clear lifetime loss data?"
      └─ Execute: handle_clear_loss_data()
```
**Steps:** MAIN MENU → RISK → CLEAR LOSS → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_clear_loss_data()`

---

#### 6.9 `/clear_daily_loss` - Clear Daily Loss
```
Main Menu → Risk → Clear Daily Loss
└─ Button: "🗑️ Clear Daily"
   └─ Confirmation: "Clear daily loss?"
      └─ Execute: handle_clear_daily_loss()
```
**Steps:** MAIN MENU → RISK → CLEAR DAILY → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_clear_daily_loss()`

---

#### 6.10 `/lot_size_status` - Lot Size Status
```
Main Menu → Risk → Lot Size Status
└─ Button: "📦 Lot Status"
   └─ Execute: handle_lot_size_status()
      └─ Result: Current lot sizes for all tiers
```
**Steps:** MAIN MENU → RISK → LOT STATUS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_lot_size_status()`

---

#### 6.11 `/set_lot_size` - Override Lot Size
```
Main Menu → Risk → Set Lot Size
└─ Button: "📦 Set Lot"
   ├─ Select Tier:
   │  └─ [$5000, $10000, $25000, $50000, $100000]
   ├─ Select Lot Size:
   │  ├─ "0.01"
   │  ├─ "0.05"
   │  ├─ "0.1"
   │  ├─ "0.2"
   │  ├─ "0.5"
   │  ├─ "1.0"
   │  ├─ "2.0"
   │  ├─ "5.0"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_lot_size(tier, lot_size)
```
**Steps:** MAIN MENU → RISK → SET LOT → TIER → SIZE → CONFIRM (5 clicks)  
**Parameters:** tier, lot_size  
**Handler:** `handle_set_lot_size()`

---

#### 6.12 `/reset_risk_settings` - Reset All Risk Settings
```
Main Menu → Risk → Reset Settings
└─ Button: "🔄 Reset Settings"
   └─ Confirmation: "Reset all risk settings to factory defaults?"
      └─ Execute: handle_reset_risk_settings()
         └─ Result: Restores default tier configurations
```
**Steps:** MAIN MENU → RISK → RESET SETTINGS → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_reset_risk_settings()`  
**Resets To:**
- $5000 tier: Daily $100, Lifetime $500, Lot 0.01 (becomes active)
- $10000 tier: Daily $200, Lifetime $1000, Lot 0.05
- $25000 tier: Daily $500, Lifetime $2500, Lot 0.1
- $50000 tier: Daily $1000, Lifetime $5000, Lot 0.2
- $100000 tier: Daily $2000, Lifetime $10000, Lot 0.5

---

## 7. ⚙️ SL SYSTEM CONTROL (8 Commands)

#### 7.1 `/sl_status` - SL System Status
```
Main Menu → SL System → Status
└─ Button: "📊 SL Status"
   └─ Execute: handle_sl_status()
      └─ Result: Active system, enabled status, reductions
```
**Steps:** MAIN MENU → SL SYSTEM → STATUS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_sl_status()`

---

#### 7.2 `/sl_system_change` - Switch SL System
```
Main Menu → SL System → Change System
└─ Button: "🔄 Change System"
   ├─ Select System:
   │  ├─ "sl-1" (Conservative - Wider SLs)
   │  └─ "sl-2" (Aggressive - Tighter SLs)
   └─ Confirmation
      └─ Execute: handle_sl_system_change(system)
```
**Steps:** MAIN MENU → SL SYSTEM → CHANGE → SELECT → CONFIRM (4 clicks)  
**Parameters:** system (sl-1/sl-2)  
**Handler:** `handle_sl_system_change()`

---

#### 7.3 `/sl_system_on` - Enable SL System
```
Main Menu → SL System → Enable System
└─ Button: "✅ Enable System"
   ├─ Select System:
   │  ├─ "sl-1"
   │  └─ "sl-2"
   └─ Confirmation
      └─ Execute: handle_sl_system_on(system)
```
**Steps:** MAIN MENU → SL SYSTEM → ENABLE → SELECT → CONFIRM (4 clicks)  
**Parameters:** system  
**Handler:** `handle_sl_system_on()`

---

#### 7.4 `/complete_sl_system_off` - Disable All SL
```
Main Menu → SL System → Disable All
└─ Button: "❌ Disable All"
   └─ Confirmation: "Disable ALL SL systems?"
      └─ Execute: handle_complete_sl_system_off()
```
**Steps:** MAIN MENU → SL SYSTEM → DISABLE → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_complete_sl_system_off()`

---

#### 7.5 `/view_sl_config` - View SL Configuration
```
Main Menu → SL System → View Config
└─ Button: "⚙️ Config"
   └─ Execute: handle_view_sl_config()
      └─ Result: All symbol SL values
```
**Steps:** MAIN MENU → SL SYSTEM → CONFIG (2 clicks)  
**Type:** Direct  
**Handler:** `handle_view_sl_config()`

---

#### 7.6 `/set_symbol_sl` - Reduce Symbol SL
```
Main Menu → SL System → Set Symbol SL
└─ Button: "📉 Symbol SL"
   ├─ Select Symbol:
   │  └─ [XAUUSD, EURUSD, GBPUSD, etc.]
   ├─ Select Reduction %:
   │  ├─ "10%"
   │  ├─ "20%"
   │  ├─ "30%"
   │  ├─ "40%"
   │  ├─ "50%"
   │  └─ "✏️ Custom"
   └─ Confirmation
      └─ Execute: handle_set_symbol_sl(symbol, percent)
```
**Steps:** MAIN MENU → SL SYSTEM → SET → SYMBOL → PERCENT → CONFIRM (5 clicks)  
**Parameters:** symbol, percent (5-50%)  
**Handler:** `handle_set_symbol_sl()`

---

#### 7.7 `/reset_symbol_sl` - Reset One Symbol
```
Main Menu → SL System → Reset Symbol SL
└─ Button: "🔄 Reset Symbol"
   ├─ Select Symbol:
   │  └─ [XAUUSD, EURUSD, etc.]
   └─ Confirmation
      └─ Execute: handle_reset_symbol_sl(symbol)
```
**Steps:** MAIN MENU → SL SYSTEM → RESET → SYMBOL → CONFIRM (4 clicks)  
**Parameters:** symbol  
**Handler:** `handle_reset_symbol_sl()`

---

#### 7.8 `/reset_all_sl` - Reset All SLs
```
Main Menu → SL System → Reset All
└─ Button: "🔄 Reset All"
   └─ Confirmation: "Reset ALL symbol SLs?"
      └─ Execute: handle_reset_all_sl()
```
**Steps:** MAIN MENU → SL SYSTEM → RESET ALL → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_reset_all_sl()`

---

## 8. 💎 DUAL ORDERS (2 Commands)

#### 8.1 `/dual_order_status` - Dual Order Status
```
Main Menu → Orders → Dual Status
└─ Button: "📊 Status"
   └─ Execute: handle_dual_order_status()
      └─ Result: Dual order system status
```
**Steps:** MAIN MENU → ORDERS → STATUS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_dual_order_status()`

---

#### 8.2 `/toggle_dual_orders` - Toggle Dual Orders
```
Main Menu → Orders → Toggle
└─ Button: "🔄 Toggle"
   └─ Confirmation: "Toggle dual orders?"
      └─ Execute: handle_toggle_dual_orders()
         └─ Result: Enabled/Disabled
```
**Steps:** MAIN MENU → ORDERS → TOGGLE → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_toggle_dual_orders()`

---

## 9. 📈 PROFIT BOOKING (15 Commands)

#### 9.1 `/profit_status` - Profit System Status
```
Main Menu → Profit → Status
└─ Button: "📊 Status"
   └─ Execute: handle_profit_status()
      └─ Result: System status, max level, targets
```
**Steps:** MAIN MENU → PROFIT → STATUS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_profit_status()`

---

#### 9.2 `/profit_stats` - Profit Statistics
```
Main Menu → Profit → Stats
└─ Button: "📈 Stats"
   └─ Execute: handle_profit_stats()
      └─ Result: Chain stats, profits, averages
```
**Steps:** MAIN MENU → PROFIT → STATS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_profit_stats()`

---

#### 9.3 `/toggle_profit_booking` - Toggle System
```
Main Menu → Profit → Toggle
└─ Button: "🔄 Toggle"
   └─ Confirmation: "Toggle profit booking?"
      └─ Execute: handle_toggle_profit_booking()
```
**Steps:** MAIN MENU → PROFIT → TOGGLE → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_toggle_profit_booking()`

---

#### 9.4 `/set_profit_targets` - Set Profit Targets
```
Main Menu → Profit → Set Targets
└─ Button: "🎯 Targets"
   └─ Input Screen: "Enter space-separated targets"
      └─ Type: "10 20 40 80 160"
         └─ Confirmation
            └─ Execute: handle_set_profit_targets(targets)
```
**Steps:** MAIN MENU → PROFIT → TARGETS → TYPE VALUES → CONFIRM (4 inputs)  
**Parameters:** targets (list of numbers)  
**Type:** Multi-targets (requires typed input)  
**Handler:** `handle_set_profit_targets()`

---

#### 9.5 `/profit_chains` - View Active Chains
```
Main Menu → Profit → Chains
└─ Button: "🔗 Chains"
   └─ Execute: handle_profit_chains()
      └─ Result: All active profit chains
```
**Steps:** MAIN MENU → PROFIT → CHAINS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_profit_chains()`

---

#### 9.6 `/stop_profit_chain` - Stop One Chain
```
Main Menu → Profit → Stop Chain
└─ Button: "🛑 Stop Chain"
   ├─ Dynamic List: Shows all active chains
   │  └─ Select chain from list
   └─ Confirmation
      └─ Execute: handle_stop_profit_chain(chain_id)
```
**Steps:** MAIN MENU → PROFIT → STOP → SELECT CHAIN → CONFIRM (4 clicks)  
**Parameters:** chain_id (dynamic)  
**Type:** Dynamic (loads from active chains)  
**Handler:** `handle_stop_profit_chain()`

---

#### 9.7 `/stop_all_profit_chains` - Stop All Chains
```
Main Menu → Profit → Stop All
└─ Button: "🛑 Stop All"
   └─ Confirmation: "Stop ALL profit chains?"
      └─ Execute: handle_stop_all_profit_chains()
```
**Steps:** MAIN MENU → PROFIT → STOP ALL → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_stop_all_profit_chains()`

---

#### 9.8 `/set_chain_multipliers` - Set Multipliers
```
Main Menu → Profit → Multipliers
└─ Button: "🔢 Multipliers"
   └─ Input Screen: "Enter space-separated multipliers"
      └─ Type: "1 2 4 8 16"
         └─ Confirmation
            └─ Execute: handle_set_chain_multipliers(multipliers)
```
**Steps:** MAIN MENU → PROFIT → MULTIPLIERS → TYPE → CONFIRM (4 inputs)  
**Parameters:** multipliers (list)  
**Type:** Multi-targets  
**Handler:** `handle_set_chain_multipliers()`

---

#### 9.9 `/profit_config` - View Configuration
```
Main Menu → Profit → Config
└─ Button: "⚙️ Config"
   └─ Execute: handle_profit_config()
      └─ Result: All profit booking settings
```
**Steps:** MAIN MENU → PROFIT → CONFIG (2 clicks)  
**Type:** Direct  
**Handler:** `handle_profit_config()`

---

#### 9.10 `/profit_sl_status` - Profit SL Status
```
Main Menu → Profit → SL Status
└─ Button: "📊 SL Status"
   └─ Execute: handle_profit_sl_status()
      └─ Result: Current SL mode, settings
```
**Steps:** MAIN MENU → PROFIT → SL STATUS (2 clicks)  
**Type:** Direct  
**Handler:** `handle_profit_sl_status()`

---

#### 9.11 `/profit_sl_mode` - Switch SL Mode
```
Main Menu → Profit → SL Mode
└─ Button: "🔄 SL Mode"
   ├─ Select Mode:
   │  ├─ "SL-1.1" (Logic-Specific: $20/$40/$50)
   │  └─ "SL-2.1" (Universal Fixed: $10)
   └─ Confirmation
      └─ Execute: handle_profit_sl_mode(profit_sl_mode)
```
**Steps:** MAIN MENU → PROFIT → SL MODE → SELECT → CONFIRM (4 clicks)  
**Parameters:** profit_sl_mode (SL-1.1/SL-2.1)  
**Handler:** `handle_profit_sl_mode()`

---

#### 9.12 `/enable_profit_sl` - Enable Profit SL
```
Main Menu → Profit → Enable SL
└─ Button: "✅ Enable SL"
   └─ Confirmation
      └─ Execute: handle_enable_profit_sl()
```
**Steps:** MAIN MENU → PROFIT → ENABLE SL → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_enable_profit_sl()`

---

#### 9.13 `/disable_profit_sl` - Disable Profit SL
```
Main Menu → Profit → Disable SL
└─ Button: "❌ Disable SL"
   └─ Confirmation
      └─ Execute: handle_disable_profit_sl()
```
**Steps:** MAIN MENU → PROFIT → DISABLE SL → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_disable_profit_sl()`

---

#### 9.14 `/set_profit_sl` - Set Custom Profit SL
```
Main Menu → Profit → Set SL
└─ Button: "⚙️ Set SL"
   ├─ Select Logic:
   │  ├─ "LOGIC1"
   │  ├─ "LOGIC2"
   │  └─ "LOGIC3"
   ├─ Select Amount:
   │  └─ [Presets or Custom]
   └─ Confirmation
      └─ Execute: handle_set_profit_sl(logic, amount)
```
**Steps:** MAIN MENU → PROFIT → SET SL → LOGIC → AMOUNT → CONFIRM (5 clicks)  
**Parameters:** logic, amount  
**Handler:** `handle_set_profit_sl()`

---

#### 9.15 `/reset_profit_sl` - Reset Profit SL
```
Main Menu → Profit → Reset SL
└─ Button: "🔄 Reset SL"
   └─ Confirmation: "Reset to defaults?"
      └─ Execute: handle_reset_profit_sl()
```
**Steps:** MAIN MENU → PROFIT → RESET SL → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `handle_reset_profit_sl()`

---

## 10. 🔍 DIAGNOSTICS & HEALTH (15 Commands)

#### 10.1 `/health_status` - System Health
```
Main Menu → Diagnostics → Health Status
└─ Button: "🏥 Health"
   └─ Execute: _execute_health_status()
      └─ Result: Full system health report
```
**Steps:** MAIN MENU → DIAGNOSTICS → HEALTH (2 clicks)  
**Type:** Direct  
**Handler:** `_execute_health_status()`

---

#### 10.2 `/set_log_level` - Set Logging Level
```
Main Menu → Diagnostics → Set Log Level
└─ Button: "📝 Log Level"
   ├─ Select Level:
   │  ├─ "DEBUG"
   │  ├─ "INFO"
   │  ├─ "WARNING"
   │  ├─ "ERROR"
   │  └─ "CRITICAL"
   └─ Confirmation
      └─ Execute: _execute_set_log_level(level)
```
**Steps:** MAIN MENU → DIAGNOSTICS → LOG LEVEL → SELECT → CONFIRM (4 clicks)  
**Parameters:** level (DEBUG/INFO/WARNING/ERROR/CRITICAL)  
**Handler:** `_execute_set_log_level()`

---

#### 10.3 `/get_log_level` - Current Log Level
```
Main Menu → Diagnostics → Get Log Level
└─ Button: "❓ Log Level"
   └─ Execute: _execute_get_log_level()
      └─ Result: Current logging level
```
**Steps:** MAIN MENU → DIAGNOSTICS → GET LEVEL (2 clicks)  
**Type:** Direct  
**Handler:** `_execute_get_log_level()`

---

#### 10.4 `/reset_log_level` - Reset to Default
```
Main Menu → Diagnostics → Reset Log Level
└─ Button: "🔄 Reset Level"
   └─ Confirmation
      └─ Execute: _execute_reset_log_level()
```
**Steps:** MAIN MENU → DIAGNOSTICS → RESET LEVEL → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `_execute_reset_log_level()`

---

#### 10.5 `/error_stats` - Error Statistics
```
Main Menu → Diagnostics → Error Stats
└─ Button: "📊 Error Stats"
   └─ Execute: _execute_error_stats()
      └─ Result: Error counts, types, last errors
```
**Steps:** MAIN MENU → DIAGNOSTICS → ERROR STATS (2 clicks)  
**Type:** Direct  
**Handler:** `_execute_error_stats()`

---

#### 10.6 `/reset_errors` - Reset Error Counters
```
Main Menu → Diagnostics → Reset Errors
└─ Button: "🔄 Reset Errors"
   └─ Confirmation
      └─ Execute: _execute_reset_errors()
```
**Steps:** MAIN MENU → DIAGNOSTICS → RESET ERRORS → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `_execute_reset_errors()`

---

#### 10.7 `/reset_health` - Reset Health Stats
```
Main Menu → Diagnostics → Reset Health
└─ Button: "🔄 Reset Health"
   └─ Confirmation
      └─ Execute: _execute_reset_health()
```
**Steps:** MAIN MENU → DIAGNOSTICS → RESET HEALTH → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `_execute_reset_health()`

---

#### 10.8 `/export_logs` - Export Recent Logs
```
Main Menu → Diagnostics → Export Logs
└─ Button: "📄 Export Logs"
   ├─ Select Lines:
   │  ├─ "100 lines"
   │  ├─ "500 lines"
   │  └─ "1000 lines"
   └─ Execute: _execute_export_logs(lines)
      └─ Result: Sends log file via Telegram
```
**Steps:** MAIN MENU → DIAGNOSTICS → EXPORT → LINES → EXECUTE (3 clicks)  
**Parameters:** lines (100/500/1000)  
**Handler:** `_execute_export_logs()`  
**Uses:** `send_document()` method

---

#### 10.9 `/export_current_session` - Export Current Session
```
Main Menu → Diagnostics → Export Session
└─ Button: "📄 Current Session"
   └─ Execute: _execute_export_current_session()
      └─ Result: Sends current session log
```
**Steps:** MAIN MENU → DIAGNOSTICS → EXPORT SESSION (2 clicks)  
**Type:** Direct  
**Handler:** `_execute_export_current_session()`  
**Uses:** `send_document()` method

---

#### 10.10 `/export_by_date` - Export by Date
```
Main Menu → Diagnostics → Export by Date
└─ Button: "📅 By Date"
   ├─ Select Date:
   │  ├─ "Today (25-11-2025)"
   │  ├─ "24-11-2025"
   │  ├─ "23-11-2025"
   │  ├─ "22-11-2025"
   │  ├─ "21-11-2025"
   │  ├─ "20-11-2025"
   │  └─ "19-11-2025"
   └─ Execute: _execute_export_by_date(date)
      └─ Result: Sends specified date log
```
**Steps:** MAIN MENU → DIAGNOSTICS → BY DATE → SELECT → EXECUTE (3 clicks)  
**Parameters:** date (YYYY-MM-DD format)  
**Presets:** Last 7 days (dynamic)  
**Handler:** `_execute_export_by_date()`  
**Uses:** `send_document()` method

---

#### 10.11 `/export_date_range` - Export Date Range
```
Main Menu → Diagnostics → Export Range
└─ Button: "📅 Date Range"
   ├─ Select Start Date:
   │  └─ [Last 7 days]
   ├─ Select End Date:
   │  └─ [Last 7 days]
   └─ Execute: _execute_export_date_range(start_date, end_date)
      └─ Result: Sends combined log file
```
**Steps:** MAIN MENU → DIAGNOSTICS → RANGE → START → END → EXECUTE (4 clicks)  
**Parameters:** start_date, end_date  
**Handler:** `_execute_export_date_range()`  
**Uses:** `send_document()` method

---

#### 10.12 `/log_file_size` - Check Log File Size
```
Main Menu → Diagnostics → Log Size
└─ Button: "📏 File Size"
   └─ Execute: _execute_log_file_size()
      └─ Result: Current log file size
```
**Steps:** MAIN MENU → DIAGNOSTICS → SIZE (2 clicks)  
**Type:** Direct  
**Handler:** `_execute_log_file_size()`

---

#### 10.13 `/clear_old_logs` - Clear Old Logs
```
Main Menu → Diagnostics → Clear Logs
└─ Button: "🗑️ Clear Old"
   └─ Confirmation: "Clear logs older than 30 days?"
      └─ Execute: _execute_clear_old_logs()
```
**Steps:** MAIN MENU → DIAGNOSTICS → CLEAR → CONFIRM (3 clicks)  
**Type:** Direct  
**Handler:** `_execute_clear_old_logs()`

---

#### 10.14 `/trading_debug_mode` - Trading Debug
```
Main Menu → Diagnostics → Debug Mode
└─ Button: "🐛 Debug"
   ├─ Select Mode:
   │  ├─ "status"
   │  ├─ "on"
   │  └─ "off"
   └─ Confirmation
      └─ Execute: _execute_trading_debug_mode(mode)
```
**Steps:** MAIN MENU → DIAGNOSTICS → DEBUG → MODE → CONFIRM (4 clicks)  
**Parameters:** mode (status/on/off)  
**Handler:** `_execute_trading_debug_mode()`

---

#### 10.15 `/system_resources` - System Resources
```
Main Menu → Diagnostics → Resources
└─ Button: "💻 Resources"
   └─ Execute: _execute_system_resources()
      └─ Result: CPU, RAM, disk usage
```
**Steps:** MAIN MENU → DIAGNOSTICS → RESOURCES (2 clicks)  
**Type:** Direct  
**Handler:** `_execute_system_resources()`

---

## 📊 SUMMARY STATISTICS

### Total Command Count: **81 Commands**

### By Category:
1. 💰 Trading Control: **6 commands**
2. ⚡ Performance & Analytics: **6 commands**
3. ⚙️ Strategy Control: **7 commands**
4. 🔄 Re-entry System: **12 commands**
5. 📍 Trend Management: **5 commands**
6. 🛡️ Risk & Lot Management: **11 commands** (⬆️ Updated: +3 new commands)
7. ⚙️ SL System Control: **8 commands**
8. 💎 Dual Orders: **2 commands**
9. 📈 Profit Booking: **15 commands**
10. 🔍 Diagnostics & Health: **15 commands**

### By Command Type:
- **Direct (No Parameters):** 46 commands (56.8%) ⬆️ +2 (view_risk_status, reset_risk_settings)
- **Single Parameter:** 18 commands (22.2%) ⬆️ +1 (switch_tier)
- **Multi Parameter:** 11 commands (13.6%)
- **Multi-targets (Type Input):** 2 commands (2.5%)
- **Dynamic (Load from Data):** 2 commands (2.5%)
- **Submenu:** 2 commands (2.5%)

### Click Depth Analysis:
- **2 Clicks (Direct):** 46 commands ⬆️ +2
- **3 Clicks (Confirm):** 13 commands ⬆️ +1
- **4 Clicks (1 Param + Confirm):** 17 commands
- **5 Clicks (2 Params + Confirm):** 4 commands
- **6 Clicks (3 Params + Confirm):** 2 commands

### Commands Using `send_document()` Method:
1. `/export_logs` ✅
2. `/export_current_session` ✅
3. `/export_by_date` ✅
4. `/export_date_range` ✅

---

## 🔍 TESTING CHECKLIST

### To Test if a Command is Working:

#### 1. **Direct Commands (2 clicks)**
   - Open Telegram
   - Click MAIN MENU → Category → Command
   - ✅ Should execute immediately
   - ✅ Should receive response message

#### 2. **Single Parameter (4 clicks)**
   - Click MAIN MENU → Category → Command
   - Select parameter value from buttons
   - Click "✅ Confirm"
   - ✅ Should execute with selected parameter
   - ✅ Should receive success/failure message

#### 3. **Multi Parameter (5-6 clicks)**
   - Click MAIN MENU → Category → Command
   - Select first parameter
   - Select second parameter
   - (Select third parameter if needed)
   - Click "✅ Confirm"
   - ✅ All parameters should be shown in confirmation
   - ✅ Should execute with all parameters

#### 4. **Multi-targets (Type Input)**
   - Click MAIN MENU → Category → Command
   - Type space-separated values
   - Click "✅ Confirm"
   - ✅ Should parse input correctly
   - ✅ Should execute with typed values

#### 5. **Dynamic Commands**
   - Click MAIN MENU → Category → Command
   - ✅ Should load dynamic list (e.g., active chains)
   - Select from dynamic list
   - Click "✅ Confirm"
   - ✅ Should execute with selected value

---

## ⚠️ COMMON SILENT FAILURE POINTS

### 1. **Missing Dependencies**
**Commands Affected:** 28 commands (see COMMAND_DEPENDENCIES)  
**Symptoms:**
- Command appears to execute
- No error message shown
- No action taken
- Logs show "Bot still initializing"

**Check:**
```python
# In telegram_bot.py, these must be set:
self.trading_engine  ✓
self.risk_manager    ✓
self.trend_manager   ✓
self.profit_booking_manager ✓
```

---

### 2. **Parameter Validation Failures**
**Symptoms:**
- Command fails after confirmation
- Message: "❌ Invalid parameter"
- No execution

**Check:** Each parameter type has validation rules in `PARAM_TYPE_DEFINITIONS`

---

### 3. **Export Commands Failing**
**Previous Issue:** `send_document method not available`  
**Fixed:** ✅ Added `send_document()` to telegram_bot.py (Line 262-286)

**Test:**
```
1. /export_current_session
2. Should receive .txt file via Telegram
3. If fails, check:
   - telegram_bot.send_document() exists
   - File path is correct
   - File permissions are OK
```

---

### 4. **Menu System Errors**
**Symptoms:**
- Buttons don't respond
- "Unknown callback" error
- Returns to main menu

**Check:**
```python
# In telegram_bot.py
self.menu_manager  # Must be initialized
callback_data format: "cmd_category_command"
```

---

### 5. **Confirmation Screen Not Showing**
**Symptoms:**
- Command executes without confirmation
- Parameters not collected

**Debug:**
- Check `menu_manager.show_confirmation()`
- Verify params stored in context
- Look for "CONFIRMATION" in logs

---

## 🎯 HOW TO REPORT A BROKEN COMMAND

### Template:
```
**Command:** /command_name
**Category:** [Trading/Performance/etc.]
**Steps Taken:**
1. MAIN MENU → Category → Command
2. Selected: [parameter values]
3. Clicked: Confirm

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Error Message (if any):**
[Exact error text]

**Log Entry (if available):**
[Paste relevant log lines]

**Click Path:**
MAIN MENU (click 1) → Category (click 2) → Command (click 3) → ...
```

---

## 📝 DEVELOPER NOTES

### All Handlers Located In:
1. **Direct Telegram Handlers:** `src/clients/telegram_bot.py` (Lines 29-109)
2. **Menu Executor Handlers:** `src/menu/command_executor.py`
3. **Parameter Mapping:** `src/menu/command_mapping.py`
4. **Menu Structure:** `src/menu/menu_constants.py`

### Recent Fixes (27-Nov-2025):
1. **Logic Control Commands Fixed:**
   - Issue: Generic success screen was overwriting handler messages
   - Fix: Added `self_messaging_commands` list in `_execute_command_from_context()`
   - Commands now skip success screen and show their own messages
   - Affected commands: logic1_on, logic1_off, logic2_on, logic2_off, logic3_on, logic3_off
   - Also applied to: pause, resume, status, trades, performance, stats
   
2. **Handler Return Values:**
   - All logic handlers now return their message text
   - Maintains backward compatibility by still calling `send_message()`
   - Enables future enhancements to capture handler output

### Debugging a Command:
1. Enable DEBUG logging: `/set_log_level DEBUG`
2. Execute command
3. Check logs for:
   - `[PARAM SELECTION]` - Parameter collection
   - `[CONFIRMATION]` - Confirmation screen
   - `[MENU EXECUTION]` - Command execution
   - `[VALIDATE]` - Parameter validation
   - Handler call and result

### Adding a New Command:
1. Add to `COMMAND_PARAM_MAP` in `command_mapping.py`
2. Add handler to `command_executor.py`
3. Add to category in `menu_constants.py`
4. Add parameter validation if needed
5. If command sends its own messages, add to `self_messaging_commands` list
6. Test full flow: Menu → Params → Confirm → Execute

---

**Document Version:** 1.2  
**Last Updated:** 27-Nov-2025 06:30 IST  
**Total Commands Documented:** 81  
**Total Categories:** 10  
**Completeness:** 100%

**Recent Changes:**
- **27-Nov-2025 06:30:** Added 3 new Risk Management commands (view_risk_status, switch_tier, reset_risk_settings)
- **27-Nov-2025 06:30:** Updated Risk & Lot Management section from 8 to 11 commands
- **27-Nov-2025 06:30:** Updated total command count from 78 to 81
- **27-Nov-2025 05:18:** Fixed Logic Control commands (logic1_on/off, logic2_on/off, logic3_on/off)
- **27-Nov-2025 05:18:** Updated command flow to show proper status messages
- **27-Nov-2025 05:18:** Added handler response documentation
- **27-Nov-2025 05:18:** Updated click counts (2 clicks → 3 clicks for logic control)
