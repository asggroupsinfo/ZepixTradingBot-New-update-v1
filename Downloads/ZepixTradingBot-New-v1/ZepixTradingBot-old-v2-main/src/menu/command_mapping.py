"""
Complete Command Parameter Mapping for all 78 commands (73 original + 5 new diagnostics)
Maps each command to its parameter requirements, types, and validation rules
"""
from .menu_constants import (
    SYMBOLS, TIMEFRAMES, TRENDS, LOGICS, AMOUNT_PRESETS, PERCENTAGE_PRESETS,
    SL_SYSTEMS, PROFIT_SL_MODES, RISK_TIERS, INTERVAL_PRESETS, COOLDOWN_PRESETS,
    RECOVERY_PRESETS, MAX_LEVELS_PRESETS, SL_REDUCTION_PRESETS, SL_OFFSET_PRESETS,
    LOT_SIZE_PRESETS, DATE_PRESETS, get_date_presets
)

# Complete parameter mapping for all 72 commands
COMMAND_PARAM_MAP = {
    # Trading Control (6 commands)
    "pause": {"params": [], "type": "direct", "handler": "handle_pause"},
    "resume": {"params": [], "type": "direct", "handler": "handle_resume"},
    "status": {"params": [], "type": "direct", "handler": "handle_status"},
    "trades": {"params": [], "type": "direct", "handler": "handle_trades"},
    "signal_status": {"params": [], "type": "direct", "handler": "handle_signal_status"},
    "simulation_mode": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_simulation_mode"},
    
    # Performance & Analytics (7 commands)
    "performance": {"params": [], "type": "direct", "handler": "handle_performance"},
    "stats": {"params": [], "type": "direct", "handler": "handle_stats"},
    "performance_report": {"params": [], "type": "direct", "handler": "handle_performance_report"},
    "sessions": {"params": [], "type": "direct", "handler": "handle_sessions"},
    "session_report": {"params": ["session_id"], "type": "dynamic", "handler": "handle_session_report"},
    "pair_report": {"params": [], "type": "direct", "handler": "handle_pair_report"},
    "strategy_report": {"params": [], "type": "direct", "handler": "handle_strategy_report"},
    "chains": {"params": [], "type": "direct", "handler": "handle_chains_status"},
    
    # Strategy Control (7 commands)
    "logic_status": {"params": [], "type": "direct", "handler": "handle_logic_status"},
    "logic_control": {"params": [], "type": "direct", "handler": "handle_logic_control"},
    "logic1_on": {"params": [], "type": "direct", "handler": "handle_logic1_on"},
    "logic1_off": {"params": [], "type": "direct", "handler": "handle_logic1_off"},
    "logic2_on": {"params": [], "type": "direct", "handler": "handle_logic2_on"},
    "logic2_off": {"params": [], "type": "direct", "handler": "handle_logic2_off"},
    "logic3_on": {"params": [], "type": "direct", "handler": "handle_logic3_on"},
    "logic3_off": {"params": [], "type": "direct", "handler": "handle_logic3_off"},
    
    # Re-entry System (12 commands)
    "tp_system": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_tp_system"},
    "sl_hunt": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_sl_hunt"},
    "exit_continuation": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_exit_continuation"},
    "tp_report": {"params": [], "type": "direct", "handler": "handle_tp_report"},
    "reentry_config": {"params": [], "type": "direct", "handler": "handle_reentry_config"},
    "set_monitor_interval": {"params": ["value"], "type": "single", "presets": INTERVAL_PRESETS, "handler": "handle_set_monitor_interval"},
    "set_sl_offset": {"params": ["value"], "type": "single", "presets": SL_OFFSET_PRESETS, "handler": "handle_set_sl_offset"},
    "set_cooldown": {"params": ["value"], "type": "single", "presets": COOLDOWN_PRESETS, "handler": "handle_set_cooldown"},
    "set_recovery_time": {"params": ["value"], "type": "single", "presets": RECOVERY_PRESETS, "handler": "handle_set_recovery_time"},
    "set_max_levels": {"params": ["value"], "type": "single", "presets": MAX_LEVELS_PRESETS, "handler": "handle_set_max_levels"},
    "set_sl_reduction": {"params": ["value"], "type": "single", "presets": SL_REDUCTION_PRESETS, "handler": "handle_set_sl_reduction"},
    "reset_reentry_config": {
        "params": [],
        "type": "direct",
        "handler": "handle_reset_reentry_config",
        "description": "Reset all re-entry settings to defaults"
    },

    # Timeframe Logic Commands
    "menu_timeframe": {
        "params": [],
        "type": "direct",
        "handler": "handle_menu_timeframe",
        "description": "Show timeframe configuration menu"
    },
    "toggle_timeframe": {
        "params": [],
        "type": "direct",
        "handler": "handle_toggle_timeframe",
        "description": "Toggle timeframe-specific logic"
    },
    "view_logic_settings": {
        "params": [],
        "type": "direct",
        "handler": "handle_view_logic_settings",
        "description": "View settings for each logic type"
    },
    "reset_timeframe_default": {
        "params": [],
        "type": "direct",
        "handler": "handle_reset_timeframe_default",
        "description": "Reset timeframe config to defaults"
    },

    # Trend Commands
    "show_trends": {"params": [], "type": "direct", "handler": "handle_show_trends"},
    "trend_matrix": {"params": [], "type": "direct", "handler": "handle_trend_matrix"},
    "set_trend": {"params": ["symbol", "timeframe", "trend"], "type": "multi", "handler": "handle_set_trend", "presets": {"symbol": SYMBOLS, "timeframe": TIMEFRAMES, "trend": TRENDS}},
    "set_auto": {"params": ["symbol", "timeframe"], "type": "multi", "handler": "handle_set_auto", "presets": {"symbol": SYMBOLS, "timeframe": TIMEFRAMES}},
    "trend_mode": {"params": [], "type": "direct", "handler": "handle_trend_mode"},
    
    # Risk & Lot Management (11 commands - Complete risk menu)
    "view_risk_caps": {"params": [], "type": "direct", "handler": "handle_view_risk_caps"},
    "view_risk_status": {"params": [], "type": "direct", "handler": "handle_view_risk_status"},
    "set_daily_cap": {"params": ["amount"], "type": "single", "presets": AMOUNT_PRESETS, "handler": "handle_set_daily_cap"},
    "set_lifetime_cap": {"params": ["amount"], "type": "single", "presets": AMOUNT_PRESETS, "handler": "handle_set_lifetime_cap"},
    "set_risk_tier": {"params": ["tier", "daily", "lifetime"], "type": "multi", "handler": "handle_set_risk_tier", "presets": {"tier": "DYNAMIC_TIERS", "daily": AMOUNT_PRESETS, "lifetime": AMOUNT_PRESETS}},
    "switch_tier": {"params": ["tier"], "type": "single", "presets": {"tier": "DYNAMIC_TIERS"}, "handler": "handle_switch_tier"},
    "clear_loss_data": {"params": [], "type": "direct", "handler": "handle_clear_loss_data"},
    "clear_daily_loss": {"params": [], "type": "direct", "handler": "handle_clear_daily_loss"},
    "lot_size_status": {"params": [], "type": "direct", "handler": "handle_lot_size_status"},
    "set_lot_size": {"params": ["tier", "lot_size"], "type": "multi", "handler": "handle_set_lot_size", "presets": {"tier": "DYNAMIC_TIERS", "lot_size": "DYNAMIC_LOTS"}},
    "reset_risk_settings": {"params": [], "type": "direct", "handler": "handle_reset_risk_settings"},
    
    # SL System Control (8 commands)
    "sl_status": {"params": [], "type": "direct", "handler": "handle_sl_status"},
    "sl_system_change": {"params": ["system"], "type": "single", "options": SL_SYSTEMS, "handler": "handle_sl_system_change"},
    "sl_system_on": {"params": ["system"], "type": "single", "options": SL_SYSTEMS, "handler": "handle_sl_system_on"},
    "complete_sl_system_off": {"params": [], "type": "direct", "handler": "handle_complete_sl_system_off"},
    "view_sl_config": {"params": [], "type": "direct", "handler": "handle_view_sl_config"},
    "set_symbol_sl": {"params": ["symbol", "percent"], "type": "multi", "handler": "handle_set_symbol_sl", "presets": {"symbol": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "AUDJPY"], "percent": ["5", "10", "15", "20", "25", "30", "35", "40", "45", "50"]}},
    "reset_symbol_sl": {"params": ["symbol"], "type": "single", "options": SYMBOLS, "handler": "handle_reset_symbol_sl"},
    "reset_all_sl": {"params": [], "type": "direct", "handler": "handle_reset_all_sl"},
    
    # Dual Orders (2 commands)
    "dual_order_status": {"params": [], "type": "direct", "handler": "handle_dual_order_status"},
    "toggle_dual_orders": {"params": [], "type": "direct", "handler": "handle_toggle_dual_orders"},
    
    # Profit Booking (16 commands) - ALL PROFIT BOOKING COMMANDS INCLUDED
    "profit_status": {"params": [], "type": "direct", "handler": "handle_profit_status"},
    "profit_stats": {"params": [], "type": "direct", "handler": "handle_profit_stats"},
    "toggle_profit_booking": {"params": [], "type": "direct", "handler": "handle_toggle_profit_booking"},
    "set_profit_targets": {"params": ["preset"], "type": "single", "presets": ["conservative", "moderate", "aggressive", "custom_1", "custom_2"], "handler": "handle_set_profit_targets"},
    "profit_chains": {"params": [], "type": "direct", "handler": "handle_profit_chains"},
    "stop_profit_chain": {"params": ["chain_id"], "type": "dynamic", "handler": "handle_stop_profit_chain"},
    "stop_all_profit_chains": {"params": [], "type": "direct", "handler": "handle_stop_all_profit_chains"},
    "set_chain_multipliers": {"params": ["preset"], "type": "single", "presets": ["standard", "conservative", "aggressive", "linear", "fibonacci"], "handler": "handle_set_chain_multipliers"},
    "profit_config": {"params": [], "type": "direct", "handler": "handle_profit_config"},
    "profit_sl_status": {"params": [], "type": "direct", "handler": "handle_profit_sl_status"},
    "profit_sl_mode": {"params": ["profit_sl_mode"], "type": "single", "options": PROFIT_SL_MODES, "handler": "handle_profit_sl_mode"},
    "enable_profit_sl": {"params": [], "type": "direct", "handler": "handle_enable_profit_sl"},
    
    # Autonomous Control (4 commands)
    "autonomous_dashboard": {"params": [], "type": "direct", "handler": "handle_autonomous_dashboard"},
    "autonomous_mode": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_autonomous_mode"},
    "autonomous_status": {"params": [], "type": "direct", "handler": "handle_autonomous_status"},
    "profit_sl_hunt": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_profit_sl_hunt"},

    "disable_profit_sl": {"params": [], "type": "direct", "handler": "handle_disable_profit_sl"},
    "set_profit_sl": {"params": ["logic", "amount"], "type": "multi", "handler": "handle_set_profit_sl", "presets": {"logic": ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"], "amount": ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]}},
    "reset_profit_sl": {"params": [], "type": "direct", "handler": "handle_reset_profit_sl"},
    
    # Settings (1 command)
    "chains": {"params": [], "type": "direct", "handler": "handle_chains_status"},
    
    # Diagnostics & Monitoring (15 commands - 12 original + 3 new date-based exports)
    "health_status": {"params": [], "type": "direct", "handler": "_execute_health_status"},
    "set_log_level": {"params": ["level"], "type": "single", "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], "handler": "_execute_set_log_level"},
    "get_log_level": {"params": [], "type": "direct", "handler": "_execute_get_log_level"},
    "reset_log_level": {"params": [], "type": "direct", "handler": "_execute_reset_log_level"},
    "error_stats": {"params": [], "type": "direct", "handler": "_execute_error_stats"},
    "reset_errors": {"params": [], "type": "direct", "handler": "_execute_reset_errors"},
    "reset_health": {"params": [], "type": "direct", "handler": "_execute_reset_health"},
    # Log Export Commands (4 variants)
    "export_logs": {"params": ["lines"], "type": "single", "options": ["100", "500", "1000"], "handler": "_execute_export_logs"},
    "export_current_session": {"params": [], "type": "direct", "handler": "_execute_export_current_session"},
    "export_by_date": {"params": ["date"], "type": "single", "presets": DATE_PRESETS, "handler": "_execute_export_by_date"},
    "export_date_range": {"params": ["start_date", "end_date"], "type": "multi", "handler": "_execute_export_date_range", "presets": {"start_date": DATE_PRESETS, "end_date": DATE_PRESETS}},
    "log_file_size": {"params": [], "type": "direct", "handler": "_execute_log_file_size"},
    "clear_old_logs": {"params": [], "type": "direct", "handler": "_execute_clear_old_logs"},
    "trading_debug_mode": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "_execute_trading_debug_mode"},
    "system_resources": {"params": [], "type": "direct", "handler": "_execute_system_resources"},
    
    "autonomous_dashboard": {"params": [], "type": "direct", "handler": "handle_autonomous_dashboard"},
    "autonomous_mode": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_autonomous_mode"},
    "autonomous_status": {"params": [], "type": "direct", "handler": "handle_autonomous_status"},
    "profit_sl_hunt": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "handle_profit_sl_hunt"},
    "reset_reentry_config": {"params": [], "type": "direct", "handler": "handle_reset_reentry_config"},

    # Deprecated/alias commands (for backward compatibility)
    "set_sl_reductions": {"params": ["value"], "type": "single", "presets": SL_REDUCTION_PRESETS, "handler": "handle_set_sl_reductions", "deprecated": True},
    "close_profit_chain": {"params": ["chain_id"], "type": "dynamic", "handler": "handle_stop_profit_chain"},  # Alias for stop_profit_chain
}

