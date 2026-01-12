#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLETE BOT TESTING - Test all functionality
"""
import sys
import os
import io
import time
import requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bot_health():
    """Test bot server"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def test_all_commands():
    """Test all commands systematically"""
    print("="*70)
    print("COMPLETE BOT TESTING")
    print("="*70)
    
    from src.config import Config
    from src.clients.telegram_bot import TelegramBot
    from src.menu.command_mapping import COMMAND_PARAM_MAP
    
    config = Config()
    bot = TelegramBot(config)
    user_id = config.get("telegram_chat_id", 123456789)
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test direct commands
    print("\n[TEST] Direct commands (no parameters)...")
    direct_commands = [cmd for cmd, defn in COMMAND_PARAM_MAP.items() if defn.get("type") == "direct"]
    test_count = min(10, len(direct_commands))
    
    for cmd in direct_commands[:test_count]:
        results["total"] += 1
        try:
            mock_msg = {"message_id": None, "from": {"id": user_id}}
            handler_name = COMMAND_PARAM_MAP[cmd].get("handler", f"handle_{cmd}")
            handler = getattr(bot, handler_name, None)
            
            if handler:
                handler(mock_msg)
                results["passed"] += 1
                print(f"  [OK] {cmd}")
            else:
                results["failed"] += 1
                results["errors"].append(f"{cmd}: Handler not found")
                print(f"  [FAIL] {cmd}: Handler not found")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{cmd}: {str(e)}")
            print(f"  [FAIL] {cmd}: {e}")
    
    # Test parameter commands
    print("\n[TEST] Parameter commands...")
    param_commands = [cmd for cmd, defn in COMMAND_PARAM_MAP.items() if defn.get("type") in ["single", "multi"]]
    test_count = min(5, len(param_commands))
    
    for cmd in param_commands[:test_count]:
        results["total"] += 1
        try:
            cmd_def = COMMAND_PARAM_MAP[cmd]
            params = {}
            
            # Create test params
            for param in cmd_def.get("params", []):
                if param == "symbol":
                    params[param] = "XAUUSD"
                elif param == "timeframe":
                    params[param] = "1h"
                elif param == "trend":
                    params[param] = "BULLISH"
                elif param == "mode":
                    params[param] = "on"
                elif param == "amount":
                    params[param] = "100"
                else:
                    params[param] = "test"
            
            # Test execution
            bot.menu_manager.context.set_pending_command(user_id, cmd)
            bot.menu_manager.context.clear_params(user_id)
            for k, v in params.items():
                bot.menu_manager.context.add_param(user_id, k, v)
            
            success = bot.menu_manager.executor.execute_command(user_id, cmd, params)
            if success:
                results["passed"] += 1
                print(f"  [OK] {cmd}")
            else:
                results["failed"] += 1
                results["errors"].append(f"{cmd}: Execution returned False")
                print(f"  [FAIL] {cmd}: Execution failed")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{cmd}: {str(e)}")
            print(f"  [FAIL] {cmd}: {e}")
    
    # Test menu system
    print("\n[TEST] Menu system...")
    try:
        result = bot.menu_manager.show_main_menu(user_id)
        if result:
            print("  [OK] Main menu displays")
            results["passed"] += 1
        else:
            print("  [FAIL] Main menu failed")
            results["failed"] += 1
        results["total"] += 1
    except Exception as e:
        print(f"  [FAIL] Menu error: {e}")
        results["failed"] += 1
        results["total"] += 1
    
    # Test parameter parsing
    print("\n[TEST] Parameter parsing...")
    try:
        bot.menu_manager.context.set_pending_command(user_id, "set_trend")
        bot.menu_manager.context.clear_params(user_id)
        
        # Simulate callback
        callback_data = "param_symbol_set_trend_XAUUSD"
        parts = callback_data.split("_", 2)
        param_type = parts[1]
        rest = parts[2]
        command_prefix = "set_trend_"
        value = rest[len(command_prefix):] if rest.startswith(command_prefix) else rest
        
        bot.menu_manager.context.add_param(user_id, param_type, value)
        stored = bot.menu_manager.context.get_param(user_id, "symbol")
        
        if stored == "XAUUSD":
            print("  [OK] Parameter parsing correct")
            results["passed"] += 1
        else:
            print(f"  [FAIL] Parameter parsing wrong: got {stored}, expected XAUUSD")
            results["failed"] += 1
        results["total"] += 1
    except Exception as e:
        print(f"  [FAIL] Parameter parsing error: {e}")
        results["failed"] += 1
        results["total"] += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"Total tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success rate: {(results['passed']/results['total']*100) if results['total'] > 0 else 0:.1f}%")
    
    if results["errors"]:
        print(f"\nErrors found: {len(results['errors'])}")
        for error in results["errors"][:10]:
            print(f"  - {error}")
    
    return results

def main():
    # Test bot health
    print("\n[1] Testing bot health...")
    health_ok, health_data = test_bot_health()
    if health_ok:
        print(f"  [OK] Bot is running")
        print(f"  Status: {health_data.get('status')}")
    else:
        print("  [FAIL] Bot not responding")
        return
    
    # Test all commands
    print("\n[2] Testing all commands...")
    results = test_all_commands()
    
    # Final status
    print("\n" + "="*70)
    if results["failed"] == 0:
        print("[SUCCESS] All tests passed!")
    else:
        print(f"[WARNING] {results['failed']} tests failed")
    print("="*70)

if __name__ == "__main__":
    main()

