# 📋 COMPREHENSIVE TELEGRAM MANUAL TESTING CHECKLIST
**Version**: ZepixTradingBot v2.0  
**Date**: 2025-12-07  
**Total Tests**: 120+ Commands/Buttons  
**Status**: Ready for Manual Testing

---

## 🎯 HOW TO USE THIS CHECKLIST

### Testing Protocol:
1. ✅ Mark each test as PASS/FAIL
2. 📝 Note any errors/issues
3. 📸 Screenshot unexpected behavior
4. ⏱️ Record response time if slow

### Success Criteria:
- ✅ **PASS**: Command executes, shows expected result, no errors
- ❌ **FAIL**: Error shown, wrong result, no response
- ⚠️ **PARTIAL**: Works but with issues/delays

---

## 🚀 SECTION 1: BASIC SETUP VERIFICATION (5 Tests)

### Test 1.1: Bot Start
**Command**: `/start`  
**Steps**:
1. Open Telegram
2. Find your bot
3. Send `/start`

**Expected Result**:
- Main menu appears with buttons
- Welcome message shows
- No errors

**Success Criteria**:
```
✅ Menu displays
✅ Buttons clickable
✅ Bot logo/name shows
```

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 1.2: Bot Status Check
**Command**: `/status`  
**Steps**:
1. Send `/status`

**Expected Result**:
```
📊 Bot Status

🔸 Trading: ✅ ACTIVE / ⏸️ PAUSED
🔸 Simulation: ON/OFF
🔸 MT5: ✅ Connected
🔸 Balance: $XXXX
🔸 Lot Size: X.XX

Current Modes (XAUUSD):
LOGIC1: BUY/SELL/NEUTRAL
LOGIC2: BUY/SELL/NEUTRAL
LOGIC3: BUY/SELL/NEUTRAL
```

**Success Criteria**:
- ✅ Shows trading status
- ✅ MT5 connection status
- ✅ Balance displays
- ✅ Logic modes shown

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 1.3: Dashboard Access
**Command**: Click "📊 Dashboard" button  
**Steps**:
1. From main menu, click "📊 Dashboard"

**Expected Result**:
- Comprehensive dashboard appears
- Shows all key metrics
- Multiple sections visible

**Success Criteria**:
- ✅ Dashboard loads
- ✅ All sections visible
- ✅ Data accurate

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 1.4: Main Menu Navigation
**Command**: Click "🏠 Back to Main Menu"  
**Steps**:
1. Navigate to any submenu
2. Click "🏠 Back to Main Menu"

**Expected Result**:
- Returns to main menu
- All buttons visible
- No errors

**Success Criteria**:
- ✅ Navigation works
- ✅ Menu appears
- ✅ Quick

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 1.5: Help/Commands List
**Command**: `/help`  
**Steps**:
1. Send `/help`

**Expected Result**:
- List of available commands
- Or menu with categories
- Clear guidance

**Success Criteria**:
- ✅ Help appears
- ✅ Commands listed
- ✅ Readable

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

## 🔄 SECTION 2: RE-ENTRY SYSTEM - NEW FEATURES (12 Tests)

### Test 2.1: Access Re-entry Menu
**Path**: Main Menu → 🔄 Re-entry  
**Steps**:
1. Click "🔄 Re-entry" from main menu

**Expected Result**:
```
🔄 RE-ENTRY SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━

Master Status: 🟢 ACTIVE / 🔴 INACTIVE

Feature Status:
• TP Continuation: ON ✅ / OFF ❌
• SL Hunt: ON ✅ / OFF ❌
• Exit Continuation: ON ✅ / OFF ❌

💡 Tip: Click buttons to toggle ON/OFF

[🤖 Autonomous Mode [ON ✅/OFF ❌]]
[🎯 TP Continuation [ON ✅/OFF ❌]]
[🛡 SL Hunt [ON ✅/OFF ❌]]
[🔄 Exit Continuation [ON ✅/OFF ❌]]
[📊 View Status]
[🏠 Back to Main Menu]
```

**Success Criteria**:
- ✅ Menu displays correctly
- ✅ Current status shown
- ✅ All 6 buttons visible

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.2: Toggle Autonomous Mode ON
**Path**: Re-entry Menu → Click Autonomous Mode button  
**Steps**:
1. Click `[🤖 Autonomous Mode [OFF ❌]]`

