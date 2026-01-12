# Zepix Trading Bot v2.0 - Configuration & Setup Guide

## Overview

This document provides comprehensive instructions for setting up and configuring the Zepix Trading Bot v2.0. It covers environment setup, configuration files, and all configurable parameters.

## Prerequisites

### System Requirements

| Requirement | Specification |
|-------------|---------------|
| Operating System | Windows 10/11 (for MT5), Linux (for server) |
| Python Version | 3.10 or higher |
| RAM | Minimum 4GB |
| Storage | Minimum 1GB free space |
| Network | Stable internet connection |

### Required Software

1. **MetaTrader 5 Terminal**: Must be installed and running on Windows
2. **Python 3.10+**: With pip package manager
3. **Git**: For repository management

### Required Accounts

1. **MT5 Trading Account**: With broker credentials
2. **Telegram Bot**: Created via @BotFather
3. **TradingView**: For sending webhook alerts

## Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/asggroupsinfo/ZepixTradingBot-new-v13.git
cd ZepixTradingBot-new-v13
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- pydantic
- MetaTrader5
- python-telegram-bot (optional)
- requests

### Step 4: Configure Environment Variables

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Telegram Configuration
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# MT5 Configuration
MT5_LOGIN=your_mt5_account_number
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_broker_server_name
```

### Step 5: Configure Main Settings

Edit `config/config.json` with your trading parameters (see Configuration Reference below).

### Step 6: Start the Bot

```bash
# Using uvicorn directly
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# Or using the startup script (Windows)
START_BOT.bat
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Bot token from @BotFather | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | `123456789` |
| `MT5_LOGIN` | MT5 account number | `12345678` |
| `MT5_PASSWORD` | MT5 account password | `your_password` |
| `MT5_SERVER` | MT5 broker server | `XMGlobal-MT5` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |

### Getting Telegram Credentials

1. **Create Bot**:
   - Open Telegram and search for @BotFather
   - Send `/newbot` command
   - Follow prompts to name your bot
   - Copy the token provided

2. **Get Chat ID**:
   - Start a chat with your new bot
   - Send any message
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find `chat.id` in the response

### Getting MT5 Credentials

1. Open MetaTrader 5 terminal
2. Go to File → Login to Trade Account
3. Note your:
   - Login (account number)
   - Password
   - Server name (exactly as shown)

## Configuration Reference

### Main Configuration File (config/config.json)

The main configuration file contains all trading parameters organized in sections.

### Telegram Configuration

```json
{
    "telegram_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
}
```

### MT5 Configuration

```json
{
    "mt5_login": "12345678",
    "mt5_password": "your_password",
    "mt5_server": "XMGlobal-MT5",
    "mt5_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
}
```

### Symbol Mapping

Maps TradingView symbols to broker symbols:

```json
{
    "symbol_mapping": {
        "XAUUSD": "GOLD",
        "EURUSD": "EURUSD",
        "GBPUSD": "GBPUSD",
        "USDJPY": "USDJPY",
        "USDCAD": "USDCAD",
        "AUDUSD": "AUDUSD",
        "NZDUSD": "NZDUSD",
        "EURJPY": "EURJPY",
        "GBPJPY": "GBPJPY",
        "AUDJPY": "AUDJPY"
    }
}
```

### Risk Tier Configuration

```json
{
    "risk_by_account_tier": {
        "5000": {
            "daily_loss_cap": 100,
            "lifetime_loss_cap": 500,
            "base_lot": 0.05
        },
        "10000": {
            "daily_loss_cap": 200,
            "lifetime_loss_cap": 1000,
            "base_lot": 0.10
        },
        "25000": {
            "daily_loss_cap": 500,
            "lifetime_loss_cap": 2500,
            "base_lot": 0.25
        },
        "50000": {
            "daily_loss_cap": 1000,
            "lifetime_loss_cap": 5000,
            "base_lot": 0.50
        },
        "100000": {
            "daily_loss_cap": 2000,
            "lifetime_loss_cap": 10000,
            "base_lot": 1.00
        }
    }
}
```

