# 07 - Database Schema

## 💾 Complete Database Documentation

**Database Type**: SQLite  
**File**: `data/trading_bot.db`  
**ORM**: SQLAlchemy

---

## Tables Overview

| Table | Purpose | Records (typical) |
|-------|---------|-------------------|
| `trades` | All executed trades | 1000+ |
| `profit_chains` | Active profit chains | 0-50 |
| `session_stats` | Daily trading sessions | 30+ |
| `risk_caps` | Daily/lifetime loss tracking | 365+ |
| `reentry_history` | Re-entry audit trail | 500+ |
| `configurations` | Bot settings | ~50 |
| `error_logs` | Error tracking | 100+ |
| `notifications` | Notification history | 1000+ |
| `health_metrics` | System health data | 7-30 |
| `profit_targets` | Profit booking targets | 5-10 |

---

## 1. `trades` Table

**Purpose**: Store all trade executions

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Position identification
    position_id INTEGER UNIQUE NOT NULL,
    chain_id TEXT,
    
    -- Trade details
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,  -- 'buy' or 'sell'
    lots REAL NOT NULL,
    
    -- Prices
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,
    close_price REAL,
    
    -- Timing
    open_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    close_time TIMESTAMP,
    
    -- Financial
    profit REAL DEFAULT 0.0,
    commission REAL DEFAULT 0.0,
    swap REAL DEFAULT 0.0,
    
    -- Status
    status TEXT DEFAULT 'open',  -- 'open', 'closed', 'cancelled'
    close_reason TEXT,  -- 'tp', 'sl', 'manual', 'exit_signal', etc.
    
    -- Re-entry tracking
    reentry_level INTEGER DEFAULT 0,
    reentry_type TEXT,  -- NULL, 'sl_hunt', 'tp_continuation', 'exit_continuation'
    parent_position_id INTEGER,  -- For re-entries
    
    -- Classification
    order_type TEXT,  -- 'A' (TP Trail) or 'B' (Profit Booking)
    logic_type TEXT,  -- 'LOGIC1', 'LOGIC2', 'LOGIC3'
    timeframe TEXT,
    
    -- Additional
    comment TEXT,
    session_id TEXT,
    
    -- Risk/SL info
    sl_system TEXT,  -- 'sl-1' or 'sl-2'
    original_sl_distance REAL,
    sl_reduction_percent REAL DEFAULT 0.0,
    
    FOREIGN KEY (session_id) REFERENCES session_stats(session_id),
    FOREIGN KEY (chain_id) REFERENCES profit_chains(chain_id)
);
```

**Indexes**:
```sql
CREATE INDEX idx_trades_position_id ON trades(position_id);
CREATE INDEX idx_trades_chain_id ON trades(chain_id);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_session_id ON trades(session_id);
CREATE INDEX idx_trades_open_time ON trades(open_time);
```

**Sample Row**:
```
id: 123
position_id: 123456789
chain_id: CHAIN_EURUSD_20251226_001
symbol: EURUSD
direction: buy
lots: 0.10
entry_price: 1.10000
sl_price: 1.09000
tp_price: 1.11500
close_price: 1.11500
open_time: 2025-12-26 03:00:00
close_time: 2025-12-26 05:00:00
profit: 15.00
status: closed
close_reason: tp
reentry_level: 0
order_type: A
logic_type: LOGIC2
timeframe: 1h
sl_system: sl-1
```

---

## 2. `profit_chains` Table

**Purpose**: Track profit booking chains

```sql
CREATE TABLE profit_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Chain identity
    chain_id TEXT UNIQUE NOT NULL,
    
    -- Trade details
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    
    -- Chain progression
    current_level INTEGER DEFAULT 1,
    max_level INTEGER DEFAULT 5,
    
    -- Financial tracking
    base_lot_size REAL NOT NULL,
    current_lot_size REAL,
    total_profit REAL DEFAULT 0.0,
    
    -- Current position
    position_id INTEGER,
    
    -- Status
    status TEXT DEFAULT 'active',  -- 'active', 'completed', 'stopped'
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Configuration
    multiplier_preset TEXT DEFAULT 'standard',  -- 'standard', 'conservative', etc.
    profit_target_per_level REAL DEFAULT 7.0,
    
    FOREIGN KEY (position_id) REFERENCES trades(position_id)
);
```

**Sample Row**:
```
id: 5
chain_id: CHAIN_EURUSD_20251226_001
symbol: EURUSD
direction: buy
current_level: 3
base_lot_size: 0.10
current_lot_size: 0.40  (0.10 * 2^2)
total_profit: 49.00  (7 + 14 + 28)
position_id: 123456792
status: active
multiplier_preset: standard
```

---

## 3. `session_stats` Table

**Purpose**: Daily session tracking

```sql
CREATE TABLE session_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Session identity
    session_id TEXT UNIQUE NOT NULL,
    
    -- Timing
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    
    -- Trade counts
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    breakeven_trades INTEGER DEFAULT 0,
    
   -- Financial summary
    total_profit REAL DEFAULT 0.0,
    total_loss REAL DEFAULT 0.0,
    net_profit REAL DEFAULT 0.0,
    
    -- Extremes
    largest_win REAL DEFAULT 0.0,
    largest_loss REAL DEFAULT 0.0,
    
    -- Re-entry stats
    sl_hunt_triggers INTEGER DEFAULT 0,
    tp_continuation_triggers INTEGER DEFAULT 0,
    exit_continuation_triggers INTEGER DEFAULT 0,
    
    -- Profit chain stats
    chains_started INTEGER DEFAULT 0,
    chains_completed INTEGER DEFAULT 0,
    chain_profit REAL DEFAULT 0.0
);
```

**Sample Row**:
```
session_id: SES_20251226_025000
start_time: 2025-12-26 02:50:00
total_trades: 15
winning_trades: 9
losing_trades: 6
total_profit: 135.00
total_loss: -60.00
net_profit: 75.00
largest_win: 25.00
chains_started: 2
chains_completed: 1
```

---

## 4. `risk_caps` Table

**Purpose**: Track daily and lifetime losses

```sql
CREATE TABLE risk_caps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Date tracking
    date DATE UNIQUE NOT NULL,
    
    -- Loss tracking
    daily_loss REAL DEFAULT 0.0,
    lifetime_loss REAL DEFAULT 0.0,
    
    -- Caps (configurable)
    daily_cap REAL NOT NULL,
    lifetime_cap REAL NOT NULL,
    
    -- Tier info
    active_tier INTEGER,
    tier_lot_size REAL,
    
    -- Status
    daily_exceeded BOOLEAN DEFAULT FALSE,
    lifetime_exceeded BOOLEAN DEFAULT FALSE,
    trading_paused BOOLEAN DEFAULT FALSE,
    
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Auto-reset Logic**:
```python
# Daily loss resets at midnight
if current_date != last_date:
    database.reset_daily_loss()
```

