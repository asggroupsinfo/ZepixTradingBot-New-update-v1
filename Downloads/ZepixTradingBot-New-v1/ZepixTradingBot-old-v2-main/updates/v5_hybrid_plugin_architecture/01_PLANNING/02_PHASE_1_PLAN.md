# 📘 PHASE 1 DETAILED PLAN - CORE PLUGIN SYSTEM FOUNDATION

**Phase:** 1 of 6  
**Duration:** Week 2 (5-7 days)  
**Complexity:** 🔴 HIGH  
**Dependencies:** Phase 0 Complete ✅  
**Goal:** Build plugin system WITHOUT breaking existing bot

---

## 🎯 PHASE 1 OBJECTIVES

**Primary Goal:**
Create a fully functional plugin system that can:
1. Load plugins dynamically
2. Register plugins with unique IDs
3. Execute plugin logic independently
4. Isolate plugin state (databases, configs)
5. Coexist with existing legacy code (NO breaking changes)

**Success Criteria:**
- ✅ Plugin system loads and registers test plugins
- ✅ Dummy plugin processes alerts successfully
- ✅ Existing bot functionality 100% intact
- ✅ Zero errors in plugin system tests
- ✅ Documentation complete and accurate

---

## 📁 FILES TO CREATE (7 Files)

### **1. `src/core/plugin_system/base_plugin.py`** (NEW)

**Purpose:** Abstract base class for all logic plugins

**Content:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseLogicPlugin(ABC):
    """
    Base class for all trading logic plugins.
    
    Plugins must implement:
    - process_entry_signal()
    - process_exit_signal()
    - process_reversal_signal()
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """
        Initialize plugin instance.
        
        Args:
            plugin_id: Unique identifier for this plugin
            config: Plugin-specific configuration
            service_api: Access to shared services
        """
        self.plugin_id = plugin_id
        self.config = config
        self.service_api = service_api
        self.logger = logging.getLogger(f"plugin.{plugin_id}")
        
        # Plugin metadata
        self.metadata = self._load_metadata()
        
        # Plugin state
        self.enabled = config.get("enabled", True)
        
        # Database connection (plugin-specific)
        self.db_path = f"data/zepix_{plugin_id}.db"
        
        self.logger.info(f"Initialized plugin: {plugin_id}")
    
    @abstractmethod
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process entry signal and execute trade.
        
        Args:
            alert: Alert data (ZepixV3Alert or similar)
            
        Returns:
            dict: Execution result with trade details
        """
        pass
    
    @abstractmethod
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process exit signal and close trades.
        
        Args:
            alert: Exit alert data
            
        Returns:
            dict: Exit execution result
        """
        pass
    
    @abstractmethod
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process reversal signal (close + opposite entry).
        
        Args:
            alert: Reversal alert data
            
        Returns:
            dict: Reversal execution result
        """
        pass
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "Base plugin",
            "supported_signals": []
        }
    
    def validate_alert(self, alert: Any) -> bool:
        """
        Validate alert before processing.
        
        Override for custom validation logic.
        """
        return True
    
    def get_database_connection(self):
        """Get plugin's isolated database connection"""
        import sqlite3
        return sqlite3.connect(self.db_path)
    
    def enable(self):
        """Enable this plugin"""
        self.enabled = True
        self.logger.info(f"Plugin {self.plugin_id} enabled")
    
    def disable(self):
        """Disable this plugin"""
        self.enabled = False
        self.logger.info(f"Plugin {self.plugin_id} disabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        return {
            "plugin_id": self.plugin_id,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "database": self.db_path
        }
```

**Testing:**
- Unit test: Can instantiate (with mock)
- Unit test: Abstract methods enforced
- Unit test: Enable/disable works

---

### **2. `src/core/plugin_system/plugin_registry.py`** (NEW)

**Purpose:** Manage plugin lifecycle (loading, registration, execution)

**Content:**
```python
import importlib
import os
from typing import Dict, Optional, List
import logging

from .base_plugin import BaseLogicPlugin

logger = logging.getLogger(__name__)

