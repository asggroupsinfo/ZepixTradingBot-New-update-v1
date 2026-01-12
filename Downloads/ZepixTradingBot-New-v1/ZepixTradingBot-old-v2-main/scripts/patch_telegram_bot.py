"""
Safe Patcher for telegram_bot.py
Applies minimal changes to enable menu callback handling
"""

def patch_telegram_bot():
    file_path = "src/clients/telegram_bot.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Patch 1: Add import (after line 12)
    for i, line in enumerate(lines):
        if 'from src.managers.timeframe_trend_manager import TimeframeTrendManager' in line:
            # Insert new import after this line
            if 'MenuCallbackHandler' not in lines[i+1]:
                lines.insert(i+1, 'from src.clients.menu_callback_handler import MenuCallbackHandler\n')
                print("✅ Patch 1: Added MenuCallbackHandler import")
            break
    
    # Patch 2: Initialize handler in __init__ (after menu_manager initialization)
    for i, line in enumerate(lines):
        if 'self.menu_manager = MenuManager(self)' in line:
            # Check if already patched
            if i+2 < len(lines) and 'menu_callback_handler' not in lines[i+1]:
                lines.insert(i+1, '        \n')
                lines.insert(i+2, '        # Initialize menu callback handler\n')
                lines.insert(i+3, '        self.menu_callback_handler = MenuCallbackHandler(self)\n')
                print("✅ Patch 2: Added MenuCallbackHandler initialization")
            break
    
    # Patch 3: Replace menu navigation code with delegation
    for i, line in enumerate(lines):
        if '# Handle menu navigation' in line and 'if callback_data == "menu_main"' in lines[i+1]:
            # Find the end of menu handling block
            end_idx = i
            for j in range(i, min(i+20, len(lines))):
                if 'elif callback_data == "action' in lines[j] or '# Handle command selection' in lines[j]:
                    end_idx = j
                    break
            
            # Replace this section
            if end_idx > i:
                new_code = [
                    '            # Delegate menu navigation to MenuCallbackHandler\n',
                    '            if self.menu_callback_handler.handle_menu_callback(callback_data, user_id, message_id):\n',
                    '                return\n',
                    '            \n',
                    '            # Delegate action callbacks to MenuCallbackHandler\n',
                    '            if self.menu_callback_handler.handle_action_callback(callback_data, user_id, message_id):\n',
                    '               return\n',
                    '            \n'
                ]
                
                #Replace old lines
                del lines[i:end_idx]
                for idx, new_line in enumerate(new_code):
                    lines.insert(i+idx, new_line)
                
                print("✅ Patch 3: Replaced menu navigation with MenuCallbackHandler delegation")
                break
    
    # Write the patched file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ ALL PATCHES APPLIED SUCCESSFULLY!")
    print("Bot file patched with menu callback handling")

if __name__ == "__main__":
    try:
        patch_telegram_bot()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
