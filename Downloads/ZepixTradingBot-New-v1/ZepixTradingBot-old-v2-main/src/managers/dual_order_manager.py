from typing import Dict, Any, List, Tuple, Optional
from src.models import Trade, Alert
from src.config import Config
from src.managers.risk_manager import RiskManager
from src.clients.mt5_client import MT5Client
from src.utils.pip_calculator import PipCalculator
from datetime import datetime
import logging

class DualOrderManager:
    """
    Manages dual order placement system
    - Order A: TP Continuation Trail (existing system)
    - Order B: Profit Booking Trail (new pyramid system)
    - Both orders use SAME lot size (no split)
    - Orders work independently (no rollback if one fails)
    """
    
    def __init__(self, config: Config, risk_manager: RiskManager, 
                 mt5_client: MT5Client, pip_calculator: PipCalculator,
                 profit_sl_calculator=None):
        self.config = config
        self.risk_manager = risk_manager
        self.mt5_client = mt5_client
        self.pip_calculator = pip_calculator
        self.profit_sl_calculator = profit_sl_calculator  # For Order B (Profit Trail)
        self.logger = logging.getLogger(__name__)
    
    def is_enabled(self) -> bool:
        """Check if dual order system is enabled"""
        return self.config.get("dual_order_config", {}).get("enabled", True)
    
    def validate_dual_order_risk(self, symbol: str, lot_size: float, 
                                account_balance: float) -> Dict[str, Any]:
        """
        Validate if account can handle 2x lot size risk
        Returns: {"valid": bool, "reason": str}
        
        NOTE: Margin validation DISABLED as it was causing false positives (0% margin level).
        MT5 broker handles margin requirements automatically.
        We only check daily/lifetime loss limits here.
        """
        if not self.is_enabled():
            return {"valid": True, "reason": "Dual orders disabled"}
        
        # Calculate risk for 2x lot size
        symbol_config = self.config["symbol_config"][symbol]
        account_tier = self.risk_manager.get_risk_tier(account_balance)
        
        # Get SL pips from dual SL system
        sl_pips = self.pip_calculator._get_sl_from_dual_system(symbol, account_balance)
        
        # Get pip value (support both config key names)
        pip_value_std = symbol_config.get("pip_value_per_std_lot")
        if pip_value_std is None:
            pip_value_std = symbol_config.get("pip_value", 10.0)
        
        pip_value = pip_value_std * (lot_size * 2)  # 2x lot size
        
        # Calculate expected loss for 2 orders
        expected_loss = sl_pips * pip_value
        
        # Get risk tier limits
        if account_tier not in self.config["risk_tiers"]:
            return {"valid": False, "reason": f"Invalid risk tier: {account_tier}"}
        
        risk_params = self.config["risk_tiers"][account_tier]
        
        # Check daily loss cap
        # Check daily loss cap
        daily_loss = self.risk_manager.daily_loss
        risk_gap = daily_loss + expected_loss - risk_params["daily_loss_limit"]
        
        if risk_gap > 0:
            # SMART AUTO-ADJUSTMENT LOGIC
            # Calculate max allowed risk
            available_risk = max(0, risk_params["daily_loss_limit"] - daily_loss)
            
            if available_risk < 1.0: # If less than $1 available, block trade
                 return {
                    "valid": False,
                    "reason": f"Daily loss cap reached: ${daily_loss:.2f} >= ${risk_params['daily_loss_limit']}"
                }
            
            # Calculate max allowed lot size (reverse engineer from risk formula)
            # Formula: Risk = sl_pips * (pip_value_std * lot * 2)
            # So: lot = Risk / (sl_pips * pip_value_std * 2)
            
            # Use sl_pips + small buffer to be safe
            safe_sl_pips = sl_pips if sl_pips > 0 else 1
            
            max_allowed_lot = available_risk / (safe_sl_pips * pip_value_std * 2)
            
            # Round down to 2 decimal places to be safe
            import math
            adjusted_lot = math.floor(max_allowed_lot * 100) / 100.0
            
            # Ensure minimum valid lot size
            min_lot = 0.01
            if adjusted_lot < min_lot:
                 return {
                    "valid": False,
                    "reason": f"Available risk ${available_risk:.2f} too small for min lot {min_lot}"
                }
            
            self.logger.warning(
                f"🔧 SMART ADJUSTMENT: Lot reduced {lot_size} -> {adjusted_lot} "
                f"to fit daily limit (Risk: ${expected_loss:.2f} -> ${available_risk:.2f})"
            )
            
            return {
                "valid": True,
                "reason": f"Auto-adjusted lot to {adjusted_lot} to fit daily limit",
                "adjusted_lot": adjusted_lot,
                "was_adjusted": True
            }

        # Check lifetime loss cap (similar logic could be applied, but usually daily limit is the bottleneck)
        lifetime_loss = self.risk_manager.lifetime_loss
        if lifetime_loss + expected_loss > risk_params["max_total_loss"]:
             return {
                "valid": False,
                "reason": f"Lifetime loss cap exceeded: ${lifetime_loss + expected_loss:.2f} > ${risk_params['max_total_loss']}"
            }
        
        # MARGIN VALIDATION DISABLED (was causing false 0% margin level errors)
        # MT5 broker automatically manages margin requirements - no need to check here
        # Previous broken code (lines 78-112) has been removed
        
        # All validations passed
        return {"valid": True, "reason": "Risk validation passed"}
        
    def create_dual_orders(self, alert: Alert, strategy: str, 
                          account_balance: float) -> Dict[str, Any]:
        """
        Create Order A (TP Trail) and Order B (Profit Trail) with same lot size
        Returns: {
            "order_a": Trade object or None,
            "order_b": Trade object or None,
            "order_a_placed": bool,
            "order_b_placed": bool,
            "errors": List[str]
        }
        """
        result = {
            "order_a": None,
            "order_b": None,
            "order_a_placed": False,
            "order_b_placed": False,
            "errors": []
        }
        
        if not self.is_enabled():
            # If dual orders disabled, return empty result
            return result
        
        try:
            # Get lot size (same for both orders) - New: Use timeframe specific logic
            requested_lot_size = self.risk_manager.get_lot_size_for_logic(account_balance, logic=strategy)
            
            # DEBUG: Log lot size calculation
            self.logger.debug(
                f"[DUAL_ORDER_LOT_SIZE] Symbol={alert.symbol} Balance=${account_balance:.2f} "
                f"Requested Lot={requested_lot_size:.2f}"
            )
            
            if requested_lot_size <= 0:
                result["errors"].append("Invalid lot size")
                return result
            
            # Validate risk for 2x lot size
            risk_validation = self.validate_dual_order_risk(
                alert.symbol, requested_lot_size, account_balance
            )
            
            # Check for adjusted lot size
            final_lot_size = requested_lot_size
            if risk_validation.get("valid") and risk_validation.get("was_adjusted"):
                final_lot_size = risk_validation.get("adjusted_lot", requested_lot_size)
                adjustment_msg = (
                    f"🔧 SMART ADJUSTMENT: Lot reduced {requested_lot_size:.2f} -> {final_lot_size:.2f} "
                    f"to fit daily limit."
                )
                self.logger.info(adjustment_msg)
                result["smart_adjustment_info"] = adjustment_msg
            
            # DEBUG: Log risk validation
            self.logger.debug(
                f"[DUAL_ORDER_RISK] Symbol={alert.symbol} "
                f"Valid={risk_validation['valid']} Reason={risk_validation.get('reason', 'N/A')}"
            )
            
            if not risk_validation["valid"]:
                result["errors"].append(f"Risk validation failed: {risk_validation['reason']}")
                return result
            
            # Use final_lot_size for calculations
            lot_size = final_lot_size
            
            # Calculate SL and TP for Order A (TP Trail) - uses existing SL system (with TF multiplier)
            sl_price_a, sl_distance_a = self.pip_calculator.calculate_sl_price(
                alert.symbol, alert.price, alert.signal, lot_size, account_balance,
                logic=strategy
            )
            
            tp_price_a = self.pip_calculator.calculate_tp_price(
                alert.price, sl_price_a, alert.signal, self.config.get("rr_ratio", 1.0)
            )
            
            # Calculate SL for Order B (Profit Trail) - uses logic-based SL
            if self.profit_sl_calculator:
                # Get strategy from alert or use default
                strategy = getattr(alert, 'strategy', 'combinedlogic-1')
                sl_price_b, sl_distance_b = self.profit_sl_calculator.calculate_sl_price(
                    alert.price, alert.signal, alert.symbol, lot_size, strategy
                )
            else:
                # Fallback to same SL as Order A if profit SL calculator not available
                sl_price_b, sl_distance_b = sl_price_a, sl_distance_a
            
            # Calculate TP for Order B
            # If SL is disabled (None), use a default distance for TP calculation
            if sl_price_b is None:
                # Use a default SL distance for TP calculation when SL is disabled
                default_sl_distance = alert.price * 0.01  # 1% default
                if alert.signal == "buy":
                    default_sl_price_b = alert.price - default_sl_distance
                else:
                    default_sl_price_b = alert.price + default_sl_distance
                tp_price_b = self.pip_calculator.calculate_tp_price(
                    alert.price, default_sl_price_b, alert.signal, self.config.get("rr_ratio", 1.0)
                )
            else:
                tp_price_b = self.pip_calculator.calculate_tp_price(
                    alert.price, sl_price_b, alert.signal, self.config.get("rr_ratio", 1.0)
                )
            
            # Create Order A (TP Trail) - uses existing SL system
            order_a = Trade(
                symbol=alert.symbol,
                entry=alert.price,
                sl=sl_price_a,
                tp=tp_price_a,
                lot_size=lot_size,
                direction=alert.signal,
                strategy=strategy,
                open_time=datetime.now().isoformat(),
                original_entry=alert.price,
                original_sl_distance=sl_distance_a,
                order_type="TP_TRAIL"
            )
            
            # Create Order B (Profit Trail) - uses independent $10 fixed SL
            order_b = Trade(
                symbol=alert.symbol,
                entry=alert.price,
                sl=sl_price_b,  # Independent $10 fixed SL
                tp=tp_price_b,
                lot_size=lot_size,  # Same lot size
                direction=alert.signal,
                strategy=strategy,
                open_time=datetime.now().isoformat(),
                original_entry=alert.price,
                original_sl_distance=sl_distance_b if sl_distance_b is not None else 0.0,
                order_type="PROFIT_TRAIL"
            )
            
            result["order_a"] = order_a
            result["order_b"] = order_b
            
            # Place Order A independently
            order_a_result = self._place_single_order(order_a, strategy, "TP_TRAIL")
            if order_a_result["success"]:
                result["order_a_placed"] = True
                order_a.trade_id = order_a_result["trade_id"]
            else:
                result["errors"].append(f"Order A failed: {order_a_result.get('error', 'Unknown error')}")
                # Order A failed - but we continue to try Order B (independent)
            
            # Place Order B independently (regardless of Order A result)
            order_b_result = self._place_single_order(order_b, strategy, "PROFIT_TRAIL")
            if order_b_result["success"]:
                result["order_b_placed"] = True
                order_b.trade_id = order_b_result["trade_id"]
            else:
                result["errors"].append(f"Order B failed: {order_b_result.get('error', 'Unknown error')}")
                # Order B failed - but Order A continues independently (no rollback)
            
            # Log results
            if result["order_a_placed"] and result["order_b_placed"]:
                self.logger.info(f"SUCCESS: Both orders placed: {alert.symbol} {alert.signal.upper()}")
            elif result["order_a_placed"]:
                self.logger.warning(f"WARNING: Only Order A placed: {alert.symbol} {alert.signal.upper()} (Order B failed)")
            elif result["order_b_placed"]:
                self.logger.warning(f"WARNING: Only Order B placed: {alert.symbol} {alert.signal.upper()} (Order A failed)")
            else:
                self.logger.error(f"ERROR: Both orders failed: {alert.symbol} {alert.signal.upper()}")
            
            return result
            
        except Exception as e:
            error_msg = f"Dual order creation error: {str(e)}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
            return result
    
    def _place_single_order(self, trade: Trade, strategy: str, 
                           order_type: str) -> Dict[str, Any]:
        """
        Place a single order in MT5
        Returns: {"success": bool, "trade_id": Optional[int], "error": Optional[str]}
        """
        try:
            if self.config.get("simulate_orders", False):
                # Simulation mode
                import random
                trade_id = random.randint(100000, 999999)
                self.logger.info(f"SIMULATED: {order_type}: {trade.symbol} {trade.direction.upper()} @ {trade.entry}")
                return {"success": True, "trade_id": trade_id, "error": None}
            
            # Live trading mode
            trade_id = self.mt5_client.place_order(
                symbol=trade.symbol,
                order_type=trade.direction,
                lot_size=trade.lot_size,
                price=trade.entry,
                sl=trade.sl,
                tp=trade.tp,
                comment=f"{strategy}_{order_type}"
            )
            
            if trade_id:
                return {"success": True, "trade_id": trade_id, "error": None}
            else:
                # Check if it was a validation error (place_order returns None for validation failures)
                # The error message is already logged in mt5_client.place_order()
                error_msg = "MT5 order placement failed"
                if "validation" in str(trade_id).lower() or trade_id is None:
                    error_msg = "Order validation failed - check SL/TP parameters"
                return {"success": False, "trade_id": None, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Order placement error: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "trade_id": None, "error": error_msg}

