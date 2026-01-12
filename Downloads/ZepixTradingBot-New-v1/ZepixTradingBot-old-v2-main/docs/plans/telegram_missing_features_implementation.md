# 🔧 Telegram Missing Features - Implementation Plan

**Date**: 2025-12-07  
**Target**: Complete remaining 15% of Telegram Integration  
**Complexity**: Medium  
**Estimated Time**: 4-6 hours

---

## 📋 FEATURES TO IMPLEMENT

### 1️⃣ Re-entry System Visual Toggles (Priority: HIGH)
**Current State**: Command-based (`/autonomous_mode on`)  
**Target State**: Button toggles with visual `[ON✅/OFF]` indicators

**Impact**: High (improves UX significantly)  
**Effort**: Medium (2-3 hours)

---

### 2️⃣ Profit Booking SL Mode Visual Selector (Priority: MEDIUM)
**Current State**: Parameter selection flow  
**Target State**: Direct visual buttons `[SL-1.1 Logic ✅]` `[SL-2.1 Fixed]`

**Impact**: Medium (simplifies selection)  
**Effort**: Low (1 hour)

---

### 3️⃣ Recovery Windows Edit Interface (Priority: MEDIUM)
**Current State**: Info display only  
**Target State**: Symbol-specific editing with ⬇⬆ buttons

**Impact**: Medium (completes Fine-Tune system)  
**Effort**: Medium (2-3 hours)

---

## 🎯 IMPLEMENTATION STRATEGY

### Phase 1: Re-entry System Visual Toggles

#### Step 1.1: Create Re-entry Submenu Handler
**File**: `src/menu/reentry_menu_handler.py` (NEW)

**Purpose**: Dedicated handler for Re-entry system menu with visual toggles

**Features**:
- Show current status of all re-entry features
- Visual toggle buttons for each feature
- Status display (ON✅/OFF❌)
- Integration with existing autonomous system

**Code Structure**:
```python
class ReentryMenuHandler:
    def __init__(self, bot, autonomous_manager):
        self.bot = bot
        self.autonomous_manager = autonomous_manager
        self.config = bot.config
    
    def show_reentry_menu(self, user_id, message_id=None):
        """Show Re-entry System menu with visual toggles"""
        # Get current statuses
        autonomous_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        
        autonomous_enabled = autonomous_config.get("enabled", False)
        tp_cont_enabled = autonomous_config.get("tp_continuation", {}).get("enabled", False)
        sl_hunt_enabled = autonomous_config.get("sl_hunt_recovery", {}).get("enabled", False)
        exit_cont_enabled = autonomous_config.get("exit_continuation", {}).get("enabled", False)
        
        # Create keyboard with visual indicators
        keyboard = [
            [self._toggle_button("🤖 Autonomous Mode", autonomous_enabled, "toggle_autonomous")],
            [self._toggle_button("🎯 TP Continuation", tp_cont_enabled, "toggle_tp_continuation")],
            [self._toggle_button("🛡 SL Hunt", sl_hunt_enabled, "toggle_sl_hunt")],
            [self._toggle_button("🔄 Exit Continuation", exit_cont_enabled, "toggle_exit_continuation")],
            [],
            [{"text": "📊 View Status", "callback_data": "reentry_view_status"}],
            [{"text": "⚙ Advanced Settings", "callback_data": "menu_reentry_advanced"}],
            [{"text": "🏠 Back to Main Menu", "callback_data": "menu_main"}]
        ]
        # ... message and display
    
    def _toggle_button(self, label, is_enabled, callback):
        """Create toggle button with visual indicator"""
        status = "ON ✅" if is_enabled else "OFF ❌"
        return {"text": f"{label} [{status}]", "callback_data": callback}
    
    def handle_toggle_callback(self, callback_data, user_id, message_id):
        """Handle toggle button clicks"""
        # Toggle config
        # Update display
        # Show confirmation
```

