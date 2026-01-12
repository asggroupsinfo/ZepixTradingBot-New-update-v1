# 📁 Zepix Trading Bot - Project Structure

## 🎯 Root Directory Layout

```
ZepixTradingBot-old-v2-main/
│
├── 📂 src/                          # Core source code
│   ├── clients/                     # External service clients (MT5, Telegram)
│   ├── core/                        # Trading engine & core logic
│   ├── managers/                    # Business logic managers
│   ├── processors/                  # Alert & data processors
│   ├── services/                    # Background services
│   └── utils/                       # Utility functions
│
├── 📂 config/                       # Configuration files
│   ├── config.json                  # Main bot configuration
│   ├── config_prod.json             # Production config
│   └── base_trends.json             # Trend data storage
│
├── 📂 data/                         # Runtime data & database
│   └── trades.db                    # SQLite trading database
│
├── 📂 logs/                         # Log files
│   └── logs-24-11-25 details.md     # Historical logs
│
├── 📂 docs/                         # Documentation
│   ├── reports/                     # Status & verification reports
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── PRODUCTION_READINESS_REPORT.md
│   │   └── VERIFICATION_REPORT.md
│   ├── tradingview/                 # TradingView setup files
│   │   └── setup_files/             # Indicator code & configs
│   └── QUICK_REFERENCE.md           # Quick command reference
│
├── 📂 tests/                        # Test files
│   ├── test_*.py                    # Unit & integration tests
│   └── verify_*.py                  # Verification scripts
│
├── 📂 scripts/                      # Utility scripts
│
├── 📂 archive/                      # Archived/backup files
│   ├── debug_files/
│   ├── documentation/
│   └── temp_scripts/
│
├── 📂 assets/                       # Reference documents
│   └── *.txt                        # Planning & briefing docs
│
├── 📂 important/                    # Critical reference files
│
├── 📂 important_for_developer/      # Developer documentation
│
├── 📄 run_bot.py                    # Main bot launcher
├── 📄 start_bot_standalone.py       # Standalone launcher
├── 📄 START_BOT.bat                 # Windows batch launcher
├── 📄 requirements.txt              # Python dependencies
├── 📄 README.md                     # Main documentation
├── 📄 .env                          # Environment variables (PRIVATE)
└── 📄 .env.example                  # Environment template

```

---

## 🚀 Quick Start Files

| File | Purpose |
|------|---------|
| `run_bot.py` | Primary bot launcher (recommended) |
| `START_BOT.bat` | Windows one-click launcher |
| `requirements.txt` | Install dependencies: `pip install -r requirements.txt` |
| `.env` | **PRIVATE** - Contains API keys & credentials |

---

## 📋 Important Directories

### **Core Source (`src/`)**
- `clients/telegram_bot.py` - Telegram bot handler (81 commands)
- `clients/mt5_client.py` - MetaTrader 5 connection
- `core/trading_engine.py` - Main trading logic
- `managers/` - Risk, trend, profit booking, re-entry managers
- `services/price_monitor_service.py` - Real-time price tracking

### **Configuration (`config/`)**
- `config.json` - Main settings (risk tiers, symbols, strategies)
- `base_trends.json` - Trend alignment data

### **Documentation (`docs/`)**
- `reports/PRODUCTION_READINESS_REPORT.md` - Go-live checklist
- `tradingview/setup_files/` - TradingView indicators & alert setup
- `QUICK_REFERENCE.md` - Command cheat sheet

### **Tests (`tests/`)**
- Comprehensive test suite for all bot features
- Live verification scripts

---

## 🔧 File Cleanup Done

### ✅ Moved to Proper Locations:
- Documentation → `docs/reports/`
- Logs → `logs/`
- TradingView files → `docs/tradingview/`

### ✅ Removed:
- Old virtual environment folders
- Temporary IDE files (`.cursor`, `.replit`)

---

## 📊 Current Structure Stats

**Total Structure:**
- **Core Modules:** 40+ Python files
- **Test Files:** 30+ test scripts
- **Documentation:** 10+ markdown files
- **Configuration:** 5+ config files

**Active Components:**
- ✅ 3 Trading Strategies (LOGIC1/2/3)
- ✅ 81 Telegram Commands
- ✅ 5 Risk Tiers
- ✅ 18 TradingView Alert Types
- ✅ Dual SL System
- ✅ Profit Booking Manager
- ✅ Re-entry System

---

## 🎯 Next Steps

1. **Check Environment:**
   ```bash
   # Ensure .env is configured
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Bot:**
   ```bash
   python run_bot.py
   # OR
   START_BOT.bat
   ```

4. **View Documentation:**
   - Production Guide: `docs/reports/PRODUCTION_READINESS_REPORT.md`
   - Quick Commands: `docs/QUICK_REFERENCE.md`

---

## 📞 Support

- Check `docs/reports/` for detailed status reports
- Review `important_for_developer/` for dev notes
- See `assets/` for original planning documents

---

**Last Updated:** November 27, 2025  
**Bot Version:** 2.0  
**Status:** ✅ Production Ready
