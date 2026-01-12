
import sys
import os
import importlib
import traceback

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

modules_to_check = [
    'src.database',
    'src.models',
    'src.config',
    'src.core.trading_engine',
    'src.managers.session_manager',
    'src.clients.telegram_bot',
    'src.managers.risk_manager',
    'src.managers.timeframe_trend_manager',
    'src.processors.alert_processor',
    'src.services.price_monitor_service',
    'src.services.reversal_exit_handler',
    'src.managers.dual_order_manager',
    'src.managers.profit_booking_manager',
    'src.managers.profit_booking_reentry_manager',
    'src.managers.autonomous_system_manager',
    'src.managers.reentry_manager',
    'src.utils.pip_calculator',
    'src.utils.optimized_logger'
]

print("🔍 Starting Import Verification Scan...")
print("-" * 50)

failed = False

for module_name in modules_to_check:
    try:
        print(f"Checking {module_name}...", end=" ")
        importlib.import_module(module_name)
        print("✅ OK")
    except Exception as e:
        print(f"❌ FAILED")
        print(f"Error in {module_name}: {str(e)}")
        traceback.print_exc()
        failed = True

print("-" * 50)
if failed:
    print("❌ Scan Completed with ERRORS")
    sys.exit(1)
else:
    print("✅ Scan Completed Successfully - No Circular Imports or Syntax Errors")
    sys.exit(0)
