# API SPECIFICATIONS

**Version:** 2.0 (Updated with V3/V6 Order Routing)  
**Date:** 2026-01-12  
**Type:** ServiceAPI Internal Layer

---

## 📋 SERVICE API OVERVIEW

**Purpose:** Provide plugins safe, isolated access to bot core functions with V3/V6 specific order routing.

**Key Additions for V3/V6:**
- Dual order methods (V3 requirement)
- Single Order A / Order B methods (V6 requirement)
- Conditional order routing
- Dual trend systems (Traditional TF + V6 Trend Pulse)

---

## 🔧 OrderExecutionService API

### **V3-Specific: Dual Order Methods**

#### `place_dual_orders_v3()`
**Purpose:** Place V3 hybrid SL dual order system (Order A + Order B)

**Signature:**
```python
async def place_dual_orders_v3(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size_total: float,
    order_a_sl: float,      # V3 Smart SL from Pine Script
    order_a_tp: float,      # TP2 (extended target)
    order_b_sl: float,      # Fixed $10 SL (DIFFERENT from order_a)
    order_b_tp: float,      # TP1 (closer target)
    logic_route: str        # 'LOGIC1', 'LOGIC2', 'LOGIC3'
) -> Tuple[int, int]:       # (order_a_ticket, order_b_ticket)
```

**Returns:** Tuple of two MT5 tickets

**Example:**
```python
order_a, order_b = await service_api.orders.place_dual_orders_v3(
    plugin_id='combined_v3',
    symbol='XAUUSD',
    direction='BUY',
    lot_size_total=0.10,    # Will be split 50/50
    order_a_sl=2028.00,     # Smart SL
    order_a_tp=2035.00,     # Extended TP
    order_b_sl=2029.50,     # Fixed $10 SL (different!)
    order_b_tp=2032.00,     # Closer TP
    logic_route='LOGIC2'
)
# Returns: (12345, 12346)
```

---

### **V6-Specific: Conditional Order Methods**

#### `place_single_order_a()`
**Purpose:** Place Order A ONLY (for 15M/1H V6 plugins)

**Signature:**
```python
async def place_single_order_a(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,
    comment: str = 'ORDER_A'
) -> int:
```

**Example:**
```python
# 15M plugin uses ORDER A ONLY
ticket = await service_api.orders.place_single_order_a(
    plugin_id='price_action_15m',
    symbol='XAUUSD',
    direction='BUY',
    lot_size=0.10,
    sl_price=2028.00,
    tp_price=2035.00
)
```

---

#### `place_single_order_b()`
**Purpose:** Place Order B ONLY (for 1M V6 plugin)

**Signature:**
```python
async def place_single_order_b(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,  # Uses TP1 for quick exit
    comment: str = 'ORDER_B'
) -> int:
```

**Example:**
```python
# 1M plugin uses ORDER B ONLY
ticket = await service_api.orders.place_single_order_b(
    plugin_id='price_action_1m',
    symbol='XAUUSD',
    direction='BUY',
    lot_size=0.05,  # Half size for scalping
    sl_price=2029.00,
    tp_price=2031.00  # TP1 quick exit
)
```

---

#### `place_dual_orders_v6()`
**Purpose:** Place DUAL orders for 5M V6 plugin

**Signature:**
```python
async def place_dual_orders_v6(
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size_total: float,
    sl_price: float,        # Same SL for both orders
    tp1_price: float,       # Order B target
    tp2_price: float        # Order A target
) -> Tuple[int, int]:
```

**Example:**
```python
# 5M plugin uses DUAL orders (different from V3)
order_a, order_b = await service_api.orders.place_dual_orders_v6(
    plugin_id='price_action_5m',
    symbol='XAUUSD',
    direction='BUY',
    lot_size_total=0.10,
    sl_price=2028.00,       # Same SL for both
    tp1_price=2032.00,      # Order B target
    tp2_price=2035.00       # Order A target
)
```

---

### **Universal Order Methods (Both V3 & V6)**

