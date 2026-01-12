# PHASE 4: V3 COMBINED LOGIC MIGRATION

**Version:** 2.0 (Updated with accurate V3 trading logic)  
**Timeline:** Week 4 (5-7 days)  
**Prerequisites:** Phases 1-3 complete  
**Status:** 🟡 PLANNED

---

## 🎯 PHASE OBJECTIVES

**SCOPE: V3 COMBINED LOGIC ONLY**

1. Migrate V3 12-signal Combined Logic to `combined_v3` plugin
2. Implement V3 specific features (dual orders, hybrid SL, MTF 4-pillar)
3. Test in shadow mode (72-hour parallel execution)
4. Cutover to plugin (disable legacy code)
5. **Zero logic regressions** - V3 behavior 100% preserved

**OUT OF SCOPE:**
- ❌ V6 Price Action Logic (moved to Phase 7)
- ❌ Trend Pulse system (V6 feature)
- ❌ Conditional order routing (V6 feature)

---

## 📊 V3 COMBINED LOGIC SUMMARY

### **12 Signals to Migrate**

**Entry Signals (7):**
1. Signal 1: Institutional Launchpad
2. Signal 2: Liquidity Trap
3. Signal 3: Momentum Breakout
4. Signal 4: Mitigation Test
5. Signal 5: Golden Pocket Flip
6. Signal 9/10: Screener Full Bullish/Bearish
7. **Signal 12: Sideways Breakout** (BONUS SIGNAL)

**Exit Signals (2):**
- Signal 7: Bullish Exit
- Signal 8: Bearish Exit

**Info Signals (2):**
- Signal 6: Volatility Squeeze
- Signal 11: Trend Pulse (info only, DB update)

---

### **V3 Routing Matrix (2-Tier System)**

**Priority 1: Signal Type Override**
```python
SIGNAL_OVERRIDES = {
    'Screener_Full_Bullish': 'LOGIC3',  # Force swing
    'Screener_Full_Bearish': 'LOGIC3',
    'Golden_Pocket_Flip_1H': 'LOGIC3',  # Higher TF
    'Golden_Pocket_Flip_4H': 'LOGIC3'
}
```

**Priority 2: Timeframe Routing**
```python
TIMEFRAME_ROUTING = {
    '5': 'LOGIC1',    # Scalping (1.25x multiplier)
    '15': 'LOGIC2',   # Intraday (1.0x multiplier)
    '60': 'LOGIC3',   # Swing (0.625x multiplier)
    '240': 'LOGIC3'   # Swing (0.625x multiplier)
}
DEFAULT = 'LOGIC2'
```

---

### **V3 Dual Order System (ALWAYS BOTH)**

**Order A: TP Trail**
```python
{
  "sl_price": alert.sl_price,  # V3 Smart SL from Pine Script
  "tp_price": alert.tp2_price,  # Extended TP target
  "lot_size": final_lot * 0.5,
  "comment": "OrderA_TP_Trail"
}
```

**Order B: Profit Trail**
```python
{
  "sl_price": FIXED_10_DOLLAR_SL,  # IGNORES alert.sl_price
  "tp_price": alert.tp1_price,      # Closer TP target
  "lot_size": final_lot * 0.5,
  "comment": "OrderB_Profit_Trail"
}
```

**CRITICAL:** Order B MUST use pyramid fixed $10 SL, NOT smart SL.

---

### **V3 MTF 4-Pillar System**

**Pine Script sends:** `[1m, 5m, 15m, 1H, 4H, 1D]` (6 trends)  
**Bot extracts:** Indices `[2:6]` = `[15m, 1H, 4H, 1D]` (4 pillars)  
**Bot ignores:** Indices `[0:2]` = `[1m, 5m]` (too noisy)

```python
def extract_mtf_trends(mtf_string: str) -> dict:
    """
    Parse MTF string and extract 4-pillar trends
    Input: "1,1,-1,1,1,1" (6 values)
    Output: {"15m": -1, "1h": 1, "4h": 1, "1d": 1}
    """
    trends = [int(x) for x in mtf_string.split(',')]
    return {
        "15m": trends[2],  # Index 2
        "1h": trends[3],   # Index 3
        "4h": trends[4],   # Index 4
        "1d": trends[5]    # Index 5
    }
```

