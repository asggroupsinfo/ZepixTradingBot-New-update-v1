# DATABASE SCHEMA DESIGNS

**Version:** 2.0 (Updated with V3/V6 Logic Details)  
**Date:** 2026-01-12  
**Status:** Design Complete

---

## 🗄️ DATABASE STRATEGY

**Three-Database Architecture:**
1. **V3 Combined Logic DB** (`zepix_combined.db` or `combined_v3.db`)
2. **V6 Price Action DB** (`zepix_price_action.db`)
3. **Central System DB** (`zepix_bot.db`)

**Isolation Principle:**
- V3 and V6 MUST have separate databases
- No cross-contamination of trading data
- Central DB aggregates for dashboards only

---

## 📊 V3 COMBINED LOGIC DATABASE

**File:** `data/zepix_combined.db` (or `combined_v3.db`)

### **Table: combined_v3_trades**

```sql
CREATE TABLE combined_v3_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification
    order_a_ticket INTEGER UNIQUE,          -- Order A (TP Trail) ticket
    order_b_ticket INTEGER UNIQUE,          -- Order B (Profit Trail) ticket
    mt5_parent_ticket INTEGER,              -- Primary ticket for linking
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V3 Specific: Signal Details
    signal_type TEXT NOT NULL,              -- 'Institutional_Launchpad', 'Liquidity_Trap', etc. (12 types)
    signal_timeframe TEXT,                  -- '5', '15', '60', '240'
    consensus_score INTEGER CHECK(consensus_score BETWEEN 0 AND 9),  -- 0-9 range
    position_multiplier REAL,               -- Calculated from consensus (0.2-1.0)
    
    -- V3 Specific: MTF 4-Pillar Trends (extracted indices 2-5)
    mtf_15m INTEGER CHECK(mtf_15m IN (-1, 0, 1)),   -- Index 2: 15-minute trend
    mtf_1h INTEGER CHECK(mtf_1h IN (-1, 0, 1)),     -- Index 3: 1-hour trend
    mtf_4h INTEGER CHECK(mtf_4h IN (-1, 0, 1)),     -- Index 4: 4-hour trend
    mtf_1d INTEGER CHECK(mtf_1d IN (-1, 0, 1)),     -- Index 5: 1-day trend
    mtf_raw_string TEXT,                    -- Original "1,1,-1,1,1,1" for reference
    
    -- V3 Specific: Routing
    logic_route TEXT CHECK(logic_route IN ('LOGIC1', 'LOGIC2', 'LOGIC3')),
    logic_multiplier REAL,                  -- 1.25 (L1), 1.0 (L2), 0.625 (L3)
    routing_reason TEXT,                    -- 'signal_override' or 'timeframe_routing'
    
    -- V3 Specific: Dual Order Details
    order_a_lot_size REAL,
    order_b_lot_size REAL,
    order_a_sl_price REAL,                  -- V3 Smart SL from Pine Script
    order_b_sl_price REAL,                  -- Fixed $10 SL (DIFFERENT from order_a)
    order_a_tp_price REAL,                  -- TP2 (extended target)
    order_b_tp_price REAL,                  -- TP1 (closer target)
    
    -- Order A Results
    order_a_exit_price REAL,
    order_a_exit_time TIMESTAMP,
    order_a_profit_pips REAL,
    order_a_profit_dollars REAL,
    order_a_status TEXT CHECK(order_a_status IN ('OPEN', 'CLOSED')),
    
    -- Order B Results
    order_b_exit_price REAL,
    order_b_exit_time TIMESTAMP,
    order_b_profit_pips REAL,
    order_b_profit_dollars REAL,
    order_b_status TEXT CHECK(order_b_status IN ('OPEN', 'CLOSED')),
    
    -- Combined P&L
    total_profit_pips REAL,
    total_profit_dollars REAL,
    commission REAL DEFAULT 0,
    swap REAL DEFAULT 0,
    
    -- Metadata
    trend_bypass_used BOOLEAN DEFAULT 0,    -- Was trend check bypassed?
    is_entry_v3_signal BOOLEAN DEFAULT 0,   -- Fresh v3 signal?
    close_reason TEXT,
    notes TEXT
);

-- Indexes for V3
CREATE INDEX idx_v3_trades_status ON combined_v3_trades(status);
CREATE INDEX idx_v3_trades_symbol ON combined_v3_trades(symbol);
CREATE INDEX idx_v3_trades_signal_type ON combined_v3_trades(signal_type);
CREATE INDEX idx_v3_trades_logic_route ON combined_v3_trades(logic_route);
CREATE INDEX idx_v3_trades_entry_time ON combined_v3_trades(entry_time);
```

