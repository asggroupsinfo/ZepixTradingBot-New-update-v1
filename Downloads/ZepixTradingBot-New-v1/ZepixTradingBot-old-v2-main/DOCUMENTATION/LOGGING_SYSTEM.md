# Zepix Trading Bot v2.0 - Logging System

## Overview

This document provides comprehensive documentation of the logging system used in the Zepix Trading Bot, including log configuration, log levels, log file management, and log analysis techniques.

## Logging Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOGGING SYSTEM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Logger    │───▶│  Handlers   │───▶│   Output    │        │
│  │  (Python)   │    │             │    │             │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                            │                                    │
│                     ┌──────┴──────┐                            │
│                     │             │                            │
│              ┌──────▼─────┐ ┌─────▼──────┐                    │
│              │   File     │ │  Console   │                    │
│              │  Handler   │ │  Handler   │                    │
│              └──────┬─────┘ └─────┬──────┘                    │
│                     │             │                            │
│              ┌──────▼─────┐ ┌─────▼──────┐                    │
│              │ bot.log    │ │  stdout    │                    │
│              │ (rotating) │ │            │                    │
│              └────────────┘ └────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Logger Configuration

### Default Configuration

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str = "zepix_bot") -> logging.Logger:
    """Configure and return the application logger."""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename="logs/bot.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### Optimized Logger

The bot uses an optimized logger for high-performance logging:

```python
class OptimizedLogger:
    """High-performance logger with batching and async support."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._buffer = []
        self._buffer_size = 100
        self._flush_interval = 5  # seconds
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)
        self._flush()  # Immediate flush for critical
    
    def _log(self, level: int, message: str, **kwargs):
        extra = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        full_message = f"{message} | {extra}" if extra else message
        self.logger.log(level, full_message)
```

## Log Levels

### Level Hierarchy

| Level | Value | Description | Use Case |
|-------|-------|-------------|----------|
| DEBUG | 10 | Detailed diagnostic info | Development, troubleshooting |
| INFO | 20 | General operational info | Normal operations |
| WARNING | 30 | Potential issues | Non-critical problems |
| ERROR | 40 | Error conditions | Failed operations |
| CRITICAL | 50 | Severe errors | System failures |

### Level Usage Guidelines

**DEBUG Level:**
```python
logger.debug(f"Processing alert: {alert_data}")
logger.debug(f"Calculated lot size: {lot_size} for tier {tier}")
logger.debug(f"Trend check: {symbol} {timeframe} = {trend}")
```

**INFO Level:**
```python
logger.info(f"Trade opened: {symbol} {direction} @ {price}")
logger.info(f"Profit chain progressed to level {level}")
logger.info(f"Configuration reloaded successfully")
```

**WARNING Level:**
```python
logger.warning(f"Trend not aligned for {symbol}, skipping trade")
logger.warning(f"Daily loss at 80% of cap: ${daily_loss}/${daily_cap}")
logger.warning(f"Duplicate alert detected, ignoring")
```

**ERROR Level:**
```python
logger.error(f"Order placement failed: {error_message}")
logger.error(f"MT5 connection lost: {exception}")
logger.error(f"Database error: {error}")
```

**CRITICAL Level:**
```python
logger.critical(f"Daily loss cap exceeded! Trading halted.")
logger.critical(f"MT5 initialization failed, bot cannot start")
logger.critical(f"Panic close executed: {reason}")
```

## Log File Structure

### File Location

```
ZepixTradingBot-new-v13/
└── logs/
    ├── bot.log           # Current log file
    ├── bot.log.1         # First rotation backup
    ├── bot.log.2         # Second rotation backup
    ├── bot.log.3         # Third rotation backup
    ├── bot.log.4         # Fourth rotation backup
    └── bot.log.5         # Fifth rotation backup
```

### Rotation Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| maxBytes | 10 MB | Maximum file size before rotation |
| backupCount | 5 | Number of backup files to keep |
| encoding | UTF-8 | File encoding |

### Log Entry Format

```
TIMESTAMP | LEVEL | LOGGER_NAME | FUNCTION:LINE | MESSAGE
```

**Example Entries:**

