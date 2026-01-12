# Zepix Trading Bot v2.0 - Error Handling & Troubleshooting

## Overview

This document provides comprehensive guidance on error handling mechanisms within the Zepix Trading Bot and troubleshooting procedures for common issues.

## Error Handling Architecture

### Error Handling Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  - FastAPI exception handlers                                   │
│  - HTTP error responses                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
│  - Trading engine error handling                                │
│  - Manager-level exception handling                             │
│  - Validation errors                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                            │
│  - MT5 connection errors                                        │
│  - Telegram API errors                                          │
│  - Database errors                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Error Categories

| Category | Description | Handling Strategy |
|----------|-------------|-------------------|
| Validation | Invalid input data | Return error message, skip processing |
| Connection | MT5/Telegram disconnection | Auto-reconnect, notify user |
| Trading | Order placement failures | Log error, notify user, continue |
| Configuration | Invalid settings | Log error, use defaults |
| System | Memory/disk issues | Log critical, alert user |

## Common Errors and Solutions

### 1. MT5 Connection Errors

#### Error: MT5 Initialization Failed

**Symptoms:**
- Bot starts but cannot place trades
- Log shows "MT5 initialization failed"
- Health check shows `mt5_connected: false`

**Causes:**
- MT5 terminal not running
- Invalid credentials
- Network issues
- MT5 path incorrect

**Solutions:**

```python
# Check MT5 terminal is running
# On Windows, ensure MetaTrader 5 is open

# Verify credentials in .env
MT5_LOGIN=12345678
MT5_PASSWORD=correct_password
MT5_SERVER=ExactServerName

# Check MT5 path in config
"mt5_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
```

**Diagnostic Commands:**
```bash
# Check MT5 process (Windows)
tasklist | findstr terminal64

# Test connection manually
python -c "import MetaTrader5 as mt5; print(mt5.initialize())"
```

#### Error: MT5 Login Failed

**Symptoms:**
- Log shows "Login failed" or "Invalid account"
- Error code from MT5

**Error Codes:**
| Code | Meaning | Solution |
|------|---------|----------|
| -1 | Generic error | Check all credentials |
| -2 | Invalid account | Verify account number |
| -3 | Invalid password | Check password |
| -4 | Server not found | Verify server name |
| -5 | Connection timeout | Check network |

**Solutions:**
1. Verify account is active with broker
2. Check server name matches exactly (case-sensitive)
3. Ensure account has API trading enabled
4. Try logging in manually via MT5 terminal

#### Error: Order Placement Failed

**Symptoms:**
- Trade not executed
- Log shows "Order failed" with error code

**Common MT5 Order Errors:**
| Error | Description | Solution |
|-------|-------------|----------|
| 10004 | Requote | Retry with updated price |
| 10006 | Request rejected | Check account permissions |
| 10014 | Invalid volume | Check lot size limits |
| 10015 | Invalid price | Verify SL/TP levels |
| 10016 | Invalid stops | Check stops level distance |
| 10019 | Not enough money | Check margin |
| 10030 | Invalid order type | Verify order parameters |

**Solutions:**
```python
# Check symbol info for limits
symbol_info = mt5.symbol_info(symbol)
print(f"Min lot: {symbol_info.volume_min}")
print(f"Max lot: {symbol_info.volume_max}")
print(f"Stops level: {symbol_info.trade_stops_level}")
```

### 2. Telegram Errors

#### Error: Telegram Bot Not Responding

**Symptoms:**
- Commands not working
- No notifications received
- Log shows Telegram errors

**Causes:**
- Invalid bot token
- Bot not started in chat
- Network issues
- Rate limiting

**Solutions:**

```bash
# Verify bot token
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# Check for updates
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"

# Verify chat ID
# Send message to bot, then check getUpdates for chat.id
```

#### Error: Telegram Rate Limit

**Symptoms:**
- Messages delayed or not sent
- Log shows "Too Many Requests"
- Error code 429

**Solutions:**
1. Reduce notification frequency
2. Batch multiple updates into single message
3. Implement exponential backoff

**Code Pattern:**
```python
async def send_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            await send_telegram_message(message)
            return True
        except TelegramError as e:
            if "Too Many Requests" in str(e):
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                raise
    return False
```

#### Error: Invalid Chat ID

**Symptoms:**
- Bot responds to getMe but not to messages
- Log shows "Chat not found"

**Solutions:**
1. Start conversation with bot first
2. Verify chat ID is numeric (not username)
3. For groups, ensure bot is added to group
4. Use getUpdates to find correct chat ID

### 3. Webhook Errors

#### Error: Webhook Not Receiving Alerts

**Symptoms:**
- TradingView alerts sent but not processed
- No log entries for incoming webhooks

**Causes:**
- Server not accessible from internet
- Firewall blocking port
- Wrong webhook URL in TradingView
- SSL/TLS issues

**Solutions:**

```bash
# Check server is listening
curl http://localhost:8000/health

# Check from external
curl http://YOUR_IP:8000/health

# Check firewall (Linux)
sudo ufw status
sudo ufw allow 8000

# Check firewall (Windows)
netsh advfirewall firewall show rule name=all | findstr 8000
```

