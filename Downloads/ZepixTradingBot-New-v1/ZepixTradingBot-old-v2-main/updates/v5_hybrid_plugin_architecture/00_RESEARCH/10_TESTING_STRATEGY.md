# 🧪 UNIVERSAL TESTING STRATEGY
**Zero Tolerance for Errors | Hybrid Architecture**

## 1. CORE PHILOSOPHY
**"Guilty until proven innocent."**
All code is considered broken until it passes all testing gates. We do not "hope" it works; we **prove** it works.

**Key Principles:**
1.  **Zero Regression:** Existing functionality must NEVER break.
2.  **Parallel Verification:** New systems run alongside old ones (Shadow Mode) before switching.
3.  **Data Integrity:** Database states are verified before and after every migration.
4.  **Bot Health:** If a bot doesn't respond in 5 seconds, it's considered failed.

---

## 2. TESTING PYRAMID

### Level 1: Unit Tests (30%)
*   **Scope:** Individual functions, classes, and methods.
*   **Tools:** `pytest`
*   **Requirement:** 100% coverage for new logic (Plugins, Services).
*   **Example:** Testing `BaseLogicPlugin.process_entry_signal` with a mock alert.

### Level 2: Integration Tests (40%)
*   **Scope:** Interactions between components (e.g., Plugin <-> Registry, Manager <-> Database).
*   **Tools:** `pytest`, local Service API mocks.
*   **Requirement:** Verify data flow and error handling between systems.
*   **Example:** Registry successfully routing an alert to the correct loaded plugin.

### Level 3: Shadow/Parallel Tests (20%)
*   **Scope:** Real-time production data processing.
*   **Method:** Run Legacy Manager AND New Plugin/Service simultaneously on the same inputs.
*   **Verification:** Compare outputs (orders placed, logs generated). Mismatch = Failure.
*   **Duration:** Minimum 24-48 hours per major migration.

### Level 4: End-to-End (E2E) & User Acceptance (10%)
*   **Scope:** Full user workflows (Telegram commands, Trade lifecycle).
*   **Method:** User performs specific scenarios (Entry -> TP -> Exit).
*   **Verification:** Manual confirmation + "Voice Verification" (User confirms "Yes, this works").

---

## 3. PHASE-SPECIFIC TESTING GATES

### Phase 1: Plugin Foundation
*   [ ] **Unit:** `PluginRegistry` discovers/loads plugins correctly.
*   [ ] **Integration:** Dummy plugin receives alerts via `route_alert`.
*   [ ] **Regression:** Legacy system operates normally with Plugin System enabled (but idle).

### Phase 2: Multi-Telegram
*   [ ] **Health:** All 3 bots (Controller, Notif, Analytics) respond to `/ping`.
*   [ ] **Routing:** Trade alerts go ONLY to Notification Bot.
*   [ ] **Routing:** Control commands worked ONLY on Controller Bot.
*   [ ] **Fallback:** Legacy bot still works if new bots are disabled.

### Phase 3: Service API
*   [ ] **Parity:** Logic extracted to Services matches Managers exactly (Shadow Test).
*   [ ] **Integration:** Managers successfully call Services.
*   [ ] **Performance:** No latency increase > 10ms per call.

### Phase 4: V3 Migration
*   [ ] **Data:** Database migration script transfers 100% of historical trades.
*   [ ] **Shadow:** `combined_v3` plugin output matches `TradingEngine` V3 logic for 48 hrs.
*   [ ] **Function:** User confirms 5 live trades matched exactly.

### Phase 5: V6 Implementation
*   [ ] **Logic:** All 14 V6 alert types trigger correct internal handlers.
*   [ ] **Conflict:** V6 plugin runs alongside V3 plugin without database locks/errors.
*   [ ] **Database:** `zepix_price_action.db` saves data correctly.

---

## 4. TEST DATA & ENVIRONMENT

### Test Environment
*   **Config:** `config_test.json` (Clone of prod, separate DBs).
*   **Database:** `tests/test_zepix.db` (Reset before every test run).
*   **Mocking:** MT5 and Telegram APIs mocked for Unit/Integration tests.

### Synthetic Data Generation
*   Script: `scripts/generate_test_alerts.py`
*   Generates: standard entries, exits, reversals, malformed alerts, rapid-fire bursts.

---

## 5. AUTOMATED TEST SUITE COMMANDS

```bash
# Run all unit tests
pytest tests/unit

# Run plugin specific tests
pytest tests/plugins/test_v3_plugin.py

# Run database migration verification
python scripts/verify_migration.py --source old.db --target new.db

# Run full regression suite (must pass before any commit)
./run_regression_suite.sh
```

## 6. EXIT CRITERIA (DEFINITION OF DONE)
For any phase to be marked complete:
1.  All Unit/Integration tests PASS.
2.  No "Critical" or "High" severity bugs open.
3.  Shadow testing shows 0 logic mismatches.
4.  Documentation updated.
5.  **USER APPROVAL** given.
