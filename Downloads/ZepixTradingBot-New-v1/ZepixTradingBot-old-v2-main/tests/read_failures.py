
import os

try:
    # Try UTF-16 first (common for PowerShell redirection)
    try:
        with open('test_output.txt', 'r', encoding='utf-16') as f:
            lines = f.readlines()
    except UnicodeError:
        with open('test_output.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    print("--- FAILURES FOUND ---")
    printing = False
    for line in lines:
        if "FAILED COMMANDS" in line:
            printing = True
        if printing:
            print(line.strip())
        elif "❌" in line or "FAIL" in line or "Traceback" in line:
            print(line.strip())
    print("--- END OF FAILURES ---")
except Exception as e:
    print(f"Error reading file: {e}")
