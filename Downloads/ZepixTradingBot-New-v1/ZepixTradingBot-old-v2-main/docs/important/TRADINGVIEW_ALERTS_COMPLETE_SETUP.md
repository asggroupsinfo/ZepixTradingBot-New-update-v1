# 🎯 COMPLETE TRADINGVIEW ALERTS SETUP - FINAL VERSION

**Document Version:** 5.0 (Simplified with Universal Alerts)  
**Last Updated:** December 07, 2025  
**Verified Against:** Updated Signals and Overlays (with Trend Alerts)  
**Bot Compatible:** Zepix Trading Bot v7  
**Total Alerts:** 20 (Simplified from previous versions)

---

## ⚠️ CRITICAL UPDATE - VERSION 5.0

### 🆕 **What Changed:**
- ✅ Added **2 Universal Trend Alerts** in Pine Script
- ✅ Total alerts: **20** (not 30!)
- ✅ Timeframe selection in TradingView (not in Pine Script)
- ✅ Simpler setup, fewer alerts
- ✅ Same functionality with less complexity

### **Previous Confusion Resolved:**
```
❌ OLD APPROACH: 10 separate trend alerts for each timeframe in Pine Script
✅ NEW APPROACH: 2 universal trend alerts, select timeframe in TradingView

Result: Same functionality, 80% fewer alerts to manage!
```

---

## 📋 COMPLETE ALERT SUMMARY

| Category | Pine Conditions | TradingView Alerts | Priority |
|----------|----------------|-------------------|----------|
| **🆕 TREND** | **2 universal** | **4** | 🔴 **CRITICAL** |
| **BIAS** | 2 universal | 4 | 🔴 CRITICAL |
| **ENTRY** | 2 universal | 6 | 🔴 CRITICAL |
| **EXIT** | 2 universal | 4 | 🟡 RECOMMENDED |
| **REVERSAL** | 2 universal | 2 | 🟢 OPTIONAL |
| **TOTAL** | **10 conditions** | **20 alerts** | |

---

## 🌐 WEBHOOK CONFIGURATION

```
URL: http://3.110.221.62/webhook
Method: POST
Content-Type: application/json
```

**All Alerts Must Use:**
- ✅ Webhook URL: `http://3.110.221.62/webhook`
- ✅ Frequency: `Once Per Bar Close`
- ✅ Expiration: `Open-ended`
- ✅ Alert actions: Webhook URL only
- ❌ Disable: App notifications, popups, emails, sounds

---

## 🆕 1️⃣ TREND ALERTS (4 alerts) - 🔴 CRITICAL

### 🎯 **PURPOSE - YOUR MAIN PROBLEM SOLVER**

**Why These Are Important:**
- ✅ Automatic trend updates - no manual /set_trend
- ✅ Real-time synchronization with bot
- ✅ No more missing trades due to outdated trends
- ✅ Bot always knows latest trend state

### 📡 **HOW IT WORKS**

```
Chart: 15M timeframe
Trend changes: Bearish → Bullish
         ↓
Alert fires: "Bullish Trend"
         ↓
Webhook → Bot receives
         ↓
Bot updates: XAUUSD 15M = BULLISH
         ↓
Next entry: Alignment check uses latest trend ✅
```

### 🔧 **PINE SCRIPT CONDITION**

**Universal Alerts (works on ANY timeframe):**
- `Bullish Trend` - Fires when trend changes to bullish
- `Bearish Trend` - Fires when trend changes to bearish

**Location:** Lines 128-129 in updated Pine Script

---

### **Setup for 15M Trends (2 alerts):**

#### 15M Bullish TREND
**Chart:** XAUUSD **15M** ← Select timeframe here!  
**Indicator:** Signals and Overlays - Updated with Trend Alerts  
**Alert Name:** `15M TREND BULL - XAUUSD`  
**Condition:** `Bullish Trend` ← Universal condition  
**Message:**
```json
{"type":"trend","symbol":"{{ticker}}","signal":"bull","tf":"15m","price":{{close}},"strategy":"ZepixPremium"}
```

#### 15M Bearish TREND
**Chart:** XAUUSD **15M**  
**Alert Name:** `15M TREND BEAR - XAUUSD`  
**Condition:** `Bearish Trend` ← Same universal condition  
**Message:**
```json
{"type":"trend","symbol":"{{ticker}}","signal":"bear","tf":"15m","price":{{close}},"strategy":"ZepixPremium"}
```

