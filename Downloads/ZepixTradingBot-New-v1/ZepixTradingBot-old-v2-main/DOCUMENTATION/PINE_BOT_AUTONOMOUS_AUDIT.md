# Pine Script to Bot Logic - Autonomous Audit Report

**Audit Date:** 2026-01-13
**Auditor:** Devin AI (Autonomous Analysis)
**Method:** Evidence-based matching without assumptions

---

## SECTION A: PINE-1 ANALYSIS

### Script Information

**File:** `ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine`
**Title:** ZEPIX ULTIMATE BOT v3.0 (Hybrid Intelligence)
**Version:** 3.0
**Author:** Zepix

### Script Purpose

This Pine Script combines Smart Money Concepts (40%), Consensus Engine (25%), Breakout Detection (20%), Risk Management (10%), and Conflict Resolution (5%) into a unified trading system with 12 specific signals. It implements a 5-layer architecture for institutional-grade signal generation.

### Alert Format

**Format Type:** JSON

```pine
// From lines 1716-1717
activeMessage := '{"type":"entry_v3","signal_type":"Institutional_Launchpad","symbol":"{{ticker}}","direction":"buy","tf":"' + timeframe.period + '","price":{{close}},"consensus_score":' + str.tostring(consensusScore) + ',"sl_price":' + str.tostring(smartStopLong) + ',"tp1_price":' + str.tostring(tp1Long) + ',"tp2_price":' + str.tostring(tp2Long) + ',"mtf_trends":"' + mtfString + '","market_trend":' + str.tostring(marketTrend) + ',"volume_delta_ratio":' + str.tostring(volumeDeltaRatio) + ',"price_in_ob":true,"position_multiplier":' + str.tostring(positionMultiplier) + '}'
```

### All Alert Types (12 Total)

| # | Signal Type | Direction | Type Field | Pine Variable |
|---|-------------|-----------|------------|---------------|
| 1 | Institutional_Launchpad | buy/sell | entry_v3 | `signal1_InstitutionalLaunchpad` |
| 2 | Liquidity_Trap_Reversal | buy/sell | entry_v3 | `signal2_LiquidityTrapBull/Bear` |
| 3 | Momentum_Breakout | buy/sell | entry_v3 | `signal3_MomentumBreakoutBull/Bear` |
| 4 | Mitigation_Test_Entry | buy/sell | entry_v3 | `signal4_MitigationTestBull/Bear` |
| 5 | Bullish_Exit | sell | exit_v3 | `signal5_BullishExit` |
| 6 | Bearish_Exit | buy | exit_v3 | `signal6_BearishExit` |
| 7 | Golden_Pocket_Flip | buy/sell | entry_v3 | `signal7_GoldenPocketFlipBull/Bear` |
| 8 | Volatility_Squeeze | neutral | squeeze_v3 | `signal8_VolatilitySqueeze` |
| 9 | Screener_Full_Bullish | buy | entry_v3 | `signal9_ScreenerFullBullish` |
| 10 | Screener_Full_Bearish | sell | entry_v3 | `signal10_ScreenerFullBearish` |
| 11 | Trend_Pulse | neutral | trend_pulse_v3 | `trendPulseTriggered` |
| 12 | Sideways_Breakout | buy/sell | entry_v3 | `signal12_SidewaysBreakoutBull/Bear` |

### Example Alert Messages

**Entry Signal (Institutional_Launchpad):**
```json
{
  "type": "entry_v3",
  "signal_type": "Institutional_Launchpad",
  "symbol": "EURUSD",
  "direction": "buy",
  "tf": "15",
  "price": 1.23456,
  "consensus_score": 7,
  "sl_price": 1.23000,
  "tp1_price": 1.24000,
  "tp2_price": 1.24500,
  "mtf_trends": "1,1,-1,1,1",
  "market_trend": 1,
  "volume_delta_ratio": 1.5,
  "price_in_ob": true,
  "position_multiplier": 0.8
}
```

