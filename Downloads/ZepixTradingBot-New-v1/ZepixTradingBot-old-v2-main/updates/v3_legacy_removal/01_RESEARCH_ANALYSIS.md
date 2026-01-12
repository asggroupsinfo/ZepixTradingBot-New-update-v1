# RESEARCH & ANALYSIS: Legacy Removal & V3 Standardization
*Date: 2026-01-11*
*Objective: Remove legacy 10-alerts system and standardize on V3 Combined Logic*

## 1. Goal
The objective is to remove all legacy alert processing (simple buy/sell 10 alerts system) and standardize the bot to use only the **V3 Integration System**. Additionally, the three V3 logic modes will be renamed and grouped under a "Combined Logic" group.

## 2. Terminology Changes
| Current Name | New Name | Description |
|:---|:---|:---|
| `LOGIC1` | `combinedlogic-1` | V3 Scalping Mode |
| `LOGIC2` | `combinedlogic-2` | V3 Intraday Mode (Default) |
| `LOGIC3` | `combinedlogic-3` | V3 Swing Mode |
| Legacy Alerts | REMOVED | Simple entry/exit/reversal alerts |
| V3 Alerts | RETAINED | `entry_v3`, `exit_v3`, `squeeze_v3`, `trend_pulse_v3` |

## 3. Impact Analysis

### 3.1 Configuration (`config/config.json` & `src/config.py`)
- **Impact**: High
- **Changes**:
    - Rename `strategies` list values.
    - Rename configuration keys `logic1`, `logic2`, `logic3` to `combinedlogic-1`, `combinedlogic-2`, `combinedlogic-3`.
    - Update `profit_booking_config.sl_1_1_settings` keys.

### 3.2 Alert Processing (`src/processors/alert_processor.py`)
- **Impact**: High
- **Changes**:
    - Remove `validate_legacy_alert` method.
    - Remove routing to legacy validator in `validate_alert`.
    - Routing should strictly validate V3 alerts and reject others.
    - Remove `is_duplicate_alert` logic specific to legacy types if not used by V3 (V3 seems to use its own validation, but need to ensure `validate_v3_alert` is robust).

### 3.3 Trading Engine (`src/core/trading_engine.py`)
- **Impact**: Medium
- **Changes**:
    - Update `_route_v3_to_logic` to return new names.
    - Update `_get_logic_multiplier` to look up new config keys.
    - Rename instance variables `self.logic1_enabled` -> `self.combinedlogic1_enabled`, etc.
    - Update logging and comments.

### 3.4 Risk Manager (`src/managers/risk_manager.py`)
- **Impact**: Low
- **Check**: Does it use logic names for risk? (Need to verify, likely generic).

## 4. Migration Strategy
1.  **Backup**: Ensure `config.json` is backed up (already has `.bak`).
2.  **Config Update**: Programmatically or manually update `config.json`.
3.  **Code Refactoring**:
    - Step 1: `config.py` default config updates.
    - Step 2: `alert_processor.py` legacy stripping.
    - Step 3: `trading_engine.py` logic renaming.
4.  **Verification**: Test with mock V3 alerts.

## 5. Directory Structure for Updates
As requested, all update documentation is stored in `updates/v3_legacy_removal/`.
