# API Reference

**Version:** 1.0
**Date:** 2026-01-12
**Type:** API Reference

---

This document provides a complete reference for all APIs in the V5 Hybrid Plugin Architecture.

# Service API

The Service API provides access to core trading services for plugins.

## Order Execution Service

APIs for placing, modifying, and closing orders.

### `async` service_api.place_dual_orders_v3()

**Place Dual Orders (V3)**

Place dual orders (Order A + Order B) for V3 Combined Logic plugin.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | str | Yes | Trading symbol (e.g., 'XAUUSD') |
| `direction` | str | Yes | Trade direction ('BUY' or 'SELL') |
| `lot_size_a` | float | Yes | Lot size for Order A |
| `lot_size_b` | float | Yes | Lot size for Order B |
| `stop_loss` | float | Yes | Stop loss price |
| `take_profit` | float | No | Take profit price |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Place BUY dual orders*

```python
result = await service_api.place_dual_orders_v3(
    symbol="XAUUSD",
    direction="BUY",
    lot_size_a=0.1,
    lot_size_b=0.2,
    stop_loss=2025.00,
    take_profit=2035.00,
    plugin_id="combined_v3"
)
```

### `async` service_api.place_order()

**Place Single Order**

Place a single order for any plugin.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | str | Yes | Trading symbol |
| `direction` | str | Yes | Trade direction |
| `lot_size` | float | Yes | Lot size |
| `stop_loss` | float | No | Stop loss price |
| `take_profit` | float | No | Take profit price |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Place single order*

```python
result = await service_api.place_order(
    symbol="EURUSD",
    direction="SELL",
    lot_size=0.1,
    stop_loss=1.0850,
    plugin_id="price_action_5m"
)
```

### `async` service_api.modify_order()

**Modify Order**

Modify an existing order's stop loss or take profit.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ticket` | int | Yes | Order ticket number |
| `stop_loss` | float | No | New stop loss price |
| `take_profit` | float | No | New take profit price |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Modify stop loss*

```python
result = await service_api.modify_order(
    ticket=12345,
    stop_loss=2027.00,
    plugin_id="combined_v3"
)
```

### `async` service_api.close_position()

**Close Position**

Close an open position.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ticket` | int | Yes | Position ticket number |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Close position*

```python
result = await service_api.close_position(
    ticket=12345,
    plugin_id="combined_v3"
)
```

### `async` service_api.close_position_partial()

**Close Position Partial**

Partially close an open position.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ticket` | int | Yes | Position ticket number |
| `lot_size` | float | Yes | Lot size to close |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Partial close*

```python
result = await service_api.close_position_partial(
    ticket=12345,
    lot_size=0.05,
    plugin_id="combined_v3"
)
```

## Risk Management Service

APIs for risk calculation and daily limit management.

### `async` service_api.calculate_lot_size()

**Calculate Lot Size**

Calculate lot size based on risk percentage and stop loss.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | str | Yes | Trading symbol |
| `risk_percentage` | float | Yes | Risk percentage (e.g., 1.5) |
| `stop_loss_pips` | float | Yes | Stop loss in pips |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Calculate lot size*

```python
lot_size = await service_api.calculate_lot_size(
    symbol="XAUUSD",
    risk_percentage=1.5,
    stop_loss_pips=25,
    plugin_id="combined_v3"
)
```

### `async` service_api.check_daily_limit()

**Check Daily Limit**

Check if plugin has reached daily loss limit.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Check daily limit*

```python
can_trade = await service_api.check_daily_limit(
    plugin_id="combined_v3"
)
if not can_trade:
    logger.warning("Daily limit reached")
```

### `async` service_api.get_risk_status()

**Get Risk Status**

Get current risk status for a plugin.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Get risk status*

```python
status = await service_api.get_risk_status(
    plugin_id="combined_v3"
)
print(f"Daily P&L: {status['daily_pnl']}")
print(f"Open risk: {status['open_risk']}")
```

## Notification Service

APIs for sending notifications and trade alerts.

### `async` service_api.send_notification()

