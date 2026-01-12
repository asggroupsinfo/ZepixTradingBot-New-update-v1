# 🛠️ V6 IMPLEMENTATION: CODE CHANGES REQUIRED

**File:** `01_CODE_CHANGES_REQUIRED.md`  
**Date:** 2026-01-11 04:30 IST  
**Phase:** 3 (Implementation Details)  
**Root Path:** `.../ZepixTradingBot-old-v2-main/ZepixTradingBot-old-v2-main`

---

## 1. FILE MODIFICATION LIST

### **A. Data Models**
**File:** `src/v3_alert_models.py`
-   **Action:** Modify `ZepixV3Alert` (or create `ZepixV6Alert`).
-   **Changes:**
    -   Add fields: `adx` (float), `adx_strength` (str), `confidence_score` (int).
    -   Add fields: `trend_pulse_alignment` (str), `trendline_status` (str).
    -   Add fields: `market_state` (str).

### **B. Configuration**
**File:** `config/config.json`
-   **Action:** Add V6 Feature Toggles.
-   **New Section:**
    ```json
    "v6_integration": {
      "enable_adx_filter": true,
      "enable_momentum_monitor": true,
      "enable_pulse_db_update": true
    }
    ```

### **C. Alert Processor**
**File:** `src/processors/alert_processor.py`
-   **Action:** Update parsing logic.
-   **Changes:**
    -   Add `parse_v6_payload()` method.
    -   Handle 15-field payload.
    -   Implement `_handle_trend_pulse_alert()` to update DB.

### **D. Trading Engine (CORE)**
**File:** `src/core/trading_engine.py`
-   **Action:** Implement 4-Logic Routing.
-   **Changes:**
    -   Remove `_route_v3_to_logic` (Logic 1/2/3).
    -   Add `PriceActionLogic` class/methods.
    -   Implement routing: `1m` -> `logic_1m`, `5m` -> `logic_5m`, etc.
    -   Add `check_adx_filter(alert)` method.

### **E. Database Manager** (New/Update)
**File:** `src/core/database_manager.py` (or equivalent)
-   **Action:** Ensure `market_trends` table exists.
-   **Changes:** Add methods to `update_trend_pulse(tf, direction)`.

---

## 2. NEW FILES TO CREATE

1.  **`src/core/logics/price_action_logics.py`**
    -   *Purpose:* Encapsulate the 4 Logic Classes (1m, 5m, 15m, 1h) to keep Engine clean.
    -   *Why:* SOLID Principles. Single Responsibility.

2.  **`src/core/state/trend_manager.py`**
    -   *Purpose:* Handle `TREND_PULSE` updates and provide `get_alignment()` API.

---

## 3. IMPLEMENTATION SEQUENCE

1.  **Step 1:** Update `ZepixV3Alert` model (Foundation).
2.  **Step 2:** Update `alert_processor.py` to parse new JSON (Input).
3.  **Step 3:** Create `trend_manager.py` (State).
4.  **Step 4:** Create `price_action_logics.py` (Brain).
5.  **Step 5:** Wire it all up in `trading_engine.py` (Execution).

**STATUS: PLANNED - READY TO CODE**