---

### **Setup for 1H Trends (2 alerts):**

#### 1H Bullish TREND
**Chart:** XAUUSD **1H** ← Different chart timeframe  
**Alert Name:** `1H TREND BULL - XAUUSD`  
**Condition:** `Bullish Trend` ← Same condition, different TF  
**Message:**
```json
{"type":"trend","symbol":"{{ticker}}","signal":"bull","tf":"1h","price":{{close}},"strategy":"ZepixPremium"}
```

#### 1H Bearish TREND
**Chart:** XAUUSD **1H**  
**Alert Name:** `1H TREND BEAR - XAUUSD`  
**Condition:** `Bearish Trend`  
**Message:**
```json
{"type":"trend","symbol":"{{ticker}}","signal":"bear","tf":"1h","price":{{close}},"strategy":"ZepixPremium"}
```

---

## 2️⃣ BIAS ALERTS (4 alerts) - 🔴 CRITICAL

### Purpose
Foundation for LOGIC3 (1H entry signals). Requires **ALL 9 indicators** to agree:
1. RSI
2. MFI (Money Flow Index)
3. Fisher Transform
4. DMI
5. Momentum
6. PSAR
7. MACD
8. Stochastic RSI
9. Vortex

### Indicator Condition
`[Screener] Full Bullish Alert` / `[Screener] Full Bearish Alert`

**Pine Script Reference:** Lines 748-752

---

### 1D Bullish BIAS
**Chart:** XAUUSD, **1D timeframe**  
**Alert Name:** `1D BIAS BULL - XAUUSD`  
**Condition:** `[Screener] Full Bullish Alert`  
**Message:**
```json
{"type":"bias","symbol":"{{ticker}}","signal":"bull","tf":"1d","price":{{close}},"strategy":"ZepixPremium"}
```

### 1D Bearish BIAS
**Chart:** XAUUSD, **1D timeframe**  
**Alert Name:** `1D BIAS BEAR - XAUUSD`  
**Condition:** `[Screener] Full Bearish Alert`  
**Message:**
```json
{"type":"bias","symbol":"{{ticker}}","signal":"bear","tf":"1d","price":{{close}},"strategy":"ZepixPremium"}
```

### 1H Bullish BIAS
**Chart:** XAUUSD, **1H timeframe**  
**Alert Name:** `1H BIAS BULL - XAUUSD`  
**Condition:** `[Screener] Full Bullish Alert`  
**Message:**
```json
{"type":"bias","symbol":"{{ticker}}","signal":"bull","tf":"1h","price":{{close}},"strategy":"ZepixPremium"}
```

### 1H Bearish BIAS
**Chart:** XAUUSD, **1H timeframe**  
**Alert Name:** `1H BIAS BEAR - XAUUSD`  
**Condition:** `[Screener] Full Bearish Alert`  
**Message:**
```json
{"type":"bias","symbol":"{{ticker}}","signal":"bear","tf":"1h","price":{{close}},"strategy":"ZepixPremium"}
```

---

## 3️⃣ ENTRY ALERTS (6 alerts) - 🔴 CRITICAL

### Purpose
Trade execution signals based on zero-lag EMA crossovers with dynamic volatility bands.

### Indicator Condition
`Bullish Entry Signals` / `Bearish Entry Signals`

**Pine Script Reference:** Lines 123-124

---

### 5M BUY Entry (LOGIC1)
**Chart:** XAUUSD, **5M timeframe**  
**Alert Name:** `5M ENTRY BUY - XAUUSD`  
**Condition:** `Bullish Entry Signals`  
**Message:**
```json
{"type":"entry","symbol":"{{ticker}}","signal":"buy","tf":"5m","price":{{close}},"strategy":"ZepixPremium"}
```

### 5M SELL Entry (LOGIC1)
**Chart:** XAUUSD, **5M timeframe**  
**Alert Name:** `5M ENTRY SELL - XAUUSD`  
**Condition:** `Bearish Entry Signals`  
**Message:**
```json
{"type":"entry","symbol":"{{ticker}}","signal":"sell","tf":"5m","price":{{close}},"strategy":"ZepixPremium"}
```

