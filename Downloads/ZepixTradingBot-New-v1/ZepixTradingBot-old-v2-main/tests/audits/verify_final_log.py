
import sys

try:
    with open('master_audit_res.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    print("--- RAW LOG DUMP START ---")
    
    # Filter for relevant lines to keep it concise for the user if needed, or dump all
    # The user asked for "Just the RAW LOGS". I should provide the full relevant sections.
    
    lines = content.splitlines()
    for line in lines:
        # Skip debug noise if seemingly irrelevant, but user asked for raw logs.
        # However, Windows encoding issues made "raw logs" messy in previous steps.
        # I'll print them here so they appear in the tool output cleanly.
        print(line)
        
    print("--- RAW LOG DUMP END ---")

except Exception as e:
    print(f"Error reading log: {e}")