**Exit Signal (Bullish_Exit):**
```json
{
  "type": "exit_v3",
  "signal_type": "Bullish_Exit",
  "symbol": "EURUSD",
  "direction": "sell",
  "tf": "15",
  "price": 1.24500,
  "consensus_score": 3,
  "market_trend": -1,
  "reason": "TP_hit_or_reversal_or_momentum_loss"
}
```

**Info Signal (Trend_Pulse):**
```json
{
  "type": "trend_pulse_v3",
  "signal_type": "Trend_Pulse",
  "symbol": "EURUSD",
  "tf": "15",
  "price": 1.23456,
  "current_trends": "1,1,1,1,1,1",
  "previous_trends": "1,1,-1,1,1,1",
  "changed_timeframes": "15m",
  "change_details": "15m: -1 -> 1",
  "trend_labels": "1m,5m,15m,1H,4H,1D",
  "market_trend": 1,
  "consensus_score": 8,
  "message": "Trend change detected on: 15m"
}
```

### Alert Trigger Code

```pine
// From lines 1820-1836
bool anySignalActive = signal1_InstitutionalLaunchpad or signal1_InstitutionalLaunchpadBear or 
                       signal2_LiquidityTrapBull or signal2_LiquidityTrapBear or 
                       signal3_MomentumBreakoutBull or signal3_MomentumBreakoutBear or 
                       signal4_MitigationTestBull or signal4_MitigationTestBear or 
                       signal5_BullishExit or signal6_BearishExit or 
                       signal7_GoldenPocketFlipBull or signal7_GoldenPocketFlipBear or 
                       signal8_VolatilitySqueeze or 
                       signal9_ScreenerFullBullish or signal10_ScreenerFullBearish or 
                       trendPulseTriggered or
                       signal12_SidewaysBreakoutBull or signal12_SidewaysBreakoutBear

if anySignalActive
    alert(activeMessage, alert.freq_once_per_bar_close)
```

---

## SECTION B: PINE-2 ANALYSIS

### Script Information

**File:** `Signals_and_Overlays_V6_Enhanced_Build.pine`
**Title:** Signals and Overlays V6 Enhanced
**Version:** 6.0 (Real-Time Monitor)
**Build Date:** 2026-01-11
**Author:** Zepix Team

### Script Purpose

Multi-preset indicator with three modes: Zero Lag Overlays, Reversal + Volumes, and Breakouts Detector. Enhanced with Trendline Integration, Trend Pulse (Multi-Timeframe Analysis), ADX Momentum Filter, Enhanced Alert System, and Real-Time Monitoring for momentum and state changes.

### Alert Format

**Format Type:** Pipe-separated (|)

```pine
// From lines 733-777
buildAlertMessage(string signalType, string direction) =>
    string msg = ""
    msg += signalType + "|"
    msg += syminfo.ticker + "|"
    msg += timeframe.period + "|"
    msg += str.tostring(close, "#.#####") + "|"
    msg += direction + "|"
    // ... additional fields based on signal type
```

### All Alert Types (14 Total)

| # | Signal Type | Category | Fields | Pine Trigger |
|---|-------------|----------|--------|--------------|
| 1 | BULLISH_ENTRY | Entry | 15 | `enhancedBullishEntry` |
| 2 | BEARISH_ENTRY | Entry | 15 | `enhancedBearishEntry` |
| 3 | TREND_PULSE | Info | 7 | `trendPulseTriggered` |
| 4 | SIDEWAYS_BREAKOUT | Entry | 8 | `sidewaysBreakout` |
| 5 | TRENDLINE_BULLISH_BREAK | Entry | 6 | `trendlineBullishBreak` |
| 6 | TRENDLINE_BEARISH_BREAK | Entry | 6 | `trendlineBearishBreak` |
| 7 | MOMENTUM_CHANGE | Info | 8 | `cond_mom_change` |
| 8 | STATE_CHANGE | Info | 6 | `cond_state_change` |
| 9 | EXIT_BULLISH | Exit | 5 | `cond_exit_bull` |
| 10 | EXIT_BEARISH | Exit | 5 | `cond_exit_bear` |
| 11 | BREAKOUT | Entry | 7 | `not na(bomax) and num >= mintest` |
| 12 | BREAKDOWN | Entry | 7 | `not na(bomin) and num1 >= mintest` |
| 13 | SCREENER_FULL_BULLISH | Info | 4 | `fullBullish` |
| 14 | SCREENER_FULL_BEARISH | Info | 4 | `fullBearish` |