---

## 5. `reentry_history` Table

**Purpose**: Audit trail for re-entries

```sql
CREATE TABLE reentry_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Original trade
    original_position_id INTEGER NOT NULL,
    
    -- Re-entry trade
    reentry_position_id INTEGER NOT NULL,
    
    -- Re-entry details
    reentry_type TEXT NOT NULL,  -- 'sl_hunt', 'tp_continuation', 'exit_continuation'
    reentry_level INTEGER NOT NULL,
    
    -- Configuration at time of re-entry
    sl_reduction_percent REAL,
    original_sl_distance REAL,
    new_sl_distance REAL,
    
    -- Timing
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Outcome
    success BOOLEAN,  -- Did re-entry make profit?
    profit REAL,
    
    FOREIGN KEY (original_position_id) REFERENCES trades(position_id),
    FOREIGN KEY (reentry_position_id) REFERENCES trades(position_id)
);
```

---

## 6. `configurations` Table

**Purpose**: Store bot configuration

```sql
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Config key-value
    config_key TEXT UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    
    -- Metadata
    category TEXT,  -- 'risk', 'reentry', 'profit', etc.
    data_type TEXT,  -- 'boolean', 'integer', 'float', 'string', 'json'
    
    -- Tracking
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by TEXT  -- 'system' or user_id
);
```

**Sample Rows**:
```
config_key: sl_hunt_enabled
config_value: true
category: reentry
data_type: boolean

config_key: daily_loss_cap
config_value: 100.0
category: risk
data_type: float

config_key: profit_chain_multipliers
config_value: [1, 2, 4, 8, 16]
category: profit
data_type: json
```

---

## 7. `error_logs` Table

**Purpose**: Track errors for diagnostics

```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Error details
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    error_traceback TEXT,
    
    -- Context
    component TEXT,  -- 'mt5_client', 'telegram_bot', etc.
    function_name TEXT,
    
    -- Timing
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Severity
    severity TEXT DEFAULT 'ERROR'  -- 'WARNING', 'ERROR', 'CRITICAL'
);
```

---

## 8. Database Operations

### Connection Management
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///data/trading_bot.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Common Queries

**Get open trades**:
```python
def get_open_trades(session):
    return session.query(Trade).filter(
        Trade.status == 'open'
    ).all()
```

**Get active chains**:
```python
def get_active_chains(session):
    return session.query(ProfitChain).filter(
        ProfitChain.status == 'active'
    ).all()
```

**Get today's session**:
```python
def get_current_session(session):
    today = date.today()
    return session.query(SessionStats).filter(
        func.date(SessionStats.start_time) == today
    ).first()
```

**Track loss**:
```python
def add_loss(session, amount):
    today = date.today()
    risk_cap = session.query(RiskCaps).filter(
        RiskCaps.date == today
    ).first()
    
    if not risk_cap:
        risk_cap = RiskCaps(date=today)
        session.add(risk_cap)
    
    risk_cap.daily_loss += amount
    risk_cap.lifetime_loss += amount
    session.commit()
```

---

## Database Files

| File | Purpose |
|------|---------|
| `src/database.py` | Database operations, queries |
| `src/models.py` | SQLAlchemy models |
| `data/trading_bot.db` | Actual database file |

---

## Maintenance

### Backup
```bash
# Regular backup (recommended daily)
cp data/trading_bot.db data/backups/trading_bot_$(date +%Y%m%d).db
```

### Vacuum (optimize)
```python
# Reduce file size, improve performance
session.execute("VACUUM")
```

### Cleanup old data
```python
# Delete old sessions (>90 days)
cutoff_date = datetime.now() - timedelta(days=90)
session.query(SessionStats).filter(
    SessionStats.start_time < cutoff_date
).delete()
```
