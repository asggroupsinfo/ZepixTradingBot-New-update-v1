# Telegram Multi-Bot User Manual

## Overview

The Zepix Trading Bot uses a 3-bot Telegram system for complete trading control and monitoring. Each bot has a specific purpose, allowing for organized communication and efficient operation.

## The 3-Bot System

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ZEPIX TELEGRAM SYSTEM                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  CONTROLLER     │  │  NOTIFICATION   │  │  ANALYTICS      │     │
│  │  BOT            │  │  BOT            │  │  BOT            │     │
│  │                 │  │                 │  │                 │     │
│  │  Commands &     │  │  Trade Alerts   │  │  Reports &      │     │
│  │  Control        │  │  & Signals      │  │  Statistics     │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Bot Purposes

| Bot | Purpose | Message Types |
|-----|---------|---------------|
| Controller Bot | System control & commands | Menu navigation, settings, admin |
| Notification Bot | Trade alerts & signals | Entry/exit alerts, SL/TP hits, errors |
| Analytics Bot | Reports & statistics | Daily reports, P&L, performance |

## Getting Started

### Step 1: Start the Controller Bot

Send `/start` to the Controller Bot to initialize the main menu:

```
🤖 ZEPIX TRADING BOT
━━━━━━━━━━━━━━━━━━━━━
Welcome to Zepix Trading Bot v5.0

📊 Status    💰 Trades
🔌 Plugins   ⚙️ Settings
📈 Analytics 🛡️ Risk
❓ Help      👤 Admin
```

### Step 2: Check System Status

Tap **📊 Status** to view:

```
📊 SYSTEM STATUS
━━━━━━━━━━━━━━━━━━━━━
🟢 Bot: RUNNING
🟢 MT5: CONNECTED
🟢 Plugins: 3 Active

📅 Today's Stats:
├─ Trades: 5
├─ Win Rate: 80%
├─ P&L: +$125.50
└─ Open Positions: 2
```

## Main Menu Navigation

### Zero-Typing Interface

The bot uses a button-based interface - no typing required for most operations:

```
┌─────────────────────────────────────┐
│         MAIN MENU                   │
├─────────────────────────────────────┤
│  📊 Status    │  💰 Trades          │
├───────────────┼─────────────────────┤
│  🔌 Plugins   │  ⚙️ Settings         │
├───────────────┼─────────────────────┤
│  📈 Analytics │  🛡️ Risk             │
├───────────────┼─────────────────────┤
│  ❓ Help      │  👤 Admin            │
└─────────────────────────────────────┘
```

### Navigation Buttons

Every submenu includes navigation buttons:

| Button | Action |
|--------|--------|
| ◀️ Back | Return to previous menu |
| 🏠 Home | Return to main menu |

## Trading Menu

Access via **💰 Trades** from main menu:

```
💰 TRADING MENU
━━━━━━━━━━━━━━━━━━━━━
📋 Open Positions  📜 Trade History
🔴 Close All       💵 Book Profits
🎯 Modify SL       🎯 Modify TP
⚖️ Move to Breakeven
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Open Positions

View all active trades:

```
📋 OPEN POSITIONS
━━━━━━━━━━━━━━━━━━━━━
#1 XAUUSD BUY 0.10
   Entry: 2030.50
   SL: 2025.00 | TP: 2040.00
   P&L: +$15.30 🟢

#2 EURUSD SELL 0.05
   Entry: 1.0850
   SL: 1.0880 | TP: 1.0800
   P&L: -$3.20 🔴
━━━━━━━━━━━━━━━━━━━━━
🔄 Refresh
```

### Close All Positions

Tap **🔴 Close All** to close all open positions:

```
⚠️ CONFIRM CLOSE ALL
━━━━━━━━━━━━━━━━━━━━━
Are you sure you want to close
ALL 2 open positions?

Current P&L: +$12.10

[✅ Yes, Close All] [❌ Cancel]
```

### Book Profits

Tap **💵 Book Profits** to book profits on winning trades:

```
💵 BOOK PROFITS
━━━━━━━━━━━━━━━━━━━━━
Positions in profit:

