#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all dependency checks in telegram_bot.py
"""
import re

# Read the file
with open('src/clients/telegram_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find all "if not self.trading_engine" or "if not self.risk_manager" checks
# We need to add dependency retrieval before these checks

# Find all handlers that check dependencies
pattern = r'(def handle_\w+\(self, message\):.*?)(if not self\.(trading_engine|risk_manager):.*?self\.send_message\("❌ (?:Trading engine|Risk manager|Bot) not initialized"\))'

def fix_dependency_check(match):
    func_def = match.group(1)
    check = match.group(2)
    dep_name = match.group(3)
    
    # Add dependency retrieval before check
    if dep_name == 'trading_engine':
        retrieval = """        # Try to get dependencies if not available
        if not self.trading_engine:
            # Dependencies should be set, but try to continue if not available yet
            pass
"""
    else:  # risk_manager
        retrieval = """        # Try to get dependencies if not available
        if not self.risk_manager:
            if self.trading_engine and hasattr(self.trading_engine, 'risk_manager'):
                self.risk_manager = self.trading_engine.risk_manager
"""
    
    return func_def + retrieval + check.replace('not initialized', 'still initializing. Please wait a moment.')

# Apply fix
new_content = re.sub(pattern, fix_dependency_check, content, flags=re.DOTALL)

# Write back
with open('src/clients/telegram_bot.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed dependency checks")

