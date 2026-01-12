# Quick Reference: Risk Commands Improvements

## 🎯 What Changed?

### 4 Commands Fixed:
1. **set_daily_cap** - Now asks for tier first, then amount
2. **set_lifetime_cap** - Now asks for tier first, then amount
3. **set_risk_tier** - Now sends success message after execution
4. **set_lot_size** - Now sends success message after execution

---

## ✨ New Features

### 1. Tier Selection
All risk commands now let you choose which tier to configure:
- ✅ Current tier is highlighted
- Shows all tiers: $5000, $10000, $25000, $50000, $100000

### 2. Smart Presets
Amount and lot size options adjust automatically based on tier:

**$5,000 Tier:**
- Daily amounts: $10, $20, $50, $100, $200, $500
- Lifetime amounts: Same range
- Lot sizes: 0.01, 0.02, 0.05, 0.1

**$10,000 Tier:**
- Daily amounts: $50, $100, $200, $400, $500, $1000
- Lifetime amounts: Same range
- Lot sizes: 0.05, 0.1, 0.15, 0.2, 0.5

**$25,000 Tier:**
- Daily amounts: $100, $200, $500, $1000, $2000, $2500
- Lifetime amounts: Same range
- Lot sizes: 0.5, 1.0, 1.5, 2.0

**$50,000 Tier:**
- Daily amounts: $200, $500, $1000, $2000, $5000
- Lifetime amounts: Same range
- Lot sizes: 1.0, 2.0, 3.0, 5.0

**$100,000 Tier:**
- Daily amounts: $500, $1000, $2000, $5000, $10000
- Lifetime amounts: Same range
- Lot sizes: 2.0, 5.0, 7.0, 10.0

### 3. Custom Value Input
Now you can enter custom values:
- Click "✏️ Custom Value" button
- Type your amount
- Automatic validation:
  - Amounts: Must be positive, max $1,000,000
  - Lot sizes: Must be between 0.01 and 10.0
  - Percentages: Must be between 5% and 50%

### 4. Success Confirmation
Every command now shows a detailed success message:
```
✅ DAILY LOSS LIMIT UPDATED

🎯 Tier: $10000
📉 Daily Limit: $400.00

✅ Configuration saved successfully!
```

---

## 📱 How to Use (Examples)

### Example 1: Set Daily Cap for $10,000 Tier
```
1. Click: Risk Menu → set_daily_cap
2. Select Tier: Click "✅ $10000 (Current)"
3. Select Amount: Click "$400"
4. Confirm: Click "✅ Confirm"
5. ✅ See success message with tier and amount
```

### Example 2: Set Lot Size with Custom Value
```
1. Click: Risk Menu → set_lot_size
2. Select Tier: Click "$10000"
3. Click: "✏️ Custom Value"
4. Type: 0.15
5. Send message
6. Confirm: Click "✅ Confirm"
7. ✅ See success message
```

### Example 3: Configure Complete Risk Tier
```
1. Click: Risk Menu → set_risk_tier
2. Select Balance: Click "$10000"
3. Select Daily Limit: Click "$400"
4. Select Lifetime Limit: Click "$2000"
5. Confirm: Click "✅ Confirm"
6. ✅ See complete success message with all 3 values
```

---

## 🔧 Technical Details

### Files Modified
- `src/menu/command_mapping.py` - Command parameter definitions
- `src/menu/menu_manager.py` - Dynamic preset generation
- `src/menu/command_executor.py` - Command execution logic
- `src/clients/telegram_bot.py` - Handler implementations

### Backward Compatibility
✅ All changes are backward compatible
✅ Existing config structure unchanged
✅ No database migrations needed

### Debug Logging
All commands now include detailed logging:
- Parameter validation
- Execution status
- Error messages

Look for logs like:
```
[EXECUTE SET_DAILY_CAP] Received params: {'tier': '10000', 'amount': '400'}
[EXECUTE SET_DAILY_CAP] Calling handler with tier=10000, amount=400
```

---

## 🐛 Troubleshooting

### Issue: "No success message appears"
**Solution:** Check logs for execution errors. Ensure config.json has `risk_tiers` section.

### Issue: "Presets don't match my tier"
**Solution:** Presets are dynamically generated based on selected tier. If tier is not recognized, fallback presets are used.

### Issue: "Custom value rejected"
**Solution:** Check validation rules:
- Amounts: Positive, max $1,000,000
- Lot sizes: 0.01 to 10.0
- Percentages: 5% to 50%

### Issue: "Current tier not highlighted"
**Solution:** Ensure `default_risk_tier` is set in config.json. If not set, no tier will be highlighted (still functional).

---

## ✅ Validation Checklist

Before deployment, verify:
- [ ] No syntax errors in modified files
- [ ] Bot restarts successfully
- [ ] Telegram commands respond
- [ ] Tier selection shows current tier
- [ ] Smart presets adjust by tier
- [ ] Custom input validates correctly
- [ ] Success messages appear with correct formatting
- [ ] Config.json updates correctly

---

## 📞 Support

If you encounter any issues:
1. Check `IMPLEMENTATION_SUMMARY.md` for detailed changes
2. Review debug logs in terminal
3. Verify config.json structure
4. Test with simple values first

---

**Version:** ZepixTradingBot v2.0  
**Last Updated:** November 27, 2025  
**Status:** ✅ Ready for Production
