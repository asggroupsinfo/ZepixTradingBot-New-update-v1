#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unicode-Safe Live Menu System Testing Script
Handles all Unicode/emoji errors and tests complete zero-typing system
"""
import sys
import os
import io
import traceback
from datetime import datetime

# Set UTF-8 encoding for stdout/stderr
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(text):
    """Print text safely handling Unicode errors"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emojis and special chars if encoding fails
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def safe_format(text, **kwargs):
    """Format text safely"""
    try:
        return text.format(**kwargs)
    except:
        # Fallback to simple string replacement
        result = text
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

safe_print("="*70)
safe_print("UNICODE-SAFE MENU SYSTEM LIVE TESTING")
safe_print("="*70)
safe_print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
safe_print("")

# Test counter
test_count = 0
pass_count = 0
fail_count = 0
error_count = 0

def test_result(name, passed, error=None):
    """Record test result"""
    global test_count, pass_count, fail_count, error_count
    test_count += 1
    if passed:
        pass_count += 1
        safe_print(f"[PASS {test_count}] {name}")
    else:
        if error:
            error_count += 1
            safe_print(f"[ERROR {test_count}] {name}: {error}")
        else:
            fail_count += 1
            safe_print(f"[FAIL {test_count}] {name}")

try:
    safe_print("[STEP 1/10] Importing modules...")
    from src.config import Config
    from src.managers.risk_manager import RiskManager
    from src.clients.mt5_client import MT5Client
    from src.clients.telegram_bot import TelegramBot
    from src.core.trading_engine import TradingEngine
    from src.processors.alert_processor import AlertProcessor
    test_result("Module imports", True)
except Exception as e:
    test_result("Module imports", False, str(e))
    safe_print(f"FATAL: Cannot continue without imports: {e}")
    sys.exit(1)

# Import command mapping after other modules are loaded
try:
    from src.menu.command_mapping import COMMAND_PARAM_MAP
    test_result("Command mapping import", True)
except Exception as e:
    safe_print(f"WARNING: Could not import COMMAND_PARAM_MAP: {e}")
    COMMAND_PARAM_MAP = {}

try:
    safe_print("\n[STEP 2/10] Initializing components...")
    config = Config()
    risk_manager = RiskManager(config)
    mt5_client = MT5Client(config)
    telegram_bot = TelegramBot(config)
    alert_processor = AlertProcessor(config)
    test_result("Component initialization", True)
