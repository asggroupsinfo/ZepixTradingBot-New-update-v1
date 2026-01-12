#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIVE MENU FLOW TESTING - Test actual menu execution
"""
import sys
import os
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_menu_flow():
    """Test complete menu flow"""
    print("="*70)
    print("TESTING MENU FLOW - COMPLETE EXECUTION")
    print("="*70)
    
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        
        config = Config()
        bot = TelegramBot(config)
        user_id = config.get("telegram_chat_id", 123456789)
        
        print("\n[TEST 1] Testing command selection...")
        # Simulate clicking a command with parameters
        mock_callback = {
            "id": "test_123",
            "from": {"id": user_id},
            "message": {"message_id": 9999, "chat": {"id": user_id}},
            "data": "cmd_trends_set_trend"
        }
        
        print("  Simulating: Click 'Set Trend' command")
        bot.handle_callback_query(mock_callback)
        print("  [OK] Callback handled")
        
        print("\n[TEST 2] Testing parameter selection...")
        # Check if context has pending command
        context = bot.menu_manager.context.get_context(user_id)
        print(f"  Pending command: {context.get('pending_command')}")
        print(f"  Params: {context.get('params')}")
        
        if context.get('pending_command') == 'set_trend':
            print("  [OK] Command set in context")
            
            # Simulate selecting first parameter (symbol)
            mock_callback2 = {
                "id": "test_124",
                "from": {"id": user_id},
                "message": {"message_id": 9999, "chat": {"id": user_id}},
                "data": "param_symbol_set_trend_XAUUSD"
            }
            print("  Simulating: Select symbol XAUUSD")
            bot.handle_callback_query(mock_callback2)
            
            # Check context again
            context2 = bot.menu_manager.context.get_context(user_id)
            print(f"  Params after selection: {context2.get('params')}")
            
            if 'symbol' in context2.get('params', {}):
                print("  [OK] Parameter stored in context")
            else:
                print("  [FAIL] Parameter NOT stored!")
        else:
            print("  [FAIL] Command NOT set in context!")
        
        print("\n[TEST 3] Testing command execution...")
        # Check execution log
        stats = bot.menu_manager.executor.get_execution_stats()
        print(f"  Execution stats: {stats}")
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_menu_flow()