```
2025-01-15 10:30:15 | INFO     | zepix_bot | process_alert:125 | Received entry alert: XAUUSD BUY 15m
2025-01-15 10:30:15 | DEBUG    | zepix_bot | check_alignment:89 | Checking trend alignment for XAUUSD LOGIC2
2025-01-15 10:30:15 | DEBUG    | zepix_bot | check_alignment:95 | 1H trend: BULLISH, 15M trend: BULLISH
2025-01-15 10:30:15 | INFO     | zepix_bot | execute_trades:210 | Trends aligned, executing dual orders
2025-01-15 10:30:16 | INFO     | zepix_bot | place_order:150 | Order A placed: ticket=12345, lot=0.10
2025-01-15 10:30:16 | INFO     | zepix_bot | place_order:150 | Order B placed: ticket=12346, lot=0.10
2025-01-15 10:30:16 | INFO     | zepix_bot | execute_trades:225 | Trade execution complete: 2 orders placed
```

## Log Categories

### Trading Logs

```python
# Entry signals
logger.info(f"ENTRY | {symbol} | {direction} | {logic} | price={price}")

# Trade execution
logger.info(f"TRADE_OPEN | ticket={ticket} | {symbol} | {direction} | lot={lot} | entry={entry} | sl={sl} | tp={tp}")

# Trade closure
logger.info(f"TRADE_CLOSE | ticket={ticket} | {symbol} | pnl={pnl} | reason={reason}")

# Order modification
logger.info(f"ORDER_MODIFY | ticket={ticket} | sl={new_sl} | tp={new_tp}")
```

### Re-entry Logs

```python
# SL hit
logger.info(f"SL_HIT | chain={chain_id} | {symbol} | level={level} | loss={loss}")

# Recovery monitoring
logger.debug(f"RECOVERY_CHECK | chain={chain_id} | price={price} | threshold={threshold}")

# Recovery execution
logger.info(f"RECOVERY_ENTRY | chain={chain_id} | {symbol} | level={level}")

# TP continuation
logger.info(f"TP_CONT | chain={chain_id} | {symbol} | level={level} | profit={profit}")
```

### Profit Booking Logs

```python
# Chain creation
logger.info(f"PROFIT_CHAIN_CREATE | chain={chain_id} | {symbol} | {direction}")

# Level progression
logger.info(f"PROFIT_LEVEL_UP | chain={chain_id} | level={level} | orders={order_count}")

# Profit booking
logger.info(f"PROFIT_BOOK | chain={chain_id} | order={ticket} | profit={profit}")

# Chain completion
logger.info(f"PROFIT_CHAIN_COMPLETE | chain={chain_id} | total_profit={total}")
```

### System Logs

```python
# Startup
logger.info("BOT_START | version=2.0 | mode=production")

# Connection status
logger.info(f"MT5_CONNECT | status=connected | account={account}")
logger.info(f"TELEGRAM_CONNECT | status=active | chat_id={chat_id}")

# Configuration
logger.info(f"CONFIG_LOAD | file=config.json | status=success")
logger.info(f"CONFIG_RELOAD | changes={changes}")

# Shutdown
logger.info("BOT_STOP | reason={reason} | uptime={uptime}")
```

### Error Logs

```python
# Connection errors
logger.error(f"MT5_ERROR | error={error} | code={code}")
logger.error(f"TELEGRAM_ERROR | error={error}")

# Trading errors
logger.error(f"ORDER_FAILED | {symbol} | error={error} | code={code}")
logger.error(f"CLOSE_FAILED | ticket={ticket} | error={error}")

# System errors
logger.error(f"DATABASE_ERROR | operation={op} | error={error}")
logger.critical(f"FATAL_ERROR | component={component} | error={error}")
```

## Log Analysis

### Common Log Queries

**Find All Errors:**
```bash
grep -E "ERROR|CRITICAL" logs/bot.log
```

**Find Trade Executions:**
```bash
grep "TRADE_OPEN\|TRADE_CLOSE" logs/bot.log
```

**Find Specific Symbol:**
```bash
grep "XAUUSD" logs/bot.log
```

**Find Today's Logs:**
```bash
grep "$(date +%Y-%m-%d)" logs/bot.log
```

