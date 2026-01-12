import re

# Read log file
with open('logs-24-11-25 details.md', 'r', encoding='utf-8') as f:
    log = f.read()

# Find all EXECUTION SUCCESS
successes = re.findall(r'✅ EXECUTION SUCCESS: (\w+)', log)
print(f"Commands Successfully Executed: {len(set(successes))}")
for cmd in sorted(set(successes)):
    count = successes.count(cmd)
    print(f"  {cmd}: {count} times")

# Find Unknown logic errors  
unknown = log.count('Unknown logic')
print(f"\n'Unknown logic' errors: {unknown}")

# Find set_trend and set_auto
set_trend_matches = len(re.findall(r'set_trend', log))
set_auto_matches = len(re.findall(r'set_auto', log))
print(f"\nset_trend mentions: {set_trend_matches}")
print(f"set_auto mentions: {set_auto_matches}")