**Integration Points**:
- `menu_constants.py`: Update reentry category to use new handler
- `menu_callback_handler.py`: Route reentry callbacks to new handler
- `telegram_bot.py`: Initialize ReentryMenuHandler

---

#### Step 1.2: Implement Toggle Logic
**File**: `src/menu/reentry_menu_handler.py`

**Toggle Functions**:
```python
def toggle_autonomous_mode(self):
    """Toggle master autonomous mode"""
    current = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("enabled", False)
    new_value = not current
    
    # Update config
    self.config.update_nested("re_entry_config.autonomous_config.enabled", new_value)
    
    # If disabling, disable all sub-features
    if not new_value:
        self.config.update_nested("re_entry_config.autonomous_config.tp_continuation.enabled", False)
        self.config.update_nested("re_entry_config.autonomous_config.sl_hunt_recovery.enabled", False)
        self.config.update_nested("re_entry_config.autonomous_config.exit_continuation.enabled", False)
    
    # Save config
    self.config.save()
    
    return new_value

def toggle_tp_continuation(self):
    """Toggle TP Continuation feature"""
    current = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("tp_continuation", {}).get("enabled", False)
    new_value = not current
    
    self.config.update_nested("re_entry_config.autonomous_config.tp_continuation.enabled", new_value)
    self.config.save()
    
    return new_value

# Similar for sl_hunt and exit_continuation
```

---

#### Step 1.3: Update Menu Navigation
**File**: `src/clients/menu_callback_handler.py`

**Add Routes**:
```python
def handle_menu_callback(self, callback_data, user_id, message_id):
    # Existing code...
    
    # Re-entry menu
    elif callback_data == "menu_reentry":
        return self._handle_reentry_menu(user_id, message_id)
    
    # Re-entry toggles
    elif callback_data.startswith("toggle_"):
        return self._handle_reentry_toggle(callback_data, user_id, message_id)

def _handle_reentry_menu(self, user_id, message_id):
    """Show Re-entry menu"""
    if not self.reentry_handler and hasattr(self.bot, 'reentry_menu_handler'):
        self.reentry_handler = self.bot.reentry_menu_handler
    
    if self.reentry_handler:
        self.reentry_handler.show_reentry_menu(user_id, message_id)
        return True
    return False
```

---

### Phase 2: Profit Booking SL Mode Visual Selector

#### Step 2.1: Create Profit Booking Menu Handler
**File**: `src/menu/profit_booking_menu_handler.py` (NEW)

**Simple Implementation**:
```python
class ProfitBookingMenuHandler:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
    
    def show_profit_booking_menu(self, user_id, message_id=None):
        """Show Profit Booking menu with visual SL mode selector"""
        profit_config = self.config.get("profit_booking_config", {})
        current_mode = profit_config.get("sl_system", "SL-1.1")
        
        # SL Mode buttons
        sl_11_indicator = "✅" if current_mode == "SL-1.1" else ""
        sl_21_indicator = "✅" if current_mode == "SL-2.1" else ""
        
        keyboard = [
            [{"text": "🛡 Profit Protection", "callback_data": "action_profit_protection"}],
            [{"text": "📊 Active Chains", "callback_data": "cmd_profit_profit_chains"}],
            [{"text": "💎 SL Hunt Status", "callback_data": "profit_sl_hunt_status"}],
            [],
            [{"text": "⚙ SL MODE", "callback_data": "noop"}],  # Header
            [
                {"text": f"SL-1.1 (Logic) {sl_11_indicator}", "callback_data": "profit_sl_mode_11"},
                {"text": f"SL-2.1 (Fixed) {sl_21_indicator}", "callback_data": "profit_sl_mode_21"}
            ],
            [],
            [{"text": "📈 View Config", "callback_data": "cmd_profit_profit_config"}],
            [{"text": "🏠 Back to Main Menu", "callback_data": "menu_main"}]
        ]
        
        message = (
            "📈 <b>PROFIT BOOKING</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Current SL Mode:</b> {current_mode}\n\n"
            "Select an option:\n"
        )
        
        # Send/edit message
        if message_id:
            self.bot.edit_message(message, message_id, {"inline_keyboard": keyboard}, parse_mode="HTML")
        else:
            self.bot.send_message_with_keyboard(message, {"inline_keyboard": keyboard}, parse_mode="HTML")
    
    def handle_sl_mode_change(self, mode, user_id, message_id):
        """Handle SL mode change"""
        self.config.update_nested("profit_booking_config.sl_system", mode)
        self.config.save()
        
        # Show confirmation
        self.bot.send_message(f"✅ Profit SL Mode changed to {mode}")
        
        # Refresh menu
        self.show_profit_booking_menu(user_id, message_id)
```

