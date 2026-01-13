# Pine Script to Bot Logic Audit Report

**Audit Date:** 2026-01-13
**Auditor:** Devin AI
**Status:** CRITICAL ISSUES FOUND

## Executive Summary

This audit compares the TradingView Pine Script alert structures with the Python bot implementation to verify trading logic accuracy. The audit reveals **critical mismatches** between V6 Pine alerts and bot handlers that will prevent V6 signals from being processed correctly.

| Component | Status | Severity |
|-----------|--------|----------|
| V3 Pine to Bot | Partial Match | MEDIUM |
| V6 Pine to Bot | Critical Mismatch | HIGH |

---

## SECTION A: V3 Alert Structure

### A.1 Pine Script Source
**File:** `ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine`
**Version:** 3.0

### A.2 Alert Message Format

V3 uses **JSON format** for all alerts:

```pine
// Entry Signal Example (lines 1716-1717)
activeMessage := '{"type":"entry_v3","signal_type":"Institutional_Launchpad","symbol":"{{ticker}}","direction":"buy","tf":"' + timeframe.period + '","price":{{close}},"consensus_score":' + str.tostring(consensusScore) + ',"sl_price":' + str.tostring(smartStopLong) + ',"tp1_price":' + str.tostring(tp1Long) + ',"tp2_price":' + str.tostring(tp2Long) + ',"mtf_trends":"' + mtfString + '","market_trend":' + str.tostring(marketTrend) + ',"volume_delta_ratio":' + str.tostring(volumeDeltaRatio) + ',"price_in_ob":true,"position_multiplier":' + str.tostring(positionMultiplier) + '}'
```

### A.3 V3 Signal Types (12 Total)

**Entry Signals (10):**

| Signal # | Signal Type | Direction | Pine Variable |
|----------|-------------|-----------|---------------|
| 1 | Institutional_Launchpad | buy/sell | `signal1_InstitutionalLaunchpad` |
| 2 | Liquidity_Trap_Reversal | buy/sell | `signal2_LiquidityTrapBull/Bear` |
| 3 | Momentum_Breakout | buy/sell | `signal3_MomentumBreakoutBull/Bear` |
| 4 | Mitigation_Test_Entry | buy/sell | `signal4_MitigationTestBull/Bear` |
| 5 | Golden_Pocket_Flip | buy/sell | `signal7_GoldenPocketFlipBull/Bear` |
| 9 | Screener_Full_Bullish | buy | `signal9_ScreenerFullBullish` |
| 10 | Screener_Full_Bearish | sell | `signal10_ScreenerFullBearish` |
| 12 | Sideways_Breakout | buy/sell | `signal12_SidewaysBreakoutBull/Bear` |

**Exit Signals (2):**

| Signal # | Signal Type | Direction | Pine Variable |
|----------|-------------|-----------|---------------|
| 5 | Bullish_Exit | sell | `signal5_BullishExit` |
| 6 | Bearish_Exit | buy | `signal6_BearishExit` |

**Info Signals (2):**

| Signal # | Signal Type | Type Field | Pine Variable |
|----------|-------------|------------|---------------|
| 8 | Volatility_Squeeze | squeeze_v3 | `signal8_VolatilitySqueeze` |
| 11 | Trend_Pulse | trend_pulse_v3 | `trendPulseTriggered` |

### A.4 V3 Alert Fields

```json
{
  "type": "entry_v3",           // entry_v3, exit_v3, squeeze_v3, trend_pulse_v3
  "signal_type": "Institutional_Launchpad",
  "symbol": "EURUSD",
  "direction": "buy",           // buy or sell
  "tf": "15",                   // timeframe period
  "price": 1.23456,             // close price
  "consensus_score": 7,         // 0-9
  "sl_price": 1.23000,          // calculated stop loss
  "tp1_price": 1.24000,         // take profit 1
  "tp2_price": 1.24500,         // take profit 2
  "mtf_trends": "1,1,-1,1,1",   // comma-separated trend values
  "market_trend": 1,            // 1 (bullish) or -1 (bearish)
  "volume_delta_ratio": 1.5,    // volume confirmation
  "price_in_ob": true,          // in order block
  "position_multiplier": 0.8    // lot size multiplier
}
```

### A.5 Alert Triggers (Conditions)