#1 XAUUSD BUY +$15.30
   [Book 50%] [Book 100%]

━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Modify SL/TP

Use the input wizard to modify stop loss or take profit:

```
🎯 MODIFY STOP LOSS
━━━━━━━━━━━━━━━━━━━━━
Select position:

#1 XAUUSD BUY (SL: 2025.00)
#2 EURUSD SELL (SL: 1.0880)

━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

After selecting a position:

```
🎯 ENTER NEW SL
━━━━━━━━━━━━━━━━━━━━━
Current SL: 2025.00
Entry Price: 2030.50

Enter new SL price:
(or tap a quick option)

[2027.00] [2028.00] [Breakeven]
━━━━━━━━━━━━━━━━━━━━━
[❌ Cancel]
```

## Plugins Menu

Access via **🔌 Plugins** from main menu:

```
🔌 PLUGINS
━━━━━━━━━━━━━━━━━━━━━
✅ Active Plugins  📋 All Plugins
▶️ Enable Plugin   ⏹️ Disable Plugin
⚙️ Plugin Config   🔄 Reload Plugins
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Active Plugins

View currently active plugins:

```
✅ ACTIVE PLUGINS
━━━━━━━━━━━━━━━━━━━━━
1. combined_v3 (V3 Combined Logic)
   Status: 🟢 Running
   Trades Today: 3

2. price_action_15m (V6 15M)
   Status: 🟢 Running
   Trades Today: 2

3. price_action_1h (V6 1H)
   Status: 🟢 Running
   Trades Today: 1
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Enable/Disable Plugin

```
▶️ ENABLE PLUGIN
━━━━━━━━━━━━━━━━━━━━━
Select plugin to enable:

[price_action_5m]
[price_action_1m]
[hello_world]

━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

## Settings Menu

Access via **⚙️ Settings** from main menu:

```
⚙️ SETTINGS
━━━━━━━━━━━━━━━━━━━━━
📊 Lot Size     📉 Risk %
🛑 Default SL   🎯 Default TP
🔔 Notifications 🔊 Voice Alerts
💱 Symbols      🕐 Sessions
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Lot Size Settings

```
📊 LOT SIZE SETTINGS
━━━━━━━━━━━━━━━━━━━━━
Current: 0.10 lots

Select new lot size:
[0.01] [0.05] [0.10]
[0.25] [0.50] [1.00]

Or enter custom value:
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Notification Settings

```
🔔 NOTIFICATION SETTINGS
━━━━━━━━━━━━━━━━━━━━━
Trade Alerts: ✅ ON
Signal Alerts: ✅ ON
Error Alerts: ✅ ON
Daily Reports: ✅ ON

[Toggle Trade Alerts]
[Toggle Signal Alerts]
[Toggle Error Alerts]
[Toggle Daily Reports]
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Voice Alerts

```
🔊 VOICE ALERTS
━━━━━━━━━━━━━━━━━━━━━
Voice Alerts: ✅ ON

Alert Types:
├─ Trade Entry: ✅
├─ Trade Exit: ✅
├─ SL Hit: ✅
├─ TP Hit: ✅
└─ Errors: ❌

[Toggle Voice Alerts]
[Configure Alert Types]
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Session Settings

```
🕐 TRADING SESSIONS
━━━━━━━━━━━━━━━━━━━━━
Current Session: LONDON 🟢

Sessions:
├─ Sydney: 22:00-07:00 UTC
├─ Tokyo: 00:00-09:00 UTC
├─ London: 08:00-17:00 UTC
└─ New York: 13:00-22:00 UTC

Active Sessions: London, New York

[Session Alerts: ON]
[Configure Sessions]
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

## Risk Menu

Access via **🛡️ Risk** from main menu:

```
🛡️ RISK MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━
📊 Risk Status   📅 Daily Limits
📉 Max Risk %    🔢 Max Trades
🛑 Daily Loss Limit  📉 Max Drawdown
🚨 Emergency Stop
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Risk Status

