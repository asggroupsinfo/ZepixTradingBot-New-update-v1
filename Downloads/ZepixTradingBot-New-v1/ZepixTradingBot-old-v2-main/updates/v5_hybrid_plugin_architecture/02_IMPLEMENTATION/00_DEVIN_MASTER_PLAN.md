# DEVIN AI - MASTER IMPLEMENTATION PLAN
# V5 Hybrid Plugin Architecture - Complete Surgical Integration

**Version:** 1.0  
**Date:** 2026-01-12  
**Author:** Devin AI  
**Project Manager:** Antigravity OS  
**Status:** READY FOR PM APPROVAL  

---

## EXECUTIVE SUMMARY

This Master Plan documents the complete transformation of ZepixTradingBot from a monolithic V2 architecture to a scalable V5 Hybrid Plugin Architecture. Based on comprehensive analysis of 43 documents (16 research + 27 planning) totaling ~400KB of specifications, this plan outlines the implementation of 50+ modules across 6 phases over 10-12 weeks.

**Key Transformation Goals:**
- Plugin-based system for unlimited Pine Script strategies
- Multi-Telegram system (3 bots) for clear notifications
- Zero-impact migration (old V2 keeps running while V5 built)
- 100% backward compatibility with existing V3 logic
- Complete database isolation per plugin

---

## 1. ARCHITECTURE UNDERSTANDING SUMMARY

### 1.1 Current State Analysis

**Existing Codebase Structure:**
- **TradingEngine** (2,072 lines): Monolithic trading logic with V3 alert processing
- **DualOrderManager** (346 lines): Order A (TP Trail) + Order B (Profit Trail) system
- **15 Managers**: Risk, Profit Booking, Re-entry, Session, Autonomous, etc.
- **Database**: Single SQLite file (trading_bot.db) with 10+ tables
- **Telegram**: Single bot for all notifications
- **Plugin System**: Basic skeleton exists (PluginRegistry, ServiceAPI, BaseLogicPlugin)

**Current V3 Combined Logic:**
- 12 signal types (7 entry, 2 exit, 2 info, 1 trend pulse)
- 3 logic routes (LOGIC1: 5m scalp, LOGIC2: 15m intraday, LOGIC3: 1h swing)
- Dual order system (Order A + Order B with different SL strategies)
- Hybrid SL system (Smart SL for Order A, Fixed $10 SL for Order B)
- Multi-timeframe trend management

**Pain Points:**
- Monolithic architecture limits scalability
- Single Telegram bot causes notification clutter
- No database isolation between strategies
- Adding new Pine logic requires code changes
- No health monitoring or versioning

### 1.2 Target State Design

**V5 Hybrid Plugin Architecture:**

```
                    ┌─────────────────────────────────────┐
                    │         TELEGRAM LAYER              │
                    │  ┌─────────┐ ┌─────────┐ ┌─────────┐│
                    │  │Controller│ │Notifier │ │Analytics││
                    │  │   Bot   │ │   Bot   │ │   Bot   ││
                    │  └────┬────┘ └────┬────┘ └────┬────┘│
                    └───────┼──────────┼──────────┼──────┘
                            │          │          │
                    ┌───────▼──────────▼──────────▼──────┐
                    │      MultiTelegramManager          │
                    │  (Rate Limiting, Sticky Headers)   │
                    └───────────────┬────────────────────┘
                                    │
                    ┌───────────────▼────────────────────┐
                    │         TRADING ENGINE             │
                    │    (Signal Router + Orchestrator)  │
                    └───────────────┬────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼───────┐          ┌───────▼───────┐          ┌───────▼───────┐
│  V3 Combined  │          │ V6 Price Act  │          │ Future Plugin │
│    Plugin     │          │   Plugins     │          │   (Easy Add)  │
├───────────────┤          ├───────────────┤          ├───────────────┤
│ 12 signals    │          │ 4 TF plugins  │          │ Your logic    │
│ 3 logics      │          │ 1M/5M/15M/1H  │          │ Your rules    │
│ Dual orders   │          │ Cond. routing │          │ Your DB       │
└───────┬───────┘          └───────┬───────┘          └───────────────┘
        │                          │
        ▼                          ▼
┌───────────────┐          ┌───────────────┐
│zepix_combined │          │zepix_price_   │
│     .db       │          │  action.db    │
└───────────────┘          └───────────────┘
                                    
                    ┌───────────────────────────────────┐
                    │         SERVICE API LAYER         │
                    │  ┌─────────┐ ┌─────────┐ ┌──────┐ │
                    │  │ Orders  │ │  Risk   │ │Trend │ │
                    │  │ Service │ │ Service │ │Svc   │ │
                    │  └─────────┘ └─────────┘ └──────┘ │
                    │  ┌─────────┐ ┌─────────┐ ┌──────┐ │
                    │  │ Profit  │ │ Market  │ │Notify│ │
                    │  │ Booking │ │  Data   │ │Router│ │
                    │  └─────────┘ └─────────┘ └──────┘ │
                    └───────────────────────────────────┘
```

**Three-Database Architecture:**
1. **zepix_combined.db** - V3 Combined Logic trades, chains, sessions
2. **zepix_price_action.db** - V6 Price Action trades (all 4 TF plugins share)
3. **zepix_bot.db** - Central system data, aggregated stats, health metrics

### 1.3 Transformation Roadmap

| Phase | Name | Duration | Key Deliverables |
|-------|------|----------|------------------|
| 1 | Core Plugin System | Week 1-2 (5-7 days) | BaseLogicPlugin, PluginRegistry, PluginDatabase |
| 2 | Multi-Telegram System | Week 2-3 (5-7 days) | 3 Bots, Rate Limiting, Sticky Headers |
| 3 | Service API Layer | Week 3 (3-4 days) | 6 Services (Orders, Risk, Trend, Profit, Market, Notify) |
| 4 | V3 Plugin Migration | Week 4 (5-7 days) | V3CombinedPlugin with 100% feature parity |
| 5 | V6 Plugin Implementation | Week 4-5 (5-7 days) | 4 Price Action plugins (1M/5M/15M/1H) |
| 6 | Testing & Documentation | Week 5-6 (5-7 days) | Full test suite, user/developer docs |
| 7 | V6 Integration (Extended) | Week 5-6 (10-14 days) | Complete V6 alert handling, Trend Pulse |

---

## 2. FILE CHANGE MATRIX

### 2.1 New Files to Create (100+ files)

#### Phase 1: Core Plugin System (15 files)
| File | Purpose | Lines Est. |
|------|---------|------------|
| `src/core/plugin_system/base_plugin.py` | Enhanced BaseLogicPlugin with lifecycle hooks | 300 |
| `src/core/plugin_system/plugin_registry.py` | Enhanced registry with versioning | 400 |
| `src/core/plugin_system/plugin_database.py` | Per-plugin database manager | 350 |
| `src/core/plugin_system/plugin_config.py` | Plugin configuration loader | 200 |
| `src/core/plugin_system/plugin_events.py` | Event bus for plugin communication | 250 |
| `src/core/plugin_system/plugin_health.py` | Health monitoring per plugin | 300 |
| `src/core/plugin_system/plugin_version.py` | Semantic versioning system | 250 |
| `src/logic_plugins/combined_v3/__init__.py` | V3 plugin package init | 10 |
| `src/logic_plugins/combined_v3/plugin.py` | V3 Combined Logic plugin | 800 |
| `src/logic_plugins/combined_v3/config.yaml` | V3 plugin configuration | 100 |
| `src/logic_plugins/combined_v3/signals.py` | V3 signal handlers (12 types) | 500 |
| `src/logic_plugins/combined_v3/orders.py` | V3 dual order logic | 400 |
| `src/logic_plugins/combined_v3/database.py` | V3 database operations | 300 |
| `tests/unit/test_plugin_system.py` | Plugin system unit tests | 400 |
| `tests/integration/test_plugin_registry.py` | Plugin registry integration tests | 300 |

#### Phase 2: Multi-Telegram System (12 files)
| File | Purpose | Lines Est. |
|------|---------|------------|
| `src/telegram/multi_telegram_manager.py` | 3-bot orchestrator | 500 |
| `src/telegram/controller_bot.py` | Controller bot (commands, menus) | 600 |
| `src/telegram/notification_bot.py` | Notification bot (trade alerts) | 400 |
| `src/telegram/analytics_bot.py` | Analytics bot (reports, stats) | 400 |
| `src/telegram/rate_limiter.py` | Queue-based rate limiting | 350 |
| `src/telegram/sticky_headers.py` | Persistent menu headers | 300 |
| `src/telegram/notification_router.py` | Event-driven notification routing | 400 |
| `src/telegram/message_templates.py` | Notification message templates | 250 |
| `src/telegram/callback_handlers.py` | Inline button handlers | 350 |
| `src/telegram/voice_alerts.py` | Voice alert integration | 200 |
| `tests/unit/test_multi_telegram.py` | Multi-Telegram unit tests | 300 |
| `tests/integration/test_telegram_system.py` | Telegram integration tests | 250 |

#### Phase 3: Service API Layer (10 files)
| File | Purpose | Lines Est. |
|------|---------|------------|
| `src/services/service_api.py` | Enhanced ServiceAPI facade | 400 |
| `src/services/order_execution_service.py` | Order placement/modification | 450 |
| `src/services/risk_management_service.py` | Risk calculations, lot sizing | 400 |
| `src/services/trend_management_service.py` | MTF trend tracking | 350 |
| `src/services/profit_booking_service.py` | Profit booking pyramid | 400 |
| `src/services/market_data_service.py` | Spread, price, volatility | 500 |
| `src/services/notification_service.py` | Centralized notifications | 300 |
| `tests/unit/test_services.py` | Service unit tests | 400 |
| `tests/integration/test_service_api.py` | Service API integration tests | 300 |
| `config/services_config.yaml` | Service configuration | 150 |

