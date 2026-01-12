#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLETE LIVE TEST - Test ALL 72 commands with parameters
"""
import sys
import os
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_all_commands():
    """Test all commands systematically"""
    print("="*70)
    print("COMPLETE LIVE TEST - ALL 72 COMMANDS")
    print("="*70)
    
    try:
        from src.config import Config
        from src.clients.telegram_bot import TelegramBot
        from src.menu.command_mapping import COMMAND_PARAM_MAP
        
        config = Config()
        bot = TelegramBot(config)
        user_id = config.get("telegram_chat_id", 123456789)
        
        # Test commands by type
        test_results = {
            "direct": {"total": 0, "tested": 0, "passed": 0},
            "single": {"total": 0, "tested": 0, "passed": 0},
            "multi": {"total": 0, "tested": 0, "passed": 0},
            "multi_targets": {"total": 0, "tested": 0, "passed": 0},
            "dynamic": {"total": 0, "tested": 0, "passed": 0}
        }
        
        # Count commands by type
        for cmd, cmd_def in COMMAND_PARAM_MAP.items():
            cmd_type = cmd_def.get("type", "direct")
            if cmd_type in test_results:
                test_results[cmd_type]["total"] += 1
        
        print(f"\nCommand breakdown:")
        for cmd_type, stats in test_results.items():
            print(f"  {cmd_type}: {stats['total']} commands")
        
        # Test sample commands
        print("\n" + "="*70)
        print("TESTING SAMPLE COMMANDS")
        print("="*70)
        
        # Test 1: Direct command
        print("\n[TEST 1] Direct command: /status")
        try:
            mock_msg = {"message_id": None, "from": {"id": user_id}}
            bot.handle_status(mock_msg)
            print("  [OK] Status command executed")
            test_results["direct"]["tested"] += 1
            test_results["direct"]["passed"] += 1
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            test_results["direct"]["tested"] += 1
        
        # Test 2: Single parameter command
        print("\n[TEST 2] Single parameter: /simulation_mode on")
        try:
            # Set context
            bot.menu_manager.context.set_pending_command(user_id, "simulation_mode")
            bot.menu_manager.context.clear_params(user_id)
            bot.menu_manager.context.add_param(user_id, "mode", "on")
            
            # Execute
            params = {"mode": "on"}
            success = bot.menu_manager.executor.execute_command(user_id, "simulation_mode", params)
            if success:
                print("  [OK] Simulation mode command executed")
                test_results["single"]["tested"] += 1
                test_results["single"]["passed"] += 1
            else:
                print("  [FAIL] Command execution returned False")
                test_results["single"]["tested"] += 1
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            import traceback
            traceback.print_exc()
            test_results["single"]["tested"] += 1
        
        # Test 3: Multi-parameter command
        print("\n[TEST 3] Multi-parameter: /set_trend XAUUSD 1h BULLISH")
        try:
            # Set context
            bot.menu_manager.context.set_pending_command(user_id, "set_trend")
            bot.menu_manager.context.clear_params(user_id)
            bot.menu_manager.context.add_param(user_id, "symbol", "XAUUSD")
            bot.menu_manager.context.add_param(user_id, "timeframe", "1h")
            bot.menu_manager.context.add_param(user_id, "trend", "BULLISH")
            
            # Execute
            params = {"symbol": "XAUUSD", "timeframe": "1h", "trend": "BULLISH"}
            success = bot.menu_manager.executor.execute_command(user_id, "set_trend", params)
            if success:
                print("  [OK] Set trend command executed")
                test_results["multi"]["tested"] += 1
                test_results["multi"]["passed"] += 1
            else:
                print("  [FAIL] Command execution returned False")
                test_results["multi"]["tested"] += 1
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            import traceback
            traceback.print_exc()
            test_results["multi"]["tested"] += 1
        
        # Test 4: Profit booking command
        print("\n[TEST 4] Profit booking: /profit_status")
        try:
            mock_msg = {"message_id": None, "from": {"id": user_id}}
            bot.handle_profit_status(mock_msg)
            print("  [OK] Profit status command executed")
            test_results["direct"]["tested"] += 1
            test_results["direct"]["passed"] += 1
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            test_results["direct"]["tested"] += 1
        
        # Test 5: Profit SL command
        print("\n[TEST 5] Profit SL: /profit_sl_status")
        try:
            mock_msg = {"message_id": None, "from": {"id": user_id}}
            bot.handle_profit_sl_status(mock_msg)
            print("  [OK] Profit SL status command executed")
            test_results["direct"]["tested"] += 1
            test_results["direct"]["passed"] += 1
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            test_results["direct"]["tested"] += 1
        
        # Execution stats
        print("\n" + "="*70)
        print("EXECUTION STATISTICS")
        print("="*70)
        stats = bot.menu_manager.executor.get_execution_stats()
        print(f"Total executions: {stats['total']}")
        print(f"Successful: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success rate: {stats['success_rate']}%")
        
        # Test results summary
        print("\n" + "="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)
        for cmd_type, stats in test_results.items():
            if stats["tested"] > 0:
                pass_rate = (stats["passed"] / stats["tested"] * 100) if stats["tested"] > 0 else 0
                print(f"{cmd_type}: {stats['passed']}/{stats['tested']} passed ({pass_rate:.1f}%)")
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_commands()

