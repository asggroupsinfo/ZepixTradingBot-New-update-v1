# STICKY HEADER IMPLEMENTATION GUIDE

**Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Production-Ready Code Examples  
**Priority:** 🔴 HIGH (Required for Telegram 3-Bot UX)

---

## 🎯 PURPOSE

Implement **persistent menu headers** in Telegram so users always see control buttons, creating a unified 3-bot experience.

**User Experience:**
```
┌──────────────────────────────────┐
│  [🏠 Menu] [📊 Status] [⚙️ Settings] [📈 Analytics]  ← ALWAYS VISIBLE
├──────────────────────────────────┤
│  📢 Trade alerts appear here...   │
│  📊 Reports appear here...         │
│  🎛️ Responses appear here...      │
└──────────────────────────────────┘
```

---

## 🏗️ IMPLEMENTATION OPTIONS

### **Option 1: ReplyKeyboardMarkup (RecommendedHOME for Mobile)**

**Pros:** Always visible at bottom, native Telegram UI  
**Cons:** Takes screen space, limited customization

```python
from telegram import ReplyKeyboardMarkup, KeyboardButton

async def send_persistent_menu(bot, chat_id):
    """
    Create persistent menu that stays visible
    """
    keyboard = [
        [
            KeyboardButton("🏠 Menu"),
            KeyboardButton("📊 Status")
        ],
        [
            KeyboardButton("⚙️ Settings"),
            KeyboardButton("📈 Analytics")
        ]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,     # Fit to button size
        persistent=True,          # Telegram Bot API 7.0+ feature
        one_time_keyboard=False   # Don't hide after use
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text="🎛️ <b>Control Menu Active</b>\n\nUse buttons below to navigate.",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
```

---

### **Option 2: InlineKeyboardMarkup (Recommended for Desktop)**

**Pros:** Attached to specific messages, more flexible  
**Cons:** Scrolls away with message history

```python
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def send_inline_menu(bot, chat_id):
    """
    Create inline menu attached to message
    """
    keyboard = [
        [
            InlineKeyboardButton("🏠 Menu", callback_data='menu_home'),
            InlineKeyboardButton("📊 Status", callback_data='menu_status')
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='menu_settings'),
            InlineKeyboardButton("📈 Analytics", callback_data='menu_analytics')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send and PIN the message
    message = await bot.send_message(
        chat_id=chat_id,
        text="🎛️ <b>Control Panel</b>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    # Pin the menu message
    await bot.pin_chat_message(
        chat_id=chat_id,
        message_id=message.message_id,
        disable_notification=True  # Don't notify user
    )
```

---

### **Option 3: Hybrid Approach (RECOMMENDED)**

**Best of Both:** Reply keyboard for quick access + Pinned inline for advanced features

