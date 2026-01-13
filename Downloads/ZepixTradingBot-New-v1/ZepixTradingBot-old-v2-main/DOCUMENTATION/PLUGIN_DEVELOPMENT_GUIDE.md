# V6 Plugin Development Guide

## Overview

This guide explains how to build trading logic plugins for the V5 Hybrid Plugin Architecture. The system supports both V3 (Combined Logic) and V6 (Price Action) plugins, each with their own databases and configurations.

## Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │         Plugin Registry             │
                    │   (src/core/plugin_system/)         │
                    └─────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  V3 Combined    │     │  V6 Price       │     │  Your Custom    │
    │  Logic Plugin   │     │  Action Plugin  │     │  Plugin         │
    └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
             │                       │                       │
             ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │ zepix_combined  │     │ zepix_price_    │     │ zepix_your_     │
    │ .db             │     │ action.db       │     │ plugin.db       │
    └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Quick Start: Hello World Plugin

The fastest way to learn is to study the Hello World example plugin at `src/logic_plugins/hello_world/plugin.py`.

### Step 1: Create Plugin Directory

```bash
mkdir -p src/logic_plugins/my_strategy
touch src/logic_plugins/my_strategy/__init__.py
touch src/logic_plugins/my_strategy/plugin.py
```

### Step 2: Create Plugin Class

```python
# src/logic_plugins/my_strategy/plugin.py

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MyStrategyPlugin:
    """
    My custom trading strategy plugin.
    """
    
    PLUGIN_ID = "my_strategy"
    PLUGIN_NAME = "My Strategy"
    VERSION = "1.0.0"
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api: Any):
        """
        Initialize the plugin.
        
        Args:
            plugin_id: Unique identifier for this plugin instance
            config: Plugin configuration dictionary
            service_api: ServiceAPI instance for accessing core services
        """
        self.plugin_id = plugin_id
        self.config = config
        self.service_api = service_api
        self.enabled = config.get("enabled", True)
        
        logger.info(f"[{self.plugin_id}] Plugin initialized")
    
    async def on_signal_received(self, signal_data: Dict[str, Any]) -> bool:
        """
        Process incoming trading signal.
        
        Args:
            signal_data: Signal information from TradingView
        
        Returns:
            bool: True if trade was placed, False otherwise
        """
        if not self.enabled:
            return False
        
        symbol = signal_data.get("symbol")
        direction = signal_data.get("direction")
        
        logger.info(f"[{self.plugin_id}] Processing: {symbol} {direction}")
        
        # Your trading logic here
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "plugin_id": self.plugin_id,
            "name": self.PLUGIN_NAME,
            "version": self.VERSION,
            "enabled": self.enabled
        }
```

### Step 3: Register Plugin

Add to `src/logic_plugins/__init__.py`:

```python
from .my_strategy.plugin import MyStrategyPlugin
```

## BaseLogicPlugin (Abstract Base Class)

For more advanced plugins, extend the `BaseLogicPlugin` class:

```python
from src.core.plugin_system.base_plugin import BaseLogicPlugin
from typing import Dict, Any

class MyAdvancedPlugin(BaseLogicPlugin):
    """Advanced plugin extending BaseLogicPlugin."""
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        super().__init__(plugin_id, config, service_api)
        # Custom initialization
    
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        """Process entry signal - REQUIRED."""
        # Your entry logic
        return {"success": True, "ticket": 12345}
    
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """Process exit signal - REQUIRED."""
        # Your exit logic
        return {"success": True, "closed": 1}
    
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        """Process reversal signal - REQUIRED."""
        # Your reversal logic
        return {"success": True}
```

### BaseLogicPlugin Features

| Feature | Description |
|---------|-------------|
| `plugin_id` | Unique identifier |
| `config` | Plugin configuration |
| `service_api` | Access to core services |
| `db_path` | Per-plugin database path |
| `enabled` | Enable/disable state |
| `on_config_changed()` | Hot-reload callback |

## ServiceAPI Reference

The `service_api` provides access to core trading services:

### Order Service

```python
# Place an order
ticket = await self.service_api.orders.place_order(
    symbol="XAUUSD",
    direction="BUY",
    lot_size=0.1,
    sl_price=2025.00,
    tp_price=2035.00,
    comment="my_strategy_entry"
)

# Close a position
success = await self.service_api.orders.close_position(ticket)

# Get open orders
orders = await self.service_api.orders.get_open_orders(symbol="XAUUSD")
```

### Risk Service