#### Error: Invalid Alert Format

**Symptoms:**
- Webhook received but not processed
- Log shows "Invalid alert format"

**Solutions:**
1. Verify JSON format in TradingView alert
2. Check required fields: type, symbol, signal, tf
3. Validate signal values match expected

**Valid Alert Examples:**
```json
// Entry alert
{"type":"entry","symbol":"XAUUSD","signal":"buy","tf":"15m"}

// Trend alert
{"type":"trend","symbol":"XAUUSD","signal":"bull","tf":"1h"}
```

#### Error: Duplicate Alert Rejected

**Symptoms:**
- Alert received but marked as duplicate
- Log shows "Duplicate alert detected"

**Explanation:**
- Same alert within 5-minute window is rejected
- Prevents double execution

**Solutions:**
1. Wait 5 minutes between identical alerts
2. Check if previous alert was processed
3. Review duplicate detection logic if needed

### 4. Database Errors

#### Error: Database Locked

**Symptoms:**
- Operations fail with "database is locked"
- Multiple processes accessing database

**Solutions:**
```python
# Ensure single connection
# In database.py, connection uses check_same_thread=False

# Implement retry logic
def execute_with_retry(query, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                time.sleep(0.1 * (attempt + 1))
            else:
                raise
```

#### Error: Database Corruption

**Symptoms:**
- Queries fail with integrity errors
- Data inconsistencies

**Solutions:**
```bash
# Check database integrity
sqlite3 data/trading_bot.db "PRAGMA integrity_check;"

# Backup and recreate if needed
cp data/trading_bot.db data/trading_bot.db.backup
# Bot will recreate tables on startup
```

### 5. Configuration Errors

#### Error: Invalid Configuration

**Symptoms:**
- Bot fails to start
- Log shows "Configuration error"

**Solutions:**
```bash
# Validate JSON syntax
python -c "import json; json.load(open('config/config.json'))"

# Check for common issues
# - Missing commas
# - Trailing commas
# - Unquoted strings
# - Invalid escape sequences
```

#### Error: Missing Required Fields

**Symptoms:**
- KeyError in logs
- Features not working

**Solutions:**
1. Compare config with .env.example
2. Ensure all required fields present
3. Check for typos in field names

### 6. Trading Logic Errors

#### Error: Trend Alignment Failed

**Symptoms:**
- Entry signals not executing
- Log shows "Trend not aligned"

**Explanation:**
- Higher timeframe trends don't match entry direction
- This is expected behavior, not an error

**Solutions:**
1. Check current trends via `/show_trends`
2. Wait for trend alignment
3. Manually set trends if needed via `/set_trend`

#### Error: Risk Limit Reached

**Symptoms:**
- Trades not executing
- Log shows "Daily limit reached" or "Lifetime limit reached"

**Solutions:**
1. Check current risk status via `/risk_status`
2. Wait for daily reset (midnight)
3. Reset lifetime loss via Telegram command
4. Adjust risk caps in configuration

#### Error: Logic Disabled

**Symptoms:**
- Specific timeframe entries not executing
- Log shows "Logic X disabled"

**Solutions:**
1. Check logic status via `/logic_status`
2. Enable logic via `/logic1_on`, `/logic2_on`, `/logic3_on`

### 7. Profit Booking Errors

#### Error: Profit Chain Not Progressing

**Symptoms:**
- Orders at profit but not closing
- Chain stuck at level

**Causes:**
- PnL not reaching $7 target
- Monitoring not running
- Chain status incorrect

**Solutions:**
1. Check chain status via `/profit_chains`
2. Verify monitoring is active
3. Check individual order PnL

#### Error: Profit Order Placement Failed

**Symptoms:**
- Chain progresses but new orders fail
- Log shows order errors

**Solutions:**
1. Check margin availability
2. Verify lot size within limits
3. Check symbol trading hours

### 8. Re-entry Errors

#### Error: Recovery Not Triggering

**Symptoms:**
- SL hit but no recovery attempt
- Chain in recovery mode but no trade

**Causes:**
- Recovery disabled
- Daily limit reached
- Price not recovering enough

**Solutions:**
1. Check SL hunt status via `/sl_status`
2. Verify recovery is enabled
3. Check recovery threshold (70% default)
4. Review daily recovery limits

#### Error: TP Continuation Not Working

**Symptoms:**
- TP hit but no continuation
- Chain not progressing

**Causes:**
- TP continuation disabled
- Trend no longer aligned
- Max levels reached

**Solutions:**
1. Check TP system status via `/tp_system`
2. Verify trend alignment
3. Check current chain level

## Error Handling Code Patterns

### Try-Catch Pattern