#### `modify_order()`
**Purpose:** Modify existing order SL/TP

**Signature:**
```python
async def modify_order(
    plugin_id: str,
    order_id: int,
    new_sl: float = None,
    new_tp: float = None
) -> bool
```

#### `close_position()`
**Purpose:** Close entire position

**Signature:**
```python
async def close_position(
    plugin_id: str,
    order_id: int,
    reason: str = 'Manual'
) -> Dict
```

**Returns:**
```json
{
    "success": true,
    "closed_volume": 0.10,
    "profit_pips": 15.5,
    "profit_dollars": 155.00
}
```

#### `close_position_partial()`
**Purpose:** Close partial position (for TP1/TP2/TP3)

**Signature:**
```python
async def close_position_partial(
    plugin_id: str,
    order_id: int,
    percentage: float  # 25.0 = close 25%
) -> Dict
```

#### `get_open_orders()`
**Purpose:** Get all open orders for this plugin

**Signature:**
```python
async def get_open_orders(
    plugin_id: str,
    symbol: str = None
) -> List[Dict]
```

---

## 📊 RiskManagementService API

### `calculate_lot_size()`
**Purpose:** Calculate safe lot size based on risk

**Signature:**
```python
async def calculate_lot_size(
    plugin_id: str,
    symbol: str,
    risk_percentage: float,  # e.g., 1.5
    stop_loss_pips: float,
    account_balance: float = None  # Auto-fetch if None
) -> float
```

### `check_daily_limit()`
**Purpose:** Check if daily loss limit reached

**Signature:**
```python
async def check_daily_limit(plugin_id: str) -> Dict
```

**Returns:**
```json
{
    "daily_loss": 250.00,
    "daily_limit": 500.00,
    "remaining": 250.00,
    "can_trade": true
}
```

---

## 📈 TrendManagementService API (Dual Systems)

### **V3 Traditional Timeframe Trend Manager**

#### `get_timeframe_trend()`
**Purpose:** Get V3 4-pillar MTF trend

**Signature:**
```python
async def get_timeframe_trend(
    symbol: str,
    timeframe: str  # '15m', '1h', '4h', '1d' ONLY
) -> Dict
```

**Returns:**
```json
{
    "timeframe": "15m",
    "direction": "bullish",  # or "bearish"
    "value": 1,             # 1=bullish, -1=bearish
    "last_updated": "2026-01-12 10:30"
}
```

**Example:**
```python
# V3 plugin checks 15m trend
trend_15m = await service_api.trend.get_timeframe_trend('XAUUSD', '15m')
if trend_15m['direction'] == 'bullish' and signal_direction == 'BUY':
    # Proceed with entry
    pass
```

---

#### `get_mtf_trends()`
**Purpose:** Get ALL 4-pillar trends at once

**Signature:**
```python
async def get_mtf_trends(symbol: str) -> Dict
```

**Returns:**
```json
{
    "15m": 1,   # bullish
    "1h": 1,    # bullish
    "4h": -1,   # bearish
    "1d": 1     # bullish
}
```

---

#### `validate_v3_trend_alignment()`
**Purpose:** Check if signal aligns with V3 4-pillar system

**Signature:**
```python
async def validate_v3_trend_alignment(
    symbol: str,
    direction: str,  # 'BUY' or 'SELL'
    min_aligned: int = 3  # At least 3/4 pillars must align
) -> bool
```

**Example:**
```python
# For BUY: need 3+ bullish trends
aligned = await service_api.trend.validate_v3_trend_alignment(
    'XAUUSD',
    'BUY',
    min_aligned=3
)
# Returns True if 3 or 4 pillars are bullish
```

---

### **V6 Trend Pulse System (NEW)**

#### `update_trend_pulse()`
**Purpose:** Update market_trends table with Trend Pulse alert data

**Signature:**
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

