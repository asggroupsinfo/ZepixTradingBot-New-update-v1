#### 6.5 Debugging Tips

##### Enable Debug Logging

**File:** `config/config.json`

```json
{
  "debug": true  // Enable detailed debug logs
}
```

**Log Location:** `logs/bot.log`

**View Logs:**

```bash
# Windows PowerShell
Get-Content logs/bot.log -Tail 50 -Wait

# Linux
tail -f logs/bot.log
```

##### Common Debug Scenarios

**1. Trade Not Executing**

**Check:**

- Logs for "ERROR: Signal BULLISH doesn't match trend BEARISH"
- Logs for "BLOCKED: Daily loss limit reached"
- Logs for "Trend not aligned for LOGIC1"
- Telegram: `/status` to check trading paused

**Debug Steps:**

```python
# Add debug logging in trading_engine.py
print(f"[DEBUG] Entry signal: {alert.signal}, Trend: {alignment['direction']}")
print(f"[DEBUG] Alignment check: {alignment}")
print(f"[DEBUG] Risk check: {risk_manager.can_trade()}")
```

**2. Re-entry Not Triggering**

**Check:**

- Logs for "SL Hunt Re-entry" or "TP Continuation"
- Price monitor service running (every 30 seconds)
- Re-entry config enabled: `/reentry_config`

**Debug Steps:**

```python
# Check price monitor in price_monitor_service.py
print(f"[DEBUG] Current price: {current_price}, SL+offset: {sl_offset_price}")
print(f"[DEBUG] SL hunt pending: {self.sl_hunt_pending}")
```

**3. Profit Booking Not Progressing**

**Check:**

- Logs for "Profit target reached"
- Chain status: `/profit_chains`
- Order PnL values

**Debug Steps:**

```python
# Check profit booking in profit_booking_manager.py
print(f"[DEBUG] Chain: {chain.chain_id}, Level: {chain.current_level}")
print(f"[DEBUG] Total profit: {chain.total_profit}, Target: {target}")
print(f"[DEBUG] Active orders: {chain.active_orders}")
```

**4. MT5 Connection Issues**

**Check:**

- MT5 terminal running
- Credentials correct in `.env`
- Server name exact match (case-sensitive)

**Debug Steps:**

```python
# Test MT5 connection
from src.clients.mt5_client import MT5Client
from src.config import Config

config = Config()
mt5 = MT5Client(config)
success = mt5.initialize()
print(f"MT5 Connected: {success}")
```

##### Log Analysis

**Search for Errors:**

```bash
# Windows PowerShell
Select-String -Path logs/bot.log -Pattern "ERROR" | Select-Object -Last 20

# Linux
grep "ERROR" logs/bot.log | tail -20
```

**Search for Specific Symbol:**

```bash
# Windows PowerShell
Select-String -Path logs/bot.log -Pattern "XAUUSD"

# Linux
grep "XAUUSD" logs/bot.log
```

**Count Error Types:**

```bash
# Windows PowerShell
Select-String -Path logs/bot.log -Pattern "ERROR" | Group-Object | Sort-Object Count -Descending

# Linux
grep "ERROR" logs/bot.log | sort | uniq -c | sort -rn
```

##### Interactive Debugging

**Python REPL:**

```python
# Start Python in project directory
python

# Import and test
from src.config import Config
from src.managers.risk_manager import RiskManager

config = Config()
risk_manager = RiskManager(config)

# Check risk status
print(risk_manager.can_trade())
print(risk_manager.daily_loss)
print(risk_manager.lifetime_loss)
```

**Telegram Commands for Debugging:**

- `/status` - Check bot status
- `/view_risk_caps` - Check risk limits
- `/trend_matrix` - Check trend alignment
- `/reentry_config` - Check re-entry settings
- `/profit_chains` - Check profit chains

---

#### 6.6 Best Practices

##### Code Quality

**1. Follow PEP 8 Style Guide**

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

**Example:**

```python
def calculate_sl_price(
    symbol: str,
    entry: float,
    direction: str,
    lot_size: float,
    balance: float
) -> float:
    """
    Calculate stop loss price based on risk tier and symbol.
    
    Args:
        symbol: Trading symbol (e.g., "XAUUSD")
        entry: Entry price
        direction: "buy" or "sell"
        lot_size: Lot size for trade
        balance: Account balance
        
    Returns:
        Stop loss price
    """
    # Implementation
    pass
```

**2. Use Type Hints**

