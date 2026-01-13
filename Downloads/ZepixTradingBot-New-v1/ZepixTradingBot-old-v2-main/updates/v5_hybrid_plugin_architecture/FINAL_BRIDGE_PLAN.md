# FINAL BRIDGE PLAN - Voice, Session, and Notification Integration

**Date:** 2026-01-13
**Status:** PLANNING COMPLETE
**Objective:** Connect Voice, Session, and Notification systems to V3/V6 plugins

---

## 1. FILE CREATION PLAN

### 1.1 Missing Files to Create

| File Path | Source Reference | Purpose |
|-----------|------------------|---------|
| `src/telegram/notification_system.py` | Doc 19 + DOCUMENTATION/VOICE_NOTIFICATION_SYSTEM_V3.md | Centralized notification router |
| `src/services/voice_alert_service.py` | Doc 11 + src/modules/voice_alert_system.py | Service wrapper for voice alerts |
| `src/core/database_manager.py` | Doc 23 + Doc 09 | Multi-DB routing manager |

### 1.2 File Content Specifications

#### A. `src/telegram/notification_system.py`

**Purpose:** Centralized notification router that accepts alerts from plugins and routes them to Telegram/Voice.

**Key Classes:**
- `NotificationRouter` - Routes notifications by priority
- `NotificationPriority` - Enum for CRITICAL/HIGH/MEDIUM/LOW/INFO

**Key Methods:**
- `send(notification_type, data, priority)` - Central dispatch
- `format_notification(type, data)` - Format message
- `route_to_voice(message, priority)` - Voice alert routing
- `route_to_telegram(message, priority)` - Telegram routing

**Integration Points:**
- Imports `VoiceAlertSystem` from `src/modules/voice_alert_system.py`
- Uses `TelegramManager` for message delivery
- Called by plugins via `ServiceAPI.notifications.send()`

#### B. `src/services/voice_alert_service.py`

**Purpose:** Service layer wrapper for VoiceAlertSystem. Provides clean API for plugins.

**Key Classes:**
- `VoiceAlertService` - Service wrapper

**Key Methods:**
- `announce_trade(symbol, direction, price, lot_size)` - Trade announcement
- `announce_sl_hit(symbol, loss_amount)` - SL hit alert
- `announce_tp_hit(symbol, profit_amount)` - TP hit alert
- `announce_session_change(session_name)` - Session change alert
- `send_alert(message, priority)` - Generic alert

**Integration Points:**
- Wraps `VoiceAlertSystem` from `src/modules/voice_alert_system.py`
- Wraps `WindowsAudioPlayer` from `src/modules/windows_audio_player.py`
- Exposed via `ServiceAPI.voice`

#### C. `src/core/database_manager.py`

**Purpose:** Multi-DB routing manager for V3 and V6 databases.

**Key Classes:**
- `DatabaseManager` - Central DB manager
- `DatabaseRouter` - Routes queries to correct DB

**Key Methods:**
- `get_v3_connection()` - Get V3 database connection
- `get_v6_connection()` - Get V6 database connection
- `route_query(plugin_id, query)` - Route query to correct DB
- `sync_databases()` - Sync data between DBs

**Integration Points:**
- Uses `src/database/v3_database.py` for V3 data
- Uses `src/database/v6_database.py` for V6 data
- Exposed via `ServiceAPI.database`

---

## 2. WIRING DIAGRAM

### 2.1 Infrastructure Wiring in `src/main.py`

**Current State:** Voice and Session systems NOT initialized.

**Required Changes:**

```python
# Line ~50: Add imports
from src.modules.voice_alert_system import VoiceAlertSystem, AlertPriority
from src.modules.session_manager import ForexSessionManager
from src.telegram.notification_system import NotificationRouter
from src.services.voice_alert_service import VoiceAlertService
from src.core.database_manager import DatabaseManager

# Line ~100: Initialize systems in startup
async def startup():
    # Existing code...
    
    # NEW: Initialize Voice Alert System
    voice_system = VoiceAlertSystem(
        bot=telegram_bot,
        chat_id=config.get('telegram_chat_id')
    )
    voice_service = VoiceAlertService(voice_system)
    
    # NEW: Initialize Session Manager
    session_manager = ForexSessionManager(
        config=config.get('session_config', {})
    )
    
    # NEW: Initialize Notification Router
    notification_router = NotificationRouter(
        telegram_manager=telegram_manager,
        voice_service=voice_service
    )
    
    # NEW: Initialize Database Manager
    database_manager = DatabaseManager(
        v3_path='data/zepix_combined_v3.db',
        v6_path='data/zepix_price_action.db'
    )
    
    # NEW: Pass to TradingEngine
    trading_engine = TradingEngine(
        config=config,
        mt5_client=mt5_client,
        telegram_bot=telegram_bot,
        voice_service=voice_service,        # NEW
        session_manager=session_manager,    # NEW
        notification_router=notification_router,  # NEW
        database_manager=database_manager   # NEW
    )
```

