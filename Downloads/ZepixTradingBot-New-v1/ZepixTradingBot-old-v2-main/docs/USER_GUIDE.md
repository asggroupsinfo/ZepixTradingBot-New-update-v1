# User Guide

**Version:** 3.0
**Date:** 2026-01-12
**Type:** User Guide

---

## Getting Started

Your Zepix Trading Bot now has a **Plugin Architecture**! This means:

- **More organized** - Each trading strategy is a separate plugin
- **Independent performance** - Track each strategy separately
- **Easy to enable/disable** - Turn strategies on/off without code changes
- **Better notifications** - 3 specialized Telegram bots

## Telegram Bots Guide

You now have **3 Telegram bots** instead of 1:

**1. Controller Bot** (`@zepix_controller_bot`)
- Purpose: Manage the bot
- Commands: `/status`, `/enable_plugin`, `/disable_plugin`, `/daily_report`, `/help`

**2. Notification Bot** (`@zepix_notifications_bot`)
- Purpose: Receive trade alerts
- Receives: Entry alerts, Exit alerts, Profit bookings, Warnings

**3. Analytics Bot** (`@zepix_analytics_bot`)
- Purpose: Performance reports
- Commands: `/daily_report`, `/weekly_report`, `/plugin_stats`, `/export_trades`

## Plugins Explained

A **plugin** is a self-contained trading strategy. Think of it like an app on your phone - you can install, enable, disable, or uninstall it without affecting others.

**Current Plugins:**

**combined_v3** - Your original V3 logic (combinedlogic-1/2/3)
- Symbols: XAUUSD, EURUSD, GBPUSD
- Risk: 1.5% per trade
- Max Daily Loss: $500

**Commands:**
- Check status: `/status`
- Disable: `/disable_plugin combined_v3`
- Enable: `/enable_plugin combined_v3`

## Understanding Notifications

**Entry Alert Format:**
```
[combined_v3] ENTRY
Symbol: XAUUSD
Direction: BUY
Lot: 0.12
Entry: 2030.50
SL: 2028.00 (-25 pips)
TP: 2035.00 (+45 pips)
```

**Exit Alert Format:**
```
[combined_v3] EXIT
Symbol: XAUUSD
Ticket: #12345
Direction: BUY -> CLOSED
Exit: 2032.50
Profit: +20 pips (+$200.00)
Duration: 2h 15m
Reason: TP1 Hit
```

## Safety Features

**Daily Loss Limit**
Each plugin has a daily loss limit. When reached:
- Plugin stops trading for the day
- You get a notification
- Resumes next day automatically

**Emergency Stop**
To stop ALL trading immediately:
```
/emergency_stop
```
This will close all open trades, disable all plugins, and require manual re-activation.

## Quick Reference

**Most Used Commands:**

| Command | Bot | Purpose |
|---------|-----|---------|
| `/status` | Controller | System health |
| `/daily_report` | Analytics | Today's P&L |
| `/enable_plugin <name>` | Controller | Turn on strategy |
| `/disable_plugin <name>` | Controller | Turn off strategy |
| `/emergency_stop` | Controller | Stop everything |

**Config File Locations:**
- Main Config: `config/config.json`
- Plugin Configs: `src/logic_plugins/<plugin_id>/config.json`
- Logs: `logs/bot.log`
- Database: `data/zepix_combined_v3.db`
