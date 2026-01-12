# 09_MIGRATION_PATH_ANALYSIS.md

**Document Version:** 1.0  
**Date:** 2026-01-12  
**Status:** Research Complete

---

## 🎯 OBJECTIVE

Map the exact migration path from current V3 monolithic logic to Plugin-based V3.

---

## 📍 CURRENT STATE (Before Migration)

### **File Structure**
```
src/
├── core/
│   └── trading_engine.py  ← Contains ALL V3 logic
│       ├── process_alert()
│       ├── _handle_entry_combinedlogic_1()
│       ├── _handle_entry_combinedlogic_2()
│       ├── _handle_entry_combinedlogic_3()
│       ├── _handle_exit_signal()
│       └── _handle_reversal_signal()
```

### **Logic Distribution**
- **combinedlogic-1:** Lines 500-800 in trading_engine.py
- **combinedlogic-2:** Lines 800-1100 in trading_engine.py
- **combinedlogic-3:** Lines 1100-1400 in trading_engine.py

### **Database**
- Single DB: `data/zepix_bot.db`
- All logics write to same `trades` table
- Differentiation via `comment` field

---

## 🎯 TARGET STATE (After Migration)

### **File Structure**
```
src/
├── core/
│   ├── trading_engine.py  ← Simplified, routes to plugins
│   └── plugin_system/
│       ├── base_plugin.py
│       ├── plugin_registry.py
│       └── service_api.py
│
├── logic_plugins/
│   └── combined_v3/
│       ├── plugin.py
│       ├── entry_logic.py
│       ├── exit_logic.py
│       └── config.json
│
└── services/
    ├── order_execution_service.py
    ├── risk_management_service.py
    └── profit_booking_service.py
```

### **Database**
- Plugin DB: `data/zepix_combined_v3.db`
- Main DB: `data/zepix_bot.db` (aggregation only)

---

## 🗺️ MIGRATION MAPPING

### **Step 1: Extract Entry Logic**

**Source:** `trading_engine.py` lines 500-1400

**Target:** `logic_plugins/combined_v3/entry_logic.py`

**Extraction Map:**
| Original Method | New Location | Changes |
|---|---|---|
| `_handle_entry_combinedlogic_1()` | `EntryLogic.process_entry()` | Use ServiceAPI instead of managers |
| `_handle_entry_combinedlogic_2()` | Same method, different config | Config-driven behavior |
| `_handle_entry_combinedlogic_3()` | Same method, different config | Config-driven behavior |
| `_validate_trend()` | `EntryLogic._check_trend()` | Call TrendManagementService |
| `_calculate_lot_size()` | Remove | Use RiskManagementService |
| `_place_dual_orders()` | `EntryLogic._execute_dual_orders()` | Use OrderExecutionService |

**Code Diff Example:**
```python
# BEFORE (in trading_engine.py)
def _handle_entry_combinedlogic_1(self, alert):
    trend = self.trend_manager.get_trend(alert.symbol)
    lot_a = self.risk_manager.calculate_lot(alert.sl_pips)
    lot_b = lot_a * 2
    
    order_a = self.mt5_client.place_order(...)
    order_b = self.mt5_client.place_order(...)

# AFTER (in combined_v3/entry_logic.py)
def process_entry(self, alert):
    # Use services instead of managers
    trend = self.service_api.trend.get_current_trend(alert.symbol)
    lot_a = self.service_api.risk.calculate_lot_size(
        plugin_id=self.plugin.plugin_id,
        ...
    )
    lot_b = lot_a * 2
    
    order_a = self.service_api.orders.place_order(
        plugin_id=self.plugin.plugin_id,
        ...
    )
    order_b = self.service_api.orders.place_order(...)
```

---

### **Step 2: Extract Exit Logic**

**Source:** `trading_engine.py` lines 1450-1600

**Target:** `logic_plugins/combined_v3/exit_logic.py`

**Extraction Map:**
| Original Method | New Location |
|---|---|
| `_handle_exit_signal()` | `ExitLogic.process_exit()` |
| `_close_all_for_symbol()` | `ExitLogic._close_symbol_trades()` |
| `_partial_close()` | Remove, use ProfitBookingService |

