# IMPLEMENTATION PLAN v2: Deep Legacy Removal
*Date: 2026-01-11*
*Refined based on Deep Scan Report*

## 1. Goal
Complete eradication of "LOGIC1/2/3" and legacy alert systems. Standardization on "combinedlogic-1/2/3" across Core, UI, and Utils.

## 2. Proposed Changes

### 2.1 Configuration (`config.json` & `config.py`)
*   **Rename Object Keys**: `logic1` -> `combinedlogic-1`, `logic2` -> `combinedlogic-2`, `logic3` -> `combinedlogic-3`.
*   **Update Lists**: `strategies` -> `["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]`.
*   **Update Settings**: `v3_integration.signal_routing` values.

### 2.2 Telegram Bot (`src/menu/timeframe_menu_handler.py`)
*   **Display Text**: Update button labels to "combinedlogic-1 (V3 Scalping)", etc.
*   **Callback Data**: Update `tf_config_logic1` -> `tf_config_comb1` (using short code to check byte limits).
*   **Logic Retrieval**: Update `config.get("LOGIC1")` calls to `config.get("combinedlogic-1")`.
*   **Help Text**: Rewrite help section to explain Combined Logic modes.

### 2.3 Core Trading Engine (`trading_engine.py`)
*   **Attribute Renaming**: Convert `self.logic1_enabled` -> `self.combinedlogic1_enabled`.
*   **Routing Logic**: `_route_v3_to_logic` returns new strings.
*   **Loop Processing**: Loop over new logic names instead of hardcoded `LOGIC` list.

### 2.4 Calculators (`utils/*.py`)
*   **Validation**: Update `profit_sl_calculator.py` to accept `combinedlogic-*` strings.
*   **Defaults**: Change default `logic="LOGIC1"` to `logic="combinedlogic-1"`.

### 2.5 Alert Processor (`alert_processor.py`)
*   **Legacy Purge**: Remove `validate_legacy_alert` and routing logic.
*   **Strict V3**: Enforce V3-only validation pipeline.

## 3. Verification Plan

### 3.1 Static Code Analysis
*   **Zero-Result Grep**: Run `grep -r "LOGIC1" src` -> Must return 0 results (except maybe migration comments).
*   **Config Validator**: Script to load `config.json` and assert `combinedlogic-1` key exists.

### 3.2 System Integrity Test
*   **Startup Test**: Run `minimal_app.py` or main entry to ensure configuration loads without `KeyError`.
*   **Telegram Menu Test**:
    *   Mock calling `timeframe_menu_handler.show_configure_logics()`.
    *   Verify generated keyboard contains new names.
    *   Verify callback data matches new handlers.

### 3.3 Mock Trade Flow
*   Send `entry_v3` alert.
*   Trace signal routing in logs: `Alert -> Route(combinedlogic-2) -> Order Placement`.

## 4. Execution Sequence
1.  **Config**: Update `config.json` and `src/config.py`.
2.  **Utils**: Update calculators (safe, low dep).
3.  **Core**: Update `trading_engine.py` and `alert_processor.py`.
4.  **UI**: Refactor `timeframe_menu_handler.py`.
5.  **Verify**: Run verify script.