```python
# Calculate lot size based on risk
lot_size = await self.service_api.risk.calculate_lot_size(
    symbol="XAUUSD",
    risk_percentage=1.0,
    stop_loss_pips=25
)

# Check daily limit
status = await self.service_api.risk.check_daily_limit(self.plugin_id)
if not status["can_trade"]:
    logger.warning("Daily limit reached")
```

### Trend Service

```python
# Get current trend
trend = await self.service_api.trend.get_current_trend(
    symbol="XAUUSD",
    timeframe="15m"
)
# Returns: {"direction": "BULLISH", "strength": 0.75}
```

### Notification Service

```python
# Send notification
await self.service_api.notifications.send(
    message="Trade opened: XAUUSD BUY 0.1 lots",
    priority="high"  # "low", "normal", "high", "critical"
)
```

## V6 Price Action Plugin Structure

V6 plugins follow a timeframe-specific structure:

```
src/logic_plugins/
├── price_action_1m/
│   └── plugin.py          # 1-minute strategy
├── price_action_5m/
│   └── plugin.py          # 5-minute strategy
├── price_action_15m/
│   └── plugin.py          # 15-minute strategy
├── price_action_1h/
│   └── plugin.py          # 1-hour strategy
└── price_action_v6/
    ├── plugin.py          # Main V6 plugin
    ├── adx_integration.py # ADX filter
    ├── momentum_integration.py
    └── timeframe_strategies.py
```

### V6 Order Routing Rules

| Timeframe | Order Type | Description |
|-----------|------------|-------------|
| 1M | ORDER B only | Quick scalp, single order |
| 5M | DUAL ORDERS | Order A + Order B |
| 15M | ORDER A only | Swing entry, single order |
| 1H | ORDER A only | Position trade, single order |

### V6 ADX Filter

```python
from src.logic_plugins.price_action_v6.adx_integration import ADXIntegration

adx = ADXIntegration()

# Check if ADX allows entry
if adx.should_enter(adx_value=25, threshold=20):
    # Proceed with entry
    pass
```

## Configuration

### Plugin Configuration Schema

```python
# src/config/schemas.py

from dataclasses import dataclass
from typing import List

@dataclass
class MyPluginConfig:
    plugin_id: str = "my_strategy"
    enabled: bool = True
    max_lot_size: float = 1.0
    risk_percent: float = 1.0
    supported_symbols: List[str] = None
    
    def __post_init__(self):
        if self.supported_symbols is None:
            self.supported_symbols = ["XAUUSD", "EURUSD"]
```

### Config File (config/plugins/my_strategy.json)

```json
{
    "plugin_id": "my_strategy",
    "enabled": true,
    "max_lot_size": 0.5,
    "risk_percent": 1.0,
    "supported_symbols": ["XAUUSD", "EURUSD", "GBPUSD"],
    "entry_threshold": 7,
    "custom_settings": {
        "use_trend_filter": true,
        "min_adx": 20
    }
}
```

### Hot-Reload Support

Plugins can respond to configuration changes in real-time:

```python
def on_config_changed(self, changes: List[str]) -> None:
    """Called when config file changes."""
    self.logger.info(f"Config updated: {changes}")
    
    # Reload specific settings
    if "max_lot_size" in changes:
        self.max_lot = self.config.get("max_lot_size", 1.0)
    
    if "enabled" in changes:
        self.enabled = self.config.get("enabled", True)
```

## Database Operations

Each plugin has its own isolated database:

```python
def get_database_connection(self):
    """Get plugin's isolated database connection."""
    import sqlite3
    return sqlite3.connect(self.db_path)

def save_trade(self, trade_data: Dict[str, Any]):
    """Save trade to plugin database."""
    conn = self.get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            ticket INTEGER,
            symbol TEXT,
            direction TEXT,
            lot_size REAL,
            entry_price REAL,
            sl_price REAL,
            tp_price REAL,
            timestamp TEXT
        )
    """)
    
    cursor.execute("""
        INSERT INTO trades (ticket, symbol, direction, lot_size, 
                           entry_price, sl_price, tp_price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade_data["ticket"],
        trade_data["symbol"],
        trade_data["direction"],
        trade_data["lot_size"],
        trade_data["entry_price"],
        trade_data["sl_price"],
        trade_data["tp_price"],
        trade_data["timestamp"]
    ))
    
    conn.commit()
    conn.close()
```

## Signal Processing

### Signal Data Structure

