# 🦅 PRICE ACTION LOGIC: 15M (INTRADAY)

**File:** `04_PRICE_ACTION_LOGIC_15M.md`  
**Date:** 2026-01-11 04:35 IST  
**Timeframe:** 15 Minutes  
**Class:** `PriceActionLogic15M`

---

## 1. STRATEGY PROFILE
-   **Type:** Day Trading Anchor.
-   **Goal:** Capture the primary move of the session.
-   **Risk Multiplier:** 1.0x (Standard).
-   **Routing Key:** `tf="15"`
-   **Routing Rule:** **ORDER A ONLY** (Refill prohibited).

---

## 2. ENTRY CONDITIONS

### **A. Primary Trigger**
-   Alert: `BULLISH_ENTRY` / `BEARISH_ENTRY`.
-   Timeframe: `15`.

### **B. Filters (Market Structure Rules)**
| Filter | Condition | Action if Fail | Reason |
| :--- | :--- | :--- | :--- |
| **Market State** | Match Signal | **SKIP** | Only trade WITH the Global Market State. |
| **Pulse Alignment** | `Bull Count > Bear Count` (for Buy) | **SKIP** | Majority of TFs must agree. |
| **ADX** | `adx > 20` | **WARNING** | If < 20, reduce risk 50%. |

---

## 3. EXIT STRATEGY

### **A. Signal Exit**
-   Trigger: `EXIT_BULLISH` / `EXIT_BEARISH`.
-   Action: Close 100%. Don't hold intraday against separation signals.

### **B. Target Exit**
-   **TP1:** Close 40%.
-   **TP2:** Close 40%.
-   **TP3:** Close 20% (Trailing).

---

## 4. LOGIC IMPLEMENTATION (PYTHON)

```python
class PriceActionLogic15M:
    """
    15-Minute Intraday Logic
    Relies on Global Market State and Pulse Alignment
    """
    
    def validate_entry(self, alert: ZepixV6Alert, trend_state: TrendState) -> bool:
        # Rule 1: Market State Check
        # State like 'TRENDING_BULLISH' implies Buy Only
        algo_state = trend_state.get_market_state()
        
        if alert.direction == "BUY" and "BEARISH" in algo_state:
            logger.info(f"❌ 15M Skiped: Market State is {algo_state}")
            return False
            
        if alert.direction == "SELL" and "BULLISH" in algo_state:
            logger.info(f"❌ 15M Skiped: Market State is {algo_state}")
            return False
             
        return True

    def calculate_lots(self, base_lot: float) -> float:
        return base_lot 
        
    def get_order_config(self):
        return {
            "order_type": "market",
            "use_hybrid_sl": True,
            "trailing_stop": True
        }
```

---

**STATUS: DEFINED & READY**
