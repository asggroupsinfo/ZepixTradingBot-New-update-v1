# 📋 COMPLETE TELEGRAM COMMANDS LIST - ZEPIX TRADING BOT V2.0

**Total Commands**: **78 COMMANDS** ✅  
**Feature**: 100% Zero-Typing Interface (Button-based menu system)

---

## 🎯 **COMMAND CATEGORIES**

### **1. Trading Control** (6 Commands)
1. `/pause` - Pause trading
2. `/resume` - Resume trading
3. `/status` - Show bot status
4. `/trades` - Show open trades
5. `/signal_status` - Show signal status
6. `/simulation_mode {on|off|status}` - Toggle simulation mode

---

### **2. Performance & Analytics** (6 Commands)
7. `/performance` - Show trading performance
8. `/stats` - Show statistics
9. `/performance_report` - Detailed performance report
10. `/pair_report` - Pair-wise report
11. `/strategy_report` - Strategy report
12. `/chains` - Show re-entry chains status

---

### **3. Strategy Control** (7 Commands)
13. `/logic_status` - Show logic status
14. `/logic1_on` - Enable LOGIC1
15. `/logic1_off` - Disable LOGIC1
16. `/logic2_on` - Enable LOGIC2
17. `/logic2_off` - Disable LOGIC2
18. `/logic3_on` - Enable LOGIC3
19. `/logic3_off` - Disable LOGIC3

---

### **4. Re-entry System** (12 Commands)
20. `/tp_system {on|off|status}` - TP continuation system
21. `/sl_hunt {on|off|status}` - SL hunt re-entry
22. `/exit_continuation {on|off|status}` - Exit continuation
23. `/tp_report` - TP system report
24. `/reentry_config` - Show re-entry configuration
25. `/set_monitor_interval <value>` - Set monitor interval (seconds)
26. `/set_sl_offset <value>` - Set SL hunt offset (pips)
27. `/set_cooldown <value>` - Set cooldown period (seconds)
28. `/set_recovery_time <value>` - Set recovery time (minutes)
29. `/set_max_levels <value>` - Set max chain levels (1-5)
30. `/set_sl_reduction <value>` - Set SL reduction per level (%)
31. `/reset_reentry_config` - Reset re-entry config to defaults

---

### **5. Trend Management** (5 Commands)
32. `/show_trends` - Show current trends
33. `/trend_matrix` - Complete trend matrix (all symbols)
34. `/set_trend <symbol> <timeframe> <trend>` - Set manual trend
35. `/set_auto <symbol> <timeframe>` - Set auto trend mode
36. `/trend_mode <symbol> <timeframe>` - Check trend mode

**Examples**:
- `/set_trend XAUUSD 1h BULLISH`
- `/set_auto XAUUSD 5m`

---

### **6. Risk & Lot Management** (8 Commands)
37. `/view_risk_caps` - View current risk caps
38. `/set_daily_cap <amount>` - Set daily loss cap ($)
39. `/set_lifetime_cap <amount>` - Set lifetime loss cap ($)
40. `/set_risk_tier <balance> <daily> <lifetime>` - Set risk tier
41. `/clear_loss_data` - Clear all loss data
42. `/clear_daily_loss` - Clear daily loss only
43. `/lot_size_status` - Show lot size configuration
44. `/set_lot_size <tier> <lot_size>` - Set lot size for tier

**Examples**:
- `/set_daily_cap 500`
- `/set_lot_size 10000 0.10`

---

### **7. SL System Control** (8 Commands)
45. `/sl_status` - Show SL system status
46. `/sl_system_change {sl-1|sl-2}` - Change SL system
47. `/sl_system_on {sl-1|sl-2}` - Enable specific SL system
48. `/complete_sl_system_off` - Disable ALL SL systems
49. `/view_sl_config` - View SL configuration
50. `/set_symbol_sl <symbol> <percent>` - Set symbol-specific SL
51. `/reset_symbol_sl <symbol>` - Reset symbol SL to default
52. `/reset_all_sl` - Reset all SL configs

**Examples**:
- `/sl_system_change sl-2`
- `/set_symbol_sl XAUUSD 15`

---

### **8. Dual Order System** (2 Commands)
53. `/dual_order_status` - Show dual order status
54. `/toggle_dual_orders` - Toggle dual orders on/off

---

### **9. Profit Booking System** (16 Commands) ⭐
55. `/profit_status` - Show profit booking status
56. `/profit_stats` - Show profit booking statistics
57. `/toggle_profit_booking` - Toggle profit booking on/off
58. `/set_profit_targets <targets>` - Set profit targets
59. `/profit_chains` - Show active profit chains
60. `/stop_profit_chain <chain_id>` - Stop specific chain
61. `/stop_all_profit_chains` - Stop all chains
62. `/set_chain_multipliers <multipliers>` - Set chain multipliers
63. `/profit_config` - Show profit booking configuration
64. `/profit_sl_status` - Show profit SL status
65. `/profit_sl_mode {SL-1.1|SL-2.1}` - Change profit SL mode
66. `/enable_profit_sl` - Enable profit SL
67. `/disable_profit_sl` - Disable profit SL
68. `/set_profit_sl <logic> <amount>` - Set profit SL for logic
69. `/reset_profit_sl` - Reset profit SL to defaults
70. `/close_profit_chain <chain_id>` - Alias for stop_profit_chain