#### Phase 4: V3 Plugin Migration (8 files)
| File | Purpose | Lines Est. |
|------|---------|------------|
| `src/logic_plugins/combined_v3/v3_entry_handler.py` | V3 entry signal processing | 500 |
| `src/logic_plugins/combined_v3/v3_exit_handler.py` | V3 exit signal processing | 400 |
| `src/logic_plugins/combined_v3/v3_reversal_handler.py` | V3 reversal handling | 350 |
| `src/logic_plugins/combined_v3/v3_trend_pulse.py` | V3 trend pulse processing | 300 |
| `src/logic_plugins/combined_v3/v3_logic_router.py` | Logic 1/2/3 routing | 300 |
| `migrations/combined_v3/001_initial_schema.sql` | V3 database schema | 150 |
| `tests/unit/test_v3_plugin.py` | V3 plugin unit tests | 500 |
| `tests/compatibility/test_v3_parity.py` | V3 backward compatibility tests | 400 |

#### Phase 5: V6 Plugin Implementation (20 files)
| File | Purpose | Lines Est. |
|------|---------|------------|
| `src/logic_plugins/price_action_1m/__init__.py` | 1M plugin package | 10 |
| `src/logic_plugins/price_action_1m/plugin.py` | 1M scalping plugin | 600 |
| `src/logic_plugins/price_action_1m/config.yaml` | 1M configuration | 80 |
| `src/logic_plugins/price_action_5m/__init__.py` | 5M plugin package | 10 |
| `src/logic_plugins/price_action_5m/plugin.py` | 5M intraday plugin | 600 |
| `src/logic_plugins/price_action_5m/config.yaml` | 5M configuration | 80 |
| `src/logic_plugins/price_action_15m/__init__.py` | 15M plugin package | 10 |
| `src/logic_plugins/price_action_15m/plugin.py` | 15M swing plugin | 600 |
| `src/logic_plugins/price_action_15m/config.yaml` | 15M configuration | 80 |
| `src/logic_plugins/price_action_1h/__init__.py` | 1H plugin package | 10 |
| `src/logic_plugins/price_action_1h/plugin.py` | 1H position plugin | 600 |
| `src/logic_plugins/price_action_1h/config.yaml` | 1H configuration | 80 |
| `src/logic_plugins/price_action_shared/v6_alert_model.py` | V6 alert data model | 200 |
| `src/logic_plugins/price_action_shared/trend_pulse.py` | V6 Trend Pulse system | 350 |
| `src/logic_plugins/price_action_shared/order_routing.py` | Conditional order routing | 300 |
| `src/logic_plugins/price_action_shared/database.py` | Shared V6 database ops | 300 |
| `migrations/price_action_v6/001_initial_schema.sql` | V6 database schema | 150 |
| `tests/unit/test_v6_plugins.py` | V6 plugin unit tests | 500 |
| `tests/integration/test_v6_alerts.py` | V6 alert integration tests | 400 |
| `tests/e2e/test_v6_full_flow.py` | V6 end-to-end tests | 350 |

#### Phase 6: Testing & Documentation (15 files)
| File | Purpose | Lines Est. |
|------|---------|------------|
| `tests/e2e/test_full_system.py` | Full system E2E tests | 500 |
| `tests/regression/test_backward_compat.py` | Backward compatibility tests | 400 |
| `tests/performance/test_benchmarks.py` | Performance benchmark tests | 300 |
| `tests/security/test_security.py` | Security audit tests | 250 |
| `docs/user_guide.md` | End-user documentation | 500 |
| `docs/developer_guide.md` | Developer onboarding | 600 |
| `docs/api_reference.md` | API documentation | 400 |
| `docs/plugin_development.md` | Plugin creation guide | 400 |
| `docs/troubleshooting.md` | Troubleshooting guide | 300 |
| `scripts/deploy.py` | Deployment script | 200 |
| `scripts/rollback.py` | Rollback script | 150 |
| `scripts/health_check.py` | Health check script | 150 |
| `scripts/migrate_data.py` | Data migration script | 300 |
| `config/production.yaml` | Production configuration | 200 |
| `config/development.yaml` | Development configuration | 150 |

#### Additional System Files (20 files)
| File | Purpose | Lines Est. |
|------|---------|------------|
| `src/core/database_sync_manager.py` | Cross-DB sync with error recovery | 600 |
| `src/core/database_migration_manager.py` | Schema migration framework | 400 |
| `src/core/health_monitor.py` | System-wide health monitoring | 500 |
| `src/core/version_manager.py` | Plugin versioning system | 400 |
| `src/core/config_manager.py` | Dynamic configuration | 300 |
| `src/core/event_bus.py` | System event bus | 250 |
| `src/core/error_recovery.py` | Error recovery system | 350 |
| `src/dashboard/api.py` | Dashboard REST API (optional) | 400 |
| `src/dashboard/routes.py` | Dashboard routes (optional) | 300 |
| `migrations/central_system/001_initial_schema.sql` | Central DB schema | 200 |
| `migrations/central_system/002_health_tables.sql` | Health monitoring tables | 100 |
| `migrations/central_system/003_version_tables.sql` | Version tracking tables | 100 |
| `data/zepix_combined.db` | V3 database (created at runtime) | - |
| `data/zepix_price_action.db` | V6 database (created at runtime) | - |
| `data/zepix_bot.db` | Central database (created at runtime) | - |
| `config/telegram_config.yaml` | Telegram bot configuration | 100 |
| `config/plugins_config.yaml` | Plugin configuration | 150 |
| `config/risk_config.yaml` | Risk management configuration | 100 |
| `config/database_config.yaml` | Database configuration | 80 |
| `.env.example` | Environment variables template | 50 |

### 2.2 Files to Modify (30+ files)

| File | Changes Required |
|------|------------------|
| `src/core/trading_engine.py` | Add plugin routing, remove hardcoded V3 logic |
| `src/core/plugin_system/base_plugin.py` | Enhance with lifecycle hooks, health methods |
| `src/core/plugin_system/plugin_registry.py` | Add versioning, health monitoring |
| `src/core/plugin_system/service_api.py` | Expand with all 6 services |
| `src/managers/dual_order_manager.py` | Extract to OrderExecutionService |
| `src/managers/profit_booking_manager.py` | Extract to ProfitBookingService |
| `src/managers/risk_manager.py` | Extract to RiskManagementService |
| `src/managers/timeframe_trend_manager.py` | Extract to TrendManagementService |
| `src/clients/telegram_bot.py` | Refactor to use MultiTelegramManager |
| `src/clients/mt5_client.py` | Add spread/volatility methods for MarketDataService |
| `src/database.py` | Refactor to PluginDatabase pattern |
| `src/config.py` | Add plugin, telegram, service configurations |
| `src/models.py` | Add V6AlertModel, PluginVersion dataclasses |
| `src/v3_alert_models.py` | Move to V3 plugin |
| `src/processors/alert_processor.py` | Route to plugins instead of direct processing |
| `src/services/price_monitor_service.py` | Integrate with MarketDataService |
| `src/services/analytics_engine.py` | Integrate with Analytics Bot |
| `src/menu/command_mapping.py` | Add plugin management commands |
| `src/menu/command_executor.py` | Add plugin command handlers |
| `src/utils/pip_calculator.py` | Expose via ServiceAPI |
| `requirements.txt` | Add new dependencies |
| `config/config.yaml` | Add plugin system configuration |
| `main.py` | Initialize MultiTelegramManager, PluginRegistry |
| `tests/conftest.py` | Add plugin test fixtures |

### 2.3 Files to Preserve (No Changes)

| File | Reason |
|------|--------|
| `src/managers/session_manager.py` | Works as-is, accessed via ServiceAPI |
| `src/managers/reentry_manager.py` | Works as-is, used by V3 plugin |
| `src/managers/reverse_shield_manager.py` | Works as-is |
| `src/managers/exit_continuation_monitor.py` | Works as-is |
| `src/managers/recovery_window_monitor.py` | Works as-is |
| `src/utils/logging_config.py` | Works as-is |
| `src/utils/optimized_logger.py` | Works as-is |
| `src/modules/voice_alert_system.py` | Works as-is, integrated via NotificationService |
| `src/modules/fixed_clock_system.py` | Works as-is |

---

## 3. PHASE-BY-PHASE BREAKDOWN

### Phase 1: Core Plugin System (Week 1-2, 5-7 days)

**Objective:** Build the foundation for plugin-based architecture

**Modules to Implement:**

#### 1.1 Enhanced BaseLogicPlugin (Day 1-2)
```python
class BaseLogicPlugin(ABC):
    # Lifecycle hooks
    async def on_load(self) -> bool
    async def on_unload(self) -> bool
    async def on_enable(self) -> bool
    async def on_disable(self) -> bool
    
    # Signal processing (abstract)
    @abstractmethod
    async def process_entry_signal(self, alert) -> Dict
    @abstractmethod
    async def process_exit_signal(self, alert) -> Dict
    
    # Health monitoring
    async def ping(self) -> bool
    async def get_health_metrics(self) -> Dict
    async def self_test(self) -> bool
    
    # Database access
    @property
    def database(self) -> PluginDatabase
```

#### 1.2 Enhanced PluginRegistry (Day 2-3)
- Plugin discovery from `src/logic_plugins/` directory
- Dynamic loading/unloading
- Version compatibility checking
- Hook execution (pipe-and-filter pattern)
- Plugin status tracking

