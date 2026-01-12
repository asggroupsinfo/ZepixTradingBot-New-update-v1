# ⚡ TRADINGVIEW ALERTS - QUICK REFERENCE v5.0

**Version:** 5.0 - Simplified with Universal Alerts  
**Date:** December 07, 2025  
**Total Alerts:** 20  
**Pine Conditions:** 10  
**Print & Keep Handy!**

---

## 🎯 QUICK SUMMARY

```
Total Alerts: 20 (not 30!)
Pine Script: 2 universal trend alerts added
Setup Time: ~30-40 minutes
Complexity: SIMPLE ✅
```

---

## 📊 ALERT BREAKDOWN

| Type | Alerts | Timeframes |
|------|--------|------------|
| TREND | 4 | 15M (2), 1H (2) |
| BIAS | 4 | 1D (2), 1H (2) |
| ENTRY | 6 | 5M, 15M, 1H (2 each) |
| EXIT | 4 | 5M (2), 15M (2) |
| REVERSAL | 2 | 5M (2) |
| **TOTAL** | **20** | |

---

## 🆕 TREND ALERTS (UNIVERSAL)

### Pine Script Conditions (2):
```
1. "Bullish Trend"
2. "Bearish Trend"
```

### TradingView Setup (4 alerts):

**15M Chart:**
- Alert 1: Bullish Trend → `{"type":"trend","symbol":"{{ticker}}","signal":"bull","tf":"15m"}`
- Alert 2: Bearish Trend → `{"type":"trend","symbol":"{{ticker}}","signal":"bear","tf":"15m"}`

**1H Chart:**
- Alert 3: Bullish Trend → `{"type":"trend","symbol":"{{ticker}}","signal":"bull","tf":"1h"}`
- Alert 4: Bearish Trend → `{"type":"trend","symbol":"{{ticker}}","signal":"bear","tf":"1h"}`

**Key:** Same condition, different charts!

---

## 📝 COMPLETE ALERT LIST

### CRITICAL (14 alerts):

**TREND (4):**
```
15M TREND BULL    | Chart: 15M | Condition: Bullish Trend
15M TREND BEAR    | Chart: 15M | Condition: Bearish Trend
1H TREND BULL     | Chart: 1H  | Condition: Bullish Trend
1H TREND BEAR     | Chart: 1H  | Condition: Bearish Trend
```

**BIAS (4):**
```
1D BIAS BULL      | Chart: 1D  | Condition: [Screener] Full Bullish Alert
1D BIAS BEAR      | Chart: 1D  | Condition: [Screener] Full Bearish Alert
1H BIAS BULL      | Chart: 1H  | Condition: [Screener] Full Bullish Alert
1H BIAS BEAR      | Chart: 1H  | Condition: [Screener] Full Bearish Alert
```

**ENTRY (6):**
```
5M ENTRY BUY      | Chart: 5M  | Condition: Bullish Entry Signals
5M ENTRY SELL     | Chart: 5M  | Condition: Bearish Entry Signals
15M ENTRY BUY     | Chart: 15M | Condition: Bullish Entry Signals
15M ENTRY SELL    | Chart: 15M | Condition: Bearish Entry Signals
1H ENTRY BUY      | Chart: 1H  | Condition: Bullish Entry Signals
1H ENTRY SELL     | Chart: 1H  | Condition: Bearish Entry Signals
```

### OPTIONAL (6 alerts):

**EXIT (4):**
```
5M EXIT BULL      | Chart: 5M  | Condition: Bullish Exit Appeared
5M EXIT BEAR      | Chart: 5M  | Condition: Bearish Exit Appeared
15M EXIT BULL     | Chart: 15M | Condition: Bullish Exit Appeared
15M EXIT BEAR     | Chart: 15M | Condition: Bearish Exit Appeared
```

**REVERSAL (2):**
```
5M REVERSAL BULL  | Chart: 5M  | Condition: Bullish Reversal Signals
5M REVERSAL BEAR  | Chart: 5M  | Condition: Bearish Reversal Signals
```

---

## 🚀 3-STEP SETUP

### Step 1: Import Pine Script (5 min)
```
File: Signals and Overlays - Updated with Trend Alerts.html
Location: docs/tradingview/setup_files/Zepix Setup Files/
Action: Copy → TradingView Pine Editor → Save
```

### Step 2: Add to Charts (5 min)
```
Add indicator to:
- 5M chart
- 15M chart
- 1H chart
- 1D chart
```

### Step 3: Create Alerts (20-30 min)
```
Phase 1: TREND (4 alerts)
Phase 2: BIAS (4 alerts)
Phase 3: ENTRY (6 alerts)
Phase 4: EXIT + REVERSAL (6 alerts) - Optional
```

---

## 📱 WEBHOOK SETTINGS

