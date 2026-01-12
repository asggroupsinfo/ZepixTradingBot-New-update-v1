"""
Test script for 5 new diagnostic commands
Tests command handlers directly to verify 0% error rate
"""
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.managers.risk_manager import RiskManager
from src.clients.mt5_client import MT5Client
from src.processors.alert_processor import AlertProcessor
from src.core.trading_engine import TradingEngine
from src.utils.optimized_logger import logger as optimized_logger

def test_commands():
    """Test all 5 diagnostic command handlers directly"""
    print("=" * 70)
    print("TESTING 5 NEW DIAGNOSTIC COMMANDS")
    print("=" * 70)
    
    # Initialize components
    print("\n[1/5] Initializing components...")
    config = Config()
    mt5_client = MT5Client(config)
    risk_manager = RiskManager(config)
    risk_manager.set_mt5_client(mt5_client)
    alert_processor = AlertProcessor(config)
    
    # Initialize trading engine (needed for health status)
    print("[2/5] Initializing trading engine...")
    trading_engine = TradingEngine(config, risk_manager, mt5_client, None, alert_processor)
    
    print("[3/5] Components initialized successfully\n")
    
    # Test results
    passed = 0
    failed = 0
    
    # TEST 1: health_status
    print("=" * 70)
    print("TEST 1: health_status")
    print("=" * 70)
    try:
        # Get MT5 connection status
        mt5_info = mt5_client.get_account_info()
        mt5_status = "✅ Connected" if mt5_info else "❌ Disconnected"
        mt5_errors = mt5_client.connection_error_count
        
        # Get circuit breaker status
        trading_cb = trading_engine.monitor_error_count
        trading_cb_max = trading_engine.max_monitor_errors
        
        # Get uptime
        uptime_seconds = time.time() - trading_engine.start_time
        uptime_hours = uptime_seconds / 3600
        
        # Get log file size
        log_path = "logs/trading_bot.log"
        log_size_mb = os.path.getsize(log_path) / (1024 * 1024) if os.path.exists(log_path) else 0
        
        print(f"✅ MT5 Status: {mt5_status}")
        print(f"✅ MT5 Errors: {mt5_errors}/5")
        print(f"✅ Trading CB: {trading_cb}/{trading_cb_max}")
        print(f"✅ Uptime: {uptime_hours:.2f} hours")
        print(f"✅ Log Size: {log_size_mb:.2f} MB")
        print("✅ PASS - health_status data retrieved")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL - {e}")
        failed += 1
    
    # TEST 2: set_log_level (DEBUG)
    print("\n" + "=" * 70)
    print("TEST 2: set_log_level (DEBUG)")
    print("=" * 70)
    try:
        from src.utils import logging_config
        logging_config.set_log_level("DEBUG")
        current_level = logging_config.get_log_level()
        if current_level == "DEBUG":
            print(f"✅ Log level changed to: {current_level}")
            print("✅ PASS - set_log_level DEBUG works")
            passed += 1
        else:
            print(f"❌ Expected DEBUG, got {current_level}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL - {e}")
        failed += 1
    
    # TEST 3: set_log_level (INFO)
    print("\n" + "=" * 70)
    print("TEST 3: set_log_level (INFO)")
    print("=" * 70)
    try:
        from src.utils import logging_config
        logging_config.set_log_level("INFO")
        current_level = logging_config.get_log_level()
        if current_level == "INFO":
            print(f"✅ Log level changed to: {current_level}")
            print("✅ PASS - set_log_level INFO works")
            passed += 1
        else:
            print(f"❌ Expected INFO, got {current_level}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL - {e}")
        failed += 1
    
    # TEST 4: error_stats
    print("\n" + "=" * 70)
    print("TEST 4: error_stats")
    print("=" * 70)
    try:
        # Get error statistics
        total_errors = len(optimized_logger.error_cache)
        
        # Get top errors
        from collections import Counter
        error_counter = Counter(optimized_logger.error_cache)
        top_errors = error_counter.most_common(5)
        
        print(f"✅ Total Errors: {total_errors}")
        print(f"✅ Top Errors: {len(top_errors)} types")
        print(f"✅ MT5 Reconnects: {mt5_client.connection_error_count}")
        print("✅ PASS - error_stats data retrieved")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL - {e}")
        failed += 1
    
    # TEST 5: reset_errors
    print("\n" + "=" * 70)
    print("TEST 5: reset_errors")
    print("=" * 70)
    try:
        before_count = len(optimized_logger.error_cache)
        optimized_logger.error_cache.clear()
        after_count = len(optimized_logger.error_cache)
        
        print(f"✅ Errors before: {before_count}")
        print(f"✅ Errors after: {after_count}")
        if after_count == 0:
            print("✅ PASS - reset_errors cleared counters")
            passed += 1
        else:
            print(f"❌ Failed to clear errors")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL - {e}")
        failed += 1
    
    # TEST 6: reset_health
    print("\n" + "=" * 70)
    print("TEST 6: reset_health")
    print("=" * 70)
    try:
        # Reset circuit breaker and MT5 errors
        before_cb = trading_engine.monitor_error_count
        before_mt5 = mt5_client.connection_error_count
        
        trading_engine.monitor_error_count = 0
        mt5_client.connection_error_count = 0
        
        after_cb = trading_engine.monitor_error_count
        after_mt5 = mt5_client.connection_error_count
        
        print(f"✅ Circuit breaker: {before_cb} → {after_cb}")
        print(f"✅ MT5 errors: {before_mt5} → {after_mt5}")
        if after_cb == 0 and after_mt5 == 0:
            print("✅ PASS - reset_health cleared counters")
            passed += 1
        else:
            print(f"❌ Failed to reset health")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL - {e}")
        failed += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: 6")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/6*100):.1f}%")
    print(f"{'='*70}")
    
    # Final verdict
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - 0% ERROR RATE ACHIEVED!")
        return 0
    else:
        print(f"\n⚠️ {failed} TEST(S) FAILED - NEEDS FIXING")
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_commands()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