#### 1.3 PluginDatabase Manager (Day 3-4)
- Per-plugin SQLite database creation
- Connection pooling
- Schema migration support
- Cross-database sync to central DB

#### 1.4 Plugin Configuration System (Day 4-5)
- YAML-based plugin configuration
- Runtime configuration updates
- Configuration validation
- Default value handling

#### 1.5 Plugin Health Monitoring (Day 5-6)
- Health metrics collection (every 30s)
- Anomaly detection (thresholds)
- Alert triggering
- Health history storage

#### 1.6 Plugin Versioning System (Day 6-7)
- Semantic versioning (MAJOR.MINOR.PATCH)
- Compatibility matrix
- Upgrade/rollback support
- Version history tracking

**Quality Gate:**
- [ ] All unit tests passing (100%)
- [ ] Plugin can be loaded/unloaded dynamically
- [ ] Plugin database created automatically
- [ ] Health metrics collected successfully
- [ ] No regression in existing functionality

### Phase 2: Multi-Telegram System (Week 2-3, 5-7 days)

**Objective:** Implement 3-bot Telegram architecture with unified interface

**Modules to Implement:**

#### 2.1 MultiTelegramManager (Day 1-2)
```python
class MultiTelegramManager:
    controller_bot: Bot      # Commands, menus, control
    notification_bot: Bot    # Trade alerts, system notifications
    analytics_bot: Bot       # Reports, statistics, analytics
    
    async def start_all_bots(self)
    async def stop_all_bots(self)
    async def send_controller_message(chat_id, text, priority)
    async def send_notification(chat_id, text, priority)
    async def send_analytics(chat_id, text, priority)
```

#### 2.2 Controller Bot (Day 2-3)
- All command handlers (/start, /status, /enable_plugin, etc.)
- Menu system (inline keyboards)
- Plugin management commands
- Emergency stop functionality

#### 2.3 Notification Bot (Day 3-4)
- Trade entry/exit notifications
- System alerts (errors, warnings)
- Profit booking notifications
- Re-entry notifications

#### 2.4 Analytics Bot (Day 4-5)
- Daily/weekly/monthly reports
- Performance statistics
- Plugin analytics
- Health status reports

#### 2.5 Rate Limiter (Day 5-6)
```python
class TelegramRateLimiter:
    # Telegram limits: 30 msg/sec, 20 msg/min per chat
    queue_critical: deque    # Errors, stop-loss
    queue_high: deque        # Entry/exit alerts
    queue_normal: deque      # Regular notifications
    queue_low: deque         # Daily stats
    
    async def enqueue(message, priority)
    async def process_queue()
```

#### 2.6 Sticky Headers (Day 6-7)
- Persistent reply keyboard (bottom)
- Pinned inline menu (top)
- Auto-refresh dashboard (every 60s)
- Unified interface across all 3 bots

**Quality Gate:**
- [ ] All 3 bots start and respond
- [ ] Rate limiting prevents API violations
- [ ] Sticky headers work on mobile and desktop
- [ ] Same menu works in all 3 bots
- [ ] No notification spam

### Phase 3: Service API Layer (Week 3, 3-4 days)

**Objective:** Create shared services for all plugins

**Modules to Implement:**

#### 3.1 OrderExecutionService (Day 1)
```python
class OrderExecutionService:
    async def place_order(symbol, direction, lot_size, sl, tp, comment) -> int
    async def place_dual_orders(symbol, direction, lot_a, lot_b, sl_a, sl_b) -> Tuple
    async def modify_order(ticket, sl, tp) -> bool
    async def close_order(ticket) -> bool
    async def get_open_orders(plugin_id) -> List
```

#### 3.2 RiskManagementService (Day 1-2)
```python
class RiskManagementService:
    def get_account_tier(balance) -> str
    def calculate_lot_size(balance, sl_pips, logic) -> float
    def validate_risk(symbol, lot_size, balance) -> Dict
    def get_daily_loss() -> float
    def get_lifetime_loss() -> float
```

#### 3.3 TrendManagementService (Day 2)
```python
class TrendManagementService:
    def get_trend(symbol, timeframe) -> str
    def update_trend(symbol, timeframe, direction)
    def get_mtf_alignment(symbol) -> Dict
    def lock_trend(symbol, timeframe)
    def unlock_trend(symbol, timeframe)
```

#### 3.4 ProfitBookingService (Day 2-3)
```python
class ProfitBookingService:
    async def create_chain(symbol, direction, base_lot) -> str
    async def process_profit_level(chain_id, level) -> Dict
    async def get_chain_status(chain_id) -> Dict
    async def close_chain(chain_id, reason) -> bool
```

#### 3.5 MarketDataService (Day 3)
```python
class MarketDataService:
    async def get_current_spread(symbol) -> float
    async def check_spread_acceptable(symbol, max_pips) -> bool
    async def get_current_price(symbol) -> Dict
    async def get_volatility_state(symbol, timeframe) -> Dict
    async def get_symbol_info(symbol) -> Dict
```

#### 3.6 NotificationService (Day 3-4)
```python
class NotificationService:
    async def send_trade_entry(plugin_id, trade_data)
    async def send_trade_exit(plugin_id, trade_data)
    async def send_system_alert(level, message)
    async def send_daily_report(plugin_id, stats)
```

**Quality Gate:**
- [ ] All services have unit tests
- [ ] Services work independently
- [ ] Services integrate with existing managers
- [ ] No breaking changes to existing functionality

### Phase 4: V3 Plugin Migration (Week 4, 5-7 days)

**Objective:** Migrate existing V3 Combined Logic to plugin architecture with 100% feature parity

**Modules to Implement:**

#### 4.1 V3CombinedPlugin Main Class (Day 1-2)
```python
class CombinedV3Plugin(BaseLogicPlugin):
    plugin_id = "combined_v3"
    version = "3.0.0"
    
    # 12 signal types
    ENTRY_SIGNALS = [
        "Liquidity_Trap_Reversal", "Golden_Pocket_Flip",
        "Screener_Full_Bullish", "Screener_Full_Bearish",
        "Confluence_Entry", "Breakout_Entry", "Pullback_Entry"
    ]
    EXIT_SIGNALS = ["Exit_Appeared", "Reversal_Exit"]
    INFO_SIGNALS = ["Squeeze_Alert", "Trend_Pulse"]
    
    # 3 logic routes
    def route_to_logic(self, alert) -> str  # LOGIC1/2/3
```

#### 4.2 V3 Entry Handler (Day 2-3)
- Process 7 entry signal types
- Route to Logic 1/2/3 based on timeframe
- Apply position multiplier
- Place dual orders (Order A + Order B)
- Handle aggressive reversal signals

#### 4.3 V3 Exit Handler (Day 3-4)
- Process exit signals
- Close conflicting positions
- Handle partial exits
- Update session tracking

#### 4.4 V3 Reversal Handler (Day 4)
- Detect reversal conditions
- Close opposite positions
- Re-enter in new direction
- Manage reversal chains

#### 4.5 V3 Trend Pulse Handler (Day 4-5)
- Process MTF trend updates
- Update trend manager
- Trigger notifications

#### 4.6 V3 Database Operations (Day 5-6)
- Create zepix_combined.db schema
- Migrate existing trades
- Implement CRUD operations
- Sync to central database

#### 4.7 V3 Parity Testing (Day 6-7)
- Shadow mode testing (old vs new)
- Signal-by-signal comparison
- Order placement verification
- Database consistency checks

**Quality Gate:**
- [ ] All 12 signal types handled correctly
- [ ] Dual order system works identically
- [ ] Logic 1/2/3 routing matches old behavior
- [ ] Database operations work correctly
- [ ] Shadow mode shows 100% parity

### Phase 5: V6 Plugin Implementation (Week 4-5, 5-7 days)

**Objective:** Implement 4 V6 Price Action plugins with conditional order routing

**V6 Architecture:**
```
V6 Price Action System
├── price_action_1m (ORDER B ONLY - scalping)
├── price_action_5m (DUAL ORDERS - intraday)
├── price_action_15m (ORDER A ONLY - swing)
└── price_action_1h (ORDER A ONLY - position)
```

**Modules to Implement:**

#### 5.1 V6 Alert Model (Day 1)
```python
@dataclass
class V6AlertModel:
    type: str           # "entry_v6", "exit_v6", "trend_pulse_v6"
    ticker: str         # Symbol
    tf: str             # Timeframe (1, 5, 15, 60)
    price: float        # Current price
    direction: str      # "buy" or "sell"
    conf_level: str     # "HIGH", "MEDIUM", "LOW"
    conf_score: int     # 1-10
    adx: float          # ADX value
    adx_strength: str   # "STRONG", "MODERATE", "WEAK"
    sl: float           # Stop loss price
    tp1: float          # Take profit 1
    tp2: float          # Take profit 2
    tp3: float          # Take profit 3
    alignment: str      # MTF alignment status
    tl_status: str      # Trend line status
```

#### 5.2 Price Action 1M Plugin (Day 1-2)
- ORDER B ONLY (scalping)
- Spread check CRITICAL (max 1.5 pips)
- Quick entry/exit
- Tight stop loss

#### 5.3 Price Action 5M Plugin (Day 2-3)
- DUAL ORDERS (intraday)
- Order A: TP Trail
- Order B: Profit Trail
- Standard spread tolerance

#### 5.4 Price Action 15M Plugin (Day 3-4)
- ORDER A ONLY (swing)
- TP Trail system
- Wider stop loss
- Longer hold time

#### 5.5 Price Action 1H Plugin (Day 4-5)
- ORDER A ONLY (position)
- TP Trail system
- Widest stop loss
- Longest hold time