---

### **V3 Position Sizing (4-Step Flow)**

```python
def calculate_v3_lot_size(alert, config) -> tuple:
    """
    Returns: (order_a_lot, order_b_lot)
    """
    # Step 1: Base lot from risk tier
    base_lot = config['risk_tiers'][alert.risk_tier]['base_lot']  # e.g. 0.10
    
    # Step 2: Apply V3 consensus multiplier (0.2 to 1.0)
    consensus_score = alert.consensus_score  # 0-9
    v3_multiplier = 0.2 + (consensus_score / 9.0) * 0.8  # Maps 0→0.2, 9→1.0
    
    # Step 3: Apply logic multiplier (LOGIC1/2/3)
    logic_route = determine_logic_route(alert)
    logic_multiplier = config['logic_multipliers'][logic_route]  # 1.25, 1.0, or 0.625
    
    # Step 4: Final lot = base × v3_mult × logic_mult
    final_lot = base_lot * v3_multiplier * logic_multiplier
    
    # Split 50/50 between Order A and Order B
    order_a_lot = final_lot * 0.5
    order_b_lot = final_lot * 0.5
    
    return round(order_a_lot, 2), round(order_b_lot, 2)
```

---

### **V3 Trend Bypass Logic**

```python
def should_bypass_trend_check(alert) -> bool:
    """
    V3 signals that bypass trend validation
    """
    # entry_v3 signals = fresh signals, bypass trend
    if alert.signal_source == 'entry_v3':
        return True
    
    # Legacy entries = require trend check
    if alert.signal_source == 'legacy':
        return False
    
    # SL hunt re-entry = require trend check
    if alert.is_sl_hunt_reentry:
        return False
    
    return False
```

---

## 📋 MIGRATION TASKS

### **STEP 1: Create Plugin Structure** (Day 1 - 4 hours)

**Directory:**
```
src/logic_plugins/combined_v3/
├── __init__.py
├── plugin.py               # Main plugin class
├── signal_handlers.py      # All 12 signal handlers
├── routing_logic.py        # 2-tier routing matrix
├── dual_order_manager.py   # Hybrid SL dual orders
├── mtf_processor.py        # 4-pillar extraction
├── position_sizer.py       # 4-step lot calculation
├── config.json             # Plugin configuration
└── README.md               # Documentation
```

**Plugin Config (`config.json`):**
```json
{
  "plugin_id": "combined_v3",
  "version": "1.0.0",
  "enabled": false,
  "shadow_mode": true,
  "description": "V3 Combined Logic - 12 Signals with Dual Orders",
  
  "signal_routing": {
    "signal_overrides": {
      "Screener_Full_Bullish": "LOGIC3",
      "Screener_Full_Bearish": "LOGIC3",
      "Golden_Pocket_Flip_1H": "LOGIC3",
      "Golden_Pocket_Flip_4H": "LOGIC3"
    },
    "timeframe_routing": {
      "5": "LOGIC1",
      "15": "LOGIC2",
      "60": "LOGIC3",
      "240": "LOGIC3"
    },
    "default_logic": "LOGIC2"
  },
  
  "logic_multipliers": {
    "LOGIC1": 1.25,
    "LOGIC2": 1.0,
    "LOGIC3": 0.625
  },
  
  "mtf_config": {
    "pillars_only": ["15m", "1h", "4h", "1d"],
    "ignore_timeframes": ["1m", "5m"]
  },
  
  "dual_orders": {
    "split_ratio": 0.5,
    "order_a_comment": "OrderA_TP_Trail",
    "order_b_comment": "OrderB_Profit_Trail",
    "order_b_fixed_sl": 10.0
  },
  
  "trend_bypass": {
    "bypass_for_entry_v3": true,
    "bypass_for_legacy": false,
    "bypass_for_sl_hunt": false
  },
  
  "supported_symbols": ["XAUUSD", "EURUSD", "GBPUSD"],
  "max_daily_loss": 500.0
}
```

---

### **STEP 2: Implement Signal Handlers** (Day 1-2)

**File:** `signal_handlers.py`

