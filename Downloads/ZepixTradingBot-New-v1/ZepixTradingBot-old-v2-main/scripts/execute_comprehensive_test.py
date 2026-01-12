#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Execution Script
Actually deploys bot and tests all systems
"""
import os
import sys
import time
import subprocess
import requests
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("PHASE 1: MODULE IMPORT TESTING")
    print("=" * 60)
    
    tests = []
    
    # Core modules
    try:
        from src.config import Config
        tests.append(("Config", True))
    except Exception as e:
        tests.append(("Config", False, str(e)))
    
    try:
        from src.core.trading_engine import TradingEngine
        tests.append(("TradingEngine", True))
    except Exception as e:
        tests.append(("TradingEngine", False, str(e)))
    
    try:
        from src.managers.profit_booking_manager import ProfitBookingManager
        tests.append(("ProfitBookingManager", True))
    except Exception as e:
        tests.append(("ProfitBookingManager", False, str(e)))
    
    try:
        from src.utils.profit_sl_calculator import ProfitBookingSLCalculator
        tests.append(("ProfitBookingSLCalculator", True))
    except Exception as e:
        tests.append(("ProfitBookingSLCalculator", False, str(e)))
    
    try:
        from src.services.price_monitor_service import PriceMonitorService
        tests.append(("PriceMonitorService", True))
    except Exception as e:
        tests.append(("PriceMonitorService", False, str(e)))
    
    try:
        from src.managers.dual_order_manager import DualOrderManager
        tests.append(("DualOrderManager", True))
    except Exception as e:
        tests.append(("DualOrderManager", False, str(e)))
    
    # Print results
    all_passed = True
    for test in tests:
        if test[1]:
            print(f"[OK] {test[0]}: OK")
        else:
            print(f"[FAIL] {test[0]}: FAILED - {test[2]}")
            all_passed = False
    
    return all_passed

def test_configuration():
    """Test configuration loading"""
    print("\n" + "=" * 60)
    print("PHASE 2: CONFIGURATION TESTING")
    print("=" * 60)
    
    try:
        from src.config import Config
        config = Config()
        
        # Check symbols
        symbols = list(config.get("symbol_config", {}).keys())
        print(f"[OK] Symbols configured: {len(symbols)}")
        print(f"   Symbols: {', '.join(symbols[:5])}...")
        
        # Check re-entry config
        re_entry = config.get("re_entry_config", {})
        print(f"[OK] Re-entry config loaded")
        print(f"   SL Hunt: {re_entry.get('sl_hunt_reentry_enabled', False)}")
        print(f"   TP Re-entry: {re_entry.get('tp_reentry_enabled', False)}")
        print(f"   Exit Continuation: {re_entry.get('exit_continuation_enabled', False)}")
        
        # Check profit booking config
        profit_config = config.get("profit_booking_config", {})
        print(f"[OK] Profit booking config loaded")
        print(f"   Enabled: {profit_config.get('enabled', False)}")
        print(f"   Min Profit: ${profit_config.get('min_profit', 7.0)}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Configuration test failed: {e}")
        return False

def test_telegram_commands():
    """Test Telegram command handlers"""
    print("\n" + "=" * 60)
    print("PHASE 3: TELEGRAM COMMANDS TESTING")
    print("=" * 60)
    
    try:
        from src.clients.telegram_bot import TelegramBot
        from src.config import Config
        
        config = Config()
        bot = TelegramBot(config)
        
        commands = list(bot.command_handlers.keys())
        print(f"[OK] Found {len(commands)} Telegram commands")
        
        # Verify key commands exist
        key_commands = [
            "/start", "/status", "/logic_status", "/tp_system",
            "/sl_hunt", "/exit_continuation", "/profit_status",
            "/dual_order_status", "/risk_status", "/clear_loss_data"
        ]
        
        missing = []
        for cmd in key_commands:
            if cmd in bot.command_handlers:
                print(f"[OK] {cmd}: Handler exists")
            else:
                print(f"[FAIL] {cmd}: Handler missing")
                missing.append(cmd)
        
        if missing:
            print(f"[WARN] Missing commands: {missing}")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Telegram commands test failed: {e}")
        return False

def test_profit_booking_system():
    """Test profit booking system"""
    print("\n" + "=" * 60)
    print("PHASE 4: PROFIT BOOKING SYSTEM TESTING")
    print("=" * 60)
    
    try:
        from src.managers.profit_booking_manager import ProfitBookingManager
        from src.utils.profit_sl_calculator import ProfitBookingSLCalculator
        from src.config import Config
        
        config = Config()
        
        # Test SL calculator
        calc = ProfitBookingSLCalculator(config)
        print(f"[OK] ProfitBookingSLCalculator: OK")
        print(f"   Fixed SL: ${calc.fixed_sl_dollar}")
        
        # Test SL calculation for different symbols
        test_cases = [
            ("XAUUSD", 2640.00, "buy", 0.1),
            ("EURUSD", 1.08000, "buy", 0.1),
            ("USDJPY", 150.00, "buy", 0.1)
        ]
        
        for symbol, price, direction, lot in test_cases:
            try:
                sl_price, sl_distance = calc.calculate_sl_price(price, direction, symbol, lot)
                print(f"[OK] {symbol} SL calculation: OK (SL={sl_price:.5f})")
            except Exception as e:
                print(f"[FAIL] {symbol} SL calculation failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Profit booking system test failed: {e}")
        return False

def test_reentry_systems():
    """Test re-entry systems"""
    print("\n" + "=" * 60)
    print("PHASE 5: RE-ENTRY SYSTEMS TESTING")
    print("=" * 60)
    
    try:
        from src.services.price_monitor_service import PriceMonitorService
        from src.managers.timeframe_trend_manager import TimeframeTrendManager
        from src.config import Config
        
        config = Config()
        
        # Test alignment checks
        trend_manager = TimeframeTrendManager()
        print("[OK] TrendManager: OK")
        
        # Test alignment for different logics
        test_symbol = "XAUUSD"
        for logic in ["LOGIC1", "LOGIC2", "LOGIC3"]:
            result = trend_manager.check_logic_alignment(test_symbol, logic)
            print(f"[OK] {logic} alignment check: OK (aligned={result.get('aligned', False)})")
        
        return True
    except Exception as e:
        print(f"[FAIL] Re-entry systems test failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("PHASE 6: DATABASE TESTING")
    print("=" * 60)
    
    try:
        import sqlite3
        db_path = project_root / "data" / "trading_bot.db"
        
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            print(f"[OK] Database exists: {db_path}")
            print(f"[OK] Tables found: {len(tables)}")
            print(f"   Tables: {', '.join(tables[:5])}...")
            return True
        else:
            print(f"[WARN] Database not found (will be created on first run)")
            return True
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False

def start_bot():
    """Start the bot"""
    print("\n" + "=" * 60)
    print("PHASE 7: BOT DEPLOYMENT")
    print("=" * 60)
    
    try:
        # Check if bot is already running
        try:
            response = requests.get("http://localhost:5000/", timeout=2)
            if response.status_code == 200:
                print("[OK] Bot is already running on port 5000")
                return True
        except:
            pass
        
        # Start bot
        print("Starting bot on port 5000...")
        process = subprocess.Popen(
            [sys.executable, "src/main.py", "--port", "5000"],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Wait for bot to start
        print("Waiting for bot to start...")
        for i in range(30):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:5000/", timeout=2)
                if response.status_code == 200:
                    print("[OK] Bot started successfully on port 5000")
                    return True
            except:
                if i % 5 == 0:
                    print(f"   Waiting... ({i+1}/30)")
        
        print("[WARN] Bot may not have started (check manually)")
        return False
    except Exception as e:
        print(f"[FAIL] Bot deployment failed: {e}")
        return False

def test_webhook():
    """Test webhook endpoint"""
    print("\n" + "=" * 60)
    print("PHASE 8: WEBHOOK TESTING")
    print("=" * 60)
    
    try:
        # Test webhook endpoint
        alert_data = {
            "symbol": "XAUUSD",
            "signal": "BUY",
            "price": 2640.00,
            "signal_type": "entry",
            "strategy": "LOGIC1",
            "tf": "5m",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            "http://localhost:5000/webhook",
            json=alert_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("[OK] Webhook endpoint responding")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"[WARN] Webhook returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[WARN] Bot not running - cannot test webhook")
        return False
    except Exception as e:
        print(f"[FAIL] Webhook test failed: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("COMPREHENSIVE END-TO-END TESTING EXECUTION")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bot Version: Zepix Trading Bot v2.0")
    print()
    
    results = {}
    
    # Phase 1: Module imports
    results["imports"] = test_imports()
    
    # Phase 2: Configuration
    results["configuration"] = test_configuration()
    
    # Phase 3: Telegram commands
    results["telegram"] = test_telegram_commands()
    
    # Phase 4: Profit booking
    results["profit_booking"] = test_profit_booking_system()
    
    # Phase 5: Re-entry systems
    results["reentry"] = test_reentry_systems()
    
    # Phase 6: Database
    results["database"] = test_database()
    
    # Phase 7: Bot deployment
    results["deployment"] = start_bot()
    
    # Phase 8: Webhook
    if results["deployment"]:
        results["webhook"] = test_webhook()
    else:
        results["webhook"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - BOT IS PRODUCTION READY")
    else:
        print("[WARN] SOME TESTS FAILED - REVIEW RESULTS")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

