# PHASE 7: V6 PRICE ACTION INTEGRATION

**Version:** 1.0  
**Timeline:** Week 5-6 (10-14 days)  
**Prerequisites:** Phase 1-6 Complete  
**Status:** 🟡 PLANNED

---

## 🎯 PHASE OBJECTIVE

Integrate V6 Price Action Logic as **4 independent plugins** running in parallel with V3 Combined Logic, implementing specialized order routing, Trend Pulse system, and complete database isolation.

**Success Criteria:**
- ✅ 4 V6 plugins operational (1M/5M/15M/1H)
- ✅ Trend Pulse system updating DB
- ✅ Conditional order routing working
- ✅ Zero interference with V3 system
- ✅ All ADX/momentum filters active

---

## 📊 V6 ARCHITECTURE SUMMARY

### **Dual Core Concept**

```
┌─────────────────────────────────────────────────────────┐
│                   ZEPIX BOT v3.0                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GROUP 1: V3 COMBINED LOGIC          GROUP 2: V6 PRICE ACTION │
│  ┌──────────────────────┐            ┌──────────────────────┐ │
│  │ Plugin: combined_v3  │            │ Plugin: price_action_1m│ │
│  │ DB: zepix_combined.db│            │ DB: zepix_price_action.db│ │
│  │ Signals: 12 types    │            │ ORDER B ONLY         │ │
│  │ Orders: DUAL (always)│            ├──────────────────────┤ │
│  │ Trend: Traditional   │            │ Plugin: price_action_5m│ │
│  └──────────────────────┘            │ DUAL ORDERS          │ │
│                                       ├──────────────────────┤ │
│                                       │ Plugin: price_action_15m│ │
│                                       │ ORDER A ONLY         │ │
│                                       ├──────────────────────┤ │
│                                       │ Plugin: price_action_1h│ │
│                                       │ ORDER A ONLY         │ │
│                                       └──────────────────────┘ │
│                                                          │
│              ISOLATED: Separate DBs, Managers, States   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 STEP-BY-STEP IMPLEMENTATION

### **STEP 1: Create V6 Data Models** (Day 1-2)

**Files to Create:**
- `src/v6_alert_models.py`

**Content:**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class ZepixV6Alert(BaseModel):
    """
    V6 Enhanced Alert Payload - 15 Fields
    Source: Pine Script Signals & Overlays V6
    """
    type: str  # BULLISH_ENTRY, BEARISH_ENTRY, EXIT_*, TREND_PULSE
    ticker: str
    tf: str  # "1", "5", "15", "60"
    price: float
    direction: str  # BUY, SELL
    conf_level: str  # HIGH, MODERATE
    conf_score: int  # 0-100
    adx: Optional[float]
    adx_strength: str  # STRONG, WEAK, NONE
    sl: Optional[float]
    tp1: Optional[float]
    tp2: Optional[float]
    tp3: Optional[float]
    alignment: str  # "5/1" (bull_count/bear_count)
    tl_status: str  # TL_OK, TL_BROKEN
    
    @validator('adx', pre=True)
    def handle_na(cls, v):
        return None if v == 'NA' else v
    
    def get_pulse_counts(self) -> tuple:
        """Parse alignment '5/1' -> (5, 1)"""
        parts = self.alignment.split('/')
        return int(parts[0]), int(parts[1])


class TrendPulseAlert(BaseModel):
    """
    Separate alert type for Trend Pulse updates
    """
    type: str  # "TREND_PULSE"
    symbol: str
    tf: str
    bull_count: int
    bear_count: int
    changes: str  # Comma-separated TF changes
    state: str  # TRENDING_BULLISH, SIDEWAYS, etc.
```

**Testing:**
```python
# tests/test_v6_models.py
def test_v6_alert_parsing():
    payload = "BULLISH_ENTRY|XAUUSD|5|2030.50|BUY|HIGH|85|25.5|STRONG|2028.00|2032.00|2035.00|2038.00|5/1|TL_OK"
    alert = parse_v6_payload(payload)
    assert alert.tf == "5"
    assert alert.conf_score == 85
    assert alert.adx == 25.5
```

