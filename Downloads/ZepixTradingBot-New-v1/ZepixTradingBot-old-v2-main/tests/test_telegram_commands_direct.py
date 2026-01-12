#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Telegram Command Testing - Simulates actual Telegram messages
"""
import sys
import os
import io
import time

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(text):
    """Print safely"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def test_start_command():
    """Test /start command"""
    safe_print("\n[TEST] Testing /start command...")
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        
        config = Config()
        telegram_bot = TelegramBot(config)
        
        # Simulate Telegram message
        mock_message = {
            "message_id": 12345,
            "from": {"id": config.get("telegram_chat_id", 123456789), "first_name": "Test"},
            "text": "/start",
            "chat": {"id": config.get("telegram_chat_id", 123456789)}
        }
        
        safe_print("  Calling handle_start...")
        telegram_bot.handle_start(mock_message)
        safe_print("  [OK] /start command executed")
        return True
    except Exception as e:
        safe_print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_command():
    """Test /dashboard command"""
    safe_print("\n[TEST] Testing /dashboard command...")
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        
        config = Config()
        telegram_bot = TelegramBot(config)
        
        # Simulate Telegram message
        mock_message = {
            "message_id": 12346,
            "from": {"id": config.get("telegram_chat_id", 123456789), "first_name": "Test"},
            "text": "/dashboard",
            "chat": {"id": config.get("telegram_chat_id", 123456789)}
        }
        
        safe_print("  Calling handle_dashboard...")
        telegram_bot.handle_dashboard(mock_message)
        safe_print("  [OK] /dashboard command executed")
        return True
    except Exception as e:
        safe_print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_manager():
    """Test menu manager directly"""
    safe_print("\n[TEST] Testing MenuManager directly...")
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        
        config = Config()
        telegram_bot = TelegramBot(config)
        
        if not telegram_bot.menu_manager:
            safe_print("  [FAIL] MenuManager not initialized")
            return False
        
        user_id = config.get("telegram_chat_id", 123456789)
        safe_print(f"  Calling show_main_menu for user {user_id}...")
        result = telegram_bot.menu_manager.show_main_menu(user_id)
        
        if result:
            safe_print(f"  [OK] Menu sent successfully (result: {result})")
        else:
            safe_print("  [WARN] Menu returned None or False")
        
        return True
    except Exception as e:
        safe_print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_callback_query():
    """Test callback query handling"""
    safe_print("\n[TEST] Testing callback query handling...")
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        
        config = Config()
        telegram_bot = TelegramBot(config)
        
        # Simulate callback query for menu_main
        mock_callback = {
            "id": "test_callback_123",
            "from": {"id": config.get("telegram_chat_id", 123456789), "first_name": "Test"},
            "message": {
                "message_id": 12347,
                "chat": {"id": config.get("telegram_chat_id", 123456789)},
                "text": "Test message"
            },
            "data": "menu_main"
        }
        
        safe_print("  Calling handle_callback_query...")
        telegram_bot.handle_callback_query(mock_callback)
        safe_print("  [OK] Callback query handled")
        return True
    except Exception as e:
        safe_print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    safe_print("="*70)
    safe_print("DIRECT TELEGRAM COMMAND TESTING")
    safe_print("="*70)
    
    results = []
    
    results.append(("MenuManager Direct", test_menu_manager()))
    results.append(("/start Command", test_start_command()))
    results.append(("/dashboard Command", test_dashboard_command()))
    results.append(("Callback Query", test_callback_query()))
    
    safe_print("\n" + "="*70)
    safe_print("TEST RESULTS")
    safe_print("="*70)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        safe_print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in results)
    
    safe_print("\n" + "="*70)
    if all_passed:
        safe_print("[OK] All tests passed!")
    else:
        safe_print("[WARN] Some tests failed - check output above")
    safe_print("="*70)
    
    return all_passed

if __name__ == "__main__":
    main()