# Parameter type definitions for validation
PARAM_TYPE_DEFINITIONS = {
    "symbol": {
        "type": "string",
        "format": "uppercase",
        "valid_values": SYMBOLS,
        "validation": lambda x: x.upper() in SYMBOLS
    },
    "timeframe": {
        "type": "string",
        "format": "lowercase",
        "valid_values": TIMEFRAMES,
        "validation": lambda x: x.lower() in TIMEFRAMES
    },
    "trend": {
        "type": "string",
        "format": "uppercase",
        "valid_values": TRENDS,
        "validation": lambda x: x.upper() in TRENDS
    },
    "logic": {
        "type": "string",
        "format": "lowercase",
        "valid_values": LOGICS,
        "validation": lambda x: x.lower() in LOGICS
    },
    "amount": {
        "type": "float",
        "min": 0.01,
        "max": 1000000,
        "validation": lambda x: 0.01 <= float(x) <= 1000000
    },
    "percent": {
        "type": "float",
        "min": 5,
        "max": 50,
        "validation": lambda x: 5 <= float(x) <= 50
    },
    "value": {
        "type": "float",
        "min": 0,
        "validation": lambda x: float(x) >= 0
    },
    "mode": {
        "type": "string",
        "format": "lowercase",
        "validation": lambda x: x.lower() in ["on", "off", "status"]
    },
    "profit_sl_mode": {
        "type": "string",
        "format": "uppercase",
        "valid_values": PROFIT_SL_MODES,
        "validation": lambda x: x.upper() in PROFIT_SL_MODES
    },
    "system": {
        "type": "string",
        "format": "lowercase",
        "valid_values": SL_SYSTEMS,
        "validation": lambda x: x.lower() in SL_SYSTEMS
    },
    "tier": {
        "type": "string",
        "valid_values": RISK_TIERS,
        "validation": lambda x: str(x) in RISK_TIERS
    },
    "lot_size": {
        "type": "float",
        "min": 0.01,
        "max": 10.0,
        "validation": lambda x: 0.01 <= float(x) <= 10.0
    },
    "balance": {
        "type": "string",
        "validation": lambda x: x.isdigit() or x.replace('.', '').isdigit()
    },
    "daily": {
        "type": "float",
        "min": 0,
        "validation": lambda x: float(x) >= 0
    },
    "lifetime": {
        "type": "float",
        "min": 0,
        "validation": lambda x: float(x) >= 0
    },
    "chain_id": {
        "type": "string",
        "validation": lambda x: len(x) > 0  # Dynamic validation from active chains
    },
    "targets": {
        "type": "list",
        "validation": lambda x: isinstance(x, list) and all(float(t) > 0 for t in x)
    },
    "preset": {
        "type": "string",
        "valid_values": ["conservative", "moderate", "aggressive", "custom_1", "custom_2", "standard", "linear", "fibonacci"],
        "validation": lambda x: x in ["conservative", "moderate", "aggressive", "custom_1", "custom_2", "standard", "linear", "fibonacci"]
    },
    "multipliers": {
        "type": "list",
        "validation": lambda x: isinstance(x, list) and all(float(m) > 0 for m in x)
    },
    "level": {
        "type": "string",
        "format": "uppercase",
        "valid_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "validation": lambda x: x.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    },
    "lines": {
        "type": "string",
        "valid_values": ["100", "500", "1000"],
        "validation": lambda x: x in ["100", "500", "1000"]
    },
    "date": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "valid_values": DATE_PRESETS,
        "validation": lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-'
    },
    "start_date": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "valid_values": DATE_PRESETS,
        "validation": lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-'
    },
    "end_date": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "valid_values": DATE_PRESETS,
        "validation": lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-'
    }
}

# Commands that require special dependencies
COMMAND_DEPENDENCIES = {
    "set_trend": ["trend_manager"],
    "set_auto": ["trend_manager"],
    "trend_mode": ["trend_manager"],
    "show_trends": ["trend_manager"],
    "trend_matrix": ["trend_manager"],
    "set_lot_size": ["risk_manager"],
    "lot_size_status": ["risk_manager"],
    "switch_tier": [],
    "enable_profit_sl": ["trading_engine", "profit_booking_manager"],
    "disable_profit_sl": ["trading_engine", "profit_booking_manager"],
    "reset_profit_sl": ["trading_engine", "profit_booking_manager"],
    "profit_status": ["trading_engine", "profit_booking_manager"],
    "profit_stats": ["trading_engine", "profit_booking_manager"],
    "toggle_profit_booking": ["trading_engine", "profit_booking_manager"],
    "set_profit_targets": ["trading_engine"],
    "set_chain_multipliers": ["trading_engine"],
    "pause": ["trading_engine"],
    "resume": ["trading_engine"],
    "status": ["trading_engine"],
    "simulation_mode": ["trading_engine"],
}

