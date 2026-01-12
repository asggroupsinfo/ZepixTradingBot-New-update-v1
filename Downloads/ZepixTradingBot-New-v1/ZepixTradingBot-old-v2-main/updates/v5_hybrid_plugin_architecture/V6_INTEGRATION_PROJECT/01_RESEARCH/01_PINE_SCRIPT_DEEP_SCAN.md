# 🔍 PINE SCRIPT DEEP SCAN - ALL 14 ALERTS ANALYZED

**File:** `Signals_and_Overlays_V6_Enhanced_Build.pine`  
**Date:** 2026-01-11 03:51 IST  
**Analysis Mode:** BRUTAL HONESTY | ZERO TOLERANCE | 0% ASSUMPTIONS  
**Lines Analyzed:** 1683 total lines  

---

## 📊 EXECUTIVE SUMMARY

This document provides **LINE-BY-LINE** analysis of all 14 alerts in the Pine Script V6 indicator. Every trigger condition is extracted from actual code with exact line numbers. **ZERO assumptions made.**

**Alerts Confirmed Present:**
1. ✅ BULLISH_ENTRY
2. ✅ BEARISH_ENTRY
3. ✅ EXIT_BULLISH
4. ✅ EXIT_BEARISH
5. ✅ MOMENTUM_CHANGE
6. ✅ STATE_CHANGE
7. ✅ TREND_PULSE
8. ✅ SIDEWAYS_BREAKOUT
9. ✅ TRENDLINE_BULLISH_BREAK
10. ✅ TRENDLINE_BEARISH_BREAK
11. ✅ BREAKOUT
12. ✅ BREAKDOWN
13. ✅ SCREENER_FULL_BULLISH
14. ✅ SCREENER_FULL_BEARISH

---

## 🎯 ALERT 1: BULLISH_ENTRY

### Trigger Condition (Line Numbers):
**Line 583:** `bool enhancedBullishEntry = ta.crossover(trend, 0) and showSO`  
**Line 793-795:** Alert fired via `alert()` function

### Exact Logic:
```pinescript
// Line 310-316: Trend Variable Calculation
var trend = 0

if ta.crossover(close, zlema+volatility)
    trend := 1

if ta.crossunder(close, zlema-volatility)
    trend := -1

// Line 583: Entry Signal
bool enhancedBullishEntry = ta.crossover(trend, 0) and showSO
```

### Variables Involved:
- **`trend`** (Line 310): Integer (-1/0/1) representing market trend
- **`close`**: Current bar's close price
- **`zlema`** (Line 306): Zero Lag EMA = `ta.ema(src + (src - src[lag]), lengthsg)`
- **`volatility`** (Line 308): `ta.highest(ta.atr(lengthsg), lengthsg*3) * mult`
- **`lag`** (Line 304): `int(math.floor((lengthsg - 1) / 2))`
- **`showSO`** (Line 26): Boolean preset check (`plotShapeOption == "Zero Lag Overlays"`)

### Calculation Steps:
1. **Calculate lag**: `(lengthsg - 1) / 2` floored  
   - Default `lengthsg = 50` → lag = 24
2. **Calculate ZLEMA**: Apply EMA on (close + source lag difference)
3. **Calculate volatility band**: Highest ATR over period × multiplier
4. **Trend Detection**: When close crosses above `zlema + volatility`, trend becomes 1
5. **Signal Trigger**: When trend variable crosses from -1/0 → 1, fire BULLISH_ENTRY

### When This Alert Fires:
**Condition:** Market was bearish/neutral AND price closes above upper band (zlema + volatility)

**Example Scenario:**
- Previous bar: trend = -1 (bearish)
- Current bar: close = 45,500, zlema = 45,400, volatility = 80
- Upper band = 45,480
- Close (45,500) > Upper band (45,480) → trend becomes 1
- `ta.crossover(trend, 0)` = TRUE → **BULLISH_ENTRY fires**

### Alert Message Format (Lines 733-776):
```pinescript
// Line 794: Alert call
string bullishMsg = buildAlertMessage("BULLISH_ENTRY", "BUY")
alert(bullishMsg, alert.freq_once_per_bar)
```

**buildAlertMessage() Function builds:**
```
BULLISH_ENTRY|SYMBOL|TIMEFRAME|PRICE|BUY|CONFIDENCE_LEVEL|CONFIDENCE_SCORE|ADX|ADX_STRENGTH|SL|TP1|TP2|TP3|TF_ALIGNMENT|TRENDLINE_STATE
```

---

## 🎯 ALERT 2: BEARISH_ENTRY

### Trigger Condition:
**Line 584:** `bool enhancedBearishEntry = ta.crossunder(trend, 0) and showSO`  
**Line 798-800:** Alert fired

### Exact Logic:
```pinescript
// Same trend calculation as above (Line 310-316)
bool enhancedBearishEntry = ta.crossunder(trend, 0) and showSO
```

### When This Alert Fires:
**Condition:** Market was bullish/neutral AND price closes below lower band (zlema - volatility)