---

### **Step 3: Data Migration**

```python
# Migration script: scripts/migrate_v3_to_plugin_db.py

def migrate_trades():
    """
    Copies V3 trades from main DB to plugin DB.
    """
    main_db = sqlite3.connect("data/zepix_bot.db")
    plugin_db = sqlite3.connect("data/zepix_combined_v3.db")
    
    # Get V3 trades
    v3_trades = main_db.execute("""
        SELECT * FROM trades 
        WHERE comment LIKE '%combinedlogic%'
        AND created_at >= '2026-01-01'  -- Only recent data
    """).fetchall()
    
    print(f"Migrating {len(v3_trades)} trades...")
    
    # Insert into plugin DB
    for trade in v3_trades:
        plugin_db.execute("""
            INSERT INTO trades 
            (mt5_ticket, symbol, direction, lot_size, ...)
            VALUES (?, ?, ?, ?, ...)
        """, trade)
    
    plugin_db.commit()
    print("✅ Migration complete")
```

---

## 🧪 SHADOW TESTING STRATEGY

### **Phase 4.3: Parallel Execution**

**Goal:** Run old V3 and new V3 Plugin side-by-side, verify identical behavior.

**Setup:**
```python
# In trading_engine.py

async def process_alert(self, alert):
    # LEGACY V3 (Still active)
    if self.config["legacy_v3"]["enabled]:
        legacy_result = await self._process_v3_legacy(alert)
    
    # NEW V3 PLUGIN (Shadow mode)
    if self.config["plugin_system"]["shadow_mode"]:
        plugin_result = await self.plugin_registry.route_alert(
            alert, 
            "combined_v3"
        )
        
        # Compare results
        if legacy_result != plugin_result:
            self.telegram.send_message(
                f"⚠️ MISMATCH DETECTED:\n"
                f"Legacy: {legacy_result}\n"
                f"Plugin: {plugin_result}"
            )
```

**Test Duration:** 72 hours minimum

**Success Criteria:**
- 100% decision parity (same orders placed)
- 100% lot size parity
- 100% SL/TP parity
- Zero logic regressions

---

## 📋 MIGRATION CHECKLIST

### **Pre-Migration**
- [ ] Create plugin database schema
- [ ] Implement plugin code
- [ ] Write migration scripts
- [ ] Create rollback procedure

### **Shadow Testing**
- [ ] Enable shadow mode
- [ ] Monitor for 72 hours
- [ ] Log all mismatches
- [ ] Fix any discrepancies
- [ ] Re-test until 100% parity

### **Cutover**
- [ ] Backup main database
- [ ] Disable legacy V3 logic
- [ ] Enable V3 plugin
- [ ] Migrate existing open trades
- [ ] Monitor for 24 hours

### **Post-Migration**
- [ ] Verify all trades routing correctly
- [ ] Check analytics reports
- [ ] Confirm Telegram notifications
- [ ] Update documentation

---

## 🔄 ROLLBACK PROCEDURE

**If plugin fails in first 48 hours:**

```bash
# 1. Disable plugin
echo '{"plugins": {"combined_v3": {"enabled": false}}}' > config/override.json

# 2. Re-enable legacy V3
# In config.json: "legacy_v3": {"enabled": true}

# 3. Restore main database (if needed)
cp backups/2026-01-11/zepix_bot.db data/zepix_bot.db

# 4. Restart bot
systemctl restart zepix-bot

# 5. Verify
curl http://localhost:8000/health
```

**RTO (Recovery Time Objective):** < 5 minutes  
**RPO (Recovery Point Objective):** 0 trades lost

---

## 📊 RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Logic regression | Medium | Critical | Shadow testing |
| Data loss | Low | Critical | Backups before cutover |
| Performance degradation | Low | Medium | Benchmark before/after |
| Plugin crash | Medium | High | Fallback to legacy |

---

## ✅ DECISION

**APPROVED:** Phased migration with shadow testing and instant rollback capability.

**Timeline:**
- Week 4: Shadow testing starts
- Week 5: Cutover (if 100% parity achieved)
- Week 6: Monitoring period