```python
class V3SignalHandlers:
    """
    Handles all 12 V3 signal types
    """
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.service_api = plugin.service_api
    
    async def handle_institutional_launchpad(self, alert):
        """Signal 1: Institutional Launchpad Entry"""
        logger.info(f"Signal 1: Institutional Launchpad - {alert.symbol} {alert.direction}")
        return await self._process_entry_signal(alert, signal_type='inst_launchpad')
    
    async def handle_liquidity_trap(self, alert):
        """Signal 2: Liquidity Trap Entry"""
        logger.info(f"Signal 2: Liquidity Trap - {alert.symbol}")
        return await self._process_entry_signal(alert, signal_type='liq_trap')
    
    async def handle_momentum_breakout(self, alert):
        """Signal 3: Momentum Breakout Entry"""
        return await self._process_entry_signal(alert, signal_type='momentum')
    
    async def handle_mitigation_test(self, alert):
        """Signal 4: Mitigation Test Entry"""
        return await self._process_entry_signal(alert, signal_type='mitigation')
    
    async def handle_golden_pocket_flip(self, alert):
        """Signal 5: Golden Pocket Flip Entry"""
        # This signal has TF-based routing override
        return await self._process_entry_signal(alert, signal_type='golden_pocket')
    
    async def handle_volatility_squeeze(self, alert):
        """Signal 6: Volatility Squeeze (Info only)"""
        logger.info(f"📊 Signal 6: Volatility Squeeze - {alert.symbol}")
        # Info signal, no trade placement
        return None
    
    async def handle_bullish_exit(self, alert):
        """Signal 7: Bullish Exit"""
        return await self._process_exit_signal(alert, exit_type='bullish')
    
    async def handle_bearish_exit(self, alert):
        """Signal 8: Bearish Exit"""
        return await self._process_exit_signal(alert, exit_type='bearish')
    
    async def handle_screener_full(self, alert):
        """Signal 9/10: Screener Full Bullish/Bearish"""
        # Always routes to LOGIC3 (override)
        return await self._process_entry_signal(alert, signal_type='screener_full')
    
    async def handle_trend_pulse(self, alert):
        """Signal 11: Trend Pulse (DB Update)"""
        await self.plugin.mtf_processor.update_trend_database(alert)
        return None
    
    async def handle_sideways_breakout(self, alert):
        """Signal 12: Sideways Breakout (BONUS)"""
        logger.info(f"Signal 12: Sideways Breakout - {alert.symbol}")
        return await self._process_entry_signal(alert, signal_type='sideways_breakout')
    
    async def _process_entry_signal(self, alert, signal_type):
        """Common entry processing"""
        # Route through plugin's entry pipeline
        return await self.plugin.process_v3_entry(alert, signal_type)
    
    async def _process_exit_signal(self, alert, exit_type):
        """Common exit processing"""
        return await self.plugin.process_v3_exit(alert, exit_type)
```

---

### **STEP 3: Implement Routing Logic** (Day 2)

**File:** `routing_logic.py`

```python
class V3RoutingLogic:
    """
    2-Tier routing: Signal Override → Timeframe Routing
    """
    
    def __init__(self, config):
        self.config = config
        self.overrides = config['signal_routing']['signal_overrides']
        self.tf_routing = config['signal_routing']['timeframe_routing']
        self.default = config['signal_routing']['default_logic']
    
    def determine_logic_route(self, alert, signal_type) -> str:
        """
        Returns: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
        """
        # Priority 1: Check signal type override
        if signal_type in self.overrides:
            route = self.overrides[signal_type]
            logger.debug(f"✅ Signal override: {signal_type} → {route}")
            return route
        
        # Priority 2: Check timeframe routing
        tf = str(alert.timeframe)
        if tf in self.tf_routing:
            route = self.tf_routing[tf]
            logger.debug(f"✅ TF routing: {tf}m → {route}")
            return route
        
        # Default
        logger.debug(f"✅ Default routing → {self.default}")
        return self.default
    
    def get_logic_multiplier(self, logic_route: str) -> float:
        """Get multiplier for given logic"""
        return self.config['logic_multipliers'][logic_route]
```

---