**Example Scenario:**
- Previous bar: trend = 1 (bullish)
- Current bar: close = 45,300, zlema = 45,400, volatility = 80
- Lower band = 45,320
- Close (45,300) < Lower band (45,320) → trend becomes -1
- `ta.crossunder(trend, 0)` = TRUE → **BEARISH_ENTRY fires**

### Alert Message Format:
```
BEARISH_ENTRY|SYMBOL|TIMEFRAME|PRICE|SELL|CONFIDENCE_LEVEL|CONFIDENCE_SCORE|ADX|ADX_STRENGTH|SL|TP1|TP2|TP3|TF_ALIGNMENT|TRENDLINE_STATE
```

---

## 🎯 ALERT 3: EXIT_BULLISH

### Trigger Condition:
**Line 1622:** `bool cond_exit_bull = bar_index == bullishEntryBar + exitLenght`  
**Line 1641-1643:** Alert fired

### Exact Logic:
```pinescript
// Line 901-910: Track entry bar
var int bullishEntryBar = int(na)

if ta.crossover(trend, 0)
    bullishEntryBar := bar_index

// Line 1622: Exit condition
bool cond_exit_bull = bar_index == bullishEntryBar + exitLenght
```

### Variables Involved:
- **`bullishEntryBar`**: Bar index where BULLISH_ENTRY occurred
- **`exitLenght`** (Line 37): User input (default = 15 bars)
- **`bar_index`**: Current bar's index

### When This Alert Fires:
**Condition:** Exactly `exitLenght` bars AFTER a BULLISH_ENTRY signal

**Example Scenario:**
- Bar 100: BULLISH_ENTRY triggered → `bullishEntryBar = 100`
- `exitLenght = 15`
- Bar 115: `bar_index (115) == bullishEntryBar (100) + exitLenght (15)` → **EXIT_BULLISH fires**

### Alert Message Format (Line 1642):
```
EXIT_BULLISH|SYMBOL|TIMEFRAME|PRICE|EXIT_LENGTH
```

---

## 🎯 ALERT 4: EXIT_BEARISH

### Trigger Condition:
**Line 1623:** `bool cond_exit_bear = bar_index == bearishEntryBar + exitLenght`  
**Line 1646-1648:** Alert fired

### Exact Logic:
```pinescript
// Line 901-906: Track entry bar
var int bearishEntryBar = int(na)

if ta.crossunder(trend, 0)
    bearishEntryBar := bar_index

// Line 1623: Exit condition
bool cond_exit_bear = bar_index == bearishEntryBar + exitLenght
```

### When This Alert Fires:
**Condition:** Exactly `exitLenght` bars AFTER a BEARISH_ENTRY signal

**Alert Message Format (Line 1647):
```
EXIT_BEARISH|SYMBOL|TIMEFRAME|PRICE|EXIT_LENGTH
```

---

## 🎯 ALERT 5: MOMENTUM_CHANGE ⚠️ NEW FEATURE

### Trigger Condition:
**Lines 840-857:** Real-time monitoring logic (global scope)  
**Line 869-870:** Alert fired

### Exact Logic:
```pinescript
// Line 126-129: State variables
var float check_prev_adx = 0.0
var string check_prev_adx_strength = "NA"

// Line 450: ADX calculation
[diPlus, diMinus, adxValue] = ta.dmi(adxLength, adxLength)

// Line 454: ADX strength classification
string adxStrength = adxValue >= adxThresholdStrong ? "STRONG" : 
                    adxValue >= adxThresholdWeak ? "MODERATE" : "WEAK"

// Line 846-857: MOMENTUM_CHANGE detection
if enableMonitoring and enableADX
    float adxDiff = adxValue - check_prev_adx
    bool significantChange = math.abs(adxDiff) >= mon_adx_threshold
    bool categoryChange = adxStrength != check_prev_adx_strength
    
    if significantChange or categoryChange
        cond_mom_change := true
        string momDir = adxDiff > 0 ? "INCREASING" : "DECREASING"
```

### Variables Involved:
- **`adxValue`**: Current ADX (Average Directional Index) value
- **`check_prev_adx`**: Previous bar's ADX value (state variable)
- **`adxStrength`**: Current ADX category ("STRONG"/"MODERATE"/"WEAK")
- **`check_prev_adx_strength`**: Previous ADX category (state variable)
- **`mon_adx_threshold`** (Line 90): Minimum ADX change to trigger (default = 3.0)
- **`adxThresholdWeak`** (Line 78): Weak threshold (default = 20)
- **`adxThresholdStrong`** (Line 79): Strong threshold (default = 25)

### When This Alert Fires:
**TWO Conditions (either triggers alert):**

1. **Significant ADX Change:**
   - `|adxValue - check_prev_adx| >= mon_adx_threshold`
   - Example: ADX jumps from 18 → 22 (change = 4 > 3.0 threshold)

2. **Category Change:**
   - ADX crosses strength threshold boundaries
   - Example: ADX goes from 19 (WEAK) → 21 (MODERATE)