```python
from typing import Dict, List, Optional

def process_alert(data: Dict[str, Any]) -> bool:
    """Process trading alert."""
    pass
```

**3. Error Handling**

Always wrap risky operations:

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {str(e)}")
    # Handle gracefully
    return default_value
except Exception as e:
    logger.critical(f"Unexpected error: {str(e)}")
    raise
```

**4. Logging Best Practices**

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical failure")
```

##### Configuration Management

**1. Never Hardcode Values**

❌ **Bad:**

```python
lot_size = 0.1  # Hardcoded
```

✅ **Good:**

```python
lot_size = self.config.get("fixed_lot_sizes", {}).get("10000", 0.1)
```

**2. Use Environment Variables for Secrets**

❌ **Bad:**

```python
token = "1234567890:ABC"  # In code
```

✅ **Good:**

```python
token = os.getenv("TELEGRAM_TOKEN")  # From .env
```

**3. Validate Configuration on Startup**

```python
def validate_config(config: Config) -> bool:
    """Validate configuration on startup."""
    required_keys = ["telegram_token", "mt5_login", "mt5_server"]
    for key in required_keys:
        if not config.get(key):
            raise ValueError(f"Missing required config: {key}")
    return True
```

##### Testing Best Practices

**1. Test in Simulation Mode First**

```bash
# Enable simulation mode
/simulation_mode on

# Test with sample alerts
# Verify behavior before live trading
```

**2. Test Individual Components**

```python
# Test risk manager
def test_risk_manager():
    risk_manager = RiskManager(config)
    assert risk_manager.can_trade() == True
    assert risk_manager.get_fixed_lot_size(10000) == 0.1
```

**3. Test Edge Cases**

- Empty alerts
- Invalid symbols
- Extreme price values
- Network failures
- Database errors

##### Performance Optimization

**1. Use Async/Await for I/O Operations**

```python
async def process_alert(data):
    # Non-blocking operations
    result = await trading_engine.process_alert(data)
    return result
```

**2. Cache Expensive Operations**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_trend(symbol: str, timeframe: str) -> str:
    """Cached trend lookup."""
    return trend_manager.get_trend(symbol, timeframe)
```

**3. Batch Database Operations**

```python
# Instead of multiple inserts
for trade in trades:
    db.save_trade(trade)

# Batch insert
db.save_trades_batch(trades)
```

##### Security Best Practices

**1. Never Commit Secrets**

- Use `.env` file (in `.gitignore`)
- Never commit `.env` to repository
- Use environment variables in production

**2. Validate All Inputs**

```python
def validate_alert(alert_data: Dict) -> bool:
    """Validate alert before processing."""
    required_fields = ["type", "symbol", "signal", "tf"]
    for field in required_fields:
        if field not in alert_data:
            return False
    return True
```

**3. Sanitize User Inputs**

```python
def sanitize_symbol(symbol: str) -> str:
    """Sanitize symbol input."""
    # Remove special characters
    return symbol.upper().strip()
```

##### Documentation Best Practices

**1. Document All Public Methods**

```python
def place_order(
    symbol: str,
    direction: str,
    lot_size: float
) -> Optional[int]:
    """
    Place order on MT5.
    
    Args:
        symbol: Trading symbol
        direction: "buy" or "sell"
        lot_size: Lot size
        
    Returns:
        Trade ID if successful, None otherwise
        
    Raises:
        MT5ConnectionError: If MT5 not connected
    """
    pass
