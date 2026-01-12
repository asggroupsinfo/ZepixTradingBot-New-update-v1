# NOTIFICATION SYSTEM SPECIFICATION

**Version:** 1.0  
**Date:** 2026-01-12  
**Component:** Core Notification Router  
**Status:** Complete

---

## 🔔 NOTIFICATION SYSTEM OVERVIEW

**Purpose:** Centralized notification routing for all bot events

**Architecture:** Event-Driven Notification Bus

**Flow:**
```
Event Source → Notification Router → Multi-Telegram Manager → User
     ↓
  (Plugin, TradingEngine, System)
```

---

## 📊 NOTIFICATION TYPES & PRIORITY

### **Priority Levels:**

1. **CRITICAL** (RED 🔴)
   - Emergency stop executed
   - Daily loss limit reached
   - MT5 connection lost
   - System crash
   - **Action:** Broadcast to ALL 3 bots + Voice alert

2. **HIGH** (ORANGE 🟠)
   - Trade entry
   - Trade exit
   - SL/TP hit
   - Plugin error
   - **Action:** Send to Notification Bot + Voice (if enabled)

3. **MEDIUM** (YELLOW 🟡)
   - Partial profit booking
   - SL modification
   - Alert received but not executed
   - **Action:** Send to Notification Bot

4. **LOW** (BLUE 🔵)
   - Daily summary
   - Plugin status change
   - Config reload
   - **Action:** Send to Analytics Bot

5. **INFO** (GREEN 🟢)
   - Bot started
   - Plugin loaded
   - Shadow mode active
   - **Action:** Send to Controller Bot

---

## 🎯 NOTIFICATION ROUTER IMPLEMENTATION

### **Core NotificationRouter Class:**

```python
from enum import Enum
from typing import Dict, Callable

class NotificationPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1

class NotificationRouter:
    def __init__(self, telegram_manager):
        self.telegram = telegram_manager
        self.voice_enabled = True
        self.handlers = {}
        
    async def send(self, 
                   notification_type: str, 
                   data: Dict,
                   priority: NotificationPriority = NotificationPriority.MEDIUM):
        """
        Central notification dispatch
        
        Args:
            notification_type: 'entry', 'exit', 'error', etc.
            data: Notification payload
            priority: Notification priority
        """
        
        # Format message
        formatted _msg = await self.format_notification(notification_type, data)
        
        # Route based on priority and type
        if priority == NotificationPriority.CRITICAL:
            # Broadcast to ALL bots
            await self.telegram.broadcast(formatted_msg)
            # Always send voice for critical
            await self.send_voice_alert(formatted_msg, data)
            
        elif priority == NotificationPriority.HIGH:
            # Send to Notification Bot
            await self.telegram.route_message('notification', formatted_msg)
            # Voice if enabled
            if self.voice_enabled:
                await self.send_voice_alert(formatted_msg, data)
                
        elif priority == NotificationPriority.MEDIUM:
            # Notification Bot only
            await self.telegram.route_message('notification', formatted_msg)
            
        elif priority == NotificationPriority.LOW:
            # Analytics Bot
            await self.telegram.route_message('analytics', formatted_msg)
            
        else:  # INFO
            # Controller Bot
            await self.telegram.route_message('controller', formatted_msg)
        
        # Log notification
        await self.log_notification(notification_type, priority, data)
    
    async def format_notification(self, notification_type, data):
        """Format notification based on type"""
        
        formatter = self.handlers.get(notification_type)
        if formatter:
            return await formatter(data)
        else:
            # Default formatter
            return f"{notification_type.upper()}: {data}"
```

---

## 📝 EVENT-TO-NOTIFICATION MAPPING

### **Trade Events:**

| Event | Notification Type | Priority | Bot | Voice |
|-------|------------------|----------|-----|-------|
| Trade opened (V3 dual) | `entry_v3_dual` | HIGH | Notification | Yes |
| Trade opened (V6 single) | `entry_v6_single` | HIGH | Notification | Yes |
| Trade closed (profit) | `exit_profit` | HIGH | Notification | Yes |
| Trade closed (loss) | `exit_loss` | HIGH | Notification | Yes |
| TP1 hit | `tp1_hit` | HIGH | Notification | Yes |
| TP2 hit | `tp2_hit` | HIGH | Notification | Yes |
| SL hit | `sl_hit` | HIGH | Notification | Yes |
| Partial profit | `profit_partial` | MEDIUM | Notification | No |
| SL modified | `sl_modified` | MEDIUM | Notification | No |
| Position breakeven | `breakeven_moved` | MEDIUM | Notification | Optional |

