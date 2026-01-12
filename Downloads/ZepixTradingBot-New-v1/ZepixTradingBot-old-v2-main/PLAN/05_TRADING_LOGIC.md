# 05 - Trading Logic & Strategies

## 📈 Complete Trading Logic Documentation

---

## 1. Multi-Logic System

### LOGIC1 (15-minute timeframe)
**Purpose**: Quick scalps, short-term moves

**Settings**:
- Timeframe: 15m
- Risk/Reward: 1:1.5
- Lot multiplier: 1.0
- SL multiplier: 1.0
- Recovery window: 5 minutes

**When to use**: High-frequency trading, volatile sessions

---

### LOGIC2 (1-hour timeframe)
**Purpose**: Intraday swings

**Settings**:
- Timeframe: 1h
- Risk/Reward: 1:1.5
- Lot multiplier: 1.0
- SL multiplier: 1.0
- Recovery window: 10 minutes

**When to use**: Standard trading, most reliable

---

### LOGIC3 (Daily timeframe)
**Purpose**: Position trading, major trends

**Settings**:
- Timeframe: 1d
- Risk/Reward: 1:1.5
- Lot multiplier: 1.0
- SL multiplier: 1.0
- Recovery window: 30 minutes

**When to use**: Low-frequency, high-conviction trades

---

## 2. Trend Alignment Logic

### Required Alignment
```
Signal Timeframe = LOGIC2 (1h buy)

Check:
├─ 15m trend: BULLISH ✓
├─ 1h trend: BULLISH ✓ (required)
└─ 1d trend: BULLISH ✓

If all aligned → ALLOW ENTRY
If not aligned → REJECT with notification
```

### Alignment Rules
- **Same timeframe**: MUST match
- **Lower timeframe**: Should support (warning if not)
- **Higher timeframe**: Should support (warning if not)

### Override
User can set manual trends:
```
/set_trend EURUSD 1h bullish
```
This locks trend until changed or set to AUTO.

---

## 3. Entry Validation Process

```python
def validate_entry(alert):
    """Complete entry validation"""
    
    # 1. Symbol validation
    if alert['symbol'] not in SUPPORTED_SYMBOLS:
        return REJECT("Unsupported symbol")
    
    # 2. Trend alignment
    trends = get_trends(alert['symbol'], alert['tf'])
    if not check_alignment(alert['signal'], trends):
        return REJECT("Trend misalignment")
    
    # 3. Logic active check
    if not is_logic_active(alert['tf']):
        return REJECT("Logic disabled")
    
    # 4. Risk caps
    if daily_loss >= daily_cap:
        return REJECT("Daily cap exceeded")
    if lifetime_loss >= lifetime_cap:
        return REJECT("Lifetime cap exceeded")
    
    # 5. Bot paused
    if is_paused:
        return REJECT("Bot paused")
    
    # 6. Margin available
    if not check_margin(lot_size):
        return REJECT("Insufficient margin")
    
    return ALLOW
```

---

## 4. SL/TP Calculation

### SL Calculation (SL-1 System)
```python
def calculate_sl_sl1(entry, direction, symbol):
    """Fixed percentage SL"""
    
    # Get symbol-specific SL percent
    sl_percent = get_symbol_sl_percent(symbol)  # e.g., 20% for XAUUSD
    
    if direction == "buy":
        sl = entry - (entry * sl_percent / 100)
    else:  # sell
        sl = entry + (entry * sl_percent / 100)
    
    return round(sl, symbol_decimals(symbol))
```

### SL Calculation (SL-2 System)
```python
def calculate_sl_sl2(entry, direction, symbol):
    """Dynamic SL based on volatility"""
    
    # Get recent volatility (ATR-based)
    atr = get_atr(symbol, timeframe, periods=14)
    
    # SL = entry ± (ATR * multiplier)
    multiplier = 1.5  # configurable
    
    if direction == "buy":
        sl = entry - (atr * multiplier)
    else:
        sl = entry + (atr * multiplier)
    
    return round(sl, symbol_decimals(symbol))
```

### TP Calculation
```python
def calculate_tp(entry, sl, direction, rr_ratio=1.5):
    """Fixed RR ratio TP"""
    
    risk_distance = abs(entry - sl)
    reward_distance = risk_distance * rr_ratio
    
    if direction == "buy":
        tp = entry + reward_distance
    else:
        tp = entry - reward_distance
    
    return round(tp, symbol_decimals(symbol))
```

---

## 5. Dual Order Logic