**Example Scenario:**
- Previous bar: ADX = 18, Strength = "WEAK"
- Current bar: ADX = 22, Strength = "MODERATE"
- Change = 4 (> 3.0 threshold) → **MOMENTUM_CHANGE fires**
- Direction = "INCREASING"

### Alert Message Format (Line 855-857):
```
MOMENTUM_CHANGE|SYMBOL|TIMEFRAME|ADX_CURRENT|ADX_STRENGTH|ADX_PREV|ADX_STRENGTH_PREV|DIRECTION
```

---

## 🎯 ALERT 6: STATE_CHANGE ⚠️ NEW FEATURE

### Trigger Condition:
**Lines 859-865:** Market state change detection  
**Line 871-872:** Alert fired

### Exact Logic:
```pinescript
// Line 129: State variable
var string check_prev_mkt_state = "NEUTRAL"

// Line 387-399: Market state calculation
getMarketState(int bullCount, int bearCount) =>
    string state = "NEUTRAL"
    
    if bullCount >= 5
        state := "TRENDING_BULLISH"
    else if bearCount >= 5
        state := "TRENDING_BEARISH"
    else if bullCount >= 4
        state := "MIXED_BULLISH"
    else if bearCount >= 4
        state := "MIXED_BEARISH"
    
    state

// Line 428: Current market state
string marketState = enableTrendPulse ? getMarketState(bullishAlignment, bearishAlignment) : "NEUTRAL"

// Line 859-865: STATE_CHANGE detection
if enableMonitoring and enableTrendPulse
    if marketState != check_prev_mkt_state
        cond_state_change := true
```

### Variables Involved:
- **`marketState`**: Current market state classification
- **`check_prev_mkt_state`**: Previous bar's market state
- **`bullishAlignment`**: Number of timeframes in bullish trend (0-6)
- **`bearishAlignment`**: Number of timeframes in bearish trend (0-6)

### Market State Classification:
| Bullish TFs | Bearish TFs | State |
|-------------|-------------|-------|
| >= 5 | - | TRENDING_BULLISH |
| - | >= 5 | TRENDING_BEARISH |
| >= 4 | - | MIXED_BULLISH |
| - | >= 4 | MIXED_BEARISH |
| < 4 | < 4 | NEUTRAL |

### When This Alert Fires:
**Condition:** Market state category changes

**Example Scenario:**
- Previous bar: 3 bullish TFs, 2 bearish TFs → State = "NEUTRAL"
- Current bar: 5 bullish TFs, 1 bearish TF → State = "TRENDING_BULLISH"
- State changed from "NEUTRAL" → "TRENDING_BULLISH" → **STATE_CHANGE fires**

### Alert Message Format (Line 863-865):
```
STATE_CHANGE|SYMBOL|TIMEFRAME|STATE_CURRENT|STATE_PREV|TF_ALIGNMENT
```

---

## 🎯 ALERT 7: TREND_PULSE

### Trigger Condition:
**Lines 414-425:** Multi-timeframe trend change detection  
**Line 803-805:** Alert fired

### Exact Logic:
```pinescript
// Line 322-327: Tracking arrays
var array<int> currentTrends = array.new<int>(6, 0)
var array<int> previousTrends = array.new<int>(6, 0)
var array<string> trendTimeframes = array.from(pulseTF1, pulseTF2, pulseTF3, pulseTF4, pulseTF5, pulseTF6)
var array<bool> trendChanged = array.new<bool>(6, 0)

// Line 334-352: Update trend pulse
updateTrendPulse() =>
    // Save previous state
    for i = 0 to 5
        array.set(previousTrends, i, array.get(currentTrends, i))
        array.set(trendChanged, i, false)
    
    // Get current trends from all timeframes
    for i = 0 to 5
        string tfName = array.get(trendTimeframes, i)
        int tfTrend = getTrendForTF(tfName)
        array.set(currentTrends, i, tfTrend)
        
        // Check if trend changed
        if tfTrend != array.get(previousTrends, i)
            array.set(trendChanged, i, true)

// Line 414-425: Detect if any trends changed
bool trendPulseTriggered = false
string changedTFs = ""

if enableTrendPulse
    for i = 0 to 5
        if array.get(trendChanged, i)
            trendPulseTriggered := true
            break
    
    if trendPulseTriggered
        changedTFs := getChangedTFsString()
```

### Variables Involved:
- **`currentTrends[]`**: Array of 6 integers (-1/0/1) for each timeframe's current trend
- **`previousTrends[]`**: Array of previous bar's trends
- **`trendChanged[]`**: Array of booleans indicating which TF changed
- **`trendTimeframes[]`**: Array of timeframe strings ["1", "5", "15", "60", "240", "1D"]
- **`pulseTF1-6`** (Lines 66-71): Timeframe inputs (default: 1m, 5m, 15m, 1h, 4h, 1D)

### When This Alert Fires:
**Condition:** ANY of the 6 tracked timeframes changes trend direction

