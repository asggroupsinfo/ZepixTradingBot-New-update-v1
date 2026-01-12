# TESTING CHECKLISTS

**Version:** 2.0 (V3/V6 Specific Tests)  
**Date:** 2026-01-12  
**Coverage:** Unit + Integration + E2E + Shadow Mode

---

## 🧪 V3 COMBINED LOGIC TESTS

### **1. Signal Processing Tests**

**Test 12 Signal Types:**
- [ ] Institutional_Launchpad → correct routing
- [ ] Liquidity_Trap → correct routing
- [ ] Momentum_Ignition → correct routing
- [ ] Mitigation_Block → correct routing
- [ ] Golden_Pocket (5m) → LOGIC2
- [ ] Golden_Pocket (1H) → LOGIC3
- [ ] Golden_Pocket (4H) → LOGIC3
- [ ] Screener → LOGIC3 (override)
- [ ] entry_v3 → trend bypass enabled
- [ ] Exit_Bullish → close logic
- [ ] Exit_Bearish → close logic
- [ ] Volatility_Squeeze → DB update only
- [ ] **Signal 12 (Sideways_Breakout)** → correct handling

**Test Data:**
```json
{
    "signal_type": "Institutional_Launchpad",
    "tf": "5",
    "consensus": "8",
    "direction": "BUY",
    "mtf": "1,1,1,1,1,-1"
}
```

**Expected:** Route to LOGIC1, extract pillars [1,1,1,1], allow entry

---

### **2. Routing Matrix Tests**

**Priority 1 (Signal Overrides):**
- [ ] Screener always → LOGIC3
- [ ] Golden Pocket 1H → LOGIC3
- [ ] Golden Pocket 4H → LOGIC3

**Priority 2 (Timeframe Routing):**
- [ ] 5m signal → LOGIC1 (1.25x multiplier)
- [ ] 15m signal → LOGIC2 (1.0x multiplier)
- [ ] 60m signal → LOGIC3 (0.625x multiplier)
- [ ] 240m signal → LOGIC3 (0.625x multiplier)

**Test:**
```python
def test_routing_matrix():
    # Signal override takes priority
    signal = {"signal_type": "Screener", "tf": "5"}
    route = get_logic_route(signal)
    assert route == "LOGIC3"  # NOT LOGIC1
    
    # Timeframe routing
    signal = {"signal_type": "Institutional_Launchpad", "tf": "15"}
    route = get_logic_route(signal)
    assert route == "LOGIC2"
```

---

### **3. Dual Order System Tests**

**Hybrid SL Verification:**
- [ ] Order A receives V3 Smart SL from alert
- [ ] Order B receives Fixed $10 SL (IGNORES Pine SL)
- [ ] Order A has TP2 (extended target)
- [ ] Order B has TP1 (closer target)
- [ ] 50/50 lot split applied

**Test:**
```python
def test_dual_orders_hybrid_sl():
    alert = {
        "symbol": "XAUUSD",
        "direction": "BUY",
        "sl_price": 2028.00,  # V3 Smart SL
        "tp1_price": 2032.00,
        "tp2_price": 2035.00,
        "entry_price": 2030.00
    }
    
    order_a, order_b = place_v3_dual_orders(alert, lot_total=0.10)
    
    # Verify Order A
    assert order_a["sl"] == 2028.00  # Uses V3 Smart SL
    assert order_a["tp"] == 2035.00  # Uses TP2
    assert order_a["lot"] == 0.05
    
    # Verify Order B
    fixed_sl = 2030.00 - 10.0/2030.00*100  # $10 SL calculation
    assert abs(order_b["sl"] - fixed_sl) < 0.01  # Fixed $10 SL
    assert order_b["tp"] == 2032.00  # Uses TP1
    assert order_b["lot"] == 0.05
```

---

### **4. MTF 4-Pillar Extraction Tests**

**Test Extraction:**
- [ ] Pine sends 6 trends: `[1m, 5m, 15m, 1H, 4H, 1D]`
- [ ] Bot extracts indices `[2:6]` = `[15m, 1H, 4H, 1D]`
- [ ] Bot ignores indices `[0:2]` = `[1m, 5m]`

