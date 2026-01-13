# AGNI PARIKSHA - ULTIMATE SYSTEM TEST RESULTS

**Date:** 2026-01-13 18:37:17
**Duration:** 0.02 seconds
**Total Tests:** 35
**Passed:** 33
**Failed:** 2
**Overall Status:** FAIL

---

## EXECUTIVE SUMMARY

| Scenario | Status | Pass | Fail |
|----------|--------|------|------|
| 1. STARTUP & INTEGRITY | PASS | 5 | 0 |
| 2. COMPLEX ENTRY LOGIC | PASS | 6 | 0 |
| 3. RE-ENTRY & MANAGEMENT | PASS | 5 | 0 |
| 4. SESSION & FILTERS | PASS | 5 | 0 |
| 5. PROFIT PROTECTION | PASS | 4 | 0 |
| 6. DATA & TREND UPDATES | PASS | 5 | 0 |
| 7. TELEGRAM & VOICE | FAIL | 3 | 2 |

---

## SCENARIO 1: STARTUP & INTEGRITY

**Status:** PASS

### V3 Database Connection (zepix_combined.db)

**Result:** PASS
**Duration:** 0.21ms

**Evidence:**
```
Connected to /home/ubuntu/repos/ZepixTradingBot-New-update-v1/Downloads/ZepixTradingBot-New-v1/ZepixTradingBot-old-v2-main/data/zepix_combined.db
```

### V6 Database Connection (zepix_price_action.db)

**Result:** PASS
**Duration:** 0.15ms

**Evidence:**
```
Connected to /home/ubuntu/repos/ZepixTradingBot-New-update-v1/Downloads/ZepixTradingBot-New-v1/ZepixTradingBot-old-v2-main/data/zepix_price_action.db
```

### Plugin Discovery (6 plugins)

**Result:** PASS
**Duration:** 0.42ms

**Evidence:**
```
Found plugins: ['combined_v3', 'price_action_5m', 'price_action_1m', 'hello_world', 'price_action_v6', 'price_action_1h', 'price_action_15m']
```

### Plugin Health Monitor File Exists

**Result:** PASS
**Duration:** 0.13ms

**Evidence:**
```
File exists: True, Has class: True, Has status: True
```

### MT5 Connection (Mock)

**Result:** PASS
**Duration:** 0.09ms

**Evidence:**
```
Connected: True, Balance: $10000.0
```

## SCENARIO 2: COMPLEX ENTRY LOGIC

**Status:** PASS

### V3 Combined Plugin Files Exist

**Result:** PASS
**Duration:** 0.16ms

**Evidence:**
```
Plugin: True, Routing: True, Has routing logic: True, Has institutional: False
```

### V6 5M BULLISH_ENTRY - ADX >= 25 Check

**Result:** PASS
**Duration:** 2.83ms

**Evidence:**
```
ADX: 28.0 >= 25.0: True, Strength != WEAK: True
```

### V6 5M Rejection - ADX WEAK

**Result:** PASS
**Duration:** 0.01ms

**Evidence:**
```
Signal with adx_strength='WEAK' should be rejected: True
```

### V6 5M Rejection - ADX < 25

**Result:** PASS
**Duration:** 0.01ms

**Evidence:**
```
Signal with adx=15.0 < 25.0 should be rejected: True
```

### V6 1H Risk Multiplier = 0.6x

**Result:** PASS
**Duration:** 2.36ms

**Evidence:**
```
Risk multiplier: 0.6 (expected: 0.6)
```

### V6 1H ADX Extreme Threshold = 50

**Result:** PASS
**Duration:** 0.01ms

**Evidence:**
```
ADX extreme threshold: 50.0 (expected: 50.0)
```

## SCENARIO 3: RE-ENTRY & MANAGEMENT

**Status:** PASS

### V3 Routing Logic File Exists

**Result:** PASS
**Duration:** 0.10ms

**Evidence:**
```
File exists: True, Has LOGIC_TYPES: True
```

### V3 Position Sizer File Exists

