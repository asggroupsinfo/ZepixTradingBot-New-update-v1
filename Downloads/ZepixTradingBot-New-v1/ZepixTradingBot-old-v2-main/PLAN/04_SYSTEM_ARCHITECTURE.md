# 04 - System Architecture (Technical Details)

## 🏗️ Deep Technical Architecture

---

## 1. Application Stack

### Runtime Environment
- **Python**: 3.12+
- **Async Framework**: asyncio
- **Event Loop**: WindowsProactorEventLoop (Windows)
- **Web Framework**: FastAPI (Uvicorn server)
- **Port**: 80 (requires admin on Windows)

### Core Dependencies
```
MetaTrader5==5.0.45
python-telegram-bot==13.7
FastAPI==0.104.1
SQLAlchemy==2.0.23
asyncio
requests
```

---

## 2. Directory Structure (Detailed)

```
ZepixTradingBot/
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Configuration loader
│   ├── database.py               # Database operations
│   ├── models.py                 # Data models
│   │
│   ├── core/                     # Core trading logic
│   │   ├── __init__.py
│   │   └── trading_engine.py    # Main trading orchestrator
│   │
│   ├── clients/                  # External integrations
│   │   ├── __init__.py
│   │   ├── mt5_client.py        # MetaTrader 5 client
│   │   └── telegram_bot.py      # Telegram bot (5118 lines)
│   │
│   ├── managers/                 # Business logic managers
│   │   ├── __init__.py
│   │   ├── dual_order_manager.py
│   │   ├── profit_booking_manager.py
│   │   ├── risk_manager.py
│   │   ├── reentry_manager.py
│   │   ├── timeframe_trend_manager.py
│   │   ├── session_manager.py
│   │   ├── autonomous_system_manager.py
│   │   ├── profit_protection_manager.py
│   │   ├── sl_reduction_optimizer.py
│   │   ├── reverse_shield_manager.py
│   │   └── recovery_window_monitor.py
│   │
│   ├── menu/                     # Menu system
│   │   ├── __init__.py
│   │   ├── menu_manager.py      # Menu rendering
│   │   ├── command_executor.py   # Command execution
│   │   ├── command_mapping.py    # 78 command definitions
│   │   ├── menu_constants.py     # Menu layouts & constants
│   │   ├── reentry_menu_handler.py
│   │   ├── profit_menu_handler.py
│   │   └── fine_tune_menu_handler.py
│   │
│   ├── processors/               # Data processors
│   │   ├── __init__.py
│   │   └── alert_processor.py   # TradingView alert processing
│   │
│   ├── services/                 # Background services
│   │   ├── __init__.py
│   │   ├── price_monitor_service.py    # 30s price monitoring
│   │   ├── reversal_exit_handler.py
│   │   └── analytics_engine.py
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── pip_calculator.py    # Pip/price calculations
│       ├── profit_sl_calculator.py
│       └── exit_strategies.py
│
├── config/                       # Configuration files
│   ├── config.json              # Main configuration (1000+ lines)
│   ├── timeframe_trends.json   # Trend storage
│   ├── log_level.txt           # Current log level
│   └── trading_debug.txt       # Debug mode flag
│
├── data/                        # Runtime data
│   ├── trading_bot.db          # SQLite database
│   └── stats.json              # Performance stats
│
├── logs/                        # Log files
│   └── bot.log                 # Rotating log (10MB max)
│
├── DOCUMENTATION/               # This documentation
│
├── .env                        # Environment variables
├── requirements.txt
└── README.md
```

---

## 3. Component Dependencies Graph

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    (FastAPI Application)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├──► config.py (loads config.json)
                       │
                       ├──► database.py (SQLite connection)
                       │
                       └──► TradingEngine
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   TelegramBot          AlertProcessor        MT5Client
        │                     │                     │
        ├─► MenuManager       └─► Validation        └─► MT5 Terminal
        │
        └─► CommandExecutor
                │
                ├──► RiskManager
                ├──► DualOrderManager
                ├──► ProfitBookingManager
                ├──► ReentryManager
                ├──► TimeframeTrendManager
                ├──► AutonomousSystemManager
                └──► SessionManager

Background Services (async tasks):
- PriceMonitorService (30s loop)
- TelegramBot polling (continuous)
- Trade monitor (5s loop)
```

---

## 4. Data Flow Architecture

### Request Flow
```
External Request
    ↓
FastAPI Endpoint (/webhook or Telegram)
    ↓
Request Validation
    ↓
Business Logic (Managers)
    ↓
Database Operations (if needed)
    ↓
MT5 Operations (if trading)
    ↓
Response/Notification
```

### Background Task Flow
```
Async Task Started
    ↓
While is_running:
    ↓
    Execute logic silently
    ↓
    Catch exceptions → Log errors only
    ↓
    Sleep (interval)
    ↓
Loop
```

---

## 5. Database Architecture

### Connection
- **Type**: SQLite (file-based)
- **File**: `data/trading_bot.db`
- **ORM**: SQLAlchemy
- **Connection Pool**: SingletonSession

### Schema Overview
```sql
-- trades table
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    position_id INTEGER,
    symbol TEXT,
    direction TEXT,
    lots REAL,
    entry_price REAL,
    sl_price REAL,
    tp_price REAL,
    open_time TIMESTAMP,
    close_time TIMESTAMP,
    profit REAL,
    status TEXT,
    chain_id TEXT,
    reentry_level INTEGER,
    comment TEXT
);

