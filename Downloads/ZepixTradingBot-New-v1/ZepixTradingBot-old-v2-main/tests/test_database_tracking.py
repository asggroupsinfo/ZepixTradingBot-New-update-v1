"""
Database Tracking Test - Verify logic_type and multipliers are saved correctly
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import TradeDatabase
from src.models import Trade

def test_database_logic_tracking():
    """Test that database correctly saves and retrieves logic-specific data"""
    
    print("=" * 60)
    print("DATABASE LOGIC TRACKING TEST")
    print("=" * 60)
    
    # Initialize database
    db = TradeDatabase()
    
    # Create test trades with different logics
    test_trades = [
        {
            "symbol": "EURUSD",
            "entry": 1.1000,
            "sl": 1.0950,
            "tp": 1.1050,
            "lot_size": 0.125,  # Base 0.10 * 1.25
            "direction": "BUY",
            "strategy": "LOGIC1",
            "status": "open",
            "open_time": datetime.now().isoformat(),
            # Logic-specific fields
            "logic_type": "LOGIC1",
            "base_lot_size": 0.10,
            "final_lot_size": 0.125,
            "lot_multiplier": 1.25,
            "sl_multiplier": 1.0,
            "base_sl_pips": 50.0,
            "final_sl_pips": 50.0
        },
        {
            "symbol": "GBPUSD",
            "entry": 1.2500,
            "sl": 1.2375,
            "tp": 1.2625,
            "lot_size": 0.0625,  # Base 0.10 * 0.625
            "direction": "BUY",
            "strategy": "LOGIC3",
            "status": "open",
            "open_time": datetime.now().isoformat(),
            # Logic-specific fields
            "logic_type": "LOGIC3",
            "base_lot_size": 0.10,
            "final_lot_size": 0.0625,
            "lot_multiplier": 0.625,
            "sl_multiplier": 2.5,
            "base_sl_pips": 50.0,
            "final_sl_pips": 125.0  # 50 * 2.5
        }
    ]
    
    # Step 1: Save trades
    print("\n1️⃣ SAVING TEST TRADES...")
    for trade_data in test_trades:
        trade = Trade(**trade_data)
        db.save_trade(trade)
        print(f"   ✅ Saved {trade.strategy}: Lot={trade.lot_size}, Multiplier={trade_data['lot_multiplier']}")
    
    # Step 2: Verify data in database
    print("\n2️⃣ VERIFYING DATABASE STORAGE...")
    cursor = db.conn.cursor()
    
    # Check LOGIC1 trade
    cursor.execute("""
        SELECT trade_id, strategy, lot_size, base_lot_size, final_lot_size, 
               lot_multiplier, sl_multiplier, logic_type
        FROM trades 
        WHERE strategy = 'LOGIC1' AND symbol = 'EURUSD'
        ORDER BY open_time DESC LIMIT 1
    """)
    logic1_result = cursor.fetchone()
    
    if logic1_result:
        print(f"\n   📊 LOGIC1 Trade Retrieved:")
        print(f"      Trade ID: {logic1_result[0]}")
        print(f"      Strategy: {logic1_result[1]}")
        print(f"      Lot Size: {logic1_result[2]}")
        print(f"      Base Lot: {logic1_result[3]}")
        print(f"      Final Lot: {logic1_result[4]}")
        print(f"      Lot Multiplier: {logic1_result[5]}")
        print(f"      SL Multiplier: {logic1_result[6]}")
        print(f"      Logic Type: {logic1_result[7]}")
        
        # Verify correctness
        assert logic1_result[5] == 1.25, f"❌ Lot multiplier mismatch! Expected 1.25, got {logic1_result[5]}"
        assert logic1_result[3] == 0.10, f"❌ Base lot mismatch! Expected 0.10, got {logic1_result[3]}"
        assert logic1_result[4] == 0.125, f"❌ Final lot mismatch! Expected 0.125, got {logic1_result[4]}"
        print("      ✅ All values correct!")
    else:
        print("   ❌ LOGIC1 trade not found in database!")
        return False
    
    # Check LOGIC3 trade
    cursor.execute("""
        SELECT trade_id, strategy, lot_size, base_lot_size, final_lot_size, 
               lot_multiplier, sl_multiplier, logic_type, base_sl_pips, final_sl_pips
        FROM trades 
        WHERE strategy = 'LOGIC3' AND symbol = 'GBPUSD'
        ORDER BY open_time DESC LIMIT 1
    """)
    logic3_result = cursor.fetchone()
    
    if logic3_result:
        print(f"\n   📊 LOGIC3 Trade Retrieved:")
        print(f"      Trade ID: {logic3_result[0]}")
        print(f"      Strategy: {logic3_result[1]}")
        print(f"      Lot Size: {logic3_result[2]}")
        print(f"      Base Lot: {logic3_result[3]}")
        print(f"      Final Lot: {logic3_result[4]}")
        print(f"      Lot Multiplier: {logic3_result[5]}")
        print(f"      SL Multiplier: {logic3_result[6]}")
        print(f"      Logic Type: {logic3_result[7]}")
        print(f"      Base SL Pips: {logic3_result[8]}")
        print(f"      Final SL Pips: {logic3_result[9]}")
        
        # Verify correctness
        assert logic3_result[5] == 0.625, "❌ Lot multiplier mismatch!"
        assert logic3_result[6] == 2.5, "❌ SL multiplier mismatch!"
        assert logic3_result[3] == 0.10, "❌ Base lot mismatch!"
        assert logic3_result[4] == 0.0625, "❌ Final lot mismatch!"
        print("      ✅ All values correct!")
    else:
        print("   ❌ LOGIC3 trade not found in database!")
        return False
    
    # Step 3: Test retrieval and analysis
    print("\n3️⃣ TESTING LOGIC-SPECIFIC QUERIES...")
    
    # Get all LOGIC1 trades
    cursor.execute("""
        SELECT COUNT(*), AVG(lot_multiplier), AVG(sl_multiplier)
        FROM trades 
        WHERE logic_type = 'LOGIC1'
    """)
    logic1_stats = cursor.fetchone()
    print(f"   📈 LOGIC1 Stats: {logic1_stats[0]} trades, Avg Lot Mult: {logic1_stats[1]}, Avg SL Mult: {logic1_stats[2]}")
    
    # Get all LOGIC3 trades
    cursor.execute("""
        SELECT COUNT(*), AVG(lot_multiplier), AVG(sl_multiplier)
        FROM trades 
        WHERE logic_type = 'LOGIC3'
    """)
    logic3_stats = cursor.fetchone()
    print(f"   📈 LOGIC3 Stats: {logic3_stats[0]} trades, Avg Lot Mult: {logic3_stats[1]}, Avg SL Mult: {logic3_stats[2]}")
    
    print("\n" + "=" * 60)
    print("✅ DATABASE TRACKING TEST PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_database_logic_tracking()
        if success:
            print("\n🎉 Database is correctly saving and retrieving logic-specific data!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