```python
async def process_alert(self, alert_data):
    try:
        # Validate alert
        validated = self.alert_processor.validate_alert(alert_data)
        if not validated:
            logger.warning(f"Invalid alert: {alert_data}")
            return {"status": "error", "message": "Invalid alert format"}
        
        # Process based on type
        result = await self._route_alert(validated)
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return {"status": "error", "message": str(e)}
        
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        await self._handle_connection_error(e)
        return {"status": "error", "message": "Connection failed"}
        
    except Exception as e:
        logger.exception(f"Unexpected error processing alert: {e}")
        return {"status": "error", "message": "Internal error"}
```

### Retry Pattern

```python
async def place_order_with_retry(self, order_params, max_retries=3):
    last_error = None
    
    for attempt in range(max_retries):
        try:
            result = await self.mt5_client.place_order(**order_params)
            if result.success:
                return result
            
            # Handle specific error codes
            if result.error_code == 10004:  # Requote
                order_params['price'] = await self._get_current_price()
                continue
            elif result.error_code == 10019:  # Not enough money
                raise InsufficientMarginError(result.error_message)
            else:
                last_error = result.error_message
                
        except ConnectionError:
            await self._reconnect_mt5()
            
        await asyncio.sleep(0.5 * (attempt + 1))
    
    raise OrderPlacementError(f"Failed after {max_retries} attempts: {last_error}")
```

### Graceful Degradation

```python
async def send_notification(self, message):
    try:
        await self.telegram_bot.send_message(message)
    except TelegramError as e:
        logger.warning(f"Telegram notification failed: {e}")
        # Continue operation even if notification fails
        # Trading should not stop due to notification issues
```

## Diagnostic Commands

### Health Check

```bash
# API health check
curl http://localhost:8000/health

# Expected response
{
    "status": "healthy",
    "mt5_connected": true,
    "telegram_active": true,
    "uptime": "2h 30m"
}
```

### Log Analysis

```bash
# View recent errors
grep -i error logs/bot.log | tail -50

# View specific error type
grep "MT5" logs/bot.log | tail -20

# View trade execution logs
grep "execute_trades" logs/bot.log | tail -20

# Count errors by type
grep -i error logs/bot.log | cut -d':' -f4 | sort | uniq -c | sort -rn
```

### Database Queries

```sql
-- Check recent trades
SELECT * FROM trades ORDER BY open_time DESC LIMIT 10;

-- Check active chains
SELECT * FROM reentry_chains WHERE status = 'ACTIVE';

-- Check profit chains
SELECT * FROM profit_booking_chains WHERE status = 'ACTIVE';

-- Check SL events
SELECT * FROM sl_events ORDER BY hit_time DESC LIMIT 10;
```

### Telegram Diagnostics

```
/status - Overall bot status
/health - System health check
/diagnostics - Detailed diagnostics
/risk_status - Risk limit status
/logic_status - Logic enable status
/show_trends - Current trend states
```

## Recovery Procedures

### Procedure 1: MT5 Connection Recovery

1. Check MT5 terminal is running
2. Verify network connectivity
3. Check credentials in .env
4. Restart bot if needed
5. Monitor logs for successful reconnection

### Procedure 2: Database Recovery

1. Stop the bot
2. Backup current database
3. Check database integrity
4. If corrupted, restore from backup or let bot recreate
5. Restart bot
6. Verify data consistency

### Procedure 3: Full System Recovery

1. Stop all bot processes
2. Backup configuration and data
3. Verify MT5 terminal running
4. Verify network connectivity
5. Check all credentials
6. Start bot
7. Monitor logs for errors
8. Verify via Telegram /status

### Procedure 4: Emergency Trade Closure

1. Use `/panic_close` command
2. Or manually close via MT5 terminal
3. Check all positions closed
4. Review logs for any issues
5. Investigate cause before resuming

## Monitoring and Alerts

### Key Metrics to Monitor

| Metric | Normal Range | Alert Threshold |
|--------|--------------|-----------------|
| MT5 Connection | Connected | Any disconnect |
| Daily Loss | < 50% of cap | > 80% of cap |
| Error Rate | < 1/hour | > 5/hour |
| Response Time | < 1s | > 5s |
| Memory Usage | < 500MB | > 1GB |

### Log Monitoring

```bash
# Real-time log monitoring
tail -f logs/bot.log | grep -E "(ERROR|CRITICAL|WARNING)"

# Alert on critical errors
tail -f logs/bot.log | grep "CRITICAL" | while read line; do
    echo "CRITICAL ERROR: $line" | mail -s "Bot Alert" admin@example.com
done
```

## Preventive Measures

### Daily Checks

1. Review overnight logs for errors
2. Check MT5 connection status
3. Verify risk statistics
4. Check active chains status
5. Review any failed trades

### Weekly Maintenance

1. Backup database
2. Review error patterns
3. Check disk space
4. Update dependencies if needed
5. Review and optimize configuration

### Monthly Review

1. Analyze trading performance
2. Review error trends
3. Update documentation
4. Test recovery procedures
5. Review and update alerts

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) - Configuration guide
- [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md) - Logging details
- [DEPLOYMENT_MAINTENANCE.md](DEPLOYMENT_MAINTENANCE.md) - Deployment guide