**Integration**:
- Update `menu_callback_handler.py` to route `menu_profit` to this handler
- Add callback routing for `profit_sl_mode_11` and `profit_sl_mode_21`

---

### Phase 3: Recovery Windows Edit Interface

#### Step 3.1: Extend Fine-Tune Menu Handler
**File**: `src/menu/fine_tune_menu_handler.py`

**Add Edit Interface**:
```python
def show_recovery_windows_edit(self, user_id: int, page: int = 0, message_id: Optional[int] = None):
    """
    Show recovery windows with edit capability (similar to adaptive symbol settings)
    """
    # Get recovery windows from RecoveryWindowMonitor
    recovery_windows = self._get_recovery_windows()
    
    # Pagination
    symbols_per_page = 6
    all_symbols = sorted(recovery_windows.keys())
    start_idx = page * symbols_per_page
    end_idx = start_idx + symbols_per_page
    symbols_page = all_symbols[start_idx:end_idx]
    
    keyboard = []
    
    # Symbol adjustment buttons (similar to SL Reduction)
    for symbol in symbols_page:
        window_min = recovery_windows[symbol]
        
        keyboard.append([
            self._btn("⬇", f"rw_dec_{symbol}"),
            self._btn(f"{symbol}: {window_min}m", f"rw_info_{symbol}"),
            self._btn("⬆", f"rw_inc_{symbol}")
        ])
    
    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(self._btn("⬅ Previous", f"rw_page_{page-1}"))
    if end_idx < len(all_symbols):
        nav_buttons.append(self._btn("➡ Next", f"rw_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Additional options
    keyboard.append([self._btn("📖 Window Guide", "rw_guide")])
    keyboard.append([self._btn("🏠 Back", "menu_fine_tune")])
    
    message = (
        "🔍 <b>RECOVERY WINDOWS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Page {page + 1}</b>\n\n"
        "Adjust maximum wait time for SL Hunt recovery per symbol.\n\n"
        "<b>Range:</b> 5 - 60 minutes\n"
        "<b>⬇</b> Decrease by 5 min\n"
        "<b>⬆</b> Increase by 5 min\n"
    )
    
    self._send_or_edit_message(message, {"inline_keyboard": keyboard}, message_id)

def _get_recovery_windows(self):
    """Get recovery windows from RecoveryWindowMonitor or config"""
    # Check if RecoveryWindowMonitor has symbol_windows
    if hasattr(self.bot, 'autonomous_system_manager'):
        asm = self.bot.autonomous_system_manager
        if hasattr(asm, 'recovery_monitor') and asm.recovery_monitor:
            monitor = asm.recovery_monitor
            if hasattr(monitor, 'symbol_windows'):
                return monitor.symbol_windows.copy()
    
    # Fallback to default windows
    return {
        "XAUUSD": 15, "BTCUSD": 12, "XAGUSD": 18,
        "GBPJPY": 20, "GBPUSD": 22, "EURUSD": 30,
        "USDJPY": 28, "AUDUSD": 30, "NZDUSD": 30,
        # ... more symbols
    }

def handle_recovery_window_callback(self, callback_query: dict):
    """Handle recovery window adjustment callbacks"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    
    if data.startswith("rw_inc_") or data.startswith("rw_dec_"):
        action = "inc" if data.startswith("rw_inc_") else "dec"
        symbol = data.replace(f"rw_{action}_", "")
        
        # Get current window
        windows = self._get_recovery_windows()
        current = windows.get(symbol, 30)
        
        # Adjust by 5 minutes
        new_window = current + 5 if action == "inc" else current - 5
        
        # Validate range (5-60 minutes)
        if 5 <= new_window <= 60:
            self._update_recovery_window(symbol, new_window)
            self.bot.answer_callback_query(
                callback_query.id,
                text=f"{symbol}: {current}m → {new_window}m"
            )
            # Refresh menu
            page = int(data.split("_")[-1]) if "_page_" in data else 0
            self.show_recovery_windows_edit(user_id, page, message_id)
        else:
            self.bot.answer_callback_query(
                callback_query.id,
                text=f"❌ Range limit: 5-60 minutes",
                show_alert=True
            )
    
    elif data.startswith("rw_page_"):
        page = int(data.replace("rw_page_", ""))
        self.show_recovery_windows_edit(user_id, page, message_id)
    
    elif data == "rw_guide":
        self.show_recovery_window_guide(user_id, message_id)

def _update_recovery_window(self, symbol, new_window):
    """Update recovery window in monitor and config"""
    # Update in RecoveryWindowMonitor
    if hasattr(self.bot, 'autonomous_system_manager'):
        asm = self.bot.autonomous_system_manager
        if hasattr(asm, 'recovery_monitor') and asm.recovery_monitor:
            monitor = asm.recovery_monitor
            if hasattr(monitor, 'update_symbol_window'):
                monitor.update_symbol_window(symbol, new_window)
    
    # Persist to config
    self.bot.config.update_nested(f"recovery_windows.{symbol}", new_window)
    self.bot.config.save()
```