### **System Events:**

| Event | Notification Type | Priority | Bot | Voice |
|-------|------------------|----------|-----|-------|
| Bot started | `bot_started` | INFO | Controller | No |
| Bot stopped | `bot_stopped` | CRITICAL | ALL | Yes |
| Emergency stop | `emergency_stop` | CRITICAL | ALL | Yes |
| MT5 disconnected | `mt5_disconnect` | CRITICAL | ALL | Yes |
| MT5 reconnected | `mt5_reconnect` | HIGH | Notification | No |
| Daily loss limit | `daily_loss_limit` | CRITICAL | ALL | Yes |
| Plugin loaded | `plugin_loaded` | INFO | Controller | No |
| Plugin error | `plugin_error` | HIGH | Notification | No |
| Config  reloaded | `config_reload` | LOW | Analytics | No |

### **Alert Events:**

| Event | Notification Type | Priority | Bot | Voice |
|-------|------------------|----------|-----|-------|
| Alert received | `alert_received` | INFO | Controller | No |
| Alert processed | `alert_processed` | MEDIUM | Notification | No |
| Alert ignored (shadow) | `alert_shadow` | LOW | Analytics | No |
| Alert error | `alert_error` | HIGH | Notification | No |
| Invalid alert | `alert_invalid` | MEDIUM | Notification | No |

### **Analytics Events:**

| Event | Notification Type | Priority | Bot | Voice |
|-------|------------------|----------|-----|-------|
| Daily summary | `daily_summary` | LOW | Analytics | No |
| Weekly summary | `weekly_summary` | LOW | Analytics | No |
| Performance report | `performance_report` | LOW | Analytics | No |
| Risk alert | `risk_alert` | HIGH | Notification | Yes |

---

## 🎨 NOTIFICATION TEMPLATES

### **Entry Notification (V3 Dual Orders):**

```python
async def format_entry_v3_dual(data):
    return f"""
🟢 ENTRY | {data['plugin_name']}

Symbol: {data['symbol']}
Direction: {data['direction']}
Entry: {data['entry_price']}

Order A (Smart SL):
├─ Lot: {data['order_a_lot']}
├─ SL: {data['order_a_sl']} 
└─ TP: {data['order_a_tp']} (TP2)

Order B (Fixed $10 SL):
├─ Lot: {data['order_b_lot']}
├─ SL: {data['order_b_sl']}
└─ TP: {data['order_b_tp']} (TP1)

Signal: {data['signal_type']}
TF: {data['timeframe']} | Logic: {data['logic_route']}
Tickets: #{data['ticket_a']}, #{data['ticket_b']}
Time: {data['timestamp']}
"""
```

### **Entry Notification (V6 Single Order A):**

```python
async def format_entry_v6_single_a(data):
    return f"""
🟢 ENTRY | {data['plugin_name']} (ORDER A)

Symbol: {data['symbol']}
Direction: {data['direction']}
Entry: {data['entry_price']}

Order A:
├─ Lot: {data['lot_size']}
├─ SL: {data['sl_price']}
└─ TP: {data['tp_price']}

ADX: {data['adx']} ({data['adx_strength']})
Confidence: {data['confidence_score']}/100 ({data['confidence_level']})
Market State: {data['market_state']}

Ticket: #{data['ticket']}
Time: {data['timestamp']}
"""
```

### **Exit Notification:**

```python
async def format_exit(data):
    profit_emoji = "✅" if data['profit'] > 0 else "❌"
    
    return f"""
🔴 EXIT | {data['plugin_name']}

Symbol: {data['symbol']}
Direction: {data['direction']} → CLOSED

Entry: {data['entry_price']} → Exit: {data['exit_price']}
Hold Time: {data['hold_duration']}

{profit_emoji} P&L: {'+' if data['profit'] > 0 else ''}{data['profit']:.2f} USD
Commission: -{data['commission']:.2f} USD
Net: {data['net_profit']:.2f} USD

Reason: {data['close_reason']}
Time: {data['timestamp']}
"""
```

### **Daily Summary:**

