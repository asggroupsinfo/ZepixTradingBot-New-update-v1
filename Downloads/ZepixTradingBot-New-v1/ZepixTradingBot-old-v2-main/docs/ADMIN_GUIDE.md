# Administrator Guide

**Version:** 1.0
**Date:** 2026-01-12
**Type:** Admin Guide

---

## System Requirements

**Hardware Requirements:**
- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- Storage: 10GB free space
- Network: Stable internet connection

**Software Requirements:**
- Python 3.10 or higher
- MetaTrader 5 Terminal
- SQLite 3.x
- Git (for updates)

## Installation

**Step 1: Clone Repository**
```bash
git clone https://github.com/asggroupsinfo/ZepixTradingBot-New-update-v1.git
cd ZepixTradingBot-New-update-v1
```

**Step 2: Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Step 5: Initialize Database**
```bash
python scripts/init_database.py
```

**Step 6: Start Bot**
```bash
python main.py
```

## Configuration Management

**Main Configuration File:** `config/config.json`

**Key Settings:**
```json
{
    "mt5": {
        "login": 12345678,
        "password": "your_password",
        "server": "XMGlobal-MT5"
    },
    "telegram": {
        "controller_token": "BOT_TOKEN_1",
        "notification_token": "BOT_TOKEN_2",
        "analytics_token": "BOT_TOKEN_3",
        "chat_id": -1001234567890
    },
    "plugins": {
        "combined_v3": {
            "enabled": true,
            "risk_percentage": 1.5,
            "max_lot_size": 1.0,
            "daily_loss_limit": 500.0
        }
    }
}
```

**Hot Reload Configuration:**
```
/config_reload <plugin_name>
```

## Plugin Management

**Enable Plugin:**
```
/enable_plugin <plugin_name>
```

**Disable Plugin:**
```
/disable_plugin <plugin_name>
```

**Check Plugin Status:**
```
/status
```

**Plugin Directory Structure:**
```
src/logic_plugins/
├── combined_v3/
│   ├── __init__.py
│   ├── plugin.py
│   ├── config.json
│   └── README.md
└── price_action_1m/
    ├── __init__.py
    ├── plugin.py
    └── config.json
```

## Monitoring & Logging

**Log Files:**
- `logs/bot.log` - Main bot log
- `logs/trades.log` - Trade execution log
- `logs/errors.log` - Error log

**View Live Logs:**
```bash
tail -f logs/bot.log
```

**Log Rotation:**
Logs are automatically rotated daily. Old logs are compressed and stored in `logs/archive/`.

**Health Check:**
```
/health
```
Returns system status including:
- MT5 connection status
- Telegram bot status
- Plugin health
- Database status

## Backup & Recovery

**Database Backup:**
```bash
python scripts/backup_database.py
```
Backups are stored in `backups/` directory.

**Restore Database:**
```bash
python scripts/restore_database.py backups/backup_2026-01-12.db
```

**Configuration Backup:**
```bash
cp config/config.json config/config.json.backup
```

**Emergency Recovery:**
1. Stop the bot: `Ctrl+C` or `/emergency_stop`
2. Restore last known good config
3. Restart: `python main.py`
