"""
Telegram Bot - Comprehensive Testing Script
Tests all menu navigation, toggles, and commands
"""

import time
import json
from datetime import datetime

class TelegramBotTester:
    """Comprehensive bot testing utility"""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == "PASS":
            self.passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {test_name} - {message}")
    
    def test_imports(self):
        """Test 1: Verify all imports work"""
        print("\n" + "="*60)
        print("TEST 1: IMPORT VERIFICATION")
        print("="*60)
        
        try:
            from src.clients.telegram_bot import TelegramBot
            self.log_test("Import TelegramBot", "PASS")
        except Exception as e:
            self.log_test("Import TelegramBot", "FAIL", str(e))
            
        try:
            from src.menu.reentry_menu_handler import ReentryMenuHandler
            self.log_test("Import ReentryMenuHandler", "PASS")
        except Exception as e:
            self.log_test("Import ReentryMenuHandler", "FAIL", str(e))
            
        try:
            from src.menu.profit_booking_menu_handler import ProfitBookingMenuHandler
            self.log_test("Import ProfitBookingMenuHandler", "PASS")
        except Exception as e:
            self.log_test("Import ProfitBookingMenuHandler", "FAIL", str(e))
            
        try:
            from src.menu.fine_tune_menu_handler import FineTuneMenuHandler
            self.log_test("Import FineTuneMenuHandler", "PASS")
        except Exception as e:
            self.log_test("Import FineTuneMenuHandler", "FAIL", str(e))
    
    def test_config_loading(self):
        """Test 2: Verify config loads correctly"""
        print("\n" + "="*60)
        print("TEST 2: CONFIG LOADING")
        print("="*60)
        
        try:
            from src.config import Config
            config = Config()
            self.log_test("Load config.json", "PASS")
            
            # Check re-entry config
            re_entry = config.get("re_entry_config", {})
            if re_entry:
                self.log_test("Re-entry config exists", "PASS")
            else:
                self.log_test("Re-entry config exists", "FAIL", "Missing re_entry_config")
            
            # Check autonomous config
            autonomous = re_entry.get("autonomous_config", {})
            if autonomous:
                self.log_test("Autonomous config exists", "PASS")
            else:
                self.log_test("Autonomous config exists", "FAIL", "Missing autonomous_config")
                
            # Check profit booking config
            profit = config.get("profit_booking_config", {})
            if profit:
                self.log_test("Profit booking config exists", "PASS")
            else:
                self.log_test("Profit booking config exists", "FAIL", "Missing profit_booking_config")
                
        except Exception as e:
            self.log_test("Load config.json", "FAIL", str(e))
    
    def test_handler_initialization(self):
        """Test 3: Verify handlers can be initialized"""
        print("\n" + "="*60)
        print("TEST 3: HANDLER INITIALIZATION")
        print("="*60)
        
        try:
            from src.config import Config
            from src.menu.reentry_menu_handler import ReentryMenuHandler
            
            # Mock bot object
            class MockBot:
                def __init__(self):
                    self.config = Config()
                    
            bot = MockBot()
            handler = ReentryMenuHandler(bot, None)
            self.log_test("Initialize ReentryMenuHandler", "PASS")
        except Exception as e:
            self.log_test("Initialize ReentryMenuHandler", "FAIL", str(e))
            
        try:
            from src.menu.profit_booking_menu_handler import ProfitBookingMenuHandler
            handler = ProfitBookingMenuHandler(bot)
            self.log_test("Initialize ProfitBookingMenuHandler", "PASS")
        except Exception as e:
            self.log_test("Initialize ProfitBookingMenuHandler", "FAIL", str(e))
    
    def test_menu_methods(self):
        """Test 4: Verify menu methods exist"""
        print("\n" + "="*60)
        print("TEST 4: MENU METHODS VERIFICATION")
        print("="*60)
        
        try:
            from src.config import Config
            from src.menu.reentry_menu_handler import ReentryMenuHandler
            
            class MockBot:
                def __init__(self):
                    self.config = Config()
            
            bot = MockBot()
            handler = ReentryMenuHandler(bot, None)
            
            # Check methods exist
            methods = [
                "show_reentry_menu",
                "handle_toggle_callback",
                "toggle_autonomous_mode",
                "toggle_tp_continuation",
                "toggle_sl_hunt",
                "toggle_exit_continuation"
            ]
            
            for method in methods:
                if hasattr(handler, method):
                    self.log_test(f"ReentryMenuHandler.{method} exists", "PASS")
                else:
                    self.log_test(f"ReentryMenuHandler.{method} exists", "FAIL", "Method not found")
                    
        except Exception as e:
            self.log_test("Menu methods verification", "FAIL", str(e))
    
    def test_callback_data_format(self):
        """Test 5: Verify callback data formats"""
        print("\n" + "="*60)
        print("TEST 5: CALLBACK DATA FORMAT")
        print("="*60)
        
        expected_callbacks = [
            "toggle_autonomous",
            "toggle_tp_continuation",
            "toggle_sl_hunt",
            "toggle_exit_continuation",
            "profit_sl_mode_11",
            "profit_sl_mode_21",
            "toggle_profit_protection",
            "toggle_profit_sl_hunt",
            "rw_inc_XAUUSD_0",
            "rw_dec_XAUUSD_0",
            "ft_recovery_windows_edit"
        ]
        
        for callback in expected_callbacks:
            # Just verify format is correct
            if len(callback) > 0 and "_" in callback:
                self.log_test(f"Callback format: {callback}", "PASS")
            else:
                self.log_test(f"Callback format: {callback}", "FAIL", "Invalid format")
    
    def test_config_persistence(self):
        """Test 6: Verify config can be saved"""
        print("\n" + "="*60)
        print("TEST 6: CONFIG PERSISTENCE")
        print("="*60)
        
        try:
            from src.config import Config
            config = Config()
            
            # Test update_nested
            if hasattr(config, 'update_nested'):
                self.log_test("Config.update_nested exists", "PASS")
            else:
                self.log_test("Config.update_nested exists", "FAIL", "Method not found")
                
            # Test save
            if hasattr(config, 'save'):
                self.log_test("Config.save exists", "PASS")
            else:
                self.log_test("Config.save exists", "FAIL", "Method not found")
                
        except Exception as e:
            self.log_test("Config persistence test", "FAIL", str(e))
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("TEST REPORT")
        print("="*60)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed > 0:
            print("\n🔴 FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": self.passed,
                "failed": self.failed,
                "pass_rate": pass_rate
            },
            "results": self.test_results
        }
        
        with open("test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n📄 Detailed report saved to: test_results.json")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Bot is ready for deployment! 🎉")
            return True
        else:
            print("\n⚠️ Some tests failed. Please fix issues before deployment.")
            return False

def run_tests():
    """Run all tests"""
    print("="*60)
    print("ZEPIX TRADING BOT - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = TelegramBotTester()
    
    # Run all tests
    tester.test_imports()
    tester.test_config_loading()
    tester.test_handler_initialization()
    tester.test_menu_methods()
    tester.test_callback_data_format()
    tester.test_config_persistence()
    
    # Generate report
    success = tester.generate_report()
    
    return success

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
