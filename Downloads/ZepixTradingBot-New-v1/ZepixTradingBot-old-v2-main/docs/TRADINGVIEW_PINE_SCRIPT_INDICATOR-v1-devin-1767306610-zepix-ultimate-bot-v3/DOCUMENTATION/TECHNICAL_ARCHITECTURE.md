# Zepix Trading Bot v2.0 - Technical Architecture

## System Design Overview

The Zepix Trading Bot v2.0 follows a modular, event-driven architecture designed for reliability, maintainability, and scalability. The system is built around a central Trading Engine that orchestrates all trading operations, with specialized managers handling specific domains like risk, profit booking, and re-entry logic.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL INTERFACES                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐           │
│  │   TradingView   │     │    Telegram     │     │   MetaTrader 5  │           │
│  │    Webhooks     │     │      API        │     │     Terminal    │           │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘           │
│           │                       │                       │                     │
└───────────┼───────────────────────┼───────────────────────┼─────────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐           │
│  │    FastAPI      │     │  Telegram Bot   │     │   MT5 Client    │           │
│  │    Server       │     │    Client       │     │                 │           │
│  │  (main.py)      │     │(telegram_bot.py)│     │ (mt5_client.py) │           │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘           │
│           │                       │                       │                     │
│           └───────────────────────┼───────────────────────┘                     │
│                                   │                                             │
│                                   ▼                                             │
│                    ┌──────────────────────────────┐                             │
│                    │       TRADING ENGINE         │                             │
│                    │    (trading_engine.py)       │                             │
│                    │                              │                             │
│                    │  - Signal Processing         │                             │
│                    │  - Trade Execution           │                             │
│                    │  - Position Management       │                             │
│                    └──────────────┬───────────────┘                             │
│                                   │                                             │
└───────────────────────────────────┼─────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              BUSINESS LOGIC LAYER                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │    Risk      │  │  Dual Order  │  │   Profit     │  │   Re-entry   │        │
│  │   Manager    │  │   Manager    │  │   Booking    │  │   Manager    │        │
│  │              │  │              │  │   Manager    │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Timeframe   │  │  Autonomous  │  │   Alert      │  │   Reversal   │        │
│  │   Trend      │  │   System     │  │  Processor   │  │    Exit      │        │
│  │   Manager    │  │   Manager    │  │              │  │   Handler    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SERVICES LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────┐     ┌──────────────────────────┐                 │
│  │   Price Monitor Service  │     │    Analytics Engine      │                 │
│  │  (Background Monitoring) │     │   (Performance Stats)    │                 │
│  └──────────────────────────┘     └──────────────────────────┘                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   SQLite     │  │   Config     │  │    Stats     │  │   Trends     │        │
│  │  Database    │  │    JSON      │  │    JSON      │  │    JSON      │        │
│  │              │  │              │  │              │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Server (src/main.py)

The FastAPI server serves as the entry point for the application, handling HTTP requests and managing the application lifecycle.

**Key Responsibilities:**
- Webhook endpoint for TradingView alerts (`POST /webhook`)
- Health check endpoint (`GET /health`)
- Statistics endpoint (`GET /stats`)
- Trends endpoint (`GET /trends`)
- Application startup and shutdown lifecycle management

**Lifecycle Management:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    - Initialize Trading Engine
    - Start Telegram polling thread
    - Start background trade monitor task
    - Send startup notification
    
    yield  # Application runs
    
    # Shutdown
    - Stop Telegram polling
    - Cancel background tasks
    - Cleanup resources
