# 🔧 Quick Reference Guide - New Logging System

## Import and Use the Logger

```python
# Import the global logger instance
from src.utils.optimized_logger import logger

# Or import config for advanced control
from src.config.logging_config import logging_config, LogLevel
```

---

## Basic Logging Methods

### Standard Logging
```python
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # Include traceback
logger.critical("Critical system failure")
logger.debug("Debug information")  # Only shown in DEBUG mode
```

### System Events
```python
logger.log_system_event("Bot started", "Version 2.0")
logger.log_system_event("Trade execution", "Symbol: EURUSD, Direction: BUY")
```

### Command Execution Logging
```python
# Automatically filters based on importance
logger.log_command_execution("start", user_id=12345)  # Always logged
logger.log_command_execution("dashboard", user_id=12345, {"page": 1})  # Always logged
logger.log_command_execution("trades", user_id=12345)  # Only in DEBUG mode
```

### Trading Debug Logging
```python
# Detailed trading decision logging (when trading_debug=True)
logger.log_trading_debug(
    alert=alert_object,
    alignment={"aligned": True, "direction": "BULLISH"},
    signal_direction="BULLISH",
    logic="LOGIC1"
)
```

### Trading Error Logging (with Deduplication)
```python
# Automatically prevents spam - logs max 3 times + suppression notice
logger.log_trading_error("Trend not aligned for LOGIC1", alert=alert_object)
logger.log_trading_error("Risk check failed - trading blocked")
```

### Missing Order Logging (with Deduplication)
```python
# Logs max 3 times per chain/order pair
logger.log_missing_order(chain_id="PROFIT_EURUSD_abc123", order_id="12345678")
```

---

## Configuration Control

### Change Log Level at Runtime
```python
from src.config.logging_config import logging_config, LogLevel

# Set to DEBUG (shows everything)
logging_config.set_level(LogLevel.DEBUG)

# Set to INFO (production default)
logging_config.set_level(LogLevel.INFO)

# Set to WARNING (only warnings and errors)
logging_config.set_level(LogLevel.WARNING)

# Set to ERROR (only errors and critical)
logging_config.set_level(LogLevel.ERROR)
```

### Toggle Trading Debug Mode
```python
# Enable detailed trading decision logging
logging_config.enable_trading_debug()

# Disable trading debug logging
logging_config.disable_trading_debug()

# Or set directly
logging_config.trading_debug = True  # Enable
logging_config.trading_debug = False  # Disable
```

### Toggle Output Destinations
```python
# Disable console logging (only file)
logging_config.enable_console_logs = False

# Disable file logging (only console)
logging_config.enable_file_logs = False

# Enable both (default)
logging_config.enable_console_logs = True
logging_config.enable_file_logs = True
```

---

## Important Commands (Always Logged)

These commands are logged regardless of log level:
- `start`, `dashboard`, `pause`, `resume`, `status`, `performance`
- `set_trend`, `set_profit_sl`, `profit_sl_mode`, `profit_sl_status`
- `stop_all`, `emergency_stop`, `set_risk`, `account_status`

## Routine Commands (DEBUG Mode Only)

These are only logged when log level is DEBUG:
- `trades`, `signal_status`, `simulation_mode`, `logic_status`
- `open_trades`, `chains`, `statistics`

---

## Error Deduplication

### Automatic Deduplication for:
1. **Trading Errors** - Max 3 repeats per unique error message
2. **Missing Orders** - Max 3 repeats per chain/order pair

### How It Works:
```python
# First occurrence
logger.log_trading_error("Trend not aligned")  # ✅ Logged

# Second occurrence (within same session)
logger.log_trading_error("Trend not aligned")  # ✅ Logged

# Third occurrence
logger.log_trading_error("Trend not aligned")  # ✅ Logged

# Fourth occurrence
logger.log_trading_error("Trend not aligned")  # ✅ Logged with "(suppressing further repeats)"

# Fifth+ occurrences
logger.log_trading_error("Trend not aligned")  # ❌ Silently counted, not logged
```

---

## Log File Management

### Log Location
```
logs/bot_activity.log
```

### Log Rotation
- **Max Size:** 10 MB
- **Backups:** 5 files
- **Naming:** `bot_activity.log.1`, `bot_activity.log.2`, etc.
- **Automatic:** Happens when file reaches 10 MB

