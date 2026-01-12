# 06_SERVICE_API_DESIGN_RESEARCH.md

**Document Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Research Complete

---

## 🎯 OBJECTIVE

Design a secure, stateless Service API layer that allows plugins to safely interact with core bot functionality without direct access to internal managers.

---

## 🏗️ SERVICE LAYER ARCHITECTURE

### **Pattern:** Facade + Dependency Injection

```
┌─────────────────────────────────────────┐
│           PLUGIN LAYER                   │
│  (Plugin 1)  (Plugin 2)  (Plugin 3)     │
└──────────────┬───────────────────────────┘
               │ Safe, Controlled Interface
┌──────────────▼───────────────────────────┐
│         SERVICE API LAYER                 │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Order    │  │ Risk     │  │ Profit │ │
│  │ Service  │  │ Service  │  │ Service│ │
│  └──────────┘  └──────────┘  └────────┘ │
└──────────────┬───────────────────────────┘
               │ Internal Implementation
┌──────────────▼───────────────────────────┐
│         CORE BOT LAYER                    │
│  MT5Client, Managers, Database, etc.     │
└──────────────────────────────────────────┘
```

---

## 📡 SERVICE API COMPONENTS

### **1. OrderExecutionService**

**Purpose:** Place, modify, and close orders on behalf of plugins.

**Methods:**
```python
class OrderExecutionService:
    def place_order(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,  # "BUY" or "SELL"
        lot_size: float,
        sl_price: float = 0.0,
        tp_price: float = 0.0,
        comment: str = ""
    ) -> Optional[int]:  # Returns order_id or None
        """
        Places a market order.
        - Tags order with plugin_id
        - Saves to plugin-specific database
        - Returns MT5 ticket number
        """
        
    def close_position(
        self,
        plugin_id: str,
        order_id: int,
        partial_volume: float = 0.0  # 0 = full close
    ) -> bool:
        """Closes an open position"""
        
    def modify_position(
        self,
        plugin_id: str,
        order_id: int,
        new_sl: float = None,
        new_tp: float = None
    ) -> bool:
        """Modifies SL/TP of existing order"""
        
    def get_open_orders(self, plugin_id: str) -> List[Dict]:
        """Returns all open orders for this plugin"""
```

**Security:**
- Plugins can only see/modify their own orders
- Order comments tagged with `plugin_id` for tracking
- Validation: lot size limits, SL/TP reasonableness

---

### **2. RiskManagementService**

**Purpose:** Calculate safe lot sizes based on risk parameters.

**Methods:**
```python
class RiskManagementService:
    def calculate_lot_size(
        self,
        plugin_id: str,
        symbol: str,
        risk_percentage: float,  # 1.0 = 1%
        stop_loss_pips: float,
        account_balance: float = None  # If None, fetch current
    ) -> float:
        """
        Returns safe lot size based on:
        - Account balance
        - Risk %
        - SL distance
        - Symbol pip value
        """
        
    def check_daily_limit(
        self,
        plugin_id: str
    ) -> Dict:
        """
        Returns:
        {
            "daily_loss": 150.0,
            "daily_limit": 500.0,
            "remaining": 350.0,
            "can_trade": True
        }
        """
        
    def validate_trade_parameters(
        self,
        symbol: str,
        lot_size: float,
        sl_pips: float
    ) -> Dict:
        """
        Validates:
        - Lot size within broker limits
        - SL distance meets minimum
        - Symbol is tradeable
        """
```

---

### **3. ProfitBookingService**

**Purpose:** Manage partial TPs and profit booking chains.

**Methods:**
```python
class ProfitBookingService:
    def book_profit(
        self,
        plugin_id: str,
        order_id: int,
        percentage: float,  # 50.0 = 50% of position
        reason: str = ""  # "TP1", "TRAILING", etc.
    ) -> Dict:
        """
        Books partial profit:
        - Closes percentage of lot size
        - Updates database
        - Returns profit in pips and $
        """
        
    def create_profit_chain(
        self,
        plugin_id: str,
        base_order_id: int,
        levels: List[Dict]  # [{"pips": 50, "volume": 0.05}, ...]
    ) -> str:  # Returns chain_id
        """
        Sets up multi-level profit taking:
        - TP1 at +50 pips: close 0.05 lots
        - TP2 at +100 pips: close 0.03 lots
        - TP3 at +150 pips: close remaining
        """
        
    def get_chain_status(
        self,
        plugin_id: str,
        chain_id: str
    ) -> Dict:
        """Returns current state of profit chain"""
```