### Order A (TP Trail)
```python
def create_order_a(signal):
    """Main order with flexible SL"""
    
    entry = current_price
    
    # Use active SL system (SL-1 or SL-2)
    if active_sl_system == "sl-1":
        sl = calculate_sl_sl1(entry, signal['direction'], signal['symbol'])
    else:
        sl = calculate_sl_sl2(entry, signal['direction'], signal['symbol'])
    
    tp = calculate_tp(entry, sl, signal['direction'], rr_ratio=1.5)
    
    lot_size = get_tier_lot_size(current_tier)
    
    order = {
        'symbol': signal['symbol'],
        'type': signal['direction'],
        'lots': lot_size,
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'comment': f"{signal['logic']}_A"
    }
    
    return place_order(order)
```

### Order B (Profit Booking)
```python
def create_order_b(signal, chain_id):
    """Profit chain order with fixed $10 SL"""
    
    entry = current_price
    lot_size = get_tier_lot_size(current_tier)
    
    # Calculate SL for exactly $10 risk
    sl = calculate_sl_for_dollar_amount(
        entry=entry,
        risk_amount=10.0,
        lot_size=lot_size,
        symbol=signal['symbol'],
        direction=signal['direction']
    )
    
    # Calculate TP for exactly $7 profit
    tp = calculate_tp_for_dollar_amount(
        entry=entry,
        profit_amount=7.0,
        lot_size=lot_size,
        symbol=signal['symbol'],
        direction=signal['direction']
    )
    
    order = {
        'symbol': signal['symbol'],
        'type': signal['direction'],
        'lots': lot_size,
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'comment': f"{signal['logic']}_B",
        'chain_id': chain_id
    }
    
    return place_order(order)
```

---

## 6. Re-entry Logic Details

### SL Hunt Re-entry
```python
def check_sl_hunt_opportunity(closed_trade):
    """Check if SL hunt re-entry should trigger"""
    
    # 1. Was it a loss?
    if closed_trade['profit'] >= 0:
        return False
    
    # 2. SL Hunt enabled?
    if not config['sl_hunt_enabled']:
        return False
    
    # 3. Max attempts not exceeded?
    attempts = count_sl_hunt_attempts(closed_trade['chain_id'])
    if attempts >= MAX_SL_HUNT_ATTEMPTS:  # = 1
        return False
    
    # 4. Create recovery window
    window = {
        'symbol': closed_trade['symbol'],
        'direction': closed_trade['direction'],
        'sl_price': closed_trade['sl_price'],
        'recovery_target': closed_trade['sl_price'] + recovery_offset,  # +1 pip
        'expiry': now() + recovery_window  # 5 minutes
    }
    
    # 5. Start monitoring
    monitor_recovery_window(window)
    return True
```

### TP Continuation
```python
def check_tp_continuation(closed_trade):
    """Check if TP continuation should trigger"""
    
    # 1. Was it a profit?
    if closed_trade['profit'] <= 0:
        return False
    
    # 2. TP Continuation enabled?
    if not config['tp_continuation_enabled']:
        return False
    
    # 3. Max levels not exceeded?
    level = closed_trade['reentry_level'] or 0
    if level >= MAX_REENTRY_LEVELS:  # = 2
        return False
    
    # 4. Check price gap
    current_price = get_current_price(closed_trade['symbol'])
    gap = abs(current_price - closed_trade['tp_price'])
    
    if gap >= config['tp_continuation_gap']:  # 2 pips
        # 5. Create re-entry with reduced SL
        create_reentry_order(
            symbol=closed_trade['symbol'],
            direction=closed_trade['direction'],
            sl_reduction=0.5,  # 50% reduced
            level=level + 1
        )
        return True
    
    return False
```

---

## 7. Profit Chain Logic

### Level Progression
```python
def handle_profit_chain_progression(closed_order_b):
    """Handle profit chain level advancement"""
    
    # 1. Get chain info
    chain = database.get_chain(closed_order_b['chain_id'])
    
    if chain is None:
        return  # Not a chain order
    
    # 2. Check current level
    current_level = chain['current_level']
    
    if current_level >= 5:
        # Chain complete!
        database.mark_chain_complete(chain['chain_id'])
        telegram_bot.send_notification(
            f"🎉 PROFIT CHAIN COMPLETE!\n"
            f"Total profit: ${chain['total_profit']}"
        )
        return
    
    # 3. Calculate next level
    next_level = current_level + 1
    multiplier = get_multiplier(next_level)  # e.g., 2^next_level for standard
    
    # 4. Create next level order
    new_lot_size = chain['base_lot_size'] * multiplier
    
    order_b = create_order_b(
        signal={
            'symbol': chain['symbol'],
            'direction': chain['direction'],
            'logic': 'PROFIT_CHAIN'
        },
        chain_id=chain['chain_id']
    )
    
    # Override lot size
    order_b['lots'] = new_lot_size
    
    # 5. Place order
    position_id = place_order(order_b)
    
    # 6. Update database
    database.update_chain(
        chain_id=chain['chain_id'],
        current_level=next_level,
        position_id=position_id,
        total_profit=chain['total_profit'] + closed_order_b['profit']
    )
```