### Fixed Lot Sizes

```json
{
    "fixed_lot_sizes": {
        "5000": 0.05,
        "10000": 0.10,
        "25000": 0.25,
        "50000": 0.50,
        "100000": 1.00
    }
}
```

### Timeframe Logic Configuration

```json
{
    "timeframe_specific_config": {
        "enabled": true,
        "LOGIC1": {
            "entry_timeframe": "5m",
            "required_alignment": ["1h", "15m"],
            "lot_multiplier": 1.25,
            "sl_multiplier": 1.0,
            "description": "5-minute scalping entries"
        },
        "LOGIC2": {
            "entry_timeframe": "15m",
            "required_alignment": ["1h", "15m"],
            "lot_multiplier": 1.0,
            "sl_multiplier": 1.5,
            "description": "15-minute intraday entries"
        },
        "LOGIC3": {
            "entry_timeframe": "1h",
            "required_alignment": ["1d", "1h"],
            "lot_multiplier": 0.625,
            "sl_multiplier": 2.5,
            "description": "1-hour swing entries"
        }
    }
}
```

### SL Systems Configuration

```json
{
    "sl_systems": {
        "active_system": "sl-1",
        "sl-1": {
            "name": "ORIGINAL",
            "description": "Standard SL system with wider stops",
            "symbols": {
                "XAUUSD": {
                    "5000": {"sl_pips": 100, "risk_dollars": 10},
                    "10000": {"sl_pips": 100, "risk_dollars": 20},
                    "25000": {"sl_pips": 100, "risk_dollars": 50},
                    "50000": {"sl_pips": 100, "risk_dollars": 100},
                    "100000": {"sl_pips": 100, "risk_dollars": 200}
                },
                "EURUSD": {
                    "5000": {"sl_pips": 30, "risk_dollars": 10},
                    "10000": {"sl_pips": 30, "risk_dollars": 20},
                    "25000": {"sl_pips": 30, "risk_dollars": 50},
                    "50000": {"sl_pips": 30, "risk_dollars": 100},
                    "100000": {"sl_pips": 30, "risk_dollars": 200}
                }
            }
        },
        "sl-2": {
            "name": "TIGHT",
            "description": "Tighter SL system for ranging markets",
            "symbols": {
                "XAUUSD": {
                    "5000": {"sl_pips": 70, "risk_dollars": 7},
                    "10000": {"sl_pips": 70, "risk_dollars": 14}
                }
            }
        }
    }
}
```

### Symbol SL Reductions

```json
{
    "symbol_sl_reductions": {
        "EURUSD": 10,
        "GBPUSD": 15,
        "USDJPY": 10,
        "USDCAD": 10,
        "AUDUSD": 10,
        "NZDUSD": 10,
        "EURJPY": 15,
        "GBPJPY": 20,
        "AUDJPY": 15
    }
}
```

### Re-entry Configuration

```json
{
    "re_entry_config": {
        "sl_hunt_recovery": {
            "enabled": true,
            "recovery_threshold": 0.7,
            "recovery_window_minutes": 60,
            "sl_reduction_percent": 20,
            "max_recovery_attempts": 3,
            "daily_recovery_limit": 10
        },
        "tp_continuation": {
            "enabled": true,
            "max_levels": 5,
            "sl_reductions": [0, 10, 25, 40, 50],
            "require_trend_alignment": true
        },
        "exit_continuation": {
            "enabled": true,
            "min_gap_pips": 20,
            "max_wait_minutes": 30
        }
    }
}
```

### Profit Booking Configuration

```json
{
    "profit_booking_config": {
        "enabled": true,
        "min_profit_per_order": 7,
        "max_level": 4,
        "multipliers": [1, 2, 4, 8, 16],
        "sl_reductions": [0, 10, 25, 40, 50],
        "profit_sl_mode": "FIXED",
        "fixed_sl_amount": 10
    }
}
```

### Autonomous System Configuration

