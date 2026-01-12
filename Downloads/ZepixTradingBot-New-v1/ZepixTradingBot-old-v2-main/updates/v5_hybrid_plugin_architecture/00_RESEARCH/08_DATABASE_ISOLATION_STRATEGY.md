# 08_DATABASE_ISOLATION_STRATEGY.md

**Document Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Research Complete

---

## 🎯 OBJECTIVE

Define how each plugin maintains isolated data storage while supporting cross-plugin analytics.

---

## 🗄️ DATABASE ARCHITECTURE

### **Two-Tier Database Strategy**

```
┌──────────────────────────────────────┐
│     PLUGIN DATABASES (Isolated)      │
├──────────────────────────────────────┤
│ data/zepix_combined_v3.db            │
│ data/zepix_price_action_v6.db        │
│ data/zepix_custom_strategy.db        │
└──────────────────────────────────────┘
            │
            │ Aggregation Layer
            ▼
┌──────────────────────────────────────┐
│   MAIN DATABASE (Cross-Plugin)       │
├──────────────────────────────────────┤
│ data/zepix_bot.db                    │
│ - System metrics                     │
│ - Cross-plugin analytics             │
│ - Global configuration               │
└──────────────────────────────────────┘
```

---

## 📊 PLUGIN DATABASE SCHEMA

Each plugin has its own SQLite database with this schema:

```sql
-- data/zepix_{plugin_id}.db

CREATE TABLE plugin_info (
    plugin_id TEXT PRIMARY KEY,
    version TEXT,
    last_started TIMESTAMP,
    total_runtime_hours REAL
);

CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mt5_ticket INTEGER UNIQUE,
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    exit_price REAL,
    profit_pips REAL,
    profit_dollars REAL,
    commission REAL DEFAULT 0,
    swap REAL DEFAULT 0,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED', 'PARTIAL')),
    close_reason TEXT,  -- 'TP', 'SL', 'MANUAL', 'REVERSAL'
    signal_data TEXT  -- JSON with original alert data
);

CREATE TABLE profit_chains (
    chain_id TEXT PRIMARY KEY,
    base_trade_id INTEGER REFERENCES trades(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')),
    current_level INTEGER DEFAULT 0,
    max_levels INTEGER,
    total_profit_booked REAL DEFAULT 0
);

CREATE TABLE chain_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id TEXT REFERENCES profit_chains(chain_id),
    level_number INTEGER,
    target_pips REAL,
    volume_to_close REAL,
    executed_at TIMESTAMP,
    profit_pips REAL,
    profit_dollars REAL
);

CREATE TABLE daily_stats (
    date TEXT PRIMARY KEY,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    breakeven_trades INTEGER DEFAULT 0,
    total_profit_pips REAL DEFAULT 0,
    total_profit_dollars REAL DEFAULT 0,
    max_drawdown REAL DEFAULT 0,
    largest_win REAL DEFAULT 0,
    largest_loss REAL DEFAULT 0
);

CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_entry_time ON trades(entry_time);
```

---

## 🔒 ISOLATION RULES

### **1. Plugin Cannot Access Other Plugin DBs**

```python
class PluginDatabase:
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.db_path = f"data/zepix_{plugin_id}.db"
        
        # Ensure only this plugin's DB is accessible
        if not os.path.exists(self.db_path):
            self._create_schema()
    
    def _validate_access(self, requested_db_path: str):
        """Prevent cross-plugin access"""
        if requested_db_path != self.db_path:
            raise PermissionError(
                f"Plugin {self.plugin_id} cannot access {requested_db_path}"
            )
```

### **2. Main Database for Aggregation Only**

```sql
-- data/zepix_bot.db

CREATE TABLE system_metrics (
    timestamp TIMESTAMP PRIMARY KEY,
    total_open_trades INTEGER,
    total_daily_profit REAL,
    active_plugins TEXT  -- Comma-separated plugin IDs
);

CREATE TABLE cross_plugin_stats (
    date TEXT,
    plugin_id TEXT,
    trades_count INTEGER,
    profit REAL,
    PRIMARY KEY (date, plugin_id)
);
```

**Access Pattern:**
- Plugins WRITE to their own DB
- Analytics service READS from all plugin DBs
- Analytics service WRITES aggregated data to main DB

---

## 📈 CROSS-PLUGIN ANALYTICS

### **Aggregation Service**