---

#### Step 3.2: Add Method to RecoveryWindowMonitor
**File**: `src/managers/recovery_window_monitor.py`

**Add Update Method**:
```python
def update_symbol_window(self, symbol: str, new_window_minutes: int):
    """
    Update recovery window for a specific symbol
    
    Args:
        symbol: Trading symbol
        new_window_minutes: New window duration in minutes
    """
    if hasattr(self, 'symbol_windows'):
        self.symbol_windows[symbol] = new_window_minutes
    
    logger.info(f"✅ Recovery window updated: {symbol} → {new_window_minutes} minutes")
```

---

## 📁 FILE STRUCTURE

### New Files to Create:
1. `src/menu/reentry_menu_handler.py` (250 lines)
2. `src/menu/profit_booking_menu_handler.py` (150 lines)

### Files to Modify:
1. `src/menu/fine_tune_menu_handler.py` (+150 lines)
2. `src/clients/menu_callback_handler.py` (+50 lines)
3. `src/clients/telegram_bot.py` (+20 lines for initialization)
4. `src/managers/recovery_window_monitor.py` (+10 lines)
5. `src/menu/menu_constants.py` (minor updates)

---

## 🔗 INTEGRATION CHECKLIST

### Step 1: Initialize New Handlers
**File**: `src/clients/telegram_bot.py`

```python
def __init__(self, ...):
    # Existing code...
    
    # Initialize new menu handlers
    self.reentry_menu_handler = None
    self.profit_booking_menu_handler = None
    
    # Initialize after fine_tune_handler
    if hasattr(self, 'fine_tune_handler'):
        from src.menu.reentry_menu_handler import ReentryMenuHandler
        from src.menu.profit_booking_menu_handler import ProfitBookingMenuHandler
        
        self.reentry_menu_handler = ReentryMenuHandler(self, self.autonomous_system_manager)
        self.profit_booking_menu_handler = ProfitBookingMenuHandler(self)
```

### Step 2: Route Callbacks
**File**: `src/clients/menu_callback_handler.py`

