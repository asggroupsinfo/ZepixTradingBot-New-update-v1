# Timeframe-Specific Trading Logic - Implementation Guide

## Overview
The Timeframe-Specific Trading Logic is a new enhancement for the Zepix Trading Bot that allows for dynamic optimization of trading parameters based on the logic/strategy used (LOGIC1, LOGIC2, LOGIC3). This system adjusts Lot Sizes and Stop Loss (SL) distances per timeframe to align with the specific characteristics of each strategy.

### Key Features
*   **Logic-Specific Lot Multipliers**: Increase or decrease position size based on the logic type (e.g., higher lots for scalp trades).
*   **Logic-Specific SL Multipliers**: Adjust SL distance based on logic (e.g., tighter or wider SL).
*   **Timeframe-Specific Recovery Windows**: Customize the window for re-entries (SL Hunt/TP Continuation) for each logic.

## Configuration
The feature is configured in `config.json` under the `timeframe_specific_config` section.

### JSON Structure
```json
"timeframe_specific_config": {
    "enabled": true,
    "LOGIC1": {
        "lot_multiplier": 1.0, 
        "sl_multiplier": 1.0, 
        "recovery_window_minutes": 30
    },
    "LOGIC2": {
        "lot_multiplier": 1.0, 
        "sl_multiplier": 1.0, 
        "recovery_window_minutes": 60
    },
    "LOGIC3": {
        "lot_multiplier": 1.5, 
        "sl_multiplier": 1.2, 
        "recovery_window_minutes": 120
    }
}
```

*   **enabled**: Master switch to turn the feature on/off.
*   **lot_multiplier**: Multiplier applied to the base lot size (e.g., 1.5x).
*   **sl_multiplier**: Multiplier applied to the calculated SL distance (e.g., 1.2x).
*   **recovery_window_minutes**: Duration in minutes for re-entry opportunities.

## Implementation Details

### Components Modified
1.  **Config (`config.json`)**: Added `timeframe_specific_config`.
2.  **PipCalculator (`pip_calculator.py`)**: Updated `calculate_sl_price` to accept `logic` parameter and apply `sl_multiplier`.
3.  **RiskManager (`risk_manager.py`)**: Added `get_lot_size_for_logic` to apply `lot_multiplier`.
4.  **TradingEngine (`trading_engine.py`)**: 
    *   `place_fresh_order`: Uses specific lot size and SL logic.
    *   `place_reentry_order`: Uses specific lot size and SL logic.
5.  **DualOrderManager (`dual_order_manager.py`)**: Updated `create_dual_orders` to use specific logic.
6.  **PriceMonitorService (`price_monitor_service.py`)**: Updated re-entry execution for SL Hunt and TP Continuation.
7.  **ProfitBookingManager (`profit_booking_manager.py`)**: Updated pyramid orders to use logic-specific lot sizing.
8.  **TelegramBot (`telegram_bot.py`)**: Added commands for control.

### Telegram Commands
*   `/toggle_timeframe`: Enable/Disable the timeframe specific logic.
*   `/view_logic_settings`: View current multipliers and settings.
*   `/reset_timeframe_default`: Reset configuration to default values.
*   `/timeframe_config`: Open the visual configuration menu.

### Telegram Menu System
A dedicated **Timeframe Config** menu has been added to the main trading menu:
1.  Navigate to **Menu** > **Trading** > **Timeframe Config**.
2.  Use **Toggle System** to enable/disable the feature instantly.
3.  Use **View Settings** to check multipliers for each logic strategy.
4.  Use **Reset Defaults** to restore original multiplier values.

## Verification
A verification script `verify_timeframe_logic.py` was created to validate the calculations without live trading.

**Verification Results:**
*   **Lot Calculation**: Correctly applies 1.0x for LOGIC1 and 1.5x for LOGIC3.
*   **SL Calculation**: Correctly applies 1.0x for LOGIC1 and 1.2x for LOGIC3.
*   **Disabling**: Correctly reverts to base values when feature is disabled.

## Usage
1.  Ensure `enabled` is set to `true` in `config.json` or use `/toggle_timeframe`.
2.  Send alerts with standard syntax. The bot automatically detects the strategy (LOGIC1/2/3) and applies the multipliers.
3.  Monitor logs or Telegram notifications to see the adjusted Lot Size and SL.
