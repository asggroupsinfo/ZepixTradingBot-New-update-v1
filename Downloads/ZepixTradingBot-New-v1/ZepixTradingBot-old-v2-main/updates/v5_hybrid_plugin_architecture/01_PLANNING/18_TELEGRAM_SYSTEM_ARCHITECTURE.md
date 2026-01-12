# TELEGRAM SYSTEM ARCHITECTURE

**Version:** 2.0 (Complete Specification)  
**Date:** 2026-01-12  
**Status:** Production Documentation

---

## 📱 MULTI-TELEGRAM SYSTEM OVERVIEW

**Architecture:** 3 Telegram Bots + 1 Manager

**Bots:**
1. **Controller Bot** - System control & commands
2. **Notification Bot** - Trade alerts & signals  
3. **Analytics Bot** - Reports & statistics

**Manager:** `MultiTelegramManager` routes messages to appropriate bot

---

## 🤖 BOT CONFIGURATION

### **1. Controller Bot**

**Token:** `TELEGRAM_CONTROLLER_TOKEN`  
**Chat ID:** `TELEGRAM_CHAT_ID`  
**Purpose:** System control, manual interventions, emergency commands

**Handles:**
- All `/` slash commands
- Bot configuration
- Emergency controls
- System status queries
- Manual trade placement

---

### **2. Notification Bot**

**Token:** `TELEGRAM_NOTIFICATION_TOKEN`  
**Chat ID:** `TELEGRAM_CHAT_ID` (same user, different bot)  
**Purpose:** All trading-related notifications

**Handles:**
- Entry alerts (when trade placed)
- Exit alerts (when trade closed)
- Partial profit bookings
- SL/TP modifications
- Error alerts
- Daily summary

---

### **3. Analytics Bot**

**Token:** `TELEGRAM_ANALYTICS_TOKEN`  
**Chat ID:** `TELEGRAM_CHAT_ID` (same user, different bot)  
**Purpose:** Performance reports & analytics

**Handles:**
- Daily P&L reports
- Weekly performance summaries
- Plugin-wise statistics
- Win rate analysis
- Risk metrics

---

## 🎛️ MENU SYSTEM ARCHITECTURE

### **Main Menu (Reply Keyboard)**

```
┌─────────────────────────────────────┐
│  ZEPIX TRADING BOT v3.0             │
├─────────────────────────────────────┤
│  [📊 Status]     [💰 Trades]        │
│  [⚙️ Settings]   [📈 Analytics]     │
│  [🔔 Alerts]     [🛑 Emergency]     │
└─────────────────────────────────────┘
```

**Implementation:**
```python
from telegram import ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup([
    ['📊 Status', '💰 Trades'],
    ['⚙️ Settings', '📈 Analytics'],
    ['🔔 Alerts', '🛑 Emergency']
], resize_keyboard=True)

await context.bot.send_message(
    chat_id=chat_id,
    text="Main Menu:",
    reply_markup=main_menu
)
```

---

### **Status Submenu (Inline Keyboard)**

**Triggered by:** "📊 Status" button

```
Status Information:
Bot: 🟢 Active | Uptime: 3d 15h
Plugins: 5/5 Active
Open Trades: 7

───────────────────────
[🔄 Refresh] [📋 Details] [🏠 Main Menu]
```

**Implementation:**
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

status_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔄 Refresh", callback_data="status_refresh"),
        InlineKeyboardButton("📋 Details", callback_data="status_details")
    ],
    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
])
```

---

### **Trades Menu (Inline Keyboard)**

**Triggered by:** "💰 Trades" button

```
Open Positions (7):

1️⃣ XAUUSD BUY 0.10 | +$55.00
   Plugin: combined_v3 | Age: 2h 15m
   [Close] [Modify] [Book Profit]

2️⃣ XAUUSD SELL 0.05 | +$12.50
   Plugin: price_action_1m | Age: 15m
   [Close] [Modify] [Book Profit]

───────────────────────
[▶️ Next Page] [🏠 Main Menu]
```

**Callback Data Format:**
```
close_trade_145        # Close trade ID 145
modify_trade_145       # Modify SL/TP for trade 145
profit_trade_145_25    # Book 25% profit on trade 145
next_page_2            # Show page 2 of trades
```

---

### **Settings Menu**

```
⚙️ Bot Settings:

