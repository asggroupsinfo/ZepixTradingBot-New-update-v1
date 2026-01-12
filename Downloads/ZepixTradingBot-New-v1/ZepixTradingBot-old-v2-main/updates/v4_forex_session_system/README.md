# V4 Forex Session Enhancement System 🚀

**Version:** 1.0  
**Status:** 📝 Planning Complete | 🔧 Ready for Implementation  
**Target Bot:** Zepix Trading Bot v2.0 (Forex Edition)

---

## 🎯 What's This Update?

This update package adds **4 critical real-time features** to transform the Zepix Trading Bot into a Forex-optimized system:

### ✨ Feature 1: Real-Time IST Clock
- **What:** Live clock showing current Asia/Kolkata time
- **Where:** Pinned message in Telegram (fixed position)
- **Update Frequency:** Every second
- **Format:** `HH:MM:SS IST`

### 📅 Feature 2: Real-Time Calendar
- **What:** Date and day display
- **Where:** Combined with clock in same message
- **Update Frequency:** Auto-refresh at midnight
- **Format:** `DD MMM YYYY (Day)` → `11 Jan 2026 (Saturday)`

### 🕐 Feature 3: Forex Session Manager
- **What:** Dynamic session-based trading control
- **Sessions:** Asian, London, Overlap, NY Late, Dead Zone
- **Control:** Zero-typing Telegram UI with inline buttons
- **Features:**
  - ✅ Master switch (global ON/OFF)
  - ✅ Per-session symbol filtering
  - ✅ 30-minute advance alerts
  - ✅ Optional force-close at session end
  - ✅ Dynamic time adjustment (±30 min increments)

### 🔊 Feat 4: Voice Alert System
- **What:** Multi-channel notification delivery
- **Channels:** Telegram Voice → Text → SMS (fallback)
- **Priority Levels:** CRITICAL, HIGH, MEDIUM, LOW
- **Retry:** 3 attempts with exponential backoff (10s, 30s, 60s)
- **Works Even When:** Phone is locked or turned off!

---

## 📂 Package Contents

```
v4_forex_session_system/
├── 00_PROJECT_BRIEF.md          # 40-page feature specification
├── 01_IMPLEMENTATION_PLAN.md     # 60-page detailed code plan
├── README.md                     # This file
└── (code files will be added during implementation)
```

**External Files Created:**
- `data/session_settings.json` - Default Forex session configuration

---

## 🏗️ Implementation Phases

### ✅ Phase 1: Documentation & Setup (COMPLETE)
- [x] Project Brief
- [x] Implementation Plan
- [x] Session Settings JSON schema
- [x] Task checklist (80+ sub-tasks)

### 🔄 Phase 2: Fixed Clock System (Next)
**ETA:** 1 day  
**Files:** `src/modules/fixed_clock_system.py`  
**What:** IST timezone support, pinned message updates, async loop

### ⏸️ Phase 3: Session Manager
**ETA:** 2 days  
**Files:** `src/modules/session_manager.py`  
**What:** JSON config management, symbol filtering, session detection

### ⏸️ Phase 4: Voice Alert System
**ETA:** 2 days  
**Files:** `src/modules/voice_alert_system.py`  
**What:** TTS generation, multi-channel delivery, retry logic

### ⏸️ Phase 5: Telegram UI
**ETA:** 2 days  
**Files:** `src/telegram/session_menu_handler.py`  
**What:** Zero-typing menu, dynamic buttons, callback handlers

### ⏸️ Phase 6: Main Bot Integration
**ETA:** 1.5 days  
**Files:** Updates to `main.py`, `trading_engine.py`  
**What:** Connect all systems, session-based trade filtering

### ⏸️ Phase 7: Testing
**ETA:** 1 day  
**What:** Unit, integration, E2E tests + 24-hour stress test

### ⏸️ Phase 8: Documentation
**ETA:** 1 day  
**What:** User guides, troubleshooting, deployment checklist

**Total Estimated Timeline:** ~10 days

---

## 🔧 Technical Stack

### New Dependencies
```txt
python-telegram-bot>=20.0    # Existing (Telegram API)
pytz>=2023.3                 # NEW (Timezone handling)
gTTS>=2.3.0                  # NEW (Text-to-Speech)
asyncio                      # Built-in (Async runtime)
datetime                     # Built-in (Time utilities)
json                         # Built-in (Config parsing)
```

