# Zepix Trading Bot v2.0 - Features Specification

## Overview

This document provides a comprehensive catalog of all features implemented in the Zepix Trading Bot v2.0. Each feature is described with its purpose, configuration options, and operational behavior.

## Feature 1: V3 Integration System

## 1.1 Core V3 Architecture

**Production Status**: Fully enabled (`v3_integration.enabled: true`)

### Multi-Timeframe Pillar Analysis

V3 system analyzes signals across 4 strategic timeframes:
- **15m**: Short-term momentum shifts
- **1h**: Intraday trend confirmation
- **4h**: Swing structure validation
- **1d**: Major trend alignment

**Configuration**: `v3_integration.mtf_pillars_only: ["15m", "1h", "4h", "1d"]`

### Consensus Scoring System

**Minimum Consensus Score**: 5 (configurable)

Scoring logic evaluates:
- Cross-timeframe signal alignment
- Trend coherence across pillars
- Momentum convergence
- Support/resistance confluence

**High-conviction signals** (score ≥ 5) receive priority routing.

### Signal Classification

**Aggressive Reversal Signals** (high risk, high reward):
- `Liquidity_Trap_Reversal`: Counter-trend liquidity grabs
- `Golden_Pocket_Flip`: Fibonacci golden zone reversals
- `Screener_Full_Bullish`: All-timeframe bullish alignment
- `Screener_Full_Bearish`: All-timeframe bearish alignment

**Conservative Exit Signals** (capital preservation):
- `Bullish_Exit`: Momentum exhaustion on longs
- `Bearish_Exit`: Momentum exhaustion on shorts

### Dynamic Signal Routing

V3 routes signals to optimal logic based on timeframe and type:

| Signal Source | Default Route | Override Conditions |
|---------------|---------------|---------------------|
| 5m signals | LOGIC1 (Scalping) | - |
| 15m signals | LOGIC2 (Intraday) | - |
| 1h signals | LOGIC3 (Swing) | - |
| 4h signals | LOGIC3 (Swing) | - |
| Any timeframe | LOGIC3 Override | If `Screener_Full_Bullish/Bearish` |
| Higher TF | LOGIC3 Override | If `Golden_Pocket_Flip` |

**Configuration Path**: `v3_integration.signal_routing`

### Trend Check Bypass

**Feature**: Optional bypass of standard trend alignment checks for V3 entries  
**Status**: Enabled (`bypass_trend_check_for_v3_entries: true`)

**Rationale**: High-consensus V3 signals (score ≥ 5) are sufficiently validated by multi-timeframe analysis, allowing profitable counter-trend entries.

### V3 Order Strategy Integration

V3 system powers the hybrid dual-order approach:

**Order A - V3 Smart SL**:
- SL system: SL-1.1 (logic-specific dynamic SL)
- Re-entry: Pyramid capability enabled
- Target: TP continuation for compounding

**Order B - Fixed Risk**:
- SL system: SL-2.1 (adaptive $10 max risk)
- Re-entry: Profit booking chain integration
- Target: Individual order profit threshold ($7 minimum)

---

# Feature 2: Multi-Timeframe Signal Processing System

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

### 2.1 Dual Order System

**V3 Hybrid Strategy**: Every entry signal creates two independent orders with complementary approaches:

**Order A (TP Trail - V3 Smart SL)**
- Uses V3 Smart SL system with TP continuation capability
- Can continue trading after hitting TP
- Integrates with profit booking pyramid for re-entry
- SL varies by logic (LOGIC1: 20 pips, LOGIC2: 40 pips, LOGIC3: 50 pips)

**Order B (Profit Trail - Fixed Risk)**  
- Uses adaptive SL calculated for $10 maximum risk/loss
- **SL in pips varies** based on lot size and symbol
- Dedicated to profit booking chains
- Tracks profit progression independently
- Example: 0.01 lot on XAUUSD = ~5 pip SL, 0.10 lot = ~0.5 pip SL

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

## 2.3 Multi-Timeframe Logic

The bot implements three V3-powered timeframe-based logics:

**LOGIC1 - V3 Scalping Mode (5m entries)**
- Entry timeframe: 5m
- Lot multiplier: 1.25x (aggressive)
- SL multiplier: 1.0x (standard)
- Trend requirement: 1H + 15M aligned
- V3 routing: 5m signals → LOGIC1

**LOGIC2 - V3 Intraday Mode (15m entries)**
- Entry timeframe: 15m  
- Lot multiplier: 1.0x (balanced)
- SL multiplier: 1.5x (wider)
- Trend requirement: 1H + 15M aligned
- V3 routing: 15m signals → LOGIC2

**LOGIC3 - V3 Swing Mode (1h entries)**
- Entry timeframe: 1h
- Lot multiplier: 0.625x (conservative)
- SL multiplier: 2.5x (widest)
- Trend requirement: 1D + 1H aligned
- V3 routing: 1h/4h signals, Screener Full, Golden Pocket → LOGIC3

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

## 3.1 Account Tier System

Dynamic lot sizing based on account balance (using ≥ logic):

| Account Tier | Balance Threshold (≥) | Base Lot Size | Daily Loss Limit | Lifetime Loss Limit |
|--------------|----------------------|---------------|------------------|----------------------|
| $5,000 | ≥ $5,000 | 0.01 | $100 | $500 |
| $10,000 | ≥ $10,000 | 0.02 | $200 | $1,000 |
| $25,000 | ≥ $25,000 | 0.125 | $500 | $2,500 |
| $50,000 | ≥ $50,000 | 0.50 | $1,000 | $5,000 |
| $100,000 | ≥ $100,000 | 1.00 | $2,000 | $10,000 |

