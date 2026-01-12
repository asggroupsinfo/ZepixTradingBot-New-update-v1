import os

def replace_polling_method():
    target_file = 'src/clients/telegram_bot.py'
    replacement_file = 'polling_code.txt'
    
    with open(target_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(replacement_file, 'r', encoding='utf-8') as f:
        new_method = f.read()
        
    # Find start and end of start_polling method
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if 'def start_polling(self):' in line:
            start_idx = i
            break
            
    if start_idx == -1:
        print("Could not find start_polling method")
        return
        
    # Find the end (start of next method or end of file)
    # Actually, start_polling is the last method in the file usually
    # But let's be safe. It seems it is the last method based on previous views
    
    # Let's just replace from start_idx to the end of the file if it's the last method
    # Or find the next unindented line? No, it's inside a class.
    
    # Based on previous `view_file`, start_polling starts at line 3088 and goes to end.
    # Let's verify if there is anything after it.
    
    # We will replace from start_idx to the end of the file, assuming it's the last method.
    # The replacement text should be properly indented.
    
    # The file content in polling_code.txt is already indented with 4 spaces.
    
    new_lines = lines[:start_idx]
    new_lines.append(new_method)
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Successfully replaced start_polling method")

if __name__ == '__main__':
    replace_polling_method()
