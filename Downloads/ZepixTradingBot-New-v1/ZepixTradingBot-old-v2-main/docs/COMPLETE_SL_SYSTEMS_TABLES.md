# Complete SL Systems Configuration Tables

**Document Version:** 1.0  
**Date:** 2025-12-24  
**Source:** config.json & config.py

---

## Overview

This document contains complete tables for all **4 SL Systems** implemented in the Zepix Trading Bot:

**Order A (TP_TRAIL):**
1. **sl-1**: SL-1 ORIGINAL (Wide/Conservative)
2. **sl-2**: SL-2 RECOMMENDED (Tight/Aggressive)

**Order B (PROFIT_TRAIL):**
3. **SL-1.1**: Logic-Specific SL
4. **SL-2.1**: Universal Fixed SL

---

## Order A: TP_TRAIL SL Systems

### Table 1: sl-1 "SL-1 ORIGINAL" (Wide/Conservative)

**Description:** User approved volatility-based SL system with wide breathing room

| Symbol | Account Tier | SL (Pips) | Risk ($) | Risk (%) |
|---|---|---|---|---|
| **XAUUSD** | $5,000 | 1000 | $50 | 1.0% |
| **XAUUSD** | $10,000 | 1500 | $150 | 1.5% |
| **XAUUSD** | $25,000 | 500 | $500 | 2.0% |
| **XAUUSD** | $50,000 | 500 | $1250 | 2.5% |
| **XAUUSD** | $100,000 | 600 | $3000 | 3.0% |
| **EURUSD** | $5,000 | 150 | $75 | 1.5% |
| **EURUSD** | $10,000 | 150 | $150 | 1.5% |
| **EURUSD** | $25,000 | 50 | $500 | 2.0% |
| **EURUSD** | $50,000 | 40 | $1000 | 2.0% |
| **EURUSD** | $100,000 | 40 | $2000 | 2.0% |
| **GBPUSD** | $5,000 | 150 | $75 | 1.5% |
| **GBPUSD** | $10,000 | 150 | $150 | 1.5% |
| **GBPUSD** | $25,000 | 50 | $500 | 2.0% |
| **GBPUSD** | $50,000 | 40 | $1000 | 2.0% |
| **GBPUSD** | $100,000 | 50 | $2500 | 2.5% |
| **AUDUSD** | $5,000 | 150 | $75 | 1.5% |
| **AUDUSD** | $10,000 | 150 | $150 | 1.5% |
| **AUDUSD** | $25,000 | 50 | $500 | 2.0% |
| **AUDUSD** | $50,000 | 40 | $1000 | 2.0% |
| **AUDUSD** | $100,000 | 50 | $2500 | 2.5% |
| **USDCAD** | $5,000 | 150 | $75 | 1.5% |
| **USDCAD** | $10,000 | 150 | $150 | 1.5% |
| **USDCAD** | $25,000 | 50 | $500 | 2.0% |
| **USDCAD** | $50,000 | 40 | $1000 | 2.0% |
| **USDCAD** | $100,000 | 50 | $2500 | 2.5% |
| **NZDUSD** | $5,000 | 150 | $75 | 1.5% |
| **NZDUSD** | $10,000 | 150 | $150 | 1.5% |
| **NZDUSD** | $25,000 | 50 | $500 | 2.0% |
| **NZDUSD** | $50,000 | 40 | $1000 | 2.0% |
| **NZDUSD** | $100,000 | 50 | $2500 | 2.5% |
| **USDJPY** | $5,000 | 166 | $75 | 1.5% |
| **USDJPY** | $10,000 | 166 | $150 | 1.5% |
| **USDJPY** | $25,000 | 55 | $500 | 2.0% |
| **USDJPY** | $50,000 | 44 | $1000 | 2.0% |
| **USDJPY** | $100,000 | 55 | $2500 | 2.5% |
| **EURJPY** | $5,000 | 111 | $50 | 1.0% |
| **EURJPY** | $10,000 | 111 | $100 | 1.0% |
| **EURJPY** | $25,000 | 41 | $375 | 1.5% |
| **EURJPY** | $50,000 | 44 | $1000 | 2.0% |
| **EURJPY** | $100,000 | 44 | $2000 | 2.0% |
| **GBPJPY** | $5,000 | 111 | $50 | 1.0% |
| **GBPJPY** | $10,000 | 111 | $100 | 1.0% |
| **GBPJPY** | $25,000 | 41 | $375 | 1.5% |
| **GBPJPY** | $50,000 | 44 | $1000 | 2.0% |
| **GBPJPY** | $100,000 | 44 | $2000 | 2.0% |
| **AUDJPY** | $5,000 | 111 | $50 | 1.0% |
| **AUDJPY** | $10,000 | 111 | $100 | 1.0% |
| **AUDJPY** | $25,000 | 41 | $375 | 1.5% |
| **AUDJPY** | $50,000 | 44 | $1000 | 2.0% |
| **AUDJPY** | $100,000 | 44 | $2000 | 2.0% |

