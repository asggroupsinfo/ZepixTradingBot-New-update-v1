# 07_PLUGIN_SYSTEM_DEEP_DIVE.md

**Document Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Research Complete

---

## 🎯 OBJECTIVE

Detailed analysis of plugin lifecycle, discovery, loading, and execution mechanisms.

---

## 🔄 PLUGIN LIFECYCLE

```
┌─────────────┐
│  DISCOVERY  │ ← Scan plugin directory
└──────┬──────┘
       │
┌──────▼──────┐
│   LOADING   │ ← Import and instantiate
└──────┬──────┘
       │
┌──────▼──────┐
│INITIALIZATION│ ← Setup databases, configs
└──────┬──────┘
       │
┌──────▼──────┐
│   RUNNING   │ ← Process signals, execute trades
└──────┬──────┘
       │
┌──────▼──────┐
│  SHUTDOWN   │ ← Cleanup resources
└─────────────┘
```

---

## 📂 PLUGIN DIRECTORY STRUCTURE

```
src/logic_plugins/
├── _template/          # Template for new plugins
│   ├── plugin.py
│   ├── config.json
│   └── README.md
│
├── combined_v3/        # Migrated V3 logic
│   ├── plugin.py
│   ├── entry_logic.py
│   ├── exit_logic.py
│   ├── config.json
│   └── README.md
│
└── price_action_v6/    # Future V6 logic
    ├── plugin.py
    ├── config.json
    └── README.md
```

**Discovery Rules:**
- Directory must not start with `_` (template exception)
- Must contain `plugin.py` file
- Must have valid Python class inheriting `BaseLogicPlugin`

---

## 🔍 PLUGIN DISCOVERY MECHANISM

```python
class PluginRegistry:
    def discover_plugins(self) -> List[str]:
        """
        Scans plugin_dir for valid plugins.
        Returns list of plugin IDs (directory names).
        """
        plugin_dir = self.config["plugin_system"]["plugin_dir"]
        plugins = []
        
        for item in os.listdir(plugin_dir):
            path = os.path.join(plugin_dir, item)
            
            # Check validity
            if os.path.isdir(path) and not item.startswith("_"):
                if os.path.exists(os.path.join(path, "plugin.py")):
                    plugins.append(item)
        
        return plugins
```

**Validation:**
- Directory exists
- `plugin.py` exists
- `plugin.py` contains valid class
- Class name matches convention: `{PluginId}Plugin`

---

## 📥 PLUGIN LOADING

```python
def load_plugin(self, plugin_id: str) -> bool:
    """
    Dynamically imports and instantiates plugin.
    """
    try:
        # Convert path to module: src/logic_plugins → src.logic_plugins
        module_path = f"src.logic_plugins.{plugin_id}.plugin"
        plugin_module = importlib.import_module(module_path)
        
        # Get class: combined_v3 → CombinedV3Plugin
        class_name = f"{plugin_id.title().replace('_', '')}Plugin"
        plugin_class = getattr(plugin_module, class_name)
        
        # Load plugin config
        plugin_config = self.config.get("plugins", {}).get(plugin_id, {})
        
        # Instantiate
        plugin_instance = plugin_class(
            plugin_id=plugin_id,
            config=plugin_config,
            service_api=self.service_api
        )
        
        # Register
        self.plugins[plugin_id] = plugin_instance
        
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import plugin {plugin_id}: {e}")
        return False
```

**Error Handling:**
- ImportError → Plugin module not found
- AttributeError → Plugin class not found
- TypeError → Invalid constructor signature

---

## ⚙️ PLUGIN INITIALIZATION

Each plugin's `__init__` method:

```python
class CombinedV3Plugin(BaseLogicPlugin):
    def __init__(self, plugin_id, config, service_api):
        super().__init__(plugin_id, config, service_api)
        
        # 1. Set plugin metadata
        self.metadata = {
            "version": "1.0.0",
            "name": "Combined V3 Logic",
            "author": "Zepix Team"
        }
        
        # 2. Initialize plugin database
        self.db_path = f"data/zepix_{plugin_id}.db"
        self._initialize_database()
        
        # 3. Load plugin-specific config
        self.max_lot = config.get("max_lot_size", 1.0)
        self.risk_pct = config.get("risk_percentage", 1.0)
        
        # 4. Initialize sub-components
        self.entry_logic = EntryLogic(self)
        self.exit_logic = ExitLogic(self)
        
        logger.info(f"Plugin {plugin_id} initialized")
```

