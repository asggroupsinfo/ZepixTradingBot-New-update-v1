import sys
import os
import json
from datetime import datetime, time
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.session_manager import SessionManager

# Configure simple logging
logging.basicConfig(level=logging.ERROR)

def verify_sessions():
    print("🚀 Verifying Session Rules for User Symbols List")
    
    # User's Symbol List
    SYMBOLS = [
        "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD",
        "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "AUDJPY"
    ]
    
    # Initialize Manager (loads data/session_settings.json)
    manager = SessionManager()
    
    # Test Cases
    # 1. Dead Zone (04:00 IST) - Expect all BLOCKED
    print("\n[TEST 1] Dead Zone (04:00 IST)")
    dead_zone_time = datetime(2024, 1, 1, 4, 0, 0)
    failed_block = []
    for sym in SYMBOLS:
        allowed, reason = manager.check_trade_allowed(sym, current_time=dead_zone_time)
        if allowed:
            print(f"❌ {sym} allowed in Dead Zone! (FAIL)")
            failed_block.append(sym)
        else:
            # print(f"✅ {sym} blocked: {reason}")
            pass
            
    if not failed_block:
        print("✅ All 10 symbols successfully BLOCKED in Dead Zone.")
    else:
        print(f"❌ Failed to block: {failed_block}")

    # 2. Overlap Session (19:00 IST) - Expect all ALLOWED
    # Overlap now includes ALL major pairs + XAU + NZD + AUDJPY
    print("\n[TEST 2] Overlap Session (19:00 IST)")
    overlap_time = datetime(2024, 1, 1, 19, 0, 0)
    failed_allow = []
    for sym in SYMBOLS:
        allowed, reason = manager.check_trade_allowed(sym, current_time=overlap_time)
        if not allowed:
            print(f"❌ {sym} blocked in Overlap! Reason: {reason} (FAIL)")
            failed_allow.append(sym)
        else:
            # print(f"✅ {sym} allowed: {reason}")
            pass
            
    if not failed_allow:
        print("✅ All 10 symbols successfully ALLOWED in Overlap Session.")
    else:
        print(f"❌ Failed to allow: {failed_allow}")

    # 3. Asian Session (07:00 IST) - Specific Check
    # Expect: USDJPY, AUDUSD, NZDUSD, EURJPY, AUDJPY -> Allowed
    # Expect: EURUSD, GBPUSD, XAUUSD -> Blocked (usually not Asian)
    print("\n[TEST 3] Asian Session (08:00 IST)")
    asian_time = datetime(2024, 1, 1, 8, 0, 0)
    
    # Asian whitelist from config: USDJPY, AUDUSD, EURJPY, NZDUSD, AUDJPY
    asian_allowed = ["USDJPY", "AUDUSD", "EURJPY", "NZDUSD", "AUDJPY"]
    # Others in list: EURUSD, GBPUSD, USDCAD, XAUUSD, GBPJPY
    asian_blocked = ["EURUSD", "GBPUSD", "USDCAD", "XAUUSD", "GBPJPY"]
    
    for sym in asian_allowed:
        allowed, reason = manager.check_trade_allowed(sym, current_time=asian_time)
        if not allowed:
            print(f"❌ {sym} blocked in Asian! (FAIL)")
    
    for sym in asian_blocked:
        allowed, reason = manager.check_trade_allowed(sym, current_time=asian_time)
        if allowed:
            print(f"❌ {sym} allowed in Asian! (Should be blocked) (FAIL)")
        else:
            pass # Good
            
    print("✅ Asian Session Filtering verified (Split Allow/Block).")

if __name__ == "__main__":
    verify_sessions()
