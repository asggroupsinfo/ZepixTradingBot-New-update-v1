# Zepix Trading Bot v2.0 - Features Specification

## Overview

This document provides a comprehensive catalog of all features implemented in the Zepix Trading Bot v2.0. Each feature is described with its purpose, configuration options, and operational behavior.

## Core Trading Features

### 1. Signal Processing System

The bot processes five types of trading signals from TradingView webhooks:

**Signal Types:**

| Type | Purpose | Valid Signals | Action |
|------|---------|---------------|--------|
| `bias` | Long-term market direction | bull, bear | Updates trend state |
| `trend` | Timeframe-specific trend | bull, bear | Updates trend state |
| `entry` | Trade entry signal | buy, sell | Executes trade if aligned |
| `reversal` | Trend reversal signal | reversal_bull, reversal_bear | Closes opposing trades |
| `exit` | Exit warning signal | bull, bear | Closes opposing trades |

**Validation Rules:**
- All signals must include: type, symbol, signal, tf (timeframe)
- Timeframe must be one of: 5m, 15m, 1h, 1d
- Symbol must be in supported list (10 symbols)
- Duplicate alerts within 5-minute window are rejected

**Alert Format:**
```json
{
    "type": "entry",
    "symbol": "XAUUSD",
    "signal": "buy",
    "tf": "15m",
    "price": 2650.50,
    "strategy": "LOGIC2"
}
```

### 2. Dual Order System

Every entry signal creates two independent orders that work simultaneously.

**Order A (TP Trail):**
- Uses the standard SL system (sl-1 or sl-2)
- SL calculated based on account tier and symbol volatility
- TP calculated using RR ratio (default 1:1.5)
- Supports TP continuation after TP hit
- Supports SL hunt recovery after SL hit

**Order B (Profit Trail):**
- Uses fixed $10 SL (calculated as pip distance)
- Integrates with profit booking chain system
- $7 profit target per order
- Pyramid compounding through 5 levels

**Independence:**
- Both orders use the same lot size
- If Order A fails, Order B still executes
- No rollback mechanism - partial success is acceptable
- Each order tracked separately in database

**Configuration:**
```json
{
    "dual_order_enabled": true,
    "order_a_enabled": true,
    "order_b_enabled": true
}
```

### 3. Multi-Timeframe Logic System

Three distinct trading logics based on entry timeframe:

**LOGIC1 (5-Minute Entries):**
```
Entry Timeframe: 5m
Trend Alignment: 1H + 15M must match entry direction
Lot Multiplier: 1.25x (aggressive)
SL Multiplier: 1.0x (standard)
Use Case: Scalping, quick entries
```

**LOGIC2 (15-Minute Entries):**
```
Entry Timeframe: 15m
Trend Alignment: 1H + 15M must match entry direction
Lot Multiplier: 1.0x (balanced)
SL Multiplier: 1.5x (wider)
Use Case: Intraday trading
```

**LOGIC3 (1-Hour Entries):**
```
Entry Timeframe: 1h
Trend Alignment: 1D + 1H must match entry direction
Lot Multiplier: 0.625x (conservative)
SL Multiplier: 2.5x (widest)
Use Case: Swing trading
```

**Configuration:**
```json
{
    "timeframe_specific_config": {
        "enabled": true,
        "LOGIC1": {
            "lot_multiplier": 1.25,
            "sl_multiplier": 1.0
        },
        "LOGIC2": {
            "lot_multiplier": 1.0,
            "sl_multiplier": 1.5
        },
        "LOGIC3": {
            "lot_multiplier": 0.625,
            "sl_multiplier": 2.5
        }
    }
}
```

### 4. Trend Alignment System

Trades only execute when higher timeframe trends align with entry direction.

**Alignment Rules:**

| Logic | Entry TF | Required Alignment |
|-------|----------|-------------------|
| LOGIC1 | 5m | 1H BULLISH + 15M BULLISH for BUY |
| LOGIC2 | 15m | 1H BULLISH + 15M BULLISH for BUY |
| LOGIC3 | 1h | 1D BULLISH + 1H BULLISH for BUY |

**Trend Modes:**
- **AUTO**: Trend updated automatically by incoming signals
- **MANUAL**: Trend locked, not updated by signals (user override)

**Trend Storage:**
```json
{
    "XAUUSD": {
        "5m": {"trend": "BULLISH", "mode": "AUTO"},
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BEARISH", "mode": "MANUAL"},
        "1d": {"trend": "BULLISH", "mode": "AUTO"}
    }
}
```

## Risk Management Features

