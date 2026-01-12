# ZEPIX ULTIMATE BOT v3.0 - Parameter Optimization Guide

This guide provides recommended parameter settings for different market conditions and trading styles.

## Default Settings (Balanced)

These settings work well for most markets and timeframes.

```
Smart Money:
- Structure Length: 5
- Show Last N Order Blocks: 5
- OB Mitigation Method: Close
- Show Last N FVGs: 5
- EHL Mode: Short-Term

Consensus Engine:
- Signal Sensitivity: 50
- Band Multiplier: 1.0
- All indicators enabled

Breakout System:
- Trendline Period: 10
- Retest Type: Wicks
- Sensitivity: 50
- Breakout Period: 5
- Minimum Tests: 2

Risk Management:
- Take Profit 1: 1.5 R:R
- Take Profit 2: 3.0 R:R
- Stop Loss ATR Multiplier: 1.5
- Trailing Stop ATR Mult: 2.0

Conflict Resolution:
- Require MTF Alignment: Yes
- Require Volume Confirmation: Yes
- Block EQH/EQL Trades: Yes
- Minimum Confluence Score: 6
```

## Scalping Settings (1-5 minute charts)

For fast-paced trading on lower timeframes.

```
Smart Money:
- Structure Length: 3
- Show Last N Order Blocks: 3
- OB Mitigation Method: Wick
- EHL Mode: Short-Term

Consensus Engine:
- Signal Sensitivity: 30
- Band Multiplier: 0.6

Breakout System:
- Trendline Period: 5
- Sensitivity: 25
- Breakout Period: 3

Risk Management:
- Take Profit 1: 1.0 R:R
- Take Profit 2: 2.0 R:R
- Stop Loss ATR Multiplier: 1.0
- Use Trailing Stop: Yes

Conflict Resolution:
- Minimum Confluence Score: 5
```

## Swing Trading Settings (1H-4H charts)

For medium-term position trading.

```
Smart Money:
- Structure Length: 8
- Show Last N Order Blocks: 7
- OB Mitigation Method: Close
- EHL Mode: Mid-Term

Consensus Engine:
- Signal Sensitivity: 60
- Band Multiplier: 1.2

Breakout System:
- Trendline Period: 15
- Sensitivity: 50
- Breakout Period: 7
- Minimum Tests: 3

Risk Management:
- Take Profit 1: 2.0 R:R
- Take Profit 2: 4.0 R:R
- Stop Loss ATR Multiplier: 2.0

Conflict Resolution:
- Minimum Confluence Score: 7
```

## Position Trading Settings (Daily+ charts)

For long-term trend following.

```
Smart Money:
- Structure Length: 12
- Show Last N Order Blocks: 10
- OB Mitigation Method: Close
- EHL Mode: Long-Term

Consensus Engine:
- Signal Sensitivity: 80
- Band Multiplier: 1.5

Breakout System:
- Trendline Period: 20
- Sensitivity: 75
- Breakout Period: 10
- Minimum Tests: 3

Risk Management:
- Take Profit 1: 2.5 R:R
- Take Profit 2: 5.0 R:R
- Stop Loss ATR Multiplier: 2.5

Conflict Resolution:
- Minimum Confluence Score: 7
```

## Market-Specific Settings

### Forex (Major Pairs)
- Signal Sensitivity: 50
- Band Multiplier: 1.0
- Minimum Confluence Score: 6
- All modules enabled

### Crypto (BTC, ETH)
- Signal Sensitivity: 40
- Band Multiplier: 1.2
- Stop Loss ATR Multiplier: 2.0
- Minimum Confluence Score: 5

### Indices (NAS100, SPX)
- Signal Sensitivity: 55
- Band Multiplier: 0.8
- Minimum Confluence Score: 6

### Commodities (Gold, Oil)
- Signal Sensitivity: 60
- Band Multiplier: 1.3
- Stop Loss ATR Multiplier: 1.8
- Minimum Confluence Score: 7

## Volatility-Based Adjustments

### High Volatility Markets
- Increase Band Multiplier to 1.5-2.0
- Increase Stop Loss ATR Multiplier to 2.0-2.5
- Increase Minimum Confluence Score to 7-8
- Use Trailing Stop: Yes

### Low Volatility Markets
- Decrease Band Multiplier to 0.6-0.8
- Decrease Stop Loss ATR Multiplier to 1.0-1.2
- Decrease Minimum Confluence Score to 5
- Consider disabling Volatility Squeeze alerts

## Indicator Selection Guide

### Conservative Trading
Enable only:
- MACD
- RSI
- DMI
- PSAR

### Aggressive Trading
Enable all 9 indicators for maximum confluence detection.

### Momentum Focus
Prioritize:
- MACD (Weight: 2)
- Momentum (Weight: 2)
- RSI (Weight: 2)

## Optimization Tips

1. **Start with defaults** and adjust based on backtest results
2. **Test one parameter at a time** to understand its impact
3. **Use bar replay** to verify no repainting
4. **Monitor false signal rate** - if too high, increase confluence score
5. **Adjust for market conditions** - trending vs ranging markets need different settings
6. **Review weekly** and fine-tune based on performance

## Performance Metrics to Track

- Win Rate (Target: 70-80%)
- Profit Factor (Target: 1.8-2.2)
- Max Drawdown (Target: < 15%)
- Average R:R (Target: > 1.5)
- False Signal Rate (Target: < 20%)
