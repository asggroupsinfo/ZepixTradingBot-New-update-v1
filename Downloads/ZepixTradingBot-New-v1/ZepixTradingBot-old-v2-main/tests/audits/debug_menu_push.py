import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"DEBUG: Token loaded? {'Yes' if BOT_TOKEN else 'No'}")
print(f"DEBUG: Chat ID loaded? {CHAT_ID}")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ ERROR: Missing Credentials in .env")
    exit(1)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Exact payload structure from MenuManager
# Note: "is_persistent" is a valid field since Bot API 6.0
keyboard_payload = {
    "keyboard": [
        [{"text": "📊 Dashboard"}, {"text": "⏸️ Pause/Resume"}],
        [{"text": "📈 Active Trades"}, {"text": "💰 Performance"}],
        [{"text": "🛡️ Risk"}, {"text": "🔄 Re-entry"}],
        [{"text": "⚙️ SL System"}, {"text": "📈 Profit"}],
        [{"text": "📍 Trends"}, {"text": "⏱️ Timeframe"}],
        [{"text": "🔍 Diagnostics"}, {"text": "⚡ Fine-Tune"}],
        [{"text": "🆘 Help"}, {"text": "🚨 PANIC CLOSE"}]
    ],
    "resize_keyboard": True,
    "is_persistent": True,
    "one_time_keyboard": False,
    "input_field_placeholder": "Use buttons below ⬇️"
}

payload = {
    "chat_id": CHAT_ID,
    "text": "👇 **DEBUG TEST: Force Keyboard Push**\nIf you see this, the API is accepting the JSON.",
    "parse_mode": "Markdown",
    "reply_markup": json.dumps(keyboard_payload)  # CRITICAL: JSON DUMP AS STRING
}

print("Sending request...")
try:
    response = requests.post(url, data=payload, timeout=10)
    
    print("\n" + "="*40)
    print(f"STATUS CODE: {response.status_code}")
    print("="*40)
    print("RESPONSE BODY:")
    print(json.dumps(response.json(), indent=2))
    print("="*40)
    
    if response.status_code == 200 and response.json().get("ok"):
        print("\n✅ SUCCESS: Telegram accepted the keyboard payload.")
    else:
        print("\n❌ FAILURE: Telegram rejected the payload.")

except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
