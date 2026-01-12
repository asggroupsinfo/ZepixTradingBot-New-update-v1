"""
API Contracts - Service API Interface Definitions

Document 10: API Specifications
Defines the complete API contracts for all services with V3/V6 specific order routing.

Services:
- OrderExecutionService: V3 dual orders, V6 conditional orders
- RiskManagementService: Lot size calculation, daily limits
- TrendManagementService: V3 4-pillar MTF + V6 Trend Pulse
- ProfitBookingService: Partial profit booking, breakeven
- MarketDataService: Spread, price data
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class OrderType(Enum):
    """Order type enumeration."""
    ORDER_A = "ORDER_A"
    ORDER_B = "ORDER_B"
    DUAL = "DUAL"


class LogicRoute(Enum):
    """V3 logic route enumeration."""
    LOGIC1 = "LOGIC1"  # 5m scalp
    LOGIC2 = "LOGIC2"  # 15m intraday
    LOGIC3 = "LOGIC3"  # 1h swing


class MarketState(Enum):
    """V6 market state enumeration."""
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"


class IOrderExecutionService(ABC):
    """
    Order Execution Service API Contract.
    
    Provides methods for placing, modifying, and closing orders
    with V3/V6 specific routing.
    """
    
    # =========================================================================
    # V3-Specific: Dual Order Methods
    # =========================================================================
    
    @abstractmethod
    async def place_dual_orders_v3(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size_total: float,
        order_a_sl: float,
        order_a_tp: float,
        order_b_sl: float,
        order_b_tp: float,
        logic_route: str
    ) -> Tuple[int, int]:
        """
        Place V3 hybrid SL dual order system (Order A + Order B).
        
        V3 uses DIFFERENT SL for each order:
        - Order A: Smart SL from Pine Script
        - Order B: Fixed $10 SL
        
        Args:
            plugin_id: Plugin identifier (must be 'combined_v3')
            symbol: Trading symbol (e.g., 'XAUUSD')
            direction: Trade direction ('BUY' or 'SELL')
            lot_size_total: Total lot size (will be split 50/50)
            order_a_sl: Smart SL price for Order A
            order_a_tp: TP2 (extended target) for Order A
            order_b_sl: Fixed $10 SL price for Order B (DIFFERENT from order_a)
            order_b_tp: TP1 (closer target) for Order B
            logic_route: Logic route ('LOGIC1', 'LOGIC2', 'LOGIC3')
            
        Returns:
            Tuple of (order_a_ticket, order_b_ticket)
        """
        pass
    
    # =========================================================================
    # V6-Specific: Conditional Order Methods
    # =========================================================================
    
    @abstractmethod
    async def place_single_order_a(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str = "ORDER_A"
    ) -> int:
        """
        Place Order A ONLY (for 15M/1H V6 plugins).
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            direction: Trade direction
            lot_size: Lot size
            sl_price: Stop loss price
            tp_price: Take profit price
            comment: Order comment
            
        Returns:
            MT5 ticket number
        """
        pass
    
    @abstractmethod
    async def place_single_order_b(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str = "ORDER_B"
    ) -> int:
        """
        Place Order B ONLY (for 1M V6 plugin).
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            direction: Trade direction
            lot_size: Lot size (typically 0.5x for scalping)
            sl_price: Stop loss price
            tp_price: TP1 (quick exit target)
            comment: Order comment
            
        Returns:
            MT5 ticket number
        """
        pass
    
    @abstractmethod
    async def place_dual_orders_v6(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size_total: float,
        sl_price: float,
        tp1_price: float,
        tp2_price: float
    ) -> Tuple[int, int]:
        """
        Place DUAL orders for 5M V6 plugin.
        
        V6 uses SAME SL for both orders (different from V3).
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            direction: Trade direction
            lot_size_total: Total lot size
            sl_price: Same SL for both orders
            tp1_price: Order B target (closer)
            tp2_price: Order A target (extended)
            
        Returns:
            Tuple of (order_a_ticket, order_b_ticket)
        """
        pass
    
    # =========================================================================
    # Universal Order Methods (Both V3 & V6)
    # =========================================================================
    
    @abstractmethod
    async def modify_order(
        self,
        plugin_id: str,
        order_id: int,
        new_sl: Optional[float] = None,
        new_tp: Optional[float] = None
    ) -> bool:
        """
        Modify existing order SL/TP.
        
        Args:
            plugin_id: Plugin identifier
            order_id: MT5 order ticket
            new_sl: New stop loss price (optional)
            new_tp: New take profit price (optional)
            
        Returns:
            True if modification successful
        """
        pass
    
    @abstractmethod
    async def close_position(
        self,
        plugin_id: str,
        order_id: int,
        reason: str = "Manual"
    ) -> Dict[str, Any]:
        """
        Close entire position.
        
        Args:
            plugin_id: Plugin identifier
            order_id: MT5 order ticket
            reason: Close reason
            
        Returns:
            Dict with success, closed_volume, profit_pips, profit_dollars
        """
        pass
    
    @abstractmethod
    async def close_position_partial(
        self,
        plugin_id: str,
        order_id: int,
        percentage: float
    ) -> Dict[str, Any]:
        """
        Close partial position (for TP1/TP2/TP3).
        
        Args:
            plugin_id: Plugin identifier
            order_id: MT5 order ticket
            percentage: Percentage to close (25.0 = close 25%)
            
        Returns:
            Dict with closed_volume, remaining_volume, profit_pips, profit_dollars
        """
        pass
    
    @abstractmethod
    async def get_open_orders(
        self,
        plugin_id: str,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all open orders for this plugin.
        
        Args:
            plugin_id: Plugin identifier
            symbol: Optional symbol filter
            
        Returns:
            List of order dictionaries
        """
        pass


