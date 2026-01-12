---

## 9. COMMON PROBLEMS & SOLUTIONS

### 9.1 Trend-Signal Mismatch Errors

#### Problem Description

**Error Message:**
```
ERROR: Signal BULLISH doesn't match trend BEARISH
ERROR: Signal BEARISH doesn't match trend BULLISH
```

**Frequency:** High (most common reason for trade rejection)

**Root Cause:**
- Entry signal direction doesn't match aligned multi-timeframe trend
- Occurs when TradingView sends entry signal but trends haven't updated yet
- Timeframe misalignment (1H vs 15M conflict for LOGIC1/LOGIC2)

**Impact:**
- 🔴 **CRITICAL:** Blocks all trade execution
- Prevents profitable trades from executing
- Most common reason for "no trades executed" issues

#### Solution 1: Relax Trend Matching (Quick Fix)

**File:** `src/core/trading_engine.py`

**Change:**
```python
# Before (strict matching)
if signal_direction != alignment['direction']:
    logger.error(f"Signal {signal_direction} doesn't match trend {alignment['direction']}")
    return

# After (allow NEUTRAL trends)
if alignment['direction'] != 'NEUTRAL' and signal_direction != alignment['direction']:
    logger.warning(f"Signal {signal_direction} doesn't match trend {alignment['direction']}, but proceeding...")
    # Continue execution
```

**Pros:** Quick fix, allows more trades
**Cons:** May execute trades against trend

#### Solution 2: Add Delay Tolerance (Recommended)

**File:** `src/core/trading_engine.py`

**Change:**
```python
# Check if trend was updated recently (within last 5 minutes)
trend_update_time = timeframe_trend_manager.get_trend_update_time(symbol, logic)
if trend_update_time and (datetime.now() - trend_update_time).seconds < 300:
    # Trend recently updated, strict matching
    if signal_direction != alignment['direction']:
        logger.error(f"Signal {signal_direction} doesn't match trend {alignment['direction']}")
        return
else:
    # Trend not recently updated, allow trade if signal is valid
    logger.info(f"Trend not recently updated, allowing trade based on signal only")
```

**Pros:** Balances safety with flexibility
**Cons:** Requires tracking trend update times

#### Solution 3: Improve Trend Update Timing (Long-term)

**File:** `src/processors/alert_processor.py`

**Change:**
- Ensure trend/bias alerts arrive before entry alerts
- Add trend update confirmation before processing entry
- Implement trend update queue

**Pros:** Most robust solution
**Cons:** Requires TradingView alert timing coordination

#### Prevention

1. **Verify TradingView Alert Order:**
   - Trend alerts should fire before entry alerts
   - Add delay in TradingView: `alertcondition(..., delay=1)`

2. **Monitor Trend Alignment:**
   - Use `/trend_matrix` command regularly
   - Check `/show_trends` before trading session

3. **Enable Auto Trend Updates:**
   - Use `/set_auto [symbol] [timeframe]` for all timeframes
   - Let bot update trends automatically from TradingView

---

### 9.2 Daily Loss Cap Blocking Trades

#### Problem Description

**Error Message:**
```
WARNING: Dual order error: Risk validation failed: Daily loss cap exceeded: $150.00 > $100.0
BLOCKED: Daily loss limit reached
```

**Frequency:** Medium (occurs when daily losses accumulate)

**Root Cause:**
- Daily loss exceeds configured limit for risk tier
- Lifetime loss exceeds maximum total loss
- Dual order system requires 2x risk validation

**Impact:**
- 🔴 **CRITICAL:** Blocks all new trades
- Trading paused automatically
- Requires manual intervention to resume

#### Solution 1: Increase Daily Loss Limit (Quick Fix)

**File:** `config/config.json`

**Change:**
```json
{
  "risk_tiers": {
    "10000": {
      "daily_loss_limit": 400,  // Increase from 100 to 400
      "max_total_loss": 1000
    }
  }
}
```

**Pros:** Immediate fix
**Cons:** Increases risk exposure

#### Solution 2: Clear Daily Loss (Temporary)

