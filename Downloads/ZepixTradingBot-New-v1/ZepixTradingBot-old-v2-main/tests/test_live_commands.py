"""
LIVE COMMAND TESTING - Tests actual command handlers
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.managers.risk_manager import RiskManager
from src.clients.mt5_client import MT5Client
from src.clients.telegram_bot import TelegramBot
from src.core.trading_engine import TradingEngine
from src.processors.alert_processor import AlertProcessor

print("="*70)
print("LIVE COMMAND HANDLER TESTING")
print("="*70)

# Initialize all components
print("\n[1/5] Initializing components...")
config = Config()
risk_manager = RiskManager(config)
mt5_client = MT5Client(config)
telegram_bot = TelegramBot(config)
alert_processor = AlertProcessor(config)

print("[2/5] Creating trading engine...")
trading_engine = TradingEngine(config, risk_manager, mt5_client, telegram_bot, alert_processor)

print("[3/5] Setting dependencies...")
telegram_bot.set_dependencies(risk_manager, trading_engine)

print("[4/5] Verifying dependencies...")
checks = {
    "trading_engine set": telegram_bot.trading_engine is not None,
    "profit_booking_manager set": telegram_bot.profit_booking_manager is not None,
    "profit_sl_calculator exists": hasattr(telegram_bot.profit_booking_manager, 'profit_sl_calculator'),
    "profit_sl_calculator initialized": telegram_bot.profit_booking_manager.profit_sl_calculator is not None,
}

all_ok = True
for check, result in checks.items():
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} {check}")
    if not result:
        all_ok = False

if not all_ok:
    print("\n[ERROR] Dependencies not set correctly!")
    sys.exit(1)

print("\n[5/5] Testing command handlers...")

# Mock message object
class MockMessage:
    def __init__(self, text):
        self.text = text
        self.data = {'text': text}
    
    def get(self, key, default=None):
        return self.data.get(key, default)

# Test each command
commands_to_test = [
    ("/profit_sl_status", "handle_profit_sl_status"),
    ("/profit_sl_mode SL-2.1", "handle_profit_sl_mode"),
    ("/enable_profit_sl", "handle_enable_profit_sl"),
    ("/disable_profit_sl", "handle_disable_profit_sl"),
    ("/set_profit_sl LOGIC1 25", "handle_set_profit_sl"),
    ("/reset_profit_sl", "handle_reset_profit_sl"),
]

print("\nTesting command execution:")
results = {}

# Override send_message to capture responses
original_send = telegram_bot.send_message
captured_messages = []

def capture_send(message):
    captured_messages.append(message)
    # Remove emojis for console output
    safe_msg = message.encode('ascii', 'ignore').decode('ascii')
    print(f"  -> Response: {safe_msg[:100]}...")

telegram_bot.send_message = capture_send

for cmd_text, handler_name in commands_to_test:
    print(f"\nTesting: {cmd_text}")
    try:
        message = MockMessage(cmd_text)
        handler = telegram_bot.command_handlers.get(cmd_text.split()[0])
        
        if handler:
            print(f"  [OK] Handler found: {handler_name}")
            try:
                handler(message)
                if captured_messages:
                    last_msg = captured_messages[-1]
                    if "Error" in last_msg or "not available" in last_msg:
                        print(f"  [WARN] Handler executed but returned error")
                        print(f"         Message: {last_msg[:150]}")
                    else:
                        print(f"  [OK] Handler executed successfully")
                    results[cmd_text] = "OK"
                else:
                    print(f"  [WARN] Handler executed but no message sent")
                    results[cmd_text] = "WARN"
            except Exception as e:
                print(f"  [FAIL] Handler crashed: {str(e)}")
                import traceback
                traceback.print_exc()
                results[cmd_text] = "FAIL"
        else:
            print(f"  [FAIL] Handler not found in command_handlers")
            results[cmd_text] = "FAIL"
    except Exception as e:
        print(f"  [FAIL] Test failed: {str(e)}")
        results[cmd_text] = "FAIL"

# Restore original send_message
telegram_bot.send_message = original_send

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

all_passed = True
for cmd, result in results.items():
    status = "[OK]" if result == "OK" else "[WARN]" if result == "WARN" else "[FAIL]"
    print(f"{status} {cmd}")
    if result == "FAIL":
        all_passed = False

print("\n" + "="*70)
if all_passed:
    print("[SUCCESS] All commands can be executed")
    print("Next: Test in actual Telegram to see responses")
else:
    print("[FAILURE] Some commands failed - check errors above")
print("="*70)