### 15M BUY Entry (LOGIC2)
**Chart:** XAUUSD, **15M timeframe**  
**Alert Name:** `15M ENTRY BUY - XAUUSD`  
**Condition:** `Bullish Entry Signals`  
**Message:**
```json
{"type":"entry","symbol":"{{ticker}}","signal":"buy","tf":"15m","price":{{close}},"strategy":"ZepixPremium"}
```

### 15M SELL Entry (LOGIC2)
**Chart:** XAUUSD, **15M timeframe**  
**Alert Name:** `15M ENTRY SELL - XAUUSD`  
**Condition:** `Bearish Entry Signals`  
**Message:**
```json
{"type":"entry","symbol":"{{ticker}}","signal":"sell","tf":"15m","price":{{close}},"strategy":"ZepixPremium"}
```

### 1H BUY Entry (LOGIC3)
**Chart:** XAUUSD, **1H timeframe**  
**Alert Name:** `1H ENTRY BUY - XAUUSD`  
**Condition:** `Bullish Entry Signals`  
**Message:**
```json
{"type":"entry","symbol":"{{ticker}}","signal":"buy","tf":"1h","price":{{close}},"strategy":"ZepixPremium"}
```

### 1H SELL Entry (LOGIC3)
**Chart:** XAUUSD, **1H timeframe**  
**Alert Name:** `1H ENTRY SELL - XAUUSD`  
**Condition:** `Bearish Entry Signals`  
**Message:**
```json
{"type":"entry","symbol":"{{ticker}}","signal":"sell","tf":"1h","price":{{close}},"strategy":"ZepixPremium"}
```

---

## 4️⃣ EXIT ALERTS (4 alerts) - 🟡 RECOMMENDED

### Purpose
Time-based exit warnings after N bars from entry (configurable via indicator settings).

### Indicator Condition
`Bullish Exit Appeared` / `Bearish Exit Appeared`

**Pine Script Reference:** Lines 153-154

---

### 5M Bullish EXIT
**Chart:** XAUUSD, **5M timeframe**  
**Alert Name:** `5M EXIT BULL - XAUUSD`  
**Condition:** `Bullish Exit Appeared`  
**Message:**
```json
{"type":"exit","symbol":"{{ticker}}","signal":"bull","tf":"5m","price":{{close}},"strategy":"ZepixPremium"}
```

### 5M Bearish EXIT
**Chart:** XAUUSD, **5M timeframe**  
**Alert Name:** `5M EXIT BEAR - XAUUSD`  
**Condition:** `Bearish Exit Appeared`  
**Message:**
```json
{"type":"exit","symbol":"{{ticker}}","signal":"bear","tf":"5m","price":{{close}},"strategy":"ZepixPremium"}
```

### 15M Bullish EXIT
**Chart:** XAUUSD, **15M timeframe**  
**Alert Name:** `15M EXIT BULL - XAUUSD`  
**Condition:** `Bullish Exit Appeared`  
**Message:**
```json
{"type":"exit","symbol":"{{ticker}}","signal":"bull","tf":"15m","price":{{close}},"strategy":"ZepixPremium"}
```

### 15M Bearish EXIT
**Chart:** XAUUSD, **15M timeframe**  
**Alert Name:** `15M EXIT BEAR - XAUUSD`  
**Condition:** `Bearish Exit Appeared`  
**Message:**
```json
{"type":"exit","symbol":"{{ticker}}","signal":"bear","tf":"15m","price":{{close}},"strategy":"ZepixPremium"}
```

---

## 5️⃣ REVERSAL ALERTS (2 alerts) - 🟢 OPTIONAL

### Purpose
Immediate profit booking on strong reversal signals (use for 5M only).

**⚠️ Note:** These are different from TREND alerts. Reversal alerts use VIDYA-based volume confirmation for immediate exits.

### Indicator Condition
`Bullish Reversal Signals` / `Bearish Reversal Signals`

**Pine Script Reference:** Lines 428-429

---

### 5M Bullish REVERSAL
**Chart:** XAUUSD, **5M timeframe**  
**Alert Name:** `5M REVERSAL BULL - XAUUSD`  
**Condition:** `Bullish Reversal Signals`  
**Message:**
```json
{"type":"reversal","symbol":"{{ticker}}","signal":"reversal_bull","tf":"5m","price":{{close}},"strategy":"ZepixPremium"}
```

