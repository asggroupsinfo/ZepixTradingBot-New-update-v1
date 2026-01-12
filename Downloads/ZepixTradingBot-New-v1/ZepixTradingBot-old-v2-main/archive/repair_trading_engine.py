
import os

target_file = r"src\core\trading_engine.py"

try:
    print(f"Repairing {target_file}...")
    
    # Read as binary
    with open(target_file, "rb") as f:
        content = f.read()
    
    print(f"Original size: {len(content)} bytes")
    
    # Count null bytes
    null_count = content.count(b'\x00')
    print(f"Found {null_count} null bytes")
    
    if null_count > 0:
        # Remove null bytes
        clean_content = content.replace(b'\x00', b'')
        
        # Write back as binary
        with open(target_file, "wb") as f:
            f.write(clean_content)
            
        print(f"Repaired size: {len(clean_content)} bytes")
        print("✅ Success: File repaired (Null bytes removed)")
    else:
        print("ℹ️ File was already clean (No null bytes found)")

except Exception as e:
    print(f"❌ Error: {e}")