---

### Table 2: sl-2 "SL-2 RECOMMENDED" (Tight/Aggressive)

**Description:** Realistic tighter SL system for aggressive trading

| Symbol | Account Tier | SL (Pips) | Risk ($) | Risk (%) |
|---|---|---|---|---|
| **XAUUSD** | $5,000 | 500 | $25 | 1.0% |
| **XAUUSD** | $10,000 | 800 | $80 | 1.5% |
| **XAUUSD** | $25,000 | 300 | $300 | 2.0% |
| **XAUUSD** | $50,000 | 300 | $750 | 2.5% |
| **XAUUSD** | $100,000 | 200 | $1000 | 3.0% |
| **EURUSD** | $5,000 | 100 | $50 | 1.5% |
| **EURUSD** | $10,000 | 100 | $100 | 1.5% |
| **EURUSD** | $25,000 | 35 | $350 | 2.0% |
| **EURUSD** | $50,000 | 30 | $750 | 2.0% |
| **EURUSD** | $100,000 | 30 | $1500 | 2.0% |
| **GBPUSD** | $5,000 | 120 | $60 | 1.5% |
| **GBPUSD** | $10,000 | 120 | $120 | 1.5% |
| **GBPUSD** | $25,000 | 40 | $400 | 2.0% |
| **GBPUSD** | $50,000 | 35 | $875 | 2.0% |
| **GBPUSD** | $100,000 | 40 | $2000 | 2.5% |
| **AUDUSD** | $5,000 | 120 | $60 | 1.5% |
| **AUDUSD** | $10,000 | 120 | $120 | 1.5% |
| **AUDUSD** | $25,000 | 40 | $400 | 2.0% |
| **AUDUSD** | $50,000 | 35 | $875 | 2.0% |
| **AUDUSD** | $100,000 | 40 | $2000 | 2.5% |
| **USDCAD** | $5,000 | 120 | $60 | 1.5% |
| **USDCAD** | $10,000 | 120 | $120 | 1.5% |
| **USDCAD** | $25,000 | 40 | $400 | 2.0% |
| **USDCAD** | $50,000 | 35 | $875 | 2.0% |
| **USDCAD** | $100,000 | 40 | $2000 | 2.5% |
| **NZDUSD** | $5,000 | 120 | $60 | 1.5% |
| **NZDUSD** | $10,000 | 120 | $120 | 1.5% |
| **NZDUSD** | $25,000 | 40 | $400 | 2.0% |
| **NZDUSD** | $50,000 | 35 | $875 | 2.0% |
| **NZDUSD** | $100,000 | 40 | $2000 | 2.5% |
| **USDJPY** | $5,000 | 130 | $58 | 1.5% |
| **USDJPY** | $10,000 | 130 | $117 | 1.5% |
| **USDJPY** | $25,000 | 45 | $405 | 2.0% |
| **USDJPY** | $50,000 | 38 | $855 | 2.0% |
| **USDJPY** | $100,000 | 45 | $2025 | 2.5% |
| **EURJPY** | $5,000 | 80 | $38 | 1.0% |
| **EURJPY** | $10,000 | 80 | $76 | 1.0% |
| **EURJPY** | $25,000 | 30 | $285 | 1.5% |
| **EURJPY** | $50,000 | 35 | $831 | 2.0% |
| **EURJPY** | $100,000 | 35 | $1662 | 2.0% |
| **GBPJPY** | $5,000 | 80 | $36 | 1.0% |
| **GBPJPY** | $10,000 | 80 | $72 | 1.0% |
| **GBPJPY** | $25,000 | 30 | $270 | 1.5% |
| **GBPJPY** | $50,000 | 35 | $788 | 2.0% |
| **GBPJPY** | $100,000 | 35 | $1575 | 2.0% |
| **AUDJPY** | $5,000 | 80 | $37 | 1.0% |
| **AUDJPY** | $10,000 | 80 | $74 | 1.0% |
| **AUDJPY** | $25,000 | 30 | $276 | 1.5% |
| **AUDJPY** | $50,000 | 35 | $805 | 2.0% |
| **AUDJPY** | $100,000 | 35 | $1610 | 2.0% |

