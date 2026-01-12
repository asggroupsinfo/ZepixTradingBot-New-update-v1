"""
V3 ALL 10 SYMBOLS - CONFIG VERIFICATION TEST
=============================================
Simplified test to verify all 10 symbols are properly configured.
"""

import json
import sys
import os

# Change to project root
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')

print()
print("=" * 80)
print("🔍 V3 ALL 10 SYMBOLS - CONFIGURATION AUDIT")
print("=" * 80)
print()

# Load config
with open('config/config.json', 'r') as f:
    config = json.load(f)

# ALL 10 SYMBOLS
ALL_SYMBOLS = [
    "XAUUSD",   # 1. Gold
    "EURUSD",   # 2. EUR/USD
    "GBPUSD",   # 3. GBP/USD
    "USDJPY",   # 4. USD/JPY
    "USDCAD",   # 5. USD/CAD
    "AUDUSD",   # 6. AUD/USD
    "NZDUSD",   # 7. NZD/USD
    "EURJPY",   # 8. EUR/JPY
    "GBPJPY",   # 9. GBP/JPY
    "AUDJPY"    # 10. AUD/JPY
]

# Check each symbol
symbol_config = config.get('symbol_config', {})
symbol_mapping = config.get('symbol_mapping', {})
sl_system_1 = config.get('sl_systems', {}).get('sl-1', {}).get('symbols', {})
sl_system_2 = config.get('sl_systems', {}).get('sl-2', {}).get('symbols', {})
v3_enabled = config.get('v3_integration', {}).get('enabled', False)

print("✅ V3 Integration Enabled:", v3_enabled)
print()
print("=" * 80)
print("📊 SYMBOL-BY-SYMBOL CONFIGURATION CHECK")
print("=" * 80)
print()

all_ready = True
ready_count = 0

for i, symbol in enumerate(ALL_SYMBOLS, 1):
    print(f"{i:2d}. {symbol:8s}")
    print("-" * 60)
    
    # Check 1: Symbol Config
    has_config = symbol in symbol_config
    if has_config:
        sym_cfg = symbol_config[symbol]
        print(f"   ✅ Symbol Config      | Volatility: {sym_cfg.get('volatility', 'N/A'):6s} | Pip Size: {sym_cfg.get('pip_size', 0)}")
    else:
        print(f"   ❌ Symbol Config      | MISSING")
        all_ready = False
    
    # Check 2: Symbol Mapping
    has_mapping = symbol in symbol_mapping
    if has_mapping:
        print(f"   ✅ Symbol Mapping     | TradingView → MT5: {symbol} → {symbol_mapping[symbol]}")
    else:
        print(f"   ❌ Symbol Mapping     | MISSING")
        all_ready = False
    
    # Check 3: SL System 1
    has_sl1 = symbol in sl_system_1
    if has_sl1:
        sl1_levels = len(sl_system_1[symbol].keys())
        print(f"   ✅ SL System 1        | {sl1_levels} account tiers configured")
    else:
        print(f"   ❌ SL System 1        | MISSING")
        all_ready = False
    
    # Check 4: SL System 2
    has_sl2 = symbol in sl_system_2
    if has_sl2:
        sl2_levels = len(sl_system_2[symbol].keys())
        print(f"   ✅ SL System 2        | {sl2_levels} account tiers configured")
    else:
        print(f"   ❌ SL System 2        | MISSING")
        all_ready = False
    
    # Overall Status
    symbol_ready = has_config and has_mapping and has_sl1 and has_sl2
    if symbol_ready:
        print(f"   🎯 STATUS: ✅ READY FOR V3 TRADING")
        ready_count += 1
    else:
        print(f"   🎯 STATUS: ❌ NOT READY")
    
    print()

# Final Summary
print("=" * 80)
print("📊 FINAL SUMMARY")
print("=" * 80)
print()
print(f"Total Symbols: {len(ALL_SYMBOLS)}")
print(f"Ready Symbols: {ready_count}/{len(ALL_SYMBOLS)}")
print(f"Completion: {(ready_count/len(ALL_SYMBOLS))*100:.1f}%")
print()

if all_ready:
    print("✅ ALL 10 SYMBOLS ARE FULLY CONFIGURED AND V3-READY!")
    print()
    print("🚀 YOU CAN START TRADING ON ALL SYMBOLS:")
    for i, symbol in enumerate(ALL_SYMBOLS, 1):
        print(f"   {i:2d}. {symbol}")
    print()
    print("=" * 80)
    print("🎯 NEXT STEPS:")
    print("=" * 80)
    print("1. Add TradingView indicator on all 10 symbols")
    print("2. Configure webhook alerts for each symbol")
    print("3. Start bot: python main.py")
    print("4. Bot will automatically handle alerts from any of these symbols")
    print()
    sys.exit(0)
else:
    print("⚠️ SOME SYMBOLS ARE NOT FULLY CONFIGURED")
    print("Please check missing configurations above.")
    print()
    sys.exit(1)
