# Zepix Trading Bot v2.0 - Bot Working Scenarios

## Overview

This document provides detailed scenarios of how the Zepix Trading Bot operates in various situations. It covers trade execution scenarios, background processes, logic flows, and edge cases to help understand the bot's behavior in real-world trading conditions.

## Scenario Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOT WORKING SCENARIOS                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Trade Execution Scenarios                                   │
│  2. Profit Booking Scenarios                                    │
│  3. Re-entry Scenarios                                          │
│  4. Risk Management Scenarios                                   │
│  5. Background Process Scenarios                                │
│  6. Edge Cases and Special Situations                           │
│  7. Multi-Symbol Scenarios                                      │
│  8. Recovery Scenarios                                          │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Trade Execution Scenarios

### Scenario 1.1: Successful LOGIC2 Entry

**Context:** XAUUSD 15-minute entry signal with aligned trends.

**Initial State:**
- Bot: Running
- LOGIC2: Enabled
- 1H Trend: BULLISH
- 15M Trend: BULLISH
- Account Balance: $10,000

**Incoming Alert:**
```json
{
    "type": "entry",
    "symbol": "XAUUSD",
    "signal": "buy",
    "tf": "15m"
}
```

**Execution Flow:**

```
Step 1: Alert Reception
        │
        ▼
┌───────────────────────────────────────┐
│ Webhook receives alert                │
│ Validate JSON format                  │
│ Check for duplicates (5-min window)   │
└───────────────────┬───────────────────┘
                    │ Valid, not duplicate
                    ▼
Step 2: Alert Processing
        │
        ▼
┌───────────────────────────────────────┐
│ Identify alert type: ENTRY            │
│ Map symbol: XAUUSD → GOLD             │
│ Determine logic: LOGIC2 (15m entry)   │
└───────────────────┬───────────────────┘
                    │
                    ▼
Step 3: Trend Alignment Check
        │
        ▼
┌───────────────────────────────────────┐
│ LOGIC2 requires: 1H + 15M alignment   │
│ Check 1H trend: BULLISH ✓             │
│ Check 15M trend: BULLISH ✓            │
│ Direction: BUY matches trends ✓       │
└───────────────────┬───────────────────┘
                    │ Aligned
                    ▼
Step 4: Risk Validation
        │
        ▼
┌───────────────────────────────────────┐
│ Check daily loss cap: $15/$200 ✓      │
│ Check lifetime loss: $85/$1000 ✓      │
│ Calculate lot size: 0.10 (tier-based) │
│ Validate margin: Sufficient ✓         │
└───────────────────┬───────────────────┘
                    │ Approved
                    ▼
Step 5: Dual Order Execution
        │
        ▼
┌───────────────────────────────────────┐
│ Get current price: 2650.00            │
│ Calculate SL: 2640.00 (100 pips)      │
│ Calculate TP-A: 2665.00 (RR 1:1.5)    │
│ Calculate TP-B: 2657.00 (70% of TP)   │
└───────────────────┬───────────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
┌─────────────────┐   ┌─────────────────┐
│ Order A (TP)    │   │ Order B (Profit)│
│ Lot: 0.10       │   │ Lot: 0.10       │
│ Entry: 2650.00  │   │ Entry: 2650.00  │
│ SL: 2640.00     │   │ SL: 2640.00     │
│ TP: 2665.00     │   │ TP: 2657.00     │
│ Ticket: 12345   │   │ Ticket: 12346   │
└─────────────────┘   └─────────────────┘
                    │
                    ▼
Step 6: Post-Execution
        │
        ▼
┌───────────────────────────────────────┐
│ Create re-entry chain                 │
│ Create profit booking chain           │
│ Log trade execution                   │
│ Send Telegram notification            │
└───────────────────────────────────────┘
```

**Result:**
- 2 orders placed (Order A and Order B)
- Re-entry chain created for recovery tracking
- Profit booking chain created for Order B
- User notified via Telegram

---

### Scenario 1.2: Entry Rejected - Trend Not Aligned

**Context:** EURUSD 15-minute entry signal with misaligned trends.

**Initial State:**
- Bot: Running
- LOGIC2: Enabled
- 1H Trend: BEARISH
- 15M Trend: BULLISH

**Incoming Alert:**
```json
{
    "type": "entry",
    "symbol": "EURUSD",
    "signal": "buy",
    "tf": "15m"
}
```

**Execution Flow:**