```

**2. Keep README Updated**

- Update installation steps
- Document new features
- Update configuration examples

**3. Add Inline Comments for Complex Logic**

```python
# Calculate SL based on risk tier and volatility
# Tier 10000 uses 150 pips for EURUSD (LOW volatility)
# Tier 25000 uses 50 pips for EURUSD (MEDIUM volatility)
sl_pips = get_sl_pips(symbol, tier, volatility)
```

---

## 7. CONFIGURATION REFERENCE

### 7.1 Main Configuration File

**File:** `config/config.json`

#### Telegram Configuration

```json
{
  "telegram_token": "your_bot_token",
  "telegram_chat_id": 123456789,
  "allowed_telegram_user": 123456789
}
```

**Description:**

- `telegram_token`: Bot token from @BotFather
- `telegram_chat_id`: Your Telegram chat ID
- `allowed_telegram_user`: User ID allowed to use bot

---

#### MT5 Configuration

```json
{
  "mt5_login": 123456,
  "mt5_password": "your_password",
  "mt5_server": "XMGlobal-MT5 6",
  "mt5_retries": 3,
  "mt5_wait": 5
}
```

**Description:**

- `mt5_login`: MT5 account login number
- `mt5_password`: MT5 account password
- `mt5_server`: MT5 server name (exact match, case-sensitive)
- `mt5_retries`: Number of retry attempts for MT5 operations
- `mt5_wait`: Wait time between retries (seconds)

---

#### Symbol Mapping

```json
{
  "symbol_mapping": {
    "XAUUSD": "GOLD",
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "USDCAD": "USDCAD",
    "AUDUSD": "AUDUSD",
    "NZDUSD": "NZDUSD",
    "EURJPY": "EURJPY",
    "GBPJPY": "GBPJPY",
    "AUDJPY": "AUDJPY"
  }
}
```

**Description:**

- Maps TradingView symbols to MT5 broker symbols
- Key: TradingView symbol (uppercase)
- Value: MT5 broker symbol (as shown in MT5)

---

#### Fixed Lot Sizes

```json
{
  "fixed_lot_sizes": {
    "5000": 0.05,
    "10000": 0.1,
    "25000": 1.0,
    "100000": 5.0
  },
  "manual_lot_overrides": {
    "5000": 0.1
  }
}
```

**Description:**

- `fixed_lot_sizes`: Default lot sizes per risk tier
- `manual_lot_overrides`: Manual overrides (takes precedence)
- Tier keys: "5000", "10000", "25000", "50000", "100000"

---

#### Risk Tiers

```json
{
  "risk_tiers": {
    "5000": {
      "daily_loss_limit": 100.0,
      "max_total_loss": 500
    },
    "10000": {
      "daily_loss_limit": 400,
      "max_total_loss": 1000
    },
    "25000": {
      "daily_loss_limit": 1000,
      "max_total_loss": 2500
    },
    "50000": {
      "daily_loss_limit": 2000,
      "max_total_loss": 5000
    },
    "100000": {
      "daily_loss_limit": 4000,
      "max_total_loss": 10000
    }
  }
}
```

**Description:**

- `daily_loss_limit`: Maximum daily loss before trading paused
- `max_total_loss`: Maximum lifetime loss before trading paused
- Tier determined automatically based on account balance

---

#### Symbol Configuration

```json
{
  "symbol_config": {
    "EURUSD": {
      "volatility": "LOW",
      "pip_size": 0.0001,
      "pip_value_per_std_lot": 10.0,
      "min_sl_distance": 0.0005
    },
    "XAUUSD": {
      "volatility": "HIGH",
      "pip_size": 0.01,
      "pip_value_per_std_lot": 1.0,
      "min_sl_distance": 0.1,
      "is_gold": true
    }
  }
}
```

**Description:**

- `volatility`: "LOW", "MEDIUM", or "HIGH"
- `pip_size`: Pip size for symbol (0.0001 for forex, 0.01 for gold)
- `pip_value_per_std_lot`: Dollar value per pip for 1 standard lot
- `min_sl_distance`: Minimum SL distance (broker requirement)
- `is_gold`: Special flag for gold/XAUUSD

---

#### Re-entry Configuration

```json
{
  "re_entry_config": {
    "max_chain_levels": 2,
    "sl_reduction_per_level": 0.5,
    "recovery_window_minutes": 30,
    "min_time_between_re_entries": 60,
    "sl_hunt_offset_pips": 1.0,
    "tp_reentry_enabled": true,
    "sl_hunt_reentry_enabled": true,
    "reversal_exit_enabled": true,
    "exit_continuation_enabled": true,
    "price_monitor_interval_seconds": 30,
    "tp_continuation_price_gap_pips": 2.0,
    "sl_hunt_cooldown_seconds": 60,
    "price_recovery_check_minutes": 2
  }
}
```

**Description:**

- `max_chain_levels`: Maximum re-entry levels (default: 2)
- `sl_reduction_per_level`: SL reduction per level (0.5 = 50%)
- `recovery_window_minutes`: Window for SL recovery
- `min_time_between_re_entries`: Minimum time between re-entries (seconds)
- `sl_hunt_offset_pips`: Offset above SL for re-entry (1.0 pip)
- `tp_reentry_enabled`: Enable TP continuation re-entry
- `sl_hunt_reentry_enabled`: Enable SL hunt re-entry
- `reversal_exit_enabled`: Enable reversal exit handling
- `exit_continuation_enabled`: Enable exit continuation re-entry
- `price_monitor_interval_seconds`: Price check interval (30 seconds)
- `tp_continuation_price_gap_pips`: Price gap after TP for re-entry (2.0 pips)
- `sl_hunt_cooldown_seconds`: Cooldown between SL hunt checks
- `price_recovery_check_minutes`: Time to check price recovery after SL

---

#### Dual Order Configuration

```json
{
  "dual_order_config": {
    "enabled": true,
    "split_ratio": 0.5
  }
}
```

**Description:**

- `enabled`: Enable/disable dual order system
- `split_ratio`: Not used (both orders use same lot size)

---

#### Profit Booking Configuration

```json
{
  "profit_booking_config": {
    "enabled": true,
    "min_profit": 7.0,
    "multipliers": [1, 2, 4, 8, 16],
    "max_level": 4
  }
}
```

**Description:**

- `enabled`: Enable/disable profit booking system
- `min_profit`: Minimum profit per order ($7)
- `multipliers`: Order multipliers per level [1, 2, 4, 8, 16]
- `max_level`: Maximum profit booking level (0-4)

---

#### SL Systems Configuration

```json
{
  "active_sl_system": "sl-1",
  "sl_systems": {
    "sl-1": {
      "name": "SL-1 ORIGINAL",
      "description": "Wide/Conservative SL system",
      "symbols": {
        "XAUUSD": {
          "5000": {
            "sl_pips": 1000,
            "risk_dollars": 50,
            "risk_percent": 1.0
          },
          "10000": {
            "sl_pips": 1500,
            "risk_dollars": 150,
            "risk_percent": 1.5
          }
        }
      }
    },
    "sl-2": {
      "name": "SL-2 RECOMMENDED",
      "description": "Tight/Aggressive SL system",
      "symbols": {
        "XAUUSD": {
          "5000": {
            "sl_pips": 500,
            "risk_dollars": 50,
            "risk_percent": 1.0
          }
        }
      }
    }
  }
}
```

**Description:**

- `active_sl_system`: Currently active SL system ("sl-1" or "sl-2")
- `sl_systems`: SL system definitions
  - `sl_pips`: Stop loss in pips
  - `risk_dollars`: Risk amount in dollars
  - `risk_percent`: Risk as percentage of balance

---

#### Profit Booking SL Configuration

```json
{
  "profit_booking_config": {
    "sl_system": {
      "enabled": true,
      "current_mode": "SL-1.1",
      "modes": {
        "SL-1.1": {
          "LOGIC1": 10.0,
          "LOGIC2": 10.0,
          "LOGIC3": 10.0
        },
        "SL-2.1": {
          "LOGIC1": 10.0,
          "LOGIC2": 10.0,
          "LOGIC3": 10.0
        }
      }
    }
  }
}
```

**Description:**

- `enabled`: Enable profit booking SL system
- `current_mode`: Active mode ("SL-1.1" or "SL-2.1")
- `modes`: SL amounts per logic per mode ($10 fixed)

---

#### General Configuration

```json
{
  "rr_ratio": 1.5,
  "simulate_orders": true,
  "debug": true,
  "strategies": ["LOGIC1", "LOGIC2", "LOGIC3"],
  "daily_reset_time": "03:35"
}
```

**Description:**

- `rr_ratio`: Risk-reward ratio (1.5 = 1:1.5)
- `simulate_orders`: Enable simulation mode (no real trades)
- `debug`: Enable debug logging
- `strategies`: Enabled strategies
- `daily_reset_time`: Time to reset daily loss (HH:MM format)

---

### 7.2 Environment Variables

**File:** `.env` (root directory)

```bash
# Telegram Configuration
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# MT5 Configuration
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server_name

