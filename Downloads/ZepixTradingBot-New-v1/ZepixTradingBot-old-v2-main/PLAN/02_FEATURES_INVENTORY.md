# 02 - Complete Features Inventory

## 📋 All Features क्रिया विवरण

This document lists **every feature** with purpose, workflow, and implementation details.

---

## Feature Categories

1. **Core Trading Features** - 8 features
2. **Risk Management** - 7 features  
3. **Re-entry Systems** - 3 systems
4. **Profit Booking** - 5-level chain system
5. **Autonomous Features** - 6 automated systems
6. **Menu & Control** - Telegram interface
7. **Monitoring & Diagnostics** - 8 tools

**Total: 35+ distinct features**

---

## 1. Core Trading Features

### 1.1 Dual Order System
**Purpose**: Execute two orders simultaneously for different purposes

**Components**:
- **Order A** (TP Trail): Uses existing SL system, aims for big moves
- **Order B** (Profit Booking): Fixed $10 SL, profit chain participation

**Why**: Balances safety (Order A with flexible SL) and profit maximization (Order B chains)

**Workflow**:
```
Entry Signal Received
    ↓
Dual Order Manager validates
    ↓
Create Order A:
    - SL: Based on SL-1/SL-2 system
    - TP: 1.5x SL distance
    ↓
Create Order B:
    - SL: Fixed $10
    - TP: Fixed $7
    ↓
Both orders placed simultaneously
    ↓
Independent management
```

**Configuration**: `config.json → dual_order_config`

---

### 1.2 Multi-Timeframe Analysis
**Purpose**: Filter entries based on alignment across timeframes

**Logics**:
- **LOGIC1**: 15-minute timeframe
- **LOGIC2**: 1-hour timeframe
- **LOGIC3**: Daily timeframe

**Why**: Higher timeframe confirmation reduces false signals

**Workflow**:
```
TradingView Alert (e.g., 15m LOGIC1 buy)
    ↓
Check trend alignment:
    - 15m must be bullish
    - 1h should support
    - 1d should support
    ↓
[ALIGNED] → Allow entry
[NOT ALIGNED] → Reject with notification
```

**Configuration**: `/menu_timeframe` or `/view_logic_settings`

---

### 1.3 Trend Management
**Purpose**: Manual control over trend direction per symbol/timeframe

**Modes**:
- **AUTO**: Use TradingView bias alerts
- **MANUAL**: Locked by user (ignores incoming trends)
- **BULLISH/BEARISH/NEUTRAL**: Explicit direction

**Why**: Override automatic trends when market analysis differs

**Workflow**:
```
User sets: /set_trend EURUSD 1h bullish
    ↓
Stored in timeframe_trends.json
    ↓
Future signals check this trend
    ↓
Only bullish signals allowed for EURUSD 1h
```

**Commands**: `/trend_matrix`, `/set_trend`, `/set_auto`

---

### 1.4 Symbol Compatibility
**Purpose**: Support 10 major currency pairs and gold

**Supported Symbols**:
- XAUUSD (Gold)
- EURUSD, GBPUSD, USDJPY, USDCAD
- AUDUSD, NZDUSD
- EURJPY, GBPJPY, AUDJPY

**Why**: Focus on liquid, actively traded pairs

**Implementation**: Symbol mapping in `src/utils/pip_calculator.py`

---

### 1.5 RR Ratio Enforcement
**Purpose**: Ensure minimum 1:1.5 risk-reward on all trades

**Validation**:
```python
TP_distance = abs(TP - entry)
SL_distance = abs(entry - SL)

if TP_distance < (SL_distance * 1.5):
    REJECT_TRADE
```

**Why**: Positive expectancy even with 50% win rate

---

### 1.6 Simulation Mode
**Purpose**: Test bot without real money

**Features**:
- Runs without MT5 connection
- Simulates order execution
- Logs all actions
- Safe for testing new strategies

**Usage**: `/simulation_mode on`

---

### 1.7 Webhook Integration
**Purpose**: Receive TradingView alerts

**Endpoint**: `POST /webhook`

**Alert Types**:
1. **Entry** - buy/sell signals
2. **Exit** - close position signals
3. **Trend** - bull/bear trend updates
4. **Bias** - market bias changes
5. **Reversal** - reversal signals

**Alert Format**:
```json
{
  "type": "entry",
  "symbol": "EURUSD",
  "signal": "buy",
  "tf": "1h",
  "price": 1.1000,
  "strategy": "ZepixPremium"
}
```

---