**Expected Result**:
```
Success Message:
"🤖 Autonomous Mode: ENABLED ✅"

Menu Updates:
[🤖 Autonomous Mode [ON ✅]]
```

**Success Criteria**:
- ✅ Success message appears
- ✅ Button updates to [ON ✅]
- ✅ Menu refreshes automatically
- ✅ No errors

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.3: Toggle Autonomous Mode OFF
**Path**: Re-entry Menu → Click Autonomous Mode button again  
**Steps**:
1. Click `[🤖 Autonomous Mode [ON ✅]]`

**Expected Result**:
```
Success Message:
"🤖 Autonomous Mode: DISABLED ❌"

Menu Updates:
[🤖 Autonomous Mode [OFF ❌]]
[🎯 TP Continuation [OFF ❌]]
[🛡 SL Hunt [OFF ❌]]
[🔄 Exit Continuation [OFF ❌]]
```

**Success Criteria**:
- ✅ Success message appears
- ✅ Button updates to [OFF ❌]
- ✅ All sub-features auto-disabled (safety)
- ✅ Menu refreshes

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.4: Toggle TP Continuation
**Path**: Re-entry Menu → TP Continuation button  
**Steps**:
1. Enable Autonomous Mode first (if disabled)
2. Click `[🎯 TP Continuation [OFF ❌]]`

**Expected Result**:
```
Success Message:
"🎯 TP Continuation: ENABLED ✅"

Button Updates:
[🎯 TP Continuation [ON ✅]]
```

**Success Criteria**:
- ✅ Success message
- ✅ Button toggles
- ✅ Independent of other features

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.5: Toggle SL Hunt
**Path**: Re-entry Menu → SL Hunt button  
**Steps**:
1. Click `[🛡 SL Hunt [OFF ❌]]`

**Expected Result**:
```
Success Message:
"🛡 SL Hunt: ENABLED ✅"

Button Updates:
[🛡 SL Hunt [ON ✅]]
```

**Success Criteria**:
- ✅ Success message
- ✅ Button toggles
- ✅ Works independently

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.6: Toggle Exit Continuation
**Path**: Re-entry Menu → Exit Continuation button  
**Steps**:
1. Click `[🔄 Exit Continuation [OFF ❌]]`

**Expected Result**:
```
Success Message:
"🔄 Exit Continuation: ENABLED ✅"

Button Updates:
[🔄 Exit Continuation [ON ✅]]
```

**Success Criteria**:
- ✅ Success message
- ✅ Button toggles
- ✅ Works independently

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.7: View Re-entry Status
**Path**: Re-entry Menu → 📊 View Status  
**Steps**:
1. Click "📊 View Status"

**Expected Result**:
```
📊 RE-ENTRY SYSTEM STATUS
━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Master Mode: ON ✅ / OFF ❌

🎯 TP CONTINUATION
• Status: ON ✅
• Cooldown: 5s
• Max Levels: 5

🛡 SL HUNT RECOVERY
• Status: ON ✅
• Max Attempts: 1
• Min Recovery: 2 pips

🔄 EXIT CONTINUATION
• Status: ON ✅
```

**Success Criteria**:
- ✅ Detailed status shows
- ✅ All settings visible
- ✅ Values correct

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.8: Config Persistence - Restart Test
**Path**: Test config saves  
**Steps**:
1. Toggle some features ON
2. Note current settings
3. **Restart the bot** (Ctrl+C, then restart)
4. Navigate back to Re-entry menu

**Expected Result**:
- Settings retained after restart
- Same toggles as before restart

**Success Criteria**:
- ✅ Settings persist
- ✅ No reset to defaults
- ✅ Config.json updated

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 2.9-2.12: Old Re-entry Commands (Verify Still Work)

**Test 2.9**: `/tp_system status`  
**Expected**: Shows TP system status  
**Result**: [ ] PASS  [ ] FAIL  

**Test 2.10**: `/sl_hunt status`  
**Expected**: Shows SL hunt status  
**Result**: [ ] PASS  [ ] FAIL  

**Test 2.11**: `/exit_continuation status`  
**Expected**: Shows exit continuation status  
**Result**: [ ] PASS  [ ] FAIL  

