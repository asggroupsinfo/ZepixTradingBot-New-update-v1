# 09 - Configuration Reference

## ⚙️ Complete Configuration Guide

---

## 1. Environment Variables (.env)

**File**: `.env` (project root)

```bash
# Telegram Configuration
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321

# MT5 Configuration
MT5_LOGIN=308646228
MT5_PASSWORD=YourPassword123
MT5_SERVER=XMGlobal-MT5 6

# Optional
LOG_LEVEL=INFO
DEBUG_MODE=false
```

**Security**: `.env` is in `.gitignore` - never commit to git!

---

## 2. Main Configuration (config.json)

**File**: `config/config.json`

### Structure Overview
```json
{
  "rr_ratio": 1.5,
  "simulate_orders": false,
  "dual_order_config": {...},
  "profit_booking_config": {...},
  "re_entry_config": {...},
  "sl_systems": {...},
  "risk_tiers": {...},
  "timeframe_config": {...}
}
```

---

### Global Settings
```json
{
  "rr_ratio": 1.5,
  "simulate_orders": false,
  "max_concurrent_trades": 10,
  "bot_magic_number": 234000,
  "telegram_notifications_enabled": true,
  "auto_pause_on_error": true
}
```

---

### Dual Order Configuration
```json
{
  "dual_order_config": {
    "enabled": true,
    "order_a": {
      "name": "TP Trail",
      "purpose": "Main trend following",
      "sl_system": "active",
      "lots": "tier_based"
    },
    "order_b": {
      "name": "Profit Booking",
      "purpose": "Chain progression",
      "sl_fixed_amount": 10.0,
      "tp_target": 7.0,
      "lots": "tier_based"
    }
  }
}
```

---

### Profit Booking Configuration
```json
{
  "profit_booking_config": {
    "enabled": true,
    "max_levels": 5,
    "profit_target_per_level": 7.0,
    "base_lot_size": "tier_based",
    
    "multiplier_presets": {
      "standard": [1, 2, 4, 8, 16],
      "conservative": [1, 1.5, 2, 3, 4],
      "aggressive": [1, 3, 6, 12, 24],
      "linear": [1, 2, 3, 4, 5],
      "fibonacci": [1, 1, 2, 3, 5]
    },
    
    "active_preset": "standard",
    
    "auto_stop_on_loss": true,
    "chain_recovery_enabled": true
  }
}
```

---

### Re-entry Configuration
```json
{
  "re_entry_config": {
    "sl_hunt": {
      "enabled": true,
      "max_attempts": 1,
      "recovery_offset_pips": 1.0,
      "recovery_window_minutes": 5,
      "sl_reduction_percent": 30.0
    },
    
    "tp_continuation": {
      "enabled": true,
      "max_levels": 5,
      "gap_requirement_pips": 2.0,
      "cooldown_seconds": 30,
      "sl_reduction_percent": 50.0
    },
    
    "exit_continuation": {
      "enabled": true,
      "gap_requirement_pips": 2.0,
      "max_attempts": 2,
      "sl_reduction_percent": 30.0
    },
    
    "global_settings": {
      "monitor_interval_seconds": 30,
      "max_reentry_level": 2,
      "enforce_level_cap": true
    }
  }
}
```

---

### SL Systems Configuration
```json
{
  "sl_systems": {
    "active_system": "sl-1",
    
    "sl-1": {
      "name": "Fixed Percentage SL",
      "type": "fixed",
      "default_percent": 15.0,
      
      "symbol_specific": {
        "XAUUSD": 20.0,
        "EURUSD": 10.0,
        "GBPUSD": 12.0,
        "USDJPY": 10.0,
        "USDCAD": 10.0,
        "AUDUSD": 10.0,
        "NZDUSD": 12.0,
        "EURJPY": 12.0,
        "GBPJPY": 15.0,
        "AUDJPY": 15.0
      }
    },
    
    "sl-2": {
      "name": "Dynamic ATR-based SL",
      "type": "dynamic",
      "atr_periods": 14,
      "atr_multiplier": 1.5,
      "min_sl_percent": 8.0,
      "max_sl_percent": 25.0
    }
  }
}
```

---

### Risk Tiers Configuration
```json
{
  "risk_tiers": {
    "5000": {
      "balance_threshold": 5000,
      "lot_size": 0.05,
      "daily_loss_cap": 50.0,
      "lifetime_loss_cap": 200.0,
      "max_concurrent_trades": 5
    },
    
    "10000": {
      "balance_threshold": 10000,
      "lot_size": 0.10,
      "daily_loss_cap": 100.0,
      "lifetime_loss_cap": 500.0,
      "max_concurrent_trades": 10
    },
    
    "25000": {
      "balance_threshold": 25000,
      "lot_size": 0.20,
      "daily_loss_cap": 200.0,
      "lifetime_loss_cap": 1000.0,
      "max_concurrent_trades": 15
    },
    
    "50000": {
      "balance_threshold": 50000,
      "lot_size": 0.50,
      "daily_loss_cap": 500.0,
      "lifetime_loss_cap": 2000.0,
      "max_concurrent_trades": 20
    },
    
    "100000": {
      "balance_threshold": 100000,
      "lot_size": 1.00,
      "daily_loss_cap": 1000.0,
      "lifetime_loss_cap": 5000.0,
      "max_concurrent_trades": 30
    },
    
    "default_tier": "10000"
  }
}
```

