# Zepix Trading Bot v2.0 - API Integration Guide

## Overview

This document details all API integrations used by the Zepix Trading Bot, including the FastAPI webhook server, MetaTrader 5 API, Telegram Bot API, and internal APIs.

## FastAPI Webhook Server

### Server Configuration

The bot runs a FastAPI server to receive TradingView webhook alerts.

**Default Configuration:**
```python
app = FastAPI(
    title="Zepix Trading Bot",
    version="2.0",
    description="Automated trading bot for MT5"
)

# Run with uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### API Endpoints

#### POST /webhook

Receives trading alerts from TradingView.

**Request:**
```http
POST /webhook HTTP/1.1
Host: your-server:8000
Content-Type: application/json

{
    "type": "entry",
    "symbol": "XAUUSD",
    "signal": "buy",
    "tf": "15m",
    "price": 2650.50,
    "strategy": "LOGIC2"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "Alert processed",
    "trade_id": "12345678",
    "details": {
        "symbol": "XAUUSD",
        "direction": "BUY",
        "lot_size": 0.10,
        "entry_price": 2650.50,
        "sl_price": 2640.50,
        "tp_price": 2665.50
    }
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Invalid alert format",
    "details": "Missing required field: symbol"
}
```

**Response (Skipped):**
```json
{
    "status": "skipped",
    "message": "Trend not aligned",
    "details": {
        "required": "1H BULLISH + 15M BULLISH",
        "current": "1H BEARISH + 15M BULLISH"
    }
}
```

#### GET /health

Health check endpoint for monitoring.

**Request:**
```http
GET /health HTTP/1.1
Host: your-server:8000
```

**Response:**
```json
{
    "status": "healthy",
    "mt5_connected": true,
    "telegram_active": true,
    "uptime": "2h 30m 15s",
    "version": "2.0",
    "last_alert": "2025-01-15T10:30:00Z"
}
```

#### GET /stats

Trading statistics endpoint.

**Request:**
```http
GET /stats HTTP/1.1
Host: your-server:8000
```

**Response:**
```json
{
    "total_trades": 150,
    "winning_trades": 95,
    "losing_trades": 55,
    "win_rate": 63.33,
    "total_pnl": 1250.50,
    "daily_pnl": 85.00,
    "daily_loss": 15.00,
    "lifetime_loss": 250.00,
    "active_chains": 3,
    "active_profit_chains": 2
}
```

#### GET /trends

Current trend states endpoint.

**Request:**
```http
GET /trends HTTP/1.1
Host: your-server:8000
```

**Response:**
```json
{
    "XAUUSD": {
        "5m": {"trend": "BULLISH", "mode": "AUTO"},
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BEARISH", "mode": "MANUAL"},
        "1d": {"trend": "BULLISH", "mode": "AUTO"}
    },
    "EURUSD": {
        "5m": {"trend": "NEUTRAL", "mode": "AUTO"},
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BULLISH", "mode": "AUTO"},
        "1d": {"trend": "BEARISH", "mode": "AUTO"}
    }
}
```

### Alert Format Specification

#### Entry Alert

```json
{
    "type": "entry",
    "symbol": "XAUUSD",
    "signal": "buy",
    "tf": "15m",
    "price": 2650.50,
    "strategy": "LOGIC2"
}
```

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| type | string | Yes | "entry" | Alert type |
| symbol | string | Yes | See supported symbols | Trading symbol |
| signal | string | Yes | "buy", "sell" | Trade direction |
| tf | string | Yes | "5m", "15m", "1h", "1d" | Entry timeframe |
| price | number | No | Current price | Entry price (optional) |
| strategy | string | No | "LOGIC1", "LOGIC2", "LOGIC3" | Logic override |

#### Trend Alert

```json
{
    "type": "trend",
    "symbol": "XAUUSD",
    "signal": "bull",
    "tf": "1h"
}
```

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| type | string | Yes | "trend" | Alert type |
| symbol | string | Yes | See supported symbols | Trading symbol |
| signal | string | Yes | "bull", "bear" | Trend direction |
| tf | string | Yes | "5m", "15m", "1h", "1d" | Timeframe |

#### Bias Alert

```json
{
    "type": "bias",
    "symbol": "XAUUSD",
    "signal": "bull",
    "tf": "1d"
}
```

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| type | string | Yes | "bias" | Alert type |
| symbol | string | Yes | See supported symbols | Trading symbol |
| signal | string | Yes | "bull", "bear" | Bias direction |
| tf | string | Yes | "1d" | Typically daily |

#### Exit Alert

```json
{
    "type": "exit",
    "symbol": "XAUUSD",
    "signal": "bear",
    "tf": "15m"
}
```

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| type | string | Yes | "exit" | Alert type |
| symbol | string | Yes | See supported symbols | Trading symbol |
| signal | string | Yes | "bull", "bear" | Exit direction |
| tf | string | Yes | "5m", "15m", "1h" | Timeframe |

#### Reversal Alert

```json
{
    "type": "reversal",
    "symbol": "XAUUSD",
    "signal": "reversal_bull",
    "tf": "15m"
}
```

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| type | string | Yes | "reversal" | Alert type |
| symbol | string | Yes | See supported symbols | Trading symbol |
| signal | string | Yes | "reversal_bull", "reversal_bear" | Reversal direction |
| tf | string | Yes | "5m", "15m", "1h" | Timeframe |

### Supported Symbols

```
XAUUSD, EURUSD, GBPUSD, USDJPY, USDCAD, 
AUDUSD, NZDUSD, EURJPY, GBPJPY, AUDJPY
```

## MetaTrader 5 API Integration

### Connection Management

```python
import MetaTrader5 as mt5

