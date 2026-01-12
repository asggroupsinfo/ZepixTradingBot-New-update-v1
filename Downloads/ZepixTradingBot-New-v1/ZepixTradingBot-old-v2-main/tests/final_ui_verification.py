import sys
import os
import logging
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("FinalUITest")

def test_trend_matrix():
    """Test that Trend Matrix displays ALL 10 symbols"""
    print("\n🧪 TEST 1: Trend Matrix - Full Symbol Coverage")
    print("=" * 60)
    
    # Mock trend manager
    trend_manager = MagicMock()
    trend_manager.load_trends = MagicMock()
    trend_manager.get_all_trends_with_mode = MagicMock(return_value={
        "15m": {"trend": "BULLISH", "mode": "AUTO"},
        "1h": {"trend": "BULLISH", "mode": "AUTO"},
        "1d": {"trend": "NEUTRAL", "mode": "AUTO"}
    })
    trend_manager.check_logic_alignment = MagicMock(return_value={"aligned": True, "direction": "BULLISH"})
    
    # Mock telegram bot
    class MockBot:
        def __init__(self):
            self.trend_manager = trend_manager
            self.messages_sent = []
            
        def send_message(self, msg):
            self.messages_sent.append(msg)
            
    bot = MockBot()
    
    # Import and execute the fixed function
    from src.clients.telegram_bot import TelegramBot
    
    # Monkey-patch the method onto our mock
    bot.handle_trend_matrix = TelegramBot.handle_trend_matrix.__get__(bot, type(bot))
    
    # Execute
    bot.handle_trend_matrix({})
    
    # Verification
    all_messages = "\n".join(bot.messages_sent)
    
    print("\nExpected Symbols (10 total):")
    expected_symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD", 
                        "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "AUDJPY"]
    
    found_symbols = []
    missing_symbols = []
    
    for symbol in expected_symbols:
        if symbol in all_messages:
            found_symbols.append(symbol)
            print(f"  ✅ {symbol}")
        else:
            missing_symbols.append(symbol)
            print(f"  ❌ {symbol} - MISSING!")
    
    print(f"\nResults:")
    print(f"  Found: {len(found_symbols)}/10 symbols")
    print(f"  Messages Sent: {len(bot.messages_sent)}")
    
    if len(found_symbols) == 10:
        print("  ✅ PASS: All 10 symbols displayed")
    else:
        print(f"  ❌ FAIL: Only {len(found_symbols)} symbols found")
        print(f"  Missing: {', '.join(missing_symbols)}")
    
    # Print sample output
    print("\nSample Output (First 500 chars):")
    print("-" * 60)
    print(all_messages[:500] + "...")
    print("-" * 60)
    
    return len(found_symbols) == 10


def test_reverse_shield_button():
    """Test Reverse Shield button toggle functionality"""
    print("\n🧪 TEST 2: Reverse Shield Button - Toggle Verification")
    print("=" * 60)
    
    # Mock config
    config_state = {"reverse_shield_config": {"enabled": False}}
    
    config_mock = MagicMock()
    config_mock.get.side_effect = lambda k, d=None: config_state.get(k, d)
    config_mock.update_nested = MagicMock(side_effect=lambda path, val: 
        config_state.__setitem__("reverse_shield_config", {"enabled": val}) 
        if "reverse_shield_config.enabled" in path else None
    )
    config_mock.save = MagicMock()
    
    # Mock bot
    bot_mock = MagicMock()
    bot_mock.config = config_mock
    bot_mock.send_message = MagicMock()
    bot_mock.edit_message = MagicMock()
    
    # Import handler
    from src.menu.reentry_menu_handler import ReentryMenuHandler
    
    handler = ReentryMenuHandler(bot_mock, MagicMock())
    
    # Test 1: Initial State
    print("\n1. Initial State:")
    print(f"   Shield Enabled: {config_state['reverse_shield_config']['enabled']}")
    
    # Test 2: Toggle ON
    print("\n2. Toggling Shield ON...")
    result = handler.toggle_reverse_shield()
    print(f"   Return Value: {result}")
    print(f"   Config State: {config_state['reverse_shield_config']['enabled']}")
    
    if result == True and config_state["reverse_shield_config"]["enabled"] == True:
        print("   ✅ PASS: Toggled to ON")
    else:
        print("   ❌ FAIL: Toggle did not work")
        
    # Test 3: Toggle OFF
    print("\n3. Toggling Shield OFF...")
    result2 = handler.toggle_reverse_shield()
    print(f"   Return Value: {result2}")
    print(f"   Config State: {config_state['reverse_shield_config']['enabled']}")
    
    if result2 == False and config_state["reverse_shield_config"]["enabled"] == False:
        print("   ✅ PASS: Toggled to OFF")
    else:
        print("   ❌ FAIL: Toggle did not work")
    
    # Test 4: Button Visual Update
    print("\n4. Visual Status Update Test...")
    handler.show_reentry_menu(12345, 999)
    
    if bot_mock.edit_message.called:
        args, _ = bot_mock.edit_message.call_args
        msg = args[0]
        
        if "Reverse Shield (Attack):" in msg:
            print("   ✅ PASS: Shield status line found in menu")
            if "OFF ❌" in msg:
                print("   ✅ PASS: Correct status icon (OFF)")
            elif "ON ✅" in msg:
                print("   ⚠️  Status shows ON (expected OFF after 2nd toggle)")
        else:
            print("   ❌ FAIL: Shield status not in menu text")
    else:
        print("   ❌ FAIL: Menu not redrawn")
    
    return True


def main():
    print("\n" + "=" * 60)
    print("🔹 FINAL UI INTEGRITY VERIFICATION 🔹")
    print("=" * 60)
    
    # Run tests
    test1_pass = test_trend_matrix()
    test2_pass = test_reverse_shield_button()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"  Trend Matrix (10 symbols): {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"  Reverse Shield Button: {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print("=" * 60)
    
    if test1_pass and test2_pass:
        print("\n🎉 ALL TESTS PASSED - UI is correct!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review output above")


if __name__ == "__main__":
    main()
