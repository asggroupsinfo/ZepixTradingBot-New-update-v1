"""
V3 Combined Logic - Position Sizer Module

Implements V3 4-step position sizing flow:
1. Base lot from risk tier
2. Apply V3 consensus multiplier (0.2 to 1.0)
3. Apply logic multiplier (LOGIC1/2/3)
4. Final lot = base × v3_mult × logic_mult

Part of Document 06: Phase 4 - V3 Plugin Migration
"""

from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class V3PositionSizer:
    """
    V3 Position Sizing with 4-step flow.
    
    Step 1: Base lot from risk tier
    Step 2: Apply V3 consensus multiplier (0.2 to 1.0)
    Step 3: Apply logic multiplier (LOGIC1/2/3)
    Step 4: Final lot = base × v3_mult × logic_mult
    
    Consensus Score Mapping:
    - Score 0 -> 0.2 multiplier
    - Score 9 -> 1.0 multiplier
    - Formula: 0.2 + (score / 9.0) * 0.8
    """
    
    # Risk tier base lots
    DEFAULT_RISK_TIERS = {
        'micro': {'min_balance': 0, 'max_balance': 1000, 'base_lot': 0.01},
        'mini': {'min_balance': 1000, 'max_balance': 5000, 'base_lot': 0.05},
        'standard': {'min_balance': 5000, 'max_balance': 25000, 'base_lot': 0.10},
        'premium': {'min_balance': 25000, 'max_balance': 100000, 'base_lot': 0.25},
        'elite': {'min_balance': 100000, 'max_balance': float('inf'), 'base_lot': 0.50}
    }
    
    # Logic multipliers
    DEFAULT_LOGIC_MULTIPLIERS = {
        'LOGIC1': 1.25,   # Scalping - larger lots
        'LOGIC2': 1.0,    # Intraday - balanced
        'LOGIC3': 0.625   # Swing - smaller lots
    }
    
    # Consensus score range
    MIN_CONSENSUS_MULTIPLIER = 0.2
    MAX_CONSENSUS_MULTIPLIER = 1.0
    MAX_CONSENSUS_SCORE = 9
    
    # Lot size limits
    MIN_LOT_SIZE = 0.01
    MAX_LOT_SIZE = 10.0
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize V3 Position Sizer.
        
        Args:
            config: Plugin configuration (optional)
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.V3PositionSizer")
        
        # Load risk tiers from config or use defaults
        self.risk_tiers = self.config.get('risk_tiers', self.DEFAULT_RISK_TIERS)
        self.logic_multipliers = self.config.get('logic_multipliers', self.DEFAULT_LOGIC_MULTIPLIERS)
        
        self.logger.info("V3PositionSizer initialized - 4-step flow ready")
    
    def calculate_v3_lot_size(
        self,
        alert: Any,
        logic_multiplier: float,
        balance: float = None
    ) -> float:
        """
        Calculate V3 lot size using 4-step flow.
        
        Args:
            alert: V3 alert data with consensus_score
            logic_multiplier: Logic route multiplier (1.25, 1.0, or 0.625)
            balance: Account balance (optional, uses alert.risk_tier if not provided)
            
        Returns:
            float: Final lot size
        """
        # Step 1: Get base lot from risk tier
        risk_tier = self._get_attr(alert, 'risk_tier', 'standard')
        base_lot = self._get_base_lot(risk_tier, balance)
        
        # Step 2: Apply V3 consensus multiplier
        consensus_score = self._get_attr(alert, 'consensus_score', 5)
        v3_multiplier = self._calculate_consensus_multiplier(consensus_score)
        
        # Step 3: Apply logic multiplier (already provided)
        # Step 4: Final lot = base × v3_mult × logic_mult
        final_lot = base_lot * v3_multiplier * logic_multiplier
        
        # Apply limits
        final_lot = max(self.MIN_LOT_SIZE, min(final_lot, self.MAX_LOT_SIZE))
        final_lot = round(final_lot, 2)
        
        self.logger.debug(
            f"V3 Lot calculation: base={base_lot} × v3={v3_multiplier:.2f} "
            f"× logic={logic_multiplier} = {final_lot}"
        )
        
        return final_lot
    
    def calculate_dual_lots(
        self,
        alert: Any,
        logic_multiplier: float,
        balance: float = None
    ) -> Tuple[float, float]:
        """
        Calculate lot sizes for Order A and Order B.
        
        Returns: (order_a_lot, order_b_lot)
        Both are 50% of total lot size.
        
        Args:
            alert: V3 alert data
            logic_multiplier: Logic route multiplier
            balance: Account balance (optional)
            
        Returns:
            Tuple[float, float]: (order_a_lot, order_b_lot)
        """
        final_lot = self.calculate_v3_lot_size(alert, logic_multiplier, balance)
        
        # Split 50/50 between Order A and Order B
        order_a_lot = round(final_lot * 0.5, 2)
        order_b_lot = round(final_lot * 0.5, 2)
        
        # Ensure minimum lot size
        order_a_lot = max(order_a_lot, self.MIN_LOT_SIZE)
        order_b_lot = max(order_b_lot, self.MIN_LOT_SIZE)
        
        return order_a_lot, order_b_lot
    
    def _get_base_lot(self, risk_tier: str, balance: float = None) -> float:
        """
        Get base lot from risk tier.
        
        Args:
            risk_tier: Risk tier name or balance-based
            balance: Account balance (optional)
            
        Returns:
            float: Base lot size
        """
        # If balance provided, determine tier from balance
        if balance is not None:
            for tier_name, tier_config in self.risk_tiers.items():
                min_bal = tier_config.get('min_balance', 0)
                max_bal = tier_config.get('max_balance', float('inf'))
                if min_bal <= balance < max_bal:
                    return tier_config.get('base_lot', 0.01)
        
        # Otherwise use tier name
        if risk_tier in self.risk_tiers:
            return self.risk_tiers[risk_tier].get('base_lot', 0.01)
        
        # Default
        return 0.10
    
    def _calculate_consensus_multiplier(self, consensus_score: int) -> float:
        """
        Calculate V3 consensus multiplier from score.
        
        Formula: 0.2 + (score / 9.0) * 0.8
        Maps: 0 -> 0.2, 9 -> 1.0
        
        Args:
            consensus_score: Score from 0-9
            
        Returns:
            float: Multiplier from 0.2 to 1.0
        """
        # Clamp score to valid range
        score = max(0, min(consensus_score, self.MAX_CONSENSUS_SCORE))
        
        # Calculate multiplier
        multiplier = (
            self.MIN_CONSENSUS_MULTIPLIER +
            (score / self.MAX_CONSENSUS_SCORE) *
            (self.MAX_CONSENSUS_MULTIPLIER - self.MIN_CONSENSUS_MULTIPLIER)
        )
        
        return round(multiplier, 2)
    
    def get_logic_multiplier(self, logic_route: str) -> float:
        """
        Get lot multiplier for logic route.
        
        Args:
            logic_route: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
            
        Returns:
            float: Multiplier value
        """
        return self.logic_multipliers.get(logic_route, 1.0)
    
    def get_tier_for_balance(self, balance: float) -> str:
        """
        Get risk tier name for balance.
        
        Args:
            balance: Account balance
            
        Returns:
            str: Tier name
        """
        for tier_name, tier_config in self.risk_tiers.items():
            min_bal = tier_config.get('min_balance', 0)
            max_bal = tier_config.get('max_balance', float('inf'))
            if min_bal <= balance < max_bal:
                return tier_name
        return 'standard'
    
    def validate_lot_size(self, lot_size: float, symbol: str = None) -> Tuple[bool, str]:
        """
        Validate lot size against limits.
        
        Args:
            lot_size: Lot size to validate
            symbol: Trading symbol (optional, for symbol-specific limits)
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if lot_size < self.MIN_LOT_SIZE:
            return False, f"Lot size {lot_size} below minimum {self.MIN_LOT_SIZE}"
        
        if lot_size > self.MAX_LOT_SIZE:
            return False, f"Lot size {lot_size} above maximum {self.MAX_LOT_SIZE}"
        
        return True, "Valid"
    
    def adjust_lot_for_symbol(self, lot_size: float, symbol: str) -> float:
        """
        Adjust lot size for symbol-specific requirements.
        
        Args:
            lot_size: Base lot size
            symbol: Trading symbol
            
        Returns:
            float: Adjusted lot size
        """
        # Gold typically has different lot requirements
        if 'XAU' in symbol or 'GOLD' in symbol:
            # Gold often uses smaller lots
            lot_size = lot_size * 0.1
        
        # Ensure minimum
        lot_size = max(lot_size, self.MIN_LOT_SIZE)
        
        return round(lot_size, 2)
    
    def _get_attr(self, alert: Any, attr: str, default: Any = None) -> Any:
        """Get attribute from alert (supports dict and object)."""
        if isinstance(alert, dict):
            return alert.get(attr, default)
        return getattr(alert, attr, default)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get position sizer statistics."""
        return {
            'risk_tiers': list(self.risk_tiers.keys()),
            'logic_multipliers': self.logic_multipliers,
            'min_lot': self.MIN_LOT_SIZE,
            'max_lot': self.MAX_LOT_SIZE,
            'consensus_range': f"{self.MIN_CONSENSUS_MULTIPLIER}-{self.MAX_CONSENSUS_MULTIPLIER}"
        }