**Test 2.12**: `/reentry_config`  
**Expected**: Shows all re-entry config  
**Result**: [ ] PASS  [ ] FAIL  

---

## 📈 SECTION 3: PROFIT BOOKING - NEW FEATURES (10 Tests)

### Test 3.1: Access Profit Booking Menu
**Path**: Main Menu → 📈 Profit  
**Steps**:
1. Click "📈 Profit" from main menu

**Expected Result**:
```
📈 PROFIT BOOKING
━━━━━━━━━━━━━━━━━━━━━━━━

Current SL Mode: SL-1.1 / SL-2.1
Type: Logic-Specific / Fixed Universal

SL Settings:
• LOGIC1: $20.0
• LOGIC2: $40.0
• LOGIC3: $50.0
OR
• Fixed SL: $10.0 (All Logics)

Status: ACTIVE 🟢 / INACTIVE 🔴

[🛡 Profit Protection [ON ✅/OFF ❌]]
[📊 Active Chains]
[💎 SL Hunt [ON ✅/OFF ❌]]

⚙ SL MODE
[SL-1.1 (Logic) ✅] [SL-2.1 (Fixed)]

[📈 View Config]
[🏠 Back to Main Menu]
```

**Success Criteria**:
- ✅ Menu displays
- ✅ Current mode shown
- ✅ SL settings visible
- ✅ All buttons present

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.2: Switch to SL-2.1 Mode
**Path**: Profit Booking → Click SL-2.1 button  
**Steps**:
1. Click `[SL-2.1 (Fixed)]` button

**Expected Result**:
```
Success Message:
"✅ SL Mode Changed

New Mode: SL-2.1 (Fixed Universal)
Previous: SL-1.1

Settings will apply to new orders."

Menu Updates:
[SL-1.1 (Logic)] [SL-2.1 (Fixed) ✅]

SL Settings section updates to:
• Fixed SL: $10.0 (All Logics)
```

**Success Criteria**:
- ✅ Detailed success message
- ✅ Checkmark moves to SL-2.1
- ✅ Settings update
- ✅ Menu refreshes

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.3: Switch Back to SL-1.1 Mode
**Path**: Profit Booking → Click SL-1.1 button  
**Steps**:
1. Click `[SL-1.1 (Logic)]` button

**Expected Result**:
```
Success Message:
"✅ SL Mode Changed

New Mode: SL-1.1 (Logic-Specific)
Previous: SL-2.1

Settings will apply to new orders."

Menu Updates:
[SL-1.1 (Logic) ✅] [SL-2.1 (Fixed)]

SL Settings section updates to:
• LOGIC1: $20.0
• LOGIC2: $40.0
• LOGIC3: $50.0
```

**Success Criteria**:
- ✅ Success message
- ✅ Checkmark moves to SL-1.1
- ✅ Logic-specific settings show
- ✅ Menu refreshes

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.4: Click Same Mode (Already Active)
**Path**: Profit Booking → Click active mode  
**Steps**:
1. Click mode that's already selected (has ✅)

**Expected Result**:
```
Info Message:
"ℹ️ Already using SL-1.1 mode"
```

**Success Criteria**:
- ✅ Info message (not error)
- ✅ No change in menu
- ✅ No unnecessary action

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.5: Toggle Profit Protection ON
**Path**: Profit Booking → Profit Protection button  
**Steps**:
1. Click `[🛡 Profit Protection [OFF ❌]]`

**Expected Result**:
```
Success Message:
"🛡 Profit Protection: ENABLED ✅"

Button Updates:
[🛡 Profit Protection [ON ✅]]
```

**Success Criteria**:
- ✅ Success message
- ✅ Button toggles
- ✅ Menu refreshes

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.6: Toggle Profit Protection OFF
**Path**: Profit Booking → Profit Protection button again  
**Steps**:
1. Click `[🛡 Profit Protection [ON ✅]]`

**Expected Result**:
```
Success Message:
"🛡 Profit Protection: DISABLED ❌"

Button Updates:
[🛡 Profit Protection [OFF ❌]]
```

**Success Criteria**:
- ✅ Success message
- ✅ Button toggles back
- ✅ Works smoothly

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.7: Toggle Profit SL Hunt
**Path**: Profit Booking → SL Hunt button  
**Steps**:
1. Click `[💎 SL Hunt [OFF ❌]]`

