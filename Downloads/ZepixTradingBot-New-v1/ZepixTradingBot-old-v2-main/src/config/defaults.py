"""
Configuration Defaults Management for V5 Hybrid Plugin Architecture.

Document 11: Configuration Templates - Defaults Management
Provides robust default value fallback system for all configurations.

Author: Devin AI
Date: 2026-01-12
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from copy import deepcopy


class DefaultsManager:
    """Manages default configuration values with fallback system."""
    
    MAIN_CONFIG_DEFAULTS: Dict[str, Any] = {
        "telegram_controller_token": "",
        "telegram_notification_token": "",
        "telegram_analytics_token": "",
        "telegram_token": "",
        "telegram_chat_id": "",
        "mt5_login": "",
        "mt5_password": "",
        "mt5_server": "MetaQuotesDemo-MT5",
        "mt5_path": "",
        "plugin_system": {
            "enabled": True,
            "plugin_directory": "src/logic_plugins",
            "auto_discover": True,
            "max_plugin_execution_time": 5.0,
            "dual_core_mode": True
        },
        "plugins": {
            "combined_v3": {
                "enabled": True,
                "shadow_mode": False,
                "type": "V3_COMBINED",
                "database": "data/zepix_combined.db"
            },
            "price_action_1m": {
                "enabled": True,
                "shadow_mode": False,
                "type": "V6_PRICE_ACTION",
                "database": "data/zepix_price_action.db"
            },
            "price_action_5m": {
                "enabled": True,
                "shadow_mode": False,
                "type": "V6_PRICE_ACTION",
                "database": "data/zepix_price_action.db"
            },
            "price_action_15m": {
                "enabled": True,
                "shadow_mode": False,
                "type": "V6_PRICE_ACTION",
                "database": "data/zepix_price_action.db"
            },
            "price_action_1h": {
                "enabled": True,
                "shadow_mode": False,
                "type": "V6_PRICE_ACTION",
                "database": "data/zepix_price_action.db"
            }
        },
        "symbol_config": {
            "XAUUSD": {
                "symbol_name": "XAUUSD",
                "digits": 2,
                "pip_value_per_std_lot": 1.0,
                "min_lot": 0.01,
                "max_lot": 50.0,
                "max_spread_pips": 3.0
            }
        },
        "bot_config": {
            "combinedlogic-1": {
                "enabled": True,
                "lot_multiplier": 1.25,
                "risk_per_trade": 1.5,
                "max_daily_trades": 10,
                "logic_route": "LOGIC1"
            },
            "combinedlogic-2": {
                "enabled": True,
                "lot_multiplier": 1.0,
                "risk_per_trade": 1.0,
                "max_daily_trades": 8,
                "logic_route": "LOGIC2"
            },
            "combinedlogic-3": {
                "enabled": True,
                "lot_multiplier": 0.625,
                "risk_per_trade": 2.0,
                "max_daily_trades": 5,
                "logic_route": "LOGIC3"
            }
        }
    }
    
    V3_PLUGIN_DEFAULTS: Dict[str, Any] = {
        "plugin_id": "combined_v3",
        "version": "1.0.0",
        "enabled": True,
        "shadow_mode": False,
        "metadata": {
            "name": "V3 Combined Logic",
            "description": "12-signal V3 system with dual orders and MTF 4-pillar trends",
            "author": "Zepix Team",
            "created": "2026-01-12",
            "category": "V3_COMBINED",
            "logic_type": "LEGACY_V3"
        },
        "settings": {
            "supported_symbols": ["XAUUSD"],
            "supported_timeframes": ["5", "15", "60", "240"],
            "max_lot_size": 1.0,
            "daily_loss_limit": 500.0,
            "signal_handling": {
                "entry_signals": [
                    "Institutional_Launchpad",
                    "Liquidity_Trap",
                    "Momentum_Ignition",
                    "Mitigation_Block",
                    "Golden_Pocket",
                    "Screener",
                    "entry_v3"
                ],
                "exit_signals": ["Exit_Bullish", "Exit_Bearish"],
                "info_signals": ["Volatility_Squeeze", "Trend_Pulse"],
                "signal_12_enabled": True,
                "signal_12_name": "Sideways_Breakout"
            },
            "routing_matrix": {
                "priority_1_overrides": {
                    "Screener": "LOGIC3",
                    "Golden_Pocket_1H": "LOGIC3",
                    "Golden_Pocket_4H": "LOGIC3"
                },
                "priority_2_timeframe_routing": {
                    "5": "LOGIC1",
                    "15": "LOGIC2",
                    "60": "LOGIC3",
                    "240": "LOGIC3"
                },
                "logic_multipliers": {
                    "LOGIC1": 1.25,
                    "LOGIC2": 1.0,
                    "LOGIC3": 0.625
                }
            },
            "dual_order_system": {
                "enabled": True,
                "order_split_ratio": 0.5,
                "order_a_settings": {
                    "use_v3_smart_sl": True,
                    "target_level": "TP2",
                    "trailing_enabled": True
                },
                "order_b_settings": {
                    "use_fixed_sl": True,
                    "fixed_sl_dollars": 10.0,
                    "target_level": "TP1",
                    "trailing_enabled": False
                }
            },
            "mtf_4_pillar_system": {
                "enabled": True,
                "pillars": ["15m", "1h", "4h", "1d"],
                "extraction_indices": [2, 3, 4, 5],
                "ignore_indices": [0, 1],
                "min_aligned_for_entry": 3,
                "alignment_weight": {
                    "15m": 1.0,
                    "1h": 1.5,
                    "4h": 2.0,
                    "1d": 2.5
                }
            },
            "position_sizing": {
                "base_risk_percentage": 1.5,
                "consensus_score_range": [0, 9],
                "consensus_multiplier_range": [0.2, 1.0],
                "apply_logic_multiplier": True,
                "min_lot_size": 0.01,
                "max_lot_size": 1.0
            },
            "trend_bypass_logic": {
                "enabled": True,
                "bypass_signals": ["entry_v3"],
                "require_trend_signals": [
                    "Institutional_Launchpad",
                    "Liquidity_Trap",
                    "Momentum_Ignition"
                ]
            },
            "risk_management": {
                "max_open_trades": 5,
                "max_daily_trades": 10,
                "max_symbol_exposure": 0.30,
                "daily_loss_limit": 500.0
            }
        },
        "notifications": {
            "notify_on_entry": True,
            "notify_on_exit": True,
            "notify_on_routing": True,
            "notify_on_error": True,
            "use_voice_alerts": True,
            "telegram_bot": "controller"
        },
        "database": {
            "path": "data/zepix_combined.db",
            "backup_enabled": True,
            "backup_frequency": "daily",
            "sync_to_central": True,
            "sync_interval_minutes": 5
        }
    }
    
    V6_1M_DEFAULTS: Dict[str, Any] = {
        "plugin_id": "price_action_1m",
        "version": "1.0.0",
        "enabled": True,
        "shadow_mode": False,
        "metadata": {
            "name": "V6 1M Scalping",
            "description": "Ultra-fast 1-minute scalping with Order B only",
            "author": "Zepix Team",
            "created": "2026-01-12",
            "category": "V6_PRICE_ACTION",
            "timeframe": "1m"
        },
        "settings": {
            "supported_symbols": ["XAUUSD"],
            "supported_timeframes": ["1"],
            "order_routing": "ORDER_B_ONLY",
            "entry_conditions": {
                "adx_threshold": 20,
                "adx_strength_required": "MODERATE",
                "confidence_threshold": 80,
                "max_spread_pips": 2.0,
                "require_market_state_alignment": True
            },
            "order_configuration": {
                "use_order_a": False,
                "use_order_b": True,
                "target_level": "TP1",
                "quick_exit_enabled": True
            },
            "risk_management": {
                "risk_multiplier": 0.5,
                "base_risk_percentage": 1.0,
                "max_lot_size": 0.10,
                "max_open_trades": 3,
                "max_daily_trades": 20,
                "daily_loss_limit": 200.0
            },
            "trend_pulse_integration": {
                "enabled": True,
                "require_pulse_alignment": True,
                "min_bull_count_for_buy": 3,
                "min_bear_count_for_sell": 3
            },
            "exit_rules": {
                "tp1_pips": 10,
                "sl_pips": 15,
                "use_trailing_stop": False,
                "max_hold_time_minutes": 15
            }
        },
        "notifications": {
            "notify_on_entry": True,
            "notify_on_exit": True,
            "notify_on_error": True,
            "use_voice_alerts": False,
            "telegram_bot": "notification"
        },
        "database": {
            "path": "data/zepix_price_action.db",
            "table_name": "price_action_1m_trades",
            "backup_enabled": True,
            "sync_to_central": True
        }
    }
    
    V6_5M_DEFAULTS: Dict[str, Any] = {
        "plugin_id": "price_action_5m",
        "version": "1.0.0",
        "enabled": True,
        "shadow_mode": False,
        "metadata": {
            "name": "V6 5M Momentum",
            "description": "5-minute momentum trades with dual orders",
            "author": "Zepix Team",
            "created": "2026-01-12",
            "category": "V6_PRICE_ACTION",
            "timeframe": "5m"
        },
        "settings": {
            "supported_symbols": ["XAUUSD"],
            "supported_timeframes": ["5"],
            "order_routing": "DUAL_ORDERS",
            "entry_conditions": {
                "adx_threshold": 25,
                "adx_strength_required": "STRONG",
                "confidence_threshold": 70,
                "require_15m_alignment": True,
                "require_momentum_increasing": True
            },
            "order_configuration": {
                "use_order_a": True,
                "use_order_b": True,
                "split_ratio": 0.5,
                "order_a_target": "TP2",
                "order_b_target": "TP1",
                "same_sl_for_both": True
            },
            "risk_management": {
                "risk_multiplier": 1.0,
                "base_risk_percentage": 1.5,
                "max_lot_size": 0.20,
                "max_open_trades": 4,
                "max_daily_trades": 12,
                "daily_loss_limit": 300.0
            },
            "trend_pulse_integration": {
                "enabled": True,
                "require_pulse_alignment": True
            },
            "exit_rules": {
                "tp1_pips": 15,
                "tp2_pips": 30,
                "move_to_breakeven_after_tp1": True,
                "breakeven_buffer_pips": 2.0
            }
        },
        "notifications": {
            "notify_on_entry": True,
            "notify_on_exit": True,
            "notify_on_error": True,
            "use_voice_alerts": False,
            "telegram_bot": "notification"
        },
        "database": {
            "path": "data/zepix_price_action.db",
            "table_name": "price_action_5m_trades",
            "backup_enabled": True,
            "sync_to_central": True
        }
    }
    
    V6_15M_DEFAULTS: Dict[str, Any] = {
        "plugin_id": "price_action_15m",
        "version": "1.0.0",
        "enabled": True,
        "shadow_mode": False,
        "metadata": {
            "name": "V6 15M Intraday",
            "description": "15-minute intraday with Order A only",
            "author": "Zepix Team",
            "created": "2026-01-12",
            "category": "V6_PRICE_ACTION",
            "timeframe": "15m"
        },
        "settings": {
            "supported_symbols": ["XAUUSD"],
            "supported_timeframes": ["15"],
            "order_routing": "ORDER_A_ONLY",
            "entry_conditions": {
                "adx_threshold": 22,
                "confidence_threshold": 65,
                "require_market_state_match": True,
                "require_pulse_alignment": True
            },
            "order_configuration": {
                "use_order_a": True,
                "use_order_b": False,
                "target_level": "TP2"
            },
            "risk_management": {
                "risk_multiplier": 1.25,
                "base_risk_percentage": 1.5,
                "max_lot_size": 0.25,
                "max_open_trades": 3,
                "max_daily_trades": 8,
                "daily_loss_limit": 400.0
            },
            "trend_pulse_integration": {
                "enabled": True,
                "require_pulse_alignment": True,
                "check_bull_bear_ratio": True
            }
        },
        "notifications": {
            "notify_on_entry": True,
            "notify_on_exit": True,
            "notify_on_error": True,
            "use_voice_alerts": False,
            "telegram_bot": "notification"
        },
        "database": {
            "path": "data/zepix_price_action.db",
            "table_name": "price_action_15m_trades",
            "backup_enabled": True,
            "sync_to_central": True
        }
    }
    
    V6_1H_DEFAULTS: Dict[str, Any] = {
        "plugin_id": "price_action_1h",
        "version": "1.0.0",
        "enabled": True,
        "shadow_mode": False,
        "metadata": {
            "name": "V6 1H Swing",
            "description": "1-hour swing trades with Order A only",
            "author": "Zepix Team",
            "created": "2026-01-12",
            "category": "V6_PRICE_ACTION",
            "timeframe": "1h"
        },
        "settings": {
            "supported_symbols": ["XAUUSD"],
            "supported_timeframes": ["60"],
            "order_routing": "ORDER_A_ONLY",
            "entry_conditions": {
                "confidence_threshold": 60,
                "require_4h_alignment": True,
                "require_1d_alignment": True,
                "higher_tf_weight": 2.0
            },
            "order_configuration": {
                "use_order_a": True,
                "use_order_b": False,
                "target_level": "TP2",
                "extended_tp_enabled": True
            },
            "risk_management": {
                "risk_multiplier": 1.5,
                "base_risk_percentage": 2.0,
                "max_lot_size": 0.30,
                "max_open_trades": 2,
                "max_daily_trades": 5,
                "daily_loss_limit": 500.0
            },
            "trend_pulse_integration": {
                "enabled": False,
                "use_traditional_tf_trends": True
            }
        },
        "notifications": {
            "notify_on_entry": True,
            "notify_on_exit": True,
            "notify_on_error": True,
            "use_voice_alerts": False,
            "telegram_bot": "notification"
        },
        "database": {
            "path": "data/zepix_price_action.db",
            "table_name": "price_action_1h_trades",
            "backup_enabled": True,
            "sync_to_central": True
        }
    }
    
    SHADOW_MODE_DEFAULTS: Dict[str, Any] = {
        "log_all_signals": True,
        "simulate_order_placement": True,
        "track_hypothetical_pnl": True,
        "shadow_duration_hours": 72
    }
    
    ENV_DEFAULTS: Dict[str, str] = {
        "TELEGRAM_CONTROLLER_TOKEN": "",
        "TELEGRAM_NOTIFICATION_TOKEN": "",
        "TELEGRAM_ANALYTICS_TOKEN": "",
        "TELEGRAM_MAIN_TOKEN": "",
        "MT5_PASSWORD": "",
        "DB_ENCRYPTION_KEY": "",
        "ADMIN_CHAT_ID": "",
        "ADMIN_PASSWORD": "",
        "ENVIRONMENT": "development",
        "DEBUG_MODE": "false",
        "LOG_LEVEL": "INFO"
    }
    
    @classmethod
    def get_main_config_defaults(cls) -> Dict[str, Any]:
        """Get deep copy of main config defaults."""
        return deepcopy(cls.MAIN_CONFIG_DEFAULTS)
    
    @classmethod
    def get_v3_plugin_defaults(cls) -> Dict[str, Any]:
        """Get deep copy of V3 plugin defaults."""
        return deepcopy(cls.V3_PLUGIN_DEFAULTS)
    
    @classmethod
    def get_v6_1m_defaults(cls) -> Dict[str, Any]:
        """Get deep copy of V6 1M plugin defaults."""
        return deepcopy(cls.V6_1M_DEFAULTS)
    
    @classmethod
    def get_v6_5m_defaults(cls) -> Dict[str, Any]:
        """Get deep copy of V6 5M plugin defaults."""
        return deepcopy(cls.V6_5M_DEFAULTS)
    
    @classmethod
    def get_v6_15m_defaults(cls) -> Dict[str, Any]:
        """Get deep copy of V6 15M plugin defaults."""
        return deepcopy(cls.V6_15M_DEFAULTS)
    
    @classmethod
    def get_v6_1h_defaults(cls) -> Dict[str, Any]:
        """Get deep copy of V6 1H plugin defaults."""
        return deepcopy(cls.V6_1H_DEFAULTS)
    
    @classmethod
    def get_shadow_mode_defaults(cls) -> Dict[str, Any]:
        """Get deep copy of shadow mode defaults."""
        return deepcopy(cls.SHADOW_MODE_DEFAULTS)
    
    @classmethod
    def get_env_defaults(cls) -> Dict[str, str]:
        """Get deep copy of environment defaults."""
        return deepcopy(cls.ENV_DEFAULTS)
    
    @classmethod
    def get_v6_defaults_by_timeframe(cls, timeframe: str) -> Dict[str, Any]:
        """Get V6 defaults by timeframe."""
        timeframe_map = {
            "1m": cls.get_v6_1m_defaults,
            "1": cls.get_v6_1m_defaults,
            "5m": cls.get_v6_5m_defaults,
            "5": cls.get_v6_5m_defaults,
            "15m": cls.get_v6_15m_defaults,
            "15": cls.get_v6_15m_defaults,
            "1h": cls.get_v6_1h_defaults,
            "60": cls.get_v6_1h_defaults
        }
        getter = timeframe_map.get(timeframe)
        if getter:
            return getter()
        raise ValueError(f"Unknown timeframe: {timeframe}")
    
    @staticmethod
    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence."""
        result = deepcopy(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DefaultsManager.deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)
        return result
    
    @classmethod
    def apply_defaults(cls, config: Dict[str, Any], config_type: str) -> Dict[str, Any]:
        """Apply defaults to a configuration, filling in missing values."""
        if config_type == "main":
            defaults = cls.get_main_config_defaults()
        elif config_type == "v3":
            defaults = cls.get_v3_plugin_defaults()
        elif config_type == "v6_1m":
            defaults = cls.get_v6_1m_defaults()
        elif config_type == "v6_5m":
            defaults = cls.get_v6_5m_defaults()
        elif config_type == "v6_15m":
            defaults = cls.get_v6_15m_defaults()
        elif config_type == "v6_1h":
            defaults = cls.get_v6_1h_defaults()
        else:
            raise ValueError(f"Unknown config type: {config_type}")
        
        return cls.deep_merge(defaults, config)


