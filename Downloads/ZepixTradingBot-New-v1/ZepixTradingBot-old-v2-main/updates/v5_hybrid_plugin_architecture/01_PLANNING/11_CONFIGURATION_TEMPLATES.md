# CONFIGURATION TEMPLATES

**Version:** 2.0 (V3/V6 Specific Configs)  
**Date:** 2026-01-12  
**Status:** Production-Ready Templates

---

## 🎛️ MAIN BOT CONFIGURATION

**File:** `config/config.json`

```json
{
    "telegram_controller_token": "${TELEGRAM_CONTROLLER_TOKEN}",
    "telegram_notification_token": "${TELEGRAM_NOTIFICATION_TOKEN}",
    "telegram_analytics_token": "${TELEGRAM_ANALYTICS_TOKEN}",
    "telegram_token": "${TELEGRAM_MAIN_TOKEN}",
    "telegram_chat_id": "YOUR_CHAT_ID",
    
    "mt5_login": "YOUR_MT5_LOGIN",
    "mt5_password": "${MT5_PASSWORD}",
    "mt5_server": "MetaQuotesDemo-MT5",
    "mt5_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
    
    "plugin_system": {
        "enabled": true,
        "plugin_directory": "src/logic_plugins",
        "auto_discover": true,
        "max_plugin_execution_time": 5.0,
        "dual_core_mode": true
    },
    
    "plugins": {
        "combined_v3": {
            "enabled": true,
            "shadow_mode": false,
            "type": "V3_COMBINED",
            "database": "data/zepix_combined.db"
        },
        "price_action_1m": {
            "enabled": true,
            "shadow_mode": false,
            "type": "V6_PRICE_ACTION",
            "database": "data/zepix_price_action.db"
        },
        "price_action_5m": {
            "enabled": true,
            "shadow_mode": false,
            "type": "V6_PRICE_ACTION",
            "database": "data/zepix_price_action.db"
        },
        "price_action_15m": {
            "enabled": true,
            "shadow_mode": false,
            "type": "V6_PRICE_ACTION",
            "database": "data/zepix_price_action.db"
        },
        "price_action_1h": {
            "enabled": true,
            "shadow_mode": false,
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
            "enabled": true,
            "lot_multiplier": 1.25,
            "risk_per_trade": 1.5,
            "max_daily_trades": 10,
            "logic_route": "LOGIC1"
        },
        "combinedlogic-2": {
            "enabled": true,
            "lot_multiplier": 1.0,
            "risk_per_trade": 1.0,
            "max_daily_trades": 8,
            "logic_route": "LOGIC2"
        },
        "combinedlogic-3": {
            "enabled": true,
            "lot_multiplier": 0.625,
            "risk_per_trade": 2.0,
            "max_daily_trades": 5,
            "logic_route": "LOGIC3"
        }
    }
}
```

---

## 🔌 V3 COMBINED LOGIC PLUGIN CONFIG

**File:** `src/logic_plugins/combined_v3/config.json`

```json
{
    "plugin_id": "combined_v3",
    "version": "1.0.0",
    "enabled": true,
    "shadow_mode": false,
    
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
            
            "signal_12_enabled": true,
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
            "enabled": true,
            "order_split_ratio": 0.5,
            "order_a_settings": {
                "use_v3_smart_sl": true,
                "target_level": "TP2",
                "trailing_enabled": true
            },
            "order_b_settings": {
                "use_fixed_sl": true,
                "fixed_sl_dollars": 10.0,
                "target_level": "TP1",
                "trailing_enabled": false
            }
        },
        
        "mtf_4_pillar_system": {
            "enabled": true,
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
            "apply_logic_multiplier": true,
            "min_lot_size": 0.01,
            "max_lot_size": 1.0
        },
        
        "trend_bypass_logic": {
            "enabled": true,
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
        "notify_on_entry": true,
        "notify_on_exit": true,
        "notify_on_routing": true,
        "notify_on_error": true,
        "use_voice_alerts": true,
        "telegram_bot": "controller"
    },
    
    "database": {
        "path": "data/zepix_combined.db",
        "backup_enabled": true,
        "backup_frequency": "daily",
        "sync_to_central": true,
        "sync_interval_minutes": 5
    }
}
```

---

## 🎯 V6 1M SCALPING PLUGIN CONFIG

**File:** `src/logic_plugins/price_action_1m/config.json`