### **Table: v3_profit_bookings**

```sql
CREATE TABLE v3_profit_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,              -- References combined_v3_trades.id
    order_type TEXT CHECK(order_type IN ('ORDER_A', 'ORDER_B')),
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_percentage REAL NOT NULL,
    closed_volume REAL NOT NULL,
    profit_pips REAL,
    profit_dollars REAL,
    reason TEXT,                            -- 'TP1', 'TP2', 'Manual', 'Trailing'
    FOREIGN KEY (trade_id) REFERENCES combined_v3trades(id)
);
```

### **Table: v3_signals_log**

```sql
CREATE TABLE v3_signals_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signal_type TEXT NOT NULL,              -- All 12 signal types
    symbol TEXT NOT NULL,
    direction TEXT,
    timeframe TEXT,
    consensus_score INTEGER,
    mtf_raw_string TEXT,
    signal_json TEXT,                       -- Full alert payload
    processed BOOLEAN DEFAULT 0,
    trade_placed BOOLEAN DEFAULT 0,
    trade_id INTEGER,
    skip_reason TEXT,                       -- Why skipped (if any)
    FOREIGN KEY (trade_id) REFERENCES combined_v3_trades(id)
);
```

### **Table: v3_daily_stats**

```sql
CREATE TABLE v3_daily_stats (
    date TEXT PRIMARY KEY,
    total_dual_entries INTEGER DEFAULT 0,
    total_order_a_closed INTEGER DEFAULT 0,
    total_order_b_closed INTEGER DEFAULT 0,
    logic1_trades INTEGER DEFAULT 0,
    logic2_trades INTEGER DEFAULT 0,
    logic3_trades INTEGER DEFAULT 0,
    total_profit_dollars REAL DEFAULT 0,
    win_rate REAL DEFAULT 0,
    profit_factor REAL DEFAULT 0
);
```

---

## 🎯 V6 PRICE ACTION DATABASE

**File:** `data/zepix_price_action.db`

### **Table: price_action_1m_trades**

```sql
CREATE TABLE price_action_1m_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification
    order_b_ticket INTEGER UNIQUE,          -- 1M uses ORDER B ONLY
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,                          -- Uses TP1 (quick exit)
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    exit_price REAL,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 1M Specific Fields
    adx REAL,
    adx_strength TEXT,                      -- 'STRONG', 'WEAK', 'NONE'
    confidence_score INTEGER,               -- 0-100
    confidence_level TEXT,                  -- 'HIGH', 'MODERATE'
    spread_pips REAL,                       -- Spread at entry
    market_state TEXT,                      -- 'TRENDING_BULLISH', 'SIDEWAYS', etc.
    
    -- Results
    profit_pips REAL,
    profit_dollars REAL,
    close_reason TEXT,
    
    -- Metadata
    execution_speed_ms INTEGER,             -- How fast was execution?
    slippage_pips REAL,
    notes TEXT
);

CREATE INDEX idx_v6_1m_status ON price_action_1m_trades(status);
CREATE INDEX idx_v6_1m_symbol ON price_action_1m_trades(symbol);
```

### **Table: price_action_5m_trades**

```sql
CREATE TABLE price_action_5m_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification (DUAL ORDERS)
    order_a_ticket INTEGER UNIQUE,
    order_b_ticket INTEGER UNIQUE,
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 5M Specific Fields
    adx REAL,
    adx_strength TEXT,
    confidence_score INTEGER,
    trend_15m_aligned BOOLEAN,              -- Was 15m trend aligned?
    momentum_increasing BOOLEAN,            -- Momentum check result
    
    -- Dual Order Details
    order_a_lot_size REAL,
    order_b_lot_size REAL,
    order_a_sl_price REAL,
    order_b_sl_price REAL,
    order_a_tp_price REAL,                  -- TP2
    order_b_tp_price REAL,                  -- TP1
    
    -- Order A Results
    order_a_exit_price REAL,
    order_a_exit_time TIMESTAMP,
    order_a_profit_dollars REAL,
    order_a_status TEXT,
    
    -- Order B Results
    order_b_exit_price REAL,
    order_b_exit_time TIMESTAMP,
    order_b_profit_dollars REAL,
    order_b_status TEXT,
    
    -- Combined Results
    total_profit_dollars REAL,
    breakeven_moved BOOLEAN DEFAULT 0,      -- Did we move to breakeven after TP1?
    notes TEXT
);

CREATE INDEX idx_v6_5m_status ON price_action_5m_trades(status);
```