### **STEP 4: Implement Dual Order Manager** (Day 2-3)

**File:** `dual_order_manager.py`

```python
class V3DualOrderManager:
    """
    Manages V3 hybrid SL dual order system
    """
    
    def __init__(self, plugin, service_api):
        self.plugin = plugin
        self.service_api = service_api
        self.config = plugin.config['dual_orders']
    
    async def place_dual_orders_v3(self, alert, final_lot_size, logic_route):
        """
        Place Order A (Smart SL) + Order B (Fixed SL)
        """
        # Split lots 50/50
        lot_a = final_lot_size * self.config['split_ratio']
        lot_b = final_lot_size * self.config['split_ratio']
        
        # Order A: Use Pine Script Smart SL
        order_a_ticket = await self.service_api.orders.place_order(
            symbol=alert.symbol,
            direction=alert.direction,
            lot_size=round(lot_a, 2),
            sl_price=alert.sl_price,  # V3 Smart SL
            tp_price=alert.tp2_price,  # Extended TP
            comment=f"{self.config['order_a_comment']}_{logic_route}"
        )
        
        # Order B: Use Fixed $10 SL
        sl_distance_pips = self.config['order_b_fixed_sl'] / self._get_pip_value(alert.symbol)
        fixed_sl_price = self._calculate_fixed_sl(alert, sl_distance_pips)
        
        order_b_ticket = await self.service_api.orders.place_order(
            symbol=alert.symbol,
            direction=alert.direction,
            lot_size=round(lot_b, 2),
            sl_price=fixed_sl_price,  # FIXED $10 SL
            tp_price=alert.tp1_price,  # Closer TP
            comment=f"{self.config['order_b_comment']}_{logic_route}"
        )
        
        logger.info(f"✅ V3 Dual Orders: A#{order_a_ticket} B#{order_b_ticket}")
        
        # Save to database
        await self.plugin.database.save_dual_trade({
            'order_a_ticket': order_a_ticket,
            'order_b_ticket': order_b_ticket,
            'order_a_sl': alert.sl_price,
            'order_b_sl': fixed_sl_price,
            'logic_route': logic_route
        })
        
        return order_a_ticket, order_b_ticket
    
    def _calculate_fixed_sl(self, alert, sl_pips):
        """Calculate fixed SL price from pips"""
        if alert.direction == 'BUY':
            return alert.price - (sl_pips * self._get_pip_size(alert.symbol))
        else:
            return alert.price + (sl_pips * self._get_pip_size(alert.symbol))
    
    def _get_pip_value(self, symbol):
        """Get pip value for $10 SL calculation"""
        # Simplified (should query from service API)
        if 'JPY' in symbol:
            return 0.01
        return 0.0001
    
    def _get_pip_size(self, symbol):
        """Get pip size for price calculation"""
        return self._get_pip_value(symbol)
```

---

### **STEP 5: Implement MTF Processor** (Day 3)

**File:** `mtf_processor.py`

```python
class V3MTFProcessor:
    """
    Processes Multi-Timeframe 4-Pillar system
    """
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.config = plugin.config['mtf_config']
        self.pillars = self.config['pillars_only']  # ["15m", "1h", "4h", "1d"]
    
    def extract_4_pillar_trends(self, mtf_string: str) -> dict:
        """
        Extract only 4-pillar trends, ignore 1m/5m
        
        Input: "1,1,-1,1,1,1" (6 values: 1m,5m,15m,1H,4H,1D)
        Output: {"15m": -1, "1h": 1, "4h": 1, "1d": 1}
        """
        trends = [int(x) for x in mtf_string.split(',')]
        
        if len(trends) != 6:
            raise ValueError(f"Invalid MTF string: expected 6 values, got {len(trends)}")
        
        return {
            "15m": trends[2],  # Index 2
            "1h": trends[3],   # Index 3
            "4h": trends[4],   # Index 4
            "1d": trends[5]    # Index 5
        }
    
    async def update_trend_database(self, alert):
        """
        Update market_trends table with 4-pillar data
        """
        pillars = self.extract_4_pillar_trends(alert.mtf_trends)
        
        for tf, direction in pillars.items():
            await self.plugin.database.update_trend(
                symbol=alert.symbol,
                timeframe=tf,
                direction='bullish' if direction == 1 else 'bearish'
            )
        
        logger.info(f"✅ MTF 4-Pillar updated: {pillars}")
    
    async def validate_trend_alignment(self, alert) -> bool:
        """
        Check if signal aligns with current trends
        """
        # Extract current trends
        pillars = self.extract_4_pillar_trends(alert.mtf_trends)
        
        # For BUY: majority should be bullish
        # For SELL: majority should be bearish
        bullish_count = sum(1 for v in pillars.values() if v == 1)
        bearish_count = sum(1 for v in pillars.values() if v == -1)
        
        if alert.direction == 'BUY':
            return bullish_count >= 3  # At least 3/4 bullish
        else:
            return bearish_count >= 3  # At least 3/4 bearish
```