**Send Notification**

Send a notification via Telegram.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `message` | str | Yes | Notification message |
| `priority` | str | No | Priority level ('low', 'normal', 'high', 'critical') |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Send notification*

```python
await service_api.send_notification(
    message="Trade opened: XAUUSD BUY 0.1 lot",
    priority="high",
    plugin_id="combined_v3"
)
```

### `async` service_api.send_trade_alert()

**Send Trade Alert**

Send a formatted trade alert.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `trade_data` | dict | Yes | Trade data dictionary |
| `alert_type` | str | Yes | Alert type ('entry', 'exit', 'modify') |
| `plugin_id` | str | Yes | Plugin identifier |

**Examples:**

*Send trade alert*

```python
await service_api.send_trade_alert(
    trade_data={
        "symbol": "XAUUSD",
        "direction": "BUY",
        "lot": 0.1,
        "entry": 2030.50,
        "sl": 2025.00,
        "tp": 2040.00
    },
    alert_type="entry",
    plugin_id="combined_v3"
)
```

## Trend Management Service

APIs for trend tracking and management.

### `async` service_api.get_trend_status()

**Get Trend Status**

Get current trend status for a symbol.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | str | Yes | Trading symbol |
| `timeframe` | str | No | Timeframe (e.g., '1H', '4H') |

**Examples:**

*Get trend status*

```python
trend = await service_api.get_trend_status(
    symbol="XAUUSD",
    timeframe="1H"
)
print(f"Trend: {trend['direction']}")
print(f"Strength: {trend['strength']}")
```

### `async` service_api.update_trend()

**Update Trend**

Update trend status for a symbol.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | str | Yes | Trading symbol |
| `direction` | str | Yes | Trend direction ('BULLISH', 'BEARISH', 'NEUTRAL') |
| `strength` | float | No | Trend strength (0-100) |
| `timeframe` | str | No | Timeframe |

**Examples:**

*Update trend*

```python
await service_api.update_trend(
    symbol="XAUUSD",
    direction="BULLISH",
    strength=75.5,
    timeframe="1H"
)
```

# Telegram Bot API

Commands available in the Telegram bots.

## Controller Bot Commands

Commands for managing the trading bot.

### `command` /status

**Status**

View bot health and active plugins.

**Examples:**

*Check status*

```python
/status
```

### `command` /enable_plugin <name>

**Enable Plugin**

Enable a plugin.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | str | Yes | Plugin name to enable |

**Examples:**

*Enable combined_v3*

```python
/enable_plugin combined_v3
```

### `command` /disable_plugin <name>

**Disable Plugin**

Disable a plugin.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | str | Yes | Plugin name to disable |

**Examples:**

*Disable combined_v3*

```python
/disable_plugin combined_v3
```

### `command` /emergency_stop

**Emergency Stop**

Stop all trading immediately. Closes all positions and disables all plugins.

**Examples:**

*Emergency stop*

```python
/emergency_stop
```

### `command` /config_reload <plugin>

**Config Reload**

Reload configuration for a plugin.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin` | str | Yes | Plugin name to reload config |

**Examples:**

*Reload config*

```python
/config_reload combined_v3
```

### `command` /daily_limit <plugin>

**Daily Limit**

Check daily loss limit status for a plugin.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin` | str | Yes | Plugin name |

**Examples:**

*Check daily limit*

```python
/daily_limit combined_v3
```

## Analytics Bot Commands

Commands for viewing performance reports.

### `command` /daily_report

**Daily Report**

Get today's P&L summary.

**Examples:**

*Get daily report*

```python
/daily_report
```

### `command` /weekly_report

**Weekly Report**

Get weekly performance report.

**Examples:**

*Get weekly report*

```python
/weekly_report
```

### `command` /plugin_stats

**Plugin Stats**

Get per-plugin performance breakdown.

**Examples:**

*Get plugin stats*

```python
/plugin_stats
```

### `command` /export_trades

**Export Trades**

Download trade history as CSV.

**Examples:**

*Export trades*

```python
/export_trades
```