### 5M Bearish REVERSAL
**Chart:** XAUUSD, **5M timeframe**  
**Alert Name:** `5M REVERSAL BEAR - XAUUSD`  
**Condition:** `Bearish Reversal Signals`  
**Message:**
```json
{"type":"reversal","symbol":"{{ticker}}","signal":"reversal_bear","tf":"5m","price":{{close}},"strategy":"ZepixPremium"}
```

---

## 🔧 BOT LOGIC REQUIREMENTS

### LOGIC1 (5M Entries)
```
Required Alignment: 1H BIAS + 15M TREND
Entry: 5M entry signal matches aligned direction
Trend Updates: ✅ Automatic via universal trend alerts
```

### LOGIC2 (15M Entries)
```
Required Alignment: 1H BIAS + 15M TREND
Entry: 15M entry signal matches aligned direction
Trend Updates: ✅ Automatic via universal trend alerts
```

### LOGIC3 (1H Entries)
```
Required Alignment: 1D BIAS + 1H BIAS
Entry: 1H entry signal matches aligned direction
Trend Updates: ✅ Automatic (though 1H trend not required for LOGIC3)
```

**Note:** Bot requires:
- 15M trend (for LOGIC1/2)
- 1H bias (for all logics)
- 1D bias (for LOGIC3)

---

## 📊 INDICATOR SETUP GUIDE

### **Step 1: Import Updated Pine Script**

**IMPORTANT:** Use the **updated version** with trend alerts!

**File:** `Signals and Overlays - Updated with Trend Alerts.html`
**Location:** `docs/tradingview/setup_files/Zepix Setup Files/`

**Steps:**
1. Open file `Signals and Overlays - Updated with Trend Alerts.html`
2. Copy **all code** (Ctrl+A, Ctrl+C)
3. Go to TradingView → Pine Editor
4. Paste code → Save as "Signals and Overlays - Bot Integration"
5. Add to charts (5M, 15M, 1H, 1D)

---

### **Step 2: Indicator Preset Settings**

| Alert Type | Chart TF | Preset Required |
|------------|----------|-----------------|
| **TREND** | 15M, 1H | Any (uses main trend variable) |
| **BIAS** | 1D, 1H | Any + Screener ON |
| **ENTRY** | 5M, 15M, 1H | Zero Lag Overlays |
| **EXIT** | 5M, 15M | Zero Lag Overlays |
| **REVERSAL** | 5M | Reversal + Volumes |

**Important Settings:**
- **For ENTRY/EXIT:** Select `Zero Lag Overlays` preset
- **For TREND:** Any preset (uses main `trend` variable)
- **For BIAS:** Enable `Trend Strength Screener` toggle
- **For REVERSAL:** Select `Reversal + Volumes` preset

**Indicator Settings:**
- Signals Sensitivity: 50 (default)
- Band Multiplier: 1.0 (default)
- Exit Length: 15 bars (adjustable)
- Enable: Trend Catcher, Exit Signals, Bar Colors

---

## ⚙️ TRADINGVIEW ALERT SETTINGS (All 20 Alerts)

```
✅ Condition: [As specified for each alert above]
✅ Options: Once Per Bar Close
✅ Expiration time: Open-ended
✅ Alert actions:
   ✅ Webhook URL: http://3.110.221.62/webhook
   ❌ Notify on App: OFF
   ❌ Show popup: OFF
   ❌ Send email: OFF
   ❌ Play sound: OFF
✅ Alert name: [As specified above]
✅ Message: [JSON payload as specified above]
```

---

## 📝 SETUP PRIORITY ORDER

### **Phase 1: CRITICAL (14 alerts) - Setup First**

**TREND (4):**
```
✅ 15M Bullish Trend
✅ 15M Bearish Trend
✅ 1H Bullish Trend
✅ 1H Bearish Trend
```

**BIAS (4):**
```
✅ 1D Bullish/Bearish BIAS
✅ 1H Bullish/Bearish BIAS
```

**ENTRY (6):**
```
✅ 5M BUY/SELL
✅ 15M BUY/SELL
✅ 1H BUY/SELL
```

### **Phase 2: RECOMMENDED (6 alerts) - Optional**

**EXIT (4):**
```
✅ 5M Bullish/Bearish EXIT
✅ 15M Bullish/Bearish EXIT
```

