import logging
from typing import Dict, Any, Optional
from src.models import Trade

logger = logging.getLogger(__name__)

class ReverseShieldNotificationHandler:
    """
    Handles notifications for the Reverse Shield system (v3.0).
    Provides high-fidelity, transparent reporting of all shield actions.
    """
    
    def __init__(self, telegram_bot, config):
        self.telegram_bot = telegram_bot
        self.config = config
        self.enabled = True  # Can be toggled from config if needed
        
        # Load detailed notification preferences
        rs_config = config.get("reverse_shield_config", {})
        self.notify_settings = rs_config.get("notifications", {
            "shield_activated": True,
            "kill_switch_triggered": True,
            "shield_closed": True,
            "shield_profit_booked": True,
            "shield_cancelled": True,
            "show_smart_adjustment_details": True,
            "show_pnl_breakdown": True,
            "show_recovery_projection": True
        })

    async def send_shield_activation(self, original_trade: Trade, params: Dict, 
                                     lot_result: Dict, shield_a: Dict, shield_b: Dict):
        """
        Sends Template A: SHIELD ACTIVATION
        """
        if not self.notify_settings.get("shield_activated", True):
            return

        symbol = original_trade.symbol
        original_ticket = original_trade.ticket
        gap_pips = params.get('loss_gap_pips', 0.0)
        
        msg = f"🛡️ <b>REVERSE SHIELD DEPLOYED</b>\n"
        msg += f"Symbol: <b>{symbol}</b>\n\n"
        
        msg += f"🔴 Trigger: SL Hit on Order #{original_ticket}\n"
        msg += f"📉 Loss Gap: {gap_pips:.1f} pips\n\n"
        
        # Smart Adjustment Section
        if lot_result.get('adjusted', False) and self.notify_settings.get("show_smart_adjustment_details", True):
            req_lot = lot_result.get('requested_lot', 0.0)
            final_lot = lot_result.get('final_lot', 0.0)
            reason = lot_result.get('adjustment_reason', 'Risk Limits')
            msg += f"🔧 <b>SMART ADJUSTMENT:</b> Lot reduced {req_lot} → {final_lot}\n"
            msg += f"Reason: {reason}\n\n"

        # Shield Order A
        msg += f"⚔️ <b>SHIELD ORDER A (Recovery):</b>\n"
        msg += f"• Ticket: #{shield_a.get('order', 0)} ({shield_a.get('request', {}).get('type_str', 'OPPOSITE')})\n"
        msg += f"• Entry: {shield_a.get('price', 0.0)}\n"
        msg += f"• TP: {shield_a.get('request', {}).get('tp', 0.0)} (1:1 Fixed)\n"
        msg += f"• SL: {shield_a.get('request', {}).get('sl', 0.0)} (Break-even)\n"
        msg += f"• Lot: {shield_a.get('request', {}).get('volume', 0.0)}\n\n"
        
        # Shield Order B
        msg += f"⚔️ <b>SHIELD ORDER B (Profit Loop):</b>\n"
        msg += f"• Ticket: #{shield_b.get('order', 0)} ({shield_b.get('request', {}).get('type_str', 'OPPOSITE')})\n"
        msg += f"• Entry: {shield_b.get('price', 0.0)}\n"
        msg += f"• Logic: Connected to Profit Manager 🔄\n"
        msg += f"• SL: {shield_b.get('request', {}).get('sl', 0.0)}\n"
        msg += f"• Lot: {shield_b.get('request', {}).get('volume', 0.0)}\n\n"
        
        # Monitor Info
        rec_70 = params.get('recovery_70_level', 0.0)
        msg += f"🎯 <b>DEEP MONITOR ACTIVE:</b>\n"
        msg += f"Kill Switch Level (70%): {rec_70}\n"
        msg += "(If price hits this, Shields CLOSE & Original Re-opens)"

        await self.telegram_bot.send_message(msg)

    async def send_kill_switch_triggered(self, original_trade: Trade, current_price: float,
                                        elapsed_time: float, shield_a_pnl: Dict, shield_b_pnl: Dict):
        """
        Sends Template B: KILL SWITCH TRIGGERED
        """
        if not self.notify_settings.get("kill_switch_triggered", True):
            return

        symbol = original_trade.symbol
        
        msg = f"⚠️ <b>KILL SWITCH TRIGGERED</b>\n"
        msg += f"Symbol: <b>{symbol}</b>\n\n"
        
        msg += f"📈 Price Reached 70% Recovery Level: {current_price}\n"
        msg += f"Elapsed Time: {elapsed_time:.1f}s\n\n"
        
        # PnL Breakdown
        if self.notify_settings.get("show_pnl_breakdown", True):
            pnl_a = shield_a_pnl.get('profit', 0.0)
            pnl_b = shield_b_pnl.get('profit', 0.0)
            total_pnl = pnl_a + pnl_b
            
            msg += f"1️⃣ <b>Closing Shield Orders...</b>\n"
            msg += f"   • Shield A #{shield_a_pnl.get('ticket')} PnL: ${pnl_a:.2f}\n"
            msg += f"   • Shield B #{shield_b_pnl.get('ticket')} PnL: ${pnl_b:.2f}\n"
            msg += f"   <b>Total Shield PnL: ${total_pnl:.2f}</b>\n\n"
        else:
            msg += f"1️⃣ <b>Closing Shield Orders...</b>\n\n"

        # Restoration Info
        msg += f"2️⃣ <b>RESTORING ORIGINAL TRADE 🔄</b>\n"
        msg += f"   • Executing {original_trade.direction} Recovery Order...\n"
        if self.notify_settings.get("show_recovery_projection", True):
             msg += f"   • Expected to recover original loss"

        await self.telegram_bot.send_message(msg)

    async def send_shield_profit_booked(self, shield_order_ticket: int, symbol: str, 
                                        profit_amount: float, duration: str, 
                                        is_order_a: bool, shield_b_status: str = "Active"):
        """
        Sends Template C: SHIELD PROFIT BOOKED (Order A) or variations
        """
        if not self.notify_settings.get("shield_profit_booked", True):
            return
            
        msg = f"💰 <b>SHIELD PROFIT BOOKED</b>\n"
        msg += f"Symbol: <b>{symbol}</b>\n\n"
        
        if is_order_a:
            msg += f"✅ <b>Shield Order A Target Hit!</b>\n"
            msg += f"Ticket: #{shield_order_ticket}\n"
            msg += f"💵 Recovered Amount: ${profit_amount:.2f}\n"
            msg += f"Recovery Time: {duration}\n\n"
            msg += f"Shield Order B Status: {shield_b_status}\n"
            # In a real scenario we might sum total profit so far, but here we show just this event
        else:
            # Fallback for generic profit
            msg += f"✅ <b>Shield Order Profit!</b>\n"
            msg += f"Ticket: #{shield_order_ticket}\n"
            msg += f"💵 Profit: ${profit_amount:.2f}\n"

        await self.telegram_bot.send_message(msg)

    async def send_shield_level_up(self, symbol: str, chain_id: str, old_level: int, 
                                   new_level: int, closed_ticket: int, close_price: float, 
                                   profit: float, new_order_count: int, new_lot: float, 
                                   profit_target: float, shield_a_status: str):
        """
        Sends Template D: SHIELD LEVEL UP (Order B)
        """
        if not self.notify_settings.get("shield_profit_booked", True):
            return

        msg = f"💰 <b>SHIELD LEVEL UP!</b>\n"
        msg += f"Symbol: <b>{symbol}</b>\n\n"
        
        msg += f"🔄 Shield Order B Profit Booking\n"
        msg += f"Chain: {chain_id}\n"
        msg += f"Level: {old_level} → {new_level}\n\n"
        
        msg += f"Closed:\n"
        msg += f"• Order #{closed_ticket} @ {close_price}\n"
        msg += f"• Profit: ${profit:.2f}\n\n"
        
        msg += f"Opening {new_order_count} New Shield B Orders:\n"
        msg += f"• Level {new_level} | Lot: {new_lot}\n"
        msg += f"• Target: ${profit_target} each\n\n"
        
        msg += f"Shield A Status: {shield_a_status}"
        
        await self.telegram_bot.send_message(msg)

    async def send_shield_cancelled(self, original_trade: Trade, lot_result: Dict, reason: str):
        """
        Sends Template E: SHIELD ACTIVATION CANCELLED
        """
        if not self.notify_settings.get("shield_cancelled", True):
            return

        symbol = original_trade.symbol
        original_ticket = original_trade.ticket
        
        msg = f"🚫 <b>SHIELD ACTIVATION CANCELLED</b>\n"
        msg += f"Symbol: <b>{symbol}</b>\n\n"
        
        msg += f"Trigger: SL Hit on Order #{original_ticket}\n"
        msg += f"Reason: {reason}\n\n"
        
        msg += f"Details:\n"
        msg += f"• Requested Lot: {lot_result.get('requested_lot', 0.0)}\n"
        msg += f"• After Adjustment: {lot_result.get('final_lot', 0.0)}\n"
        if lot_result.get('min_lot'):
             msg += f"• Broker Minimum: {lot_result.get('min_lot')}\n\n"
        else:
             msg += "\n"
        
        msg += f"⚠️ <b>FALLBACK: Using Standard v2.1 Recovery</b>"
        
        await self.telegram_bot.send_message(msg)