```

**Logging Configuration:**
- Rotating file handler with 2MB max size
- 50 backup files retained
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Output to both file and console

### 2. Trading Engine (src/core/trading_engine.py)

The Trading Engine is the central orchestrator that coordinates all trading operations.

**Initialization:**
```python
def __init__(self, config):
    self.config = config
    self.mt5_client = MT5Client(config)
    self.telegram_bot = TelegramBot(config)
    self.db = TradeDatabase()
    self.risk_manager = RiskManager(config)
    self.pip_calculator = PipCalculator(config)
    self.profit_sl_calculator = ProfitBookingSLCalculator(config)
    self.dual_order_manager = DualOrderManager(...)
    self.profit_booking_manager = ProfitBookingManager(...)
    self.reentry_manager = ReEntryManager(...)
    self.trend_manager = TimeframeTrendManager(config)
    self.autonomous_manager = AutonomousSystemManager(...)
    self.price_monitor = PriceMonitorService(...)
    self.reversal_handler = ReversalExitHandler(...)
    self.alert_processor = AlertProcessor(...)
```

**Signal Processing Flow:**
```
process_alert(alert_data)
    │
    ├─► validate_alert()
    │
    ├─► Route by alert type:
    │   ├─► "bias" / "trend" → update_trend()
    │   ├─► "entry" → execute_trades()
    │   ├─► "reversal" → handle_reversal()
    │   └─► "exit" → handle_exit()
    │
    └─► Return result
```

**Trade Execution:**
```
execute_trades(alert)
    │
    ├─► Check risk limits (can_trade)
    │
    ├─► Check trend alignment (check_logic_alignment)
    │
    ├─► Place fresh order (place_fresh_order)
    │   ├─► Create dual orders (Order A + Order B)
    │   ├─► Create re-entry chain
    │   └─► Create profit booking chain (for Order B)
    │
    └─► Send notifications
```

### 3. MT5 Client (src/clients/mt5_client.py)

The MT5 Client provides the interface to MetaTrader 5 for all trading operations.

**Key Features:**
- Symbol mapping (TradingView → Broker symbols)
- Connection health monitoring with auto-reconnect
- Order validation before placement
- Position management (open, close, modify)

**Symbol Mapping:**
```python
SYMBOL_MAPPING = {
    "XAUUSD": "GOLD",      # XM Broker mapping
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    # ... other symbols
}
```

**Order Placement Flow:**
```
place_order(symbol, order_type, lot_size, sl, tp)
    │
    ├─► Map symbol to broker symbol
    │
    ├─► Validate order parameters
    │   ├─► Check symbol info
    │   ├─► Validate SL/TP distance
    │   └─► Check stops level
    │
    ├─► Create order request
    │
    ├─► Send to MT5
    │
    └─► Return trade_id or error
```

### 4. Telegram Bot (src/clients/telegram_bot.py)

The Telegram Bot provides the user interface for bot control and monitoring.

**Architecture:**
- Command handlers (60+ commands)
- Callback query handlers (menu navigation)
- Menu system with inline keyboards
- Message formatting (HTML/Markdown)

**Command Categories:**
```
├── Status/Control: /start, /status, /pause, /resume
├── Logic Control: /logic1_on, /logic2_on, /logic3_on, /logic_status
├── Trend Management: /set_trend, /show_trends, /trend_matrix
├── Risk Management: /lot_size_status, /set_lot_size, /view_risk_caps
├── TP System: /tp_system, /tp_report, /profit_chains
├── SL System: /sl_hunt, /sl_status, /sl_system_change
├── Profit Booking: /profit_stats, /profit_config
├── Fine-Tune: /fine_tune, /autonomous_dashboard
└── Dashboard: /dashboard
```

**Menu System:**
```
MenuManager
    │
    ├─► ContextManager (tracks user state)
    │
    ├─► CommandExecutor (executes commands)
    │
    └─► Menu Handlers
        ├─► TimeframeMenuHandler
        ├─► ReentryMenuHandler
        ├─► ProfitBookingMenuHandler
        └─► FineTuneMenuHandler
```

### 5. Risk Manager (src/managers/risk_manager.py)

The Risk Manager handles all risk-related calculations and validations.

**Key Functions:**
- `get_fixed_lot_size(balance)`: Returns lot size based on account tier
- `can_trade()`: Checks daily/lifetime loss limits
- `validate_dual_orders()`: Validates risk for dual order placement
- `record_trade_result()`: Updates loss tracking after trade close

**Tier-Based Lot Sizing:**
```python
def get_fixed_lot_size(self, account_balance):
    # Check manual override first
    if self.manual_lot_override:
        return self.manual_lot_override
    
    # Get tier from balance
    tier = self.get_risk_tier(account_balance)
    
    # Return fixed lot for tier
    return self.config["fixed_lot_sizes"][tier]