### Manual Log Review
```bash
# View latest log
tail -f logs/bot_activity.log

# Search for errors
grep "ERROR" logs/bot_activity.log

# Search for trading decisions
grep "TRADING_DEBUG" logs/bot_activity.log

# View specific time range
grep "2024-01-15 14:" logs/bot_activity.log
```

---

## Trading Debug Mode Examples

### Enable Trading Debug
```python
from src.config.logging_config import logging_config
logging_config.trading_debug = True
```

### What Gets Logged:
```
[2024-01-15 14:30:15] 🔍 TRADING_DEBUG: Alert=buy, TF=5m, Symbol=EURUSD
[2024-01-15 14:30:15] 🔍 TRADING_DEBUG: Alignment={'aligned': True, 'direction': 'BULLISH'}
[2024-01-15 14:30:15] 🔍 TRADING_DEBUG: SignalDir=BULLISH, Logic=LOGIC1
[2024-01-15 14:30:15] 🔔 Trade execution starting | Symbol: EURUSD, Direction: BULLISH
```

### Disable Trading Debug (Reduce Logs)
```python
logging_config.trading_debug = False
```

---

## Circuit Breaker Monitoring

### Trading Engine Monitor
```python
# In trading_engine.py
self.monitor_error_count  # Current error count
self.max_monitor_errors = 10  # Threshold before shutdown

# What happens:
# - Errors 1-9: Logged, retries continue
# - Error 10: Critical alert + Telegram message + Monitor stops
```

### Price Monitor Service
```python
# In price_monitor_service.py
self.monitor_error_count  # Current error count
self.max_monitor_errors = 10  # Threshold before shutdown

# What happens:
# - Errors 1-9: Logged, retries continue
# - Error 10: Critical alert + Telegram message + Service stops
```

---

## MT5 Connection Health

### Manual Health Check
```python
# Check connection health
is_healthy = await mt5_client.check_connection_health()

if not is_healthy:
    logger.critical("MT5 connection lost")
```

### Auto-Reconnect Behavior:
1. Connection lost detected
2. Attempts reconnection (uses existing `initialize()` method)
3. If successful: Resets error counter, continues
4. If failed: Increments error counter
5. After 5 failures: Critical alert + Telegram message

---

## Best Practices

### 1. Use Appropriate Log Levels
```python
logger.debug("Detailed debugging info")      # Development only
logger.info("Normal operations")             # Production default
logger.warning("Something unusual")          # Needs attention
logger.error("Error occurred")               # Actionable error
logger.critical("System failure")            # Immediate action required
```

### 2. Include Context in Error Messages
```python
# ❌ Bad
logger.error("Trade failed")

# ✅ Good
logger.error(f"Trade failed: Symbol={symbol}, Direction={direction}, Reason={reason}")
```

### 3. Use Specialized Methods
```python
# ❌ Don't do this
logger.info(f"Command {command} executed by {user_id}")

# ✅ Do this (automatic importance filtering)
logger.log_command_execution(command, user_id, params)
```

### 4. Enable Trading Debug for Troubleshooting
```python
# When debugging trading decisions
logging_config.trading_debug = True

# When in production (reduce logs)
logging_config.trading_debug = False
```

---

## Troubleshooting

### Too Many Logs?
```python
# Increase log level
logging_config.set_level(LogLevel.WARNING)  # Only warnings and errors

# Disable trading debug
logging_config.trading_debug = False

# Disable console (file only)
logging_config.enable_console_logs = False
```

### Missing Logs?
```python
# Decrease log level
logging_config.set_level(LogLevel.DEBUG)  # Show everything

# Enable trading debug
logging_config.trading_debug = True

# Ensure outputs enabled
logging_config.enable_console_logs = True
logging_config.enable_file_logs = True
```

### Log File Too Large?
- Automatic rotation at 10 MB
- Keeps 5 backup files
- Oldest backup is deleted automatically

---

## Summary

✅ **Simple to use** - Just import and log  
✅ **Smart filtering** - Automatic importance-based filtering  
✅ **No spam** - Built-in error deduplication  
✅ **Flexible** - Configure levels, outputs, and modes  
✅ **Production-ready** - Log rotation, circuit breakers, health monitoring  

**The logging system is now enterprise-grade and production-ready! 🚀**