**Example:**
```python
# When TREND_PULSE alert received
await service_api.trend.update_trend_pulse(
    symbol='XAUUSD',
    timeframe='15',
    bull_count=5,
    bear_count=1,
    market_state='TRENDING_BULLISH',
    changes='15m,1h'  # Which TFs changed
)
```

---

#### `get_market_state()`
**Purpose:** Get current market state for symbol (V6)

**Signature:**
```python
async def get_market_state(symbol: str) -> str
```

**Returns:** `'TRENDING_BULLISH'`, `'TRENDING_BEARISH'`, `'SIDEWAYS'`, etc.

**Example:**
```python
# 15M V6 plugin checks market state
state = await service_api.trend.get_market_state('XAUUSD')
if state == 'TRENDING_BULLISH' and signal_direction == 'BUY':
    # Proceed
    pass
```

---

#### `check_pulse_alignment()`
**Purpose:** Check if signal aligns with Trend Pulse counts

**Signature:**
```python
async def check_pulse_alignment(
    symbol: str,
    direction: str  # 'BUY' or 'SELL'
) -> bool
```

**Logic:**
- For BUY: `bull_count > bear_count`
- For SELL: `bear_count > bull_count`

**Example:**
```python
# 5M V6 plugin checks pulse alignment
aligned = await service_api.trend.check_pulse_alignment('XAUUSD', 'BUY')
# Returns True if bull_count > bear_count across all TFs
```

---

#### `get_pulse_data()`
**Purpose:** Get raw Trend Pulse counts

**Signature:**
```python
async def get_pulse_data(symbol: str, timeframe: str = None) -> Dict
```

**Returns:**
```json
{
    "5": {"bull_count": 4, "bear_count": 2},
    "15": {"bull_count": 5, "bear_count": 1},
    "60": {"bull_count": 3, "bear_count": 3}
}
```

---

## 💰 ProfitBookingService API

### `book_profit()`
**Purpose:** Book partial profit (TP1, TP2, TP3)

**Signature:**
```python
async def book_profit(
    plugin_id: str,
    order_id: int,
    percentage: float,  # 25.0, 50.0, 100.0
    reason: str = 'TP1'
) -> Dict
```

**Returns:**
```json
{
    "closed_volume": 0.05,
    "remaining_volume": 0.15,
    "profit_pips": 10.0,
    "profit_dollars": 50.00
}
```

### `move_to_breakeven()`
**Purpose:** Move SL to breakeven + buffer

**Signature:**
```python
async def move_to_breakeven(
    plugin_id: str,
    order_id: int,
    buffer_pips: float = 2.0
) -> bool
```

**Example:**
```python
# After TP1 hit (V6 5M plugin)
await service_api.profit.book_profit(
    plugin_id='price_action_5m',
    order_id=order_a_ticket,
    percentage=50.0,
    reason='TP1'
)

# Move to breakeven
await service_api.profit.move_to_breakeven(
    plugin_id='price_action_5m',
    order_id=order_a_ticket,
    buffer_pips=2.0
)
```

---

## 📊 MarketDataService API

### `get_current_spread()`
**Purpose:** Get current spread in pips

**Signature:**
```python
async def get_current_spread(symbol: str) -> float
```

**Example:**
```python
# 1M V6 plugin checks spread before entry
spread = await service_api.market.get_current_spread('XAUUSD')
if spread > 2.0:
    logger.info("❌ Entry skipped: spread too high")
    return False
```

### `get_current_price()`
**Purpose:** Get current bid/ask prices

**Signature:**
```python
async def get_current_price(symbol: str) -> Dict
```

**Returns:**
```json
{
    "bid": 2030.45,
    "ask": 2030.55,
    "spread_pips": 1.0
}
```

---

## 🔐 SECURITY & PERMISSIONS

### **Plugin Isolation**
- Each plugin can ONLY access its own orders
- Cross-plugin queries return empty results
- ServiceAPI enforces `plugin_id` checks on ALL methods

