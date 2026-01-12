"""
Session Logic Tracking Test - Verify Phase 6 implementation
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import TradeDatabase
from src.models import Trade
from src.managers.session_manager import SessionManager

# Mock MT5 Client
class MockMT5Client:
    pass

def test_session_logic_tracking():
    """Test that session manager correctly tracks logic-specific stats"""
    
    print("=" * 70)
    print("PHASE 6: SESSION LOGIC TRACKING TEST")
    print("=" * 70)
    
    # Initialize components
    db = TradeDatabase()
    mt5_client = MockMT5Client()
    config = {}
    session_mgr = SessionManager(config, db, mt5_client)
    
    # Step 1: Create sessions for different logics
    print("\n1️⃣ CREATING SESSIONS WITH DIFFERENT LOGICS...")
    
    session_id_logic1 = session_mgr.create_session(
        symbol="EURUSD",
        direction="BUY",
        signal="BULLISH",
        logic="LOGIC1"
    )
    print(f"   ✅ Created LOGIC1 session: {session_id_logic1}")
    
    # Step 2: Simulate trades and update stats
    print("\n2️⃣ SIMULATING LOGIC1 TRADES...")
    
    # Trade 1: LOGIC1 Win
    trade1 = Trade(
        symbol="EURUSD",
        entry=1.1000,
        sl=1.0950,
        tp=1.1050,
        lot_size=0.125,
        direction="BUY",
        strategy="LOGIC1",
        status="closed",
        open_time=datetime.now().isoformat(),
        close_time=datetime.now().isoformat(),
        pnl=50.0,
        logic_type="LOGIC1",
        lot_multiplier=1.25,
        sl_multiplier=1.0
    )
    
    db.save_trade(trade1)
    session_mgr.update_logic_stats(trade1)
    print(f"   ✅ Trade 1: WIN +$50 (Lot Mult: 1.25x)")
    
    # Trade 2: LOGIC1 Loss
    trade2 = Trade(
        symbol="EURUSD",
        entry=1.1000,
        sl=1.0950,
        tp=1.1050,
        lot_size=0.125,
        direction="BUY",
        strategy="LOGIC1",
        status="closed",
        open_time=datetime.now().isoformat(),
        close_time=datetime.now().isoformat(),
        pnl=-25.0,
        logic_type="LOGIC1",
        lot_multiplier=1.25,
        sl_multiplier=1.0
    )
    
    db.save_trade(trade2)
    session_mgr.update_logic_stats(trade2)
    print(f"   ✅ Trade 2: LOSS -$25 (Lot Mult: 1.25x)")
    
    # Close current session and create LOGIC3 session
    session_mgr.close_session("TEST_SWITCH")
    
    print("\n3️⃣ CREATING LOGIC3 SESSION...")
    session_id_logic3 = session_mgr.create_session(
        symbol="GBPUSD",
        direction="SELL",
        signal="BEARISH",
        logic="LOGIC3"
    )
    print(f"   ✅ Created LOGIC3 session: {session_id_logic3}")
    
    # Trade 3: LOGIC3 Win
    trade3 = Trade(
        symbol="GBPUSD",
        entry=1.2500,
        sl=1.2625,
        tp=1.2375,
        lot_size=0.0625,
        direction="SELL",
        strategy="LOGIC3",
        status="closed",
        open_time=datetime.now().isoformat(),
        close_time=datetime.now().isoformat(),
        pnl=75.0,
        logic_type="LOGIC3",
        lot_multiplier=0.625,
        sl_multiplier=2.5
    )
    
    db.save_trade(trade3)
    session_mgr.update_logic_stats(trade3)
    print(f"   ✅ Trade 3: WIN +$75 (Lot Mult: 0.625x, SL Mult: 2.5x)")
    
    # Step 3: Verify session metadata
    print("\n4️⃣ VERIFYING SESSION METADATA...")
    
    import json
    cursor = db.conn.cursor()
    
    # Check LOGIC1 session
    cursor.execute(
        "SELECT metadata FROM trading_sessions WHERE session_id = ?",
        (session_id_logic1,)
    )
    result1 = cursor.fetchone()
    
    if result1 and result1[0]:
        metadata1 = json.loads(result1[0])
        logic_stats1 = metadata1.get("logic_stats", {}).get("LOGIC1", {})
        
        print(f"\n   📊 LOGIC1 Session Stats:")
        print(f"      Total Trades: {logic_stats1.get('trades', 0)}")
        print(f"      Wins: {logic_stats1.get('wins', 0)}")
        print(f"      Losses: {logic_stats1.get('losses', 0)}")
        print(f"      Total PnL: ${logic_stats1.get('pnl', 0):.2f}")
        print(f"      Avg Lot Multiplier: {logic_stats1.get('avg_lot_multiplier', 0):.2f}x")
        print(f"      Avg SL Multiplier: {logic_stats1.get('avg_sl_multiplier', 0):.2f}x")
        
        # Verify correctness
        assert logic_stats1['trades'] == 2, f"Expected 2 trades, got {logic_stats1['trades']}"
        assert logic_stats1['wins'] == 1, f"Expected 1 win, got {logic_stats1['wins']}"
        assert logic_stats1['losses'] == 1, f"Expected 1 loss, got {logic_stats1['losses']}"
        assert logic_stats1['pnl'] == 25.0, f"Expected PnL $25.0, got ${logic_stats1['pnl']}"
        assert logic_stats1['avg_lot_multiplier'] == 1.25, f"Expected avg lot mult 1.25, got {logic_stats1['avg_lot_multiplier']}"
        print("      ✅ All stat values correct!")
    else:
        print("  ❌ LOGIC1 session metadata not found!")
        return False
    
    # Check LOGIC3 session
    cursor.execute(
        "SELECT metadata FROM trading_sessions WHERE session_id = ?",
        (session_id_logic3,)
    )
    result3 = cursor.fetchone()
    
    if result3 and result3[0]:
        metadata3 = json.loads(result3[0])
        logic_stats3 = metadata3.get("logic_stats", {}).get("LOGIC3", {})
        
        print(f"\n   📊 LOGIC3 Session Stats:")
        print(f"      Total Trades: {logic_stats3.get('trades', 0)}")
        print(f"      Wins: {logic_stats3.get('wins', 0)}")
        print(f"      Losses: {logic_stats3.get('losses', 0)}")
        print(f"      Total PnL: ${logic_stats3.get('pnl', 0):.2f}")
        print(f"      Avg Lot Multiplier: {logic_stats3.get('avg_lot_multiplier', 0):.2f}x")
        print(f"      Avg SL Multiplier: {logic_stats3.get('avg_sl_multiplier', 0):.2f}x")
        
        # Verify correctness
        assert logic_stats3['trades'] == 1, f"Expected 1 trade, got {logic_stats3['trades']}"
        assert logic_stats3['wins'] == 1, f"Expected 1 win, got {logic_stats3['wins']}"
        assert logic_stats3['pnl'] == 75.0, f"Expected PnL $75.0, got ${logic_stats3['pnl']}"
        assert logic_stats3['avg_sl_multiplier'] == 2.5, f"Expected avg SL mult 2.5, got {logic_stats3['avg_sl_multiplier']}"
        print("      ✅ All LOGIC3 values correct!")
    else:
        print("   ❌ LOGIC3 session metadata not found!")
        return False
    
    print("\n" + "=" * 70)
    print("✅ PHASE 6: SESSION LOGIC TRACKING TEST PASSED!")
    print("=" * 70)
    print("\n🎉 Sessions correctly track logic-specific performance stats!")
    return True

if __name__ == "__main__":
    try:
        success = test_session_logic_tracking()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