class PluginRegistry:
    """
    Central registry for all trading logic plugins.
    
    Responsibilities:
    - Discover plugins from plugin directory
    - Load and initialize plugins
    - Route alerts to correct plugin
    - Manage plugin lifecycle
    """
    
    def __init__(self, config: Dict, service_api):
        """
        Initialize plugin registry.
        
        Args:
            config: Bot configuration
            service_api: Shared services API
        """
        self.config = config
        self.service_api = service_api
        self.plugins: Dict[str, BaseLogicPlugin] = {}
        
        self.plugin_dir = config.get("plugin_system", {}).get("plugin_dir", "src/logic_plugins")
        
        logger.info("Plugin registry initialized")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directory.
        
        Returns:
            list: Plugin directory names
        """
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return []
        
        plugins = []
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            # Check if it's a valid plugin directory
            if os.path.isdir(plugin_path) and not item.startswith("_"):
                if os.path.exists(os.path.join(plugin_path, "plugin.py")):
                    plugins.append(item)
        
        logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins
    
    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load and register a single plugin.
        
        Args:
            plugin_id: Plugin identifier (directory name)
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            # Import plugin module
            module_path = f"{self.plugin_dir.replace('/', '.')}.{plugin_id}.plugin"
            plugin_module = importlib.import_module(module_path)
            
            # Get plugin class
            plugin_class = getattr(plugin_module, f"{plugin_id.title().replace('_', '')}Plugin")
            
            # Load plugin config
            plugin_config = self.config.get("plugins", {}).get(plugin_id, {})
            
            # Instantiate plugin
            plugin_instance = plugin_class(
                plugin_id=plugin_id,
                config=plugin_config,
                service_api=self.service_api
            )
            
            # Register
            self.plugins[plugin_id] = plugin_instance
            
            logger.info(f"Loaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    def load_all_plugins(self):
        """Discover and load all available plugins"""
        plugins = self.discover_plugins()
        
        for plugin_id in plugins:
            self.load_plugin(plugin_id)
        
        logger.info(f"Loaded {len(self.plugins)} plugins")
    
    def get_plugin(self, plugin_id: str) -> Optional[BaseLogicPlugin]:
        """
        Get plugin instance by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            BaseLogicPlugin or None
        """
        return self.plugins.get(plugin_id)
    
    async def route_alert_to_plugin(self, alert, plugin_id: str):
        """
        Route alert to specified plugin.
        
        Args:
            alert: Alert data
            plugin_id: Target plugin ID
            
        Returns:
            dict: Execution result from plugin
        """
        plugin = self.get_plugin(plugin_id)
        
        if not plugin:
            raise ValueError(f"Plugin not found: {plugin_id}")
        
        if not plugin.enabled:
            logger.warning(f"Plugin {plugin_id} is disabled, skipping alert")
            return {"skipped": True, "reason": "plugin_disabled"}
        
        # Route based on alert type
        signal_type = getattr(alert, "signal_type", None)
        
        if "entry" in signal_type.lower():
            return await plugin.process_entry_signal(alert)
        elif "exit" in signal_type.lower():
            return await plugin.process_exit_signal(alert)
        elif "reversal" in signal_type.lower():
            return await plugin.process_reversal_signal(alert)
        else:
            logger.warning(f"Unknown signal type: {signal_type}")
            return {"error": "unknown_signal_type"}
    
    def get_all_plugins(self) -> Dict[str, BaseLogicPlugin]:
        """Get all registered plugins"""
        return self.plugins
    
    def get_plugin_status(self, plugin_id: str) -> Optional[Dict]:
        """Get status of specific plugin"""
        plugin = self.get_plugin(plugin_id)
        return plugin.get_status() if plugin else None
```

**Testing:**
- Unit test: Plugin discovery works
- Unit test: Plugin loading works
- Unit test: Alert routing works
- Integration test: Load dummy plugin

---

### **3. `src/core/plugin_system/__init__.py`** (NEW)

```python
"""
Plugin system for Zepix Trading Bot.

Enables multiple independent trading logics to coexist.
"""

from .base_plugin import BaseLogicPlugin
from .plugin_registry import PluginRegistry

__all__ = ["BaseLogicPlugin", "PluginRegistry"]
```

---

### **4. `src/logic_plugins/_template/plugin.py`** (NEW)

**Purpose:** Template for creating new plugins

```python
from src.core.plugin_system import BaseLogicPlugin
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TemplatePlugin(BaseLogicPlugin):
    """
    Template plugin - copy this to create new plugins.
    
    Steps to create a new plugin:
    1. Copy this template directory
    2. Rename to your plugin ID (e.g., `my_logic`)
    3. Update class name (e.g., `MyLogicPlugin`)
    4. Implement process_entry_signal, process_exit_signal, process_reversal_signal
    5. Update config.json with your plugin settings
    6. Register plugin in main config
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        super().__init__(plugin_id, config, service_api)
        
        # Plugin-specific initialization
        self.logger.info(f"Template Plugin '{plugin_id}' initialized")
    
    async def process_entry_signal(self, alert) -> Dict[str, Any]:
        """
        Process entry signal.
        
        Example implementation:
        1. Validate alert
        2. Calculate lot size using service_api.risk_management
        3. Place order using service_api.order_execution
        4. Record trade in database
        5. Send notification using service_api.telegram
        """
        self.logger.info(f"Processing entry signal: {alert.symbol}")
        
        # TODO: Implement your entry logic
        
        return {
            "success": True,
            "message": "Entry processed (template)"
        }
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        """Process exit signal"""
        self.logger.info(f"Processing exit signal: {alert.symbol}")
        
        # TODO: Implement your exit logic
        
        return {
            "success": True,
            "message": "Exit processed (template)"
        }
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        """Process reversal signal"""
        self.logger.info(f"Processing reversal signal: {alert.symbol}")
        
        # TODO: Implement your reversal logic
        
        return {
            "success": True,
            "message": "Reversal processed (template)"
        }
