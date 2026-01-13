# Zepix Trading Bot v5.0 - Workflow Processes

## Overview

This document details the complete workflow processes within the Zepix Trading Bot, including signal processing, trade execution, profit booking, re-entry systems, and state management.

## V5 Signal → Order → Notification Flow (NEW)

The V5 architecture introduces a unified signal processing flow that routes alerts through the plugin system:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    V5 COMPLETE SIGNAL FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐                                                                │
│  │ TradingView │                                                                │
│  │   Alert     │                                                                │
│  └──────┬──────┘                                                                │
│         │                                                                       │
│         ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      WEBHOOK RECEIVER                                    │   │
│  │                    POST /webhook                                         │   │
│  │                                                                          │   │
│  │  1. Parse JSON payload                                                   │   │
│  │  2. Validate required fields (type, symbol, signal, tf)                 │   │
│  │  3. Check for duplicates (5-minute window)                              │   │
│  │  4. Route to appropriate handler                                         │   │
│  └──────────────────────────────┬──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      PLUGIN REGISTRY                                     │   │
│  │                                                                          │   │
│  │  Route by alert source:                                                  │   │
│  │  - V3 Combined Logic alerts → combined_v3 plugin                        │   │
│  │  - V6 1M Price Action → price_action_1m plugin                          │   │
│  │  - V6 5M Price Action → price_action_5m plugin                          │   │
│  │  - V6 15M Price Action → price_action_15m plugin                        │   │
│  │  - V6 1H Price Action → price_action_1h plugin                          │   │
│  │  - Trend Pulse alerts → Update market_trends table                      │   │
│  └──────────────────────────────┬──────────────────────────────────────────┘   │
│                                 │                                               │
│         ┌───────────────────────┼───────────────────────────────┐              │
│         │                       │                               │              │
│         ▼                       ▼                               ▼              │
│  ┌─────────────┐         ┌─────────────┐                 ┌─────────────┐       │
│  │    V3       │         │    V6       │                 │   Trend     │       │
│  │  Combined   │         │ Price Action│                 │   Pulse     │       │
│  │   Plugin    │         │   Plugins   │                 │   Update    │       │
│  └──────┬──────┘         └──────┬──────┘                 └─────────────┘       │
│         │                       │                                               │
│         ▼                       ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      SERVICE API LAYER                                   │   │
│  │                                                                          │   │
│  │  1. RiskManagementService.check_daily_limit()                           │   │
│  │  2. RiskManagementService.calculate_lot_size()                          │   │
│  │  3. TrendManagementService.validate_trend_alignment()                   │   │
│  │  4. MarketDataService.get_current_spread()                              │   │
│  └──────────────────────────────┬──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      ORDER EXECUTION                                     │   │
│  │                                                                          │   │
│  │  V3 Combined Logic:                                                      │   │
│  │  ├─ place_dual_orders_v3() → Order A (Smart SL) + Order B (Fixed $10)   │   │
│  │  └─ DIFFERENT SL for each order                                         │   │
│  │                                                                          │   │
│  │  V6 1M Plugin:                                                           │   │
│  │  └─ place_single_order_b() → Order B ONLY (quick scalp)                 │   │
│  │                                                                          │   │
│  │  V6 5M Plugin:                                                           │   │
│  │  └─ place_dual_orders_v6() → Order A + Order B (SAME SL)                │   │
│  │                                                                          │   │
│  │  V6 15M/1H Plugin:                                                       │   │
│  │  └─ place_single_order_a() → Order A ONLY (swing trade)                 │   │
│  └──────────────────────────────┬──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      DATABASE OPERATIONS                                 │   │
│  │                                                                          │   │
│  │  Per-Plugin Isolation:                                                   │   │
│  │  ├─ combined_v3 → data/plugins/combined_v3/zepix_v3.db                  │   │
│  │  ├─ price_action_1m → data/plugins/price_action_1m/zepix_1m.db          │   │
│  │  ├─ price_action_5m → data/plugins/price_action_5m/zepix_5m.db          │   │
│  │  ├─ price_action_15m → data/plugins/price_action_15m/zepix_15m.db       │   │
│  │  └─ price_action_1h → data/plugins/price_action_1h/zepix_1h.db          │   │
│  │                                                                          │   │
│  │  Tables: trades, orders, profit_chains, reentry_chains, sl_events       │   │
│  └──────────────────────────────┬──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      NOTIFICATION SYSTEM                                 │   │
│  │                                                                          │   │
│  │  1. NotificationRouter.route_notification()                             │   │
│  │     ├─ Determine notification type (TRADE, SIGNAL, ERROR, REPORT)       │   │
│  │     └─ Select target bot                                                 │   │
│  │                                                                          │   │
│  │  2. NotificationFormatter.format_message()                              │   │
│  │     ├─ Apply template for notification type                             │   │
│  │     └─ Include trade details, P&L, timestamps                           │   │
│  │                                                                          │   │
│  │  3. DeliveryManager.deliver()                                           │   │
│  │     ├─ Add to priority queue                                            │   │
│  │     ├─ Apply rate limiting (30 msg/sec global)                          │   │
│  │     └─ Retry on failure (3 attempts)                                    │   │
│  │                                                                          │   │
│  │  4. VoiceAlertEngine.speak() (if enabled)                               │   │
│  │     ├─ Generate TTS audio                                               │   │
│  │     └─ Send voice message to Notification Bot                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                 │                                               │
│         ┌───────────────────────┼───────────────────────────────┐              │
│         │                       │                               │              │
│         ▼                       ▼                               ▼              │
│  ┌─────────────┐         ┌─────────────┐                 ┌─────────────┐       │
│  │ Controller  │         │ Notification│                 │  Analytics  │       │
│  │    Bot      │         │    Bot      │                 │    Bot      │       │
│  │             │         │             │                 │             │       │
│  │ Status Msg  │         │ Trade Alert │                 │ Daily Report│       │
│  │ Menu Update │         │ Voice Alert │                 │ P&L Summary │       │
│  └─────────────┘         └─────────────┘                 └─────────────┘       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### V5 Notification Types