---

### **STEP 2: Create 4 Price Action Logic Classes** (Day 2-4)

**Files to Create:**
- `src/logic_plugins/price_action_1m/plugin.py`
- `src/logic_plugins/price_action_5m/plugin.py`
- `src/logic_plugins/price_action_15m/plugin.py`
- `src/logic_plugins/price_action_1h/plugin.py`

**Template (1M Example):**
```python
from src.core.plugin_system.base_plugin import BaseLogicPlugin

class PriceAction1M(BaseLogicPlugin):
    """
    1-Minute Scalping Logic
    - ADX > 20
    - Confidence >= 80
    - Spread < 2 pips
    - ORDER B ONLY
    """
    
    async def on_signal_received(self, signal):
        # 1. Validate filters
        if not self._validate_entry(signal):
            return False
        
        # 2. Calculate lot size (0.5x risk multiplier)
        lot = await self.service_api.risk.calculate_lot_size(
            symbol=signal['symbol'],
            risk_percentage=1.0,  # Base risk
            stop_loss_pips=self._calculate_sl_pips(signal)
        )
        lot = lot * 0.5  # 1M scalping uses half size
        
        # 3. Place ORDER B ONLY
        ticket = await self.service_api.orders.place_single_order_b(
            symbol=signal['symbol'],
            direction=signal['direction'],
            lot_size=lot,
            sl_price=signal.get('sl_price'),
            tp_price=signal.get('tp1_price'),  # TP1 for quick exit
            comment=f"{self.plugin_id}_entry"
        )
        
        # 4. Log to database
        self.database.save_trade({
            'ticket': ticket,
            'adx': signal.get('adx'),
            'confidence_score': signal.get('conf_score'),
            'order_type': 'ORDER_B_ONLY'
        })
        
        return True
    
    def _validate_entry(self, signal):
        # ADX Filter
        if signal.get('adx', 0) < 20:
            self.logger.info("❌ 1M Skip: ADX < 20 (choppy)")
            return False
        
        # Confidence Filter
        if signal.get('conf_score', 0) < 80:
            self.logger.info(f"❌ 1M Skip: Confidence {signal['conf_score']} < 80")
            return False
        
        # Spread Filter (check via ServiceAPI)
        spread = await self.service_api.market.get_current_spread(signal['symbol'])
        if spread > 2.0:
            self.logger.info(f"❌ 1M Skip: Spread {spread} > 2 pips")
            return False
        
        return True
```

**5M Logic (DUAL ORDERS):**
```python
class PriceAction5M(BaseLogicPlugin):
    async def on_signal_received(self, signal):
        # Validate: ADX >= 25, 15m alignment
        if not self._validate_with_trend_alignment(signal):
            return False
        
        # Place DUAL ORDERS
        order_a, order_b = await self.service_api.orders.place_dual_orders(
            symbol=signal['symbol'],
            direction=signal['direction'],
            lot_size=lot,
            order_a_sl=signal['sl_price'],
            order_a_tp=signal['tp2_price'],
            order_b_sl=signal['sl_price'],
            order_b_tp=signal['tp1_price']
        )
        
        return True
```

**15M Logic (ORDER A ONLY):**
```python
class PriceAction15M(BaseLogicPlugin):
    async def on_signal_received(self, signal):
        # Validate: Market State, Pulse Alignment
        market_state = await self.service_api.trend.get_market_state(signal['symbol'])
        if not self._is_aligned(signal['direction'], market_state):
            return False
        
        # Place ORDER A ONLY
        ticket = await self.service_api.orders.place_single_order_a(...)
        return True
```

---

### **STEP 3: Implement Trend Pulse System** (Day 4-5)