**Result:** PASS
**Duration:** 0.09ms

**Evidence:**
```
File exists: True, Has V3PositionSizer: True
```

### V3 MTF Processor File Exists

**Result:** PASS
**Duration:** 0.07ms

**Evidence:**
```
File exists: True, Has MTF logic: True
```

### V3 Dual Order Manager File Exists

**Result:** PASS
**Duration:** 0.07ms

**Evidence:**
```
File exists: True, Has dual order logic: True
```

### V6 Timeframe Strategies File Exists

**Result:** PASS
**Duration:** 0.07ms

**Evidence:**
```
File exists: True, Has TF strategies: True
```

## SCENARIO 4: SESSION & FILTERS

**Status:** PASS

### Session Settings File Exists

**Result:** PASS
**Duration:** 0.11ms

**Evidence:**
```
File: /home/ubuntu/repos/ZepixTradingBot-New-update-v1/Downloads/ZepixTradingBot-New-v1/ZepixTradingBot-old-v2-main/data/session_settings.json, Sessions: ['asian', 'london', 'overlap', 'ny_late', 'dead_zone']
```

### Asian Session - GBPUSD Blocked

**Result:** PASS
**Duration:** 0.10ms

**Evidence:**
```
Asian allowed symbols: ['USDJPY', 'AUDJPY', 'AUDUSD', 'NZDUSD'], GBPUSD blocked: True
```

### London Session - GBPUSD Allowed

**Result:** PASS
**Duration:** 0.08ms

**Evidence:**
```
London allowed symbols: ['EURUSD', 'GBPUSD', 'EURGBP', 'GBPJPY', 'EURJPY', 'XAUUSD'], GBPUSD allowed: True
```

### V6 1M Spread Filter (< 2 pips)

**Result:** PASS
**Duration:** 2.04ms

**Evidence:**
```
Max spread: 2.0 pips (expected: 2.0)
```

### V6 5M Spread Filter (< 3 pips)

**Result:** PASS
**Duration:** 0.01ms

**Evidence:**
```
Max spread: 3.0 pips (expected: 3.0)
```

## SCENARIO 5: PROFIT PROTECTION

**Status:** PASS

### ProfitBookingManager File Exists

**Result:** PASS
**Duration:** 0.23ms

**Evidence:**
```
File exists: True, Has class: True
```

### DualOrderManager File Exists

**Result:** PASS
**Duration:** 0.15ms

**Evidence:**
```
File exists: True, Has class: True
```

### V3 Dual Order Manager File Exists

**Result:** PASS
**Duration:** 0.08ms

**Evidence:**
```
File exists: True, Has dual order logic: True
```

### V6 Order Types per Timeframe

**Result:** PASS
**Duration:** 2.25ms

**Evidence:**
```
Order types: {'1M': 'ORDER_B_ONLY', '5M': 'DUAL_ORDERS', '15M': 'ORDER_A_ONLY', '1H': 'ORDER_A_ONLY'}
```

## SCENARIO 6: DATA & TREND UPDATES

**Status:** PASS

### V6 Alert Parser File Exists

**Result:** PASS
**Duration:** 0.11ms

**Evidence:**
```
File exists: True, Has parse function: True, Has pipe format: True
```

### V6 Signal Mapper Defined

**Result:** PASS
**Duration:** 0.09ms

**Evidence:**
```
Has SIGNAL_FIELDS: True, BULLISH: True, BEARISH: True, TREND_PULSE: True
```

### V6 Database File Exists

**Result:** PASS
**Duration:** 0.31ms

**Evidence:**
```
File exists: True, Tables: ['v6_trades', 'sqlite_sequence', 'v6_trend_pulse', 'v6_momentum_state']
```

### V6 Plugin File Exists

**Result:** PASS
**Duration:** 0.12ms

**Evidence:**
```
File exists: True, Has class: True, Has process: False
```

### V3 MTF Processor File Exists

**Result:** PASS
**Duration:** 0.07ms

**Evidence:**
```
File exists: True, Has MTF class: True
```

