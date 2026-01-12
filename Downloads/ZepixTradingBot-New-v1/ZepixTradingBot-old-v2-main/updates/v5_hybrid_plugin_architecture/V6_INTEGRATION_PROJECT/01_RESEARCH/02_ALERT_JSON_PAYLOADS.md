# 📡 COMPLETE ALERT JSON PAYLOADS - PINE SCRIPT V6

**File:** `02_ALERT_JSON_PAYLOADS.md`
**Date:** 2026-01-11 04:05 IST
**Source:** `Signals_and_Overlays_V6_Enhanced_Build.pine`
**Standard:** ALL FEATURES ENABLED (ADX, TrendPulse, Risk, Trendline)

---

## 1. ENTRY SIGNALS
**Alerts:** `BULLISH_ENTRY`, `BEARISH_ENTRY`
**Trigger:** `alert(buildAlertMessage(...))`

```text
TYPE|TICKER|TIMEFRAME|PRICE|DIRECTION|CONF_LEVEL|CONF_SCORE|ADX|ADX_STRENGTH|SL|TP1|TP2|TP3|ALIGNMENT|TL_STATUS
```

**Example:**
```text
BULLISH_ENTRY|BTCUSDT|5|45000.50|BUY|HIGH|85|26.5|STRONG|44800.00|45100.00|45200.00|45300.00|5/1|TL_OK
```

---

## 2. EXIT SIGNALS
**Alerts:** `EXIT_BULLISH`, `EXIT_BEARISH`
**Trigger:** `alert("EXIT_..." + ...)`

```text
TYPE|TICKER|TIMEFRAME|PRICE|EXIT_BARS
```

**Example:**
```text
EXIT_BULLISH|BTCUSDT|5|45500.00|15
```

---

## 3. MOMENTUM CHANGE
**Alert:** `MOMENTUM_CHANGE`
**Trigger:** `alert(momMsg_global)`

```text
TYPE|TICKER|TIMEFRAME|ADX_CURR|ADX_STR_CURR|ADX_PREV|ADX_STR_PREV|DIRECTION
```

**Example:**
```text
MOMENTUM_CHANGE|BTCUSDT|5|25.5|STRONG|19.0|WEAK|INCREASING
```

---

## 4. STATE CHANGE
**Alert:** `STATE_CHANGE`
**Trigger:** `alert(stateMsg_global)`

```text
TYPE|TICKER|TIMEFRAME|STATE_CURR|STATE_PREV|ALIGNMENT
```

**Example:**
```text
STATE_CHANGE|BTCUSDT|5|TRENDING_BULLISH|NEUTRAL|5/1
```

---

## 5. TREND PULSE
**Alert:** `TREND_PULSE`
**Trigger:** `alert(buildTrendPulseAlert())`

```text
TYPE|TICKER|TIMEFRAME|BULL_COUNT|BEAR_COUNT|CHANGES|MARKET_STATE
```

**Example:**
```text
TREND_PULSE|BTCUSDT|5|4|2|15:BULL->BEAR,60:SIDE->BEAR|MIXED_BEARISH
```

---

## 6. SIDEWAYS BREAKOUT
**Alert:** `SIDEWAYS_BREAKOUT`
**Trigger:** `alert("SIDEWAYS_BREAKOUT|..." + ...)`

```text
TYPE|TICKER|TIMEFRAME|DIRECTION|ADX_VAL|ADX_STR|PREV_STATE|MOMENTUM
```

**Example:**
```text
SIDEWAYS_BREAKOUT|BTCUSDT|5|BULLISH|26.0|STRONG|SIDEWAYS|INCREASING
```

---

## 7. TRENDLINE BREAKS
**Alerts:** `TRENDLINE_BULLISH_BREAK`, `TRENDLINE_BEARISH_BREAK`
**Trigger:** `alert("TRENDLINE_..." + ...)`

```text
TYPE|TICKER|TIMEFRAME|PRICE|SLOPE|BARS_AGO
```

**Example:**
```text
TRENDLINE_BULLISH_BREAK|BTCUSDT|5|45200.00|12.5|45
```

---

## 8. PATTERN BREAKOUTS
**Alerts:** `BREAKOUT`, `BREAKDOWN`
**Trigger:** `alert("BREAKOUT|..." + ...)`

```text
TYPE|TICKER|TIMEFRAME|LEVEL|TESTS|START_BAR|CURR_BAR
```

**Example:**
```text
BREAKOUT|BTCUSDT|5|46000.00|3|10500|10550
```

---

## 9. SCREENER SIGNALS
**Alerts:** `SCREENER_FULL_BULLISH`, `SCREENER_FULL_BEARISH`
**Trigger:** `alert("SCREENER_..." + ...)`

```text
TYPE|TICKER|TIMEFRAME|COUNT|INDICATORS
```

**Example:**
```text
SCREENER_FULL_BULLISH|BTCUSDT|5|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER
```

---

## ⚠️ PARSING RULES
1. **Delimiter:** `|` (Pipe)
2. **Index 0:** Always Alert Type
3. **Numeric:** Parse String to Float/Int
4. **Variable Length:** Depends on `enableADX`, `includeRiskManagement`, `enableTrendPulse`, `enableTrendline`. **Assumed ALL TRUE** for this document.

**END OF DOCUMENT 02**
