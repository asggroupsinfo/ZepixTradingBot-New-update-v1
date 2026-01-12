# Quick fix for menu_manager.py param_name bug
filepath = 'src/menu/menu_manager.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix param_name to param_type for lines section
content = content.replace(
    'keyboard = [\n                [{"text": f"📄 {opt} lines", "callback_data": f"param_{param_name}_{opt}"}]',
    'keyboard = [\n                [{"text": f"📄 {opt} lines", "callback_data": f"param_{param_type}_{opt}"}]'
)

# Fix param_name to param_type for mode section  
content = content.replace(
    '[{"text": f"{emoji_map[opt]} {opt.upper()}", "callback_data": f"param_{param_name}_{opt}"}]',
    '[{"text": f"{emoji_map[opt]} {opt.upper()}", "callback_data": f"param_{param_type}_{opt}"}]'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed param_name bug in menu_manager.py')