### **Permission Model**
```python
class PluginPermissions:
    """
    Each plugin has specific permissions
    """
    V3_COMBINED = [
        'place_dual_orders_v3',
        'modify_orders',
        'close_positions',
        'get_mtf_trends',
        'validate_v3_trend_alignment'
    ]
    
    V6_1M = [
        'place_single_order_b',  # ORDER B ONLY
        'get_market_state',
        'check_pulse_alignment'
    ]
    
    V6_5M = [
        'place_dual_orders_v6',  # DUAL ORDERS
        'move_to_breakeven',
        'check_pulse_alignment'
    ]
    
    V6_15M = [
        'place_single_order_a',  # ORDER A ONLY
        'get_market_state',
        'check_pulse_alignment'
    ]
    
    V6_1H = [
        'place_single_order_a',  # ORDER A ONLY
        'get_market_state'
    ]
```

---

## ✅ COMPLETE USAGE EXAMPLES

### **V3 Plugin Usage**
```python
class CombinedV3Plugin(BaseLogicPlugin):
    async def process_entry(self, alert):
        # 1. Validate V3 trend alignment (4-pillar)
        aligned = await self.service_api.trend.validate_v3_trend_alignment(
            symbol=alert.symbol,
            direction=alert.direction,
            min_aligned=3  # Need 3/4 pillars
        )
        
        if not aligned:
            return False
        
        # 2. Calculate lot size
        lot_total = await self.service_api.risk.calculate_lot_size(...)
        
        # 3. Place V3 dual orders (hybrid SL)
        order_a, order_b = await self.service_api.orders.place_dual_orders_v3(
            plugin_id=self.plugin_id,
            symbol=alert.symbol,
            direction=alert.direction,
            lot_size_total=lot_total,
            order_a_sl=alert.sl_price,      # Smart SL
            order_a_tp=alert.tp2_price,
            order_b_sl=fixed_sl_price,      # Fixed $10 SL
            order_b_tp=alert.tp1_price,
            logic_route='LOGIC2'
        )
        
        return True
```

### **V6 1M Plugin Usage**
```python
class PriceAction1M(BaseLogicPlugin):
    async def process_entry(self, alert):
        # 1. Check spread
        spread = await self.service_api.market.get_current_spread(alert.symbol)
        if spread > 2.0:
            return False
        
        # 2. Calculate lot (0.5x risk multiplier)
        lot = await self.service_api.risk.calculate_lot_size(...) * 0.5
        
        # 3. Place ORDER B ONLY
        ticket = await self.service_api.orders.place_single_order_b(
            plugin_id=self.plugin_id,
            symbol=alert.symbol,
            direction=alert.direction,
            lot_size=lot,
            sl_price=alert.sl_price,
            tp_price=alert.tp1_price  # TP1 quick exit
        )
        
        return True
```

### **V6 5M Plugin Usage**
```python
class PriceAction5M(BaseLogicPlugin):
    async def process_entry(self, alert):
        # 1. Check pulse alignment
        aligned = await self.service_api.trend.check_pulse_alignment(
            symbol=alert.symbol,
            direction=alert.direction
        )
        
        if not aligned:
            return False
        
        # 2. Place DUAL orders
        order_a, order_b = await self.service_api.orders.place_dual_orders_v6(
            plugin_id=self.plugin_id,
            symbol=alert.symbol,
            direction=alert.direction,
            lot_size_total=lot,
            sl_price=alert.sl_price,
            tp1_price=alert.tp1_price,
            tp2_price=alert.tp2_price
        )
        
        # 3. After TP1, move to breakeven
        # (handled by profit booking service)
        
        return True
```

---

## 🎯 IMPLEMENTATION CHECKLIST

- [ ] V3 dual order methods implemented
- [ ] V6 conditional order methods (single A, single B, dual)
- [ ] Traditional TF trend manager functional
- [ ] V6 Trend Pulse system operational
- [ ] Plugin isolation verified
- [ ] All examples tested
- [ ] Documentation complete

**Status:** READY FOR PHASE 4 & 7 IMPLEMENTATION
