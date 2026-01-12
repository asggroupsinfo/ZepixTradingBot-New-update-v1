import json
import os
import logging
from datetime import datetime, date
from typing import Dict, Any, List
from src.config import Config

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, config: Config):
        self.config = config
        self.stats_file = "data/stats.json"
        self.daily_loss = 0.0
        self.lifetime_loss = 0.0
        self.daily_profit = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.open_trades = []
        self.mt5_client = None
        self.load_stats()
        
    def load_stats(self):
        """Load statistics from file with error handling"""
        try:
            if os.path.exists(self.stats_file) and os.path.getsize(self.stats_file) > 0:
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                    
                if stats.get("date") != str(date.today()):
                    self.daily_loss = 0.0
                    self.daily_profit = 0.0
                else:
                    self.daily_loss = stats.get("daily_loss", 0.0)
                    self.daily_profit = stats.get("daily_profit", 0.0)
                    
                self.lifetime_loss = stats.get("lifetime_loss", 0.0)
                self.total_trades = stats.get("total_trades", 0)
                self.winning_trades = stats.get("winning_trades", 0)
            else:
                # Initialize with default values if file doesn't exist or is empty
                self.reset_daily_stats()
                
        except (json.JSONDecodeError, Exception) as e:
            print(f"WARNING: Stats file corrupted, resetting: {str(e)}")
            self.reset_daily_stats()
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_loss = 0.0
        self.daily_profit = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.save_stats()
    
    def reset_lifetime_loss(self):
        """Reset lifetime loss counter"""
        self.lifetime_loss = 0.0
        self.save_stats()
    
    def reset_daily_loss(self):
        """Reset daily loss and profit counters (keeps lifetime loss)"""
        logger.info(f"[RESET_DAILY_LOSS] Clearing daily stats (Current: Loss=${self.daily_loss:.2f}, Profit=${self.daily_profit:.2f})")
        
        # Explicitly set to zero
        self.daily_loss = 0.0
        self.daily_profit = 0.0
        
        # Save with verification
        save_success = self.save_stats()
        
        if save_success:
            logger.info(f"[RESET_DAILY_LOSS] ✅ Daily loss cleared successfully and verified in {self.stats_file}")
            return True
        else:
            logger.error(f"[RESET_DAILY_LOSS] ❌ CRITICAL: Failed to save cleared stats to file!")
            return False
    
    def save_stats(self):
        """Save statistics to file with verification and retry"""
        stats = {
            "date": str(date.today()),
            "daily_loss": self.daily_loss,
            "daily_profit": self.daily_profit,
            "lifetime_loss": self.lifetime_loss,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades
        }
        
        # Try to save with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
                
                # Write stats file
                with open(self.stats_file, 'w') as f:
                    json.dump(stats, f, indent=4)
                
                # CRITICAL FIX: Verify file was written correctly
                with open(self.stats_file, 'r') as f:
                    verify_data = json.load(f)
                
                # Check if daily_loss matches what we tried to save
                if abs(verify_data.get("daily_loss", -999) - self.daily_loss) < 0.01:
                    logger.info(f"✅ Stats saved successfully: Daily Loss=${self.daily_loss:.2f}, Lifetime=${self.lifetime_loss:.2f}")
                    return True
                else:
                    raise ValueError(f"Verification failed: Expected daily_loss={self.daily_loss}, got {verify_data.get('daily_loss')}")
                    
            except Exception as e:
                error_msg = f"ERROR: Stats save attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                print(error_msg)
                logger.error(error_msg)
                
                if attempt < max_retries - 1:
                    # Wait before retry
                    import time
                    time.sleep(1)
                else:
                    # Final attempt failed
                    logger.error(f"CRITICAL: Failed to save stats after {max_retries} attempts. File: {self.stats_file}")
                    return False
        
        return False
    
    def get_fixed_lot_size(self, balance: float) -> float:
        """Get fixed lot size based on account balance or active tier"""
        
        # 1. Manual overrides (Highest Priority)
        manual_overrides = self.config.get("manual_lot_overrides", {})
        
        # Check if there's an active tier set
        active_tier = self.config.get("default_risk_tier")
        
        # If active tier exists, check for override on that tier specifically
        if active_tier and str(active_tier) in manual_overrides:
            return manual_overrides[str(active_tier)]
            
        # Also check based on raw balance (legacy support)
        if str(int(balance)) in manual_overrides:
            return manual_overrides[str(int(balance))]
        
        # 2. Active Tier Logic (High Priority)
        # If user explicitly selected a tier, use that tier's lot size regardless of balance
        if active_tier:
            fixed_lots = self.config["fixed_lot_sizes"]
            if str(active_tier) in fixed_lots:
                return fixed_lots[str(active_tier)]
        
        # 3. Balance-based Logic (Fallback)
        # Only used if no active tier is selected (shouldn't happen normally)
        fixed_lots = self.config["fixed_lot_sizes"]
        
        for tier_balance in sorted(fixed_lots.keys(), key=int, reverse=True):
            if balance >= int(tier_balance):
                return fixed_lots[tier_balance]
        
        return 0.05  # Default minimum
    
    def set_manual_lot_size(self, balance_tier: int, lot_size: float):
        """Manually override lot size for a balance tier"""
        
        if "manual_lot_overrides" not in self.config.config:
            self.config.config["manual_lot_overrides"] = {}
        
        self.config.config["manual_lot_overrides"][str(balance_tier)] = lot_size
        self.config.save_config()
    
    def get_lot_size_for_logic(self, balance: float, logic: str = None) -> float:
        """
        Get lot size with timeframe-specific multiplier adjustment
        """
        # Get base lot size
        base_lot = self.get_fixed_lot_size(balance)
        
        # Apply timeframe multiplier
        try:
            timeframe_config = self.config.get("timeframe_specific_config", {})
            if timeframe_config.get("enabled", False) and logic:
                logic_config = timeframe_config.get(logic)
                if logic_config:
                    multiplier = logic_config.get("lot_multiplier", 1.0)
                    adjusted_lot = base_lot * multiplier
                    
                    # Sanity Check: Min lot 0.01
                    adjusted_lot = max(0.01, round(adjusted_lot, 3))
                    
                    # print(f"Timeframe Config: {logic} Lot x{multiplier} -> {adjusted_lot} lots")
                    return adjusted_lot
        except Exception as e:
            print(f"Error applying timeframe lot multiplier: {e}")
                
        return base_lot
    
    def get_risk_tier(self, balance: float) -> str:
        """Get risk tier based on account balance"""
        for tier in ["100000", "50000", "25000", "10000", "5000"]:
            if balance >= int(tier):
                return tier
        return "5000"
    
    def can_trade(self) -> bool:
        """Check if trading is allowed based on risk limits"""
        if not self.mt5_client:
            return False
            
        account_balance = self.mt5_client.get_account_balance()
        risk_tier = self.get_risk_tier(account_balance)
        
        if risk_tier not in self.config["risk_tiers"]:
            return False
            
        risk_params = self.config["risk_tiers"][risk_tier]
        
        # Check closed loss limits
        if self.lifetime_loss >= risk_params["max_total_loss"]:
            print(f"BLOCKED: Lifetime loss limit reached: ${self.lifetime_loss}")
            return False
            
        if self.daily_loss >= risk_params["daily_loss_limit"]:
            print(f"BLOCKED: Daily loss limit reached: ${self.daily_loss}")
            return False
        
        # Note: Dual order validation is done separately in validate_dual_orders()
        # This method checks basic trading permission
        
        return True
    
    def update_pnl(self, pnl: float):
        """Update PnL and risk statistics"""
        self.total_trades += 1
        
        if pnl > 0:
            self.daily_profit += pnl
            self.winning_trades += 1
        else:
            self.daily_loss += abs(pnl)
            self.lifetime_loss += abs(pnl)
        
        self.save_stats()
    
    def add_open_trade(self, trade):
        """Add trade to open trades list"""
        self.open_trades.append(trade)
    
    def remove_open_trade(self, trade):
        """Remove trade from open trades list"""
        self.open_trades = [t for t in self.open_trades 
                          if getattr(t, 'trade_id', None) != getattr(trade, 'trade_id', None)]
    
    def set_mt5_client(self, mt5_client):
        """Set MT5 client for balance checking"""
        self.mt5_client = mt5_client
    
    def validate_dual_orders(self, symbol: str, lot_size: float, 
                            account_balance: float) -> Dict[str, Any]:
        """
        Validate if account can handle 2x lot size risk for dual orders
        Returns: {"valid": bool, "reason": str}
        """
        # Check if dual orders enabled
        dual_config = self.config.get("dual_order_config", {})
        if not dual_config.get("enabled", True):
            return {"valid": True, "reason": "Dual orders disabled"}
        
        # Get risk tier
        risk_tier = self.get_risk_tier(account_balance)
        
        if risk_tier not in self.config["risk_tiers"]:
            return {"valid": False, "reason": f"Invalid risk tier: {risk_tier}"}
        
        risk_params = self.config["risk_tiers"][risk_tier]
        
        # Calculate expected loss for 2x lot size
        # Get symbol config
        symbol_config = self.config["symbol_config"][symbol]
        volatility = symbol_config["volatility"]
        
        # Get SL pips (approximate - actual calculation done in pip_calculator)
        # For validation, we use a conservative estimate
        # Get pip value (support both keys)
        pip_value_std = symbol_config.get("pip_value_per_std_lot")
        if pip_value_std is None:
             pip_value_std = symbol_config.get("pip_value", 10.0)
             
        pip_value = pip_value_std * (lot_size * 2)  # 2x lot size
        
        # Estimate SL pips (RELAXED ESTIMATES to avoid blocking valid trades)
        # The real validation happens later with actual SL
        sl_estimates = {"LOW": 30, "MEDIUM": 45, "HIGH": 60}
        estimated_sl_pips = sl_estimates.get(volatility, 60)
        
        
        # Calculate expected loss for 2 orders
        expected_loss = estimated_sl_pips * pip_value

        # DEBUG PRINTS FOR USER
        print(f"\n[DEBUG RISK] Validating {symbol} Dual Orders")
        print(f"[DEBUG RISK] Lot Size: {lot_size}")
        print(f"[DEBUG RISK] Volatility: {volatility}")
        print(f"[DEBUG RISK] Pip Value Std: {pip_value_std}")
        print(f"[DEBUG RISK] Estimated SL Pips: {estimated_sl_pips}")
        print(f"[DEBUG RISK] Max Daily Limit: {risk_params['daily_loss_limit']}")
        print(f"[DEBUG RISK] Calculated Expected Loss: {expected_loss}")
        
        # Check daily loss cap
        if self.daily_loss + expected_loss > risk_params["daily_loss_limit"]:
            return {
                "valid": False,
                "reason": f"Daily loss cap would be exceeded: ${self.daily_loss + expected_loss:.2f} > ${risk_params['daily_loss_limit']}"
            }
        
        # Check lifetime loss cap
        if self.lifetime_loss + expected_loss > risk_params["max_total_loss"]:
            return {
                "valid": False,
                "reason": f"Lifetime loss cap would be exceeded: ${self.lifetime_loss + expected_loss:.2f} > ${risk_params['max_total_loss']}"
            }
        
        return {"valid": True, "reason": "Dual order risk validation passed"}
    
    def calculate_profit_booking_risk(self, chain_level: int, base_lot: float, 
                                     symbol: str, account_balance: float) -> Dict[str, Any]:
        """
        Calculate risk for profit booking chain at specific level
        Returns: {"total_risk": float, "order_count": int, "total_lot_size": float}
        """
        # Get profit booking config
        profit_config = self.config.get("profit_booking_config", {})
        multipliers = profit_config.get("multipliers", [1, 2, 4, 8, 16])
        sl_reductions = profit_config.get("sl_reductions", [0, 10, 25, 40, 50])
        
        if chain_level >= len(multipliers):
            return {"total_risk": 0.0, "order_count": 0, "total_lot_size": 0.0}
        
        # Get order count for this level
        order_count = multipliers[chain_level]
        total_lot_size = base_lot * order_count
        
        # Get SL reduction for this level
        sl_reduction = sl_reductions[chain_level] if chain_level < len(sl_reductions) else 0
        sl_adjustment = 1.0 - (sl_reduction / 100.0)
        
        # Get symbol config
        symbol_config = self.config["symbol_config"][symbol]
        pip_value_std = symbol_config.get("pip_value_per_std_lot", 10.0)
        
        # Estimate SL pips (conservative estimate)
        volatility = symbol_config["volatility"]
        sl_estimates = {"LOW": 50, "MEDIUM": 75, "HIGH": 100}
        estimated_sl_pips = sl_estimates.get(volatility, 75) * sl_adjustment
        
        # Calculate total risk
        pip_value = pip_value_std * total_lot_size
        total_risk = estimated_sl_pips * pip_value
        
        return {
            "total_risk": total_risk,
            "order_count": order_count,
            "total_lot_size": total_lot_size,
            "sl_reduction_percent": sl_reduction
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        if not self.mt5_client:
            return {}
            
        account_balance = self.mt5_client.get_account_balance()
        risk_tier = self.get_risk_tier(account_balance)
        lot_size = self.get_fixed_lot_size(account_balance)
        
        if risk_tier not in self.config["risk_tiers"]:
            return {}
            
        risk_params = self.config["risk_tiers"][risk_tier]
        
        return {
            "daily_loss": self.daily_loss,
            "daily_profit": self.daily_profit,
            "lifetime_loss": self.lifetime_loss,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "win_rate": (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            "current_risk_tier": risk_tier,
            "risk_parameters": risk_params,
            "current_lot_size": lot_size,
            "account_balance": account_balance
        }
    
    def get_todays_performance(self, db) -> Dict[str, Any]:
        """
        Calculate today's profit, loss, and net PnL from database
        Returns: {"profit": float, "loss": float, "net": float, "trade_count": int}
        """
        try:
            today = date.today()
            
            # Query database for trades closed today
            cursor = db.conn.cursor()
            cursor.execute('''
                SELECT pnl FROM trades 
                WHERE DATE(close_time) = DATE(?) AND status = 'closed'
            ''', (today.isoformat(),))
            
            today_trades = cursor.fetchall()
            
            # Calculate profit and loss
            profit = sum(trade[0] for trade in today_trades if trade[0] and trade[0] > 0)
            loss = sum(trade[0] for trade in today_trades if trade[0] and trade[0] < 0)
            net = profit + loss  # loss is negative, so this gives net
            
            return {
                'profit': profit,
                'loss': loss,
                'net': net,
                'trade_count': len(today_trades)
            }
            
        except Exception as e:
            logger.error(f"Error calculating today's performance: {e}")
            return {'profit': 0.0, 'loss': 0.0, 'net': 0.0, 'trade_count': 0}
    
    def get_live_open_trades_pnl(self, trading_engine, mt5_client, pip_calculator) -> Dict[str, Any]:
        """
        Calculate real-time PnL for all open trades
        Returns: {"total_live_pnl": float, "trade_details": List[Dict]}
        """
        try:
            open_trades = trading_engine.get_open_trades()
            total_live_pnl = 0.0
            trade_details = []
            
            for trade in open_trades:
                try:
                    # Get current price from MT5
                    current_price = mt5_client.get_current_price(trade.symbol)
                    if current_price is None or current_price == 0:
                        logger.warning(f"Could not get current price for {trade.symbol}")
                        continue
                    
                    # Get pip size and pip value
                    pip_size = pip_calculator.get_pip_size(trade.symbol)
                    pip_value = pip_calculator.get_pip_value(trade.symbol, trade.lot_size)
                    
                    # Calculate pips moved
                    if trade.direction.lower() == 'buy':
                        pips = (current_price - trade.entry) / pip_size
                    else:  # sell
                        pips = (trade.entry - current_price) / pip_size
                    
                    # Calculate live PnL
                    live_pnl = pips * pip_value
                    total_live_pnl += live_pnl
                    
                    trade_details.append({
                        'symbol': trade.symbol,
                        'direction': trade.direction.upper(),
                        'live_pnl': live_pnl,
                        'entry_price': trade.entry,
                        'current_price': current_price,
                        'sl_price': trade.sl,
                        'tp_price': trade.tp,
                        'lot_size': trade.lot_size,
                        'trade_id': getattr(trade, 'trade_id', None)
                    })
                    
                except Exception as e:
                    logger.error(f"Error calculating PnL for trade {getattr(trade, 'trade_id', 'unknown')}: {e}")
                    continue
            
            return {
                'total_live_pnl': total_live_pnl,
                'trade_details': trade_details
            }
            
        except Exception as e:
            logger.error(f"Error calculating live open trades PnL: {e}")
            return {'total_live_pnl': 0.0, 'trade_details': []}
    
    @staticmethod
    def format_pnl_value(pnl: float) -> str:
        """
        Format PnL with colors and symbols
        Returns formatted string: "🟢 +$X.XX" or "🔴 -$X.XX" or "⚪ $0.00"
        """
        if pnl > 0:
            return f"🟢 +${abs(pnl):.2f}"
        elif pnl < 0:
            return f"🔴 -${abs(pnl):.2f}"
        else:
            return f"⚪ ${pnl:.2f}"
    
    def get_win_rate(self) -> float:
        """
        Calculate win rate percentage
        Returns: float (0-100)
        """
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100.0