import json
import os
from typing import Dict, Any

def safe_int_from_env(env_var: str, default: int = 0) -> int:
    """Safely parse integer from environment variable with normalization"""
    value = os.getenv(env_var)
    if value is None:
        return default
    
    # Strip and normalize
    value = value.strip().replace(",", "").replace("+", "")
    
    if not value:
        return default
        
    try:
        return int(value)
    except ValueError:
        print(f"WARNING: Invalid integer value for {env_var}: '{os.getenv(env_var)}', using default {default}")
        return default

class Config:
    def __init__(self):
        self.config_file = "config/config.json"
        self.default_config = {
            "telegram_token": os.getenv("TELEGRAM_TOKEN", ""),
            "telegram_chat_id": safe_int_from_env("TELEGRAM_CHAT_ID", 0),
            "allowed_telegram_user": safe_int_from_env("TELEGRAM_CHAT_ID", 0),
            "mt5_login": safe_int_from_env("MT5_LOGIN", 0),
            "mt5_password": os.getenv("MT5_PASSWORD", ""),
            "mt5_server": os.getenv("MT5_SERVER", ""),
            "risk_tiers": {
                "5000": {"per_trade_cap": 150, "daily_loss_limit": 200, "max_total_loss": 500, "base_multiplier": 1.0},
                "10000": {"per_trade_cap": 300, "daily_loss_limit": 400, "max_total_loss": 1000, "base_multiplier": 2.0},
                "25000": {"per_trade_cap": 750, "daily_loss_limit": 1000, "max_total_loss": 2500, "base_multiplier": 5.0},
                "50000": {"per_trade_cap": 1500, "daily_loss_limit": 2000, "max_total_loss": 5000, "base_multiplier": 10.0},
                "100000": {"per_trade_cap": 3000, "daily_loss_limit": 4000, "max_total_loss": 10000, "base_multiplier": 20.0}
            },
            "volatility_risk_levels": {
                "LOW": {"base_per_trade_cap": 30, "base_sl_points": 7},
                "MEDIUM": {"base_per_trade_cap": 50, "base_sl_points": 10},
                "HIGH": {"base_per_trade_cap": 80, "base_sl_points": 15}
            },
            "symbol_config": {
                "EURUSD": {"volatility": "LOW", "pip_value": 10.0, "max_lots": 10.0, "contract_size": 100000},
                "GBPUSD": {"volatility": "MEDIUM", "pip_value": 10.0, "max_lots": 8.0, "contract_size": 100000},
                "USDJPY": {"volatility": "MEDIUM", "pip_value": 9.0, "max_lots": 10.0, "contract_size": 100000},
                "AUDUSD": {"volatility": "MEDIUM", "pip_value": 10.0, "max_lots": 8.0, "contract_size": 100000},
                "USDCAD": {"volatility": "MEDIUM", "pip_value": 8.0, "max_lots": 10.0, "contract_size": 100000},
                "NZDUSD": {"volatility": "MEDIUM", "pip_value": 10.0, "max_lots": 8.0, "contract_size": 100000},
                "EURJPY": {"volatility": "HIGH", "pip_value": 9.5, "max_lots": 5.0, "contract_size": 100000},
                "GBPJPY": {"volatility": "HIGH", "pip_value": 9.0, "max_lots": 3.0, "contract_size": 100000},
                "AUDJPY": {"volatility": "HIGH", "pip_value": 9.2, "max_lots": 5.0, "contract_size": 100000},
                "XAUUSD": {"volatility": "HIGH", "pip_value": 1.0, "max_lots": 2.0, "contract_size": 100}
            },
            "default_risk_tier": "5000",
            "mt5_retries": 3,
            "mt5_wait": 5,
            "simulate_orders": False,
            "debug": True,
            "strategies": ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"],
            "daily_reset_time": "03:35",
            "fibonacci_levels": {"tp1": 0.618, "tp2": 1.0, "tp3": 1.618},
            "exit_strategies": {
                "default_trailing_points": 50.0,
                "default_time_exit_hours": 4.0,
                "check_interval_seconds": 5
            },
            "dual_order_config": {
                "enabled": True
            },
            "profit_booking_config": {
                "enabled": True,
                "base_profit": 10,
                "max_level": 4,
                "multipliers": [1, 2, 4, 8, 16],
                "profit_targets": [10, 20, 40, 80, 160],
                "sl_reductions": [0, 10, 25, 40, 50],
                "sl_system": "SL-1.1",
                "sl_1_1_settings": {
                    "combinedlogic-1": 20.0,
                    "combinedlogic-2": 40.0,
                    "combinedlogic-3": 50.0
                },
                "sl_2_1_settings": {
                    "fixed_sl": 10.0
                },
                "sl_enabled": True
            },
            "reverse_shield_config": {
                "enabled": False,  # Default OFF for safety
                "recovery_threshold_percent": 0.70,  # 70% recovery level
                "shield_order_a_rr": 1.0,  # 1:1 TP for Order A
                "use_profit_booking_for_order_b": True,
                "shield_lot_size_multiplier": 0.5,  # 50% of original lot (SAFETY)
                "max_concurrent_shields": 3,
                
                # Risk Integration
                "risk_integration": {
                    "enable_smart_adjustment": True,
                    "min_daily_loss_buffer": 50.0,
                    "min_margin_buffer_percent": 20.0,
                    "cancel_if_below_min_lot": True,
                    "fallback_to_v2_on_cancel": True
                },
                
                # Notifications
                "notifications": {
                    "shield_activated": True,
                    "kill_switch_triggered": True,
                    "shield_closed": True,
                    "shield_profit_booked": True,
                    "shield_cancelled": True,
                    "show_smart_adjustment_details": True,
                    "show_pnl_breakdown": True,
                    "show_recovery_projection": True
                }
            }
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Environment variables ALWAYS override config.json (highest priority)
            # If env var is SET (even if empty), it takes precedence
            # If env var is NOT SET (None), keep config.json value
            
            if os.getenv("TELEGRAM_TOKEN") is not None:
                self.config["telegram_token"] = os.getenv("TELEGRAM_TOKEN", "")
            
            if os.getenv("TELEGRAM_CHAT_ID") is not None:
                chat_id = safe_int_from_env("TELEGRAM_CHAT_ID", 0)
                self.config["telegram_chat_id"] = chat_id
                self.config["allowed_telegram_user"] = chat_id
            
            if os.getenv("MT5_LOGIN") is not None:
                self.config["mt5_login"] = safe_int_from_env("MT5_LOGIN", 0)
            
            if os.getenv("MT5_PASSWORD") is not None:
                self.config["mt5_password"] = os.getenv("MT5_PASSWORD", "")
            
            if os.getenv("MT5_SERVER") is not None:
                self.config["mt5_server"] = os.getenv("MT5_SERVER", "")
            
            # Ensure new config sections exist (backward compatibility)
            if "dual_order_config" not in self.config:
                self.config["dual_order_config"] = self.default_config["dual_order_config"]
            if "profit_booking_config" not in self.config:
                self.config["profit_booking_config"] = self.default_config["profit_booking_config"]
            
            # Debug: Show loaded credentials (mask password)
            if self.config.get("debug", False):
                try:
                    print(f"Config loaded - MT5 Login: {self.config['mt5_login']}, Server: {self.config['mt5_server']}")
                except UnicodeEncodeError:
                    print(f"Config loaded - MT5 Login: {self.config['mt5_login']}, Server: {self.config['mt5_server']}")
        else:
            self.config = self.default_config
            self.save_config()

    def save_config(self):
        """Save config to file with error handling (optimized for speed)"""
        try:
            import os
            import tempfile
            
            # Use atomic write with temp file (faster than backup copy)
            # Write to temp file first, then rename (atomic operation)
            temp_file = f"{self.config_file}.tmp"
            
            # Write config to temp file
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            # Atomic rename (faster than copy)
            # On Windows, need to remove existing file first
            if os.path.exists(self.config_file):
                os.replace(temp_file, self.config_file)  # Atomic on POSIX, near-atomic on Windows
            else:
                os.rename(temp_file, self.config_file)
                
        except Exception as e:
            print(f"[CONFIG SAVE ERROR] Failed to save config: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
            raise  # Re-raise to be caught by caller

    def __getitem__(self, key):
        return self.config.get(key)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def update(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def update_nested(self, path: str, value):
        """
        Update nested config value using dot notation
        
        Args:
            path: Dot-separated path (e.g., "re_entry_config.autonomous_config.enabled")
            value: New value to set
        """
        keys = path.split(".")
        current = self.config
        
        # Navigate to the nested location
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def save(self):
        """Alias for save_config() for compatibility"""
        self.save_config()