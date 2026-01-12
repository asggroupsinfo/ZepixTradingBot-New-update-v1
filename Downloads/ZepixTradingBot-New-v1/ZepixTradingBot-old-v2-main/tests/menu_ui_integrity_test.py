import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.clients.telegram_bot import TelegramBot
from src.menu.reentry_menu_handler import ReentryMenuHandler
from src.menu.menu_manager import MenuManager

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("MenuTest")

async def run_menu_test():
    print("\n🔹 MENU UI INTEGRITY TEST 🔹\n")
    
    # --- MOCK SETUP ---
    # We need a Config object that supports update_nested and save
    config_dict = {
        "reverse_shield_config": {"enabled": False},
        "re_entry_config": {
            "autonomous_config": {
                "enabled": True,
                "tp_continuation": {"enabled": True},
                "sl_hunt_recovery": {"enabled": False},
                "exit_continuation": {"enabled": True}
            }
        },
        "default_risk_tier": "5000"
    }

    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = lambda k: config_dict.get(k)
    config_mock.get.side_effect = lambda k, d=None: config_dict.get(k, d)
    
    def update_nested(path, val):
        print(f"   [Config Update] {path} -> {val}")
        # Simplistic nester
        if path == "reverse_shield_config.enabled":
            config_dict["reverse_shield_config"]["enabled"] = val
        elif path == "re_entry_config.autonomous_config.enabled":
            config_dict["re_entry_config"]["autonomous_config"]["enabled"] = val
    
    config_mock.update_nested.side_effect = update_nested
    config_mock.save.side_effect = lambda: print("   [Config Saved]")
    
    # Mock Bot
    with patch('requests.Session'):
        telegram_bot = TelegramBot(config_mock)
    
    telegram_bot.send_message = MagicMock()
    telegram_bot.edit_message = MagicMock()
    telegram_bot.send_message_with_keyboard = MagicMock()
    
    # Initialize Handlers
    reentry_handler = ReentryMenuHandler(telegram_bot, MagicMock())
    telegram_bot.reentry_menu_handler = reentry_handler
    
    menu_manager = MenuManager(telegram_bot)
    telegram_bot.menu_manager = menu_manager

    # --- TEST 1: REVERSE SHIELD TOGGLE BUTTON ---
    print("🧪 TEST 1: Reverse Shield Button Toggle")
    print("---------------------------------------")
    
    print("Action: Clicking 'toggle_reverse_shield'...")
    # Simulate Callback
    reentry_handler.handle_toggle_callback("toggle_reverse_shield", 12345, 999)
    
    # Verify Config Change
    is_enabled = config_dict["reverse_shield_config"]["enabled"]
    if is_enabled:
         print("✅ PASS: Config toggled to TRUE")
    else:
         print("❌ FAIL: Config did not toggle")
         
    # Verify Menu Redraw
    print("\nVerifying Menu Visuals...")
    # Check last call to edit_message or send_message_with_keyboard
    if telegram_bot.edit_message.called:
        args,_ = telegram_bot.edit_message.call_args
        msg_text = args[0]
        keyboard = args[2]
        
        if "Reverse Shield (Attack): ON ✅" in msg_text:
             print("✅ PASS: Status Text Updated (ON ✅)")
        else:
             print(f"❌ FAIL: Status text incorrect: {msg_text[:100]}...")
             
        # Check if button exists in keyboard
        found_btn = False
        for row in keyboard["inline_keyboard"]:
            for btn in row:
                if "Reverse Shield" in btn["text"]:
                    found_btn = True
                    print(f"   Found Button: {btn['text']}")
        if found_btn:
            print("✅ PASS: Shield Button Present")
        else:
            print("❌ FAIL: Shield Button missing from layout")

    # --- TEST 2: SL SYSTEM MENU REGRESSION CHECK ---
    print("\n🧪 TEST 2: SL System Menu Verification")
    print("---------------------------------------")
    
    print("Action: Opening 'SL System' Category Menu...")
    menu_manager.show_category_menu(12345, "sl_system", 999)
    
    # Check Output
    args, _ = telegram_bot.edit_message.call_args
    menu_text = args[0]
    keyboard = args[2]
    
    print(f"Menu Title: {menu_text.splitlines()[0]}")
    
    # Verify Buttons
    expected_buttons = ["Sl Status", "Sl System Change", "View Sl Config"]
    found_count = 0
    for row in keyboard["inline_keyboard"]:
        for btn in row:
            txt = btn["text"]
            # Remove emojis for check
            clean_txt = "".join(c for c in txt if c.isalnum() or c.isspace()).strip()
            if clean_txt in expected_buttons:
                found_count += 1
                print(f"   found button: {txt}")
    
    if found_count >= 2:
        print("✅ PASS: SL System Menu Buttons Restored")
    else:
        print(f"❌ FAIL: Only found {found_count} buttons. Menu might be empty.")

    print("\n🔹 MENU TEST COMPLETE 🔹")

if __name__ == "__main__":
    asyncio.run(run_menu_test())