```python
class AnalyticsAggregator:
    def generate_daily_report(self) -> Dict:
        """
        Reads from all plugin databases.
        Aggregates into single report.
        """
        report = {
            "date": datetime.now().date(),
            "plugins": []
        }
        
        for plugin_id in self.plugin_registry.get_all_plugins():
            plugin_db = PluginDatabase(plugin_id)
            stats = plugin_db.get_daily_stats()
            
            report["plugins"].append({
                "plugin_id": plugin_id,
                "trades": stats["total_trades"],
                "profit": stats["total_profit"]
            })
        
        report["total_profit"] = sum(p["profit"] for p in report["plugins"])
        
        # Save to main DB for historical tracking
        self.main_db.save_aggregate(report)
        
        return report
```

---

## 🔄 DATA MIGRATION STRATEGY

### **Phase-by-Phase Migration**

**Phase 1: Baseline (Current State)**
- Single database: `data/zepix_bot.db`
- All logics write to same tables

**Phase 4: Migration to Plugin DBs**

```python
def migrate_v3_data_to_plugin_db():
    """
    Moves V3 logic trades from main DB to plugin DB.
    """
    # 1. Connect to both DBs
    main_db = sqlite3.connect("data/zepix_bot.db")
    plugin_db = sqlite3.connect("data/zepix_combined_v3.db")
    
    # 2. Copy V3 trades
    trades = main_db.execute("""
        SELECT * FROM trades 
        WHERE comment LIKE 'combinedlogic%'
    """).fetchall()
    
    # 3. Insert into plugin DB
    for trade in trades:
        plugin_db.execute("""
            INSERT INTO trades VALUES (?, ?, ?, ...)
        """, trade)
    
    # 4. Mark as migrated in main DB (don't delete yet)
    main_db.execute("""
        UPDATE trades 
        SET migrated_to_plugin = 'combined_v3'
        WHERE comment LIKE 'combinedlogic%'
    """)
    
    plugin_db.commit()
    main_db.commit()
```

**Rollback Plan:**
- Keep migrated data in main DB for 30 days
- If rollback needed, restore from main DB

---

## 💾 BACKUP STRATEGY

### **Per-Plugin Backups**

```bash
# Daily backup script
for db in data/zepix_*.db; do
    plugin_name=$(basename "$db" .db)
    backup_dir="backups/$(date +%Y-%m-%d)"
    mkdir -p "$backup_dir"
    
    # SQLite backup
    sqlite3 "$db" ".backup '$backup_dir/$plugin_name.db'"
    
    # Compress
    gzip "$backup_dir/$plugin_name.db"
done
```

**Retention Policy:**
- Daily backups: Keep 7 days
- Weekly backups: Keep 4 weeks
- Monthly backups: Keep 12 months

---

## 🔍 QUERYING STRATEGY

### **Plugin Queries (Fast)**

```python
# Plugin queries its own DB
plugin_db = PluginDatabase("combined_v3")
open_trades = plugin_db.query("""
    SELECT * FROM trades WHERE status = 'OPEN'
""")
```

**Performance:** <10ms (single small DB)

### **Cross-Plugin Queries (Slower)**

```python
# Analytics aggregates across plugins
all_profits = []
for plugin_id in plugins:
    db = PluginDatabase(plugin_id)
    profit = db.query("SELECT SUM(profit_dollars) FROM trades")
    all_profits.append(profit)

total = sum(all_profits)
```

**Performance:** ~50ms for 5 plugins

---

## ⚠️ EDGE CASES

### **1. Plugin Deletion**
**Q:** What happens to plugin DB when plugin is remove

d?
A:** 
- Move to `data/archived/zepix_{plugin_id}.db`
- Keep for 90 days
- Compress after 7 days

### **2. Plugin Conflicts**
**Q:** What if two plugins trade same symbol simultaneously?
**A:**
- Each plugin has independent state
- Both can have open trades on XAUUSD
- MT5 treats as separate positions (comment field differs)

### **3. Database Corruption**
**Q:** What if plugin DB corrupts?
**A:**
- Restore from latest backup
- Replay MT5 order history to reconstruct
- Alert admin via Telegram

---

## ✅ DECISION

**APPROVED:** Two-tier isolated database architecture.

**Next Steps:**
1. Create plugin database schema template
2. Implement PluginDatabase class
3. Create migration scripts
4. Setup backup automation