```
📊 RISK STATUS
━━━━━━━━━━━━━━━━━━━━━
Account Balance: $10,000
Account Tier: $10,000

Daily Limits:
├─ Daily Loss Cap: $200
├─ Used Today: $45 (22.5%)
├─ Remaining: $155
└─ Status: 🟢 OK

Lifetime Limits:
├─ Lifetime Cap: $1,000
├─ Used: $250 (25%)
└─ Status: 🟢 OK
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Emergency Stop

```
🚨 EMERGENCY STOP
━━━━━━━━━━━━━━━━━━━━━
⚠️ This will:
1. Close ALL open positions
2. Cancel ALL pending orders
3. Pause ALL plugins
4. Stop accepting new signals

Are you sure?

[🚨 CONFIRM EMERGENCY STOP]
[❌ Cancel]
━━━━━━━━━━━━━━━━━━━━━
```

## Analytics Menu

Access via **📈 Analytics** from main menu:

```
📈 ANALYTICS
━━━━━━━━━━━━━━━━━━━━━
📊 Daily Report   📈 Weekly Report
🎯 Win Rate       📉 P&L Chart
🔌 Plugin Stats   💱 Symbol Stats
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Daily Report

```
📊 DAILY REPORT
━━━━━━━━━━━━━━━━━━━━━
Date: 2026-01-12

Summary:
├─ Total Trades: 8
├─ Winning: 6 (75%)
├─ Losing: 2 (25%)
├─ Gross Profit: +$185.00
├─ Gross Loss: -$45.00
└─ Net P&L: +$140.00

Best Trade: XAUUSD +$52.00
Worst Trade: EURUSD -$28.00

By Plugin:
├─ combined_v3: +$95.00 (5 trades)
├─ price_action_15m: +$45.00 (3 trades)
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### Win Rate

```
🎯 WIN RATE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━
Overall Win Rate: 72%

By Timeframe:
├─ 5M: 65% (20 trades)
├─ 15M: 75% (40 trades)
├─ 1H: 80% (25 trades)

By Symbol:
├─ XAUUSD: 78% (45 trades)
├─ EURUSD: 68% (25 trades)
├─ GBPUSD: 70% (15 trades)

By Direction:
├─ BUY: 74%
├─ SELL: 70%
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

## Admin Menu

Access via **👤 Admin** from main menu:

```
👤 ADMIN
━━━━━━━━━━━━━━━━━━━━━
▶️ Start Bot     ⏹️ Stop Bot
🖥️ System Status 📡 MT5 Status
📜 View Logs     🗑️ Clear Logs
🔄 Restart Bot
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### System Status

```
🖥️ SYSTEM STATUS
━━━━━━━━━━━━━━━━━━━━━
Bot Version: 5.0.0
Uptime: 2d 5h 32m

Components:
├─ Trading Engine: 🟢 Running
├─ MT5 Client: 🟢 Connected
├─ Telegram Bots: 🟢 3/3 Active
├─ Plugin System: 🟢 Healthy
└─ Database: 🟢 Connected

Memory: 256MB / 1GB
CPU: 12%
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

### MT5 Status

```
📡 MT5 STATUS
━━━━━━━━━━━━━━━━━━━━━
Connection: 🟢 CONNECTED
Server: XMGlobal-MT5
Account: 12345678

Account Info:
├─ Balance: $10,250.00
├─ Equity: $10,385.50
├─ Margin: $125.00
├─ Free Margin: $10,260.50
└─ Margin Level: 8308%

Open Positions: 2
Pending Orders: 0
━━━━━━━━━━━━━━━━━━━━━
◀️ Back  🏠 Home
```

## Notification Bot Messages

The Notification Bot sends real-time alerts:

### Trade Entry Alert

```
🟢 TRADE OPENED
━━━━━━━━━━━━━━━━━━━━━
Symbol: XAUUSD
Direction: BUY
Lot Size: 0.10

Entry: 2030.50
SL: 2025.00 (-55 pips)
TP: 2040.00 (+95 pips)

Plugin: combined_v3
Time: 14:32:15 IST
━━━━━━━━━━━━━━━━━━━━━
```

