#!/usr/bin/env python3
"""
Fix the Telegram polling bug in telegram_bot.py
"""

# Read the file
with open('src/clients/telegram_bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the bug at line 3102-3120
# The issue is that after line 3107's continue, there's nested code that is unreachable
# We need to restructure the logic

fixed_lines = []
i = 0
while i < len(lines):
    # Check if we're at the bug location (around line 3102)
    if i >= 3101 and i < 3102:  # Line 3102 (0-indexed: 3101)
        # Replace lines 3102-3120 with fixed version
        if lines[i].strip().startswith('if response.status_code == 200:'):
            fixed_lines.append('                    # Handle non-200 responses first\n')
            fixed_lines.append('                    if response.status_code == 409:\n')
            fixed_lines.append('                        # Conflict - another bot instance is polling\n')
            fixed_lines.append('                        print(f"[POLLING] Got HTTP 409 - another instance may be polling. Waiting...")\n')
            fixed_lines.append('                    time.sleep(30)\n')
            fixed_lines.append('                        continue\n')
            fixed_lines.append('                    elif response.status_code != 200:\n')
            fixed_lines.append('                        print(f"[POLLING] Unexpected status code: {response.status_code}")\n')
            fixed_lines.append('                        time.sleep(10)\n')
            fixed_lines.append('                        continue\n')
            fixed_lines.append('                    \n')
            fixed_lines.append('                    # Process 200 response\n')
            fixed_lines.append('                    data = response.json()\n')
            fixed_lines.append('                    if not data.get("ok"):\n')
            fixed_lines.append('                        print(f"Telegram API error: {data}")\n')
            fixed_lines.append('                        time.sleep(10)\n')
            fixed_lines.append('                        continue\n')
            fixed_lines.append('                    \n')
            fixed_lines.append('                    # Get updates and process them\n')
            fixed_lines.append('                    updates = data.get("result", [])\n')
            fixed_lines.append('                    \n')
            fixed_lines.append('                    for update in updates:\n')
            
            # Skip the old buggy lines (3102-3120, which is indices 3101-3119)
            i = 3119  # Jump to line after 'for update in updates:'
            continue
    
    fixed_lines.append(lines[i])
    i += 1

# Write back
with open('src/clients/telegram_bot.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Fixed polling bug in telegram_bot.py")
