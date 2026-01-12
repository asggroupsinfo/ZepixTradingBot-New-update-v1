#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Telegram Bot Testing - Tests actual Telegram commands
"""
import sys
import os
import io
import time
import requests
import json

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

def test_bot_health():
    """Test if bot is running"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            safe_print("[OK] Bot is running on port 5000")
            return True
    except:
        pass
    safe_print("[FAIL] Bot is NOT running on port 5000")
    return False

def test_bot_status():
    """Test bot status endpoint"""
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            safe_print(f"[OK] Bot status: {data.get('status', 'unknown')}")
            return True
    except Exception as e:
        safe_print(f"[FAIL] Status check failed: {e}")
    return False

def test_menu_system():
    """Test menu system components"""
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        
        config = Config()
        telegram_bot = TelegramBot(config)
        
        checks = {
            "MenuManager": telegram_bot.menu_manager is not None,
            "CommandExecutor": telegram_bot.menu_manager.executor is not None if telegram_bot.menu_manager else False,
            "ContextManager": telegram_bot.menu_manager.context is not None if telegram_bot.menu_manager else False,
            "/start handler": "/start" in telegram_bot.command_handlers,
            "/dashboard handler": "/dashboard" in telegram_bot.command_handlers,
        }
        
        all_ok = True
        for check, result in checks.items():
            status = "[OK]" if result else "[FAIL]"
            safe_print(f"  {status} {check}")
            if not result:
                all_ok = False
        
        return all_ok
    except Exception as e:
        safe_print(f"[FAIL] Menu system test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    safe_print("="*70)
    safe_print("LIVE TELEGRAM BOT TESTING")
    safe_print("="*70)
    
    safe_print("\n[TEST 1] Bot Health Check...")
    if not test_bot_health():
        safe_print("\n[ERROR] Bot is not running!")
        safe_print("Please start bot first:")
        safe_print("  python deploy_bot_permanent.py")
        safe_print("  OR")
        safe_print("  python src/main.py --port 5000")
        return False
    
    safe_print("\n[TEST 2] Bot Status Check...")
    test_bot_status()
    
    safe_print("\n[TEST 3] Menu System Check...")
    if test_menu_system():
        safe_print("[OK] Menu system is ready")
    else:
        safe_print("[FAIL] Menu system has issues")
    
    safe_print("\n" + "="*70)
    safe_print("TESTING COMPLETE")
    safe_print("="*70)
    safe_print("\nBot is running. Test in Telegram:")
    safe_print("1. Send /start - Menu should appear")
    safe_print("2. Click buttons - Should work")
    safe_print("3. Send /dashboard - Dashboard should appear")
    safe_print("4. Click menu button - Should return to menu")
    safe_print("\n" + "="*70)
    
    return True

if __name__ == "__main__":
    main()