### 2.2 ServiceAPI Wiring in `src/core/plugin_system/service_api.py`

**Current State:** Only exposes OrderExecutionService, ProfitBookingService, RiskManagementService, TrendMonitorService.

**Required Changes:**

```python
# Line ~20: Add imports
from src.services.voice_alert_service import VoiceAlertService
from src.modules.session_manager import ForexSessionManager
from src.telegram.notification_system import NotificationRouter
from src.core.database_manager import DatabaseManager

# Line ~50: Add class-level service instances
class ServiceAPI:
    _order_service = None
    _profit_service = None
    _risk_service = None
    _trend_service = None
    _voice_service = None        # NEW
    _session_manager = None      # NEW
    _notification_router = None  # NEW
    _database_manager = None     # NEW
    _initialized = False

# Line ~90: Add initialization
def _init_services(self):
    # Existing code...
    
    # NEW: Initialize voice service
    if hasattr(self._engine, 'voice_service'):
        ServiceAPI._voice_service = self._engine.voice_service
    
    # NEW: Initialize session manager
    if hasattr(self._engine, 'session_manager'):
        ServiceAPI._session_manager = self._engine.session_manager
    
    # NEW: Initialize notification router
    if hasattr(self._engine, 'notification_router'):
        ServiceAPI._notification_router = self._engine.notification_router
    
    # NEW: Initialize database manager
    if hasattr(self._engine, 'database_manager'):
        ServiceAPI._database_manager = self._engine.database_manager

# Line ~130: Add properties
@property
def voice(self) -> VoiceAlertService:
    """Get VoiceAlertService instance."""
    return ServiceAPI._voice_service

@property
def sessions(self) -> ForexSessionManager:
    """Get ForexSessionManager instance."""
    return ServiceAPI._session_manager

@property
def notifications(self) -> NotificationRouter:
    """Get NotificationRouter instance."""
    return ServiceAPI._notification_router

@property
def database(self) -> DatabaseManager:
    """Get DatabaseManager instance."""
    return ServiceAPI._database_manager

# Line ~400: Add convenience methods
async def check_session_allowed(self, symbol: str) -> bool:
    """Check if symbol is allowed in current session."""
    if ServiceAPI._session_manager:
        return ServiceAPI._session_manager.is_symbol_allowed(symbol)
    return True  # Default allow if no session manager

async def announce_trade(self, symbol: str, direction: str, price: float, lot_size: float):
    """Announce trade via voice system."""
    if ServiceAPI._voice_service:
        await ServiceAPI._voice_service.announce_trade(symbol, direction, price, lot_size)

async def send_notification(self, notification_type: str, data: dict, priority: str = "MEDIUM"):
    """Send notification via notification router."""
    if ServiceAPI._notification_router:
        await ServiceAPI._notification_router.send(notification_type, data, priority)
```

---

## 3. PLUGIN INTEGRATION PLAN

### 3.1 Update `src/logic_plugins/combined_v3/plugin.py`

**Current State:** No session check, no voice alert.

**Required Changes:**

```python
# In process_signal() method, BEFORE trade execution:

async def process_signal(self, signal: Dict) -> Dict:
    symbol = signal.get('symbol')
    direction = signal.get('direction')
    
    # NEW: Session Check
    if not await self.service_api.check_session_allowed(symbol):
        self.logger.warning(f"Session blocked for {symbol}")
        return {"status": "blocked", "reason": "session_not_allowed"}
    
    # Existing trade logic...
    result = await self._execute_trade(signal)
    
    # NEW: Voice Alert on successful trade
    if result.get('status') == 'success':
        await self.service_api.announce_trade(
            symbol=symbol,
            direction=direction,
            price=result.get('entry_price'),
            lot_size=result.get('lot_size')
        )
        
        # NEW: Send notification
        await self.service_api.send_notification(
            notification_type="TRADE_EXECUTED",
            data={
                "symbol": symbol,
                "direction": direction,
                "price": result.get('entry_price'),
                "lot_size": result.get('lot_size'),
                "plugin": "combined_v3"
            },
            priority="HIGH"
        )
    
    return result
```

