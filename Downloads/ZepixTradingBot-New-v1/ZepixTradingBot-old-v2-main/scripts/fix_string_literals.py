#!/usr/bin/env python3
"""Fix all unterminated string literals in command_executor.py"""

import re

filepath = 'src/menu/command_executor.py'

# Read file
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic section - the handlers we added
# These have newlines embedded in strings which breaks Python syntax

# Fix pattern: text += "...
# Should be: text += "...\\n"

# Replace all instances of newline inside double-quoted strings
# Pattern: text += "anything
# Replace with: text += "anything\n"

fixes = [
    (r'text \+= "([^"]*)\n"', r'text += "\1\\n"'),
    (r"text \+= '([^']*)\\n'", r"text += '\1\\n'"),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content)

# Also fix the specific f-string issues
content = content.replace('text += "🔄 *Backup Files:*\n"', 'text += "🔄 *Backup Files:*\\n"')
content = content.replace('text += f"• {filename}: {backup_size:.2f} MB\n"', 'text += f"• {filename}: {backup_size:.2f} MB\\n"')
content = content.replace('text += f"\n📦 *Total Size:* {total_size_mb:.2f} MB\n\n"', 'text += f"\\n📦 *Total Size:* {total_size_mb:.2f} MB\\n\\n"')
content = content.replace('text += f"📦 *Total Size:* {total_size_mb:.2f} MB\n\n"', 'text += f"📦 *Total Size:* {total_size_mb:.2f} MB\\n\\n"')
content = content.replace('text += "\n💡 Use /export_logs to download recent logs"', 'text += "\\n💡 Use /export_logs to download recent logs"')
content = content.replace('self.bot.send_message(f"❌ Invalid mode: {mode}\\nUse: on, off, or status")', 'self.bot.send_message(f"❌ Invalid mode: {mode}\\\\nUse: on, off, or status")')

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed string literals in command_executor.py')

# Verify syntax
import subprocess
result = subprocess.run(['python', '-m', 'py_compile', filepath], capture_output=True, text=True)
if result.returncode == 0:
    print('✅ Syntax check passed!')
else:
    print(f'❌ Syntax errors still exist:')
    print(result.stderr)
