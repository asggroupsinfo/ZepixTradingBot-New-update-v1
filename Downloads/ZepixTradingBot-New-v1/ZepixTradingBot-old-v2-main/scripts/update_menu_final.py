filepath = 'src/menu/menu_constants.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find diagnostics section and add 5 new commands
old_diagnostics = '''    "diagnostics": {
        "name": "🔍 Diagnostics & Health",
        "commands": {
            "health_status": COMMAND_PARAM_MAP["health_status"],
            "set_log_level": COMMAND_PARAM_MAP["set_log_level"],
            "get_log_level": COMMAND_PARAM_MAP["get_log_level"],
            "reset_log_level": COMMAND_PARAM_MAP["reset_log_level"],
            "error_stats": COMMAND_PARAM_MAP["error_stats"],
            "reset_errors": COMMAND_PARAM_MAP["reset_errors"],
            "reset_health": COMMAND_PARAM_MAP["reset_health"],
        }
    }'''

new_diagnostics = '''    "diagnostics": {
        "name": "🔍 Diagnostics & Health",
        "commands": {
            "health_status": COMMAND_PARAM_MAP["health_status"],
            "set_log_level": COMMAND_PARAM_MAP["set_log_level"],
            "get_log_level": COMMAND_PARAM_MAP["get_log_level"],
            "reset_log_level": COMMAND_PARAM_MAP["reset_log_level"],
            "error_stats": COMMAND_PARAM_MAP["error_stats"],
            "reset_errors": COMMAND_PARAM_MAP["reset_errors"],
            "reset_health": COMMAND_PARAM_MAP["reset_health"],
            "export_logs": COMMAND_PARAM_MAP["export_logs"],
            "log_file_size": COMMAND_PARAM_MAP["log_file_size"],
            "clear_old_logs": COMMAND_PARAM_MAP["clear_old_logs"],
            "trading_debug_mode": COMMAND_PARAM_MAP["trading_debug_mode"],
            "system_resources": COMMAND_PARAM_MAP["system_resources"],
        }
    }'''

content = content.replace(old_diagnostics, new_diagnostics)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Added 5 new commands to Diagnostics menu!')