### 5. Tier-Based Risk System

Account balance determines risk parameters automatically.

**Risk Tiers:**

| Tier | Balance Range | Base Lot | Daily Loss Cap | Lifetime Loss Cap |
|------|---------------|----------|----------------|-------------------|
| $5,000 | < $7,500 | 0.05 | $100 | $500 |
| $10,000 | $7,500 - $17,500 | 0.10 | $200 | $1,000 |
| $25,000 | $17,500 - $37,500 | 0.25 | $500 | $2,500 |
| $50,000 | $37,500 - $75,000 | 0.50 | $1,000 | $5,000 |
| $100,000 | > $75,000 | 1.00 | $2,000 | $10,000 |

**Tier Detection:**
```python
def get_risk_tier(balance):
    if balance < 10000:
        return "5000"
    elif balance < 25000:
        return "10000"
    elif balance < 50000:
        return "25000"
    elif balance < 100000:
        return "50000"
    else:
        return "100000"
```

### 6. Daily and Lifetime Loss Caps

Automatic trading halt when loss limits are reached.

**Daily Loss Cap:**
- Resets at midnight (server time)
- Tracks cumulative losses for the day
- Trading paused when limit reached
- Resumes automatically next day

**Lifetime Loss Cap:**
- Cumulative loss since last reset
- Manual reset required via Telegram command
- Trading paused when limit reached
- Protects against extended drawdowns

**Smart Lot Adjustment:**
When approaching daily limit, lot size is automatically reduced:
```python
remaining_risk = daily_cap - daily_loss
if remaining_risk < normal_risk:
    adjusted_lot = calculate_lot_for_risk(remaining_risk)
```

### 7. Dual SL System

Two configurable SL calculation systems:

**sl-1 (ORIGINAL):**
- Symbol-specific SL in pips
- Tier-specific risk amounts
- Wider stops for volatile symbols

**sl-2 (TIGHT):**
- Reduced SL distances
- Lower risk per trade
- Suitable for ranging markets

**Symbol-Specific Configuration:**
```json
{
    "sl_systems": {
        "sl-1": {
            "name": "ORIGINAL",
            "description": "Standard SL system",
            "symbols": {
                "XAUUSD": {
                    "5000": {"sl_pips": 100, "risk_dollars": 10},
                    "10000": {"sl_pips": 100, "risk_dollars": 20}
                }
            }
        }
    }
}
```

**Symbol SL Reductions:**
Individual symbols can have percentage-based SL reductions:
```json
{
    "symbol_sl_reductions": {
        "EURUSD": 10,
        "GBPUSD": 15
    }
}
```

### 8. Manual Lot Override

Override automatic lot sizing for specific tiers.

**Features:**
- Per-tier override capability
- Persists across restarts
- Can be cleared to return to automatic

**Configuration:**
```json
{
    "manual_lot_overrides": {
        "5000": 0.03,
        "10000": 0.08
    }
}
```

## Profit Booking Features

### 9. Pyramid Profit Booking System

5-level compounding system for Order B trades.

**Level Structure:**

| Level | Orders | Multiplier | Profit Target | Cumulative |
|-------|--------|------------|---------------|------------|
| 0 | 1 | 1x | $7 | 1 order |
| 1 | 2 | 2x | $7 each | 3 orders |
| 2 | 4 | 4x | $7 each | 7 orders |
| 3 | 8 | 8x | $7 each | 15 orders |
| 4 | 16 | 16x | $7 each | 31 orders |

**Profit Target:**
- Fixed $7 minimum profit per order
- Individual order booking (not combined)
- Dynamic PnL monitoring every 30 seconds

**Chain Progression:**
1. Order reaches $7 profit
2. Order is closed (profit booked)
3. When all orders at level closed, progress to next level
4. Place new orders at next level (2x previous count)
5. Continue until Level 4 or chain stopped

**Configuration:**
```json
{
    "profit_booking_config": {
        "enabled": true,
        "min_profit_per_order": 7,
        "max_level": 4,
        "multipliers": [1, 2, 4, 8, 16],
        "sl_reductions": [0, 10, 25, 40, 50]
    }
}
```

### 10. Profit SL Mode

Special SL calculation for profit booking orders.

**Modes:**
- **FIXED**: Fixed $10 SL for all profit orders
- **DYNAMIC**: SL based on profit target and lot size

**Calculation:**
```python
def calculate_profit_sl(entry, direction, lot_size, risk_amount=10):
    pip_value = get_pip_value(symbol, lot_size)
    sl_pips = risk_amount / pip_value
    sl_distance = sl_pips * pip_size
    
    if direction == "buy":
        return entry - sl_distance
    else:
        return entry + sl_distance
```