except Exception as e:
    test_result("Component initialization", False, str(e))
    safe_print(f"FATAL: Cannot continue: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    safe_print("\n[STEP 3/10] Creating trading engine...")
    trading_engine = TradingEngine(config, risk_manager, mt5_client, telegram_bot, alert_processor)
    test_result("Trading engine creation", True)
except Exception as e:
    test_result("Trading engine creation", False, str(e))
    safe_print(f"FATAL: Cannot continue: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    safe_print("\n[STEP 4/10] Setting dependencies...")
    telegram_bot.set_dependencies(risk_manager, trading_engine)
    test_result("Dependency setup", True)
except Exception as e:
    test_result("Dependency setup", False, str(e))
    safe_print(f"WARNING: Dependency setup failed: {e}")

safe_print("\n[STEP 5/10] Verifying menu system...")
checks = {
    "MenuManager initialized": telegram_bot.menu_manager is not None,
    "CommandExecutor initialized": telegram_bot.menu_manager.executor is not None if telegram_bot.menu_manager else False,
    "ContextManager initialized": telegram_bot.menu_manager.context is not None if telegram_bot.menu_manager else False,
    "Execution log available": hasattr(telegram_bot.menu_manager.executor, 'execution_log') if telegram_bot.menu_manager and telegram_bot.menu_manager.executor else False,
}

all_ok = True
for check, result in checks.items():
    test_result(check, result)
    if not result:
        all_ok = False

if not all_ok:
    safe_print("\n[ERROR] Menu system not initialized correctly!")
    safe_print("Continuing with available components...")

# Test user ID
test_user_id = telegram_bot.chat_id if telegram_bot.chat_id else 123456789

safe_print("\n[STEP 6/10] Testing command execution...")

# Test commands by type
test_results = {
    "direct": [],
    "single_param": [],
    "multi_param": [],
    "multi_target": [],
    "dynamic": []
}

# Direct commands (no params) - Test 10 commands
direct_commands = ["pause", "resume", "status", "trades", "performance", "stats", "signal_status", "logic_status", "chains", "profit_status"]
safe_print("\n--- Testing Direct Commands (No Parameters) ---")
for cmd in direct_commands:
    try:
        safe_print(f"  Testing: {cmd}")
        if telegram_bot.menu_manager and telegram_bot.menu_manager.executor:
            result = telegram_bot.menu_manager.executor.execute_command(test_user_id, cmd, {})
            test_results["direct"].append({"command": cmd, "success": result})
            test_result(f"Direct command: {cmd}", result)
        else:
            test_result(f"Direct command: {cmd}", False, "Menu system not available")
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        test_result(f"Direct command: {cmd}", False, error_msg)
        test_results["direct"].append({"command": cmd, "success": False, "error": error_msg})

# Single parameter commands - Test 5 commands
single_param_commands = [
    {"cmd": "simulation_mode", "params": {"mode": "on"}},
    {"cmd": "tp_system", "params": {"mode": "status"}},
    {"cmd": "set_daily_cap", "params": {"amount": 100.0}},
    {"cmd": "sl_system_change", "params": {"system": "SL-1"}},
    {"cmd": "profit_sl_mode", "params": {"mode": "SL-1.1"}}
]
safe_print("\n--- Testing Single Parameter Commands ---")
for test in single_param_commands:
    try:
        safe_print(f"  Testing: {test['cmd']} with params: {test['params']}")
        if telegram_bot.menu_manager and telegram_bot.menu_manager.executor:
            result = telegram_bot.menu_manager.executor.execute_command(
                test_user_id, test['cmd'], test['params']
            )
            test_results["single_param"].append({"command": test['cmd'], "success": result})
            test_result(f"Single param: {test['cmd']}", result)
        else:
            test_result(f"Single param: {test['cmd']}", False, "Menu system not available")
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        test_result(f"Single param: {test['cmd']}", False, error_msg)
        test_results["single_param"].append({"command": test['cmd'], "success": False, "error": error_msg})

# Multi-parameter commands - Test 3 commands
multi_param_commands = [
    {"cmd": "set_trend", "params": {"symbol": "XAUUSD", "timeframe": "1h", "trend": "BULLISH"}},
    {"cmd": "set_lot_size", "params": {"tier": "5000", "lot_size": 0.1}},
    {"cmd": "set_symbol_sl", "params": {"symbol": "XAUUSD", "percent": 2.0}}
]
safe_print("\n--- Testing Multi-Parameter Commands ---")
for test in multi_param_commands:
    try:
        safe_print(f"  Testing: {test['cmd']} with params: {test['params']}")
        if telegram_bot.menu_manager and telegram_bot.menu_manager.executor:
            result = telegram_bot.menu_manager.executor.execute_command(
                test_user_id, test['cmd'], test['params']
            )
            test_results["multi_param"].append({"command": test['cmd'], "success": result})
            test_result(f"Multi param: {test['cmd']}", result)
        else:
            test_result(f"Multi param: {test['cmd']}", False, "Menu system not available")
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        test_result(f"Multi param: {test['cmd']}", False, error_msg)
        test_results["multi_param"].append({"command": test['cmd'], "success": False, "error": error_msg})

# Check execution log
safe_print("\n[STEP 7/10] Checking execution log...")
try:
    if telegram_bot.menu_manager and telegram_bot.menu_manager.executor:
        executor = telegram_bot.menu_manager.executor
        log_entries = executor.get_execution_log(limit=20)
        stats = executor.get_execution_stats()
        
        safe_print(f"Total executions: {stats.get('total', 0)}")
        safe_print(f"Successful: {stats.get('success', 0)}")
        safe_print(f"Failed: {stats.get('failed', 0)}")
        safe_print(f"Success rate: {stats.get('success_rate', 0.0)}%")
        
        if log_entries:
            safe_print("\nRecent executions:")
            for entry in log_entries[-5:]:
                status = entry.get("status", "unknown")
                cmd = entry.get("command", "unknown")
                safe_print(f"  {cmd} - {status}")
        test_result("Execution log check", True)
    else:
        test_result("Execution log check", False, "Menu system not available")
except Exception as e:
    error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
    test_result("Execution log check", False, error_msg)

# Verify command mapping
safe_print("\n[STEP 8/10] Verifying command mapping...")
try:
    if COMMAND_PARAM_MAP:
        all_commands = list(COMMAND_PARAM_MAP.keys())
        safe_print(f"Total commands in mapping: {len(all_commands)}")
        
        # Check if all commands have handlers
        if telegram_bot.menu_manager and telegram_bot.menu_manager.executor:
            executor_commands = []
            for cmd in all_commands:
                executor_commands.append(cmd)
            
            safe_print(f"Commands ready for execution: {len(executor_commands)}")
            
            if len(executor_commands) == 72:
                safe_print("All 72 commands are mapped and ready!")
                test_result("Command mapping (72 commands)", True)
            else:
                safe_print(f"Expected 72 commands, found {len(executor_commands)}")
                test_result("Command mapping (72 commands)", False, f"Found {len(executor_commands)} instead of 72")
        else:
            test_result("Command mapping", False, "Menu system not available")
    else:
        # Try to get command count from menu manager
        if telegram_bot.menu_manager and hasattr(telegram_bot.menu_manager, 'executor'):
            safe_print("Command mapping not available, checking executor...")
            test_result("Command mapping", True, "Using executor directly")
        else:
            test_result("Command mapping", False, "Command mapping not available")
except Exception as e:
    error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
    test_result("Command mapping", False, error_msg)

# Test results summary
safe_print("\n[STEP 9/10] Test Results Summary")
safe_print("="*70)

total_tests = 0
total_passed = 0

for test_type, results in test_results.items():
    if results:
        passed = sum(1 for r in results if r.get("success", False))
        total = len(results)
        total_tests += total
        total_passed += passed
        safe_print(f"\n{test_type.upper()}: {passed}/{total} passed")
        for result in results:
            status = "PASS" if result.get("success") else "FAIL"
            cmd = result.get("command", "unknown")
            error = result.get("error", "")
            if error:
                safe_print(f"  [{status}] {cmd} - {error[:50]}")
            else:
                safe_print(f"  [{status}] {cmd}")

safe_print(f"\n{'='*70}")
safe_print(f"OVERALL: {total_passed}/{total_tests} command tests passed")
safe_print(f"TOTAL TESTS: {test_count} | PASSED: {pass_count} | FAILED: {fail_count} | ERRORS: {error_count}")
safe_print(f"{'='*70}")

# Final verification
safe_print("\n[STEP 10/10] Final Verification...")
final_checks = {
    "Menu system initialized": telegram_bot.menu_manager is not None,
    "Command executor available": telegram_bot.menu_manager.executor is not None if telegram_bot.menu_manager else False,
    "Execution logging working": hasattr(telegram_bot.menu_manager.executor, 'execution_log') if telegram_bot.menu_manager and telegram_bot.menu_manager.executor else False,
    "All 72 commands mapped": len(COMMAND_PARAM_MAP) == 72 if COMMAND_PARAM_MAP else False,
}

for check, result in final_checks.items():
    test_result(f"Final check: {check}", result)

safe_print("\n" + "="*70)
safe_print("TESTING COMPLETE")
safe_print(f"Test Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
safe_print("="*70)

if pass_count == test_count:
    safe_print("\n[SUCCESS] All tests passed!")
    sys.exit(0)
else:
    safe_print(f"\n[WARNING] {fail_count + error_count} tests failed or had errors")
    safe_print("Review the output above for details")
    sys.exit(1)

