# 🎳 MOMENTUM MONITORING & STATE INTEGRATION

**File:** `07_MOMENTUM_FEATURE_INTEGRATION.md`  
**Date:** 2026-01-11 04:50 IST  
**Alert:** `MOMENTUM_CHANGE`  
**Type:** Real-Time Monitoring

---

## 1. PURPOSE
Unlike "ADX Filters" (which filter entries), this module **Monitors** the market's horsepower.
It answers: *"Is the trend accelerating or dying?"*

---

## 2. ALERT PAYLOAD PARSING
**Source:** `02_ALERT_JSON_PAYLOADS.md` (Index 3)

```python
# Payload Indices
TYPE = 0            # MOMENTUM_CHANGE
SYMBOL = 1
TF = 2
ADX_CURR = 3        # Float
ADX_STR_CURR = 4    # STRONG, MODERATE, WEAK
ADX_PREV = 5
ADX_STR_PREV = 6
DIRECTION = 7       # INCREASING, DECREASING
```

---

## 3. STATE UPDATE LOGIC (THE "DYNO")

We need a `MomentumState` class in the bot's memory.

```python
class MomentumState:
    def __init__(self):
        # Store by Symbol + TF
        self.states = {} 
        
    def update(self, symbol, tf, data):
        key = f"{symbol}_{tf}"
        self.states[key] = {
            "value": float(data['adx_curr']),
            "strength": data['adx_str_curr'],
            "direction": data['direction'],
            "last_updated": datetime.now()
        }
```

---

## 4. TRADING IMPLICATIONS

### **A. Entry Modification**
When `PriceActionLogic` requests entry, it checks `MomentumState`:
-   **If INCREASING:** Normal Execution.
-   **If DECREASING:** Warning! 
    -   *Logic:* "Trend is losing steam."
    -   *Action:* Reduce Lot Size by 25%.

### **B. Active Trade Management**
When `MOMENTUM_CHANGE` alert arrives:
-   **If Trend was STRONG -> Now WEAK:**
    -   *Action:* **Tighten Stop Loss** (Move to Trailing).
    -   *Reason:* The push is over. Protect profits.

---

## 5. SCENARIO

**Scenario:** Long EURUSD (5m) is open.
1.  **Alert:** `MOMENTUM_CHANGE|EURUSD|5|...|DECREASING` received.
2.  **Bot Action:** 
    -   Detects open Long.
    -   Sees momentum fading.
    -   **Triggers:** `update_sl_to_breakeven()` or `tighten_trailing_stop()`.

**STATUS: PLANNED**
