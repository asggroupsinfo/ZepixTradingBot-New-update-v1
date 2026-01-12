# V4 Forex Session Enhancement System - Project Brief

**Version:** 1.0  
**Created:** 2026-01-11  
**Target Bot:** Zepix Trading Bot v2.0 (Forex Edition)

---

## Executive Summary

This project adds **4 critical real-time features** to transform the Zepix Trading Bot into a Forex-optimized trading system with advanced session management, visual time tracking, and robust alert delivery.

### Core Features

1. **Real-Time IST Clock** - Fixed display showing current time in Asia/Kolkata timezone
2. **Real-Time Calendar** - Date and day display with auto-refresh
3. **Forex Session Timing System** - Dynamic session-based trading control with advance alerts
4. **Voice Alert System** - Multi-channel notification system that works even when phone is off

---

## Problem Statement

### Current Limitations
- ❌ No visual time reference for traders
- ❌ No session-based trading restrictions for Forex market
- ❌ Hard-coded session timings requiring code changes
- ❌ Alert delivery fails when phone is locked/off
- ❌ No advance warning before session transitions
- ❌ Manual symbol filtering during specific sessions

### Impact
- Traders miss optimal entry windows during specific Forex sessions
- Alert failures during critical market movements
- Time zone confusion leading to missed trades
- Inability to enforce session-specific trading rules

---

## Solution Overview

### Feature 1: Real-Time Clock System
**Purpose:** Display current IST time with fixed positioning in Telegram

**Key Components:**
- Timezone: `Asia/Kolkata` (IST)
- Display format: `HH:MM:SS IST`
- Update frequency: Every second
- Telegram integration: Pinned message or header display

**Technical Approach:**
- Use `pytz` for timezone conversion
- `asyncio.sleep()` loop for continuous updates
- Edit pinned message to avoid chat spam

---

### Feature 2: Real-Time Calendar Display
**Purpose:** Show current date and day alongside the clock

**Key Components:**
- Display format: `DD MMM YYYY (Day)`
- Example: `11 Jan 2026 (Saturday)`
- Combined with clock in single message
- Auto-updates at midnight IST

**Technical Approach:**
- `datetime` module with IST timezone
- Same message as clock (combined display)
- Scheduled midnight refresh

---

### Feature 3: Forex Session Timing System
**Purpose:** Enforce session-based trading with dynamic configuration

#### Session Structure (IST)
| Session | Start (IST) | End (IST) | Active Symbols | Characteristics |
|---------|-------------|-----------|----------------|-----------------|
| **Asian** | 05:30 | 14:30 | USDJPY, AUDUSD, EURJPY | Low volatility, range-bound |
| **London** | 13:00 | 22:00 | GBPUSD, EURUSD, GBPJPY | High liquidity, trend moves |
| **Overlap** | 18:00 | 20:30 | All major pairs | Highest volume period |
| **NY Late** | 22:00 | 02:00 | USDCAD, EURUSD | Consolidation phase |
| **Dead Zone** | 02:00 | 05:30 | None | No trading recommended |

#### Key Features
✅ **Dynamic Configuration** - All settings stored in `data/session_settings.json`  
✅ **Telegram Control** - Zero-typing button-based session editor  
✅ **Master Switch** - Global enable/disable for all session filtering  
✅ **Advance Alerts** - 30-minute warning before session starts  
✅ **Force Close** - Optional auto-close trades at session end  
✅ **Symbol Filtering** - Per-session allowed symbol control  

#### Telegram Menu Structure
```
📊 Session Manager Dashboard
├── 🔴 Master Switch: OFF
├── 🕐 Current Session: London
├── ✅ Allowed Symbols: GBPUSD, EURUSD (2/7)
└── [Edit Sessions] [Settings] [Back]

Session Edit Menu (Asian Session)
├── Symbol Toggle Buttons (ON/OFF state)
│   ├── [✅ USDJPY] [❌ EURUSD] [✅ AUDUSD]
├── Time Adjustment
│   ├── Start: 05:30 IST [−30m] [+30m]
│   ├── End: 14:30 IST [−30m] [+30m]
├── Notifications
│   ├── [✅ Start Alert (30m advance)]
│   ├── [❌ Force Close at End]
└── [Save] [Reset] [Back]
```

#### Session Configuration File (`data/session_settings.json`)
```json
{
  "master_switch": true,
  "sessions": {
    "asian": {
      "name": "Asian Session",
      "start_time": "05:30",
      "end_time": "14:30",
      "allowed_symbols": ["USDJPY", "AUDUSD", "EURJPY"],
      "advance_alert_enabled": true,
      "advance_alert_minutes": 30,
      "force_close_enabled": false
    },
    "london": { ... },
    "overlap": { ... },
    "ny_late": { ... }
  },
  "all_symbols": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "GBPJPY", "USDCAD"]
}
```

---

### Feature 4: Voice Alert System
**Purpose:** Ensure critical alerts are delivered even when phone is locked/off