### Optional Dependencies
```txt
twilio                       # For SMS fallback (optional)
```

### Environment Variables (New)
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional (for SMS failover)
SMS_GATEWAY_API_KEY=your_sms_api_key
SMS_FROM_NUMBER=+1234567890
```

---

## 📊 Session Configuration

All session settings are stored in `data/session_settings.json`:

### Default Forex Sessions (IST)

| Session | Time (IST) | Active Symbols | Description |
|---------|------------|----------------|-------------|
| **Asian** | 05:30 - 14:30 | USDJPY, AUDUSD, EURJPY | Low volatility, range-bound |
| **London** | 13:00 - 22:00 | GBPUSD, EURUSD, GBPJPY | High liquidity, trending |
| **Overlap** | 18:00 - 20:30 | All major pairs | Highest volume |
| **NY Late** | 22:00 - 02:00 | USDCAD, EURUSD | Consolidation |
| **Dead Zone** | 02:00 - 05:30 | None | No trading |

**Key Features:**
- ✅ Dynamic updates via Telegram (no code changes needed)
- ✅ Master switch to enable/disable ALL filtering
- ✅ Per-session symbol ON/OFF toggles
- ✅ Time adjustments in 30-minute increments
- ✅ Force-close option at session end

---

## 🎮 How It Works (User Perspective)

### 1. Clock & Calendar
```
User opens Telegram
      ↓
Sees pinned message:
"🕐 Current Time: 22:15:30 IST
 📅 Date: 11 Jan 2026 (Saturday)"
      ↓
Updates automatically every second
```

### 2. Session Manager
```
User taps "Session Manager" button
      ↓
Sees dashboard:
- Master Switch: ON
- Current Session: London
- Allowed Symbols: GBPUSD, EURUSD (2/7)
      ↓
Taps "Edit Sessions"
      ↓
Selects "Asian Session"
      ↓
Toggle symbols: USDJPY [✅] EURUSD [❌]
Adjust times: Start [−30m] [+30m]
Enable: Force Close [✅]
      ↓
Tap "Save" → Config updated instantly
```

### 3. Session-Based Trading
```
15:00 IST - London Session
GBPUSD signal received
      ↓
Bot checks: Is GBPUSD allowed in London? → YES
      ↓
Trade executed ✅
Voice alert: "Trade opened: BUY GBPUSD 0.5 lots"
      ↓
19:50 IST - 30 min before Overlap
Voice alert: "London-NY Overlap starts in 30 minutes"
```

### 4. Voice Alerts
```
Trade executed
      ↓
Alert queued (Priority: HIGH)
Channels: [Voice, Text]
      ↓
Telegram Voice Message sent
(Text-to-Speech: "Trade opened: BUY EURUSD...")
      ↓
If fails → Try Text fallback
If fails → Try SMS (CRITICAL only)
      ↓
Retry 3 times: 10s, 30s, 60s
```

---

## ⚙️ Configuration Reference

### session_settings.json Structure

```json
{
  "version": "1.0",
  "master_switch": true,              // Global ON/OFF
  "timezone": "Asia/Kolkata",
  "sessions": {
    "asian": {
      "name": "Asian Session",
      "start_time": "05:30",           // HH:MM format
      "end_time": "14:30",
      "allowed_symbols": ["USDJPY"],
      "advance_alert_enabled": true,   // 30-min warning
      "advance_alert_minutes": 30,
      "force_close_enabled": false     // Auto-close at end
    },
    // ... (other sessions)
  },
  "all_symbols": ["EURUSD", "GBPUSD", ...]
}
```

**Modification Methods:**
1. **Via Telegram UI** (Recommended): Zero-typing button interface
2. **Manual Edit**: Direct JSON file edit (requires bot restart)

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Session detection accuracy (all 5 sessions)
- [ ] Symbol filtering (allowed/disallowed symbols)
- [ ] Time adjustment edge cases (midnight boundary)
- [ ] IST timezone conversion accuracy
- [ ] Voice message TTS generation
- [ ] Alert queue processing

### Integration Tests
- [ ] Session transition detection (30-min advance alerts)
- [ ] Force-close mechanism at session end
- [ ] Master switch global override
- [ ] Telegram UI button interactions
- [ ] Voice alert multi-channel fallback

### End-to-End Tests
- [ ] Full trading workflow with session filtering
- [ ] Clock stability (24-hour continuous run)
- [ ] Voice alerts with phone locked
- [ ] JSON config persistence (1000 saves)
- [ ] Memory leak test (7-day operation)

---

## 🚀 Deployment Steps

### 1. Install Dependencies
```bash
cd ZepixTradingBot-old-v2-main
pip install -r requirements.txt
```

### 2. Verify Configuration
```bash
# Check if session_settings.json exists
ls data/session_settings.json

