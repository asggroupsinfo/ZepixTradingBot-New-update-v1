# 15_DEVELOPER_ONBOARDING.md

**Version:** 1.0  
**Date:** 2026-01-12  
**Audience:** New Developers

---

## 👋 WELCOME TO ZEPIX BOT DEVELOPMENT

This guide will help you understand the v5 Hybrid Architecture and start contributing.

---

## 📚 PREREQUISITES

**Required Skills:**
- Python 3.9+
- Async/await programming
- SQLite databases
- Basic MT5 knowledge
- Git version control

**Recommended Reading:**
- [Plugin Architecture Research](00_RESEARCH/07_PLUGIN_SYSTEM_DEEP_DIVE.md)
- [Service API Design](00_RESEARCH/06_SERVICE_API_DESIGN_RESEARCH.md)
- [Database Strategy](01_PLANNING/09_DATABASE_SCHEMA_DESIGNS.md)

---

## 🛠️ DEVELOPMENT ENVIRONMENT SETUP

### **Step 1: Clone Repository**
```bash
git clone https://github.com/your-org/zepix-bot.git
cd zepix-bot
```

### **Step 2: Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **Step 3: Configure Bot**
```bash
# Copy template
cp config/config.template.json config/config.json

# Edit with your credentials
nano config/config.json
```

### **Step 4: Setup MT5 Demo Account**
1. Download MT5 from broker
2. Open demo account
3. Copy login credentials to `config.json`

### **Step 5: Create Telegram Bots**
```
1. Open Telegram, find @BotFather
2. /newbot → Create bot
3. Copy token to config.json
4. Repeat for all 3 bots
```

### **Step 6: Run Bot**
```bash
python src/main.py
```

**Expected Output:**
```
✅ MT5 connected
✅ Database initialized
✅ Plugin registry loaded
✅ Plugin 'combined_v3' initialized
✅ Telegram bots started
🚀 Bot is running...
```

---

## 🏗️ ARCHITECTURE OVERVIEW

### **Project Structure**
```
zepix-bot/
├── src/
│   ├── core/
│   │   ├── trading_engine.py      # Main orchestrator
│   │   ├── plugin_system/         # Plugin framework
│   │   │   ├── base_plugin.py
│   │   │   ├── plugin_registry.py
│   │   │   └── service_api.py
│   ├── services/                   # Business logic services
│   │   ├── order_execution_service.py
│   │   ├── risk_management_service.py
│   │   ├── profit_booking_service.py
│   │   └── trend_management_service.py
│   ├── telegram/                   # Telegram bots
│   │   ├── multi_telegram_manager.py
│   │   ├── controller_bot.py
│   │   ├── notification_bot.py
│   │   └── analytics_bot.py
│   ├── logic_plugins/              # Trading strategies
│   │   ├── combined_v3/
│   │   │   ├── plugin.py
│   │   │   ├── entry_logic.py
│   │   │   ├── exit_logic.py
│   │   │   └── config.json
│   │   └── _template/              # Use this to create new plugins
│   └── utils/
├── config/
│   └── config.json
├── data/                           # Databases
│   ├── zepix_bot.db               # Central DB
│   └── zepix_combined_v3.db       # Plugin DB
├── logs/
├── tests/
└── updates/v5_hybrid_plugin_architecture/  # This documentation
```

---

## 🔌 CREATING YOUR FIRST PLUGIN

### **Step 1: Copy Template**
```bash
cp -r src/logic_plugins/_template src/logic_plugins/my_plugin
```

### **Step 2: Edit config.json**
```json
{
    "plugin_id": "my_plugin",
    "version": "1.0.0",
    "enabled": true,
    "metadata": {
        "name": "My Custom Strategy",
        "description": "Short description",
        "author": "Your Name"
    },
    "settings": {
        "max_lot_size": 0.5,
        "daily_loss_limit": 200.0,
        "supported_symbols": ["XAUUSD"]
    }
}
```

### **Step 3: Implement Logic**

**File:** `src/logic_plugins/my_plugin/plugin.py`

```python
from src.core.plugin_system.base_plugin import BaseLogicPlugin

class MyPlugin(BaseLogicPlugin):
    def __init__(self, plugin_id, config, service_api):
        super().__init__(plugin_id, config, service_api)
        
        # Your initialization code
        self.entry_threshold = 7  # Minimum consensus score
        
        logger.info(f"✅ {self.plugin_id} initialized")
    
    async def on_signal_received(self, signal):
        """
        Main entry point for TradingView alerts.
        
        Args:
            signal: Dict with keys:
                - symbol: str
                - signal_type: str
                - direction: str
                - consensus_score: int
                - sl_price: float
                - tp_price: float
                - timeframe: str
        
        Returns:
            bool: True if trade placed, False if skipped
        """
        # 1. Validate signal
        if not self._should_process(signal):
            return False
        
        # 2. Check trend
        trend = await self.service_api.trend.get_current_trend(
            symbol=signal["symbol"],
            timeframe=signal["timeframe"]
        )
        
        if not self._is_aligned(signal["direction"], trend):
            logger.info(f"Skip: Against trend")
            return False
        
        # 3. Calculate lot size
        lot_size = await self.service_api.risk.calculate_lot_size(
            symbol=signal["symbol"],
            risk_percentage=1.5,
            stop_loss_pips=self._calculate_sl_pips(signal)
        )
        
        # 4. Place order
        ticket = await self.service_api.orders.place_order(
            symbol=signal["symbol"],
            direction=signal["direction"],
            lot_size=lot_size,
            sl_price=signal["sl_price"],
            tp_price=signal["tp_price"],
            comment=f"{self.plugin_id}_entry"
        )
        
        # 5. Log to database
        self.database.save_trade({
            "ticket": ticket,
            "signal_data": signal
        })
        
        return True
    
    def _should_process(self, signal):
        """Your custom validation logic"""
        # Check if enabled
        if not self.enabled:
            return False
        
        # Check symbol
        if signal["symbol"] not in self.config["supported_symbols"]:
            return False
        
        # Check consensus score
        if signal.get("consensus_score", 0) < self.entry_threshold:
            return False
        
        return True
    
    def _is_aligned(self, direction, trend):
        """Check if signal aligns with trend"""
        if direction == "BUY" and trend["direction"] != "BULLISH":
            return False
        if direction == "SELL" and trend["direction"] != "BEARISH":
            return False
        return True
    
    def _calculate_sl_pips(self, signal):
        """Calculate stop loss in pips"""
        # Your custom SL calculation
        return abs(signal["entry_price"] - signal["sl_price"]) * 10
```