# Optional: Override config.json settings
SIMULATE_ORDERS=true
DEBUG=true
```

**Priority:** Environment variables override `config.json` values

**Security:** Never commit `.env` file to repository

---

### 7.3 Risk Tier Settings

#### Tier Determination

Tier is automatically determined based on account balance:

| Balance Range | Tier | Lot Size | Daily Loss Limit | Lifetime Loss Limit |
|--------------|------|----------|------------------|---------------------|
| < $7,500 | 5000 | 0.05 | $100 | $500 |
| $7,500 - $17,499 | 10000 | 0.1 | $400 | $1,000 |
| $17,500 - $37,499 | 25000 | 1.0 | $1,000 | $2,500 |
| $37,500 - $74,999 | 50000 | 1.0 | $2,000 | $5,000 |
| ≥ $75,000 | 100000 | 5.0 | $4,000 | $10,000 |

#### Manual Override

Override lot size for specific tier:

```json
{
  "manual_lot_overrides": {
    "5000": 0.1  // Override tier 5000 lot size to 0.1
  }
}
```

---

### 7.4 SL System Configurations

#### SL-1 System (Wide/Conservative)

**Purpose:** Wider stops, more conservative approach

**Characteristics:**

- Higher pip values
- Lower risk percentage for lower tiers
- Better for volatile markets

**Example (XAUUSD):**

- Tier 5000: 1000 pips, $50 risk (1.0%)
- Tier 10000: 1500 pips, $150 risk (1.5%)
- Tier 25000: 500 pips, $500 risk (2.0%)

#### SL-2 System (Tight/Aggressive)

**Purpose:** Tighter stops, more aggressive approach

**Characteristics:**

- Lower pip values
- Higher risk percentage
- Better for stable markets

**Example (XAUUSD):**

- Tier 5000: 500 pips, $50 risk (1.0%)
- Tier 10000: 750 pips, $150 risk (1.5%)
- Tier 25000: 250 pips, $500 risk (2.0%)

#### Switching SL Systems

**Via Telegram:**

```
/profit_sl_mode SL-1.1  # Switch to SL-1.1
/profit_sl_mode SL-2.1  # Switch to SL-2.1
```

**Via Config:**

```json
{
  "profit_booking_config": {
    "sl_system": {
      "current_mode": "SL-2.1"
    }
  }
}
```

---

### 7.5 Feature Toggles

#### Enable/Disable Features

**Dual Orders:**

```json
{
  "dual_order_config": {
    "enabled": true  // false to disable
  }
}
```

**Profit Booking:**

```json
{
  "profit_booking_config": {
    "enabled": true  // false to disable
  }
}
```

**Re-entry Systems:**

```json
{
  "re_entry_config": {
    "tp_reentry_enabled": true,
    "sl_hunt_reentry_enabled": true,
    "exit_continuation_enabled": true
  }
}
```

**Strategies:**

```json
{
  "strategies": ["LOGIC1", "LOGIC2", "LOGIC3"]  // Remove to disable
}
```

**Via Telegram:**

- `/toggle_dual_orders` - Toggle dual orders
- `/toggle_profit_booking` - Toggle profit booking
- `/tp_system off` - Disable TP re-entry
- `/sl_hunt off` - Disable SL hunt
- `/logic1_off` - Disable LOGIC1

---

## 8. API REFERENCE

### 8.1 Webhook Endpoint

#### POST /webhook

**Purpose:** Receive TradingView alerts

**URL:** `http://your-server:80/webhook`