### Example Alert Messages

**Entry Signal (BULLISH_ENTRY) - 15 fields:**
```
BULLISH_ENTRY|EURUSD|15|1.23456|BUY|HIGH|85|25.5|STRONG|1.23000|1.24000|1.24500|1.25000|4/2|TL_OK|
```

Field breakdown:
1. Signal Type: BULLISH_ENTRY
2. Symbol: EURUSD
3. Timeframe: 15
4. Price: 1.23456
5. Direction: BUY
6. Confidence Level: HIGH
7. Confidence Score: 85
8. ADX Value: 25.5
9. ADX Strength: STRONG
10. SL Price: 1.23000
11. TP1 Price: 1.24000
12. TP2 Price: 1.24500
13. TP3 Price: 1.25000
14. TF Alignment: 4/2 (4 bullish, 2 bearish)
15. Trendline State: TL_OK

**Info Signal (TREND_PULSE) - 7 fields:**
```
TREND_PULSE|EURUSD|15|4|2|15m,1H|TRENDING_BULLISH
```

**Exit Signal (EXIT_BULLISH) - 5 fields:**
```
EXIT_BULLISH|EURUSD|15|1.24500|15
```

**Info Signal (MOMENTUM_CHANGE) - 8 fields:**
```
MOMENTUM_CHANGE|EURUSD|15|28.5|STRONG|22.3|MODERATE|INCREASING
```

### Alert Trigger Code

```pine
// From lines 791-826
if useEnhancedAlerts
    if enhancedBullishEntry
        string bullishMsg = buildAlertMessage("BULLISH_ENTRY", "BUY")
        alert(bullishMsg, alert.freq_once_per_bar)
    
    if enhancedBearishEntry
        string bearishMsg = buildAlertMessage("BEARISH_ENTRY", "SELL")
        alert(bearishMsg, alert.freq_once_per_bar)
    
    if trendPulseTriggered and enableTrendPulse
        string pulseMsg = buildTrendPulseAlert()
        alert(pulseMsg, alert.freq_once_per_bar)
    
    if sidewaysBreakout and enableADX
        string swMsg = "SIDEWAYS_BREAKOUT|" + syminfo.ticker + "|" + timeframe.period + "|" + 
                      breakoutDirection + "|" + str.tostring(adxValue, "#.#") + "|" + 
                      adxStrength + "|SIDEWAYS|INCREASING"
        alert(swMsg, alert.freq_once_per_bar)
```

---

## SECTION C: BOT PLUGINS DISCOVERED

### Plugin Directory Scan

**Location:** `src/logic_plugins/`

| # | Plugin ID | Version | Description | Order Type |
|---|-----------|---------|-------------|------------|
| 1 | combined_v3 | 3.1.0 | V3 Combined Logic - 12 signals, 3 logics, dual orders | Dual (A+B) |
| 2 | price_action_v6 | 6.0.0 | V6 Price Action - 4 timeframes, 14 alerts | Conditional |
| 3 | price_action_1m | 1.0.0 | 1-Minute Scalping | ORDER_B_ONLY |
| 4 | price_action_5m | 1.0.0 | 5-Minute Swing | DUAL_ORDERS |
| 5 | price_action_15m | 1.0.0 | 15-Minute Position | ORDER_A_ONLY |
| 6 | price_action_1h | 1.0.0 | 1-Hour Position | ORDER_A_ONLY |
| 7 | hello_world | - | Template plugin | N/A |

### Plugin 1: combined_v3

**Expected Alert Format:** JSON object with attributes