#### Alert Types & Priority
| Priority | Type | Description | Delivery Channels |
|----------|------|-------------|-------------------|
| 🔴 **CRITICAL** | Emergency | System crashes, major losses | Voice + SMS + Text |
| 🟠 **HIGH** | Order Execution | Trade opened/closed | Voice + Text |
| 🟡 **MEDIUM** | SL/TP Hit | Stop loss or take profit triggered | Voice + Text |
| 🟢 **LOW** | Session Alert | 30-min advance warning | Text only |

#### Delivery Channels
1. **Telegram Voice Message** (Primary)
   - Text-to-Speech conversion
   - Auto-play on delivery
   - Bypasses phone lock screen

2. **Telegram Text + Sound** (Fallback)
   - High-priority notification sound
   - Rich text formatting
   - Clickable action buttons

3. **SMS** (Emergency only)
   - Used when Telegram fails
   - Critical alerts only
   - Via SMS gateway API

#### Voice Alert Queue System
```python
alert_queue = {
  "id": "uuid",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",
  "message": "Trade opened: BUY EURUSD 0.5 lots",
  "type": "ORDER_EXECUTION",
  "timestamp": "2026-01-11T22:00:00+05:30",
  "retry_count": 0,
  "max_retries": 3,
  "channels": ["voice", "text", "sms"],
  "status": "PENDING|SENT|FAILED"
}
```

#### Retry Mechanism
- **Retry intervals:** 10s, 30s, 60s (exponential backoff)
- **Max retries:** 3 attempts per channel
- **Channel rotation:** Voice → Text → SMS
- **Delivery confirmation:** Track read receipts

---

## Technical Architecture

### New Modules

#### 1. `src/modules/fixed_clock_system.py`
**Responsibilities:**
- IST time management
- Calendar formatting
- Telegram message pinning
- Auto-refresh scheduling

**Key Functions:**
```python
async def get_current_ist_time() -> str
async def format_clock_message() -> str
async def update_clock_display()
async def start_clock_loop()
```

---

#### 2. `src/modules/session_manager.py`
**Responsibilities:**
- Session configuration loading/saving
- Symbol filtering logic
- Session transition detection
- Time adjustment utilities

**Key Functions:**
```python
def load_session_config() -> dict
def save_session_config(config: dict)
def check_trade_allowed(symbol: str, current_time: datetime) -> bool
def get_current_session(current_time: datetime) -> str
def adjust_session_time(session: str, field: str, delta_minutes: int)
def check_session_transitions() -> dict
def get_session_status_text() -> str
```

---

#### 3. `src/modules/voice_alert_system.py`
**Responsibilities:**
- Alert queue management
- TTS voice message generation
- Multi-channel delivery
- Retry logic & delivery tracking

**Key Functions:**
```python
async def send_voice_alert(message: str, priority: str)
async def generate_voice_message(text: str) -> bytes
async def send_via_telegram_voice(message: str)
async def send_via_telegram_text(message: str)
async def send_via_sms(message: str)
async def process_alert_queue()
async def retry_failed_alerts()
```

---

#### 4. `src/telegram/session_menu_handler.py`
**Responsibilities:**
- Session Manager UI rendering
- Callback query handling
- JSON config updates
- Session edit workflows

**Key Functions:**
```python
async def show_session_dashboard(update, context)
async def show_session_edit_menu(update, context, session_name)
async def handle_symbol_toggle(update, context, session, symbol)
async def handle_time_adjustment(update, context, session, field, delta)
async def handle_master_switch(update, context)
async def handle_force_close_toggle(update, context, session)
```

---

### Integration Points

#### `src/main.py`
```python
# Initialize new systems
from modules.fixed_clock_system import start_clock_loop
from modules.session_manager import SessionManager
from modules.voice_alert_system import VoiceAlertSystem

# In main()
asyncio.create_task(start_clock_loop())
session_mgr = SessionManager()
voice_alerts = VoiceAlertSystem()
```

#### `src/trading_engine.py`
```python
# Before trade execution
if not session_mgr.check_trade_allowed(symbol, datetime.now()):
    await voice_alerts.send_alert(
        f"❌ Trade rejected: {symbol} not allowed in current session",
        priority="MEDIUM"
    )
    return False

# After successful trade
await voice_alerts.send_alert(
    f"✅ Trade opened: {action} {symbol} {lot_size} lots",
    priority="HIGH"
)
```

#### `src/telegram/telegram_bot.py`
```python
# Add new menu button
keyboard = [
    [InlineKeyboardButton("📊 Session Manager", callback_data="session_dashboard")],
    # ... existing buttons
]

# Register callback handler
application.add_handler(CallbackQueryHandler(session_menu_handler, pattern="^session_"))
```

---

## Development Phases

### Phase 1: Foundation Setup ✅
- [x] Create project structure
- [x] Document architecture
- [ ] Create `session_settings.json` schema
- [ ] Set up IST timezone utilities