class MT5Client:
    def __init__(self, config):
        self.login = config['mt5_login']
        self.password = config['mt5_password']
        self.server = config['mt5_server']
        self.connected = False
    
    def connect(self):
        if not mt5.initialize():
            raise ConnectionError("MT5 initialization failed")
        
        if not mt5.login(
            login=int(self.login),
            password=self.password,
            server=self.server
        ):
            raise ConnectionError(f"MT5 login failed: {mt5.last_error()}")
        
        self.connected = True
        return True
    
    def disconnect(self):
        mt5.shutdown()
        self.connected = False
```

### Symbol Mapping

```python
SYMBOL_MAPPING = {
    "XAUUSD": "GOLD",      # XM Broker specific
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

def get_broker_symbol(self, tradingview_symbol):
    return self.symbol_mapping.get(
        tradingview_symbol, 
        tradingview_symbol
    )
```

### Order Placement

```python
def place_order(self, symbol, order_type, lot_size, sl, tp, comment=""):
    broker_symbol = self.get_broker_symbol(symbol)
    
    # Get symbol info
    symbol_info = mt5.symbol_info(broker_symbol)
    if symbol_info is None:
        raise ValueError(f"Symbol {broker_symbol} not found")
    
    # Get current price
    tick = mt5.symbol_info_tick(broker_symbol)
    if tick is None:
        raise ValueError(f"Cannot get tick for {broker_symbol}")
    
    # Determine price based on order type
    if order_type == "BUY":
        price = tick.ask
        mt5_type = mt5.ORDER_TYPE_BUY
    else:
        price = tick.bid
        mt5_type = mt5.ORDER_TYPE_SELL
    
    # Create order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": broker_symbol,
        "volume": lot_size,
        "type": mt5_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Send order
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise OrderError(f"Order failed: {result.comment}")
    
    return result.order
```

### Position Management

```python
def get_open_positions(self, symbol=None):
    if symbol:
        broker_symbol = self.get_broker_symbol(symbol)
        positions = mt5.positions_get(symbol=broker_symbol)
    else:
        positions = mt5.positions_get()
    
    return positions if positions else []

def close_position(self, position_id):
    position = mt5.positions_get(ticket=position_id)
    if not position:
        raise ValueError(f"Position {position_id} not found")
    
    position = position[0]
    
    # Determine close type
    if position.type == mt5.ORDER_TYPE_BUY:
        close_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(position.symbol).bid
    else:
        close_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).ask
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": close_type,
        "position": position_id,
        "price": price,
        "deviation": 20,
        "magic": 123456,
        "comment": "Close position",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    return result.retcode == mt5.TRADE_RETCODE_DONE