**REVERSAL (2):**
```
✅ 5M Bullish/Bearish REVERSAL
```

**Total:** 20 alerts (14 critical + 6 optional)

---

## ✅ VERIFICATION CHECKLIST

### After Setting Up All Alerts:

#### Alert Counts
- [ ] **TREND:** 4 alerts (15M Bull/Bear, 1H Bull/Bear)
- [ ] **BIAS:** 4 alerts (1D, 1H × 2 each)
- [ ] **ENTRY:** 6 alerts (5M, 15M, 1H × 2 each)
- [ ] **EXIT:** 4 alerts (5M, 15M × 2 each) - Optional
- [ ] **REVERSAL:** 2 alerts (5M × 2) - Optional

#### Technical Verification
- [ ] **Webhook URL:** Correct in ALL alerts
- [ ] **Frequency:** "Once Per Bar Close" in ALL alerts
- [ ] **JSON Format:** No typos, proper placeholders `{{ticker}}`
- [ ] **Indicator:** Updated version on all timeframes
- [ ] **Preset:** Correct for each alert type
- [ ] **Timeframes:** Each alert on correct TF chart

#### Pine Script
- [ ] **File Used:** `Signals and Overlays - Updated with Trend Alerts.html`
- [ ] **Contains:** Lines 127-129 with trend alerts
- [ ] **Saved As:** Descriptive name in TradingView

---

## 🔧 TROUBLESHOOTING

### Can't Find "Bullish Trend" or "Bearish Trend" Alert

**Problem:** Alert condition not showing in dropdown

**Solution:**
1. ✅ Verify you imported **Updated** version
2. ✅ File name: `Signals and Overlays - Updated with Trend Alerts.html`
3. ✅ Check Pine Editor shows trend alert lines (127-129)
4. ✅ Re-import if needed

---

### Alert Not Triggering

**Check:**
1. ✅ Indicator added to correct timeframe chart
2. ✅ "Once Per Bar Close" selected
3. ✅ Alert not paused
4. ✅ Trend actually changed (check visual table on chart)

---

### Bot Not Receiving Trend Updates

**Check:**
1. ✅ Webhook URL correct: `http://3.110.221.62/webhook`
2. ✅ Bot running: `python src/main.py`
3. ✅ JSON format valid (no typos in `"tf"` value)
4. ✅ Bot logs show "📊 TREND UPDATE"
5. ✅ File `/data/timeframe_trends.json` exists

**Test Manually:**
```powershell
Invoke-WebRequest -Uri "http://3.110.221.62/webhook" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"type":"trend","symbol":"XAUUSD","signal":"bull","tf":"15m","strategy":"ZepixPremium"}'
```

---

### Alert Triggers But No Trade

**Check:**
1. ✅ Trend alignment via `/trend_matrix`
2. ✅ All required timeframe trends set
3. ✅ Trends in AUTO mode (not MANUAL lock)
4. ✅ Risk limits not exceeded
5. ✅ Wait for trend alert first, then entry signal

---

## 🎯 KEY DIFFERENCES FROM PREVIOUS VERSIONS

### Version 4.0 → 5.0 Changes

| Aspect | v4.0 (OLD) | v5.0 (NEW) |
|--------|------------|------------|
| **Total Alerts** | 30 alerts | 20 alerts ✅ |
| **Pine Conditions** | 20 conditions | 10 conditions ✅ |
| **Trend Alerts** | 10 timeframe-specific | 2 universal ✅ |
| **Complexity** | High | Simple ✅ |
| **TF Selection** | In Pine Script | In TradingView ✅ |
| **Maintenance** | Complex | Easy ✅ |

### What's Better
- ✅ 33% fewer alerts to manage
- ✅ 50% fewer Pine Script conditions
- ✅ Same functionality
- ✅ Easier to understand
- ✅ Less error-prone
- ✅ Follows TradingView best practices

### What Stayed Same
- ✅ Bot functionality unchanged
- ✅ All LOGIC1/2/3 work same
- ✅ Trend tracking same accuracy
- ✅ Entry/Exit signals same
- ✅ Webhook format same

---

## 📌 IMPORTANT NOTES

### 1. Universal vs Timeframe-Specific

**Universal Alerts (Our Approach):**
```
Pine Script: alertcondition(ta.change(trend)...)
TradingView: Select timeframe per alert
Benefit: Simple, maintainable
```

