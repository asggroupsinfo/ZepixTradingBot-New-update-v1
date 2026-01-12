# 03 - Complete Command Reference

## 📱 All 78 Telegram Commands

This document lists **every command** available in the bot with complete details.

---

## Command Organization

Total: **78 Commands**

Categories:
1. Trading Control - 6 commands
2. Performance & Analytics - 8 commands
3. Strategy Control - 8 commands
4. Re-entry System - 12 commands
5. Timeframe Logic - 4 commands
6. Trend Management - 5 commands
7. Risk & Lot Management - 11 commands
8. SL System Control - 8 commands
9. Dual Orders - 2 commands
10. Profit Booking - 16 commands
11. Autonomous Control - 4 commands
12. Diagnostics - 15 commands

---

## 1. Trading Control (6 Commands)

### `/pause`
- **Purpose**: Immediately pause all trading
- **Parameters**: None
- **Usage**: `/pause`
- **Response**: "Trading paused"

### `/resume`
- **Purpose**: Resume trading after pause
- **Parameters**: None
- **Usage**: `/resume`
- **Response**: "Trading resumed"

### `/status`
- **Purpose**: Show current bot status
- **Parameters**: None
- **Usage**: `/status`
- **Returns**: Paused status, MT5 connection, active trades

### `/trades`
- **Purpose**: List all active trades
- **Parameters**: None
- **Usage**: `/trades`
- **Returns**: Open positions with P/L

### `/signal_status`
- **Purpose**: Show received signals status
- **Parameters**: None
- **Usage**: `/signal_status`

### `/simulation_mode`
- **Purpose**: Toggle simulation mode
- **Parameters**: `[on/off/status]`
- **Usage**: `/simulation_mode on`
- **When**: Testing without MT5

---

## 2. Performance & Analytics (8 Commands)

### `/performance`
- **Purpose**: Overall performance metrics
- **Parameters**: None
- **Returns**: Win rate, total P/L, trades count

### `/stats`
- **Purpose**: Detailed statistics
- **Returns**: Daily/weekly/monthly breakdown

### `/performance_report`
- **Purpose**: Generate full performance report
- **Format**: Detailed analysis

### `/sessions`
- **Purpose**: List all trading sessions

### `/session_report`
- **Parameters**: `[session_id]`
- **Usage**: `/session_report SES_20251225_123456`

### `/pair_report`
- **Purpose**: Performance by currency pair
-  **Returns**: P/L per symbol

### `/strategy_report`
- **Purpose**: Performance by strategy (LOGIC1/2/3)

### `/chains`
- **Purpose**: Active profit chain status

---

## 3. Strategy Control (8 Commands)

### `/logic_status`
- **Purpose**: Show which logics are active
- **Returns**: LOGIC1/2/3 ON/OFF status

### `/logic_control`
- **Purpose**: Open logic control menu

### `/logic1_on` / `/logic1_off`
- **Purpose**: Toggle LOGIC1 (15m timeframe)

### `/logic2_on` / `/logic2_off`
- **Purpose**: Toggle LOGIC2 (1h timeframe)

### `/logic3_on` / `/logic3_off`
- **Purpose**: Toggle LOGIC3 (1d timeframe)

---

## 4. Re-entry System (12 Commands)

### `/tp_system`
- **Parameters**: `[on/off/status]`
- **Purpose**: TP Continuation system
- **Usage**: `/tp_system on`

### `/sl_hunt`
- **Parameters**: `[on/off/status]`
- **Purpose**: SL Hunt Recovery
- **Usage**: `/sl_hunt on`

### `/exit_continuation`
- **Parameters**: `[on/off/status]`
- **Purpose**: Exit Continuation system
- **Usage**: `/exit_continuation on`

### `/tp_report`
- **Purpose**: TP continuation history

### `/reentry_config`
- **Purpose**: View all re-entry settings

### `/set_monitor_interval`
- **Parameters**: `[value]` (30/60/120/300/600 seconds)
- **Purpose**: Set price monitoring interval
- **Usage**: `/set_monitor_interval 30`

### `/set_sl_offset`
- **Parameters**: `[value]` (1/2/3/4/5 pips)
- **Purpose**: Set SL recovery offset
- **Usage**: `/set_sl_offset 1`

### `/set_cooldown`
- **Parameters**: `[value]` (30/60/120/300/600 seconds)
- **Purpose**: Set re-entry cooldown
- **Usage**: `/set_cooldown 30`

### `/set_recovery_time`
- **Parameters**: `[value]` (1/2/5/10/15 minutes)
- **Purpose**: Set recovery window
- **Usage**: `/set_recovery_time 5`

### `/set_max_levels`
- **Parameters**: `[value]` (1/2/3/4/5)
- **Purpose**: Max re-entry levels
- **Usage**: `/set_max_levels 2`
- **Note**: Currently enforced at 2