def modify_position(self, position_id, sl=None, tp=None):
    position = mt5.positions_get(ticket=position_id)
    if not position:
        raise ValueError(f"Position {position_id} not found")
    
    position = position[0]
    
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": position.symbol,
        "position": position_id,
        "sl": sl if sl else position.sl,
        "tp": tp if tp else position.tp,
    }
    
    result = mt5.order_send(request)
    return result.retcode == mt5.TRADE_RETCODE_DONE
```

### Account Information

```python
def get_account_info(self):
    account = mt5.account_info()
    if account is None:
        raise ConnectionError("Cannot get account info")
    
    return {
        "balance": account.balance,
        "equity": account.equity,
        "margin": account.margin,
        "free_margin": account.margin_free,
        "profit": account.profit,
        "leverage": account.leverage
    }

def get_account_balance(self):
    account = mt5.account_info()
    return account.balance if account else 0
```

### Symbol Information

```python
def get_symbol_info(self, symbol):
    broker_symbol = self.get_broker_symbol(symbol)
    info = mt5.symbol_info(broker_symbol)
    
    if info is None:
        return None
    
    return {
        "symbol": info.name,
        "bid": info.bid,
        "ask": info.ask,
        "spread": info.spread,
        "digits": info.digits,
        "point": info.point,
        "volume_min": info.volume_min,
        "volume_max": info.volume_max,
        "volume_step": info.volume_step,
        "trade_stops_level": info.trade_stops_level
    }

def get_current_price(self, symbol):
    broker_symbol = self.get_broker_symbol(symbol)
    tick = mt5.symbol_info_tick(broker_symbol)
    
    if tick is None:
        return None
    
    return {
        "bid": tick.bid,
        "ask": tick.ask,
        "last": tick.last,
        "time": tick.time
    }
```

## Telegram Bot API Integration

### Bot Initialization

```python
import requests