### 1.8 Trading Pause/Resume
**Purpose**: Manual control to stop/start trading

**Commands**: `/pause`, `/resume`

**Behavior**:
- **Paused**: No new orders, existing positions remain
- **Resumed**: Normal operation

**Auto-pause triggers**:
- Daily loss cap exceeded
- Lifetime loss cap exceeded
- Manual pause command

---

## 2. Risk Management Features

### 2.1 Tier-Based Lot Sizing
**Purpose**: Scale lot size with account balance

**Tiers**:
| Balance Tier | Lot Size | Daily Cap | Lifetime Cap |
|--------------|----------|-----------|--------------|
| $5,000 | 0.05 | $50 | $200 |
| $10,000 | 0.10 | $100 | $500 |
| $25,000 | 0.20 | $200 | $1,000 |
| $50,000 | 0.50 | $500 | $2,000 |
| $100,000 | 1.00 | $1,000 | $5,000 |

**Why**: Proper capital management prevents over-exposure

**Configuration**: `/switch_tier 10000`

---

### 2.2 Daily Loss Cap
**Purpose**: Limit losses per day

**Workflow**:
```
Every trade closure
    ↓
Check if loss
    ↓
Add to daily_loss counter
    ↓
If daily_loss >= daily_cap:
    - Auto-pause trading
    - Send Telegram alert
    - Log event
```

**Reset**: Automatically at midnight (UTC) or `/clear_daily_loss`

---

### 2.3 Lifetime Loss Cap
**Purpose**: Absolute maximum loss limit

**Workflow**: Similar to daily cap but never auto-resets

**Reset**: Manual only via `/clear_loss_data` (use carefully!)

---

### 2.4 SL System (SL-1 & SL-2)
**Purpose**: Two different SL calculation methods

**SL-1 (Fixed)**:
- Based on symbol-specific percentage
- E.g., XAUUSD: 20% of entry price
- Consistent and predictable

**SL-2 (Dynamic)**:
- Based on market volatility
- Adapts to current conditions
- More complex logic

**Configuration**: `/sl_system_change sl-1`

---

### 2.5 Symbol-Specific SL
**Purpose**: Custom SL percent per symbol

**Example**:
```
XAUUSD: 20% (highly volatile)
EURUSD: 10% (less volatile)
```

**Commands**: `/set_symbol_sl XAUUSD 20`

---

### 2.6 Margin Check
**Purpose**: Prevent insufficient margin errors

**Validation**:
```
Before placing order:
    ↓
Calculate required margin
    ↓
Check available margin
    ↓
If insufficient → Reject order
```

---

### 2.7 Max Lot Validation
**Purpose**: Prevent excessive lot sizes

**Limits**:
- Minimum: 0.01 lot
- Maximum: 10.0 lots (configurable)

---

## 3. Re-entry Systems

### 3.1 SL Hunt Recovery
**Purpose**: Re-enter after SL hit with recovery

**Logic**:
```
Trade hits SL
    ↓
Price Monitor watches
    ↓
Price recovers +1 pip beyond SL
    ↓
Create re-entry order:
    - Same direction
    - SL reduced 30%
    - Max 1 attempt
```

**Why**: Market often reverses after stop hunting

**Configuration**: `/sl_hunt on`

---

### 3.2 TP Continuation
**Purpose**: Re-enter after TP for extended moves

**Logic**:
```
Trade hits TP
    ↓
Price continues +2 pips
    ↓
Create continuation order:
    - Same direction
    - SL reduced 50%
    - TP same distance
    ↓
Max 5 levels total
```

**Why**: Trend often continues after partial booking

**Configuration**: `/tp_system on`

---

### 3.3 Exit Continuation
**Purpose**: Re-enter after exit signal

**Logic**:
```
Exit signal received (from TradingView)
    ↓
Close existing position
    ↓
Wait for +2 pip gap
    ↓
If trend still favorable:
    - Create re-entry order
    - SL reduced 30%
```

**Why**: Exit signals may be temporary; trend may resume

**Configuration**: `/exit_continuation on`

---

### 3.4 Re-entry Parameters
All configurable via commands:
- **Monitor Interval**: How often to check price (30s default)
- **SL Offset**: Recovery amount (+1 pip default)
- **Cooldown**: Wait time between attempts (30s default)
- **Recovery Window**: Max time to wait (5 min default)
- **Max Levels**: Maximum re-entry levels (2 enforced)
- **SL Reduction**: Percent reduction per level (30% default)

**Configuration**: `/reentry_config`

