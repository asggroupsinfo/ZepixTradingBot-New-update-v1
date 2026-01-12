import re
import os

# Count from telegram_bot.py
telegram_file = 'src/clients/telegram_bot.py'
with open(telegram_file, 'r', encoding='utf-8') as f:
    telegram_content = f.read()

# Find command handlers in command_handlers dict
cmd_handlers = list(set(re.findall(r'\"/([\w_]+)\":', telegram_content)))
print(f"Commands in telegram_bot.py command_handlers: {len(cmd_handlers)}")

# Find all menu files
menu_commands = set()
for root, dirs, files in os.walk('src/menu'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find execute methods
                executes = re.findall(r'def _execute_([\w_]+)', content)
                menu_commands.update(executes)
                # Find command definitions
                cmd_defs = re.findall(r'\"([\w_]+)\":\s*{', content)
                menu_commands.update(cmd_defs)

print(f"\nMenu system commands: {len(menu_commands)}")
print(f"Total unique: {len(set(cmd_handlers) | menu_commands)}")

# List all
all_commands = sorted(set(cmd_handlers) | menu_commands)
print(f"\nALL {len(all_commands)} COMMANDS:")
for i, cmd in enumerate(all_commands, 1):
    print(f"{i}. {cmd}")
