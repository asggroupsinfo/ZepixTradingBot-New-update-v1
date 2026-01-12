import json
import os
import sys
from src.config import Config
from src.managers.risk_manager import RiskManager
from src.utils.pip_calculator import PipCalculator
from unittest.mock import MagicMock

# Create a mock config
config_data = {
    "account_balance": 10000,
    "risk_per_trade": 0.01,
    "risk_tier": "conservative",
    "sl_system": "sl-1",
    "sl_systems": {
        "sl-1": {
            "symbols": {
                "XAUUSD": {
                    "10000": {"sl_pips": 50, "risk_dollars": 50}
                }
            }
        }
    },
    "symbol_config": {
        "XAUUSD": {
            "pip_size": 0.1,
            "pip_value_per_std_lot": 10
        }
    },
    "timeframe_specific_config": {
        "enabled": True,
        "LOGIC1": {"lot_multiplier": 1.0, "sl_multiplier": 1.0, "recovery_window_minutes": 30},
        "LOGIC2": {"lot_multiplier": 1.0, "sl_multiplier": 1.0, "recovery_window_minutes": 60},
        "LOGIC3": {"lot_multiplier": 1.5, "sl_multiplier": 1.2, "recovery_window_minutes": 120}
    },
    "lot_sizes": {
        "conservative": 0.05
    },
    "fixed_lot_sizes": {
         "5000": 0.01,
         "10000": 0.05,
         "25000": 0.10,
         "50000": 0.25,
         "100000": 0.50
    }
}

class MockConfig:
    def __init__(self, data):
        self.config = data
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def __getitem__(self, key):
        return self.config[key]

def test_timeframe_logic():
    print("🧪 Starting Timeframe Logic Verification...")
    
    mock_config = MockConfig(config_data)
    
    # Initialize managers
    risk_manager = RiskManager(mock_config)
    pip_calculator = PipCalculator(mock_config)
    
    # 1. Test Lot Size Calculation
    print("\n[Test 1] Lot Size Calculation")
    
    base_balance = 10000
    base_lot = risk_manager.get_fixed_lot_size(base_balance)
    print(f"Base Lot Size: {base_lot}")
    
    # LOGIC1 (1.0x)
    lot1 = risk_manager.get_lot_size_for_logic(base_balance, "LOGIC1")
    expected_lot1 = base_lot * 1.0
    print(f"LOGIC1 Lot: {lot1} (Expected: {expected_lot1}) -> {'✅ PASS' if abs(lot1 - expected_lot1) < 0.001 else '❌ FAIL'}")
    
    # LOGIC3 (1.5x)
    lot3 = risk_manager.get_lot_size_for_logic(base_balance, "LOGIC3")
    expected_lot3 = base_lot * 1.5
    print(f"LOGIC3 Lot: {lot3} (Expected: {expected_lot3}) -> {'✅ PASS' if abs(lot3 - expected_lot3) < 0.001 else '❌ FAIL'}")
    
    # Disabled Config
    mock_config.config["timeframe_specific_config"]["enabled"] = False
    lot3_disabled = risk_manager.get_lot_size_for_logic(base_balance, "LOGIC3")
    print(f"LOGIC3 Lot (Disabled): {lot3_disabled} (Expected: {base_lot}) -> {'✅ PASS' if abs(lot3_disabled - base_lot) < 0.001 else '❌ FAIL'}")
    
    mock_config.config["timeframe_specific_config"]["enabled"] = True
    
    # 2. Test SL Calculation
    print("\n[Test 2] SL Calculation")
    
    entry_price = 2000.0
    direction = "buy"
    
    # Base SL Distance (from config: 50 pips * 0.1 = 5.0 price)
    # calculate_sl_price(symbol, entry, direction, lot, balance, sl_adjustment=1.0, logic=None)
    
    # LOGIC1 (1.0x)
    sl_price1, sl_dist1 = pip_calculator.calculate_sl_price("XAUUSD", entry_price, direction, base_lot, base_balance, logic="LOGIC1")
    base_dist = 5.0 # 50 pips * 0.1
    print(f"LOGIC1 SL Dist: {sl_dist1} (Expected: {base_dist}) -> {'✅ PASS' if abs(sl_dist1 - base_dist) < 0.001 else '❌ FAIL'}")
    
    # LOGIC3 (1.2x)
    sl_price3, sl_dist3 = pip_calculator.calculate_sl_price("XAUUSD", entry_price, direction, base_lot, base_balance, logic="LOGIC3")
    expected_dist3 = base_dist * 1.2
    print(f"LOGIC3 SL Dist: {sl_dist3} (Expected: {expected_dist3}) -> {'✅ PASS' if abs(sl_dist3 - expected_dist3) < 0.001 else '❌ FAIL'}")

    print("\n✅ Verification Complete!")

if __name__ == "__main__":
    test_timeframe_logic()
