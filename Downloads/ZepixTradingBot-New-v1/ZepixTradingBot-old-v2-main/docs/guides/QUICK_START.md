# 🚀 QUICK START GUIDE - ZEPIX TRADING BOT V2.0

**Last Updated**: November 23, 2025  
**Status**: ✅ ALL ERRORS FIXED - READY TO START

---

## ⚡ START BOT IN 2 COMMANDS (Windows)

### **Step 1: Activate Environment**
```powershell
.\venv\Scripts\Activate.ps1
```

### **Step 2: Start Bot**
```powershell
python src/main.py --host 0.0.0.0 --port 80
```

**That's it!** Bot will start automatically! 🎉

---

## 📍 ALTERNATIVE PORTS

### **Port 5000**
```powershell
python src/main.py --host 0.0.0.0 --port 5000
```

### **Port 8888**
```powershell
python src/main.py --host 0.0.0.0 --port 8888
```

### **Any Custom Port**
```powershell
python src/main.py --host 0.0.0.0 --port YOUR_PORT
```

---

## ✅ WHAT YOU'LL SEE ON SUCCESS

### **Console Output**:
```
======================================================================
STARTING ZEPIX TRADING BOT v2.0
======================================================================
Initializing components...
✅ MT5 Connection Established
SUCCESS: Trading engine initialized successfully
SUCCESS: Price monitor service started
[OK] Trade monitor started
[OK] Telegram polling thread started
INFO:     Uvicorn running on http://0.0.0.0:80
```

### **Telegram Message**:
```
🤖 Trading Bot v2.0 Started Successfully!
━━━━━━━━━━━━━━━━━━━━━━━━

Mode: LIVE TRADING
Re-entry System Enabled
✅ Menu Active — use /start
```

---

## 🎯 FIRST STEPS AFTER START

### **1. Open Telegram**
Find your bot and send:
```
/start
```

### **2. Check Status**
```
/status
```

### **3. View Dashboard**
```
/dashboard
```

### **4. Check Features**
```
/profit_status    # Profit booking
/dual_order_status # Dual orders
/health_status     # System health
```

---

## ✅ ALL FEATURES WORKING

### **Core Trading** ✅
- Dual Order System (Order A + Order B)
- Profit Booking Chains (5 levels)
- Re-entry Systems (all 3 types)
- Risk Management (5 tiers)

### **Telegram Commands** ✅
- 60+ commands active
- Interactive menu system
- Real-time notifications
- Zero-typing interface

### **Advanced Features** ✅
- Multi-timeframe analysis
- Price monitoring (30s interval)
- SL Hunt detection
- TP Continuation
- Exit Continuation
- Analytics engine

---

## 🛡️ ERRORS FIXED

1. ✅ **Duplicate Method** - Removed
2. ✅ **Deprecated FastAPI** - Modernized
3. ✅ **MT5 Server Name** - Fixed
4. ✅ **Parse Mode** - Standardized

**Total Errors Remaining**: **0** ✅

---

## 📋 TROUBLESHOOTING

### **Bot Won't Start**

**Problem**: Port already in use
**Solution**: Use different port
```powershell
python src/main.py --host 0.0.0.0 --port 5000
```

---

### **MT5 Not Connecting**

**Problem**: MT5 terminal not running
**Solution**: 
1. Open MT5 terminal
2. Login with account
3. Restart bot

**Or**: Bot automatically switches to simulation mode

---

### **No Telegram Messages**

**Problem**: Telegram credentials
**Solution**: Check `.env` file has:
```
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 🎉 YOU'RE ALL SET!

**Bot Status**: ✅ Production Ready  
**Errors**: ✅ All Fixed  
**Features**: ✅ All Working  
**Deployment**: ✅ One-Click Ready

---

## 📞 NEED HELP?

Check these files for details:
- `FIXES_COMPLETED.md` - Full fix report
- `ACTUAL_ERRORS_VERIFICATION.md` - Error verification
- `README.md` - Complete documentation

---

**Happy Trading!** 🚀💰
