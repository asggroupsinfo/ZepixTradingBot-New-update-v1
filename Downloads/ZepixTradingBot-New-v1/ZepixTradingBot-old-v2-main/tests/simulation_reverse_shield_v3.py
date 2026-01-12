import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.managers.reverse_shield_manager import ReverseShieldManager
from src.managers.risk_manager import RiskManager
from src.services.reverse_shield_notification_handler import ReverseShieldNotificationHandler
from src.models import Trade

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ReverseShieldSim")

async def run_simulation():
    print("\n🔹 STARTING REVERSE SHIELD v3.0 SIMULATION 🔹\n")
    
    # 1. Setup Mock Environment
    config_dict = {
        "reverse_shield_config": {
            "enabled": True,
            "recovery_threshold_percent": 0.70,
            "shield_lot_size_multiplier": 0.5,
            "risk_integration": {
                "enable_smart_adjustment": True,
                "min_daily_loss_buffer": 50.0,
                "cancel_if_below_min_lot": True
            },
            "notifications": {
                "shield_activated": True,
                "kill_switch_triggered": True,
                "show_smart_adjustment_details": True,
                "show_pnl_breakdown": True,
                "shield_cancelled": True
            }
        },
        "get_pip_value": lambda s: 10.0,
        "get_symbol_config": lambda s: {"pip_size": 0.01}
    }
    
    config_mock = MagicMock()
    
    def config_get(k, d=None):
        return config_dict.get(k, d)
        
    config_mock.get.side_effect = config_get
    
    # Explicitly mock methods
    config_mock.get_pip_value.side_effect = lambda s: 10.0
    config_mock.get_symbol_config.side_effect = lambda s: {"pip_size": 0.0001}

    # MT5 Client Mock
    mt5_client = MagicMock()
    mt5_client.get_symbol_tick_value.return_value = 1.0
    mt5_client.get_symbol_tick_size.return_value = 0.00001
    mt5_client.get_free_margin.return_value = 5000.0
    
    # Order execution mock
    mt5_client.execute_trade.side_effect = [
        {"order": 1001, "price": 1.1000}, # Shield A
        {"order": 1002, "price": 1.1000}  # Shield B
    ]
    
    # Close order mock
    mt5_client.close_order.return_value = {"profit": -5.0}

    # Managers Mock
    risk_manager = MagicMock()
    risk_manager.get_remaining_daily_loss.return_value = 100.0 # Strict limit for test
    
    profit_booking_manager = MagicMock()
    db = MagicMock()
    
    # Notification Handler Mock (Spy)
    telegram_bot = AsyncMock()
    notification_handler = ReverseShieldNotificationHandler(telegram_bot, config_mock)
    
    # Initialize Manager
    manager = ReverseShieldManager(
        config_mock, mt5_client, profit_booking_manager, 
        risk_manager, db, notification_handler
    )
    
    # 2. Scenario A: Shield Activation
    print("--- SCENARIO A: Shield Activation (BUY Original) ---")
    original_trade = Trade(
        trade_id=999,
        symbol="EURUSD",
        direction="BUY",
        lot_size=1.0,
        entry=1.1050,
        sl=1.1000, # SL Reached
        tp=1.1150,
        strategy="TEST",
        open_time=datetime.now().isoformat()
    )
    # Patch attributes for compatibility with older code access patterns if needed
    original_trade.entry_price = 1.1050
    original_trade.sl_price = 1.1000
    original_trade.tier = "5000"
    
    # Calculated Risk:
    # Gap = 50 pips. Multiplier 0.5 -> Shield Lot 0.5.
    # Shield Loss Per Trade = 50 pips * 0.5 lot * $10/pip = $250.
    # Total Shield Risk (2 orders) = $500.
    # Daily Room = $100. Buffer 50. Available = $50.
    # Expected: Huge reduction or Cancellation?
    # Logic: Target Loss 50. Total Potential 500. Ratio = 0.1.
    # Adjusted Lot = 0.5 * 0.1 = 0.05.
    
    print(f"Original Lot: {original_trade.lot_size}")
    print(f"Daily Room: {risk_manager.get_remaining_daily_loss.return_value}")
    
    result = await manager.activate_shield(original_trade, "TEST")
    
    if result:
        print("\n✅ Shield Activated Successfully!")
        print(f"Shield IDs: {result['shield_ids']}")
        print(f"Recovery 70% Level: {result['recovery_70_level']}")
        
        # Verify Teleprompter Output (via Mock)
        print("\n--- NOTIFICATION OUTPUT (Scenario A) ---")
        call_args = telegram_bot.send_message.call_args[0][0]
        print(call_args)
        
        if "SMART ADJUSTMENT" in call_args and "Lot reduced" in call_args:
             print("✅ Smart Adjustment Verified in Notification")
        else:
             print("❌ Smart Adjustment NOT detected!")
             
    else:
        print("❌ Shield Activation Failed unexpectedly")

    # 3. Scenario B: Kill Switch
    print("\n--- SCENARIO B: Kill Switch Trigger ---")
    
    # Simulate Price hitting 70% level
    # Buy SL 1.1000. Gap 50 pips.
    # Target 70% = SL + (50 * 0.7) = 1.1000 + 0.0035 = 1.1035.
    current_price = 1.1036
    elapsed = 120.0
    
    await manager.kill_switch(result['shield_ids'], original_trade, current_price, elapsed)
    
    print("\n✅ Kill Switch Executed")
    
    # Verify Close Calls
    print(f"MT5 Close Calls: {mt5_client.close_order.call_count} (Expected 2)")
    
    # Verify Notification
    print("\n--- NOTIFICATION OUTPUT (Scenario B) ---")
    # Get last call
    call_args_kill = telegram_bot.send_message.call_args[0][0]
    print(call_args_kill)
    
    if "KILL SWITCH TRIGGERED" in call_args_kill:
        print("✅ Kill Switch Alert Verified")
    
    print("\n🔹 SIMULATION COMPLETE 🔹")

if __name__ == "__main__":
    asyncio.run(run_simulation())