```

---

### **5. `src/logic_plugins/_template/config.json`** (NEW)

```json
{
  "plugin_id": "_template",
  "enabled": false,
  "description": "Template plugin - copy to create new plugins",
  "version": "1.0.0",
  "author": "Zepix Team",
  
  "database": {
    "path": "data/zepix_template.db",
    "backup_enabled": true
  },
  
  "trading_settings": {
    "max_concurrent_trades": 3,
    "risk_per_trade": 0.01,
    "enabled_symbols": ["XAUUSD", "EURUSD"]
  },
  
  "notification_settings": {
    "send_entry_alerts": true,
    "send_exit_alerts": true,
    "telegram_tag": "[TEMPLATE]"
  }
}
```

---

### **6. `src/logic_plugins/_template/README.md`** (NEW)

```markdown
# Template Plugin

This is a template for creating new trading logic plugins.

## Creating a New Plugin

1. **Copy this directory:**
   ```bash
   cp -r src/logic_plugins/_template src/logic_plugins/my_logic
   ```

2. **Update plugin.py:**
   - Rename class to `MyLogic Plugin`
   - Implement entry/exit/reversal logic
   
3. **Update config.json:**
   - Set `plugin_id` to `my_logic`
   - Configure trading settings
   
4. **Register in main config:**
   ```json
   {
     "plugins": {
       "my_logic": {
         "enabled": true,
         "config_path": "src/logic_plugins/my_logic/config.json"
       }
     }
   }
   ```

5. **Test:**
   ```bash
   python scripts/test_plugin.py my_logic
   ```

## Plugin API

Plugins have access to `service_api` with these services:

- `service_api.order_execution` - Place/close orders
- `service_api.risk_management` - Lot calculations
- `service_api.profit_booking` - Profit booking chains
- `service_api.reentry` - Re-entry systems
- `service_api.telegram` - Send notifications
- `service_api.analytics` - Performance tracking

See PLUGIN_DEVELOPER_GUIDE.md for complete API reference.
```

---

### **7. `scripts/test_plugin.py`** (NEW)

**Purpose:** Test plugin system with dummy alerts

```python
import asyncio
import sys
sys.path.append(".")

from src.core.plugin_system import PluginRegistry
from models.alerts import ZepixV3Alert

async def test_plugin(plugin_id: str):
    """Test a single plugin"""
    
    # Mock config and service API
    config = {
        "plugin_system": {
            "plugin_dir": "src/logic_plugins"
        },
        "plugins": {
            plugin_id: {
                "enabled": True
            }
        }
    }
    
    # TODO: Create mock ServiceAPI
    mock_service_api = None
    
    # Initialize registry
    registry = PluginRegistry(config, mock_service_api)
    
    # Load plugin
    success = registry.load_plugin(plugin_id)
    
    if not success:
        print(f"❌ Failed to load plugin: {plugin_id}")
        return False
    
    print(f"✅ Plugin loaded: {plugin_id}")
    
    # Create dummy alert
    dummy_alert = ZepixV3Alert(
        symbol="XAUUSD",
        direction="BUY",
        signal_type="entry",
        tf="5m",
        # ... etc
    )
    
    # Process alert
    result = await registry.route_alert_to_plugin(dummy_alert, plugin_id)
    
    print(f"Result: {result}")
    
    return result.get("success", False)

if __name__ == "__main__":
    plugin_id = sys.argv[1] if len(sys.argv) > 1 else "_template"
    
    success = asyncio.run(test_plugin(plugin_id))
    
    sys.exit(0 if success else 1)
```

---

## 🔧 FILES TO MODIFY (3 Files)

### **1. `config.json`** (ADD)

**Add plugin system configuration:**

```json
{
  // ... existing config ...
  
  "plugin_system": {
    "enabled": false,  // Start disabled
    "plugin_dir": "src/logic_plugins",
    "auto_discover": true,
    "fallback_to_legacy": true  // Safety: use legacy if plugin fails
  },
  
  "plugins": {
    // Plugins registered here after Phase 4
  }
}
```

**Testing:** Config validation passes

---

### **2. `src/main.py`** (ADD - Optional in Phase 1)

**Add plugin registry initialization (disabled by default):**

```python
# In lifespan() function, around line 200