**Method:** `POST`

**Content-Type:** `application/json`

**Request Body:**

```json
{
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "buy",
  "tf": "5m",
  "price": 4025.50,
  "strategy": "ZepixPremium"
}
```

**Alert Types:**

1. **Entry Alert:**

```json
{
  "type": "entry",
  "symbol": "XAUUSD",
  "signal": "buy",  // or "sell"
  "tf": "5m",       // or "15m", "1h"
  "price": 4025.50,
  "strategy": "ZepixPremium"
}
```

2. **Trend Alert:**

```json
{
  "type": "trend",
  "symbol": "XAUUSD",
  "signal": "bull",  // or "bear"
  "tf": "5m",        // or "15m", "1h", "1d"
  "price": 4025.50,
  "strategy": "ZepixPremium"
}
```

3. **Bias Alert:**

```json
{
  "type": "bias",
  "symbol": "XAUUSD",
  "signal": "bull",  // or "bear"
  "tf": "1h",        // or "15m", "5m", "1d"
  "price": 4025.50,
  "strategy": "ZepixPremium"
}
```

4. **Exit Alert:**

```json
{
  "type": "exit",
  "symbol": "XAUUSD",
  "signal": "bull",  // or "bear"
  "tf": "5m",        // or "15m", "1h"
  "price": 4025.50,
  "strategy": "ZepixPremium"
}
```

5. **Reversal Alert:**

```json
{
  "type": "reversal",
  "symbol": "XAUUSD",
  "signal": "reversal_bull",  // or "reversal_bear", "bull", "bear"
  "tf": "5m",                  // or "15m"
  "price": 4025.50,
  "strategy": "ZepixPremium"
}
```

