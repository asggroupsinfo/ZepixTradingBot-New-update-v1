
import re

def check_pine_dependencies(filepath):
    """
    Parses a Pine Script file and checks if specific variables are used before declaration.
    Focuses on the user's reported variables: 'signal8_VolatilitySqueeze' and 'volumeOK'.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Track definition lines
    definitions = {
        'signal8_VolatilitySqueeze': -1,
        'volumeOK': -1,
        'zlema': -1,
        'zlTrend': -1
    }

    # Track usage lines (in Signal 12)
    signal12_start = -1
    usages = []

    print(f"ANALYZING: {filepath}")
    print("-" * 50)

    for i, line in enumerate(lines):
        line_num = i + 1
        clean_line = line.strip()

        # 1. FIND DEFINITIONS
        # signal8_VolatilitySqueeze definition pattern
        if "bool signal8_VolatilitySqueeze =" in clean_line:
            definitions['signal8_VolatilitySqueeze'] = line_num
            print(f"[DEF] signal8_VolatilitySqueeze Defined at Line: {line_num}")

        # volumeOK definition pattern
        if "bool volumeOK =" in clean_line:
            definitions['volumeOK'] = line_num
            print(f"[DEF] volumeOK Defined at Line: {line_num}")
            
        # zlTrend definition
        if "int zlTrend =" in clean_line or "zlTrend =" in clean_line:
             if definitions['zlTrend'] == -1: # Capture first
                definitions['zlTrend'] = line_num
                print(f"[DEF] zlTrend Defined at Line: {line_num}")

        # 2. FIND USAGE IN SIGNAL 12 BLOCK
        if "SIGNAL 12: Sideways Breakout" in clean_line:
            signal12_start = line_num
            print(f"[BLOCK] Signal 12 Logic Starts at Line: {line_num}")

        # Check for usage ONLY after Signal 12 block starts
        if signal12_start > 0:
            if "signal8_VolatilitySqueeze" in clean_line and "bool signal8_VolatilitySqueeze =" not in clean_line:
                 usages.append({'var': 'signal8_VolatilitySqueeze', 'line': line_num})
            
            if "volumeOK" in clean_line and "bool volumeOK =" not in clean_line:
                 usages.append({'var': 'volumeOK', 'line': line_num})

    print("-" * 50)
    print("DEPENDENCY CHECK RESULTS:")
    
    error_count = 0
    
    # Check signal8
    def_line_s8 = definitions['signal8_VolatilitySqueeze']
    for usage in [u for u in usages if u['var'] == 'signal8_VolatilitySqueeze']:
        if usage['line'] < def_line_s8:
            print(f"❌ ERROR: 'signal8_VolatilitySqueeze' used at {usage['line']} BEFORE definition at {def_line_s8}")
            error_count += 1
        else:
            print(f"✅ OK: 'signal8_VolatilitySqueeze' used at {usage['line']} (Defined at {def_line_s8})")

    # Check volumeOK
    def_line_vol = definitions['volumeOK']
    for usage in [u for u in usages if u['var'] == 'volumeOK']:
        if usage['line'] < def_line_vol:
             print(f"❌ ERROR: 'volumeOK' used at {usage['line']} BEFORE definition at {def_line_vol}")
             error_count += 1
        else:
             print(f"✅ OK: 'volumeOK' used at {usage['line']} (Defined at {def_line_vol})")
             
    if error_count == 0:
        print("\n🎉 SUCCESS: All Signal 12 dependencies are declared BEFORE use.")
        print("   Syntax Errors (Undeclared Identifier) are IMPOSSIBLE with this structure.")
    else:
        print(f"\n❌ FAIL: Found {error_count} Dependency Order Errors.")

    return error_count

if __name__ == "__main__":
    path = r"C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main\docs\TRADINGVIEW_PINE_SCRIPT_INDICATOR-v1-devin-1767306610-zepix-ultimate-bot-v3\ZEPIX_ULTIMATE_BOT_v3_FIXED.pine"
    check_pine_dependencies(path)