**Expected Signal Types (12):**
```python
# From signal_handlers.py lines 46-64
SIGNAL_HANDLERS = {
    'Institutional_Launchpad': 'handle_institutional_launchpad',
    'Liquidity_Trap': 'handle_liquidity_trap',
    'Momentum_Breakout': 'handle_momentum_breakout',
    'Mitigation_Test': 'handle_mitigation_test',
    'Golden_Pocket_Flip': 'handle_golden_pocket_flip',
    'Golden_Pocket_Flip_1H': 'handle_golden_pocket_flip',
    'Golden_Pocket_Flip_4H': 'handle_golden_pocket_flip',
    'Screener_Full_Bullish': 'handle_screener_full',
    'Screener_Full_Bearish': 'handle_screener_full',
    'Sideways_Breakout': 'handle_sideways_breakout',
    'Bullish_Exit': 'handle_bullish_exit',
    'Bearish_Exit': 'handle_bearish_exit',
    'Volatility_Squeeze': 'handle_volatility_squeeze',
    'Trend_Pulse': 'handle_trend_pulse'
}
```

**Field Access Pattern:**
```python
# From signal_handlers.py lines 489-493
def _get_attr(self, alert: Any, attr: str, default: Any = None) -> Any:
    if isinstance(alert, dict):
        return alert.get(attr, default)
    return getattr(alert, attr, default)
```

### Plugin 2: price_action_v6

**Expected Alert Format:** Object with alert_type attribute

**Expected Signal Types (14):**
```python
# From plugin.py lines 70-91
ENTRY_ALERTS = [
    "PA_Breakout_Entry",
    "PA_Pullback_Entry",
    "PA_Reversal_Entry",
    "PA_Momentum_Entry",
    "PA_Support_Bounce",
    "PA_Resistance_Rejection",
    "PA_Trend_Continuation"
]

EXIT_ALERTS = [
    "PA_Exit_Signal",
    "PA_Reversal_Exit",
    "PA_Target_Hit"
]

INFO_ALERTS = [
    "PA_Trend_Pulse",
    "PA_Volatility_Alert",
    "PA_Session_Open",
    "PA_Session_Close"
]
```

### Plugin 3-6: price_action_1m/5m/15m/1h

**Expected Alert Format:** Dictionary with signal fields

**Expected Fields:**
```python
# Common fields across all timeframe plugins
signal.get('symbol', '')
signal.get('direction', '')
signal.get('sl_price')
signal.get('tp1_price')  # 1m, 5m
signal.get('tp2_price')  # 5m, 15m
signal.get('tp3_price')  # 1h
signal.get('price', 0)
signal.get('adx', 0)
signal.get('conf_score', 0)
```

---

## SECTION D: AUTONOMOUS MATCHING

### PINE-1 (V3) ↔ combined_v3 Plugin

**Confidence Level:** 95%

**Evidence for Match:**

1. **Format Match:** Both use JSON format
   - Pine: `'{"type":"entry_v3","signal_type":"...",...}'`
   - Bot: `alert.get('signal_type')` or `getattr(alert, 'signal_type')`

2. **Signal Type Names Match (10/12):**
   | Pine Signal | Bot Handler | Match |
   |-------------|-------------|-------|
   | Institutional_Launchpad | Institutional_Launchpad | Exact |
   | Liquidity_Trap_Reversal | Liquidity_Trap | Partial |
   | Momentum_Breakout | Momentum_Breakout | Exact |
   | Mitigation_Test_Entry | Mitigation_Test | Partial |
   | Golden_Pocket_Flip | Golden_Pocket_Flip | Exact |
   | Bullish_Exit | Bullish_Exit | Exact |
   | Bearish_Exit | Bearish_Exit | Exact |
   | Volatility_Squeeze | Volatility_Squeeze | Exact |
   | Screener_Full_Bullish | Screener_Full_Bullish | Exact |
   | Screener_Full_Bearish | Screener_Full_Bearish | Exact |
   | Trend_Pulse | Trend_Pulse | Exact |
   | Sideways_Breakout | Sideways_Breakout | Exact |

3. **Core Fields Match:**
   - symbol, direction, tf (timeframe)
   - consensus_score, market_trend
   - mtf_trends

4. **Signal Count Match:** Pine sends 12, Bot expects 12

### PINE-2 (V6) ↔ price_action_v6 Plugin