---

### Timeframe Configuration
```json
{
  "timeframe_config": {
    "LOGIC1": {
      "timeframe": "15m",
      "enabled": true,
      "lot_multiplier": 1.0,
      "sl_multiplier": 1.0,
      "recovery_window_minutes": 5
    },
    
    "LOGIC2": {
      "timeframe": "1h",
      "enabled": true,
      "lot_multiplier": 1.0,
      "sl_multiplier": 1.0,
      "recovery_window_minutes": 10
    },
    
    "LOGIC3": {
      "timeframe": "1d",
      "enabled": true,
      "lot_multiplier": 1.0,
      "sl_multiplier": 1.0,
      "recovery_window_minutes": 30
    }
  }
}
```

---

## 3. Trend Configuration (timeframe_trends.json)

**File**: `config/timeframe_trends.json`

```json
{
  "EURUSD": {
    "15m": {
      "trend": "BULLISH",
      "mode": "AUTO",
      "last_updated": "2025-12-26T03:00:00"
    },
    "1h": {
      "trend": "BULLISH",
      "mode": "MANUAL",
      "locked_by": "user",
      "last_updated": "2025-12-25T10:00:00"
    },
    "1d": {
      "trend": "BULLISH",
      "mode": "AUTO",
      "last_updated": "2025-12-26T00:00:00"
    }
  },
  
  "XAUUSD": {
    "15m": {
      "trend": "NEUTRAL",
      "mode": "AUTO"
    },
    "1h": {
      "trend": "BEARISH",
      "mode": "AUTO"
    },
    "1d": {
      "trend": "BULLISH",
      "mode": "AUTO"
    }
  }
}
```

**Modes**:
- `AUTO`: Accept TradingView trend updates
- `MANUAL`: Locked, ignore incoming trends

---

## 4. Log Level Configuration

**File**: `config/log_level.txt`

```
INFO
```

**Valid Values**: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Change via**:
- Command: `/set_log_level DEBUG`
- Direct edit: `echo DEBUG > config/log_level.txt`

---

## 5. Trading Debug Mode

**File**: `config/trading_debug.txt`

```
false
```

**Valid Values**: `true`, `false`

**Purpose**: Enable verbose trading operation logs

---

## 6. Fine-Tune Configurations

### Profit Protection
```json
{
  "profit_protection": {
    "enabled": true,
    "mode": "balanced",
    
    "modes": {
      "conservative": {
        "multiplier": 4.0,
        "min_threshold": 30.0
      },
      "balanced": {
        "multiplier": 6.0,
        "min_threshold": 20.0
      },
      "aggressive": {
        "multiplier": 8.0,
        "min_threshold": 10.0
      }
    },
    
    "order_a_enabled": true,
    "order_b_enabled": true
  }
}
```

### SL Reduction
```json
{
  "sl_reduction": {
    "enabled": true,
    "strategy": "balanced",
    
    "strategies": {
      "conservative": {
        "reduction_percent": 20.0,
        "description": "Minimal SL reduction"
      },
      "balanced": {
        "reduction_percent": 30.0,
        "description": "Recommended for most"
      },
      "aggressive": {
        "reduction_percent": 40.0,
        "description": "Maximum SL reduction"
      }
    }
  }
}
```

### Recovery Windows
```json
{
  "recovery_windows": {
    "enabled": true,
    "default_window_minutes": 5,
    "max_concurrent_windows": 10,
    "auto_cleanup_expired": true
  }
}
```

---

## 7. Configuration Loading Order

1. `.env` → Environment variables
2. `config/config.json` → Main configuration
3. `config/timeframe_trends.json` → Trend storage
4. `config/log_level.txt` → Logging level
5. `config/trading_debug.txt` → Debug mode
6. Database → Runtime settings (risk caps, etc.)

---

## 8. Configuration Management

### Via Commands
```
/set_daily_cap 100        → Updates config & database
/set_lot_size 10000 0.10  → Updates config.json
/set_log_level DEBUG      → Updates log_level.txt
/switch_tier 10000        → Updates active tier
```

### Direct File Edit
1. Edit `config/config.json`
2. Restart bot or use `/reload_config` (if implemented)

### Via Code
```python
from src.config import load_config, save_config

config = load_config()
config['rr_ratio'] = 2.0
save_config(config)
```

---

## 9. Default Values

**If config missing**, bot uses these defaults:
```python
DEFAULT_CONFIG = {
    "rr_ratio": 1.5,
    "simulate_orders": False,
    "daily_loss_cap": 100.0,
    "lifetime_loss_cap": 500.0,
    "lot_size": 0.10,
    "max_reentry_level": 2,
    "sl_hunt_enabled": True,
    "tp_continuation_enabled": True,
    "profit_booking_enabled": True
}
```

---

## Configuration Files Summary

| File | Purpose | Format |
|------|---------|--------|
| `.env` | Credentials | Key=Value |
| `config/config.json` | Main settings | JSON |
| `config/timeframe_trends.json` | Trends | JSON |
| `config/log_level.txt` | Log level | Plain text |
| `config/trading_debug.txt` | Debug mode | Plain text |
| `data/trading_bot.db` | Runtime data | SQLite |

---

**Configuration file**: `src/config.py`