| Type | Target Bot | Priority | Voice Alert |
|------|------------|----------|-------------|
| TRADE_ENTRY | Notification | HIGH | Yes |
| TRADE_EXIT | Notification | HIGH | Yes |
| SL_HIT | Notification | CRITICAL | Yes |
| TP_HIT | Notification | HIGH | Yes |
| SIGNAL_RECEIVED | Notification | NORMAL | No |
| ERROR | Controller | CRITICAL | Yes |
| DAILY_REPORT | Analytics | LOW | No |
| PLUGIN_STATUS | Controller | NORMAL | No |

### V5 Rate Limiting

The notification system implements multi-level rate limiting:

| Level | Limit | Window |
|-------|-------|--------|
| Global | 30 messages | 1 second |
| Per Bot | 20 messages | 1 second |
| Per User | 1 message | 1 second |
| Burst | 5 messages | 100ms |

---

## Legacy Workflow (v2.0)

## 1. Application Startup Workflow

### Startup Sequence

```
Application Start
        │
        ▼
┌───────────────────────────────────────┐
│  1. Load Environment Variables        │
│     - TELEGRAM_TOKEN                  │
│     - MT5_LOGIN, MT5_PASSWORD         │
│     - MT5_SERVER                      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  2. Initialize Configuration          │
│     - Load config/config.json         │
│     - Override with env vars          │
│     - Validate settings               │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  3. Setup Logging                     │
│     - Configure rotating file handler │
│     - Set log levels                  │
│     - Initialize optimized logger     │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  4. Initialize Trading Engine         │
│     - Create MT5 Client               │
│     - Create Telegram Bot             │
│     - Create Database connection      │
│     - Initialize all managers         │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  5. Connect to MT5                    │
│     - Initialize MT5 terminal         │
│     - Login with credentials          │
│     - Verify connection               │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  6. Start Background Services         │
│     - Start Telegram polling thread   │
│     - Start Price Monitor task        │
│     - Start Trade Monitor task        │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  7. Send Startup Notification         │
│     - Send Telegram message           │
│     - Display main menu keyboard      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  8. Start FastAPI Server              │
│     - Listen on port 8000             │
│     - Ready for webhooks              │
└───────────────────────────────────────┘
```

### Startup Code Flow

```python
# main.py lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global trading_engine
    
    # Initialize trading engine
    trading_engine = TradingEngine(config)
    await trading_engine.initialize()
    
    # Start Telegram polling in separate thread
    telegram_thread = threading.Thread(
        target=trading_engine.telegram_bot.start_polling,
        daemon=True
    )
    telegram_thread.start()
    
    # Start background trade monitor
    monitor_task = asyncio.create_task(
        trading_engine.background_trade_monitor()
    )
    
    # Send startup message
    trading_engine.telegram_bot.send_startup_message()
    
    yield  # Application runs here
    
    # Shutdown
    trading_engine.telegram_bot.stop_polling()
    monitor_task.cancel()
```