### `/set_sl_reduction`
- **Parameters**: `[value]` (0.3/0.4/0.5/0.6/0.7)
- **Purpose**: SL reduction per level
- **Usage**: `/set_sl_reduction 0.3`
- **Note**: 0.3 = 30% reduction

### `/reset_reentry_config`
- **Purpose**: Reset all re-entry settings to defaults

---

## 5. Timeframe Logic (4 Commands)

### `/menu_timeframe`
- **Purpose**: Open timeframe configuration menu

### `/toggle_timeframe`
- **Purpose**: Toggle timeframe-specific logic

### `/view_logic_settings`
- **Purpose**: View LOGIC1/2/3 parameters

### `/reset_timeframe_default`
- **Purpose**: Reset to default timeframe config

---

## 6. Trend Management (5 Commands)

### `/show_trends`
- **Purpose**: Show all current trends
- **Returns**: Trend matrix for all symbols/timeframes

### `/trend_matrix`
- **Purpose**: Beautiful trend matrix view
- **Format**: Grid layout with colors

### `/set_trend`
- **Parameters**: `[symbol] [timeframe] [trend]`
- **Usage**: `/set_trend EURUSD 1h bullish`
- **Symbols**: XAUUSD, EURUSD, GBPUSD, etc.
- **Timeframes**: 15m, 1h, 1d
- **Trends**: bullish, bearish, neutral, auto

### `/set_auto`
- **Parameters**: `[symbol] [timeframe]`
- **Usage**: `/set_auto EURUSD 1h`
- **Purpose**: Set trend to AUTO (from TradingView)

### `/trend_mode`
- **Purpose**: View trend configuration mode

---

## 7. Risk & Lot Management (11 Commands)

### `/view_risk_caps`
- **Purpose**: View current loss caps
- **Returns**: Daily & lifetime limits

### `/view_risk_status`
- **Purpose**: Current loss against caps
- **Returns**: Used vs available

### `/set_daily_cap`
- **Parameters**: `[amount]`
- **Usage**: `/set_daily_cap 100`
- **Presets**: 50, 100, 200, 500, 1000

### `/set_lifetime_cap`
- **Parameters**: `[amount]`
- **Usage**: `/set_lifetime_cap 1000`
- **Presets**: 200, 500, 1000, 2000, 5000

### `/set_risk_tier`
- **Parameters**: `[tier] [daily] [lifetime]`
- **Usage**: `/set_risk_tier 10000 100 500`
- **Tiers**: 5000, 10000, 25000, 50000, 100000

### `/switch_tier`
- **Parameters**: `[tier]`
- **Usage**: `/switch_tier 10000`
- **Purpose**: One-click tier switch (applies preset caps & lot)

### `/clear_loss_data`
- **Purpose**: Clear lifetime loss
- **Warning**: Resets loss tracking

### `/clear_daily_loss`
- **Purpose**: Clear daily loss only

### `/lot_size_status`
- **Purpose**: View lot sizes for all tiers

### `/set_lot_size`
- **Parameters**: `[tier] [lot_size]`
- **Usage**: `/set_lot_size 10000 0.1`
- **Range**: 0.01 to 10.0

### `/reset_risk_settings`
- **Purpose**: Reset all risk settings to defaults

---

## 8. SL System Control (8 Commands)

### `/sl_status`
- **Purpose**: Current SL system status
- **Returns**: Active system (SL-1/SL-2)

### `/sl_system_change`
- **Parameters**: `[system]`
- **Usage**: `/sl_system_change sl-1`
- **Systems**:
  - `sl-1`: Fixed SL system
  - `sl-2`: Dynamic SL system

### `/sl_system_on`
- **Parameters**: `[system]`
- **Usage**: `/sl_system_on sl-1`

### `/complete_sl_system_off`
- **Purpose**: Turn OFF all SL systems
- **Warning**: Trades without SL protection

### `/view_sl_config`
- **Purpose**: View SL configuration details

### `/set_symbol_sl`
- **Parameters**: `[symbol] [percent]`
- **Usage**: `/set_symbol_sl XAUUSD 20`
- **Range**: 5% to 50%

### `/reset_symbol_sl`
- **Parameters**: `[symbol]`
- **Usage**: `/reset_symbol_sl XAUUSD`

### `/reset_all_sl`
- **Purpose**: Reset all symbol-specific SL settings

---

## 9. Dual Orders (2 Commands)

### `/dual_order_status`
- **Purpose**: Show dual order system status
- **Returns**: Order A & B configuration

### `/toggle_dual_orders`
- **Purpose**: Enable/disable dual order system
- **Note**: Currently always ON for production

---

## 10. Profit Booking (16 Commands)

### `/profit_status`
- **Purpose**: Profit booking system status

### `/profit_stats`
- **Purpose**: Profit chain statistics
- **Returns**: Chains completed, P/L per level

### `/toggle_profit_booking`
- **Purpose**: Enable/disable profit booking

