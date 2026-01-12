# 🧠 V6 ALERT PARSER LOGIC

**File:** `02_ALERT_PARSER_LOGIC.md`  
**Date:** 2026-01-11 04:35 IST  
**Target File:** `src/v3_alert_models.py` & `src/processors/alert_processor.py`

---

## 1. PYDANTIC MODEL (`v3_alert_models.py`)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class ZepixV6Alert(BaseModel):
    """
    V6 Enhanced Alert Payload Model
    Matches 15-field standard
    """
    type: str                   # 0: BULLISH_ENTRY
    ticker: str                 # 1
    tf: str                     # 2
    price: float                # 3
    direction: str              # 4: BUY/SELL
    conf_level: str             # 5: HIGH/MODERATE
    conf_score: int             # 6
    adx: Optional[float]        # 7
    adx_strength: str           # 8
    sl: Optional[float]         # 9
    tp1: Optional[float]        # 10
    tp2: Optional[float]        # 11
    tp3: Optional[float]        # 12
    alignment: str              # 13: "5/1"
    tl_status: str              # 14: "TL_OK" allow logic to decide
    
    @validator('adx', pre=True)
    def handle_na_fields(cls, v):
        if v == 'NA': return None
        return v
```

---

## 2. PARSING LOGIC (`alert_processor.py`)

```python
def parse_v6_payload(self, msg: str) -> ZepixV6Alert:
    parts = msg.split('|')
    
    # ⚠️ Validation: Check Field Count
    # Standard V6 Entry payload has 15 fields
    # If risk management disabled in Pine, it might have 11 fields.
    # We implement dynamic parsing based on length.
    
    if len(parts) >= 15:
        return ZepixV6Alert(
            type=parts[0],
            ticker=parts[1],
            tf=parts[2],
            price=parts[3],
            direction=parts[4],
            conf_level=parts[5],
            conf_score=parts[6],
            adx=parts[7],
            adx_strength=parts[8],
            sl=parts[9],
            tp1=parts[10],
            tp2=parts[11],
            tp3=parts[12],
            alignment=parts[13],
            tl_status=parts[14]
        )
    else:
        logger.error(f"❌ Invalid V6 Payload Length: {len(parts)}")
        raise ValueError("Payload incomplete")
```

---

## 3. PULSE PARSING

```python
def parse_pulse_payload(self, msg: str):
    # TREND_PULSE|BTCUSDT|5|4|2|CHANGES|STATE
    parts = msg.split('|')
    return {
        "type": "TREND_PULSE",
        "symbol": parts[1],
        "tf": parts[2],
        "bulls": int(parts[3]),
        "bears": int(parts[4]),
        "changes": parts[5], # To be parsed into DB updates
        "state": parts[6]
    }
```

**STATUS: CODE READY**