## 2. Webhook Processing Workflow

### Alert Reception Flow

```
TradingView Alert
        │
        ▼
┌───────────────────────────────────────┐
│  POST /webhook                        │
│  Receive JSON payload                 │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Parse Alert Data                     │
│  - Extract type, symbol, signal, tf   │
│  - Add timestamp if missing           │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  AlertProcessor.validate_alert()      │
│  - Validate required fields           │
│  - Check symbol validity              │
│  - Check timeframe validity           │
│  - Check signal validity              │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Check for Duplicates                 │
│  - Compare with recent alerts         │
│  - 5-minute deduplication window      │
│  - Check trend manager for trends     │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Duplicate]     [Valid Alert]
        │               │
        ▼               ▼
   Return 200      Process Alert
   (Ignored)            │
                        ▼
              ┌─────────────────────┐
              │ Route by Alert Type │
              └─────────────────────┘
```

### Alert Type Routing

```
                    Alert Type
                        │
        ┌───────┬───────┼───────┬───────┐
        │       │       │       │       │
        ▼       ▼       ▼       ▼       ▼
     [bias]  [trend] [entry] [reversal] [exit]
        │       │       │       │       │
        ▼       ▼       ▼       ▼       ▼
    Update   Update  Execute  Handle   Handle
    Trend    Trend   Trades   Reversal Exit
```

## 3. Trade Execution Workflow

### Entry Signal Processing

```
Entry Alert Received
        │
        ▼
┌───────────────────────────────────────┐
│  1. Check Trading Status              │
│     - Is bot paused?                  │
│     - Is logic enabled?               │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Paused]        [Active]
        │               │
        ▼               ▼
    Return          Continue
    (Skipped)           │
                        ▼
┌───────────────────────────────────────┐
│  2. Check Risk Limits                 │
│     - Daily loss cap                  │
│     - Lifetime loss cap               │
│     - Smart lot adjustment            │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Limit Hit]     [Within Limits]
        │               │
        ▼               ▼
    Return          Continue
    (Risk Cap)          │
                        ▼
┌───────────────────────────────────────┐
│  3. Check Trend Alignment             │
│     - Detect V3 logic mode            │
│     - Get required timeframe trends   │
│     - Compare with entry direction    │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Not Aligned]   [Aligned]
        │               │
        ▼               ▼
    Return          Continue
    (Trend Mismatch)    │
                        ▼
┌───────────────────────────────────────┐
│  4. Place Fresh Order                 │
│     - Create dual orders              │
│     - Setup re-entry chain            │
│     - Setup profit chain              │
└───────────────────────────────────────┘
```

### Dual Order Creation

```
place_fresh_order(alert)
        │
        ▼
┌───────────────────────────────────────┐
│  1. Get Current Price                 │
│     - From MT5 client                 │
│     - Use alert price as fallback     │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  2. Calculate Lot Size                │
│     - Get base lot for tier           │
│     - Apply timeframe multiplier      │
│     - Check manual override           │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  3. Validate Risk                     │
│     - Check dual order risk           │
│     - Apply smart adjustment if needed│
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  4. **Order Types:**                  │
│     - **Order A (TP_TRAIL)**: Uses V3 Smart SL system, supports TP continuation
│     - **Order B (PROFIT_TRAIL)**: Uses adaptive Fixed Risk SL ($10), integrates with profit booking chains
│     - V3 Smart SL (Dynamic)           │
│     - Calculate TP using RR ratio     │
│     - Create Trade object             │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  5. Create Order B (Profit Trail)     │
│     - Fixed Risk SL ($10 max loss)    │
│     - Calculate TP for $7 target      │
│     - Create Trade object             │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  6. Place Order A in MT5              │
│     - Send order request              │
│     - Get trade_id                    │
│     - Handle success/failure          │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  7. Place Order B in MT5              │
│     - Independent of Order A result   │
│     - Send order request              │
│     - Get trade_id                    │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  8. Create Re-entry Chain             │
│     - Shared chain for both orders    │
│     - Store original entry/SL         │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  9. Create Profit Chain (Order B)     │
│     - Initialize at Level 0           │
│     - Link to Order B                 │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  10. Save to Database                 │
│      - Save trades                    │
│      - Save chains                    │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  11. Send Notifications               │
│      - Telegram message               │
│      - Include trade details          │
└───────────────────────────────────────┘
```

