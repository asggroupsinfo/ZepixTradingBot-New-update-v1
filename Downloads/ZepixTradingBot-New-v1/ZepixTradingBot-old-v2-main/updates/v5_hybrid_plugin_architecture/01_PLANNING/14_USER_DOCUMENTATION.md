# 14_USER_DOCUMENTATION.md

**Version:** 1.0  
**Date:** 2026-01-12  
**Audience:** End Users (Traders)

---

## 🚀 GETTING STARTED

### **What's New in v3.0?**

Your Zepix Trading Bot now has a **Plugin Architecture**! This means:

✅ **More organized** - Each trading strategy is a separate plugin  
✅ **Independent performance** - Track each strategy separately  
✅ **Easy to enable/disable** - Turn strategies on/off without code changes  
✅ **Better notifications** - 3 specialized Telegram bots

---

## 📱 TELEGRAM BOTS GUIDE

You now have **3 Telegram bots** instead of 1:

### **1. Controller Bot** (`@zepix_controller_bot`)
**Purpose:** Manage the bot

**Commands:**
- `/status` - View bot health and active plugins
- `/enable_plugin <name>` - Enable a plugin
- `/disable_plugin <name>` - Disable a plugin
- `/daily_report` - Get today's summary
- `/help` - See all commands

### **2. Notification Bot** (`@zepix_notifications_bot`)
**Purpose:** Receive trade alerts

**Receives:**
- 🚀 **Entry alerts** - When trades are placed
- 🏁 **Exit alerts** - When trades are closed
- 📊 **Profit bookings** - When TP1, TP2, TP3 hit
- ⚠️ **Warnings** - Important notices

### **3. Analytics Bot** (`@zepix_analytics_bot`)
**Purpose:** Performance reports

**Commands:**
- `/daily_report` - Today's P&L
- `/weekly_report` - Week performance
- `/plugin_stats` - Per-plugin breakdown
- `/export_trades` - Download trade history

---

## 🔌 PLUGINS EXPLAINED

### **What is a Plugin?**

A **plugin** is a self-contained trading strategy. Think of it like an app on your phone - you can install, enable, disable, or uninstall it without affecting others.

### **Current Plugins:**

#### **combined_v3** ✅ ACTIVE
- **Description:** Your original V3 logic (combinedlogic-1/2/3)
- **Symbols:** XAUUSD, EURUSD, GBPUSD
- **Risk:** 1.5% per trade
- **Max Daily Loss:** $500

**How to check status:**
```
Send to Controller Bot: /status
```

**How to disable:**
```
Send to Controller Bot: /disable_plugin combined_v3
```

**How to enable:**
```
Send to Controller Bot: /enable_plugin combined_v3
```

---

## 📊 UNDERSTANDING NOTIFICATIONS

### **Entry Alert Format:**
```
🚀 [combined_v3] ENTRY

Symbol: XAUUSD
Direction: BUY
Lot: 0.12
Entry: 2030.50
SL: 2028.00 (-25 pips)
TP: 2035.00 (+45 pips)
Time: 2026-01-12 14:30:15
```

**What this means:**
- Plugin `combined_v3` opened a BUY trade
- 0.12 lots on XAUUSD
- Entry at 2030.50
- Stop Loss at 2028.00 (risking 25 pips)
- Take Profit at 2035.00 (targeting 45 pips)

### **Exit Alert Format:**
```
🏁 [combined_v3] EXIT

Symbol: XAUUSD
Ticket: #12345
Direction: BUY → CLOSED
Exit: 2032.50
Profit: +20 pips (+$200.00)
Duration: 2h 15m
Reason: TP1 Hit
```

---

## ⚙️ CONFIGURATION GUIDE

### **Adjusting Plugin Settings**

**File:** `config/config.json`

**Example: Change max lot size for combined_v3:**

```json
{
    "plugins": {
        "combined_v3": {
            "enabled": true,
            "max_lot_size": 1.0,  ← Change this
            "daily_loss_limit": 500.0
        }
    }
}
```

