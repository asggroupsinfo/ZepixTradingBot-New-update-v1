# 05_PHASE_3_DETAILED_PLAN.md

**Phase:** 3 - Service API Layer  
**Duration:** Week 3 (5 days)  
**Dependencies:** Phase 1 & 2 complete  
**Status:** Not Started

---

## 🎯 PHASE OBJECTIVES

1. Create stateless service layer for core functionalities
2. Refactor managers to delegate to services
3. Provide secure API for plugins
4. Maintain backward compatibility

---

## 📋 SERVICE COMPONENTS

### **3.1: OrderExecutionService**
**Duration:** 1 day  
**File:** `src/services/order_execution_service.py`

**Responsibilities:**
- Place market orders
- Modify existing orders
- Close positions
- Query open orders (per-plugin)

**Key Methods:**
```python
class OrderExecutionService:
    def __init__(self, mt5_client, database):
        self.mt5 = mt5_client
        self.db = database
    
def place_order(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float = 0.0,
        tp_price: float = 0.0,
        comment: str = ""
    ) -> Optional[int]:
        """
        Places order with plugin tagging.
        Returns MT5 ticket or None.
        """
        # Tag comment with plugin
        full_comment = f"{plugin_id}|{comment}"
        
        # Place via MT5
        ticket = self.mt5.place_order(...)
        
        # Save to plugin DB
        self.db.save_order(plugin_id, ticket, ...)
        
        return ticket
```