**Timeframe-Specific (Old Approach):**
```
Pine Script: alertcondition(ta.change(s1)...) for each TF
TradingView: All TFs in one script
Benefit: None (just complexity)
```

---

### 2. TREND vs REVERSAL Alerts

**TREND Alerts (NEW):**
- Purpose: Bot trend storage sync
- Based on: Main `trend` variable (Zero-lag EMA)
- Use: 15M, 1H for alignment
- Updates: Bot's timeframe_trends.json

**REVERSAL Alerts (Existing):**
- Purpose: Quick exit signals  
- Based on: VIDYA + volume confirmation
- Use: 5M only for immediate exits
- Updates: Trade closure triggers

**Both serve different purposes!**

---

### 3. Timeframe Requirements

**Bot Actually Needs:**
- ✅ 15M trend (for LOGIC1/2 alignment)
- ✅ 1H bias (for all logics)
- ✅ 1D bias (for LOGIC3)
- ❌ 5M trend - NOT needed
- ❌ 4H trend - NOT needed  
- ❌ 1D trend - NOT needed (bias only)

**So Setup:**
- 4 TREND alerts (15M × 2, 1H × 2)
- 4 BIAS alerts (1D × 2, 1H × 2)
- 6 ENTRY alerts (5M, 15M, 1H × 2 each)

---

## 📖 QUICK REFERENCE

### Alert Count by Timeframe

| Timeframe | TREND | BIAS | ENTRY | EXIT | REVERSAL | Total |
|-----------|-------|------|-------|------|----------|-------|
| **1D** | - | 2 | - | - | - | 2 |
| **1H** | 2 | 2 | 2 | - | - | 6 |
| **15M** | 2 | - | 2 | 2 | - | 6 |
| **5M** | - | - | 2 | 2 | 2 | 6 |
| **TOTAL** | **4** | **4** | **6** | **4** | **2** | **20** |

---

### Alert Priority

**Must Setup (14 alerts):**
1. TREND (4) - Automatic bot sync
2. BIAS (4) - Foundation logic
3. ENTRY (6) - Trade execution

**Recommended (6 alerts):**
4. EXIT (4) - Exit warnings
5. REVERSAL (2) - Quick exits

---

## 🎉 SUCCESS CONFIRMATION

### You'll Know It's Working When:

**Trend Updates:**
- ✅ Bot logs: `📊 TREND UPDATE - Symbol: XAUUSD, Timeframe: 15m, New Trend: BULL`
- ✅ `/trend_matrix` shows real-time updates
- ✅ `/data/timeframe_trends.json` auto-updates
- ✅ No manual `/set_trend` needed

**Trade Execution:**
- ✅ Entry signals check latest trends
- ✅ No missed trades from outdated trends
- ✅ Alignment checks use current data
- ✅ Bot trades with confidence

---

## 📞 TESTING PROCEDURE

### Step 1: Test Trend Alert
```powershell
Invoke-WebRequest -Uri "http://3.110.221.62/webhook" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"type":"trend","symbol":"XAUUSD","signal":"bull","tf":"15m","strategy":"ZepixPremium"}'
```

**Expected:**
```
📊 TREND UPDATE
Symbol: XAUUSD
Timeframe: 15m
New Trend: BULL
```

### Step 2: Verify Storage
```
Telegram: /trend_matrix

Shows:
XAUUSD Trends:
15M: BULLISH ✅
1H: [current]
```

### Step 3: Wait for Real Alert
```
1. Chart: 15M XAUUSD
2. Wait for trend change
3. Alert fires automatically
4. Check bot logs
5. Verify trend updated
```

---

**Document Status:** ✅ FINAL VERSION  
**Last Updated:** December 07, 2025  
**Version:** 5.0 (Simplified & Correct)  
**Bot Compatibility:** Zepix Trading Bot v7  
**Total Alerts:** 20 (14 critical + 6 optional)

---

## 🚀 READY TO DEPLOY

**Total Setup Time:** ~30-40 minutes  
**Critical Alerts:** 14  
**Optional Alerts:** 6  
**Pine Script Changes:** ✅ Complete (2 lines added)  
**Bot Integration:** ✅ Ready (no changes needed)  
**Problem Solved:** ✅ No more missing trades!
