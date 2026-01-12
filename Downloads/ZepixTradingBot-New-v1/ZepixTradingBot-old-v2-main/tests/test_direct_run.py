"""Test running bot directly without uvicorn/FastAPI"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from clients.mt5_client import MT5Client
from clients.telegram_bot import TelegramBot
from core.risk_manager import RiskManager
from core.trading_engine import TradingEngine
from services.trend_manager import TrendManager
from services.price_monitor_service import PriceMonitorService
from managers.profit_booking_manager import ProfitBookingManager
from managers.reentry_manager import ReentryManager

async def main():
    print("="*70)
    print("DIRECT BOT TEST (NO UVICORN)")
    print("="*70)
    
    # Initialize components
    config = Config()
    mt5_client = MT5Client(config.get_all())
    telegram_bot = TelegramBot(config.get_all())
    risk_manager = RiskManager(config.get_all(), mt5_client, telegram_bot)
    trend_manager = TrendManager(config.get_all())
    price_monitor = PriceMonitorService(config.get_all(), mt5_client, telegram_bot)
    reentry_manager = ReentryManager(config.get_all(), mt5_client, telegram_bot, trend_manager)
    profit_manager = ProfitBookingManager(config.get_all(), mt5_client, telegram_bot)
    
    trading_engine = TradingEngine(
        config.get_all(),
        mt5_client,
        risk_manager,
        telegram_bot,
        trend_manager,
        price_monitor,
        reentry_manager,
        profit_manager
    )
    
    telegram_bot.set_dependencies(risk_manager, trading_engine)
    
    # Initialize trading engine
    success = await trading_engine.initialize()
    if not success:
        print("ERROR: Trading engine initialization failed")
        return
    
    print("✅ Trading engine initialized successfully")
    
    # Start telegram polling in thread
    import threading
    polling_thread = threading.Thread(target=telegram_bot.start_polling, daemon=True)
    polling_thread.start()
    print("✅ Telegram polling started")
    
    # Start background task
    trade_monitor_task = asyncio.create_task(trading_engine.manage_open_trades())
    print("✅ Trade monitor task started")
    
    print("="*70)
    print("BOT RUNNING - Press Ctrl+C to stop")
    print("="*70)
    
    # Wait forever
    try:
        await asyncio.Event().wait()  # Wait forever until interrupted
    except KeyboardInterrupt:
        print("\nShutting down...")
        trade_monitor_task.cancel()
        try:
            await trade_monitor_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