```
Step 1-2: Alert Reception & Processing
          │
          ▼ (Same as Scenario 1.1)

Step 3: Trend Alignment Check
        │
        ▼
┌───────────────────────────────────────┐
│ LOGIC2 requires: 1H + 15M alignment   │
│ Check 1H trend: BEARISH ✗             │
│ BUY signal requires BULLISH 1H        │
│ ALIGNMENT FAILED                      │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│ Skip trade execution                  │
│ Log: "Trend not aligned for EURUSD"   │
│ Return: {"status": "skipped"}         │
└───────────────────────────────────────┘
```

**Result:**
- No trade executed
- Warning logged
- No notification sent (configurable)

---

### Scenario 1.3: Entry Rejected - Daily Loss Cap

**Context:** Valid entry signal but daily loss cap reached.

**Initial State:**
- Bot: Running
- Daily Loss: $195 (of $200 cap)
- Potential risk: $20

**Execution Flow:**

```
Step 1-3: Alert Reception, Processing, Alignment
          │
          ▼ (All pass)

Step 4: Risk Validation
        │
        ▼
┌───────────────────────────────────────┐
│ Check daily loss cap                  │
│ Current: $195                         │
│ Cap: $200                             │
│ Potential risk: $20                   │
│ Would exceed cap: $195 + $20 > $200   │
│ RISK CHECK FAILED                     │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│ Skip trade execution                  │
│ Log: "Daily loss cap would exceed"    │
│ Send warning notification             │
│ Return: {"status": "risk_limit"}      │
└───────────────────────────────────────┘
```

**Result:**
- No trade executed
- User warned about risk limit
- Trading continues for lower-risk opportunities

---

## 2. Profit Booking Scenarios

### Scenario 2.1: Complete Profit Booking Chain

**Context:** Order B progresses through all 5 levels of profit booking.

**Initial State:**
- Order B opened at 2650.00
- Direction: BUY
- Lot: 0.10
- Profit target: $7 per order

**Progression Flow:**

```
LEVEL 0 (Initial)
┌─────────────────────────────────────────────────────────────┐
│ Orders: 1 × 0.10 lot                                        │
│ Price moves to 2657.00 (+$7 profit)                         │
│ Order reaches $7 target                                     │
│ ACTION: Close order, book $7 profit                         │
│ PROGRESS: Move to Level 1                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
LEVEL 1 (2× multiplier)
┌─────────────────────────────────────────────────────────────┐
│ Open 2 new orders × 0.10 lot each                           │
│ SL reduced by 10%: 2641.00                                  │
│ Price continues up, both orders reach $7                    │
│ ACTION: Close both orders, book $14 profit                  │
│ PROGRESS: Move to Level 2                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
LEVEL 2 (4× multiplier)
┌─────────────────────────────────────────────────────────────┐
│ Open 4 new orders × 0.10 lot each                           │
│ SL reduced by 25%: 2642.50                                  │
│ Price continues up, all 4 orders reach $7                   │
│ ACTION: Close all orders, book $28 profit                   │
│ PROGRESS: Move to Level 3                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
LEVEL 3 (8× multiplier)
┌─────────────────────────────────────────────────────────────┐
│ Open 8 new orders × 0.10 lot each                           │
│ SL reduced by 40%: 2644.00                                  │
│ Price continues up, all 8 orders reach $7                   │
│ ACTION: Close all orders, book $56 profit                   │
│ PROGRESS: Move to Level 4                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
LEVEL 4 (16× multiplier) - FINAL
┌─────────────────────────────────────────────────────────────┐
│ Open 16 new orders × 0.10 lot each                          │
│ SL reduced by 50%: 2645.00                                  │
│ Price continues up, all 16 orders reach $7                  │
│ ACTION: Close all orders, book $112 profit                  │
│ CHAIN COMPLETE                                              │
└─────────────────────────────────────────────────────────────┘

TOTAL PROFIT: $7 + $14 + $28 + $56 + $112 = $217
TOTAL ORDERS: 1 + 2 + 4 + 8 + 16 = 31 orders
```

---

### Scenario 2.2: Profit Chain Interrupted by SL

**Context:** Profit chain at Level 2 when price reverses and hits SL.

**State at Level 2:**
- 4 orders open
- SL at 2642.50
- Current profit: $21 (Level 0 + Level 1)