```json
{
    "plugin_id": "price_action_1m",
    "version": "1.0.0",
    "enabled": true,
    "shadow_mode": false,
    
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
            "require_market_state_alignment": true
        },
        
        "order_configuration": {
            "use_order_a": false,
            "use_order_b": true,
            "target_level": "TP1",
            "quick_exit_enabled": true
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
            "enabled": true,
            "require_pulse_alignment": true,
            "min_bull_count_for_buy": 3,
            "min_bear_count_for_sell": 3
        },
        
        "exit_rules": {
            "tp1_pips": 10,
            "sl_pips": 15,
            "use_trailing_stop": false,
            "max_hold_time_minutes": 15
        }
    },
    
    "notifications": {
        "notify_on_entry": true,
        "notify_on_exit": true,
        "notify_on_error": true,
        "use_voice_alerts": false,
        "telegram_bot": "notification"
    },
    
    "database": {
        "path": "data/zepix_price_action.db",
        "table_name": "price_action_1m_trades",
        "backup_enabled": true,
        "sync_to_central": true
    }
}
```

---

## 📈 V6 5M MOMENTUM PLUGIN CONFIG

**File:** `src/logic_plugins/price_action_5m/config.json`

```json
{
    "plugin_id": "price_action_5m",
    "version": "1.0.0",
    "enabled": true,
    "shadow_mode": false,
    
    "metadata": {
        "name": "V6 5M Momentum",
        "description": "5-minute momentum trades with dual orders",
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
            "require_15m_alignment": true,
            "require_momentum_increasing": true
        },
        
        "order_configuration": {
            "use_order_a": true,
            "use_order_b": true,
            "split_ratio": 0.5,
            "order_a_target": "TP2",
            "order_b_target": "TP1",
            "same_sl_for_both": true
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
            "enabled": true,
            "require_pulse_alignment": true
        },
        
        "exit_rules": {
            "tp1_pips": 15,
            "tp2_pips": 30,
            "move_to_breakeven_after_tp1": true,
            "breakeven_buffer_pips": 2.0
        }
    },
    
    "database": {
        "path": "data/zepix_price_action.db",
        "table_name": "price_action_5m_trades"
    }
}
```

---

## 📊 V6 15M INTRADAY PLUGIN CONFIG

**File:** `src/logic_plugins/price_action_15m/config.json`

```json
{
    "plugin_id": "price_action_15m",
    "version": "1.0.0",
    "enabled": true,
    "shadow_mode": false,
    
    "metadata": {
        "name": "V6 15M Intraday",
        "description": "15-minute intraday with Order A only",
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
            "require_market_state_match": true,
            "require_pulse_alignment": true
        },
        
        "order_configuration": {
            "use_order_a": true,
            "use_order_b": false,
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
            "enabled": true,
            "require_pulse_alignment": true,
            "check_bull_bear_ratio": true
        }
    },
    
    "database": {
        "path": "data/zepix_price_action.db",
        "table_name": "price_action_15m_trades"
    }
}
```

---

## ⏰ V6 1H SWING PLUGIN CONFIG

**File:** `src/logic_plugins/price_action_1h/config.json`

```json
{
    "plugin_id": "price_action_1h",
    "version": "1.0.0",
    "enabled": true,
    "shadow_mode": false,
    
    "metadata": {
        "name": "V6 1H Swing",
        "description": "1-hour swing trades with Order A only",
        "category": "V6_PRICE_ACTION",
        "timeframe": "1h"
    },
    
    "settings": {
        "supported_symbols": ["XAUUSD"],
        "supported_timeframes": ["60"],
        "order_routing": "ORDER_A_ONLY",
        
        "entry_conditions": {
            "confidence_threshold": 60,
            "require_4h_alignment": true,
            "require_1d_alignment": true,
            "higher_tf_weight": 2.0
        },
        
        "order_configuration": {
            "use_order_a": true,
            "use_order_b": false,
            "target_level": "TP2",
            "extended_tp_enabled": true
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
            "enabled": false,
            "use_traditional_tf_trends": true
        }
    },
    
    "database": {
        "path": "data/zepix_price_action.db",
        "table_name": "price_action_1h_trades"
    }
}
```

---

## 🔐 ENVIRONMENT VARIABLES

**File:** `.env` (MUST be in `.gitignore`)

```bash
# Multi-Telegram System
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
```

---

## ✅ SHADOW MODE CONFIGURATION

**Purpose:** Test plugins with real signals but WITHOUT real trades

```json
{
    "plugins": {
        "combined_v3": {
            "enabled": true,
            "shadow_mode": true,
            "shadow_settings": {
                "log_all_signals": true,
                "simulate_order_placement": true,
                "track_hypothetical_pnl": true,
                "shadow_duration_hours": 72
            }
        }
    }
}
```

---

## 🎯 COMPLETION CHECKLIST

- [x] Main bot config with 5 plugins
- [x] V3 Combined Logic config (12 signals, dual orders, MTF)
- [x] V6 1M config (ORDER B ONLY)
- [x] V6 5M config (DUAL ORDERS)
- [x] V6 15M config (ORDER A ONLY)
- [x] V6 1H config (ORDER A ONLY)
- [x] Environment variables documented
- [x] Shadow mode configuration
- [x] All configs production-ready

**Status:** READY FOR PHASE 4 & 7 IMPLEMENTATION