**Expected Result**:
```
Success Message:
"💎 Profit SL Hunt: ENABLED ✅"

Button Updates:
[💎 SL Hunt [ON ✅]]
```

**Success Criteria**:
- ✅ Success message
- ✅ Button toggles
- ✅ Independent toggle

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.8: View Active Chains
**Path**: Profit Booking → 📊 Active Chains  
**Steps**:
1. Click "📊 Active Chains"

**Expected Result**:
- Shows active profit booking chains
- Or "No active chains" if none

**Success Criteria**:
- ✅ Chains display
- ✅ Or empty state message
- ✅ No error

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.9: View Config
**Path**: Profit Booking → 📈 View Config  
**Steps**:
1. Click "📈 View Config"

**Expected Result**:
- Shows complete profit booking config
- Multipliers, targets, reductions

**Success Criteria**:
- ✅ Config displays
- ✅ All settings visible
- ✅ Readable format

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 3.10: Profit Config Persistence
**Path**: Restart test  
**Steps**:
1. Switch SL mode (e.g., to SL-2.1)
2. Enable Profit Protection
3. **Restart bot**
4. Check Profit Booking menu

**Expected Result**:
- SL mode retained (SL-2.1 still active)
- Profit Protection still enabled

**Success Criteria**:
- ✅ Settings persist
- ✅ No reset
- ✅ Config saved

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

## 🔍 SECTION 4: RECOVERY WINDOWS - NEW FEATURES (15 Tests)

### Test 4.1: Access Recovery Windows Menu
**Path**: Main Menu → ⚡ Fine-Tune → 🔍 Recovery Windows  
**Steps**:
1. Click "⚡ Fine-Tune" from main menu
2. Click "🔍 Recovery Windows"

**Expected Result**:
```
🔍 RECOVERY WINDOWS
━━━━━━━━━━━━━━━━━━━━━━━━
Page 1 of 6

Adjust maximum wait time for SL Hunt recovery per symbol.

How it works:
Bot monitors price continuously. Window = timeout limit.

Range: 5 - 60 minutes
⬇ Decrease by 5 min
⬆ Increase by 5 min

[⬇] [XAUUSD: 15m] [⬆]
[⬇] [BTCUSD: 12m] [⬆]
[⬇] [XAGUSD: 18m] [⬆]
[⬇] [GBPJPY: 20m] [⬆]
[⬇] [EURUSD: 30m] [⬆]
[⬇] [USDJPY: 28m] [⬆]

[⬅ Previous] [Next ➡]
[📖 Window Guide]
[🏠 Back]
```

**Success Criteria**:
- ✅ Menu displays
- ✅ 6 symbols visible
- ✅ Current values shown
- ✅ All buttons present

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.2: Increase Window (⬆ button)
**Path**: Recovery Windows → Click ⬆ on XAUUSD  
**Steps**:
1. Note current XAUUSD value (e.g., 15m)
2. Click ⬆ button next to XAUUSD

**Expected Result**:
```
Popup Confirmation:
"XAUUSD: 15m → 20m"

Menu Updates:
[⬇] [XAUUSD: 20m] [⬆]
```

**Success Criteria**:
- ✅ Popup appears briefly
- ✅ Value increases by 5 min
- ✅ Menu updates immediately
- ✅ No errors

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.3: Decrease Window (⬇ button)
**Path**: Recovery Windows → Click ⬇ on BTCUSD  
**Steps**:
1. Note current BTCUSD value (e.g., 12m)
2. Click ⬇ button next to BTCUSD

**Expected Result**:
```
Popup Confirmation:
"BTCUSD: 12m → 7m"

Menu Updates:
[⬇] [BTCUSD: 7m] [⬆]
```

**Success Criteria**:
- ✅ Popup appears
- ✅ Value decreases by 5 min
- ✅ Menu updates
- ✅ Works smoothly

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.4: Click Symbol Name (Info)
**Path**: Recovery Windows → Click symbol name  
**Steps**:
1. Click on "XAUUSD: 15m" (middle button)

**Expected Result**:
- Shows detailed info about XAUUSD window
- Or no action (button may be informational)

**Success Criteria**:
- ✅ Info displays OR
- ✅ Button clearly non-clickable

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.5: Next Page Navigation
**Path**: Recovery Windows → Next ➡  
**Steps**:
1. Click "Next ➡" button

