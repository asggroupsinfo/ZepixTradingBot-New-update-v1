# Zepix Trading Bot v2.0 - Project Overview

## Executive Summary

Zepix Trading Bot v2.0 is a sophisticated automated trading system designed for MetaTrader 5 (MT5) integration. The bot receives trading signals from TradingView via webhooks and executes trades automatically on MT5, with comprehensive risk management, profit booking systems, and Telegram-based control interface.

The system is built on FastAPI for webhook handling, uses SQLite for trade history persistence, and implements an advanced dual-order system with pyramid profit booking chains. It supports multi-timeframe analysis across 10 major forex pairs and gold (XAUUSD).

## Project Purpose and Goals

### Primary Objectives

The Zepix Trading Bot aims to automate the complete trading workflow from signal reception to trade execution and management. The core goals include:

1. **Signal Processing**: Receive and validate TradingView alerts for bias, trend, entry, reversal, and exit signals across multiple timeframes (5m, 15m, 1h, 1d).

2. **Automated Trade Execution**: Place dual orders (Order A: TP Trail, Order B: Profit Trail) with calculated stop-loss and take-profit levels based on configurable risk parameters.

3. **Risk Management**: Implement tier-based lot sizing, daily and lifetime loss caps, and symbol-specific SL configurations to protect capital.

4. **Profit Maximization**: Utilize a 5-level pyramid profit booking system (1→2→4→8→16 orders) to compound profits during favorable market conditions.

5. **Recovery Systems**: Provide autonomous SL Hunt Recovery, TP Continuation, and Exit Continuation mechanisms to recover from stop-loss hits and continue profitable trends.

6. **Remote Control**: Enable complete bot management through a Telegram interface with 60+ commands organized in an intuitive menu system.

## Scope and Capabilities

### Supported Trading Instruments

The bot supports trading on the following symbols:

| Symbol | Description | Volatility | Pip Size |
|--------|-------------|------------|----------|
| XAUUSD | Gold | HIGH | 0.01 |
| EURUSD | Euro/US Dollar | LOW | 0.0001 |
| GBPUSD | British Pound/US Dollar | MEDIUM | 0.0001 |
| USDJPY | US Dollar/Japanese Yen | MEDIUM | 0.01 |
| USDCAD | US Dollar/Canadian Dollar | LOW | 0.0001 |
| AUDUSD | Australian Dollar/US Dollar | LOW | 0.0001 |
| NZDUSD | New Zealand Dollar/US Dollar | LOW | 0.0001 |
| EURJPY | Euro/Japanese Yen | MEDIUM | 0.01 |
| GBPJPY | British Pound/Japanese Yen | HIGH | 0.01 |
| AUDJPY | Australian Dollar/Japanese Yen | MEDIUM | 0.01 |

### Trading Timeframes and Logic

The bot implements three distinct trading logics based on timeframe:

**LOGIC1 (5-Minute Entries)**
- Entry timeframe: 5m
- Trend alignment required: 1H + 15M must agree
- Lot multiplier: 1.25x (aggressive)
- SL multiplier: 1.0x (standard)

**LOGIC2 (15-Minute Entries)**
- Entry timeframe: 15m
- Trend alignment required: 1H + 15M must agree
- Lot multiplier: 1.0x (balanced)
- SL multiplier: 1.5x (wider)

**LOGIC3 (1-Hour Entries)**
- Entry timeframe: 1h
- Trend alignment required: 1D + 1H must agree
- Lot multiplier: 0.625x (conservative)
- SL multiplier: 2.5x (widest)

### Account Tier System

The bot supports five account tiers with corresponding risk parameters:

| Tier | Balance Range | Base Lot Size | Daily Loss Limit | Lifetime Loss Cap |
|------|---------------|---------------|------------------|-------------------|
| $5,000 | < $7,500 | 0.05 | $100 | $500 |
| $10,000 | $7,500 - $17,500 | 0.10 | $200 | $1,000 |
| $25,000 | $17,500 - $37,500 | 0.25 | $500 | $2,500 |
| $50,000 | $37,500 - $75,000 | 0.50 | $1,000 | $5,000 |
| $100,000 | > $75,000 | 1.00 | $2,000 | $10,000 |

## System Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ZEPIX TRADING BOT v2.0                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  TradingView │───▶│   FastAPI    │───▶│   Trading    │          │
│  │   Webhooks   │    │   Server     │    │   Engine     │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                 │                   │
│                                                 ▼                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Telegram   │◀──▶│   Managers   │◀──▶│  MT5 Client  │          │
│  │     Bot      │    │   (Risk,     │    │              │          │
│  └──────────────┘    │   Profit,    │    └──────────────┘          │
│                      │   Re-entry)  │           │                   │
│                      └──────────────┘           ▼                   │
│                             │            ┌──────────────┐          │
│                             ▼            │  MetaTrader  │          │
│                      ┌──────────────┐    │      5       │          │
│                      │   SQLite     │    └──────────────┘          │
│                      │   Database   │                               │
│                      └──────────────┘                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Components

1. **FastAPI Server (main.py)**: Entry point handling webhook endpoints, health checks, and application lifecycle management.

2. **Trading Engine (trading_engine.py)**: Central orchestrator for all trading operations including signal processing, order placement, and trade management.

3. **MT5 Client (mt5_client.py)**: Interface to MetaTrader 5 for order execution, position management, and account information retrieval.

