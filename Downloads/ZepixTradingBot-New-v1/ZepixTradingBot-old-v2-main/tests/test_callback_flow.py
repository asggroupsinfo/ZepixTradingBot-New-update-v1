import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Simulate callback_data parsing
from src.menu.menu_constants import COMMAND_CATEGORIES

def test_callback_parsing():
    test_cases = [
        "cmd_sl_system_sl_status",
        "cmd_sl_system_sl_system_change", 
        "cmd_profit_profit_sl_mode"
    ]
    
    category_names = sorted(COMMAND_CATEGORIES.keys(), key=len, reverse=True)
    
    for callback_data in test_cases:
        remaining = callback_data[4:]  # Remove "cmd_"
        category = None
        command = None
        
        for cat_name in category_names:
            if remaining.startswith(cat_name + "_"):
                category = cat_name
                command = remaining[len(cat_name) + 1:]
                break
        
        print(f"Callback: {callback_data}")
        print(f"  Category: {category}")
        print(f"  Command: {command}")
        print(f"  Valid: {category in COMMAND_CATEGORIES and command in COMMAND_CATEGORIES.get(category, {}).get('commands', {})}")
        print()

if __name__ == "__main__":
    test_callback_parsing()
