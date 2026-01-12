# 08 - API Integration & External Systems

## 🔌 External System Integration

---

## 1. TradingView Integration

### Webhook Endpoint
**URL**: `http://your-server:80/webhook`  
**Method**: POST  
**Content-Type**: application/json

### Alert Format
```json
{
  "type": "entry",
  "symbol": "EURUSD",
  "signal": "buy",
  "tf": "1h",
  "price": 1.10000,
  "strategy": "ZepixPremium"
}
```

### Alert Types

#### 1. Entry Alert
```json
{
  "type": "entry",
  "symbol": "EURUSD",
  "signal": "buy",      // or "sell"
  "tf": "1h",           // 15m, 1h, 1d
  "price": 1.10000,
  "strategy": "ZepixPremium"
}
```
**Purpose**: Trigger new trade entry

---

#### 2. Exit Alert
```json
{
  "type": "exit",
  "symbol": "EURUSD",
  "tf": "1h",
  "price": 1.11000,
  "reason": "exit_appeared"
}
```
**Purpose**: Close existing positions

---

#### 3. Trend Alert
```json
{
  "type": "trend",
  "symbol": "EURUSD",
  "tf": "1h",
  "trend": "bullish",   // or "bearish", "neutral"
  "price": 1.10500
}
```
**Purpose**: Update trend direction for alignment checks

---

#### 4. Bias Alert
```json
{
  "type": "bias",
  "symbol": "EURUSD",
  "tf": "1h",
  "bias": "bullish",
  "price": 1.10500
}
```
**Purpose**: Market bias update (similar to trend)

---

#### 5. Reversal Alert
```json
{
  "type": "reversal",
  "symbol": "EURUSD",
  "direction": "bearish",
  "tf": "1h",
  "price": 1.09500
}
```
**Purpose**: Trigger Reverse Shield protection

---

### TradingView Alert Template

**Pine Script Placeholder Values**:
```
{
  "type": "entry",
  "symbol": "{{ticker}}",
  "signal": "{{strategy.order.action}}",
  "tf": "{{interval}}",
  "price": {{close}},
  "strategy": "{{strategy.order.id}}"
}
```

### Alert Processing Flow
```
TradingView Alert
    ↓
POST /webhook
    ↓
FastAPI Endpoint receives JSON
    ↓
AlertProcessor.process_alert()
    ↓
Validate JSON format ✓
    ↓
Extract fields
    ↓
Route by type:
    - entry → TradingEngine.handle_entry()
    - exit → TradingEngine.handle_exit()
    - trend → TrendManager.update_trend()
    - reversal → ReverseShield.check_positions()
```

---

## 2. MetaTrader 5 Integration

### MT5 Python API
**Library**: `MetaTrader5==5.0.45`

### Initialization
```python
import MetaTrader5 as mt5

def initialize_mt5():
    """Connect to MT5 terminal"""
    
    # Initialize
    if not mt5.initialize():
        print(f"MT5 initialize() failed, error: {mt5.last_error()}")
        return False
    
    # Login
    login = int(os.getenv('MT5_LOGIN'))
    password = os.getenv('MT5_PASSWORD')
    server = os.getenv('MT5_SERVER')
    
    if not mt5.login(login, password, server):
        print(f"MT5 login failed, error: {mt5.last_error()}")
        return False
    
    print("MT5 connected successfully")
    return True
```

### Order Placement
```python
def place_order(symbol, order_type, lots, entry, sl, tp, comment=""):
    """Place order in MT5"""
    
    # Prepare request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lots,
        "type": mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL,
        "price": entry,
        "sl": sl,
        "tp": tp,
        "deviation": 10,  # Max price slippage
        "magic": 234000,  # Bot identifier
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Send order
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed, error: {result.retcode}")
        return None
    
    print(f"Order placed: {result.order}")
    return result.order
```

### Position Query
```python
def get_open_positions(symbol=None):
    """Get open positions"""
    
    if symbol:
        positions = mt5.positions_get(symbol=symbol)
    else:
        positions = mt5.positions_get()
    
    if positions is None:
        return []
    
    return [
        {
            'ticket': p.ticket,
            'symbol': p.symbol,
            'type': 'buy' if p.type == 0 else 'sell',
            'volume': p.volume,
            'price_open': p.price_open,
            'sl': p.sl,
            'tp': p.tp,
            'profit': p.profit,
            'comment': p.comment
        }
        for p in positions
    ]
```

### Position Closure
```python
def close_position(position_id):
    """Close a position"""
    
    # Get position
    position = mt5.positions_get(ticket=position_id)
    
    if not position:
        return False
    
    position = position[0]
    
    # Prepare close request
    close_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": close_type,
        "position": position_id,
        "price": mt5.symbol_info_tick(position.symbol).bid if close_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask,
        "deviation": 10,
        "magic": 234000,
        "comment": "Bot close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    return result.retcode == mt5.TRADE_RETCODE_DONE
```

### Account Information
```python
def get_account_info():
    """Get account information"""
    
    account = mt5.account_info()
    
    if account is None:
        return None
    
    return {
        'login': account.login,
        'server': account.server,
        'balance': account.balance,
        'equity': account.equity,
        'margin': account.margin,
        'margin_free': account.margin_free,
        'profit': account.profit
    }
```

