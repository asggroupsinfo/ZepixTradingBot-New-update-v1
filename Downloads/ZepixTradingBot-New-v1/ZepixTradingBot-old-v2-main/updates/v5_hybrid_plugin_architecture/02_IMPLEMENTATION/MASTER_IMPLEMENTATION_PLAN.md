# 🛠️ MASTER IMPLEMENTATION PLAN: v5 Hybrid Architecture

**Objective:** Systematic rollout of the v5 Hybrid Plugin Architecture.
**Method:** "One by One" execution of granular steps.

---

## ✅ PHASE 1: FOUNDATION (Completed)
- [x] **1.1 Base Plugin System**
  - `BaseLogicPlugin` interface created.
  - `PluginRegistry` created.
  - `ServiceAPI` created.
- [x] **1.2 Integration**
  - `TradingEngine` updated to initialize plugins.
  - Signal hooks (`on_signal_received`) implemented.
  - `src/logic_plugins` directory created.

---

## 🚧 PHASE 2: MULTI-TELEGRAM SYSTEM (Next)
**Objective:** Deploy specialized bots (Controller, Notifications, Analytics) alongside the main bot.

- [ ] **2.1 Bot Creation**
  - User to create 3 bots via BotFather.
  - Save tokens in `config/telegram_tokens.json`.
- [ ] **2.2 MultiTelegramManager**
  - Create `src/telegram/multi_telegram_manager.py`.
  - Implement routing logic (Commands vs Alerts vs Reports).
- [ ] **2.3 Specialized Bot Handlers**
  - `ControllerBot`: Handle `/start`, `/stop`, `/status`.
  - `NotificationBot`: Handle Entry/Exit alerts.
  - `AnalyticsBot`: Handle `/report`.
- [ ] **2.4 Integration**
  - Update `TradingEngine` to use `MultiTelegramManager`.
- [ ] **2.5 Verification**
  - Test all 3 bots independently.

---

## ⏳ PHASE 3: SERVICE API LAYER
**Objective:** migrate business logic (Orders, Risk, Profits) into stateless services.

- [ ] **3.1 Service Interfaces**
  - Define `BaseService` in `src/core/service_api.py`.
- [ ] **3.2 OrderExecutionService**
  - Implement `OrderExecutionService` for placing/tracking orders per plugin.
- [ ] **3.3 ProfitBookingService**
  - Implement logic for partial TPs and profit chains.
- [ ] **3.4 RiskManagementService**
  - Implement lot size calculation logic.
- [ ] **3.5 Refactor Managers**
  - Update `OrderManager` to delegate to `OrderExecutionService`.
  - Update `RiskManager` to use `RiskManagementService`.

---

## ⏳ PHASE 4: LOGIC MIGRATION (V3 Plugin)
**Objective:** Move existing V3 logic into a plugin without breaking it.

- [ ] **4.1 Plugin Structure**
  - Create `src/logic_plugins/combined_v3/`.
- [ ] **4.2 Port Logic**
  - Move Entry Logic to `combined_v3/entry_logic.py`.
  - Move Exit Logic to `combined_v3/exit_logic.py`.
- [ ] **4.3 Shadow Testing**
  - Run V3 Plugin in "Shadow Mode" (Signal-only, no trade).
  - Compare V3 Plugin signals with Legacy V3 signals.
- [ ] **4.4 Cutover**
  - Disable Legacy V3 logic in `TradingEngine`.
  - Enable V3 Plugin.

---

## ⏳ PHASE 5: DYNAMIC CONFIG & DB
**Objective:** Isolate configurations and databases per plugin.

- [ ] **5.1 Config Manager**
  - Implement `DynamicConfigManager`.
- [ ] **5.2 Database Isolation**
  - Ensure each plugin gets its own SQLite DB (e.g., `zepix_v3.db`).

---

## ⏳ PHASE 6: UI DASHBOARD (Optional)
**Objective:** Web interface for managing plugins.

- [ ] **6.1 Web API**
  - Create FastAPI endpoints for plugin management.
- [ ] **6.2 Dashboard UI**
  - Simple HTML/JS dashboard to Start/Stop plugins.

---

## 🚀 EXECUTION PROTOCOL
1. **Select Step:** We pick the next unchecked item.
2. **Implement:** I write the code.
3. **Verify:** We run tests/verification.
4. **Mark Done:** We update this plan.
5. **Repeat.**