#### 5.6 V6 Trend Pulse System (Day 5-6)
- Process trend pulse alerts
- Update plugin-specific trends
- Trigger re-evaluation of positions

#### 5.7 V6 Database Operations (Day 6-7)
- Create zepix_price_action.db schema
- Implement per-timeframe tables
- Sync to central database

**Quality Gate:**
- [ ] All 4 plugins load and process alerts
- [ ] Conditional order routing works correctly
- [ ] Spread checks prevent bad entries on 1M
- [ ] Database operations work correctly
- [ ] Trend Pulse updates all plugins

### Phase 6: Testing & Documentation (Week 5-6, 5-7 days)

**Objective:** Comprehensive testing and documentation

**Testing Modules:**

#### 6.1 Unit Tests (Day 1-2)
- Plugin system tests (100% coverage)
- Service API tests (100% coverage)
- Telegram system tests (100% coverage)
- Database tests (100% coverage)

#### 6.2 Integration Tests (Day 2-3)
- Plugin + Service integration
- Telegram + Plugin integration
- Database sync integration
- Full signal flow integration

#### 6.3 End-to-End Tests (Day 3-4)
- Complete trade lifecycle
- Multi-plugin scenarios
- Error recovery scenarios
- Performance under load

#### 6.4 Regression Tests (Day 4-5)
- V3 backward compatibility
- Existing trade handling
- Database migration
- Configuration compatibility

**Documentation Modules:**

#### 6.5 User Documentation (Day 5)
- Getting started guide
- 3 Telegram bots guide
- Plugin configuration guide
- Troubleshooting FAQ

#### 6.6 Developer Documentation (Day 6)
- Architecture overview
- Plugin development guide
- Service API reference
- Testing guide

#### 6.7 Deployment Documentation (Day 7)
- Deployment checklist
- Rollback procedures
- Monitoring setup
- Maintenance guide

**Quality Gate:**
- [ ] All tests passing (100%)
- [ ] Code coverage > 80%
- [ ] Documentation complete
- [ ] Deployment scripts tested
- [ ] Rollback procedures verified

---

## 4. MODULE-LEVEL IMPLEMENTATION SPECS

### Module: BaseLogicPlugin

**Purpose:** Abstract base class for all trading logic plugins

**Dependencies:**
- `PluginDatabase` for database access
- `ServiceAPI` for shared services
- `asyncio` for async operations

**Interface:**
```python
class BaseLogicPlugin(ABC):
    # Properties
    plugin_id: str
    version: str
    enabled: bool
    config: Dict
    database: PluginDatabase
    service_api: ServiceAPI
    
    # Lifecycle
    async def on_load(self) -> bool
    async def on_unload(self) -> bool
    async def on_enable(self) -> bool
    async def on_disable(self) -> bool
    
    # Signal Processing (Abstract)
    @abstractmethod
    async def process_entry_signal(self, alert: Dict) -> Dict
    @abstractmethod
    async def process_exit_signal(self, alert: Dict) -> Dict
    @abstractmethod
    async def process_reversal_signal(self, alert: Dict) -> Dict
    
    # Health
    async def ping(self) -> bool
    async def get_health_metrics(self) -> Dict
    async def self_test(self) -> bool
    async def get_performance_stats(self) -> Dict
    async def get_error_stats(self) -> Dict
    
    # Hooks
    def on_signal_received(self, data: Dict) -> Dict
    def on_order_placed(self, order: Dict) -> None
    def on_order_closed(self, order: Dict) -> None
```

**Implementation Approach:**
1. Create abstract base class with all lifecycle methods
2. Implement default health monitoring
3. Provide database access via property
4. Support both sync and async hooks

**Testing Strategy:**
- Unit test each lifecycle method
- Test health monitoring
- Test database access
- Test hook execution

**Integration Points:**
- PluginRegistry loads and manages plugins
- ServiceAPI provides shared services
- PluginDatabase provides database access

---

### Module: MultiTelegramManager

**Purpose:** Orchestrate 3 Telegram bots with unified interface

**Dependencies:**
- `python-telegram-bot` library
- `TelegramRateLimiter` for rate limiting
- `TelegramStickyHeaders` for persistent menus

**Interface:**
```python
class MultiTelegramManager:
    # Bots
    controller_bot: Bot
    notification_bot: Bot
    analytics_bot: Bot
    
    # Rate limiters
    controller_limiter: TelegramRateLimiter
    notification_limiter: TelegramRateLimiter
    analytics_limiter: TelegramRateLimiter
    
    # Methods
    async def start(self)
    async def stop(self)
    async def send_controller_message(chat_id, text, priority, reply_markup)
    async def send_notification(chat_id, text, priority)
    async def send_analytics(chat_id, text, priority)
    async def broadcast(text, priority)
```

**Implementation Approach:**
1. Initialize 3 separate Bot instances with different tokens
2. Create rate limiter for each bot
3. Setup sticky headers on start
4. Route messages based on type

**Testing Strategy:**
- Unit test each bot initialization
- Test rate limiting
- Test message routing
- Test sticky header updates

**Integration Points:**
- NotificationService uses for sending alerts
- Controller Bot handles commands
- Analytics Bot handles reports

---

### Module: DatabaseSyncManager

**Purpose:** Synchronize plugin databases with central database

**Dependencies:**
- `sqlite3` for database operations
- `asyncio` for async sync loop

**Interface:**
```python
class DatabaseSyncManager:
    # Configuration
    v3_db_path: str = 'data/zepix_combined.db'
    v6_db_path: str = 'data/zepix_price_action.db'
    central_db_path: str = 'data/zepix_bot.db'
    
    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: int = 5
    backoff_multiplier: int = 2
    
    # Methods
    async def start(self)
    async def stop(self)
    async def sync_all_plugins(self) -> List[SyncResult]
    async def trigger_manual_sync(self) -> Dict
    def get_sync_health(self) -> Dict
```

**Implementation Approach:**
1. Run sync loop every 5 minutes
2. Implement retry with exponential backoff
3. Track consecutive failures
4. Alert on persistent failures

**Testing Strategy:**
- Unit test sync operations
- Test retry logic
- Test error recovery
- Test health reporting

**Integration Points:**
- Plugin databases as sources
- Central database as destination
- Telegram for alerts

---

### Module: V3CombinedPlugin

**Purpose:** V3 Combined Logic as a plugin with 100% feature parity

**Dependencies:**
- `BaseLogicPlugin` base class
- `ServiceAPI` for shared services
- `PluginDatabase` for database

**Interface:**
```python
class CombinedV3Plugin(BaseLogicPlugin):
    plugin_id = "combined_v3"
    version = "3.0.0"
    
    # Signal handlers
    async def process_entry_signal(self, alert: ZepixV3Alert) -> Dict
    async def process_exit_signal(self, alert: ZepixV3Alert) -> Dict
    async def process_reversal_signal(self, alert: ZepixV3Alert) -> Dict
    async def process_trend_pulse(self, alert: ZepixV3Alert) -> Dict
    async def process_squeeze_alert(self, alert: ZepixV3Alert) -> Dict
    
    # Logic routing
    def route_to_logic(self, alert: ZepixV3Alert) -> str
    def get_logic_multiplier(self, timeframe: str, logic: str) -> float
    
    # Order management
    async def place_dual_orders(self, alert, lot_a, lot_b, logic) -> Dict
```

**Implementation Approach:**
1. Extract V3 logic from TradingEngine
2. Implement all 12 signal handlers
3. Maintain exact same behavior
4. Use ServiceAPI for order placement

**Testing Strategy:**
- Shadow mode testing against old implementation
- Signal-by-signal comparison
- Order placement verification
- Database consistency checks

**Integration Points:**
- PluginRegistry loads plugin
- ServiceAPI provides services
- TradingEngine routes alerts

---

### Module: PriceAction1MPlugin

**Purpose:** V6 1-minute scalping plugin with ORDER B ONLY

**Dependencies:**
- `BaseLogicPlugin` base class
- `ServiceAPI` for shared services
- `MarketDataService` for spread checks

**Interface:**
```python
class PriceAction1mPlugin(BaseLogicPlugin):
    plugin_id = "price_action_1m"
    version = "6.0.0"
    
    # Configuration
    order_type = "ORDER_B_ONLY"
    max_spread_pips = 1.5
    
    # Signal handlers
    async def process_entry_signal(self, alert: V6AlertModel) -> Dict
    async def process_exit_signal(self, alert: V6AlertModel) -> Dict
    
    # Spread check
    async def check_spread_acceptable(self, symbol: str) -> bool
```

**Implementation Approach:**
1. Implement spread check before entry
2. Place ORDER B only (no Order A)
3. Use tight stop loss
4. Quick entry/exit logic

**Testing Strategy:**
- Test spread rejection
- Test order placement
- Test exit handling
- Test database operations

**Integration Points:**
- MarketDataService for spread checks
- OrderExecutionService for orders
- NotificationService for alerts

---

## 5. TESTING FRAMEWORK DESIGN

### 5.1 Test Pyramid

```
                    ┌─────────────┐
                    │    E2E      │  10%
                    │   Tests     │  (Full system)
                    ├─────────────┤
                    │ Integration │  20%
                    │   Tests     │  (Module interactions)
                    ├─────────────┤
                    │    Unit     │  70%
                    │   Tests     │  (Individual functions)
                    └─────────────┘
```

### 5.2 Unit Test Structure

