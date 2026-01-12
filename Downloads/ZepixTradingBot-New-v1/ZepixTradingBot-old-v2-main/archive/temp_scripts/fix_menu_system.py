"""
Fix simulation_mode in command_executor.py to support 'status' mode
This fixes the MENU SYSTEM (buttons), not direct commands.
"""

# Read command_executor.py
with open('src/menu/command_executor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix _execute_simulation_mode
old_code = '''    def _execute_simulation_mode(self, params: Dict[str, Any]):
        """Execute simulation mode toggle"""
        mode = params.get("mode", "toggle")
        msg = self._create_message_dict("simulation_mode", {"mode": mode})
        self.bot.handle_simulation_mode(msg)'''

new_code = '''    def _execute_simulation_mode(self, params: Dict[str, Any]):
        """Execute simulation mode toggle or show status"""
        mode = params.get("mode", "status")  # Default to status instead of toggle
        msg = self._create_message_dict("simulation_mode", {"mode": mode})
        self.bot.handle_simulation_mode(msg)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ Fixed command_executor.py - simulation_mode defaults to 'status'")
else:
    print("⚠️ Pattern not found in command_executor.py")

# Write back
with open('src/menu/command_executor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Menu system fix applied!")
print("Now when you click simulation_mode button without selecting mode,")
print("it will show STATUS instead of error")
