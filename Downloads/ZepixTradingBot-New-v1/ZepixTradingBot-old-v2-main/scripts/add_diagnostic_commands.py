#!/usr/bin/env python3
"""
Automated script to add 5 new diagnostic commands to ZepixTradingBot
This script updates all necessary files without manual copy-paste
"""

import os
import re

def update_requirements():
    """Add psutil to requirements.txt"""
    print("📦 Updating requirements.txt...")
    req_file = "requirements.txt"
    
    with open(req_file, 'r') as f:
        content = f.read()
    
    if 'psutil' not in content:
        with open(req_file, 'a') as f:
            f.write('\npsutil==5.9.6\n')
        print("  ✅ Added psutil==5.9.6")
    else:
        print("  ℹ️  psutil already in requirements.txt")

def update_command_mapping():
    """Add 5 new commands to command_mapping.py"""
    print("\n📝 Updating command_mapping.py...")
    file_path = "src/menu/command_mapping.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the diagnostics section
    new_commands = '''    "export_logs": {"params": ["lines"], "type": "single", "options": ["100", "500", "1000"], "handler": "_execute_export_logs"},
    "log_file_size": {"params": [], "type": "direct", "handler": "_execute_log_file_size"},
    "clear_old_logs": {"params": [], "type": "direct", "handler": "_execute_clear_old_logs"},
    "trading_debug_mode": {"params": ["mode"], "type": "single", "options": ["on", "off", "status"], "handler": "_execute_trading_debug_mode"},
    "system_resources": {"params": [], "type": "direct", "handler": "_execute_system_resources"},
'''
    
    # Insert after reset_health
    if 'export_logs' not in content:
        content = content.replace(
            '"reset_health": {"params": [], "type": "direct", "handler": "_execute_reset_health"},',
            '"reset_health": {"params": [], "type": "direct", "handler": "_execute_reset_health"},\n    ' + new_commands.strip() + ','
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Added 5 new command definitions")
    else:
        print("  ℹ️  Commands already in command_mapping.py")

def update_menu_constants():
    """Add 5 new commands to menu buttons"""
    print("\n🔘 Updating menu_constants.py...")
    file_path = "src/menu/menu_constants.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find diagnostics section and add new commands
    if 'export_logs' not in content:
        # Replace the entire diagnostics command list
        pattern = r'("diagnostics":\s*\{[^}]*"commands":\s*\[)([^\]]*?)(\])'
        
        def add_commands(match):
            prefix = match.group(1)
            existing = match.group(2)
            suffix = match.group(3)
            
            # Add new commands if not already present
            new_cmds = [
                '"export_logs"',
                '"log_file_size"',
                '"clear_old_logs"',
                '"trading_debug_mode"',
                '"system_resources"'
            ]
            
            for cmd in new_cmds:
                if cmd not in existing:
                    existing += ',\n            ' + cmd
            
            return prefix + existing + suffix
        
        content = re.sub(pattern, add_commands, content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Added 5 new menu buttons")
    else:
        print("  ℹ️  Menu buttons already in menu_constants.py")

def update_menu_manager():
    """Add parameter type support"""
    print("\n⚙️  Updating menu_manager.py...")
    file_path = "src/menu/menu_manager.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if 'lines' parameter already exists
    if 'elif param_type == "lines"' not in content:
        # Find the level parameter section and add after it
        lines_param = '''
        elif param_type == "lines":
            # Log export line count options
            options = ["100", "500", "1000"]
            keyboard = [
                [{"text": f"📄 {opt} lines", "callback_data": f"param_{param_name}_{opt}"}]
                for opt in options
            ]
        
        elif param_type == "mode":
            # Trading debug mode options
            options = ["on", "off", "status"]
            emoji_map = {"on": "✅", "off": "❌", "status": "📊"}
            keyboard = [
                [{"text": f"{emoji_map[opt]} {opt.upper()}", "callback_data": f"param_{param_name}_{opt}"}]
                for opt in options
            ]'''
        
        # Insert before the final else
        content = content.replace(
            '        else:\n            return None',
            lines_param + '\n        \n        else:\n            return None'
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Added 'lines' and 'mode' parameter types")
    else:
        print("  ℹ️  Parameter types already in menu_manager.py")

def update_command_executor_handlers():
    """Add 5 new command handlers"""
    print("\n🔧 Updating command_executor.py (handlers)...")
    file_path = "src/menu/command_executor.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '_execute_export_logs' in content:
        print("  ℹ️  Handlers already in command_executor.py")
        return
    
    handlers_code = '''
    def _execute_export_logs(self, params: Dict[str, Any]):
        """Export last N lines of log file"""
        try:
            import os
            import gzip
            from datetime import datetime
            
            lines = int(params.get("lines", 100))
            log_file = "logs/bot_activity.log"
            
            if not os.path.exists(log_file):
                self.bot.send_message("❌ Log file not found!")
                return False
            
            # Create export directory
            export_dir = "logs/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Read last N lines
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                export_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Create export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"bot_logs_{timestamp}_{lines}lines.txt"
            export_path = os.path.join(export_dir, export_filename)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.writelines(export_lines)
            
            file_size_kb = os.path.getsize(export_path) / 1024
            
            # Compress if > 1MB
            if file_size_kb > 1024:
                gz_path = export_path + ".gz"
                with open(export_path, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(export_path)
                export_path = gz_path
                export_filename = export_filename + ".gz"
                file_size_kb = os.path.getsize(export_path) / 1024
            
            text = f"""✅ *Logs Exported Successfully*
━━━━━━━━━━━━━━━━━━━━━━━━

📄 *File:* `{export_filename}`
📊 *Lines Exported:* {len(export_lines)}
💾 *File Size:* {file_size_kb:.2f} KB
📁 *Location:* `{export_path}`

💡 File ready for download!"""
            
            self.bot.send_message(text)
            
            # Try to send file via Telegram
            try:
                if hasattr(self.bot, 'send_document'):
                    self.bot.send_document(export_path, caption=f"Bot logs export - {lines} lines")
                    logger.info(f"Logs exported and sent to Telegram: {export_filename}")
                else:
                    logger.warning("send_document method not available in telegram_bot")
            except Exception as e:
                logger.warning(f"Could not send file via Telegram: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Export logs error: {e}")
            self.bot.send_message(f"❌ Error exporting logs: {str(e)}")
            return False
    
    def _execute_log_file_size(self, params: Dict[str, Any]):
        """Show log file statistics"""
        try:
            import os
            from datetime import datetime
            
            log_file = "logs/bot_activity.log"
            
            if not os.path.exists(log_file):
                self.bot.send_message("❌ Log file not found!")
                return False
            
            # Main log file stats
            size_bytes = os.path.getsize(log_file)
            size_mb = size_bytes / (1024 * 1024)
            modified_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            
            # Count lines
            with open(log_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            # Check for backup files
            backup_files = []
            log_dir = os.path.dirname(log_file) or "logs"
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    if filename.startswith("bot_activity") and (filename.endswith(".log.1") or filename.endswith(".log.2") or filename.endswith(".log.3") or ".old" in filename):
                        backup_path = os.path.join(log_dir, filename)
                        backup_size = os.path.getsize(backup_path) / (1024 * 1024)
                        backup_files.append((filename, backup_size))
            
            total_size_mb = size_mb + sum(size for _, size in backup_files)
            
            text = f"""📊 *LOG FILE STATISTICS*
━━━━━━━━━━━━━━━━━━━━━━━━

📄 *Main Log File:*
• Size: {size_mb:.2f} MB ({size_bytes:,} bytes)
• Lines: {line_count:,}
• Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}
• Max Size: 10 MB
• Usage: {(size_mb/10)*100:.1f}%

"""
            
            if backup_files:
                text += "🔄 *Backup Files:*\n"
                for filename, backup_size in backup_files:
                    text += f"• {filename}: {backup_size:.2f} MB\n"
                text += f"\n📦 *Total Size:* {total_size_mb:.2f} MB\n\n"
            else:
                text += f"📦 *Total Size:* {total_size_mb:.2f} MB\n\n"
            
            # Rotation status
            if size_mb > 9:
                text += "⚠️ *Warning:* Log file near rotation limit!\n"
            else:
                text += "✅ *Status:* Healthy\n"
            
            text += "\n💡 Use /export_logs to download recent logs"
            
            self.bot.send_message(text)
            return True
            
        except Exception as e:
            logger.error(f"Log file size error: {e}")
            self.bot.send_message(f"❌ Error checking log size: {str(e)}")
            return False
    
    def _execute_clear_old_logs(self, params: Dict[str, Any]):
        """Clear old backup log files (admin only)"""
        try:
            import os
            from datetime import datetime, timedelta
            
            # SAFETY CHECK: Admin only
            user_id = params.get("user_id", 0)
            if not self._is_admin(user_id):
                self.bot.send_message("❌ Only admins can clear logs!")
                return False
            
            log_dir = "logs"
            retention_days = 30
            keep_min_backups = 2
            
            # Find backup files
            backup_files = []
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    if filename.startswith("bot_activity") and (filename.endswith(".log.1") or filename.endswith(".log.2") or filename.endswith(".log.3") or ".old" in filename):
                        filepath = os.path.join(log_dir, filename)
                        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        age_days = (datetime.now() - modified_time).days
                        size_mb = os.path.getsize(filepath) / (1024 * 1024)
                        backup_files.append((filename, filepath, age_days, size_mb))
            
            # Sort by age (oldest first)
            backup_files.sort(key=lambda x: x[2], reverse=True)
            
            # Determine which to delete
            to_delete = []
            for filename, filepath, age_days, size_mb in backup_files:
                # Keep at least 2 recent backups
                if len(backup_files) - len(to_delete) <= keep_min_backups:
                    break
                # Delete if older than 30 days
                if age_days > retention_days:
                    to_delete.append((filename, filepath, age_days, size_mb))
            
            if not to_delete:
                text = f"""ℹ️ *No Old Logs to Clear*
━━━━━━━━━━━━━━━━━━━━━━━━

• Backup Files: {len(backup_files)}
• Retention Policy: {retention_days} days
• Minimum Backups: {keep_min_backups}

✅ All backups are within retention period"""
                self.bot.send_message(text)
                return True
            
            # Delete old files
            deleted_count = 0
            freed_mb = 0.0
            for filename, filepath, age_days, size_mb in to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    freed_mb += size_mb
                    logger.info(f"Deleted old log: {filename} (age: {age_days} days)")
                except Exception as e:
                    logger.error(f"Failed to delete {filename}: {e}")
            
            text = f"""✅ *Old Logs Cleared*
━━━━━━━━━━━━━━━━━━━━━━━━

🗑️ *Deleted Files:* {deleted_count}
💾 *Space Freed:* {freed_mb:.2f} MB
📦 *Remaining Backups:* {len(backup_files) - deleted_count}

📅 *Retention Policy:* {retention_days} days
🔒 *Safety:* Kept {keep_min_backups} recent backups

💡 Current logs are unaffected"""
            
            self.bot.send_message(text)
            return True
            
        except Exception as e:
            logger.error(f"Clear old logs error: {e}")
            self.bot.send_message(f"❌ Error clearing logs: {str(e)}")
            return False
    
    def _execute_trading_debug_mode(self, params: Dict[str, Any]):
        """Enable/disable trading debug mode"""
        try:
            from src.utils.logging_config import logging_config
            
            mode = params.get("mode", "status").lower()
            
            if mode == "status":
                # Show current status
                status = "✅ ON" if getattr(logging_config, 'trading_debug', False) else "❌ OFF"
                text = f"""📊 *TRADING DEBUG MODE STATUS*
━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *Current Status:* {status}

"""
                
                if getattr(logging_config, 'trading_debug', False):
                    text += """🔍 *When Enabled:*
• Full trend analysis logged
• Signal decisions with reasons
• Entry/exit logic details
• Price action analysis
• Risk calculations shown

💡 Use /trading_debug_mode off to disable"""
                else:
                    text += """ℹ️ *When Disabled:*
• Only final trading actions
• Minimal log output
• Better performance

💡 Use /trading_debug_mode on to enable"""
                
                self.bot.send_message(text)
                return True
            
            elif mode == "on":
                old_status = getattr(logging_config, 'trading_debug', False)
                logging_config.trading_debug = True
                
                # Save to config for persistence
                self._save_trading_debug_to_config(True)
                
                text = f"""✅ *Trading Debug Mode ENABLED*
━━━━━━━━━━━━━━━━━━━━━━━━

• Previous: {'ON' if old_status else 'OFF'}
• New: ON

🔍 *What Will Be Logged:*
• Full trend analysis
• Signal decisions with reasons
• Entry/exit logic details
• Price action analysis
• Risk calculations

⚠️ *Impact:*
• Larger log files
• More detailed debugging
• Slightly slower execution

💡 Survives bot restart!"""
                
                self.bot.send_message(text)
                logger.info("Trading debug mode enabled")
                return True
            
            elif mode == "off":
                old_status = getattr(logging_config, 'trading_debug', False)
                logging_config.trading_debug = False
                
                # Save to config for persistence
                self._save_trading_debug_to_config(False)
                
                text = f"""✅ *Trading Debug Mode DISABLED*
━━━━━━━━━━━━━━━━━━━━━━━━

• Previous: {'ON' if old_status else 'OFF'}
• New: OFF

ℹ️ *What Will Be Logged:*
• Only final trading actions
• Order placement/closure
• Critical events only

✅ *Benefits:*
• Smaller log files
• Better performance
• Clean production logs

💡 Survives bot restart!"""
                
                self.bot.send_message(text)
                logger.info("Trading debug mode disabled")
                return True
            
            else:
                self.bot.send_message(f"❌ Invalid mode: {mode}\\nUse: on, off, or status")
                return False
                
        except Exception as e:
            logger.error(f"Trading debug mode error: {e}")
            self.bot.send_message(f"❌ Error changing debug mode: {str(e)}")
            return False
    
    def _execute_system_resources(self, params: Dict[str, Any]):
        """Show system resource usage"""
        try:
            import psutil
            import os
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            mem_total_gb = memory.total / (1024 ** 3)
            mem_used_gb = memory.used / (1024 ** 3)
            mem_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage(os.getcwd())
            disk_total_gb = disk.total / (1024 ** 3)
            disk_used_gb = disk.used / (1024 ** 3)
            disk_percent = disk.percent
            
            # Process info
            process = psutil.Process(os.getpid())
            bot_mem_mb = process.memory_info().rss / (1024 ** 2)
            bot_cpu_percent = process.cpu_percent(interval=1)
            
            # Load average
            try:
                load_avg = os.getloadavg()
                load_str = f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
            except:
                load_str = "N/A (Windows)"
            
            # Status emojis
            cpu_emoji = "🟢" if cpu_percent < 70 else "🟡" if cpu_percent < 90 else "🔴"
            mem_emoji = "🟢" if mem_percent < 70 else "🟡" if mem_percent < 90 else "🔴"
            disk_emoji = "🟢" if disk_percent < 70 else "🟡" if disk_percent < 90 else "🔴"
            
            text = f"""💻 *SYSTEM RESOURCES*
━━━━━━━━━━━━━━━━━━━━━━━━

{cpu_emoji} *CPU Usage:*
• Overall: {cpu_percent}%
• Cores: {cpu_count}
• Load Average: {load_str}

{mem_emoji} *Memory (RAM):*
• Used: {mem_used_gb:.2f} GB / {mem_total_gb:.2f} GB
• Usage: {mem_percent}%
• Available: {memory.available / (1024**3):.2f} GB

{disk_emoji} *Disk Space:*
• Used: {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB
• Usage: {disk_percent}%
• Free: {disk.free / (1024**3):.1f} GB

🤖 *Bot Process:*
• Memory: {bot_mem_mb:.1f} MB
• CPU: {bot_cpu_percent}%
• PID: {os.getpid()}

"""
            
            # Health summary
            if cpu_percent > 90 or mem_percent > 90 or disk_percent > 90:
                text += "⚠️ *Warning:* High resource usage detected!"
            elif cpu_percent > 70 or mem_percent > 70 or disk_percent > 70:
                text += "💡 *Status:* Moderate resource usage"
            else:
                text += "✅ *Status:* Healthy"
            
            self.bot.send_message(text)
            return True
            
        except ImportError:
            self.bot.send_message("❌ psutil not installed!\\nRun: pip install psutil")
            return False
        except Exception as e:
            logger.error(f"System resources error: {e}")
            self.bot.send_message(f"❌ Error checking resources: {str(e)}")
            return False
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        try:
            # Check if user_id matches configured admin
            if hasattr(self.bot, 'chat_id') and user_id == self.bot.chat_id:
                return True
            # Additional admin check from config
            if hasattr(self.bot, 'config'):
                admin_id = self.bot.config.get('telegram_chat_id', 0)
                return user_id == admin_id
            return False
        except:
            return False
    
    def _save_trading_debug_to_config(self, enabled: bool):
        """Save trading debug mode to config"""
        try:
            import json
            import os
            
            config_file = "config/logging_settings.json"
            os.makedirs("config", exist_ok=True)
            
            # Load existing settings
            settings = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    settings = json.load(f)
            
            # Update trading_debug
            settings["trading_debug"] = enabled
            
            # Save
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"Trading debug mode saved to config: {enabled}")
        except Exception as e:
            logger.warning(f"Could not save trading debug to config: {e}")
'''
    
    # Find the last handler method and insert before closing brace
    # Look for _execute_reset_health
    reset_health_pos = content.find('def _execute_reset_health')
    if reset_health_pos != -1:
        # Find the end of this method
        next_def_pos = content.find('\n    def ', reset_health_pos + 100)
        if next_def_pos == -1:
            # No next method, find class end or file end
            insert_pos = content.rfind('\n\n', reset_health_pos)
            if insert_pos == -1:
                insert_pos = len(content) - 1
        else:
            insert_pos = next_def_pos
        
        # Insert handlers
        content = content[:insert_pos] + handlers_code + '\n' + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Added 5 new command handlers + helper methods")
    else:
        print("  ⚠️  Could not find insertion point in command_executor.py")

def update_command_executor_map():
    """Add 5 commands to command_map dictionary"""
    print("\n🗺️  Updating command_executor.py (command_map)...")
    file_path = "src/menu/command_executor.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '"export_logs": self._execute_export_logs' in content:
        print("  ℹ️  Commands already in command_map")
        return
    
    # Find command_map dictionary
    map_entries = '''            "export_logs": self._execute_export_logs,
            "log_file_size": self._execute_log_file_size,
            "clear_old_logs": self._execute_clear_old_logs,
            "trading_debug_mode": self._execute_trading_debug_mode,
            "system_resources": self._execute_system_resources,'''
    
    # Insert after reset_health in command_map
    content = content.replace(
        '"reset_health": self._execute_reset_health,',
        '"reset_health": self._execute_reset_health,\n' + map_entries
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ Added 5 commands to command_map dictionary")

def update_logging_config():
    """Add trading_debug persistence loading"""
    print("\n📝 Updating logging_config.py...")
    file_path = "src/utils/logging_config.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if trading_debug already added
    if 'trading_debug = settings.get("trading_debug"' in content:
        print("  ℹ️  trading_debug persistence already in logging_config.py")
        return
    
    # Add trading_debug = False in __init__
    if 'self.trading_debug = False' not in content:
        content = content.replace(
            'self.current_level = LogLevel.INFO',
            'self.current_level = LogLevel.INFO\n        self.trading_debug = False'
        )
    
    # Add trading_debug loading in _load_log_level_from_config
    trading_debug_load = '''
                # Load trading_debug setting
                trading_debug = settings.get("trading_debug", False)
                self.trading_debug = trading_debug
                print(f"[LOGGING CONFIG] Loaded trading_debug: {trading_debug}")'''
    
    # Insert after log level loading
    content = content.replace(
        'print(f"[LOGGING CONFIG] Loaded saved log level: {level_name}")',
        'print(f"[LOGGING CONFIG] Loaded saved log level: {level_name}")' + trading_debug_load
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ Added trading_debug persistence loading")

def update_telegram_bot():
    """Add send_document method"""
    print("\n📤 Updating telegram_bot.py...")
    file_path = "src/telegram/telegram_bot.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def send_document' in content:
        print("  ℹ️  send_document method already in telegram_bot.py")
        return
    
    send_doc_method = '''
    def send_document(self, file_path: str, caption: str = ""):
        """Send a document file via Telegram"""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
            
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
            return False
'''
    
    # Find send_message method and insert after it
    send_msg_pos = content.find('def send_message')
    if send_msg_pos != -1:
        # Find end of send_message method
        next_method = content.find('\n    def ', send_msg_pos + 100)
        if next_method == -1:
            next_method = content.find('\nclass ', send_msg_pos)
        
        if next_method != -1:
            content = content[:next_method] + send_doc_method + '\n' + content[next_method:]
        else:
            # Append at end of class
            content = content.rstrip() + '\n' + send_doc_method + '\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Added send_document method")
    else:
        print("  ⚠️  Could not find send_message method")

def main():
    """Run all updates"""
    print("🚀 STARTING AUTOMATED IMPLEMENTATION")
    print("=" * 50)
    
    try:
        update_requirements()
        update_command_mapping()
        update_menu_constants()
        update_menu_manager()
        update_command_executor_handlers()
        update_command_executor_map()
        update_logging_config()
        update_telegram_bot()
        
        print("\n" + "=" * 50)
        print("✅ ALL UPDATES COMPLETED SUCCESSFULLY!")
        print("\n📋 Next steps:")
        print("1. Restart the bot: python src/main.py")
        print("2. Test commands via Telegram diagnostics menu")
        print("\n🎯 New commands added:")
        print("  • export_logs")
        print("  • log_file_size")
        print("  • clear_old_logs")
        print("  • trading_debug_mode")
        print("  • system_resources")
        print("\n" + "=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
