"""
Menu Constants - Menu structure, button layouts, parameter options
"""
# Lazy import to avoid circular dependency
_COMMAND_PARAM_MAP = None
_PARAM_TYPE_DEFINITIONS = None
_COMMAND_DEPENDENCIES = None

def _get_command_mapping():
    """Lazy load command mapping to avoid circular imports"""
    global _COMMAND_PARAM_MAP, _PARAM_TYPE_DEFINITIONS, _COMMAND_DEPENDENCIES
    if _COMMAND_PARAM_MAP is None:
        from .command_mapping import COMMAND_PARAM_MAP, PARAM_TYPE_DEFINITIONS, COMMAND_DEPENDENCIES
        _COMMAND_PARAM_MAP = COMMAND_PARAM_MAP
        _PARAM_TYPE_DEFINITIONS = PARAM_TYPE_DEFINITIONS
        _COMMAND_DEPENDENCIES = COMMAND_DEPENDENCIES
    return _COMMAND_PARAM_MAP, _PARAM_TYPE_DEFINITIONS, _COMMAND_DEPENDENCIES

# Export for backward compatibility
def get_command_param_map():
    return _get_command_mapping()[0]

def get_param_type_definitions():
    return _get_command_mapping()[1]

def get_command_dependencies():
    return _get_command_mapping()[2]

# Parameter Options
SYMBOLS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD", 
           "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "AUDJPY"]

TIMEFRAMES = ["15m", "1h", "1d"]  # Removed 1m, 5m, 4h - only keep timeframes used by combinedlogic-1/2/3

TRENDS = ["BULLISH", "BEARISH", "NEUTRAL", "AUTO"]

LOGICS = ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]

AMOUNT_PRESETS = ["10", "20", "50", "100", "200", "500", "1000", "2000", "5000"]

PERCENTAGE_PRESETS = ["10", "20", "30", "40", "50", "60", "70", "80", "90"]

SL_SYSTEMS = ["sl-1", "sl-2"]

PROFIT_SL_MODES = ["SL-1.1", "SL-2.1"]

RISK_TIERS = ["5000", "10000", "25000", "50000", "100000"]

# Interval Presets (seconds)
INTERVAL_PRESETS = ["30", "60", "120", "300", "600"]

# Cooldown Presets (seconds)
COOLDOWN_PRESETS = ["30", "60", "120", "300", "600"]

# Recovery Time Presets (minutes)
RECOVERY_PRESETS = ["1", "2", "5", "10", "15"]

# Max Levels Presets
MAX_LEVELS_PRESETS = ["1", "2", "3", "4", "5"]

# SL Reduction Presets (percentage)
SL_REDUCTION_PRESETS = ["0.3", "0.4", "0.5", "0.6", "0.7"]

# SL Offset Presets (pips)
SL_OFFSET_PRESETS = ["1", "2", "3", "4", "5"]

# Lot Size Presets
LOT_SIZE_PRESETS = ["0.01", "0.05", "0.1", "0.2", "0.5", "1.0", "2.0", "5.0"]

# Profit Target Presets (common configurations)
PROFIT_TARGET_PRESETS = {
    "conservative": ["20", "40", "80", "160", "320"],
    "moderate": ["10", "20", "40", "80", "160"],
    "aggressive": ["5", "10", "20", "40", "80"],
    "custom_1": ["15", "30", "60", "120", "240"],
    "custom_2": ["25", "50", "100", "200", "400"]
}

# Chain Multiplier Presets (common lot multiplier sequences)
MULTIPLIER_PRESETS = {
    "standard": ["1", "2", "4", "8", "16"],
    "conservative": ["1", "1.5", "2", "3", "4"],
    "aggressive": ["1", "3", "6", "12", "24"],
    "linear": ["1", "2", "3", "4", "5"],
    "fibonacci": ["1", "1", "2", "3", "5"]
}