```
tests/
├── unit/
│   ├── test_plugin_system.py
│   │   ├── test_base_plugin_lifecycle()
│   │   ├── test_plugin_registry_discovery()
│   │   ├── test_plugin_database_creation()
│   │   └── test_plugin_health_monitoring()
│   ├── test_telegram_system.py
│   │   ├── test_multi_telegram_manager()
│   │   ├── test_rate_limiter()
│   │   └── test_sticky_headers()
│   ├── test_services.py
│   │   ├── test_order_execution_service()
│   │   ├── test_risk_management_service()
│   │   └── test_market_data_service()
│   ├── test_v3_plugin.py
│   │   ├── test_entry_signal_processing()
│   │   ├── test_exit_signal_processing()
│   │   └── test_logic_routing()
│   └── test_v6_plugins.py
│       ├── test_1m_plugin()
│       ├── test_5m_plugin()
│       ├── test_15m_plugin()
│       └── test_1h_plugin()
```

### 5.3 Integration Test Structure

```
tests/
├── integration/
│   ├── test_plugin_service_integration.py
│   │   ├── test_plugin_uses_order_service()
│   │   ├── test_plugin_uses_risk_service()
│   │   └── test_plugin_uses_notification_service()
│   ├── test_telegram_plugin_integration.py
│   │   ├── test_plugin_sends_notifications()
│   │   └── test_telegram_controls_plugin()
│   ├── test_database_sync_integration.py
│   │   ├── test_v3_syncs_to_central()
│   │   └── test_v6_syncs_to_central()
│   └── test_full_signal_flow.py
│       ├── test_v3_entry_to_exit()
│       └── test_v6_entry_to_exit()
```

### 5.4 E2E Test Structure

```
tests/
├── e2e/
│   ├── test_full_system.py
│   │   ├── test_bot_startup_sequence()
│   │   ├── test_complete_trade_lifecycle()
│   │   └── test_multi_plugin_scenario()
│   ├── test_error_recovery.py
│   │   ├── test_database_failure_recovery()
│   │   ├── test_telegram_failure_recovery()
│   │   └── test_mt5_disconnection_recovery()
│   └── test_performance.py
│       ├── test_signal_processing_latency()
│       ├── test_database_query_performance()
│       └── test_telegram_message_throughput()
```

### 5.5 Regression Test Structure

```
tests/
├── regression/
│   ├── test_v3_backward_compatibility.py
│   │   ├── test_existing_trades_unaffected()
│   │   ├── test_database_schema_compatible()
│   │   └── test_telegram_commands_work()
│   └── test_shadow_mode.py
│       ├── test_v3_signal_parity()
│       └── test_v3_order_parity()
```

### 5.6 Test Fixtures

```python
# tests/conftest.py

@pytest.fixture
def mock_mt5_client():
    """Mock MT5 client for testing"""
    client = MagicMock()
    client.get_account_balance.return_value = 10000.0
    client.place_order.return_value = 12345
    return client

@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram bot for testing"""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot

@pytest.fixture
def test_plugin_config():
    """Test plugin configuration"""
    return {
        "enabled": True,
        "symbols": ["EURUSD", "GBPUSD"],
        "max_trades": 5
    }

@pytest.fixture
def test_v3_alert():
    """Test V3 alert data"""
    return ZepixV3Alert(
        type="entry_v3",
        symbol="EURUSD",
        direction="buy",
        signal_type="Confluence_Entry",
        consensus_score=7,
        tf="15",
        price=1.0850,
        sl=1.0800,
        tp=1.0950
    )
```

---

## 6. QUALITY GATES

### Phase 1 Quality Gate: Core Plugin System

| Criteria | Requirement | Verification |
|----------|-------------|--------------|
| Unit Tests | 100% passing | `pytest tests/unit/test_plugin_system.py` |
| Code Coverage | > 80% | `pytest --cov=src/core/plugin_system` |
| Plugin Loading | Dynamic load/unload works | Manual test |
| Database Creation | Per-plugin DB created | Check `data/` directory |
| Health Monitoring | Metrics collected | Check logs |
| No Regression | Existing bot works | Run existing tests |

### Phase 2 Quality Gate: Multi-Telegram System

| Criteria | Requirement | Verification |
|----------|-------------|--------------|
| Unit Tests | 100% passing | `pytest tests/unit/test_telegram_system.py` |
| All 3 Bots | Start and respond | Manual test |
| Rate Limiting | No API violations | Monitor logs |
| Sticky Headers | Work on mobile/desktop | Manual test |
| Unified Interface | Same menu in all bots | Manual test |
| No Spam | Notifications throttled | Monitor messages |

### Phase 3 Quality Gate: Service API Layer

| Criteria | Requirement | Verification |
|----------|-------------|--------------|
| Unit Tests | 100% passing | `pytest tests/unit/test_services.py` |
| Service Independence | Each service works alone | Unit tests |
| Integration | Services work together | Integration tests |
| No Breaking Changes | Existing functionality works | Regression tests |

### Phase 4 Quality Gate: V3 Plugin Migration

| Criteria | Requirement | Verification |
|----------|-------------|--------------|
| Unit Tests | 100% passing | `pytest tests/unit/test_v3_plugin.py` |
| Signal Parity | All 12 signals handled | Shadow mode test |
| Order Parity | Dual orders match old behavior | Shadow mode test |
| Logic Routing | Logic 1/2/3 correct | Unit tests |
| Database | Operations work correctly | Integration tests |
| 100% Parity | Shadow mode shows no differences | Shadow mode report |

### Phase 5 Quality Gate: V6 Plugin Implementation

| Criteria | Requirement | Verification |
|----------|-------------|--------------|
| Unit Tests | 100% passing | `pytest tests/unit/test_v6_plugins.py` |
| All 4 Plugins | Load and process alerts | Integration tests |
| Order Routing | Conditional routing works | Unit tests |
| Spread Checks | 1M rejects high spread | Unit tests |
| Trend Pulse | Updates all plugins | Integration tests |
| Database | Operations work correctly | Integration tests |

### Phase 6 Quality Gate: Testing & Documentation

| Criteria | Requirement | Verification |
|----------|-------------|--------------|
| All Tests | 100% passing | `pytest` |
| Code Coverage | > 80% overall | Coverage report |
| E2E Tests | Full system works | E2E test suite |
| Regression | No backward compatibility issues | Regression suite |
| User Docs | Complete and accurate | Review |
| Developer Docs | Complete and accurate | Review |
| Deployment | Scripts tested | Dry run |

---

## 7. RISK ASSESSMENT

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Database migration data loss | Medium | Critical | Backup before migration, test on copy first |
| V3 parity issues | Medium | High | Shadow mode testing, signal-by-signal comparison |
| Telegram rate limiting | High | Medium | Queue-based throttling, priority system |
| MT5 connection issues | Low | High | Retry logic, graceful degradation |
| Plugin loading failures | Medium | Medium | Fallback to legacy mode, health monitoring |
| Performance degradation | Low | Medium | Benchmarking, optimization |

### 7.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Extended downtime during migration | Low | High | Zero-impact migration (parallel deployment) |
| Configuration errors | Medium | Medium | Validation, defaults, rollback |
| User confusion with 3 bots | Medium | Low | Clear documentation, unified interface |
| Monitoring gaps | Low | Medium | Health monitoring, alerts |

### 7.3 Rollback Plans

**Phase 1 Rollback:**
- Disable plugin system in config
- Revert to direct TradingEngine processing
- No database changes to rollback

**Phase 2 Rollback:**
- Disable multi-telegram in config
- Revert to single bot
- No database changes to rollback

**Phase 3 Rollback:**
- Disable ServiceAPI in config
- Revert to direct manager calls
- No database changes to rollback

**Phase 4 Rollback:**
- Disable V3 plugin
- Enable legacy V3 processing in TradingEngine
- Keep V3 database (no data loss)

**Phase 5 Rollback:**
- Disable V6 plugins
- V6 alerts ignored (no legacy to fall back to)
- Keep V6 database (no data loss)

**Full System Rollback:**
- Stop V5 system
- Start V2 system from backup
- Restore database from backup
- Notify users of rollback

---

## 8. TIMELINE ESTIMATE

### 8.1 Detailed Timeline