**Via Telegram:**
```
/clear_daily_loss
```

**Via API:**
```bash
curl -X POST http://localhost:80/reset_stats
```

**Pros:** Quick reset for testing
**Cons:** Loses loss tracking data

#### Solution 3: Adjust Risk Tier (Recommended)

**File:** `config/config.json`

**Change:**
```json
{
  "risk_tiers": {
    "10000": {
      "daily_loss_limit": 200,  // More reasonable limit
      "max_total_loss": 500     // Lower lifetime cap
    }
  }
}
```

**Pros:** Better risk management
**Cons:** Requires balance adjustment

#### Prevention

1. **Monitor Daily Loss:**
   - Use `/view_risk_caps` regularly
   - Check `/status` for current loss values

2. **Set Appropriate Limits:**
   - Daily limit: 2-5% of account balance
   - Lifetime limit: 10-20% of account balance

3. **Use Risk Tier Appropriately:**
   - Match tier to actual account balance
   - Don't use higher tier for lower balance

---

### 9.3 Missing Order Chain Errors

#### Problem Description

**Error Message:**
```
WARNING: Chain PROFIT_XAUUSD_abc123 has missing order: 472200467
WARNING: Chain PROFIT_XAUUSD_abc123 has missing order: 472200473
```

**Frequency:** High (can cause log spam - 8,000+ occurrences)

**Root Cause:**
- Orders closed externally (MT5 auto-close, manual close)
- Orders never existed (placement failed)
- Chain tracking out of sync with MT5
- No deduplication for missing order checks

**Impact:**
- 🟠 **HIGH:** Log spam, performance degradation
- Makes debugging impossible
- Consumes CPU/memory resources

#### Solution 1: Add Error Deduplication (Quick Fix)

**File:** `src/managers/profit_booking_manager.py`

**Change:**
```python
class ProfitBookingManager:
    def __init__(self):
        self.missing_order_checks = {}  # Track checked orders
        
    def check_profit_targets(self, chain, open_trades):
        # Check if order was already verified as missing
        for order_id in chain.active_orders:
            check_key = f"{chain.chain_id}_{order_id}"
            if check_key in self.missing_order_checks:
                if self.missing_order_checks[check_key] >= 3:
                    # Already checked 3 times, mark as permanently missing
                    continue
                self.missing_order_checks[check_key] += 1
            else:
                self.missing_order_checks[check_key] = 1
                
            # Check order existence
            if order_id not in [t.trade_id for t in open_trades]:
                # Order missing, but only log first 3 times
                if self.missing_order_checks[check_key] <= 3:
                    logger.warning(f"Chain {chain.chain_id} has missing order: {order_id}")
```

**Pros:** Stops log spam immediately
**Cons:** Requires code change

#### Solution 2: Auto-Cleanup Stale Chains (Recommended)

**File:** `src/managers/profit_booking_manager.py`

**Change:**
```python
def cleanup_stale_chains(self):
    """Remove chains with all orders missing."""
    for chain in self.get_active_chains():
        missing_count = 0
        for order_id in chain.active_orders:
            if order_id not in [t.trade_id for t in self.trading_engine.open_trades]:
                missing_count += 1
        
        # If all orders missing, mark chain as STALE
        if missing_count == len(chain.active_orders):
            chain.status = "STALE"
            self.db.update_chain(chain)
            logger.info(f"Marked chain {chain.chain_id} as STALE (all orders missing)")
```

**Pros:** Automatic cleanup
**Cons:** May remove valid chains if orders temporarily missing

#### Solution 3: Improve Chain Synchronization (Long-term)

**File:** `src/managers/profit_booking_manager.py`

**Change:**
- Sync chain active_orders with MT5 positions on startup
- Remove closed orders from chain.active_orders immediately
- Add chain validation on every price monitor cycle

**Pros:** Prevents issue from occurring
**Cons:** Requires more complex logic

#### Prevention

1. **Monitor Chain Status:**
   - Use `/profit_chains` regularly
   - Check for STALE chains