# Verify environment variables
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

### 3. Run Initial Tests
```bash
python -m pytest tests/test_session_manager.py -v
python -m pytest tests/test_voice_alerts.py -v
```

### 4. Start Bot
```bash
python src/main.py
```

### 5. Verify in Telegram
- [ ] Clock message appears and updates
- [ ] "Session Manager" button visible
- [ ] Can toggle symbols in UI
- [ ] Voice alert test successful

---

## 🔄 Rollback Procedure

If something goes wrong:

```bash
# 1. Stop bot
Ctrl+C

# 2. Restore previous version
git checkout <previous-commit>

# 3. Restore config backup
cp data/session_settings.json.backup data/session_settings.json

# 4. Restart bot
python src/main.py
```

---

## 📜 Key Design Decisions

### Why Dynamic JSON Config?
- **Before:** Session times hardcoded in Python files
- **After:** Stored in JSON, editable via Telegram
- **Benefit:** No code changes needed, instant updates

### Why Voice Alerts?
- **Problem:** Telegram notifications fail when phone is locked
- **Solution:** Voice messages bypass lock screen
- **Fallback:** Text → SMS for guaranteed delivery

### Why Session-Based Trading?
- **Forex Reality:** Different sessions have different volatility
- **Risk Management:** Avoid low-liquidity periods
- **Strategy Optimization:** Trade only favorable sessions

### Why IST Timezone?
- **User Location:** Primary user is in India (IST)
- **Forex Advantage:** IST covers Asian + part of London session
- **Consistency:** All bot times in single timezone

---

## 📚 Documentation Index

### Planning & Design
- `00_PROJECT_BRIEF.md` - Complete feature specification (40 pages)
- `01_IMPLEMENTATION_PLAN.md` - Detailed code plans (60 pages)

### User Guides (To be created in Phase 8)
- `SESSION_MANAGER_GUIDE.md` - How to use Session Manager UI
- `VOICE_ALERT_CONFIGURATION.md` - Configuring voice alerts
- `TROUBLESHOOTING.md` - Common issues and solutions

### Developer Docs
- `ARCHITECTURE_DECISIONS.md` - Why we built it this way
- `API_REFERENCE.md` - Module/class/function documentation
- `TESTING_GUIDE.md` - How to run tests

---

## ⚠️ Known Limitations

1. **TTS Voice Quality:** Uses Google TTS (gTTS), accent may vary
2. **SMS Costs:** SMS fallback requires paid gateway account
3. **Telegram Rate Limits:** Voice messages limited to ~20/min
4. **Clock Precision:** Updates every 1 second (not millisecond)
5. **Session Detection:** Requires bot to be running continuously

---

## 🛠️ Future Enhancements (Post-V1)

- [ ] Multi-timezone support (show NY time, London time)
- [ ] Custom TTS voice selection
- [ ] WhatsApp integration for alerts
- [ ] Mobile app for session management
- [ ] Historical session performance analytics
- [ ] AI-powered optimal session suggestions

---

## 📞 Support & Contribution

### Reporting Issues
1. Check `TROUBLESHOOTING.md` first
2. Check logs in `logs/forex_sessions.log`
3. Create detailed issue report with:
   - Error message
   - Steps to reproduce
   - Configuration used
   - Bot version

### Contributing
1. Follow existing code style
2. Add unit tests for new features
3. Update documentation
4. Test on local environment first

---

## 📄 License & Credits

**Project:** Zepix Trading Bot v2.0  
**Enhancement:** V4 Forex Session System  
**Created:** 2026-01-11  
**Developer:** Development Team  
**License:** (Same as main bot project)

---

## 📊 Project Status

**Current Phase:** Phase 1 (Documentation) ✅ COMPLETE  
**Next Phase:** Phase 2 (Fixed Clock System) 🔄 STARTING  
**Overall Progress:** 20% Complete  
**Estimated Completion:** 2026-01-21 (10 days)

---

**Ready to proceed to Phase 2? Let's build the clock system! ⏰**