```pine
// Single consolidated alert (lines 1820-1836)
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

## SECTION B: V3 Bot Implementation

### B.1 Bot Source Files
- `src/logic_plugins/combined_v3/signal_handlers.py`
- `src/logic_plugins/combined_v3/entry_logic.py`
- `src/logic_plugins/combined_v3/routing_logic.py`

### B.2 Signal Handler Mapping

```python
# From signal_handlers.py (lines 46-64)
SIGNAL_HANDLERS = {
    # Entry signals (7)
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
    # Exit signals (2)
    'Bullish_Exit': 'handle_bullish_exit',
    'Bearish_Exit': 'handle_bearish_exit',
    # Info signals (2)
    'Volatility_Squeeze': 'handle_volatility_squeeze',
    'Trend_Pulse': 'handle_trend_pulse'
}
```

### B.3 Entry Processing Logic

```python
# From entry_logic.py (lines 59-165)
async def process_entry(self, alert: Any) -> Dict[str, Any]:
    symbol = getattr(alert, "symbol", "")
    direction = getattr(alert, "direction", "")
    signal_type = getattr(alert, "signal_type", "")
    timeframe = getattr(alert, "tf", "15")
    
    # Step 1: Trend validation
    if not self._is_aggressive_reversal(signal_type):
        trend_valid = await self._validate_trend(symbol, direction, timeframe)
        if not trend_valid:
            return {"success": False, "reason": "trend_not_aligned"}
    
    # Step 2: Determine logic type (LOGIC1/2/3)
    logic_type = self._get_logic_type(timeframe)
    
    # Step 3: Calculate lot sizes
    lot_a = self._calculate_lot_a(balance, sl_pips, symbol, logic_type)
    lot_b = self._calculate_lot_b(lot_a)  # 2x Order A
    
    # Step 4: Calculate SL/TP prices
    sl_a = self._calculate_sl_price(alert, logic_type, "ORDER_A")
    tp_a = self._calculate_tp_price(alert, logic_type, "ORDER_A")
```

### B.4 Order A/B Routing

```python
# From entry_logic.py (lines 220-235)
def _get_logic_type(self, timeframe: str) -> str:
    if timeframe in ["1", "5", "1M", "5M"]:
        return "LOGIC1"   # 5-minute scalping
    elif timeframe in ["15", "15M"]:
        return "LOGIC2"   # 15-minute intraday
    else:
        return "LOGIC3"   # 1-hour swing

# SL Multipliers per logic type
SL_MULTIPLIERS = {
    "LOGIC1": 1.0,   # Base SL
    "LOGIC2": 1.5,   # 1.5x base SL
    "LOGIC3": 2.0    # 2x base SL
}
```

### B.5 SL/TP Calculations

```python
# From entry_logic.py (lines 319-363)
def _calculate_sl_price(self, alert: Any, logic_type: str, order_type: str) -> float:
    sl_price = getattr(alert, "sl", 0.0)  # ISSUE: Pine sends "sl_price"
    return sl_price

def _calculate_tp_price(self, alert: Any, logic_type: str, order_type: str) -> float:
    return getattr(alert, "tp", 0.0)  # ISSUE: Pine sends "tp1_price"/"tp2_price"
```

---

## SECTION C: V6 Alert Structure

### C.1 Pine Script Source
**File:** `Signals_and_Overlays_V6_Enhanced_Build.pine`
**Version:** 6.0 (Real-Time Monitor)

### C.2 Alert Message Format

V6 uses **pipe-separated format** for all alerts:

```pine
// Entry Signal Builder (lines 732-777)
buildAlertMessage(string signalType, string direction) =>
    string msg = ""
    msg += signalType + "|"                    // 1. Signal type
    msg += syminfo.ticker + "|"                // 2. Symbol
    msg += timeframe.period + "|"              // 3. Timeframe
    msg += str.tostring(close, "#.#####") + "|" // 4. Price
    msg += direction + "|"                     // 5. Direction
    
    // For entry signals:
    msg += confLevel + "|"                     // 6. Confidence level
    msg += str.tostring(conf) + "|"            // 7. Confidence score
    msg += str.tostring(adxValue, "#.#") + "|" // 8. ADX value
    msg += adxStrength + "|"                   // 9. ADX strength
    msg += str.tostring(sl, "#.#####") + "|"   // 10. SL price
    msg += str.tostring(tp1, "#.#####") + "|"  // 11. TP1 price
    msg += str.tostring(tp2, "#.#####") + "|"  // 12. TP2 price
    msg += str.tostring(tp3, "#.#####") + "|"  // 13. TP3 price
    msg += str.tostring(bullishAlignment) + "/" + str.tostring(bearishAlignment) + "|" // 14. TF alignment
    msg += (tlBreak ? "TL_BREAK" : "TL_OK") + "|" // 15. Trendline state