---

## 8. Risk Management Logic

### Lot Sizing
```python
def get_lot_size_for_trade(symbol, account_balance):
    """Determine lot size based on tier"""
    
    # Get active tier
    tier = determine_tier(account_balance)
    
    # Tier definitions
    tiers = {
        5000:   {'lot': 0.05},
        10000:  {'lot': 0.10},
        25000:  {'lot': 0.20'},
        50000:  {'lot': 0.50},
        100000: {'lot': 1.00}
    }
    
    return tiers[tier]['lot']
```

### Loss Tracking
```python
def track_loss(trade_profit):
    """Track daily and lifetime losses"""
    
    if trade_profit >= 0:
        return  # Not a loss
    
    loss_amount = abs(trade_profit)
    
    # Update daily loss
    today = date.today()
    daily_record = database.get_daily_loss(today)
    daily_record['amount'] += loss_amount
    database.update_daily_loss(daily_record)
    
    # Update lifetime loss
    lifetime_record = database.get_lifetime_loss()
    lifetime_record['amount'] += loss_amount
    database.update_lifetime_loss(lifetime_record)
    
    # Check caps
    if daily_record['amount'] >= config['daily_cap']:
        pause_trading("Daily cap exceeded")
    
    if lifetime_record['amount'] >= config['lifetime_cap']:
        pause_trading("Lifetime cap exceeded")
```

---

## 9. Exit Logic

### Exit Signal Processing
```python
def process_exit_signal(alert):
    """Handle exit signal from TradingView"""
    
    symbol = alert['symbol']
    
    # 1. Get open positions for this symbol
    positions = get_open_positions(symbol)
    
    if not positions:
        return  # No positions to close
    
    # 2. Close all positions
    for position in positions:
        close_position(position['id'])
        
        # Log closure reason
        database.update_trade(
            position_id=position['id'],
            close_reason='exit_signal',
            close_time=now()
        )
    
    # 3. Check for exit continuation
    if config['exit_continuation_enabled']:
        for position in positions:
            check_exit_continuation_opportunity(position)
```

### Reversal Detection
```python
def handle_reversal_signal(alert):
    """Handle reversal signal (Reverse Shield)"""
    
    symbol = alert['symbol']
    detected_trend = alert['trend']  # e.g., 'bearish'
    
    # 1. Get open positions
    positions = get_open_positions(symbol)
    
    for position in positions:
        # 2. Check if position opposes reversal
        if position['direction'] == 'buy' and detected_trend == 'bearish':
            # Close immediately
            close_position(position['id'])
            
            telegram_bot.send_notification(
                f"🛡️ REVERSE SHIELD ACTIVATED\n"
                f"Closed {position['direction']} {symbol}\n"
                f"Reason: Bearish reversal detected"
            )
        
        elif position['direction'] == 'sell' and detected_trend == 'bullish':
            close_position(position['id'])
            
            telegram_bot.send_notification(
                f"🛡️ REVERSE SHIELD ACTIVATED\n"
                f"Closed {position['direction']} {symbol}\n"
                f"Reason: Bullish reversal detected"
            )
```

---

## 10. Symbol-Specific Logic

### Pip Calculation
```python
def calculate_pips(symbol, price_difference):
    """Calculate pips based on symbol type"""
    
    # JPY pairs: 1 pip = 0.01
    if 'JPY' in symbol:
        return price_difference * 100
    
    # Gold (XAUUSD): 1 pip = 0.10
    elif symbol == 'XAUUSD':
        return price_difference * 10
    
    # Standard pairs: 1 pip = 0.0001
    else:
        return price_difference * 10000
```

### Symbol Mapping
```python
# TradingView → MT5 mapping
SYMBOL_MAP = {
    'EURUSD': 'EURUSD.a',
    'GBPUSD': 'GBPUSD.a',
    'XAUUSD': 'XAUUSD.a',
    # ... etc
}

def map_symbol(tv_symbol):
    """Convert TradingView symbol to MT5 symbol"""
    return SYMBOL_MAP.get(tv_symbol, tv_symbol)
```

---

**Trading logic files**:
- Core: `src/core/trading_engine.py`
- Entry validation: `src/processors/alert_processor.py`
- Re-entry: `src/managers/reentry_manager.py`
- Profit chains: `src/managers/profit_booking_manager.py`
- Risk: `src/managers/risk_manager.py`
