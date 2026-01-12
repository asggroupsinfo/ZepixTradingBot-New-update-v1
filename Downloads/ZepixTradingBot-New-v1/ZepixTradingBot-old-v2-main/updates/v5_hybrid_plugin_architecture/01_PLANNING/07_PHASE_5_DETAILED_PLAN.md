# 07_PHASE_5_DETAILED_PLAN.md

**Phase:** 5 - Dynamic Config & Per-Plugin Databases  
**Duration:** Week 4-5 (3 days)  
**Dependencies:** Phase 4 complete  
**Status:** Not Started

---

## 🎯 PHASE OBJECTIVES

1. Implement dynamic configuration reload
2. Create per-plugin database setup
3. Enable runtime config changes
4. Zero-downtime config updates

---

## 📋 TASK BREAKDOWN

### **5.1: ConfigManager Implementation**
**Duration:** 1 day

**File:** `src/core/config_manager.py`

```python
import json
import os
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigManager:
    """
    Manages dynamic configuration loading and hot-reload.
    """
    
    def __init__(self, config_path="config/config.json"):
        self.config_path = config_path
        self.config = {}
        self.observers = []
        self.load_config()
        self.start_watching()
    
    def load_config(self):
        """Loads configuration from JSON file"""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        logger.info(f"✅ Config loaded from {self.config_path}")
    
    def reload_config(self):
        """Reloads config without restart"""
        old_config = self.config.copy()
        self.load_config()
        
        # Detect changes
        changes = self._diff_config(old_config, self.config)
        
        if changes:
            logger.info(f"Config changes detected: {changes}")
            self._notify_observers(changes)
    
    def _diff_config(self, old, new):
        """Returns list of changed keys"""
        changes = []
        for key in new:
            if key not in old or old[key] != new[key]:
                changes.append(key)
        return changes
    
    def register_observer(self, callback):
        """Register callback for config changes"""
        self.observers.append(callback)
    
    def _notify_observers(self, changes):
        """Notify all observers of changes"""
        for callback in self.observers:
            callback(changes)
    
    def start_watching(self):
        """Watch config file for changes"""
        event_handler = ConfigFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, os.path.dirname(self.config_path))
        observer.start()
```

---

### **5.2: Per-Plugin Database Setup**
**Duration:** 1 day

**File:** `src/core/plugin_database.py`

```python
import sqlite3
import os
from typing import Dict

class PluginDatabase:
    """
    Manages isolated database for each plugin.
    """
    
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.db_path = f"data/zepix_{plugin_id}.db"
        self.connection = None
        self._initialize()
    
    def _initialize(self):
        """Creates database and schema"""
        if not os.path.exists(self.db_path):
            logger.info(f"Creating new database for {self.plugin_id}")
            self.connection = sqlite3.connect(self.db_path)
            self._create_schema()
        else:
            self.connection = sqlite3.connect(self.db_path)
    
    def _create_schema(self):
        """Creates plugin database schema"""
        cursor = self.connection.cursor()
        
        # Plugin info table
        cursor.execute("""
            CREATE TABLE plugin_info (
                plugin_id TEXT PRIMARY KEY,
                version TEXT,
                last_started TIMESTAMP,
                total_runtime_hours REAL
            )
        """)
        
        # Trades table
        cursor.execute("""
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
                close_reason TEXT,
                signal_data TEXT
            )
        """)
        
        # Daily stats table
        cursor.execute("""
            CREATE TABLE daily_stats (
                date TEXT PRIMARY KEY,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_profit_pips REAL DEFAULT 0,
                total_profit_dollars REAL DEFAULT 0
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX idx_trades_status ON trades(status)")
        cursor.execute("CREATE INDEX idx_trades_symbol ON trades(symbol)")
        
        self.connection.commit()
        logger.info(f"✅ Schema created for {self.plugin_id}")
    
    def save_trade(self, trade_data: Dict):
        """Saves trade to plugin database"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO trades 
            (mt5_ticket, symbol, direction, lot_size, entry_price, sl_price, tp_price, signal_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_data["ticket"],
            trade_data["symbol"],
            trade_data["direction"],
            trade_data["lot_size"],
            trade_data["entry_price"],
            trade_data["sl_price"],
            trade_data["tp_price"],
            json.dumps(trade_data.get("signal_data", {}))
        ))
        self.connection.commit()
```

---

### **5.3: Plugin Config Hot-Reload**
**Duration:** 4 hours

**Implementation:**

```python
# In BaseLogicPlugin

class BaseLogicPlugin:
    def on_config_changed(self, changes):
        """
        Called when plugin config changes.
        Plugins can override to handle config updates.
        """
        logger.info(f"Plugin {self.plugin_id} config updated: {changes}")
        
        # Reload plugin-specific config
        self.config = self.config_manager.get_plugin_config(self.plugin_id)
        
        # Apply changes
        if "max_lot_size" in changes:
            self.max_lot = self.config["max_lot_size"]
        
        if "enabled" in changes:
            if self.config["enabled"]:
                self.on_plugin_enabled()
            else:
                self.on_plugin_disabled()
```

**User Command:**
```
/config_reload combined_v3
```

---

### **5.4: Database Migration Tools**
**Duration:** 4 hours

**Script:** `scripts/migrate_legacy_to_plugin_db.py`

```python
def migrate_trades_to_plugin_db(plugin_id: str, start_date: str):
    """
    Migrates trades from main DB to plugin DB.
    """
    main_db = sqlite3.connect("data/zepix_bot.db")
    plugin_db = PluginDatabase(plugin_id)
    
    # Query legacy trades
    cursor = main_db.cursor()
    trades = cursor.execute("""
        SELECT * FROM trades
        WHERE comment LIKE ?
        AND entry_time >= ?
    """, (f"%{plugin_id}%", start_date)).fetchall()
    
    logger.info(f"Migrating {len(trades)} trades for {plugin_id}...")
    
    # Insert into plugin DB
    for trade in trades:
        plugin_db.save_trade({
            "ticket": trade["mt5_ticket"],
            "symbol": trade["symbol"],
            # ... map all fields
        })
    
    logger.info("✅ Migration complete")
```

---

## 🧪 TESTING

### **Config Hot-Reload Test**
```python
def test_config_hot_reload():
    """Test config reload without restart"""
    # Modify config file
    config["plugins"]["combined_v3"]["max_lot_size"] = 2.0
    with open("config/config.json", "w") as f:
        json.write(config, f)
    
    # Wait for auto-reload (watchdog)
    time.sleep(2)
    
    # Verify plugin sees new config
    plugin = registry.get_plugin("combined_v3")
    assert plugin.max_lot == 2.0
```

### **Database Isolation Test**
```python
def test_plugin_database_isolation():
    """Plugins cannot access each other's DBs"""
    db_a = PluginDatabase("plugin_a")
    db_a.save_trade({...})
    
    db_b = PluginDatabase("plugin_b")
    trades_b = db_b.get_all_trades()
    
    assert len(trades_b) == 0  # Plugin B doesn't see Plugin A's trades
```

---

## ✅ COMPLETION CRITERIA

- [ ] ConfigManager implemented and tested
- [ ] Per-plugin databases created
- [ ] Config hot-reload working
- [ ] Migration scripts ready
- [ ] Zero downtime config updates verified
