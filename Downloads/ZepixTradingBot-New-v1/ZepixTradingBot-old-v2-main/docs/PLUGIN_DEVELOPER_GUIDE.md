# Plugin Developer Guide

**Version:** 1.0
**Date:** 2026-01-12
**Type:** Plugin Guide

---

## Plugin Architecture Overview

The V5 Hybrid Plugin Architecture allows you to create custom trading strategies as isolated plugins.

**Key Concepts:**
- **Plugin**: Self-contained trading strategy
- **ServiceAPI**: Interface to core services (orders, risk, notifications)
- **Plugin Database**: Isolated database per plugin
- **Plugin Config**: JSON configuration file

**Plugin Lifecycle:**
1. `on_load()` - Called when plugin is loaded
2. `on_enable()` - Called when plugin is enabled
3. `on_alert()` - Called when TradingView alert received
4. `on_disable()` - Called when plugin is disabled
5. `on_unload()` - Called when plugin is unloaded

## Creating a New Plugin

**Step 1: Create Plugin Directory**
```bash
mkdir -p src/logic_plugins/my_strategy
```

**Step 2: Create Plugin Files**

`src/logic_plugins/my_strategy/__init__.py`:
```python
from .plugin import MyStrategyPlugin

__all__ = ['MyStrategyPlugin']
```

`src/logic_plugins/my_strategy/plugin.py`:
```python
from src.core.plugin_system.base_plugin import BaseLogicPlugin
from src.core.plugin_system.service_api import ServiceAPI

class MyStrategyPlugin(BaseLogicPlugin):
    PLUGIN_ID = "my_strategy"
    PLUGIN_NAME = "My Strategy"
    VERSION = "1.0.0"
    
    def __init__(self, service_api: ServiceAPI):
        super().__init__(service_api)
        self.config = self.load_config()
    
    async def on_alert(self, alert_data: dict) -> None:
        # Process TradingView alert
        symbol = alert_data.get('symbol')
        direction = alert_data.get('direction')
        
        if direction == 'BUY':
            await self.service_api.place_order(
                symbol=symbol,
                direction='BUY',
                lot_size=0.1,
                plugin_id=self.PLUGIN_ID
            )
```

`src/logic_plugins/my_strategy/config.json`:
```json
{
    "plugin_id": "my_strategy",
    "name": "My Strategy",
    "version": "1.0.0",
    "enabled": true,
    "symbols": ["XAUUSD", "EURUSD"],
    "settings": {
        "risk_percentage": 1.0,
        "max_lot_size": 0.5
    }
}
```

## ServiceAPI Reference

The ServiceAPI provides access to core trading services.

**Order Execution:**
```python
await self.service_api.place_order(
    symbol="XAUUSD",
    direction="BUY",
    lot_size=0.1,
    stop_loss=2025.00,
    take_profit=2035.00,
    plugin_id=self.PLUGIN_ID
)

await self.service_api.close_position(
    ticket=12345,
    plugin_id=self.PLUGIN_ID
)

await self.service_api.modify_order(
    ticket=12345,
    stop_loss=2027.00,
    plugin_id=self.PLUGIN_ID
)
```

**Risk Management:**
```python
lot_size = await self.service_api.calculate_lot_size(
    symbol="XAUUSD",
    risk_percentage=1.5,
    stop_loss_pips=25,
    plugin_id=self.PLUGIN_ID
)

can_trade = await self.service_api.check_daily_limit(
    plugin_id=self.PLUGIN_ID
)
```

**Notifications:**
```python
await self.service_api.send_notification(
    message="Trade opened!",
    priority="high",
    plugin_id=self.PLUGIN_ID
)
```

## Plugin Database

Each plugin has its own isolated database.

**Accessing Plugin Database:**
```python
class MyStrategyPlugin(BaseLogicPlugin):
    def __init__(self, service_api: ServiceAPI):
        super().__init__(service_api)
        self.db = self.get_database()
    
    async def save_trade(self, trade_data: dict):
        await self.db.execute(
            "INSERT INTO trades (symbol, direction, lot) VALUES (?, ?, ?)",
            (trade_data['symbol'], trade_data['direction'], trade_data['lot'])
        )
    
    async def get_trades(self):
        return await self.db.fetch_all("SELECT * FROM trades")
```

**Database Location:**
`data/zepix_<plugin_id>.db`

**Schema Migration:**
Place migration files in `migrations/<plugin_id>/` directory.

## Testing Your Plugin

**Unit Tests:**
```python
import pytest
from src.logic_plugins.my_strategy.plugin import MyStrategyPlugin

class TestMyStrategyPlugin:
    def test_plugin_creation(self):
        plugin = MyStrategyPlugin(mock_service_api)
        assert plugin.PLUGIN_ID == "my_strategy"
    
    @pytest.mark.asyncio
    async def test_on_alert(self):
        plugin = MyStrategyPlugin(mock_service_api)
        await plugin.on_alert({'symbol': 'XAUUSD', 'direction': 'BUY'})
        # Assert order was placed
```

**Run Tests:**
```bash
pytest tests/test_my_strategy.py -v
```

**Shadow Mode Testing:**
Enable shadow mode to test without real trades:
```json
{
    "settings": {
        "shadow_mode": true
    }
}
```

## Best Practices

**1. Always Use ServiceAPI**
Never access MT5 directly. Use ServiceAPI for all trading operations.

**2. Handle Errors Gracefully**
```python
try:
    await self.service_api.place_order(...)
except OrderExecutionError as e:
    self.logger.error(f"Order failed: {e}")
    await self.service_api.send_notification(f"Order failed: {e}")
```

**3. Log Important Events**
```python
self.logger.info(f"Processing alert: {alert_data}")
self.logger.warning(f"Daily limit approaching")
self.logger.error(f"Failed to execute: {error}")
```

**4. Respect Rate Limits**
Don't spam notifications. Use appropriate priority levels.

**5. Clean Up Resources**
```python
async def on_unload(self):
    await self.db.close()
    self.logger.info("Plugin unloaded")
```
