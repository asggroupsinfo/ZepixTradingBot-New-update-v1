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

def verify_user_table():
    print("🚀 Verifying User Table Implementation (Strict Check)\n")
    
    manager = SessionManager()
    
    # CASE 1: Asian Session (05:00 - 13:30)
    # Test Time: 06:00 AM
    t1 = datetime(2024, 1, 1, 6, 0, 0)
    print(f"🔹 Testing Asian Session (Time: {t1.time()})")
    
    # Allowed: USDJPY, AUDJPY, AUDUSD, NZDUSD
    # Blocked: EURUSD, GBPUSD, GBPJPY (User specifically marked X)
    
    checks = {
        "USDJPY": True,
        "AUDJPY": True,
        "AUDUSD": True,
        "NZDUSD": True,
        "EURUSD": False,
        "GBPUSD": False,
        "EURJPY": False,
        "GBPJPY": False
    }
    
    for sym, expected in checks.items():
        allowed, reason = manager.check_trade_allowed(sym, current_time=t1)
        status = "✅ PASS" if allowed == expected else "❌ FAIL"
        scaa = "Allowed" if allowed else "Blocked"
        print(f"   {status}: {sym} is {scaa} (Expected: {'Allowed' if expected else 'Blocked'})")
        if allowed != expected:
            print(f"      Reason: {reason}")
            
    # CASE 2: London Session (13:30 - 18:30)
    # Test Time: 14:00 PM
    t2 = datetime(2024, 1, 1, 14, 0, 0)
    print(f"\n🔹 Testing London Session (Time: {t2.time()})")
    
    # Allowed: EURUSD, GBPUSD, EURGBP, GBPJPY, EURJPY, XAUUSD
    checks = {
        "EURUSD": True,
        "GBPUSD": True,
        "EURGBP": True,
        "GBPJPY": True,
        "EURJPY": True,
        "XAUUSD": True,
        "USDJPY": False # Not in London list
    }
    
    for sym, expected in checks.items():
        allowed, reason = manager.check_trade_allowed(sym, current_time=t2)
        status = "✅ PASS" if allowed == expected else "❌ FAIL"
        scaa = "Allowed" if allowed else "Blocked"
        print(f"   {status}: {sym} is {scaa} (Expected: {'Allowed' if expected else 'Blocked'})")

    # CASE 3: Overlap Session (18:30 - 22:30)
    # Test Time: 19:00 PM
    t3 = datetime(2024, 1, 1, 19, 0, 0)
    print(f"\n🔹 Testing Overlap Session (Time: {t3.time()})")
    
    # Allowed: EURUSD, GBPUSD, XAUUSD, USDJPY
    checks = {
        "EURUSD": True,
        "GBPUSD": True,
        "XAUUSD": True,
        "USDJPY": True,
        "NZDUSD": False, # Not in Overlap list
        "AUDUSD": False  # Not in Overlap list
    }
    
    for sym, expected in checks.items():
        allowed, reason = manager.check_trade_allowed(sym, current_time=t3)
        status = "✅ PASS" if allowed == expected else "❌ FAIL"
        scaa = "Allowed" if allowed else "Blocked"
        print(f"   {status}: {sym} is {scaa} (Expected: {'Allowed' if expected else 'Blocked'})")

    # CASE 4: NY Late Session (22:30 - 03:30)
    # Test Time: 23:00 PM
    t4 = datetime(2024, 1, 1, 23, 0, 0)
    print(f"\n🔹 Testing NY Late Session (Time: {t4.time()})")
    
    # Allowed: USDJPY, XAUUSD, USDCAD
    # Blocked: EURUSD, GBPUSD
    checks = {
        "USDJPY": True,
        "XAUUSD": True,
        "USDCAD": True,
        "EURUSD": False,
        "GBPUSD": False
    }
    
    for sym, expected in checks.items():
        allowed, reason = manager.check_trade_allowed(sym, current_time=t4)
        status = "✅ PASS" if allowed == expected else "❌ FAIL"
        scaa = "Allowed" if allowed else "Blocked"
        print(f"   {status}: {sym} is {scaa} (Expected: {'Allowed' if expected else 'Blocked'})")

    # CASE 5: Dead Zone (03:30 - 05:00)
    # Test Time: 04:00 AM
    t5 = datetime(2024, 1, 1, 4, 0, 0)
    print(f"\n🔹 Testing Dead Zone (Time: {t5.time()})")
    
    # Allowed: None
    checks = {
        "EURUSD": False,
        "USDJPY": False,
        "XAUUSD": False
    }
    
    for sym, expected in checks.items():
        allowed, reason = manager.check_trade_allowed(sym, current_time=t5)
        status = "✅ PASS" if allowed == expected else "❌ FAIL"
        scaa = "Allowed" if allowed else "Blocked"
        print(f"   {status}: {sym} is {scaa} (Expected: {'Allowed' if expected else 'Blocked'})")

if __name__ == "__main__":
    verify_user_table()