```

### C.3 V6 Signal Types (14 Total)

**Entry Signals (5):**

| Signal Type | Direction | Pine Trigger |
|-------------|-----------|--------------|
| BULLISH_ENTRY | BUY | `enhancedBullishEntry` |
| BEARISH_ENTRY | SELL | `enhancedBearishEntry` |
| SIDEWAYS_BREAKOUT | BUY/SELL | `sidewaysBreakout` |
| TRENDLINE_BULLISH_BREAK | BUY | `trendlineBullishBreak` |
| TRENDLINE_BEARISH_BREAK | SELL | `trendlineBearishBreak` |

**Exit Signals (4):**

| Signal Type | Pine Trigger |
|-------------|--------------|
| EXIT_BULLISH | `cond_exit_bull` |
| EXIT_BEARISH | `cond_exit_bear` |
| BREAKOUT | `not na(bomax) and num >= mintest` |
| BREAKDOWN | `not na(bomin) and num1 >= mintest` |

**Info Signals (5):**

| Signal Type | Pine Trigger |
|-------------|--------------|
| TREND_PULSE | `trendPulseTriggered` |
| MOMENTUM_CHANGE | `cond_mom_change` |
| STATE_CHANGE | `cond_state_change` |
| SCREENER_FULL_BULLISH | `fullBullish` |
| SCREENER_FULL_BEARISH | `fullBearish` |

### C.4 V6 Alert Fields (15-Field Structure)

```
BULLISH_ENTRY|EURUSD|15|1.23456|BUY|HIGH|85|25.5|STRONG|1.23000|1.24000|1.24500|1.25000|4/2|TL_OK|
     1          2    3    4     5   6   7   8     9      10      11      12      13    14   15
```

| Field # | Name | Example | Description |
|---------|------|---------|-------------|
| 1 | Signal Type | BULLISH_ENTRY | Alert type identifier |
| 2 | Symbol | EURUSD | Trading symbol |
| 3 | Timeframe | 15 | Chart timeframe |
| 4 | Price | 1.23456 | Entry price |
| 5 | Direction | BUY | Trade direction |
| 6 | Confidence Level | HIGH | HIGH/MEDIUM/LOW |
| 7 | Confidence Score | 85 | 0-100 |
| 8 | ADX Value | 25.5 | Current ADX |
| 9 | ADX Strength | STRONG | WEAK/MODERATE/STRONG |
| 10 | SL Price | 1.23000 | Stop loss |
| 11 | TP1 Price | 1.24000 | Take profit 1 |
| 12 | TP2 Price | 1.24500 | Take profit 2 |
| 13 | TP3 Price | 1.25000 | Take profit 3 |
| 14 | TF Alignment | 4/2 | Bullish/Bearish TF count |
| 15 | Trendline State | TL_OK | TL_BREAK or TL_OK |

### C.5 Alert Triggers

```pine
// From lines 791-826
if useEnhancedAlerts
    // Signal 1: Bullish Entry
    if enhancedBullishEntry
        string bullishMsg = buildAlertMessage("BULLISH_ENTRY", "BUY")
        alert(bullishMsg, alert.freq_once_per_bar)
    
    // Signal 2: Bearish Entry
    if enhancedBearishEntry
        string bearishMsg = buildAlertMessage("BEARISH_ENTRY", "SELL")
        alert(bearishMsg, alert.freq_once_per_bar)
    
    // Signal 9: Trend Pulse
    if trendPulseTriggered and enableTrendPulse
        string pulseMsg = buildTrendPulseAlert()
        alert(pulseMsg, alert.freq_once_per_bar)
    
    // Signal 10: Sideways Breakout
    if sidewaysBreakout and enableADX
        string swMsg = "SIDEWAYS_BREAKOUT|" + syminfo.ticker + "|" + timeframe.period + "|" + 
                      breakoutDirection + "|" + str.tostring(adxValue, "#.#") + "|" + 
                      adxStrength + "|SIDEWAYS|INCREASING"
        alert(swMsg, alert.freq_once_per_bar)
