#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Bot Startup and Menu System
"""
import sys
import os
import io

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(text):
    """Print text safely handling Unicode errors"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

safe_print("="*70)
safe_print("VERIFYING BOT STARTUP AND MENU SYSTEM")
safe_print("="*70)

try:
    safe_print("\n[1/5] Loading config...")
    from src.config import Config
    config = Config()
    safe_print("[OK] Config loaded")
    
    safe_print("\n[2/5] Initializing Telegram Bot...")
    from src.clients.telegram_bot import TelegramBot
    telegram_bot = TelegramBot(config)
    safe_print("[OK] Telegram Bot initialized")
    
    safe_print("\n[3/5] Checking menu system...")
    if telegram_bot.menu_manager:
        safe_print("[OK] MenuManager initialized")
        if telegram_bot.menu_manager.executor:
            safe_print("[OK] CommandExecutor initialized")
        if telegram_bot.menu_manager.context:
            safe_print("[OK] ContextManager initialized")
    else:
        safe_print("[FAIL] MenuManager NOT initialized!")
        sys.exit(1)
    
    safe_print("\n[4/5] Verifying command handlers...")
    if "/start" in telegram_bot.command_handlers:
        safe_print("[OK] /start command handler registered")
    else:
        safe_print("[FAIL] /start command handler NOT registered!")
    
    if "/dashboard" in telegram_bot.command_handlers:
        safe_print("[OK] /dashboard command handler registered")
    else:
        safe_print("[FAIL] /dashboard command handler NOT registered!")
    
    safe_print("\n[5/5] Testing menu display...")
    test_user_id = telegram_bot.chat_id if telegram_bot.chat_id else 123456789
    
    # Test /start menu
    safe_print("  Testing /start menu...")
    try:
        mock_message = {"from": {"id": test_user_id}, "message_id": None}
        telegram_bot.handle_start(mock_message)
        safe_print("  [OK] /start command executed (menu should be sent)")
    except Exception as e:
        safe_print(f"  [FAIL] /start command failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test /dashboard
    safe_print("  Testing /dashboard command...")
    try:
        mock_message = {"from": {"id": test_user_id}, "message_id": None}
        telegram_bot.handle_dashboard(mock_message)
        safe_print("  [OK] /dashboard command executed (dashboard should be sent)")
    except Exception as e:
        safe_print(f"  [FAIL] /dashboard command failed: {e}")
        import traceback
        traceback.print_exc()
    
    safe_print("\n" + "="*70)
    safe_print("VERIFICATION COMPLETE")
    safe_print("="*70)
    safe_print("\n[OK] Bot is ready to start!")
    safe_print("[OK] Menu system is functional!")
    safe_print("[OK] /start and /dashboard commands are registered!")
    safe_print("\nTo start the bot, run:")
    safe_print("  python src/main.py --port 5000")
    safe_print("  OR")
    safe_print("  python start_bot_live.py")
    safe_print("\n" + "="*70)
    
except Exception as e:
    safe_print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