**Tier Assignment**: Balance is checked sequentially from highest to lowest tier. First matching tier (where balance ≥ tier threshold) is assigned.

**Manual Lot Override Example** (from config):
- $5,000 tier manually overridden to 0.04 lots (instead of default 0.01)

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

## 5.1 Daily Loss Limits

Account tier-based daily limits:

- $5,000 tier: $100/day
- $10,000 tier: $200/day
- $25,000 tier: $500/day
- $50,000 tier: $1,000/day
- $100,000 tier: $2,000/day

**Daily Reset Time**: 03:35 UTC (configured in `daily_reset_time`)

Trading halts when limit reached, automatically resumes after daily reset.

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

### 4.1.1 Stop Loss Systems

Two SL systems available:

**SL-1.1 (Dynamic RR-based)**
- Adjusts based on risk-reward ratio
- Varies by logic:
  - LOGIC1: 20.0 pips
  - LOGIC2: 40.0 pips
  - LOGIC3: 50.0 pips
- Used for Order A (TP Trail)

**SL-2.1 (Fixed Risk)**  
- Fixed $10 maximum risk/loss (not fixed pips)
- Actual SL in pips calculated: `$10 / (lot_size × pip_value)`
- Used for Order B (Profit Trail)
- Example variations:
  - 0.01 lot XAUUSD: ~5 pips SL
  - 0.10 lot XAUUSD: ~0.5 pips SL

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

## 2.2 Profit Booking Chain System

**Individual Order Booking Strategy**: Each order in the pyramid is booked when it reaches the minimum profit threshold.

**Current Configuration** (Levels 0-2 enabled, 3-4 disabled):

| Level | Orders | Min Profit/Order | SL Reduction | Status |
|-------|--------|------------------|--------------|--------|
| 0 | 1 | $7.00 | 0% | ✅ Enabled |
| 1 | 2 | $7.00 | 10% | ✅ Enabled |
| 2 | 4 | $7.00 | 25% | ✅ Enabled |
| 3 | 8 | $7.00 | 40% | ❌ Disabled (Config) |
| 4 | 16 | $7.00 | 50% | ❌ Disabled (Config) |

**Booking Mechanism**:
- Each individual order is monitored for profit
- When any order reaches ≥ $7.00 PnL, it is immediately booked
- Remaining orders in the same level continue trading
- Level progression occurs only when ALL orders at current level are closed

**Note**: `enabled_levels` in config controls which levels are active. Levels 3-4 can be enabled if desired.

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

### 4.2.2 Recovery Windows

After SL hunt protection triggers, symbol-specific recovery windows apply:

| Symbol | Recovery Window | Rationale |
|--------|----------------|------------|
| XAUUSD | 15 minutes | High volatility, faster mean reversion |
| GBPJPY | 10 minutes | Extremely volatile pair |
| AUDJPY | 10 minutes | Yen pair volatility |
| EURUSD | 30 minutes | Major pair, moderate volatility |
| GBPUSD | 30 minutes | Major pair, moderate volatility |
| USDJPY | 30 minutes | Major pair, moderate volatility |

**Configuration Path**: `autonomous_config.sl_hunt_recovery.recovery_windows_by_symbol`

Normal trading resumes after the symbol-specific window expires, preventing revenge trading during volatile periods.

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

---

# Feature 10: Forex Session System (v4)

Advanced session management to filter trades based on market operating hours.

## 10.1 Key Capabilities
*   **Session-Based Filtering**: Blocks trades when critical sessions (Asian, London, NY) are closed.
*   **Symbol-Specific Rules**: Forex symbols follow standard market hours; Crypto symbols (BTC, ETH) are exempt (24/7).
*   **Overlap Trading**: Prioritizes high-value overlapping sessions (e.g., London+NY).
*   **Force Close**: Defines rules for closing trades at session end (e.g., before Friday market close).

## 10.2 Telegram Integration (`/session`)
*   **Dashboard**: Real-time status of all sessions.
*   **Time Config**: Edit Start/End times directly from Telegram.
*   **Toggles**: Enable/Disable specific sessions instantly.

---

# Feature 11: Voice Alert System

Audio notification system for hands-free monitoring.

## 11.1 Alert Types
*   **Trade Entry**: Speaks symbol, direction, and strategy.
*   **Session Change**: Announces when a market session opens or closes.
*   **System Error**: Critical warnings.

## 11.2 Mechanics
*   **Text-to-Speech**: Uses gTTS to generate human-like audio.
*   **Queueing**: Prevents alert floods by queuing messages (5s throttle).
*   **Telegram Voice**: Sends as native voice message (playable in background).

---

# Feature 12: Fixed Clock System

Independent, drift-corrected internal timekeeping.

## 12.1 Purpose
Eliminates reliance on server system time, which may be UTC or drifted.

## 12.2 Implementation
*   **IST Synchronization**: Always runs on Indian Standard Time (UTC+5:30).
*   **Pinned Message**: Updates a pinned message in the Telegram group every minute with the precise bot time and status.
*   **Drift Correction**: Periodically re-syncs to ensure <1s deviation.

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [WORKFLOW_PROCESSES.md](WORKFLOW_PROCESSES.md) - Detailed workflows
- [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) - Configuration guide
- [TELEGRAM_COMMAND_STRUCTURE.md](TELEGRAM_COMMAND_STRUCTURE.md) - Command reference
