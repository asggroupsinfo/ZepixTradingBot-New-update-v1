"""
Profit Protection Manager - Smart Recovery Decision System
Controls when SL Hunt recovery is allowed based on accumulated chain profits
"""

from typing import Dict, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ProfitProtectionManager:
    """
    Manages profit protection logic for SL Hunt recovery decisions
    
    Features:
    - 4 protection modes (Aggressive, Balanced, Conservative, Very Conservative)
    - Multiplier-based recovery decisions
    - Separate controls for Order A and Order B
    - Real-time configuration updates
    """
    
    # Protection Modes Configuration
    MODES = {
        "AGGRESSIVE": {
            "multiplier": 3.5,
            "min_profit_threshold": 15.0,
            "description": "Frequent recoveries, higher risk",
            "emoji": "⚡"
        },
        "BALANCED": {
            "multiplier": 6.0,
            "min_profit_threshold": 20.0,
            "description": "Recommended for most traders",
            "emoji": "⚖️"
        },
        "CONSERVATIVE": {
            "multiplier": 9.0,
            "min_profit_threshold": 30.0,
            "description": "Protect profits first",
            "emoji": "🛡️"
        },
        "VERY_CONSERVATIVE": {
            "multiplier": 15.0,
            "min_profit_threshold": 50.0,
            "description": "Rare recoveries, maximum safety",
            "emoji": "🔒"
        }
    }
    
    def __init__(self, config_manager, mt5_client=None, risk_manager=None):
        """
        Initialize Profit Protection Manager
        
        Args:
            config_manager: Reference to configuration manager
            mt5_client: MT5 Client for modifying orders
            risk_manager: Risk Manager
        """
        self.config = config_manager
        self.mt5_client = mt5_client
        self.risk_manager = risk_manager
        self.load_settings()
        
        logger.info("✅ ProfitProtectionManager initialized")

    async def check_and_update_sl(self, trade: Any, current_price: float) -> bool:
        """
        Check if trade should have SL moved to lock profit (Trailing/BreakEven)
        
        Args:
            trade: Trade object
            current_price: Current market price
            
        Returns:
            bool: True if SL was updated
        """
        if not self.enabled:
            return False
            
        if not self.mt5_client:
            return False

        # Determine logic based on mode or hardcoded "Lock Profit" rule requested
        # Rule: If Profit >= 40 pips, Lock +10 pips.
        
        try:
            # Calculate profit in pips
            if trade.direction == "buy":
                diff = current_price - trade.entry
                sl_to_be = trade.entry + 0.0010 # +10 pips (assuming 0.0001 pip)
                trigger_price = trade.entry + 0.0040 # +40 pips
                
                # Check condition
                if current_price >= trigger_price:
                    # Check if SL is already better
                    if trade.sl < sl_to_be:
                         # Update SL
                         success = self.mt5_client.modify_position(trade.trade_id, sl=sl_to_be, tp=trade.tp)
                         if success:
                             trade.sl = sl_to_be
                             logger.info(f"🛡️ PROFIT PROTECTION: SL Locked at {sl_to_be:.5f} for {trade.symbol}")
                             return True
            else: # Sell
                diff = trade.entry - current_price
                sl_to_be = trade.entry - 0.0010
                trigger_price = trade.entry - 0.0040
                
                if current_price <= trigger_price:
                    if trade.sl > sl_to_be:
                         success = self.mt5_client.modify_position(trade.trade_id, sl=sl_to_be, tp=trade.tp)
                         if success:
                             trade.sl = sl_to_be
                             logger.info(f"🛡️ PROFIT PROTECTION: SL Locked at {sl_to_be:.5f} for {trade.symbol}")
                             return True
                             
            return False
            
        except Exception as e:
            logger.error(f"Error in check_and_update_sl: {e}")
            return False
    
    def load_settings(self) -> None:
        """Load current profit protection settings from config"""
        
        pp_config = self.config.get("profit_protection", {})
        
        self.enabled = pp_config.get("enabled", True)
        self.current_mode = pp_config.get("current_mode", "BALANCED")
        self.apply_to_order_a = pp_config.get("apply_to_order_a", True)
        self.apply_to_order_b = pp_config.get("apply_to_order_b", True)
        
        # Validate current mode
        if self.current_mode not in self.MODES:
            logger.warning(f"Invalid mode '{self.current_mode}', defaulting to BALANCED")
            self.current_mode = "BALANCED"
        
        mode_info = self.MODES[self.current_mode]
        logger.info(f"""
Profit Protection Settings Loaded:
├─ Enabled: {self.enabled}
├─ Mode: {mode_info['emoji']} {self.current_mode}
├─ Multiplier: {mode_info['multiplier']}x
├─ Min Threshold: ${mode_info['min_profit_threshold']}
├─ Order A: {'ON ✅' if self.apply_to_order_a else 'OFF ❌'}
└─ Order B: {'ON ✅' if self.apply_to_order_b else 'OFF ❌'}
        """)
    
    def check_should_attempt_recovery(
        self,
        chain: Any,
        potential_loss: float,
        order_type: str = "A"
    ) -> Tuple[bool, str]:
        """
        Check if SL Hunt recovery should be attempted
        
        Args:
            chain: Trading chain object with profit calculation method
            potential_loss: Dollar amount of the SL loss
            order_type: "A" for TP Trail or "B" for Profit Booking
        
        Returns:
            Tuple[bool, str]: (should_attempt, reason)
        """
        
        # Check if protection is enabled globally
        if not self.enabled:
            return True, "Profit Protection disabled globally"
        
        # Check if protection applies to this order type
        if order_type == "A" and not self.apply_to_order_a:
            return True, "Order A protection disabled"
        
        if order_type == "B" and not self.apply_to_order_b:
            return True, "Order B protection disabled"
        
        # Get current mode settings
        mode_settings = self.MODES.get(self.current_mode)
        if not mode_settings:
            logger.error(f"Invalid mode: {self.current_mode}")
            return True, "Invalid protection mode, allowing recovery"
        
        multiplier = mode_settings["multiplier"]
        min_threshold = mode_settings["min_profit_threshold"]
        
        # Calculate total chain profit
        try:
            total_profit = chain.calculate_total_profit()
        except Exception as e:
            logger.error(f"Error calculating chain profit: {e}")
            return True, "Error calculating profit, allowing recovery"
        
        # Check 1: Minimum profit threshold
        if total_profit < min_threshold:
            return True, (
                f"Chain profit ${total_profit:.2f} below min threshold ${min_threshold:.2f} "
                f"(allowing recovery)"
            )
        
        # Check 2: Multiplier rule
        required_profit = potential_loss * multiplier
        
        if total_profit > required_profit:
            ratio = total_profit / potential_loss
            reason = (
                f"✅ Protection OK: ${total_profit:.2f} > ${required_profit:.2f} "
                f"({ratio:.1f}x loss) - Recovery ALLOWED"
            )
            
            logger.info(f"""
💰 PROFIT PROTECTION CHECK - PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order Type: {order_type}
Mode: {self.current_mode} ({multiplier}x)
Total Profit: ${total_profit:.2f}
Potential Loss: ${potential_loss:.2f}
Required Profit: ${required_profit:.2f}
Ratio: {ratio:.1f}x
Decision: ✅ ALLOW RECOVERY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)
            
            return True, reason
        else:
            reason = (
                f"🛡️ PROTECTION ACTIVE: ${total_profit:.2f} ≤ ${required_profit:.2f} "
                f"- Protecting accumulated profit, Recovery BLOCKED"
            )
            
            logger.warning(f"""
🛡️ PROFIT PROTECTION CHECK - BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order Type: {order_type}
Mode: {self.current_mode} ({multiplier}x)
Total Profit: ${total_profit:.2f}
Potential Loss: ${potential_loss:.2f}
Required Profit: ${required_profit:.2f}
Gap: ${required_profit - total_profit:.2f}
Decision: ❌ BLOCK RECOVERY
Reason: Protecting ${total_profit:.2f} profit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)
            
            return False, reason
    
    def switch_mode(self, new_mode: str) -> bool:
        """
        Switch to a different protection mode
        
        Args:
            new_mode: Mode name (AGGRESSIVE, BALANCED, CONSERVATIVE, VERY_CONSERVATIVE)
        
        Returns:
            bool: True if successful
        """
        
        new_mode = new_mode.upper()
        
        if new_mode not in self.MODES:
            logger.error(f"Invalid mode: {new_mode}. Valid modes: {list(self.MODES.keys())}")
            return False
        
        old_mode = self.current_mode
        old_settings = self.MODES[old_mode]
        new_settings = self.MODES[new_mode]
        
        # Update mode
        self.current_mode = new_mode
        
        # Save to config
        self.config.update("profit_protection.current_mode", new_mode)
        
        logger.info(f"""
🔄 PROFIT PROTECTION MODE CHANGED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Old Mode: {old_settings['emoji']} {old_mode}
├─ Multiplier: {old_settings['multiplier']}x
└─ Min Threshold: ${old_settings['min_profit_threshold']}

New Mode: {new_settings['emoji']} {new_mode}
├─ Multiplier: {new_settings['multiplier']}x
├─ Min Threshold: ${new_settings['min_profit_threshold']}
└─ Description: {new_settings['description']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        
        return True
    
    def toggle_order_type(self, order_type: str) -> bool:
        """
        Toggle profit protection for Order A or Order B
        
        Args:
            order_type: "A" or "B"
        
        Returns:
            bool: New status (True = enabled, False = disabled)
        """
        
        if order_type == "A":
            self.apply_to_order_a = not self.apply_to_order_a
            self.config.update("profit_protection.apply_to_order_a", self.apply_to_order_a)
            status = "ENABLED ✅" if self.apply_to_order_a else "DISABLED ❌"
            logger.info(f"Order A Profit Protection: {status}")
            return self.apply_to_order_a
        
        elif order_type == "B":
            self.apply_to_order_b = not self.apply_to_order_b
            self.config.update("profit_protection.apply_to_order_b", self.apply_to_order_b)
            status = "ENABLED ✅" if self.apply_to_order_b else "DISABLED ❌"
            logger.info(f"Order B Profit Protection: {status}")
            return self.apply_to_order_b
        
        else:
            logger.error(f"Invalid order type: {order_type}")
            return False
    
    def toggle_enabled(self) -> bool:
        """
        Toggle profit protection on/off globally
        
        Returns:
            bool: New status (True = enabled, False = disabled)
        """
        
        self.enabled = not self.enabled
        self.config.update("profit_protection.enabled", self.enabled)
        
        status = "ENABLED ✅" if self.enabled else "DISABLED ❌"
        logger.info(f"Profit Protection Globally: {status}")
        
        return self.enabled
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current profit protection settings for display
        
        Returns:
            Dict: Current settings
        """
        
        mode_settings = self.MODES.get(self.current_mode, self.MODES["BALANCED"])
        
        return {
            "enabled": self.enabled,
            "mode": self.current_mode,
            "multiplier": mode_settings["multiplier"],
            "min_threshold": mode_settings["min_profit_threshold"],
            "description": mode_settings["description"],
            "emoji": mode_settings["emoji"],
            "order_a_enabled": self.apply_to_order_a,
            "order_b_enabled": self.apply_to_order_b,
            "all_modes": self.MODES
        }
    
    def get_mode_info(self, mode_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific mode
        
        Args:
            mode_name: Mode name
        
        Returns:
            Optional[Dict]: Mode settings or None if invalid
        """
        
        return self.MODES.get(mode_name.upper())
    
    def calculate_required_profit(self, potential_loss: float, mode: Optional[str] = None) -> float:
        """
        Calculate required profit for a given loss amount
        
        Args:
            potential_loss: Dollar loss amount
            mode: Mode to use (defaults to current mode)
        
        Returns:
            float: Required profit amount
        """
        
        if mode is None:
            mode = self.current_mode
        
        mode_settings = self.MODES.get(mode.upper(), self.MODES["BALANCED"])
        multiplier = mode_settings["multiplier"]
        
        return potential_loss * multiplier
    
    def get_status_summary(self) -> str:
        """
        Get formatted status summary
        
        Returns:
            str: Status summary string
        """
        
        mode_settings = self.MODES[self.current_mode]
        
        status = f"""
💰 PROFIT PROTECTION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Global: {'ENABLED ✅' if self.enabled else 'DISABLED ❌'}
Mode: {mode_settings['emoji']} {self.current_mode}
Multiplier: {mode_settings['multiplier']}x
Min Threshold: ${mode_settings['min_threshold']}
Order A: {'ON ✅' if self.apply_to_order_a else 'OFF ❌'}
Order B: {'ON ✅' if self.apply_to_order_b else 'OFF ❌'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        return status