---

### **STEP 6: Main Plugin Class** (Day 3-4)

**File:** `plugin.py`

```python
from src.core.plugin_system.base_plugin import BaseLogicPlugin
from .signal_handlers import V3SignalHandlers
from .routing_logic import V3RoutingLogic
from .dual_order_manager import V3DualOrderManager
from .mtf_processor import V3MTFProcessor
from .position_sizer import V3PositionSizer

class CombinedV3Plugin(BaseLogicPlugin):
    def __init__(self, plugin_id, config, service_api):
        super().__init__(plugin_id, config, service_api)
        
        # Metadata
        self.metadata = {
            "version": "1.0.0",
            "name": "V3 Combined Logic",
            "signals": 12,
            "description": "12-signal system with dual orders and MTF 4-pillar"
        }
        
        # Initialize components
        self.signal_handlers = V3SignalHandlers(self)
        self.routing = V3RoutingLogic(self.config)
        self.dual_orders = V3DualOrderManager(self, service_api)
        self.mtf_processor = V3MTFProcessor(self)
        self.position_sizer = V3PositionSizer(self.config)
        
        # Initialize database
        self._initialize_v3_database()
        
        logger.info(f"✅ {self.plugin_id} initialized - 12 signals ready")
    
    async def on_signal_received(self, signal_data):
        """
        Main signal routing for V3
        """
        signal_type = signal_data.get('signal_type')
        
        # Route to appropriate handler
        handler_map = {
            'Institutional_Launchpad': self.signal_handlers.handle_institutional_launchpad,
            'Liquidity_Trap': self.signal_handlers.handle_liquidity_trap,
            'Momentum_Breakout': self.signal_handlers.handle_momentum_breakout,
            'Mitigation_Test': self.signal_handlers.handle_mitigation_test,
            'Golden_Pocket_Flip': self.signal_handlers.handle_golden_pocket_flip,
            'Volatility_Squeeze': self.signal_handlers.handle_volatility_squeeze,
            'Bullish_Exit': self.signal_handlers.handle_bullish_exit,
            'Bearish_Exit': self.signal_handlers.handle_bearish_exit,
            'Screener_Full_Bullish': self.signal_handlers.handle_screener_full,
            'Screener_Full_Bearish': self.signal_handlers.handle_screener_full,
            'Trend_Pulse': self.signal_handlers.handle_trend_pulse,
            'Sideways_Breakout': self.signal_handlers.handle_sideways_breakout
        }
        
        handler = handler_map.get(signal_type)
        if handler:
            return await handler(signal_data)
        
        logger.warning(f"⚠️ Unknown V3 signal type: {signal_type}")
        return None
    
    async def process_v3_entry(self, alert, signal_type):
        """
        Main entry processing pipeline
        """
        # 1. Determine routing
        logic_route = self.routing.determine_logic_route(alert, signal_type)
        logic_mult = self.routing.get_logic_multiplier(logic_route)
        
        # 2. Check trend (unless bypassed)
        if not self._should_bypass_trend(alert):
            if not await self.mtf_processor.validate_trend_alignment(alert):
                logger.info(f"❌ V3 Entry skipped: trend misalignment")
                return False
        
        # 3. Calculate lot size (4-step flow)
        final_lot = self.position_sizer.calculate_v3_lot_size(alert, logic_mult)
        
        # 4. Place dual orders
        order_a, order_b = await self.dual_orders.place_dual_orders_v3(
            alert, final_lot, logic_route
        )
        
        logger.info(f"✅ V3 Entry: {signal_type} → {logic_route}")
        return True
    
    def _should_bypass_trend(self, alert):
        """Check trend bypass rules"""
        bypass_config = self.config['trend_bypass']
        
        if alert.signal_source == 'entry_v3' and bypass_config['bypass_for_entry_v3']:
            return True
        
        return False
```

