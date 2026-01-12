
import re

try:
    with open('master_audit_latest.log', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    print("--- LOG ANALYSIS ---")
    
    # Check Order B
    order_b_match = re.search(r"💰 Order B \(Profit Trail\):(.*?)(?=Risk:)", content, re.DOTALL)
    if order_b_match:
        print("FOUND ORDER B DATA:")
        print(order_b_match.group(1).strip())
    else:
        print("ORDER B DATA NOT FOUND")

    # Check Scenario 4
    if "Position remaining open" in content:
        print("\nSCENARIO 4 STATUS: ✅ Position remaining open (Margin Logic Successfully Removed).")
    elif "EMERGENCY CLOSE" in content:
        print("\nSCENARIO 4 STATUS: ❌ FAIL (Emergency Close Triggered)")
    else:
        print("\nSCENARIO 4 STATUS: ❓ UNKNOWN")

    print("\n--- FULL RELEVANT LOGS ---")
    # Print the "DUAL ORDER PLACED" section
    start_idx = content.find("🎯 DUAL ORDER PLACED")
    end_idx = content.find("SCENARIO 2")
    if start_idx != -1:
        print(content[start_idx:end_idx if end_idx != -1 else None])

except Exception as e:
    print(f"Error reading log: {e}")
