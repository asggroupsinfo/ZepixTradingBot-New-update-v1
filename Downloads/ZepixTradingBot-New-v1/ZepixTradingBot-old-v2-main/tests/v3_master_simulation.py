
import asyncio
import sys
import io
import os
import json
import logging
from datetime import datetime

# Fix for Windows Unicode output - redundant but kept
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except:
    pass

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.trading_engine import TradingEngine
from src.config import Config
from src.managers.risk_manager import RiskManager
from src.clients.mt5_client import MT5Client
from src.processors.alert_processor import AlertProcessor
from src.v3_alert_models import ZepixV3Alert

# Setup Logging
# Use FileHandler mostly to avoid console encoding issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v3_simulation.log'), mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger("V3_SIMULATION")

class MockTelegramBot:
    def send_message(self, message):
        logger.info(f"TELEGRAM SENT: \n{message}\n" + "-"*30)

async def run_simulation():
    logger.info("STARTING V3 MASTER SIMULATION (100% HONEST TEST)")
    logger.info("="*60)

    # 1. Load Config & Force Simulation
    try:
        config = Config()
        config.config["simulate_orders"] = True
        # Ensure V3 config exists
        if "v3_integration" not in config.config:
            config.config["v3_integration"] = {
                "enabled": True,
                "bypass_trend_check_for_v3_entries": True,
                "mtf_pillars_only": ["15m", "1h", "4h", "1d"],
                "order_b_fixed_sl_risk": 10.00,
                "aggressive_reversal_signals": [
                    "Liquidity_Trap_Reversal",
                    "Golden_Pocket_Flip",
                    "Screener_Full_Bullish",
                    "Screener_Full_Bearish"
                ]
            }
        else:
            config.config["v3_integration"]["enabled"] = True
            
        logger.info("Config Loaded & Simulation Mode FORCED")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # 2. Initialize Components
    try:
        mt5_client = MT5Client(config.config)
        # Force initialization in simulation mode
        mt5_client.initialize()
        
        telegram_bot = MockTelegramBot()
        risk_manager = RiskManager(config.config)
        alert_processor = AlertProcessor(config.config)
        
        engine = TradingEngine(config, risk_manager, mt5_client, telegram_bot, alert_processor)
        logger.info("Trading Engine Initialized")
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        import traceback
        traceback.print_exc()
        return
        
    # Hack: Ensure engine has empty open trades list
    engine.open_trades = []

    # ==========================================
    # TEST SCENARIO 1: MTF 4-PILLAR UPDATE
    # ==========================================
    logger.info("\nTEST 1: MTF 4-Pillar Update (Trend Pulse)")
    
    pulse_payload = {
        "type": "trend_pulse_v3",
        "signal_type": "Trend_Pulse",
        "symbol": "XAUUSD",
        "tf": "15",
        "direction": "neutral", # Required
        "price": 2650.0,
        "consensus_score": 0,
        "position_multiplier": 1.0, # Valid range 0.1-2.0
        "mtf_trends": "1,1,-1,1,1,1", # 1m=1, 5m=1, 15m=-1, 1H=1, 4H=1, 1D=1
        "market_trend": 0 # Required
    }
    
    # Process alert via update_mtf_trends directly or process_alert routing
    try:
        engine.alert_processor.process_mtf_trends(pulse_payload["mtf_trends"], "XAUUSD")
        
        # Verify ONLY indices 2,3,4,5 updated
        t15m = engine.trend_manager.get_trend("XAUUSD", "15m")
        t1h = engine.trend_manager.get_trend("XAUUSD", "1h")
        t4h = engine.trend_manager.get_trend("XAUUSD", "4h")
        t1d = engine.trend_manager.get_trend("XAUUSD", "1d")
        
        if t15m == "BEARISH" and t1h == "BULLISH" and t4h == "BULLISH" and t1d == "BULLISH":
            logger.info("SCENARIO 1 PASSED: MTF Trends updated correctly (15m=-1, others=1)")
        else:
            logger.error(f"SCENARIO 1 FAILED: {t15m}, {t1h}, {t4h}, {t1d}")
    except Exception as e:
         logger.error(f"SCENARIO 1 EXCEPTION: {e}")

    # ==========================================
    # TEST SCENARIO 2: V3 ENTRY (HYBRID SL & MULTIPLIER)
    # ==========================================
    logger.info("\nTEST 2: V3 Entry Execution (Hybrid SL & Multiplier)")
    
    entry_payload = {
        "type": "entry_v3",
        "signal_type": "Institutional_Launchpad",
        "symbol": "XAUUSD",
        "direction": "buy",
        "tf": "15",
        "price": 2650.0,
        "consensus_score": 8,
        "sl_price": 2640.0, # V3 Smart SL
        "tp1_price": 2660.0,
        "tp2_price": 2670.0,
        "mtf_trends": "1,1,1,1,1,1",
        "position_multiplier": 0.8,
        "market_trend": 1
    }
    
    try:
        # Run process_alert
        success = await engine.process_alert(entry_payload)
        
        if success:
            logger.info("SCENARIO 2 PASSED: Entry processed successfully")
        else:
            logger.error("SCENARIO 2 FAILED: Entry processing returned False")
    except Exception as e:
        logger.error(f"SCENARIO 2 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

    # ==========================================
    # TEST SCENARIO 3: AGGRESSIVE REVERSAL
    # ==========================================
    logger.info("\nTEST 3: Aggressive Reversal (Liquidity Trap)")
    
    # 3.1 Setup: Create a fake conflicting position first
    # Minimal trade object mimicking what the engine expects
    class FakeTrade:
        def __init__(self, id, sym, direct):
            self.trade_id = id
            self.symbol = sym
            self.direction = direct
            self.status = "open"
            self.entry_price = 2650.0
            self.sl = 2640.0
            self.tp = 2660.0
            self.lot_size = 0.1
            self.profit = -5.0
            self.ticket = id
            
    fake_trade = FakeTrade(12345, "XAUUSD", "BUY")
    engine.open_trades.append(fake_trade)
    logger.info("   -> Created fake BUY position for reversal test")
    
    # 3.2 Send Reversal Signal
    reversal_payload = {
        "type": "entry_v3",
        "signal_type": "Liquidity_Trap_Reversal", # Aggressive
        "symbol": "XAUUSD",
        "direction": "sell",
        "tf": "15",
        "price": 2650.0,
        "consensus_score": 9,
        "sl_price": 2660.0,
        "tp1_price": 2640.0, 
        "tp2_price": 2630.0,
        "mtf_trends": "-1,-1,-1,-1,-1,-1",
        "position_multiplier": 1.0,
        "market_trend": -1
    }
    
    try:
        await engine.process_alert(reversal_payload)
        
        # 3.3 Verify fake trade removed/closed (it should be removed from open_trades by close logic)
        found = False
        for t in engine.open_trades:
            if t.trade_id == 12345:
                found = True
                break
                
        if not found:
             logger.info("SCENARIO 3 PASSED: Conflicting position closed aggressively")
        else:
             logger.error("SCENARIO 3 FAILED: Conflicting position remains open")
    except Exception as e:
        logger.error(f"SCENARIO 3 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

    # ==========================================
    # TEST SCENARIO 4: V3 EXIT (Bullish Exit)
    # ==========================================
    logger.info("\nTEST 4: V3 Exit (Bullish Exit - Close SELLs)")
    
    # 4.1 Create fake SELL position
    fake_sell = FakeTrade(67890, "XAUUSD", "SELL")
    engine.open_trades.append(fake_sell)
    
    exit_payload = {
        "type": "exit_v3",
        "signal_type": "Bullish_Exit",
        "symbol": "XAUUSD",
        "direction": "neutral",
        "tf": "15",
        "price": 2645.0, # In profit
        "consensus_score": 0,
        "position_multiplier": 1.0, # valid value
        "mtf_trends": "1,1,1,1,1,1", # Valid 6 values
        "market_trend": 1
    }
    
    try:
        await engine.process_alert(exit_payload)
        
        found = False
        for t in engine.open_trades:
            if t.trade_id == 67890:
                found = True
                break
        
        if not found:
            logger.info("SCENARIO 4 PASSED: SELL position closed on Bullish Exit")
        else:
            logger.error("SCENARIO 4 FAILED: SELL position remains open")
    except Exception as e:
        logger.error(f"SCENARIO 4 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

    logger.info("\nSIMULATION COMPLETE")

if __name__ == "__main__":
    asyncio.run(run_simulation())
