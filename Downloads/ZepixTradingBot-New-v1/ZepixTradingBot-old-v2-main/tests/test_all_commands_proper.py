#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROPER COMMAND TESTING - With correct parameter values
"""
import sys
import os
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_commands():
    """Test commands with proper values"""
    print("="*70)
    print("PROPER COMMAND TESTING")
    print("="*70)
    
    from src.config import Config
    from src.clients.telegram_bot import TelegramBot
    from src.menu.command_mapping import COMMAND_PARAM_MAP
    
    config = Config()
    bot = TelegramBot(config)
    user_id = config.get("telegram_chat_id", 123456789)
    
    results = {"total": 0, "passed": 0, "failed": 0, "errors": []}
    
    # Test direct commands
    print("\n[TEST] Direct commands...")
    direct_cmds = ["pause", "resume", "status", "profit_status", "profit_sl_status", "profit_chains"]
    for cmd in direct_cmds:
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
                print(f"  [FAIL] {cmd}: No handler")
        except Exception as e:
            results["failed"] += 1
            print(f"  [FAIL] {cmd}: {e}")
    
    # Test parameter commands with proper values
    print("\n[TEST] Parameter commands with proper values...")
    test_cases = [
        ("tp_system", {"mode": "on"}),
        ("sl_hunt", {"mode": "on"}),
        ("set_monitor_interval", {"value": "30"}),
        ("set_cooldown", {"value": "60"}),
    ]
    
    for cmd, params in test_cases:
        results["total"] += 1
        try:
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
                print(f"  [FAIL] {cmd}: Execution failed")
        except Exception as e:
            results["failed"] += 1
            print(f"  [FAIL] {cmd}: {e}")
    
    # Test profit booking commands
    print("\n[TEST] Profit booking commands...")
    profit_cmds = ["profit_status", "profit_stats", "profit_sl_status", "profit_chains"]
    for cmd in profit_cmds:
        results["total"] += 1
        try:
            mock_msg = {"message_id": None, "from": {"id": user_id}}
            handler = getattr(bot, COMMAND_PARAM_MAP[cmd].get("handler"), None)
            if handler:
                handler(mock_msg)
                results["passed"] += 1
                print(f"  [OK] {cmd}")
            else:
                results["failed"] += 1
                print(f"  [FAIL] {cmd}: No handler")
        except Exception as e:
            results["failed"] += 1
            print(f"  [FAIL] {cmd}: {e}")
    
    # Summary
    print("\n" + "="*70)
    print(f"Results: {results['passed']}/{results['total']} passed ({results['passed']/results['total']*100 if results['total'] > 0 else 0:.1f}%)")
    print("="*70)
    
    return results

if __name__ == "__main__":
    test_commands()