```

**Loss Tracking:**
```python
stats = {
    "daily_loss": 0.0,
    "lifetime_loss": 0.0,
    "daily_profit": 0.0,
    "total_trades": 0,
    "winning_trades": 0,
    "last_reset_date": "2025-01-01"
}
```

### 6. Dual Order Manager (src/managers/dual_order_manager.py)

Manages the dual-order system where each entry creates two independent orders.

**Order Types:**
- **Order A (TP_TRAIL)**: Uses standard SL system, supports TP continuation
- **Order B (PROFIT_TRAIL)**: Uses fixed $10 SL, integrates with profit booking chains

**Creation Flow:**
```
create_dual_orders(alert, trading_engine)
    │
    ├─► Calculate lot size (with timeframe multiplier)
    │
    ├─► Validate risk
    │
    ├─► Calculate Order A SL/TP (using PipCalculator)
    │
    ├─► Calculate Order B SL/TP (using ProfitBookingSLCalculator)
    │
    ├─► Create Trade objects
    │
    ├─► Place Order A in MT5
    │
    ├─► Place Order B in MT5 (independent - no rollback if A fails)
    │
    └─► Return results
```

### 7. Profit Booking Manager (src/managers/profit_booking_manager.py)

Manages the 5-level pyramid profit booking system.

**Pyramid Structure:**
```
Level 0: 1 order   → $7 profit target
Level 1: 2 orders  → $7 each ($14 total)
Level 2: 4 orders  → $7 each ($28 total)
Level 3: 8 orders  → $7 each ($56 total)
Level 4: 16 orders → $7 each ($112 total)
```

**Chain Lifecycle:**
```
create_profit_chain(trade)
    │
    ├─► Initialize chain at Level 0
    │
    └─► Monitor for profit target

check_profit_targets(chain, open_trades)
    │
    ├─► Calculate PnL for each order
    │
    ├─► If order reaches $7 profit:
    │   └─► book_individual_order()
    │
    └─► If all orders in level closed:
        └─► check_and_progress_chain()
            │
            ├─► Close all orders at current level
            │
            ├─► Calculate next level order count
            │
            └─► Place new orders at next level
```

### 8. Re-entry Manager (src/managers/reentry_manager.py)

Manages re-entry chains for SL recovery and TP continuation.

**Chain Types:**
- **SL Hunt Recovery**: After SL hit, monitors for price recovery
- **TP Continuation**: After TP hit, continues in same direction
- **Exit Continuation**: After exit signal, monitors for re-entry

**Recovery Logic:**
```
record_sl_hit(trade)
    │
    ├─► Create/update chain
    │
    ├─► Set chain to "recovery_mode"
    │
    └─► Start recovery window monitoring

check_sl_hunt_recovery(chain, current_price)
    │
    ├─► Calculate recovery percentage
    │   (how much price has recovered toward original entry)
    │
    ├─► If recovery >= 70%:
    │   └─► Eligible for recovery trade
    │
    └─► Return eligibility status
```

### 9. Timeframe Trend Manager (src/managers/timeframe_trend_manager.py)

Manages multi-timeframe trend tracking and alignment checking.

**Trend Storage:**
```python
trends = {
    "XAUUSD": {
        "5m": {"trend": "BULLISH", "mode": "AUTO"},
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BEARISH", "mode": "MANUAL"},
        "1d": {"trend": "BULLISH", "mode": "AUTO"}
    },
    # ... other symbols
}
```

**Alignment Logic:**
```
check_logic_alignment(symbol, direction, logic)
    │
    ├─► LOGIC1 (5m entry):
    │   └─► Requires: 1H trend + 15M trend = direction
    │
    ├─► LOGIC2 (15m entry):
    │   └─► Requires: 1H trend + 15M trend = direction
    │
    └─► LOGIC3 (1h entry):
        └─► Requires: 1D trend + 1H trend = direction
