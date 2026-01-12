# Telegram Bot Dashboard Test
# Test all commands and verify button responses

import requests
import json
import time

TOKEN = "8526101969:AAF9fqQlPbNUkb1fg3vylwG4uDNiz-Z9IY4"
CHAT_ID = 2139792302
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_command(command):
    """Send command to bot"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": command
    }
    response = requests.post(url, json=payload)
    print(f"✅ Sent: {command} - Status: {response.status_code}")
    return response

def get_latest_messages(limit=5):
    """Get latest messages from bot"""
    url = f"{BASE_URL}/getUpdates"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            results = data['result'][-limit:]
            return results
    return []

def check_for_buttons():
    """Check if bot sent messages with buttons"""
    updates = get_latest_messages(10)
    found_buttons = False
    
    for update in updates:
        if 'message' in update:
            msg = update['message']
            if msg.get('from', {}).get('is_bot', False):
                # This is from bot
                if 'reply_markup' in msg:
                    print(f"\n🎯 FOUND BUTTONS in message:")
                    print(f"   Text: {msg.get('text', '')[:100]}")
                    print(f"   Buttons: {json.dumps(msg['reply_markup'], indent=2)}")
                    found_buttons = True
                else:
                    print(f"\n⚠️ Bot message WITHOUT buttons:")
                    print(f"   Text: {msg.get('text', '')[:100]}")
    
    return found_buttons

# Test commands
print("\n" + "="*60)
print("🤖 TELEGRAM BOT COMMAND TEST")
print("="*60)

commands_to_test = [
    "/start",
    "/dashboard",
    "/fine_tune",
    "/profit_protection",
    "/autonomous_dashboard"
]

for cmd in commands_to_test:
    print(f"\n📤 Testing: {cmd}")
    send_command(cmd)
    time.sleep(2)  # Wait for bot to respond
    
print("\n\n" + "="*60)
print("🔍 CHECKING FOR BUTTON RESPONSES")
print("="*60)

time.sleep(3)  # Final wait
found = check_for_buttons()

if found:
    print("\n✅ SUCCESS: Bot is sending buttons!")
else:
    print("\n❌ ISSUE: Bot NOT sending buttons - only echo messages")
    print("\n🔧 DIAGNOSIS:")
    print("   1. Commands are being sent ✅")
    print("   2. Bot is NOT responding with buttons ❌")
    print("   3. Need to check bot's polling/handler logic")

print("\n" + "="*60)