## 4. Profit Booking Workflow

### Profit Chain Lifecycle

```
Order B Placed (PROFIT_TRAIL)
        │
        ▼
┌───────────────────────────────────────┐
│  Create Profit Chain                  │
│  - chain_id: unique identifier        │
│  - current_level: 0                   │
│  - base_lot: order lot size           │
│  - status: ACTIVE                     │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Monitor for Profit Target            │
│  - Check every 30 seconds             │
│  - Calculate current PnL              │
│  - Compare with $7 target             │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [PnL < $7]      [PnL >= $7]
        │               │
        ▼               ▼
    Continue        Book Profit
    Monitoring          │
                        ▼
┌───────────────────────────────────────┐
│  Book Individual Order                │
│  - Close order in MT5                 │
│  - Record profit                      │
│  - Update chain total_profit          │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Check Level Completion               │
│  - Are all orders at level closed?    │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Not All]       [All Closed]
        │               │
        ▼               ▼
    Continue        Progress Chain
    Monitoring          │
                        ▼
┌───────────────────────────────────────┐
│  Progress to Next Level               │
│  - Increment current_level            │
│  - Calculate new order count (2x)     │
│  - Place new orders                   │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Level < 4]     [Level = 4]
        │               │
        ▼               ▼
    Continue        Complete Chain
    (New Level)     (Max Level)
```

### Level Progression Detail

```
Level 0 (1 order)
        │
        ▼ Order reaches $7
        │
┌───────────────────────────────────────┐
│  Close Level 0 Order                  │
│  Profit: $7                           │
└───────────────┬───────────────────────┘
                │
                ▼
Level 1 (2 orders)
        │
        ▼ Both orders reach $7
        │
┌───────────────────────────────────────┐
│  Close Level 1 Orders                 │
│  Profit: $14 (2 x $7)                 │
│  Total: $21                           │
└───────────────┬───────────────────────┘
                │
                ▼
Level 2 (4 orders)
        │
        ▼ All orders reach $7
        │
┌───────────────────────────────────────┐
│  Close Level 2 Orders                 │
│  Profit: $28 (4 x $7)                 │
│  Total: $49                           │
└───────────────┬───────────────────────┘
                │
                ▼
Level 3 (8 orders)
        │
        ▼ All orders reach $7
        │
┌───────────────────────────────────────┐
│  Close Level 3 Orders                 │
│  Profit: $56 (8 x $7)                 │
│  Total: $105                          │
└───────────────┬───────────────────────┘
                │
                ▼
Level 4 (16 orders)
        │
        ▼ All orders reach $7
        │
┌───────────────────────────────────────┐
│  Close Level 4 Orders                 │
│  Profit: $112 (16 x $7)               │
│  Total: $217                          │
│  Chain COMPLETED                      │
└───────────────────────────────────────┘
```

## 5. Re-entry Workflow

### SL Hunt Recovery Process

```
SL Hit Detected
        │
        ▼
┌───────────────────────────────────────┐
│  Record SL Hit                        │
│  - Save to sl_events table            │
│  - Update chain status                │
│  - Set recovery_mode                  │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Check Recovery Eligibility           │
│  - Is SL hunt enabled?                │
│  - Within daily limits?               │
│  - Concurrent recovery limit?         │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Not Eligible]  [Eligible]
        │               │
        ▼               ▼
    Stop Chain      Start Recovery
                    Monitoring
                        │
                        ▼
┌───────────────────────────────────────┐
│  Start Recovery Window                │
│  - Window: 60 minutes (configurable)  │
│  - Monitor price every 30 seconds     │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Calculate Recovery Percentage        │
│                                       │
│  For BUY trade:                       │
│  recovery = (current - sl) /          │
│             (entry - sl)              │
│                                       │
│  For SELL trade:                      │
│  recovery = (sl - current) /          │
│             (sl - entry)              │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [< 70%]         [>= 70%]
        │               │
        ▼               ▼
    Continue        Place Recovery
    Monitoring      Trade
                        │
                        ▼
┌───────────────────────────────────────┐
│  Place Recovery Trade                 │
│  - Same direction as original         │
│  - Reduced SL (by configured %)       │
│  - New TP based on RR ratio           │
│  - Update chain level                 │
└───────────────────────────────────────┘
```

