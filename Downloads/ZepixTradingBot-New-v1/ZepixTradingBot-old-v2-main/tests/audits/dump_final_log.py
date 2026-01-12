
import sys

try:
    with open('logs/audit_final_res.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    print(content)
except Exception as e:
    # Try reading from current dir if not in logs/
    try:
        with open('audit_final_res.txt', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print(content)
    except Exception as e2:
        print(f"Error reading log: {e2}")
