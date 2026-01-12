"""
Profit Booking Service - V5 Hybrid Plugin Architecture

This service provides profit booking functionality for all plugins.
Implements the 5-level pyramid system (1->2->4->8->16 orders).

Part of Document 01: Project Overview - Service Layer Architecture
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ProfitBookingService:
    """
    Centralized profit booking service for all trading plugins.
    
    Implements the 5-Level Pyramid System:
    - Level 0: 1 order (base)
    - Level 1: 2 orders (after first TP)
    - Level 2: 4 orders (after second TP)
    - Level 3: 8 orders (after third TP)
    - Level 4: 16 orders (maximum)
    
    Responsibilities:
    - Create and manage profit booking chains
    - Process profit level triggers
    - Calculate order quantities per level
    - Track chain statistics
    
    Benefits:
    - Consistent profit booking across all plugins
    - Centralized chain management
    - Audit trail for all profit events
    
    Usage:
        service = ProfitBookingService(order_service, config)
        chain_id = await service.create_chain(
            symbol="EURUSD",
            direction="BUY",
            base_lot=0.01,
            plugin_id="combined_v3"
        )
    """
    
    # Pyramid levels: orders at each level
    PYRAMID_LEVELS = {
        0: 1,   # Base: 1 order
        1: 2,   # Level 1: 2 orders
        2: 4,   # Level 2: 4 orders
        3: 8,   # Level 3: 8 orders
        4: 16   # Level 4: 16 orders (max)
    }
    
    def __init__(self, order_service, config: Dict[str, Any]):
        """
        Initialize Profit Booking Service.
        
        Args:
            order_service: OrderExecutionService instance
            config: Service configuration
        """
        self.order_service = order_service
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ProfitBookingService")
        
        # Active chains tracked in memory
        self.active_chains: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("ProfitBookingService initialized")
    
    async def create_chain(
        self,
        symbol: str,
        direction: str,
        base_lot: float,
        plugin_id: str = ""
    ) -> str:
        """
        Create a new profit booking chain.
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            base_lot: Base lot size for the chain
            plugin_id: ID of the plugin creating the chain
            
        Returns:
            str: Chain ID for tracking
        """
        chain_id = f"{plugin_id}_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.logger.info(
            f"Creating profit chain: {chain_id} "
            f"{direction} {symbol} base_lot={base_lot}"
        )
        
        chain = {
            "chain_id": chain_id,
            "symbol": symbol,
            "direction": direction,
            "base_lot": base_lot,
            "current_level": 0,
            "total_profit": 0.0,
            "status": "ACTIVE",
            "plugin_id": plugin_id,
            "created_at": datetime.now().isoformat(),
            "orders": []
        }
        
        self.active_chains[chain_id] = chain
        
        # TODO: Persist chain to database
        # This is a skeleton - full implementation in Phase 3
        
        return chain_id
    
    async def process_profit_level(
        self,
        chain_id: str,
        profit_amount: float
    ) -> Dict[str, Any]:
        """
        Process a profit level trigger for a chain.
        
        When profit target is hit:
        1. Book profit on current orders
        2. Advance to next pyramid level
        3. Place new orders at next level quantity
        
        Args:
            chain_id: Chain identifier
            profit_amount: Profit amount booked
            
        Returns:
            dict: Processing result with new level info
        """
        if chain_id not in self.active_chains:
            self.logger.error(f"Chain not found: {chain_id}")
            return {"success": False, "error": "chain_not_found"}
        
        chain = self.active_chains[chain_id]
        current_level = chain["current_level"]
        
        self.logger.info(
            f"Processing profit level for {chain_id}: "
            f"level {current_level} -> {current_level + 1}"
        )
        
        # TODO: Implement profit level processing
        # This is a skeleton - full implementation in Phase 3
        
        return {
            "success": True,
            "chain_id": chain_id,
            "previous_level": current_level,
            "new_level": current_level + 1,
            "profit_booked": profit_amount
        }
    
    async def get_chain_status(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a profit booking chain.
        
        Args:
            chain_id: Chain identifier
            
        Returns:
            dict: Chain status or None if not found
        """
        return self.active_chains.get(chain_id)
    
    async def close_chain(
        self,
        chain_id: str,
        reason: str = "manual"
    ) -> bool:
        """
        Close a profit booking chain.
        
        Args:
            chain_id: Chain identifier
            reason: Reason for closing
            
        Returns:
            bool: True if closed successfully
        """
        if chain_id not in self.active_chains:
            self.logger.error(f"Chain not found: {chain_id}")
            return False
        
        chain = self.active_chains[chain_id]
        chain["status"] = "CLOSED"
        chain["close_reason"] = reason
        chain["closed_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Closed chain {chain_id}: {reason}")
        
        # TODO: Persist final state to database
        # This is a skeleton - full implementation in Phase 3
        
        return True
    
    async def get_active_chains(
        self,
        plugin_id: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of active profit booking chains.
        
        Args:
            plugin_id: Filter by plugin (None = all)
            symbol: Filter by symbol (None = all)
            
        Returns:
            List of active chain dictionaries
        """
        chains = []
        
        for chain in self.active_chains.values():
            if chain["status"] != "ACTIVE":
                continue
            if plugin_id and chain.get("plugin_id") != plugin_id:
                continue
            if symbol and chain.get("symbol") != symbol:
                continue
            chains.append(chain)
        
        return chains
    
    def get_orders_for_level(self, level: int) -> int:
        """
        Get number of orders for a pyramid level.
        
        Args:
            level: Pyramid level (0-4)
            
        Returns:
            int: Number of orders at that level
        """
        return self.PYRAMID_LEVELS.get(level, 16)  # Max 16 at level 4+
    
    async def get_chain_statistics(self) -> Dict[str, Any]:
        """
        Get overall profit booking statistics.
        
        Returns:
            dict: Statistics summary
        """
        total_chains = len(self.active_chains)
        active_chains = sum(
            1 for c in self.active_chains.values() if c["status"] == "ACTIVE"
        )
        total_profit = sum(
            c.get("total_profit", 0) for c in self.active_chains.values()
        )
        
        return {
            "total_chains": total_chains,
            "active_chains": active_chains,
            "closed_chains": total_chains - active_chains,
            "total_profit": total_profit
        }
