#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix and Start Bot with Proper Initialization
"""
import sys
import os
import io

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("FIXING AND STARTING BOT")
print("="*70)

try:
    print("\n[1/4] Verifying bot components...")
    from src.config import Config
    from src.core.trading_engine import TradingEngine
    from src.managers.risk_manager import RiskManager
    from src.clients.mt5_client import MT5Client
    from src.clients.telegram_bot import TelegramBot
    from src.processors.alert_processor import AlertProcessor
    
    config = Config()
    risk_manager = RiskManager(config)
    mt5_client = MT5Client(config)
    telegram_bot = TelegramBot(config)
    alert_processor = AlertProcessor(config)
    trading_engine = TradingEngine(config, risk_manager, mt5_client, telegram_bot, alert_processor)
    
    print("[OK] All components initialized")
    
    print("\n[2/4] Setting dependencies...")
    telegram_bot.set_dependencies(risk_manager, trading_engine)
    
    # Verify dependencies
    if telegram_bot.risk_manager:
        print("[OK] RiskManager set")
    else:
        print("[FAIL] RiskManager NOT set!")
    
    if telegram_bot.trading_engine:
        print("[OK] TradingEngine set")
    else:
        print("[FAIL] TradingEngine NOT set!")
    
    if telegram_bot.menu_manager:
        print("[OK] MenuManager initialized")
    else:
        print("[FAIL] MenuManager NOT initialized!")
    
    print("\n[3/4] Testing commands...")
    test_user_id = telegram_bot.chat_id if telegram_bot.chat_id else 123456789
    
    # Test /start
    try:
        mock_msg = {"from": {"id": test_user_id}, "message_id": None}
        telegram_bot.handle_start(mock_msg)
        print("[OK] /start command works")
    except Exception as e:
        print(f"[FAIL] /start command error: {e}")
    
    # Test /dashboard
    try:
        mock_msg = {"from": {"id": test_user_id}, "message_id": None}
        telegram_bot.handle_dashboard(mock_msg)
        print("[OK] /dashboard command works")
    except Exception as e:
        print(f"[FAIL] /dashboard command error: {e}")
    
    print("\n[4/4] Starting bot server...")
    print("="*70)
    print("Bot will start on port 5000")
    print("Check console for 'SUCCESS: Telegram bot polling started'")
    print("="*70)
    print("\nStarting server...\n")
    
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )
    
except KeyboardInterrupt:
    print("\n\nBot stopped by user")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