### TP Continuation Process

```
TP Hit Detected
        │
        ▼
┌───────────────────────────────────────┐
│  Record TP Hit                        │
│  - Save to tp_reentry_events          │
│  - Update chain                       │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Check Continuation Eligibility       │
│  - Is TP continuation enabled?        │
│  - Is trend still aligned?            │
│  - Within max levels?                 │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Not Eligible]  [Eligible]
        │               │
        ▼               ▼
    Complete        Place Continuation
    Chain           Trade
                        │
                        ▼
┌───────────────────────────────────────┐
│  Calculate Continuation Parameters    │
│  - Get SL reduction for level         │
│  - Apply reduction to original SL     │
│  - Calculate new TP                   │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Place Continuation Trade             │
│  - Same direction                     │
│  - Reduced SL                         │
│  - New TP                             │
│  - Increment chain level              │
└───────────────────────────────────────┘
```

### Exit Continuation Process

```
Exit Signal Received
        │
        ▼
┌───────────────────────────────────────┐
│  Close Opposing Trades                │
│  - Execute reversal exit              │
│  - Record exit reason                 │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Register Exit Continuation           │
│  - Store exit price                   │
│  - Store original direction           │
│  - Start monitoring window            │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Monitor for Price Gap                │
│  - Check every 30 seconds             │
│  - Calculate gap from exit price      │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Gap < Min]     [Gap >= Min]
        │               │
        ▼               ▼
    Continue        Place Re-entry
    Monitoring      Trade
                        │
                        ▼
┌───────────────────────────────────────┐
│  Place Exit Continuation Trade        │
│  - Same direction as original         │
│  - Tighter SL                         │
│  - New TP                             │
└───────────────────────────────────────┘
```

## 6. Trend Management Workflow

### Trend Update Process

```
Trend/Bias Alert Received
        │
        ▼
┌───────────────────────────────────────┐
│  Parse Trend Information              │
│  - Symbol                             │
│  - Timeframe                          │
│  - Direction (bull/bear)              │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Check Current Mode                   │
│  - Get mode for symbol/timeframe      │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [MANUAL]         [AUTO]
        │               │
        ▼               ▼
    Skip Update     Update Trend
    (Locked)            │
                        ▼
┌───────────────────────────────────────┐
│  Update Trend State                   │
│  - Set new trend direction            │
│  - Keep mode as AUTO                  │
│  - Save to timeframe_trends.json      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Send Notification                    │
│  - Telegram message                   │
│  - Include symbol, timeframe, trend   │
└───────────────────────────────────────┘
```

### Trend Alignment Check

```
check_logic_alignment(symbol, direction, logic)
        │
        ▼
┌───────────────────────────────────────┐
│  Determine Required Timeframes        │
│                                       │
│  LOGIC1: 1H + 15M                     │
│  LOGIC2: 1H + 15M                     │
│  LOGIC3: 1D + 1H                      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Get Current Trends                   │
│  - Fetch from trend_manager           │
│  - For each required timeframe        │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Compare with Entry Direction         │
│                                       │
│  BUY entry requires:                  │
│  - All required TFs = BULLISH         │
│                                       │
│  SELL entry requires:                 │
│  - All required TFs = BEARISH         │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Mismatch]      [Aligned]
        │               │
        ▼               ▼
    Return          Return
    False           True
```

## 7. Risk Management Workflow

### Trade Risk Validation

```
validate_dual_orders(lot_size, symbol)
        │
        ▼
┌───────────────────────────────────────┐
│  Get Account Balance                  │
│  - From MT5 client                    │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Calculate Expected Risk              │
│  - Order A risk                       │
│  - Order B risk                       │
│  - Combined risk                      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Check Daily Limit                    │
│  - Get remaining daily allowance      │
│  - Compare with combined risk         │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Exceeds]        [Within]
        │               │
        ▼               ▼
    Apply Smart     Return
    Adjustment      Valid
        │
        ▼
┌───────────────────────────────────────┐
│  Smart Lot Adjustment                 │
│  - Calculate max safe lot             │
│  - Reduce lot size                    │
│  - Recalculate risk                   │
└───────────────┬───────────────────────┘
                │
                ▼
    Return Adjusted Lot
```

### Loss Tracking

