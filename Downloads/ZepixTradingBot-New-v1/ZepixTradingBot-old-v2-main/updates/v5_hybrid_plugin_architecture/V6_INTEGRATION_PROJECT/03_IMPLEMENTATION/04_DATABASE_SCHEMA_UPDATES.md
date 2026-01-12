# 🗄️ DATABASE SCHEMA UPDATE: TREND PULSE

**File:** `04_DATABASE_SCHEMA_UPDATES.md`  
**Date:** 2026-01-11 04:45 IST  
**Module:** `src/core/database/schema.sql` (or equivalent)

---

## 1. NEW TABLE: `market_trends`
We need a dedicated table to store the state of each timeframe for each symbol.

```sql
CREATE TABLE IF NOT EXISTS market_trends (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    direction TEXT NOT NULL,       -- 'BULLISH', 'BEARISH', 'SIDEWAYS'
    strength TEXT DEFAULT 'WEAK',  -- 'STRONG', 'MODERATE', 'WEAK'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_alert TEXT,         -- 'TREND_PULSE', 'MOMENTUM'
    PRIMARY KEY (symbol, timeframe)
);
```

---

## 2. PYTHON INTERFACE (`trend_repository.py`)

```python
def update_trend(self, symbol, tf, direction, strength="WEAK"):
    """
    Upsert trend state
    """
    query = """
    INSERT INTO market_trends (symbol, timeframe, direction, strength, last_updated)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(symbol, timeframe) DO UPDATE SET
        direction=excluded.direction,
        strength=excluded.strength,
        last_updated=excluded.last_updated
    """
    self.execute(query, (symbol, tf, direction, strength, datetime.now()))
```

---

## 3. GET ALIGNMENT METHOD

```python
def get_consensus_alignment(self, symbol):
    """
    Returns Bull/Bear count from DB
    """
    rows = self.fetch("SELECT direction FROM market_trends WHERE symbol=?", (symbol,))
    bulls = sum(1 for r in rows if r['direction'] == 'BULLISH')
    bears = sum(1 for r in rows if r['direction'] == 'BEARISH')
    return bulls, bears
```

**STATUS: CODE READY**