---

### **4. TrendManagementService**

**Purpose:** Provide trend analysis to plugins.

**Methods:**
```python
class TrendManagementService:
    def get_current_trend(
        self,
        symbol: str,
        timeframe: str  # "5m", "15m", "1h", "4h"
    ) -> Dict:
        """
        Returns:
        {
            "direction": "BULLISH",
            "strength": 0.85,  # 0.0 - 1.0
            "since": "2026-01-12 14:30:00",
            "indicators": {
                "ma_slope": "positive",
                "rsi": 65,
                "adx": 28
            }
        }
        """
        
    def get_mtf_alignment(
        self,
        symbol: str
    ) -> Dict:
        """
        Returns multi-timeframe trend alignment:
        {
            "5m": "BULLISH",
            "15m": "BULLISH",
            "1h": "NEUTRAL",
            "4h": "BEARISH",
            "alignment_score": 0.5  # 50% aligned
        }
        """
```

---

## 🔐 SECURITY & ISOLATION

### **Plugin Isolation Rules**

1. **Database Isolation**
   - Each plugin has its own SQLite database
   - Path: `data/zepix_{plugin_id}.db`
   - No cross-plugin queries allowed

2. **Order Isolation**
   - Plugins can only see orders they placed
   - MT5 comment field contains plugin_id
   - Query filter: `WHERE comment LIKE '{plugin_id}%'`

3. **Config Isolation**
   - Plugins have separate config sections
   - Cannot read other plugins' configs
   - Cannot modify global config

### **Permission Model**

```python
class ServiceAPI:
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self._validate_plugin_exists()
        
    def _check_permission(self, resource_id: str):
        """
        Ensures plugin can only access its own resources
        """
        if not resource_id.startswith(self.plugin_id):
            raise PermissionError(
                f"Plugin {self.plugin_id} cannot access {resource_id}"
            )
```

---

## 📊 STATE MANAGEMENT

### **Stateless Services**

All services are **stateless**:
- No instance variables (except config/dependencies)
- Accept `plugin_id` as first parameter
- Fetch state from database on every call
- No caching (initially; can optimize later)

**Why Stateless?**
- Thread-safe (multiple plugins calling simultaneously)
- Easier to test
- Simpler error recovery
- No memory leaks

### **State Storage**

```
Plugin State is stored in:
1. Plugin Database (data/zepix_{plugin_id}.db)
  - Open trades
  - Trade history
  - Performance stats
  
2. Main Database (data/zepix_bot.db)
  - Cross-plugin analytics
  - System-wide metrics
```

---

## 🛡️ ERROR HANDLING

### **Service Error Responses**

All services return structured responses:

**Success:**
```python
{
    "success": True,
    "data": {...},
    "message": "Order placed successfully"
}
```

**Failure:**
```python
{
    "success": False,
    "error_code": "INSUFFICIENT_MARGIN",
    "error_message": "Not enough margin for this trade",
    "details": {...}
}
```

### **Common Error Codes**

| Code | Meaning | Action |
|---|---|---|
| `INSUFFICIENT_MARGIN` | Not enough balance | Reduce lot size |
| `DAILY_LIMIT_REACHED` | Max daily loss hit | Stop trading |
| `INVALID_SYMBOL` | Symbol not configured | Check config |
| `PERMISSION_DENIED` | Accessing other plugin's data | Fix plugin code |
| `MT5_CONNECTION_LOST` | MT5 offline | Retry/alert |

---

## 🧪 TESTING STRATEGY

### **Unit Tests**
```python
def test_order_service_isolation():
    # Plugin A places order
    order_a = service.place_order(
        plugin_id="plugin_a",
        symbol="XAUUSD",
        direction="BUY",
        lot_size=0.01
    )
    
    # Plugin B tries to close Plugin A's order
    result = service.close_position(
        plugin_id="plugin_b",
        order_id=order_a
    )
    
    assert result["success"] == False
    assert result["error_code"] == "PERMISSION_DENIED"
```

### **Integration Tests**
- Test service calls with real MT5 connection (demo account)
- Verify database writes
- Check order tagging

---

## ✅ DECISION

**APPROVED:** Implement stateless, plugin-isolated Service API layer.

**Next Steps:**
1. Create `BaseService` abstract class
2. Implement each service
3. Create `ServiceAPI` facade class
4. Write comprehensive tests