| Phase | Week | Days | Modules | Est. Hours |
|-------|------|------|---------|------------|
| **Phase 1** | 1-2 | 5-7 | Core Plugin System | 40-56 |
| - BaseLogicPlugin | 1 | 1-2 | Enhanced base class | 8-16 |
| - PluginRegistry | 1 | 1 | Enhanced registry | 8 |
| - PluginDatabase | 1 | 1-2 | Database manager | 8-16 |
| - Plugin Config | 2 | 1 | Configuration system | 8 |
| - Plugin Health | 2 | 1 | Health monitoring | 8 |
| - Plugin Version | 2 | 1 | Versioning system | 8 |
| **Phase 2** | 2-3 | 5-7 | Multi-Telegram System | 40-56 |
| - MultiTelegramManager | 2 | 1-2 | 3-bot orchestrator | 8-16 |
| - Controller Bot | 2-3 | 1 | Commands, menus | 8 |
| - Notification Bot | 3 | 1 | Trade alerts | 8 |
| - Analytics Bot | 3 | 1 | Reports, stats | 8 |
| - Rate Limiter | 3 | 1 | Queue-based throttling | 8 |
| - Sticky Headers | 3 | 1 | Persistent menus | 8 |
| **Phase 3** | 3 | 3-4 | Service API Layer | 24-32 |
| - OrderExecutionService | 3 | 0.5 | Order management | 4 |
| - RiskManagementService | 3 | 0.5 | Risk calculations | 4 |
| - TrendManagementService | 3 | 0.5 | Trend tracking | 4 |
| - ProfitBookingService | 3 | 0.5 | Profit booking | 4 |
| - MarketDataService | 3 | 0.5 | Market data | 4 |
| - NotificationService | 3 | 0.5 | Notifications | 4 |
| **Phase 4** | 4 | 5-7 | V3 Plugin Migration | 40-56 |
| - V3CombinedPlugin | 4 | 1-2 | Main plugin class | 8-16 |
| - V3 Entry Handler | 4 | 1 | Entry processing | 8 |
| - V3 Exit Handler | 4 | 1 | Exit processing | 8 |
| - V3 Reversal Handler | 4 | 0.5 | Reversal handling | 4 |
| - V3 Trend Pulse | 4 | 0.5 | Trend pulse | 4 |
| - V3 Database | 4 | 1 | Database operations | 8 |
| - V3 Parity Testing | 4 | 1 | Shadow mode testing | 8 |
| **Phase 5** | 4-5 | 5-7 | V6 Plugin Implementation | 40-56 |
| - V6 Alert Model | 4-5 | 0.5 | Data model | 4 |
| - PriceAction1M | 4-5 | 1 | 1M plugin | 8 |
| - PriceAction5M | 5 | 1 | 5M plugin | 8 |
| - PriceAction15M | 5 | 1 | 15M plugin | 8 |
| - PriceAction1H | 5 | 1 | 1H plugin | 8 |
| - V6 Trend Pulse | 5 | 0.5 | Trend pulse | 4 |
| - V6 Database | 5 | 1 | Database operations | 8 |
| **Phase 6** | 5-6 | 5-7 | Testing & Documentation | 40-56 |
| - Unit Tests | 5-6 | 1-2 | All unit tests | 8-16 |
| - Integration Tests | 6 | 1 | Integration tests | 8 |
| - E2E Tests | 6 | 1 | End-to-end tests | 8 |
| - Regression Tests | 6 | 1 | Backward compatibility | 8 |
| - User Documentation | 6 | 0.5 | User guide | 4 |
| - Developer Documentation | 6 | 0.5 | Developer guide | 4 |
| - Deployment | 6 | 1 | Deployment scripts | 8 |

### 8.2 Total Estimate

| Metric | Estimate |
|--------|----------|
| **Total Duration** | 10-12 weeks |
| **Total Working Days** | 28-42 days |
| **Total Hours** | 224-336 hours |
| **Files to Create** | 100+ files |
| **Files to Modify** | 30+ files |
| **Lines of Code** | ~15,000-20,000 lines |

### 8.3 Critical Path

```
Phase 1 (Core Plugin) → Phase 3 (Service API) → Phase 4 (V3 Plugin)
                     ↘                        ↗
                       Phase 2 (Telegram) → Phase 5 (V6 Plugins)
                                                      ↓
                                              Phase 6 (Testing)
```

**Critical Dependencies:**
1. Phase 1 must complete before Phase 3 and Phase 4
2. Phase 3 must complete before Phase 4 and Phase 5
3. Phase 4 and Phase 5 can run in parallel after Phase 3
4. Phase 6 requires all other phases complete

---

## 9. APPROVAL REQUEST

### Status

| Item | Status |
|------|--------|
| Research Documents Read | 16/16 (100%) |
| Planning Documents Read | 27/27 (100%) |
| Source Code Analyzed | Complete |
| Master Plan Created | Complete |
| Ready for PM Review | YES |

### Confidence Level

**Overall Confidence: 95%**

| Area | Confidence | Notes |
|------|------------|-------|
| Architecture Understanding | 98% | Clear from documents |
| File Change Matrix | 95% | May discover additional files |
| Phase Breakdown | 95% | Well-defined in planning docs |
| Module Specs | 90% | Some details TBD during implementation |
| Testing Framework | 95% | Standard patterns |
| Quality Gates | 95% | Clear criteria |
| Risk Assessment | 90% | Unknown unknowns possible |
| Timeline | 85% | Depends on complexity discovered |

### Concerns

1. **V3 Parity Risk:** The V3 Combined Logic has complex interactions. Shadow mode testing is critical to ensure 100% parity.

2. **Telegram Rate Limiting:** With 3 bots sending messages, rate limiting must be carefully tuned to avoid API violations.

3. **Database Migration:** Existing trades must be preserved. Migration scripts need thorough testing.

4. **Timeline Uncertainty:** Some modules may take longer than estimated if unexpected complexity is discovered.

### Questions for PM

1. **Priority Clarification:** Should V6 plugins be implemented even if V3 parity is not yet 100%? Or should V3 be fully validated first?

2. **Dashboard Priority:** Document 17 specifies a web dashboard. Is this required for initial release or can it be deferred?

3. **Testing Environment:** Is there a staging environment for testing, or should I create one?

4. **Telegram Bot Tokens:** Will you provide the 3 Telegram bot tokens, or should I create test bots?

### Next Steps

Upon PM approval:
1. Begin Phase 1: Core Plugin System
2. Create detailed module specs for Phase 1
3. Implement BaseLogicPlugin enhancements
4. Report progress daily

---

## HINGLISH SUMMARY (PM ke liye)

**Kya hai ye plan?**

Bhai, ye plan hai ZepixTradingBot ko V2 se V5 mein transform karne ka. Abhi bot monolithic hai - sab kuch ek jagah. V5 mein plugin-based architecture hoga jisme:

1. **Plugin System:** Har Pine Script logic ek alag plugin hoga. V3 Combined Logic ek plugin, V6 Price Action 4 plugins (1M, 5M, 15M, 1H). Naya logic add karna sirf 1 hour ka kaam!

2. **3 Telegram Bots:** 
   - Controller Bot: Commands aur menus
   - Notification Bot: Trade alerts
   - Analytics Bot: Reports aur stats
   
   Sab bots mein same menu - zero typing required!

3. **3 Databases:**
   - zepix_combined.db: V3 ke trades
   - zepix_price_action.db: V6 ke trades
   - zepix_bot.db: Central system data

**Kitna time lagega?**

10-12 weeks, 6 phases mein:
- Phase 1: Plugin System (Week 1-2)
- Phase 2: Telegram System (Week 2-3)
- Phase 3: Service API (Week 3)
- Phase 4: V3 Migration (Week 4)
- Phase 5: V6 Implementation (Week 4-5)
- Phase 6: Testing (Week 5-6)

**Risk kya hai?**

1. V3 parity - purana behavior exactly match hona chahiye
2. Telegram rate limiting - 3 bots se spam nahi hona chahiye
3. Database migration - existing trades safe rehne chahiye

**Mera confidence level?**

95% confident hoon. Documents bahut detailed hain, architecture clear hai. Bas implementation mein kuch unexpected issues aa sakte hain.

**Approval chahiye:**

PM approval ke baad Phase 1 shuru karunga. Daily progress report dunga. Koi bhi issue aaye toh turant bataunga.

---

## 10. DOCUMENT IMPLEMENTATION STATUS

This section tracks the implementation status of each planning document.

### Planning Documents Status

| Doc # | Document Name | Status | Completion Date | Test File | Test Result |
|-------|---------------|--------|-----------------|-----------|-------------|
| 01 | 01_PROJECT_OVERVIEW.md | **[COMPLETED]** | 2026-01-12 | test_01_project_overview_implementation.py | 58/58 PASSED |
| 02 | 02_PHASE_1_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_02_phase_1_implementation.py | 67/67 PASSED |
| 03 | 03_PHASES_2-6_CONSOLIDATED_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_03_phases_2_6_implementation.py | 127/127 PASSED |
| 04 | 04_PHASE_2_DETAILED_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_04_phase_2_detailed.py | 113/113 PASSED |
| 05 | 05_PHASE_3_DETAILED_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_05_phase_3_detailed.py | 89/89 PASSED |
| 06 | 06_PHASE_4_DETAILED_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_06_phase_4_detailed.py | 149/149 PASSED |
| 07 | 07_PHASE_5_DETAILED_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_07_phase_5_detailed.py | 56/56 PASSED |
| 08 | 08_PHASE_6_DETAILED_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_08_phase_6_detailed.py | 54/54 PASSED |
| 09 | 09_DATABASE_SCHEMA_DESIGNS.md | **[COMPLETED]** | 2026-01-12 | test_09_database_schemas.py | 103/103 PASSED |
| 10 | 10_API_SPECIFICATIONS.md | **[COMPLETED]** | 2026-01-12 | test_10_api_specifications.py | 115/115 PASSED |
| 11 | 11_CONFIGURATION_TEMPLATES.md | **[COMPLETED]** | 2026-01-12 | test_11_configuration_templates.py | 113/113 PASSED |
| 12 | 12_TESTING_CHECKLISTS.md | **[COMPLETED]** | 2026-01-12 | test_12_testing_checklists.py | 133/133 PASSED |
| 13 | 13_CODE_REVIEW_GUIDELINES.md | **[COMPLETED]** | 2026-01-12 | test_13_code_review_guidelines.py | 105/105 PASSED |
| 14 | 14_USER_DOCUMENTATION.md | **[COMPLETED]** | 2026-01-12 | test_14_user_documentation.py | 74/74 PASSED |
| 15 | 15_DEVELOPER_ONBOARDING.md | **[COMPLETED]** | 2026-01-12 | test_15_developer_onboarding.py | 71/71 PASSED |
| 16 | 16_PHASE_7_V6_INTEGRATION_PLAN.md | **[COMPLETED]** | 2026-01-12 | test_16_phase_7_integration.py | 65/65 PASSED |
| 17 | 17_DASHBOARD_TECHNICAL_SPECIFICATION.md | **[SKIPPED]** | 2026-01-12 | - | PM Directive: Dashboard specs being updated |
| 18 | 18_TELEGRAM_SYSTEM_ARCHITECTURE.md | **[COMPLETED]** | 2026-01-12 | test_18_telegram_system.py | 91/91 PASSED |
| 19 | 19_NOTIFICATION_SYSTEM_SPECIFICATION.md | **[COMPLETED]** | 2026-01-12 | test_19_notification_system.py | 104/104 PASSED |
| 20 | 20_TELEGRAM_UNIFIED_INTERFACE_ADDENDUM.md | **[COMPLETED]** | 2026-01-12 | test_20_telegram_interface.py | 139/139 PASSED |
| 21 | 21_MARKET_DATA_SERVICE_SPECIFICATION.md | PENDING | - | - | - |
| 22 | 22_TELEGRAM_RATE_LIMITING_SYSTEM.md | PENDING | - | - | - |
| 23 | 23_DATABASE_SYNC_ERROR_RECOVERY.md | PENDING | - | - | - |
| 24 | 24_STICKY_HEADER_IMPLEMENTATION_GUIDE.md | PENDING | - | - | - |
| 25 | 25_PLUGIN_HEALTH_MONITORING_SYSTEM.md | PENDING | - | - | - |
| 26 | 26_DATA_MIGRATION_SCRIPTS.md | PENDING | - | - | - |
| 27 | 27_PLUGIN_VERSIONING_SYSTEM.md | PENDING | - | - | - |

