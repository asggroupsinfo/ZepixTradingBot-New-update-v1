# 04_PHASE_2_DETAILED_PLAN.md

**Phase:** 2 - Multi-Telegram System  
**Duration:** Week 2-3 (5 days)  
**Dependencies:** Phase 1 complete  
**Status:** Not Started

---

## 🎯 PHASE OBJECTIVES

1. Deploy 3 specialized Telegram bots (Controller, Notification, Analytics)
2. Implement message routing logic
3. Maintain backward compatibility with single bot
4. Zero downtime migration

---

## 📋 TASKS BREAKDOWN

### **Task 2.1: Bot Creation & Token Management**
**Duration:** 30 minutes  
**Owner:** User (with agent guidance)

**Steps:**
1. Open Telegram, search for `@BotFather`
2. Create 3 new bots:
   ```
   /newbot
   Name: Zepix Controller
   Username: zepix_controller_bot
   
   /newbot
   Name: Zepix Notifications  
   Username: zepix_notifications_bot
   
   /newbot
   Name: Zepix Analytics
   Username: zepix_analytics_bot
   ```

3. Save tokens to secure location
4. Update `config/config.json`:
   ```json
   {
     "telegram_controller_token": "TOKEN_1_HERE",
     "telegram_notification_token": "TOKEN_2_HERE",
     "telegram_analytics_token": "TOKEN_3_HERE"
   }
   ```

5. Set bot privacy settings:
   ```
   /setprivacy
   Select bot: @zepix_controller_bot
   Settings: Enable (to receive all messages)
   ```

**Acceptance Criteria:**
- [ ] 3 bots created and verified
- [ ] Tokens added to config (encrypted)
- [ ] Tokens NOT in Git history
- [ ] Privacy settings configured

---

### **Task 2.2: MultiTelegramManager Implementation**
**Duration:** 2 hours  
**Status:** ✅ DONE (already created)

**File:** `src/telegram/multi_telegram_manager.py`

**Features:**
- ✅ Route messages by type
- ✅ Fallback to main bot if specialized token missing
- ✅ Broadcast to all bots for critical alerts
- ✅ Health check logging

---

### **Task 2.3: Bot-Specific Handler Classes**
**Duration:** 3 hours

**Create:** `src/telegram/controller_bot.py`
```python
class ControllerBot(TelegramBot):
    """Handles admin commands and system control"""
    
    def __init__(self, token, chat_id):
        super().__init__(token)
        self.chat_id = chat_id
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(
            CommandHandler("status", self.cmd_status)
        )
        self.application.add_handler(
            CommandHandler("enable_plugin", self.cmd_enable_plugin)
        )
        # ... more commands
    
    async def cmd_status(self, update, context):
        """Returns system health and status"""
        status = await self.trading_engine.get_status()
        await update.message.reply_text(
            f"🤖 **BOT STATUS**\n"
            f"Uptime: {status['uptime']}\n"
            f"Active Plugins: {status['plugins']}\n"
            f"Open Trades: {status['open_trades']}"
        )
```

**Create:** `src/telegram/notification_bot.py`
```python
class NotificationBot(TelegramBot):
    """Sends trade alerts and updates"""
    
    def send_entry_alert(self, trade_data):
        message = (
            f"🚀 **[{trade_data['plugin_id']}] ENTRY**\n"
            f"Symbol: {trade_data['symbol']}\n"
            f"Direction: {trade_data['direction']}\n"
            f"Lot: {trade_data['lot_size']}\n"
            f"Entry: {trade_data['entry_price']}\n"
            f"SL: {trade_data['sl_price']} (-{trade_data['sl_pips']} pips)\n"
            f"TP: {trade_data['tp_price']} (+{trade_data['tp_pips']} pips)\n"
            f"Time: {trade_data['timestamp']}"
        )
        self.send_message(message)
```

**Create:** `src/telegram/analytics_bot.py`
```python
class AnalyticsBot(TelegramBot):
    """Generates reports and insights"""
    
    async def cmd_daily_report(self, update, context):
        """Generates daily P&L report"""
        report = await self.analytics_service.generate_daily_report()
        
        await update.message.reply_text(
            f"📊 **DAILY REPORT - {report['date']}**\n\n"
            f"**Overall**\n"
            f"Total Profit: ${report['total_profit']:.2f}\n"
            f"Win Rate: {report['win_rate']:.1f}%\n"
            f"Trades: {report['total_trades']}\n\n"
            f"**Per Plugin**\n" + 
            "\n".join([
                f"• {p['id']}: ${p['profit']:.2f} ({p['trades']} trades)"
                for p in report['plugins']
            ])
        )
```

**Acceptance Criteria:**
- [ ] All 3 bot classes implemented
- [ ] Commands working in Controller
- [ ] Notifications formatted correctly
- [ ] Reports accurate

---

