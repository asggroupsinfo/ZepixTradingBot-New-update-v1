"""
Dynamic Parameter Handlers - Handles dynamic parameter selection
(e.g., chain_id from active chains, symbols from config)
"""
from typing import List, Dict, Any, Optional

class DynamicHandlers:
    """Handles dynamic parameter selection for commands"""
    
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
    
    def get_active_chain_ids(self) -> List[Dict[str, Any]]:
        """
        Get active profit booking chain IDs with details
        Returns: List of dicts with chain_id, symbol, pnl, level
        """
        try:
            if not self.bot.trading_engine:
                return []
            
            profit_manager = getattr(self.bot.trading_engine, 'profit_booking_manager', None)
            if not profit_manager:
                return []
            
            # Get all active chains
            chains = profit_manager.get_all_chains()
            if not chains:
                return []
            
            chain_list = []
            for chain_id, chain_obj in chains.items():
                # chain_obj is ProfitBookingChain object
                if hasattr(chain_obj, 'status') and chain_obj.status == "ACTIVE":
                    # Get current PnL if available
                    current_pnl = getattr(chain_obj, 'total_profit', 0.0)
                    symbol = getattr(chain_obj, 'symbol', 'N/A')
                    level = getattr(chain_obj, 'current_level', 0)
                    
                    chain_list.append({
                        "chain_id": chain_id,
                        "symbol": symbol,
                        "pnl": current_pnl,
                        "level": level,
                        "display": f"{chain_id[:12]}... | {symbol} | L{level} | ${current_pnl:.2f}"
                    })
            
            return chain_list
            
        except Exception as e:
            print(f"Error getting active chains: {e}")
            return []
    
    def get_available_symbols(self) -> List[str]:
        """Get available symbols from config"""
        try:
            symbol_config = self.bot.config.get('symbol_config', {})
            return list(symbol_config.keys())
        except Exception:
            return []
    
    def get_risk_tiers(self) -> List[str]:
        """Get configured risk tiers"""
        try:
            risk_tiers = self.bot.config.get('risk_tiers', {})
            return list(risk_tiers.keys())
        except Exception:
            return []
    
    def format_chain_selection(self, chains: List[Dict[str, Any]]) -> tuple:
        """
        Format chain list for menu display
        Returns: (text, keyboard)
        """
        if not chains:
            text = (
                "📭 *No Active Chains*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "No active profit booking chains found."
            )
            keyboard = []
            keyboard.append([{"text": "🔙 Back", "callback_data": "nav_back"}])
            return text, {"inline_keyboard": keyboard}
        
        text = (
            "🔗 *Select Profit Chain*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Active profit booking chains:\n\n"
        )
        
        keyboard = []
        for chain in chains:
            keyboard.append([{
                "text": chain["display"],
                "callback_data": f"param_chain_id_stop_profit_chain_{chain['chain_id']}"
            }])
        
        keyboard.append([])
        keyboard.append([{"text": "🔙 Back", "callback_data": "nav_back"}])
        
        return text, {"inline_keyboard": keyboard}
    
    def format_multi_target_input(self, command_name: str, current_values: List[float] = None) -> tuple:
        """
        Format multi-target input screen with BUTTON PRESETS (NO TYPING!)
        Returns: (text, keyboard)
        """
        if current_values is None:
            current_values = []
        
        if command_name == "set_profit_targets":
            title = "💰 Set Profit Targets"
            description = "Select a profit target preset:"
            
            # Profit target presets
            presets = [
                {"label": "Conservative ($7-$112)", "values": [7, 14, 28, 56, 112], "callback": "multi_profit_conservative"},
                {"label": "Balanced ($10-$160)", "values": [10, 20, 40, 80, 160], "callback": "multi_profit_balanced"},
                {"label": "Aggressive ($15-$240)", "values": [15, 30, 60, 120, 240], "callback": "multi_profit_aggressive"},
                {"label": "High Risk ($20-$320)", "values": [20, 40, 80, 160, 320], "callback": "multi_profit_highrisk"},
            ]
            
        elif command_name == "set_chain_multipliers":
            title = "📊 Set Chain Multipliers"
            description = "Select an order multiplier preset:"
            
            # Chain multiplier presets
            presets = [
                {"label": "Standard (1, 2, 4, 8, 16)", "values": [1, 2, 4, 8, 16], "callback": "multi_chain_standard"},
                {"label": "Conservative (1, 1.5, 2, 3, 4)", "values": [1, 1.5, 2, 3, 4], "callback": "multi_chain_conservative"},
                {"label": "Aggressive (1, 3, 6, 12, 24)", "values": [1, 3, 6, 12, 24], "callback": "multi_chain_aggressive"},
                {"label": "Linear (1, 2, 3, 4, 5)", "values": [1, 2, 3, 4, 5], "callback": "multi_chain_linear"},
            ]
        else:
            title = "Enter Values"
            description = "Select a preset:"
            presets = []
        
        text = (
            f"{title}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{description}\n\n"
        )
        
        if current_values:
            text += f"📊 *Current values:* `{', '.join(str(v) for v in current_values)}`\n\n"
        
        text += "✅ *Zero-typing interface* - Just click a preset!\n"
        
        # Build keyboard with presets
        keyboard = []
        for preset in presets:
            values_str = ', '.join(str(v) for v in preset['values'])
            keyboard.append([{
                "text": f"{preset['label']}: {values_str}",
                "callback_data": preset['callback']
            }])
        
        # Add back button
        keyboard.append([{"text": "🔙 Back", "callback_data": "nav_back"}])
        
        return text, {"inline_keyboard": keyboard}

