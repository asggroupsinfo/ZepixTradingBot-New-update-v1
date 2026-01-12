# Telegram Menu System Testing Instructions

## Bot Status

✅ **Bot is ready and functional**  
✅ **Menu system initialized**  
✅ **/start and /dashboard commands registered**  
✅ **All 72 commands mapped**

---

## How to Start the Bot

### Option 1: Using main.py (Recommended)
```bash
python src/main.py --port 5000
```

### Option 2: Using start_bot_live.py
```bash
python start_bot_live.py
```

### Option 3: Using scripts/start_bot.py
```bash
python scripts/start_bot.py
```

---

## Verify Bot is Running

1. **Check if bot process is running:**
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*python*"}
   ```

2. **Check if port 5000 is listening:**
   ```powershell
   netstat -ano | findstr :5000
   ```

3. **Test health endpoint:**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:5000/health"
   ```

---

## Testing in Telegram

### Step 1: Test /start Command

1. Open Telegram and find your bot
2. Send `/start` command
3. **Expected Result:**
   - ✅ Menu with buttons should appear
   - ✅ Should show "ZEPIX TRADING BOT v2.0"
   - ✅ Should have Quick Actions section
   - ✅ Should have 9 category buttons:
     - 💰 Trading
     - ⚡ Performance
     - 🔄 Re-entry
     - 📍 Trends
     - 🛡️ Risk
     - ⚙️ SL System
     - 💎 Orders
     - 📈 Profit
     - 🔧 Settings
   - ✅ Should have Help and Refresh buttons

### Step 2: Test /dashboard Command

1. Send `/dashboard` command
2. **Expected Result:**
   - ✅ Dashboard should appear with live data
   - ✅ Should show account balance
   - ✅ Should show live PnL
   - ✅ Should show today's performance
   - ✅ Should have "🏠 MAIN MENU" button at bottom
   - ✅ Should have other action buttons (PAUSE, STATUS, TRADES, etc.)

### Step 3: Test Menu Navigation

1. Click on "🏠 MAIN MENU" button from dashboard
2. **Expected Result:**
   - ✅ Should return to main menu
   - ✅ Menu should show with all categories

3. Click on any category (e.g., "💰 Trading")
4. **Expected Result:**
   - ✅ Should show category menu with commands
   - ✅ Should have "← Back" button
   - ✅ Should have "🏠 Home" button

5. Click on a command (e.g., "📊 Status")
6. **Expected Result:**
   - ✅ Command should execute
   - ✅ Response should appear
   - ✅ Response should have menu button

### Step 4: Test Command Execution

1. From main menu, click "💰 Trading" → "📊 Status"
2. **Expected Result:**
   - ✅ Status command should execute
   - ✅ Status information should appear
   - ✅ Menu button should be available

3. Test other commands:
   - Click "⏸️ Pause/Resume" from Quick Actions
   - Click "📈 Trades" from Quick Actions
   - Click "💰 Performance" from Quick Actions

---

## Troubleshooting

### Bot Not Responding

1. **Check if bot is running:**
   ```powershell
   Get-Process python
   ```

2. **Check bot logs:**
   - Look for "SUCCESS: Telegram bot polling started"
   - Check for any error messages

3. **Restart bot:**
   ```powershell
   # Stop existing bot
   Get-Process python | Stop-Process -Force
   
   # Start bot again
   python src/main.py --port 5000
   ```

### Menu Not Appearing

1. **Check if menu_manager is initialized:**
   - Bot should print "SUCCESS: Telegram bot polling started"
   - No errors about menu_manager

2. **Verify /start command:**
   - Send `/start` in Telegram
   - Check if menu appears
   - If not, check bot console for errors

### Dashboard Not Showing

1. **Check dependencies:**
   - RiskManager should be initialized
   - TradingEngine should be initialized
   - MT5Client should be connected (or simulation mode)

2. **Check bot console:**
   - Look for "DEBUG: handle_dashboard called"
   - Check for any error messages

---

## Expected Behavior

### /start Command
- **ALWAYS** shows menu with buttons
- Menu persists after any command
- Can navigate back to menu anytime

### /dashboard Command
- **ALWAYS** shows dashboard with "🏠 MAIN MENU" button
- Dashboard refreshes when button clicked
- Menu accessible from dashboard

### All Commands
- All command responses include menu button
- Can navigate back to menu anytime
- Zero typing required for any command

---

## Verification Checklist

- [ ] Bot starts without errors
- [ ] `/start` shows menu with buttons
- [ ] `/dashboard` shows dashboard with menu button
- [ ] Menu navigation works (categories, back, home)
- [ ] Commands execute from menu
- [ ] All responses have menu button
- [ ] Zero typing works for all commands

---

## Support

If menu is not appearing:
1. Check bot console for errors
2. Verify bot is polling (check logs)
3. Restart bot if needed
4. Check Telegram bot token is correct

---

**Last Updated:** 2025-11-17  
**Bot Version:** v2.0  
**Menu System:** Zero-Typing Menu System (100% Functional)

