# Troubleshooting Guide

**Version:** 1.0
**Date:** 2026-01-12
**Type:** Troubleshooting

---

## Common Issues

This guide covers common issues and their solutions.

## Bot Not Responding to Alerts

**Symptoms:**
- TradingView alerts sent but no trades executed
- No notifications received

**Solutions:**

1. **Check Plugin Status**
```
/status
```
Ensure the plugin is enabled.

2. **Check Daily Loss Limit**
```
/daily_limit combined_v3
```
If limit reached, plugin stops trading until next day.

3. **Check MT5 Connection**
```
/health
```
Verify MT5 connection is active.

4. **Check Logs**
```bash
tail -f logs/bot.log
```
Look for error messages.

5. **Verify Alert Format**
Ensure TradingView alert matches expected format.

## Wrong Lot Size Calculated

**Symptoms:**
- Lot size too large or too small
- Risk percentage not matching config

**Solutions:**

1. **Check Configuration**
```json
{
    "plugins": {
        "combined_v3": {
            "settings": {
                "risk_percentage": 1.5,
                "max_lot_size": 1.0
            }
        }
    }
}
```

2. **Verify Account Balance**
Lot size is calculated based on account balance. Check MT5 account.

3. **Check Symbol Settings**
Different symbols have different pip values and lot sizes.

4. **Reload Configuration**
```
/config_reload combined_v3
```

## Not Receiving Telegram Notifications

**Symptoms:**
- No messages from any bot
- Some bots working, others not

**Solutions:**

1. **Verify Bot Tokens**
Check `config/config.json` for correct tokens.

2. **Check Chat ID**
Ensure you're in the correct chat/group.

3. **Test Bot Connection**
```
/status
```
Should respond immediately.

4. **Check Rate Limits**
Telegram has rate limits. Wait a few minutes and try again.

5. **Restart Bots**
```bash
python main.py --restart-telegram
```

## MT5 Connection Issues

**Symptoms:**
- "MT5 not connected" error
- Orders failing to execute

**Solutions:**

1. **Check MT5 Terminal**
Ensure MT5 is running and logged in.

2. **Verify Credentials**
```json
{
    "mt5": {
        "login": 12345678,
        "password": "correct_password",
        "server": "XMGlobal-MT5"
    }
}
```

3. **Check Server**
Ensure correct server name (case-sensitive).

4. **Restart MT5**
Close and reopen MT5 terminal.

5. **Check Network**
Verify internet connection is stable.

## Database Errors

**Symptoms:**
- "Database locked" error
- "Table not found" error

**Solutions:**

1. **Database Locked**
```bash
# Stop the bot
# Wait 30 seconds
python main.py
```

2. **Table Not Found**
```bash
python scripts/init_database.py
```

3. **Corrupted Database**
```bash
python scripts/restore_database.py backups/latest.db
```

4. **Check Disk Space**
Ensure sufficient disk space available.

## Plugin Errors

**Symptoms:**
- Plugin fails to load
- Plugin crashes during operation

**Solutions:**

1. **Check Plugin Logs**
```bash
tail -f logs/plugins/combined_v3.log
```

2. **Verify Plugin Config**
Ensure `config.json` is valid JSON.

3. **Check Dependencies**
```bash
pip install -r requirements.txt
```

4. **Disable and Re-enable**
```
/disable_plugin combined_v3
/enable_plugin combined_v3
```

5. **Check Plugin Version**
Ensure plugin is compatible with current bot version.

## Getting Help

**How to Report Issues:**

1. **Collect Information**
   - Screenshot of error
   - Recent logs: `tail -n 100 logs/bot.log > issue_log.txt`
   - Configuration (remove sensitive data)

2. **Check Documentation**
   - User Guide
   - Admin Guide
   - This Troubleshooting Guide

3. **Contact Support**
   - Critical Issues: [Emergency Contact]
   - General Support: [Support Channel]

**When Reporting:**
- Describe what you expected to happen
- Describe what actually happened
- Include steps to reproduce
- Attach logs and screenshots