# Risk Tier Presets (balance thresholds and corresponding limits)
RISK_TIER_BALANCE_PRESETS = ["5000", "10000", "25000", "50000", "100000"]
RISK_TIER_DAILY_PRESETS = ["50", "100", "200", "500", "1000", "2000", "5000"]
RISK_TIER_LIFETIME_PRESETS = ["200", "500", "1000", "2000", "5000", "10000", "20000"]

# Date Presets for Log Export (last 7 days from today)
# Format: YYYY-MM-DD for internal use, shown as DD-MM-YYYY in UI
from datetime import datetime, timedelta
def get_date_presets(days=7):
    """Generate date options for last N days"""
    today = datetime.now()
    dates = []
    for i in range(days):
        date = today - timedelta(days=i)
        # Return dict format for proper menu display
        dates.append({
            "value": date.strftime("%Y-%m-%d"),  # Internal format: 2025-11-23
            "display": date.strftime("%d-%m-%Y")  # Display format: 23-11-2025
        })
    return dates

# Menu Layouts and Structures
DEFAULT_MENU_LAYOUT = {
    "dashboard": [
        [{"text": "📊 Bot Status", "callback_data": "action_status"},
         {"text": "⏸️ Pause/Resume", "callback_data": "action_toggle_pause"}],
        [{"text": "💰 Profit Report", "callback_data": "action_profit_report"},
         {"text": "📈 Performance", "callback_data": "menu_performance"}],
        [{"text": "⏱️ Timeframe Logic", "callback_data": "menu_timeframe"}],
        [{"text": "⚙️ Settings", "callback_data": "menu_settings"},
         {"text": "❓ Help", "callback_data": "action_help"}]
    ],
    "trading": [
        [{"text": "🎯 Signal Status", "callback_data": "action_signal_status"},
         {"text": "📝 Active Trades", "callback_data": "action_trades"}],
        [{"text": "🔄 Re-entry Config", "callback_data": "menu_reentry"},
         {"text": "📉 SL System", "callback_data": "menu_sl_system"}],
        [{"text": "⏱️ Timeframe Config", "callback_data": "menu_timeframe"}],
        [{"text": "🏠 Main Menu", "callback_data": "menu_main"}]
    ],
    "timeframe": [
        [{"text": "⏱️ Toggle System", "callback_data": "action_toggle_timeframe"}],
        [{"text": "📊 View Settings", "callback_data": "action_view_logic_settings"}],
        [{"text": "🔄 Reset Defaults", "callback_data": "action_reset_timeframe_default"}],
        [{"text": "🔙 Back", "callback_data": "menu_main"}]
    ]
}

MENU_CATEGORIES = {
    "dashboard": {"title": "📊 Dashboard", "description": "Main control center"},
    "trading": {"title": "💰 Trading", "description": "Trade management"},
    "performance": {"title": "⚡ Performance", "description": "Stats & Reports"},
    "reentry": {"title": "🔄 Re-entry", "description": "Re-entry configuration"},
    "trends": {"title": "📍 Trends", "description": "Trend management"},
    "risk": {"title": "🛡️ Risk", "description": "Risk management"},
    "sl_system": {"title": "⚙️ SL System", "description": "Stop Loss configuration"},
    "orders": {"title": "💎 Orders", "description": "Order management"},
    "profit": {"title": "📈 Profit", "description": "Profit booking"},
    "timeframe": {"title": "⏱️ Timeframe Config", "description": "Logic-specific parameters"}
}

DATE_PRESETS = get_date_presets(7)  # Last 7 days

