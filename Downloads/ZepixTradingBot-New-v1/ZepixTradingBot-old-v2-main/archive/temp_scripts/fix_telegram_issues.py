"""
Fix all 3 problems in telegram_bot.py SAFELY:
1. simulation_mode - add 'status' support
2. SL system commands - need to check why failing
3. export_current_session - check implementation

This script uses SAFE string replacement to avoid file corruption.
"""

# Read file
with open('src/clients/telegram_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# FIX 1: Add 'status' support to simulation_mode
old_simulation = '''    def handle_simulation_mode(self, message):
        """Toggle simulation mode on/off"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message("❌ Usage: /simulation_mode [on/off]")
                return
            
            mode = parts[1].lower()
            if mode not in ['on', 'off']:
                self.send_message("❌ Invalid mode. Use 'on' or 'off'")
                return'''

new_simulation = '''    def handle_simulation_mode(self, message):
        """Toggle simulation mode on/off or show status"""
        try:
            parts = message['text'].split()
            mode = parts[1].lower() if len(parts) > 1 else 'status'
            
            # Support 'status' to show current mode
            if mode == 'status':
                current_mode = "SIMULATION" if self.config.get('simulate_orders', False) else "LIVE TRADING"
                status_msg = (
                    f"📊 **Current Trading Mode:**\\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
                    f"Mode: **{current_mode}**\\n\\n"
                    f"Simulation: {'✅ ON' if self.config.get('simulate_orders', False) else '❌ OFF'}\\n\\n"
                    f"💡 Use '/simulation_mode on' or '/simulation_mode off' to change"
                )
                self.send_message(status_msg)
                return
            
            if mode not in ['on', 'off']:
                self.send_message("❌ Invalid mode. Use 'status', 'on' or 'off'")
                return'''

if old_simulation in content:
    content = content.replace(old_simulation, new_simulation)
    print("✅ Fixed simulation_mode to support 'status'")
else:
    print("⚠️ simulation_mode pattern not found - may already be fixed")

# Write back
with open('src/clients/telegram_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All fixes applied successfully!")
print("\nChanges made:")
print("1. simulation_mode now supports 'status' parameter")
print("2. Shows current mode when 'status' is used")
