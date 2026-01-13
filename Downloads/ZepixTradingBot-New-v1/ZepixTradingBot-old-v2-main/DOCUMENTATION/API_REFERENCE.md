# API Reference

## Overview

This document provides complete API reference for all services in the V5 Hybrid Plugin Architecture. The system uses a unified ServiceAPI interface that provides access to all core services.

## ServiceAPI Interface

The `IServiceAPI` interface provides access to all services:

```python
from src.api.contracts import IServiceAPI

class ServiceAPI(IServiceAPI):
    @property
    def orders(self) -> IOrderExecutionService:
        """Get order execution service."""
        
    @property
    def risk(self) -> IRiskManagementService:
        """Get risk management service."""
        
    @property
    def trend(self) -> ITrendManagementService:
        """Get trend management service."""
        
    @property
    def profit(self) -> IProfitBookingService:
        """Get profit booking service."""
        
    @property
    def market(self) -> IMarketDataService:
        """Get market data service."""
```

## Order Execution Service

**Location:** `src/services/order_execution.py`
**Interface:** `IOrderExecutionService`

### V3-Specific Methods

#### place_dual_orders_v3

Place V3 hybrid SL dual order system (Order A + Order B).

```python
async def place_dual_orders_v3(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size_total: float,
    order_a_sl: float,
    order_a_tp: float,
    order_b_sl: float,
    order_b_tp: float,
    logic_route: str
) -> Tuple[int, int]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier (must be 'combined_v3') |
| symbol | str | Trading symbol (e.g., 'XAUUSD') |
| direction | str | Trade direction ('BUY' or 'SELL') |
| lot_size_total | float | Total lot size (will be split 50/50) |
| order_a_sl | float | Smart SL price for Order A |
| order_a_tp | float | TP2 (extended target) for Order A |
| order_b_sl | float | Fixed $10 SL price for Order B |
| order_b_tp | float | TP1 (closer target) for Order B |
| logic_route | str | Logic route ('LOGIC1', 'LOGIC2', 'LOGIC3') |

**Returns:** `Tuple[int, int]` - (order_a_ticket, order_b_ticket)

**Example:**
```python
ticket_a, ticket_b = await service_api.orders.place_dual_orders_v3(
    plugin_id="combined_v3",
    symbol="XAUUSD",
    direction="BUY",
    lot_size_total=0.20,
    order_a_sl=2025.00,
    order_a_tp=2045.00,
    order_b_sl=2028.00,  # Fixed $10 SL
    order_b_tp=2035.00,
    logic_route="LOGIC2"
)
```

### V6-Specific Methods

#### place_single_order_a

Place Order A ONLY (for 15M/1H V6 plugins).

```python
async def place_single_order_a(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,
    comment: str = "ORDER_A"
) -> int
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| symbol | str | Trading symbol |
| direction | str | Trade direction |
| lot_size | float | Lot size |
| sl_price | float | Stop loss price |
| tp_price | float | Take profit price |
| comment | str | Order comment |

**Returns:** `int` - MT5 ticket number

#### place_single_order_b

Place Order B ONLY (for 1M V6 plugin).

```python
async def place_single_order_b(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,
    comment: str = "ORDER_B"
) -> int
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| symbol | str | Trading symbol |
| direction | str | Trade direction |
| lot_size | float | Lot size (typically 0.5x for scalping) |
| sl_price | float | Stop loss price |
| tp_price | float | TP1 (quick exit target) |
| comment | str | Order comment |

**Returns:** `int` - MT5 ticket number

#### place_dual_orders_v6

Place DUAL orders for 5M V6 plugin.

```python
async def place_dual_orders_v6(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size_total: float,
    sl_price: float,
    tp1_price: float,
    tp2_price: float
) -> Tuple[int, int]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| symbol | str | Trading symbol |
| direction | str | Trade direction |
| lot_size_total | float | Total lot size |
| sl_price | float | Same SL for both orders |
| tp1_price | float | Order B target (closer) |
| tp2_price | float | Order A target (extended) |

