# ZEPIX TRADING BOT: 2.0 DUAL CORE ARCHITECTURE MASTER PLAN

## 1. STRATEGIC VISION
To evolve the Zepix Trading Bot into a high-performance **Dual Core System**, running two independent logic engines in parallel. This architecture ensures legacy stability while introducing cutting-edge Price Action logic without conflict.

### The Dual Core Concept
The bot will be internally split into two autonomous groups:
*   **Group 1: Combined Logic (Legacy Core)** - Preserves the proven V3 strategies.
*   **Group 2: Price Action Logic (V6 Core)** - Executes new high-precision V6 strategies.

Each group operates with **Total Isolation**: separate databases, separate state managers, and separate execution rules.

---

## 2. SYSTEM ARCHITECTURE

### GROUP 1: COMBINED LOGIC (Legacy)
*   **Purpose:** Continue executing existing V3 logic.
*   **Alert Source:** Standard Zepix V3 Indicators.
*   **Logic Modules:**
    *   `CombinedLogic-1` (Former Logic 1 / 5m)
    *   `CombinedLogic-2` (Former Logic 2 / 15m)
    *   `CombinedLogic-3` (Former Logic 3 / 1h)
*   **Database:** `data/zepix_combined_logic.db`
*   **Order Execution:** **Standard Dual Orders** (Order A + Order B) for all timeframes.
*   **Trend Source:** Traditional Timeframe Trend Manager (1H/1D/etc).

### GROUP 2: PRICE ACTION LOGIC (New V6)
*   **Purpose:** Execute high-frequency Price Action strategies.
*   **Alert Source:** New V6 Pine Script (Pipe-Separated Payloads).
*   **Logic Modules:**
    *   `PriceActionLogic-1M` (Scalping)
    *   `PriceActionLogic-5M` (Momentum)
    *   `PriceActionLogic-15M` (Intraday)
    *   `PriceActionLogic-1H` (Swing)
*   **Database:** `data/zepix_price_action.db`
*   **Order Execution:** **Specialized Routing Rules** (See Section 3).
*   **Trend Source:** New V6 **Trend Pulse System** (Real-time aligned trends).

---

## 3. ORDER EXECUTION ROUTING MATRIX (Group 2 Only)

For **Group 2 (Price Action Logic)**, order execution is strictly routed based on timeframe to optimize for specific market behaviors.

| Timeframe | Strategy Type | Execution Logic | Routing Rule |
| :--- | :--- | :--- | :--- |
| **1 Min** | Scalping | **ORDER B ONLY** | ❌ Order A Restricted. ✅ Order B Executes (Trailing/Profit Booking). |
| **5 Min** | Momentum | **DUAL ORDERS** | ✅ Order A (TP Trail). ✅ Order B (Profit Trail). |
| **15 Min** | Intraday | **ORDER A ONLY** | ✅ Order A Executes. ❌ Order B Restricted. |
| **1 Hour** | Swing | **ORDER A ONLY** | ✅ Order A Executes. ❌ Order B Restricted. |

> **Note:** "Order A" refers to the primary position with fixed/trailing TP. "Order B" refers to the secondary profit-booking position (often risk-free).

---

## 4. DATABASE & STATE ISOLATION

To prevent "Feature Conflict" (e.g., a Group 1 trade interfering with a Group 2 Re-entry Chain), the system implements **Hard State Isolation**:

### 1. Database Separation
*   **Combined Logic** writes to -> `zepix_combined_logic.db` (Trades, Chains, Sessions).
*   **Price Action Logic** writes to -> `zepix_price_action.db` (Trades, Chains, Sessions).

### 2. Manager Duplication
The `TradingEngine` will instantiate parallel instances of stateful managers:
*   `SessionManager_Combined` vs `SessionManager_PriceAction`
*   `ReEntryManager_Combined` vs `ReEntryManager_PriceAction`
*   `ProfitBooking_Combined` vs `ProfitBooking_PriceAction`

This ensures that a "Session Close" in Group 2 does NOT accidentally close Group 1 trades.

---

## 5. REVISED EXECUTION ROADMAP

### PHASE 1: FOUNDATION & SEPARATION
1.  **Database Upgrade:** Modify `TradeDatabase` to support dynamic filenames.
2.  **Engine Refactor:** Update `TradingEngine.__init__` to create the Dual Manager Stacks.
3.  **Config Update:** Split configuration parameters for Group 1 and Group 2.

### PHASE 2: GROUP 1 (COMBINED) MIGRATION
1.  **Rename:** Rename current logic flags to `combined_logic1_enabled`, etc.
2.  **Bind:** Ensure legacy `execute_trades` binds strictly to `db_combined` and its managers.
3.  **Verify:** Test that legacy alerts still function correctly in their isolated lane.

### PHASE 3: GROUP 2 (PRICE ACTION) IMPLEMENTATION
1.  **V6 Models:** Re-implement Pydantic models for V6 alerts.
2.  **Logic Classes:** Implement `PriceActionLogic` classes (1-4).
3.  **Routing Engine:** Implement `execute_v6_entry` with the **Matrix Switch** (1m->B, etc).
4.  **Pulse Integration:** Implement Trend Pulse updates for Group 2's trend awareness.

### PHASE 4: FINAL INTEGRATION
1.  **Bot Startup:** Ensure both Cores initialize and connect to MT5.
2.  **Price Monitor:** Ensure `PriceMonitorService` iterates BOTH loops (Combined & PA).
3.  **Testing:** End-to-End simulation of simultaneous Combined and PA trades.

---

**Status:** PLANNING COMPLETE. Ready for Implementation.