```python
class TelegramStickyHeaders:
    """
    Manages sticky headers for 3-bot system
    """
    
    def __init__(self, controller_bot, notification_bot, analytics_bot):
        self.controller = controller_bot
        self.notification = notification_bot
        self.analytics = analytics_bot
        
        self.pinned_messages = {}  # chat_id -> message_id
    
    async def setup_sticky_headers(self, chat_id):
        """
        Setup BOTH reply keyboard AND pinned inline menu
        """
        # STEP 1: Set persistent reply keyboard (bottom of screen)
        await self._setup_reply_keyboard(chat_id)
        
        # STEP 2: Send and pin advanced menu (top of chat)
        await self._setup_pinned_menu(chat_id)
        
        logger.info(f"✅ Sticky headers setup for chat {chat_id}")
    
    async def _setup_reply_keyboard(self, chat_id):
        """Primary quick-access buttons (always visible)"""
        keyboard = [
            [KeyboardButton("🏠 Menu"), KeyboardButton("📊 Status")],
            [KeyboardButton("⚙️ Settings"), KeyboardButton("📈 Analytics")]
        ]
        
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            persistent=True
        )
        
        await self.controller.send_message(
            chat_id=chat_id,
            text="🎛️ <b>Zepix Trading Bot - Control Panel Active</b>\n\n"
                 "Quick access buttons appear below ⬇️\n"
                 "Advanced menu is pinned at top ⬆️",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    async def _setup_pinned_menu(self, chat_id):
        """Advanced menu (pinned at top)"""
        keyboard = [
            [
                InlineKeyboardButton("🏠 Dashboard", callback_data='dash_home'),
                InlineKeyboardButton("📊 Live Stats", callback_data='dash_stats')
            ],
            [
                InlineKeyboardButton("🎛️ V3 Status", callback_data='plugin_v3'),
                InlineKeyboardButton("🎯 V6 Status", callback_data='plugin_v6')
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
                InlineKeyboardButton("📈 Reports", callback_data='reports')
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data='refresh'),
                InlineKeyboardButton("❌ Emergency Stop", callback_data='emergency_stop')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await self.controller.send_message(
            chat_id=chat_id,
            text=self._generate_dashboard_text(),
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        # Pin the message
        await self.controller.pin_chat_message(
            chat_id=chat_id,
            message_id=message.message_id,
            disable_notification=True
        )
        
        # Store message ID for updates
        self.pinned_messages[chat_id] = message.message_id
    
    async def update_pinned_dashboard(self, chat_id):
        """Update the pinned dashboard without re-pinning"""
        if chat_id not in self.pinned_messages:
            await self._setup_pinned_menu(chat_id)
            return
        
        message_id = self.pinned_messages[chat_id]
        
        # Regenerate keyboard (same structure)
        keyboard = [
            [
                InlineKeyboardButton("🏠 Dashboard", callback_data='dash_home'),
                InlineKeyboardButton("📊 Live Stats", callback_data='dash_stats')
            ],
            [
                InlineKeyboardButton("🎛️ V3 Status", callback_data='plugin_v3'),
                InlineKeyboardButton("🎯 V6 Status", callback_data='plugin_v6')
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
                InlineKeyboardButton("📈 Reports", callback_data='reports')
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data='refresh'),
                InlineKeyboardButton("❌ Emergency Stop", callback_data='emergency_stop')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Edit message (keeps pin)
        await self.controller.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=self._generate_dashboard_text(),
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    def _generate_dashboard_text(self) -> str:
        """Generate current dashboard status"""
        from main import trading_engine, plugin_registry
        
        # Get real-time stats
        v3_status = "🟢 Active" if plugin_registry.is_enabled('combined_v3') else "🔴 Disabled"
        v6_status = "🟢 Active" if any([
            plugin_registry.is_enabled('price_action_1m'),
            plugin_registry.is_enabled('price_action_5m'),
            plugin_registry.is_enabled('price_action_15m'),
            plugin_registry.is_enabled('price_action_1h')
        ]) else "🔴 Disabled"
        
        open_trades = trading_engine.get_open_positions_count()
        
        text = (
            "🎛️ <b>Zepix Trading Bot - Live Dashboard</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>System Status:</b> 🟢 Running\n"
            f"<b>V3 Combined:</b> {v3_status}\n"
            f"<b>V6 Price Action:</b> {v6_status}\n\n"
            f"📊 <b>Open Trades:</b> {open_trades}\n"
            f"⏰ <b>Last Update:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
            "Use buttons below for quick actions ⬇️"
        )
        
        return text
```

---

## 🎮 CALLBACK HANDLERS

```python
@controller_bot.callback_query_handler()
async def handle_inline_menu_callbacks(update, context):
    """Handle inline button clicks"""
    query = update.callback_query
    data = query.data
    
    # Acknowledge callback
    await query.answer()
    
    # Route based on callback data
    if data == 'dash_home':
        await show_dashboard_home(query)
    
    elif data == 'dash_stats':
        await show_live_statistics(query)
    
    elif data == 'plugin_v3':
        await show_v3_plugin_status(query)
    
    elif data == 'plugin_v6':
        await show_v6_plugin_status(query)
    
    elif data == 'settings':
        await show_settings_menu(query)
    
    elif data == 'reports':
        await show_reports_menu(query)
    
    elif data == 'refresh':
        # Refresh the pinned dashboard
        chat_id = query.message.chat.id
        await sticky_headers.update_pinned_dashboard(chat_id)
        await query.answer("✅ Dashboard refreshed")
    
    elif data == 'emergency_stop':
        await handle_emergency_stop(query)

# Example handler
async def show_dashboard_home(query):
    """Show main dashboard"""
    # Edit the message that was clicked
    await query.edit_message_text(
        text=sticky_headers._generate_dashboard_text(),
        parse_mode='HTML',
        reply_markup=query.message.reply_markup  # Keep same keyboard
    )
```