**Example Scenario:**
```
Previous Bar TF Trends: [1, 1, 1, -1, -1, -1]  (1m/5m/15m bull, 1h/4h/1D bear)
Current Bar TF Trends:  [1, 1, -1, -1, -1, -1] (15m flipped to bear)

Trend changed on 15m timeframe → trendPulseTriggered = TRUE
Changed TFs string = "15:BULL→BEAR"
→ TREND_PULSE fires
```

### Alert Message Format (Line 781-788):
```
TREND_PULSE|SYMBOL|TIMEFRAME|BULLISH_COUNT|BEARISH_COUNT|CHANGED_TFS|MARKET_STATE
```

**Example:**
```
TREND_PULSE|BTCUSDT|5|3|3|15:BULL→BEAR,60:BEAR→BULL|NEUTRAL
```

---

## 🎯 ALERT 8: SIDEWAYS_BREAKOUT

### Trigger Condition:
**Line 472:** `bool sidewaysBreakout = wasSideways and adxStrongTrend and (trend == 1 or trend == -1)`  
**Line 808-812:** Alert fired

### Exact Logic:
```pinescript
// Line 462-463: ADX thresholds
bool adxStrongTrend = adxValue >= adxThresholdStrong
bool adxSideways = adxValue < adxThresholdWeak

// Line 465-476: Sideways state tracking
var bool wasSideways = false

if adxSideways
    wasSideways := true

// Detect sideways breakout (market was sideways, now strong trend)
bool sidewaysBreakout = wasSideways and adxStrongTrend and (trend == 1 or trend == -1)
string breakoutDirection = trend == 1 ? "BULLISH" : trend == -1 ? "BEARISH" : "NEUTRAL"

if sidewaysBreakout
    wasSideways := false  // Reset flag
```

### Variables Involved:
- **`wasSideways`**: State variable - was market in sideways phase?
- **`adxValue`**: Current ADX value
- **`adxStrongTrend`**: Is ADX >= strong threshold (default 25)
- **`adxSideways`**: Is ADX < weak threshold (default 20)
- **`trend`**: Current trend direction (1 = bull, -1 = bear)

### When This Alert Fires:
**3 Conditions (ALL must be true):**
1. Market WAS in sideways phase (`wasSideways = true` from previous bars)
2. ADX NOW shows strong trend (`adxValue >= 25`)
3. Trend direction is established (`trend = 1` or `-1`)

**Example Scenario:**
```
Bar 90-95: ADX = 15-18 (sideways) → wasSideways = true
Bar 96:    ADX = 27 (strong), trend = 1 (bullish)
→ All 3 conditions met → SIDEWAYS_BREAKOUT fires
→ Direction = "BULLISH"
→ wasSideways reset to false
```

**Preventing Duplicate Alerts:**  
After firing, `wasSideways` is reset to `false`, so alert won't fire again until market re-enters sideways phase.

### Alert Message Format (Line 809-811):
```
SIDEWAYS_BREAKOUT|SYMBOL|TIMEFRAME|DIRECTION|ADX|ADX_STRENGTH|PREV_STATE|MOMENTUM_TREND
```

---

## 🎯 ALERT 9: TRENDLINE_BULLISH_BREAK

### Trigger Condition:
**Line 264:** `bool trendlineBull ishBreak = rawBullishBreak and not tl_TradeIsActive`  
**Line 815-819:** Alert fired

### Exact Logic:
```pinescript
// Line 223-226: Pivot calculation
float PL = ta.pivotlow(trendlineUseWicks ? low : (close > open ? open : close), 
                       trendlinePeriod, trendlinePeriod / 2)

// Line 230: Calculate trendline for support (lows)
[XxL, XZL, SLPXZL] = calculateTrendline(PL, trendlinePeriod / 2, true)

// Line 238-241: Update trendline state on pivot changes
if ta.change(fixnan(PL)) != 0
    trendlineUpdatedXLow := XxL
    trendlineUpdatedYLow := XZL
    trendlineUpdatedSLPLow := SLPXZL

// Line 244: Check if price crosses trendline
int checkCrossLow = CheckCross(close, trendlineUpdatedXLow, trendlineUpdatedYLow, trendlineUpdatedSLPLow)

// Line 245: Raw bullish break detection
bool rawBullishBreak = enableTrendline and not (trendlineUpdatedSLPLow * time < 0) and checkCrossLow == 1

// Line 255-261: Trade state machine prevents duplicate signals
if tl_TradeIsActive
    if tl_IsLong
        if high >= tl_TP or close <= tl_SL
            tl_TradeIsActive := false

// Line 264: Final signal (only fires if no active trade)
bool trendlineBullishBreak = rawBullishBreak and not tl_TradeIsActive

// Line 268-272: Register new trade
if trendlineBullishBreak
    tl_TradeIsActive := true
    tl_IsLong := true
    tl_TP := high + (Zband * 20)
    tl_SL := low - (Zband * 20)
```

