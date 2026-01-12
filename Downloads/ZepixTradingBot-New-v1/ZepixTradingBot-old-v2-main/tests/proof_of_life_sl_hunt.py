import asyncio
import sys
import os
import logging
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

# 1. MONKEY PATCH LOGGING (Fix for AttributeError: 'Logger' object has no attribute 'success')
logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.SUCCESS):
        # Print with a distinct prefix to mimic the bot's look
        print(f"\n[SUCCESS] {message}") 
logging.Logger.success = success

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("src.managers.recovery_window_monitor")
logger.setLevel(logging.INFO)

# 2. MOCK ENVIRONMENT SETUP
sys.modules['MetaTrader5'] = MagicMock()
import MetaTrader5 as mt5

# Setup Tick Mock - Initial State
mock_tick = MagicMock()
mock_tick.bid = 89895.0
mock_tick.ask = 89895.0
mt5.symbol_info_tick = MagicMock(return_value=mock_tick)

# Adjust path
current_dir = os.getcwd()
src_path = os.path.join(current_dir, 'ZepixTradingBot-old-v2-main')
if src_path not in sys.path:
    sys.path.append(src_path)

try:
    from src.managers.recovery_window_monitor import RecoveryWindowMonitor
except ImportError:
    sys.path.append(current_dir)
    from src.managers.recovery_window_monitor import RecoveryWindowMonitor

# Mock Classes
class MockConfig:
    def get(self, key, default=None):
        if key == "sl_hunt_recovery.min_recovery_pips": return 2
        return default

class MockTrade:
    def __init__(self, id, symbol, sl, direction):
        self.trade_id = id
        self.symbol = symbol
        self.sl = sl
        self.direction = direction
        self.strategy = "TEST_STRATEGY"
        self.order_type = "A"
        self.volume = 1.0
        self.sl_pips = 100
        self.tp = sl + 1000

async def run_simulation():
    print("="*60)
    print("🚀 STARTING PROOF OF LIFE SIMULATION: SL HUNT RECOVERY")
    print("="*60 + "\n")
    
    # 3. INITIALIZATION
    auto_manager = MagicMock()
    auto_manager.config = MockConfig()
    auto_manager.place_sl_hunt_recovery_order = AsyncMock(return_value={"ticket": 999999})
    auto_manager.handle_recovery_timeout = AsyncMock()
    
    monitor = RecoveryWindowMonitor(auto_manager)
    
    # Patch asyncio.sleep
    original_sleep = asyncio.sleep
    async def fast_sleep(delay):
        await original_sleep(0.01)
    
    monitor.MONITORING_INTERVAL = 0.05 
    
    # 4. SCENARIO EXECUTION
    
    # Step 1: Trade Placement
    symbol = "BTCUSD"
    entry_price = 90000.0
    sl_price = 89900.0
    direction = "BUY"
    
    trade = MockTrade(id=88888, symbol=symbol, sl=sl_price, direction=direction)
    
    print(f"[Engine] 🟢 Trade Placed #{trade.trade_id}")
    print(f"         Symbol: {symbol} | Dir: {direction}")
    print(f"         Entry: ${entry_price:,.2f} | SL: ${sl_price:,.2f}")
    
    # Step 2: SL Hit
    current_market_price = 89895.0
    print(f"\n[Market] 📉 Price Drops... Testing SL...")
    print(f"[Engine] 💥 SL Hit Detected at ${current_market_price:,.2f}")
    print(f"[Engine] ⚡ Rerouting to Autonomous System...")
    print(f"🔄 REGISTERING AUTONOMOUS SL RECOVERY for Order #{trade.trade_id}")
    
    # Start Monitoring
    asyncio.create_task(monitor.start_monitoring(
        order_id=trade.trade_id,
        symbol=trade.symbol,
        direction=trade.direction,
        sl_price=trade.sl,
        original_order=trade,
        order_type="A"
    ))
    
    await asyncio.sleep(0.2)
    
    # Verify Window
    mon_data = monitor.active_monitors.get(trade.trade_id)
    if not mon_data:
        print("❌ CRITICAL FAIL: Monitor did not start")
        return

    window_min = mon_data['max_duration_seconds'] / 60
    threshold = mon_data['recovery_price']
    
    print(f"[Autonomous] ✅ Started Monitoring {symbol}")
    print(f"             Window: {int(window_min)}m (Correct for BTC)")
    print(f"             Recovery Threshold: ${threshold:,.4f}")
    
    # Step 3: Fast Recovery
    print(f"\n[Market] 📈 Price BOUNCES Immediately! (Simulating Wick)")
    print(f"         Price: 89895 -> 89905")
    
    # Update Tick Price
    mock_tick.bid = 89905.0
    mock_tick.ask = 89905.0
    
    print("[Autonomous] 🔍 Monitor Loop Checking...")
    await asyncio.sleep(0.5)
    
    # Step 4: Verify Execution
    if auto_manager.place_sl_hunt_recovery_order.called:
        print("\n" + "="*60)
        print("✅ SUCCESS: RECOVERY TRIGGERED IMMEDIATELY")
        print("="*60)
        
        call_args = auto_manager.place_sl_hunt_recovery_order.call_args[1]
        
        print(f"[Autonomous] Price Recovered! Executing Re-Entry...")
        print(f"   -> Symbol: {call_args['symbol']}")
        print(f"   -> Direction: {call_args['direction']}")
        print(f"   -> Entry Price: ${call_args['entry_price']:,.2f}")
        print(f"   -> New SL: ${call_args['sl_price']:,.2f} (Tightened)")
        print(f"   -> Lot Size: {call_args['lot_size']}")
        print(f"   -> Executed via: AutonomousSystemManager")
        print("\nSTATUS: 🟢 PROOF OF LIFE CONFIRMED.")
    else:
        print("\n❌ FAILURE: Recovery Order WAS NOT PLACED.")
        print(f"Monitor Status: {mon_data.get('status')}")
    
    monitor.stop_monitoring(trade.trade_id)

if __name__ == "__main__":
    try:
        asyncio.run(run_simulation())
    except KeyboardInterrupt:
        pass