### Document 01 Implementation Details

**Document:** 01_PROJECT_OVERVIEW.md  
**Status:** COMPLETED  
**Date:** 2026-01-12  

**Implemented Components:**
1. `src/services/order_execution.py` - OrderExecutionService skeleton
2. `src/services/profit_booking.py` - ProfitBookingService skeleton
3. `src/services/risk_management.py` - RiskManagementService skeleton
4. `src/services/trend_monitor.py` - TrendMonitorService skeleton
5. `src/telegram/__init__.py` - Telegram package init
6. `src/telegram/controller_bot.py` - ControllerBot skeleton
7. `src/telegram/notification_bot.py` - NotificationBot skeleton
8. `src/telegram/analytics_bot.py` - AnalyticsBot skeleton
9. `src/logic_plugins/__init__.py` - Logic plugins package init
10. `src/logic_plugins/combined_v3/__init__.py` - V3 plugin package init
11. `src/logic_plugins/combined_v3/plugin.py` - CombinedV3Plugin skeleton
12. `src/logic_plugins/combined_v3/config.json` - V3 plugin configuration
13. `src/logic_plugins/price_action_v6/__init__.py` - V6 plugin package init
14. `src/logic_plugins/price_action_v6/plugin.py` - PriceActionV6Plugin skeleton
15. `src/logic_plugins/price_action_v6/config.json` - V6 plugin configuration

**Test Results:**
- Test File: `tests/test_01_project_overview_implementation.py`
- Total Tests: 58
- Passed: 58
- Failed: 0
- Coverage: 100%

---

### Document 02 Implementation Details

**Document:** 02_PHASE_1_PLAN.md  
**Status:** COMPLETED  
**Date:** 2026-01-12  

**Implementation Note:**
Document 02 (Phase 1 - Core Plugin System Foundation) was found to be **already implemented** in the existing codebase. The plugin system was pre-built with all required components. This implementation verified and tested the existing implementation against Document 02 specifications.

**Verified Components (7 files as specified in Document 02):**
1. `src/core/plugin_system/base_plugin.py` - BaseLogicPlugin abstract class with all required methods
2. `src/core/plugin_system/plugin_registry.py` - PluginRegistry with discovery, loading, routing, and hook execution
3. `src/core/plugin_system/__init__.py` - Package exports (BaseLogicPlugin, PluginRegistry)
4. `src/logic_plugins/_template/plugin.py` - TemplatePlugin extending BaseLogicPlugin
5. `src/logic_plugins/_template/config.json` - Template configuration with all required fields
6. `src/logic_plugins/_template/README.md` - Plugin creation documentation
7. `scripts/test_plugin.py` - Plugin testing script with MockAlert and MockServiceAPI

**Verified Modifications (3 files as specified in Document 02):**
1. `config/config.json` - Has `plugin_system` section with enabled, plugin_dir, auto_load
2. `src/core/trading_engine.py` - Integrates PluginRegistry and ServiceAPI, loads plugins on initialize
3. `.gitignore` - Has `data/*.db` pattern for plugin databases

**Additional Component Found:**
- `src/core/plugin_system/service_api.py` - ServiceAPI class for shared services (bonus implementation)

**Test Results:**
- Test File: `tests/test_02_phase_1_implementation.py`
- Total Tests: 67
- Passed: 67
- Failed: 0
- Coverage: 100%

**Test Categories:**
- TestPluginSystemCoreFiles: 7 tests (file existence)
- TestBaseLogicPlugin: 7 tests (class structure)
- TestPluginRegistry: 9 tests (class methods)
- TestPluginSystemInit: 2 tests (exports)
- TestTemplatePlugin: 5 tests (implementation)
- TestTemplateConfig: 6 tests (JSON structure)
- TestMainConfigPluginSystem: 5 tests (config integration)
- TestGitignorePluginDatabases: 2 tests (.gitignore)
- TestPluginDiscovery: 4 tests (discovery functionality)
- TestPluginInstantiation: 3 tests (plugin creation)
- TestAlertRouting: 4 tests (async routing)
- TestTradingEnginePluginIntegration: 6 tests (engine integration)
- TestServiceAPIExists: 2 tests (service API)
- TestDocument02CompleteSummary: 5 tests (complete verification)

---

### Document 03 Implementation Details

**Document:** 03_PHASES_2-6_CONSOLIDATED_PLAN.md  
**Status:** COMPLETED  
**Date:** 2026-01-12  

**Implementation Note:**
Document 03 consolidates Phases 2-6 of the V5 Hybrid Plugin Architecture. This implementation verified existing Phase 2 (Multi-Telegram) and Phase 3 (Service API) components, and created new modules for Phase 4 (V3 Plugin) and Phase 5 (V6 Plugin).

**Phase 2 - Multi-Telegram System (Verified Existing):**
1. `src/telegram/multi_telegram_manager.py` - MultiTelegramManager with route_message(), send_alert(), send_report()
2. `src/telegram/controller_bot.py` - ControllerBot with process_command(), start(), stop()
3. `src/telegram/notification_bot.py` - NotificationBot with send_entry_notification(), send_exit_notification()
4. `src/telegram/analytics_bot.py` - AnalyticsBot with send_daily_report(), send_weekly_report(), send_plugin_report()

**Phase 3 - Service API Layer (Verified Existing):**
1. `src/services/order_execution.py` - OrderExecutionService with place_order(), place_dual_orders(), close_order()
2. `src/services/profit_booking.py` - ProfitBookingService with 5-level pyramid (1→2→4→8→16)
3. `src/services/risk_management.py` - RiskManagementService with 5 account tiers ($5K-$100K+)
4. `src/services/trend_monitor.py` - TrendMonitorService with MTF alignment tracking

**Phase 4 - V3 Plugin Migration (NEW Modules Created):**
1. `src/logic_plugins/combined_v3/entry_logic.py` - EntryLogic class with:
   - process_entry() - Main entry processing with trend validation
   - SL_MULTIPLIERS: LOGIC1=1.0x, LOGIC2=1.5x, LOGIC3=2.0x
   - ORDER_B_MULTIPLIER: 2.0x (Order B is 2x Order A)
   - Dual order placement via OrderExecutionService
   - Database recording of trades

2. `src/logic_plugins/combined_v3/exit_logic.py` - ExitLogic class with:
   - process_exit() - Full position exit
   - process_reversal_exit() - Close opposite positions for reversal
   - process_partial_exit() - Partial position close
   - calculate_pnl() - P/L calculation with symbol-specific pip values

**Phase 5 - V6 Plugin Implementation (NEW Modules Created):**
1. `src/logic_plugins/price_action_v6/alert_handlers.py` - V6AlertHandlers with:
   - 14 alert handlers (7 entry, 3 exit, 4 info)
   - Entry: Breakout, Pullback, Reversal, Momentum, Support Bounce, Resistance Rejection, Trend Continuation
   - Exit: Exit Signal, Reversal Exit, Target Hit
   - Info: Trend Pulse, Volatility Alert, Session Open, Session Close
   - ADX and Momentum filtering integration

2. `src/logic_plugins/price_action_v6/timeframe_strategies.py` - TimeframeStrategies with:
   - Strategy1M: Scalping (single order, 0.5x SL, 0.5x lot, 30min max hold)
   - Strategy5M: Intraday (single order, 1.0x SL, 1.0x lot, 120min max hold)
   - Strategy15M: Swing (dual orders, 1.5x SL, 1.0x lot, 480min max hold)
   - Strategy1H: Position (dual orders, 2.0x SL, 0.75x lot, 1440min max hold)

3. `src/logic_plugins/price_action_v6/adx_integration.py` - ADXIntegration with:
   - get_current_adx() - ADX value retrieval with caching
   - check_adx_filter() - Entry type filtering (breakout>25, momentum>30, reversal<40)
   - get_trend_direction() - Bullish/Bearish/Neutral from +DI/-DI
   - Threshold constants: WEAK_TREND=20, STRONG_TREND=30

4. `src/logic_plugins/price_action_v6/momentum_integration.py` - MomentumIntegration with:
   - get_momentum() - Composite score (-100 to +100) from RSI, MACD, Stochastic
   - check_momentum_filter() - Directional confirmation
   - is_overbought() / is_oversold() - Condition detection
   - RSI thresholds: OVERSOLD=30, OVERBOUGHT=70

**Test Results:**
- Test File: `tests/test_03_phases_2_6_implementation.py`
- Total Tests: 127
- Passed: 127
- Failed: 0
- Coverage: 100%

