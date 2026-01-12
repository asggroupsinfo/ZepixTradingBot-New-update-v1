
try:
    with open('master_audit_verify.log', 'r', encoding='utf-16', errors='ignore') as f:
        content = f.read()
        if "VERIFY ORDER B" in content:
            start = content.find("VERIFY ORDER B")
            end = content.find("\n", start)
            print(content[start:end])
        else:
            print("String not found in utf-16 read.")
            
    # Try utf-8 just in case
    with open('master_audit_verify.log', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if "VERIFY ORDER B" in content:
            start = content.find("VERIFY ORDER B")
            end = content.find("\n", start)
            print(content[start:end])

except Exception as e:
    print(f"Error: {e}")
