# 06 - Menu System Documentation

## 📱 Complete Menu System

---

## 1. Menu Types

### Reply Keyboard (Physical Keyboard)
**Location**: Bottom of Telegram screen
**Type**: Native Telegram keyboard
**Behavior**: Auto-hides after button click (one_time_keyboard=True)

**Configuration**:
```python
reply_keyboard = {
    "keyboard": [
        [{"text": "📊 Dashboard"}, {"text": "⏸️ Pause/Resume"}],
        [{"text": "📈 Active Trades"}, {"text": "💰 Performance"}],
        # ... 18 buttons total in 2-column layout
    ],
    "resize_keyboard": True,
    "one_time_keyboard": True,  # Auto-hide
    "is_persistent": True,       # 4-dot toggle stays
    "input_field_placeholder": "⚏ Tap to Open Menu"
}
```

---

### Inline Keyboard (Message-attached)
**Location**: Attached to bot messages
**Type**: Callback buttons
**Behavior**: Stays with message, sends callback_data on click

**Example**:
```python
inline_keyboard = {
    "inline_keyboard": [
        [{"text": "View Details", "callback_data": "view_details"}],
        [{"text": "Confirm", "callback_data": "confirm_action"}]
    ]
}
```

---

## 2. Menu Hierarchyउत्कृष्ट!

```
MAIN MENU (Reply Keyboard)
    │
    ├─► 📊 Dashboard → Dashboard view (inline menu)
    │
    ├─► ⏸️ Pause/Resume → Toggle pause status
    │
    ├─► 📈 Active Trades → List active positions
    │
    ├─► 💰 Performance → Performance metrics
    │
    ├─► 💱 Trading → Trading submenu
    │       ├─► Simulation Mode
    │       ├─► View Trades
    │       └─► Signal Status
    │
    ├─► ⏱️ Timeframe → Timeframe config submenu
    │       ├─► Toggle System
    │       ├─► View Logic Settings
    │       └─► Reset Defaults
    │
    ├─► 🔄 Re-entry → Re-entry submenu (ReentryMenuHandler)
    │       ├─► TP Continuation (ON/OFF toggle)
    │       ├─► SL Hunt (ON/OFF toggle)
    │       ├─► Exit Continuation (ON/OFF toggle)
    │       ├─► View Status
    │       └─► Configure Parameters
    │
    ├─► 📍 Trends → Trend management submenu
    │       ├─► Trend Matrix (grid view)
    │       ├─► Set Trend (symbol → timeframe → trend)
    │       └─► Set Auto
    │
    ├─► 🛡️ Risk → Risk management submenu
    │       ├─► View Caps
    │       ├─► View Status
    │       ├─► Set Daily Cap
    │       ├─► Set Lifetime Cap
    │       ├─► Switch Tier (quick tier change)
    │       ├─► Lot Size Status
    │       └─► Reset Settings
    │
    ├─► ⚙️ SL System → SL system submenu
    │       ├─► View Status
    │       ├─► Change System (SL-1/SL-2)
    │       ├─► Symbol-Specific SL
    │       └─► Reset
    │
    ├─► 📦 Orders → Dual order status
    │
    ├─► 📈 Profit → Profit booking submenu (ProfitMenuHandler)
    │       ├─► Profit Status
    │       ├─► Active Chains
    │       ├─► Set Targets
    │       ├─► Set Multipliers
    │       ├─► Stop Chain
    │       └─► Configuration
    │
    ├─► ⚙️ Settings → Settings submenu
    │       └─► Chains Status
    │
    ├─► 🔬 Diagnostics → Diagnostics submenu
    │       ├─► Health Status
    │       ├─► Set Log Level
    │       ├─► Export Logs
    │       ├─► Error Stats
    │       └─► System Resources
    │
    ├─► ⚡ Fine-Tune → Fine-tune submenu (FineTuneMenuHandler)
    │       ├─► Profit Protection
    │       ├─► SL Reduction
    │       └─► Recovery Windows
    │
    ├─► 🆘 Help → Help text
    │
    ├─► 🔄 Refresh → Refresh menus
    │
    └─► 🚨 PANIC CLOSE → Panic close confirmation
```

---

## 3. Button Mapping (REPLY_MENU_MAP)

**File**: `src/menu/menu_constants.py`