**Response (Success):**

```json
{
  "status": "success",
  "message": "Alert processed"
}
```

**Response (Rejected):**

```json
{
  "status": "rejected",
  "message": "Alert validation failed"
}
```

**Response (Error):**

```json
{
  "detail": "Webhook processing error: [error message]"
}
```

**Status Codes:**

- `200 OK` - Request processed (success or rejection)
- `400 Bad Request` - Invalid request or processing error
- `404 Not Found` - Invalid endpoint

---

### 8.2 Health Check Endpoint

#### GET /health

**Purpose:** Check bot health status

**URL:** `http://your-server:80/health`

**Method:** `GET`

**Response:**

```json
{
  "status": "healthy",
  "version": "2.0",
  "timestamp": "2025-01-18T12:34:56.789Z",
  "daily_loss": 150.0,
  "lifetime_loss": 500.0,
  "mt5_connected": true,
  "features": {
    "fixed_lots": true,
    "reentry_system": true,
    "sl_hunting_protection": true,
    "1_1_rr": true
  }
}
```

**Status Code:** `200 OK`

---

### 8.3 Status Endpoint

#### GET /status

**Purpose:** Get bot status with open trades

**URL:** `http://your-server:80/status`

**Method:** `GET`

**Response:**

```json
{
  "status": "running",
  "trading_paused": false,
  "simulation_mode": false,
  "daily_profit": 250.0,
  "daily_loss": 150.0,
  "lifetime_loss": 500.0,
  "total_trades": 45,
  "winning_trades": 28,
  "win_rate": 62.22,
  "open_trades": [
    {
      "symbol": "XAUUSD",
      "entry": 4025.50,
      "sl": 4020.00,
      "tp": 4035.25,
      "lot_size": 0.1,
      "direction": "buy",
      "strategy": "LOGIC1",
      "status": "open",
      "trade_id": 123456,
      "open_time": "2025-01-18T10:30:00",
      "close_time": null,
      "pnl": null,
      "chain_id": "XAUUSD_abc123",
      "chain_level": 1,
      "is_re_entry": false,
      "order_type": "TP_TRAIL",
      "profit_chain_id": null,
      "profit_level": 0
    }
  ],
  "active_chains": 2,
  "active_profit_chains": 1
}
```

**Status Code:** `200 OK`

---

### 8.4 Statistics Endpoint

#### GET /stats

**Purpose:** Get trading statistics

**URL:** `http://your-server:80/stats`

**Method:** `GET`

**Response:**

```json
{
  "daily_profit": 250.0,
  "daily_loss": 150.0,
  "lifetime_loss": 500.0,
  "total_trades": 45,
  "winning_trades": 28,
  "win_rate": 62.22,
  "current_risk_tier": "10000",
  "risk_parameters": {
    "daily_loss_limit": 400.0,
    "max_total_loss": 1000.0
  },
  "trading_paused": false,
  "simulation_mode": false,
  "lot_size": 0.1,
  "balance": 9264.90
}
```

**Status Code:** `200 OK`

---

### 8.5 Trading Control Endpoints

#### POST /pause

**Purpose:** Pause all trading

**URL:** `http://your-server:80/pause`

**Method:** `POST`

**Response:**

```json
{
  "status": "success",
  "message": "Trading paused"
}
```

**Status Code:** `200 OK`

---

#### POST /resume

**Purpose:** Resume trading

**URL:** `http://your-server:80/resume`

**Method:** `POST`

**Response:**

```json
{
  "status": "success",
  "message": "Trading resumed"
}
```

**Status Code:** `200 OK`

---

### 8.6 Trend Management Endpoints

#### GET /trends

**Purpose:** Get all timeframe trends

**URL:** `http://your-server:80/trends`

**Method:** `GET`

**Response:**

```json
{
  "status": "success",
  "trends": {
    "XAUUSD": {
      "5m": "BULLISH",
      "15m": "BEARISH",
      "1h": "BULLISH",
      "1d": "NEUTRAL"
    },
    "EURUSD": {
      "5m": "NEUTRAL",
      "15m": "NEUTRAL",
      "1h": "NEUTRAL",
      "1d": "NEUTRAL"
    }
  }
}
```

**Status Code:** `200 OK`

---

#### POST /set_trend

**Purpose:** Set trend via API

**URL:** `http://your-server:80/set_trend`

**Method:** `POST`

**Parameters:**