```

### 10. Autonomous System Manager (src/managers/autonomous_system_manager.py)

Coordinates all autonomous trading operations.

**Managed Systems:**
- TP Continuation (autonomous)
- SL Hunt Recovery (autonomous)
- Profit Booking SL Hunt Recovery
- Exit Continuation
- Reverse Shield System (v3.0)

**Background Monitoring:**
```
run_autonomous_checks(open_trades, trading_engine)
    │
    ├─► monitor_autonomous_tp_continuation()
    │
    ├─► monitor_profit_booking_sl_hunt()
    │
    └─► monitor_profit_booking_targets()
```

**Safety Limits:**
```python
safety_limits = {
    "daily_recovery_attempts": 10,
    "daily_recovery_losses": 5,
    "max_concurrent_recoveries": 3,
    "profit_protection_multiplier": 5
}
```

### 11. Price Monitor Service (src/services/price_monitor_service.py)

Background service that monitors prices for autonomous re-entry opportunities.

**Monitoring Loop:**
```
_monitor_loop()  # Runs every 30 seconds
    │
    ├─► _check_all_opportunities()
    │   ├─► _check_sl_hunt_reentries()
    │   ├─► _check_tp_continuation_reentries()
    │   └─► _check_exit_continuation_reentries()
    │
    └─► _check_profit_booking_chains()
```

## Data Flow

### Webhook Processing Flow

```
TradingView Alert
        │
        ▼
┌───────────────────┐
│  POST /webhook    │
│  (FastAPI)        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  AlertProcessor   │
│  - Validate       │
│  - Deduplicate    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  TradingEngine    │
│  process_alert()  │
└─────────┬─────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌───────┐  ┌───────────┐
│ Trend │  │   Entry   │
│Update │  │ Execution │
└───────┘  └─────┬─────┘
                 │
                 ▼
          ┌──────────────┐
          │ DualOrder    │
          │ Manager      │
          └──────┬───────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
   ┌─────────┐      ┌─────────┐
   │ Order A │      │ Order B │
   │TP Trail │      │Profit   │
   └────┬────┘      │Trail    │
        │           └────┬────┘
        │                │
        ▼                ▼
   ┌─────────┐      ┌─────────┐
   │ ReEntry │      │ Profit  │
   │ Chain   │      │ Chain   │
   └─────────┘      └─────────┘
```

### Trade Lifecycle

```
Entry Signal Received
        │
        ▼
┌───────────────────┐
│  Risk Validation  │
│  - Daily limit    │
│  - Lifetime limit │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Trend Alignment   │
│ Check             │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Order Placement  │
│  - Order A        │
│  - Order B        │
└─────────┬─────────┘
          │
    ┌─────┴─────────────────┐
    │                       │
    ▼                       ▼
┌───────────┐         ┌───────────┐
│  TP Hit   │         │  SL Hit   │
└─────┬─────┘         └─────┬─────┘
      │                     │
      ▼                     ▼
┌───────────┐         ┌───────────┐
│    TP     │         │  SL Hunt  │
│Continuation│        │ Recovery  │
└───────────┘         └───────────┘
```

## Database Schema

### Tables

**trades**
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    trade_id TEXT,
    symbol TEXT,
    entry_price REAL,
    exit_price REAL,
    sl_price REAL,
    tp_price REAL,
    lot_size REAL,
    direction TEXT,
    strategy TEXT,
    pnl REAL,
    commission REAL,
    swap REAL,
    comment TEXT,
    status TEXT,
    open_time DATETIME,
    close_time DATETIME,
    chain_id TEXT,
    chain_level INTEGER,
    is_re_entry BOOLEAN,
    order_type TEXT,
    profit_chain_id TEXT,
    profit_level INTEGER,
    session_id TEXT,
    logic_type TEXT,
    base_lot_size REAL,
    final_lot_size REAL,
    lot_multiplier REAL,
    sl_multiplier REAL
);
```