**All Alerts:**
```
URL: http://3.110.221.62/webhook
Frequency: Once Per Bar Close
Expiration: Open-ended
Actions: Webhook only (disable app/email/sound)
```

---

## 🎯 JSON MESSAGE TEMPLATES

### TREND
```json
{"type":"trend","symbol":"{{ticker}}","signal":"bull/bear","tf":"15m/1h","strategy":"ZepixPremium"}
```

### BIAS
```json
{"type":"bias","symbol":"{{ticker}}","signal":"bull/bear","tf":"1d/1h","strategy":"ZepixPremium"}
```

### ENTRY
```json
{"type":"entry","symbol":"{{ticker}}","signal":"buy/sell","tf":"5m/15m/1h","strategy":"ZepixPremium"}
```

### EXIT
```json
{"type":"exit","symbol":"{{ticker}}","signal":"bull/bear","tf":"5m/15m","strategy":"ZepixPremium"}
```

### REVERSAL
```json
{"type":"reversal","symbol":"{{ticker}}","signal":"reversal_bull/reversal_bear","tf":"5m","strategy":"ZepixPremium"}
```

---

## ✅ VERIFICATION CHECKLIST

### Before Starting:
- [ ] Updated Pine Script imported
- [ ] Indicator on all charts (5M, 15M, 1H, 1D)
- [ ] Bot running on port 80

### Alert Creation:
- [ ] TREND: 4 alerts ✅
- [ ] BIAS: 4 alerts ✅
- [ ] ENTRY: 6 alerts ✅
- [ ] EXIT: 4 alerts (optional)
- [ ] REVERSAL: 2 alerts (optional)

### Settings:
- [ ] Frequency: "Once Per Bar Close" (all)
- [ ] Webhook URL correct (all)
- [ ] JSON messages valid (no typos)

### Testing:
- [ ] Manual webhook test passed
- [ ] Bot logs show trend updates
- [ ] `/trend_matrix` working
- [ ] Real alert fired successfully

---

## 🔧 QUICK TROUBLESHOOTING

### Can't find "Bullish Trend" condition
**Fix:** Import **Updated** Pine Script with trend alerts

### Alert not firing
**Check:** Correct chart TF, "Once Per Bar Close", not paused

### Bot not receiving
**Check:** Webhook URL, JSON format, bot running

### No trade after alert
**Check:** Trend alignment via `/trend_matrix`

---

## ⏱️ TIME ESTIMATES

| Task | Time |
|------|------|
| Import script | 5 min |
| Add to charts | 5 min |
| TREND alerts | 10 min |
| BIAS alerts | 5 min |
| ENTRY alerts | 10 min |
| EXIT alerts | 5 min |
| REVERSAL alerts | 3 min |
| **Total** | **~40 min** |

---

## 📊 TIMEFRAME MAPPING

| JSON Value | Chart |
|------------|-------|
| `"5m"` | 5M |
| `"15m"` | 15M |
| `"1h"` | 1H or 60 |
| `"1d"` | 1D |

---

## 🎯 INDICATOR PRESETS

| Alert Type | Preset |
|------------|--------|
| TREND | Any (uses main trend) |
| BIAS | Any + Screener ON |
| ENTRY | Zero Lag Overlays |
| EXIT | Zero Lag Overlays |
| REVERSAL | Reversal + Volumes |

---

## 🚨 COMMON MISTAKES

### ❌ Wrong:
- Using old Pine Script without trend alerts
- Creating 30 alerts instead of 20
- Putting wrong `"tf"` in JSON
- Forgetting {{ticker}} placeholder

### ✅ Correct:
- Using updated Pine Script
- Total 20 alerts (14 critical)
- Matching `"tf"` to chart timeframe
- Using placeholders correctly

---

## 🎉 SUCCESS INDICATORS

**When Working:**
- ✅ Bot logs: `📊 TREND UPDATE`
- ✅ `/trend_matrix` shows updates
- ✅ No manual `/set_trend` needed
- ✅ Trades execute correctly
- ✅ No missed trades

---

## 📞 TEST COMMAND

```powershell
Invoke-WebRequest -Uri "http://3.110.221.62/webhook" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"type":"trend","symbol":"XAUUSD","signal":"bull","tf":"15m","strategy":"ZepixPremium"}'
```

**Expected Response:**
```
📊 TREND UPDATE
Symbol: XAUUSD
Timeframe: 15m
New Trend: BULL
```

---

## 📌 KEY POINTS

1. **20 alerts total** (not 30)
2. **2 universal trend conditions** in Pine Script
3. **Timeframe selection in TradingView**, not code
4. **Same functionality**, simpler setup
5. **Bot ready**, no code changes needed

---

**Version:** 5.0  
**Status:** ✅ Production Ready  
**Complexity:** Simple  
**Setup Time:** 30-40 minutes  
**Impact:** 🔴 CRITICAL - Solves missing trades