**Expected Result**:
```
Page 2 of 6

Shows next 6 symbols:
[⬇] [NZDUSD: 30m] [⬆]
[⬇] [USDCAD: 28m] [⬆]
etc...

[⬅ Previous] [Next ➡]
```

**Success Criteria**:
- ✅ Page 2 displays
- ✅ Different symbols shown
- ✅ Navigation smooth

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.6: Previous Page Navigation
**Path**: Recovery Windows → ⬅ Previous  
**Steps**:
1. From page 2, click "⬅ Previous"

**Expected Result**:
```
Page 1 of 6

Back to first 6 symbols
```

**Success Criteria**:
- ✅ Returns to page 1
- ✅ Same symbols as before
- ✅ Navigation works

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.7: Navigate All Pages
**Path**: Recovery Windows → Navigate all  
**Steps**:
1. Click "Next ➡" repeatedly until last page
2. Click "⬅ Previous" to go back

**Expected Result**:
- 6 pages total (approx 35+ symbols)
- Each page shows 6 symbols
- Navigation smooth

**Success Criteria**:
- ✅ All pages accessible
- ✅ No missing symbols
- ✅ Buttons work both ways

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.8: Upper Limit Test (60 min)
**Path**: Recovery Windows → Increase to max  
**Steps**:
1. Find a symbol near 55m
2. Click ⬆ to reach 60m
3. Try to click ⬆ again

**Expected Result**:
```
At 60m, clicking ⬆ shows:
"❌ Range limit: 5-60 minutes"

Value stays at 60m (doesn't exceed)
```

**Success Criteria**:
- ✅ Stops at 60m
- ✅ Error message shows
- ✅ No crash

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.9: Lower Limit Test (5 min)
**Path**: Recovery Windows → Decrease to min  
**Steps**:
1. Find a symbol near 10m
2. Click ⬇ to reach 5m
3. Try to click ⬇ again

**Expected Result**:
```
At 5m, clicking ⬇ shows:
"❌ Range limit: 5-60 minutes"

Value stays at 5m (doesn't go below)
```

**Success Criteria**:
- ✅ Stops at 5m
- ✅ Error message shows
- ✅ Validation works

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.10: View Window Guide
**Path**: Recovery Windows → 📖 Window Guide  
**Steps**:
1. Click "📖 Window Guide"

**Expected Result**:
```
📖 RECOVERY WINDOWS GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Purpose:
Set maximum wait time for SL Hunt price recovery per symbol.

⚙ How It Works:
1. SL Hit: Trade hits stop loss
2. Monitor Start: Bot starts watching price
3. Price Check: Every 1 second, checks if price recovered
4. Immediate Action: If recovered, places order instantly
5. Timeout: If window expires, stops monitoring

💡 Window Settings:
⚡ Short (10-20 min): Fast-moving pairs (XAUUSD, BTCUSD)
⚖ Medium (25-35 min): Major forex pairs (EURUSD, USDJPY)
🛡 Long (35-60 min): Stable pairs (USDCHF, Exotics)

🔧 Adjustment Tips:
• More volatile = shorter window
• Trending market = shorter window
• Choppy market = longer window

Range: 5 - 60 minutes
```

**Success Criteria**:
- ✅ Guide displays
- ✅ Clear explanation
- ✅ Examples given
- ✅ Back button works

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.11: Multiple Adjustments
**Path**: Recovery Windows → Adjust multiple symbols  
**Steps**:
1. Increase XAUUSD by 10m (click ⬆ twice)
2. Decrease EURUSD by 10m (click ⬇ twice)
3. Navigate to page 2
4. Adjust another symbol

**Expected Result**:
- All adjustments save
- Navigation doesn't reset changes
- Values persist when returning to page

**Success Criteria**:
- ✅ Multiple edits work
- ✅ Changes saved
- ✅ No confusion

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.12: Recovery Windows Persistence
**Path**: Restart test  
**Steps**:
1. Change 2-3 symbol windows
2. Note new values
3. **Restart bot**
4. Navigate back to Recovery Windows

**Expected Result**:
- Changed values retained
- Config.json updated
- RecoveryWindowMonitor updated