-- profit_chains table
CREATE TABLE profit_chains (
    id INTEGER PRIMARY KEY,
    chain_id TEXT UNIQUE,
    symbol TEXT,
    direction TEXT,
    current_level INTEGER,
    max_level INTEGER DEFAULT 5,
    total_profit REAL DEFAULT 0,
    position_id INTEGER,
    status TEXT,
    created_at TIMESTAMP
);

-- session_stats table
CREATE TABLE session_stats (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_profit REAL DEFAULT 0,
    total_loss REAL DEFAULT 0,
    largest_win REAL DEFAULT 0,
    largest_loss REAL DEFAULT 0
);

-- risk_caps table
CREATE TABLE risk_caps (
    id INTEGER PRIMARY KEY,
    date DATE UNIQUE,
    daily_loss REAL DEFAULT 0,
    lifetime_loss REAL DEFAULT 0,
    daily_cap REAL,
    lifetime_cap REAL
);

-- reentry_history table
CREATE TABLE reentry_history (
    id INTEGER PRIMARY KEY,
    original_position_id INTEGER,
    reentry_position_id INTEGER,
    reentry_type TEXT,  -- 'sl_hunt', 'tp_continuation', 'exit_continuation'
    reentry_level INTEGER,
    sl_reduction_percent REAL,
    timestamp TIMESTAMP
);
```

---

## 6. Configuration Management

### Configuration Loading Sequence
```python
1. Load .env file (environment variables)
   - TELEGRAM_TOKEN
   - MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
   - TELEGRAM_CHAT_ID

2. Load config/config.json (main config)
   - All bot settings
   - Risk tiers
   - SL systems
   - Profit booking config
   
3. Load config/timeframe_trends.json
   - Symbol/timeframe trends

4. Load config/log_level.txt
   - Current logging level

5. Merge and validate all configs
```

### Config Priority
1. Environment variables (.env) - Highest
2. config.json - Medium
3. Default values in code - Lowest

---

## 7. Async Architecture

### Event Loop
```python
# Windows-specific
asyncio.set_event_loop_policy(
    asyncio.WindowsProactorEventLoopPolicy()
)
```

### Background Tasks
```python
# Created on startup
app.state.background_tasks = [
    price_monitor_task,
    telegram_polling_task,
    trade_monitor_task
]

# Cleanup on shutdown
for task in app.state.background_tasks:
    task.cancel()
```

---

## 8. Error Handling Strategy

### Levels
1. **Try-Catch in every public method**
2. **Graceful degradation** (e.g., MT5 fails → simulation mode)
3. **Error tracking** (statistics stored)
4. **User notification** (critical errors only)
5. **Logging** (all errors logged)

### Example
```python
try:
    result = mt5.order_send(request)
    if result is None:
        raise MT5Error("Order failed")
except MT5Error as e:
    logger.error(f"MT5 error: {e}")
    error_stats.increment("mt5_error")
    if critical:
        telegram_bot.send_alert(f"⚠️ MT5 Error: {e}")
    # Fall back
    return simulate_order(request)
```

---

## 9. Performance Optimization

### Techniques Used
1. **Async I/O** - Non-blocking operations
2. **Caching** - Symbol mappings cached
3. **Database connection pooling**
4. **Lazy loading** - Import only when needed
5. **Efficient queries** - Indexed database columns
6. **Batch operations** - Group notifications

### Memory Management
```
Typical memory usage: ~70MB
Peak (with 100 active trades): ~150MB
```

---

## 10. Security & Safety

### API Keys
- Stored in .env (not in code)
- .env excluded from git (.gitignore)

### Validation
- All user inputs validated
- Symbol whitelist enforced
- Lot size limits checked
- Risk caps enforced

### Trading Safety
- Simulation mode available
- Auto-pause on errors
- RR ratio validation
- Margin checks before orders

---

## 11. Logging Architecture

### Log Levels
```python
DEBUG    # Detailed, troubleshooting
INFO     # Normal operation (default)
WARNING  # Non-critical issues
ERROR    # Errors needing attention
CRITICAL # Critical failures
```

### Log Rotation
```python
RotatingFileHandler(
    filename='logs/bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Silencing Background Loops
```python
# ❌ Don't log in loops
while running:
    check_prices()  # Silent
    
# ✅ Only log errors
while running:
    try:
        check_prices()
    except Exception as e:
        logger.error(f"Error: {e}")
```

---

## 12. Port Management

### Port 80 Setup
```python
# Auto-grant permission (Windows)
if port == 80:
    grant_port_permission()

# Kill existing process
kill_process_on_port(80)

# Start server
uvicorn.run(app, host="0.0.0.0", port=80)
```

---

## 13. Singleton Patterns

### Used For
- Database connection
- MT5 client
- Configuration
- Telegram bot instance

### Implementation
```python
class MT5Client:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

**Technical Files Reference**:
- Main entry: `src/main.py`
- Core engine: `src/core/trading_engine.py`
- Largest file: `src/clients/telegram_bot.py` (5118 lines)
- Most complex: `src/managers/profit_booking_manager.py`