**Test:**
```python
def test_mtf_extraction():
    raw_mtf = "1,1,1,1,1,-1"  # From Pine
    pillars = extract_mtf_pillars(raw_mtf)
    
    assert pillars == {
        "15m": 1,   # Index 2
        "1h": 1,    # Index 3
        "4h": 1,    # Index 4
        "1d": -1    # Index 5
    }
    # Indices 0,1 (1m, 5m) are NOT used
```

**Trend Alignment Test:**
- [ ] BUY requires 3/4 bullish pillars
- [ ] SELL requires 3/4 bearish pillars
- [ ] 2/4 alignment → REJECT entry

---

### **5. Position Sizing 4-Step Tests**

**Test Flow:**
```python
def test_v3_position_sizing():
    base_lot = 0.10
    consensus = 8  # maps to 0.9 multiplier
    logic_route = "LOGIC1"  # 1.25x multiplier
    
    # Step 1: base_lot
    lot = base_lot  # 0.10
    
    # Step 2: consensus multiplier
    v3_mult = map_consensus_to_multiplier(8)  # 0.9
    lot *= v3_mult  # 0.09
    
    # Step 3: logic multiplier
    logic_mult = get_logic_multiplier("LOGIC1")  # 1.25
    lot *= logic_mult  # 0.1125
    
    # Step 4: split 50/50
    order_a_lot = lot / 2  # 0.05625
    order_b_lot = lot / 2  # 0.05625
    
    assert order_a_lot == 0.05625
```

**Consensus Mapping Test:**
- [ ] Consensus 0-3 → 0.2x to 0.5x
- [ ] Consensus 4-6 → 0.6x to 0.8x
- [ ] Consensus 7-9 → 0.9x to 1.0x

---

### **6. Trend Bypass Logic Tests**

**Test Scenarios:**
- [ ] entry_v3 signal → BYPASS trend check, place order
- [ ] Institutional_Launchpad → REQUIRE trend check
- [ ] SL hunt re-entry → REQUIRE trend check

**Test:**
```python
def test_trend_bypass():
    # Fresh v3 signal bypasses trend
    signal = {"signal_type": "entry_v3", "direction": "BUY"}
    mtf_aligned = False
    should_enter = check_entry_allowed(signal, mtf_aligned)
    assert should_enter == True  # Bypassed
    
    # Legacy signal requires trend
    signal = {"signal_type": "Institutional_Launchpad", "direction": "BUY"}
    should_enter = check_entry_allowed(signal, mtf_aligned=False)
    assert should_enter == False  # Rejected
```

---

## 🎯 V6 PRICE ACTION TESTS

### **1. V6 1M Plugin Tests (ORDER B ONLY)**

**Entry Conditions:**
- [ ] ADX >= 20 → allow entry
- [ ] ADX < 20 → reject entry
- [ ] Confidence >= 80 → allow entry
- [ ] Confidence < 80 → reject entry
- [ ] Spread > 2.0 pips → reject entry

**Order Routing:**
- [ ] ONLY Order B placed
- [ ] NO Order A placed
- [ ] Uses TP1 (quick exit)

**Test:**
```python
def test_v6_1m_order_b_only():
    alert = {
        "adx": 22,
        "confidence_score": 85,
        "spread_pips": 1.5
    }
    
    order_a, order_b = process_v6_1m_alert(alert)
    
    assert order_a is None  # No Order A
    assert order_b is not None  # Order B placed
    assert order_b["tp_level"] == "TP1"
```

---

### **2. V6 5M Plugin Tests (DUAL ORDERS)**

**Entry Conditions:**
- [ ] ADX >= 25 → allow
- [ ] 15m trend aligned → allow
- [ ] Momentum increasing → allow

**Order Routing:**
- [ ] BOTH Order A and Order B placed
- [ ] Same SL for both orders
- [ ] Order B → TP1, Order A → TP2
- [ ] After TP1 hit → move to breakeven