**reentry_chains**
```sql
CREATE TABLE reentry_chains (
    chain_id TEXT PRIMARY KEY,
    symbol TEXT,
    direction TEXT,
    original_entry REAL,
    original_sl_distance REAL,
    max_level_reached INTEGER,
    total_profit REAL,
    status TEXT,
    created_at DATETIME,
    completed_at DATETIME
);
```

**profit_booking_chains**
```sql
CREATE TABLE profit_booking_chains (
    chain_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    base_lot REAL NOT NULL,
    current_level INTEGER DEFAULT 0,
    total_profit REAL DEFAULT 0,
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**sl_events**
```sql
CREATE TABLE sl_events (
    id INTEGER PRIMARY KEY,
    trade_id TEXT,
    symbol TEXT,
    sl_price REAL,
    original_entry REAL,
    hit_time DATETIME,
    recovery_attempted BOOLEAN,
    recovery_successful BOOLEAN
);
```

**trading_sessions**
```sql
CREATE TABLE trading_sessions (
    session_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    entry_signal TEXT,
    exit_reason TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    total_pnl REAL DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ACTIVE',
    metadata TEXT
);
```

## Configuration Architecture

### Configuration Files

**config/config.json** - Main configuration
```json
{
    "telegram_token": "...",
    "telegram_chat_id": "...",
    "mt5_login": "...",
    "mt5_password": "...",
    "mt5_server": "...",
    "symbol_mapping": {...},
    "fixed_lot_sizes": {...},
    "risk_by_account_tier": {...},
    "symbol_config": {...},
    "re_entry_config": {...},
    "sl_systems": {...},
    "timeframe_specific_config": {...}
}
```

**.env** - Sensitive credentials
```
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
MT5_LOGIN=...
MT5_PASSWORD=...
MT5_SERVER=...
```

**config/timeframe_trends.json** - Trend state persistence
```json
{
    "XAUUSD": {
        "5m": {"trend": "BULLISH", "mode": "AUTO"},
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BEARISH", "mode": "AUTO"},
        "1d": {"trend": "BULLISH", "mode": "AUTO"}
    }
}
```

**data/stats.json** - Risk statistics
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

## Technology Stack Details

### Python Dependencies

| Package | Purpose |
|---------|---------|
| fastapi | Web framework for webhook handling |
| uvicorn | ASGI server |
| pydantic | Data validation and models |
| MetaTrader5 | MT5 terminal integration |
| python-telegram-bot | Telegram API (optional) |
| requests | HTTP client for Telegram API |
| sqlite3 | Database (built-in) |
| asyncio | Async/await support |
| logging | Logging framework |

### Async Architecture

The bot uses Python's asyncio for non-blocking operations:

```python
# Background task example
async def _monitor_loop(self):
    while self.running:
        try:
            await self._check_all_opportunities()
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Monitor error: {e}")
```

### Thread Safety

- SQLite connection with `check_same_thread=False`
- Telegram polling runs in separate thread
- Background monitoring uses asyncio tasks
- Config saves use atomic write with temp file

## Security Considerations

1. **Credential Storage**: Sensitive data in `.env` file, not in code
2. **Symbol Mapping**: Prevents direct exposure of broker symbols
3. **Input Validation**: All webhook data validated before processing
4. **Rate Limiting**: Duplicate alert detection prevents spam
5. **Error Handling**: Comprehensive try/catch blocks prevent crashes

## Performance Optimizations

1. **Optimized Logging**: Custom logger with batching and filtering
2. **Connection Pooling**: MT5 connection health monitoring
3. **Caching**: Symbol mapping cached in memory
4. **Async Operations**: Non-blocking I/O for network operations
5. **Database Indexing**: Primary keys on frequently queried columns

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [WORKFLOW_PROCESSES.md](WORKFLOW_PROCESSES.md) - Detailed workflows
- [API_INTEGRATION.md](API_INTEGRATION.md) - API details
- [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) - Configuration guide
