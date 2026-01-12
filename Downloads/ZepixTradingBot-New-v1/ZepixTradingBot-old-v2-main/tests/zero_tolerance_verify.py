
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.clients.telegram_bot import TelegramBot
# from src.config.config_manager import ConfigManager # Does not exist
import importlib.util

# Dynamic import for src.config since it's a module
spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(__file__), "..", "src", "config.py"))
config_module = importlib.util.module_from_spec(spec)
sys.modules["src.config"] = config_module
spec.loader.exec_module(config_module)
ConfigManager = config_module.Config  # Use Config class as ConfigManager for compatibility

def detailed_verification():
    print("=== STARTING ZERO TOLERANCE VERIFICATION ===")
    
    # 1. Config Verification
    print("\n[VERIFYING CONFIG SETUP]")
    try:
        # Correct path is config/config.json absolute path
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        strategies = config.get('strategies', [])
        print(f"Strategies found: {strategies}")
        
        expected = ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]
        if sorted(strategies) != sorted(expected):
            print(f"❌ FATAL: Strategy mismatch! Expected {expected}, got {strategies}")
            sys.exit(1)
        else:
            print("✅ Config strategies are correct.")
    except Exception as e:
        print(f"❌ Config load failed: {e}")
        sys.exit(1)

    # 2. Logic Handler Mapping Verification
    print("\n[VERIFYING HANDLER MAPPING]")
    # We mock the bot to test its method existence and logic
    try:
        mock_engine = MagicMock()
        mock_engine.get_logic_status.return_value = {
            "combinedlogic-1": True,
            "combinedlogic-2": False,
            "combinedlogic-3": True
        }
        
        # TelegramBot takes config as first arg, not config_manager
        # Attempt to init with just config object (it expects object with __getitem__)
        bot = TelegramBot(config=ConfigManager())
        bot.trading_engine = mock_engine
        
        required_handlers = [
            "handle_logic1_on", "handle_logic1_off",
            "handle_logic2_on", "handle_logic2_off",
            "handle_logic3_on", "handle_logic3_off",
            "handle_logic_control", "handle_logic_status"
        ]
        
        for handler in required_handlers:
            if hasattr(bot, handler):
                print(f"✅ Handler {handler} exists.")
            else:
                print(f"❌ FATAL: Missing handler {handler}")
                sys.exit(1)
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Bot init failed: {e}")
        sys.exit(1)

    # 3. Simulate Logic Toggling
    print("\n[VERIFYING LOGIC TOGGLE CALLS]")
    try:
        # Create a mock config that behaves like the actual Config object
        mock_config = MagicMock()
        strategies_list = ["combinedlogic-1", "combinedlogic-3"] # Simulate logic 2 is off initially
        
        def get_item(key):
            if key == "telegram_token": return "TEST_TOKEN"
            if key == "telegram_chat_id": return 123456
            if key == "strategies": return strategies_list
            return None
            
        def set_item(key, value):
            if key == "strategies":
                nonlocal strategies_list
                strategies_list = value
                
        mock_config.__getitem__.side_effect = get_item
        mock_config.__setitem__.side_effect = set_item
        mock_config.get.side_effect = lambda k, d=None: strategies_list if k == 'strategies' else d

        # Re-init bot with mock config
        bot = TelegramBot(config=mock_config)
        bot.trading_engine = MagicMock() # Re-attach mock engine
        bot.send_message = MagicMock() # Mock send_message

        # Test logic1_off (should remove combinedlogic-1)
        mock_message = {"chat": {"id": 123}, "message_id": 999}
        
        print("Testing /logic1_off...")
        bot.handle_logic1_off(mock_message)
        
        # Verify save_config called and strategy removed
        if "combinedlogic-1" not in strategies_list:
             print("✅ handle_logic1_off successfully removed 'combinedlogic-1'")
        else:
             print("❌ handle_logic1_off FAILED to remove 'combinedlogic-1'")
             sys.exit(1)
             
        mock_config.save_config.assert_called()
        print("✅ handle_logic1_off triggered save_config()")
        
        # Test logic2_on (should add combinedlogic-2)
        print("Testing /logic2_on...")
        bot.handle_logic2_on(mock_message)
        
        if "combinedlogic-2" in strategies_list:
            print("✅ handle_logic2_on successfully added 'combinedlogic-2'")
        else:
            print("❌ handle_logic2_on FAILED to add 'combinedlogic-2'")
            sys.exit(1)
            
        mock_config.save_config.assert_called()
        print("✅ handle_logic2_on triggered save_config()")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Logic toggle simulation failed: {e}")
        sys.exit(1)

    print("\n=== ZERO TOLERANCE VERIFICATION PASSED ===")

if __name__ == "__main__":
    detailed_verification()
