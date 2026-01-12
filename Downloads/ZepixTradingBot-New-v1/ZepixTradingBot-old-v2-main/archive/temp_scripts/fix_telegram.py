import sys
import os

# Add path
sys.path.insert(0, 'c:/Users/Ansh Shivaay Gupta/Downloads/ZepixTradingBot-old-v2-main/ZepixTradingBot-old-v2-main')

# Read telegram_bot.py
with open('src/clients/telegram_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace send_message method SAFELY
old_code = '''            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"WARNING: Telegram API error: Status {response.status_code}, Response: {response.text}")
                return False'''

new_code = '''            response = requests.post(url, json=payload, timeout=10)
            
            # If HTML parsing fails, retry with plain text
            if response.status_code == 400 and "parse entities" in response.text.lower():
                payload["parse_mode"] = None
                response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"WARNING: Telegram API error: Status {response.status_code}, Response: {response.text}")
                return False'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('src/clients/telegram_bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Telegram formatting fix applied successfully!")
else:
    print("❌ Code pattern not found - fix already applied or code changed")