**Test:**
```python
def test_v6_5m_dual_orders():
    alert = {
        "adx": 28,
        "confidence_score": 75,
        "trend_15m_aligned": True
    }
    
    order_a, order_b = process_v6_5m_alert(alert)
    
    assert order_a is not None
    assert order_b is not None
    assert order_a["sl"] == order_b["sl"]  # Same SL
    assert order_a["tp"] > order_b["tp"]  # TP2 > TP1
```

---

### **3. V6 15M Plugin Tests (ORDER A ONLY)**

**Entry Conditions:**
- [ ] Market state matches signal direction
- [ ] Pulse alignment verified (bull_count > bear_count for BUY)

**Order Routing:**
- [ ] ONLY Order A placed
- [ ] NO Order B placed

**Test:**
```python
def test_v6_15m_order_a_only():
    alert = {"direction": "BUY", "market_state": "TRENDING_BULLISH"}
    pulse_data = {"bull_count": 5, "bear_count": 2}
    
    order_a, order_b = process_v6_15m_alert(alert, pulse_data)
    
    assert order_a is not None  # Order A placed
    assert order_b is None  # No Order B
```

---

### **4. V6 1H Plugin Tests (ORDER A ONLY)**

**Entry Conditions:**
- [ ] 4H trend aligned
- [ ] 1D trend aligned

**Order Routing:**
- [ ] ONLY Order A placed

---

### **5. Trend Pulse System Tests**

**Update Tests:**
- [ ] TREND_PULSE alert updates `market_trends` table
- [ ] Bull count incremented correctly
- [ ] Bear count incremented correctly
- [ ] Market state updated (`TRENDING_BULLISH`, `SIDEWAYS`, etc.)
- [ ] Changes field populated (which TFs changed)

**Alignment Tests:**
```python
def test_pulse_alignment():
    # BUY requires bull > bear
    pulse = {"bull_count": 5, "bear_count": 2}
    aligned = check_pulse_alignment(pulse, "BUY")
    assert aligned == True
    
    # SELL requires bear > bull
    aligned = check_pulse_alignment(pulse, "SELL")
    assert aligned == False
```

---

## 🔄 INTEGRATION TESTS

### **1. V3 + V6 Simultaneous Execution**

**Test:**
- [ ] V3 signal processed → routes to combined_v3 plugin
- [ ] V6 1M signal processed → routes to price_action_1m plugin
- [ ] Both execute independently
- [ ] Separate databases maintained
- [ ] No cross-contamination

---

### **2. ServiceAPI Integration Tests**

**V3 Methods:**
- [ ] `place_dual_orders_v3()` works
- [ ] `get_mtf_trends()` returns 4 pillars
- [ ] `validate_v3_trend_alignment()` correctly checks 3/4

**V6 Methods:**
- [ ] `place_single_order_a()` works
- [ ] `place_single_order_b()` works
- [ ] `place_dual_orders_v6()` works (different from V3)
- [ ] `update_trend_pulse()` updates market_trends table
- [ ] `check_pulse_alignment()` validates correctly

---

## 🎭 SHADOW MODE TESTS

**72-Hour Shadow Mode for V3:**
- [ ] All 12 signals logged
- [ ] Routing decisions logged
- [ ] Hypothetical dual orders tracked
- [ ] P&L calculated without real trades
- [ ] Zero actual MT5 orders placed

**72-Hour Shadow Mode for Each V6 Plugin:**
- [ ] 1M: ORDER B ONLY simulated
- [ ] 5M: DUAL ORDERS simulated
- [ ] 15M: ORDER A ONLY simulated
- [ ] 1H: ORDER A ONLY simulated

---

## ✅ FINAL VERIFICATION

**Production Readiness:**
- [ ] All HIGH priority tests passing
- [ ] V3 plugin tested with all 12 signals
- [ ] All 4 V6 plugins tested with conditional routing
- [ ] Database schemas verified
- [ ] ServiceAPI methods verified
- [ ] Shadow mode logs reviewed
- [ ] Zero errors in 72-hour shadow period
- [ ] Documentation matches implementation

**Status:** READY FOR PRODUCTION DEPLOYMENT
