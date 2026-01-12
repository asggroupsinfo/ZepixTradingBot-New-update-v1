"""
Profit Booking Service - V5 Hybrid Plugin Architecture

This service provides profit booking functionality for all plugins.
Implements the 5-level pyramid system (1->2->4->8->16 orders).

Part of Document 05: Phase 3 Detailed Plan - Service API Layer
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ChainStatus(Enum):
    """Profit chain status enumeration."""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProfitLevel(Enum):
    """Profit level enumeration for pyramid system."""
    LEVEL_0 = 0  # Base: 1 order
    LEVEL_1 = 1  # 2 orders
    LEVEL_2 = 2  # 4 orders
    LEVEL_3 = 3  # 8 orders
    LEVEL_4 = 4  # 16 orders (max)


@dataclass
class ProfitChain:
    """Represents a profit booking chain."""
    chain_id: str
    plugin_id: str
    symbol: str
    direction: str
    base_lot: float
    current_level: int
    status: ChainStatus
    created_at: datetime
    total_profit: float = 0.0
    total_orders: int = 0
    orders: List[int] = field(default_factory=list)
    level_history: List[Dict[str, Any]] = field(default_factory=list)
    closed_at: Optional[datetime] = None
    close_reason: Optional[str] = None


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
        self.chains: Dict[str, ProfitChain] = {}
        self.stats = {
            "total_chains_created": 0,
            "total_profit_booked": 0.0,
            "total_levels_advanced": 0,
            "total_orders_placed": 0
        }
        self.logger.info("ProfitBookingService initialized")
    
    async def create_chain(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        base_lot: float,
        initial_order_ticket: Optional[int] = None
    ) -> str:
        """
        Create a new profit booking chain.
        
        Args:
            plugin_id: ID of the plugin creating the chain
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            base_lot: Base lot size for the chain
            initial_order_ticket: Optional initial order ticket
            
        Returns:
            str: Chain ID for tracking
        """
        chain_id = f"{plugin_id}_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        self.logger.info(
            f"Creating profit chain: {chain_id} "
            f"{direction} {symbol} base_lot={base_lot}"
        )
        
        chain = ProfitChain(
            chain_id=chain_id,
            plugin_id=plugin_id,
            symbol=symbol,
            direction=direction.upper(),
            base_lot=base_lot,
            current_level=0,
            status=ChainStatus.ACTIVE,
            created_at=datetime.now(),
            total_orders=1 if initial_order_ticket else 0,
            orders=[initial_order_ticket] if initial_order_ticket else []
        )
        
        self.chains[chain_id] = chain
        self.stats["total_chains_created"] += 1
        
        self.logger.info(f"Chain created: {chain_id}")
        return chain_id
    
    async def process_profit_level(
        self,
        chain_id: str,
        profit_amount: float,
        close_current_orders: bool = True
    ) -> Dict[str, Any]:
        """
        Process a profit level trigger for a chain.
        
        When profit target is hit:
        1. Book profit on current orders (partial close)
        2. Advance to next pyramid level
        3. Place new orders at next level quantity
        
        Args:
            chain_id: Chain identifier
            profit_amount: Profit amount booked
            close_current_orders: Whether to close current orders
            
        Returns:
            dict: Processing result with new level info
        """
        if chain_id not in self.chains:
            self.logger.error(f"Chain not found: {chain_id}")
            return {"success": False, "error": "chain_not_found"}
        
        chain = self.chains[chain_id]
        
        if chain.status != ChainStatus.ACTIVE:
            self.logger.error(f"Chain not active: {chain_id}")
            return {"success": False, "error": "chain_not_active"}
        
        current_level = chain.current_level
        new_level = min(current_level + 1, 4)
        
        self.logger.info(
            f"Processing profit level for {chain_id}: "
            f"level {current_level} -> {new_level}, profit={profit_amount}"
        )
        
        level_record = {
            "from_level": current_level,
            "to_level": new_level,
            "profit_booked": profit_amount,
            "timestamp": datetime.now().isoformat(),
            "orders_at_level": self.get_orders_for_level(new_level)
        }
        
        chain.current_level = new_level
        chain.total_profit += profit_amount
        chain.level_history.append(level_record)
        
        self.stats["total_profit_booked"] += profit_amount
        self.stats["total_levels_advanced"] += 1
        
        new_orders_count = self.get_orders_for_level(new_level)
        new_orders = []
        
        if new_level < 4:
            lot_per_order = chain.base_lot / new_orders_count
            lot_per_order = max(0.01, round(lot_per_order, 2))
            
            for i in range(new_orders_count):
                ticket = await self.order_service.place_order(
                    plugin_id=chain.plugin_id,
                    symbol=chain.symbol,
                    direction=chain.direction,
                    lot_size=lot_per_order,
                    comment=f"PB_L{new_level}_{i+1}"
                ) if self.order_service else None
                
                if ticket:
                    new_orders.append(ticket)
                    chain.orders.append(ticket)
                    chain.total_orders += 1
                    self.stats["total_orders_placed"] += 1
        
        if new_level >= 4:
            chain.status = ChainStatus.COMPLETED
            chain.closed_at = datetime.now()
            chain.close_reason = "max_level_reached"
        
        return {
            "success": True,
            "chain_id": chain_id,
            "previous_level": current_level,
            "new_level": new_level,
            "profit_booked": profit_amount,
            "total_profit": chain.total_profit,
            "new_orders_placed": len(new_orders),
            "new_order_tickets": new_orders,
            "chain_completed": chain.status == ChainStatus.COMPLETED
        }
    
    async def book_profit(
        self,
        plugin_id: str,
        order_ticket: int,
        percentage: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Book partial profit on an order.
        
        Args:
            plugin_id: Plugin ID
            order_ticket: Order ticket to book profit from
            percentage: Percentage of position to close (0-100)
            reason: Reason for booking
            
        Returns:
            dict: Profit booking result
        """
        self.logger.info(
            f"Booking {percentage}% profit on order {order_ticket} [{plugin_id}]"
        )
        
        if not self.order_service:
            return {"success": False, "error": "no_order_service"}
        
        order_info = await self.order_service.get_order_info(order_ticket, plugin_id)
        if not order_info:
            return {"success": False, "error": "order_not_found"}
        
        close_volume = order_info["lot_size"] * (percentage / 100)
        close_volume = max(0.01, round(close_volume, 2))
        
        success = await self.order_service.close_order(
            order_ticket,
            plugin_id,
            partial_volume=close_volume
        )
        
        if success:
            return {
                "success": True,
                "order_ticket": order_ticket,
                "closed_volume": close_volume,
                "remaining_volume": order_info["lot_size"] - close_volume,
                "percentage_closed": percentage,
                "reason": reason
            }
        
        return {"success": False, "error": "close_failed"}
    
    async def get_chain_status(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a profit booking chain.
        
        Args:
            chain_id: Chain identifier
            
        Returns:
            dict: Chain status or None if not found
        """
        chain = self.chains.get(chain_id)
        if not chain:
            return None
        
        return {
            "chain_id": chain.chain_id,
            "plugin_id": chain.plugin_id,
            "symbol": chain.symbol,
            "direction": chain.direction,
            "base_lot": chain.base_lot,
            "current_level": chain.current_level,
            "status": chain.status.value,
            "total_profit": chain.total_profit,
            "total_orders": chain.total_orders,
            "orders": chain.orders,
            "level_history": chain.level_history,
            "created_at": chain.created_at.isoformat(),
            "closed_at": chain.closed_at.isoformat() if chain.closed_at else None,
            "close_reason": chain.close_reason
        }
    
    async def close_chain(
        self,
        chain_id: str,
        reason: str = "manual",
        close_orders: bool = True
    ) -> bool:
        """
        Close a profit booking chain.
        
        Args:
            chain_id: Chain identifier
            reason: Reason for closing
            close_orders: Whether to close all orders in the chain
            
        Returns:
            bool: True if closed successfully
        """
        if chain_id not in self.chains:
            self.logger.error(f"Chain not found: {chain_id}")
            return False
        
        chain = self.chains[chain_id]
        
        if close_orders and self.order_service:
            for ticket in chain.orders:
                await self.order_service.close_order(ticket, chain.plugin_id)
        
        chain.status = ChainStatus.CLOSED
        chain.close_reason = reason
        chain.closed_at = datetime.now()
        
        self.logger.info(f"Closed chain {chain_id}: {reason}")
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
        
        for chain in self.chains.values():
            if chain.status != ChainStatus.ACTIVE:
                continue
            if plugin_id and chain.plugin_id != plugin_id:
                continue
            if symbol and chain.symbol != symbol:
                continue
            
            chains.append({
                "chain_id": chain.chain_id,
                "plugin_id": chain.plugin_id,
                "symbol": chain.symbol,
                "direction": chain.direction,
                "current_level": chain.current_level,
                "total_profit": chain.total_profit,
                "total_orders": chain.total_orders
            })
        
        return chains
    
    def get_orders_for_level(self, level: int) -> int:
        """
        Get number of orders for a pyramid level.
        
        Args:
            level: Pyramid level (0-4)
            
        Returns:
            int: Number of orders at that level
        """
        return self.PYRAMID_LEVELS.get(level, 16)
    
    def get_lot_size_for_level(self, base_lot: float, level: int) -> float:
        """
        Calculate lot size per order for a pyramid level.
        
        Args:
            base_lot: Base lot size
            level: Pyramid level
            
        Returns:
            float: Lot size per order
        """
        orders_at_level = self.get_orders_for_level(level)
        lot_per_order = base_lot / orders_at_level
        return max(0.01, round(lot_per_order, 2))
    
    async def get_chain_statistics(self) -> Dict[str, Any]:
        """
        Get overall profit booking statistics.
        
        Returns:
            dict: Statistics summary
        """
        active_count = sum(1 for c in self.chains.values() if c.status == ChainStatus.ACTIVE)
        completed_count = sum(1 for c in self.chains.values() if c.status == ChainStatus.COMPLETED)
        closed_count = sum(1 for c in self.chains.values() if c.status == ChainStatus.CLOSED)
        
        level_distribution = {i: 0 for i in range(5)}
        for chain in self.chains.values():
            if chain.status == ChainStatus.ACTIVE:
                level_distribution[chain.current_level] += 1
        
        return {
            "total_chains": len(self.chains),
            "active_chains": active_count,
            "completed_chains": completed_count,
            "closed_chains": closed_count,
            "total_profit_booked": self.stats["total_profit_booked"],
            "total_levels_advanced": self.stats["total_levels_advanced"],
            "total_orders_placed": self.stats["total_orders_placed"],
            "level_distribution": level_distribution
        }
    
    def get_plugin_statistics(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            dict: Plugin-specific statistics
        """
        plugin_chains = [c for c in self.chains.values() if c.plugin_id == plugin_id]
        active = sum(1 for c in plugin_chains if c.status == ChainStatus.ACTIVE)
        total_profit = sum(c.total_profit for c in plugin_chains)
        
        return {
            "plugin_id": plugin_id,
            "total_chains": len(plugin_chains),
            "active_chains": active,
            "total_profit": total_profit,
            "total_orders": sum(c.total_orders for c in plugin_chains)
        }
