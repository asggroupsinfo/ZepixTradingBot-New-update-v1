# ZEPIX v3 - Complete Signal Decision Logic

> **Purpose:** This document maps all 11 indicator signals to bot actions. Use this as the definitive reference for implementing signal intelligence in Logic1/2/3.

---

## Table of Contents
1. [Entry Signals (6)](#entry-signals)
2. [Exit Signals (2)](#exit-signals)
3. [Warning Signals (2)](#warning-signals)
4. [Information Signal (1)](#information-signal)
5. [Logic Routing Strategy](#logic-routing)
6. [Summary Matrix](#summary)

---

<a name="entry-signals"></a>
## 🎯 ENTRY SIGNALS (6 Signals)

### Signal 1: Institutional Launchpad (Bull/Bear)

**Action:** `BUY` (Bull) or `SELL` (Bear)

**Indicator Triggers:**
- Price in bullish/bearish Order Block
- Consensus Score >= 7 (bull) or <= 2 (bear)
- Bullish breakout OR trendline break
- Market trend aligned
- Volume > 1.2× average
- MTF alignment (3+ timeframes)
- NOT in liquidity zone

**Bot Decision Code:**
```python
if alert.signal_type == "Institutional_Launchpad":
    # Score threshold validation
    if alert.direction == "buy" and alert.consensus_score < 7:
        return {"action": "REJECT", "reason": "score_too_low"}
    if alert.direction == "sell" and alert.consensus_score > 2:
        return {"action": "REJECT", "reason": "score_too_high"}
    
    # Route to LOGIC2 (15m intraday)
    logic = "LOGIC2"
    
    # Position sizing based on score
    position_multiplier = 1.0 if alert.consensus_score >= 9 else 0.8
    
    return {
        "action": "BUY" if alert.direction == "buy" else "SELL",
        "logic": logic,
        "lot_multiplier": position_multiplier,
        "priority": "HIGH"
    }
```

**Statistics:**
- Frequency: ⭐ Rare (1-3/month)
- Win Rate: 75-80%
- Position Size: Large (0.8-1.0×)

---

### Signal 2: Liquidity Trap Reversal (Bull/Bear)

**Action:** `REVERSE` (Close opposite + Enter new)

**Indicator Triggers:**
- Liquidity sweep detected
- Price in Order Block
- Volume confirmed
- Market trend aligned

**Bot Decision Code:**
```python
if alert.signal_type == "Liquidity_Trap_Reversal":
    # Check for opposite positions
    opposite_trades = get_opposite_positions(alert.symbol, alert.direction)
    
    if opposite_trades:
        # AGGRESSIVE REVERSAL
        for trade in opposite_trades:
            close_trade(trade.trade_id)
        
        # Register exit continuation (wait for gap)
        register_exit_continuation(
            symbol=alert.symbol,
            new_direction=alert.direction,
            min_gap_pips=20
        )
    
    # Position sizing (conservative for reversals)
    position_multiplier = 0.8 if alert.consensus_score>= 6 else 0.0
    
    return {
        "action": "REVERSE",
        "lot_multiplier": position_multiplier,
        "priority": "URGENT",
        "reversal_type": "AGGRESSIVE"
    }
```

**Statistics:**
- Frequency: ⭐⭐ Medium (2-4/week)
- Win Rate: 70-75%
- Use Case: Ranging markets, stop hunts

---

### Signal 3: Momentum Breakout (Bull/Bear)

**Action:** `BUY` or `SELL`

**Indicator Triggers:**
- Trendline break
- Consensus >= 7 (or <= 2)
- Volume surge
- MTF aligned
- ⚠️ OB NOT required

**Bot Decision Code:**
```python
if alert.signal_type == "Momentum_Breakout":
    # Prefer LOGIC1 for 5m scalping
    if alert.tf == "5":
        logic = "LOGIC1"
        logic_mult = 1.25
    elif alert.tf == "15":
        logic = "LOGIC2"
        logic_mult = 1.0
    
    # Dynamic position sizing
    if alert.consensus_score >= 8:
        position_multiplier = 1.0
    elif alert.consensus_score >= 7:
        position_multiplier = 0.8
    else:
        position_multiplier = 0.6
    
    return {
        "action": "BUY" if alert.direction == "buy" else "SELL",
        "logic": logic,
        "lot_multiplier": logic_mult * position_multiplier,
        "priority": "MEDIUM",
        "exit_on_score_drop": True,  # Exit if score drops 4+ points
        "exit_threshold": 4
    }
```

**Statistics:**
- Frequency: ⭐⭐⭐ Med-High (3-5/week)
- Win Rate: 65-70%
- Use Case: Trending markets

---

### Signal 4: Mitigation Test Entry (Bull/Bear)

**Action:** `BUY` or `SELL`

**Indicator Triggers:**
- Price in EXISTING OB (retest)
- NOT new Order Block
- Bullish/bearish close
- Volume confirmed

**Bot Decision Code:**
```python
if alert.signal_type == "Mitigation_Test_Entry":
    # Verify OB retest
    if not alert.get("price_in_ob"):
        return {"action": "REJECT", "reason": "not_in_ob"}
    
    # LOGIC2 with conservative sizing
    logic = "LOGIC2"
    position_multiplier = 0.7  # Precision mode
    
    return {
        "action": "BUY" if alert.direction == "buy" else "SELL",
        "logic": logic,
        "lot_multiplier": position_multiplier,
        "priority": "MEDIUM",
        "exit_on_ob_break": True,  # Exit if price breaks OB zone
        "sl_type": "TIGHT"
    }
```

**Statistics:**
- Frequency: ⭐⭐⭐⭐ High (5-8/week)
- Win Rate: 70-75%
- Risk: Low (buying support/selling resistance)

---

### Signal 5: Golden Pocket Flip (Bull/Bear)

**Action:** `BUY` or `SELL` (High Conviction)

**Indicator Triggers:**
- BOS/CHoCH structure break
- Fib 0.618-0.786 (bull) or 0.214-0.382 (bear)
- Price in OB
- Volume confirmed

**Bot Decision Code:**
```python
if alert.signal_type == "Golden_Pocket_Flip":
    # Route based on timeframe
    if alert.tf == "60":
        logic = "LOGIC3"  # Swing trade
        logic_mult = 0.625
    else:
        logic = "LOGIC2"
        logic_mult = 1.0
    
    # High conviction sizing
    position_multiplier = 1.0 if alert.consensus_score>= 8 else 0.8
    
    return {
        "action": "BUY" if alert.direction == "buy" else "SELL",
        "logic": logic,
        "lot_multiplier": logic_mult * position_multiplier,
        "priority": "HIGH",
        "tp_targets": "FIB_BASED",
        "reversal_enabled": True,
        "hold_duration": "SWING"
    }
```

**Statistics:**
- Frequency: ⭐ Low (2-4/month)
- Win Rate: 80-85% (**HIGHEST**)
- Use Case: Institutional entries

---

### Signal 6: Screener Full (Bull/Bear)

**Action:** `BUY` or `SELL` (MAXIMUM Conviction)

**Indicator Triggers:**
- Perfect Consensus: 9 (bull) or 0 (bear)
- MTF 100% aligned
- Volume delta > 2.0
- NOT in opposite OB
- NOT at EQH/EQL

**Bot Decision Code:**
```python
if alert.signal_type in ["Screener_Full_Bullish", "Screener_Full_Bearish"]:
    # Always LOGIC3 swing trade
    logic = "LOGIC3"
    
    # MAXIMUM position size
    position_multiplier = 1.0
    
    # Override score (perfect alignment)
    alert.consensus_score = 9 if "Bullish" in alert.signal_type else 0
    
    return {
        "action": "BUY" if "Bullish" in alert.signal_type else "SELL",
        "logic": logic,
        "lot_multiplier": 1.0,  # FULL position
        "priority": "CRITICAL",
        "hold_until_score": 7 if "Bullish" in alert.signal_type else 2,
        "tp_targets": "EXTENDED",
        "notifications": "IMMEDIATE"  # Alert user via Telegram
    }
```

**Statistics:**
- Frequency: ⭐ Extremely Rare (1 per 2-3 months)
- Win Rate: 85%+
- Position Size: MAXIMUM

---

<a name="exit-signals"></a>
## 🚪 EXIT SIGNALS (2 Signals)

### Signal 7: Bullish Exit

**Action:** `CLOSE ALL SELL POSITIONS`

**Indicator Triggers:**
- Active short AND (TP1 hit OR price in bearish OB OR consensus <= 3)

**Bot Decision Code:**
```python
if alert.signal_type == "Bullish_Exit":
    sell_positions = get_open_positions(symbol=alert.symbol, direction="SELL")
    
    if sell_positions:
        for trade in sell_positions:
            close_trade(trade.trade_id, reason="BULLISH_EXIT_SIGNAL")
            
            # Check exit continuation
            if trade.profit > 0:
                register_exit_continuation(
                    symbol=alert.symbol,
                    exit_price=alert.price,
                    new_direction="buy",
                    min_gap_pips=20
                )
        
        return {"action": "EXIT", "closed": len(sell_positions)}
    
    return {"action": "NO_ACTION"}
```

---

### Signal 8: Bearish Exit

**Action:** `CLOSE ALL BUY POSITIONS`

**Indicator Triggers:**
- Active long AND (TP1 hit OR price in bullish OB OR consensus >= 6)

**Bot Decision Code:**
```python
if alert.signal_type == "Bearish_Exit":
    buy_positions = get_open_positions(symbol=alert.symbol, direction="BUY")
    
    if buy_positions:
        for trade in buy_positions:
            close_trade(trade.trade_id, reason="BEARISH_EXIT_SIGNAL")
            
            if trade.profit > 0:
                register_exit_continuation(
                    symbol=alert.symbol,
                    exit_price=alert.price,
                    new_direction="sell",
                    min_gap_pips=20
                )
        
        return {"action": "EXIT", "closed": len(buy_positions)}
    
    return {"action": "NO_ACTION"}
```

---

<a name="warning-signals"></a>
## ⚠️ WARNING SIGNALS (2 Signals)

### Signal 9: Volatility Squeeze

**Action:** `HIGH ALERT MODE` (No trade)

**Indicator Triggers:**
- ATR declining (2+ periods)
- Volume < 50% average
- Range compression
- Consensus 4-5 (neutral)

**Bot Decision Code:**
```python
if alert.signal_type == "Volatility_Squeeze":
    # Enter alert mode for 5 minutes
    set_high_alert_mode(symbol=alert.symbol, duration=300)
    
    # Telegram notification
    send_telegram_alert(
        message=f"🔔 Volatility Squeeze on {alert.symbol} - Big move incoming!",
        priority="INFO"
    )
    
    # Store in memory
    store_squeeze_alert(symbol=alert.symbol, timestamp=now())
    
    return {"action": "ALERT_ONLY", "status": "high_alert_mode_active"}
```

**Statistics:**
- Frequency: ⭐⭐ Medium (1-2/week)
- Action: Information only

---

<a name="information-signal"></a>
## 📡 INFORMATION SIGNAL (1 Signal)

### Signal 10: Trend Pulse ⚡

**Action:** `UPDATE TREND DATABASE`

**Indicator Triggers:**
- ANY timeframe trend changes
- Monitors: 1m, 5m, 15m, 1H, 4H, 1D
- Triggers: current ≠ previous

**Bot Decision Code:**
```python
if alert.signal_type == "Trend_Pulse":
    # Parse trends
    current_trends = alert.get("current_trends")  # "1,1,-1,1,1,1"
    changed_tfs = alert.get("changed_timeframes")  # "5m,15m,"
    
    # Update 4-Pillar Trend Manager
    process_mtf_trends(current_trends, alert.symbol)
    
    # Filter important changes only
    important = [tf for tf in changed_tfs.split(',') 
                 if tf in ['15m', '1h', '4h', '1d']]
    
    if important:
        # Telegram for major shifts
        send_telegram_alert(
            message=f"⚡ Trend Change: {alert.symbol} {', '.join(important)}",
            priority="LOW"
        )
        
        # Re-check SL Hunt eligibility
        check_all_recovery_chains(alert.symbol)
    
    return {"action": "INFO_ONLY", "changed": important}
```

**Statistics:**
- Frequency: ⭐⭐⭐⭐⭐ Very High (every bar with trend change)
- Action: Database update only
- Filter: Ignore 1m/5m noise

---

<a name="logic-routing"></a>
## 🔄 Logic Routing Strategy

**How signals map to Logic1/2/3:**

```python
def route_signal_to_logic(alert: ZepixV3Alert) -> str:
    """Route signal to appropriate Logic based on TF and signal type."""
    
    # PRIMARY: Timeframe routing
    if alert.tf == "5":
        return "LOGIC1"  # Scalping
    elif alert.tf == "15":
        return "LOGIC2"  # Intraday
    elif alert.tf in ["60", "240"]:
        return "LOGIC3"  # Swing
    
    # SECONDARY: Signal type overrides
    if alert.signal_type in ["Screener_Full_Bullish", "Screener_Full_Bearish"]:
        return "LOGIC3"  # Always swing
    
    if alert.signal_type == "Momentum_Breakout" and alert.consensus_score >= 8:
        return "LOGIC1"  # Fast scalp
    
    # DEFAULT
    return "LOGIC2"
```

---

<a name="summary"></a>
## 📊 Summary Matrix

| # | Signal | Type | Freq | Win% | Action | Logic | Priority |
|---|---|---|---|---|---|---|---|
| 1 | Institutional Launchpad | Entry | Rare | 75-80% | BUY/SELL | L2 | HIGH |
| 2 | Liquidity Trap | Entry | Med | 70-75% | REVERSE | Auto | URGENT |
| 3 | Momentum Breakout | Entry | Med-Hi | 65-70% | BUY/SELL | L1/L2 | MEDIUM |
| 4 | Mitigation Test | Entry | High | 70-75% | BUY/SELL | L2 | MEDIUM |
| 5 | Golden Pocket | Entry | Low | 80-85% | BUY/SELL | L2/L3 | HIGH |
| 6 | Screener Full | Entry | Rare | 85%+ | BUY/SELL | L3 | CRITICAL |
| 7 | Bullish Exit | Exit | - | - | CLOSE SELLS | All | IMMEDIATE |
| 8 | Bearish Exit | Exit | - | - | CLOSE BUYS | All | IMMEDIATE |
| 9 | Volatility Squeeze | Warning | Weekly | - | ALERT | All | INFO |
| 10 | Trend Pulse | Info | Very Hi | - | UPDATE DB | All | LOW |

---

## Integration Notes

1. **All signals come through ONE webhook endpoint** with `type: "entry_v3"` or `"exit_v3"` etc.
2. **Logic1/2/3 remain unchanged** - they just get smarter input
3. **No new Logic4** - this intelligence is distributed across existing logics
4. **Order B always uses Fixed SL** regardless of signal type
5. **Trend check bypassed** for fresh v3 entries
6. **Re-entries still check trends** (SL Hunt, TP Continuation)

---

**Status:** Ready for Implementation ✅