# Command Categories Mapping (lazy loaded)
def get_command_categories():
    """Get command categories, loading COMMAND_PARAM_MAP if needed"""
    COMMAND_PARAM_MAP, _, _ = _get_command_mapping()
    return {
        "trading": {
            "name": "💰 Trading Control",
            "commands": {
                "pause": COMMAND_PARAM_MAP["pause"],
                "resume": COMMAND_PARAM_MAP["resume"],
                "status": COMMAND_PARAM_MAP["status"],
                "trades": COMMAND_PARAM_MAP["trades"],
                "signal_status": COMMAND_PARAM_MAP["signal_status"],
                "simulation_mode": COMMAND_PARAM_MAP["simulation_mode"],
                "logic_control": {"handler": "submenu_logic", "params": [], "type": "submenu"},
            }
        },
    "performance": {
        "name": "⚡ Performance & Analytics",
        "commands": {
            "performance": COMMAND_PARAM_MAP["performance"],
            "stats": COMMAND_PARAM_MAP["stats"],
            "performance_report": COMMAND_PARAM_MAP["performance_report"],
            "sessions": COMMAND_PARAM_MAP["sessions"],
            "pair_report": COMMAND_PARAM_MAP["pair_report"],
            "strategy_report": COMMAND_PARAM_MAP["strategy_report"],
            "chains": COMMAND_PARAM_MAP["chains"],
        }
    },
    "strategy": {
        "name": "⚙️ Strategy Control",
        "commands": {
            "logic_status": COMMAND_PARAM_MAP["logic_status"],
            "logic1_on": COMMAND_PARAM_MAP["logic1_on"],
            "logic1_off": COMMAND_PARAM_MAP["logic1_off"],
            "logic2_on": COMMAND_PARAM_MAP["logic2_on"],
            "logic2_off": COMMAND_PARAM_MAP["logic2_off"],
            "logic3_on": COMMAND_PARAM_MAP["logic3_on"],
            "logic3_off": COMMAND_PARAM_MAP["logic3_off"],
        }
    },
    "reentry": {
        "name": "🔄 Re-entry System",
        "commands": {
            "tp_system": COMMAND_PARAM_MAP["tp_system"],
            "sl_hunt": COMMAND_PARAM_MAP["sl_hunt"],
            "exit_continuation": COMMAND_PARAM_MAP["exit_continuation"],
            "tp_report": COMMAND_PARAM_MAP["tp_report"],
            "reentry_config": COMMAND_PARAM_MAP["reentry_config"],
            "set_monitor_interval": COMMAND_PARAM_MAP["set_monitor_interval"],
            "set_sl_offset": COMMAND_PARAM_MAP["set_sl_offset"],
            "set_cooldown": COMMAND_PARAM_MAP["set_cooldown"],
            "set_recovery_time": COMMAND_PARAM_MAP["set_recovery_time"],
            "set_max_levels": COMMAND_PARAM_MAP["set_max_levels"],
            "set_sl_reduction": COMMAND_PARAM_MAP["set_sl_reduction"],
            "reset_reentry_config": COMMAND_PARAM_MAP["reset_reentry_config"],
            "autonomous_mode": {"handler": "handle_autonomous_mode", "params": ["mode"], "type": "toggle", "options": ["status", "on", "off"]},
            "autonomous_status": {"handler": "handle_autonomous_status", "params": [], "type": "direct"},
        }
    },
    "trends": {
        "name": "📍 Trend Management",
        "commands": {
            "show_trends": COMMAND_PARAM_MAP["show_trends"],
            "trend_matrix": COMMAND_PARAM_MAP["trend_matrix"],
            "set_trend": COMMAND_PARAM_MAP["set_trend"],
            "set_auto": COMMAND_PARAM_MAP["set_auto"],
            "trend_mode": COMMAND_PARAM_MAP["trend_mode"],
        }
    },
    "risk": {
        "name": "🛡️ Risk & Lot Management",
        "commands": {
            "view_risk_caps": COMMAND_PARAM_MAP["view_risk_caps"],
            "view_risk_status": COMMAND_PARAM_MAP["view_risk_status"],
            "set_daily_cap": COMMAND_PARAM_MAP["set_daily_cap"],
            "set_lifetime_cap": COMMAND_PARAM_MAP["set_lifetime_cap"],
            "set_risk_tier": COMMAND_PARAM_MAP["set_risk_tier"],
            "switch_tier": COMMAND_PARAM_MAP["switch_tier"],
            "clear_loss_data": COMMAND_PARAM_MAP["clear_loss_data"],
            "clear_daily_loss": COMMAND_PARAM_MAP["clear_daily_loss"],
            "lot_size_status": COMMAND_PARAM_MAP["lot_size_status"],
            "set_lot_size": COMMAND_PARAM_MAP["set_lot_size"],
            "reset_risk_settings": COMMAND_PARAM_MAP["reset_risk_settings"],
        }
    },
    "sl_system": {
        "name": "⚙️ SL System Control",
        "commands": {
            "sl_status": COMMAND_PARAM_MAP["sl_status"],
            "sl_system_change": COMMAND_PARAM_MAP["sl_system_change"],
            "sl_system_on": COMMAND_PARAM_MAP["sl_system_on"],
            "complete_sl_system_off": COMMAND_PARAM_MAP["complete_sl_system_off"],
            "view_sl_config": COMMAND_PARAM_MAP["view_sl_config"],
            "set_symbol_sl": COMMAND_PARAM_MAP["set_symbol_sl"],
            "reset_symbol_sl": COMMAND_PARAM_MAP["reset_symbol_sl"],
            "reset_all_sl": COMMAND_PARAM_MAP["reset_all_sl"],
        }
    },
    "orders": {
        "name": "💎 Dual Orders",
        "commands": {
            "dual_order_status": COMMAND_PARAM_MAP["dual_order_status"],
            "toggle_dual_orders": COMMAND_PARAM_MAP["toggle_dual_orders"],
        }
    },
    "profit": {
        "name": "📈 Profit Booking",
        "commands": {
            "profit_status": COMMAND_PARAM_MAP["profit_status"],
            "profit_stats": COMMAND_PARAM_MAP["profit_stats"],
            "toggle_profit_booking": COMMAND_PARAM_MAP["toggle_profit_booking"],
            "set_profit_targets": COMMAND_PARAM_MAP["set_profit_targets"],
            "profit_chains": COMMAND_PARAM_MAP["profit_chains"],
            "stop_profit_chain": COMMAND_PARAM_MAP["stop_profit_chain"],
            "stop_all_profit_chains": COMMAND_PARAM_MAP["stop_all_profit_chains"],
            "set_chain_multipliers": COMMAND_PARAM_MAP["set_chain_multipliers"],
            "profit_config": COMMAND_PARAM_MAP["profit_config"],
            "profit_sl_status": COMMAND_PARAM_MAP["profit_sl_status"],
            "profit_sl_mode": COMMAND_PARAM_MAP["profit_sl_mode"],
            "enable_profit_sl": COMMAND_PARAM_MAP["enable_profit_sl"],
            "disable_profit_sl": COMMAND_PARAM_MAP["disable_profit_sl"],
            "set_profit_sl": COMMAND_PARAM_MAP["set_profit_sl"],
            "reset_profit_sl": COMMAND_PARAM_MAP["reset_profit_sl"],
            "profit_sl_hunt": {"handler": "handle_profit_sl_hunt", "params": ["mode"], "type": "toggle", "options": ["status", "on", "off"]},
        }
    },
    "settings": {
        "name": "🔧 System Settings",
        "commands": {
            "chains": COMMAND_PARAM_MAP["chains"],
        }
    },
    "fine_tune": {
        "name": "⚡ Fine-Tune Settings",
        "commands": {
            "fine_tune": {"handler": "handle_fine_tune_menu", "params": [], "type": "menu"},
            "profit_protection": {"handler": "handle_profit_protection", "params": [], "type": "menu"},
            "sl_reduction": {"handler": "handle_sl_reduction", "params": [], "type": "menu"},
            "recovery_windows": {"handler": "handle_recovery_windows", "params": [], "type": "menu"},
        }
    },
    "diagnostics": {
        "name": "🔍 Diagnostics & Health",
        "commands": {
            "health_status": COMMAND_PARAM_MAP["health_status"],
            "set_log_level": COMMAND_PARAM_MAP["set_log_level"],
            "get_log_level": COMMAND_PARAM_MAP["get_log_level"],
            "reset_log_level": COMMAND_PARAM_MAP["reset_log_level"],
            "error_stats": COMMAND_PARAM_MAP["error_stats"],
            "reset_errors": COMMAND_PARAM_MAP["reset_errors"],
            "reset_health": COMMAND_PARAM_MAP["reset_health"],
            "export_logs": COMMAND_PARAM_MAP["export_logs"],
            "export_current_session": COMMAND_PARAM_MAP["export_current_session"],
            "export_by_date": COMMAND_PARAM_MAP["export_by_date"],
            "export_date_range": COMMAND_PARAM_MAP["export_date_range"],
            "log_file_size": COMMAND_PARAM_MAP["log_file_size"],
            "clear_old_logs": COMMAND_PARAM_MAP["clear_old_logs"],
            "trading_debug_mode": COMMAND_PARAM_MAP["trading_debug_mode"],
            "system_resources": COMMAND_PARAM_MAP["system_resources"],
        }
    }
    }

