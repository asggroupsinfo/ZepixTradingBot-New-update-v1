import asyncio
import sys
import os
import logging
import uuid
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

# 1. MONKEY PATCH LOGGING
logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.SUCCESS):
        print(f"\n[SUCCESS] {message}") 
logging.Logger.success = success

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("src.managers.profit_booking_manager")
logger.setLevel(logging.INFO)

# 2. MOCK ENVIRONMENT SETUP
sys.modules['MetaTrader5'] = MagicMock()
import MetaTrader5 as mt5

# Adjust path - Critical Fix for "No module named src"
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Go up one level to ZepixTradingBot-old-v2-main
if project_root not in sys.path:
    sys.path.append(project_root)

# Mock Imports from src
try:
    from src.managers.profit_booking_manager import ProfitBookingManager
    from src.managers.autonomous_system_manager import AutonomousSystemManager
    from src.models import Trade, ProfitBookingChain
except ImportError:
    # Fallback absolute path addition
    sys.path.append(os.getcwd())
    from src.managers.profit_booking_manager import ProfitBookingManager
    from src.managers.autonomous_system_manager import AutonomousSystemManager
    from src.models import Trade, ProfitBookingChain

# Mock Dependencies
class MockConfig(dict):
    def get(self, key, default=None):
        if key == "profit_booking_config":
            return {
                "enabled": True, 
                "min_profit": 7.0, 
                "multipliers": [1, 2, 4],
                "max_level": 4,
                "enabled_levels": {"1": True, "2": True, "3": True}
            }
        if key == "symbol_config":
            return {"XAUUSD": {"pip_size": 0.01, "pip_value_per_std_lot": 1.0}} 
        if key == "simulated_orders": return False
        if key == "rr_ratio": return 1.5
        return super().get(key, default)

class MockMT5Client:
    def __init__(self):
        self.get_current_price = MagicMock(return_value=2000.0)
        self.place_order = MagicMock(return_value=123456)
        self.get_account_balance = MagicMock(return_value=10000)
        self.get_position = MagicMock(return_value=True)

class MockRiskManager:
    def get_lot_size_for_logic(self, balance, logic):
        return 0.1 
    def add_open_trade(self, trade): pass

class MockDB:
    def save_profit_chain(self, chain): pass
    def save_profit_booking_order(self, *args): pass
    def save_profit_booking_event(self, *args): pass
    def save_trade(self, trade): pass

class MockBot:
    def send_message(self, msg):
        print(f"\n[Telegram] 📱 {msg.splitlines()[0]}...") 

class MockTradingEngine:
    def __init__(self):
        self.open_trades = []
        self.risk_manager = MockRiskManager()
        self.telegram_bot = MockBot()
        self.db = MockDB()
        self.trade_count = 0
        self.mt5_client = MockMT5Client()
    
    async def close_trade(self, trade, reason, price):
        print(f"[Engine] 🛑 Closing Order #{trade.trade_id} at ${price:.2f} (Reason: {reason})")
        trade.status = "closed"
        trade.pnl = 7.50 
        self.open_trades = [t for t in self.open_trades if t.trade_id != trade.trade_id]
        return True

async def run_simulation():
    print("="*60)
    print("🚀 STARTING PROOF OF LIFE SIMULATION: PROFIT OFFENSE SYSTEM")
    print("="*60 + "\n")
    
    # 3. INITIALIZATION
    config = MockConfig()
    mt5_client = MockMT5Client()
    risk_manager = MockRiskManager()
    db = MockDB()
    bot = MockBot()
    engine = MockTradingEngine()
    engine.mt5_client = mt5_client # Link client to engine
    
    profit_manager = ProfitBookingManager(config, mt5_client, MagicMock(), risk_manager, db)
    profit_manager.pip_calculator = MagicMock()
    profit_manager.pip_calculator.calculate_tp_price.return_value = 2010.0
    profit_manager.profit_sl_calculator = MagicMock()
    profit_manager.profit_sl_calculator.calculate_sl_price.return_value = (1990.0, 10.0)
    
    auto_manager = AutonomousSystemManager(config, MagicMock(), profit_manager, MagicMock(), mt5_client, bot)
    
    # 4. SCENARIO SETUP
    print("[Setup] 🌱 Creating Initial State: Level 0 Active")
    chain_id = "PROFIT_XAUUSD_TEST"
    
    chain = ProfitBookingChain(
        chain_id=chain_id,
        symbol="XAUUSD",
        direction="BUY",
        base_lot=0.1,
        current_level=0,
        max_level=4,
        total_profit=0.0,
        active_orders=[1001],
        status="ACTIVE",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        profit_targets=[7.0]*5,
        multipliers=[1, 2, 4, 8],
        sl_reductions=[0]*5,
        metadata={"strategy": "TEST"}
    )
    profit_manager.active_chains[chain_id] = chain
    
    trade = Trade(
        symbol="XAUUSD",
        entry=2000.00,
        sl=1990.00,
        tp=2100.00,
        lot_size=0.1,
        direction="BUY",
        strategy="TEST",
        open_time=datetime.now().isoformat(),
        profit_chain_id=chain_id,
        profit_level=0,
        order_type="PROFIT_TRAIL"
    )
    trade.trade_id = 1001
    engine.open_trades.append(trade)
    
    print(f"[Engine] 🟢 Order B Active #{trade.trade_id}")
    print(f"         Level: 0 | Lot: 0.1 | Target: $7.00")
    
    profit_manager.calculate_individual_pnl = MagicMock(return_value=7.50)
    
    print(f"\n[Market] 💰 Price Moves... PnL Hits $7.50 (Target $7.00)")
    print("[Autonomous] 🔄 Running Check Loop...")
    
    await auto_manager.run_autonomous_checks(engine.open_trades, engine)
    
    # Step 3: Verify Actions
    print("\n" + "="*60)
    print("🔍 VERIFICATION RESULTS")
    print("="*60)
    
    # 1. Did it detect and close?
    if trade.status == "closed":
        print("✅ SUCCESS: Trade Closed Automatically")
    else:
        print("❌ FAIL: Trade Still Open")
        
    # 2. Did Level Up happen?
    if chain.current_level == 1:
         print(f"✅ SUCCESS: Chain Leveled Up (0 -> {chain.current_level})")
    else:
         print(f"❌ FAIL: Chain Level {chain.current_level}")

    # 3. Were NEW orders placed?
    place_calls = mt5_client.place_order.call_args_list
    if len(place_calls) == 2:
        print(f"✅ SUCCESS: 2 New Orders Placed (Multiplier Worked!)")
        
        args1 = place_calls[0][1] # kwargs
        print(f"\n[Engine] 🚀 Placing Level 1 Orders:")
        print(f"   -> Order 1: {args1['symbol']} {args1['order_type']} | Lot: {args1['lot_size']} | Comment: {args1['comment']}")
        
        total_lots = sum([c[1]['lot_size'] for c in place_calls])
        print(f"   -> Total New Exposure: {total_lots:.1f} Lots (Double of 0.1)")
        
        print("\nSTATUS: 🟢 PROFIT SYSTEM PROOF OF LIFE CONFIRMED.")
    else:
        print(f"❌ FAIL: Incorrect Order Count. Expected 2, got {len(place_calls)}")

if __name__ == "__main__":
    try:
        asyncio.run(run_simulation())
    except KeyboardInterrupt:
        pass
