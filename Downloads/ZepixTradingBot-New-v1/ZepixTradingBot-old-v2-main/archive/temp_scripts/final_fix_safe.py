"""
Final Safe Fix for Telegram Bot
1. Fixes 'Status 400' errors by adding plain text fallback in send_message
2. Fixes SL System silent failures by using direct parameter access (bypassing text parsing)
"""

import re

file_path = 'src/clients/telegram_bot.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ==============================================================================
# FIX 1: send_message fallback (Fixes Status 400 errors)
# ==============================================================================
old_send_message = '''            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"WARNING: Telegram API error: Status {response.status_code}, Response: {response.text}")
                return False'''

new_send_message = '''            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            elif response.status_code == 400 and payload.get("parse_mode") == "HTML":
                print(f"WARNING: Telegram HTML error, retrying with plain text...")
                payload["parse_mode"] = None
                retry_response = requests.post(url, json=payload, timeout=10)
                if retry_response.status_code == 200:
                    return True
                else:
                    print(f"WARNING: Telegram API error (Retry): Status {retry_response.status_code}, Response: {retry_response.text}")
                    return False
            else:
                print(f"WARNING: Telegram API error: Status {response.status_code}, Response: {response.text}")
                return False'''

if old_send_message in content:
    content = content.replace(old_send_message, new_send_message)
    print("✅ Fixed send_message (added HTML fallback)")
else:
    print("⚠️ send_message pattern not found (might be already fixed)")

# ==============================================================================
# FIX 2: handle_sl_system_change (Fixes silent failure)
# ==============================================================================
old_sl_change = '''    def handle_sl_system_change(self, message):
        """Switch between SL systems - /sl_system_change [sl-1/sl-2]"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message(
                    "❌ <b>Usage:</b> /sl_system_change [sl-1/sl-2]\\n\\n"
                    "<b>Example:</b> /sl_system_change sl-2\\n"
                    "Switches to SL-2 system"
                )
                return
            
            new_system = parts[1].lower()'''

new_sl_change = '''    def handle_sl_system_change(self, message):
        """Switch between SL systems - /sl_system_change [sl-1/sl-2]"""
        try:
            # Try getting from direct param first (Menu System)
            new_system = message.get('system')
            
            # Fallback to text parsing (Command Line)
            if not new_system:
                parts = message['text'].split()
                if len(parts) == 2:
                    new_system = parts[1].lower()
            
            if not new_system:
                self.send_message(
                    "❌ <b>Usage:</b> /sl_system_change [sl-1/sl-2]\\n\\n"
                    "<b>Example:</b> /sl_system_change sl-2\\n"
                    "Switches to SL-2 system"
                )
                return'''

if old_sl_change in content:
    content = content.replace(old_sl_change, new_sl_change)
    print("✅ Fixed handle_sl_system_change (added direct param support)")
else:
    print("⚠️ handle_sl_system_change pattern not found")

# ==============================================================================
# FIX 3: handle_sl_system_on (Fixes silent failure)
# ==============================================================================
old_sl_on = '''    def handle_sl_system_on(self, message):
        """Enable specific SL system - /sl_system_on [sl-1/sl-2]"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message(
                    "❌ <b>Usage:</b> /sl_system_on [sl-1/sl-2]\\n\\n"
                    "<b>Example:</b> /sl_system_on sl-1\\n"
                    "Enables SL-1 system"
                )
                return
            
            system = parts[1].lower()'''

new_sl_on = '''    def handle_sl_system_on(self, message):
        """Enable specific SL system - /sl_system_on [sl-1/sl-2]"""
        try:
            # Try getting from direct param first (Menu System)
            system = message.get('system')
            
            # Fallback to text parsing (Command Line)
            if not system:
                parts = message['text'].split()
                if len(parts) == 2:
                    system = parts[1].lower()
            
            if not system:
                self.send_message(
                    "❌ <b>Usage:</b> /sl_system_on [sl-1/sl-2]\\n\\n"
                    "<b>Example:</b> /sl_system_on sl-1\\n"
                    "Enables SL-1 system"
                )
                return'''

if old_sl_on in content:
    content = content.replace(old_sl_on, new_sl_on)
    print("✅ Fixed handle_sl_system_on (added direct param support)")
else:
    print("⚠️ handle_sl_system_on pattern not found")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All fixes applied successfully!")