if config.get("plugin_system", {}).get("enabled", False):
    # Future: Initialize plugin registry
    # plugin_registry = PluginRegistry(config, service_api)
    # plugin_registry.load_all_plugins()
    logger.info("Plugin system: ENABLED (Phase 1 testing)")
else:
    logger.info("Plugin system: DISABLED (using legacy)")
```

**Risk:** 🟢 LOW - Feature flag prevents activation  
**Testing:** Bot starts normally with plugin_system=false

---

### **3. `.gitignore`** (ADD)

**Ignore plugin databases:**

```
# Plugin databases
data/zepix_*.db
!data/zepix_bot.db  # Keep original
```

---

## 🧪 TESTING STRATEGY

### **Unit Tests (Create: `tests/test_plugin_system.py`)**

```python
import pytest
from src.core.plugin_system import BaseLogicPlugin, PluginRegistry

class DummyPlugin(BaseLogicPlugin):
    async def process_entry_signal(self, alert):
        return {"success": True}
    
    async def process_exit_signal(self, alert):
        return {"success": True}
    
    async def process_reversal_signal(self, alert):
        return {"success": True}

def test_base_plugin_instantiation():
    """Test BaseLogicPlugin can be instantiated via subclass"""
    plugin = DummyPlugin("test_plugin", {}, None)
    
    assert plugin.plugin_id == "test_plugin"
    assert plugin.enabled == True

def test_plugin_enable_disable():
    """Test plugin enable/disable"""
    plugin = DummyPlugin("test", {}, None)
    
    plugin.disable()
    assert plugin.enabled == False
    
    plugin.enable()
    assert plugin.enabled == True

# ... 10 more unit tests
```

**Run:** `pytest tests/test_plugin_system.py -v`

---

### **Integration Test**

```bash
# Test plugin discovery
python scripts/test_plugin.py _template

# Expected output:
# ✅ Plugin loaded: _template
# Result: {'success': True, 'message': 'Entry processed (template)'}
```

---

### **Regression Test**

```bash
# Ensure existing bot still works
python src/main.py

# Check logs:
grep "Plugin system: DISABLED" logs/*.log

# Send test alert to /webhook
# Verify V3 logic still processes correctly
```

---

## 📊 SUCCESS CRITERIA

### **Exit Criteria (Must Pass All):**

- [ ] **Code Quality:**
  - [ ] All 7 new files created
  - [ ] Code follows existing style
  - [ ] Type hints present
  - [ ] Docstrings complete
  
- [ ] **Functionality:**
  - [ ] BaseLogicPlugin works
  - [ ] PluginRegistry discovers plugins
  - [ ] Template plugin loads
  - [ ] Alert routing works
  
- [ ] **No Regressions:**
  - [ ] Existing bot starts normally
  - [ ] V3 alerts processed correctly
  - [ ] No new errors in logs
  - [ ] All existing tests pass
  
- [ ] **Testing:**
  - [ ] Unit tests pass (100%)
  - [ ] Integration test passes
  - [ ] Regression test passes
  
- [ ] **Documentation:**
  - [ ] README.md updated with plugin system
  - [ ] PLUGIN_DEVELOPER_GUIDE.md created
  - [ ] Code comments complete

### **User Approval Required:**
- [ ] User confirms bot still works normally
- [ ] User reviews plugin template
- [ ] User approves proceeding to Phase 2

---

## 🚨 ROLLBACK PROCEDURE

If Phase 1 fails:

```bash
# 1. Disable plugin system
# Edit config.json: "plugin_system": { "enabled": false }

# 2. Delete new files
rm -rf src/core/plugin_system/
rm -rf src/logic_plugins/
rm scripts/test_plugin.py

# 3. Revert modified files
git checkout config.json
git checkout src/main.py
git checkout .gitignore

# 4. Restart bot
systemctl restart zepix-bot

# 5. Verify
curl http://localhost:8000/health
```

---

## 📅 PHASE 1 TIMELINE

| Day | Task | Duration | Owner |
|-----|------|----------|-------|
| 1 | Create BaseLogicPlugin | 4 hours | Agent |
| 1 | Create PluginRegistry | 4 hours | Agent |
| 2 | Create template plugin | 3 hours | Agent |
| 2 | Create test script | 2 hours | Agent |
| 2 | Unit tests | 4 hours | Agent |
| 3 | Integration testing | 6 hours | Agent + User |
| 4 | Documentation | 4 hours | Agent |
| 4 | Code review | 2 hours | User |
| 5 | Final testing | 4 hours | Agent + User |
| 5 | User approval | - | User |

**Total:** 5 days (33 hours development + testing + review)

---

**Phase 1 Status:** PLANNED ✅  
**Ready to Execute:** Pending Phase 0 Approval  
**Next Phase:** Phase 2 - Multi-Telegram System