**Confidence Level:** 30%

**Evidence Against Match:**

1. **Format Mismatch:**
   - Pine: Pipe-separated string `"BULLISH_ENTRY|EURUSD|15|..."`
   - Bot: Object with attributes `getattr(alert, 'alert_type')`

2. **Signal Type Names Mismatch (0/14):**
   | Pine Signal | Bot Expected | Match |
   |-------------|--------------|-------|
   | BULLISH_ENTRY | PA_Breakout_Entry | None |
   | BEARISH_ENTRY | PA_Pullback_Entry | None |
   | SIDEWAYS_BREAKOUT | PA_Momentum_Entry | None |
   | TRENDLINE_BULLISH_BREAK | PA_Support_Bounce | None |
   | TRENDLINE_BEARISH_BREAK | PA_Resistance_Rejection | None |
   | EXIT_BULLISH | PA_Exit_Signal | None |
   | EXIT_BEARISH | PA_Reversal_Exit | None |
   | TREND_PULSE | PA_Trend_Pulse | Partial |
   | MOMENTUM_CHANGE | (not handled) | None |
   | STATE_CHANGE | (not handled) | None |
   | BREAKOUT | (not handled) | None |
   | BREAKDOWN | (not handled) | None |
   | SCREENER_FULL_BULLISH | (not handled) | None |
   | SCREENER_FULL_BEARISH | (not handled) | None |

3. **No Parser Exists:** Bot has no code to parse pipe-separated strings

### PINE-2 (V6) ↔ price_action_1m/5m/15m/1h Plugins

**Confidence Level:** 60%

**Evidence for Partial Match:**

1. **Timeframe Concept Match:**
   - Pine V6 tracks 4 timeframes (1M, 5M, 15M, 1H)
   - Bot has 4 timeframe-specific plugins

2. **Field Names Partially Match:**
   | Pine Field | Bot Field | Match |
   |------------|-----------|-------|
   | symbol (field 2) | symbol | Yes |
   | direction (field 5) | direction | Yes |
   | SL (field 10) | sl_price | Yes |
   | TP1 (field 11) | tp1_price | Yes |
   | TP2 (field 12) | tp2_price | Yes |
   | TP3 (field 13) | tp3_price | Yes |
   | ADX (field 8) | adx | Yes |
   | Confidence (field 7) | conf_score | Partial |

3. **ADX Filtering Match:**
   - Pine: `enableADX`, `adxThresholdWeak`, `adxThresholdStrong`
   - Bot: `min_adx` config per plugin

**Evidence Against Match:**

1. **No Signal Routing:** Timeframe plugins expect pre-parsed dict, not raw alert
2. **No Parser:** Need to convert pipe-separated to dict format
3. **Field Name Mapping:** Pine uses `confidence_score`, Bot uses `conf_score`

---

## SECTION E: COMPATIBILITY REPORT

### PINE-1 (V3) ↔ combined_v3

**Overall Status:** ⚠️ NEEDS MINOR FIXES

#### Field Mapping Table

| Pine Field | Bot Expected | Status | Fix Required |
|------------|--------------|--------|--------------|
| type | type | Match | None |
| signal_type | signal_type | Match | None |
| symbol | symbol | Match | None |
| direction | direction | Match | None |
| tf | tf | Match | None |
| price | price | Match | None |
| consensus_score | consensus_score | Match | None |
| sl_price | sl | Mismatch | Add mapping |
| tp1_price | tp | Mismatch | Add mapping |
| tp2_price | tp | Mismatch | Add mapping |
| mtf_trends | mtf_trends | Match | None |
| market_trend | market_trend | Match | None |
| volume_delta_ratio | volume_delta_ratio | Match | None |
| price_in_ob | price_in_ob | Match | None |
| position_multiplier | position_multiplier | Match | None |

#### Signal Type Mapping

| Pine Signal Type | Bot Signal Type | Status |
|------------------|-----------------|--------|
| Liquidity_Trap_Reversal | Liquidity_Trap | Add alias |
| Mitigation_Test_Entry | Mitigation_Test | Add alias |