2. **Manual Cleanup:**
   - Use `/stop_profit_chain [chain_id]` for problematic chains
   - Use `/stop_all_profit_chains` if needed

3. **Verify Order Placement:**
   - Check MT5 terminal for order existence
   - Verify order IDs match chain tracking

---

### 9.4 MT5 Connection Issues

#### Problem Description

**Error Message:**
```
ERROR: MT5 initialization failed
ERROR: MT5 connection error: [error details]
ERROR: Order failed: Not connected to MT5
```

**Frequency:** Low (but critical when occurs)

**Root Cause:**
- MT5 terminal not running
- Incorrect login credentials
- Server name mismatch (case-sensitive)
- Network connectivity issues
- MT5 terminal locked/blocked

**Impact:**
- 🔴 **CRITICAL:** No trades can execute
- Bot continues in simulation mode
- No real order placement

#### Solution 1: Verify MT5 Terminal (Quick Fix)

**Steps:**
1. Check MT5 terminal is running
2. Verify account is logged in
3. Check account credentials in `.env` file
4. Restart MT5 terminal if needed

**File:** `.env`
```bash
MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=XMGlobal-MT5 6  # Exact match, case-sensitive
```

#### Solution 2: Test MT5 Connection

**Python Script:**
```python
from src.clients.mt5_client import MT5Client
from src.config import Config

config = Config()
mt5 = MT5Client(config)
success = mt5.initialize()

if success:
    print("✅ MT5 Connected")
    balance = mt5.get_account_balance()
    print(f"Balance: ${balance}")
else:
    print("❌ MT5 Connection Failed")
    print("Check:")
    print("1. MT5 terminal running")
    print("2. Credentials correct")
    print("3. Server name exact match")
```

#### Solution 3: Enable Simulation Mode (Temporary)

**Via Telegram:**
```
/simulation_mode on
```

**Via Config:**
```json
{
  "simulate_orders": true
}
```

**Pros:** Allows bot to continue without MT5
**Cons:** No real trades executed

#### Prevention

1. **Auto-Start MT5:**
   - Add MT5 to Windows startup
   - Use task scheduler to start MT5 on boot

2. **Connection Monitoring:**
   - Bot automatically checks connection on startup
   - Sends Telegram notification on connection failure

3. **Credential Management:**
   - Store credentials in `.env` (not in code)
   - Never commit `.env` to repository
   - Use environment variables in production

---

### 9.5 Telegram API Errors

#### Problem Description

**Error Message:**
```
ERROR: Telegram API error: [error details]
WARNING: Failed to send Telegram message
ERROR: Bad Request: message is too long
```

