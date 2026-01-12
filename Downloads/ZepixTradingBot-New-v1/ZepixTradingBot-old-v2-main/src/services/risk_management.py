"""
Risk Management Service - V5 Hybrid Plugin Architecture

This service provides risk calculation and management for all plugins.
Implements tier-based risk management for different account sizes.

Part of Document 01: Project Overview - Service Layer Architecture
"""

from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskManagementService:
    """
    Centralized risk management service for all trading plugins.
    
    Implements Tier-Based Risk Management:
    - Tier 1: $5K-$10K accounts
    - Tier 2: $10K-$25K accounts
    - Tier 3: $25K-$50K accounts
    - Tier 4: $50K-$100K accounts
    - Tier 5: $100K+ accounts
    
    Responsibilities:
    - Calculate appropriate lot sizes
    - Validate risk per trade
    - Track daily/lifetime loss limits
    - Provide account tier information
    
    Benefits:
    - Consistent risk management across all plugins
    - Automatic lot size calculation
    - Loss limit enforcement
    - Account protection
    
    Usage:
        service = RiskManagementService(mt5_client, config)
        lot_size = service.calculate_lot_size(
            balance=10000,
            sl_pips=50,
            symbol="EURUSD"
        )
    """
    
    # Account tiers with risk parameters
    ACCOUNT_TIERS = {
        "TIER_1": {"min": 5000, "max": 10000, "risk_pct": 0.01, "max_lot": 0.05},
        "TIER_2": {"min": 10000, "max": 25000, "risk_pct": 0.01, "max_lot": 0.10},
        "TIER_3": {"min": 25000, "max": 50000, "risk_pct": 0.01, "max_lot": 0.20},
        "TIER_4": {"min": 50000, "max": 100000, "risk_pct": 0.01, "max_lot": 0.50},
        "TIER_5": {"min": 100000, "max": float('inf'), "risk_pct": 0.01, "max_lot": 1.00}
    }
    
    # Daily and lifetime loss limits
    DAILY_LOSS_LIMIT_PCT = 0.03  # 3% of balance
    LIFETIME_LOSS_LIMIT = 500.0  # $500 absolute
    
    def __init__(self, mt5_client, config: Dict[str, Any]):
        """
        Initialize Risk Management Service.
        
        Args:
            mt5_client: MetaTrader 5 client instance
            config: Service configuration
        """
        self.mt5_client = mt5_client
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.RiskManagementService")
        
        # Track daily losses per plugin
        self.daily_losses: Dict[str, float] = {}
        self.lifetime_loss: float = 0.0
        
        self.logger.info("RiskManagementService initialized")
    
    def get_account_tier(self, balance: float) -> str:
        """
        Determine account tier based on balance.
        
        Args:
            balance: Current account balance
            
        Returns:
            str: Tier name (e.g., "TIER_1", "TIER_2")
        """
        for tier_name, tier_config in self.ACCOUNT_TIERS.items():
            if tier_config["min"] <= balance < tier_config["max"]:
                return tier_name
        
        return "TIER_5"  # Default to highest tier
    
    def get_tier_config(self, balance: float) -> Dict[str, Any]:
        """
        Get tier configuration for a balance.
        
        Args:
            balance: Current account balance
            
        Returns:
            dict: Tier configuration
        """
        tier_name = self.get_account_tier(balance)
        return self.ACCOUNT_TIERS[tier_name]
    
    def calculate_lot_size(
        self,
        balance: float,
        sl_pips: float,
        symbol: str = "EURUSD",
        risk_override: Optional[float] = None
    ) -> float:
        """
        Calculate appropriate lot size based on risk parameters.
        
        Args:
            balance: Current account balance
            sl_pips: Stop loss distance in pips
            symbol: Trading symbol
            risk_override: Override risk percentage (None = use tier default)
            
        Returns:
            float: Calculated lot size
        """
        tier_config = self.get_tier_config(balance)
        risk_pct = risk_override or tier_config["risk_pct"]
        max_lot = tier_config["max_lot"]
        
        # Risk amount in dollars
        risk_amount = balance * risk_pct
        
        # Pip value calculation (simplified)
        # TODO: Get actual pip value from MT5 for accurate calculation
        pip_value = 10.0  # $10 per pip for 1 lot on most pairs
        if "JPY" in symbol:
            pip_value = 1000.0 / 100  # Adjusted for JPY pairs
        elif "XAU" in symbol or "GOLD" in symbol:
            pip_value = 1.0  # Gold has different pip value
        
        # Calculate lot size
        if sl_pips > 0 and pip_value > 0:
            lot_size = risk_amount / (sl_pips * pip_value)
        else:
            lot_size = 0.01  # Minimum lot
        
        # Apply tier maximum
        lot_size = min(lot_size, max_lot)
        
        # Round to 2 decimal places
        lot_size = round(lot_size, 2)
        
        # Ensure minimum lot size
        lot_size = max(lot_size, 0.01)
        
        self.logger.debug(
            f"Calculated lot size: {lot_size} "
            f"(balance={balance}, sl_pips={sl_pips}, risk={risk_pct})"
        )
        
        return lot_size
    
    def get_fixed_lot_size(self, balance: float) -> float:
        """
        Get fixed lot size based on account tier.
        
        Used when SL pips are not known in advance.
        
        Args:
            balance: Current account balance
            
        Returns:
            float: Fixed lot size for the tier
        """
        tier_config = self.get_tier_config(balance)
        
        # Use a conservative fixed lot based on tier
        fixed_lots = {
            "TIER_1": 0.01,
            "TIER_2": 0.02,
            "TIER_3": 0.05,
            "TIER_4": 0.10,
            "TIER_5": 0.20
        }
        
        tier_name = self.get_account_tier(balance)
        return fixed_lots.get(tier_name, 0.01)
    
    def validate_risk(
        self,
        symbol: str,
        lot_size: float,
        sl_pips: float,
        balance: float,
        plugin_id: str = ""
    ) -> Dict[str, Any]:
        """
        Validate if a trade meets risk requirements.
        
        Args:
            symbol: Trading symbol
            lot_size: Proposed lot size
            sl_pips: Stop loss in pips
            balance: Current balance
            plugin_id: Plugin requesting validation
            
        Returns:
            dict: Validation result with approved lot size
        """
        tier_config = self.get_tier_config(balance)
        max_lot = tier_config["max_lot"]
        
        # Check lot size limit
        if lot_size > max_lot:
            return {
                "valid": False,
                "reason": f"Lot size {lot_size} exceeds tier max {max_lot}",
                "suggested_lot": max_lot
            }
        
        # Check daily loss limit
        daily_loss = self.daily_losses.get(plugin_id, 0.0)
        daily_limit = balance * self.DAILY_LOSS_LIMIT_PCT
        
        if daily_loss >= daily_limit:
            return {
                "valid": False,
                "reason": f"Daily loss limit reached: ${daily_loss:.2f}/${daily_limit:.2f}",
                "suggested_lot": 0
            }
        
        # Check lifetime loss limit
        if self.lifetime_loss >= self.LIFETIME_LOSS_LIMIT:
            return {
                "valid": False,
                "reason": f"Lifetime loss limit reached: ${self.lifetime_loss:.2f}",
                "suggested_lot": 0
            }
        
        return {
            "valid": True,
            "approved_lot": lot_size,
            "tier": self.get_account_tier(balance),
            "daily_loss_remaining": daily_limit - daily_loss
        }
    
    def record_loss(self, amount: float, plugin_id: str = ""):
        """
        Record a trading loss.
        
        Args:
            amount: Loss amount (positive number)
            plugin_id: Plugin that incurred the loss
        """
        if amount <= 0:
            return
        
        # Update daily loss
        current_daily = self.daily_losses.get(plugin_id, 0.0)
        self.daily_losses[plugin_id] = current_daily + amount
        
        # Update lifetime loss
        self.lifetime_loss += amount
        
        self.logger.info(
            f"Recorded loss: ${amount:.2f} [{plugin_id}] "
            f"(daily: ${self.daily_losses[plugin_id]:.2f}, "
            f"lifetime: ${self.lifetime_loss:.2f})"
        )
    
    def reset_daily_losses(self):
        """Reset daily loss counters (call at start of trading day)."""
        self.daily_losses = {}
        self.logger.info("Daily loss counters reset")
    
    def get_daily_loss(self, plugin_id: Optional[str] = None) -> float:
        """
        Get daily loss amount.
        
        Args:
            plugin_id: Specific plugin (None = total)
            
        Returns:
            float: Daily loss amount
        """
        if plugin_id:
            return self.daily_losses.get(plugin_id, 0.0)
        return sum(self.daily_losses.values())
    
    def get_lifetime_loss(self) -> float:
        """Get lifetime loss amount."""
        return self.lifetime_loss
    
    def get_risk_summary(self, balance: float) -> Dict[str, Any]:
        """
        Get comprehensive risk summary.
        
        Args:
            balance: Current account balance
            
        Returns:
            dict: Risk summary
        """
        tier_name = self.get_account_tier(balance)
        tier_config = self.ACCOUNT_TIERS[tier_name]
        daily_limit = balance * self.DAILY_LOSS_LIMIT_PCT
        
        return {
            "balance": balance,
            "tier": tier_name,
            "risk_per_trade": tier_config["risk_pct"],
            "max_lot_size": tier_config["max_lot"],
            "daily_loss_limit": daily_limit,
            "daily_loss_used": self.get_daily_loss(),
            "daily_loss_remaining": daily_limit - self.get_daily_loss(),
            "lifetime_loss": self.lifetime_loss,
            "lifetime_loss_limit": self.LIFETIME_LOSS_LIMIT,
            "lifetime_loss_remaining": self.LIFETIME_LOSS_LIMIT - self.lifetime_loss
        }
