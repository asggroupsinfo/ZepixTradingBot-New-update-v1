# ↩️ COMPREHENSIVE ROLLBACK PROCEDURES
**Emergency Recovery Manual | Hybrid Architecture**

## 1. ROLLBACK PHILOSOPHY
**"Better safe than sorry."**
If a critical error occurs that cannot be fixed within **1 hour**, we DO NOT debug in production. We **ROLLBACK** immediately to the last stable state.

**Triggers for Immediate Rollback:**
1.  Loss of trading capability (orders not filling).
2.  Database corruption or data loss.
3.  Uncontrolled loop/spamming of Telegram or MT5.
4.  User reports "Something feels wrong" regarding money/risk.

---

## 2. GENERAL RECOVERY STEPS (APP-WIDE)

### Level 1: Configuration Disable (Soft Rollback)
*Used when a new feature causes minor issues but core bot is fine.*
1.  Stop the bot: `Ctrl+C` or kill process.
2.  Edit `config.json`: Set `plugin_system.enabled = false`.
3.  Restart bot.
4.  **Result:** Bot reverts to using only legacy managers.

### Level 2: Code Revert (Hard Rollback)
*Used when code changes broke logic even when feature is disabled.*
1.  Stop the bot.
2.  Restore backup: `cp -r backups/pre_phase_X/* .` (Assuming backups taken).
3.  **Alternative (Git):** `git reset --hard <tag_pre_phase_X>`
4.  Restart bot.

### Level 3: Database Restoration (Critical Rollback)
*Used when database schema/data is corrupted.*
1.  Stop the bot.
2.  Identify last healthy DB backup in `backups/db/`.
3.  Replace file: `cp backups/db/zepix.db_TIMESTAMP data/zepix.db`
4.  Restart bot.

---

## 3. PHASE-SPECIFIC ROLLBACK PROCEDURES

### Phase 1 Rollback (Plugin System)
**Scenario:** Plugin Registry causes bot crash on startup.
**Action:**
1.  Set `config.json`: `"plugin_system": { "enabled": false }`.
2.  Delete `src/logic_plugins/_template` if causing import errors.
3.  Verify: Bot starts and says "Plugin system disabled".

### Phase 2 Rollback (Multi-Telegram)
**Scenario:** Notifications missing or going to wrong bots.
**Action:**
1.  Stop bot.
2.  Configuration: Revert to single bot token in `config.json`.
3.  Code: Revert `main.py` to initialize `TelegramBot` instead of `MultiTelegramManager`.
4.  Verify: Old bot responds to `/start`.

### Phase 3 Rollback (Service API)
**Scenario:** Extracted service logic (e.g., OrderExecution) fails to place trades.
**Action:**
1.  Stop bot.
2.  **Restore Managers:** The legacy Managers (`dual_order_manager.py`, etc.) are kept in specific `_legacy` folders or git branches.
3.  Revert `trading_engine.py` imports to point back to Managers, not Services.
4.  Verify: Test trade functionality in demo execution.

### Phase 4 Rollback (V3 Migration)
**Scenario:** `combined_v3` plugin executing trades incorrectly/doubling orders.
**Action:**
1.  **DISABLE PLUGIN:** Set `plugins.combined_v3.enabled = false` in `config.json`.
2.  **ENABLE LEGACY:** In `config.json`, verify legacy `strategies` logic is active.
3.  **DB Revert:** If `zepix.db` was altered, restore pre-migration backup.
4.  **Verify:** Legacy `TradingEngine` picks up the next alert.

### Phase 5 Rollback (V6 Implementation)
**Scenario:** V6 plugin conflicts with V3 or causes latency.
**Action:**
1.  Set `plugins.price_action_v6.enabled = false`.
2.  Verify V3 plugin/legacy logic continues to work.
3.  Debug V6 plugin offline/in isolation.

---

## 4. EMERGENCY "KILL SWITCH" SCRIPT

**File:** `scripts/emergency_stop.py`
(To be created in Phase 1)

**Function:**
1.  Immediately stops all Python processes related to Zepix.
2.  Disables all trading in `config.json` (`trading_enabled: false`).
3.  Sends "EMERGENCY STOP TRIGGERED" message to Admin Telegram.

**Running it:**
```bash
python scripts/emergency_stop.py
```

## 5. POST-ROLLBACK CHECKLIST
After any rollback, you must:
1.  [ ] Verify Bot is Online (`/ping`).
2.  [ ] Verify MT5 Connection.
3.  [ ] Check Logs for specific "Rollback Successful" or normal startup messages.
4.  [ ] Notify User: "System rolled back to stable state. Investigation started."
