# 05_MULTI_TELEGRAM_ARCHITECTURE_RESEARCH.md

**Document Version:** 1.0  
**Date:** 2026-01-12  
**Author:** Antigravity Agent  
**Status:** Research Complete

---

## 🎯 OBJECTIVE

Research and define the architecture for deploying 3 specialized Telegram bots instead of a single monolithic bot.

---

## 📊 BOT SPECIALIZATION STRATEGY

### **Bot 1: Controller Bot**
**Purpose:** Admin interface and system control  
**Responsibilities:**
- Handle `/start`, `/stop`, `/pause`, `/resume` commands
- Execute `/status`, `/health`, `/stats` commands
- Plugin management: `/enable_plugin`, `/disable_plugin`, `/list_plugins`
- System configuration changes
- Emergency stop/restart functionality

**Command List:**
```
/start - Initialize bot system
/stop - Gracefully shutdown
/pause_trading - Pause all trading logic
/resume_trading - Resume trading
/status - System health and plugin status
/enable_plugin [plugin_id] - Enable a plugin
/disable_plugin [plugin_id] - Disable a plugin
/list_plugins - Show all plugins with status
/config_get [key] - Get configuration value
/config_set [key] [value] - Update configuration
/emergency_close_all - Close all open positions
```

**Security:** Admin-only, restricted to `allowed_telegram_user` from config.

---

### **Bot 2: Notification Bot**
**Purpose:** Real-time trade alerts and updates  
**Responsibilities:**
- Entry alerts (BUY/SELL signals received)
- Exit alerts (TP hit, SL hit, Manual close)
- Profit booking notifications (50% TP, 75% TP, etc.)
- Re-entry alerts (SL Hunt recovery, TP continuation)
- Error alerts (Order failed, MT5 connection lost)

**Message Format:**
```
🚀 **[PLUGIN_ID] ENTRY**
Symbol: XAUUSD
Direction: BUY
Lot: 0.05
Entry: 2032.50
SL: 2030.00 (-250 pips)
TP: 2037.50 (+500 pips)
Time: 15:30:45 IST
```

**Frequency:** High (multiple messages per minute during active trading)

**Security:** Read-only, no commands accepted.

---

### **Bot 3: Analytics Bot**
**Purpose:** Performance reports and insights  
**Responsibilities:**
- Daily P&L summary
- Weekly performance breakdown
- Per-plugin statistics
- Win rate, profit factor, drawdown analysis
- Trade journal summaries

**Command List:**
```
/daily_report - Today's performance
/weekly_report - Last 7 days
/monthly_report - Current month
/plugin_stats [plugin_id] - Specific plugin performance
/top_symbols - Best performing symbols
/worst_trades - Biggest losses today
/equity_curve - Visual equity chart
```

**Frequency:** On-demand + scheduled (daily at 11:59 PM IST)

**Security:** Read-only for reports, admin-only for commands.

---

## 🔀 MESSAGE ROUTING LOGIC

### **Routing Table**

| Message Type | Target Bot | Priority | Example |
|---|---|---|---|
| Command Response | Controller | High | "✅ Trading paused" |
| Entry Signal | Notification | High | "🚀 XAUUSD BUY 0.05" |
| Exit Signal | Notification | High | "💰 XAUUSD CLOSED +50 pips" |
| Profit Booking | Notification | Medium | "📈 50% profit booked" |
| Re-entry Alert | Notification | High | "🔄 SL Hunt recovery active" |
| Daily Report | Analytics | Low | "📊 Daily P&L: +$250" |
| Error/Warning | **ALL 3 BOTS** | Critical | "❌ MT5 Connection Lost" |
| System Status | Controller | Medium | "⚙️ System healthy" |

### **Routing Implementation**

```python
class MultiTelegramManager:
    def route_message(self, message_type, content):
        if message_type == "command":
            self.controller_bot.send(content)
        elif message_type in ["entry", "exit", "profit_book", "reentry"]:
            self.notification_bot.send(content)
        elif message_type in ["report", "stats"]:
            self.analytics_bot.send(content)
        elif message_type == "critical":
            self.broadcast_to_all(content)
```

---

## 📡 TELEGRAM API CONSIDERATIONS

### **Rate Limits**
- **Per Bot:** 30 messages/second
- **Per Chat:** 1 message/second (recommendation)
- **Bulk Messages:** Use 100ms delay between sends

**Strategy:** With 3 bots, effective rate is 3 messages/second to same chat (safe margin).

### **Message Size Limits**
- Text: 4096 characters
- Photo captions: 1024 characters

**Strategy:** Split long reports into multiple messages or use Markdown formatting.

### **Connection Reliability**
- Use `python-telegram-bot` library v20.x with async support
- Implement retry logic (3 attempts with exponential backoff)
- Fallback to main bot if specialized bot fails

---

## 🔒 TOKEN MANAGEMENT

### **Storage**
```json
{
  "telegram_token": "MAIN_BOT_TOKEN",
  "telegram_controller_token": "CONTROLLER_BOT_TOKEN",
  "telegram_notification_token": "NOTIFICATION_BOT_TOKEN",
  "telegram_analytics_token": "ANALYTICS_BOT_TOKEN"
}
```

### **Fallback Logic**
If any specialized token is empty or invalid:
- Fall back to `telegram_token` (main bot)
- Log warning: "⚠️ Using main bot as fallback for [bot_type]"

---

## 🛡️ ERROR HANDLING

### **Bot Failure Scenarios**

1. **Token Invalid**
   - Detect on initialization
   - Fallback to main bot
   - Alert admin via controller bot

2. **Network Timeout**
   - Retry 3 times (1s, 2s, 4s delays)
   - If all fail, queue message for later
   - Alert admin if >10 messages queued

3. **Rate Limit Hit**
   - Implement message queue
   - Stagger sends with 150ms delays
   - Log rate limit events

### **Monitoring**
- Track message send success rate per bot
- Alert if success rate <95%
- Daily health check pings

---

## 📈 BENEFITS OF MULTI-BOT ARCHITECTURE

| Aspect | Single Bot | Multi-Bot |
|---|---|---|
| Message organization | Mixed alerts | Clean separation |
| Rate limits | 30 msg/s | 90 msg/s (3x) |
| User experience | Cluttered | Clean, organized |
| Debugging | Hard to filter | Easy per-bot logs |
| Scalability | Limited | High |

---

## ⚠️ RISKS AND MITIGATIONS

| Risk | Impact | Mitigation |
|---|---|---|
| Token leak | Critical | Store in env vars, gitignore config |
| Bot ban/suspension | High | Follow Telegram ToS, rate limits |
| Increased complexity | Medium | Centralized routing logic |
| Cost (if premium) | Low | All bots free |

---

## 🧪 TESTING PLAN

1. **Unit Tests**
   - Test routing logic with mock bots
   - Test fallback mechanism
   - Test rate limiting

2. **Integration Tests**
   - Send test messages to all 3 bots
   - Verify correct bot receives message
   - Test broadcast to all bots

3. **Load Tests**
   - Send 100 messages/minute
   - Verify no rate limit errors
   - Check message queue behavior

---

## ✅ DECISION

**APPROVED:** Implement multi-bot architecture with Controller, Notification, and Analytics bots.

**Next Steps:**
1. Create bots via @BotFather
2. Implement `MultiTelegramManager` class
3. Integrate with `TradingEngine`
4. Test with shadow bot setup
