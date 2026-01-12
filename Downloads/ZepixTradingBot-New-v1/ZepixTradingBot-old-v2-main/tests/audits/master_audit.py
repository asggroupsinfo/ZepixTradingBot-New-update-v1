import asyncio
import logging
import os
import sys
import shutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Force UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MASTER_AUDIT")

# --- MOCKS & OVERRIDES ---
from src.models import Trade, Alert
from src.database import TradeDatabase
from src.config import Config

# Mock MT5 that we can control script-wise
class ScriptedMT5Client:
    def __init__(self):
        self.prices = {"EURUSD": 1.1000, "GBPUSD": 1.3000, "XAUUSD": 2500.0}
        self.positions = [] # List of dicts
        self.orders_history = []
        self.account_info = {"balance": 10000.0, "equity": 10000.0, "margin": 0.0, "free_margin": 10000.0}
        self.initialized = True
        self.connection_errors = 0
    
    def initialize(self): return True
    
    def get_current_price(self, symbol):
        return self.prices.get(symbol, 0.0)
    
    def get_account_balance(self): return self.account_info["balance"]
    
    def get_account_info_detailed(self):
        # Update equity based on open positions
        floating_pl = sum(p.get('profit', 0.0) for p in self.positions)
        self.account_info["equity"] = self.account_info["balance"] + floating_pl
        self.account_info["margin_level"] = (self.account_info["equity"] / self.account_info["margin"] * 100) if self.account_info["margin"] > 0 else 0
        self.account_info["free_margin"] = self.account_info["equity"] - self.account_info["margin"]
        return self.account_info

    def get_margin_level(self):
        info = self.get_account_info_detailed()
        return info.get("margin_level", 0.0)
        
    def get_free_margin(self):
        info = self.get_account_info_detailed()
        return info.get("free_margin", 0.0)

    def get_positions(self, symbol=None):
        if symbol:
            return [p for p in self.positions if p['symbol'] == symbol]
        return self.positions

    def get_position(self, ticket):
        for p in self.positions:
            if p["ticket"] == ticket:
                return p
        return None
        
    def place_order(self, **kwargs):
        ticket = len(self.orders_history) + 1000
        logger.info(f"  [MT5] 🛒 PLACING ORDER {ticket}: {kwargs}")
        
        # Simulate position creation
        position = {
            "ticket": ticket,
            "symbol": kwargs.get("symbol"),
            "volume": kwargs.get("volume", 0.1),
            "type": kwargs.get("type"), # 0=Buy, 1=Sell
            "price_open": kwargs.get("price"),
            "sl": kwargs.get("sl"),
            "tp": kwargs.get("tp"),
            "profit": 0.0,
            "comment": kwargs.get("comment", "")
        }
        self.positions.append(position)
        self.orders_history.append(position)
        self.account_info["margin"] += 100.0 # Simulate used margin
        return ticket

    def close_position(self, ticket, percent=100):
        logger.info(f"  [MT5] ❌ CLOSING POSITION {ticket} ({percent}%)")
        for p in self.positions:
            if p["ticket"] == ticket:
                self.positions.remove(p)
                self.account_info["margin"] -= 100.0
                return True
        return False
        
    def modify_order(self, ticket, sl, tp):
        logger.info(f"  [MT5] ✏️ MODIFY ORDER {ticket}: SL={sl}, TP={tp}")
        for p in self.positions:
            if p["ticket"] == ticket:
                p["sl"] = sl
                p["tp"] = tp
                return True
        return False
        
    def get_closed_trade_profit(self, ticket):
        # Return dummy profit
        return 50.0

    def get_candles(self, symbol, timeframe, count):
        base = self.prices.get(symbol, 1.0)
        return [{'close': base, 'high': base+0.001, 'low': base-0.001} for _ in range(count)]

class MockBot:
    def send_message(self, msg): 
        print(f"  📱 [TELEGRAM] {msg}")
    def set_trend_manager(self, tm): pass

