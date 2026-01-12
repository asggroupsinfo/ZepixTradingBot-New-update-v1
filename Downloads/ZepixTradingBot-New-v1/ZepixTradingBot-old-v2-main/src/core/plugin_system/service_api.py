"""
Service API - V5 Hybrid Plugin Architecture

Unified interface for all services, providing plugins with controlled access
to trading functionality. Integrates OrderExecutionService, ProfitBookingService,
RiskManagementService, and TrendMonitorService.

Part of Document 05: Phase 3 Detailed Plan - Service API Layer

Features:
- Plugin-specific API instances with isolation
- Unified access to all 4 core services
- Backward compatibility with existing code
- Convenience methods for common operations
- Health monitoring and statistics
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ServiceAPI:
    """
    Unified Service API for plugins.
    
    Exposes core bot functionality to plugins in a safe, controlled manner.
    Acts as a facade over TradingEngine, Managers, and all 4 core services.
    
    Services Integrated:
    - OrderExecutionService: Order placement, modification, closing
    - ProfitBookingService: 5-level pyramid profit management
    - RiskManagementService: Lot sizing, daily limits, tier management
    - TrendMonitorService: MTF trend tracking, consensus scoring
    
    Usage:
        # Get plugin-specific API instance
        api = ServiceAPI.for_plugin("combined_v3", trading_engine)
        
        # Place order with plugin isolation
        ticket = await api.place_order("EURUSD", "BUY", 0.1, sl=1.0900)
        
        # Check risk before trading
        can_trade = api.check_daily_limit()
    """
    
    # Class-level service instances (shared across all plugins)
    _order_service = None
    _profit_service = None
    _risk_service = None
    _trend_service = None
    _initialized = False
    
    def __init__(self, trading_engine, plugin_id: str = "core"):
        """
        Initialize Service API.
        
        Args:
            trading_engine: TradingEngine instance
            plugin_id: Plugin identifier for isolation (default: "core")
        """
        self._engine = trading_engine
        self._config = trading_engine.config if hasattr(trading_engine, 'config') else {}
        self._mt5 = trading_engine.mt5_client if hasattr(trading_engine, 'mt5_client') else None
        self._risk = trading_engine.risk_manager if hasattr(trading_engine, 'risk_manager') else None
        self._telegram = trading_engine.telegram_bot if hasattr(trading_engine, 'telegram_bot') else None
        self._logger = logger
        self._plugin_id = plugin_id
        
        # Initialize services if not already done
        self._init_services()
    
    @classmethod
    def for_plugin(cls, plugin_id: str, trading_engine) -> 'ServiceAPI':
        """
        Create a plugin-specific ServiceAPI instance.
        
        Args:
            plugin_id: Plugin identifier
            trading_engine: TradingEngine instance
            
        Returns:
            ServiceAPI: Plugin-specific API instance
        """
        return cls(trading_engine, plugin_id)
    
    def _init_services(self):
        """Initialize service instances if not already done."""
        if ServiceAPI._initialized:
            return
        
        try:
            from src.services.order_execution import OrderExecutionService
            from src.services.profit_booking import ProfitBookingService
            from src.services.risk_management import RiskManagementService
            from src.services.trend_monitor import TrendMonitorService
            
            ServiceAPI._order_service = OrderExecutionService(self._mt5, self._config)
            ServiceAPI._profit_service = ProfitBookingService(self._mt5, self._config)
            ServiceAPI._risk_service = RiskManagementService(self._mt5, self._config)
            ServiceAPI._trend_service = TrendMonitorService(self._config)
            ServiceAPI._initialized = True
            
            self._logger.info("ServiceAPI: All services initialized")
        except ImportError as e:
            self._logger.warning(f"ServiceAPI: Could not import services: {e}")
        except Exception as e:
            self._logger.error(f"ServiceAPI: Error initializing services: {e}")
    
    @property
    def plugin_id(self) -> str:
        """Get the plugin ID for this API instance."""
        return self._plugin_id
    
    @property
    def order_service(self):
        """Get OrderExecutionService instance."""
        return ServiceAPI._order_service
    
    @property
    def profit_service(self):
        """Get ProfitBookingService instance."""
        return ServiceAPI._profit_service
    
    @property
    def risk_service(self):
        """Get RiskManagementService instance."""
        return ServiceAPI._risk_service
    
    @property
    def trend_service(self):
        """Get TrendMonitorService instance."""
        return ServiceAPI._trend_service

    # --- Market Data ---

    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        tick = self._mt5.get_symbol_tick(symbol)
        if tick:
            return tick['bid'] # Return bid by default or maybe close?
        return 0.0

    def get_symbol_info(self, symbol: str) -> Dict:
        """Get symbol validation info"""
        return self._mt5.get_symbol_info(symbol)

    # --- Account Info ---

    def get_balance(self) -> float:
        """Get current account balance"""
        return self._mt5.get_account_balance()
    
    def get_equity(self) -> float:
        """Get current account equity"""
        return self._mt5.get_account_equity()

    # --- Order Management ---

    def place_order(self, symbol: str, direction: str, lot_size: float, 
                   sl_price: float = 0.0, tp_price: float = 0.0, 
                   comment: str = "") -> Optional[int]:
        """
        Place a new order.
        direction: "BUY" or "SELL"
        """
        if not self._engine.trading_enabled:
            self._logger.warning("Trading is paused. Order rejected.")
            return None

        return self._mt5.place_order(
            symbol=symbol,
            order_type=direction.upper(),
            lot_size=lot_size,
            price=0.0, # Market order usually 0.0 or current Ask/Bid
            sl=sl_price,
            tp=tp_price,
            comment=comment
        )

    def close_trade(self, trade_id: int) -> bool:
        """Close an existing trade"""
        return self._mt5.close_position(trade_id)

    def modify_order(self, trade_id: int, sl: float = 0.0, tp: float = 0.0) -> bool:
        """Modify SL/TP of a trade"""
        return self._mt5.modify_position(trade_id, sl, tp)
    
    def get_open_trades(self) -> List[Any]:
        """Get list of ALL open trades"""
        return self._engine.get_open_trades()

    # --- Risk Management ---

    def calculate_lot_size(self, symbol: str, stop_loss_pips: float = 0.0) -> float:
        """Calculate recommended lot size based on risk settings"""
        balance = self.get_balance()
        # If the risk manager has a method for this, use it.
        # Check risk_manager.py: get_fixed_lot_size or calculate_lot_size
        if hasattr(self._risk, 'calculate_lot_size') and stop_loss_pips > 0:
             return self._risk.calculate_lot_size(balance, stop_loss_pips)
        return self._risk.get_fixed_lot_size(balance)

    # --- Communication ---

    def send_notification(self, message: str):
        """Send message via Telegram"""
        self._telegram.send_message(message)

    def log(self, message: str, level: str = "info"):
        """Log message"""
        if level.lower() == "error":
            self._logger.error(message)
        elif level.lower() == "warning":
            self._logger.warning(message)
        elif level.lower() == "debug":
            self._logger.debug(message)
        else:
            self._logger.info(message)
    
    # --- Configuration ---
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)
    
    # --- Plugin-Specific Convenience Methods ---
    
    async def place_plugin_order(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float = 0.0,
        tp_price: float = 0.0,
        comment: str = ""
    ) -> Optional[int]:
        """
        Place an order with plugin isolation.
        
        Uses OrderExecutionService with automatic plugin_id tagging.
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            lot_size: Lot size
            sl_price: Stop loss price
            tp_price: Take profit price
            comment: Order comment
            
        Returns:
            int: Order ticket or None if failed
        """
        if ServiceAPI._order_service:
            return await ServiceAPI._order_service.place_order(
                plugin_id=self._plugin_id,
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                sl_price=sl_price,
                tp_price=tp_price,
                comment=comment
            )
        return self.place_order(symbol, direction, lot_size, sl_price, tp_price, comment)
    
    async def place_dual_orders(
        self,
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
        Place dual orders (Order A + Order B) with plugin isolation.
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            lot_a: Lot size for Order A
            lot_b: Lot size for Order B
            sl_a: Stop loss for Order A
            sl_b: Stop loss for Order B
            tp_a: Take profit for Order A
            tp_b: Take profit for Order B
            comment_prefix: Comment prefix
            
        Returns:
            Tuple of (ticket_a, ticket_b)
        """
        if ServiceAPI._order_service:
            return await ServiceAPI._order_service.place_dual_orders(
                plugin_id=self._plugin_id,
                symbol=symbol,
                direction=direction,
                lot_a=lot_a,
                lot_b=lot_b,
                sl_a=sl_a,
                sl_b=sl_b,
                tp_a=tp_a,
                tp_b=tp_b,
                comment_prefix=comment_prefix
            )
        return (None, None)
    
    async def close_plugin_order(
        self,
        ticket: int,
        partial_volume: Optional[float] = None
    ) -> bool:
        """
        Close an order with plugin isolation verification.
        
        Args:
            ticket: Order ticket
            partial_volume: Optional partial close volume
            
        Returns:
            bool: True if closed successfully
        """
        if ServiceAPI._order_service:
            return await ServiceAPI._order_service.close_order(
                ticket=ticket,
                plugin_id=self._plugin_id,
                partial_volume=partial_volume
            )
        return self.close_trade(ticket)
    
    async def get_plugin_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders for this plugin only.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of order dictionaries
        """
        if ServiceAPI._order_service:
            return await ServiceAPI._order_service.get_open_orders(
                plugin_id=self._plugin_id,
                symbol=symbol
            )
        return []
    
    def check_daily_limit(self, balance: Optional[float] = None) -> Dict[str, Any]:
        """
        Check daily loss limit for this plugin.
        
        Args:
            balance: Optional account balance
            
        Returns:
            dict: Daily limit status with can_trade flag
        """
        if ServiceAPI._risk_service:
            return ServiceAPI._risk_service.check_daily_limit(
                plugin_id=self._plugin_id,
                balance=balance
            )
        return {"can_trade": True, "daily_loss": 0, "daily_limit": 0}
    
    def get_trend_consensus(self, symbol: str) -> Dict[str, Any]:
        """
        Get trend consensus score for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: Consensus analysis with score and direction
        """
        if ServiceAPI._trend_service:
            return ServiceAPI._trend_service.get_consensus_score(symbol)
        return {"consensus_score": 0, "direction": "UNKNOWN", "confidence": "LOW"}
    
    def check_trend_alignment(
        self,
        symbol: str,
        required_direction: str,
        min_timeframes: int = 3,
        min_score: int = 50
    ) -> Dict[str, Any]:
        """
        Check if trend alignment meets trading requirements.
        
        Args:
            symbol: Trading symbol
            required_direction: Required direction ("BULLISH" or "BEARISH")
            min_timeframes: Minimum aligned timeframes
            min_score: Minimum consensus score
            
        Returns:
            dict: Alignment check result with can_trade flag
        """
        if ServiceAPI._trend_service:
            return ServiceAPI._trend_service.check_trend_alignment(
                symbol=symbol,
                required_direction=required_direction,
                min_timeframes=min_timeframes,
                min_score=min_score
            )
        return {"can_trade": False, "direction_match": False}
    
    async def create_profit_chain(
        self,
        symbol: str,
        direction: str,
        base_lot: float,
        initial_order_ticket: Optional[int] = None
    ) -> str:
        """
        Create a profit booking chain for pyramid trading.
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            base_lot: Base lot size for pyramid
            initial_order_ticket: Optional initial order ticket
            
        Returns:
            str: Chain ID
        """
        if ServiceAPI._profit_service:
            return await ServiceAPI._profit_service.create_chain(
                plugin_id=self._plugin_id,
                symbol=symbol,
                direction=direction,
                base_lot=base_lot,
                initial_order_ticket=initial_order_ticket
            )
        return ""
    
    async def process_profit_level(
        self,
        chain_id: str,
        profit_amount: float,
        close_current_orders: bool = True
    ) -> Dict[str, Any]:
        """
        Process profit level advancement in a chain.
        
        Args:
            chain_id: Profit chain ID
            profit_amount: Profit amount to book
            close_current_orders: Whether to close current orders
            
        Returns:
            dict: Processing result
        """
        if ServiceAPI._profit_service:
            return await ServiceAPI._profit_service.process_profit_level(
                chain_id=chain_id,
                profit_amount=profit_amount,
                close_current_orders=close_current_orders
            )
        return {"success": False, "error": "Profit service not available"}
    
    # --- Health Monitoring ---
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Get health status of all services.
        
        Returns:
            dict: Health status for each service
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "plugin_id": self._plugin_id,
            "services": {}
        }
        
        if ServiceAPI._order_service:
            health["services"]["order_execution"] = {
                "status": "healthy",
                "statistics": ServiceAPI._order_service.get_statistics()
            }
        else:
            health["services"]["order_execution"] = {"status": "unavailable"}
        
        if ServiceAPI._profit_service:
            health["services"]["profit_booking"] = {
                "status": "healthy",
                "statistics": ServiceAPI._profit_service.get_plugin_statistics(self._plugin_id)
            }
        else:
            health["services"]["profit_booking"] = {"status": "unavailable"}
        
        if ServiceAPI._risk_service:
            health["services"]["risk_management"] = {
                "status": "healthy",
                "daily_limit": ServiceAPI._risk_service.check_daily_limit(self._plugin_id)
            }
        else:
            health["services"]["risk_management"] = {"status": "unavailable"}
        
        if ServiceAPI._trend_service:
            health["services"]["trend_monitor"] = {
                "status": "healthy",
                "service_status": ServiceAPI._trend_service.get_service_status()
            }
        else:
            health["services"]["trend_monitor"] = {"status": "unavailable"}
        
        return health
    
    def get_plugin_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for this plugin across all services.
        
        Returns:
            dict: Plugin-specific statistics
        """
        stats = {
            "plugin_id": self._plugin_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if ServiceAPI._order_service:
            stats["orders"] = ServiceAPI._order_service.get_plugin_statistics(self._plugin_id)
        
        if ServiceAPI._profit_service:
            stats["profit_chains"] = ServiceAPI._profit_service.get_plugin_statistics(self._plugin_id)
        
        if ServiceAPI._risk_service:
            stats["risk"] = ServiceAPI._risk_service.check_daily_limit(self._plugin_id)
        
        return stats
    
    @classmethod
    def reset_services(cls):
        """Reset all service instances (for testing)."""
        cls._order_service = None
        cls._profit_service = None
        cls._risk_service = None
        cls._trend_service = None
        cls._initialized = False