## Re-entry Features

### 11. SL Hunt Recovery System

Autonomous recovery after stop-loss hit.

**Recovery Process:**
1. SL hit detected
2. Chain enters "recovery_mode"
3. Price monitored for recovery
4. If price recovers 70% toward original entry:
   - Recovery trade placed
   - Tighter SL (reduced by configured percentage)
   - Same direction as original trade

**Recovery Window:**
- Default: 60 minutes
- Configurable per symbol
- Timeout results in chain closure

**Configuration:**
```json
{
    "re_entry_config": {
        "sl_hunt_recovery": {
            "enabled": true,
            "recovery_threshold": 0.7,
            "recovery_window_minutes": 60,
            "sl_reduction_percent": 20,
            "max_recovery_attempts": 3
        }
    }
}
```

### 12. TP Continuation System

Continue trading after take-profit hit.

**Continuation Process:**
1. TP hit detected
2. Check if trend still aligned
3. If aligned, place continuation trade:
   - Same direction
   - Reduced SL (progressive reduction)
   - New TP based on RR ratio

**Progressive SL Reduction:**
| Level | SL Reduction |
|-------|--------------|
| 1 | 0% |
| 2 | 10% |
| 3 | 25% |
| 4 | 40% |
| 5 | 50% |

**Configuration:**
```json
{
    "re_entry_config": {
        "tp_continuation": {
            "enabled": true,
            "max_levels": 5,
            "sl_reductions": [0, 10, 25, 40, 50],
            "require_trend_alignment": true
        }
    }
}
```

### 13. Exit Continuation System

Re-entry after exit signal with price gap.

**Process:**
1. Exit signal closes trade
2. Monitor for price gap (pullback)
3. If price pulls back sufficiently:
   - Place re-entry trade
   - Same direction as original
   - Tighter SL

**Configuration:**
```json
{
    "re_entry_config": {
        "exit_continuation": {
            "enabled": true,
            "min_gap_pips": 20,
            "max_wait_minutes": 30
        }
    }
}
```

### 14. Profit Booking SL Hunt

Recovery system for profit booking orders.

**Features:**
- Monitors profit chain orders for SL hits
- Attempts recovery within profit chain context
- Maintains chain integrity during recovery

## Autonomous Features

### 15. Autonomous System Manager

Central coordinator for all autonomous operations.

**Managed Systems:**
- TP Continuation (autonomous)
- SL Hunt Recovery (autonomous)
- Profit Booking SL Hunt
- Exit Continuation
- Reverse Shield System

**Safety Limits:**
```json
{
    "autonomous_config": {
        "safety_limits": {
            "daily_recovery_attempts": 10,
            "daily_recovery_losses": 5,
            "max_concurrent_recoveries": 3,
            "profit_protection_multiplier": 5
        }
    }
}
```

### 16. Price Monitor Service

Background service for autonomous monitoring.

**Monitoring Interval:** 30 seconds

**Monitored Events:**
- SL hunt recovery opportunities
- TP continuation opportunities
- Exit continuation opportunities
- Profit booking target checks

### 17. Profit Protection

Skip recovery if existing profit is too valuable.

**Logic:**
```python
if total_profit > (potential_loss * protection_multiplier):
    skip_recovery()  # Protect existing profits
```

### 18. Recovery Window Monitor

Tracks recovery windows for SL hit trades.

**Features:**
- Configurable window duration
- Timeout handling
- Multi-symbol support

## Reversal and Exit Features

### 19. Reversal Exit Handler

Immediate profit booking on reversal signals.

**Trigger Conditions:**
1. Explicit reversal alert (type: reversal)
2. Opposite entry signal (BUY trade + SELL entry)
3. Trend reversal (opposite trend direction)
4. Exit appeared alert (type: exit)

**Actions:**
- Close all opposing trades
- Stop associated profit chains
- Register for exit continuation

### 20. Reverse Shield System (v3.0)

Advanced protection during recovery.

**Features:**
- Activates during SL recovery
- Places protective orders
- Monitors 70% recovery level
- Automatic shield deactivation

## Telegram Interface Features

### 21. Command System

60+ commands organized in categories.

**Categories:**
- Status/Control
- Logic Control
- Trend Management
- Risk Management
- TP System
- SL System
- Profit Booking
- Fine-Tune
- Diagnostics
- Dashboard

### 22. Interactive Menu System

Zero-typing interface with inline keyboards.

