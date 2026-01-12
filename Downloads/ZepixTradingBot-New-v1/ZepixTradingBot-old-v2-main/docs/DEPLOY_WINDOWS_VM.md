# Windows VM Deployment Guide - ZepixTradingBot v2.0

## Prerequisites
- Windows 10/11 or Windows Server
- Python 3.12 installed
- MetaTrader 5 installed and logged in
- Internet connection
- Admin rights on VM

## Step-by-Step Deployment

### 1. Install Python 3.12
```powershell
# Download from: https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
```

### 2. Install MetaTrader 5
```powershell
# Download from: https://www.metatrader5.com/en/download
# After installation, login with:
# Account: 308646228
# Password: Fast@@2801@@!!!
# Server: XMGlobal-MT5 6
```

### 3. Clone Repository
```powershell
# Open PowerShell as Administrator
cd C:\
git clone https://github.com/asggroupsinfo/ZepixTradingBot-old-v6.git
cd ZepixTradingBot-old-v6
```

### 4. Create Virtual Environment
```powershell
python -m venv venv
```

### 5. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get execution policy error, run:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 6. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Verify Configuration Files

**Check `.env` file exists with credentials:**
```powershell
Get-Content .env
```

Should show:
```
TELEGRAM_TOKEN=8526101969:AAF9fqQlPbNUkb1fg3vylwG4uDNiz-Z9IY4
TELEGRAM_CHAT_ID=2139792302
MT5_LOGIN=308646228
MT5_PASSWORD=Fast@@2801@@!!!
MT5_SERVER=XMGlobal-MT5 6
```

**Check `config/config.json` exists:**
```powershell
Get-Content config\config.json
```

### 8. Open Required Port (for Webhook)
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "ZepixBot Webhook" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 9. Test MT5 Connection
```powershell
python -c "import MetaTrader5 as mt5; print('MT5 Version:', mt5.__version__); mt5.initialize(); info = mt5.account_info(); print('Account:', info.login if info else 'Not logged in'); mt5.shutdown()"
```

### 10. Start the Bot
```powershell
python run_bot.py
```

## Expected Output on Successful Start:

```
========================================
ZepixTradingBot v2.0 - Production Mode
========================================
Environment: PRODUCTION
Config loaded: config_prod.json
Telegram Token: 8526******
MT5 Account: 308646228

2024-11-27 10:30:15 - INFO - MT5 initialized successfully
2024-11-27 10:30:15 - INFO - Account: 308646228
2024-11-27 10:30:15 - INFO - Balance: $9288.10
2024-11-27 10:30:15 - INFO - Server: XMGlobal-MT5 6
2024-11-27 10:30:16 - INFO - Telegram bot started polling...
2024-11-27 10:30:16 - INFO - Webhook server started on http://127.0.0.1:8000
2024-11-27 10:30:16 - SUCCESS - Bot is fully operational!
```

## Automatic Startup (Optional)

### Create Windows Service using NSSM:

1. Download NSSM: https://nssm.cc/download
2. Install as service:

```powershell
# Run as Administrator
nssm install ZepixTradingBot "C:\ZepixTradingBot-old-v6\venv\Scripts\python.exe"
nssm set ZepixTradingBot AppDirectory "C:\ZepixTradingBot-old-v6"
nssm set ZepixTradingBot AppParameters "run_bot.py"
nssm set ZepixTradingBot DisplayName "Zepix Trading Bot v2.0"
nssm set ZepixTradingBot Description "Automated MT5 Trading Bot with Telegram Integration"
nssm set ZepixTradingBot Start SERVICE_AUTO_START
nssm start ZepixTradingBot
```

### Or Create Scheduled Task:

```powershell
# Run as Administrator
$action = New-ScheduledTaskAction -Execute "C:\ZepixTradingBot-old-v6\venv\Scripts\python.exe" -Argument "C:\ZepixTradingBot-old-v6\run_bot.py" -WorkingDirectory "C:\ZepixTradingBot-old-v6"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "ZepixTradingBot" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Start-ScheduledTask -TaskName "ZepixTradingBot"
```

## Troubleshooting

### Bot not starting?
```powershell
# Check Python version
python --version  # Should be 3.12.x

# Check MT5 is running
Get-Process -Name "terminal64" -ErrorAction SilentlyContinue

# Check if port 8000 is available
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

### Dependencies installation failed?
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install Visual C++ Build Tools (required for some packages)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Retry installation
pip install -r requirements.txt --force-reinstall
```

### MT5 connection issues?
1. Ensure MT5 Terminal is running
2. Verify you're logged into account 308646228
3. Check MT5 allows DLL imports: Tools → Options → Expert Advisors → Check "Allow DLL imports"
4. Restart MT5 Terminal

### Telegram not responding?
```powershell
# Test Telegram API
python -c "import requests; print(requests.get('https://api.telegram.org/bot8526101969:AAF9fqQlPbNUkb1fg3vylwG4uDNiz-Z9IY4/getMe').json())"
```

## Monitoring

### Check Bot Status:
```powershell
Get-Process -Name "python" | Where-Object {$_.Path -like "*ZepixTradingBot*"}
```

### View Logs:
```powershell
Get-Content logs\trading_bot.log -Tail 50 -Wait
```

### Stop Bot:
```powershell
Stop-Process -Name "python" -Force
```

## Security Recommendations

1. **Change default passwords** after first deployment
2. **Use firewall** to restrict access to port 8000
3. **Enable Windows Defender** or antivirus
4. **Regular backups** of `data/` and `logs/` folders
5. **Monitor system resources** (CPU, RAM, Disk)
6. **Keep Python and dependencies updated**

## Production Checklist

- [ ] Python 3.12 installed
- [ ] MT5 installed and logged in (account 308646228)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file verified
- [ ] `config/config.json` verified
- [ ] Port 8000 opened
- [ ] MT5 connection tested
- [ ] Telegram bot tested
- [ ] Bot started successfully
- [ ] Auto-startup configured (optional)
- [ ] Logs monitoring enabled

## Contact & Support

For issues or updates, check the GitHub repository:
https://github.com/asggroupsinfo/ZepixTradingBot-old-v6

---
**Last Updated:** November 27, 2024
**Version:** 2.0
**Status:** Production Ready ✅
