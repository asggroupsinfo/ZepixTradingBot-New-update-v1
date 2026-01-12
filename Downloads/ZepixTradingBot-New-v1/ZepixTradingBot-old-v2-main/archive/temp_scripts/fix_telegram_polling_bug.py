#!/usr/bin/env python3
"""
Fix the critical polling bug in telegram_bot.py
This script fixes lines 3102-3120 where updates processing code was unreachable
"""

def fix_telegram_bot():
    file_path = 'src/clients/telegram_bot.py'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # The bug is at lines 3102-3120 (0-indexed: 3101-3119)
    # We need to replace this section with properly indented code
    
    # Find the exact line with "if response.status_code == 200:"
    start_idx = None
    for i, line in enumerate(lines):
        if i >= 3100 and 'if response.status_code == 200:' in line:
            start_idx = i
            break
    
    if start_idx is None:
        print("❌ Could not find the buggy code section")
        return False
    
    # New correct code block
    new_lines = [
        '                    # Handle non-200 responses first\n',
        '                    if response.status_code == 409:\n',
        '                        # Conflict - another bot instance is polling\n',
        '                        print(f"[POLLING] Got HTTP 409 - another instance may be polling. Waiting...")\n',
        '                        time.sleep(30)\n',
        '                        continue\n',
        '                    elif response.status_code != 200:\n',
        '                        print(f"[POLLING] Unexpected status code: {response.status_code}")\n',
        '                        time.sleep(10)\n',
        '                        continue\n',
        '                    \n',
        '                    # Process 200 response\n',
        '                    data = response.json()\n',
        '                    if not data.get("ok"):\n',
        '                        print(f"Telegram API error: {data}")\n',
        '                        time.sleep(10)\n',
        '                        continue\n',
        '                    \n',
        '                    # Get updates and process them\n',
        '                    updates = data.get("result", [])\n',
        '                    \n',
        '                    for update in updates:\n',
    ]
    
    # Find where the buggy block ends (at "for update in updates:")
    end_idx = None
    for i in range(start_idx, min(start_idx + 30, len(lines))):
        if 'for update in updates:' in lines[i]:
            end_idx = i + 1  # Include the line with 'for update in updates:'
            break
    
    if end_idx is None:
        print("❌ Could not find end of buggy code section")
        return False
    
    # Replace the buggy section with fixed code
    fixed_lines = lines[:start_idx] + new_lines + lines[end_idx:]
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Successfully fixed polling bug!")
    print(f"   Replaced lines {start_idx+1} to {end_idx} ({end_idx - start_idx} lines)")
    print(f"   with {len(new_lines)} new lines")
    return True

if __name__ == "__main__":
    success = fix_telegram_bot()
    exit(0 if success else 1)