```python
signal_data = {
    "type": "entry",           # entry, exit, reversal, trend
    "symbol": "XAUUSD",
    "direction": "BUY",        # BUY, SELL
    "timeframe": "15m",
    "price": 2030.50,
    "sl_price": 2025.00,
    "tp_price": 2040.00,
    "consensus_score": 8,      # 0-10
    "adx": 25.0,
    "conf_level": "HIGH"       # LOW, MEDIUM, HIGH
}
```

### Signal Validation

```python
def validate_signal(self, signal: Dict[str, Any]) -> bool:
    """Validate incoming signal."""
    
    # Check required fields
    required = ["symbol", "direction", "timeframe"]
    for field in required:
        if field not in signal:
            return False
    
    # Check symbol support
    if signal["symbol"] not in self.config.supported_symbols:
        return False
    
    # Check consensus score
    if signal.get("consensus_score", 0) < self.config.entry_threshold:
        return False
    
    return True
```

## Error Handling

```python
async def on_signal_received(self, signal_data: Dict[str, Any]) -> bool:
    """Process signal with proper error handling."""
    try:
        # Validate
        if not self.validate_signal(signal_data):
            self.logger.warning(f"Invalid signal: {signal_data}")
            return False
        
        # Process
        result = await self._execute_trade(signal_data)
        
        # Log success
        self.logger.info(f"Trade executed: {result}")
        return True
        
    except ConnectionError as e:
        self.logger.error(f"Connection error: {e}")
        # Retry logic here
        return False
        
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return False
```

## Testing Your Plugin

### Unit Tests

```python
# tests/test_my_strategy.py

import pytest
from src.logic_plugins.my_strategy.plugin import MyStrategyPlugin

class TestMyStrategyPlugin:
    
    def test_plugin_initialization(self):
        """Test plugin initializes correctly."""
        config = {"enabled": True, "max_lot_size": 0.5}
        plugin = MyStrategyPlugin("my_strategy", config, MockServiceAPI())
        
        assert plugin.plugin_id == "my_strategy"
        assert plugin.enabled == True
    
    @pytest.mark.asyncio
    async def test_signal_processing(self):
        """Test signal processing."""
        plugin = MyStrategyPlugin("my_strategy", {}, MockServiceAPI())
        
        signal = {
            "symbol": "XAUUSD",
            "direction": "BUY",
            "consensus_score": 8
        }
        
        result = await plugin.on_signal_received(signal)
        assert result == True
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_trade_flow(self):
    """Test complete trade flow."""
    plugin = MyStrategyPlugin("my_strategy", {}, real_service_api)
    
    # Entry signal
    entry_result = await plugin.on_signal_received({
        "type": "entry",
        "symbol": "XAUUSD",
        "direction": "BUY"
    })
    assert entry_result == True
    
    # Exit signal
    exit_result = await plugin.on_signal_received({
        "type": "exit",
        "symbol": "XAUUSD"
    })
    assert exit_result == True
```

## Best Practices

### 1. Plugin Isolation

Each plugin should be completely independent:

```python
# GOOD: Use plugin-specific database
self.db_path = f"data/zepix_{self.plugin_id}.db"

# BAD: Share database with other plugins
self.db_path = "data/shared.db"
```

### 2. Logging

Use structured logging with plugin ID:

```python
# GOOD
self.logger.info(f"[{self.plugin_id}] Trade placed: {ticket}")

# BAD
print("Trade placed")
```

### 3. Configuration

Use dataclasses for type-safe configuration:

```python
@dataclass
class MyPluginConfig:
    max_lot_size: float = 1.0
    risk_percent: float = 1.0
```

### 4. Error Handling

Always handle errors gracefully:

```python
try:
    result = await self.service_api.orders.place_order(...)
except Exception as e:
    self.logger.error(f"Order failed: {e}")
    return False
```

### 5. Testing

Write tests for all critical paths:

```python
def test_entry_signal(self):
    """Test entry signal processing."""
    pass

def test_exit_signal(self):
    """Test exit signal processing."""
    pass

def test_risk_limits(self):
    """Test risk limit enforcement."""
    pass
```

## Plugin Versioning

Use semantic versioning for your plugins:

```python
class MyPlugin:
    VERSION = "1.2.3"  # MAJOR.MINOR.PATCH
    
    # MAJOR: Breaking changes
    # MINOR: New features (backward compatible)
    # PATCH: Bug fixes
```

### Plugin Manifest