```

---

## SECTION D: V6 Bot Implementation

### D.1 Bot Source Files
- `src/logic_plugins/price_action_v6/alert_handlers.py`
- `src/logic_plugins/price_action_v6/plugin.py`
- `src/logic_plugins/price_action_v6/adx_integration.py`

### D.2 Expected Alert Types

```python
# From alert_handlers.py (lines 55-73)
self.handlers: Dict[str, Callable] = {
    # Entry alerts
    "PA_Breakout_Entry": self.handle_breakout_entry,
    "PA_Pullback_Entry": self.handle_pullback_entry,
    "PA_Reversal_Entry": self.handle_reversal_entry,
    "PA_Momentum_Entry": self.handle_momentum_entry,
    "PA_Support_Bounce": self.handle_support_bounce,
    "PA_Resistance_Rejection": self.handle_resistance_rejection,
    "PA_Trend_Continuation": self.handle_trend_continuation,
    # Exit alerts
    "PA_Exit_Signal": self.handle_exit_signal,
    "PA_Reversal_Exit": self.handle_reversal_exit,
    "PA_Target_Hit": self.handle_target_hit,
    # Info alerts
    "PA_Trend_Pulse": self.handle_trend_pulse,
    "PA_Volatility_Alert": self.handle_volatility_alert,
    "PA_Session_Open": self.handle_session_open,
    "PA_Session_Close": self.handle_session_close,
}
```

### D.3 Timeframe-Specific Logic

```python
# From plugin.py (lines 94-123)
TIMEFRAME_SETTINGS = {
    "1M": {
        "name": "Scalping",
        "dual_orders": False,
        "sl_multiplier": 0.5,
        "lot_multiplier": 0.5,
        "max_hold_minutes": 30
    },
    "5M": {
        "name": "Intraday",
        "dual_orders": False,
        "sl_multiplier": 1.0,
        "lot_multiplier": 1.0,
        "max_hold_minutes": 120
    },
    "15M": {
        "name": "Swing",
        "dual_orders": True,
        "sl_multiplier": 1.5,
        "lot_multiplier": 1.0,
        "max_hold_minutes": 480
    },
    "1H": {
        "name": "Position",
        "dual_orders": True,
        "sl_multiplier": 2.0,
        "lot_multiplier": 0.75,
        "max_hold_minutes": 1440
    }
}
```

### D.4 ADX Filter Implementation

```python
# From alert_handlers.py (lines 463-482)
async def _check_adx_filter(self, symbol: str, threshold: int = 25) -> bool:
    if not hasattr(self.plugin, 'adx_integration') or self.plugin.adx_integration is None:
        return True
    
    try:
        adx_value = self.plugin.adx_integration.get_current_adx(symbol)
        return adx_value >= threshold
    except Exception as e:
        self.logger.warning(f"ADX check error: {e}")
        return True