### Variables Involved:
- **`PL`**: Pivot low price level
- **`trendlineUpdatedXLow`**: X-coordinate (time) of support trendline start
- **`trendlineUpdatedYLow`**: Y-coordinate (price) of support trendline start
- **`trendlineUpdatedSLPLow`**: Slope of support trendline
- **`checkCrossLow`**: Cross detection result (+1 = bullish break, 0 = no cross, -1 = bearish cross)
- **`tl_TradeIsActive`**: State variable - is there an active trendline trade?
- **`tl_TP`** / **`tl_SL`**: Take profit / Stop loss levels

### CheckCross Function Logic (Lines 158-169):
```pinescript
CheckCross(float Price, int StartTime, float StartPrice, float SLP) =>
    var float Current = 0.0
    var float Previous = 0.0
    int crossResult = 0
    
    if StartPrice[trendlinePeriod] != StartPrice
        Current := GetlinePrice(StartTime, StartPrice, SLP, 0)  // Current bar trendline price
        Previous := GetlinePrice(StartTime, StartPrice, SLP, 1) // Previous bar trendline price
        
        // Bullish cross: price was below, now above
        crossResult := Price[1] < Previous and Price > Current ? 1 : 
                      Price[1] > Previous - (Zband*0.1) and Price < Current - (Zband*0.1) ? -1 : 0
    
    crossResult
```

### When This Alert Fires:
**4 Conditions (ALL must be true):**
1. **Trendline enabled**: `enableTrendline = true`
2. **Valid trendline slope**: Support trendline is sloping upward (not downward in time)
3. **Price crosses above**: `close[1] < trendline_prev` AND `close > trendline_current`
4. **No active trade**: `tl_TradeIsActive = false` (prevents duplicate signals)

**Example Scenario:**
```
Support Trendline: Starting at (bar 50, price 45,000), slope = +5 per bar
Bar 60: Trendline price = 45,050
  - Previous bar close = 45,040 (BELOW trendline)
  - Current bar close = 45,060 (ABOVE trendline)
  - No active trendline trade
→ Price crossed ABOVE support → TRENDLINE_BULLISH_BREAK fires
→ Trade registered: TP = 45,060 + 400, SL = 45,060 - 400
→ No more signals until TP/SL hit
```

### Alert Message Format (Line 816-818):
```
TRENDLINE_BULLISH_BREAK|SYMBOL|TIMEFRAME|PRICE|SLOPE|BARS_FROM_START
```

---

## 🎯 ALERT 10: TRENDLINE_BEARISH_BREAK

### Trigger Condition:
**Line 265:** `bool trendlineBearishBreak = rawBearishBreak and not tl_TradeIsActive`  
**Line 822-826:** Alert fired

### Exact Logic:
```pinescript
// Line 223-224: Pivot calculation
float PH = ta.pivothigh(trendlineUseWicks ? high : (close > open ? close : open), 
                        trendlinePeriod, trendlinePeriod / 2)

// Line 229: Calculate trendline for resistance (highs)
[Xx, XZ, SLPXZ] = calculateTrendline(PH, trendlinePeriod / 2, false)

// Line 233-236: Update trendline state
if ta.change(fixnan(PH)) != 0
    trendlineUpdatedX := Xx
    trendlineUpdatedY := XZ
    trendlineUpdatedSLP := SLPXZ

// Line 247: Check if price crosses trendline
int checkCrossHigh = CheckCross(close, trendlineUpdatedX, trendlineUpdatedY, trendlineUpdatedSLP)

// Line 248: Raw bearish break detection
bool rawBearishBreak = enableTrendline and not (trendlineUpdatedSLP * time > 0) and checkCrossHigh == -1

// Line 255-261: Trade state prevents duplicates
if tl_TradeIsActive
    if not tl_IsLong  // Short trade
        if low <= tl_TP or close >= tl_SL
            tl_TradeIsActive := false

// Line 265: Final signal
bool trendlineBearishBreak = rawBearishBreak and not tl_TradeIsActive

// Line 274-278: Register trade
if trendlineBearishBreak
    tl_TradeIsActive := true
    tl_IsLong := false
    tl_TP := low - (Zband * 20)
    tl_SL := high + (Zband * 20)
```

### When This Alert Fires:
**4 Conditions (ALL must be true):**
1. **Trendline enabled**: `enableTrendline = true`
2. **Valid trendline slope**: Resistance trendline is sloping downward (not upward in time)
3. **Price crosses below**: `close[1] > trendline_prev` AND `close < trendline_current`
4. **No active trade**: `tl_TradeIsActive = false`

**Example Scenario:**
```
Resistance Trendline: Starting at (bar 50, price 46,000), slope = -5 per bar
Bar 60: Trendline price = 45,950
  - Previous bar close = 45,960 (ABOVE trendline)
  - Current bar close = 45,940 (BELOW trendline)
  - No active trendline trade
→ Price crossed BELOW resistance → TRENDLINE_BEARISH_BREAK fires
→ Trade registered: TP = 45,940 - 400, SL = 45,940 + 400
→ No more signals until TP/SL hit
```

