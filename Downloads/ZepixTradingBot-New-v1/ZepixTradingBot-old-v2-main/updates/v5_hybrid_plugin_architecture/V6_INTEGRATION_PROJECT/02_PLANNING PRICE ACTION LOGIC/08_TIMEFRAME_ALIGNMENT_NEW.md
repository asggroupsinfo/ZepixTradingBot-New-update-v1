# 🌐 TIMEFRAME ALIGNMENT (TREND PULSE SYSTEM)

**File:** `08_TIMEFRAME_ALIGNMENT_NEW.md`  
**Date:** 2026-01-11 04:55 IST  
**Alert:** `TREND_PULSE`  
**Core Upgrade:** Decoupled Trend Management

---

## 1. THE PROBLEM (V3)
In V3, the Bot's Global Trend Database was updated via **Entry Signals** (CSV string).
-   **Issue:** Trends change *between* signals. Waiting for an entry to know the trend is slow.
-   **Risk:** Entry logic might use outdated trend info.

---

## 2. THE SOLUTION (V6 PULSE)
V6 introduces `TREND_PULSE` - a dedicated heartbeat alert that fires **ONLY** when trends flip.

**Payload:**
```text
TREND_PULSE|BTCUSDT|5|4|2|15:BULL->BEAR,60:SIDE->BEAR|MIXED_BEARISH
```

### **Components:**
1.  **Bull/Bear Count:** Immediate raw alignment score (e.g., 4/2).
2.  **Changes List:** Specific TFs that flipped.
3.  **Market State:** Interpreted state (e.g., `MIXED_BEARISH`).

---

## 3. IMPLEMENTATION STRATEGY

### **A. Trend Database (DB)**
The DB Schema needs to store the **Latest State** per timeframe independently.
```sql
CREATE TABLE market_trends (
    symbol TEXT,
    timeframe TEXT,
    direction TEXT, -- BULL/BEAR/SIDE
    last_updated TIMESTAMP
);
```

### **B. Processor Logic**
When `TREND_PULSE` arrives:
```python
def handle_trend_pulse(self, alert):
    # Field 5: "15:BULL->BEAR,60:SIDE->BEAR"
    changes = alert.raw_payload[5].split(',')
    
    for change in changes:
        # Parse "15:BULL->BEAR"
        tf, transition = change.split(':')
        old_dir, new_dir = transition.split('->')
        
        # UPDATE DB
        self.db.update_trend(alert.symbol, tf, new_dir)
        
        # Log
        logger.info(f"🔄 Trend Flip {alert.symbol} {tf}: {new_dir}")
```

### **C. The "Single Source of Truth"**
All `PriceActionLogic` classes (1m, 5m, 15m, 1H) must query this DB for validation.
-   **OLD V3:** Accepted "Alignment" from Entry Signal string.
-   **NEW V6:** Queries `self.trend_manager.get_alignment(symbol)`.

---

## 4. ALIGNMENT RULES

| Logic Profile | Required Alignment | Source |
| :--- | :--- | :--- |
| **1M Scalper** | Ignore | (Noise) |
| **5M Momentum** | Align w/ **15M** | DB Query |
| **15M Intraday** | Align w/ **Global State** | DB Query |
| **1H Swing** | Align w/ **4H** | DB Query |

---

**STATUS: PLANNED - CRITICAL UPGRADE**