**Count Errors by Type:**
```bash
grep ERROR logs/bot.log | cut -d'|' -f5 | sort | uniq -c | sort -rn
```

**Find Failed Orders:**
```bash
grep "ORDER_FAILED" logs/bot.log
```

**Find SL Hits:**
```bash
grep "SL_HIT" logs/bot.log
```

**Find Profit Bookings:**
```bash
grep "PROFIT_BOOK" logs/bot.log | awk -F'profit=' '{sum+=$2} END {print "Total: $"sum}'
```

### Log Analysis Script

```python
#!/usr/bin/env python3
"""Log analysis utility for Zepix Trading Bot."""

import re
from collections import Counter
from datetime import datetime

def analyze_logs(log_file: str = "logs/bot.log"):
    """Analyze log file and generate report."""
    
    stats = {
        "total_lines": 0,
        "errors": 0,
        "warnings": 0,
        "trades_opened": 0,
        "trades_closed": 0,
        "sl_hits": 0,
        "tp_hits": 0,
        "profit_bookings": 0,
        "total_profit": 0.0,
        "total_loss": 0.0,
        "error_types": Counter(),
        "symbols": Counter()
    }
    
    with open(log_file, 'r') as f:
        for line in f:
            stats["total_lines"] += 1
            
            if "ERROR" in line:
                stats["errors"] += 1
                # Extract error type
                match = re.search(r'\| (\w+_ERROR)', line)
                if match:
                    stats["error_types"][match.group(1)] += 1
            
            if "WARNING" in line:
                stats["warnings"] += 1
            
            if "TRADE_OPEN" in line:
                stats["trades_opened"] += 1
                # Extract symbol
                match = re.search(r'TRADE_OPEN \| ticket=\d+ \| (\w+)', line)
                if match:
                    stats["symbols"][match.group(1)] += 1
            
            if "TRADE_CLOSE" in line:
                stats["trades_closed"] += 1
                # Extract PnL
                match = re.search(r'pnl=([-\d.]+)', line)
                if match:
                    pnl = float(match.group(1))
                    if pnl > 0:
                        stats["total_profit"] += pnl
                    else:
                        stats["total_loss"] += abs(pnl)
            
            if "SL_HIT" in line:
                stats["sl_hits"] += 1
            
            if "TP_HIT" in line or "TP_CONT" in line:
                stats["tp_hits"] += 1
            
            if "PROFIT_BOOK" in line:
                stats["profit_bookings"] += 1
    
    return stats

def print_report(stats: dict):
    """Print formatted analysis report."""
    
    print("=" * 60)
    print("ZEPIX TRADING BOT - LOG ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nTotal Log Lines: {stats['total_lines']}")
    print(f"\nErrors: {stats['errors']}")
    print(f"Warnings: {stats['warnings']}")
    print(f"\nTrades Opened: {stats['trades_opened']}")
    print(f"Trades Closed: {stats['trades_closed']}")
    print(f"\nSL Hits: {stats['sl_hits']}")
    print(f"TP Hits: {stats['tp_hits']}")
    print(f"Profit Bookings: {stats['profit_bookings']}")
    print(f"\nTotal Profit: ${stats['total_profit']:.2f}")
    print(f"Total Loss: ${stats['total_loss']:.2f}")
    print(f"Net PnL: ${stats['total_profit'] - stats['total_loss']:.2f}")
    
    if stats['error_types']:
        print("\nError Types:")
        for error_type, count in stats['error_types'].most_common(10):
            print(f"  {error_type}: {count}")
    
    if stats['symbols']:
        print("\nTrades by Symbol:")
        for symbol, count in stats['symbols'].most_common():
            print(f"  {symbol}: {count}")

if __name__ == "__main__":
    stats = analyze_logs()
    print_report(stats)
```

### Real-time Log Monitoring

```bash
# Watch logs in real-time
tail -f logs/bot.log

# Watch only errors
tail -f logs/bot.log | grep --line-buffered -E "ERROR|CRITICAL"

# Watch trades
tail -f logs/bot.log | grep --line-buffered "TRADE"

# Watch with highlighting
tail -f logs/bot.log | grep --line-buffered -E "ERROR|WARNING" --color=always
```

