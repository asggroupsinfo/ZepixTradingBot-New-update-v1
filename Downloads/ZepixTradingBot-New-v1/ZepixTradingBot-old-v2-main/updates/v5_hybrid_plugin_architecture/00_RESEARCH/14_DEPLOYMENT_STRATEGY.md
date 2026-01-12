# 14_DEPLOYMENT_STRATEGY.md

**Document Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Research Complete

---

## 🎯 OBJECTIVE

Define zero-downtime deployment strategy for each phase of v5 migration.

---

## 🚀 DEPLOYMENT PRINCIPLES

1. **Zero Downtime:** Bot never goes offline during deployment
2. **Instant Rollback:** Can revert in <5 minutes
3. **Data Safety:** No trade data loss
4. **Monitoring:** Alert on any degradation

---

## 📋 PHASE-BY-PHASE DEPLOYMENT

### **Phase 1: Plugin System (Silent)**

**Goal:** Add plugin system without activating it.

**Steps:**
1. Deploy new code (plugin_system disabled in config)
2. Restart bot (gracefully)
3. Verify bot starts correctly
4. Monitor for 1 hour

**Rollback:** Git revert + restart

**Risk:** 🟢 LOW (plugin system inactive)

---

### **Phase 2: Multi-Telegram (Parallel)**

**Goal:** Run 3 bots alongside main bot.

**Steps:**
1. Create 3 new bots via @BotFather
2. Add tokens to config (secure)
3. Deploy MultiTelegramManager code
4. Enable multi_telegram in config
5. Restart bot
6. Test all 3 bots respond

**Fallback:** If any bot fails, revert to main bot token

**Risk:** 🟡 MEDIUM (Telegram API dependency)

---

### **Phase 3: Service API (Transparent)**

**Goal:** Add services without breaking existing managers.

**Steps:**
1. Deploy service layer code
2. Refactor managers to delegate to services (backward compatible)
3. Restart bot
4. Verify orders still placed correctly
5. Monitor latency (should be <10% increase)

**Rollback:** Managers fall back to direct MT5 calls

**Risk:** 🟡 MEDIUM (Performance risk)

---

### **Phase 4: V3 Plugin (Shadow Mode → Cutover)**

**Goal:** Migrate V3 logic to plugin.

**Steps:**

**4.1 Shadow Deployment** (Week 1)
1. Deploy V3 plugin code
2. Enable shadow mode (plugin receives signals but doesn't trade)
3. Compare decisions (legacy vs plugin) for 72 hours
4. Fix any discrepancies

**4.2 Cutover** (Week 2, Friday evening)
1. **18:00:** Backup all databases
2. **18:10:** Enable V3 plugin
3. **18:15:** Disable legacy V3 logic
4. **18:20:** Send test alert, verify plugin responds
5. **18:30:** Monitor first real alert

**Monitoring Window:** 48 hours of intensive monitoring

**Rollback Trigger:**
- Any logic regression
- >5% performance degradation
- Any critical bug

**Rollback Procedure:**
```bash
# 1. Disable plugin
curl -X POST http://localhost:8000/admin/disable_plugin/combined_v3

# 2. Enable legacy
curl -X POST http://localhost:8000/admin/enable_legacy_v3

# 3. Verify
curl http://localhost:8000/health
```

**Risk:** 🔴 HIGH (Core logic change)

---

## 🔄 ZERO-DOWNTIME RESTART PROCEDURE

```bash
# 1. Graceful shutdown (wait for in-flight requests)
kill -SIGTERM $(pidof python src/main.py)

# Wait for process to exit (max 30s)
timeout 30 bash -c 'while kill -0 $PID 2>/dev/null; do sleep 1; done'

# 2. Start new version
nohup python src/main.py > logs/bot.log 2>&1 &

# 3. Health check
sleep 5
curl http://localhost:8000/health || (echo "FAILED TO START" && exit 1)
```

**Downtime:** ~5-10 seconds (acceptable)

---

## 📊 MONITORING STRATEGY

### **Key Metrics**

| Metric | Normal | Alert Threshold |
|---|---|---|
| Alert Processing Time | <500ms | >1000ms |
| Order Success Rate | >98% | <95% |
| MT5 Connection | UP | DOWN |
| Memory Usage | <300MB | >500MB |
| CPU Usage | <30% | >70% |
| Error Rate | <1% | >5% |

### **Monitoring Tools**

1. **Health Endpoint:** `GET /health`
   ```json
   {
       "status": "healthy",
       "uptime": 86400,
       "open_trades": 5,
       "plugins_active": ["combined_v3"],
       "telegram_bots": ["controller", "notification", "analytics"]
   }
   ```

2. **Telegram Alerts:** Auto-alert on anomalies

3. **Log Monitoring:** Grep for errors
   ```bash
   tail -f logs/bot.log | grep "ERROR"
   ```

---

## 🧪 PRE-DEPLOYMENT TESTING

### **Staging Environment**

**Setup:**
```
├── Production
│   ├── MT5: Live account
│   └── Port: 8000
│
└── Staging
    ├── MT5: Demo account
    └── Port: 8001
```

**Test Sequence:**
1. Deploy to staging first
2. Run 100 simulated alerts
3. Verify all alerts processed correctly
4. Check for errors in logs
5. If clean, promote to production

---

## 📅 DEPLOYMENT SCHEDULE

### **Recommended Timeline**

| Phase | Duration | Deployment Window | Monitoring |
|---|---|---|---|
| Phase 1 | Week 1 | Tuesday 10:00 | 24h |
| Phase 2 | Week 2 | Tuesday 10:00 | 24h |
| Phase 3 | Week 3 | Tuesday 10:00 | 48h |
| Phase 4 (Shadow) | Week 4 | Monday 09:00 | 72h |
| Phase 4 (Cutover) | Week 5 | Friday 18:00 | 48h |

**Deployment Days:** Tuesday or Friday (low market volatility)  
**Deployment Time:** 10:00 IST or 18:00 IST (after major sessions)

---

## ✅ DECISION

**APPROVED:** Phased deployment with shadow testing and instant rollback.

**Next Steps:**
1. Setup staging environment
2. Create deployment scripts
3. Document rollback procedures