class IRiskManagementService(ABC):
    """
    Risk Management Service API Contract.
    
    Provides methods for lot size calculation and risk checks.
    """
    
    @abstractmethod
    async def calculate_lot_size(
        self,
        plugin_id: str,
        symbol: str,
        risk_percentage: float,
        stop_loss_pips: float,
        account_balance: Optional[float] = None
    ) -> float:
        """
        Calculate safe lot size based on risk.
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            risk_percentage: Risk percentage (e.g., 1.5)
            stop_loss_pips: Stop loss in pips
            account_balance: Account balance (auto-fetch if None)
            
        Returns:
            Calculated lot size
        """
        pass
    
    @abstractmethod
    async def check_daily_limit(
        self,
        plugin_id: str
    ) -> Dict[str, Any]:
        """
        Check if daily loss limit reached.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Dict with daily_loss, daily_limit, remaining, can_trade
        """
        pass
    
    @abstractmethod
    async def get_risk_tier(
        self,
        plugin_id: str
    ) -> Dict[str, Any]:
        """
        Get current risk tier for plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Dict with tier, risk_percentage, max_trades
        """
        pass


class ITrendManagementService(ABC):
    """
    Trend Management Service API Contract.
    
    Provides methods for both V3 4-pillar MTF and V6 Trend Pulse systems.
    """
    
    # =========================================================================
    # V3 Traditional Timeframe Trend Manager
    # =========================================================================
    
    @abstractmethod
    async def get_timeframe_trend(
        self,
        symbol: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Get V3 4-pillar MTF trend for a specific timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe ('15m', '1h', '4h', '1d' ONLY)
            
        Returns:
            Dict with timeframe, direction, value, last_updated
        """
        pass
    
    @abstractmethod
    async def get_mtf_trends(
        self,
        symbol: str
    ) -> Dict[str, int]:
        """
        Get ALL 4-pillar trends at once.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with 15m, 1h, 4h, 1d values (1=bullish, -1=bearish)
        """
        pass
    
    @abstractmethod
    async def validate_v3_trend_alignment(
        self,
        symbol: str,
        direction: str,
        min_aligned: int = 3
    ) -> bool:
        """
        Check if signal aligns with V3 4-pillar system.
        
        Args:
            symbol: Trading symbol
            direction: Trade direction ('BUY' or 'SELL')
            min_aligned: Minimum pillars that must align (default: 3)
            
        Returns:
            True if aligned
        """
        pass
    
    # =========================================================================
    # V6 Trend Pulse System
    # =========================================================================
    
    @abstractmethod
    async def update_trend_pulse(
        self,
        symbol: str,
        timeframe: str,
        bull_count: int,
        bear_count: int,
        market_state: str,
        changes: str
    ) -> None:
        """
        Update market_trends table with Trend Pulse alert data.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            bull_count: Bullish count
            bear_count: Bearish count
            market_state: Market state string
            changes: Which TFs changed
        """
        pass
    
    @abstractmethod
    async def get_market_state(
        self,
        symbol: str
    ) -> str:
        """
        Get current market state for symbol (V6).
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Market state string (TRENDING_BULLISH, TRENDING_BEARISH, SIDEWAYS, etc.)
        """
        pass
    
    @abstractmethod
    async def check_pulse_alignment(
        self,
        symbol: str,
        direction: str
    ) -> bool:
        """
        Check if signal aligns with Trend Pulse counts.
        
        Logic:
        - For BUY: bull_count > bear_count
        - For SELL: bear_count > bull_count
        
        Args:
            symbol: Trading symbol
            direction: Trade direction
            
        Returns:
            True if aligned
        """
        pass
    
    @abstractmethod
    async def get_pulse_data(
        self,
        symbol: str,
        timeframe: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get raw Trend Pulse counts.
        
        Args:
            symbol: Trading symbol
            timeframe: Optional specific timeframe
            
        Returns:
            Dict with timeframe -> {bull_count, bear_count}
        """
        pass


class IProfitBookingService(ABC):
    """
    Profit Booking Service API Contract.
    
    Provides methods for partial profit booking and breakeven.
    """
    
    @abstractmethod
    async def book_profit(
        self,
        plugin_id: str,
        order_id: int,
        percentage: float,
        reason: str = "TP1"
    ) -> Dict[str, Any]:
        """
        Book partial profit (TP1, TP2, TP3).
        
        Args:
            plugin_id: Plugin identifier
            order_id: MT5 order ticket
            percentage: Percentage to close (25.0, 50.0, 100.0)
            reason: Booking reason
            
        Returns:
            Dict with closed_volume, remaining_volume, profit_pips, profit_dollars
        """
        pass
    
    @abstractmethod
    async def move_to_breakeven(
        self,
        plugin_id: str,
        order_id: int,
        buffer_pips: float = 2.0
    ) -> bool:
        """
        Move SL to breakeven + buffer.
        
        Args:
            plugin_id: Plugin identifier
            order_id: MT5 order ticket
            buffer_pips: Buffer pips above breakeven
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def get_booking_history(
        self,
        plugin_id: str,
        order_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get profit booking history.
        
        Args:
            plugin_id: Plugin identifier
            order_id: Optional order filter
            
        Returns:
            List of booking records
        """
        pass


class IMarketDataService(ABC):
    """
    Market Data Service API Contract.
    
    Provides methods for market data access.
    """
    
    @abstractmethod
    async def get_current_spread(
        self,
        symbol: str
    ) -> float:
        """
        Get current spread in pips.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Spread in pips
        """
        pass
    
    @abstractmethod
    async def get_current_price(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Get current bid/ask prices.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with bid, ask, spread_pips
        """
        pass
    
    @abstractmethod
    async def get_symbol_info(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Get symbol information.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with pip_value, lot_step, min_lot, max_lot
        """
        pass


class IServiceAPI(ABC):
    """
    Unified Service API Interface.
    
    Provides access to all service APIs through a single interface.
    """
    
    @property
    @abstractmethod
    def orders(self) -> IOrderExecutionService:
        """Get order execution service."""
        pass
    
    @property
    @abstractmethod
    def risk(self) -> IRiskManagementService:
        """Get risk management service."""
        pass
    
    @property
    @abstractmethod
    def trend(self) -> ITrendManagementService:
        """Get trend management service."""
        pass
    
    @property
    @abstractmethod
    def profit(self) -> IProfitBookingService:
        """Get profit booking service."""
        pass
    
    @property
    @abstractmethod
    def market(self) -> IMarketDataService:
        """Get market data service."""
        pass
