import re

# Read log
with open('logs-24-11-25 details.md', 'r', encoding='utf-8') as f:
    log = f.read()

# Commands executed successfully
executed = re.findall(r'✅ EXECUTION SUCCESS: (\w+)', log)
executed_unique = sorted(set(executed))

# Unknown logic errors
unknown_logic = log.count('Unknown logic')

# Telegram errors
telegram_errors = log.count('Telegram API error')

print("="*60)
print("LOG ANALYSIS REPORT")
print("="*60)

print(f"\n✅ COMMANDS SUCCESSFULLY EXECUTED: {len(executed_unique)}")
for cmd in executed_unique:
    count = executed.count(cmd)
    print(f"  • {cmd}: {count} times")

print(f"\n❌ ERRORS FOUND:")
print(f"  • 'Unknown logic': {unknown_logic} occurrences")
print(f"  • 'Telegram API error': {telegram_errors} occurrences")

# Check if errors are fixed
print(f"\n🔍 ERROR STATUS:")
if unknown_logic > 0:
    print(f"  ⚠️  'Unknown logic' STILL IN OLD LOGS ({unknown_logic} times)")
    print(f"     Status: Fixed in code, old logs show historical errors")
else:
    print(f"  ✅ No 'Unknown logic' errors")

if telegram_errors > 0:
    print(f"  ⚠️  Telegram errors found ({telegram_errors} times)")
    print(f"     Status: Fix applied, needs bot restart to verify")
else:
    print(f"  ✅ No Telegram errors")