### **Table: price_action_15m_trades**

```sql
CREATE TABLE price_action_15m_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification (ORDER A ONLY)
    order_a_ticket INTEGER UNIQUE,
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 15M Specific Fields
    adx REAL,
    confidence_score INTEGER,
    market_state TEXT,                      -- MUST match signal direction
    pulse_bull_count INTEGER,               -- From Trend Pulse
    pulse_bear_count INTEGER,
    pulse_alignment_ok BOOLEAN,             -- bull_count > bear_count for BUY?
    
    -- Results
    exit_price REAL,
    profit_dollars REAL,
    close_reason TEXT,
    notes TEXT
);

CREATE INDEX idx_v6_15m_status ON price_action_15m_trades(status);
```

### **Table: price_action_1h_trades**

```sql
CREATE TABLE price_action_1h_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification (ORDER A ONLY)
    order_a_ticket INTEGER UNIQUE,
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 1H Specific Fields
    trend_4h INTEGER,                       -- 4H trend value
    trend_1d INTEGER,                       -- 1D trend value
    higher_tf_aligned BOOLEAN,              -- 4H/1D alignment
    confidence_score INTEGER,
    
    -- Results
    exit_price REAL,
    exit_time TIMESTAMP,
    profit_dollars REAL,
    close_reason TEXT,
    notes TEXT
);

CREATE INDEX idx_v6_1h_status ON price_action_1h_trades(status);
```

### **Table: market_trends (Shared by all V6 plugins)**

```sql
CREATE TABLE market_trends (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,                -- '5', '15', '60', '240', '1440'
    bull_count INTEGER DEFAULT 0,
    bear_count INTEGER DEFAULT 0,
    market_state TEXT,                      -- 'TRENDING_BULLISH', 'TRENDING_BEARISH', 'SIDEWAYS', etc.
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changes TEXT,                           -- Comma-separated TF changes from TREND_PULSE
    PRIMARY KEY (symbol, timeframe)
);

-- For quick lookups
CREATE INDEX idx_market_trends_symbol ON market_trends(symbol);
```

### **Table: v6_signals_log**

```sql
CREATE TABLE v6_signals_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signal_type TEXT NOT NULL,              -- 'BULLISH_ENTRY', 'BEARISH_ENTRY', 'TREND_PULSE'
    plugin_target TEXT,                     -- 'price_action_1m', '5m', '15m', '1h'
    symbol TEXT NOT NULL,
    timeframe TEXT,
    adx REAL,
    confidence_score INTEGER,
    signal_json TEXT,                       -- Full 15-field payload
    processed BOOLEAN DEFAULT 0,
    trade_placed BOOLEAN DEFAULT 0,
    trade_id INTEGER,
    skip_reason TEXT
);
```

### **Table: v6_daily_stats**

```sql
CREATE TABLE v6_daily_stats (
    date TEXT PRIMARY KEY,
    plugin_1m_trades INTEGER DEFAULT 0,
    plugin_5m_trades INTEGER DEFAULT 0,
    plugin_15m_trades INTEGER DEFAULT 0,
    plugin_1h_trades INTEGER DEFAULT 0,
    total_profit_dollars REAL DEFAULT 0,
    trend_pulse_updates INTEGER DEFAULT 0,
    win_rate REAL DEFAULT 0
);
```

---

## 🌐 CENTRAL SYSTEM DATABASE

**File:** `data/zepix_bot.db`

### **Table: plugins_registry**

```sql
CREATE TABLE plugins_registry (
    plugin_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plugin_type TEXT CHECK(plugin_type IN ('V3_COMBINED', 'V6_PRICE_ACTION')),
    version TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    installed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    database_path TEXT,
    status TEXT CHECK(status IN ('ACTIVE', 'DISABLED', 'ERROR')),
    error_message TEXT
);

-- Pre-populate
INSERT INTO plugins_registry VALUES 
    ('combined_v3', 'V3 Combined Logic', 'V3_COMBINED', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_combined.db', 'ACTIVE', NULL),
    ('price_action_1m', 'V6 1M Scalping', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL),
    ('price_action_5m', 'V6 5M Momentum', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL),
    ('price_action_15m', 'V6 15M Intraday', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL),
    ('price_action_1h', 'V6 1H Swing', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL);
```

