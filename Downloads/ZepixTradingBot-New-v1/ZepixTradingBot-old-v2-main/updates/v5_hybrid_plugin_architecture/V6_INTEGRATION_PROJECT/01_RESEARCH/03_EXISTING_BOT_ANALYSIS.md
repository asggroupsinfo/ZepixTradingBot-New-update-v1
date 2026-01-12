# 🤖 EXISTING BOT ANALYSIS (V3 ARCHITECTURE)

**File:** `03_EXISTING_BOT_ANALYSIS.md`  
**Date:** 2026-01-11 04:10 IST  
**Source:** V3 Verification Reports (Source Code Not Detected in Workspace)  
**Verification Level:** Inferred from `V3_FINAL_REPORTS/02_IMPLEMENTATION_VERIFICATION_REPORT.md`

---

## 🚨 CRITICAL NOTE
The bot source code (`ZepixTradingBot-old-v5`) was **NOT FOUND** in the active workspace. This analysis relies 100% on the verified `V3_FINAL_REPORTS`. The V3 architecture described below is the **Confirmed Production State** as of Jan 8, 2026.

---

## 1. CURRENT ARCHITECTURE

### **Data Flow**
1.  **Webhook** receives JSON payload.
2.  **AlertProcessor** validates and converts to `ZepixV3Alert` (Pydantic Model).
3.  **TradingEngine** receives validated alert.
4.  **Routing Logic** determines execution path.
5.  **Order Manager** places hybrid orders (Order A + Order B).

### **Core Components (Confirmed)**
-   **`src/v3_alert_models.py`**: Defines `ZepixV3Alert` schema.
-   **`src/processors/alert_processor.py`**: Handles MTF decoding (`1,1,-1...`) and validation.
-   **`src/core/trading_engine.py`**: Contains `execute_v3_entry` and logic routing.
-   **`config/config.json`**: Defines multipliers for `logic1`, `logic2`, `logic3`.

---

## 2. THE "3-LOGIC" SYSTEM (TO BE REMOVED)

The current bot uses a **3-Tier Routing System** based on Timeframe:

| Logic ID | Profile | Timeframes | Multiplier | Status for V6 |
| :--- | :--- | :--- | :--- | :--- |
| **LOGIC1** | Scalping | 5m | 1.25x | ❌ **REMOVE** |
| **LOGIC2** | Intraday | 15m | 1.0x | ❌ **REMOVE** |
| **LOGIC3** | Swing | 1H, 4H | 0.625x | ❌ **REMOVE** |

**Current Routing Code (Inferred):**
```python
def _route_v3_to_logic(self, alert):
    if alert.tf == "5": return "LOGIC1"
    elif alert.tf == "15": return "LOGIC2"
    elif alert.tf in ["60", "240"]: return "LOGIC3"
    return "LOGIC2"
```

**Why Remove?**
V6 requires **4 Specific Price Action Logics** (1m, 5m, 15m, 1h) with distinct behaviors, not just multipliers.

---

## 3. INTEGRATION POINTS FOR V6

### **A. Pydantic Model Update**
**Target:** `src/v3_alert_models.py`
-   **Current:** `ZepixV3Alert` (optimized for V3 signals).
-   **Required:** `ZepixV6Alert` (or update V3 model).
-   **New Fields:** `adx`, `adx_strength`, `confidence_score`, `trend_pulse_alignment`, `trendline_status`.

### **B. Routing Matrix Rebuild**
**Target:** `src/core/trading_engine.py` -> `_route_v3_to_logic`
-   **Action:** Replace 3-Logic hardcoding with 4-Logic dynamic mapping.
-   **New Mapping:**
    -   1m -> `PRICE_ACTION_1M`
    -   5m -> `PRICE_ACTION_5M`
    -   15m -> `PRICE_ACTION_15M`
    -   60m -> `PRICE_ACTION_1H`

### **C. Feature Feature Integration**
**Target:** `src/core/trading_engine.py` -> `execute_v3_entry`
-   **Current:** Uses `position_multiplier` and `consensus_score`.
-   **Required:** Add checks for `ADX > Threshold` and `Momentum` direction before placing orders.

### **D. Trend Update Mechanism**
**Target:** `src/processors/alert_processor.py` -> `validate_v3_alert`
-   **Current:** Updates DB using `mtf_trends` string from signal (e.g. "1,1,-1...").
-   **Required:** Switch to `TREND_PULSE` alert data. The entry signal should NO LONGER update the trend database.

---

## 4. CODE REMOVAL CHECKLIST

-   [ ] Remove `LOGIC1`, `LOGIC2`, `LOGIC3` definitions from `config.json`.
-   [ ] Remove `_route_v3_to_logic` current implementation.
-   [ ] Remove `should_bypass_trend_check` logic (if V6 adheres to trend strictness).
-   [ ] Remove signal-based Trend DB updates (move to dedicated `TREND_PULSE` handler).

---

**VERDICT:**
The existing system is modular enough to upgrade, provided we cleanly rip out the 3-Logic routing and replace the Data Model to support V6's rich payload.