**Files to Create/Modify:**
- `src/services/trend_pulse_manager.py` (NEW)
- `src/processors/alert_processor.py` (MODIFY)

**Trend Pulse Manager:**
```python
class TrendPulseManager:
    """
    Manages V6 Trend Pulse alerts
    Separate from V3 Traditional Trend Manager
    """
    
    def __init__(self, database):
        self.db = database
        self._ensure_table_exists()
    
    async def update_pulse(self, alert: TrendPulseAlert):
        """
        Update market_trends table with pulse data
        """
        self.db.execute("""
            INSERT OR REPLACE INTO market_trends 
            (symbol, timeframe, bull_count, bear_count, market_state, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alert.symbol,
            alert.tf,
            alert.bull_count,
            alert.bear_count,
            alert.state,
            datetime.now()
        ))
        
        logger.info(f"✅ Trend Pulse: {alert.symbol} {alert.tf} → {alert.state}")
    
    async def get_market_state(self, symbol: str) -> str:
        """
        Get current market state for symbol
        Returns: TRENDING_BULLISH, TRENDING_BEARISH, SIDEWAYS
        """
        # Aggregate across timeframes
        rows = self.db.query("""
            SELECT market_state, COUNT(*) as count
            FROM market_trends
            WHERE symbol = ?
            GROUP BY market_state
            ORDER BY count DESC
        """, (symbol,))
        
        return rows[0]['market_state'] if rows else 'UNKNOWN'
    
    async def check_pulse_alignment(self, symbol: str, direction: str) -> bool:
        """
        For BUY: bull_count should be > bear_count
        For SELL: bear_count should be > bull_count
        """
        total_bulls = self.db.query_scalar("""
            SELECT SUM(bull_count) FROM market_trends WHERE symbol = ?
        """, (symbol,))
        
        total_bears = self.db.query_scalar("""
            SELECT SUM(bear_count) FROM market_trends WHERE symbol = ?
        """, (symbol,))
        
        if direction == 'BUY':
            return total_bulls > total_bears
        else:
            return total_bears > total_bulls
```

**Alert Processor Integration:**
```python
# In alert_processor.py
async def process_alert(self, message: str):
    if message.startswith('TREND_PULSE'):
        alert = parse_trend_pulse(message)
        await self.trend_pulse_manager.update_pulse(alert)
        return  # Don't route to trading engine
    
    elif message.startswith('BULLISH_ENTRY') or message.startswith('BEARISH_ENTRY'):
        alert = parse_v6_payload(message)
        await self.trading_engine.execute_v6_entry(alert)
```

---

### **STEP 4: Implement Conditional Order Routing in ServiceAPI** (Day 5-6)

**File:** `src/core/plugin_system/service_api.py`

**Add Methods:**
```python
class ServiceAPI:
    # ... existing methods ...
    
    async def place_single_order_a(self, plugin_id, symbol, direction, lot_size, sl_price, tp_price, comment):
        """
        Place Order A only (for 15M/1H plugins)
        """
        ticket = await self.order_manager.place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_size,
            sl_price=sl_price,
            tp_price=tp_price,
            comment=f"{plugin_id}_order_a"
        )
        
        logger.info(f"✅ {plugin_id}: ORDER A placed #{ticket}")
        return ticket
    
    async def place_single_order_b(self, plugin_id, symbol, direction, lot_size, sl_price, tp_price, comment):
        """
        Place Order B only (for 1M plugin)
        """
        ticket = await self.order_manager.place_order(
            symbol=symbol,
            direction=direction,
            lot_size=lot_size,
            sl_price=sl_price,
            tp_price=tp_price,
            comment=f"{plugin_id}_order_b"
        )
        
        logger.info(f"✅ {plugin_id}: ORDER B placed #{ticket}")
        return ticket
    
    async def place_dual_orders(self, plugin_id, symbol, direction, lot_size, order_a_sl, order_a_tp, order_b_sl, order_b_tp):
        """
        Place both Order A and Order B (for 5M plugin)
        """
        lot_a = lot_size * 0.5
        lot_b = lot_size * 0.5
        
        ticket_a = await self.place_single_order_a(...)
        ticket_b = await self.place_single_order_b(...)
        
        return ticket_a, ticket_b
```

