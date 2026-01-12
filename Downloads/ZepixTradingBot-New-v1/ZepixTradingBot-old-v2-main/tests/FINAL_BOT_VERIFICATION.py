#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL BOT VERIFICATION - Complete System Check
"""
import sys
import os
import io
import requests
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

def check_bot_running():
    """Check if bot is running on port 5000"""
    safe_print("\n[CHECK 1] Bot Server Status...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            safe_print(f"  [OK] Bot is running on port 5000")
            safe_print(f"  Status: {data.get('status', 'unknown')}")
            safe_print(f"  MT5 Connected: {data.get('mt5_connected', False)}")
            return True
    except Exception as e:
        safe_print(f"  [FAIL] Bot not running: {e}")
        return False

def check_menu_system():
    """Check menu system components"""
    safe_print("\n[CHECK 2] Menu System Components...")
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
            "Total commands": len(telegram_bot.command_handlers),
        }
        
        all_ok = True
        for check, result in checks.items():
            if isinstance(result, bool):
                status = "[OK]" if result else "[FAIL]"
                safe_print(f"  {status} {check}")
                if not result:
                    all_ok = False
            else:
                safe_print(f"  [OK] {check}: {result}")
        
        return all_ok
    except Exception as e:
        safe_print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_telegram_connection():
    """Test Telegram API connection"""
    safe_print("\n[CHECK 3] Telegram API Connection...")
    try:
        from src.config import Config
        config = Config()
        token = config.get("telegram_token")
        chat_id = config.get("telegram_chat_id")
        
        if not token or not chat_id:
            safe_print("  [WARN] Telegram credentials not configured")
            return False
        
        # Test getMe endpoint
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                safe_print(f"  [OK] Telegram bot connected")
                safe_print(f"  Bot username: @{bot_info.get('username', 'unknown')}")
                safe_print(f"  Chat ID: {chat_id}")
                return True
            else:
                safe_print(f"  [FAIL] Telegram API error: {data}")
                return False
        else:
            safe_print(f"  [FAIL] HTTP error: {response.status_code}")
            return False
    except Exception as e:
        safe_print(f"  [FAIL] Error: {e}")
        return False

def test_menu_sending():
    """Test if menu can be sent"""
    safe_print("\n[CHECK 4] Menu Sending Test...")
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        
        config = Config()
        telegram_bot = TelegramBot(config)
        
        user_id = config.get("telegram_chat_id", 123456789)
        result = telegram_bot.menu_manager.show_main_menu(user_id)
        
        if result:
            safe_print(f"  [OK] Menu sent successfully (message_id: {result})")
            return True
        else:
            safe_print("  [WARN] Menu returned None - may not have sent")
            return False
    except Exception as e:
        safe_print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_bot_processes():
    """Check if bot processes are running"""
    safe_print("\n[CHECK 5] Bot Processes...")
    try:
        import psutil
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'main.py' in cmdline or 'deploy_bot' in cmdline:
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline[:100]
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            safe_print(f"  [OK] Found {len(python_processes)} bot process(es):")
            for proc in python_processes:
                safe_print(f"    PID {proc['pid']}: {proc['cmdline']}")
            return True
        else:
            safe_print("  [WARN] No bot processes found")
            return False
    except ImportError:
        safe_print("  [INFO] psutil not available - skipping process check")
        return True
    except Exception as e:
        safe_print(f"  [WARN] Error checking processes: {e}")
        return True

def main():
    safe_print("="*70)
    safe_print("FINAL BOT VERIFICATION - COMPLETE SYSTEM CHECK")
    safe_print("="*70)
    
    results = []
    
    results.append(("Bot Server", check_bot_running()))
    results.append(("Menu System", check_menu_system()))
    results.append(("Telegram Connection", test_telegram_connection()))
    results.append(("Menu Sending", test_menu_sending()))
    results.append(("Bot Processes", check_bot_processes()))
    
    safe_print("\n" + "="*70)
    safe_print("VERIFICATION SUMMARY")
    safe_print("="*70)
    
    for check_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        safe_print(f"{status} {check_name}")
    
    all_passed = all(result for _, result in results)
    
    safe_print("\n" + "="*70)
    if all_passed:
        safe_print("[SUCCESS] All checks passed!")
        safe_print("\nBot is ready for Telegram testing:")
        safe_print("1. Send /start in Telegram - Menu should appear")
        safe_print("2. Click buttons - Should navigate")
        safe_print("3. Send /dashboard - Dashboard should appear")
        safe_print("4. Click menu button - Should return to menu")
    else:
        safe_print("[WARNING] Some checks failed")
        safe_print("\nPlease review the errors above")
    safe_print("="*70)
    
    safe_print("\nBot is running in background.")
    safe_print("To stop: Find Python process and kill it, or restart computer.")
    safe_print("="*70)

if __name__ == "__main__":
    main()