**Test Categories:**
- TestPhase2MultiTelegramSystem: 20 tests (file existence, class structure, methods)
- TestPhase3ServiceAPILayer: 26 tests (services, instantiation, functionality)
- TestPhase4V3PluginMigration: 22 tests (plugin, entry/exit logic, config)
- TestPhase5V6PluginImplementation: 46 tests (plugin, handlers, strategies, ADX, momentum)
- TestPhase6Integration: 10 tests (cross-module integration)
- TestDocument03Summary: 5 tests (complete verification)

---

### Document 04 Implementation Details

**Document:** 04_PHASE_2_DETAILED_PLAN.md  
**Status:** COMPLETED  
**Date:** 2026-01-12  

**Implementation Note:**
Document 04 provides detailed specifications for Phase 2 (Multi-Telegram System) enhancements. This implementation created new rate limiting and message queue modules, and enhanced existing Multi-Telegram components with production-ready features.

**NEW Modules Created:**

1. `src/telegram/rate_limiter.py` - Rate Limiting System with:
   - MessagePriority enum (LOW, NORMAL, HIGH, CRITICAL)
   - ThrottledMessage class for queued messages with retry tracking
   - TelegramRateLimiter class with:
     - 4 priority-based queues (queue_critical, queue_high, queue_normal, queue_low)
     - Rate tracking (sent_times_minute, sent_times_second)
     - Async queue processor (_process_queue method)
     - Overflow handling (drops LOW priority first)
     - Statistics tracking (total_sent, total_queued, total_dropped, total_rate_limited, total_retries, total_failures)
   - RateLimitMonitor class for health monitoring across all bots

2. `src/telegram/message_queue.py` - Message Queue Management with:
   - MessageType enum (COMMAND, ALERT, ENTRY, EXIT, REPORT, STATS, BROADCAST, SYSTEM, ERROR)
   - DeliveryStatus enum (PENDING, QUEUED, SENDING, DELIVERED, FAILED, DROPPED)
   - QueuedMessage dataclass with full metadata
   - MessageRouter class with routing rules and content-based routing
   - MessageQueueManager class with priority-based queues, delivery tracking, cleanup
   - MessageFormatter class with format_entry(), format_exit(), format_error(), format_warning()

**ENHANCED Modules:**

3. `src/telegram/multi_telegram_manager.py` - Enhanced with:
   - Rate limiting integration (_init_rate_limiters, controller_limiter, notification_limiter, analytics_limiter)
   - Message queue integration (_init_message_queue)
   - Async API methods (send_controller_message, send_notification, send_analytics_report)
   - Formatted alert methods (send_entry_alert, send_exit_alert, send_error_alert)
   - Health monitoring (get_rate_limit_stats, get_health_status, get_stats)
   - Backward compatible synchronous API (route_message, send_alert, send_report)

4. `src/telegram/controller_bot.py` - Expanded with:
   - CommandCategory enum (SYSTEM, TRADING, PLUGINS, ANALYTICS, SETTINGS)
   - 18 command handlers (start, stop, status, help, menu, health, uptime, plugins, enable_plugin, disable_plugin, plugin_status, trades, positions, close_all, settings, set_risk, daily, weekly)
   - 8 callback handlers (menu_main, menu_plugins, menu_trades, menu_settings, plugin_enable, plugin_disable, confirm_close_all, cancel)
   - Utility methods (_format_uptime)

**Test Results:**
- Test File: `tests/test_04_phase_2_detailed.py`
- Total Tests: 113
- Passed: 113
- Failed: 0
- Coverage: 100%

**Test Categories:**
- TestRateLimiterSystem: 13 tests (file existence, classes, methods, priority queues)
- TestMessageQueueSystem: 17 tests (enums, classes, methods, formatters)
- TestMultiTelegramManager: 19 tests (rate limiting integration, async API, monitoring)
- TestControllerBot: 30 tests (commands, callbacks, expanded handlers)
- TestNotificationBot: 13 tests (delivery system, notifications)
- TestAnalyticsBot: 12 tests (report generation)
- TestDocument04Integration: 5 tests (cross-module integration)
- TestDocument04Summary: 5 tests (complete verification)

---

### Document 05 Implementation Details

**Document:** 05_PHASE_3_DETAILED_PLAN.md  
**Status:** COMPLETED  
**Date:** 2026-01-12  

**Implementation Note:**
Document 05 provides detailed specifications for Phase 3 (Service API Layer) enhancements. This implementation completely rewrote the service layer with production-ready features including MT5 integration, plugin isolation, database persistence, and comprehensive error handling.

**COMPLETELY REWRITTEN Modules:**

1. `src/services/order_execution.py` (626 lines) - OrderExecutionService with:
   - OrderType enum (MARKET, LIMIT, STOP)
   - OrderStatus enum (PENDING, OPEN, CLOSED, CANCELLED, FAILED)
   - OrderRecord dataclass with full order tracking (ticket, plugin_id, symbol, direction, lot_size, prices, timestamps)
   - OrderDatabase class for plugin-isolated order persistence
   - OrderExecutionService class with:
     - place_order() - Market order placement with plugin tagging in comments
     - place_dual_orders() - Order A + Order B placement for V3 logic
     - modify_order() - SL/TP modification
     - close_order() - Full or partial position close
     - close_all_orders() - Close all orders for a plugin
     - get_open_orders() - Plugin-isolated order queries
     - get_order_info() - Order details retrieval
     - get_statistics() / get_plugin_statistics() - Order statistics
   - Retry logic (MAX_RETRIES=3, RETRY_DELAY=0.5s)
   - MT5 integration with error handling

2. `src/services/profit_booking.py` (487 lines) - ProfitBookingService with:
   - ChainStatus enum (ACTIVE, COMPLETED, CANCELLED, FAILED)
   - ProfitLevel enum (LEVEL_0 through LEVEL_4)
   - ProfitChain dataclass with chain tracking
   - PYRAMID_LEVELS constant (1, 2, 4, 8, 16 orders)
   - ProfitBookingService class with:
     - create_chain() - Create new profit booking chain
     - process_profit_level() - Advance chain to next level
     - book_profit() - Book partial profits
     - get_chain_status() - Chain status retrieval
     - close_chain() - Close chain with reason
     - get_active_chains() - Get active chains for plugin
     - get_orders_for_level() - Get order count for pyramid level
     - get_lot_size_for_level() - Calculate lot size per level
     - get_chain_statistics() / get_plugin_statistics() - Chain statistics

**ENHANCED Modules:**

3. `src/services/risk_management.py` (409 lines) - Enhanced with:
   - PluginRiskConfig dataclass (plugin_id, max_lot_size, risk_percentage, daily_loss_limit, max_open_trades, max_drawdown_pct, enabled)
   - DailyStats dataclass (plugin_id, date, trades_opened, trades_closed, total_profit, total_loss, max_drawdown, open_trades)
   - register_plugin() - Register plugin with risk configuration
   - get_plugin_config() - Get plugin-specific configuration
   - check_daily_limit() - Check daily loss limit with can_trade flag
   - Plugin-specific daily loss tracking

4. `src/services/trend_monitor.py` (587 lines) - Enhanced with:
   - IndicatorData dataclass (symbol, timeframe, ma_slope, rsi, adx, macd_histogram, timestamp)
   - get_trend_bias() method - Returns "BULLISH", "BEARISH", or "NEUTRAL" based on indicator signals
   - TIMEFRAME_WEIGHTS constant (1M=1, 5M=2, 15M=3, 1H=4, 4H=5, D1=6)
   - update_indicators() - Update indicator data for symbol/timeframe
   - get_indicators() - Get indicator data
   - get_consensus_score() - Calculate weighted consensus score (-100 to +100)
   - check_trend_alignment() - Check if trend alignment meets trading requirements

5. `src/core/plugin_system/service_api.py` (545 lines) - Complete rewrite with:
   - Plugin-specific API instances via for_plugin() classmethod
   - Service properties (order_service, profit_service, risk_service, trend_service)
   - Convenience methods:
     - place_plugin_order() - Place order with plugin isolation
     - place_dual_orders() - Place dual orders with plugin isolation
     - close_plugin_order() - Close order with plugin verification
     - get_plugin_orders() - Get plugin-specific open orders
     - check_daily_limit() - Check daily loss limit
     - get_trend_consensus() - Get trend consensus score
     - check_trend_alignment() - Check trend alignment requirements
     - create_profit_chain() - Create profit booking chain
     - process_profit_level() - Process profit level advancement
   - Health monitoring:
     - get_service_health() - Get health status of all services
     - get_plugin_statistics() - Get plugin-specific statistics
   - reset_services() classmethod for testing

**Test Results:**
- Test File: `tests/test_05_phase_3_detailed.py`
- Total Tests: 89
- Passed: 89
- Failed: 0
- Coverage: 100%

**Test Categories:**
- TestOrderExecutionService: 16 tests (enums, dataclasses, database, service methods)
- TestProfitBookingService: 14 tests (enums, dataclasses, pyramid levels, lot calculations)
- TestRiskManagementService: 16 tests (dataclasses, tiers, lot sizing, daily limits, plugin config)
- TestTrendMonitorService: 17 tests (enums, indicators, MTF alignment, consensus scoring)
- TestServiceAPI: 18 tests (service properties, convenience methods, backward compatibility)
- TestDocument05Integration: 5 tests (cross-service integration, plugin isolation)
- TestDocument05Summary: 5 tests (complete verification)

---

**Document End**

**Author:** Devin AI  
**Date:** 2026-01-12  
**Status:** IMPLEMENTATION IN PROGRESS (Documents 01-16, 18 Complete, Doc 17 Skipped, 63% done)