```python
REPLY_MENU_MAP = {
    # Row 1
    "📊 Dashboard": "action_dashboard",
    "⏸️ Pause/Resume": "action_pause_resume",
    
    # Row 2
    "📈 Active Trades": "action_trades",
    "💰 Performance": "performance",
    
    # Row 3
    "💱 Trading": "trading",
    "⏱️ Timeframe": "menu_timeframe",
    
    # Row 4
    "🔄 Re-entry": "menu_reentry",
    "📍 Trends": "menu_trend",
    
    # Row 5
    "🛡️ Risk": "menu_risk",
    "⚙️ SL System": "menu_sl_system",
    
    # Row 6
    "📦 Orders": "orders",
    "📈 Profit": "menu_profit",
    
    # Row 7
    "⚙️ Settings": "settings",
    "🔬 Diagnostics": "menu_diagnostics",
    
    # Row 8
    "⚡ Fine-Tune": "menu_finetune",
    "🆘 Help": "action_help",
    
    # Row 9
    "🔄 Refresh": "refresh",
    "🚨 PANIC CLOSE": "action_panic_close"
}
```

**Processing**:
1. User clicks button (e.g., "🔄 Re-entry")
2. Telegram sends text message: "🔄 Re-entry"
3. Bot intercepts in `handle_text_message`
4. Looks up in REPLY_MENU_MAP: "🔄 Re-entry" → "menu_reentry"
5. Creates synthetic callback query
6. Calls `handle_callback_query("menu_reentry")`

---

## 4. Callback Query Routing

**File**: `src/clients/telegram_bot.py`

```python
def handle_callback_query(self, query):
    """Route callback to appropriate handler"""
    
    callback_data = query['data']
    
    # Menu routing
    if callback_data.startswith("menu_"):
        menu_type = callback_data.replace("menu_", "")
        
        if menu_type == "reentry":
            self.reentry_menu_handler.show_reentry_menu()
        elif menu_type == "profit":
            self.profit_menu_handler.show_profit_menu()
        elif menu_type == "finetune":
            self.fine_tune_menu_handler.show_finetune_menu()
        # ... etc
    
    # Action routing
    elif callback_data.startswith("action_"):
        action = callback_data.replace("action_", "")
        self._handle_action(action)
    
    # Command routing
    elif callback_data.startswith("cmd_"):
        # Parse: cmd_category_command_name
        parts = callback_data.split("_", 2)
        category = parts[1]
        command = parts[2]
        self.command_executor.execute(command)
    
    # Parameter routing
    elif callback_data.startswith("param_"):
        # Parameter selection for multi-param commands
        self._handle_param_selection(callback_data)
    
    # Confirmation routing
    elif callback_data.startswith("execute_"):
        # Execute confirmed command
        command = callback_data.replace("execute_", "")
        self.command_executor.execute_confirmed(command)
```

---

## 5. Parameter Collection System

### Multi-step Parameter Collection

**Example**: `/set_trend EURUSD 1h bullish`

```
Step 1: Select Command
    User clicks: "Set Trend"
    ↓
Step 2: Select Symbol
    Bot shows: [EURUSD] [GBPUSD] [XAUUSD] ...
    User clicks: [EURUSD]
    State stored: {'symbol': 'EURUSD'}
    ↓
Step 3: Select Timeframe
    Bot shows: [15m] [1h] [1d]
    User clicks: [1h]
    State stored: {'symbol': 'EURUSD', 'timeframe': '1h'}
    ↓
Step 4: Select Trend
    Bot shows: [BULLISH] [BEARISH] [NEUTRAL] [AUTO]
    User clicks: [BULLISH]
    State stored: {'symbol': 'EURUSD', 'timeframe': '1h', 'trend': 'BULLISH'}
    ↓
Step 5: Confirmation
    Bot shows: "Change EURUSD 1h to BULLISH? [✓ Confirm] [✗ Cancel]"
    User clicks: [✓ Confirm]
    ↓
Step 6: Execute
    Command executed: set_trend(symbol='EURUSD', timeframe='1h', trend='BULLISH')
```

**Implementation**:
```python
# State management
user_states = {}  # {user_id: {'command': ..., 'params': {...}}}

def handle_param_selection(callback_data, user_id):
    """Store parameter and check if all collected"""
    
    # Parse: param_type_command_value
    parts = callback_data.split("_")
    param_type = parts[1]
    command = parts[2]
    value = "_".join(parts[3:])
    
    # Get user state
    state = user_states.get(user_id, {})
    if 'params' not in state:
        state['params'] = {}
    
    # Store parameter
    state['params'][param_type] = value
    state['command'] = command
    user_states[user_id] = state
    
    # Check if all params collected
    required_params = COMMAND_PARAM_MAP[command]['params']
    collected_params = list(state['params'].keys())
    
    if set(required_params) == set(collected_params):
        # All collected, show confirmation
        show_confirmation(user_id, command, state['params'])
    else:
        # Show next parameter selection
        next_param = find_next_missing_param(required_params, collected_params)
        show_param_options(user_id, next_param)
```

