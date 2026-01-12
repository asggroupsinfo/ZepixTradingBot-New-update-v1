# 🚦 V6 SIGNAL ROUTING MATRIX

**File:** `03_SIGNAL_ROUTING_MATRIX.md`  
**Date:** 2026-01-11 04:40 IST  
**Target File:** `src/core/trading_engine.py`

---

## 1. THE ROUTING METHOD

Replace `_route_v3_to_logic` with this:

```python
async def execute_v6_entry(self, alert: ZepixV6Alert):
    """
    Main Execution Hub for V6
    Routes to Dedicated Logic Classes based on Timeframe
    """
    
    # 1. Select Logic Handler
    logic_handler = self._get_logic_handler(alert.tf)
    
    # 2. ValidateFilters (ADX, Momentum, Trend)
    if not logic_handler.validate_entry(alert, self.trend_state):
        logger.info(f"🚫 {alert.tf}m Trade Filtered by Logic")
        return
        
    # 3. Calculate Lots
    final_lots = logic_handler.calculate_lots(self.base_risk, alert)
    
    # 4. Execute Hybrid Orders
    config = logic_handler.get_order_config()
    await self.order_manager.place_hybrid_orders(alert, final_lots, config)
```

---

## 2. THE HANDLER SELECTOR

```python
def _get_logic_handler(self, tf: str):
    """
    Maps Timeframe string to Logic Instance
    """
    if tf == "1":
        return self.logic_1m
    elif tf == "5":
        return self.logic_5m
    elif tf == "15":
        return self.logic_15m
    elif tf in ["60", "240", "1H", "4H"]:
        return self.logic_1h
    else:
        # Default fallback
        logger.warning(f"⚠️ Unknown TF {tf}, Using 15m Logic")
        return self.logic_15m
```

---

## 3. LOGIC INITIALIZATION

In `TradingEngine.__init__`:
```python
# Initialize V6 Logics
self.logic_1m = PriceActionLogic1M(self.config)
self.logic_5m = PriceActionLogic5M(self.config)
self.logic_15m = PriceActionLogic15M(self.config)
self.logic_1h = PriceActionLogic1H(self.config)
```

**STATUS: CODE READY**