```
record_trade_result(trade, pnl)
        │
        ▼
┌───────────────────────────────────────┐
│  Check if Loss                        │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   [Profit]         [Loss]
        │               │
        ▼               ▼
    Update          Update Loss
    daily_profit    Counters
                        │
                        ▼
┌───────────────────────────────────────┐
│  Update Daily Loss                    │
│  daily_loss += abs(pnl)               │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Update Lifetime Loss                 │
│  lifetime_loss += abs(pnl)            │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Save Stats                           │
│  - Write to data/stats.json           │
│  - Verify write success               │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Check Limits                         │
│  - Daily cap reached?                 │
│  - Lifetime cap reached?              │
│  - Send notification if hit           │
└───────────────────────────────────────┘
```

## 8. Background Monitoring Workflow

### Price Monitor Loop

```
_monitor_loop() [Every 30 seconds]
        │
        ▼
┌───────────────────────────────────────┐
│  Check All Opportunities              │
└───────────────┬───────────────────────┘
                │
        ┌───────┼───────┬───────┐
        │       │       │       │
        ▼       ▼       ▼       ▼
   [SL Hunt] [TP Cont] [Exit] [Profit]
        │       │       │       │
        ▼       ▼       ▼       ▼
    Check    Check    Check   Check
    Recovery Contin.  Contin. Targets
        │       │       │       │
        └───────┴───────┴───────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Sleep 30 seconds                     │
└───────────────┬───────────────────────┘
                │
                ▼
            Loop Back
```

### Autonomous System Checks

```
run_autonomous_checks(open_trades)
        │
        ▼
┌───────────────────────────────────────┐
│  1. Monitor TP Continuation           │
│     - Check active chains             │
│     - Verify trend alignment          │
│     - Place continuation orders       │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  2. Monitor Profit Booking SL Hunt    │
│     - Check profit chain orders       │
│     - Start recovery monitoring       │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  3. Monitor Profit Booking Targets    │
│     - Check PnL for each order        │
│     - Book orders at $7 profit        │
│     - Progress chains                 │
└───────────────────────────────────────┘
```

## 9. State Management

### Configuration State

```
Configuration Loading
        │
        ▼
┌───────────────────────────────────────┐
│  Load config/config.json              │
│  - Parse JSON                         │
│  - Validate structure                 │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Override with Environment            │
│  - Check for env vars                 │
│  - Override matching keys             │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Store in Memory                      │
│  - Config object accessible           │
│  - Hot reload supported               │
└───────────────────────────────────────┘
```

### Trend State Persistence

```
Trend Update
        │
        ▼
┌───────────────────────────────────────┐
│  Update In-Memory State               │
│  - trends[symbol][timeframe]          │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Save to File                         │
│  - Write timeframe_trends.json        │
│  - Atomic write (temp file)           │
└───────────────────────────────────────┘

Application Restart
        │
        ▼
┌───────────────────────────────────────┐
│  Load from File                       │
│  - Read timeframe_trends.json         │
│  - Restore trend state                │
└───────────────────────────────────────┘
```

### Risk Statistics Persistence

```
Trade Closed
        │
        ▼
┌───────────────────────────────────────┐
│  Update Statistics                    │
│  - daily_loss / daily_profit          │
│  - lifetime_loss                      │
│  - total_trades / winning_trades      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Save to File                         │
│  - Write data/stats.json              │
│  - Retry on failure                   │
│  - Verify write                       │
└───────────────────────────────────────┘

Daily Reset Check
        │
        ▼
┌───────────────────────────────────────┐
│  Check Date                           │
│  - Compare last_reset_date            │
│  - If new day, reset daily stats      │
└───────────────────────────────────────┘
```

## 10. Shutdown Workflow

```
Shutdown Signal Received
        │
        ▼
┌───────────────────────────────────────┐
│  1. Stop Telegram Polling             │
│     - Set running = False             │
│     - Wait for thread to finish       │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  2. Cancel Background Tasks           │
│     - Cancel monitor task             │
│     - Cancel price monitor            │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  3. Save Final State                  │
│     - Save risk statistics            │
│     - Save trend state                │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  4. Close Connections                 │
│     - Close MT5 connection            │
│     - Close database connection       │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  5. Send Shutdown Notification        │
│     - Telegram message (if possible)  │
└───────────────────────────────────────┘
```

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [FEATURES_SPECIFICATION.md](FEATURES_SPECIFICATION.md) - Feature catalog
- [BOT_WORKING_SCENARIOS.md](BOT_WORKING_SCENARIOS.md) - Execution scenarios