```

---

## SECTION E: Comparison & Verdict

### E.1 What Matches Perfectly

| Component | V3 | V6 |
|-----------|----|----|
| Signal type concept | Yes | No |
| Direction field | Yes | Yes |
| Symbol field | Yes | Yes |
| Timeframe field | Yes | Yes |
| SL/TP concept | Yes | Yes |
| ADX filtering | Yes | Yes |
| Dual order logic | Yes | Yes |

### E.2 Minor Discrepancies

| Issue | Pine Script | Bot Expected | Severity |
|-------|-------------|--------------|----------|
| V3 Liquidity Trap naming | `Liquidity_Trap_Reversal` | `Liquidity_Trap` | LOW |
| V3 Mitigation Test naming | `Mitigation_Test_Entry` | `Mitigation_Test` | LOW |
| V3 SL field name | `sl_price` | `sl` | MEDIUM |
| V3 TP field names | `tp1_price`, `tp2_price` | `tp` | MEDIUM |

### E.3 Critical Mismatches

#### V6 Alert Type Mismatch

| Pine Sends | Bot Expects | Status |
|------------|-------------|--------|
| `BULLISH_ENTRY` | `PA_Breakout_Entry` | MISMATCH |
| `BEARISH_ENTRY` | `PA_Pullback_Entry` | MISMATCH |
| `SIDEWAYS_BREAKOUT` | `PA_Momentum_Entry` | MISMATCH |
| `TRENDLINE_BULLISH_BREAK` | `PA_Support_Bounce` | MISMATCH |
| `TRENDLINE_BEARISH_BREAK` | `PA_Resistance_Rejection` | MISMATCH |
| `EXIT_BULLISH` | `PA_Exit_Signal` | MISMATCH |
| `EXIT_BEARISH` | `PA_Reversal_Exit` | MISMATCH |
| `TREND_PULSE` | `PA_Trend_Pulse` | PARTIAL |
| `MOMENTUM_CHANGE` | (not handled) | MISSING |
| `STATE_CHANGE` | (not handled) | MISSING |
| `BREAKOUT` | (not handled) | MISSING |
| `BREAKDOWN` | (not handled) | MISSING |

#### V6 Alert Format Mismatch

| Aspect | Pine Script | Bot Expected |
|--------|-------------|--------------|
| Format | Pipe-separated string | Object with attributes |
| Parser | None exists | Expects `getattr(alert, "field")` |
| Field access | String split required | Direct attribute access |

### E.4 Missing Components

| Component | Description | Priority |
|-----------|-------------|----------|
| V6 Alert Parser | Convert pipe-separated string to object | CRITICAL |
| V6 Signal Mapper | Map Pine signal types to bot handlers | CRITICAL |
| V3 Field Mapper | Map `sl_price` to `sl`, `tp1_price` to `tp` | HIGH |
| V6 MOMENTUM_CHANGE handler | Handle ADX momentum changes | MEDIUM |
| V6 STATE_CHANGE handler | Handle market state changes | MEDIUM |
| V6 BREAKOUT/BREAKDOWN handlers | Handle breakout signals | MEDIUM |

### E.5 Recommendations for Fixes

#### Priority 1: V6 Alert Parser (CRITICAL)

Create a parser to convert V6 pipe-separated alerts to objects:

```python
# Recommended implementation
class V6AlertParser:
    FIELD_ORDER = [
        "signal_type", "symbol", "timeframe", "price", "direction",
        "confidence_level", "confidence_score", "adx_value", "adx_strength",
        "sl_price", "tp1_price", "tp2_price", "tp3_price",
        "tf_alignment", "trendline_state"
    ]
    
    def parse(self, alert_string: str) -> Dict[str, Any]:
        fields = alert_string.split("|")
        return {
            self.FIELD_ORDER[i]: fields[i] if i < len(fields) else None
            for i in range(len(self.FIELD_ORDER))
        }
```

#### Priority 2: V6 Signal Type Mapper (CRITICAL)

Create mapping from Pine signal types to bot handlers:

```python
# Recommended implementation
V6_SIGNAL_MAP = {
    "BULLISH_ENTRY": "PA_Breakout_Entry",
    "BEARISH_ENTRY": "PA_Breakout_Entry",  # Same handler, different direction
    "SIDEWAYS_BREAKOUT": "PA_Momentum_Entry",
    "TRENDLINE_BULLISH_BREAK": "PA_Support_Bounce",
    "TRENDLINE_BEARISH_BREAK": "PA_Resistance_Rejection",
    "EXIT_BULLISH": "PA_Exit_Signal",
    "EXIT_BEARISH": "PA_Exit_Signal",
    "TREND_PULSE": "PA_Trend_Pulse",
}
```

#### Priority 3: V3 Field Mapper (HIGH)

Update V3 entry logic to handle Pine field names:

```python
# In entry_logic.py
def _calculate_sl_price(self, alert: Any, logic_type: str, order_type: str) -> float:
    # Try Pine field name first, then fallback
    sl_price = getattr(alert, "sl_price", None) or getattr(alert, "sl", 0.0)
    return sl_price

def _calculate_tp_price(self, alert: Any, logic_type: str, order_type: str) -> float:
    # Try Pine field names first
    tp1 = getattr(alert, "tp1_price", None) or getattr(alert, "tp", 0.0)
    tp2 = getattr(alert, "tp2_price", None)
    return tp1 if order_type == "ORDER_A" else (tp2 or tp1)
