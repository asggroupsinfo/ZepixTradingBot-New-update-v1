# 📚 V3 INTEGRATION STUDY & STANDARDS

**File:** `04_V3_INTEGRATION_STUDY.md`  
**Date:** 2026-01-11 04:15 IST  
**Source:** V3 Verification Reports  
**Purpose:** Extract best practices for V6 Integration

---

## 1. SUCCESS FACTORS (TO REPLICATE)

### **A. Pydantic Data Models**
V3 replaced dictionary-based parsing with strict **Pydantic Models** (`ZepixV3Alert`).
-   **Why:** Guaranteed type safety, automatic validation, and clear error messages.
-   **V6 Rule:** Must create `ZepixV6Alert` model immediately.

### **B. Hybrid Dual Orders**
The "Order A (Smart) + Order B (Fixed)" strategy was a game changer.
-   **Order A:** Uses identifying SL/TP from the signal (dynamic).
-   **Order B:** Uses fixed 10-pip SL for pyramid protection.
-   **V6 Rule:** Keep this logic. It allows aggressive entry with safe risk management.

### **C. MTF Extraction Strategy**
V3 extracted "Pillars" (15m, 1H, 4H, 1D) from a CSV string `"1,1,-1,1..."`.
-   **V6 Rule:** V6 uses `TREND_PULSE` alert instead of CSV string. This is cleaner but requires a dedicated **State Manager**.

---

## 2. STANDARDS TO MAINTAIN ("V3 QUALITY")

### **A. Line-Number Verification**
Every claim in documentation MUST cite the exact line number in the source code.
-   *Bad:* "Updated the logic."
-   *Good:* "Updated `trading_engine.py` (Line 405-412) to handle V6."

### **B. Zero Tolerance for "Assumptions"**
If a file or variable is not found, report it. Do not guess.

### **C. "Brutal Honesty" Reporting**
If a test fails or a file is missing (like the bot source code), state it clearly in the report header.

---

## 3. LESSONS FOR V6 (IMPROVEMENTS)

### **A. Logic Flexibility**
**Problem:** V3 used "Logic1/2/3" hardcoded to specific timeframes.
**Solution:** V6 will use **4 Dedicated Price Action Logic Classes** (or Functions) that are explicitly named `Action_1M`, `Action_5M`, etc. This decouples logic from config multipliers.

### **B. Trend Management**
**Problem:** V3 updated trend DB on *every entry signal*. This caused noise.
**Solution:** V6 separates Trend Updates to the `TREND_PULSE` alert. Entry signals should **READ** from the DB, not Write to it. This ensures the DB is the "Single Source of Truth".

### **C. Feature Toggles**
**Problem:** V3 had limited toggles.
**Solution:** V6 config must support granular toggles: `enable_adx_filter`, `enable_momentum_check`, `enable_trendline_confirmation`.

---

## 📜 INTEGRATION BLUEPRINT FOR V6

1.  **Define Model**: Create `ZepixV6Alert` with all 15 fields.
2.  **Separate Routing**: Create `PriceActionLogic` handler with 4 sub-methods.
3.  **State Manager**: Implement `TrendPulseHandler` for DB updates.
4.  **Verify**: Use V3-style line-by-line verification for every change.

**END OF STUDY**