### **Step 4: Register Plugin**

**Add to:** `config/config.json`

```json
{
    "plugins": {
        "combined_v3": {...},
        "my_plugin": {
            "enabled": true,
            "max_lot_size": 0.5,
            "daily_loss_limit": 200.0
        }
    }
}
```

### **Step 5: Test Plugin**

```bash
# Run test script
python scripts/test_plugin.py my_plugin

# Or start bot and send test alert
python src/main.py
```

---

## 🧪 TESTING YOUR PLUGIN

### **Unit Tests**

**Create:** `tests/test_my_plugin.py`

```python
import pytest
from src.logic_plugins.my_plugin.plugin import MyPlugin

def test_plugin_initialization():
    """Test plugin loads correctly"""
    plugin = MyPlugin("my_plugin", config, service_api)
    assert plugin.plugin_id == "my_plugin"
    assert plugin.enabled == True

def test_signal_validation():
    """Test signal validation logic"""
    plugin = MyPlugin("my_plugin", config, service_api)
    
    # Valid signal
    signal = {
        "symbol": "XAUUSD",
        "consensus_score": 8
    }
    assert plugin._should_process(signal) == True
    
    # Invalid signal (low consensus)
    signal["consensus_score"] = 5
    assert plugin._should_process(signal) == False

@pytest.mark.asyncio
async def test_entry_logic():
    """Test complete entry flow"""
    plugin = MyPlugin("my_plugin", config, service_api)
    
    signal = {
        "symbol": "XAUUSD",
        "direction": "BUY",
        "consensus_score": 8,
        "sl_price": 2028.00,
        "tp_price": 2035.00
    }
    
    result = await plugin.on_signal_received(signal)
    assert result == True  # Trade placed
```

### **Run Tests**
```bash
pytest tests/test_my_plugin.py -v
```

---

## 📖 SERVICAPI REFERENCE

### **Available Services:**

#### **OrderExecutionService**
```python
# Place order
ticket = await self.service_api.orders.place_order(
    symbol="XAUUSD",
    direction="BUY",
    lot_size=0.10
)

# Get open orders
orders = await self.service_api.orders.get_open_orders(
    symbol="XAUUSD"
)

# Close position
await self.service_api.orders.close_position(
    order_id=ticket
)
```

#### **RiskManagementService**
```python
# Calculate lot size
lot = await self.service_api.risk.calculate_lot_size(
    symbol="XAUUSD",
    risk_percentage=1.5,
    stop_loss_pips=25.0
)

# Check daily limit
status = await self.service_api.risk.check_daily_limit()
if not status["can_trade"]:
    return  # Skip trading
```

#### **TrendManagementService**
```python
# Get current trend
trend = await self.service_api.trend.get_current_trend(
    symbol="XAUUSD",
    timeframe="15m"
)

print(trend["direction"])  # "BULLISH", "BEARISH", "NEUTRAL"
print(trend["strength"])   # 0.0 - 1.0
```

---

## 🚀 BEST PRACTICES

### **1. Always Use ServiceAPI**
❌ **Don't:** Direct MT5 access  
✅ **Do:** Use `service_api.orders.place_order()`

### **2. Handle Errors Gracefully**
```python
try:
    ticket = await self.service_api.orders.place_order(...)
except Exception as e:
    logger.error(f"Order placement failed: {e}")
    return False  # Don't crash entire bot
```

### **3. Log Meaningful Messages**
```python
logger.info(f"[{self.plugin_id}] Processing {signal['symbol']} signal")
logger.warning(f"Risk limit reached, skipping trade")
logger.error(f"Failed to place order: {error}")
```

### **4. Test Before Deploy**
- Write unit tests
- Test with demo account
- Verify in shadow mode (if available)

---

## 📝 CODE REVIEW PROCESS

1. **Fork** repository
2. **Create branch:** `feature/my-plugin`
3. **Commit** with clear messages
4. **Push** to your fork
5. **Open PR** with description
6. **Address** review comments
7. **Merge** after approval

---

## 🆘 GETTING HELP

**Resources:**
- [Architecture Documentation](00_RESEARCH/)
- [API Specifications](01_PLANNING/10_API_SPECIFICATIONS.md)
- [Code Review Guidelines](01_PLANNING/13_CODE_REVIEW_GUIDELINES.md)

**Support Channels:**
- **Discord:** [Your Discord Server]
- **Email:** dev-support@zepix.com

---

## ✅ ONBOARDING CHECKLIST

- [ ] Dev environment setup
- [ ] Bot runs successfully
- [ ] Understand architecture
- [ ] Created first plugin
- [ ] Wrote unit tests
- [ ] Read code review guidelines
- [ ] Joined Discord

**Welcome to the team! 🎉**