**Frequency:** Low (cosmetic, doesn't block trading)

**Root Cause:**
- Invalid bot token
- Network connectivity issues
- Message too long (>4096 characters)
- Rate limiting (too many messages)
- Invalid chat ID

**Impact:**
- 🟡 **MEDIUM:** No Telegram notifications
- Bot continues trading normally
- Commands may not work

#### Solution 1: Verify Bot Token

**File:** `.env`
```bash
TELEGRAM_TOKEN=your_bot_token  # Get from @BotFather
TELEGRAM_CHAT_ID=your_chat_id  # Get from @userinfobot
```

**Test:**
```bash
curl https://api.telegram.org/bot<TOKEN>/getMe
```

#### Solution 2: Fix Long Messages

**File:** `src/clients/telegram_bot.py`

**Change:**
```python
def send_message(self, text, parse_mode="HTML"):
    """Send message with length check."""
    if len(text) > 4096:
        # Split into chunks
        chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for chunk in chunks:
            self.bot.send_message(chat_id=self.chat_id, text=chunk, parse_mode=parse_mode)
    else:
        self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode=parse_mode)
```

#### Solution 3: Handle Rate Limiting

**File:** `src/clients/telegram_bot.py`

**Change:**
```python
import time

def send_message(self, text, parse_mode="HTML"):
    """Send message with rate limiting."""
    try:
        self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode=parse_mode)
    except Exception as e:
        if "rate limit" in str(e).lower():
            time.sleep(1)  # Wait 1 second and retry
            self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode=parse_mode)
        else:
            logger.error(f"Telegram error: {str(e)}")
```

#### Prevention

1. **Monitor Telegram Status:**
   - Test bot with `/start` command
   - Check for error messages in logs

2. **Limit Message Frequency:**
   - Batch notifications
   - Use summary messages instead of individual updates

3. **Error Handling:**
   - Bot continues even if Telegram fails
   - Log errors but don't crash

---

### 9.6 Configuration Issues

#### Problem Description

**Error Message:**
```
ERROR: Missing required config: [key]
ERROR: Invalid configuration value
ERROR: Config file not found
```

**Frequency:** Low (usually on first setup)

**Root Cause:**
- Missing `config.json` file
- Missing required configuration keys
- Invalid JSON syntax
- Environment variables not set

**Impact:**
- 🔴 **CRITICAL:** Bot won't start
- Prevents all operations

#### Solution 1: Verify Config File

**File:** `config/config.json`

**Check:**
1. File exists in `config/` directory
2. Valid JSON syntax (use JSON validator)
3. All required keys present:
   - `telegram_token`
   - `mt5_login`
   - `mt5_password`
   - `mt5_server`
   - `symbol_mapping`
   - `risk_tiers`

#### Solution 2: Verify Environment Variables

**File:** `.env` (root directory)

**Required:**
```bash
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=your_server
```

**Test:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"Token: {os.getenv('TELEGRAM_TOKEN')}")
print(f"MT5 Login: {os.getenv('MT5_LOGIN')}")
```

#### Solution 3: Validate Configuration on Startup

**File:** `src/config.py`

**Add:**
```python
def validate_config(self):
    """Validate all required configuration."""
    required_keys = [
        "telegram_token",
        "mt5_login",
        "mt5_password",
        "mt5_server",
        "symbol_mapping",
        "risk_tiers"
    ]
    
    for key in required_keys:
        if not self.get(key):
            raise ValueError(f"Missing required config: {key}")
    
    return True