### Symbol Information
```python
def get_symbol_info(symbol):
    """Get symbol trading information"""
    
    info = mt5.symbol_info(symbol)
    
    if info is None:
        return None
    
    return {
        'name': info.name,
        'digits': info.digits,
        'point': info.point,
        'trade_contract_size': info.trade_contract_size,
        'volume_min': info.volume_min,
        'volume_max': info.volume_max,
        'volume_step': info.volume_step,
        'spread': info.spread
    }
```

### Price Data
```python
def get_current_price(symbol):
    """Get current bid/ask"""
    
    tick = mt5.symbol_info_tick(symbol)
    
    if tick is None:
        return None
    
    return {
        'bid': tick.bid,
        'ask': tick.ask,
        'last': tick.last,
        'time': tick.time
    }
```

---

## 3. Telegram Bot API

### Bot Initialization
```python
from telegram import Bot
from telegram.ext import Updater

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = Bot(token=TOKEN)
```

### Send Message
```python
def send_message(text, reply_markup=None):
    """Send message to user"""
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    response = requests.post(url, data=payload)
    return response.json()
```

### Send File
```python
def send_document(file_path, caption=""):
    """Send file to user"""
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    
    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {
            'chat_id': CHAT_ID,
            'caption': caption
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json()
```

### Polling (Receive Updates)
```python
def start_polling():
    """Start receiving updates"""
    
    offset = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {
                'offset': offset,
                'timeout': 30
            }
            
            response = requests.get(url, params=params)
            updates = response.json()
            
            if updates['ok']:
                for update in updates['result']:
                    process_update(update)
                    offset = update['update_id'] + 1
        
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)
```

---

## 4. Symbol Mapping

### TradingView → MT5
```python
SYMBOL_MAP = {
    # Major pairs
    'EURUSD': 'EURUSD.a',
    'GBPUSD': 'GBPUSD.a',
    'USDJPY': 'USDJPY.a',
    'USDCAD': 'USDCAD.a',
    'AUDUSD': 'AUDUSD.a',
    'NZDUSD': 'NZDUSD.a',
    
    # Cross pairs
    'EURJPY': 'EURJPY.a',
    'GBPJPY': 'GBPJPY.a',
    'AUDJPY': 'AUDJPY.a',
    
    # Gold
    'XAUUSD': 'XAUUSD.a'
}

def map_symbol(tradingview_symbol):
    """Convert TradingView symbol to MT5 symbol"""
    return SYMBOL_MAP.get(tradingview_symbol, tradingview_symbol)
```

---

## 5. Error Handling

### MT5 Errors
```python
MT5_ERROR_CODES = {
    10004: "Requote",
    10006: "Request rejected",
    10007: "Request canceled",
    10008: "Order placed",
    10009: "Request completed",
    10010: "Only part done",
    10011: "Request processing error",
    10012: "Request canceled by timeout",
    10013: "Invalid request",
    10014: "Invalid volume",
    10015: "Invalid price",
    10016: "Invalid stops",
    10017: "Trade disabled",
    10018: "Market closed",
    10019: "No money",
    10020: "Prices changed",
    10021: "No quotes",
    10022: "Invalid expiration",
    10023: "Order state changed",
    10024: "Too many requests",
    10025: "No changes in request",
    10026: "Autotrading disabled",
    10027: "Autotrading disabled by client",
    10028: "Request locked",
    10029: "Order or position frozen",
    10030: "Invalid fill",
    10031: "Connection problem",
    10032: "Only close allowed",
    10033: "Not enough orders",
}

def handle_mt5_error(retcode):
    """Handle MT5 error code"""
    
    error_message = MT5_ERROR_CODES.get(retcode, f"Unknown error: {retcode}")
    
    logger.error(f"MT5 Error {retcode}: {error_message}")
    
    # Specific handling
    if retcode == 10019:  # No money
        telegram_bot.send_alert("⚠️ Insufficient margin!")
        pause_trading()
    
    elif retcode == 10018:  # Market closed
        logger.warning("Market closed, will retry when open")
    
    return error_message
```

---

## 6. Rate Limiting

### TradingView Webhooks
- No built-in rate limiting
- Bot processes all incoming alerts

### Telegram API
- **Message limit**: 30 messages/second
- **Implementation**: Queue with rate limiter

```python
import time
from collections import deque

class TelegramRateLimiter:
    def __init__(self, max_per_second=20):
        self.max_per_second = max_per_second
        self.timestamps = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        
        now = time.time()
        
        # Remove timestamps older than 1 second
        while self.timestamps and now - self.timestamps[0] > 1:
            self.timestamps.popleft()
        
        # Check if limit reached
        if len(self.timestamps) >= self.max_per_second:
            sleep_time = 1 - (now - self.timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.timestamps.append(now)
```

---

## Integration Files

| File | Purpose |
|------|---------|
| `src/clients/mt5_client.py` | MT5 integration |
| `src/clients/telegram_bot.py` | Telegram integration |
| `src/processors/alert_processor.py` | TradingView alert processing |
| `src/main.py` | Webhook endpoint (`/webhook`) |