**Event Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ Price reverses from 2660.00                                 │
│ Price drops to 2642.50 (SL level)                           │
│ All 4 Level 2 orders hit SL                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PROFIT BOOKING SL HUNT TRIGGERED                            │
│ Record SL hit for profit chain                              │
│ Start recovery monitoring                                   │
│ Recovery threshold: 70% of SL distance                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Monitor price for recovery                                  │
│ If price recovers to 2654.75 (70% recovery)                 │
│ → Re-enter at Level 2 with reduced SL                       │
│ If recovery window expires (60 min)                         │
│ → Chain terminated, keep booked profit                      │
└─────────────────────────────────────────────────────────────┘
```

**Possible Outcomes:**
1. **Recovery Success:** Re-enter at Level 2, continue chain
2. **Recovery Fail:** Chain ends, $21 profit kept

---

## 3. Re-entry Scenarios

### Scenario 3.1: SL Hunt Recovery Success

**Context:** Trade hits SL, price recovers, bot re-enters.

**Initial Trade:**
- Symbol: XAUUSD
- Direction: BUY
- Entry: 2650.00
- SL: 2640.00
- Status: SL HIT at 2640.00

**Recovery Flow:**

```
T+0: SL Hit
┌─────────────────────────────────────────────────────────────┐
│ Order closed at SL: 2640.00                                 │
│ Loss recorded: -$10                                         │
│ SL Hunt Recovery activated                                  │
│ Recovery threshold: 70% = 2647.00                           │
│ Recovery window: 60 minutes                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
T+15min: Price Monitoring
┌─────────────────────────────────────────────────────────────┐
│ Current price: 2643.00                                      │
│ Recovery: 30% (not enough)                                  │
│ Continue monitoring...                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
T+30min: Recovery Threshold Reached
┌─────────────────────────────────────────────────────────────┐
│ Current price: 2648.00                                      │
│ Recovery: 80% (exceeds 70% threshold)                       │
│ TRIGGER RE-ENTRY                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Recovery Entry Execution
┌─────────────────────────────────────────────────────────────┐
│ Check trend alignment: Still aligned ✓                      │
│ Check risk limits: Within limits ✓                          │
│ Calculate new SL: 2640.00 - 20% = 2638.00                   │
│ Execute recovery trade                                      │
│                                                             │
│ New Order:                                                  │
│   Entry: 2648.00                                            │
│   SL: 2638.00 (reduced by 20%)                              │
│   TP: 2663.00                                               │
│   Lot: 0.10                                                 │
└─────────────────────────────────────────────────────────────┘
```

**Result:**
- Recovery trade placed
- Chain level incremented
- Monitoring continues for new trade

---

### Scenario 3.2: TP Continuation

**Context:** Trade hits TP, bot continues with new entry.

**Initial Trade:**
- Symbol: EURUSD
- Direction: BUY
- Entry: 1.0850
- TP: 1.0880
- Status: TP HIT

**Continuation Flow:**

```
T+0: TP Hit
┌─────────────────────────────────────────────────────────────┐
│ Order closed at TP: 1.0880                                  │
│ Profit recorded: +$30                                       │
│ TP Continuation check triggered                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Continuation Eligibility Check
┌─────────────────────────────────────────────────────────────┐
│ TP Continuation enabled: ✓                                  │
│ Chain level: 0 (max: 5) ✓                                   │
│ Trend still aligned: ✓                                      │
│ Daily limits OK: ✓                                          │
│ ELIGIBLE FOR CONTINUATION                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Continuation Entry
┌─────────────────────────────────────────────────────────────┐
│ New entry at current price: 1.0882                          │
│ SL reduced by 10%: 1.0855 (was 1.0850)                      │
│ New TP: 1.0912                                              │
│ Chain level: 1                                              │
│                                                             │
│ Continue until:                                             │
│   - Max level reached (5)                                   │
│   - Trend changes                                           │
│   - SL hit                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

### Scenario 3.3: Exit Continuation

**Context:** Exit signal received, bot waits for re-entry opportunity.

**State:**
- Active BUY trade on XAUUSD
- Exit signal received (BEAR)

**Flow:**

