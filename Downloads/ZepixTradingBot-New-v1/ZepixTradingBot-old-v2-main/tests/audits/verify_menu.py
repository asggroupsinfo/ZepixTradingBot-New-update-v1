from src.menu.menu_constants import REPLY_MENU_MAP
import sys

print("VERIFYING MENU KEYS...")
keys = list(REPLY_MENU_MAP.keys())
print(f"Count: {len(keys)}")
print("Keys:", keys)

if "💰 Performance" in keys:
    print("❌ FAILURE: Performance button still present!")
    sys.exit(1)
elif len(keys) != 10:
    print(f"❌ FAILURE: Expected 10 keys, found {len(keys)}")
    sys.exit(1)
else:
    print("✅ SUCCESS: Menu keys verified (10 items, no Performance)")