class TelegramBot:
    def __init__(self, config):
        self.token = config['telegram_token']
        self.chat_id = config['telegram_chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, text, parse_mode="HTML", reply_markup=None):
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        
        response = requests.post(url, json=payload)
        return response.json()
```

### Message Formatting

```python
def format_trade_notification(self, trade):
    emoji = "🟢" if trade.direction == "BUY" else "🔴"
    
    message = f"""
{emoji} <b>NEW TRADE OPENED</b>

<b>Symbol:</b> {trade.symbol}
<b>Direction:</b> {trade.direction}
<b>Lot Size:</b> {trade.lot_size}
<b>Entry:</b> {trade.entry_price}
<b>SL:</b> {trade.sl_price}
<b>TP:</b> {trade.tp_price}
<b>Logic:</b> {trade.logic_type}
<b>Order Type:</b> {trade.order_type}

<i>Trade ID: {trade.trade_id}</i>
"""
    return message

def format_close_notification(self, trade, pnl):
    emoji = "✅" if pnl > 0 else "❌"
    
    message = f"""
{emoji} <b>TRADE CLOSED</b>

<b>Symbol:</b> {trade.symbol}
<b>Direction:</b> {trade.direction}
<b>Entry:</b> {trade.entry_price}
<b>Exit:</b> {trade.exit_price}
<b>PnL:</b> ${pnl:.2f}

<i>Trade ID: {trade.trade_id}</i>
"""
    return message
```

### Inline Keyboard

```python
def create_inline_keyboard(self, buttons):
    """
    buttons format: [[{"text": "Button 1", "callback_data": "action1"}]]
    """
    return {
        "inline_keyboard": buttons
    }

def create_main_menu(self):
    buttons = [
        [
            {"text": "📊 Dashboard", "callback_data": "dashboard"},
            {"text": "⏸ Pause", "callback_data": "pause"}
        ],
        [
            {"text": "📈 Trades", "callback_data": "trades"},
            {"text": "📉 Performance", "callback_data": "performance"}
        ],
        [
            {"text": "⚙️ Settings", "callback_data": "settings"},
            {"text": "❓ Help", "callback_data": "help"}
        ]
    ]
    return self.create_inline_keyboard(buttons)
```

### Reply Keyboard

```python
def create_reply_keyboard(self, buttons, resize=True):
    """
    buttons format: [["Button 1", "Button 2"], ["Button 3"]]
    """
    return {
        "keyboard": buttons,
        "resize_keyboard": resize,
        "one_time_keyboard": False
    }

def create_persistent_keyboard(self):
    buttons = [
        ["📊 Dashboard", "⏸ Pause/Resume", "📈 Active Trades"],
        ["💰 Risk", "🔄 Re-entry", "🛑 SL System"],
        ["📉 Trends", "💵 Profit", "❓ Help"],
        ["🚨 PANIC CLOSE"]
    ]
    return self.create_reply_keyboard(buttons)
```

### Polling for Updates

```python
def start_polling(self):
    self.running = True
    offset = 0
    
    while self.running:
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                "offset": offset,
                "timeout": 30
            }
            
            response = requests.get(url, params=params)
            updates = response.json().get("result", [])
            
            for update in updates:
                offset = update["update_id"] + 1
                self._handle_update(update)
                
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)

def _handle_update(self, update):
    if "message" in update:
        self._handle_message(update["message"])
    elif "callback_query" in update:
        self._handle_callback(update["callback_query"])
```

### Callback Query Handling

```python
def answer_callback_query(self, callback_query_id, text=None):
    url = f"{self.base_url}/answerCallbackQuery"
    
    payload = {
        "callback_query_id": callback_query_id
    }
    
    if text:
        payload["text"] = text
    
    return requests.post(url, json=payload)

