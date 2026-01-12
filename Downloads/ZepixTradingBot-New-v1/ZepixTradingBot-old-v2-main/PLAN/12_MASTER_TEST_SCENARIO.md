# Master Test Scenario: End-to-End System Integrity

This document outlines the five ultimate scenarios designed to verify the Zepix Trading Bot as a cohesive unit. These tests cover the complete lifecycle from webhook ingestion to trade finalization and system recovery.

## 🟢 Scenario 1: The Perfect Trade (Profit Progression)
**Objective:** Verify the "Happy Path" where a trade hits TP and triggers the Profit Booking System to scale up.

1.  **Trigger:** Incoming Webhook (BUY EURUSD, LOGIC1).
2.  **Action:** `TradingEngine` places **Dual Orders** (Order A & Order B).
3.  **Event:** Price moves in favor. Order A hits TP1.
4.  **Reaction:**
    *   Order A closes (Bank Profit).
    *   **Order B** enters `ProfitBookingChain` (Level 1).
    *   `Database` records the new Chain ID.
    *   SL is moved to Breakeven.
5.  **Conclusion:** Order B hits Level 2 Target. SL tightens further. State saved to DB.

## 🔴 Scenario 2: The Recovery Warrior (SL Hunt & Recovery)
**Objective:** Verify the autonomous "SL Hunt Recovery" mechanism when a stop loss is hunted.

1.  **Trigger:** Incoming Webhook (SELL GBPUSD, LOGIC2).
2.  **Action:** Trade placed.
3.  **Event:** Price spikes against trade, hitting SL.
4.  **Watchman:**
    *   `PriceMonitorService` detects closed trade.
    *   Checks `sl_hunt_pending` list.
    *   Verifies 70% Recovery Logic (Price enters "Recovery Window").
5.  **Reaction:** `ReEntryManager` triggers immediate **Re-Entry Order** with optimized lot size.
6.  **Conclusion:** Re-entry trade turns profit. Chain resumed.

## 🛡️ Scenario 3: The Shield Defense (Trend Reversal)
**Objective:** Verify the "Reverse Shield" protection against sudden trend changes.

1.  **Trigger:** Open position (BUY XAUUSD).
2.  **Event:** **Opposite Signal** received (SELL XAUUSD) or Trend Manager detects "BEARISH_LOCK".
3.  **Action:** `ReverseShieldManager` calculates potential loss.
4.  **Reaction:**
    *   Original BUY trade is **Emergency Closed**.
    *   New SELL trade (Reverse Shield) is placed immediately.
    *   Lot size calculated to recover the loss of the closed trade.
5.  **Conclusion:** Account equity protected; bad trade swapped for good trade.

## ⏱️ Scenario 4: The Watchman's Duty (Stagnation & Margin)
**Objective:** Verify background monitoring for stale trades and account health.

1.  **Trigger:** Trade open for extended period (e.g., > 4 hours) with low volatility.
2.  **Watchman:**
    *   `PriceMonitorService` scan cycle (2s interval).
    *   Detects `open_time` exceeds `max_hold_time`.
3.  **Action:** Triggers **Time-Based Exit**.
4.  **Sub-Scenario (Margin):**
    *   Simulate Equity Drop (Margin Level < 100%).
    *   Watchman detects "CRITICAL MARGIN".
    *   Triggers **Emergency Liquidation** of largest losing position.

## 🧟 Scenario 5: The Resurrection (Crash Recovery)
**Objective:** Verify the system's ability to pick up where it left off after a restart.

1.  **State:** Open trades (EURUSD, GBPUSD) and active Chains exist.
2.  **Event:** System **CRASH** (Simulate `sys.exit()` or Process Kill).
3.  **Action:** System **RESTART**.
4.  **Reaction:**
    *   `TradingEngine` initializes.
    *   `ProfitBookingManager` calls `recover_chains_from_database()`.
    *   `ReEntryManager` re-populates pending SL Hunt targets from DB.
5.  **Conclusion:** Watchman resumes monitoring the *original* trades. No data lost.
