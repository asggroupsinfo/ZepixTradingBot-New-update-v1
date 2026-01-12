#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL TELEGRAM COMMAND TEST - Test with actual dependencies
"""
import sys
import os
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_commands_with_dependencies():
    """Test commands ensuring dependencies are available"""
    print("="*70)
    print("FINAL TELEGRAM COMMAND TEST")
    print("="*70)
    
    from src.config import Config
    from src.clients.telegram_bot import TelegramBot
    
    config = Config()
    bot = TelegramBot(config)
    user_id = config.get("telegram_chat_id", 123456789)
    
    # Wait for bot to initialize
    print("\n[WAIT] Waiting for bot to initialize...")
    time.sleep(2)
    
    # Test commands that were failing
    test_commands = [
        ("status", {}),
        ("profit_status", {}),
        ("profit_sl_status", {}),
        ("pause", {}),
        ("resume", {}),
    ]
    
    results = {"total": 0, "passed": 0, "failed": 0}
    
    for cmd, params in test_commands:
        results["total"] += 1
        try:
            mock_msg = {"message_id": None, "from": {"id": user_id}}
            handler_name = f"handle_{cmd}"
            handler = getattr(bot, handler_name, None)
            
            if handler:
                # Ensure dependencies before calling
                bot._ensure_dependencies()
                handler(mock_msg)
                results["passed"] += 1
                print(f"  [OK] {cmd}")
            else:
                results["failed"] += 1
                print(f"  [FAIL] {cmd}: No handler")
        except Exception as e:
            results["failed"] += 1
            print(f"  [FAIL] {cmd}: {e}")
    
    print("\n" + "="*70)
    print(f"Results: {results['passed']}/{results['total']} passed")
    print("="*70)
    
    # Check dependencies
    print("\n[DEPENDENCIES]")
    print(f"  trading_engine: {bot.trading_engine is not None}")
    print(f"  risk_manager: {bot.risk_manager is not None}")
    print(f"  profit_booking_manager: {bot.profit_booking_manager is not None if hasattr(bot, 'profit_booking_manager') else 'N/A'}")
    
    return results

if __name__ == "__main__":
    test_commands_with_dependencies()

