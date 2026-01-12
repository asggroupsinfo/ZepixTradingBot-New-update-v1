# Background Workflow & Heartbeat Audit

This document details the background processes that keep the Zepix Trading Bot alive, focusing on the `PriceMonitorService` (The Watchman) and its interactions with the Database and Trading Engine.

## 1. The Pulse: Price Monitor Service

The `PriceMonitorService` acts as the system's heartbeat. It does **not** listen to a real-time tick stream (tick-by-tick) for everything. Instead, it operates on a **polling interval** (Default: 30 seconds) to check specifically tracked opportunities.

### 1.1 Polling Frequency
- **Interval:** Determined by `re_entry_config.price_monitor_interval_seconds` (Default: 30s).
- **Operation:** Every 30 seconds, it wakes up and performs a full cycle check.
- **Tick Stream vs Polling:**
    - **Alerts (Webhooks):** Processed immediately (Push based).
    - **Re-entries (SL Hunt/TP Cont):** Processed every 30s (Pull/Poll based).
    - **Margin Health:** Checked every cycle.

### 1.2 What does it Monitor?
Only **pending** opportunities are monitored. It does not iterate every open trade unless required by a specific module.

| Module | tracked in | Trigger Condition | Action |
| :--- | :--- | :--- | :--- |
| **SL Hunt** | `sl_hunt_pending` dictionary | Price reaches `target_price` (SL + Offset) | Calls `_execute_sl_hunt_reentry` |
| **TP Continuation** | `tp_continuation_pending` dictionary | Price reaches `target_price` (TP + Gap) | Calls `_execute_tp_continuation_reentry` |
| **Exit Continuation** | `exit_continuation_pending` dictionary | Price reaches `gap` after reversal | Calls `register_exit_continuation` (re-entry) |
| **Profit Chains** | `ProfitBookingReEntryManager` | `check_recoveries()` logic | Calls `_execute_profit_recovery` |
| **Margin Health** | Global Account Info | Margin Level < 100% | **EMERGENCY CLOSE** of worst position |

## 2. Database Interactions

The Database (`TradeDatabase`) is primarily an **Event Log** and **State Store**, not a high-frequency Time-Series Database (TSDB).

- **Save on State Change:** Trades are saved/updated only when their state changes (Open, Close, Modified).
- **No Tick History:** The DB does NOT store every price tick.
- **Reconstruction:** `ProfitBookingManager` and `ReEntryManager` reconstruct their state by reading active trades/chains from the DB on startup.

## 3. Inter-Component Communication

The system uses a **Direct Invocation** model rather than an Event Bus.

1.  **TradingEngine** initializes everything.
2.  **TradingEngine** receives Webhook -> Checks `ReversalExitHandler`.
3.  **PriceMonitorService** (Background) -> Checks `ReEntryManager` / `ProfitBookingReEntryManager`.
4.  If Triggered -> Calls `TradingEngine` methods (`place_recovery_order`, etc.).
5.  **AutonomousSystemManager** is mostly a coordinator validation layer, injected into the Engine and Managers.

## 4. The Critical "Watchman" Loop

```python
while self.is_running:
    # 1. Margin Check
    await self._check_margin_health()

    # 2. SL Hunt Check
    # Iterates sl_hunt_pending -> Get Price -> Compare -> Execute
    await self._check_sl_hunt_reentries()

    # 3. TP Continuation Check
    # Iterates tp_continuation_pending -> Get Price -> Compare -> Execute
    await self._check_tp_continuation_reentries()
    
    # 4. Exit Continuation Check (New)
    await self._check_exit_continuation_reentries()

    # 5. Profit Chain Recovery
    await self._check_profit_booking_chains()
```

## 5. Potential Failure Points (Audit Targets)

1.  **Zombie Monitor:** If `_monitor_loop` crashes without restarting, re-entries stop functioning. (Mitigated by `monitor_error_count` and try-except block).
2.  **Stale Prices:** If `MT5Client.get_current_price` fails (returns 0 or old price), logic may trigger incorrectly or block.
3.  **Database Lock:** SQLite write contention could block the main loop if `save_trade` takes too long.
