import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

# --- MOCKS ---

class MockMT5Client:
    def __init__(self):
        self.prices = {"EURUSD": 1.1000}
        self.account_info = {"margin": 100.0, "balance": 5000.0, "equity": 5000.0}
        self.positions = []
        
    def get_current_price(self, symbol):
        return self.prices.get(symbol, 0.0)
    
    def get_margin_level(self):
        if self.account_info["margin"] <= 0: return 0.0
        return (self.account_info["equity"] / self.account_info["margin"]) * 100
        
    def get_free_margin(self):
        return self.account_info["equity"] - self.account_info["margin"]
        
    def get_account_info_detailed(self):
        return self.account_info
        
    def get_positions(self):
        return self.positions
        
    def get_account_balance(self):
        return self.account_info["balance"]
    
    def place_order(self, **kwargs):
        print(f"    [MT5] PLACING ORDER: {kwargs}")
        return 12345
        
    def close_position(self, ticket):
        print(f"    [MT5] CLOSING POSITION #{ticket} (Emergency)")
        return True

class MockTrendingManager:
    def check_logic_alignment(self, symbol, logic):
        return {"aligned": True, "direction": "BULLISH" if "buy" in logic.lower() or "LOGIC" in logic else "BEARISH"}

class MockProfitBookingReEntryManager:
    def check_recoveries(self):
        # Always return empty logic for basic test unless we want to test this specific flow
        print("    [Watchman] >> Waking up ProfitManager (Checking Recoveries)")
        return []

class MockReEntryManager:
    def __init__(self):
        self.active_chains = {}
        self.trend_analyzer = None

    def check_autonomous_reentry(self):
        return []

    def create_chain(self, *args):
        pass

class MockRiskManager:
    def get_fixed_lot_size(self, balance): return 0.1

class MockTradingEngine:
    def __init__(self):
        self.risk_manager = MockRiskManager()
        self.profit_booking_reentry_manager = MockProfitBookingReEntryManager()
        
    async def place_recovery_order(self, **kwargs):
        print(f"    [Engine] EXECUTING RECOVERY: {kwargs}")
        return 999
        
    # Add telegram bot mock
    class MockBot:
        def send_message(self, msg): print(f"    [Bot] {msg}")
    telegram_bot = MockBot()

class MockConfig:
    def __getitem__(self, key):
        if key == "re_entry_config":
            return {
                "price_monitor_interval_seconds": 0.1, # Fast simulation
                "sl_hunt_reentry_enabled": True,
                "tp_reentry_enabled": True,
                "exit_continuation_enabled": True,
                "tp_continuation_price_gap_pips": 2.0
            }
        if key == "symbol_config":
            return {"EURUSD": {"pip_size": 0.0001}}
        return {}
    def get(self, key, default=None):
        if key == "symbol_config": return {"EURUSD": {"pip_size": 0.0001}}
        return default

# --- AUDIT SCRIPT ---

async def run_watchman_audit():
    print("="*60)
    print("WATCHMAN AUDIT: PRICE MONITOR STRESS TEST")
    print("="*60)
    
    # 1. Setup
    config = MockConfig()
    mt5 = MockMT5Client()
    trend_manager = MockTrendingManager()
    engine = MockTradingEngine()
    reentry_manager = MockReEntryManager()
    
    # Import service (assuming in path)
    from src.services.price_monitor_service import PriceMonitorService
    
    # Init service
    service = PriceMonitorService(
        config, mt5, reentry_manager, trend_manager, None, engine
    )
    
    # Mock the execute methods to avoid complex dependencies
    async def mock_execute_sl_hunt(*args):
        print(f"    [Watchman] >> EXECUTING SL HUNT RE-ENTRY for {args[0]}")
        return True
    
    async def mock_execute_tp_cont(*args):
        print(f"    [Watchman] >> EXECUTING TP CONTINUATION for {args[0]}")
        return True
        
    service._execute_sl_hunt_reentry = mock_execute_sl_hunt
    service._execute_tp_continuation_reentry = mock_execute_tp_cont
    
    # 2. Inject Pending Items (The Audit Targets)
    print("\n[SETUP] Injecting Pending Monitoring Targets:")
    
    # Target 1: SL Hunt (Needs to hit 1.0980)
    service.sl_hunt_pending["EURUSD"] = [{
        "target_price": 1.0980,
        "direction": "buy",
        "chain_id": "SL_TEST_CHAIN",
        "logic": "LOGIC1",
        "sl_price": 1.0950
    }]
    print("  - Added SL Hunt Target: Buy EURUSD @ 1.0980")
    
    # Target 2: TP Continuation (Needs to hit 1.1050)
    service.tp_continuation_pending["EURUSD"] = [{
        "tp_price": 1.1030,
        "direction": "buy",
        "chain_id": "TP_TEST_CHAIN",
        "logic": "LOGIC1"
    }]
    print("  - Added TP Constinuation Base: 1.1030 (Target: 1.1050 with 20 pips gap)")
    
    # 3. Running Stress Test (50 Ticks)
    print("\n[STRESS TEST] Simulating 50 Price Ticks...")
    
    # Tick Stream Simulation
    
    start_price = 1.1000
    ticks = []
    
    # Generate Down trend
    for i in range(1, 26):
        ticks.append(1.1000 - (i * 0.0001)) # Ends at 1.0975
        
    # Generate Up trend
    for i in range(1, 30):
        ticks.append(1.0975 + (i * 0.0003)) # Fast recovery up to ~1.1062
        
    # Execution Loop
    detected_sl = False
    detected_tp = False
    
    for i, tick in enumerate(ticks):
        mt5.prices["EURUSD"] = tick
        
        # Check Opportunities manually (Simulation of interval)
        await service._check_all_opportunities()
        
        # Verification Checks logic inside mocks prints output
        # checks if lists cleared
        if "EURUSD" not in service.sl_hunt_pending and not detected_sl:
            print(f"✅ [TICK {i+1}] SL Hunt Triggered & Cleared at {tick:.5f}")
            detected_sl = True
            
        if "EURUSD" not in service.tp_continuation_pending and not detected_tp:
            print(f"✅ [TICK {i+1}] TP Continuation Triggered & Cleared at {tick:.5f}")
            detected_tp = True

    # 4. Margin Stress Test
    print("\n[MARGIN STRESS TEST]")
    mt5.account_info["margin"] = 4500.0 # Equity 5000 -> Level 111% (Warning)
    print(f"Action: Reducing Margin Level to 111% (Warning Zone)")
    await service._check_margin_health()
    
    mt5.account_info["margin"] = 5100.0 # Equity 5000 -> Level 98% (Critical)
    # Need a position to close
    mt5.positions = [{"ticket": 12345, "profit": -100.0}]
    print(f"Action: Reducing Margin Level to 98% (Critical Zone)")
    await service._check_margin_health()
    
    print("\n[AUDIT CONCLUSION]")
    if detected_sl and detected_tp:
        print("✅ PASS: Watchman successfully detected all targets.")
    else:
        print("❌ FAIL: Missed targets.")
        if not detected_sl: print("   - Missed SL Hunt")
        if not detected_tp: print("   - Missed TP Continuation")

if __name__ == "__main__":
    asyncio.run(run_watchman_audit())
