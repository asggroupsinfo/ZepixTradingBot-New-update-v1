
try:
    with open('master_audit_fix.log', 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read())
except Exception as e:
    print(f"Error: {e}")