---

## Order B: PROFIT_TRAIL SL Systems

### Table 3: SL-1.1 "Logic-Specific SL"

**Description:** Variable SL based on trading strategy

**Configuration:**

| Strategy | SL Amount ($) | Description |
|---|---|---|
| **LOGIC1** | $20.00 | Conservative - Tighter SL for smaller accounts |
| **LOGIC2** | $40.00 | Balanced - Medium risk |
| **LOGIC3** | $50.00 | Aggressive - Wider SL for trend-following |

**Key Features:**
- Dollar-based SL (not pip-based)
- Independent of account tier
- Independent of symbol
- Adapts based on strategy logic only

**Example Calculation:**
- Entry: $2000 XAUUSD BUY
- Strategy: LOGIC1
- SL Amount: $20
- Lot Size: 0.1
- Calculated SL Price: ~$1998 (varies by lot and pip value)

---

### Table 4: SL-2.1 "Universal Fixed SL"

**Description:** Fixed $10 SL for all logics and symbols

**Configuration:**

| Strategy | SL Amount ($) | Description |
|---|---|---|
| **ALL (LOGIC1/2/3)** | $10.00 | Universal - Same for all strategies |

**Key Features:**
- Fixed $10 regardless of strategy
- Independent of account tier
- Independent of symbol
- Simplest SL system for profit compounding
- Enables tighter risk management

**Example Calculation:**
- Entry: $2000 XAUUSD BUY
- Strategy: ANY (LOGIC1/2/3)
- SL Amount: $10
- Lot Size: 0.1
- Calculated SL Price: ~$1999 (varies by lot and pip value)

---

## Comparison Summary

### Order A (TP_TRAIL) Systems

| Feature | sl-1 ORIGINAL | sl-2 RECOMMENDED |
|---|---|---|
| **Measurement** | Pips | Pips |
| **Adaptability** | Tier & Symbol | Tier & Symbol |
| **Risk Style** | Wide/Conservative | Tight/Aggressive |
| **XAUUSD $5K** | 1000 pips ($50) | 500 pips ($25) |
| **EURUSD $5K** | 150 pips ($75) | 100 pips ($50) |
| **Volatility** | High tolerance | Lower tolerance |
| **Use Case** | Beginners, volatile markets | Experienced traders |

### Order B (PROFIT_TRAIL) Systems

| Feature | SL-1.1 Logic-Specific | SL-2.1 Universal Fixed |
|---|---|---|
| **Measurement** | Dollars | Dollars |
| **Adaptability** | Strategy-dependent | None (fixed) |
| **Risk Style** | Variable | Ultra-tight |
| **LOGIC1** | $20 | $10 |
| **LOGIC2** | $40 | $10 |
| **LOGIC3** | $50 | $10 |
| **Complexity** | Medium | Low |
| **Use Case** | Flexible profit trailing | Simple compounding |

---

## Telegram Switch Commands

| Order | Current System | Switch Command | New System |
|---|---|---|---|
| **Order A** | sl-1 → sl-2 | `/switch_sl_system sl-2` | SL-2 RECOMMENDED |
| **Order A** | sl-2 → sl-1 | `/switch_sl_system sl-1` | SL-1 ORIGINAL |
| **Order B** | SL-1.1 → SL-2.1 | `/profit_sl_mode SL-2.1` | Universal Fixed |
| **Order B** | SL-2.1 → SL-1.1 | `/profit_sl_mode SL-1.1` | Logic-Specific |

---

**END OF DOCUMENT**