---

## 6. Menu Managers

### MenuManager (Base)
**File**: `src/menu/menu_manager.py`

**Responsibilities**:
- Render menus
- Handle common menu operations
- State management
- Context tracking

---

### ReentryMenuHandler
**File**: `src/menu/reentry_menu_handler.py`

**Features**:
- Show re-entry status (TP Cont, SL Hunt, Exit Cont)
- Toggle switches for each system
- View detailed configuration
- Configure parameters (intervals, offsets, etc.)

**Menu Layout**:
```
📊 RE-ENTRY SYSTEM STATUS

🎯 TP CONTINUATION
  Status: ON ✅
  Cooldown: 30s
  Max Levels: 5

🛡 SL HUNT RECOVERY
  Status: ON ✅
  Max Attempts: 1
  Recovery: +1 pip

🔄 EXIT CONTINUATION
  Status: OFF ❌

[Toggle TP Cont] [Toggle SL Hunt] [Toggle Exit Cont]
[View Status] [Configure] [« Back]
```

---

### ProfitMenuHandler
**File**: `src/menu/profit_menu_handler.py`

**Features**:
- Show profit booking status
- List active chains
- Set profit targets (presets)
- Set chain multipliers
- Stop individual or all chains

---

### FineTuneMenuHandler
**File**: `src/menu/fine_tune_menu_handler.py`

**Features**:
- Profit Protection settings (conservative/balanced/aggressive)
- SL Reduction settings
- Recovery Window configuration

---

## 7. CommandExecutor

**File**: `src/menu/command_executor.py`

**Process**:
```python
def execute(self, command, params, user_id):
    """Execute a command with parameters"""
    
    # 1. Validate
    validation_result = validate_command(command, params)
    if not validation_result['valid']:
        return send_error(validation_result['error'])
    
    # 2. Get handler
    handler_name = COMMAND_PARAM_MAP[command]['handler']
    handler = getattr(self.bot, handler_name)
    
    # 3. Format parameters
    formatted_params = format_params(params, command)
    
    # 4. Execute
    try:
        result = handler(**formatted_params)
        send_success(f"✅ {command} executed successfully")
        return result
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        send_error(f"❌ Error: {e}")
        raise
```

---

## 8. Menu Button Formats

### Inline Button
```python
{
    "text": "Confirm",
    "callback_data": "execute_set_trend"
}
```

### Reply Keyboard Button
```python
{
    "text": "📊 Dashboard"
}
```

### URL Button (not used currently)
```python
{
    "text": "Documentation",
    "url": "https://docs.example.com"
}
```

---

## 9. Menu State Management

**Context System**:
```python
class MenuContext:
    def __init__(self):
        self.user_contexts = {}
    
    def set_context(self, user_id, context):
        """Store user context"""
        self.user_contexts[user_id] = context
    
    def get_context(self, user_id):
        """Get user context"""
        return self.user_contexts.get(user_id, {})
    
    def clear_context(self, user_id):
        """Clear user context"""
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
```

**Usage**:
```python
# Store state
context.set_context(user_id, {
    'waiting_for_input': 'custom_lot_size',
    'command': 'set_lot_size',
    'params': {'tier': '10000'}
})

# Retrieve state
user_context = context.get_context(user_id)
if user_context.get('waiting_for_input') == 'custom_lot_size':
    # Process custom input
    process_lot_size_input(user_message)
```

---

## 10. Menu Refresh Logic

**Auto-refresh triggers**:
- After command execution
- After toggle switches
- When configuration changes
- On /refresh command

**Implementation**:
```python
def refresh_menu(user_id, menu_type):
    """Refresh a specific menu"""
    
    if menu_type == 'reentry':
        reentry_menu_handler.show_reentry_menu(user_id)
    elif menu_type == 'profit':
        profit_menu_handler.show_profit_menu(user_id)
    # ... etc
```

---

## Menu System Files

| File | Purpose | Lines |
|------|---------|-------|
| `menu_manager.py` | Base menu manager | ~500 |
| `command_executor.py` | Command execution | ~800 |
| `command_mapping.py` | Command definitions | 334 |
| `menu_constants.py` | Constants & layouts | 381 |
| `reentry_menu_handler.py` | Re-entry menus | ~400 |
| `profit_menu_handler.py` | Profit menus | ~350 |
| `fine_tune_menu_handler.py` | Fine-tune menus | ~300 |

**Total**: ~3,000+ lines for complete menu system
