
import asyncio
import sys
import io
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Fix for Windows Unicode output
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
from src.models import Trade, Alert

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system_health.log'), mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger("SYSTEM_HEALTH_CHECK")

# ---------------- MOCK COMPONENTS ----------------
class MockTelegramBot:
    def send_message(self, message):
        logger.info(f"📱 TELEGRAM: \n{message}\n" + "-"*30)
    
    def send_profit_recovery_notification(self, *args):
        logger.info(f"📱 TELEGRAM (Profit Recovery): {args}")

    def send_sl_hunt_notification(self, *args):
        logger.info(f"📱 TELEGRAM (SL Hunt): {args}")

class MockDB:
    def save_trade(self, trade):
        logger.info(f"💾 DB: Trade Saved #{trade.trade_id} Status={trade.status}")

    def update_trade_status(self, trade):
        logger.info(f"💾 DB: Status Updated #{trade.trade_id} -> {trade.status}")

    def get_active_session(self):
        return None

    def save_session(self, session):
        pass

# ---------------- SIMULATION SCRIPT ----------------
async def run_system_health_check():
    logger.info("\n🏥 STARTING COMPLETE SYSTEM HEALTH CHECK (V3 + LEGACY REGRESSION)")
    logger.info("="*80)

    # 1. SETUP & INITIALIZATION
    try:
        config = Config()
        config.config["simulate_orders"] = True
        config.config['risk_management'] = {
            "max_daily_loss": 50.0,  # Small limit for testing
            "max_drawdown": 10.0,
            "max_open_trades": 5
        }
        
        # Ensure V3 config exists
        if "v3_integration" not in config.config:
            config.config["v3_integration"] = {"enabled": True}

        mt5_client = MT5Client(config.config)
        mt5_client.initialize() # Mocked/Simulated
        
        risk_manager = RiskManager(config.config)
        alert_processor = AlertProcessor(config.config)
        telegram_bot = MockTelegramBot()
        
        # Initialize Engine with Mocks
        engine = TradingEngine(config, risk_manager, mt5_client, telegram_bot, alert_processor)
        engine.db = MockDB() # Inject mock DB
        engine.open_trades = [] # Reset state
        
        # Verify wiring
        if engine.alert_processor.trend_manager is None:
            raise Exception("CRITICAL: AlertProcessor not linked to TrendManager!")

        logger.info("✅ PHASE 1: Initialization & Wiring Check PASSED")
        
    except Exception as e:
        logger.error(f"❌ PHASE 1 FAlLED: {e}")
        return

    # 2. LEGACY ALERT REGRESSION TEST
    logger.info("\n🧪 PHASE 2: LEGACY ALERT REGRESSION TEST")
    try:
        # 2.1 Setup Signal Alignment (Force Auto Trends)
        engine.trend_manager.update_trend("EURUSD", "1h", "bull")
        engine.trend_manager.update_trend("EURUSD", "15m", "bull")
        
        legacy_payload = {
            "symbol": "EURUSD",
            "tf": "5m", # Requires 1h+15m alignment for LOGIC1
            "type": "entry",
            "signal": "buy",
            "price": 1.1050,
            "strategy": "LOGIC1"
        }
        
        logger.info(f"   Input: Legacy BUY on EURUSD (LOGIC1)")
        await engine.process_alert(legacy_payload)
        
        # Check if trade placed
        is_legacy_placed = any(t.symbol == "EURUSD" and t.direction == "BUY" for t in engine.open_trades)
        if is_legacy_placed:
             logger.info("✅ PHASE 2: Legacy Entry Execution PASSED")
        else:
             logger.error("❌ PHASE 2: Legacy Entry Execution FAILED (Trade not in list)")

    except Exception as e:
        logger.error(f"❌ PHASE 2 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

    # 3. V3 INTEGRATION TEST (Quick Sanity)
    logger.info("\n🧪 PHASE 3: V3 INTEGRATION SANITY CHECK")
    try:
        v3_payload = {
            "type": "entry_v3",
            "signal_type": "Institutional_Launchpad",
            "symbol": "GBPUSD",
            "direction": "sell",
            "tf": "15",
            "price": 1.2500,
            "consensus_score": 8,
            "sl_price": 1.2550,
            "tp1_price": 1.2400,
            "tp2_price": 1.2300,
            "mtf_trends": "-1,-1,-1,-1,-1,-1",
            "position_multiplier": 1.0,
            "market_trend": -1
        }
        
        logger.info(f"   Input: V3 SELL on GBPUSD")
        await engine.process_alert(v3_payload)
        
        # Should create Dual Orders (2 trades)
        gbp_trades = [t for t in engine.open_trades if t.symbol == "GBPUSD"]
        if len(gbp_trades) == 2:
            logger.info(f"✅ PHASE 3: V3 Dual Order Placement PASSED ({len(gbp_trades)} trades)")
        else:
            logger.error(f"❌ PHASE 3: V3 Dual Order Count FAILED (Got {len(gbp_trades)}, expected 2)")

    except Exception as e:
        logger.error(f"❌ PHASE 3 EXCEPTION: {e}")

    # 4. RISK MANAGEMENT & SAFETY TEST
    logger.info("\n🧪 PHASE 4: RISK MANAGEMENT & SAFETY")
    try:
        # Simulate triggering max daily loss
        risk_manager.daily_loss = 60.0 # Limit is 50.0
        
        risky_payload = {
            "symbol": "USDJPY",
            "tf": "1h",
            "type": "entry",
            "signal": "buy",
            "price": 150.00,
            "strategy": "LOGIC3"
        }
        
        logger.info("   Input: New Trade request while Daily Loss > Limit")
        await engine.process_alert(risky_payload)
        
        usdjpy_trades = [t for t in engine.open_trades if t.symbol == "USDJPY"]
        if len(usdjpy_trades) == 0:
            logger.info("✅ PHASE 4: Daily Loss Limit Block PASSED (Trade correctly rejected)")
        else:
            logger.error("❌ PHASE 4: Daily Loss Limit FAILED (Trade was placed)")
            
    except Exception as e:
        logger.error(f"❌ PHASE 4 EXCEPTION: {e}")

    # 5. MIXED MODE INTEROPERABILITY
    logger.info("\n🧪 PHASE 5: MIXED MODE INTEROPERABILITY")
    try:
        # V3 Exit signal should close LEGACY trades too
        # Create a Legacy Trade manually
        legacy_trade = Trade(
            symbol="AUDUSD", 
            entry=0.6500, 
            sl=0.6400, 
            tp=0.6600, 
            lot_size=0.1, 
            direction="BUY", 
            strategy="LEGACY_LOGIC",
            open_time=datetime.now().isoformat()
        )
        legacy_trade.trade_id = 99999
        legacy_trade.ticket = 99999
        engine.open_trades.append(legacy_trade)
        engine.risk_manager.add_open_trade(legacy_trade)
        
        logger.info("   Input: Created Legacy AUDUSD BUY trade")
        logger.info("   Action: Sending V3 Bearish_Exit")
        
        exit_payload = {
            "type": "exit_v3",
            "signal_type": "Bearish_Exit", # Should close BUYs
            "symbol": "AUDUSD",
            "direction": "neutral",
            "tf": "15",
            "price": 0.6550,
            "consensus_score": 0,
            "position_multiplier": 1.0,
            "mtf_trends": "1,1,1,1,1,1",
            "market_trend": 0
        }
        
        await engine.process_alert(exit_payload)
        
        # Verify closure
        is_open = any(t.trade_id == 99999 for t in engine.open_trades)
        if not is_open:
            logger.info("✅ PHASE 5: V3 Exit closing Legacy Trade PASSED")
        else:
            logger.error("❌ PHASE 5: V3 Exit closing Legacy Trade FAILED")
            
    except Exception as e:
        logger.error(f"❌ PHASE 5 EXCEPTION: {e}")


    logger.info("\n🏁 SYSTEM HEALTH CHECK COMPLETE")

if __name__ == "__main__":
    asyncio.run(run_system_health_check())