- `symbol` (string): Trading symbol (e.g., "XAUUSD")
- `timeframe` (string): Timeframe ("5m", "15m", "1h", "1d")
- `trend` (string): Trend direction ("bull", "bear", "neutral")
- `mode` (string, optional): "MANUAL" or "AUTO" (default: "MANUAL")

**Response (Success):**

```json
{
  "status": "success",
  "message": "Trend set for XAUUSD 1h: BULLISH"
}
```

**Response (Error):**

```json
{
  "status": "error",
  "message": "Error message here"
}
```

**Status Code:** `200 OK`

---

### 8.7 Re-entry Chains Endpoint

#### GET /chains

**Purpose:** Get active re-entry chains

**URL:** `http://your-server:80/chains`

**Method:** `GET`

**Response:**

```json
{
  "status": "success",
  "chains": [
    {
      "chain_id": "XAUUSD_abc123",
      "symbol": "XAUUSD",
      "direction": "buy",
      "original_entry": 4025.50,
      "original_sl_distance": 5.50,
      "current_level": 2,
      "max_level": 2,
      "total_profit": 0.0,
      "trades": [123456, 123457],
      "status": "active",
      "created_at": "2025-01-18T10:30:00",
      "last_update": "2025-01-18T11:00:00",
      "trend_at_creation": {
        "1h": "BULLISH",
        "15m": "BULLISH"
      },
      "metadata": {
        "sl_system_used": "sl-1",
        "sl_reduction_percent": 0,
        "original_sl_pips": 55.0,
        "applied_sl_pips": 55.0
      }
    }
  ]
}
```

**Status Code:** `200 OK`

---

### 8.8 Lot Size Configuration Endpoints

#### GET /lot_config

**Purpose:** Get lot size configuration

**URL:** `http://your-server:80/lot_config`

**Method:** `GET`

**Response:**

```json
{
  "fixed_lots": {
    "5000": 0.05,
    "10000": 0.1,
    "25000": 1.0,
    "100000": 5.0
  },
  "manual_overrides": {
    "5000": 0.1
  },
  "current_balance": 9264.90,
  "current_lot": 0.1
}
```

**Status Code:** `200 OK`

---

#### POST /set_lot_size

**Purpose:** Set manual lot size override

**URL:** `http://your-server:80/set_lot_size`

**Method:** `POST`

**Parameters:**

- `tier` (int): Risk tier (5000, 10000, 25000, 50000, 100000)
- `lot_size` (float): Lot size to set

**Response (Success):**

```json
{
  "status": "success",
  "message": "Lot size set: $10000 → 0.15"
}
```

**Response (Error):**

```json
{
  "status": "error",
  "message": "Error message here"
}
```

**Status Code:** `200 OK`

---

### 8.9 Statistics Reset Endpoint

#### POST /reset_stats

**Purpose:** Reset trading statistics (testing only)

**URL:** `http://your-server:80/reset_stats`

**Method:** `POST`

**Response (Success):**

```json
{
  "status": "success",
  "message": "Stats reset successfully"
}
```

**Response (Error):**

```json
{
  "status": "error",
  "message": "Error message here"
}
```

**Status Code:** `200 OK`

---

### 8.10 Telegram Commands List

**Complete list of 72+ Telegram commands:**

#### Trading Control (6 commands)

- `/start` - Start bot and show main menu
- `/pause` - Pause all trading
- `/resume` - Resume trading
- `/status` - Bot status and statistics
- `/trades` - List open trades
- `/signal_status` - Current signal status
- `/simulation_mode [on/off]` - Toggle simulation mode

#### Performance & Analytics (7 commands)

- `/performance` - Performance overview
- `/stats` - Trading statistics
- `/performance_report` - Detailed performance report
- `/pair_report` - Symbol-wise performance
- `/strategy_report` - Strategy-wise performance
- `/chains` - Re-entry and profit chains status

#### Strategy Control (7 commands)

- `/logic_status` - Logic enable/disable status
- `/logic1_on` - Enable LOGIC1
- `/logic1_off` - Disable LOGIC1
- `/logic2_on` - Enable LOGIC2
- `/logic2_off` - Disable LOGIC2
- `/logic3_on` - Enable LOGIC3
- `/logic3_off` - Disable LOGIC3

#### Re-entry System (12 commands)