```json
{
    "plugin_id": "my_strategy",
    "version": "1.2.3",
    "min_core_version": "5.0.0",
    "dependencies": [
        {"plugin_id": "trend_monitor", "version": ">=1.0.0"}
    ],
    "author": "Your Name",
    "description": "My custom trading strategy"
}
```

## Deployment Checklist

Before deploying your plugin:

1. [ ] All tests pass
2. [ ] Configuration validated
3. [ ] Database migrations ready
4. [ ] Logging configured
5. [ ] Error handling complete
6. [ ] Documentation updated
7. [ ] Version number updated
8. [ ] Backward compatibility verified

## Example: Complete V6 Plugin

```python
"""
Complete V6 Price Action Plugin Example.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TradeRecord:
    ticket: int
    symbol: str
    direction: str
    lot_size: float
    entry_price: float
    sl_price: float
    tp_price: float

class PriceActionV6Example:
    """
    V6 Price Action Plugin for 15-minute timeframe.
    
    Features:
    - ADX filter (minimum 20)
    - Trend alignment check
    - ORDER A only (swing entries)
    - Per-plugin database
    """
    
    PLUGIN_ID = "price_action_15m_example"
    VERSION = "1.0.0"
    TIMEFRAME = "15m"
    ORDER_TYPE = "ORDER_A"  # Single order for 15M
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        self.plugin_id = plugin_id
        self.config = config
        self.service_api = service_api
        self.enabled = config.get("enabled", True)
        self._trades: List[TradeRecord] = []
        
        # V6 specific settings
        self.min_adx = config.get("min_adx", 20)
        self.min_conf_score = config.get("min_conf_score", 65)
        
        logger.info(f"[{self.plugin_id}] V6 Plugin initialized")
    
    async def on_signal_received(self, signal: Dict[str, Any]) -> bool:
        """Process V6 alert."""
        if not self.enabled:
            return False
        
        # Validate ADX
        adx = signal.get("adx", 0)
        if adx < self.min_adx:
            logger.info(f"[{self.plugin_id}] ADX too low: {adx}")
            return False
        
        # Validate confidence
        conf_score = signal.get("conf_score", 0)
        if conf_score < self.min_conf_score:
            logger.info(f"[{self.plugin_id}] Confidence too low: {conf_score}")
            return False
        
        # Check risk limits
        risk_status = await self.service_api.risk.check_daily_limit(self.plugin_id)
        if not risk_status.get("can_trade", True):
            logger.warning(f"[{self.plugin_id}] Daily limit reached")
            return False
        
        # Calculate lot size
        lot_size = await self.service_api.risk.calculate_lot_size(
            symbol=signal["symbol"],
            risk_percentage=self.config.get("risk_percent", 1.0),
            stop_loss_pips=signal.get("sl_pips", 25)
        )
        
        # Place ORDER A only (15M timeframe rule)
        ticket = await self.service_api.orders.place_order(
            symbol=signal["symbol"],
            direction=signal["direction"],
            lot_size=lot_size,
            sl_price=signal.get("sl_price", 0),
            tp_price=signal.get("tp2_price", 0),  # ORDER A uses TP2
            comment=f"{self.plugin_id}_order_a"
        )
        
        if ticket:
            trade = TradeRecord(
                ticket=ticket,
                symbol=signal["symbol"],
                direction=signal["direction"],
                lot_size=lot_size,
                entry_price=signal.get("price", 0),
                sl_price=signal.get("sl_price", 0),
                tp_price=signal.get("tp2_price", 0)
            )
            self._trades.append(trade)
            
            logger.info(f"[{self.plugin_id}] ORDER A placed: {ticket}")
            
            await self.service_api.notifications.send(
                f"V6 15M Entry: {signal['symbol']} {signal['direction']} @ {lot_size} lots",
                priority="high"
            )
            
            return True
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "plugin_id": self.plugin_id,
            "version": self.VERSION,
            "timeframe": self.TIMEFRAME,
            "order_type": self.ORDER_TYPE,
            "enabled": self.enabled,
            "active_trades": len(self._trades),
            "min_adx": self.min_adx,
            "min_conf_score": self.min_conf_score
        }
```

## Support

For questions or issues:

1. Check existing documentation in `DOCUMENTATION/`
2. Review the Hello World example at `src/logic_plugins/hello_world/`
3. Study the V6 plugins at `src/logic_plugins/price_action_*/`
4. Run tests: `pytest tests/test_15_developer_onboarding.py -v`

---

**Document Version:** 1.0
**Last Updated:** January 2026
**Architecture Version:** V5 Hybrid Plugin Architecture