---

### **STEP 7: Shadow Mode Testing** (Day 4-7, 72 hours)

**Concept:** Run legacy V3 AND plugin V3 in parallel, compare every decision.

**Implementation in TradingEngine:**
```python
async def process_v3_alert(self, alert):
    results = {}
    
    # Run legacy V3
    if self.config['legacy_v3']['enabled']:
        legacy_result = await self._process_v3_legacy(alert)
        results['legacy'] = legacy_result
        
        # Execute legacy trade
        await self._execute_v3_trade(legacy_result)
    
    # Run plugin V3 (shadow mode - observe only)
    if self.config['plugins']['combined_v3']['shadow_mode']:
        plugin_result = await self.plugin_registry.route_alert(
            alert, 'combined_v3'
        )
        results['plugin'] = plugin_result
        
        # Compare decisions
        await self._compare_v3_results(results)
    
    return results

async def _compare_v3_results(self, results):
    """Compare legacy vs plugin V3 decisions"""
    legacy = results['legacy']
    plugin = results['plugin']
    
    mismatches = []
    
    # Compare routing
    if legacy.get('logic_route') != plugin.get('logic_route'):
        mismatches.append(f"Route: {legacy['logic_route']} vs {plugin['logic_route']}")
    
    # Compare lot sizes (allow 0.01 tolerance)
    if abs(legacy.get('lot_a', 0) - plugin.get('lot_a', 0)) > 0.01:
        mismatches.append(f"Lot A: {legacy['lot_a']} vs {plugin['lot_a']}")
    
    if abs(legacy.get('lot_b', 0) - plugin.get('lot_b', 0)) > 0.01:
        mismatches.append(f"Lot B: {legacy['lot_b']} vs {plugin['lot_b']}")
    
    # Compare SL prices
    if legacy.get('order_a_sl') != plugin.get('order_a_sl'):
        mismatches.append(f"Order A SL: {legacy['order_a_sl']} vs {plugin['order_a_sl']}")
    
    if mismatches:
        await self.multi_telegram.send_admin_alert(
            f"⚠️ V3 SHADOW MISMATCH\\n"
            f"Signal: {legacy['symbol']} {legacy['signal_type']}\\n"
            f"Issues: {', '.join(mismatches)}"
        )
        logger.error(f"Shadow mismatch: {mismatches}")
```

**Success Criteria:**
- [ ] 72 hours of continuous monitoring
- [ ] 100% decision parity (zero mismatches)
- [ ] Performance delta < 10%

---

### **STEP 8: Cutover to Plugin** (Day 7, Weekend)

**Timeline:**
- **Friday 18:00:** Database backup
- **Friday 18:10:** Disable `legacy_v3` in config
- **Friday 18:15:** Enable `combined_v3` plugin (`shadow_mode: false`)
- **Friday 18:20:** Send test alert, verify execution
- **Saturday-Sunday:** Monitor all live alerts

**Rollback Plan:**
```bash
# If issues detected
curl -X POST http://localhost:8000/admin/disable_plugin/combined_v3
curl -X POST http://localhost:8000/admin/enable_legacy_v3
```

---

## ✅ COMPLETION CRITERIA

- [ ] All 12 V3 signal handlers implemented
- [ ] 2-tier routing matrix working (signal + TF)
- [ ] Dual order system with hybrid SL operational
- [ ] MTF 4-pillar extraction correct
- [ ] 4-step position sizing validated
- [ ] Trend bypass logic for entry_v3 working
- [ ] Shadow mode: 72 hours, 100% parity
- [ ] Cutover successful with zero downtime
- [ ] Week 5 monitoring: zero regressions

---

**Phase 4 Status:** READY TO EXECUTE (after Phases 1-3 complete)
