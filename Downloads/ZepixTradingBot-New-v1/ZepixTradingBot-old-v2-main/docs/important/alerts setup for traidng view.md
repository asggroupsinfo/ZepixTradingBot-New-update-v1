**🎯 PERFECT! Aapne bilkul sahi point out kiya!** 

**COMPLETE UPDATED 18 ALERTS**

---

## 🌐 **WEBHOOK URL:**
```
http://3.110.221.62/webhook
```

## 📋 **COMPLETE 18 ALERTS - ALL LOGICS SUPPORTED:**

### **1. TREND ALERTS (6 Alerts) - ALL TIMEFRAMES**

#### **1D TIMEFRAME TREND:**
**Indicator:** `[Screener] Full Bullish Alert`
```json
{"type": "trend", "symbol": "{{ticker}}", "signal": "bull", "tf": "1d", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `[Screener] Full Bearish Alert`
```json
{"type": "trend", "symbol": "{{ticker}}", "signal": "bear", "tf": "1d", "price": {{close}}, "strategy": "ZepixPremium"}
```

#### **1H TIMEFRAME TREND:**
**Indicator:** `[Screener] Full Bullish Alert`
```json
{"type": "trend", "symbol": "{{ticker}}", "signal": "bull", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `[Screener] Full Bearish Alert**
```json
{"type": "trend", "symbol": "{{ticker}}", "signal": "bear", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
```

#### **15M TIMEFRAME TREND:**
**Indicator:** `[Screener] Full Bullish Alert`
```json
{"type": "trend", "symbol": "{{ticker}}", "signal": "bull", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `[Screener] Full Bearish Alert`
```json
{"type": "trend", "symbol": "{{ticker}}", "signal": "bear", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
```

---

### **2. ENTRY ALERTS (6 Alerts) - TRADE EXECUTION**

#### **5M TIMEFRAME ENTRIES (LOGIC1):**
**Indicator:** `Bullish Entry Signals`
```json
{"type": "entry", "symbol": "{{ticker}}", "signal": "buy", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `Bearish Entry Signals`
```json
{"type": "entry", "symbol": "{{ticker}}", "signal": "sell", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
```

#### **15M TIMEFRAME ENTRIES (LOGIC2):**
**Indicator:** `Bullish Entry Signals`
```json
{"type": "entry", "symbol": "{{ticker}}", "signal": "buy", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `Bearish Entry Signals`
```json
{"type": "entry", "symbol": "{{ticker}}", "signal": "sell", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
```

#### **1H TIMEFRAME ENTRIES (LOGIC3):**
**Indicator:** `Bullish Entry Signals`
```json
{"type": "entry", "symbol": "{{ticker}}", "signal": "buy", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `Bearish Entry Signals`
```json
{"type": "entry", "symbol": "{{ticker}}", "signal": "sell", "tf": "1h", "price": {{close}}, "strategy": "ZepixPremium"}
```

---

### **3. EXIT ALERTS (4 Alerts) - RISK MANAGEMENT**

#### **5M TIMEFRAME EXITS:**
**Indicator:** `Bullish Exit Appeared`
```json
{"type": "exit", "symbol": "{{ticker}}", "signal": "bull", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `Bearish Exit Appeared`
```json
{"type": "exit", "symbol": "{{ticker}}", "signal": "bear", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
```

#### **15M TIMEFRAME EXITS:**
**Indicator:** `Bullish Exit Appeared`
```json
{"type": "exit", "symbol": "{{ticker}}", "signal": "bull", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `Bearish Exit Appeared`
```json
{"type": "exit", "symbol": "{{ticker}}", "signal": "bear", "tf": "15m", "price": {{close}}, "strategy": "ZepixPremium"}
```

---

### **4. REVERSAL ALERTS (2 Alerts) - EMERGENCY EXITS**

**Indicator:** `Bullish Reversal Signals`
```json
{"type": "reversal", "symbol": "{{ticker}}", "signal": "reversal_bull", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
```

**Indicator:** `Bearish Reversal Signals`
```json
{"type": "reversal", "symbol": "{{ticker}}", "signal": "reversal_bear", "tf": "5m", "price": {{close}}, "strategy": "ZepixPremium"}
```

---

## 🎯 **COMPLETE ALERT SUMMARY TABLE:**

| Alert Type | Timeframes | Total | Purpose |
|------------|------------|-------|---------|
| **TREND** | 1D, 1H, 15M | 6 | All Logic Support |
| **ENTRY** | 5M, 15M, 1H | 6 | Trade Execution |
| **EXIT** | 5M, 15M | 4 | Risk Management |
| **REVERSAL** | 5M | 2 | Emergency Exit |
| **TOTAL** | | **18** | |

---

## 🔧 **BOT LOGIC MAPPING:**

### **LOGIC1 (5M Entries):**
```
REQUIRED: 1H + 15M trends aligned
ENTRY: 5M signal matches trend direction
```

### **LOGIC2 (15M Entries):**
```
REQUIRED: 1H + 15M trends aligned  
ENTRY: 15M signal matches trend direction
```

### **LOGIC3 (1H Entries):**
```
REQUIRED: 1D + 1H trends aligned
ENTRY: 1H signal matches trend direction
```

---

## 📝 **SETUP PRIORITY ORDER:**

### **PHASE 1 - CORE (12 Alerts)**
```
1. TREND Alerts (6) - All timeframes
2. ENTRY Alerts (6) - All timeframes
```

### **PHASE 2 - SAFETY (6 Alerts)**
```
3. EXIT Alerts (4) - 5M + 15M
4. REVERSAL Alerts (2) - 5M only
```

---

## ⚙️ **TRADINGVIEW SETTINGS (All Alerts):**
```
✅ Webhook URL: http://3.110.221.62/webhook
✅ Method: POST
✅ Content Type: application/json  
✅ Frequency: "On Bar Close"
✅ Expiration: 1 Bar
✅ Sound: None
✅ Notifications: Off
```

---