**Returns:** `Tuple[int, int]` - (order_a_ticket, order_b_ticket)

### Universal Order Methods

#### modify_order

Modify existing order SL/TP.

```python
async def modify_order(
    plugin_id: str,
    order_id: int,
    new_sl: Optional[float] = None,
    new_tp: Optional[float] = None
) -> bool
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| order_id | int | MT5 order ticket |
| new_sl | float | New stop loss price (optional) |
| new_tp | float | New take profit price (optional) |

**Returns:** `bool` - True if modification successful

**Example:**
```python
success = await service_api.orders.modify_order(
    plugin_id="combined_v3",
    order_id=12345,
    new_sl=2028.00
)
```

#### close_position

Close entire position.

```python
async def close_position(
    plugin_id: str,
    order_id: int,
    reason: str = "Manual"
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| order_id | int | MT5 order ticket |
| reason | str | Close reason |

**Returns:** `Dict[str, Any]` with keys:
- `success`: bool
- `closed_volume`: float
- `profit_pips`: float
- `profit_dollars`: float

#### close_position_partial

Close partial position (for TP1/TP2/TP3).

```python
async def close_position_partial(
    plugin_id: str,
    order_id: int,
    percentage: float
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| order_id | int | MT5 order ticket |
| percentage | float | Percentage to close (25.0 = close 25%) |

**Returns:** `Dict[str, Any]` with keys:
- `closed_volume`: float
- `remaining_volume`: float
- `profit_pips`: float
- `profit_dollars`: float

#### get_open_orders

Get all open orders for this plugin.

```python
async def get_open_orders(
    plugin_id: str,
    symbol: Optional[str] = None
) -> List[Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| symbol | str | Optional symbol filter |

**Returns:** `List[Dict[str, Any]]` - List of order dictionaries

**Example:**
```python
orders = await service_api.orders.get_open_orders(
    plugin_id="combined_v3",
    symbol="XAUUSD"
)
for order in orders:
    print(f"Ticket: {order['ticket']}, P&L: {order['profit']}")
```

## Risk Management Service

**Location:** `src/services/risk_management.py`
**Interface:** `IRiskManagementService`

### calculate_lot_size

Calculate safe lot size based on risk.

```python
async def calculate_lot_size(
    plugin_id: str,
    symbol: str,
    risk_percentage: float,
    stop_loss_pips: float,
    account_balance: Optional[float] = None
) -> float
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| symbol | str | Trading symbol |
| risk_percentage | float | Risk percentage (e.g., 1.5) |
| stop_loss_pips | float | Stop loss in pips |
| account_balance | float | Account balance (auto-fetch if None) |

**Returns:** `float` - Calculated lot size

**Example:**
```python
lot_size = await service_api.risk.calculate_lot_size(
    plugin_id="combined_v3",
    symbol="XAUUSD",
    risk_percentage=1.5,
    stop_loss_pips=25
)
```

### check_daily_limit

Check if daily loss limit reached.

```python
async def check_daily_limit(
    plugin_id: str
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |

**Returns:** `Dict[str, Any]` with keys:
- `daily_loss`: float - Today's loss
- `daily_limit`: float - Daily limit
- `remaining`: float - Remaining allowance
- `can_trade`: bool - Whether trading is allowed

**Example:**
```python
status = await service_api.risk.check_daily_limit("combined_v3")
if not status["can_trade"]:
    logger.warning(f"Daily limit reached: {status['daily_loss']}")
```

### get_risk_tier

Get current risk tier for plugin.

```python
async def get_risk_tier(
    plugin_id: str
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |

**Returns:** `Dict[str, Any]` with keys:
- `tier`: str - Tier name
- `risk_percentage`: float - Max risk %
- `max_trades`: int - Max concurrent trades

## Trend Management Service

**Location:** `src/services/trend_monitor.py`
**Interface:** `ITrendManagementService`

### V3 Traditional Timeframe Methods

#### get_timeframe_trend

Get V3 4-pillar MTF trend for a specific timeframe.

```python
async def get_timeframe_trend(
    symbol: str,
    timeframe: str
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |
| timeframe | str | Timeframe ('15m', '1h', '4h', '1d' ONLY) |

**Returns:** `Dict[str, Any]` with keys:
- `timeframe`: str
- `direction`: str - 'BULLISH' or 'BEARISH'
- `value`: int - 1 or -1
- `last_updated`: str - ISO timestamp

#### get_mtf_trends

Get ALL 4-pillar trends at once.

```python
async def get_mtf_trends(
    symbol: str
) -> Dict[str, int]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |

**Returns:** `Dict[str, int]` with keys:
- `15m`: int - 1=bullish, -1=bearish
- `1h`: int
- `4h`: int
- `1d`: int

**Example:**
```python
trends = await service_api.trend.get_mtf_trends("XAUUSD")
# {'15m': 1, '1h': 1, '4h': -1, '1d': 1}
```

#### validate_v3_trend_alignment

Check if signal aligns with V3 4-pillar system.

```python
async def validate_v3_trend_alignment(
    symbol: str,
    direction: str,
    min_aligned: int = 3
) -> bool
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |
| direction | str | Trade direction ('BUY' or 'SELL') |
| min_aligned | int | Minimum pillars that must align (default: 3) |

**Returns:** `bool` - True if aligned

### V6 Trend Pulse Methods

#### update_trend_pulse

Update market_trends table with Trend Pulse alert data.

```python
async def update_trend_pulse(
    symbol: str,
    timeframe: str,
    bull_count: int,
    bear_count: int,
    market_state: str,
    changes: str
) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |
| timeframe | str | Timeframe |
| bull_count | int | Bullish count |
| bear_count | int | Bearish count |
| market_state | str | Market state string |
| changes | str | Which TFs changed |

#### get_market_state

Get current market state for symbol (V6).

```python
async def get_market_state(
    symbol: str
) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |

**Returns:** `str` - Market state:
- `TRENDING_BULLISH`
- `TRENDING_BEARISH`
- `SIDEWAYS`
- `VOLATILE`
- `UNKNOWN`

#### check_pulse_alignment

Check if signal aligns with Trend Pulse counts.

```python
async def check_pulse_alignment(
    symbol: str,
    direction: str
) -> bool
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |
| direction | str | Trade direction |

**Returns:** `bool` - True if aligned

**Logic:**
- For BUY: bull_count > bear_count
- For SELL: bear_count > bull_count

#### get_pulse_data

Get raw Trend Pulse counts.

```python
async def get_pulse_data(
    symbol: str,
    timeframe: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |
| timeframe | str | Optional specific timeframe |

**Returns:** `Dict[str, Any]` - timeframe -> {bull_count, bear_count}

## Profit Booking Service

**Location:** `src/services/profit_booking.py`
**Interface:** `IProfitBookingService`

### book_profit

Book partial profit (TP1, TP2, TP3).

```python
async def book_profit(
    plugin_id: str,
    order_id: int,
    percentage: float,
    reason: str = "TP1"
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| order_id | int | MT5 order ticket |
| percentage | float | Percentage to close (25.0, 50.0, 100.0) |
| reason | str | Booking reason |

**Returns:** `Dict[str, Any]` with keys:
- `closed_volume`: float
- `remaining_volume`: float
- `profit_pips`: float
- `profit_dollars`: float

**Example:**
```python
result = await service_api.profit.book_profit(
    plugin_id="combined_v3",
    order_id=12345,
    percentage=50.0,
    reason="TP1"
)
print(f"Booked ${result['profit_dollars']}")
```

### move_to_breakeven

Move SL to breakeven + buffer.

```python
async def move_to_breakeven(
    plugin_id: str,
    order_id: int,
    buffer_pips: float = 2.0
) -> bool
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| order_id | int | MT5 order ticket |
| buffer_pips | float | Buffer pips above breakeven |

**Returns:** `bool` - True if successful

### get_booking_history

Get profit booking history.

```python
async def get_booking_history(
    plugin_id: str,
    order_id: Optional[int] = None
) -> List[Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| plugin_id | str | Plugin identifier |
| order_id | int | Optional order filter |

**Returns:** `List[Dict[str, Any]]` - List of booking records

## Market Data Service

**Location:** `src/services/market_data.py`
**Interface:** `IMarketDataService`

### get_current_spread

Get current spread in pips.

```python
async def get_current_spread(
    symbol: str
) -> float
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |

**Returns:** `float` - Spread in pips

### get_current_price

Get current bid/ask prices.

```python
async def get_current_price(
    symbol: str
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |

**Returns:** `Dict[str, Any]` with keys:
- `bid`: float
- `ask`: float
- `spread_pips`: float

**Example:**
```python
price = await service_api.market.get_current_price("XAUUSD")
print(f"Bid: {price['bid']}, Ask: {price['ask']}")
```

### get_symbol_info

Get symbol information.

```python
async def get_symbol_info(
    symbol: str
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | str | Trading symbol |

**Returns:** `Dict[str, Any]` with keys:
- `pip_value`: float
- `lot_step`: float
- `min_lot`: float
- `max_lot`: float

## Enumerations

### OrderType

```python
class OrderType(Enum):
    ORDER_A = "ORDER_A"
    ORDER_B = "ORDER_B"
    DUAL = "DUAL"
```

### LogicRoute

```python
class LogicRoute(Enum):
    LOGIC1 = "LOGIC1"  # 5m scalp
    LOGIC2 = "LOGIC2"  # 15m intraday
    LOGIC3 = "LOGIC3"  # 1h swing
```

### MarketState

```python
class MarketState(Enum):
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"
```

### OrderStatus

```python
class OrderStatus(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
```

## Data Classes

### OrderRecord

```python
@dataclass
class OrderRecord:
    ticket: int
    plugin_id: str
    symbol: str
    direction: str
    lot_size: float
    open_price: float
    sl_price: float
    tp_price: float
    comment: str
    status: OrderStatus
    created_at: datetime
    closed_at: Optional[datetime] = None
    close_price: Optional[float] = None
    profit: Optional[float] = None
    swap: Optional[float] = None
    commission: Optional[float] = None
    magic_number: int = 0
    order_type: str = "A"
```

## Error Handling

All service methods may raise exceptions. Wrap calls in try-except:

```python
try:
    ticket = await service_api.orders.place_order(...)
except ConnectionError as e:
    logger.error(f"MT5 connection error: {e}")
except ValueError as e:
    logger.error(f"Invalid parameter: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## Plugin Isolation

All services enforce plugin isolation:

1. Orders are tagged with `plugin_id` in the comment field
2. Plugins can only query/modify their own orders
3. Each plugin has its own magic number for MT5 orders
4. Database tracks orders per plugin

```python
# Plugin A cannot access Plugin B's orders
orders_a = await service_api.orders.get_open_orders("plugin_a")
orders_b = await service_api.orders.get_open_orders("plugin_b")
# orders_a and orders_b are completely separate
```

## Rate Limiting

Services implement internal rate limiting:

| Operation | Limit |
|-----------|-------|
| Order placement | 3 retries, 0.5s delay |
| Order modification | 3 retries, 0.5s delay |
| Market data | Cached for 1 second |

## Best Practices

1. **Always check risk before trading:**
```python
status = await service_api.risk.check_daily_limit(plugin_id)
if not status["can_trade"]:
    return
```

2. **Use calculated lot sizes:**
```python
lot_size = await service_api.risk.calculate_lot_size(...)
lot_size = min(lot_size, max_lot_size)
```

3. **Validate trend alignment:**
```python
aligned = await service_api.trend.validate_v3_trend_alignment(...)
if not aligned:
    return
```

4. **Handle partial closes properly:**
```python
result = await service_api.profit.book_profit(
    plugin_id=plugin_id,
    order_id=ticket,
    percentage=50.0
)
if result["remaining_volume"] > 0:
    # Move remaining to breakeven
    await service_api.profit.move_to_breakeven(plugin_id, ticket)
```

---

**Document Version:** 1.0
**Last Updated:** January 2026
**Architecture Version:** V5 Hybrid Plugin Architecture
