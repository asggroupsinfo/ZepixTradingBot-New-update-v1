filepath = 'src/menu/command_mapping.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix double comma
content = content.replace('},,', '},')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed double comma')