```
T+0: Exit Signal Received
┌─────────────────────────────────────────────────────────────┐
│ Alert: {"type": "exit", "signal": "bear", "tf": "15m"}      │
│ Close all BUY positions for XAUUSD                          │
│ Profit/Loss recorded                                        │
│ Exit Continuation activated                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Exit Continuation Monitoring
┌─────────────────────────────────────────────────────────────┐
│ Wait for price gap: 20 pips minimum                         │
│ Max wait time: 30 minutes                                   │
│ Direction: SELL (opposite of closed BUY)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
T+10min: Gap Detected
┌─────────────────────────────────────────────────────────────┐
│ Exit price: 2655.00                                         │
│ Current price: 2652.00                                      │
│ Gap: 30 pips (exceeds 20 pip minimum)                       │
│ Check trend: 15M now BEARISH ✓                              │
│ TRIGGER SELL ENTRY                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
New SELL Trade
┌─────────────────────────────────────────────────────────────┐
│ Entry: 2652.00                                              │
│ Direction: SELL                                             │
│ SL: 2662.00                                                 │
│ TP: 2637.00                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Risk Management Scenarios

### Scenario 4.1: Daily Loss Cap Reached

**Context:** Multiple losing trades reach daily cap.

**Flow:**

```
Trade 1: -$50 (Daily: $50/$200)
Trade 2: -$45 (Daily: $95/$200)
Trade 3: -$60 (Daily: $155/$200)
Trade 4: -$50 (Daily: $205/$200) ← EXCEEDS CAP
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ DAILY LOSS CAP EXCEEDED                                     │
│                                                             │
│ Actions:                                                    │
│ 1. Block new trade entries                                  │
│ 2. Keep existing trades open                                │
│ 3. Continue profit booking on existing                      │
│ 4. Send critical notification                               │
│ 5. Log critical event                                       │
│                                                             │
│ Trading resumes: Next day (midnight reset)                  │
└─────────────────────────────────────────────────────────────┘
```

---

### Scenario 4.2: Smart Lot Adjustment

**Context:** Account balance changes, lot size adjusts.

**Flow:**

```
Initial State:
  Balance: $10,500
  Tier: $10,000
  Base Lot: 0.10

After Profits:
  Balance: $25,200
  New Tier: $25,000
  New Base Lot: 0.25

┌─────────────────────────────────────────────────────────────┐
│ TIER UPGRADE DETECTED                                       │
│                                                             │
│ Previous: $10,000 tier (0.10 lot)                           │
│ Current: $25,000 tier (0.25 lot)                            │
│                                                             │
│ New trades will use:                                        │
│   LOGIC1: 0.25 × 1.25 = 0.3125 lot                          │
│   LOGIC2: 0.25 × 1.0 = 0.25 lot                             │
│   LOGIC3: 0.25 × 0.625 = 0.15625 lot                        │
│                                                             │
│ Existing trades: Unchanged                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Background Process Scenarios

### Scenario 5.1: Price Monitor Loop

**Context:** Background service monitoring prices every 30 seconds.

**Continuous Loop:**

```
┌─────────────────────────────────────────────────────────────┐
│                    PRICE MONITOR LOOP                       │
│                    (Every 30 seconds)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Get all active re-entry chains                           │
│    - SL Hunt chains in MONITORING state                     │
│    - TP Continuation chains                                 │
│    - Exit Continuation chains                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. For each chain, get current price                        │
│    - Query MT5 for symbol price                             │
│    - Calculate recovery percentage                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Check recovery conditions                                │
│    - Has price recovered enough? (70% threshold)            │
│    - Is recovery window still open? (60 min)                │
│    - Is trend still aligned?                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Execute actions                                          │
│    - Trigger re-entry if conditions met                     │
│    - Expire chain if window closed                          │
│    - Update chain status                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Check profit booking chains                              │
│    - Get PnL for each order                                 │
│    - Close orders at $7 profit                              │
│    - Progress chains to next level                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    [Wait 30 seconds]
                              │
                              ▼
                    [Repeat Loop]
```

---

### Scenario 5.2: Autonomous System Coordination

**Context:** Multiple systems operating simultaneously.

**Coordination Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│              AUTONOMOUS SYSTEM MANAGER                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ SL Hunt       │     │ TP Cont       │     │ Profit Book   │
│ Recovery      │     │ System        │     │ System        │
│               │     │               │     │               │
│ 2 chains      │     │ 1 chain       │     │ 3 chains      │
│ monitoring    │     │ active        │     │ active        │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ COORDINATION RULES:                                         │
│                                                             │
│ 1. Max concurrent recoveries: 3                             │
│ 2. Daily recovery limit: 10                                 │
│ 3. Profit protection: 5× multiplier                         │
│ 4. Priority: Profit booking > TP Cont > SL Hunt             │
│                                                             │
│ Current Status:                                             │
│   Active recoveries: 2/3 ✓                                  │
│   Daily recoveries: 5/10 ✓                                  │
│   Profit chains: 3 active                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Edge Cases and Special Situations