#### Code Snippet - Current Bot Field Access

```python
# From entry_logic.py - ISSUE: Field name mismatch
def _calculate_sl_price(self, alert: Any, logic_type: str, order_type: str) -> float:
    sl_price = getattr(alert, "sl", 0.0)  # Pine sends "sl_price"
    return sl_price
```

#### Recommended Fix

```python
# Add field mapping in entry_logic.py
def _calculate_sl_price(self, alert: Any, logic_type: str, order_type: str) -> float:
    # Try Pine field name first, then fallback
    sl_price = getattr(alert, "sl_price", None) or getattr(alert, "sl", 0.0)
    return sl_price

def _calculate_tp_price(self, alert: Any, logic_type: str, order_type: str) -> float:
    tp1 = getattr(alert, "tp1_price", None) or getattr(alert, "tp", 0.0)
    tp2 = getattr(alert, "tp2_price", None)
    return tp1 if order_type == "ORDER_A" else (tp2 or tp1)
```

### PINE-2 (V6) ↔ price_action_v6

**Overall Status:** ❌ BROKEN - NON-FUNCTIONAL

#### Critical Issues

1. **No Parser:** Bot cannot parse pipe-separated alerts
2. **Signal Names Mismatch:** 0/14 signal types match
3. **Field Access Fails:** Bot uses `getattr()` on string

#### Code Snippet - Current Bot Validation

```python
# From plugin.py lines 329-358 - FAILS for V6 Pine alerts
def validate_alert(self, alert: Any) -> bool:
    required_fields = ["symbol", "direction", "alert_type"]
    
    for field in required_fields:
        if not hasattr(alert, field) and not isinstance(alert, dict):
            return False  # V6 Pine alert is a string, not object
```

#### Recommended Fix - V6 Alert Parser

```python
class V6AlertParser:
    """Parse V6 pipe-separated alerts to dict."""
    
    ENTRY_FIELDS = [
        "signal_type", "symbol", "timeframe", "price", "direction",
        "confidence_level", "confidence_score", "adx_value", "adx_strength",
        "sl_price", "tp1_price", "tp2_price", "tp3_price",
        "tf_alignment", "trendline_state"
    ]
    
    def parse(self, alert_string: str) -> Dict[str, Any]:
        fields = alert_string.strip().split("|")
        signal_type = fields[0] if fields else ""
        
        if signal_type in ["BULLISH_ENTRY", "BEARISH_ENTRY"]:
            return self._parse_entry(fields)
        elif signal_type in ["EXIT_BULLISH", "EXIT_BEARISH"]:
            return self._parse_exit(fields)
        elif signal_type == "TREND_PULSE":
            return self._parse_trend_pulse(fields)
        # ... other signal types
        
        return {"signal_type": signal_type, "raw": alert_string}
    
    def _parse_entry(self, fields: List[str]) -> Dict[str, Any]:
        return {
            "signal_type": fields[0],
            "symbol": fields[1],
            "timeframe": fields[2],
            "price": float(fields[3]),
            "direction": fields[4],
            "confidence_level": fields[5] if len(fields) > 5 else "MEDIUM",
            "conf_score": int(fields[6]) if len(fields) > 6 else 50,
            "adx": float(fields[7]) if len(fields) > 7 else 0,
            "adx_strength": fields[8] if len(fields) > 8 else "NA",
            "sl_price": float(fields[9]) if len(fields) > 9 else 0,
            "tp1_price": float(fields[10]) if len(fields) > 10 else 0,
            "tp2_price": float(fields[11]) if len(fields) > 11 else 0,
            "tp3_price": float(fields[12]) if len(fields) > 12 else 0,
        }
```

#### Recommended Fix - V6 Signal Mapper