### 3.2 Update `src/logic_plugins/price_action_v6/plugin.py`

**Current State:** No session check, no voice alert.

**Required Changes:**

```python
# In process_signal() method, BEFORE trade execution:

async def process_signal(self, signal: Dict) -> Dict:
    symbol = signal.get('symbol')
    direction = signal.get('direction')
    
    # NEW: Session Check
    if not await self.service_api.check_session_allowed(symbol):
        self.logger.warning(f"Session blocked for {symbol}")
        return {"status": "blocked", "reason": "session_not_allowed"}
    
    # Existing trade logic...
    result = await self._execute_trade(signal)
    
    # NEW: Voice Alert on successful trade
    if result.get('status') == 'success':
        await self.service_api.announce_trade(
            symbol=symbol,
            direction=direction,
            price=result.get('entry_price'),
            lot_size=result.get('lot_size')
        )
        
        # NEW: Send notification
        await self.service_api.send_notification(
            notification_type="TRADE_EXECUTED",
            data={
                "symbol": symbol,
                "direction": direction,
                "price": result.get('entry_price'),
                "lot_size": result.get('lot_size'),
                "plugin": "price_action_v6"
            },
            priority="HIGH"
        )
    
    return result
```

---

## 4. VERIFICATION CHECKLIST

### 4.1 File Creation Verification

| File | Created | Has Required Classes | Has Required Methods |
|------|---------|---------------------|---------------------|
| `src/telegram/notification_system.py` | [ ] | [ ] | [ ] |
| `src/services/voice_alert_service.py` | [ ] | [ ] | [ ] |
| `src/core/database_manager.py` | [ ] | [ ] | [ ] |

### 4.2 Wiring Verification

| Component | Initialized in main.py | Exposed in ServiceAPI | Accessible by Plugins |
|-----------|------------------------|----------------------|----------------------|
| VoiceAlertService | [ ] | [ ] | [ ] |
| ForexSessionManager | [ ] | [ ] | [ ] |
| NotificationRouter | [ ] | [ ] | [ ] |
| DatabaseManager | [ ] | [ ] | [ ] |

### 4.3 Plugin Integration Verification

| Plugin | Session Check Added | Voice Alert Added | Notification Added |
|--------|--------------------|--------------------|-------------------|
| combined_v3 | [ ] | [ ] | [ ] |
| price_action_v6 | [ ] | [ ] | [ ] |

### 4.4 Agni Pariksha Verification

| Test | Expected Result | Actual Result |
|------|-----------------|---------------|
| Asian Session blocks EURUSD | REJECTED | [ ] |
| Asian Session allows USDJPY | ACCEPTED | [ ] |
| Trade triggers WindowsAudioPlayer | "Speaking: Trade Executed" | [ ] |
| Notification sent to Telegram | Message received | [ ] |
| V3 orders in zepix_combined_v3.db | Orders found | [ ] |
| V6 orders in zepix_price_action.db | Orders found | [ ] |

---

## 5. IMPLEMENTATION ORDER

1. **Create `src/services/voice_alert_service.py`** (30 min)
   - Wrapper for existing VoiceAlertSystem
   - Trade announcement methods

2. **Create `src/telegram/notification_system.py`** (1 hour)
   - NotificationRouter class
   - Priority-based routing
   - Voice integration

3. **Create `src/core/database_manager.py`** (1 hour)
   - Multi-DB routing
   - V3/V6 database connections

4. **Update `src/core/plugin_system/service_api.py`** (30 min)
   - Add voice, sessions, notifications, database properties
   - Add convenience methods

5. **Update `src/main.py`** (30 min)
   - Initialize all new systems
   - Pass to TradingEngine

6. **Update `src/logic_plugins/combined_v3/plugin.py`** (30 min)
   - Add session check
   - Add voice alert
   - Add notification

7. **Update `src/logic_plugins/price_action_v6/plugin.py`** (30 min)
   - Add session check
   - Add voice alert
   - Add notification

8. **Run Agni Pariksha** (30 min)
   - Verify all tests pass
   - Generate completion report

**Total Estimated Time:** 5 hours

---

## 6. ROLLBACK PLAN

If any step fails:

1. **File Creation Fails:** Delete created file, fix error, recreate
2. **Wiring Fails:** Revert main.py and service_api.py changes
3. **Plugin Update Fails:** Revert plugin changes, keep existing logic
4. **Agni Pariksha Fails:** Identify failing test, fix specific issue

---

**Plan Created:** 2026-01-13 19:15 UTC
**Status:** READY FOR IMPLEMENTATION
