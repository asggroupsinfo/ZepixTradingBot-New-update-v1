# ⚡ QUICK SETUP GUIDE - Multi-Timeframe Trend Alerts

## 📋 FILES CREATED

✅ **Updated Signals and Overlays.html** - Complete Pine Script with trend alerts
✅ **UPDATE_NOTES.md** - Detailed documentation
✅ **QUICK_SETUP.md** - This file (quick reference)

---

## 🚀 3-STEP SETUP

### **STEP 1: Import to TradingView** (2 minutes)

1. Open file: `Updated Signals and Overlays.html`
2. **Copy all code** (Ctrl+A, Ctrl+C)
3. Go to TradingView → Pine Editor
4. Paste code → Save
5. Add to Chart

**✅ Done!** Indicator is now on your chart.

---

### **STEP 2: Create 10 Alerts** (10 minutes)

For each timeframe, create **2 alerts** (Bullish + Bearish):

#### **Alert Template:**

**Name:** `XAUUSD [Timeframe] [Direction]`
**Condition:** Select from dropdown
**Webhook URL:** `http://your-bot-ip:80/webhook`

**Message:**
```json
{
  "type": "trend",
  "symbol": "{{ticker}}",
  "timeframe": "[TF]",
  "trend": "[DIRECTION]",
  "strategy": "ZepixPremium"
}
```

#### **Replace Values:**

| Alert | [TF] | [DIRECTION] |
|-------|------|-------------|
| 5M Bullish | `5m` | `bull` |
| 5M Bearish | `5m` | `bear` |
| 15M Bullish | `15m` | `bull` |
| 15M Bearish | `15m` | `bear` |
| 1H Bullish | `1h` | `bull` |
| 1H Bearish | `1h` | `bear` |
| 4H Bullish | `4h` | `bull` |
| 4H Bearish | `4h` | `bear` |
| 1D Bullish | `1d` | `bull` |
| 1D Bearish | `1d` | `bear` |

**✅ Done!** All alerts configured.

---

### **STEP 3: Test Bot** (2 minutes)

**Check bot is receiving:**

```powershell
# In PowerShell, test webhook:
Invoke-WebRequest -Uri "http://localhost:80/webhook" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"type":"trend","symbol":"XAUUSD","timeframe":"5m","trend":"bull"}'
```

**Expected Bot Response:**
```
📊 TREND UPDATE
Symbol: XAUUSD
Timeframe: 5m
New Trend: BULL
```

**✅ Done!** Bot is ready to receive trend updates.

---

## 📊 ALERT CHECKLIST

Use this checklist to track alert setup:

### **5M Timeframe:**
- [ ] 5M Bullish Trend
- [ ] 5M Bearish Trend

### **15M Timeframe:**
- [ ] 15M Bullish Trend
- [ ] 15M Bearish Trend

### **1H Timeframe:**
- [ ] 1H Bullish Trend
- [ ] 1H Bearish Trend

### **4H Timeframe:**
- [ ] 4H Bullish Trend
- [ ] 4H Bearish Trend

### **1D Timeframe:**
- [ ] 1D Bullish Trend
- [ ] 1D Bearish Trend

**Total: 10 alerts** ✅

---

## 🎯 WEBHOOK MESSAGE TEMPLATES

### **5M Alerts:**

**Bullish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"5m","trend":"bull","strategy":"ZepixPremium"}
```

**Bearish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"5m","trend":"bear","strategy":"ZepixPremium"}
```

### **15M Alerts:**

**Bullish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"15m","trend":"bull","strategy":"ZepixPremium"}
```

**Bearish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"15m","trend":"bear","strategy":"ZepixPremium"}
```

### **1H Alerts:**

**Bullish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"1h","trend":"bull","strategy":"ZepixPremium"}
```

**Bearish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"1h","trend":"bear","strategy":"ZepixPremium"}
```

### **4H Alerts:**

**Bullish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"4h","trend":"bull","strategy":"ZepixPremium"}
```

**Bearish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"4h","trend":"bear","strategy":"ZepixPremium"}
```

### **1D Alerts:**

**Bullish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"1d","trend":"bull","strategy":"ZepixPremium"}
```

**Bearish:**
```json
{"type":"trend","symbol":"{{ticker}}","timeframe":"1d","trend":"bear","strategy":"ZepixPremium"}
```

---

## ⚙️ ALERT SETTINGS

For **each alert**, configure:

| Setting | Value |
|---------|-------|
| **Condition** | (Select from dropdown) |
| **Options** | Once Per Bar Close |
| **Expiration** | Open-ended |
| **Alert Actions** | Webhook URL |
| **Webhook URL** | `http://your-bot-ip:80/webhook` |
| **Message** | (Use templates above) |
| **Alert Name** | Descriptive (e.g., "XAUUSD 5M Bull") |

---

## 🔍 VERIFICATION STEPS

### **1. Pine Script Loaded:**
- [ ] Indicator visible on chart
- [ ] Table showing all timeframes
- [ ] No compilation errors

### **2. Alerts Created:**
- [ ] 10 total alerts in TradingView
- [ ] All webhooks configured
- [ ] All alerts enabled (not paused)

### **3. Bot Integration:**
- [ ] Bot running on port 80
- [ ] Webhook test successful
- [ ] Bot logs show trend updates

### **4. Real-Time Test:**
- [ ] Wait for trend change on chart
- [ ] Alert fires automatically
- [ ] Bot receives and updates trend
- [ ] Check `/data/timeframe_trends.json`

---

## 🐛 TROUBLESHOOTING

### **Alerts Not Firing:**
1. Check indicator is on chart
2. Verify alert condition selected correctly
3. Ensure alerts are not paused
4. Check TradingView subscription allows alerts

### **Bot Not Receiving:**
1. Verify bot running: `python src/main.py`
2. Check port 80 is open
3. Test webhook manually (see Step 3)
4. Check firewall settings

### **Webhook Errors:**
1. Verify JSON format (use JSON validator)
2. Check URL is correct
3. Ensure Content-Type is `application/json`
4. Review bot logs for error messages

---

## 📞 NEED HELP?

**Check these files:**
1. `UPDATE_NOTES.md` - Full documentation
2. `Updated Signals and Overlays.html` - Pine Script code
3. Bot logs - `python src/main.py` output

**Common Issues:**
- **Webhook fails:** Check bot IP and port
- **Alert doesn't fire:** Verify condition setup
- **Bot doesn't update:** Check JSON message format

---

## ✅ SUCCESS CONFIRMATION

**You'll know it's working when:**

1. ✅ Chart shows trend changes visually
2. ✅ TradingView alerts fire automatically
3. ✅ Bot logs show: `📊 TREND UPDATE`
4. ✅ `/data/timeframe_trends.json` updates automatically
5. ✅ Entry signals check trends correctly

---

## 🎉 YOU'RE DONE!

**Setup Complete! Your bot now:**
- ✅ Receives real-time trend updates
- ✅ Auto-syncs with TradingView
- ✅ Makes better trading decisions
- ✅ No manual trend updates needed

**Time to Trade!** 🚀

---

**Total Setup Time:** ~15 minutes
**Maintenance Required:** None (automatic)
**Bot Enhancement:** 100% ready for autonomous trading