# Cached command categories for backward compatibility
_COMMAND_CATEGORIES_CACHE = None

def _init_command_categories():
    """Initialize COMMAND_CATEGORIES cache"""
    global _COMMAND_CATEGORIES_CACHE
    if _COMMAND_CATEGORIES_CACHE is None:
        _COMMAND_CATEGORIES_CACHE = get_command_categories()
    return _COMMAND_CATEGORIES_CACHE

# Create a class that acts like a dict but lazy-loads
class _LazyCommandCategories:
    def __getitem__(self, key):
        return _init_command_categories()[key]
    
    def __contains__(self, key):
        return key in _init_command_categories()
    
    def items(self):
        return _init_command_categories().items()
    
    def keys(self):
        return _init_command_categories().keys()
    
    def values(self):
        return _init_command_categories().values()
    
    def get(self, key, default=None):
        return _init_command_categories().get(key, default)

# Module-level variable that lazy-loads
COMMAND_CATEGORIES = _LazyCommandCategories()

# Quick Actions
QUICK_ACTIONS = {
    "dashboard": {"handler": "handle_dashboard", "text": "📊 Dashboard"},
    "pause_resume": {"handler": "action_pause_resume", "text": "⏸️ Pause/Resume"},
    "trades": {"handler": "handle_trades", "text": "📈 Trades"},
    "performance": {"handler": "handle_performance", "text": "💰 Performance"},
}