---

## 🔄 PLUGIN EXECUTION FLOW

### **Signal Processing**

```
TradingView Alert
       │
┌──────▼──────────┐
│ TradingEngine   │
└──────┬──────────┘
       │
┌──────▼──────────┐
│ PluginRegistry  │
│ .execute_hook() │
└──────┬──────────┘
       │
┌──────▼──────────┐
│ Plugin          │
│ .on_signal_     │
│  received()     │
└──────┬──────────┘
       │
┌──────▼──────────┐
│ Plugin Logic    │
│ (Entry/Exit)    │
└──────┬──────────┘
       │
┌──────▼──────────┐
│ ServiceAPI      │
│ .place_order()  │
└──────┬──────────┘
       │
┌──────▼──────────┐
│ MT5Client       │
└─────────────────┘
```

---

## 🔌 PLUGIN HOOKS

Plugins can define hooks for various events:

| Hook Name | Trigger | Purpose |
|---|---|---|
| `on_signal_received` | Alert arrives | Pre-process/filter signals |
| `on_order_placed` | Order executed | Log/notify |
| `on_position_update` | MT5 position changes | Profit booking, trailing |
| `on_daily_reset` | 03:35 IST daily | Reset stats, cleanup |
| `on_plugin_enabled` | Plugin activated | Resume monitoring |
| `on_plugin_disabled` | Plugin deactivated | Stop all activity |

**Example:**
```python
class MyPlugin(BaseLogicPlugin):
    async def on_signal_received(self, signal_data):
        """
        Called BEFORE core logic processes signal.
        Can modify or reject signal.
        """
        if signal_data["symbol"] not in self.allowed_symbols:
            logger.info(f"Rejecting signal for {signal_data['symbol']}")
            return False  # Reject
        
        # Modify signal
        signal_data["lot_multiplier"] = 1.5
        return signal_data  # Modified signal
```

---

## 🛡️ PLUGIN SANDBOXING

### **What Plugins CAN Do:**
✅ Call ServiceAPI methods
✅ Read/write to their own database
✅ Send Telegram notifications (via ServiceAPI)
✅ Access their own config
✅ Import standard Python libraries
✅ Define custom logic classes

### **What Plugins CANNOT Do:**
❌ Direct MT5 access (must use ServiceAPI)
❌ Access other plugins' databases
❌ Modify global config
❌ Access TradingEngine internals
❌ Execute system commands
❌ Import restricted modules (`os.system`, `subprocess`)

### **Enforcement:**
- ServiceAPI validates `plugin_id` on every call
- Database paths are plugin-specific
- No direct manager access (encapsulated in services)

---

## 📊 PLUGIN STATE PERSISTENCE

Each plugin maintains state in its database:

```sql
-- data/zepix_{plugin_id}.db

CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    symbol TEXT,
    direction TEXT,
    lot_size REAL,
    entry_price REAL,
    sl_price REAL,
    tp_price REAL,
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    profit_pips REAL,
    profit_dollars REAL,
    status TEXT  -- OPEN, CLOSED, PARTIAL
);

CREATE TABLE performance (
    date TEXT PRIMARY KEY,
    total_trades INTEGER,
    win_count INTEGER,
    loss_count INTEGER,
    total_profit REAL,
    max_drawdown REAL
);
```

---

## 🔄 PLUGIN HOT-RELOAD (Future)

**Goal:** Reload plugin without restarting bot.

**Mechanism:**
1. User sends `/reload_plugin combined_v3`
2. PluginRegistry:
   - Disables plugin
   - Closes all plugin's open trades (optional)
   - Unloads module from memory
   - Re-imports module
   - Re-instantiates plugin
   - Enables plugin

**Current Status:** Not implemented (Phase 7+)

---

## ✅ DECISION

**APPROVED:** Implement plugin system with discovery, loading, hook mechanism, and database isolation.

**Next Steps:**
1. Create `BaseLogicPlugin` abstract class
2. Implement `PluginRegistry`
3. Create template plugin
4. Test with dummy plugins
