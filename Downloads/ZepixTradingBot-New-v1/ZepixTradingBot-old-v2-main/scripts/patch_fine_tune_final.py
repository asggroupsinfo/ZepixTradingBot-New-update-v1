"""
Safe Patcher for telegram_bot.py - Integration Step
Integrates FineTuneMenuHandler and Callback Routing
"""

def patch_telegram_bot_fine_tune():
    file_path = "src/clients/telegram_bot.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 1. Add Import
    imported = False
    for i, line in enumerate(lines):
        if 'from src.clients.menu_callback_handler import MenuCallbackHandler' in line:
            if 'FineTuneMenuHandler' not in lines[i+1]:
                lines.insert(i+1, 'from src.menu.fine_tune_menu_handler import FineTuneMenuHandler\n')
                print("✅ Patch 1: Added FineTuneMenuHandler import")
            imported = True
            break
    
    if not imported:
        # Fallback if specific line not found
        for i, line in enumerate(lines):
            if 'import' in line and i > 10:
                lines.insert(i, 'from src.menu.fine_tune_menu_handler import FineTuneMenuHandler\n')
                print("✅ Patch 1: Added FineTuneMenuHandler import (Fallback position)")
                break

    # 2. Add Initialization in set_dependencies based on TradingEngine
    # We need to find set_dependencies and add the init logic
    init_patched = False
    for i in range(len(lines)):
        if 'def set_dependencies(self' in lines[i]:
            # Look for where dependencies are set
            insert_idx = -1
            for j in range(i, i+30):
                if 'self.db = trading_engine.db' in lines[j]:
                    insert_idx = j + 1
                    break
            
            if insert_idx != -1:
                # Check if already patched
                 if not any('self.fine_tune_handler =' in l for l in lines[insert_idx:insert_idx+15]):
                    code_block = [
                        '\n',
                        '            # Initialize Fine-Tune Menu Handler\n',
                        '            if hasattr(trading_engine, "autonomous_manager") and trading_engine.autonomous_manager:\n',
                        '                am = trading_engine.autonomous_manager\n',
                        '                if hasattr(am, "profit_protection") and hasattr(am, "sl_optimizer"):\n',
                        '                    self.fine_tune_handler = FineTuneMenuHandler(self, am.profit_protection, am.sl_optimizer)\n',
                        '                    print("✅ TelegramBot: Fine-Tune Menu Handler initialized")\n',
                        '                else:\n',
                        '                    print("⚠️ TelegramBot: Autonomous Manager missing sub-managers")\n',
                        '                    self.fine_tune_handler = None\n',
                        '            else:\n',
                        '                print("⚠️ TelegramBot: Trading Engine missing autonomous_manager")\n',
                        '                self.fine_tune_handler = None\n'
                    ]
                    for idx, code in enumerate(code_block):
                        lines.insert(insert_idx + idx, code)
                    print("✅ Patch 2: Added FineTuneMenuHandler initialization in set_dependencies")
                    init_patched = True
            break
    
    # 3. Add Callback Routing in handle_callback_query
    # We will hook into the menu_callback_handler section we added previously
    routing_patched = False
    for i in range(len(lines)):
        if 'Delegate action callbacks to MenuCallbackHandler' in lines[i]:
            # Insert BEFORE this line (Fine tune takes priority or sits alongside)
            # Actually, let's insert AFTER functionality to avoid breaking flow, or check if we can insert 
            # specifically for ft_ prefix.
            
            # Find the spot before "cmd_" handling or after action callback
            insert_spot = -1
            for j in range(i, i+20):
                if '# Handle command selection' in lines[j]:
                    insert_spot = j
                    break
            
            if insert_spot != -1:
                 if not any('callback_data.startswith("ft_")' in l for l in lines[insert_spot-10:insert_spot]):
                    code_block = [
                        '            \n',
                        '            # Handle Fine-Tune Callbacks (ft_, pp_, slr_)\n',
                        '            if callback_data.startswith("ft_") or callback_data.startswith("pp_") or callback_data.startswith("slr_"):\n',
                        '                if hasattr(self, "fine_tune_handler") and self.fine_tune_handler:\n',
                        '                    if callback_data.startswith("pp_"):\n',
                        '                        self.fine_tune_handler.handle_profit_protection_callback(callback_query)\n',
                        '                    elif callback_data.startswith("slr_"):\n',
                        '                        self.fine_tune_handler.handle_sl_reduction_callback(callback_query)\n',
                        '                    else:\n',
                        '                        # ft_ or specific menu navigation\n',
                        '                        if callback_data == "ft_profit_protection":\n',
                        '                            self.fine_tune_handler.show_profit_protection_menu(user_id)\n',
                        '                        elif callback_data == "ft_sl_reduction":\n',
                        '                            self.fine_tune_handler.show_sl_reduction_menu(user_id)\n',
                        '                        elif callback_data == "ft_recovery_windows":\n',
                        '                             # Show window info (assuming method exists or using default)\n',
                        '                             self.send_message("🔍 Recovery Windows feature coming in next update.", user_id)\n',
                        '                        elif callback_data == "ft_view_all":\n',
                        '                             # Use show_fine_tune_menu as hub\n',
                        '                             self.fine_tune_handler.show_fine_tune_menu(user_id)\n',
                        '                        elif callback_data == "fine_tune_menu":\n',
                        '                             self.fine_tune_handler.show_fine_tune_menu(user_id)\n',
                        '                        else:\n',
                        '                             # Default fallback\n',
                        '                             self.fine_tune_handler.show_fine_tune_menu(user_id)\n',
                        '                    return\n',
                        '                else:\n',
                        '                    self.send_message("❌ Fine-Tune system not initialized. Please restart bot.")\n',
                        '                    return\n'
                    ]
                    for idx, code in enumerate(code_block):
                        lines.insert(insert_spot + idx, code)
                    print("✅ Patch 3: Added Fine-Tune callback routing")
                    routing_patched = True
            break

    # Write the patched file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ TELEGRAM BOT PATCHED FOR FINE-TUNE SYSTEM!")

if __name__ == "__main__":
    try:
        patch_telegram_bot_fine_tune()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
