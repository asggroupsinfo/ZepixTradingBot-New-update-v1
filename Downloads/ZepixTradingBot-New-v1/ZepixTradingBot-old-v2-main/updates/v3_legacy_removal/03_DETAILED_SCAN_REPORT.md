# DETAILED SCAN REPORT: Legacy Logic & References
*Date: 2026-01-11*

## 1. Executive Summary
A deep grep scan of the codebase has identified **53+ occurrences** of legacy logic terms (`LOGIC1`, `LOGIC2`, `LOGIC3`, `logic1`, `logic2`, `logic3`) across **7 critical files**. The removal scope is significantly larger than initially estimated, involving the UI layer (Telegram), Utility layer (Calculators), and Core Logic.

## 2. Affected Files & Locations

### 2.1 Core System
*   **`src/core/trading_engine.py`**
    *   **Usage**: Routing logic, instance flags (`self.logic1_enabled`), logging, string constants.
    *   **Action**: Rename all flags, update `_route_v3_to_logic`, update `_get_logic_multiplier`.
*   **`config/config.json`** & **`src/config.py`**
    *   **Usage**: Configuration keys (`"logic1": {...}`), strategy list.
    *   **Action**: Rename keys to `combinedlogic-1` etc., update strategy list.

### 2.2 User Interface (Telegram Bot)
*   **`src/menu/timeframe_menu_handler.py`**
    *   **Usage**: **HEAVY**. Hardcoded button text (`"🔧 LOGIC1..."`), callback data (`"tf_config_logic1"`), help text descriptions.
    *   **Risk**: Changing callback data requires careful regex or handler updates to ensure button clicks still work.
    *   **Action**: Refactor entire menu to use dynamic logic names or strictly new `combinedlogic` naming.

### 2.3 Utilities & Calculators
*   **`src/utils/pip_calculator.py`**
    *   **Usage**: Docstrings and logic flow for timeframe adjustments.
    *   **Action**: Update logic parameter handling.
*   **`src/utils/profit_sl_calculator.py`**
    *   **Usage**: Default logic variable (`logic = "LOGIC1"`), logic validation check (`if s.upper() in ['LOGIC1'...]`).
    *   **Action**: Update validation list and default values.
*   **`src/utils/optimized_logger.py`**
    *   **Usage**: Logging format docstrings.
    *   **Action**: Update docstrings to reflect new terminology.

### 2.4 Processors
*   **`src/processors/alert_processor.py`**
    *   **Usage**: Legacy validation logic (already slated for removal).

## 3. Specific String Remapping Matrix

| Original String | New Target String | Context |
|:---|:---|:---|
| `LOGIC1` | `combinedlogic-1` | Config values, Logs, UI Text |
| `LOGIC2` | `combinedlogic-2` | Config values, Logs, UI Text |
| `LOGIC3` | `combinedlogic-3` | Config values, Logs, UI Text |
| `logic1` | `combinedlogic-1` | Config keys (JSON) |
| `logic2` | `combinedlogic-2` | Config keys (JSON) |
| `logic3` | `combinedlogic-3` | Config keys (JSON) |
| `tf_config_logic1` | `tf_config_comb1` | Telegram Callback Data (Shortened for limit) |
| `tf_config_logic2` | `tf_config_comb2` | Telegram Callback Data |
| `tf_config_logic3` | `tf_config_comb3` | Telegram Callback Data |

**Note on Telegram Callbacks**: Telegram has a 64-byte limit. `combinedlogic-1` might be long if part of a complex string. Will use `comb1` for internal callbacks but display full name in UI text.

## 4. Conclusion
The legacy removal must be surgical. Simple find/replace will break Telegram callbacks if not matched with handler updates.
