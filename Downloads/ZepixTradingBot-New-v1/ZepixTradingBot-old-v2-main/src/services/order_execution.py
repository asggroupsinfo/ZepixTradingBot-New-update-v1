"""
Order Execution Service - V5 Hybrid Plugin Architecture

This service provides a unified interface for order management across all plugins.
Plugins call this service instead of directly interacting with MT5.

Part of Document 05: Phase 3 Detailed Plan - Service API Layer
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order type enumeration."""
    MARKET_BUY = "BUY"
    MARKET_SELL = "SELL"
    LIMIT_BUY = "LIMIT_BUY"
    LIMIT_SELL = "LIMIT_SELL"
    STOP_BUY = "STOP_BUY"
    STOP_SELL = "STOP_SELL"


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"


@dataclass
class OrderRecord:
    """Represents an order record for tracking."""
    ticket: int
    plugin_id: str
    symbol: str
    direction: str
    lot_size: float
    open_price: float
    sl_price: float
    tp_price: float
    comment: str
    status: OrderStatus
    created_at: datetime
    closed_at: Optional[datetime] = None
    close_price: Optional[float] = None
    profit: Optional[float] = None
    swap: Optional[float] = None
    commission: Optional[float] = None
    magic_number: int = 0
    order_type: str = "A"


class OrderDatabase:
    """
    In-memory order database for plugin isolation.
    Each plugin can only access its own orders.
    """
    
    def __init__(self):
        self.orders: Dict[int, OrderRecord] = {}
        self.plugin_orders: Dict[str, List[int]] = {}
        self.logger = logging.getLogger(f"{__name__}.OrderDatabase")
    
    def save_order(self, order: OrderRecord) -> bool:
        """Save an order to the database."""
        self.orders[order.ticket] = order
        if order.plugin_id not in self.plugin_orders:
            self.plugin_orders[order.plugin_id] = []
        if order.ticket not in self.plugin_orders[order.plugin_id]:
            self.plugin_orders[order.plugin_id].append(order.ticket)
        self.logger.debug(f"Saved order {order.ticket} for plugin {order.plugin_id}")
        return True
    
    def get_order(self, ticket: int, plugin_id: Optional[str] = None) -> Optional[OrderRecord]:
        """Get an order by ticket, optionally filtered by plugin."""
        order = self.orders.get(ticket)
        if order and plugin_id and order.plugin_id != plugin_id:
            return None
        return order
    
    def get_plugin_orders(self, plugin_id: str, status: Optional[OrderStatus] = None) -> List[OrderRecord]:
        """Get all orders for a plugin, optionally filtered by status."""
        tickets = self.plugin_orders.get(plugin_id, [])
        orders = [self.orders[t] for t in tickets if t in self.orders]
        if status:
            orders = [o for o in orders if o.status == status]
        return orders
    
    def update_order(self, ticket: int, **kwargs) -> bool:
        """Update order fields."""
        if ticket not in self.orders:
            return False
        order = self.orders[ticket]
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)
        return True
    
    def get_open_orders(self, plugin_id: Optional[str] = None, symbol: Optional[str] = None) -> List[OrderRecord]:
        """Get open orders with optional filters."""
        orders = []
        for order in self.orders.values():
            if order.status != OrderStatus.OPEN:
                continue
            if plugin_id and order.plugin_id != plugin_id:
                continue
            if symbol and order.symbol != symbol:
                continue
            orders.append(order)
        return orders


