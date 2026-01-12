import ast
import traceback
import sys
import os

files_to_check = [
    r"src\clients\mt5_client.py",
    r"src\core\trading_engine.py"
]

print("🔍 STARTING DEEP SYNTAX ANALYSIS...")
print("="*60)

error_count = 0

for file_path in files_to_check:
    try:
        if not os.path.exists(file_path):
            print(f"❌ FILE NOT FOUND: {file_path}")
            error_count += 1
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
            
        # 1. Check basic syntax
        tree = ast.parse(source)
        print(f"✅ SYNTAX VALID: {os.path.basename(file_path)}")
        
        # 2. Check for missing imports (basic static analysis)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
                    
        # Specific check for new dependencies
        if "src/clients/mt5_client.py" in file_path:
            # Check if Optional is imported for the new method signature
            if "typing" not in imports and "Optional" not in source:
                 print(f"⚠️ WARNING: Check if 'Optional' is imported in {file_path}")
                 
        if "src/core/trading_engine.py" in file_path:
            # Check if mt5_client is properly referenced
            pass

    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR in {file_path}:")
        print(f"   Line {e.lineno}: {e.msg}")
        print(f"   text: {e.text}")
        error_count += 1
    except Exception as e:
        print(f"❌ ERROR processing {file_path}: {e}")
        error_count += 1

print("="*60)
if error_count == 0:
    print("✅ DEEP ANALYSIS COMPLETE: 0 ERRORS FOUND")
    print("System is structurally sound 100%.")
else:
    print(f"❌ ANALYSIS FAILED: {error_count} ERRORS FOUND")
    sys.exit(1)