## Log Management

### Log Rotation

The bot uses Python's `RotatingFileHandler` for automatic log rotation:

```python
file_handler = RotatingFileHandler(
    filename="logs/bot.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5
)
```

**Rotation Behavior:**
1. When `bot.log` reaches 10 MB
2. `bot.log` → `bot.log.1`
3. `bot.log.1` → `bot.log.2`
4. ... and so on
5. `bot.log.5` is deleted
6. New `bot.log` is created

### Manual Log Cleanup

```bash
# Remove old logs (keep last 7 days)
find logs/ -name "*.log.*" -mtime +7 -delete

# Compress old logs
gzip logs/bot.log.[2-5]

# Archive logs
tar -czvf logs_archive_$(date +%Y%m%d).tar.gz logs/bot.log.*
```

### Log Backup

```bash
#!/bin/bash
# backup_logs.sh

BACKUP_DIR="/opt/backups/logs"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Copy current logs
cp logs/bot.log $BACKUP_DIR/bot_$DATE.log

# Compress
gzip $BACKUP_DIR/bot_$DATE.log

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

## Logging Best Practices

### Do's

1. **Use appropriate log levels**
   ```python
   # Good
   logger.debug(f"Processing data: {data}")
   logger.info(f"Trade executed successfully")
   logger.error(f"Order failed: {error}")
   ```

2. **Include context in messages**
   ```python
   # Good
   logger.info(f"TRADE_OPEN | ticket={ticket} | symbol={symbol} | lot={lot}")
   ```

3. **Log at entry and exit points**
   ```python
   # Good
   logger.debug(f"Entering process_alert with data: {alert_data}")
   # ... processing ...
   logger.debug(f"Exiting process_alert with result: {result}")
   ```

4. **Use structured logging for parsing**
   ```python
   # Good - easy to parse
   logger.info(f"METRIC | trades={count} | pnl={pnl} | win_rate={rate}")
   ```

### Don'ts

1. **Don't log sensitive data**
   ```python
   # Bad
   logger.info(f"Login with password: {password}")
   
   # Good
   logger.info(f"Login attempt for account: {account_id}")
   ```

2. **Don't over-log in loops**
   ```python
   # Bad
   for item in large_list:
       logger.debug(f"Processing: {item}")
   
   # Good
   logger.debug(f"Processing {len(large_list)} items")
   for item in large_list:
       # process without logging each
       pass
   logger.debug(f"Completed processing {len(large_list)} items")
   ```

3. **Don't use print() for logging**
   ```python
   # Bad
   print(f"Error: {error}")
   
   # Good
   logger.error(f"Error: {error}")
   ```

## Troubleshooting with Logs

### Common Issues

**Issue: Bot not receiving alerts**
```bash
# Check for webhook logs
grep "webhook\|alert" logs/bot.log | tail -20
```

**Issue: Trades not executing**
```bash
# Check for trade execution logs
grep "execute_trades\|TRADE_OPEN\|ORDER_FAILED" logs/bot.log | tail -50
```

**Issue: MT5 connection problems**
```bash
# Check MT5 related logs
grep -i "mt5\|metatrader" logs/bot.log | tail -30
```

**Issue: Telegram not responding**
```bash
# Check Telegram logs
grep -i "telegram\|message\|callback" logs/bot.log | tail -30
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
# In config or environment
LOG_LEVEL=DEBUG

# Or programmatically
logger.setLevel(logging.DEBUG)
```

## Performance Considerations

### Async Logging

For high-performance scenarios, use async logging:

```python
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

class AsyncLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    async def info(self, message: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.logger.info,
            message
        )
```

### Log Buffering

For reducing I/O overhead:

```python
import logging

# Use MemoryHandler for buffering
memory_handler = logging.handlers.MemoryHandler(
    capacity=1000,
    flushLevel=logging.ERROR,
    target=file_handler
)
```

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [ERROR_HANDLING_TROUBLESHOOTING.md](ERROR_HANDLING_TROUBLESHOOTING.md) - Error handling
- [DEPLOYMENT_MAINTENANCE.md](DEPLOYMENT_MAINTENANCE.md) - Deployment guide
