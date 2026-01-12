# Add 2 missing diagnostic handlers to command_executor.py
filepath = 'src/menu/command_executor.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where to insert - after _execute_set_log_level method ends
insert_line = None
for i, line in enumerate(lines):
    if 'def _execute_set_log_level' in line:
        # Find end of this method (next def or end of class)
        for j in range(i+1, len(lines)):
            if lines[j].strip().startswith('def ') and not lines[j].strip().startswith('def _'):
                insert_line = j
                break
            elif lines[j].strip().startswith('def _execute_'):
                insert_line = j
                break
        break

if not insert_line:
    print('❌ Could not find insertion point')
    exit(1)

# Prepare the 2 missing handlers
handlers_code = '''
    def _execute_get_log_level(self, params: Dict[str, Any]):
        """Show current log level with descriptions"""
        try:
            from src.utils.logging_config import logging_config
            
            current = logging_config.current_level.name
            
            text = (
                "📊 *CURRENT LOG LEVEL*\\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
                f"🎯 *Active Level:* `{current}`\\n\\n"
            )
            
            # Description based on current level
            if current == "DEBUG":
                text += (
                    "🔍 *DEBUG MODE*\\n"
                    "• Maximum verbosity\\n"
                    "• All details logged\\n"
                    "• Slower performance\\n"
                    "• Large log files\\n"
                )
            elif current == "INFO":
                text += (
                    "ℹ️ *INFO MODE (Recommended)*\\n"
                    "• Important events only\\n"
                    "• Balanced detail\\n"
                    "• Optimal for production\\n"
                    "• Moderate log size\\n"
                )
            elif current == "WARNING":
                text += (
                    "⚠️ *WARNING MODE*\\n"
                    "• Warnings & errors only\\n"
                    "• Minimal output\\n"
                    "• May miss info events\\n"
                )
            elif current == "ERROR":
                text += (
                    "❌ *ERROR MODE*\\n"
                    "• Errors only\\n"
                    "• Very quiet\\n"
                )
            else:  # CRITICAL
                text += (
                    "🚨 *CRITICAL MODE*\\n"
                    "• Critical failures only\\n"
                    "• Almost silent\\n"
                )
            
            text += "\\n\\n📋 *Available Levels:*\\n"
            levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            for lvl in levels:
                emoji = "✅" if lvl == current else "  "
                text += f"{emoji} {lvl}\\n"
            
            text += "\\n💡 Use /set_log_level to change"
            
            self.bot.send_message(text)
            logger.info(f"Displayed current log level: {current}")
            return True
            
        except Exception as e:
            logger.error(f"Get log level error: {e}")
            self.bot.send_message(f"❌ Error checking log level: {str(e)}")
            return False
    
    def _execute_reset_log_level(self, params: Dict[str, Any]):
        """Reset log level to default INFO"""
        try:
            from src.utils.logging_config import logging_config, LogLevel
            import logging as std_logging
            
            old_level = logging_config.current_level.name
            
            # Reset to INFO
            logging_config.set_level(LogLevel.INFO)
            std_logging.getLogger().setLevel(std_logging.INFO)
            
            # Save to config
            self._save_log_level_to_config("INFO")
            
            # Verify
            new_level = logging_config.current_level.name
            verified = (new_level == "INFO")
            
            text = (
                "✅ *Log Level Reset to Default*\\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
                f"• Previous: `{old_level}`\\n"
                f"• Reset to: `INFO` (default)\\n"
                f"• Verified: {'✅ YES' if verified else '❌ NO'}\\n\\n"
                "ℹ️ *INFO Level Features:*\\n"
                "• Important events logged\\n"
                "• Trading actions recorded\\n"
                "• Optimal for production\\n"
                "• Balanced performance\\n\\n"
                "💡 This setting persists across restarts"
            )
            
            self.bot.send_message(text)
            logger.info(f"Reset log level from {old_level} to INFO")
            return True
            
        except Exception as e:
            logger.error(f"Reset log level error: {e}")
            self.bot.send_message(f"❌ Error resetting log level: {str(e)}")
            return False

'''

# Insert handlers
lines.insert(insert_line, handlers_code)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'✅ Added 2 missing handlers at line {insert_line}')
print('   - _execute_get_log_level')
print('   - _execute_reset_log_level')
