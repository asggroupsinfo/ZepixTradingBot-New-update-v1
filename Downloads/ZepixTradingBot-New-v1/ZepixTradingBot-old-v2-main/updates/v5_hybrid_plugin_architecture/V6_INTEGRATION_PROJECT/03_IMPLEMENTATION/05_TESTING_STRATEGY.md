# 🧪 V6 TESTING STRATEGY: 4-TIER VERIFICATION

**File:** `05_TESTING_STRATEGY.md`  
**Date:** 2026-01-11 04:50 IST  
**Goal:** Zero-Bug Deployment

---

## 1. UNIT TESTS (PYTHON)
**Focus:** Payload Parsing & Logic Routing.

-   **Test A: Parser Accuracy**
    -   Input: Raw JSON String (15 fields).
    -   Verify: `adx=26.5`, `conf_score=85`.
    -   Command: `pytest tests/v6/test_parser.py`

-   **Test B: Routing Logic**
    -   Input: Alert with `tf="1"`.
    -   Verify: Routed to `logic_1m`.
    -   Input: Alert with `tf="60"`.
    -   Verify: Routed to `logic_1h`.

---

## 2. LOGIC SIMULATION (DRY RUN)
**Focus:** Filter Rules.

-   **Test C: 1M Logic Filter**
    -   Scenario: ADX=15.
    -   Expected: `validate_entry` returns `False` (Skipped).
    -   Scenario: ADX=25.
    -   Expected: `validate_entry` returns `True`.

-   **Test D: Trend Alignment**
    -   Scenario: 15m Signal BUY, Global Trend BEARISH.
    -   Expected: Skipped.

---

## 3. INTEGRATION TEST (LIVE DB)
**Focus:** Pulse Update.

-   **Test E: Pulse Update**
    -   Action: Send `TREND_PULSE` alert.
    -   Verify: Database `market_trends` table updates correctly.
    -   Verify: `get_alignment()` reflects new state.

---

## 4. END-TO-END (PAPER TRADING)
**Focus:** Full Cycle.

-   **Test F: Full Trade**
    -   Send `BULLISH_ENTRY`.
    -   Verify Orders Placed (Smart SL + Fixed SL).
    -   Send `EXIT_BULLISH`.
    -   Verify Trade Closed.

**STATUS: STRATEGY DEFINED**
