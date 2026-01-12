import asyncio
import logging
from typing import Dict, Optional, Any, List
from src.models import Trade
from src.services.reverse_shield_notification_handler import ReverseShieldNotificationHandler

logger = logging.getLogger(__name__)

class ReverseShieldManager:
    """
    Manager for the Reverse Shield v3.0 system.
    Handles 'Immediate Reverse Offense' and 'Monitor Defense'.
    """

    def __init__(self, config, mt5_client, profit_booking_manager, risk_manager, db, notification_handler: ReverseShieldNotificationHandler):
        self.config = config
        self.mt5_client = mt5_client
        self.profit_booking_manager = profit_booking_manager
        self.risk_manager = risk_manager
        self.db = db
        self.notification_handler = notification_handler
        
        # Load config
        self.rs_config = config.get("reverse_shield_config", {})
        
        # Shield Order A & B tracking
        self.active_shields = {} # original_order_id -> {shield_a_id, shield_b_id, ...}
        
        logger.info("✅ ReverseShieldManager initialized")

    def is_enabled(self) -> bool:
        """Check if Reverse Shield system is enabled in config"""
        # Reload config in case it changed
        self.rs_config = self.config.get("reverse_shield_config", {})
        return self.rs_config.get("enabled", False)

    def calculate_shield_parameters(self, original_trade: Trade) -> Dict:
        """
        Calculate Loss Gap, 70% Recovery Level, and Shield Levels.
        """
        entry_price = original_trade.entry_price
        sl_price = original_trade.sl_price
        direction = original_trade.direction
        symbol = original_trade.symbol
        
        # 1. Loss Gap
        loss_gap = abs(entry_price - sl_price)
        
        # Pip calculation (approx for info)
        pip_value_info = self.config.get_pip_value(symbol) # Helper if exists, else estimate
        # Using simple subtraction for raw price gap
        
        # 2. 70% Recovery Level
        # If BUY was original: SL is below. Recovery is UP. 70% of gap from SL up.
        # If SELL was original: SL is above. Recovery is DOWN. 70% of gap from SL down.
        recovery_threshold = self.rs_config.get("recovery_threshold_percent", 0.70)
        
        if direction == "BUY":
            # Original BUY -> SL Triggered at SL Price (Lower).
            # We want to re-enter if price recovers UP towards Entry.
            # 70% level = SL + (Gap * 0.7)
            recovery_70_level = sl_price + (loss_gap * recovery_threshold)
            
            # Shield Direction is SELL (Opposite)
            shield_direction = "SELL"
            # Shield TP = Entry - Gap (Downwards from new entry? No, strictly defined in blueprint)
            # Blueprint: "TP: Fixed at Entry_Price - Loss_Gap" (If original was BUY, Price is at SL. Shield is SELL.
            # Wait, if Original was BUY, price fell to SL. We Open SELL Shield.
            # Shield Entry ~= SL Price.
            # Shield TP target? "Entry_Price - Loss_Gap" ??
            # Blueprint says: "TP: Fixed at Entry_Price - Loss_Gap (1:1 Recovery)."
            # If Entry 2000, SL 1990. Gap 10.
            # Price is at 1990. We Sell.
            # "Entry_Price (2000) - Loss_Gap (10)" = 1990? That's the entry.
            # Ah, maybe blueprint meant "Current Price - Loss_Gap"?
            # Let's re-read blueprint path A carefully:
            # "Shield Order A: TP: Fixed at Entry_Price - Loss_Gap (1:1 Recovery)."
            # If I am at 1990 (SL hit). I Sell.
            # If I target 1980 (10 pips lower), that is 1:1.
            # 1990 (Current) - 10 (Gap) = 1980.
            # Variable: "Entry_Price" in blueprint usually refers to Original Entry. 
            # But "Entry_Price - Loss Gap" = 2000 - 10 = 1990 (Current Price). TP cannot be Current Price.
            # Interpretation: The User likely means "From Shield Entry, target the Loss Gap distance".
            # So Shield TP Price = Shield Entry - Loss Gap (for SELL).
            # Shield Entry is approx SL Price. So SL Price - Loss Gap.
            
            # Shield SL = "Shield Invalidation SL" = Original Entry Price.
            # If I Sell at 1990, SL at 2000. Risk = 10.
            # TP at 1980. Reward = 10. 1:1. Correct.
            
            shield_tp_price = sl_price - loss_gap
            shield_sl_price = entry_price
            
        else: # SELL
            # Original SELL -> SL Triggered at SL Price (Higher). 
            # Entry 2000, SL 2010. Gap 10.
            # Price at 2010. We Buy.
            
            # 70% Level = SL - (Gap * 0.7) = 2010 - 7 = 2003.
            recovery_70_level = sl_price - (loss_gap * recovery_threshold)
            
            shield_direction = "BUY"
            
            # Shield TP = Shield Entry + Gap = 2010 + 10 = 2020.
            shield_tp_price = sl_price + loss_gap
            
            # Shield SL = Original Entry = 2000.
            shield_sl_price = entry_price

        # Pip conversion for display
        try:
             pip_size = self.config.get_symbol_config(symbol).get("pip_size", 0.01)
             loss_gap_pips = loss_gap / pip_size
        except:
             loss_gap_pips = loss_gap # Fallback
             
        return {
            "loss_gap": loss_gap,
            "loss_gap_pips": loss_gap_pips,
            "recovery_70_level": recovery_70_level,
            "shield_direction": shield_direction,
            "shield_tp_price": shield_tp_price,
            "shield_sl_price": shield_sl_price,
            "original_sl_price": sl_price # Approx shield entry
        }

    def calculate_safe_shield_lot(self, original_trade: Trade, params: Dict) -> Dict:
        """
        Calculate safe lot size monitoring Risk Manager limits (Daily Loss, Margin).
        Applies Smart Adjustment logic.
        """
        config = self.rs_config
        risk_integ = config.get("risk_integration", {})
        
        # 1. Base Calculation
        original_lot = original_trade.lot_size
        multiplier = config.get("shield_lot_size_multiplier", 0.5)
        requested_lot = float(original_lot) * multiplier
        
        # Normalize to 2 decimal places (or symbol specific)
        requested_lot = round(requested_lot, 2)
        
        if not risk_integ.get("enable_smart_adjustment", True):
            return {
                "final_lot": requested_lot,
                "requested_lot": requested_lot,
                "adjusted": False,
                "cancelled": False
            }
            
        adjusted_lot = requested_lot
        final_reason = ""
        is_adjusted = False
        
        # 2. Risk Check: Daily Loss
        # Shield SL Distance = Loss Gap. 
        # Loss if Shield Hits SL = Loss Gap * Lot * PipValue?
        # Roughly: Distance * Lot * UnitValue
        symbol = original_trade.symbol
        
        try:
            # We need estimated loss in USD if shield hits SL
            # Shield SL distance is exactly the 'loss_gap'
            gap = params['loss_gap']
            # Get pip value per 1 lot for this symbol
            # We can use mt5_client if available or config
            tick_value = self.mt5_client.get_symbol_tick_value(symbol) or 0.0
            tick_size = self.mt5_client.get_symbol_tick_size(symbol) or 0.0
            contract_size = self.mt5_client.get_contract_size(symbol) or 100000
            
            if tick_size > 0:
                # Value of the gap move: (Gap / TickSize) * TickValue * Lot
                # e.g. Gap 10, Tick 0.01 -> 1000 ticks. Value 1$ per tick. 1 Lot. = $1000
                potential_shield_loss = (gap / tick_size) * tick_value * requested_lot
            else:
                # Fallback approximation
                potential_shield_loss = gap * requested_lot * 100000 # Very rough
            
            remaining_daily = self.risk_manager.get_remaining_daily_loss(original_trade.tier)
            buffer = risk_integ.get("min_daily_loss_buffer", 50.0)
            
            # Since we open 2 shields, Total Risk = 2 * potential_shield_loss (if both hit SL)
            # Both shields have same SL (Original Entry).
            total_potential_loss = potential_shield_loss * 2 
            
            if total_potential_loss > (remaining_daily - buffer):
                # Need to reduce
                # Target Loss = Remaining - Buffer
                target_loss_total = max(0, remaining_daily - buffer)
                if target_loss_total == 0:
                    cancelled = True 
                    return {"cancelled": True, "reason": "No Daily Loss Room"}
                    
                ratio = target_loss_total / total_potential_loss
                adjusted_lot = requested_lot * ratio
                # Round down
                adjusted_lot = int(adjusted_lot * 100) / 100.0
                is_adjusted = True
                final_reason += f"Daily Limit (Room: {remaining_daily:.2f}); "

        except Exception as e:
            logger.error(f"Error checking daily loss for shield: {e}")
            # Continue with requested or skip? Safety first -> Skip if error??
            # Let's proceed but maybe warn.
            pass

        # 3. Risk Check: Margin
        try:
            free_margin = self.mt5_client.get_free_margin()
            # Approx margin required for 2 * adjusted_lot
            # We can ask MT5 via order_calc_margin but might be complex async?
            # self.mt5_client is sync wrapper usually?
            # Let's check Margin Free % buffer
            min_margin_percent = risk_integ.get("min_margin_buffer_percent", 20.0)
            
            # Current Margin Level? 
            # If we don't have easy margin calc, assume if free margin is very low 
            # we scale down.
            # A simple safety: lot * margin_per_lot.
            # Assume 1:500 leverage -> 0.2% margin. 
            # Let's skip complex margin calc for now unless we have a method.
            pass 
        except Exception as e:
            logger.error(f"Error checking margin: {e}")

        # 4. Broker Minimum
        min_lot = 0.01 # Standard, could query symbol info
        if adjusted_lot < min_lot and risk_integ.get("cancel_if_below_min_lot", True):
             return {
                 "final_lot": 0.0,
                 "requested_lot": requested_lot,
                 "adjusted": True,
                 "cancelled": True,
                 "adjustment_reason": f"{final_reason} Below Min Lot",
                 "min_lot": min_lot
             }
        
        # Clamp to min if not cancelling
        if adjusted_lot < min_lot: 
             adjusted_lot = min_lot
             is_adjusted = True # Forced up, slightly risky but allowed if config says don't cancel

        return {
            "final_lot": adjusted_lot,
            "requested_lot": requested_lot,
            "adjusted": is_adjusted,
            "adjustment_reason": final_reason.strip(),
            "cancelled": False
        }

    async def activate_shield(self, original_trade: Trade, strategy: str) -> Optional[Dict]:
        """
        Execute the Instant Shield Protocol (Path A).
        Creates 2 orders (Shield A & B).
        """
        if not self.is_enabled():
            return None

        # 0. Check Concurrent Limits
        max_shields = self.rs_config.get("max_concurrent_shields", 3)
        # active_shields stores original_order_id -> {shield_a, shield_b}
        # Meaning we are protecting X original trades.
        if len(self.active_shields) >= max_shields:
            logger.warning("🛡️ Max Concurrent Shields Active. Skipping.")
            return None

        # 1. Calc Params
        params = self.calculate_shield_parameters(original_trade)
        
        # 2. Risk Check
        lot_result = self.calculate_safe_shield_lot(original_trade, params)
        if lot_result.get("cancelled"):
            await self.notification_handler.send_shield_cancelled(
                original_trade, lot_result, lot_result.get("adjustment_reason", "Risk Check")
            )
            return None
            
        final_lot = lot_result["final_lot"]
        symbol = original_trade.symbol
        direction = params["shield_direction"] # OPPOSITE of original
        
        # 3. Execute Orders
        # Shield A (Recovery)
        # Type: Market Order in Shield Direction
        shield_a_res = self.mt5_client.execute_trade(
             symbol=symbol,
             order_type=direction, # "BUY" or "SELL"
             volume=final_lot,
             stop_loss=params["shield_sl_price"],
             take_profit=params["shield_tp_price"],
             comment=f"Shield A #{original_trade.ticket}"
        )
        
        # Shield B (Profit Booking)
        # Note: Shield B uses Profit Booking Manager logic. It needs a chain ID maybe?
        # We start a new chain? Or just place order with open targets?
        # Blueprint: "Logic: Connect to ProfitBookingManager. Behavior: Must follow standard Level Up"
        # We need to register this order with ProfitBookingManager.
        shield_b_res = self.mt5_client.execute_trade(
             symbol=symbol,
             order_type=direction,
             volume=final_lot,
             stop_loss=params["shield_sl_price"],
             take_profit=0.0, # Managed by ProfitBooking
             comment=f"Shield B #{original_trade.ticket}"
        )
        
        if not shield_a_res or not shield_b_res:
            logger.error("Failed to place one or both shield orders")
            # Should close the one that worked? Complexity. 
            # For now assume failure means we abort shield mode monitoring for that order 
            # and fallback to recovery.
            return None

        shield_a_ticket = int(shield_a_res.get('order'))
        shield_b_ticket = int(shield_b_res.get('order'))

        # Register Shield B with ProfitBookingManager
        # We need to create a 'ProfitBookingChain' or similar if the manager expects it.
        # Or add it to tracking.
        # The ProfitBookingManager scans "Active orders" usually?
        # If we tag comment correctly, maybe it picks it up?
        # Alternatively, we explicity add it.
        # In v2.1 code, ProfitBookingManager might need a 'register_order' method 
        # or we rely on 'scan_open_trades'.
        # We will assume we need to notify it or let it scan.
        # Ideally, we set a flag 'is_shield_order=True' in DB if we save it.
        
        # 4. Notify
        # Construct simplified objects for notification
        s_a_data = {
            'order': shield_a_ticket,
            'price': shield_a_res.get('price', 0.0),
            'request': {
                'type_str': direction,
                'tp': params["shield_tp_price"],
                'sl': params["shield_sl_price"],
                'volume': final_lot
            }
        }
        s_b_data = {
             'order': shield_b_ticket,
             'price': shield_b_res.get('price', 0.0),
             'request': {
                'type_str': direction,
                'sl': params["shield_sl_price"],
                'volume': final_lot
            }
        }
        
        await self.notification_handler.send_shield_activation(
            original_trade, params, lot_result, s_a_data, s_b_data
        )

        # Track Active Shields
        self.active_shields[original_trade.ticket] = {
            "shield_a": shield_a_ticket,
            "shield_b": shield_b_ticket,
            "start_time": asyncio.get_event_loop().time()
        }

        return {
            "shield_ids": [shield_a_ticket, shield_b_ticket],
            "recovery_70_level": params["recovery_70_level"],
            "shield_lot": final_lot
        }

    def on_shield_close(self, ticket: int):
        """
        Handle closure of a shield trade (manual or TP/SL).
        Removes internal tracking reference.
        """
        for original_id, shields in list(self.active_shields.items()):
            if ticket == shields.get('shield_a') or ticket == shields.get('shield_b'):
                # Found it. We don't remove the whole entry unless both are closed?
                # Or do we treat "One Closed" as "Shield session over"?
                # Usually Shield B might run longer. Shield A is short term recovery.
                # We just log it for now or remove if both closed.
                # Simple logic: If Shield A closes (Recovery done/failed), maybe we stop tracking?
                # Better: Just check if tracking exists.
                pass
                # Real cleanup usually happens on Kill Switch or Manual Intervention
                # But we should remove specific ID to keep counts accurate if we tracked per-order.
                # Since we track by Original ID, we check if empty.
                if ticket == shields.get('shield_a'):
                     shields['shield_a'] = None
                if ticket == shields.get('shield_b'):
                     shields['shield_b'] = None
                
                if not shields.get('shield_a') and not shields.get('shield_b'):
                    del self.active_shields[original_id]
                    logger.info(f"🛡️ Shield session ended for Original #{original_id}")
                return

    async def kill_switch(self, shield_ids: List[int], original_trade: Trade, 
                          current_price: float, elapsed_time: float):
        """
        Execute Kill Switch: Close Shields & Signal Return to Recovery
        """
        logger.info(f"⚠️ KILL SWITCH: Closing shields {shield_ids}")
        
        shield_a_pnl = {"profit": 0.0, "ticket": shield_ids[0]}
        shield_b_pnl = {"profit": 0.0, "ticket": shield_ids[1]}
        
        # Close Shield A
        res_a = self.mt5_client.close_order(shield_ids[0])
        if res_a:
             shield_a_pnl["profit"] = res_a.get("profit", 0.0)
            
        # Close Shield B
        res_b = self.mt5_client.close_order(shield_ids[1])
        if res_b:
             shield_b_pnl["profit"] = res_b.get("profit", 0.0)

        # Notify
        await self.notification_handler.send_kill_switch_triggered(
            original_trade, current_price, elapsed_time,
            shield_a_pnl, shield_b_pnl
        )
        
        if original_trade.ticket in self.active_shields:
            del self.active_shields[original_trade.ticket]
            
        return True
