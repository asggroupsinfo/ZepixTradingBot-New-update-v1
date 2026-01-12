
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

# Mock Dependencies
class MockConfig:
    def __init__(self):
        self.data = {
            "re_entry_config": {
                "autonomous_config": {
                    "sl_hunt_recovery": {
                        "enabled": True,
                        "tight_sl_multiplier": 0.5,
                        "min_recovery_pips": 2, # Old param, should be ignored/overridden by logic
                        "recovery_window_minutes": 60,
                        "resume_to_next_level_on_success": True
                    }
                }
            },
            "symbol_config": {
                "EURUSD": {"pip_size": 0.0001, "pip_value_per_std_lot": 10.0}
            }
        }
    def get(self, key, default=None): return self.data.get(key, default)

class MockTrendAnalyzer:
    def get_current_trend(self, symbol): return "BULLISH"
    def is_aligned(self, dir, trend): return True

class MockChain:
    def __init__(self, **kwargs):
        for k, v in kwargs.items(): setattr(self, k, v)
        if not hasattr(self, 'metadata'): self.metadata = {}

# Import REAL ReEntryManager (to test the PATCHED logic)
from src.managers.reentry_manager import ReEntryManager

async def run_simulation():
    print("\n" + "="*50)
    print("PHASE 4 AUDIT: 70% RECOVERY LOGIC VERIFICATION")
    print("="*50)
    
    # Setup Logic
    config = MockConfig()
    manager = ReEntryManager(config)
    manager.trend_analyzer = MockTrendAnalyzer() # Inject mock trend analyzer
    
    # Setup Scenario
    # Buy Entry: 1.1000
    # SL: 1.0900 (100 pips distance)
    # SL Hit -> Recovery Mode
    
    chain = MockChain(
        chain_id="CHAIN_70_PCT_TEST",
        status="recovery_mode",
        symbol="EURUSD",
        direction="buy",
        original_sl_distance=0.0100, # 100 pips
        current_level=1,
        max_level=5,
        metadata={
            "recovery_sl_price": 1.0900, # SL Level
            "recovery_started_at": datetime.now().isoformat(),
            "applied_sl_pips": 100
        }
    )
    
    current_sl = 1.0900
    target_recovery = 0.0100 * 0.70 # 0.0070 (70 pips)
    target_price = 1.0970
    
    print(f"Scenario Setup:")
    print(f"  Direction: BUY")
    print(f"  SL Level: {current_sl:.4f}")
    print(f"  Original SL Distance: 100 pips")
    print(f"  Required Recovery: 70% (70 pips)")
    print(f"  Target Price: {target_price:.4f}")
    
    # TEST 1: Minor Recovery (+10 pips)
    # Logic should REJECT this (unlike old logic which accepted +1 pip)
    price_minor = 1.0910
    print(f"\n[TEST 1] Testing Price: {price_minor:.4f} (+10 pips)")
    
    result_1 = manager.check_sl_hunt_recovery(chain, price_minor)
    print(f"  Result: {result_1['eligible']}")
    print(f"  Reason: {result_1['reason']}")
    
    if not result_1['eligible'] and "Price not recovered 70%" in result_1['reason']:
        print("  ✅ PASS: correctly rejected minor recovery")
    else:
        print("  ❌ FAIL: accepted minor recovery or wrong reason")

    # TEST 2: Major Recovery (+70 pips)
    # Logic should ACCEPT this
    price_major = 1.0970
    print(f"\n[TEST 2] Testing Price: {price_major:.4f} (+70 pips - Exact Threshold)")
    
    result_2 = manager.check_sl_hunt_recovery(chain, price_major)
    print(f"  Result: {result_2['eligible']}")
    if result_2['eligible']:
        print("  ✅ PASS: correctly accepted 70% recovery")
    else:
         print(f"  ❌ FAIL: rejected valid recovery ({result_2['reason']})")
         
    # TEST 3: Major Recovery (+75 pips)
    price_super = 1.0975
    print(f"\n[TEST 3] Testing Price: {price_super:.4f} (+75 pips - Above Threshold)")
    result_3 = manager.check_sl_hunt_recovery(chain, price_super)
    if result_3['eligible']:
        print("  ✅ PASS: correctly accepted >70% recovery")
    else:
         print(f"  ❌ FAIL: rejected valid recovery")

    print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(run_simulation())
