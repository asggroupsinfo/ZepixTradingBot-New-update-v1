# LIVE DEPLOYMENT VERIFICATION GUIDE

## ✅ CODE VERIFICATION COMPLETE

All code checks passed:
- ✅ All 6 commands registered in command_handlers
- ✅ /start shows "TOTAL COMMANDS: 72"
- ✅ All 6 new commands listed in /start message
- ✅ All handlers implemented with proper error handling
- ✅ Dependencies set correctly in set_dependencies()

## 🚀 DEPLOYMENT STEPS

### Step 1: Start the Bot
```powershell
cd "C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-old-v2-main\ZepixTradingBot-old-v2-main"
python src/main.py --host 0.0.0.0 --port 80
```

### Step 2: Wait for Initialization
Wait for message: "Trading Bot v2.0 Started Successfully!"

### Step 3: Test in Telegram

#### Test 1: /start Command
Send: `/start`
**Expected:**
- Shows "TOTAL COMMANDS: 72"
- Shows "PROFIT BOOKING SYSTEM (16 commands)"
- Lists all 6 new commands:
  - /profit_sl_status
  - /profit_sl_mode SL-1.1/SL-2.1
  - /enable_profit_sl
  - /disable_profit_sl
  - /set_profit_sl LOGIC AMOUNT
  - /reset_profit_sl

#### Test 2: /profit_sl_status
Send: `/profit_sl_status`
**Expected:**
- Shows current mode (SL-1.1 or SL-2.1)
- Shows enabled/disabled status
- Shows current SL settings

#### Test 3: /profit_sl_mode
Send: `/profit_sl_mode SL-2.1`
**Expected:**
- Message: "✅ Profit Booking SL Mode Changed"
- Mode switches to SL-2.1

Send: `/profit_sl_mode SL-1.1`
**Expected:**
- Mode switches back to SL-1.1

#### Test 4: /enable_profit_sl
Send: `/enable_profit_sl`
**Expected:**
- Message: "✅ Profit Booking SL Enabled"

#### Test 5: /disable_profit_sl
Send: `/disable_profit_sl`
**Expected:**
- Message: "✅ Profit Booking SL Disabled"

#### Test 6: /set_profit_sl
Send: `/set_profit_sl LOGIC1 25`
**Expected:**
- Message: "✅ Profit Booking SL Updated (SL-1.1)"
- Shows: "LOGIC1: $20.00 → $25.00"

#### Test 7: /reset_profit_sl
Send: `/reset_profit_sl`
**Expected:**
- Message: "✅ Profit Booking SL Reset"
- All settings restored to defaults

## 🔍 TROUBLESHOOTING

### If commands don't respond:
1. Check bot logs for errors
2. Verify bot is running: Check for "Bot Started" message
3. Check dependencies: Bot needs trading_engine initialized

### If /start doesn't show 72 commands:
- Bot might be using cached code
- Restart bot to reload changes

### If commands show "not available" error:
- Bot may still be initializing
- Wait 10-15 seconds and try again
- Check that set_dependencies() was called

## ✅ VERIFICATION CHECKLIST

- [ ] Bot starts without errors
- [ ] /start shows 72 commands
- [ ] /start shows all 6 new Profit SL commands
- [ ] /profit_sl_status responds correctly
- [ ] /profit_sl_mode switches modes
- [ ] /enable_profit_sl enables system
- [ ] /disable_profit_sl disables system
- [ ] /set_profit_sl updates custom SL
- [ ] /reset_profit_sl resets to defaults
- [ ] Configuration persists after bot restart

## 📝 NOTES

- All commands require bot to be fully initialized
- Dependencies are set in main.py line 92
- Calculator is initialized in ProfitBookingManager
- All handlers check for dependencies before executing

