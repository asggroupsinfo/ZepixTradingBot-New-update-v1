
try:
    with open(r"src\core\trading_engine.py", "rb") as f:
        content = f.read()
    
    # Remove null bytes
    clean_content = content.replace(b'\x00', b'')
    
    # Try decoding
    text = clean_content.decode('utf-8', errors='replace')
    
    with open("temp_trading_engine_clean.py", "w", encoding="utf-8") as f:
        f.write(text)
        
    print("Cleaned file saved to temp_trading_engine_clean.py")
except Exception as e:
    print(f"Error: {e}")