class EnvironmentVariableResolver:
    """Resolves environment variable placeholders in configuration."""
    
    ENV_VAR_PATTERN = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)\}')
    
    @classmethod
    def resolve(cls, value: Any) -> Any:
        """Resolve environment variables in a value."""
        if isinstance(value, str):
            return cls._resolve_string(value)
        elif isinstance(value, dict):
            return {k: cls.resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [cls.resolve(item) for item in value]
        return value
    
    @classmethod
    def _resolve_string(cls, value: str) -> str:
        """Resolve environment variables in a string."""
        def replace_env_var(match):
            var_name = match.group(1)
            env_value = os.environ.get(var_name, "")
            return env_value
        
        return cls.ENV_VAR_PATTERN.sub(replace_env_var, value)
    
    @classmethod
    def resolve_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all environment variables in a configuration."""
        return cls.resolve(config)
    
    @classmethod
    def has_unresolved_vars(cls, config: Dict[str, Any]) -> List[str]:
        """Check for unresolved environment variables."""
        unresolved = []
        
        def check_value(value: Any, path: str = ""):
            if isinstance(value, str):
                matches = cls.ENV_VAR_PATTERN.findall(value)
                for var_name in matches:
                    if not os.environ.get(var_name):
                        unresolved.append(f"{path}: ${{{var_name}}}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    check_value(item, f"{path}[{i}]")
        
        check_value(config)
        return unresolved


class ConfigLoader:
    """Configuration loader with defaults and environment variable support."""
    
    def __init__(self, base_path: str = ""):
        """Initialize config loader with optional base path."""
        self.base_path = base_path
    
    def load_main_config(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Load main configuration with defaults and env var resolution."""
        if file_path is None:
            file_path = os.path.join(self.base_path, "config", "config.json")
        
        config = self._load_json_file(file_path)
        config = DefaultsManager.apply_defaults(config, "main")
        config = EnvironmentVariableResolver.resolve_config(config)
        return config
    
    def load_v3_config(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Load V3 plugin configuration with defaults."""
        if file_path is None:
            file_path = os.path.join(
                self.base_path, "src", "logic_plugins", "combined_v3", "config.json"
            )
        
        config = self._load_json_file(file_path)
        config = DefaultsManager.apply_defaults(config, "v3")
        config = EnvironmentVariableResolver.resolve_config(config)
        return config
    
    def load_v6_config(self, timeframe: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Load V6 plugin configuration with defaults for specific timeframe."""
        if file_path is None:
            tf_dir_map = {
                "1m": "price_action_1m",
                "1": "price_action_1m",
                "5m": "price_action_5m",
                "5": "price_action_5m",
                "15m": "price_action_15m",
                "15": "price_action_15m",
                "1h": "price_action_1h",
                "60": "price_action_1h"
            }
            dir_name = tf_dir_map.get(timeframe, f"price_action_{timeframe}")
            file_path = os.path.join(
                self.base_path, "src", "logic_plugins", dir_name, "config.json"
            )
        
        config = self._load_json_file(file_path)
        
        config_type_map = {
            "1m": "v6_1m", "1": "v6_1m",
            "5m": "v6_5m", "5": "v6_5m",
            "15m": "v6_15m", "15": "v6_15m",
            "1h": "v6_1h", "60": "v6_1h"
        }
        config_type = config_type_map.get(timeframe, "v6_1m")
        
        config = DefaultsManager.apply_defaults(config, config_type)
        config = EnvironmentVariableResolver.resolve_config(config)
        return config
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file, returning empty dict if not found."""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict[str, Any], file_path: str) -> None:
        """Save configuration to JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def generate_template(self, config_type: str) -> Dict[str, Any]:
        """Generate a configuration template with defaults."""
        if config_type == "main":
            return DefaultsManager.get_main_config_defaults()
        elif config_type == "v3":
            return DefaultsManager.get_v3_plugin_defaults()
        elif config_type == "v6_1m":
            return DefaultsManager.get_v6_1m_defaults()
        elif config_type == "v6_5m":
            return DefaultsManager.get_v6_5m_defaults()
        elif config_type == "v6_15m":
            return DefaultsManager.get_v6_15m_defaults()
        elif config_type == "v6_1h":
            return DefaultsManager.get_v6_1h_defaults()
        else:
            raise ValueError(f"Unknown config type: {config_type}")


def generate_env_template() -> str:
    """Generate .env template file content."""
    return """# Multi-Telegram System
TELEGRAM_CONTROLLER_TOKEN=123456:ABC-DEF...
TELEGRAM_NOTIFICATION_TOKEN=789012:GHI-JKL...
TELEGRAM_ANALYTICS_TOKEN=345678:MNO-PQR...
TELEGRAM_MAIN_TOKEN=901234:STU-VWX...

# MT5 Credentials
MT5_PASSWORD=YourSecurePassword123!

# Database Encryption
DB_ENCRYPTION_KEY=your-32-char-encryption-key

# Admin Settings
ADMIN_CHAT_ID=123456789
ADMIN_PASSWORD=SecureAdminPass456!

# Development/Production Mode
ENVIRONMENT=production
DEBUG_MODE=false
LOG_LEVEL=INFO
"""


def generate_gitignore_additions() -> str:
    """Generate .gitignore additions for sensitive files."""
    return """# Environment and secrets
.env
.env.local
.env.production
*.pem
*.key

# Database files
data/*.db
data/*.db-journal

# Logs
logs/
*.log

# Config backups
config/*.bak
"""
