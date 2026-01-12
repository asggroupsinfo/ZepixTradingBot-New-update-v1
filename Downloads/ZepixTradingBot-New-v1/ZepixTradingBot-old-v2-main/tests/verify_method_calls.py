import os

# Check if get_closed_trade_profit is being used in trading_engine.py
file_path = r"src\core\trading_engine.py"

try:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    if "get_closed_trade_profit" in content:
        print("✅ METHOD CALL FOUND in trading_engine.py")
        
        # Count occurrences
        count = content.count("get_closed_trade_profit")
        print(f"✅ Found {count} occurrence(s)")
        
        # Show line numbers
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if "get_closed_trade_profit" in line:
                print(f"   Line {i}: {line.strip()}")
    else:
        print("❌ METHOD CALL NOT FOUND")
        
except Exception as e:
    print(f"Error: {e}")