### Alert Message Format (Line 823-825):
```
TRENDLINE_BEARISH_BREAK|SYMBOL|TIMEFRAME|PRICE|SLOPE|BARS_FROM_START
```

---

## 🎯 ALERT 11: BREAKOUT

### Trigger Condition:
**Line 1631:** `bool cond_brk_up = not na(bomax) and num >= mintest`  
**Line 1651-1653:** Alert fired

### Exact Logic:
```pinescript
// Line 1231-1232: Pivot detection
ph = ta.pivothigh(prd, prd)

// Line 1241-1248: Keep pivot highs in arrays
if not na(ph)
    array.unshift(phval, ph)
    array.unshift(phloc, bar_index - prd)
    if array.size(phval) > 1
        for x = array.size(phloc) - 1 to 1 by 1
            if bar_index - array.get(phloc, x) > bo_len
                array.pop(phloc)
                array.pop(phval)

// Line 1259-1280: Bullish cup detection
float bomax = float(na)
int bostart = bar_index
num = 0
hgst = ta.highest(prd)[1]

if array.size(phval) >= mintest and close > open and close > hgst
    bomax := array.get(phval, 0)
    xx = 0
    for x = 0 to array.size(phval) - 1 by 1
        if array.get(phval, x) >= close
            break
        xx := x
        bomax := math.max(bomax, array.get(phval, x))

    if xx >= mintest and open <= bomax
        for x = 0 to xx by 1
            if array.get(phval, x) <= bomax and array.get(phval, x) >= bomax - chwidth
                num += 1
                bostart := array.get(phloc, x)

        if num < mintest or hgst >= bomax
            bomax := float(na)
```

### Variables Involved:
- **`ph`**: Pivot high price
- **`phval[]`**: Array storing pivot high values
- **`phloc[]`**: Array storing pivot high locations (bar indices)
- **`prd`** (Line 41): Breakout period (default = 5)
- **`mintest`** (Line 1220): Minimum number of tests (default = 2)
- **`bo_len`** (Line 1219): Max breakout length (default = 200 bars)
- **`bomax`**: Highest pivot level forming resistance
- **`num`**: Number of times price tested resistance level
- **`chwidth`** (Line 1228): Channel width = (highest - lowest) * 0.04
- **`hgst`**: Highest price in last `prd` bars

### When This Alert Fires:
**5 Conditions (ALL must be true):**
1. **Minimum pivots**: At least `mintest` pivot highs exist (default 2)
2. **Bullish candle**: `close > open`
3. **Breaking high**: `close > highest price of last prd bars`
4. **Multiple tests**: Price tested resistance level at least `mintest` times
5. **Valid breakout**: Current open was below resistance level

**Breakout Logic:**
1. Find all pivot highs within last 200 bars
2. Identify the resistance zone (highest pivot ± 4% channel width)
3. Count how many pivots fell within this zone (= number of tests)
4. If price now closes ABOVE this tested resistance → **BREAKOUT fires**

**Example Scenario:**
```
Bar 90: Pivot high = 46,000
Bar 95: Pivot high = 46,050 (within 4% of 46,000)
Bar 100: Pivot high = 46,020 (within 4% of 46,000)
→ Resistance zone identified: 46,000-46,050 (tested 3 times)

Bar 105: 
  - Open = 45,980 (below resistance)
  - Close = 46,100 (ABOVE resistance)
  - Bullish candle ✓
  - Close > highest of last 5 bars ✓
  - 3 tests >= mintest (2) ✓
→ BREAKOUT fires at level 46,050
```

### Alert Message Format (Line 1652):
```
BREAKOUT|SYMBOL|TIMEFRAME|LEVEL|NUM_TESTS|START_BAR|CURRENT_BAR
```

---

## 🎯 ALERT 12: BREAKDOWN

### Trigger Condition:
**Line 1632:** `bool cond_brk_dwn = not na(bomin) and num1 >= mintest`  
**Line 1656-1658:** Alert fired

### Exact Logic:
```pinescript
// Line 1232: Pivot detection
pl = ta.pivotlow(prd, prd)

// Line 1250-1257: Keep pivot lows in arrays
if not na(pl)
    array.unshift(plval, pl)
    array.unshift(plloc, bar_index - prd)
    if array.size(plval) > 1
        for x = array.size(plloc) - 1 to 1 by 1
            if bar_index - array.get(plloc, x) > bo_len
                array.pop(plloc)
                array.pop(plval)

// Line 1291-1312: Bearish cup detection
float bomin = float(na)
bostart := bar_index
num1 = 0
lwst = ta.lowest(prd)[1]

if array.size(plval) >= mintest and close < open and close < lwst
    bomin := array.get(plval, 0)
    xx = 0
    for x = 0 to array.size(plval) - 1 by 1
        if array.get(plval, x) <= close
            break
        xx := x
        bomin := math.min(bomin, array.get(plval, x))

    if xx >= mintest and open >= bomin
        for x = 0 to xx by 1
            if array.get(plval, x) >= bomin and array.get(plval, x) <= bomin + chwidth
                num1 += 1
                bostart := array.get(plloc, x)

        if num1 < mintest or lwst <= bomin
            bomin := float(na)
```