---

### **STEP 5: Create V6 Plugin Database Schema** (Day 6-7)

**File:** `data/zepix_price_action.db`

**Schema:**
```sql
-- Per-plugin trade tables
CREATE TABLE price_action_1m_trades (
    ticket INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction TEXT,
    lot_size REAL,
    entry_price REAL,
    sl_price REAL,
    tp_price REAL,
    adx REAL,
    confidence_score INTEGER,
    spread_pips REAL,
    order_b_ticket INTEGER,  -- Only ORDER B
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    profit REAL
);

CREATE TABLE price_action_5m_trades (
    ticket INTEGER PRIMARY KEY,
    ...
    order_a_ticket INTEGER,
    order_b_ticket INTEGER,  -- DUAL ORDERS
    ...
);

CREATE TABLE price_action_15m_trades (
    ticket INTEGER PRIMARY KEY,
    ...
    order_a_ticket INTEGER,  -- Only ORDER A
    market_state TEXT,
    pulse_alignment TEXT,
    ...
);

CREATE TABLE price_action_1h_trades (
    ticket INTEGER PRIMARY KEY,
    ...
    order_a_ticket INTEGER,  -- Only ORDER A
    ...
);

-- Shared Trend Pulse table
CREATE TABLE market_trends (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    bull_count INTEGER,
    bear_count INTEGER,
    market_state TEXT,
    last_updated TIMESTAMP,
    PRIMARY KEY (symbol, timeframe)
);
```

---

### **STEP 6: Wire V6 Plugins into TradingEngine** (Day 7-8)

**File:** `src/core/trading_engine.py`

**Modifications:**
```python
class TradingEngine:
    def __init__(self, config):
        # ... existing V3 setup ...
        
        # V6 Price Action Setup
        self.v6_enabled = config.get('v6_integration', {}).get('enabled', False)
        
        if self.v6_enabled:
            # Initialize Trend Pulse Manager
            v6_db = PluginDatabase('price_action_shared')
            self.trend_pulse = TrendPulseManager(v6_db)
            
            # Initialize 4 V6 Plugins
            self.v6_plugins = {
                '1': self.plugin_registry.load_plugin('price_action_1m'),
                '5': self.plugin_registry.load_plugin('price_action_5m'),
                '15': self.plugin_registry.load_plugin('price_action_15m'),
                '60': self.plugin_registry.load_plugin('price_action_1h')
            }
    
    async def execute_v6_entry(self, alert: ZepixV6Alert):
        """
        Route V6 entry to appropriate plugin
        """
        plugin = self.v6_plugins.get(alert.tf)
        
        if not plugin or not plugin.enabled:
            logger.warning(f"⚠️ V6 Plugin for {alert.tf}m not enabled")
            return
        
        # Execute plugin's entry logic
        success = await plugin.on_signal_received({
            'symbol': alert.ticker,
            'direction': alert.direction,
            'price': alert.price,
            'sl_price': alert.sl,
            'tp1_price': alert.tp1,
            'tp2_price': alert.tp2,
            'adx': alert.adx,
            'conf_score': alert.conf_score,
            'alignment': alert.alignment
        })
        
        if success:
            logger.info(f"✅ V6 {alert.tf}m Entry: {alert.ticker} {alert.direction}")
```

---

### **STEP 7: Configuration Setup** (Day 8)

**File:** `config/config.json`