4. **Telegram Bot (telegram_bot.py)**: User interface for bot control with 60+ commands and interactive menu system.

5. **Risk Manager (risk_manager.py)**: Handles lot sizing, loss tracking, and risk validation for all trades.

6. **Dual Order Manager (dual_order_manager.py)**: Creates and manages the dual-order system (Order A and Order B).

7. **Profit Booking Manager (profit_booking_manager.py)**: Manages the 5-level pyramid profit booking chains.

8. **Re-entry Manager (reentry_manager.py)**: Handles SL recovery and TP continuation chains.

9. **Price Monitor Service (price_monitor_service.py)**: Background service monitoring prices for autonomous re-entry opportunities.

10. **Autonomous System Manager (autonomous_system_manager.py)**: Coordinates all autonomous trading operations including recovery and continuation systems.

## Key Features Summary

### Dual Order System

Every entry signal creates two independent orders:

- **Order A (TP Trail)**: Uses the standard SL system with TP continuation capability
- **Order B (Profit Trail)**: Uses fixed $10 SL with profit booking chain integration

Both orders use the same lot size and work independently - if one fails, the other continues.

### Profit Booking Chains

The pyramid system compounds profits through 5 levels:

| Level | Orders | Profit Target | Cumulative Orders |
|-------|--------|---------------|-------------------|
| 0 | 1 | $7 | 1 |
| 1 | 2 | $7 each | 3 |
| 2 | 4 | $7 each | 7 |
| 3 | 8 | $7 each | 15 |
| 4 | 16 | $7 each | 31 |

### Re-entry Systems

1. **SL Hunt Recovery**: Monitors for price recovery after SL hit, places recovery trade with tighter SL
2. **TP Continuation**: After TP hit, continues in same direction with reduced SL
3. **Exit Continuation**: After exit signal, monitors for re-entry opportunity

### Risk Management Features

- Tier-based lot sizing with manual override capability
- Daily and lifetime loss caps with automatic trading halt
- Symbol-specific SL configurations
- Dual SL system (sl-1 ORIGINAL, sl-2 TIGHT)
- Smart lot adjustment when approaching daily limits

## Production Status

The Zepix Trading Bot v2.0 is **100% PRODUCTION READY** as of January 2025. All core systems have been implemented, tested, and verified:

- Webhook processing: Operational
- MT5 integration: Operational
- Telegram interface: Operational (60 commands)
- Risk management: Operational
- Profit booking: Operational
- Re-entry systems: Operational
- Logging system: Operational

## Directory Structure

```
ZepixTradingBot-new-v13/
├── src/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration management
│   ├── models.py               # Data models (Trade, Alert, Chain)
│   ├── database.py             # SQLite database operations
│   ├── core/
│   │   └── trading_engine.py   # Core trading logic
│   ├── clients/
│   │   ├── mt5_client.py       # MetaTrader 5 interface
│   │   ├── telegram_bot.py     # Telegram bot interface
│   │   └── menu_callback_handler.py
│   ├── managers/
│   │   ├── risk_manager.py
│   │   ├── dual_order_manager.py
│   │   ├── profit_booking_manager.py
│   │   ├── reentry_manager.py
│   │   ├── timeframe_trend_manager.py
│   │   └── autonomous_system_manager.py
│   ├── services/
│   │   ├── price_monitor_service.py
│   │   ├── reversal_exit_handler.py
│   │   └── analytics_engine.py
│   ├── processors/
│   │   └── alert_processor.py
│   ├── menu/
│   │   ├── menu_manager.py
│   │   ├── menu_constants.py
│   │   └── [various menu handlers]
│   └── utils/
│       ├── pip_calculator.py
│       ├── profit_sl_calculator.py
│       └── optimized_logger.py
├── config/
│   ├── config.json             # Main configuration
│   └── timeframe_trends.json   # Trend state persistence
├── data/
│   ├── trading_bot.db          # SQLite database
│   └── stats.json              # Risk statistics
├── logs/
│   └── bot.log                 # Application logs
├── docs/                       # Documentation
├── tests/                      # Test files
├── scripts/                    # Utility scripts
├── .env                        # Environment variables
├── .env.example                # Environment template
├── README.md                   # Project readme
└── START_BOT.bat               # Windows startup script
```

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.10+ |
| Web Framework | FastAPI | Latest |
| ASGI Server | Uvicorn | Latest |
| Database | SQLite | 3.x |
| MT5 Integration | MetaTrader5 | Latest |
| Telegram API | python-telegram-bot / requests | Latest |
| Data Validation | Pydantic | v1.x |
| HTTP Client | Requests | Latest |

## Getting Started

For detailed setup instructions, see [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md).

Quick start:
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` with MT5 and Telegram credentials
4. Configure `config/config.json` with trading parameters
5. Run: `python -m uvicorn src.main:app --host 0.0.0.0 --port 8000`

## Related Documentation

- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - Detailed system design
- [FEATURES_SPECIFICATION.md](FEATURES_SPECIFICATION.md) - Complete feature catalog
- [WORKFLOW_PROCESSES.md](WORKFLOW_PROCESSES.md) - Trading workflows
- [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) - Setup guide
- [TELEGRAM_COMMAND_STRUCTURE.md](TELEGRAM_COMMAND_STRUCTURE.md) - Command reference
- [BOT_WORKING_SCENARIOS.md](BOT_WORKING_SCENARIOS.md) - Trade execution scenarios