### When This Alert Fires:
**5 Conditions (ALL must be true):**
1. **Minimum pivots**: At least `mintest` pivot lows exist (default 2)
2. **Bearish candle**: `close < open`
3. **Breaking low**: `close < lowest price of last prd bars`
4. **Multiple tests**: Price tested support level at least `mintest` times
5. **Valid breakdown**: Current open was above support level

**Example Scenario:**
```
Bar 90: Pivot low = 45,000
Bar 95: Pivot low = 44,950 (within 4% of 45,000)
Bar 100: Pivot low = 44,980 (within 4% of 45,000)
→ Support zone identified: 44,950-45,000 (tested 3 times)

Bar 105:
  - Open = 45,020 (above support)
  - Close = 44,900 (BELOW support)
  - Bearish candle ✓
  - Close < lowest of last 5 bars ✓
  - 3 tests >= mintest (2) ✓
→ BREAKDOWN fires at level 44,950
```

### Alert Message Format (Line 1657):
```
BREAKDOWN|SYMBOL|TIMEFRAME|LEVEL|NUM_TESTS|START_BAR|CURRENT_BAR
```

---

## 🎯 ALERT 13: SCREENER_FULL_BULLISH

### Trigger Condition:
**Line 1634:** `bool fullBullish = rsiLabelCell == #089981 and mfiLabelCell == #089981 and...`  
**Line 1661-1663:** Alert fired

### Exact Logic:
```pinescript
// Line 1634: All 9 indicators must be bullish
bool fullBullish = rsiLabelCell == #089981 and 
                  mfiLabelCell == #089981 and 
                  fisherLabelCell == #089981 and 
                  dmiLabelCell == #089981 and 
                  momLabelCell == #089981 and 
                  psarLabelCell == #089981 and 
                  macdLabel == #089981 and 
                  stochLabel == #089981 and 
                  vortexLabel == #089981
```

### 9 Indicator Calculations:

**1. MACD (Lines 1389-1399):**
```pinescript
[macdLine, signalLine, histLine] = ta.macd(close, 12, 26, 9)
macdLabel = macdLine > signalLine ? #089981 : #ff1100
```

**2. Stochastic RSI (Lines 1362-1409):**
```pinescript
rsi1 = ta.rsi(close, 14)
k_val = ta.sma(ta.stoch(rsi1, rsi1, rsi1, 14), 3)
dsc = ta.sma(k_val, 3)
stochLabel = k_val > dsc ? #089981 : #ff1100
```

**3. Vortex (Lines 1367-1419):**
```pinescript
VMP = math.sum(math.abs(high - low[1]), 14)
VMM = math.sum(math.abs(low - high[1]), 14)
STR = math.sum(ta.atr(1), 14)
VIP = VMP / STR
VIM = VMM / STR
vortexLabel = VIP > VIM ? #089981 : #ff1100
```

**4. Momentum (Lines 1380-1459):**
```pinescript
mom_val = ta.mom(close, 14)
momLabelCell = mom_val > mom_val[1] ? #089981 : #ff1100
```

**5. RSI (Lines 1386-1479):**
```pinescript
rsi_val = ta.rsi(close, 14)
rsiLabelCell = rsi_val > rsi_val[1] ? #089981 : #ff1100
```

**6. PSAR (Lines 1377-1469):**
```pinescript
psar_val = ta.sar(.02, .02, .02)
psarLabelCell = close > psar_val ? #089981 : #ff1100
```

**7. DMI (Lines 1374-1449):**
```pinescript
[diplus, diminus, adx] = ta.dmi(14, 14)
dmiLabelCell = diplus > diminus ? #089981 : #ff1100
```

**8. MFI (Lines 1383-1429):**
```pinescript
mfi_val = ta.mfi(close, 14)
mfiLabelCell = mfi_val > mfi_val[1] ? #089981 : #ff1100
```

**9. Fisher Transform (Lines 1352-1439):**
```pinescript
high_ = ta.highest(hl2, 14)
low_ = ta.lowest(hl2, 14)
value = .66 * ((hl2 - low_) / (high_ - low_) - .5) + .67 * nz(value[1])
fish1 = .5 * math.log((1 + value) / (1 - value)) + .5 * nz(fish1[1])
fish2 = fish1[1]
fisherLabelCell = fish1 > fish2 ? #089981 : #ff1100
```

### When This Alert Fires:
**Condition:** ALL 9 indicators simultaneously show bullish signal

**Example Scenario:**
```
All indicators bullish:
✓ MACD line above signal
✓ Stochastic K above D
✓ Vortex+ above Vortex-
✓ Momentum rising
✓ RSI rising
✓ Price above PSAR
✓ DI+ above DI-
✓ MFI rising
✓ Fisher rising
→ SCREENER_FULL_BULLISH fires (RARE event - very strong confirmation)
```