**Testing:**
- [ ] Place order test (demo account)
- [ ] Plugin isolation test (Plugin A can't see Plugin B orders)
- [ ] Comment tagging verification

---

### **3.2: RiskManagementService**
**Duration:** 1 day  
**File:** `src/services/risk_management_service.py`

**Responsibilities:**
- Calculate safe lot sizes
- Check daily loss limits
- Validate trade parameters

**Key Methods:**
```python
class RiskManagementService:
    def calculate_lot_size(
        self,
        plugin_id: str,
        symbol: str,
        risk_percentage: float,
        stop_loss_pips: float,
        account_balance: float = None
    ) -> float:
        """
        Returns safe lot size based on:
        - Risk %
        - SL distance  
        - Account balance
        - Symbol pip value
        """
        if account_balance is None:
            account_balance = self.mt5.get_balance()
        
        # Get symbol config
        symbol_config = self.config["symbol_config"][symbol]
        pip_value = symbol_config["pip_value_per_std_lot"]
        
        # Risk in dollars
        risk_dollars = account_balance * (risk_percentage / 100)
        
        # Lot size calculation
        lot_size = risk_dollars / (stop_loss_pips * pip_value)
        
        # Apply limits
        max_lot = self.config["plugins"][plugin_id].get("max_lot_size", 1.0)
        lot_size = min(lot_size, max_lot)
        
        return round(lot_size, 2)
    
    def check_daily_limit(self, plugin_id: str) -> Dict:
        """Returns daily loss status"""
        stats = self.db.get_plugin_daily_stats(plugin_id)
        limit = self.config["plugins"][plugin_id]["daily_loss_limit"]
        
        return {
            "daily_loss": stats["loss"],
            "daily_limit": limit,
            "remaining": limit - stats["loss"],
            "can_trade": stats["loss"] < limit
        }
```

**Testing:**
- [ ] Lot size calculation accuracy
- [ ] Daily limit enforcement
- [ ] Multiple plugins independent limits

---

### **3.3: ProfitBookingService**
**Duration:** 1 day  
**File:** `src/services/profit_booking_service.py`

**Responsibilities:**
- Book partial profits
- Manage profit chains (TP1, TP2, TP3)
- Track profit booking history

**Key Methods:**
```python
class ProfitBookingService:
    def book_profit(
        self,
        plugin_id: str,
        order_id: int,
        percentage: float,
        reason: str = ""
    ) -> Dict:
        """
        Books partial profit.
        Returns profit in pips and dollars.
        """
        # Get order details
        order = self.db.get_order(plugin_id, order_id)
        
        # Calculate volume to close
        close_volume = order["lot_size"] * (percentage / 100)
        
        # Close partial
        result = self.mt5.close_position_partial(
            order_id, 
            close_volume
        )
        
        # Update database
        self.db.update_order_partial_close(...)
        
        return {
            "closed_volume": close_volume,
            "remaining_volume": order["lot_size"] - close_volume,
            "profit_pips": result["profit_pips"],
            "profit_dollars": result["profit_dollars"]
        }
```

---

### **3.4: TrendManagementService**
**Duration:** 1 day  
**File:** `src/services/trend_management_service.py`

**Responsibilities:**
- Provide trend analysis
- Multi-timeframe alignment
- Trend strength calculation

**Key Methods:**
```python
class TrendManagementService:
    def get_current_trend(
        self,
        symbol: str,
        timeframe: str
    ) -> Dict:
        """
        Returns trend analysis for symbol/timeframe.
        """
        # Delegate to existing TrendManager
        trend_data = self.trend_manager.get_trend(symbol, timeframe)
        
        return {
            "direction": trend_data["direction"],  # "BULLISH", "BEARISH", "NEUTRAL"
            "strength": trend_data["strength"],    # 0.0 - 1.0
            "since": trend_data["change_time"],
            "indicators": {
                "ma_slope": trend_data["ma_slope"],
                "rsi": trend_data["rsi"],
                "adx": trend_data["adx"]
            }
        }
```

---

### **3.5: ServiceAPI Facade**
**Duration:** 1 day  
**File:** `src/core/plugin_system/service_api.py` (update)

**Integrate all services:**
```python
class ServiceAPI:
    def __init__(self, plugin_id, config, managers):
        self.plugin_id = plugin_id
        
        # Initialize services
        self.orders = OrderExecutionService(managers.mt5, managers.db)
        self.risk = RiskManagementService(config, managers.mt5, managers.db)
        self.profit = ProfitBookingService(managers.mt5, managers.db)
        self.trend = TrendManagementService(managers.trend_manager)
    
    # Convenience methods
    def place_order(self, **kwargs):
        return self.orders.place_order(self.plugin_id, **kwargs)
    
    def calculate_lot(self, **kwargs):
        return self.risk.calculate_lot_size(self.plugin_id, **kwargs)
```

---

## 🔄 MANAGER REFACTORING

### **Update Existing Managers**

**Goal:** Managers delegate to services (backward compatible)

**Example: OrderManager**
```python
# BEFORE (Phase 2)
class OrderManager:
    def place_order(self, symbol, direction, lot_size, ...):
        ticket = self.mt5_client.place_order(...)
        self.db.save_order(...)
        return ticket

# AFTER (Phase 3)
class OrderManager:
    def __init__(self, ...):
        self.order_service = OrderExecutionService(self.mt5, self.db)
    
    def place_order(self, symbol, direction, lot_size, ...):
        # Delegate to service (with "core" plugin_id)
        return self.order_service.place_order(
            plugin_id="core",  # Core bot orders
            symbol=symbol,
            ...
        )
```

**Benefits:**
- Existing code continues to work
- Gradual migration possible
- Services are reusable

---

## 🧪 TESTING STRATEGY

### **Unit Tests**
```python
def test_order_service_isolation():
    """Plugins can only access their own orders"""
    service = OrderExecutionService(mt5, db)
    
    # Plugin A places order
    order_a = service.place_order("plugin_a", ...)
    
    # Plugin B tries to query Plugin A's orders
    orders_b = service.get_open_orders("plugin_b")
    
    assert order_a not in orders_b
```

### **Integration Tests**
- [ ] Place order via service → verify in MT5
- [ ] Calculate lot size → verify realistic
- [ ] Book profit → verify partial close works

---

## 📊 SUCCESS METRICS

| Metric | Target |
|---|---|
| Service Response Time | < 50ms |
| Plugin Isolation | 100% |
| Backward Compatibility | 100% |
| Test Coverage | > 90% |

---

## ✅ COMPLETION CRITERIA

- [ ] All 4 services implemented
- [ ] ServiceAPI updated and tested
- [ ] Managers refactored (backward compatible)
- [ ] Plugin can place orders via ServiceAPI
- [ ] Zero regressions in existing logic
