from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging

class ProfitBookingReEntryManager:
    """
    Manages re-entry logic specifically for Profit Booking (Order B) chains.
    Ensures that if a profit order hits SL, it is not abandoned but recovered.
    """
    
    def __init__(self, config, profit_booking_manager, mt5_client, trend_analyzer):
        self.config = config
        self.profit_booking_manager = profit_booking_manager
        self.mt5_client = mt5_client
        self.trend_analyzer = trend_analyzer
        self.logger = logging.getLogger(__name__)
        
        # Track pending recoveries
        self.pending_recoveries = {} # chain_id -> {sl_price, time, level, ...}
        
    def register_sl_hit(self, chain_id: str, symbol: str, direction: str, level: int, sl_price: float, loss_amount: float):
        """Register that a profit order hit SL and needs recovery"""
        
        # Check if feature is enabled
        if not self.config["re_entry_config"].get("autonomous_config", {}).get("profit_sl_hunt_enabled", True):
            return
            
        self.logger.info(f"💎 Profit Order SL Hit registered: {symbol} Level {level} @ {sl_price}")
        
        # Update pending recoveries with tracking
        current_attempts = self.pending_recoveries.get(chain_id, {}).get("attempts", 0)
        
        if current_attempts >= 1:
            self.logger.info(f"🛑 Profit Chain {chain_id} Hard Stopped (Max Recovery Exceeded)")
            return

        self.pending_recoveries[chain_id] = {
            "symbol": symbol,
            "direction": direction,
            "level": level,
            "sl_price": sl_price,
            "loss_amount": loss_amount,
            "time": datetime.now(),
            "status": "PENDING",
            "attempts": current_attempts + 1
        }
        self.logger.info(f"🔄 Profit Chain {chain_id} Entered Recovery Mode (Attempt {current_attempts + 1}/1)")
        
    def check_recoveries(self) -> List[Dict[str, Any]]:
        """Check if any pending recoveries are ready for re-entry"""
        ready_ops = []
        
        for chain_id, data in list(self.pending_recoveries.items()):
            try:
                symbol = data["symbol"]
                current_price = self.mt5_client.get_current_price(symbol)
                
                if not current_price: continue
                
                # Check Trend Alignment (Safety)
                trend = self.trend_analyzer.get_current_trend(symbol)
                if not self.trend_analyzer.is_aligned(data["direction"], trend):
                    continue
                    
                # Check Price Recovery
                # If BUY, price must be > SL Price (recovering up)
                # If SELL, price must be < SL Price (recovering down)
                is_recovered = False
                if data["direction"] == "buy":
                    is_recovered = current_price > data["sl_price"]
                else:
                    is_recovered = current_price < data["sl_price"]
                    
                if is_recovered:
                    ready_ops.append({
                        "type": "profit_recovery",
                        "chain_id": chain_id,
                        "symbol": symbol,
                        "direction": data["direction"],
                        "level": data["level"],
                        "current_price": current_price,
                        "data": data
                    })
                    
            except Exception as e:
                self.logger.error(f"Error checking profit recovery for {chain_id}: {e}")
                
        return ready_ops
        
    def complete_recovery(self, chain_id: str):
        """Mark recovery as completed"""
        if chain_id in self.pending_recoveries:
            del self.pending_recoveries[chain_id]