Current Configuration:
• Max Lot Size: 1.0
• Daily Loss Limit: $500
• Risk per Trade: 1.5%

───────────────────────
[🔌 Plugins] [⚡ Quick Settings]
[📝 Edit Config] [🏠 Main Menu]
```

---

### **Emergency Menu**

```
🛑 EMERGENCY CONTROLS

⚠️ WARNING: These actions are immediate!

[🔴 CLOSE ALL TRADES]
[⏸️ PAUSE BOT]
[▶️ RESUME BOT]
[🔄 RESTART PLUGINS]

───────────────────────
[❌ Cancel] [🏠 Main Menu]
```

**Confirmation Flow:**
```
User clicks: 🔴 CLOSE ALL TRADES
↓
Bot asks: "⚠️ Close ALL 7 open trades?
          Total P&L: +$125.50
          
          [✅ YES, CLOSE ALL] [❌ CANCEL]"
↓
User confirms
↓
Bot executes & reports: "✅ Closed 7 trades. Final P&L: +$125.50"
```

---

## 📨 NOTIFICATION SYSTEM

### **Entry Notification Format**

```
🟢 ENTRY ALERT | V3 Combined Logic

Symbol: XAUUSD
Direction: BUY
Entry Price: 2030.50

Order Details:
├─ Order A: 0.05 lots
│  SL: 2028.00 (Smart SL)
│  TP: 2035.00 (TP2)
├─ Order B: 0.05 lots
│  SL: 2029.50 (Fixed $10 SL)
│  TP: 2032.00 (TP1)

Signal: Institutional_Launchpad
Timeframe: 15m
Logic Route: LOGIC2 (1.0x)
Consensus: 8/9 (0.9x multiplier)

MT5 Tickets: #12345, #12346
Entry Time: 17:42:15
```

**Implementation:**
```python
async def send_entry_notification(trade_data):
    message = f"""
🟢 ENTRY ALERT | {trade_data['plugin_name']}

Symbol: {trade_data['symbol']}
Direction: {trade_data['direction']}
Entry Price: {trade_data['entry_price']}

Order Details:
├─ Order A: {trade_data['order_a_lot']} lots
│  SL: {trade_data['order_a_sl']}
│  TP: {trade_data['order_a_tp']}
├─ Order B: {trade_data['order_b_lot']} lots
│  SL: {trade_data['order_b_sl']}
│  TP: {trade_data['order_b_tp']}

Signal: {trade_data['signal_type']}
Timeframe: {trade_data['timeframe']}
Logic Route: {trade_data['logic_route']}

MT5 Tickets: #{trade_data['ticket_a']}, #{trade_data['ticket_b']}
Entry Time: {trade_data['timestamp']}
    """
    
    await notification_bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode='HTML'
    )
    
    # Voice alert if enabled
    if config.get('voice_alerts_enabled'):
        await send_voice_alert(trade_data)
```

---

### **Exit Notification Format**

```
🔴 EXIT ALERT | V3 Combined Logic

Symbol: XAUUSD
Direction: BUY → CLOSED

Entry: 2030.50 | Exit: 2036.00
Hold Time: 2h 15m

Results:
├─ Order A: CLOSED at TP2
│  Profit: +$75.00 (+7.5 pips)
├─ Order B: CLOSED at TP1
│  Profit: +$50.00 (+5.0 pips)

Total P&L: +$125.00 (+12.5 pips)
Commission: -$0.50
Net Profit: +$124.50

Reason: Both TPs Hit
Close Time: 19:57:30
```

---

### **Partial Profit Booking Notification**

```
💰 PROFIT BOOKED | V3 Combined Logic

Symbol: XAUUSD BUY
Position: #12345

Booking Details:
• Closed: 25% (0.025 lots)
• Remaining: 75% (0.075 lots)

P&L:
• This Booking: +$25.00 (+2.5 pips)
• Total Position: +$100.00 (+10.0 pips)

Action: TP1 Hit
Next Target: TP2 at 2035.00
```

---

### **Error Notification Format**

```
❌ ERROR ALERT | System

Error Type: MT5 Connection Lost
Severity: HIGH
Time: 18:30:45

Details:
MT5 terminal disconnected. Attempting reconnection...

