# ⚡ PRICE ACTION LOGIC: 1M (SCALPER)

**File:** `02_PRICE_ACTION_LOGIC_1M.md`  
**Date:** 2026-01-11 04:25 IST  
**Timeframe:** 1 Minute  
**Class:** `PriceActionLogic1M`

---

## 1. STRATEGY PROFILE
-   **Type:** Hyper-Scalping.
-   **Goal:** Capture quick 10-20 pip moves.
-   **Risk Multiplier:** 0.5x (Half size due to noise).
-   **Routing Key:** `tf="1"`
-   **Routing Rule:** **ORDER B ONLY** (No Main Orders).

---

## 2. ENTRY CONDITIONS

### **A. Primary Trigger**
-   Alert Type: `BULLISH_ENTRY` or `BEARISH_ENTRY`.
-   Timeframe: `1`.

### **B. Filters (Scalper Rules)**
| Filter | Condition | Action if Fail | Reason |
| :--- | :--- | :--- | :--- |
| **ADX Check** | `adx > 20` | **SKIP** | Avoid dead/choppy markets. |
| **Confidence** | `score >= 80` | **SKIP** | 1m noise requires high confidence. |
| **Trend Pulse** | **IGNORE** | N/A | 1m is too fast for 4H alignment. |
| **Spread** | `< 2 Pips` | **SKIP** | Spread kills scalping profit. |

---

## 3. EXIT STRATEGY

### **A. Signal Exit**
-   Trigger: `EXIT_BULLISH` / `EXIT_BEARISH`.
-   Action: **CLOSE ALL IMMEDIATELY**. Speed is key.

### **B. Target Exit**
-   **TP1:** Close 50% (Lock profit early).
-   **TP2:** Close 50% (Runner).
-   **Trailing:** Activate immediately at TP1.

---

## 4. LOGIC IMPLEMENTATION (PYTHON)

```python
class PriceActionLogic1M:
    """
    1-Minute Scalping Logic
    High ADX, High Confidence, Quick Exits
    """
    
    def validate_entry(self, alert: ZepixV6Alert) -> bool:
        # Rule 1: ADX Filter
        if alert.adx is None or alert.adx < 20: 
            logger.info("❌ 1M Skiped: ADX < 20 (Choppy)")
            return False
            
        # Rule 2: High Confidence
        if alert.confidence_score < 80:
            logger.info(f"❌ 1M Skiped: Confidence {alert.confidence_score} < 80")
            return False
            
        return True

    def calculate_lots(self, base_lot: float) -> float:
        # Rule 3: 0.5x Scaling
        return base_lot * 0.5
        
    def get_order_config(self):
        return {
            "order_type": "market",
            "use_hybrid_sl": True,  # Use Pine SL
            "trailing_stop": True   # Aggressive trailing
        }
```

---

## 5. SCENARIO SIMULATION

**Scenario:** 1m EURUSD Bullish Signal
-   **Data:** Price 1.0500, ADX 25, Conf 85.
-   **Action:**
    1.  Validate: ADX (25) > 20 ✅. Conf (85) > 80 ✅.
    2.  Execute: Buy 0.5 Lots.
    3.  Set SL: Pine Script Value (e.g. 1.0490).
    4.  Set TP1: Pine Script Value (e.g. 1.0510).

**Scenario:** 1m GBPUSD Choppy Signal
-   **Data:** Price 1.2200, ADX 15, Conf 90.
-   **Action:**
    1.  Validate: ADX (15) < 20 ❌.
    2.  Result: **NO TRADE**.

---

**STATUS: DEFINED & READY FOR IMPLEMENTATION**