### `/set_profit_targets`
- **Parameters**: `[preset]`
- **Usage**: `/set_profit_targets conservative`
- **Presets**:
  - conservative: 20,40,80,160,320
  - moderate: 10,20,40,80,160
  - aggressive: 5,10,20,40,80

### `/profit_chains`
- **Purpose**: List active chains
- **Returns**: All ongoing profit chains

### `/stop_profit_chain`
- **Parameters**: `[chain_id]`
- **Usage**: `/stop_profit_chain CHAIN_EURUSD_123`

### `/stop_all_profit_chains`
- **Purpose**: Stop all active chains

### `/set_chain_multipliers`
- **Parameters**: `[preset]`
- **Usage**: `/set_chain_multipliers standard`
- **Presets**:
  - standard: 1,2,4,8,16
  - conservative: 1,1.5,2,3,4
  - aggressive: 1,3,6,12,24
  - linear: 1,2,3,4,5
  - fibonacci: 1,1,2,3,5

### `/profit_config`
- **Purpose**: View profit booking configuration

### `/profit_sl_status`
- **Purpose**: Profit SL (Order B) status

### `/profit_sl_mode`
- **Parameters**: `[mode]`
- **Usage**: `/profit_sl_mode SL-1.1`
- **Modes**: SL-1.1, SL-2.1

### `/enable_profit_sl`
- **Purpose**: Enable profit booking SL

### `/disable_profit_sl`
- **Purpose**: Disable profit booking SL

### `/set_profit_sl`
- **Parameters**: `[logic] [amount]`
- **Usage**: `/set_profit_sl LOGIC1 10`

### `/reset_profit_sl`
- **Purpose**: Reset profit SL to defaults

### `/profit_sl_hunt`
- **Parameters**: `[on/off/status]`
- **Purpose**: Enable SL hunt for profit chains

---

## 11. Autonomous Control (4 Commands)

### `/autonomous_dashboard`
- **Purpose**: Open autonomous system dashboard

### `/autonomous_mode`
- **Parameters**: `[on/off/status]`
- **Usage**: `/autonomous_mode on`
- **Purpose**: Master autonomous switch

### `/autonomous_status`
- **Purpose**: Detailed autonomous system status
- **Returns**: All autonomous features status

### `/profit_sl_hunt`
- **See**: Profit Booking section

---

## 12. Diagnostics (15 Commands)

### `/health_status`
- **Purpose**: System health check
- **Returns**: MT5, Telegram, services status

### `/set_log_level`
- **Parameters**: `[level]`
- **Usage**: `/set_log_level DEBUG`
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### `/get_log_level`
- **Purpose**: Current log level

### `/reset_log_level`
- **Purpose**: Reset to INFO

### `/error_stats`
- **Purpose**: Error statistics
- **Returns**: Error counts by type

### `/reset_errors`
- **Purpose**: Clear error tracking

### `/reset_health`
- **Purpose**: Reset health metrics

### `/export_logs`
- **Parameters**: `[lines]`
- **Usage**: `/export_logs 500`
- **Options**: 100, 500, 1000
- **Returns**: Log file via Telegram

### `/export_current_session`
- **Purpose**: Export today's logs

### `/export_by_date`
-  **Parameters**: `[date]`
- **Usage**: `/export_by_date 2025-12-25`
- **Presets**: Last 7 days available

### `/export_date_range`
- **Parameters**: `[start_date] [end_date]`
- **Usage**: `/export_date_range 2025-12-20 2025-12-25`

### `/log_file_size`
- **Purpose**: Current log file size

### `/clear_old_logs`
- **Purpose**: Delete old log files (>7 days)

### `/trading_debug_mode`
- **Parameters**: `[on/off/status]`
- **Usage**: `/trading_debug_mode on`
- **Purpose**: Verbose trading logs

### `/system_resources`
- **Purpose**: CPU, memory, disk usage

---

## Quick Reference Tables

### Most Used Commands

| Purpose | Command |
|---------|---------|
| Pause trading | `/pause` |
| Resume trading | `/resume` |
| Check status | `/status` |
| View trades | `/trades` |
| View trends | `/trend_matrix` |
| Set trend | `/set_trend EURUSD 1h bullish` |
| Switch tier | `/switch_tier 10000` |
| View risk | `/view_risk_status` |
| Profit status | `/profit_status` |
| Export logs | `/export_current_session` |

### Emergency Commands

| Purpose | Command |
|---------|---------|
| Stop trading immediately | `/pause` |
| Close all positions | (Manual in MT5) |
| Stop all profit chains | `/stop_all_profit_chains` |
| Turn off SL systems | `/complete_sl_system_off` |
| Switch to simulation | `/simulation_mode on` |

---

**Next**: Read [04_SYSTEM_ARCHITECTURE.md](04_SYSTEM_ARCHITECTURE.md) for technical details