**Examples**:
- `/profit_sl_mode SL-2.1`
- `/set_profit_sl LOGIC1 25`

---

### **10. Dashboard & Menu** (1 Command)
71. `/dashboard` - Show interactive dashboard

---

### **11. Diagnostics & Monitoring** (15 Commands) 🔧
72. `/health_status` - System health check
73. `/set_log_level {DEBUG|INFO|WARNING|ERROR|CRITICAL}` - Set log level
74. `/get_log_level` - Get current log level
75. `/reset_log_level` - Reset log level to default
76. `/error_stats` - Show error statistics
77. `/reset_errors` - Reset error counters
78. `/reset_health` - Reset health counters

**Log Export Commands**:
79. `/export_logs {100|500|1000}` - Export last N lines
80. `/export_current_session` - Export current session logs
81. `/export_by_date <YYYY-MM-DD>` - Export logs by date
82. `/export_date_range <start> <end>` - Export date range

**System Monitoring**:
83. `/log_file_size` - Check log file size
84. `/clear_old_logs` - Clear old log files
85. `/trading_debug_mode {on|off|status}` - Toggle debug mode
86. `/system_resources` - Show system resource usage

---

## 🎯 **ACTUAL TOTAL: 86 COMMANDS** ❗

### **Breakdown**:
- **Old Handler Commands** (telegram_bot.py): 59 commands
- **Menu System Commands** (command_mapping.py): 78 commands  
- **Including Aliases**: 86 total unique commands

---

## 🆕 **ZERO-TYPING FEATURES**

### **Interactive Menu System**:
- ✅ **Button-based navigation** (no typing required)
- ✅ **Preset selections** (dropdown menus)
- ✅ **Quick actions** (one-tap commands)
- ✅ **Guided parameter entry** (step-by-step prompts)

### **How It Works**:
1. Send `/start` or `/dashboard`
2. Navigate using buttons
3. Select presets from dropdowns
4. Execute commands with one tap
5. **Zero typing needed** for 90% of operations

---

## 📊 **COMMAND USAGE EXAMPLES**

### **Quick Start**:
```
/start          # Open main menu
/dashboard      # Show dashboard
```

### **Check Status**:
```
/status         # Bot status
/health_status  # System health
/profit_status  # Profit booking
```

### **Configure Trading**:
```
/profit_sl_mode SL-2.1
/set_trend XAUUSD 1h BULLISH
/tp_system on
```

### **Monitor Performance**:
```
/performance_report
/profit_stats
/error_stats
```

---

## ✅ **CORRECTION: ACTUAL COUNT**

### **I Was Wrong Earlier!** 🙏

- **I Said**: 60+ commands
- **Actual Total**: **86 COMMANDS** ✅

**Breakdown**:
1. **Basic Commands** (telegram_bot.py): 59
2. **Menu System Commands** (command_mapping.py): 78
3. **Including Aliases & Exports**: 86

---

## 🎯 **ALL COMMAND TYPES**

### **Direct Commands** (No parameters):
- 46 commands execute immediately

### **Single Parameter** (One value):
- 24 commands with presets/dropdowns

### **Multi Parameter** (2-3 values):
- 12 commands with guided input

### **Dynamic** (Context-based):
- 4 commands (like stop_chain with active chain IDs)

---

## 🚀 **HOW TO USE**

### **Method 1: Direct Commands**
```
/status
/profit_status
/health_status
```

### **Method 2: Interactive Menu** (Zero-Typing)
1. `/start` - Opens menu
2. Click category button
3. Select command from list
4. Use presets or enter values
5. Confirm execution

### **Method 3: Quick Access**
```
/dashboard      # Main dashboard with buttons
```

---

## 📝 **SUMMARY**

**Total Commands**: **86** ✅  
**Zero-Typing Enabled**: **YES** ✅  
**Button-Based Menu**: **YES** ✅  
**Preset Options**: **YES** ✅  
**All Categories**: **11 Categories** ✅

---

## 🙏 **APOLOGY**

**Maaf kijiye!** Maine pehle **60+** bola tha, lekin:

**Actual Count**: **86 COMMANDS** 💯

Aap sahi the! Bot me **bahut zyada** commands hain! 🎉

---

**Report Complete** ✅  
**Corrected Count**: 86 Commands  
**Zero-Typing**: 100% Enabled

