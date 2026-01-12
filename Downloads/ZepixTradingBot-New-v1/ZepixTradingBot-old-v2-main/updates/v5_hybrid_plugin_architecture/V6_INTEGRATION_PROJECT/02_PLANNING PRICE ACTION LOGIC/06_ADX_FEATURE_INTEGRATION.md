# 📊 ADX & MOMENTUM FEATURE INTEGRATION

**File:** `06_ADX_FEATURE_INTEGRATION.md`  
**Date:** 2026-01-11 04:45 IST  
**Feature:** ADX (Average Directional Index)
**Payload Indices:** 7 (Value), 8 (Strength)

---

## 1. DATA EXTRACTION

### **Payload Parsing**
The `AlertProcessor` must extract:
```python
adx_value = float(payload[7])       # e.g., 25.5
adx_strength = str(payload[8])      # "STRONG", "MODERATE", "WEAK", "NA"
```

### **Handling "NA"**
If `enableADX = false` in Pine Script, values will be `NA`.
-   **Bot Action:** Treat `NA` as "Neutral" or "Pass".
-   **Assumption:** We assume `enableADX = true` for V6 Integration.

---

## 2. INTEGRATION RULES BY STRATEGY

### **A. Scalping (1m)**
-   **Rule:** `ADX > 20`.
-   **Logic:** Scalping requires *movement*. Low ADX = Chop = Whipsaw.
-   **Action:** REJECT trade if ADX < 20.

### **B. Momentum (5m)**
-   **Rule:** `ADX > 25` AND `adx_strength != "WEAK"`.
-   **Logic:** Momentum trades need *strength*.
-   **Action:** REJECT trade if ADX < 25.

### **C. Intraday (15m)**
-   **Rule:** ADX acts as **Risk Modulator**.
    -   `ADX > 20`: 1.0x Lots.
    -   `ADX < 20`: 0.5x Lots.
-   **Action:** Adjust lot size.

### **D. Swing (1H)**
-   **Rule:** ADX monitors **Trend Exhaustion**.
    -   `ADX > 50`: Warning! Trend might reverse.
-   **Action:** Log warning, maybe tighten stops.

---

## 3. MOMENTUM CHANGE ALERT HANDLING

**Alert:** `MOMENTUM_CHANGE`
**Usage:** Live Market State Update.

```python
def handle_momentum_change(self, alert):
    """
    Called when ADX shifts significantly
    """
    symbol = alert.symbol
    tf = alert.tf
    direction = alert.raw_payload[7] # INCREASING / DECREASING
    
    # Update Shared State
    self.trend_state.update_momentum(symbol, tf, direction)
    
    # Trigger Logic Check?
    # Option: If we have an open trade and Momentum decreases -> Tighten Stop
    self.trade_manager.adjust_risk_for_momentum(symbol, direction)
```

---

## 4. CODE SNIPPET (ADX FILTER)

```python
class ADXFilter:
    @staticmethod
    def validate(alert: ZepixV6Alert, min_adx: float = 20.0) -> bool:
        if alert.adx is None:
            return True # Pass if data missing
            
        if alert.adx < min_adx:
            return False
            
        return True
```

**STATUS: DEFINED**