```json
{
    "autonomous_config": {
        "enabled": true,
        "safety_limits": {
            "daily_recovery_attempts": 10,
            "daily_recovery_losses": 5,
            "max_concurrent_recoveries": 3,
            "profit_protection_multiplier": 5
        },
        "monitoring_interval_seconds": 30
    }
}
```

### Symbol Configuration

```json
{
    "symbol_config": {
        "XAUUSD": {
            "pip_size": 0.01,
            "pip_value_per_lot": 1.0,
            "volatility": "HIGH",
            "spread_typical": 30
        },
        "EURUSD": {
            "pip_size": 0.0001,
            "pip_value_per_lot": 10.0,
            "volatility": "LOW",
            "spread_typical": 1
        },
        "GBPUSD": {
            "pip_size": 0.0001,
            "pip_value_per_lot": 10.0,
            "volatility": "MEDIUM",
            "spread_typical": 2
        },
        "USDJPY": {
            "pip_size": 0.01,
            "pip_value_per_lot": 6.67,
            "volatility": "MEDIUM",
            "spread_typical": 1
        }
    }
}
```

### Logic Enable/Disable

```json
{
    "logic_enabled": {
        "LOGIC1": true,
        "LOGIC2": true,
        "LOGIC3": true
    }
}
```

### Dual Order Configuration

```json
{
    "dual_order_config": {
        "enabled": true,
        "order_a_enabled": true,
        "order_b_enabled": true,
        "order_a_type": "TP_TRAIL",
        "order_b_type": "PROFIT_TRAIL"
    }
}
```

### RR Ratio Configuration

```json
{
    "rr_ratio": {
        "default": 1.5,
        "by_symbol": {
            "XAUUSD": 1.5,
            "EURUSD": 1.5,
            "GBPUSD": 1.5
        }
    }
}
```

## Trend State File (config/timeframe_trends.json)

This file persists trend states across restarts:

```json
{
    "XAUUSD": {
        "5m": {"trend": "BULLISH", "mode": "AUTO"},
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BEARISH", "mode": "AUTO"},
        "1d": {"trend": "BULLISH", "mode": "AUTO"}
    },
    "EURUSD": {
        "5m": {"trend": "NEUTRAL", "mode": "AUTO"},
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BULLISH", "mode": "AUTO"},
        "1d": {"trend": "BEARISH", "mode": "AUTO"}
    }
}
```

**Trend Values:**
- `BULLISH`: Upward trend
- `BEARISH`: Downward trend
- `NEUTRAL`: No clear trend

**Mode Values:**
- `AUTO`: Updated automatically by incoming signals
- `MANUAL`: Locked by user, not updated by signals

## Risk Statistics File (data/stats.json)

Tracks risk statistics:

```json
{
    "daily_loss": 0.0,
    "lifetime_loss": 0.0,
    "daily_profit": 0.0,
    "total_trades": 0,
    "winning_trades": 0,
    "last_reset_date": "2025-01-01"
}
```

## TradingView Webhook Setup

### Webhook URL

Configure TradingView alerts to send to:

```
http://YOUR_SERVER_IP:8000/webhook
```

Or if using ngrok/tunnel:

```
https://your-tunnel-url.ngrok.io/webhook
```

### Alert Message Format

Configure your TradingView alert message as JSON:

**Entry Alert:**
```json
{
    "type": "entry",
    "symbol": "{{ticker}}",
    "signal": "buy",
    "tf": "15m",
    "price": {{close}},
    "strategy": "LOGIC2"
}
```

**Trend Alert:**
```json
{
    "type": "trend",
    "symbol": "{{ticker}}",
    "signal": "bull",
    "tf": "1h"
}
```

**Bias Alert:**
```json
{
    "type": "bias",
    "symbol": "{{ticker}}",
    "signal": "bull",
    "tf": "1d"
}
```

**Exit Alert:**
```json
{
    "type": "exit",
    "symbol": "{{ticker}}",
    "signal": "bear",
    "tf": "15m"
}
```

**Reversal Alert:**
```json
{
    "type": "reversal",
    "symbol": "{{ticker}}",
    "signal": "reversal_bull",
    "tf": "15m"
}
```