```python
def handle_menu_callback(self, callback_data, user_id, message_id):
    # ... existing code ...
    
    # Re-entry menu
    elif callback_data == "menu_reentry":
        if self.bot.reentry_menu_handler:
            self.bot.reentry_menu_handler.show_reentry_menu(user_id, message_id)
            return True
    
    # Profit booking menu
    elif callback_data == "menu_profit":
        if self.bot.profit_booking_menu_handler:
            self.bot.profit_booking_menu_handler.show_profit_booking_menu(user_id, message_id)
            return True
    
    # Re-entry toggles
    elif callback_data.startswith("toggle_"):
        if self.bot.reentry_menu_handler:
            self.bot.reentry_menu_handler.handle_toggle_callback(callback_data, user_id, message_id)
            return True
    
    # Profit SL mode
    elif callback_data.startswith("profit_sl_mode_"):
        if self.bot.profit_booking_menu_handler:
            mode = "SL-1.1" if "11" in callback_data else "SL-2.1"
            self.bot.profit_booking_menu_handler.handle_sl_mode_change(mode, user_id, message_id)
            return True
    
    # Recovery windows
    elif callback_data.startswith("rw_"):
        if self.bot.fine_tune_handler:
            self.bot.fine_tune_handler.handle_recovery_window_callback(callback_query)
            return True
```

---

## 🧪 TESTING PLAN

### Test Case 1: Re-entry Menu Toggles
1. Navigate to Main Menu → Re-entry System
2. Verify all features show current ON/OFF status
3. Click Autonomous Mode toggle → should switch ON ↔ OFF
4. Click TP Continuation → should toggle independently
5. Disable Autonomous Mode → all sub-features should auto-disable
6. Verify config.json updates persist

### Test Case 2: Profit SL Mode Selector
1. Navigate to Main Menu → Profit Booking
2. Verify current mode shows (e.g., SL-1.1 ✅)
3. Click SL-2.1 button → mode should switch
4. Verify checkmark moves to SL-2.1
5. Check config.json updates

### Test Case 3: Recovery Windows Edit
1. Navigate to Fine-Tune → Recovery Windows
2. Verify symbol list with current minutes
3. Click ⬆ on XAUUSD → should increase by 5 minutes
4. Click ⬇ → should decrease by 5 minutes
5. Test range limits (5-60 minutes)
6. Verify RecoveryWindowMonitor updates
7. Check config persistence

---

## ⏱ IMPLEMENTATION TIMELINE

| Task | Duration | Dependencies |
|:-----|:---------|:------------|
| Create ReentryMenuHandler | 1.5 hours | None |
| Integrate Re-entry Menu | 0.5 hours | ReentryMenuHandler |
| Create ProfitBookingMenuHandler | 0.5 hours | None |
| Integrate Profit Menu | 0.5 hours | ProfitBookingMenuHandler |
| Extend Fine-Tune for Recovery Windows | 1.5 hours | None |
| Add RecoveryWindowMonitor update method | 0.25 hours | None |
| Integration & Routing | 0.5 hours | All above |
| Testing | 1 hour | All above |

**Total Estimated Time**: 5.75 hours

---

## 🎯 SUCCESS CRITERIA

✅ All three features implemented and working
✅ Zero-typing interface maintained
✅ Visual toggles work correctly
✅ Config persistence works
✅ No breaking changes to existing features
✅ Clean code with proper error handling
✅ Documentation updated

---

## 📝 POST-IMPLEMENTATION

### Documentation Updates:
1. Update `TELEGRAM_INTEGRATION.md` with new features
2. Add screenshots to documentation
3. Update user guide

### Config Schema:
Ensure config.json includes:
```json
{
  "recovery_windows": {
    "XAUUSD": 15,
    "EURUSD": 30,
    ...
  }
}
```

---

**Ready to Implement**: YES ✅  
**Breaking Changes**: NO ❌  
**Backward Compatible**: YES ✅
