# 01 - Bot Overview & Architecture

## 🎯 Purpose

**Zepix Trading Bot** एक fully automated trading system है jo MetaTrader 5 (MT5) के साथ integrate होता है और TradingView alerts के based पर trades execute करता है।

### Main Objectives
1. **Automated Trading** - Manual intervention के बिना trades execute करना
2. **Risk Management** - Strict capital protection के साथ trading करना
3. **Profit Maximization** - Multiple re-entry और profit booking strategies
4. **Real-time Monitoring** - 24/7 market monitoring और instant execution
5. **User Control** - Telegram के through complete bot control

---

## 🏗️ System Architecture

### High-Level Design

```
┌──────────────────────────────────────────────────────────────┐
│                     EXTERNAL SYSTEMS                          │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  TradingView         MetaTrader 5         Telegram            │
│  (Alerts) ─────►     (Execution) ◄─────── (Control)          │
│     │                     │                    │               │
│     │                     │                    │               │
│     ▼                     ▼                    ▼               │
├─────────────────────────────────────────────────────────────┤
│                    ZEPIX TRADING BOT                          │
├─────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐    ┌──────────────┐   ┌─────────────────┐  │
│  │   Webhook    │───▶│ Alert        │──▶│ Trading         │  │
│  │   Endpoint   │    │ Processor    │   │  Engine         │  │
│  └──────────────┘    └──────────────┘   └─────────────────┘  │
│                                                  │             │
│                            ┌────────────────────┼────────┐    │
│                            │                    │         │    │
│  ┌──────────────┐    ┌────▼─────┐    ┌────────▼──┐  ┌──▼───┐ │
│  │  Telegram    │───▶│  Risk    │    │  Profit   │  │ Re   │ │
│  │  Bot         │    │  Manager │    │  Booking  │  │Entry │ │
│  └──────────────┘    └──────────┘    └───────────┘  └──────┘ │
│                                                                │
│  ┌──────────────┐    ┌──────────────┐   ┌─────────────────┐  │
│  │  Price       │    │  Database    │   │  Config         │  │
│  │  Monitor     │    │  (SQLite)    │   │  Manager        │  │
│  └──────────────┘    └──────────────┘   └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Trading Engine** (`src/core/trading_engine.py`)
- **Purpose**: Central hub जो सभी trading operations को control करता है
- **Key Functions**:
  - Signal processing
  - Order placement
  - Position management
  - Risk validation
  - Trade coordination

#### 2. **Alert Processor** (`src/processors/alert_processor.py`)
- **Purpose**: TradingView alerts को process करना
- **Alert Types**:
  - Entry alerts (buy/sell)
  - Exit alerts
  - Trend updates
  - Bias changes
  - Reversal signals

#### 3. **MT5 Client** (`src/clients/mt5_client.py`)
- **Purpose**: MetaTrader 5 के साथ communication
- **Functions**:
  - Order execution
  - Position monitoring
  - Account information
  - Price data fetch

#### 4. **Telegram Bot** (`src/clients/telegram_bot.py`)
- **Purpose**: User interface via Telegram
- **Features**:
  - 78 commands
  - Real-time notifications
  - Interactive menus
  - Status reports

#### 5. **Managers** (`src/managers/`)
All business logic managers:
- **DualOrderManager**: Dual order system (Order A + Order B)
- **ProfitBookingManager**: 5-level profit chain management
- **RiskManager**: Loss caps और lot sizing
- **ReentryManager**: SL Hunt, TP Continuation, Exit Continuation
- **TimeframeTrendManager**: Multi-timeframe trend management
- **AutonomousSystemManager**: Automated re-entry orchestration
- **ProfitProtectionManager**: Dynamic SL adjustment
- **SLReductionOptimizer**: Progressive SL reduction
- **ReverseShieldManager**: Reversal protection

#### 6. **Services** (`src/services/`)
Background services:
- **PriceMonitorService**: Real-time price monitoring (30s intervals)
- **ReversalExitHandler**: Exit signal detection
- **AnalyticsEngine**: Performance metrics

---

## 🔄 Data Flow

### 1. **Entry Signal Flow**

```
TradingView Alert
    ↓
Webhook Endpoint (/webhook)
    ↓
Alert Processor
    ↓
Validation (symbol, trend, alignment)
    ↓
Trading Engine
    ↓
Risk Check (caps, lot size, margin)
    ↓
[PASS] → Dual Order Creation
    ├─ Order A (existing SL)
    └─ Order B (profit booking)
    ↓
MT5 Execution
    ↓
Database Storage
    ↓
Telegram Notification
```

### 2. **Re-entry Flow**

```
SL Hit / TP Hit / Exit Signal
    ↓
Price Monitor detects closure
    ↓
ReentryManager evaluation
    ↓
Check conditions:
    ├─ SL Hunt: price recovered +1 pip?
    ├─ TP Continuation: +2 pip gap?
    └─ Exit Continuation: +2 pip gap?
    ↓
[MATCH] → AutonomousSystemManager
    ↓
Create re-entry order (SL reduced 30%)
    ↓
Max levels check (≤ 2)
    ↓
MT5 Execution
```

### 3. **Profit Chain Flow**

```
Order B hits TP ($7 profit)
    ↓
ProfitBookingManager detects
    ↓
Current level check
    ↓
Create next level order:
    - Level 1: 1 lot
    - Level 2: 2 lots
    - Level 3: 4 lots
    - Level 4: 8 lots
    - Level 5: 16 lots
    ↓
MT5 Execution
    ↓
Chain progression stored
```

---

## 💾 Database Schema

### Tables

1. **trades** - All executed trades
2. **profit_chains** - Active profit booking chains
3. **reentry_history** - Re-entry tracking
4. **session_stats** - Daily statistics
5. **risk_caps** - Loss tracking
6. **configurations** - Bot settings

---

## 🔐 Security & Safety

### Built-in Protections

1. **Risk Caps**
   - Daily loss limit
   - Lifetime loss limit
   - Automatic trading pause

2. **Lot Size Limits**
   - Tier-based sizing
   - Maximum lot validation
   - Balance-based checks

3. **RR Ratio Enforcement**
   - 1:1.5 minimum enforced
   - Cannot place order without valid TP

4. **Simulation Mode**
   - Can run without MT5
   - Paper trading option
   - Safe testing environment

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| Total Commands | 78 |
| Python Files | 133 |
| Core Managers | 15+ |
| Supported Symbols | 10 (XAUUSD, majors) |
| Timeframes | 15m, 1h, 1d |
| Alert Types | 5 |
| Background Services | 3 |
| Re-entry Systems | 3 |
| Profit Levels | 5 |
| Database Tables | 10+ |

---

## 🎯 Design Philosophy

1. **Autonomous Operation** - Minimal manual intervention
2. **Safety First** - Multiple layers of protection
3. **Transparency** - Real-time Telegram updates
4. **Flexibility** - 78 commands for fine control
5. **Reliability** - Error handled gracefully
6. **Scalability** - Async architecture for performance

---

## 🔌 Integration Points

### Input
- **TradingView** - HTTP webhooks (`/webhook`)
- **Telegram** - User commands (polling)

### Output
- **MetaTrader 5** - Order execution
- **Telegram** - Notifications & reports
- **SQLite** - Data persistence
- **Logs** - File-based logging

---

**Next**: Read [02_FEATURES_INVENTORY.md](02_FEATURES_INVENTORY.md) for complete feature list