## SCENARIO 7: TELEGRAM & VOICE

**Status:** FAIL

### StickyHeaderManager Class Exists

**Result:** PASS
**Duration:** 3.97ms

**Evidence:**
```
StickyHeaderManager imported successfully
```

### NotificationManager File Exists

**Result:** FAIL
**Duration:** 0.05ms

**Evidence:**
```
File exists: False, Has class: False
```

### VoiceAlertService File Exists

**Result:** FAIL
**Duration:** 0.04ms

**Evidence:**
```
File exists: False, Has class: False
```

### TelegramRateLimiter Class Exists

**Result:** PASS
**Duration:** 3.12ms

**Evidence:**
```
TelegramRateLimiter imported successfully
```

### MenuBuilder Class Exists

**Result:** PASS
**Duration:** 1.85ms

**Evidence:**
```
MenuBuilder imported successfully
```

---

## LOG SNIPPETS

```
2026-01-13 18:37:17,315 | DEBUG | asyncio | Using selector: EpollSelector
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | ================================================================================
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | AGNI PARIKSHA - ULTIMATE SYSTEM TEST
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | ================================================================================
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | Start Time: 2026-01-13T18:37:17.315536
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | Testing ALL code paths with ACTUAL logic
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | ================================================================================
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | SCENARIO 1: STARTUP & INTEGRITY
2026-01-13 18:37:17,315 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,316 | INFO | AGNI_PARIKSHA | MT5 Mock: Connection established
2026-01-13 18:37:17,316 | INFO | AGNI_PARIKSHA | SCENARIO 1 COMPLETE: 5/5 passed
2026-01-13 18:37:17,316 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,316 | INFO | AGNI_PARIKSHA | SCENARIO 2: COMPLEX ENTRY LOGIC
2026-01-13 18:37:17,317 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,322 | INFO | AGNI_PARIKSHA | SCENARIO 2 COMPLETE: 6/6 passed
2026-01-13 18:37:17,322 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,322 | INFO | AGNI_PARIKSHA | SCENARIO 3: RE-ENTRY & MANAGEMENT
2026-01-13 18:37:17,322 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,323 | INFO | AGNI_PARIKSHA | SCENARIO 3 COMPLETE: 5/5 passed
2026-01-13 18:37:17,323 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,323 | INFO | AGNI_PARIKSHA | SCENARIO 4: SESSION & FILTERS
2026-01-13 18:37:17,323 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,325 | INFO | AGNI_PARIKSHA | SCENARIO 4 COMPLETE: 5/5 passed
2026-01-13 18:37:17,325 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,325 | INFO | AGNI_PARIKSHA | SCENARIO 5: PROFIT PROTECTION
2026-01-13 18:37:17,325 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,328 | INFO | AGNI_PARIKSHA | SCENARIO 5 COMPLETE: 4/4 passed
2026-01-13 18:37:17,328 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,328 | INFO | AGNI_PARIKSHA | SCENARIO 6: DATA & TREND UPDATES
2026-01-13 18:37:17,328 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,329 | INFO | AGNI_PARIKSHA | SCENARIO 6 COMPLETE: 5/5 passed
2026-01-13 18:37:17,329 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,329 | INFO | AGNI_PARIKSHA | SCENARIO 7: TELEGRAM & VOICE
2026-01-13 18:37:17,329 | INFO | AGNI_PARIKSHA | ============================================================
2026-01-13 18:37:17,330 | WARNING | telegram.multi_telegram_manager | Rate limiting modules not available, using basic mode
2026-01-13 18:37:17,331 | WARNING | telegram.multi_telegram_manager | TelegramBot module not available
2026-01-13 18:37:17,339 | INFO | AGNI_PARIKSHA | SCENARIO 7 COMPLETE: 3/5 passed

```

---

## FINAL VERDICT

**SOME SCENARIOS FAILED - SYSTEM REQUIRES FIXES**

The following issues were detected:

- TELEGRAM & VOICE: NotificationManager File Exists - 
- TELEGRAM & VOICE: VoiceAlertService File Exists - 
