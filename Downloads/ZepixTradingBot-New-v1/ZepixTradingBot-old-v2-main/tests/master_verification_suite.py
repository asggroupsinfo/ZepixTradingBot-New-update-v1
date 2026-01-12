import sys
import os
import subprocess
import time
from datetime import datetime

# Define test files
UNIT_TESTS = [
    "tests/test_fixed_clock_system.py",
    "tests/test_session_manager.py",
    "tests/test_session_menu_handler.py",
    "tests/test_voice_alert_system.py"
]

INTEGRATION_TESTS = [
    "tests/test_integration_phase6.py"
]

SIMULATIONS = [
    "tests/simulations/session_trade_simulation.py"
]

REQUIRED_FILES = [
    "src/modules/fixed_clock_system.py",
    "src/modules/session_manager.py",
    "src/modules/voice_alert_system.py",
    "src/telegram/session_menu_handler.py",
    "data/session_settings.json",
    "DOCUMENTATION/SESSION_MANAGER_GUIDE.md",
    "DOCUMENTATION/VOICE_ALERT_CONFIGURATION.md",
    "updates/v4_forex_session_system/07_FINAL_PROJECT_REPORT.md"
]

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_files():
    print_header("1. FILE EXISTENCE CHECK")
    missing = []
    for file_path in REQUIRED_FILES:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ MISSING: {file_path}")
            missing.append(file_path)
    
    if missing:
        print(f"\n❌ CRITICAL: {len(missing)} files missing!")
        return False
    return True

def run_test(command, description):
    print(f"\n🔹 Running {description}...")
    start = time.time()
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', env=env)
    duration = time.time() - start
    
    if result.returncode == 0:
        print(f"✅ PASSED ({duration:.2f}s)")
        return True, result.stdout
    else:
        print(f"❌ FAILED ({duration:.2f}s)")
        print("-" * 40)
        print(result.stdout)
        print(result.stderr)
        print("-" * 40)
        return False, result.stdout + result.stderr

def main():
    print_header("ZEPIX BOT v4 - MASTER VERIFICATION SUITE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. File Check
    if not check_files():
        print("\n⛔ ABORTING: File verification failed.")
        sys.exit(1)
        
    # 2. Unit Tests
    print_header("2. UNIT TESTS (Individual Modules)")
    failed_tests = []
    for test_file in UNIT_TESTS:
        success, _ = run_test(f"python -m pytest {test_file}", test_file)
        if not success: failed_tests.append(test_file)

    # 3. Integration Tests
    print_header("3. INTEGRATION TESTS (Wiring)")
    for test_file in INTEGRATION_TESTS:
        success, _ = run_test(f"python -m pytest {test_file}", test_file)
        if not success: failed_tests.append(test_file)

    # 4. Simulation
    print_header("4. E2E SIMULATION (Logic Flow)")
    for sim_file in SIMULATIONS:
        success, _ = run_test(f"python {sim_file}", sim_file)
        if not success: failed_tests.append(sim_file)

    # Summary
    print_header("VERIFICATION SUMMARY")
    if not failed_tests:
        print("✅ ALL SYSTEMS FUNCTIONAL")
        print("✅ ZERO TOLERANCE: 100% CODE COMPLIANCE")
        print("🚀 READY FOR DEPLOYMENT")
        sys.exit(0)
    else:
        print(f"❌ {len(failed_tests)} TESTS FAILED:")
        for t in failed_tests:
            print(f"   - {t}")
        print("⛔ DO NOT DEPLOY")
        sys.exit(1)

if __name__ == "__main__":
    main()