class OrderExecutionService:
    """
    Centralized order execution service for all trading plugins.
    
    Responsibilities:
    - Place market orders (BUY/SELL) with plugin tagging
    - Place dual orders (Order A + Order B) for V3 logic
    - Modify existing orders (SL/TP)
    - Close orders (single or batch)
    - Query open positions with plugin isolation
    - Track all orders in database
    
    Plugin Isolation:
    - Each order is tagged with plugin_id in comment
    - Plugins can only query/modify their own orders
    - Database tracks orders per plugin
    
    Usage:
        service = OrderExecutionService(mt5_client, config)
        ticket = await service.place_order(
            plugin_id="combined_v3",
            symbol="EURUSD",
            direction="BUY",
            lot_size=0.01,
            sl_price=1.0800,
            tp_price=1.0900,
            comment="Entry_Logic1"
        )
    """
    
    MAGIC_NUMBER_BASE = 100000
    MAX_RETRIES = 3
    RETRY_DELAY = 0.5
    
    def __init__(self, mt5_client, config: Dict[str, Any], database: Optional[OrderDatabase] = None):
        """
        Initialize Order Execution Service.
        
        Args:
            mt5_client: MetaTrader 5 client instance
            config: Service configuration
            database: Optional order database (creates new if not provided)
        """
        self.mt5_client = mt5_client
        self.config = config
        self.database = database or OrderDatabase()
        self.logger = logging.getLogger(f"{__name__}.OrderExecutionService")
        self.plugin_magic_numbers: Dict[str, int] = {}
        self._next_magic_offset = 0
        self.stats = {
            "orders_placed": 0,
            "orders_closed": 0,
            "orders_modified": 0,
            "orders_failed": 0,
            "total_profit": 0.0,
            "total_loss": 0.0
        }
        self.logger.info("OrderExecutionService initialized")
    
    def _get_magic_number(self, plugin_id: str) -> int:
        """Get or create magic number for a plugin."""
        if plugin_id not in self.plugin_magic_numbers:
            self.plugin_magic_numbers[plugin_id] = self.MAGIC_NUMBER_BASE + self._next_magic_offset
            self._next_magic_offset += 1
        return self.plugin_magic_numbers[plugin_id]
    
    def _format_comment(self, plugin_id: str, comment: str) -> str:
        """Format order comment with plugin tag."""
        return f"{plugin_id}|{comment}" if comment else plugin_id
    
    def _parse_comment(self, comment: str) -> Tuple[str, str]:
        """Parse plugin_id and original comment from formatted comment."""
        if "|" in comment:
            parts = comment.split("|", 1)
            return parts[0], parts[1]
        return comment, ""
    
    async def place_order(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float = 0.0,
        tp_price: float = 0.0,
        comment: str = ""
    ) -> Optional[int]:
        """
        Place a single market order with plugin tagging.
        
        Args:
            plugin_id: ID of the plugin placing the order
            symbol: Trading symbol (e.g., "EURUSD", "XAUUSD")
            direction: "BUY" or "SELL"
            lot_size: Position size in lots
            sl_price: Stop loss price (0 = no SL)
            tp_price: Take profit price (0 = no TP)
            comment: Order comment for tracking
            
        Returns:
            int: Order ticket number if successful, None if failed
        """
        self.logger.info(
            f"Placing order: {direction} {lot_size} {symbol} "
            f"SL={sl_price} TP={tp_price} [{plugin_id}]"
        )
        
        full_comment = self._format_comment(plugin_id, comment)
        magic_number = self._get_magic_number(plugin_id)
        ticket = None
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                tick = self.mt5_client.get_symbol_tick(symbol) if self.mt5_client else None
                current_price = tick.get("bid", 0.0) if tick else 1.0
                
                if self.mt5_client:
                    ticket = self.mt5_client.place_order(
                        symbol=symbol,
                        order_type=direction.upper(),
                        lot_size=lot_size,
                        price=0.0,
                        sl=sl_price,
                        tp=tp_price,
                        comment=full_comment,
                        magic=magic_number
                    )
                else:
                    ticket = int(datetime.now().timestamp() * 1000) % 1000000000
                
                if ticket:
                    order_record = OrderRecord(
                        ticket=ticket,
                        plugin_id=plugin_id,
                        symbol=symbol,
                        direction=direction.upper(),
                        lot_size=lot_size,
                        open_price=current_price,
                        sl_price=sl_price,
                        tp_price=tp_price,
                        comment=comment,
                        status=OrderStatus.OPEN,
                        created_at=datetime.now(),
                        magic_number=magic_number
                    )
                    self.database.save_order(order_record)
                    self.stats["orders_placed"] += 1
                    self.logger.info(f"Order placed successfully: ticket={ticket}")
                    return ticket
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Order placement attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY)
        
        self.stats["orders_failed"] += 1
        self.logger.error(f"Order placement failed after {self.MAX_RETRIES} attempts: {last_error}")
        return None
    
    async def place_dual_orders(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_a: float,
        lot_b: float,
        sl_a: float,
        sl_b: float,
        tp_a: float = 0.0,
        tp_b: float = 0.0,
        comment_prefix: str = ""
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Place dual orders (Order A + Order B) for V3 logic.
        
        Order A: TP Trail system with timeframe-based SL
        Order B: Profit Trail system with fixed $10 SL
        
        Args:
            plugin_id: ID of the plugin placing orders
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            lot_a: Lot size for Order A
            lot_b: Lot size for Order B
            sl_a: Stop loss for Order A
            sl_b: Stop loss for Order B (typically fixed $10)
            tp_a: Take profit for Order A
            tp_b: Take profit for Order B
            comment_prefix: Comment prefix for tracking
            
        Returns:
            Tuple[int, int]: (ticket_a, ticket_b) or (None, None) if failed
        """
        self.logger.info(
            f"Placing dual orders: {direction} {symbol} "
            f"A={lot_a}@SL{sl_a} B={lot_b}@SL{sl_b} [{plugin_id}]"
        )
        
        ticket_a = await self.place_order(
            plugin_id=plugin_id,
            symbol=symbol,
            direction=direction,
            lot_size=lot_a,
            sl_price=sl_a,
            tp_price=tp_a,
            comment=f"{comment_prefix}_OrderA"
        )
        
        if not ticket_a:
            self.logger.error("Failed to place Order A")
            return (None, None)
        
        self.database.update_order(ticket_a, order_type="A")
        
        ticket_b = await self.place_order(
            plugin_id=plugin_id,
            symbol=symbol,
            direction=direction,
            lot_size=lot_b,
            sl_price=sl_b,
            tp_price=tp_b,
            comment=f"{comment_prefix}_OrderB"
        )
        
        if not ticket_b:
            self.logger.error("Failed to place Order B, closing Order A")
            await self.close_order(ticket_a, plugin_id)
            return (None, None)
        
        self.database.update_order(ticket_b, order_type="B")
        self.logger.info(f"Dual orders placed: A={ticket_a}, B={ticket_b}")
        return (ticket_a, ticket_b)
    
    async def modify_order(
        self,
        ticket: int,
        plugin_id: str,
        sl_price: float = 0.0,
        tp_price: float = 0.0
    ) -> bool:
        """
        Modify an existing order's SL/TP.
        
        Args:
            ticket: Order ticket number
            plugin_id: ID of the plugin modifying the order
            sl_price: New stop loss price (0 = no change)
            tp_price: New take profit price (0 = no change)
            
        Returns:
            bool: True if modification successful
        """
        self.logger.info(
            f"Modifying order {ticket}: SL={sl_price} TP={tp_price} [{plugin_id}]"
        )
        
        order = self.database.get_order(ticket, plugin_id)
        if not order:
            self.logger.error(f"Order {ticket} not found or not owned by {plugin_id}")
            return False
        
        for attempt in range(self.MAX_RETRIES):
            try:
                if self.mt5_client:
                    success = self.mt5_client.modify_position(
                        ticket,
                        sl_price if sl_price > 0 else order.sl_price,
                        tp_price if tp_price > 0 else order.tp_price
                    )
                else:
                    success = True
                
                if success:
                    updates = {}
                    if sl_price > 0:
                        updates["sl_price"] = sl_price
                    if tp_price > 0:
                        updates["tp_price"] = tp_price
                    self.database.update_order(ticket, **updates)
                    self.stats["orders_modified"] += 1
                    self.logger.info(f"Order {ticket} modified successfully")
                    return True
                
            except Exception as e:
                self.logger.warning(f"Modify attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY)
        
        self.logger.error(f"Order modification failed after {self.MAX_RETRIES} attempts")
        return False
    
    async def close_order(
        self,
        ticket: int,
        plugin_id: str,
        partial_volume: Optional[float] = None
    ) -> bool:
        """
        Close a single order (full or partial).
        
        Args:
            ticket: Order ticket number
            plugin_id: ID of the plugin closing the order
            partial_volume: Volume to close (None = full close)
            
        Returns:
            bool: True if close successful
        """
        self.logger.info(
            f"Closing order {ticket} [{plugin_id}]"
            f"{f' partial={partial_volume}' if partial_volume else ''}"
        )
        
        order = self.database.get_order(ticket, plugin_id)
        if not order:
            self.logger.error(f"Order {ticket} not found or not owned by {plugin_id}")
            return False
        
        for attempt in range(self.MAX_RETRIES):
            try:
                if self.mt5_client:
                    if partial_volume:
                        success = self.mt5_client.close_position_partial(ticket, partial_volume)
                    else:
                        success = self.mt5_client.close_position(ticket)
                else:
                    success = True
                
                if success:
                    if partial_volume and partial_volume < order.lot_size:
                        new_lot_size = order.lot_size - partial_volume
                        self.database.update_order(
                            ticket,
                            lot_size=new_lot_size,
                            status=OrderStatus.PARTIALLY_CLOSED
                        )
                    else:
                        self.database.update_order(
                            ticket,
                            status=OrderStatus.CLOSED,
                            closed_at=datetime.now()
                        )
                    self.stats["orders_closed"] += 1
                    self.logger.info(f"Order {ticket} closed successfully")
                    return True
                
            except Exception as e:
                self.logger.warning(f"Close attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY)
        
        self.logger.error(f"Order close failed after {self.MAX_RETRIES} attempts")
        return False
    
    async def close_all_orders(
        self,
        plugin_id: str,
        symbol: Optional[str] = None,
        direction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Close multiple orders with optional filters.
        
        Args:
            plugin_id: ID of the plugin closing orders
            symbol: Filter by symbol (None = all symbols)
            direction: Filter by direction (None = all directions)
            
        Returns:
            dict: Summary of closed orders
        """
        self.logger.info(
            f"Closing all orders: symbol={symbol} direction={direction} [{plugin_id}]"
        )
        
        orders = self.database.get_plugin_orders(plugin_id, OrderStatus.OPEN)
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        if direction:
            orders = [o for o in orders if o.direction == direction.upper()]
        
        closed = 0
        failed = 0
        tickets = []
        
        for order in orders:
            success = await self.close_order(order.ticket, plugin_id)
            if success:
                closed += 1
                tickets.append(order.ticket)
            else:
                failed += 1
        
        result = {
            "closed": closed,
            "failed": failed,
            "tickets": tickets,
            "total_attempted": len(orders)
        }
        self.logger.info(f"Close all result: {result}")
        return result
    
    async def get_open_orders(
        self,
        plugin_id: str,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of open orders for a plugin.
        
        Args:
            plugin_id: Plugin ID (required for isolation)
            symbol: Filter by symbol (None = all)
            
        Returns:
            List of order dictionaries
        """
        orders = self.database.get_open_orders(plugin_id, symbol)
        return [
            {
                "ticket": o.ticket,
                "symbol": o.symbol,
                "direction": o.direction,
                "lot_size": o.lot_size,
                "open_price": o.open_price,
                "sl_price": o.sl_price,
                "tp_price": o.tp_price,
                "comment": o.comment,
                "order_type": o.order_type,
                "created_at": o.created_at.isoformat()
            }
            for o in orders
        ]
    
    async def get_order_info(self, ticket: int, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific order.
        
        Args:
            ticket: Order ticket number
            plugin_id: Plugin ID for ownership verification
            
        Returns:
            dict: Order details or None if not found
        """
        order = self.database.get_order(ticket, plugin_id)
        if not order:
            return None
        
        current_profit = 0.0
        if self.mt5_client and order.status == OrderStatus.OPEN:
            position = self.mt5_client.get_position(ticket)
            if position:
                current_profit = position.get("profit", 0.0)
        
        return {
            "ticket": order.ticket,
            "plugin_id": order.plugin_id,
            "symbol": order.symbol,
            "direction": order.direction,
            "lot_size": order.lot_size,
            "open_price": order.open_price,
            "sl_price": order.sl_price,
            "tp_price": order.tp_price,
            "comment": order.comment,
            "status": order.status.value,
            "order_type": order.order_type,
            "magic_number": order.magic_number,
            "created_at": order.created_at.isoformat(),
            "closed_at": order.closed_at.isoformat() if order.closed_at else None,
            "close_price": order.close_price,
            "profit": order.profit,
            "current_profit": current_profit,
            "swap": order.swap,
            "commission": order.commission
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self.stats,
            "total_orders_in_db": len(self.database.orders),
            "open_orders": len(self.database.get_open_orders()),
            "plugins_tracked": len(self.plugin_magic_numbers)
        }
    
    def get_plugin_statistics(self, plugin_id: str) -> Dict[str, Any]:
        """Get statistics for a specific plugin."""
        orders = self.database.get_plugin_orders(plugin_id)
        open_orders = [o for o in orders if o.status == OrderStatus.OPEN]
        closed_orders = [o for o in orders if o.status == OrderStatus.CLOSED]
        total_profit = sum(o.profit or 0 for o in closed_orders)
        
        return {
            "plugin_id": plugin_id,
            "total_orders": len(orders),
            "open_orders": len(open_orders),
            "closed_orders": len(closed_orders),
            "total_profit": total_profit,
            "magic_number": self.plugin_magic_numbers.get(plugin_id)
        }