### Scenario 6.1: Duplicate Alert Handling

**Context:** Same alert received twice within 5 minutes.

**Flow:**

```
T+0: First Alert
┌─────────────────────────────────────────────────────────────┐
│ Alert: {"type":"entry","symbol":"XAUUSD","signal":"buy"}    │
│ Generate hash: abc123                                       │
│ Check cache: Not found                                      │
│ Store in cache with 5-min expiry                            │
│ Process alert → Execute trade                               │
└─────────────────────────────────────────────────────────────┘

T+2min: Duplicate Alert
┌─────────────────────────────────────────────────────────────┐
│ Alert: {"type":"entry","symbol":"XAUUSD","signal":"buy"}    │
│ Generate hash: abc123                                       │
│ Check cache: FOUND (expires in 3 min)                       │
│ REJECT as duplicate                                         │
│ Log: "Duplicate alert detected"                             │
│ Return: {"status": "duplicate"}                             │
└─────────────────────────────────────────────────────────────┘

T+6min: Same Alert (After Expiry)
┌─────────────────────────────────────────────────────────────┐
│ Alert: {"type":"entry","symbol":"XAUUSD","signal":"buy"}    │
│ Generate hash: abc123                                       │
│ Check cache: Not found (expired)                            │
│ Process as new alert                                        │
└─────────────────────────────────────────────────────────────┘
```

---

### Scenario 6.2: MT5 Disconnection During Trade

**Context:** MT5 connection lost while placing order.

**Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ Attempting to place order...                                │
│ MT5 connection lost mid-execution                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ ERROR HANDLING:                                             │
│                                                             │
│ 1. Catch connection exception                               │
│ 2. Log error with details                                   │
│ 3. Attempt reconnection (3 retries)                         │
│ 4. If reconnected:                                          │
│    - Check if order was placed                              │
│    - If not, retry order placement                          │
│ 5. If reconnection fails:                                   │
│    - Send critical notification                             │
│    - Mark bot as disconnected                               │
│    - Continue monitoring for reconnection                   │
└─────────────────────────────────────────────────────────────┘
```

---

### Scenario 6.3: Reversal Signal During Active Trade

**Context:** Reversal signal received while trade is open.

**Flow:**

```
Active State:
  - BUY trade open on XAUUSD
  - Entry: 2650.00
  - Current PnL: +$15

Incoming Alert:
  {"type": "reversal", "symbol": "XAUUSD", "signal": "reversal_bear"}

┌─────────────────────────────────────────────────────────────┐
│ REVERSAL EXIT HANDLER                                       │
│                                                             │
│ 1. Identify all BUY positions for XAUUSD                    │
│ 2. Check if profitable (PnL > 0)                            │
│ 3. Close all positions immediately                          │
│ 4. Book profit: +$15                                        │
│ 5. Update statistics                                        │
│ 6. Send notification                                        │
│                                                             │
│ Note: Does NOT open reverse position automatically          │
│       Waits for proper entry signal                         │
└─────────────────────────────────────────────────────────────┘
```

---

### Scenario 6.4: Panic Close Execution

**Context:** User triggers emergency close.

**Flow:**

```
User Command: /panic_close

┌─────────────────────────────────────────────────────────────┐
│ PANIC CLOSE INITIATED                                       │
│                                                             │
│ Step 1: Pause all trading immediately                       │
│ Step 2: Get all open positions                              │
│ Step 3: Close each position at market                       │
│ Step 4: Stop all re-entry chains                            │
│ Step 5: Stop all profit booking chains                      │
│ Step 6: Record all closures                                 │
│ Step 7: Calculate total PnL                                 │
│ Step 8: Send summary notification                           │
│                                                             │
│ Result:                                                     │
│   Positions closed: 5                                       │
│   Chains stopped: 3                                         │
│   Total PnL: +$45                                           │
│   Bot status: PAUSED                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Multi-Symbol Scenarios

### Scenario 7.1: Simultaneous Entries on Multiple Symbols

**Context:** Entry signals for XAUUSD and EURUSD arrive within seconds.

**Flow:**