---

## 4. Profit Booking System

### 4.1 5-Level Profit Chain
**Purpose**: Pyramid profits with progressive lot sizes

**Chain Structure**:
```
Level 1: 1 lot × $7 = $7
Level 2: 2 lots × $7 = $14  
Level 3: 4 lots × $7 = $28
Level 4: 8 lots × $7 = $56
Level 5: 16 lots × $7 = $112

Total if all hit: $217 profit
```

**Why**: Exponential profit growth on winning trades

---

### 4.2 Chain Progression Logic
**Workflow**:
```
Order B hits TP ($7 profit)
    ↓
ProfitBookingManager triggered
    ↓
Check current level
    ↓
If level < 5:
    - Create next level order
    - Lot size = 2^level
    - Same symbol/direction
    - Store chain_id in database
```

**Database**: `profit_chains` table tracks active chains

---

### 4.3 Chain Recovery
**Purpose**: Resume chains after bot restart

**Logic**:
```
Bot starts
    ↓
Query database for active chains
    ↓
Check if positions still exist in MT5
    ↓
Resume monitoring for TP hits
```

---

### 4.4 Chain Multiplier Presets
**Purpose**: Different risk profiles

**Presets**:
- **Standard**: 1,2,4,8,16 (default)
- **Conservative**: 1,1.5,2,3,4
- **Aggressive**: 1,3,6,12,24
- **Linear**: 1,2,3,4,5
- **Fibonacci**: 1,1,2,3,5

**Configuration**: `/set_chain_multipliers aggressive`

---

### 4.5 Profit Chain Management
**Commands**:
- `/profit_chains` - List all active chains
- `/stop_profit_chain CHAIN_ID` - Stop specific chain
- `/stop_all_profit_chains` - Stop all chains
- `/profit_stats` - Performance metrics

---

## 5. Autonomous Features

### 5.1 Autonomous System Manager
**Purpose**: Orchestrate all automated re-entry logic

**Responsibilities**:
- Monitor all positions
- Trigger re-entry systems
- Coordinate timing
- Prevent conflicts

**Configuration**: `/autonomous_mode on`

---

### 5.2 Profit Protection
**Purpose**: Dynamic SL adjustment to lock in profits

**Strategies**:
- **Conservative**: Move SL slowly
- **Balanced**: Moderate adjustment
- **Aggressive**: Quick profit locking

**Logic**:
```
Trade in profit
    ↓
Check multiplier (e.g., 6x)
    ↓
If profit >= (initial_risk × 6):
    - Move SL to breakeven + buffer
    - Lock in minimum profit
```

**Configuration**: Via Fine-Tune menu

---

### 5.3 SL Reduction Optimizer
**Purpose**: Progressive SL reduction on re-entries

**Strategy**:
```
Level 1: 100% of original SL
Level 2: 70% of original SL (30% reduction)
Level 3: 49% of original SL (cumulative)
```

**Why**: Risk decreases as confidence increases (already recovered once)

---

### 5.4 Reverse Shield v3.0
**Purpose**: Protect against trend reversals

**Detection**:
- Reversal signals from TradingView
- Opposite bias alerts
- Exit signals

**Action**:
```
Reversal detected
    ↓
Check if position exists
    ↓
If yes:
    - Close position
    - Notify user
    - Log reason
```

---

### 5.5 Recovery Window Monitor
**Purpose**: Manage time-based re-entry windows

**Logic**:
```
Re-entry opportunity created
    ↓
Start 5-minute timer
    ↓
Monitor price within window
    ↓
If conditions met → Execute
If window expires → Cancel
```

---

### 5.6 Price Monitor Service
**Purpose**: Real-time price tracking

**Frequency**: 30-second intervals

**Monitors**:
- Active positions
- Potential re-entry setups
- Chain progression opportunities
- Reversal conditions

**Implementation**: Background async task

---

## 6. Menu & Control System

### 6.1 Telegram Bot Interface
**Purpose**: Full bot control via mobile

**Features**:
- 78 commands
- Interactive buttons (Reply Keyboard)
- Real-time notifications
- Menu navigation

---

### 6.2 Reply Keyboard Menu
**Purpose**: Zero-typing interface

**Layout** (2-column grid):
```
📊 Dashboard      ⏸️ Pause/Resume
📈 Active Trades  💰 Performance
💱 Trading        ⏱️ Timeframe
🔄 Re-entry      📍 Trends
🛡️ Risk          ⚙️ SL System
📦 Orders        📈 Profit
⚙️ Settings      🔬 Diagnostics
⚡ Fine-Tune     🆘 Help
🔄 Refresh       🚨 PANIC CLOSE
```

