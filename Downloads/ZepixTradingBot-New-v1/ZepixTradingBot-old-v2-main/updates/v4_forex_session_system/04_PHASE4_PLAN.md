# Phase 4 Implementation Plan: Telegram UI for Session Management

**Date:** 2026-01-11  
**Mode:** PLANNING → EXECUTION  
**Focus:** Zero-typing button-based interface for dynamic session control

---

## Objective

Create a Telegram inline keyboard interface for Session Manager with:
- Dashboard view (current session, master switch, allowed symbols)
- Session edit menu (5 sessions)
- Symbol toggle buttons (7 Forex pairs)  
- Time adjustment controls (±30 min)
- Force-close toggles
- **Zero typing required** - all interactions via buttons

---

## Proposed Changes

### 1. Create `src/telegram/session_menu_handler.py` (NEW)
**Purpose:** Handle all Session Manager UI interactions

**Methods to Implement:**
- `__init__(session_manager)` - Initialize with SessionManager instance
- `show_session_dashboard()` - Display main dashboard with status
- `show_session_edit_menu()` - List all 5 sessions to edit
- `show_session_details(session_id)` - Detailed edit screen for one session
- `handle_symbol_toggle()` - Toggle symbol ON/OFF
- `handle_time_adjustment()` - Adjust start/end times
- `handle_master_switch()` - Toggle global master switch
- `handle_force_close_toggle()` - Toggle force-close per session

**Callback Data Patterns:**
- `session_dashboard` - Show dashboard
- `session_edit_menu` - Show session list
- `session_edit_{session_id}` - Edit specific session
- `session_toggle_{session_id}_{symbol}` - Toggle symbol
- `session_time_{session_id}_{field}_{delta}` - Adjust time
- `session_toggle_master` - Toggle master switch
- `session_force_{session_id}` - Toggle force close

**UI Layout:**
```
📊 Session Manager Dashboard
━━━━━━━━━━━━━━━━━━━━━━━
🟢 Master Switch: ON
🕐 Current Session: London Session
✅ Allowed Symbols: GBPUSD, EURUSD, GBPJPY (3/7)

Buttons:
[🟢 Master: ON]
[📝 Edit Sessions]
[« Back]
```

**Edit Session Layout:**
```
Editing: London Session
━━━━━━━━━━━━━━━━━━━━━━━
📝 Description: European session...
⏰ Active: 13:00 - 22:00
📊 Allowed Symbols: 3/7

[✅ EURUSD] [✅ GBPUSD]
[❌ USDJPY] [✅ GBPJPY]
[❌ AUDUSD] [❌ EURJPY]
[❌ USDCAD]

[Start:] [13:00] [−30m] [+30m]
[End:]   [22:00] [−30m] [+30m]

[❌ Force Close at End]
[« Back]
```

---

### 2. Update `src/telegram/telegram_bot.py` (MODIFY)
**Changes:**
- Import `SessionMenuHandler`
- Initialize handler with `SessionManager` instance
- Add "Session Manager" button to main menu
- Register callback query handlers for all `session_*` patterns

**Code to Add:**
```python
from telegram.session_menu_handler import SessionMenuHandler
from modules.session_manager import SessionManager

# In initialization
session_mgr = SessionManager()
session_menu = SessionMenuHandler(session_mgr)

# Add button to main menu
keyboard.append([InlineKeyboardButton("⚙️ Session Manager", callback_data="session_dashboard")])

# Register handlers
application.add_handler(CallbackQueryHandler(session_menu.show_session_dashboard, pattern="^session_dashboard$"))
application.add_handler(CallbackQueryHandler(session_menu.show_session_edit_menu, pattern="^session_edit_menu$"))
application.add_handler(CallbackQueryHandler(session_menu.handle_symbol_toggle, pattern="^session_toggle_"))
application.add_handler(CallbackQueryHandler(session_menu.handle_time_adjustment, pattern="^session_time_"))
application.add_handler(CallbackQueryHandler(session_menu.handle_master_switch, pattern="^session_toggle_master$"))
application.add_handler(CallbackQueryHandler(session_menu.handle_force_close_toggle, pattern="^session_force_"))

# Handle session_edit_{session_id}
def session_edit_router(update, context):
    session_id = update.callback_query.data.split('_', 2)[2]
    return session_menu.show_session_details(update, context, session_id)

application.add_handler(CallbackQueryHandler(session_edit_router, pattern="^session_edit_"))
```

---

### 3. Create `tests/test_session_menu_handler.py` (NEW)
**Test Coverage:**
- Dashboard rendering
- Session list display
- Symbol toggle functionality
- Time adjustment
- Master switch toggle
- Force-close toggle
- Callback data parsing
- Button state updates

---

## Verification Plan

### Unit Tests
**File:** `tests/test_session_menu_handler.py`

**Test Cases:**
1. `test_dashboard_display()` - Verify dashboard text and buttons
2. `test_session_list()` - Verify all 5 sessions shown
3. `test_symbol_toggle()` - Toggle EURUSD ON → OFF → ON
4. `test_time_adjustment()` - Adjust start time +30, end time -30
5. `test_master_switch()` - Toggle ON → OFF → ON
6. `test_force_close_toggle()` - Toggle for each session
7. `test_callback_data_parsing()` - Parse all callback patterns
8. `test_button_update()` - Verify UI refreshes after changes

**Run Command:**
```bash
python -m pytest tests/test_session_menu_handler.py -v
```

**Target:** 100% test pass (all tests green)

---

### Integration Test (Manual)
**Prerequisite:** Bot running with Telegram integration

**Steps:**
1. Open Telegram bot
2. Click "Session Manager" button
3. Verify dashboard shows:
   - Current session (based on IST time)
   - Master switch state
   - Allowed symbols count
4. Click "Edit Sessions"
5. Select "London Session"
6. Toggle EURUSD OFF (✅ → ❌)
7. Verify button updates immediately
8. Click Start +30m
9. Verify time updates from 13:00 to 13:30
10. Toggle "Force Close" ON
11. Click Back twice to dashboard
12. Verify no errors, all buttons responsive

**Expected Result:** All clicks work, UI updates instantly, no typing required

---

### Browser Test (Optional)
Not applicable - Telegram UI only

---

## Dependencies

**New:**
None - uses existing `python-telegram-bot` library

**Existing:**
- `python-telegram-bot>=20.0`
- `src/modules/session_manager.py` (Phase 3)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Telegram API rate limits | UI freezes | Add 0.5s debounce between rapid clicks |
| Callback data too long | Telegram rejects | Keep patterns short (<64 chars) |
| Concurrent user edits | Config conflicts | Add file locking to session_manager |
| Button state desync | Wrong symbols shown | Reload config before each display |

---

## Success Criteria

- ✅ Dashboard displays current session accurately
- ✅ All 5 sessions editable
- ✅ All 7 symbols toggleable per session
- ✅ Time adjustments work (±30 min, midnight wrap)
- ✅ Master switch works globally
- ✅ Force-close toggles per session
- ✅ **100% button-based (zero typing)**
- ✅ UI responds within 1 second
- ✅ Config changes persist across restarts
- ✅ All unit tests passing (100%)

---

**Ready for user review and approval to proceed with implementation.**