### Alert Conditions

| Alert Type | Signal Values | Purpose |
|------------|---------------|---------|
| entry | buy, sell | Execute trade |
| trend | bull, bear | Update timeframe trend |
| bias | bull, bear | Update long-term bias |
| exit | bull, bear | Close opposing trades |
| reversal | reversal_bull, reversal_bear | Immediate reversal exit |

## Directory Structure

```
ZepixTradingBot-new-v13/
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Environment template
├── config/
│   ├── config.json         # Main configuration
│   └── timeframe_trends.json # Trend state persistence
├── data/
│   ├── trading_bot.db      # SQLite database
│   └── stats.json          # Risk statistics
├── logs/
│   └── bot.log             # Application logs
├── src/
│   ├── main.py             # Entry point
│   └── ...                 # Source code
├── START_BOT.bat           # Windows startup script
└── requirements.txt        # Python dependencies
```

## Verification Steps

### 1. Verify Environment

```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | grep -E "fastapi|uvicorn|MetaTrader5"
```

### 2. Verify Configuration

```bash
# Check config file exists
ls config/config.json

# Validate JSON syntax
python -c "import json; json.load(open('config/config.json'))"
```

### 3. Verify MT5 Connection

```python
# Test MT5 connection
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(login=12345678, password="password", server="Server")
print(mt5.account_info())
mt5.shutdown()
```

### 4. Verify Telegram Bot

```bash
# Test bot token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

### 5. Verify Webhook

```bash
# Test webhook endpoint
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"type":"trend","symbol":"XAUUSD","signal":"bull","tf":"1h"}'
```

## Common Configuration Scenarios

### Scenario 1: Conservative Trading

```json
{
    "fixed_lot_sizes": {
        "5000": 0.03,
        "10000": 0.05,
        "25000": 0.15,
        "50000": 0.30,
        "100000": 0.60
    },
    "timeframe_specific_config": {
        "LOGIC1": {"lot_multiplier": 0.8},
        "LOGIC2": {"lot_multiplier": 0.8},
        "LOGIC3": {"lot_multiplier": 0.5}
    }
}
```

### Scenario 2: Aggressive Trading

```json
{
    "fixed_lot_sizes": {
        "5000": 0.08,
        "10000": 0.15,
        "25000": 0.35,
        "50000": 0.70,
        "100000": 1.50
    },
    "timeframe_specific_config": {
        "LOGIC1": {"lot_multiplier": 1.5},
        "LOGIC2": {"lot_multiplier": 1.25},
        "LOGIC3": {"lot_multiplier": 0.8}
    }
}
```

### Scenario 3: Gold Only

```json
{
    "symbol_mapping": {
        "XAUUSD": "GOLD"
    },
    "logic_enabled": {
        "LOGIC1": true,
        "LOGIC2": true,
        "LOGIC3": false
    }
}
```

### Scenario 4: Disable Profit Booking

```json
{
    "profit_booking_config": {
        "enabled": false
    },
    "dual_order_config": {
        "order_b_enabled": false
    }
}
```

## Troubleshooting Configuration

### Issue: Bot Not Receiving Alerts

1. Check webhook URL is accessible
2. Verify TradingView alert format
3. Check firewall settings
4. Review logs for errors

### Issue: MT5 Connection Failed

1. Verify MT5 terminal is running
2. Check login credentials
3. Verify server name exactly matches
4. Check MT5 path in config

### Issue: Telegram Not Working

1. Verify bot token is correct
2. Check chat ID is correct
3. Ensure bot is started in chat
4. Check network connectivity

### Issue: Trades Not Executing

1. Check logic is enabled
2. Verify trend alignment
3. Check risk limits not exceeded
4. Review alert format

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [ERROR_HANDLING_TROUBLESHOOTING.md](ERROR_HANDLING_TROUBLESHOOTING.md) - Troubleshooting guide
- [DEPLOYMENT_MAINTENANCE.md](DEPLOYMENT_MAINTENANCE.md) - Deployment guide