def edit_message(self, message_id, text, reply_markup=None):
    url = f"{self.base_url}/editMessageText"
    
    payload = {
        "chat_id": self.chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    return requests.post(url, json=payload)
```

## Internal API Reference

### Trading Engine API

```python
class TradingEngine:
    async def process_alert(self, alert_data: dict) -> dict:
        """Process incoming alert and execute trades if valid."""
        pass
    
    async def execute_trades(self, alert: Alert) -> dict:
        """Execute dual orders based on validated alert."""
        pass
    
    async def close_trade(self, trade_id: int) -> bool:
        """Close a specific trade by ID."""
        pass
    
    async def close_all_trades(self, symbol: str = None) -> int:
        """Close all trades, optionally filtered by symbol."""
        pass
    
    def get_open_trades(self) -> List[Trade]:
        """Get all currently open trades."""
        pass
    
    def get_trade_history(self, days: int = 7) -> List[Trade]:
        """Get trade history for specified days."""
        pass
```

### Risk Manager API

```python
class RiskManager:
    def can_trade(self) -> Tuple[bool, str]:
        """Check if trading is allowed based on risk limits."""
        pass
    
    def get_fixed_lot_size(self, balance: float) -> float:
        """Get lot size for account balance tier."""
        pass
    
    def validate_dual_orders(self, lot_size: float, symbol: str) -> Tuple[bool, float]:
        """Validate risk for dual order placement."""
        pass
    
    def record_trade_result(self, pnl: float) -> None:
        """Record trade result and update statistics."""
        pass
    
    def get_risk_status(self) -> dict:
        """Get current risk status and limits."""
        pass
```

### Profit Booking Manager API

```python
class ProfitBookingManager:
    def create_profit_chain(self, trade: Trade) -> ProfitBookingChain:
        """Create new profit booking chain for trade."""
        pass
    
    def check_profit_targets(self, chain: ProfitBookingChain) -> List[Trade]:
        """Check and book profits for orders at target."""
        pass
    
    def progress_chain(self, chain: ProfitBookingChain) -> bool:
        """Progress chain to next level."""
        pass
    
    def get_active_chains(self) -> List[ProfitBookingChain]:
        """Get all active profit booking chains."""
        pass
    
    def stop_chain(self, chain_id: str) -> bool:
        """Stop and close a profit booking chain."""
        pass
```

### Re-entry Manager API

```python
class ReEntryManager:
    def create_chain(self, trade: Trade) -> ReEntryChain:
        """Create new re-entry chain for trade."""
        pass
    
    def record_sl_hit(self, trade: Trade) -> None:
        """Record SL hit and start recovery monitoring."""
        pass
    
    def record_tp_hit(self, trade: Trade) -> None:
        """Record TP hit and check for continuation."""
        pass
    
    def check_recovery_eligibility(self, chain: ReEntryChain, price: float) -> bool:
        """Check if price has recovered enough for re-entry."""
        pass
    
    def get_active_chains(self) -> List[ReEntryChain]:
        """Get all active re-entry chains."""
        pass
```

### Trend Manager API

```python
class TimeframeTrendManager:
    def update_trend(self, symbol: str, timeframe: str, trend: str) -> None:
        """Update trend for symbol/timeframe."""
        pass
    
    def get_trend(self, symbol: str, timeframe: str) -> str:
        """Get current trend for symbol/timeframe."""
        pass
    
    def check_alignment(self, symbol: str, direction: str, logic: str) -> bool:
        """Check if trends align for entry."""
        pass
    
    def set_manual_mode(self, symbol: str, timeframe: str) -> None:
        """Lock trend to manual mode."""
        pass
    
    def set_auto_mode(self, symbol: str, timeframe: str) -> None:
        """Set trend to auto mode."""
        pass
    
    def get_all_trends(self) -> dict:
        """Get all current trends."""
        pass
```

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Authentication failed |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Error | Server error |

### MT5 Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 10004 | Requote | Price changed, retry |
| 10006 | Rejected | Request rejected |
| 10014 | Invalid Volume | Lot size invalid |
| 10015 | Invalid Price | Price invalid |
| 10016 | Invalid Stops | SL/TP invalid |
| 10019 | No Money | Insufficient margin |

### Internal Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| E001 | Validation Error | Invalid alert format |
| E002 | Duplicate Alert | Alert already processed |
| E003 | Trend Mismatch | Trends not aligned |
| E004 | Risk Limit | Risk cap reached |
| E005 | Logic Disabled | Trading logic disabled |
| E006 | Connection Error | MT5/Telegram disconnected |

## Rate Limits

### Telegram API

| Endpoint | Limit |
|----------|-------|
| sendMessage | 30/second to same chat |
| getUpdates | 1/second |
| Overall | 30 requests/second |

### MT5 API

| Operation | Recommended Limit |
|-----------|-------------------|
| Order placement | 1/second |
| Position queries | 10/second |
| Symbol info | 10/second |

## Security Considerations

### Authentication

- Telegram bot token stored in environment variable
- MT5 credentials stored in environment variable
- No credentials in code or config files

### Input Validation

- All webhook data validated before processing
- Symbol whitelist enforced
- Timeframe validation
- Signal value validation

### Rate Limiting

- Duplicate alert detection (5-minute window)
- Telegram message batching
- MT5 request throttling

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) - Configuration guide
- [TELEGRAM_COMMAND_STRUCTURE.md](TELEGRAM_COMMAND_STRUCTURE.md) - Telegram commands