**After editing:**
```
Send to Controller Bot: /config_reload combined_v3
```

---

## 🛡️ SAFETY FEATURES

### **Daily Loss Limit**

Each plugin has a daily loss limit. When reached:
- ❌ Plugin stops trading for the day
- 📱 You get a notification
- ✅ Resumes next day automatically

**To check limit:**
```
Send to Controller Bot: /daily_limit combined_v3
```

### **Emergency Stop**

**To stop ALL trading immediately:**
```
Send to Controller Bot: /emergency_stop
```

This will:
- Close all open trades
- Disable all plugins
- Require manual re-activation

---

## 📈 PERFORMANCE TRACKING

### **Daily Report**

**Request:**
```
Send to Analytics Bot: /daily_report
```

**Response:**
```
📊 DAILY REPORT - 2026-01-12

Overall:
Total Profit: +$350.50
Win Rate: 75.0%
Trades: 12

Per Plugin:
• combined_v3: +$350.50 (12 trades)
```

### **Weekly Report**

**Request:**
```
Send to Analytics Bot: /weekly_report
```

Includes:
- Weekly P&L
- Win rate
- Best/worst days
- Symbol performance

---

## 🔧 TROUBLESHOOTING

### **"Bot not responding to alerts"**

**Check:**
1. Is plugin enabled?
   ```
   /status
   ```
2. Did you hit daily loss limit?
   ```
   /daily_limit combined_v3
   ```
3. Check bot logs:
   ```
   tail -f logs/bot.log
   ```

### **"Wrong lot size calculated"**

Check configuration:
```json
{
    "plugins": {
        "combined_v3": {
            "settings": {
                "risk_percentage": 1.5,  ← Your risk %
                "max_lot_size": 1.0      ← Cap
            }
        }
    }
}
```

### **"Not receiving Telegram notifications"**

1. Verify bot tokens in config
2. Check you're in the correct chat
3. Test:
   ```
   /status
   ```
   Should respond immediately

---

## 📞 SUPPORT

### **How to Report Issues**

1. **Screenshot** the error/issue
2. **Copy** recent logs:
   ```bash
   tail -n 50 logs/bot.log > issue_log.txt
   ```
3. **Send** to support with description

### **Emergency Contacts**

- **Critical Issues:** [Your Telegram]
- **General Support:** [Support Channel]

---

## ✅ BEST PRACTICES

1. **Monitor daily** - Check daily reports
2. **Review losses** - Understand losing trades
3. **Adjust limits** - Fine-tune risk settings
4. **Keep updated** - Watch for bot updates
5. **Backup configs** - Save config changes

---

## 🎯 QUICK REFERENCE

### **Most Used Commands**

| Command | Bot | Purpose |
|---|---|---|
| `/status` | Controller | System health |
| `/daily_report` | Analytics | Today's P&L |
| `/enable_plugin <name>` | Controller | Turn on strategy |
| `/disable_plugin <name>` | Controller | Turn off strategy |
| `/emergency_stop` | Controller | Stop everything |

### **Config File Locations**

- **Main Config:** `config/config.json`
- **Plugin Configs:** `src/logic_plugins/<plugin_id>/config.json`
- **Logs:** `logs/bot.log`
- **Database:** `data/zepix_combined_v3.db`

---

## 🆘 FAQ

**Q: Can I run multiple plugins at once?**  
A: Yes! Each plugin trades independently.

**Q: Will plugins interfere with each other?**  
A: No, they're isolated and have separate databases.

**Q: Can I see which plugin placed which trade?**  
A: Yes, check MT5 order comment or Telegram alert.

**Q: How do I add a new plugin?**  
A: See [Developer Onboarding](#) or contact support.

**Q: What happens if the bot crashes?**  
A: Open trades remain in MT5. Bot resumes on restart.

---

**Last Updated:** 2026-01-12  
**Version:** 3.0.0  
**Support:** [Your Contact Info]
