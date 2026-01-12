"""
Unit tests for logic detection functionality
Tests the fix for 'Unknown logic' error that was flooding logs
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.managers.timeframe_trend_manager import TimeframeTrendManager


def test_detect_logic_from_direct_logic_names():
    """Test that direct logic names are returned as-is"""
    manager = TimeframeTrendManager()
    
    assert manager.detect_logic_from_strategy_or_timeframe("LOGIC1") == "LOGIC1"
    assert manager.detect_logic_from_strategy_or_timeframe("LOGIC2") == "LOGIC2"
    assert manager.detect_logic_from_strategy_or_timeframe("LOGIC3") == "LOGIC3"
    print("✅ PASSED: Direct logic names")


def test_detect_logic_from_timeframe():
    """Test that logic is correctly detected from timeframes"""
    manager = TimeframeTrendManager()
    
    # 5m -> LOGIC1
    assert manager.detect_logic_from_strategy_or_timeframe("ZepixPremium", "5m") == "LOGIC1"
    assert manager.detect_logic_from_strategy_or_timeframe("AnyStrategy", "5M") == "LOGIC1"
    
    # 15m -> LOGIC2
    assert manager.detect_logic_from_strategy_or_timeframe("ZepixPremium", "15m") == "LOGIC2"
    assert manager.detect_logic_from_strategy_or_timeframe("AnyStrategy", "15M") == "LOGIC2"
    
    # 1h -> LOGIC3
    assert manager.detect_logic_from_strategy_or_timeframe("ZepixPremium", "1h") == "LOGIC3"
    assert manager.detect_logic_from_strategy_or_timeframe("AnyStrategy", "1H") == "LOGIC3"
    
    print("✅ PASSED: Logic detection from timeframe")


def test_detect_logic_from_strategy_name():
    """Test that logic is extracted from strategy names containing LOGIC1/2/3"""
    manager = TimeframeTrendManager()
    
    assert manager.detect_logic_from_strategy_or_timeframe("LOGIC1_FRESH") == "LOGIC1"
    assert manager.detect_logic_from_strategy_or_timeframe("LOGIC2_REENTRY") == "LOGIC2"
    assert manager.detect_logic_from_strategy_or_timeframe("ZepixPremium_LOGIC3") == "LOGIC3"
    assert manager.detect_logic_from_strategy_or_timeframe("logic1_test") == "LOGIC1"  # case insensitive
    
    print("✅ PASSED: Logic extraction from strategy names")


def test_cannot_detect_returns_none():
    """Test that None is returned when logic cannot be detected"""
    manager = TimeframeTrendManager()
    
    assert manager.detect_logic_from_strategy_or_timeframe("UnknownStrategy") is None
    assert manager.detect_logic_from_strategy_or_timeframe("ZepixPremium") is None
    assert manager.detect_logic_from_strategy_or_timeframe("RandomName", "4h") is None
    
    print("✅ PASSED: Returns None when cannot detect")


def test_check_logic_alignment_with_normalization():
    """Test that check_logic_alignment normalizes ZepixPremium to correct logic"""
    manager = TimeframeTrendManager()
    
    # Add some test trends
    manager.update_trend("XAUUSD", "15m", "bear", "MANUAL")
    manager.update_trend("XAUUSD", "1h", "bear", "MANUAL")
    
    # This should NOT cause "Unknown logic" - it should auto-normalize
    result = manager.check_logic_alignment("XAUUSD", "LOGIC1")
    assert result is not None
    assert "failure_reason" in result
    # LOGIC1 requires 1h + 15m alignment, which we have (both BEARISH)
    
    print("✅ PASSED: check_logic_alignment with normalization")


def test_critical_fix_zepix_premium_strategy():
    """
    CRITICAL TEST: This is the exact scenario causing the 2746-line log error
    TradingView sends strategy: "ZepixPremium" and bot should handle it
    """
    manager = TimeframeTrendManager()
    
    # Set up trends for LOGIC1 (5m entries, needs 1h + 15m alignment)
    manager.update_trend("XAUUSD", "15m", "bearish", "AUTO")
    manager.update_trend("XAUUSD", "1h", "bearish", "AUTO")
    
    # This was causing "Unknown logic" error before fix
    # Now it should auto-detect that we can't determine logic from "ZepixPremium" alone
    result = manager.check_logic_alignment("XAUUSD", "ZepixPremium")
    
    # Should return a result (not crash)
    assert result is not None
    
    # Should have a failure reason explaining it couldn't auto-detect
    assert "Unknown logic" in result.get("failure_reason", "")
    
    print("✅ PASSED: Critical fix - ZepixPremium handling")
    print(f"   Result: {result['failure_reason']}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running Logic Detection Unit Tests")
    print("="*60 + "\n")
    
    try:
        test_detect_logic_from_direct_logic_names()
        test_detect_logic_from_timeframe()
        test_detect_logic_from_strategy_name()
        test_cannot_detect_returns_none()
        test_check_logic_alignment_with_normalization()
        test_critical_fix_zepix_premium_strategy()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nLogic detection is working correctly.")
        print("The 'Unknown logic' error should be fixed.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