**Add Section:**
```json
{
  "v6_integration": {
    "enabled": true,
    "plugins": {
      "price_action_1m": {
        "enabled": true,
        "filters": {
          "min_adx": 20,
          "min_confidence": 80,
          "max_spread_pips": 2.0
        },
        "risk_multiplier": 0.5
      },
      "price_action_5m": {
        "enabled": true,
        "filters": {
          "min_adx": 25,
          "min_confidence": 70,
          "require_15m_alignment": true
        },
        "risk_multiplier": 1.0
      },
      "price_action_15m": {
        "enabled": true,
        "filters": {
          "min_adx": 20,
          "check_market_state": true,
          "check_pulse_alignment": true
        },
        "risk_multiplier": 1.0
      },
      "price_action_1h": {
        "enabled": true,
        "filters": {
          "require_4h_1d_alignment": true
        },
        "risk_multiplier": 0.625
      }
    }
  }
}
```

---

### **STEP 8: Testing** (Day 9-11)

**Test Scenarios:**

**1M Plugin Tests:**
```python
def test_1m_adx_filter():
    alert = create_v6_alert(tf='1', adx=15)
    result = plugin_1m.on_signal_received(alert)
    assert result == False  # ADX < 20

def test_1m_order_b_only():
    alert = create_v6_alert(tf='1', adx=25, conf=85)
    result = plugin_1m.on_signal_received(alert)
    assert result == True
    # Verify ORDER B placed, ORDER A not placed
```

**5M Plugin Tests:**
```python
def test_5m_dual_orders():
    alert = create_v6_alert(tf='5', adx=30, conf=75)
    result = plugin_5m.on_signal_received(alert)
    assert result == True
    # Verify both ORDER A and ORDER B placed
```

**Trend Pulse Tests:**
```python
def test_trend_pulse_update():
    pulse = TrendPulseAlert(
        type='TREND_PULSE',
        symbol='XAUUSD',
        tf='15',
        bull_count=5,
        bear_count=1,
        state='TRENDING_BULLISH'
    )
    trend_pulse_manager.update_pulse(pulse)
    
    state = trend_pulse_manager.get_market_state('XAUUSD')
    assert state == 'TRENDING_BULLISH'
```

---

### **STEP 9: Integration Testing (V3 + V6 Simultaneous)** (Day 11-12)

**Test:** Both systems running in parallel

```python
async def test_dual_core_execution():
    # Send V3 signal
    v3_alert = create_v3_alert(signal_type='Momentum_Breakout', tf='15')
    await trading_engine.execute_v3_entry(v3_alert)
    
    # Send V6 signal
    v6_alert = create_v6_alert(tf='5')
    await trading_engine.execute_v6_entry(v6_alert)
    
    # Verify:
    # - V3 trade in zepix_combined.db
    # - V6 trade in zepix_price_action.db
    # - No cross-contamination
```

---

### **STEP 10: Shadow Mode & Production Deployment** (Day 12-14)

**Shadow Mode (3 days):**
- V6 plugins observe but don't trade
- Log what trades WOULD have been placed
- Compare with V3 system performance
- Validate Trend Pulse accuracy

**Cutover:**
1. Enable V6 plugins one by one (1M → 5M → 15M → 1H)
2. Monitor for 24 hours each
3. Full activation after validation

---

## ✅ COMPLETION CRITERIA

- [ ] All 4 V6 plugins load successfully
- [ ] Trend Pulse alerts update DB correctly
- [ ] 1M plugin only places ORDER B
- [ ] 5M plugin places DUAL ORDERS
- [ ] 15M/1H plugins only place ORDER A
- [ ] ADX/confidence/spread filters working
- [ ] V3 and V6 systems isolated (no interference)
- [ ] All tests passing (unit + integration + E2E)
- [ ] Shadow mode validation complete
- [ ] User acceptance testing passed

---

## 🚨 ROLLBACK PLAN

**If V6 fails:**
1. Disable all V6 plugins via config
2. V3 system continues unaffected
3. Debug V6 in isolation
4. Re-deploy after fixes

**No impact on V3:**
- Separate databases ensure V3 continues
- Plugin system allows V6 disable without code changes

---

**Phase 7 Status:** READY TO EXECUTE (after Phases 1-6 complete)