**Behavior**:
- `one_time_keyboard=True` → Auto-hides after click
- 4-dot button shows when hidden
- Click 4-dot → Menu reappears

---

### 6.3 Inline Keyboard Menus
**Purpose**: Sub-menus for complex operations

**Examples**:
- Risk tier selection (buttons for 5K/10K/25K/50K/100K)
- Trend setting (symbol → timeframe → trend)
- SL system selection (SL-1/SL-2)

---

### 6.4 Parameter Collection System
**Purpose**: Multi-step command input

**Flow**:
```
User clicks: "Set Trend"
    ↓
Bot: "Select Symbol" (buttons)
    ↓
User: EURUSD
    ↓
Bot: "Select Timeframe" (buttons)
    ↓
User: 1h
    ↓
Bot: "Select Trend" (buttons)
    ↓
User: Bullish
    ↓
Confirmation screen
    ↓
User: Confirm
    ↓
Execute command
```

---

### 6.5 Notifications
**Purpose**: Real-time trade updates

**Notification Types**:
- Entry executed
- Position closed (TP/SL/Manual)
- Re-entry triggered
- Chain progression
- Risk cap alerts
- Error notifications

**Format**: Formatted messages with emojis

---

## 7. Monitoring & Diagnostic Tools

### 7.1 Health Status
**Purpose**: System component health check

**Checks**:
- MT5 connection
- Telegram connectivity
- Database access
- Background services running

**Command**: `/health_status`

---

### 7.2 Log Level Control
**Purpose**: Adjust logging verbosity

**Levels**:
- **DEBUG**: All details (for troubleshooting)
- **INFO**: Standard operation (production default)
- **WARNING**: Only warnings and errors
- **ERROR**: Errors only

**Command**: `/set_log_level DEBUG`

---

### 7.3 Log Export
**Purpose**: Share logs with developers

**Variants**:
- `/export_logs 500` - Last 500 lines
- `/export_current_session` - Today's logs
- `/export_by_date 2025-12-25` - Specific date
- `/export_date_range start end` - Date range

**Output**: .log file sent via Telegram

---

### 7.4 Error Tracking
**Purpose**: Monitor and analyze errors

**Command**: `/error_stats`

**Returns**: Count by error type

---

### 7.5 Trading Debug Mode
**Purpose**: Verbose trade execution logs

**When**: Debugging order placement issues

**Command**: `/trading_debug_mode on`

**Caution**: Generates large log files

---

### 7.6 System Resources
**Purpose**: Monitor server health

**Command**: `/system_resources`

**Returns**:
- CPU usage
- Memory usage
- Disk space
- Network status

---

### 7.7 Performance Reports
**Purpose**: Analyze trading results

**Reports**:
- Overall performance
- By symbol
- By strategy (LOGIC1/2/3)
- By session
- Profit chain statistics

**Commands**: `/performance`, `/pair_report`, `/strategy_report`

---

### 7.8 Session Management
**Purpose**: Track trading sessions

**Features**:
- Auto-create new session daily
- Link all trades to session
- Session-based P/L calculation
-  Historical session review

**Commands**: `/sessions`, `/session_report SES_ID`

---

## Feature Implementation Files

| Feature | Primary File |
|---------|-------------|
| Dual Orders | `src/managers/dual_order_manager.py` |
| Trading Engine | `src/core/trading_engine.py` |
| Risk Management | `src/managers/risk_manager.py` |
| SL Hunt Re-entry| `src/managers/reentry_manager.py` |
| Profit Booking | `src/managers/profit_booking_manager.py` |
| Trend Management | `src/managers/timeframe_trend_manager.py` |
| Autonomous System | `src/managers/autonomous_system_manager.py` |
| Profit Protection | `src/managers/profit_protection_manager.py` |
| SL Reduction | `src/managers/sl_reduction_optimizer.py` |
| Reverse Shield | `src/managers/reverse_shield_manager.py` |
| Price Monitor | `src/services/price_monitor_service.py` |
| Telegram Bot |`src/clients/telegram_bot.py` |
| Menu System | `src/menu/menu_manager.py` |
| Alert Processing | `src/processors/alert_processor.py` |
| MT5 Client | `src/clients/mt5_client.py` |

---

**Next**: Read [10_WORKFLOWS.md](10_WORKFLOWS.md) for end-to-end process flows