**Features:**
- Main menu with quick actions
- Category sub-menus
- Parameter selection buttons
- Confirmation dialogs
- Context-aware navigation

**Menu Structure:**
```
Main Menu
├── Quick Actions
│   ├── Dashboard
│   ├── Pause/Resume
│   ├── Trades
│   └── Performance
├── Trading
├── Timeframe
├── Performance
├── Re-entry
├── Trends
├── Risk
├── SL System
├── Orders
├── Profit
├── Settings
├── Diagnostics
└── Fine-Tune
```

### 23. Persistent Reply Keyboard

Always-visible quick access buttons.

**Layout:**
```
Row 1: [Dashboard] [Pause/Resume] [Active Trades]
Row 2: [Risk] [Re-entry] [SL System]
Row 3: [Trends] [Profit] [Help]
Row 4: [PANIC CLOSE]
```

### 24. Real-time Notifications

Telegram notifications for all trading events.

**Notification Types:**
- Trade opened
- Trade closed (TP/SL/Manual)
- Reversal exit
- Recovery attempt
- Chain progression
- Error alerts
- Daily summaries

## Configuration Features

### 25. Hot Configuration Reload

Change settings without restart.

**Reloadable Settings:**
- Risk parameters
- SL systems
- Re-entry config
- Profit booking config
- Timeframe logic

### 26. Symbol Mapping

TradingView to broker symbol translation.

**Default Mappings:**
```json
{
    "symbol_mapping": {
        "XAUUSD": "GOLD",
        "EURUSD": "EURUSD",
        "GBPUSD": "GBPUSD"
    }
}
```

### 27. Environment Variable Override

Sensitive data via environment variables.

**Supported Variables:**
- TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID
- MT5_LOGIN
- MT5_PASSWORD
- MT5_SERVER

## Monitoring Features

### 28. Health Check Endpoint

API endpoint for monitoring.

**Endpoint:** `GET /health`

**Response:**
```json
{
    "status": "healthy",
    "mt5_connected": true,
    "telegram_active": true,
    "uptime": "2h 30m"
}
```

### 29. Statistics Endpoint

Trading statistics API.

**Endpoint:** `GET /stats`

**Response:**
```json
{
    "total_trades": 150,
    "winning_trades": 95,
    "win_rate": 63.3,
    "total_pnl": 1250.50,
    "daily_pnl": 85.00
}
```

### 30. Dashboard Command

Comprehensive status overview.

**Displays:**
- Account balance
- Open positions
- Daily P&L
- Active chains
- System status
- Risk utilization

## Database Features

### 31. Trade History

Complete trade record storage.

**Stored Data:**
- Entry/exit prices
- SL/TP levels
- PnL
- Commission/swap
- Chain associations
- Logic type
- Timestamps

### 32. Chain Tracking

Re-entry and profit chain persistence.

**Tracked Chains:**
- Re-entry chains
- Profit booking chains
- Chain levels
- Chain status
- Total profit

### 33. Event Logging

Trading event history.

**Event Types:**
- SL events
- TP re-entry events
- Reversal exit events
- Profit booking events

### 34. Session Tracking

Trading session management.

**Session Data:**
- Session ID
- Symbol/direction
- Entry/exit signals
- Total P&L
- Trade count

## Logging Features

### 35. Rotating File Logs

Automatic log rotation.

**Configuration:**
- Max file size: 2MB
- Backup count: 50
- Format: timestamp + level + message

### 36. Log Levels

Configurable verbosity.

**Levels:**
- DEBUG: Detailed debugging
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Errors requiring attention
- CRITICAL: System failures

### 37. Optimized Logger

Performance-optimized logging.

**Features:**
- Batched writes
- Filtered output
- Async logging option

## Safety Features

### 38. Duplicate Alert Detection

Prevent duplicate trade execution.

**Detection:**
- 5-minute window
- Same type + symbol + timeframe + signal
- Entry alerts stored only after execution

### 39. Connection Health Monitoring

MT5 connection reliability.

**Features:**
- Periodic health checks
- Auto-reconnect on failure
- Error tracking
- Notification on disconnect

### 40. Panic Close

Emergency position closure.

**Features:**
- Closes all open positions
- Stops all active chains
- Pauses trading
- Telegram confirmation

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [WORKFLOW_PROCESSES.md](WORKFLOW_PROCESSES.md) - Detailed workflows
- [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) - Configuration guide
- [TELEGRAM_COMMAND_STRUCTURE.md](TELEGRAM_COMMAND_STRUCTURE.md) - Command reference
