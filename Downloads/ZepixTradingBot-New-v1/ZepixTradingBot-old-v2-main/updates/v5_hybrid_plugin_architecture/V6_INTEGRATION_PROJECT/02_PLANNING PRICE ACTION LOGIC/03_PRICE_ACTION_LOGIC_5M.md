# 🚀 PRICE ACTION LOGIC: 5M (MOMENTUM)

**File:** `03_PRICE_ACTION_LOGIC_5M.md`  
**Date:** 2026-01-11 04:30 IST  
**Timeframe:** 5 Minutes  
**Class:** `PriceActionLogic5M`

---

## 1. STRATEGY PROFILE
-   **Type:** Momentum Trading.
-   **Goal:** Catch intraday breakouts and rapid moves.
-   **Risk Multiplier:** 1.0x (Standard Size).
-   **Routing Key:** `tf="5"`
-   **Routing Rule:** **DUAL ORDERS** (Order A + Order B).

---

## 2. ENTRY CONDITIONS

### **A. Primary Trigger**
-   Alert Type: `BULLISH_ENTRY` or `BEARISH_ENTRY`.
-   Timeframe: `5`.

### **B. Filters (Momentum Rules)**
| Filter | Condition | Action if Fail | Reason |
| :--- | :--- | :--- | :--- |
| **ADX Strength** | `adx >= 25` | **SKIP** | Need proven momentum, not just noise. |
| **Momentum Dir** | `increasing` | **WARNING** | Prefer increasing momentum. If decreasing, reduce lots 50%. |
| **Confidence** | `score >= 70` | **SKIP** | Standard confidence threshold. |
| **Alignment** | `Same as 15m` | **SKIP** | Must align with immediate higher TF. |

---

## 3. EXIT STRATEGY

### **A. Signal Exit**
-   Trigger: `EXIT_BULLISH` / `EXIT_BEARISH`.
-   Action: Close 80%. Leave 20% runner if in profit.

### **B. Target Exit**
-   **TP1:** Close 50% (Secure banking).
-   **TP2:** Close 30%.
-   **TP3:** Close 20% (Moonbag).
-   **Breakeven:** Move SL to Entry after TP1.

---

## 4. LOGIC IMPLEMENTATION (PYTHON)

```python
class PriceActionLogic5M:
    """
    5-Minute Momentum Logic
    Requires ADX > 25 and Trend Alignment
    """
    
    def validate_entry(self, alert: ZepixV6Alert, trend_state: TrendState) -> bool:
        # Rule 1: Momentum Strength
        if alert.adx < 25: 
            logger.info("❌ 5M Skiped: Low Momentum (ADX < 25)")
            return False
            
        # Rule 2: Immediate Higher TF Alignment (15m)
        tf_15m_trend = trend_state.get_trend("15")
        if tf_15m_trend != alert.direction:
             logger.info(f"❌ 5M Skiped: 15m Trend Mismatch ({tf_15m_trend} vs {alert.direction})")
             return False
             
        return True

    def calculate_lots(self, base_lot: float, alert: ZepixV6Alert) -> float:
        # Dynamic Sizing based on Momentum Direction
        # This requires parsing 'MOMENTUM_CHANGE' state stored in memory
        # For now, base lot
        return base_lot
        
    def get_order_config(self):
        return {
            "order_type": "market",
            "use_hybrid_sl": True,
            "breakeven_at": "tp1"
        }
```

---

**STATUS: DEFINED & READY**