---

## 🧪 INTEGRATION WITH MULTI-TELEGRAM MANAGER

```python
class MultiTelegramManager:
    """Enhanced with sticky headers"""
    
    def __init__(self, config):
        # Original initialization
        self.controller_bot = Bot(token=config['telegram_controller_token'])
        self.notification_bot = Bot(token=config['telegram_notification_token'])
        self.analytics_bot = Bot(token=config['telegram_analytics_token'])
        
        # Sticky headers manager
        self.sticky_headers = TelegramStickyHeaders(
            self.controller_bot,
            self.notification_bot,
            self.analytics_bot
        )
    
    async def start(self):
        """Start telegram system with sticky headers"""
        # Setup sticky headers for admin chat
        chat_id = config['telegram_chat_id']
        await self.sticky_headers.setup_sticky_headers(chat_id)
        
        # Start rate limiters
        await self.controller_limiter.start()
        await self.notification_limiter.start()
        await self.analytics_limiter.start()
        
        logger.info("✅ Telegram system started with sticky headers")
    
    async def send_notification(self, chat_id, text, **kwargs):
        """
        Send notification WITHOUT disrupting sticky headers
        """
        # DON'T include reply_markup (preserve sticky keyboard)
        await self.notification_bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
            # No reply_markup = sticky keyboard remains
        )
```

---

## 📱 MOBILE vs DESKTOP OPTIMIZATION

### **Mobile-First Design**

```python
# Primary: Reply Keyboard (always visible on mobile)
# Secondary: Pinned menu (for advanced features)

keyboard_mobile = [
    [KeyboardButton("🏠"), KeyboardButton("📊")],
    [KeyboardButton("⚙️"), KeyboardButton("📈")]
]
```

### **Desktop-First Design**

```python
# Primary: Pinned inline menu (rich features)
# Secondary: Reply keyboard (quick shortcuts)

keyboard_desktop = [
    [
        InlineKeyboardButton("🏠 Dashboard", callback_data='home'),
        InlineKeyboardButton("📊 Live Stats", callback_data='stats'),
        InlineKeyboardButton("📈 Analytics", callback_data='analytics')
    ],
    [
        InlineKeyboardButton("🎛️ V3 Control", callback_data='v3'),
        InlineKeyboardButton("🎯 V6 Control", callback_data='v6')
    ]
]
```

---

## 🔄 AUTO-REFRESH PINNED DASHBOARD

```python
async def auto_refresh_dashboard():
    """Background task to keep dashboard updated"""
    while True:
        try:
            # Update every 30 seconds
            await asyncio.sleep(30)
            
            # Update pinned dashboard for all active chats
            for chat_id in active_chats:
                await sticky_headers.update_pinned_dashboard(chat_id)
            
        except Exception as e:
            logger.error(f"Dashboard auto-refresh error: {e}")
            await asyncio.sleep(60)
```

---

## ✅ COMPLETION CHECKLIST

- [x] ReplyKeyboardMarkup implementation (persistent buttons)
- [x] InlineKeyboardMarkup implementation (pinned menu)
- [x] Hybrid approach (recommended)
- [x] `TelegramStickyHeaders` class
- [x] Callback handlers for inline buttons
- [x] Integration with `MultiTelegramManager`
- [x] Auto-refresh mechanism
- [x] Mobile vs Desktop optimization
- [x] Complete code examples

**Status:** ✅ READY FOR IMPLEMENTATION