# Zero-Typing UI - Reply Keyboard to Callback Mapping
# Maps Reply Keyboard Text Buttons to Internal Callback Data (2-Column Layout)
REPLY_MENU_MAP = {
    # Row 1
    "📊 Dashboard": "action_dashboard",
    "⏸️ Pause/Resume": "action_pause_resume",
    
    # Row 2
    "📈 Active Trades": "action_trades",
    "💰 Performance": "performance",
    
    # Row 3
    "💱 Trading": "trading",
    "⏱️ Timeframe": "menu_timeframe",
    
    # Row 4
    "🔄 Re-entry": "menu_reentry",
    "📍 Trends": "menu_trend",
    
    # Row 5
    "🛡️ Risk": "menu_risk",
    "⚙️ SL System": "menu_sl_system",
    
    # Row 6
    "📦 Orders": "orders",
    "📈 Profit": "menu_profit",
    
    # Row 7
    "⚙️ Settings": "settings",
    "🔬 Diagnostics": "menu_diagnostics",
    
    # Row 8
    "⚡ Fine-Tune": "menu_finetune",
    "🆘 Help": "action_help",
    
    # Row 9
    "🔄 Refresh": "refresh",
    "🚨 PANIC CLOSE": "action_panic_close",

    # Added Keys for New Buttons
    "📋 Sessions": "action_session_menu",
    "⏰ Clock System": "action_clock_system",
    "🔊 Voice Test": "action_voice_test"
}

# Reverse mapping for validation
CALLBACK_TO_BUTTON = {v: k for k, v in REPLY_MENU_MAP.items()}
