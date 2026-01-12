#!/usr/bin/env python3
"""Fix indentation error in logging_config.py"""

import os

filepath = 'src/utils/logging_config.py'

# Read file
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the indentation issue around line 96
fixed_lines = []
for i, line in enumerate(lines, 1):
    # Line 94-97 area - trading_debug section needs to be indented properly
    if 'trading_debug = settings.get("trading_debug"' in line:
        # Ensure this block is indented at same level as previous if block
        if not line.startswith('                        '):
            # Fix indentation to match the if level_name block above
            fixed_lines.append('                        # Load trading_debug setting\n')
            fixed_lines.append('                        trading_debug = settings.get("trading_debug", False)\n')
            fixed_lines.append('                        self.trading_debug = trading_debug\n')
            fixed_lines.append('                        print(f"[LOGGING CONFIG] Loaded trading_debug: {trading_debug}")\n')
            # Skip next 3 lines as we just added them
            continue
    elif 'self.trading_debug = trading_debug' in line or 'print(f"[LOGGING CONFIG] Loaded trading_debug:' in line:
        # Skip these as they were already added above
        continue
    elif '# Load trading_debug setting' in line and i > 90:
        # Skip duplicate comment
        continue
    else:
        fixed_lines.append(line)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('✅ Fixed indentation in logging_config.py')