```

---

## Summary

| Verdict | V3 | V6 |
|---------|----|----|
| Alert Format | JSON (Good) | Pipe-separated (Needs Parser) |
| Signal Types | 12/12 Matched | 0/14 Matched |
| Field Names | 2 Minor Issues | N/A (No Parser) |
| Overall Status | FUNCTIONAL with fixes | NON-FUNCTIONAL |

**V3 Status:** Mostly functional. Requires field name mapping fixes for `sl_price` and `tp1_price`/`tp2_price`.

**V6 Status:** Non-functional. Requires complete alert parser and signal type mapper implementation before any V6 signals can be processed by the bot.

---

## Appendix: Code Snippets

### A1: V3 Pine Alert Generation (Complete)

```pine
// From ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine lines 1700-1836
mtfString = str.tostring(htfTrend5) + "," + str.tostring(htfTrend4) + "," + str.tostring(htfTrend3) + ","  + str.tostring(htfTrend2) + "," + str.tostring(htfTrend1)

var string activeSignalType = ""
var string activeDirection = ""
var string activeType = ""
var string activeMessage = ""

if signal1_InstitutionalLaunchpad
    activeSignalType := "Institutional_Launchpad"
    activeDirection := "buy"
    activeType := "entry_v3"
    activeMessage := '{"type":"entry_v3","signal_type":"Institutional_Launchpad","symbol":"{{ticker}}","direction":"buy","tf":"' + timeframe.period + '","price":{{close}},"consensus_score":' + str.tostring(consensusScore) + ',"sl_price":' + str.tostring(smartStopLong) + ',"tp1_price":' + str.tostring(tp1Long) + ',"tp2_price":' + str.tostring(tp2Long) + ',"mtf_trends":"' + mtfString + '","market_trend":' + str.tostring(marketTrend) + ',"volume_delta_ratio":' + str.tostring(volumeDeltaRatio) + ',"price_in_ob":true,"position_multiplier":' + str.tostring(positionMultiplier) + '}'

// ... (other signals follow same pattern)

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

### A2: V6 Pine Alert Generation (Complete)

```pine
// From Signals_and_Overlays_V6_Enhanced_Build.pine lines 732-826
buildAlertMessage(string signalType, string direction) =>
    string msg = ""
    msg += signalType + "|"
    msg += syminfo.ticker + "|"
    msg += timeframe.period + "|"
    msg += str.tostring(close, "#.#####") + "|"
    msg += direction + "|"
    
    if signalType == "BULLISH_ENTRY" or signalType == "BEARISH_ENTRY"
        int conf = direction == "BUY" ? bullishConfidence : bearishConfidence
        string confLevel = getConfidenceLevel(conf)
        msg += confLevel + "|"
        msg += str.tostring(conf) + "|"
        
        if enableADX
            msg += str.tostring(adxValue, "#.#") + "|" + adxStrength + "|"
        else
            msg += "NA|NA|"
        
        if includeRiskManagement
            float sl = direction == "BUY" ? bullishSL : bearishSL
            float tp1 = direction == "BUY" ? bullishTP1 : bearishTP1
            float tp2 = direction == "BUY" ? bullishTP2 : bearishTP2
            float tp3 = direction == "BUY" ? bullishTP3 : bearishTP3
            
            msg += str.tostring(sl, "#.#####") + "|"
            msg += str.tostring(tp1, "#.#####") + "|"
            msg += str.tostring(tp2, "#.#####") + "|"
            msg += str.tostring(tp3, "#.#####") + "|"
        
        if enableTrendPulse
            msg += str.tostring(bullishAlignment) + "/" + str.tostring(bearishAlignment) + "|"
        
        if enableTrendline
            bool tlBreak = direction == "BUY" ? trendlineBullishBreak : trendlineBearishBreak
            msg += (tlBreak ? "TL_BREAK" : "TL_OK") + "|"
    
    msg

if useEnhancedAlerts
    if enhancedBullishEntry
        string bullishMsg = buildAlertMessage("BULLISH_ENTRY", "BUY")
        alert(bullishMsg, alert.freq_once_per_bar)
    
    if enhancedBearishEntry
        string bearishMsg = buildAlertMessage("BEARISH_ENTRY", "SELL")
        alert(bearishMsg, alert.freq_once_per_bar)
```

---

**End of Audit Report**
