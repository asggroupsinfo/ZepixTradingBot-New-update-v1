# 🤖 Zepix Trading Bot v2.0

**Advanced Automated Trading Bot for MetaTrader 5 (MT5)**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()
[![Version](https://img.shields.io/badge/Version-4.0-blue)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()

---

## 🚀 Quick Start

### 🖥️ **Windows VM Deployment (Recommended)**

**One-Click Deployment:**
```powershell
# Run as Administrator
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/asggroupsinfo/ZepixTradingBot-old-v6/main/deploy_vm.ps1" -OutFile "deploy_vm.ps1"
.\deploy_vm.ps1
```

**📖 For detailed deployment guide, see:** [DEPLOY_WINDOWS_VM.md](DEPLOY_WINDOWS_VM.md)

---

### 🔧 Manual Installation

#### Prerequisites
- Python 3.12+ (recommended)
- MetaTrader 5 installed and running
- Telegram Bot Token
- MT5 Account credentials

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/asggroupsinfo/ZepixTradingBot-old-v6.git
cd ZepixTradingBot-old-v6

# 2. Create virtual environment
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify .env file (already included in repo)
# Contains: TELEGRAM_TOKEN, MT5_LOGIN, MT5_PASSWORD, etc.

# 5. Start bot
python run_bot.py
```

---

## ✨ Key Features

### 🎯 Dual Order System
- **Order A (TP Trail)**: Uses existing SL system with dynamic risk management
- **Order B (Profit Trail)**: Uses fixed $10 SL for profit booking chains
- Both orders use same lot size, work independently

### 💰 Profit Booking Chains
- 5-level pyramid system (1→2→4→8→16 orders)
- $7 minimum profit per order
- Automatic progression to next levels
- Chain recovery from MT5

### 🔄 Re-entry Systems
- **SL Hunt Re-entry**: Re-enter after SL hit + 1 pip recovery
- **TP Continuation**: Re-enter after TP with 2 pip gap + 50% SL reduction
- **Exit Continuation**: Re-enter after exit signals with 2 pip gap
- Max 2 re-entry levels enforced

### 🛡️ Risk Management
- RR Ratio: 1:1.5 (enforced on all orders)
- Tier-based lot sizing (5 tiers: $5K, $10K, $25K, $50K, $100K)
- Daily/Lifetime loss caps
- Automatic trading pause when caps reached

### 📱 Telegram Integration
- 60 commands for full bot control
- Real-time notifications
- Trend management
- Risk control commands
- Performance analytics

### 📊 Multi-timeframe Analysis
- LOGIC1, LOGIC2, LOGIC3 strategies
- Trend alignment validation
- Entry signal filtering

### ⏰ Forex Session System (v4)
- Session-based trade filtering (Asian, London, NY)
- Interactive Dashboard (`/session`)
- Force Close & Advance Alerts

### 🔊 Voice Alert System
- Real-time audio trade announcements
- "Hands-free" monitoring via Telegram

### 🕰️ Fixed Clock System
- Drift-corrected IST Clock
- Pinned message with real-time status

---

## 📁 Project Structure

```
ZepixTradingBot/
├── src/                    # Core bot source code
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models
│   ├── database.py        # Database operations
│   ├── core/              # Core trading logic
│   │   └── trading_engine.py
│   ├── managers/          # Business logic managers
│   │   ├── dual_order_manager.py
│   │   ├── profit_booking_manager.py
│   │   ├── risk_manager.py
│   │   ├── reentry_manager.py
│   │   └── timeframe_trend_manager.py
│   ├── services/          # Background services
│   │   ├── price_monitor_service.py
│   │   ├── reversal_exit_handler.py
│   │   └── analytics_engine.py
│   ├── clients/           # External integrations
│   │   ├── mt5_client.py
│   │   └── telegram_bot.py
│   ├── processors/        # Data processors
│   │   └── alert_processor.py
│   └── utils/            # Utility functions
│       ├── pip_calculator.py
│       ├── profit_sl_calculator.py
│       └── exit_strategies.py
├── config/               # Configuration files
│   ├── config.json       # Main configuration
│   └── timeframe_trends.json
├── docs/                 # Documentation
│   ├── README.md         # Documentation index
│   ├── DEPLOYMENT_GUIDE.md
│   ├── COMPLETE_FEATURES_SUMMARY.md
│   └── reports/          # Historical reports
├── tests/                # Test files
├── scripts/              # Utility scripts
│   ├── start_bot.py
│   └── windows_setup_admin.bat
├── data/                 # Data files
│   ├── trading_bot.db   # SQLite database
│   └── stats.json       # Statistics
├── logs/                 # Log files
│   └── bot.log
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🚀 Production Status

### ✅ **100% PRODUCTION READY**

**Last Verified:** 2025-01-14

**All Systems Operational:**
- ✅ Zero startup errors
- ✅ All modules loading successfully
- ✅ MT5 connection established
- ✅ All 60 Telegram commands working
- ✅ Dual order system functional
- ✅ Profit booking chains operational
- ✅ All 3 re-entry systems active
- ✅ Risk management enforced
- ✅ Comprehensive error handling

**See:** [FINAL_PRODUCTION_READINESS_REPORT.md](FINAL_PRODUCTION_READINESS_REPORT.md)

---

## 📖 Documentation

### Quick Links
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[Windows Deployment](docs/WINDOWS_DEPLOYMENT_GUIDE.md)** - Windows-specific guide
- **[Features Summary](docs/COMPLETE_FEATURES_SUMMARY.md)** - All features explained
- **[Production Readiness](docs/reports/verification/FINAL_PRODUCTION_READINESS_REPORT.md)** - Pre-deployment checklist
- **[Critical Features Verification](docs/reports/verification/CRITICAL_FEATURES_VERIFICATION_REPORT.md)** - Feature verification
- **[Complete Verification](docs/reports/verification/COMPLETE_BOT_VERIFICATION_REPORT.md)** - Full system verification
- **[Deployment Status](docs/reports/deployment/BOT_DEPLOYMENT_STATUS.md)** - Current deployment status

### Documentation Index
See [docs/README.md](docs/README.md) for complete documentation index.

---

## ⚙️ Configuration

### Main Configuration
File: `config/config.json`

**Key Settings:**
- Dual order system: `dual_order_config`
- Profit booking: `profit_booking_config`
- Risk management: `risk_tiers`
- Re-entry system: `re_entry_config`
- SL systems: `sl_systems`
- RR ratio: `rr_ratio` (default: 1.5)

### Environment Variables
File: `.env` (root level)

**Required:**
```
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server
```

---

## 🔌 TradingView Integration

### Webhook Endpoint
```
POST http://your-server:80/webhook
```

### Alert JSON Format
```json
{
  "type": "entry",
  "symbol": "EURUSD",
  "signal": "buy",
  "tf": "5m",
  "price": 1.1000,
  "strategy": "ZepixPremium"
}
```

**Alert Types:**
- Entry alerts (buy/sell)
- Exit alerts (exit appeared)
- Trend alerts (bull/bear)
- Bias alerts (bull/bear)
- Reversal alerts

See [docs/COMPLETE_FEATURES_SUMMARY.md](docs/COMPLETE_FEATURES_SUMMARY.md) for all alert types.

---

## 📱 Telegram Commands

The bot supports **60 commands** for full control:

### Basic Commands
- `/start` - Start bot and see all commands
- `/status` - Bot status and statistics
- `/pause` - Pause all trading
- `/resume` - Resume trading

### Trading Control
- `/dual_order_status` - Dual order system status
- `/toggle_dual_orders` - Enable/disable dual orders
- `/profit_status` - Profit booking status
- `/toggle_profit_booking` - Enable/disable profit booking

### Risk Management
- `/view_risk_caps` - View loss caps
- `/set_daily_cap [amount]` - Set daily loss cap
- `/set_lifetime_cap [amount]` - Set lifetime loss cap
- `/clear_daily_loss` - Clear daily loss
- `/clear_loss_data` - Clear lifetime loss

### Trend Management
- `/set_trend [symbol] [bull/bear/auto]` - Set trend
- `/show_trends` - Show all trends
- `/trend_matrix` - Trend matrix view
- `/logic1_on` / `/logic1_off` - Toggle LOGIC1
- `/logic2_on` / `/logic2_off` - Toggle LOGIC2
- `/logic3_on` / `/logic3_off` - Toggle LOGIC3

**Full list:** Use `/start` in Telegram to see all 60 commands.

---

## 🧪 Testing

### Run All Tests
```bash
python scripts/run_all_tests.py
```

### Individual Tests
```bash
python tests/test_bot_complete.py
python tests/test_complete_bot.py
python tests/test_dual_sl_system.py
```

### Test Coverage
- ✅ Module imports
- ✅ Configuration loading
- ✅ Telegram commands
- ✅ Profit booking system
- ✅ Re-entry systems
- ✅ Symbol compatibility

---

## 🚨 Emergency Controls

### Telegram Commands
- `/pause` - Immediately pause all trading
- `/resume` - Resume trading
- `/close_all` - Close all open positions
- `/simulation_mode on` - Switch to simulation mode

### API Endpoints
- `GET /health` - Health check
- `GET /status` - Bot status
- `POST /webhook` - TradingView alerts

---

## 📊 Monitoring

### Logs
- **Location:** `logs/bot.log`
- **Rotation:** 10MB max, 5 backups
- **Levels:** INFO, WARNING, ERROR, DEBUG

### 6. Voice & Sessions
New interactive buttons added for instant access:
- **🕒 Sessions**: Opens the Session Manager Dashboard directly.
- **🎙️ Voice Test**: Sends a test voice alert to verify audio configuration.
- **⏰ Clock**: Shows current server time (IST).

These features are available in the **Quick Actions** menu.

### 7. Diagnostics
- **Check Status**: `/status`
- **View Logs**: `/logs`
- **Debug Mode**: Toggle debugging output
ps
- **Levels:** INFO, WARNING, ERROR, DEBUG

### Health Check
```bash
curl http://localhost:80/health
```

### Status Check
```bash
curl http://localhost:80/status
```

---

## 🔍 Logging Architecture

### Log Levels

| Level | Purpose | Usage |
|-------|---------|-------|
| **INFO** (Default) | Production logs | Clean, essential events only |
| **DEBUG** | Troubleshooting | Command traces, detailed diagnostics |
| **WARNING** | Non-critical issues | Alignment failures, margin warnings |
| **ERROR/CRITICAL** | Problems | Errors requiring attention |

### Background Loop Policy

All background monitoring loops run **100% silently** in production:

**Silent Background Processes:**
- ✅ Price monitor (30s intervals)
- ✅ Trade manager (5s intervals)
- ✅ Profit booking chains
- ✅ Telegram polling
- ✅ SL/TP checks
- ✅ Margin health checks

**What Gets Logged:**
- ❌ NO periodic heartbeats
- ❌ NO price check loops
- ❌ NO polling cycles
- ✅ One-time initialization messages
- ✅ Errors and warnings only
- ✅ User-triggered actions
- ✅ Trading alerts (sent to Telegram)

### Changing Log Level

**Via Telegram:**
```
/set_log_level → select DEBUG/INFO/WARNING
```

**Via Config File:**
```bash
# Edit config/log_level.txt
echo INFO > config/log_level.txt
```

**Startup Display:**
```
═══════════════════════════════════════
🚀 BOT STARTING - LOGGING LEVEL: INFO
═══════════════════════════════════════
```

### Log File Size Impact

| Mode | File Growth (per hour) | VPS Impact |
|------|------------------------|------------|
| INFO | ~1-2 MB | Minimal |
| DEBUG | ~20-50 MB | Moderate |

**Recommendation:** Use INFO for production, DEBUG only for troubleshooting.

### For Developers

**Background Loop Guidelines:**
```python
# ❌ DON'T: Log in background loops
while self.is_running:
    logger.info("Checking prices...")  # NO!
    
# ✅ DO: Silent loops, log errors only
while self.is_running:
    try:
        await self._check_opportunities()  # Silent
    except Exception as e:
        logger.error(f"Error: {e}")  # Only errors logged
```

**Important Events:**
- Send to Telegram (user sees immediately)
- Log at WARNING/ERROR level if needed
- Don't spam INFO logs


## 🔧 Troubleshooting

### Common Issues

**1. MT5 Connection Failed**
- Ensure MT5 terminal is running
- Verify credentials in `.env`
- Check server name (case-sensitive)
- Bot auto-falls back to simulation mode

**2. Port Already in Use**
- Bot automatically kills process on port
- Or manually: `netstat -ano | findstr :80`
- Then: `taskkill /F /PID <process_id>`

**3. Telegram Not Working**
- Verify token and chat ID in `.env`
- Check internet connection
- Bot continues without Telegram (logs only)

**See:** [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

---

## 📈 Performance

### System Requirements
- **CPU:** Minimal (async operations)
- **Memory:** ~70MB (stable)
- **Disk:** ~100MB (logs rotate)
- **Network:** Stable internet required

### Optimization
- ✅ Async/await for non-blocking operations
- ✅ Cached symbol mappings
- ✅ Efficient database queries
- ✅ Log rotation prevents disk fill
- ✅ Background tasks at 30s intervals

---

## 🔐 Security

### Safety Features
- ✅ Risk caps enforced
- ✅ Lot size limits
- ✅ RR ratio validation
- ✅ Trading pause on errors
- ✅ Simulation mode for testing

### Best Practices
- Use simulation mode for testing
- Set appropriate loss caps
- Monitor first few trades closely
- Keep emergency commands ready

---

## 📝 Changelog

### v4.0 (Current)
- ✅ Forex Session Manager (Asian/London/NY)
- ✅ Voice Alert System (TTS)
- ✅ Fixed IST Clock & Calendar
- ✅ Interactive Telegram Dashboard (`/session`)
- ✅ Zero Tolerance Verification

### v2.0 (Legacy)
- ✅ Dual order system
- ✅ Profit booking chains (5 levels)
- ✅ All 3 re-entry systems
- ✅ Comprehensive risk management
- ✅ 60 Telegram commands
- ✅ Multi-timeframe analysis
- ✅ Production ready

---

## 🤝 Support

### Documentation
- Main docs: `docs/` folder
- Reports: `docs/reports/` folder
- Guides: See [docs/README.md](docs/README.md)

### Issues
1. Check relevant documentation
2. Review logs: `logs/bot.log`
3. Check health endpoint: `/health`
4. Review test reports

---

## 📄 License

[Your License Here]

---

## 🎯 Version

**v4.0** - Forex Session System & Voice Alerts

**Last Updated:** 2026-01-12

**Status:** ✅ Production Ready

---

## 🔗 Quick Links

- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Features Summary](docs/COMPLETE_FEATURES_SUMMARY.md)
- [Production Readiness](docs/reports/verification/FINAL_PRODUCTION_READINESS_REPORT.md)
- [Verification Report](docs/reports/verification/COMPLETE_BOT_VERIFICATION_REPORT.md)
- [Critical Features](docs/reports/verification/CRITICAL_FEATURES_VERIFICATION_REPORT.md)
- [Deployment Status](docs/reports/deployment/BOT_DEPLOYMENT_STATUS.md)
- [Documentation Index](docs/README.md)

---

**🚀 Ready to trade? Start with the [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)!**