### **Table: aggregated_trades**

```sql
CREATE TABLE aggregated_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    plugin_type TEXT,
    mt5_ticket INTEGER,
    symbol TEXT,
    direction TEXT,
    lot_size REAL,
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    profit_dollars REAL,
    status TEXT,
    FOREIGN KEY (plugin_id) REFERENCES plugins_registry(plugin_id)
);

-- Auto-synced from per-plugin DBs every 5 minutes
CREATE INDEX idx_agg_trades_plugin ON aggregated_trades(plugin_id);
CREATE INDEX idx_agg_trades_time ON aggregated_trades(entry_time);
```

### **Table: system_config**

```sql
CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_config VALUES 
    ('bot_version', '3.0.0', datetime('now')),
    ('architecture', 'dual_core_v3_v6', datetime('now')),
    ('v3_enabled', 'true', datetime('now')),
    ('v6_enabled', 'true', datetime('now'));
```

### **Table: system_events**

```sql
CREATE TABLE system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    plugin_id TEXT,
    description TEXT,
    severity TEXT CHECK(severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);
```

---

## 🔄 DATABASE SYNC PROCESS

```python
class DatabaseSyncManager:
    """
    Syncs V3 and V6 plugin data to central DB
    """
    
    async def sync_all_plugins(self):
        """Runs every 5 minutes"""
        await self.sync_v3_trades()
        await self.sync_v6_trades()
    
    async def sync_v3_trades(self):
        v3_db = sqlite3.connect('data/zepix_combined.db')
        central_db = sqlite3.connect('data/zepix_bot.db')
        
        # Get new V3 trades
        new_trades = v3_db.execute("""
            SELECT id, order_a_ticket as mt5_ticket, symbol, direction,
                   order_a_lot_size + order_b_lot_size as lot_size,
                   entry_time, exit_time, total_profit_dollars, status
            FROM combined_v3_trades
            WHERE id > (
                SELECT COALESCE(MAX(id), 0) FROM aggregated_trades
                WHERE plugin_id = 'combined_v3'
            )
        """).fetchall()
        
        for trade in new_trades:
            central_db.execute("""
                INSERT INTO aggregated_trades 
                (plugin_id, plugin_type, mt5_ticket, symbol, direction, 
                 lot_size, entry_time, exit_time, profit_dollars, status)
                VALUES ('combined_v3', 'V3_COMBINED', ?, ?, ?, ?, ?, ?, ?, ?)
            """, trade)
        
        central_db.commit()
    
    async def sync_v6_trades(self):
        # Similar for all 4 V6 plugin tables
        pass
```

---

## ✅ MIGRATION SCRIPTS

### **Create V3 Database**

```python
def create_v3_database():
    db = sqlite3.connect('data/zepix_combined.db')
    db.execute(""" /* combined_v3_trades schema */ """)
    db.execute(""" /* v3_profit_bookings schema */ """)
    db.execute(""" /* v3_signals_log schema */ """)
    db.execute(""" /* v3_daily_stats schema */ """)
    logger.info("✅ V3 Combined Logic database created")
```

### **Create V6 Database**

```python
def create_v6_database():
    db = sqlite3.connect('data/zepix_price_action.db')
    db.execute(""" /* price_action_1m_trades schema */ """)
    db.execute(""" /* price_action_5m_trades schema */ """)
    db.execute(""" /* price_action_15m_trades schema */ """)
    db.execute(""" /* price_action_1h_trades schema */ """)
    db.execute(""" /* market_trends schema */ """)
    db.execute(""" /* v6_signals_log schema */ """)
    logger.info("✅ V6 Price Action database created")
```

---

## 🎯 COMPLETION CHECKLIST

- [ ] V3 database schema complete with 12-signal support
- [ ] V3 dual order tracking (Order A + B) implemented
- [ ] V3 MTF 4-pillar fields defined
- [ ] V6 database schema with 4 plugin-specific tables
- [ ] V6 conditional order tracking (B-only, Dual, A-only)
- [ ] V6 Trend Pulse market_trends table created
- [ ] Central aggregation system designed
- [ ] Sync process implemented
- [ ] All indexes optimized

**Status:** READY FOR PHASE 4 & 7 IMPLEMENTATION
