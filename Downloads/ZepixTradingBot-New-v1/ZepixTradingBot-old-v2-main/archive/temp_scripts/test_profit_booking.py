import sys
sys.path.insert(0, 'c:/Users/Ansh Shivaay Gupta/Downloads/ZepixTradingBot-old-v2-main/ZepixTradingBot-old-v2-main')

from src.config.config import Config
from src.managers.profit_booking_manager import ProfitBookingManager

try:
    config = Config('config/config.json')
    pbm = ProfitBookingManager(config, None)
    
    print("✅ PROFIT BOOKING MANAGER - WORKING")
    print(f"Target profit: ${pbm.target_profit}")
    print(f"Max levels: {pbm.max_levels}")
    print(f"Multipliers: {pbm.multipliers}")
    print(f"Enabled: {pbm.enabled}")
    
    # Test chain creation
    test_trade = type('obj', (object,), {
        'ticket': 12345,
        'symbol': 'XAUUSD',
        'entry_price': 2650.0,
        'sl': 2640.0,
        'volume': 0.1,
        'order_type': 'BUY',
        'strategy': 'LOGIC1'
    })()
    
    chain_id = pbm.create_profit_chain(test_trade)
    if chain_id:
        print(f"\n✅ Chain creation test: SUCCESS")
        print(f"Chain ID: {chain_id}")
    else:
        print("\n❌ Chain creation test: FAILED")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