### **Task 2.4: Integration with TradingEngine**
**Duration:** 2 hours

**Modify:** `src/core/trading_engine.py`

```python
class TradingEngine:
    def __init__(self, config):
        # OLD: Single bot
        # self.telegram = TelegramBot(config["telegram_token"])
        
        # NEW: Multi-bot manager
        self.multi_telegram = MultiTelegramManager(config)
        
        # Backward compatibility alias
        self.telegram = self.multi_telegram.controller_bot
```

**Update all notification calls:**
```python
# OLD
self.telegram.send_message("Trade opened")

# NEW (explicit routing)
self.multi_telegram.send_alert("Trade opened")  # → Notification bot

# OR (backward compatible)
self.telegram.send_message("Trade opened")  # → Controller bot
```

**Acceptance Criteria:**
- [ ] TradingEngine uses MultiTelegramManager
- [ ] Old code still works (backward compatible)
- [ ] Alerts route to Notification bot
- [ ] Commands route to Controller bot

---

### **Task 2.5: Message Routing Logic**
**Duration:** 1 hour

**Update:** `src/telegram/multi_telegram_manager.py`

Add intelligent routing:
```python
def route_message(self, message_type, content, parse_mode="Markdown"):
    """
    Routes based on message type and content analysis.
    """
    # Explicit routing
    if message_type in ["alert", "entry", "exit"]:
        return self.notification_bot.send_message(content)
    
    if message_type in ["report", "stats"]:
        return self.analytics_bot.send_message(content)
    
    # Content-based routing (if type not specified)
    if any(kw in content.lower() for kw in ["buy", "sell", "entry", "exit"]):
        return self.notification_bot.send_message(content)
    
    if any(kw in content.lower() for kw in ["report", "profit", "stats"]):
        return self.analytics_bot.send_message(content)
    
    # Default: Controller
    return self.controller_bot.send_message(content)
```

---

### **Task 2.6: Testing & Validation**
**Duration:** 2 hours

**Test Suite:** `tests/test_multi_telegram.py`

```python
import pytest
from src.telegram.multi_telegram_manager import MultiTelegramManager

def test_routing_entry_alerts():
    """Entry alerts should go to Notification bot"""
    manager = MultiTelegramManager(config)
    
    # Mock bots
    manager.notification_bot = MockBot()
    
    manager.send_alert("BUY XAUUSD at 2030.50")
    
    assert manager.notification_bot.messages_sent == 1

def test_routing_reports():
    """Reports should go to Analytics bot"""
    manager = MultiTelegramManager(config)
    
    manager.analytics_bot = MockBot()
    
    manager.send_report("Daily P&L: +$250")
    
    assert manager.analytics_bot.messages_sent == 1

def test_fallback_to_main_bot():
    """If specialized bot fails, use main bot"""
    manager = MultiTelegramManager(config)
    manager.notification_bot = FailingBot()  # Simulates failure
    
    manager.send_alert("Test alert")
    
    assert manager.main_bot.messages_sent == 1  # Fallback used
```

**Manual Testing Checklist:**
- [ ] Send test command to Controller bot
- [ ] Verify response received
- [ ] Send test alert, verify Notification bot receives
- [ ] Request report, verify Analytics bot responds
- [ ] Disable one bot, verify fallback works
- [ ] Check logs for routing decisions

---

## 🔄 ROLLBACK PLAN

**If Phase 2 fails:**

1. Revert config changes:
   ```bash
   git checkout config/config.json
   ```

2. Restart with single bot:
   ```python
   # In trading_engine.py
   self.telegram = TelegramBot(config["telegram_token"])
   ```

3. All messages route to main bot

**RTO:** < 3 minutes

---

## 📊 SUCCESS METRICS

| Metric | Target | Measured By |
|---|---|---|
| Bot Creation Time | < 30 min | Manual |
| Implementation Time | < 8 hours | Time tracking |
| Message Routing Accuracy | 100% | Logs |
| Fallback Success Rate | 100% | Error logs |
| Zero Downtime | ✅ | Uptime monitoring |

---

## 🎯 DELIVERABLES

- [ ] 3 Telegram bots created and configured
- [ ] `MultiTelegramManager` class
- [ ] 3 specialized bot handler classes
- [ ] Updated `TradingEngine` integration
- [ ] Test suite with 95% coverage
- [ ] Documentation updated

---

## 📅 TIMELINE

| Day | Tasks |
|---|---|
| Day 1 | Task 2.1, 2.2 |
| Day 2 | Task 2.3 |
| Day 3 | Task 2.4, 2.5 |
| Day 4 | Task 2.6 |
| Day 5 | Buffer & documentation |

---

## ✅ COMPLETION CRITERIA

- [  ] All 3 bots respond to test messages
- [ ] Routing works 100% correctly
- [ ] Backward compatibility verified
- [ ] No errors in 24-hour monitoring
- [ ] User approval obtained