### Trade Exit Alert

```
🔴 TRADE CLOSED
━━━━━━━━━━━━━━━━━━━━━
Symbol: XAUUSD
Direction: BUY
Lot Size: 0.10

Entry: 2030.50
Exit: 2038.75
Result: +$82.50 🟢

Reason: TP Hit
Duration: 2h 15m
━━━━━━━━━━━━━━━━━━━━━
```

### SL Hit Alert

```
🛑 STOP LOSS HIT
━━━━━━━━━━━━━━━━━━━━━
Symbol: EURUSD
Direction: SELL
Lot Size: 0.05

Entry: 1.0850
Exit: 1.0880
Result: -$15.00 🔴

Recovery: Monitoring...
━━━━━━━━━━━━━━━━━━━━━
```

### Signal Alert

```
📡 NEW SIGNAL
━━━━━━━━━━━━━━━━━━━━━
Symbol: GBPUSD
Direction: BUY
Timeframe: 15M

Consensus Score: 8/10
ADX: 28.5
Trend: BULLISH

Status: Processing...
━━━━━━━━━━━━━━━━━━━━━
```

## Sticky Header

The sticky header appears at the top of messages and updates every 60 seconds:

```
┌─────────────────────────────────────┐
│ 🤖 ZEPIX v5.0 | 🟢 RUNNING         │
│ 🕐 14:32:15 IST | 📊 +$125.50      │
│ 🌍 London | 📈 2 Open              │
└─────────────────────────────────────┘
```

### Header Components

| Component | Description |
|-----------|-------------|
| Version | Current bot version |
| Status | Running/Paused/Error |
| Time | Current IST time |
| P&L | Today's profit/loss |
| Session | Active trading session |
| Open | Number of open positions |

## Voice Alerts

When enabled, the bot sends voice messages for important events:

| Event | Voice Message |
|-------|---------------|
| Trade Entry | "Trade opened: [Symbol] [Direction]" |
| Trade Exit | "Trade closed: [Symbol] with [Profit/Loss]" |
| SL Hit | "Stop loss hit on [Symbol]" |
| TP Hit | "Take profit hit on [Symbol]" |
| Error | "Error: [Description]" |

## Quick Commands

While the bot is primarily button-based, these text commands are also available:

| Command | Description |
|---------|-------------|
| `/start` | Show main menu |
| `/status` | Quick status check |
| `/positions` | List open positions |
| `/close_all` | Close all positions |
| `/help` | Show help menu |
| `/admin` | Admin functions |

## Rate Limiting

The system implements rate limiting to comply with Telegram API limits:

| Limit | Value |
|-------|-------|
| Messages per second | 1 |
| Messages per minute | 20 |
| Burst capacity | 1000 |

Messages are queued and sent in priority order:
1. CRITICAL - Emergency alerts
2. HIGH - Trade alerts
3. NORMAL - Status updates
4. LOW - Analytics reports

## Troubleshooting

### Bot Not Responding

1. Check if bot is running: `/status`
2. Check MT5 connection in Admin menu
3. Restart bot if needed

### Missing Notifications

1. Check notification settings
2. Verify Telegram permissions
3. Check rate limiting status

### Slow Response

1. Check queue status in Admin menu
2. Reduce notification frequency
3. Check internet connection

## Best Practices

1. **Use the Main Menu**: Navigate using buttons rather than typing commands
2. **Check Status Regularly**: Monitor system health via Status menu
3. **Set Appropriate Limits**: Configure risk limits before trading
4. **Enable Voice Alerts**: For critical events when away from screen
5. **Review Daily Reports**: Check Analytics Bot for performance insights

## Support

For additional help:
- Tap **❓ Help** in main menu
- Check FAQ section
- Contact support via Support button

---

**Document Version:** 1.0
**Last Updated:** January 2026
**Compatible With:** Zepix Trading Bot v5.0