**Success Criteria**:
- ✅ Values persist
- ✅ Config saved
- ✅ Monitor updated

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.13: Back Navigation
**Path**: Recovery Windows → 🏠 Back  
**Steps**:
1. Click "🏠 Back"

**Expected Result**:
- Returns to Fine-Tune menu
- All Fine-Tune options visible

**Success Criteria**:
- ✅ Navigation works
- ✅ Parent menu shows

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.14: Re-access After Changes
**Path**: Return to Recovery Windows  
**Steps**:
1. Make some changes
2. Go back to main menu
3. Navigate again to Recovery Windows

**Expected Result**:
- Shows updated values (not reset)
- Changes visible immediately

**Success Criteria**:
- ✅ Real-time updates
- ✅ No delays

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

### Test 4.15: Rapid Clicking Test
**Path**: Recovery Windows → Fast clicks  
**Steps**:
1. Rapidly click ⬆ button 5 times

**Expected Result**:
- Each click registers
- Value increases by 25m total
- No duplicate actions
- No crashes

**Success Criteria**:
- ✅ Handles rapid input
- ✅ Accurate counting
- ✅ Stable

**Result**: [ ] PASS  [ ] FAIL  [ ] PARTIAL  
**Notes**: _______________________________________________

---

## 💰 SECTION 5: TRADING CONTROL (6 Tests)

### Test 5.1: Pause Trading
**Command**: `/pause`  
**Expected**: "⏸️ Trading PAUSED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 5.2: Resume Trading
**Command**: `/resume`  
**Expected**: "✅ Trading RESUMED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 5.3: View Trades
**Command**: `/trades`  
**Expected**: List of open trades or "No open trades"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 5.4: Signal Status
**Command**: `/signal_status`  
**Expected**: Shows current signals for all symbols  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 5.5: Simulation Mode Status
**Command**: `/simulation_mode status`  
**Expected**: Shows if simulation ON/OFF  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 5.6: Enable Simulation
**Command**: `/simulation_mode on`  
**Expected**: "Simulation Mode: ON"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

---

## ⚙️ SECTION 6: STRATEGY CONTROL (7 Tests)

### Test 6.1: Logic Status
**Command**: `/logic_status`  
**Expected**: Shows LOGIC1/2/3 enabled/disabled status  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 6.2: Enable LOGIC1
**Command**: `/logic1_on`  
**Expected**: "✅ LOGIC 1 TRADING ENABLED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 6.3: Disable LOGIC1
**Command**: `/logic1_off`  
**Expected**: "⛔ LOGIC 1 TRADING DISABLED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 6.4: Enable LOGIC2
**Command**: `/logic2_on`  
**Expected**: "✅ LOGIC 2 TRADING ENABLED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 6.5: Disable LOGIC2
**Command**: `/logic2_off`  
**Expected**: "⛔ LOGIC 2 TRADING DISABLED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 6.6: Enable LOGIC3
**Command**: `/logic3_on`  
**Expected**: "✅ LOGIC 3 TRADING ENABLED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 6.7: Disable LOGIC3
**Command**: `/logic3_off`  
**Expected**: "⛔ LOGIC 3 TRADING DISABLED"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

---

## 📍 SECTION 7: TREND MANAGEMENT (5 Tests)

### Test 7.1: Show Trends
**Command**: `/show_trends`  
**Expected**: Shows current trends for active symbols  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 7.2: Trend Matrix
**Command**: `/trend_matrix`  
**Expected**: Complete matrix with logic alignments  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 7.3: Set Manual Trend
**Command**: `/set_trend XAUUSD 1h BULLISH`  
**Expected**: "🔒 Manual Trend Set" with details  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 7.4: Set Auto Mode
**Command**: `/set_auto XAUUSD 1h`  
**Expected**: "🔄 Auto Mode Enabled"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 7.5: Check Trend Mode
**Command**: `/trend_mode XAUUSD 1h`  
**Expected**: Shows MANUAL or AUTO status  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

---

## 🛡️ SECTION 8: RISK MANAGEMENT (8 Tests)