- `/tp_system [on/off/status]` - TP continuation system
- `/sl_hunt [on/off/status]` - SL hunt re-entry
- `/exit_continuation [on/off/status]` - Exit continuation
- `/tp_report` - TP re-entry report
- `/reentry_config` - Re-entry configuration
- `/set_monitor_interval [value]` - Price monitor interval
- `/set_sl_offset [value]` - SL hunt offset
- `/set_cooldown [value]` - SL hunt cooldown
- `/set_recovery_time [value]` - Recovery window
- `/set_max_levels [value]` - Max re-entry levels
- `/set_sl_reduction [value]` - SL reduction per level
- `/reset_reentry_config` - Reset to defaults

#### Trend Management (5 commands)

- `/show_trends` - Show all trends
- `/trend_matrix` - Trend matrix view
- `/set_trend [symbol] [timeframe] [trend]` - Set manual trend
- `/set_auto [symbol] [timeframe]` - Set trend to AUTO
- `/trend_mode [symbol] [timeframe]` - Check trend mode

#### Risk & Lot Management (8 commands)

- `/view_risk_caps` - View loss caps
- `/set_daily_cap [amount]` - Set daily loss cap
- `/set_lifetime_cap [amount]` - Set lifetime loss cap
- `/set_risk_tier [balance] [daily] [lifetime]` - Set risk tier
- `/clear_loss_data` - Clear lifetime loss
- `/clear_daily_loss` - Clear daily loss
- `/lot_size_status` - Lot size status
- `/set_lot_size [tier] [lot_size]` - Set lot size

#### SL System Control (8 commands)

- `/sl_status` - SL system status
- `/sl_system_change [system]` - Change SL system
- `/sl_system_on [system]` - Enable SL system
- `/complete_sl_system_off` - Disable all SL systems
- `/view_sl_config` - View SL configuration
- `/set_symbol_sl [symbol] [percent]` - Set symbol SL reduction
- `/reset_symbol_sl [symbol]` - Reset symbol SL
- `/reset_all_sl` - Reset all symbol SL

#### Dual Orders (2 commands)

- `/dual_order_status` - Dual order system status
- `/toggle_dual_orders` - Enable/disable dual orders

#### Profit Booking (16 commands)

- `/profit_status` - Profit booking status
- `/profit_stats` - Profit booking statistics
- `/toggle_profit_booking` - Enable/disable profit booking
- `/set_profit_targets [targets]` - Set profit targets
- `/profit_chains` - List active profit chains
- `/stop_profit_chain [chain_id]` - Stop specific chain
- `/stop_all_profit_chains` - Stop all chains
- `/set_chain_multipliers [multipliers]` - Set order multipliers
- `/profit_config` - Profit booking configuration
- `/profit_sl_status` - Profit SL system status
- `/profit_sl_mode [SL-1.1/SL-2.1]` - Change profit SL mode
- `/enable_profit_sl` - Enable profit SL
- `/disable_profit_sl` - Disable profit SL
- `/set_profit_sl [logic] [amount]` - Set profit SL amount
- `/reset_profit_sl` - Reset profit SL

**Note:** Use `/start` in Telegram to see interactive menu with all commands organized by category.

---

### 8.11 Response Formats

**See:** `docs/RESPONSE_FORMATS.md` for complete response format documentation.

**Summary:**

- All endpoints return JSON
- Success responses: `{"status": "success", ...}`
- Error responses: `{"status": "error", "message": "..."}`
- Status codes: 200 (success), 400 (error), 404 (not found)

---

**Documentation Complete**

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
- Historical analysis

**Estimated Effort:** 3-4 days

---

#### 4. Multi-Exchange Support

**Enhancement:**
- Support for multiple brokers
- Exchange-agnostic trading
- Unified interface

**Benefits:**
- Diversify across brokers
- Compare execution quality
- Reduce broker dependency

**Complexity:** Very High
**Estimated Effort:** 1-2 months

---

#### 5. API Rate Limiting

**Enhancement:**
- Rate limiting for webhook endpoint
- IP whitelisting
- Request authentication
- DDoS protection

**Benefits:**
- Security improvement
- Prevent abuse
- Better resource management

**Estimated Effort:** 2-3 days

---

#### 6. Configuration Validation

**Enhancement:**
- Validate configuration on startup
- Schema validation
- Default value suggestions
- Configuration wizard

**Benefits:**
- Prevent configuration errors
- Easier setup
- Better error messages

**Estimated Effort:** 3-4 days

---

**Documentation Complete**

**Last Updated:** 2025-01-18  
**Version:** 2.0  
**Status:** Production Ready