```
T+0.0s: XAUUSD Entry Alert
T+0.5s: EURUSD Entry Alert

┌─────────────────────────────────────────────────────────────┐
│ PARALLEL PROCESSING                                         │
│                                                             │
│ Both alerts processed independently:                        │
│                                                             │
│ XAUUSD:                                                     │
│   - Check trends: Aligned ✓                                 │
│   - Check risk: OK ✓                                        │
│   - Execute: 2 orders placed                                │
│                                                             │
│ EURUSD:                                                     │
│   - Check trends: Aligned ✓                                 │
│   - Check risk: OK ✓ (after XAUUSD)                         │
│   - Execute: 2 orders placed                                │
│                                                             │
│ Total: 4 orders across 2 symbols                            │
└─────────────────────────────────────────────────────────────┘
```

---

### Scenario 7.2: Symbol-Specific Trend Management

**Context:** Different trends for different symbols.

**State:**

```
┌─────────────────────────────────────────────────────────────┐
│ TREND STATE BY SYMBOL                                       │
├─────────────────────────────────────────────────────────────┤
│ XAUUSD:                                                     │
│   1H: BULLISH | 15M: BULLISH | 5M: BULLISH                  │
│   → BUY entries allowed for all logics                      │
│                                                             │
│ EURUSD:                                                     │
│   1H: BEARISH | 15M: BULLISH | 5M: NEUTRAL                  │
│   → Only SELL entries allowed (1H dominant)                 │
│                                                             │
│ GBPUSD:                                                     │
│   1H: NEUTRAL | 15M: NEUTRAL | 5M: BEARISH                  │
│   → No entries allowed (no clear trend)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Recovery Scenarios

### Scenario 8.1: Bot Restart with Active Trades

**Context:** Bot restarts while trades are open.

**Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ BOT STARTUP RECOVERY                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Load configuration                                       │
│ 2. Connect to MT5                                           │
│ 3. Query open positions from MT5                            │
│ 4. Load chain states from database                          │
│ 5. Reconcile positions with chains                          │
│ 6. Resume monitoring for active chains                      │
│ 7. Start background services                                │
│ 8. Send startup notification                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ RECONCILIATION RESULTS:                                     │
│                                                             │
│ MT5 Positions: 3                                            │
│ Database Chains: 2                                          │
│ Matched: 2 chains with positions                            │
│ Orphaned: 1 position (no chain)                             │
│                                                             │
│ Action: Create chain for orphaned position                  │
│ Status: All positions now tracked                           │
└─────────────────────────────────────────────────────────────┘
```

---

### Scenario 8.2: Database Recovery

**Context:** Database corruption detected.

**Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ DATABASE ERROR DETECTED                                     │
│ Error: "database disk image is malformed"                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ RECOVERY PROCEDURE:                                         │
│                                                             │
│ 1. Log critical error                                       │
│ 2. Backup corrupted database                                │
│ 3. Attempt integrity check                                  │
│ 4. If recoverable:                                          │
│    - Run VACUUM and REINDEX                                 │
│    - Verify data integrity                                  │
│ 5. If not recoverable:                                      │
│    - Create new database                                    │
│    - Rebuild from MT5 positions                             │
│ 6. Resume operations                                        │
│ 7. Notify user of recovery                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

This document has covered the major working scenarios of the Zepix Trading Bot, including:

1. **Trade Execution:** How trades are validated, executed, and managed
2. **Profit Booking:** The pyramid system progression and interruption handling
3. **Re-entry Systems:** SL Hunt, TP Continuation, and Exit Continuation flows
4. **Risk Management:** Daily/lifetime caps and smart lot adjustment
5. **Background Processes:** Price monitoring and autonomous coordination
6. **Edge Cases:** Duplicates, disconnections, reversals, and panic close
7. **Multi-Symbol:** Parallel processing and symbol-specific management
8. **Recovery:** Startup reconciliation and database recovery

Understanding these scenarios is essential for:
- Troubleshooting unexpected behavior
- Optimizing configuration for specific trading styles
- Developing new features
- Training new team members

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - System architecture
- [WORKFLOW_PROCESSES.md](WORKFLOW_PROCESSES.md) - Detailed workflows
- [FEATURES_SPECIFICATION.md](FEATURES_SPECIFICATION.md) - Feature details
- [ERROR_HANDLING_TROUBLESHOOTING.md](ERROR_HANDLING_TROUBLESHOOTING.md) - Error handling