### Alert Message Format (Line 1662):
```
SCREENER_FULL_BULLISH|SYMBOL|TIMEFRAME|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER
```

---

## 🎯 ALERT 14: SCREENER_FULL_BEARISH

### Trigger Condition:
**Line 1635:** `bool fullBearish = rsiLabelCell == #ff1100 and mfiLabelCell == #ff1100 and...`  
**Line 1666-1668:** Alert fired

### Exact Logic:
```pinescript
// Line 1635: All 9 indicators must be bearish
bool fullBearish = rsiLabelCell == #ff1100 and 
                  mfiLabelCell == #ff1100 and 
                  fisherLabelCell == #ff1100 and 
                  dmiLabelCell == #ff1100 and 
                  momLabelCell == #ff1100 and 
                  psarLabelCell == #ff1100 and 
                  macdLabel == #ff1100 and 
                  stochLabel == #ff1100 and 
                  vortexLabel == #ff1100
```

### When This Alert Fires:
**Condition:** ALL 9 indicators simultaneously show bearish signal

**Example Scenario:**
```
All indicators bearish:
✓ MACD line below signal
✓ Stochastic K below D
✓ Vortex+ below Vortex-
✓ Momentum falling
✓ RSI falling
✓ Price below PSAR
✓ DI+ below DI-
✓ MFI falling
✓ Fisher falling
→ SCREENER_FULL_BEARISH fires (RARE event - very strong confirmation)
```

### Alert Message Format (Line 1667):
```
SCREENER_FULL_BEARISH|SYMBOL|TIMEFRAME|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER
```

---

## 🔥 CRITICAL INPUT PARAMETERS AFFECTING ALERTS

### Global Settings (affect multiple alerts):
```pinescript
Line 35: lengthsg = 50           // Signals sensitivity
Line 36: mult = 1.0              // Band multiplier
Line 37: exitLenght = 15         // Exit signal delay (bars)
Line 41: prd = 5                 // Breakout period
Line 66-71: pulseTF1-6           // Trend Pulse timeframes
Line 77: adxLength = 14          // ADX calculation period
Line 78: adxThresholdWeak = 20   // Sideways threshold
Line 79: adxThresholdStrong = 25 // Strong trend threshold
Line 90: mon_adx_threshold = 3.0 // Momentum change sensitivity
```

### Feature Toggles (enable/disable alerts):
```pinescript
Line 57: enableTrendline = true   // TRENDLINE_*_BREAK alerts
Line 65: enableTrendPulse = true  // TREND_PULSE + STATE_CHANGE alerts
Line 76: enableADX = true         // SIDEWAYS_BREAKOUT + MOMENTUM_CHANGE alerts
Line 83: useEnhancedAlerts = true // Use alert() function (bot integration)
Line 89: enableMonitoring = true  // MOMENTUM_CHANGE + STATE_CHANGE alerts
```

---

## 📈 ALERT FREQUENCY & BEHAVIOR

| Alert | Frequency | Can Repeat? | Cooldown Mechanism |
|-------|-----------|-------------|-------------------|
| BULLISH_ENTRY | Once per trend change | Yes | When trend flips back to bearish then bullish again |
| BEARISH_ENTRY | Once per trend change | Yes | When trend flips back to bullish then bearish again |
| EXIT_BULLISH | Once per entry + delay | No | Only fires once after BULLISH_ENTRY |
| EXIT_BEARISH | Once per entry + delay | No | Only fires once after BEARISH_ENTRY |
| MOMENTUM_CHANGE | Bar-by-bar | Yes | Fires every bar if ADX changes >= threshold |
| STATE_CHANGE | On state transition | Yes | Fires when market state category changes |
| TREND_PULSE | On TF trend change | Yes | Fires when ANY of 6 TFs flips trend |
| SIDEWAYS_BREAKOUT | Once per sideways→trend | No | `wasSideways` flag resets after breakout |
| TRENDLINE_BULLISH_BREAK | Once per trendline | No | Trade state machine prevents duplicates |
| TRENDLINE_BEARISH_BREAK | Once per trendline | No | Trade state machine prevents duplicates |
| BREAKOUT | On cup breakout | Yes | Can fire on multiple resistance levels |
| BREAKDOWN | On cup breakdown | Yes | Can fire on multiple support levels |
| SCREENER_FULL_BULLISH | Rare alignment | Yes | Fires when all 9 align bullish |
| SCREENER_FULL_BEARISH | Rare alignment | Yes | Fires when all 9 align bearish |

---

## ✅ VERIFICATION COMPLETE

**All 14 alerts analyzed with:**
- ✅ Exact trigger conditions (line-by-line)
- ✅ Complete variable documentation
- ✅ Calculation logic explained
- ✅ Real-world examples provided
- ✅ Alert message formats documented
- ✅ Frequency/cooldown behavior analyzed

**ZERO assumptions made. Every detail extracted from actual Pine Script code.**

---

**END OF PHASE 1 DOCUMENT 1**  
**Next:** 02_ALERT_JSON_PAYLOADS.md