```python
V6_SIGNAL_MAP = {
    # Pine Signal -> Bot Handler
    "BULLISH_ENTRY": "PA_Breakout_Entry",
    "BEARISH_ENTRY": "PA_Breakout_Entry",
    "SIDEWAYS_BREAKOUT": "PA_Momentum_Entry",
    "TRENDLINE_BULLISH_BREAK": "PA_Support_Bounce",
    "TRENDLINE_BEARISH_BREAK": "PA_Resistance_Rejection",
    "EXIT_BULLISH": "PA_Exit_Signal",
    "EXIT_BEARISH": "PA_Exit_Signal",
    "TREND_PULSE": "PA_Trend_Pulse",
    "BREAKOUT": "PA_Breakout_Entry",
    "BREAKDOWN": "PA_Breakout_Entry",
}
```

### PINE-2 (V6) ↔ Timeframe Plugins

**Overall Status:** ⚠️ NEEDS PARSER + ROUTER

#### Timeframe Routing Table

| Pine Timeframe | Bot Plugin | Dual Orders | SL Mult | Risk Mult |
|----------------|------------|-------------|---------|-----------|
| 1 (1M) | price_action_1m | No | 0.5x | 0.5x |
| 5 (5M) | price_action_5m | Yes | 1.0x | 1.0x |
| 15 (15M) | price_action_15m | No | 1.0x | 1.0x |
| 60 (1H) | price_action_1h | No | 1.0x | 0.625x |

#### Required Components

1. **V6 Alert Parser:** Convert pipe-separated to dict
2. **Timeframe Router:** Route parsed alert to correct plugin
3. **Field Mapper:** Map Pine field names to bot field names

---

## SECTION F: RECOMMENDATIONS

### Priority 1: CRITICAL - V6 Alert Parser

**Effort:** 2-3 hours
**Impact:** Enables V6 signal processing

Create `src/logic_plugins/price_action_v6/alert_parser.py`:
- Parse pipe-separated V6 alerts
- Convert to dict format
- Handle all 14 signal types

### Priority 2: CRITICAL - V6 Signal Mapper

**Effort:** 1-2 hours
**Impact:** Routes V6 signals to handlers

Create signal type mapping in `price_action_v6/plugin.py`:
- Map Pine signal names to bot handler names
- Add missing handlers for new signal types

### Priority 3: HIGH - V3 Field Mapping

**Effort:** 30 minutes
**Impact:** Fixes SL/TP extraction

Update `combined_v3/entry_logic.py`:
- Add fallback for `sl_price` -> `sl`
- Add fallback for `tp1_price`/`tp2_price` -> `tp`

### Priority 4: MEDIUM - V3 Signal Aliases

**Effort:** 15 minutes
**Impact:** Handles naming differences

Update `combined_v3/signal_handlers.py`:
- Add alias: `Liquidity_Trap_Reversal` -> `Liquidity_Trap`
- Add alias: `Mitigation_Test_Entry` -> `Mitigation_Test`

### Priority 5: MEDIUM - V6 Timeframe Router

**Effort:** 2-3 hours
**Impact:** Routes V6 to timeframe plugins

Create `src/logic_plugins/price_action_v6/timeframe_router.py`:
- Parse timeframe from V6 alert
- Route to appropriate plugin (1m/5m/15m/1h)

---

## Summary

| Pine Script | Bot Plugin | Confidence | Status | Action Required |
|-------------|------------|------------|--------|-----------------|
| PINE-1 (V3) | combined_v3 | 95% | ⚠️ Works | Minor field mapping |
| PINE-2 (V6) | price_action_v6 | 30% | ❌ Broken | Parser + Mapper |
| PINE-2 (V6) | price_action_1m | 60% | ⚠️ Partial | Parser + Router |
| PINE-2 (V6) | price_action_5m | 60% | ⚠️ Partial | Parser + Router |
| PINE-2 (V6) | price_action_15m | 60% | ⚠️ Partial | Parser + Router |
| PINE-2 (V6) | price_action_1h | 60% | ⚠️ Partial | Parser + Router |

**Bottom Line:**
- V3 Pine -> combined_v3 Bot: **MOSTLY FUNCTIONAL** (needs minor fixes)
- V6 Pine -> price_action_v6 Bot: **NON-FUNCTIONAL** (needs parser + mapper)
- V6 Pine -> Timeframe Plugins: **PARTIALLY FUNCTIONAL** (needs parser + router)

---

**End of Autonomous Audit Report**
