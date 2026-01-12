#!/usr/bin/env python3
"""Add send_document method to telegram_bot.py"""

import os

filepath = 'src/clients/telegram_bot.py'

# Read file
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already exists
if 'def send_document' in content:
    print('✅ send_document method already exists!')
    exit(0)

# send_document method code
send_doc_method = '''
    def send_document(self, file_path: str, caption: str = ""):
        """Send a document file via Telegram"""
        try:
            if not self.token or not self.chat_id:
                print("WARNING: Telegram credentials not configured - cannot send document")
                return False
            
            url = f"{self.base_url}/sendDocument"
            
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption
                }
                response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"[SEND_DOCUMENT] File sent successfully: {file_path}")
                return True
            else:
                print(f"[SEND_DOCUMENT] Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[SEND_DOCUMENT] Error: {e}")
            import traceback
            traceback.print_exc()
            return False
'''

# Find position after send_message_with_keyboard
pos = content.find('def send_message_with_keyboard')
next_def = content.find('\n    def ', pos + 100)

if next_def != -1:
    # Insert send_document method
    content = content[:next_def] + send_doc_method + '\n' + content[next_def:]
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ send_document method added successfully!')
else:
    print('❌ Could not find insertion point')
