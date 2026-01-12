import re

with open('src/clients/telegram_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all command handlers
handlers = list(set(re.findall(r'\"/([\w_]+)\":', content)))

print(f"TOTAL TELEGRAM COMMANDS: {len(handlers)}")
print("\nAll Commands:")
for cmd in sorted(handlers):
    print(f"  /{cmd}")