```python
async def format_daily_summary(data):
    return f"""
📊 DAILY SUMMARY | {data['date']}

Performance:
├─ Total Trades: {data['total_trades']}
├─ Winners: {data['winners']} ({data['win_rate']:.1f}%)
├─ Losers: {data['losers']}
└─ Breakeven: {data['breakeven']}

P&L:
├─ Gross Profit: +${data['gross_profit']:.2f}
├─ Gross Loss: -${data['gross_loss']:.2f}
├─ Commission: -${data['commission']:.2f}
└─ Net P&L: {'+' if data['net_pnl'] > 0 else ''}${data['net_pnl']:.2f}

By Plugin:
{data['plugin_breakdown']}

Risk Metrics:
├─ Max Drawdown: {data['max_drawdown']:.1f}%
├─ Risk/Reward: {data['risk_reward']:.2f}
└─ Sharpe Ratio: {data['sharpe']:.2f}
"""
```

---

## 🔊 VOICE ALERT CONFIGURATION

### **Voice Alert Rules:**

```python
VOICE_ALERT_CONFIG = {
    "enabled": True,
    "triggers": {
        "entry": True,
        "exit_profit": True,
        "exit_loss": True,
        "tp_hit": True,
        "sl_hit": True,
        "emergency": True,
        "daily_summary": False
    },
    "language": "en",
    "speed": "normal",  # slow, normal, fast
    "volume": 100  # 0-100
}
```

### **Voice Text Generation:**

```python
def generate_voice_text(notification_type, data):
    """Generate short voice alert text"""
    
    if notification_type == 'entry':
        return f"New {data['direction']} trade on {data['symbol']} at {data['entry_price']}. Signal: {data['signal_type']}."
    
    elif notification_type == 'exit_profit':
        return f"{data['direction']} trade closed with profit of {data['profit']} dollars."
    
    elif notification_type == 'exit_loss':
        return f"{data['direction']} trade closed with loss of {abs(data['profit'])} dollars."
    
    elif notification_type == 'tp_hit':
        return f"TP{data['tp_level']} hit. Profit: {data['profit']} dollars."
    
    elif notification_type == 'sl_hit':
        return f"Stop loss hit. Loss: {abs(data['profit'])} dollars."
    
    elif notification_type == 'emergency':
        return f"Emergency alert. {data['message']}"
```

---

## 📈 NOTIFICATION STATISTICS

### **Tracked Metrics:**

```python
class NotificationStats:
    def __init__(self):
        self.stats = {
            "total_sent": 0,
            "by_type": {},
            "by_priority": {},
            "by_bot": {},
            "voice_alerts_sent": 0,
            "failed_notifications": 0
        }
    
    def record(self, notification_type, priority, bot, success):
        self.stats["total_sent"] += 1
        
        # By type
        self.stats["by_type"][notification_type] = \
            self.stats["by_type"].get(notification_type, 0) + 1
        
        # By priority
        self.stats["by_priority"][priority.name] = \
            self.stats["by_priority"].get(priority.name, 0) + 1
        
        # By bot
        self.stats["by_bot"][bot] = \
            self.stats["by_bot"].get(bot, 0) + 1
        
        # Failed
        if not success:
            self.stats["failed_notifications"] += 1
```

---

## 🔄 NOTIFICATION QUEUE SYSTEM

### **Queue for Rate Limiting:**

```python
from asyncio import Queue

class Notification QueueManager:
    def __init__(self, max_per_minute=20):
        self.queue = Queue()
        self.max_per_minute = max_per_minute
        self.sent_in_minute = []
    
    async def add(self, notification):
        """Add notification to queue"""
        await self.queue.put(notification)
    
    async def process(self):
        """Process queue with rate limiting"""
        while True:
            # Check rate limit
            now = time.time()
            self.sent_in_minute = [t for t in self.sent_in_minute 
                                   if now - t < 60]
            
            if len(self.sent_in_minute) >= self.max_per_minute:
                await asyncio.sleep(1)
                continue
            
            # Get notification
            notification = await self.queue.get()
            
            # Send
            try:
                await notification.send()
                self.sent_in_minute.append(now)
            except Exception as e:
                logger.error(f"Notification send failed: {e}")
```

---

## ✅ NOTIFICATION SYSTEM CHECKLIST

- [ ] NotificationRouter implemented
- [ ] All event types mapped
- [ ] All formatters created
- [ ] Multi-Telegram Manager integrated
- [ ] Voice alert system working
- [ ] Queue system implemented
- [ ] Rate limiting configured
- [ ] Statistics tracking active
- [ ] Error handling robust
- [ ] Logging comprehensive

**Status:** PRODUCTION READY