```

#### Prevention

1. **Use Config Template:**
   - Copy `config/config.json.example` to `config/config.json`
   - Fill in all required values

2. **Validate on Startup:**
   - Bot should validate config on startup
   - Show clear error messages for missing config

3. **Documentation:**
   - Keep configuration reference updated
   - Document all required fields

---

### 9.7 Log Spam Problems

#### Problem Description

**Symptom:**
- Log file grows extremely large (100MB+)
- Same error repeated thousands of times
- Makes debugging impossible
- Consumes disk space

**Common Causes:**
- Missing order chain errors (8,000+ occurrences)
- Duplicate alert warnings
- Price monitor service logging too frequently
- Error in loop without deduplication

**Impact:**
- 🟡 **MEDIUM:** Performance degradation
- Disk space issues
- Debugging becomes impossible

#### Solution 1: Enable Log Rotation (Quick Fix)

**File:** `src/main.py`

**Already Implemented:**
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

**Verify:**
- Log rotation is enabled
- Max file size: 10MB
- Backup count: 5 files

#### Solution 2: Reduce Log Verbosity

**File:** `config/config.json`

**Change:**
```json
{
  "debug": false  // Disable debug logging in production
}
```

**File:** `src/main.py`

**Change:**
```python
logging.basicConfig(
    level=logging.INFO,  # Use INFO instead of DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Solution 3: Add Error Deduplication

**File:** `src/utils/logger.py`

**Add:**
```python
class DeduplicatedLogger:
    def __init__(self):
        self.error_counts = {}
        self.max_repeats = 3
        
    def error(self, message):
        if message in self.error_counts:
            self.error_counts[message] += 1
            if self.error_counts[message] <= self.max_repeats:
                logger.error(message)
            elif self.error_counts[message] == self.max_repeats + 1:
                logger.error(f"{message} (suppressing further repeats)")
        else:
            self.error_counts[message] = 1
            logger.error(message)
```

#### Prevention

1. **Monitor Log Size:**
   - Check `logs/bot.log` size regularly
   - Set up alerts for large log files

2. **Use Appropriate Log Levels:**
   - DEBUG: Development only
   - INFO: Production standard
   - ERROR: Always log

3. **Implement Log Rotation:**
   - Already implemented (10MB, 5 backups)
   - Verify it's working

---

## 10. TROUBLESHOOTING GUIDE

### 10.1 Common Errors and Fixes

#### Error: "Signal BULLISH doesn't match trend BEARISH"

**Symptoms:**
- No trades executing
- Error in logs repeatedly
- Entry signals being rejected

**Diagnosis:**
1. Check trend alignment: `/trend_matrix`
2. Verify signal direction matches trend
3. Check if trends updated recently

**Fix:**
1. **Update Trends Manually:**
   ```
   /set_trend XAUUSD 1h bull
   /set_trend XAUUSD 15m bull
   ```

2. **Enable Auto Trend Updates:**
   ```
   /set_auto XAUUSD 1h
   /set_auto XAUUSD 15m
   ```

3. **Check TradingView Alerts:**
   - Verify trend alerts fire before entry alerts
   - Add delay in TradingView alert conditions

**Prevention:**
- Use auto trend mode for all timeframes
- Monitor trend matrix regularly
- Ensure TradingView alert timing is correct

---

#### Error: "Daily loss cap exceeded"

**Symptoms:**
- Trading paused automatically
- No new trades executing
- Warning in logs

**Diagnosis:**
1. Check current loss: `/view_risk_caps`
2. Verify risk tier settings
3. Check account balance

**Fix:**
1. **Clear Daily Loss (Testing Only):**
   ```
   /clear_daily_loss
   ```

2. **Increase Daily Limit:**
   ```
   /set_daily_cap 200
   ```

3. **Adjust Risk Tier:**
   - Edit `config/config.json`
   - Update `daily_loss_limit` for your tier

**Prevention:**
- Set appropriate loss limits (2-5% of balance)
- Monitor daily loss regularly
- Use risk tier matching your balance

---

#### Error: "Chain has missing order"

**Symptoms:**
- Log spam (thousands of warnings)
- Performance degradation
- Chain status shows STALE

**Diagnosis:**
1. Check chain status: `/profit_chains`
2. Verify orders in MT5 terminal
3. Check if orders were closed externally

**Fix:**
1. **Stop Problematic Chain:**
   ```
   /stop_profit_chain [chain_id]
   ```

2. **Stop All Chains:**
   ```
   /stop_all_profit_chains
   ```

3. **Restart Bot:**
   - Bot will cleanup stale chains on startup
   - Re-sync with MT5 positions

**Prevention:**
- Monitor chain status regularly
- Don't close orders manually in MT5
- Let bot manage all order closures

---

#### Error: "MT5 initialization failed"

**Symptoms:**
- Bot starts but no trades execute
- Error in startup logs
- Simulation mode enabled automatically

**Diagnosis:**
1. Check MT5 terminal running
2. Verify credentials in `.env`
3. Test MT5 connection manually

**Fix:**
1. **Start MT5 Terminal:**
   - Open MetaTrader 5
   - Login to account
   - Keep terminal running

2. **Verify Credentials:**
   ```bash
   # Check .env file
   MT5_LOGIN=your_login
   MT5_PASSWORD=your_password
   MT5_SERVER=XMGlobal-MT5 6  # Exact match
   ```

3. **Test Connection:**
   ```python
   from src.clients.mt5_client import MT5Client
   from src.config import Config
   
   config = Config()
   mt5 = MT5Client(config)
   success = mt5.initialize()
   print(f"Connected: {success}")
   ```

**Prevention:**
- Auto-start MT5 on system boot
- Use task scheduler for MT5 startup
- Monitor connection status

---

#### Error: "Telegram API error"

**Symptoms:**
- No Telegram notifications
- Commands not working
- Error in logs

**Diagnosis:**
1. Test bot token: `curl https://api.telegram.org/bot<TOKEN>/getMe`
2. Verify chat ID
3. Check network connectivity

**Fix:**
1. **Verify Bot Token:**
   - Get token from @BotFather
   - Update `.env` file
   - Restart bot

2. **Verify Chat ID:**
   - Get from @userinfobot
   - Update `.env` file
   - Test with `/start` command

3. **Check Network:**
   - Verify internet connection
   - Check firewall settings
   - Test Telegram API access

**Prevention:**
- Store credentials securely
- Test bot after credential changes
- Monitor Telegram API status

---

### 10.2 Log Analysis Guide

#### Understanding Log Levels

**DEBUG:**
- Detailed information for debugging
- Only enabled when `debug: true` in config
- Example: `[DEBUG] Calculating SL for XAUUSD`

**INFO:**
- General information about operations
- Standard production logging
- Example: `[INFO] Order placed: 123456`

**WARNING:**
- Non-critical issues
- Operations continue normally
- Example: `[WARNING] Chain has missing order`

**ERROR:**
- Critical issues requiring attention
- May block operations
- Example: `[ERROR] Signal BULLISH doesn't match trend BEARISH`

**CRITICAL:**
- System failures
- Bot may stop functioning
- Example: `[CRITICAL] MT5 connection lost`

#### Searching Logs

**Windows PowerShell:**
```powershell
# Search for errors
Select-String -Path logs/bot.log -Pattern "ERROR" | Select-Object -Last 20

# Search for specific symbol
Select-String -Path logs/bot.log -Pattern "XAUUSD"

# Count error types
Select-String -Path logs/bot.log -Pattern "ERROR" | Group-Object | Sort-Object Count -Descending
```

**Linux:**
```bash
# Search for errors
grep "ERROR" logs/bot.log | tail -20

# Search for specific symbol
grep "XAUUSD" logs/bot.log

# Count error types
grep "ERROR" logs/bot.log | sort | uniq -c | sort -rn
```

#### Common Log Patterns

**1. Trade Execution Flow:**
```
[INFO] Alert received: entry XAUUSD buy 5m
[INFO] Risk check passed
[INFO] Trend alignment: BULLISH
[INFO] Placing dual orders...
[INFO] Order A placed: 123456
[INFO] Order B placed: 123457
```

**2. Trade Rejection Flow:**
```
[INFO] Alert received: entry XAUUSD buy 5m
[INFO] Risk check passed
[ERROR] Signal BULLISH doesn't match trend BEARISH
[INFO] Trade rejected
```

**3. Re-entry Trigger:**
```
[INFO] TP hit for trade 123456
[INFO] Checking TP continuation...
[INFO] Price gap detected: 2.5 pips
[INFO] Placing re-entry order...
[INFO] Re-entry order placed: 123458
```

#### Log File Locations

- **Main Log:** `logs/bot.log`
- **Rotated Logs:** `logs/bot.log.1`, `logs/bot.log.2`, etc.
- **Max Size:** 10MB per file
- **Backups:** 5 files kept

---

### 10.3 Performance Issues

#### High CPU Usage

**Symptoms:**
- Bot consumes excessive CPU
- System becomes slow
- Log spam indicates loops

**Diagnosis:**
1. Check for log spam (missing order errors)
2. Verify price monitor interval
3. Check for infinite loops

**Fix:**
1. **Stop Problematic Chains:**
   ```
   /stop_all_profit_chains
   ```

2. **Increase Monitor Interval:**
   ```
   /set_monitor_interval 60  # 60 seconds instead of 30
   ```

3. **Restart Bot:**
   - Clears memory
   - Resets all services

**Prevention:**
- Monitor log file size
- Use appropriate monitor intervals
- Cleanup stale chains regularly

---

#### High Memory Usage

**Symptoms:**
- Bot uses excessive RAM
- System memory warnings
- Bot becomes unresponsive

**Diagnosis:**
1. Check open trades count
2. Verify chain count
3. Check for memory leaks

**Fix:**
1. **Close Old Trades:**
   - Review open trades: `/trades`
   - Close manually if needed

2. **Cleanup Chains:**
   ```
   /stop_all_profit_chains
   ```

3. **Restart Bot:**
   - Clears all memory
   - Resets state

**Prevention:**
- Limit maximum open trades
- Cleanup completed chains
- Monitor memory usage

---

#### Slow Response Times

**Symptoms:**
- Telegram commands slow
- Webhook processing delayed
- Price updates lagging

**Diagnosis:**
1. Check network connectivity
2. Verify MT5 connection
3. Check database size

**Fix:**
1. **Optimize Database:**
   ```sql
   VACUUM;  -- SQLite optimization
   ```

2. **Reduce Log Verbosity:**
   - Set `debug: false` in config
   - Use INFO level logging

3. **Increase Monitor Interval:**
   ```
   /set_monitor_interval 60
   ```

**Prevention:**
- Regular database maintenance
- Appropriate log levels
- Optimize price monitor frequency

---

### 10.4 Deployment Problems

#### Bot Won't Start

**Symptoms:**
- Error on startup
- Bot crashes immediately
- No logs generated

**Diagnosis:**
1. Check Python version: `python --version` (need 3.8+)
2. Verify dependencies: `pip list`
3. Check configuration files

**Fix:**
1. **Verify Python Version:**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Configuration:**
   - Verify `config/config.json` exists
   - Check `.env` file exists
   - Validate JSON syntax

**Prevention:**
- Use virtual environment
- Document setup steps
- Test on clean system

---

#### Webhook Not Receiving Alerts

**Symptoms:**
- No trades executing
- No alerts in logs
- TradingView shows webhook sent

**Diagnosis:**
1. Check webhook URL accessibility
2. Verify server is running
3. Check firewall settings

**Fix:**
1. **Test Webhook Endpoint:**
   ```bash
   curl -X POST http://your-server:80/webhook \
     -H "Content-Type: application/json" \
     -d '{"type":"entry","symbol":"XAUUSD","signal":"buy","tf":"5m","price":4025.50}'
   ```

2. **Check Server Status:**
   ```bash
   curl http://your-server:80/health
   ```

3. **Verify Firewall:**
   - Port 80 must be open
   - Allow incoming connections

**Prevention:**
- Use reverse proxy (nginx)
- Enable HTTPS
- Monitor webhook endpoint

---

#### Database Corruption

**Symptoms:**
- Database errors in logs
- Trades not saving
- Statistics incorrect

**Diagnosis:**
1. Check database file: `data/trading_bot.db`
2. Verify file permissions
3. Check disk space

**Fix:**
1. **Backup Database:**
   ```bash
   cp data/trading_bot.db data/trading_bot.db.backup
   ```

2. **Repair Database:**
   ```python
   import sqlite3
   conn = sqlite3.connect('data/trading_bot.db')
   conn.execute('VACUUM')
   conn.close()
   ```

3. **Restore from Backup:**
   ```bash
   cp data/trading_bot.db.backup data/trading_bot.db
   ```

**Prevention:**
- Regular database backups
- Monitor disk space
- Use transactions for writes

---

## 11. FUTURE PLANS & IDEAS

### 11.1 Planned Improvements

#### 1. Enhanced Trend Matching Logic

**Current State:**
- Strict trend-signal matching causes many rejections
- No tolerance for timing delays

**Planned:**
- Add configurable tolerance window (e.g., 5 minutes)
- Allow trades if trend updated recently
- Implement trend confidence scoring
- Add trend prediction based on historical patterns

**Priority:** High
**Estimated Effort:** 2-3 days

---

#### 2. Advanced Risk Management

**Current State:**
- Fixed daily/lifetime loss caps
- Tier-based lot sizing

**Planned:**
- Dynamic risk adjustment based on win rate
- Volatility-based position sizing
- Correlation-based risk limits
- Portfolio-level risk management

**Priority:** Medium
**Estimated Effort:** 1 week

---

#### 3. Improved Chain Management

**Current State:**
- Manual chain cleanup required
- Missing order errors cause log spam

**Planned:**
- Automatic stale chain detection and cleanup
- Real-time chain synchronization with MT5
- Chain health monitoring and alerts
- Automatic chain recovery mechanisms

**Priority:** High
**Estimated Effort:** 3-4 days

---

#### 4. Enhanced Monitoring and Alerts

**Current State:**
- Basic Telegram notifications
- Limited monitoring capabilities

**Planned:**
- Real-time dashboard (web interface)
- Advanced analytics and reporting
- Performance metrics tracking
- Alert system for critical events
- Email notifications for important events

**Priority:** Medium
**Estimated Effort:** 1-2 weeks

---

### 11.2 Feature Ideas

#### 1. Multi-Account Support

**Idea:**
- Support multiple MT5 accounts simultaneously
- Independent risk management per account
- Portfolio-level view across accounts
- Account-specific configurations

**Benefits:**
- Diversify trading across accounts
- Test strategies on different accounts
- Manage multiple trading accounts from one bot

**Complexity:** High
**Estimated Effort:** 2-3 weeks

---

#### 2. Strategy Backtesting

**Idea:**
- Historical data backtesting
- Strategy performance analysis
- Parameter optimization
- Walk-forward analysis

**Benefits:**
- Test strategies before live trading
- Optimize parameters
- Understand strategy performance

**Complexity:** High
**Estimated Effort:** 3-4 weeks

---

#### 3. Machine Learning Integration

**Idea:**
- ML-based trend prediction
- Signal confidence scoring
- Adaptive risk management
- Pattern recognition

**Benefits:**
- Improve trade selection
- Reduce false signals
- Optimize entry/exit timing

**Complexity:** Very High
**Estimated Effort:** 1-2 months

---

#### 4. Social Trading Features

**Idea:**
- Share trading signals
- Follow other traders
- Copy trading functionality
- Performance leaderboard

**Benefits:**
- Learn from successful traders
- Diversify strategies
- Community engagement

**Complexity:** High
**Estimated Effort:** 2-3 weeks

---

### 11.3 Optimization Opportunities

#### 1. Database Optimization

**Current:**
- SQLite with basic queries
- No indexing on frequently queried fields

**Optimization:**
- Add indexes on trade_id, symbol, status
- Implement connection pooling
- Use prepared statements
- Consider PostgreSQL for production

**Expected Impact:**
- 50-70% faster query times
- Better performance with large datasets

---

#### 2. Price Monitor Optimization

**Current:**
- Checks all chains every 30 seconds
- No caching of price data

**Optimization:**
- Cache prices for 5-10 seconds
- Only check chains with pending conditions
- Batch price requests
- Use websocket for real-time prices

**Expected Impact:**
- 60-80% reduction in API calls
- Faster response times

---

#### 3. Logging Optimization

**Current:**
- Some redundant logging
- No structured logging

**Optimization:**
- Implement structured logging (JSON)
- Add log levels per module
- Reduce duplicate log messages
- Use log aggregation tools

**Expected Impact:**
- Smaller log files
- Easier log analysis
- Better debugging

---

#### 4. Memory Management

**Current:**
- Some objects kept in memory longer than needed
- No explicit cleanup

**Optimization:**
- Implement object pooling
- Add explicit cleanup methods
- Use weak references where appropriate
- Monitor memory usage

**Expected Impact:**
- 30-40% reduction in memory usage
- Better long-term stability

---

### 11.4 Enhancement Suggestions

#### 1. Web Dashboard

**Enhancement:**
- Real-time web interface
- Trade visualization
- Performance charts
- Configuration management via web UI

**Benefits:**
- Better user experience
- Mobile-friendly access
- Real-time monitoring

**Technology:** React + FastAPI
**Estimated Effort:** 2-3 weeks

---

#### 2. Advanced Analytics

**Enhancement:**
- Detailed performance metrics
- Win rate by symbol/timeframe
- Risk-adjusted returns (Sharpe ratio)
- Drawdown analysis
- Trade correlation analysis

**Benefits:**
- Better strategy understanding
- Identify profitable patterns
- Optimize trading parameters

**Estimated Effort:** 1 week

---

#### 3. Automated Reporting

**Enhancement:**
- Daily/weekly/monthly reports
- Email delivery
- PDF generation
- Performance summaries

**Benefits:**
- Track progress over time
- Share performance with others
- Historica