Status: Retry 1/3
Next Retry: 30 seconds

📌 Manual Action Required if persists.
```

---

## 🔊 VOICE ALERT SYSTEM

### **Voice Alert Triggers:**
- Trade entry (configurable)
- Trade exit (configurable)
- TP levels hit
- SL hit
- Critical errors
- Daily loss limit reached

### **Voice Message Format:**

**Entry:**
```
"New BUY trade on Gold at 2030.50. Signal: Institutional Launchpad."
```

**TP Hit:**
```
"TP1 hit on Gold BUY. Profit: 50 dollars."
```

**SL Hit:**
```
"Stop loss hit on Gold BUY. Loss: 30 dollars."
```

### **Implementation:**
```python
from gtts import gTTS
import os

async def send_voice_alert(text, chat_id):
    # Generate voice
    tts = gTTS(text=text, lang='en', slow=False)
    voice_file = f"temp_voice_{int(time.time())}.mp3"
    tts.save(voice_file)
    
    # Send voice message
    with open(voice_file, 'rb') as voice:
        await bot.send_voice(
            chat_id=chat_id,
            voice=voice
        )
    
    # Cleanup
    os.remove(voice_file)
```

---

## 🎮 CALLBACK HANDLERS

### **Callback Data Router:**

```python
async def handle_callback(update, context):
    query = update.callback_query
    data = query.data
    
    # Route based on callback data
    if data.startswith('close_trade_'):
        trade_id = int(data.split('_')[2])
        await close_trade_handler(query, trade_id)
        
    elif data.startswith('modify_trade_'):
        trade_id = int(data.split('_')[2])
        await modify_trade_handler(query, trade_id)
        
    elif data.startswith('profit_trade_'):
        parts = data.split('_')
        trade_id = int(parts[2])
        percentage = int(parts[3])
        await book_profit_handler(query, trade_id, percentage)
        
    elif data == 'status_refresh':
        await refresh_status(query)
        
    elif data == 'main_menu':
        await show_main_menu(query)
    
    # Always answer callback to remove loading state
    await query.answer()
```

---

## 🔄 MESSAGE ROUTING LOGIC

### **MultiTelegramManager Implementation:**

```python
class MultiTelegramManager:
    def __init__(self):
        self.controller_bot = Bot(token=CONTROLLER_TOKEN)
        self.notification_bot = Bot(token=NOTIFICATION_TOKEN)
        self.analytics_bot = Bot(token=ANALYTICS_TOKEN)
    
    async def route_message(self, message_type, content):
        """Route message to appropriate bot"""
        
        if message_type in ['entry', 'exit', 'profit_booking', 'error']:
            # Send to Notification Bot
            await self.notification_bot.send_message(
                chat_id=CHAT_ID,
                text=content
            )
            
        elif message_type in ['daily_report', 'weekly_summary', 'analytics']:
            # Send to Analytics Bot
            await self.analytics_bot.send_message(
                chat_id=CHAT_ID,
                text=content
            )
            
        elif message_type == 'command_response':
            # Send to Controller Bot
            await self.controller_bot.send_message(
                chat_id=CHAT_ID,
                text=content
            )
    
    async def broadcast(self, message):
        """Send to ALL bots (critical alerts)"""
        for bot in [self.controller_bot, self.notification_bot, self.analytics_bot]:
            await bot.send_message(chat_id=CHAT_ID, text=message)
```

---

## 🎯 COMMAND LIST

### **Controller Bot Commands:**

```
/start - Initialize bot
/status - Show current status
/trades - List open positions
/close <ID> - Close specific trade
/closeall - Close all positions
/pause - Pause bot
/resume - Resume bot
/enable <plugin> - Enable plugin
/disable <plugin> - Disable plugin
/config <plugin> - View plugin config
/daily - Daily summary
/help - Show all commands
```

---

## ✅ TELEGRAM SYSTEM CHECKLIST

- [ ] Multi-Telegram Manager implemented
- [ ] All 3 bots configured and tested
- [ ] Main menu working
- [ ] All submenus functional
- [ ] Callback handlers registered
- [ ] Entry notifications formatted
- [ ] Exit notifications formatted
- [ ] Voice alerts working
- [ ] Error notifications tested
- [ ] Message routing verified
- [ ] All commands working

**Status:** PRODUCTION READY
