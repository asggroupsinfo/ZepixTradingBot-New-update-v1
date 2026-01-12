from src.config import Config
from src.utils.profit_sl_calculator import ProfitBookingSLCalculator

# Create dummy config
class MockConfig:
    config = {}

config = MockConfig()
calc = ProfitBookingSLCalculator(config)

# Test DualOrderManager signature
# (alert.price, alert.signal, alert.symbol, lot_size, strategy)
entry = 1.1000
direction = "BUY"
symbol = "EURUSD"
lots = 0.05
strategy = "LOGIC1"

print("--- TESTING CALCULATOR ---")

try:
    sl_price, sl_dist = calc.calculate_sl_price(entry, direction, symbol, lots, strategy)
    print(f"Test 1 (DualOrder): Price={sl_price}, Dist={sl_dist}")
    
    # Verify values
    if sl_price < entry:
        print("✅ Test 1 Passed (Buy SL below Entry)")
    else:
        print("❌ Test 1 Failed (Buy SL inverted?)")
        
except Exception as e:
    print(f"❌ Test 1 Failed with error: {e}")

# Test Standard Argument Order (just in case)
# (entry, amount, lots, symbol, direction)
try:
    sl_price, sl_dist = calc.calculate_sl_price(entry, 10.0, lots, symbol, direction)
    print(f"Test 2 (Standard): Price={sl_price}, Dist={sl_dist}")
    
    if sl_price < entry:
        print("✅ Test 2 Passed")
    else:
        print("❌ Test 2 Failed")
except Exception as e:
    print(f"❌ Test 2 Failed with error: {e}")