### Phase 2: Clock & Calendar 🔄
- [ ] Implement `fixed_clock_system.py`
- [ ] Test pinned message updates
- [ ] Verify IST timezone accuracy
- [ ] Performance test (24-hour continuous run)

### Phase 3: Session Manager 🔄
- [ ] Implement `session_manager.py` core logic
- [ ] Create `session_settings.json` with default Forex sessions
- [ ] Implement `check_trade_allowed()` function
- [ ] Add session transition detection
- [ ] Test time adjustment logic

### Phase 4: Telegram UI 🔄
- [ ] Create Session Manager dashboard
- [ ] Implement session edit menu
- [ ] Add symbol toggle buttons
- [ ] Add time adjustment controls
- [ ] Test zero-typing workflow

### Phase 5: Voice Alert System 🔄
- [ ] Implement alert queue
- [ ] Integrate TTS library (gTTS or pyttsx3)
- [ ] Test voice message delivery
- [ ] Implement retry mechanism
- [ ] Add SMS gateway integration
- [ ] Test delivery with phone off

### Phase 6: Integration & Testing 🔄
- [ ] Integrate with `main.py`
- [ ] Integrate with `trading_engine.py`
- [ ] Test full workflow end-to-end
- [ ] Verify session-based trade filtering
- [ ] Test voice alerts during trades
- [ ] Performance benchmarking

### Phase 7: Documentation & Handover 🔄
- [ ] Update `FEATURES_SPECIFICATION.md`
- [ ] Create user guide for Session Manager
- [ ] Document voice alert configuration
- [ ] Create troubleshooting guide
- [ ] Final verification report

---

## Success Criteria

### Functional Requirements
✅ Clock displays correct IST time with ±1 second accuracy  
✅ Calendar auto-updates at midnight IST  
✅ Session filtering prevents trades outside allowed symbols  
✅ 30-minute advance alerts fire before session starts  
✅ Force close automatically closes trades at session end (when enabled)  
✅ Voice alerts deliver even with phone locked  
✅ SMS fallback works when Telegram fails  
✅ Zero-typing Telegram UI requires no text input  
✅ Session settings persist across bot restarts  
✅ Master switch globally disables all session filtering  

### Performance Requirements
✅ Clock updates every second without lag  
✅ Session checks complete in <10ms  
✅ Voice alert delivery within 5 seconds  
✅ Telegram UI responds to button clicks within 1 second  
✅ JSON config saves complete within 100ms  
✅ No memory leaks during 7-day continuous operation  

### Quality Requirements
✅ Zero errors during normal operation  
✅ 100% test coverage for core functions  
✅ All error cases handled gracefully  
✅ Comprehensive logging for debugging  
✅ Clear user feedback for all actions  

---

## Dependencies

### Python Libraries
```txt
python-telegram-bot>=20.0  # Telegram API
pytz>=2023.3               # Timezone handling
gTTS>=2.3.0                # Text-to-Speech for voice messages
asyncio                    # Async event loop (built-in)
datetime                   # Time utilities (built-in)
json                       # JSON parsing (built-in)
```

### External Services
- **Telegram Bot API** - For all bot interactions
- **SMS Gateway** (Optional) - Twilio, AWS SNS, or similar for SMS fallback

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_CHAT_ID=<your_chat_id>
SMS_GATEWAY_API_KEY=<optional_sms_key>
SMS_FROM_NUMBER=<optional_sms_sender>
```

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Voice alerts fail delivery | HIGH | MEDIUM | Multi-channel fallback + retry mechanism |
| Session time drift | MEDIUM | LOW | Use `pytz` for accurate timezone handling |
| JSON config corruption | MEDIUM | LOW | Atomic writes + backup before save |
| Telegram rate limits | MEDIUM | MEDIUM | Queue messages + respect rate limits |
| Phone always off/unreachable | HIGH | LOW | SMS fallback as ultimate delivery channel |
| Clock display spam | LOW | LOW | Edit existing message instead of new posts |

---

## Estimated Timeline

- **Phase 1 (Setup):** 0.5 days ✅ COMPLETE
- **Phase 2 (Clock):** 1 day
- **Phase 3 (Session Manager):** 2 days
- **Phase 4 (Telegram UI):** 2 days
- **Phase 5 (Voice Alerts):** 2 days
- **Phase 6 (Integration):** 1.5 days
- **Phase 7 (Documentation):** 1 day

**Total:** ~10 days (assuming single developer)

---

## Next Steps

1. ✅ Create `00_PROJECT_BRIEF.md`
2. 🔄 Create `01_IMPLEMENTATION_PLAN.md`
3. 🔄 Create `session_settings.json` schema
4. 🔄 Implement `fixed_clock_system.py`
5. 🔄 Implement `session_manager.py`
6. 🔄 Build Telegram UI
7. 🔄 Integrate voice alerts
8. 🔄 End-to-end testing

---

**Status:** Planning Phase Complete | Ready for Implementation  
**Owner:** Development Team  
**Review Date:** 2026-01-12
