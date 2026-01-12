# ZEPIX ULTIMATE BOT v3.0

A professional-grade Pine Script v5 trading indicator that combines Smart Money Concepts, Consensus Engine, Breakout Detection, Risk Management, and Conflict Resolution into a unified trading system.

## Features

### 5-Layer Architecture

**Layer 1: Smart Money Structure (40% Weight)**
- Market Structure Detection (BOS/CHoCH)
- Volumetric Order Blocks with Displacement
- Fair Value Gaps (FVG) with Magnet Effect
- Liquidity Zones (EQH/EQL/Sweeps)

**Layer 2: Consensus Signal Engine (25% Weight)**
- 9-Indicator Voting System with Weighted Scoring
- ZLEMA + VIDYA Hybrid Overlay
- Volume Delta Analysis

**Layer 3: Price Action Breakout (20% Weight)**
- Adaptive Trendlines (Volatility Adjusted)
- Close-Confirm Breakout Rule
- Pattern Recognition

**Layer 4: Risk Management (10% Weight)**
- Dynamic Position Sizing
- Smart Stop Loss (OB Distal + ATR)
- Multi-Level Take Profit System
- Trailing Stop Mechanism

**Layer 5: Conflict Resolution (5% Weight)**
- Multi-Timeframe Alignment
- Volume Confirmation
- EQH/EQL Zone Blocking

### 10 Trading Signals

1. **Institutional Launchpad** - SMC + Consensus + Breakout alignment
2. **Liquidity Trap Reversal** - Sweep + OB + Volume confirmation
3. **Momentum Breakout** - Trendline break + High consensus
4. **Mitigation Test Entry** - OB retest with volume
5. **Bullish Exit** - Take profit or reversal detection
6. **Bearish Exit** - Take profit or reversal detection
7. **Golden Pocket Flip** - Structure break + Fib retracement
8. **Volatility Squeeze Alert** - Pre-breakout compression
9. **Screener Full Bullish** - All indicators aligned bullish
10. **Screener Full Bearish** - All indicators aligned bearish

## Installation

1. Open TradingView and go to Pine Editor
2. Create a new indicator script
3. Copy the entire contents of `ZEPIX_ULTIMATE_BOT_v3.pine`
4. Paste into the Pine Editor
5. Click "Save" and give it a name
6. Click "Add to Chart"

## Quick Start

1. After adding to chart, the indicator will display:
   - Trading signals as labels (IL, LT, MB, MT, GP, FULL)
   - Order Blocks as colored boxes
   - FVG zones as transparent boxes
   - Dashboard with confluence score and status

2. Configure alerts:
   - Right-click on the chart
   - Select "Add Alert"
   - Choose ZEPIX ULTIMATE BOT v3.0
   - Select desired signal condition
   - Configure notification method

## Configuration

### Main Settings
- **Show Trading Signals**: Enable/disable signal labels
- **Enable Alerts**: Enable real-time notifications
- **Show Dashboard**: Display status table

### Smart Money Settings
- **Structure Length**: Market structure detection sensitivity (2-20)
- **Show Order Blocks**: Display OB zones
- **Show FVGs**: Display Fair Value Gaps
- **Show Equal H/L**: Display liquidity zones

### Consensus Engine
- **Signal Sensitivity**: Adjust indicator sensitivity (10-100)
- **Band Multiplier**: Volatility band width
- Toggle individual indicators (MACD, RSI, Stochastic, etc.)

### Risk Management
- **Take Profit 1/2**: Risk-reward ratios
- **Stop Loss ATR Multiplier**: Stop loss distance
- **Trailing Stop**: Enable/disable trailing stops

### Conflict Resolution
- **Require MTF Alignment**: Multi-timeframe confirmation
- **Require Volume Confirmation**: Volume filter
- **Minimum Confluence Score**: Signal threshold (1-9)

## Signal Interpretation

| Signal | Label | Meaning |
|--------|-------|---------|
| Institutional Launchpad | IL | Strong institutional entry |
| Liquidity Trap | LT | Reversal after liquidity sweep |
| Momentum Breakout | MB | Trendline breakout with momentum |
| Mitigation Test | MT | Order block retest entry |
| Golden Pocket | GP | Fibonacci reversal zone |
| Full Screener | FULL | All indicators aligned |

## Dashboard Indicators

- **Confluence**: Current consensus score (0-9)
- **Trend**: Market structure direction
- **MTF**: Multi-timeframe alignment status
- **Volume**: Volume confirmation status
- **Trade**: Current trade status
- **SMC**: Smart Money zone status

## Performance Targets

- Win Rate: 70-80%
- Profit Factor: 1.8-2.2
- Max Drawdown: < 15%
- Signal Accuracy: > 75%

## Technical Specifications

- Pine Script Version: 5
- Max Bars Back: 5000
- Max Lines: 300
- Max Labels: 300
- Max Boxes: 300

## Support

For issues or feature requests, please open an issue in this repository.

## License

Mozilla Public License 2.0