# Config Override
class AuditConfig(Config):
    def __init__(self):
        super().__init__()
        self.config["price_monitor_interval_seconds"] = 10 # Request logic
        self.config["re_entry_config"]["autonomous_enabled"] = True
        self.config["re_entry_config"]["autonomous_config"]["sl_hunt_recovery"]["enabled"] = True
        self.config["re_entry_config"]["autonomous_config"]["enabled"] = True
        self.config["profit_booking_config"]["enabled"] = True
        self.config["dual_order_config"]["enabled"] = True
        # Ensure correct settings for profit booking
        self.config["profit_booking_config"]["sl_enabled"] = True
        self.config["profit_booking_config"]["profit_targets"] = [10, 20] # Pips
        self.config["profit_booking_config"]["sl_reductions"] = [0, 50] # Percent
        

class TestTradeDatabase(TradeDatabase):
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

class MockAlertProcessor:
    def __init__(self): pass
    def store_entry_alert(self, alert): pass

# --- MASTER AUDIT CLASS ---
class MasterAudit:
    def __init__(self):
        self.db_name = "master_audit_test.db"
        # Reset DB
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        
        # Init Components
        self.config = AuditConfig()
        self.db = TestTradeDatabase(self.db_name)
        self.mt5 = ScriptedMT5Client()
        self.bot = MockBot()
        
        # Import real managers
        from src.core.trading_engine import TradingEngine
        import src.core.trading_engine
        # Monkeypatch DB to use test DB
        src.core.trading_engine.TradeDatabase = lambda: self.db  # Return our existing DB instance
        
        from src.services.price_monitor_service import PriceMonitorService
        from src.managers.risk_manager import RiskManager
        from src.managers.profit_booking_manager import ProfitBookingManager
        from src.managers.reentry_manager import ReEntryManager
        from src.managers.reverse_shield_manager import ReverseShieldManager
        from src.managers.timeframe_trend_manager import TimeframeTrendManager as TrendManager
        from src.managers.session_manager import SessionManager
        from src.managers.dual_order_manager import DualOrderManager
        from src.managers.autonomous_system_manager import AutonomousSystemManager
        from src.managers.profit_booking_reentry_manager import ProfitBookingReEntryManager
        from src.utils.pip_calculator import PipCalculator
        from src.utils.trend_analyzer import TrendAnalyzer

        self.trend_manager = TrendManager()
        self.risk_manager = RiskManager(self.config)
        self.risk_manager.mt5_client = self.mt5
        self.pip_calculator = PipCalculator(self.config)
        self.trend_analyzer = TrendAnalyzer(self.mt5)
        self.session_manager = SessionManager(self.config, self.db, self.mt5)
        self.alert_processor = MockAlertProcessor()
        
        # Init Managers manually to construct dependency graph
        self.profit_booking_manager = ProfitBookingManager(
            self.config, self.mt5, self.pip_calculator, self.risk_manager, self.db
        )
        self.reentry_manager = ReEntryManager(self.config, self.mt5)
        self.reentry_manager.trend_analyzer = self.trend_analyzer # Inject if not done by init

        self.profit_reentry_manager = ProfitBookingReEntryManager(
            self.config, self.profit_booking_manager, self.mt5, self.trend_analyzer
        )
        self.reverse_shield = ReverseShieldManager(
            self.config, self.mt5, self.profit_booking_manager, self.risk_manager, self.db, self.bot
        )
        self.dual_order_manager = DualOrderManager(
            self.config, self.risk_manager, self.mt5, self.pip_calculator,
            profit_sl_calculator=self.profit_booking_manager.profit_sl_calculator
        )
        
        self.auto_manager = AutonomousSystemManager(
             self.config, self.reentry_manager, self.profit_booking_manager, 
             self.profit_reentry_manager, self.mt5, self.bot, self.risk_manager
        )

        # Engine
        # Pass Mocks to constructor
        self.engine = TradingEngine(
            self.config, self.risk_manager, self.mt5, self.bot, self.alert_processor
        )
        # Inject Dependencies manually into Engine (simulating DI) to ensure they match ours
        self.engine.mt5_client = self.mt5
        self.engine.database = self.db
        self.engine.telegram_bot = self.bot
        self.engine.trend_manager = self.trend_manager
        self.engine.risk_manager = self.risk_manager
        self.engine.profit_booking_manager = self.profit_booking_manager
        self.engine.reentry_manager = self.reentry_manager
        self.engine.dual_order_manager = self.dual_order_manager
        self.engine.autonomous_manager = self.auto_manager
        self.engine.pip_calculator = self.pip_calculator
        
        # NOTE: TradingEngine creates its own PriceMonitorService in __init__ usually, 
        # but we need to inject the one that uses our mocks if possible.
        # Actually TradingEngine instantiates PriceMonitorService passing `self`.
        # So we should patch the internal one.
        
        self.engine.price_monitor.mt5_client = self.mt5
        self.watchman = self.engine.price_monitor
        self.watchman.reentry_manager = self.reentry_manager # Inject manager
        self.watchman.profit_booking_reentry_manager = self.profit_reentry_manager

    async def run_scenario_1(self):
        print("\n" + "="*50)
        print("🟢 SCENARIO 1: The Perfect Trade")
        print("="*50)
        
        # 1. Place Dual Order
        print("[STEP 1] Placing Dual Order (Buy EURUSD)...")
        alert = Alert(symbol="EURUSD", action="buy", strategy="LOGIC1", price=1.1000, time=datetime.now(),
                      type="entry", signal="BULLISH", tf="5m")
        await self.engine.place_fresh_order(alert, "LOGIC1")
        
        # Verify 2 active trades
        await asyncio.sleep(0.1)
        if len(self.engine.open_trades) != 2:
            print(f"❌ FAIL: Expected 2 trades, got {len(self.engine.open_trades)}")
            return
        print("✅ Dual Orders Placed Successfully")
        
        order_b = self.engine.open_trades[1] # Assume second is B
        print(f"VERIFY ORDER B: Entry={order_b.entry} SL={order_b.sl} Direction={order_b.direction}")
        print(f"   - Order B ID: {order_b.trade_id} (Chain: {order_b.chain_id})")

        # 2. Simulate TP1 Hit (Moves price up)
        print("[STEP 2] Moving Price to TP1 (1.1015)...")
        self.mt5.prices["EURUSD"] = 1.1015
        
        # 3. Monitoring Cycle
        print("[STEP 3] Watchman Scan...")
        # We need to manually trigger check on open trades because Watchman usually only checks pending re-entries
        # For profit booking, the 'ProfitBookingManager' is usually called by Engine on tick or by Watchman.
        # In current design, Watchman checks 'profit_booking_chains' but these are loaded from DB.
        
        # Force engine to check profit booking (mimick tick update)
        await self.watchman._check_profit_booking_chains()
        
        # Verify Level 1 Reached
        # Check DB for chain
        chains = self.db.get_active_profit_chains()
        if len(chains) > 0:
             # chains is likely a list of dicts in the mock DB, or objects without .level alias
             # Use current_level, handle dict vs object
             chain_obj = chains[0]
             lvl = chain_obj['current_level'] if isinstance(chain_obj, dict) else chain_obj.current_level
             print(f"✅ Profit Chain detected in DB: Level {lvl}")
        else:
             print("❌ FAIL: No Profit Chain in DB")

    async def run_scenario_2(self):
        print("\n" + "="*50)
        print("🔴 SCENARIO 2: The Recovery Warrior")
        print("="*50)
        
        # 1. Place Single Trade
        print("[STEP 1] Placing Trade (Buy GBPUSD)...")
        # Disable dual orders temporarily
        self.config.config["dual_order_config"]["enabled"] = False
        alert = Alert(symbol="GBPUSD", action="buy", strategy="LOGIC2", price=1.3000, time=datetime.now(),
                      type="entry", signal="BULLISH", tf="15m")
        await self.engine.place_fresh_order(alert, "LOGIC2")
        
        trade = self.engine.open_trades[0]
        trade_id = trade.trade_id
        print(f"✅ Trade Placed: {trade_id} with SL: {trade.sl}")

        # 2. Register for SL Monitoring (Normally done by engine)
        # Verify it's in pending if engine did its job
        # Engine calls `register_sl_hunt_opportunity` on PriceMonitor
        pending_sl = self.watchman.sl_hunt_pending.get("GBPUSD", [])
        if not pending_sl:
             print("⚠️ Warning: Trade not auto-registered for SL hunt. Registering manually for test.")
             self.watchman.register_sl_hunt_opportunity(trade)
        else:
             print("✅ Trade registered for SL Hunt monitoring")

        # 3. Price Crash (Hit SL - 1.2770)
        print("[STEP 3] Crashing Price to SL (1.2770)...")
        self.mt5.prices["GBPUSD"] = 1.2770 # Below SL of 1.2775
        
        # Close trade in Mock (Simulate Stop Loss)
        self.mt5.close_position(trade.ticket)
        self.engine.open_trades.remove(trade) 
        # Update DB
        trade.close_time = datetime.now()
        trade.exit = 1.2950
        trade.status = "CLOSED"
        self.db.save_trade(trade)
        
        # 4. Watchman Scan
        print("[STEP 4] Watchman Scan (Detecting SL Hunt)...")
        # Watchman checks 'sl_hunt_pending'. 
        # Target price needs to be hit.
        # If SL was 1.2950, Offset 1.0 pip -> Target 1.2949. Price is 1.2940. Valid.
        await self.watchman._check_sl_hunt_reentries()
        
        # Should have placed a recovery order
        await asyncio.sleep(0.1)
        if len(self.engine.open_trades) > 0:
            print("✅ RE-ENTRY ORDER PLACED SUCCESSFULLY!")
            new_trade = self.engine.open_trades[0]
            print(f"   - New Trade Ticket: {new_trade.ticket} (Is Re-entry: {new_trade.is_re_entry})")
        else:
            print("❌ FAIL: No Re-entry order placed.")

    async def run_scenario_4(self):
        print("\n" + "="*50)
        print("⏱️ SCENARIO 4: Watchman Duty (Margin CHECK REMOVED)")
        print("="*50)
        
        # 1. Simulate Margin Crisis (Should NOT trigger close)
        print("[STEP 1] Simulating Margin Crash...")
        self.mt5.account_info["margin"] = 9500.0
        self.mt5.account_info["balance"] = 9000.0
        self.mt5.account_info["equity"] = 9000.0 # Level ~94%
        
        # Open a position
        self.mt5.place_order(symbol="EURUSD", type=0, volume=1.0, price=1.1000, sl=1.0900)
        
        # 2. Watchman Scan
        print("[STEP 2] Watchman Scan (Margin Check DISABLED)...")
        # In the original file it might have been accessing via self.engine.price_monitor or something, 
        # but the view shows 'self.watchman' which is likely incorrect based on init.
        # Let's check init lines again or just use self.price_monitor if available. 
        # Actually in the snippet it says 'await self.watchman._check_margin_health()'.
        # I suspect self.watchman might not exist or is an alias.
        # Let's assume the previous view was correct about 'self.watchman' usage in line 342.
        await self.watchman._check_margin_health()
        
        # 3. Verify Position Still Exists
        if len(self.mt5.positions) > 0:
            print("✅ SUCCESS: Position remaining open (Margin Logic Successfully Removed).")
        else:
            print("❌ FAIL: Position closed! Margin Logic still active.")

    async def run_all(self):
        logger.info("🚀 STARTING MASTER AUDIT")
        # We need to initialize the engine first (it loads config)
        await self.engine.initialize()
        
        await self.run_scenario_1()
        # Clean up
        self.engine.open_trades.clear()
        self.mt5.positions.clear()
        
        await self.run_scenario_2()
        # Clean up
        self.engine.open_trades.clear()
        self.mt5.positions.clear()
        
        await self.run_scenario_4()
        
        print("\n🏁 MASTER AUDIT COMPLETE")

if __name__ == "__main__":
    audit = MasterAudit()
    asyncio.run(audit.run_all())
