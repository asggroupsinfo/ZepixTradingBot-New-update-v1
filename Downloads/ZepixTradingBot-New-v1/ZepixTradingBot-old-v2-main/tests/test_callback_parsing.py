"""
Test callback_data parsing for categories with underscores
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.menu.menu_constants import COMMAND_CATEGORIES

def test_callback_parsing():
    """Test that callback_data can be correctly parsed"""
    print("\n=== TESTING CALLBACK PARSING ===\n")
    
    # Test cases: callback_data -> (expected_category, expected_command)
    test_cases = [
        ("cmd_sl_system_sl_status", "sl_system", "sl_status"),
        ("cmd_sl_system_sl_system_change", "sl_system", "sl_system_change"),
        ("cmd_profit_profit_sl_mode", "profit", "profit_sl_mode"),
        ("cmd_trading_pause", "trading", "pause"),
        ("cmd_risk_set_daily_cap", "risk", "set_daily_cap"),
    ]
    
    # Get all category names sorted by length (longest first)
    category_names = sorted(COMMAND_CATEGORIES.keys(), key=len, reverse=True)
    print(f"Category names (sorted by length): {category_names}\n")
    
    all_passed = True
    for callback_data, expected_category, expected_command in test_cases:
        # Remove "cmd_" prefix
        remaining = callback_data[4:]  # Remove "cmd_"
        
        # Try to find matching category
        category = None
        command = None
        
        for cat_name in category_names:
            if remaining.startswith(cat_name + "_"):
                category = cat_name
                command = remaining[len(cat_name) + 1:]  # +1 for the underscore
                break
        
        if category == expected_category and command == expected_command:
            print(f"✅ {callback_data}")
            print(f"   Category: {category} (expected: {expected_category})")
            print(f"   Command: {command} (expected: {expected_command})")
        else:
            print(f"❌ {callback_data}")
            print(f"   Category: {category} (expected: {expected_category})")
            print(f"   Command: {command} (expected: {expected_command})")
            all_passed = False
        print()
    
    if all_passed:
        print("=== ALL TESTS PASSED ===")
        return True
    else:
        print("=== SOME TESTS FAILED ===")
        return False

if __name__ == "__main__":
    success = test_callback_parsing()
    sys.exit(0 if success else 1)