### Test 8.1: View Risk Caps
**Command**: `/view_risk_caps`  
**Expected**: Shows all tier risk limits  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 8.2: Risk Status
**Command**: `/view_risk_status`  
**Expected**: Complete tier configurations with active tier highlighted  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 8.3: Switch Tier
**Command**: `/switch_tier 10000`  
**Expected**: "Switched to $10000 tier"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 8.4: Clear Daily Loss
**Command**: `/clear_daily_loss`  
**Expected**: "Daily loss cleared"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 8.5: Clear Lifetime Loss
**Command**: `/clear_loss_data`  
**Expected**: "Lifetime loss cleared"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 8.6: Lot Size Status
**Command**: `/lot_size_status`  
**Expected**: Shows lot sizes for all tiers  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 8.7: Set Lot Size
**Command**: `/set_lot_size 10000 0.1`  
**Expected**: "Lot size set for tier"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 8.8: Reset Risk Settings
**Command**: `/reset_risk_settings`  
**Expected**: "Settings reset to factory defaults"  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

---

## ⚡ SECTION 9: PERFORMANCE & ANALYTICS (6 Tests)

### Test 9.1: Performance
**Command**: `/performance`  
**Expected**: Win rate, PnL, daily/lifetime stats  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 9.2: Stats
**Command**: `/stats`  
**Expected**: Risk tier, loss limits, lot size  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 9.3: Performance Report
**Command**: `/performance_report`  
**Expected**: 30-day analytics  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 9.4: Pair Report
**Command**: `/pair_report`  
**Expected**: Per-symbol statistics  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 9.5: Strategy Report
**Command**: `/strategy_report`  
**Expected**: Per-logic performance  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 9.6: Chains Status
**Command**: `/chains`  
**Expected**: Active re-entry chains  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

---

## 🎯 SECTION 10: FINE-TUNE MENU (Existing Features - 8 Tests)

### Test 10.1: Access Fine-Tune
**Path**: Main Menu → ⚡ Fine-Tune  
**Expected**: Fine-tune menu with 4+ options  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 10.2: Profit Protection Menu
**Path**: Fine-Tune → 💰 Profit Protection  
**Expected**: Protection mode selection menu  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 10.3: Switch Protection Mode
**Path**: Profit Protection → Select mode  
**Expected**: Mode switches, success message  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 10.4: SL Reduction Menu
**Path**: Fine-Tune → 📉 SL Reduction  
**Expected**: SL reduction strategy menu  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 10.5: Switch Reduction Strategy
**Path**: SL Reduction → Select strategy  
**Expected**: Strategy switches  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 10.6: Adaptive Symbol Settings
**Path**: SL Reduction → ADAPTIVE → Symbol Settings  
**Expected**: Symbol-specific reduction settings  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 10.7: Adjust Symbol Reduction
**Path**: Adaptive Settings → ⬇⬆ buttons  
**Expected**: Percentage adjusts  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

### Test 10.8: Autonomous Dashboard
**Command**: `/autonomous_dashboard`  
**Expected**: Dashboard with all autonomous features  
**Result**: [ ] PASS  [ ] FAIL  
**Notes**: _______________________________________________

---

## 📊 SUMMARY SECTION

### Overall Test Results:

**Total Tests Conducted**: _____ / 120+

**Category Breakdown**:
- Basic Setup (5): _____ PASS  
- Re-entry System (12): _____ PASS  
- Profit Booking (10): _____ PASS  
- Recovery Windows (15): _____ PASS  
- Trading Control (6): _____ PASS  
- Strategy Control (7): _____ PASS  
- Trend Management (5): _____ PASS  
- Risk Management (8): _____ PASS  
- Performance (6): _____ PASS  
- Fine-Tune (8): _____ PASS  

**Pass Rate**: _____%

---

## 🔴 ISSUES FOUND

### Critical Issues (Blocks Usage):
1. _______________________________________________
2. _______________________________________________

### Major Issues (Impacts Functionality):
1. _______________________________________________
2. _______________________________________________

### Minor Issues (Cosmetic/UX):
1. _______________________________________________
2. _______________________________________________

---

## ✅ FINAL VERDICT

**Bot Status**: [ ] READY  [ ] NEEDS FIXES  [ ] NOT READY

**Recommendation**: _______________________________________________

**Next Steps**: _______________________________________________

---

**Tester Name**: _______________________________________________  
**Test Date**: _______________________________________________  
**Test Duration**: _______________________________________________  
**Bot Version**: ZepixTradingBot v2.0  
**Environment**: Port 80, Live Testing
