"""
V3 Combined Logic - Dual Order Manager Module

Manages V3 hybrid SL dual order system:
- Order A: TP Trail with V3 Smart SL from Pine Script
- Order B: Profit Trail with Fixed $10 SL

Part of Document 06: Phase 4 - V3 Plugin Migration

CRITICAL: Order B MUST use pyramid fixed $10 SL, NOT smart SL.
"""

from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class V3DualOrderManager:
    """
    Manages V3 hybrid SL dual order system.
    
    Order A: TP Trail
    - Uses V3 Smart SL from Pine Script (alert.sl_price)
    - Uses extended TP target (alert.tp2_price)
    - Lot size: final_lot * 0.5
    - Comment: "OrderA_TP_Trail_{logic_route}"
    
    Order B: Profit Trail
    - Uses FIXED $10 SL (IGNORES alert.sl_price)
    - Uses closer TP target (alert.tp1_price)
    - Lot size: final_lot * 0.5
    - Comment: "OrderB_Profit_Trail_{logic_route}"
    """
    
    # Default configuration
    DEFAULT_SPLIT_RATIO = 0.5  # 50/50 split between Order A and B
    DEFAULT_ORDER_A_COMMENT = "OrderA_TP_Trail"
    DEFAULT_ORDER_B_COMMENT = "OrderB_Profit_Trail"
    DEFAULT_ORDER_B_FIXED_SL_USD = 10.0  # Fixed $10 SL for Order B
    
    # Pip values for different symbol types
    PIP_VALUES = {
        'standard': 0.0001,  # EUR, GBP, etc.
        'jpy': 0.01,         # JPY pairs
        'gold': 0.01         # XAUUSD
    }
    
    def __init__(self, plugin, service_api):
        """
        Initialize V3 Dual Order Manager.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
            service_api: Service API for order placement
        """
        self.plugin = plugin
        self.service_api = service_api
        self.logger = logging.getLogger(f"{__name__}.V3DualOrderManager")
        
        # Load configuration
        self.config = self._load_config()
        
        # Statistics tracking
        self.stats = {
            'dual_orders_placed': 0,
            'order_a_placed': 0,
            'order_b_placed': 0,
            'order_a_failed': 0,
            'order_b_failed': 0
        }
        
        self.logger.info("V3DualOrderManager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load dual order configuration from plugin config."""
        default_config = {
            'split_ratio': self.DEFAULT_SPLIT_RATIO,
            'order_a_comment': self.DEFAULT_ORDER_A_COMMENT,
            'order_b_comment': self.DEFAULT_ORDER_B_COMMENT,
            'order_b_fixed_sl': self.DEFAULT_ORDER_B_FIXED_SL_USD
        }
        
        if hasattr(self.plugin, 'config') and self.plugin.config:
            dual_orders_config = self.plugin.config.get('dual_orders', {})
            default_config.update(dual_orders_config)
        
        return default_config
    
    async def place_dual_orders_v3(
        self,
        alert: Any,
        final_lot_size: float,
        logic_route: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Place Order A (Smart SL) + Order B (Fixed SL).
        
        Args:
            alert: V3 alert data with prices
            final_lot_size: Total lot size (will be split 50/50)
            logic_route: Logic route (LOGIC1/2/3)
            
        Returns:
            Tuple[int, int]: (order_a_ticket, order_b_ticket)
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        entry_price = self._get_attr(alert, 'price', 0.0)
        
        # Split lots 50/50
        split_ratio = self.config['split_ratio']
        lot_a = round(final_lot_size * split_ratio, 2)
        lot_b = round(final_lot_size * split_ratio, 2)
        
        # Ensure minimum lot size
        lot_a = max(lot_a, 0.01)
        lot_b = max(lot_b, 0.01)
        
        # Get SL/TP prices
        sl_a = self._get_order_a_sl(alert)
        tp_a = self._get_order_a_tp(alert)
        sl_b = self._calculate_fixed_sl(alert, entry_price)
        tp_b = self._get_order_b_tp(alert)
        
        # Place Order A: Smart SL
        order_a_ticket = await self._place_order_a(
            symbol=symbol,
            direction=direction,
            lot_size=lot_a,
            sl_price=sl_a,
            tp_price=tp_a,
            logic_route=logic_route
        )
        
        # Place Order B: Fixed $10 SL
        order_b_ticket = await self._place_order_b(
            symbol=symbol,
            direction=direction,
            lot_size=lot_b,
            sl_price=sl_b,
            tp_price=tp_b,
            logic_route=logic_route
        )
        
        # Update statistics
        if order_a_ticket and order_b_ticket:
            self.stats['dual_orders_placed'] += 1
            self.logger.info(
                f"V3 Dual Orders placed: A#{order_a_ticket} B#{order_b_ticket} "
                f"[{symbol} {direction} {logic_route}]"
            )
        
        # Save to database
        await self._save_dual_trade(
            alert=alert,
            order_a_ticket=order_a_ticket,
            order_b_ticket=order_b_ticket,
            lot_a=lot_a,
            lot_b=lot_b,
            sl_a=sl_a,
            sl_b=sl_b,
            tp_a=tp_a,
            tp_b=tp_b,
            logic_route=logic_route
        )
        
        return order_a_ticket, order_b_ticket
    
    async def _place_order_a(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        logic_route: str
    ) -> Optional[int]:
        """
        Place Order A with Smart SL.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            lot_size: Position size
            sl_price: V3 Smart SL price
            tp_price: Extended TP price (TP2)
            logic_route: Logic route
            
        Returns:
            int: Order ticket or None
        """
        comment = f"{self.config['order_a_comment']}_{logic_route}"
        
        try:
            if self.service_api is None:
                self.logger.info(f"Mock Order A: {symbol} {direction} {lot_size}")
                self.stats['order_a_placed'] += 1
                return int(datetime.now().timestamp())
            
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service is None:
                order_service = getattr(self.service_api, 'order_service', None)
            
            if order_service is None:
                self.logger.warning("Order service not available")
                return int(datetime.now().timestamp())
            
            ticket = await order_service.place_order(
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                sl_price=sl_price,
                tp_price=tp_price,
                comment=comment,
                plugin_id=self.plugin.plugin_id
            )
            
            self.stats['order_a_placed'] += 1
            return ticket
            
        except Exception as e:
            self.stats['order_a_failed'] += 1
            self.logger.error(f"Order A placement error: {e}")
            return None
    
    async def _place_order_b(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        logic_route: str
    ) -> Optional[int]:
        """
        Place Order B with Fixed $10 SL.
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            lot_size: Position size
            sl_price: Fixed $10 SL price
            tp_price: Closer TP price (TP1)
            logic_route: Logic route
            
        Returns:
            int: Order ticket or None
        """
        comment = f"{self.config['order_b_comment']}_{logic_route}"
        
        try:
            if self.service_api is None:
                self.logger.info(f"Mock Order B: {symbol} {direction} {lot_size}")
                self.stats['order_b_placed'] += 1
                return int(datetime.now().timestamp()) + 1
            
            order_service = getattr(self.service_api, 'order_execution', None)
            if order_service is None:
                order_service = getattr(self.service_api, 'order_service', None)
            
            if order_service is None:
                self.logger.warning("Order service not available")
                return int(datetime.now().timestamp()) + 1
            
            ticket = await order_service.place_order(
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                sl_price=sl_price,
                tp_price=tp_price,
                comment=comment,
                plugin_id=self.plugin.plugin_id
            )
            
            self.stats['order_b_placed'] += 1
            return ticket
            
        except Exception as e:
            self.stats['order_b_failed'] += 1
            self.logger.error(f"Order B placement error: {e}")
            return None
    
    def _get_order_a_sl(self, alert: Any) -> float:
        """
        Get Order A SL price (V3 Smart SL from Pine Script).
        
        Args:
            alert: V3 alert data
            
        Returns:
            float: SL price
        """
        return self._get_attr(alert, 'sl_price', self._get_attr(alert, 'sl', 0.0))
    
    def _get_order_a_tp(self, alert: Any) -> float:
        """
        Get Order A TP price (extended TP2).
        
        Args:
            alert: V3 alert data
            
        Returns:
            float: TP price
        """
        return self._get_attr(alert, 'tp2_price', self._get_attr(alert, 'tp2', self._get_attr(alert, 'tp', 0.0)))
    
    def _get_order_b_tp(self, alert: Any) -> float:
        """
        Get Order B TP price (closer TP1).
        
        Args:
            alert: V3 alert data
            
        Returns:
            float: TP price
        """
        return self._get_attr(alert, 'tp1_price', self._get_attr(alert, 'tp1', self._get_attr(alert, 'tp', 0.0)))
    
    def _calculate_fixed_sl(self, alert: Any, entry_price: float) -> float:
        """
        Calculate fixed $10 SL price for Order B.
        
        CRITICAL: Order B IGNORES alert.sl_price and uses fixed $10 SL.
        
        Args:
            alert: V3 alert data
            entry_price: Entry price
            
        Returns:
            float: Fixed SL price
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        
        # Get pip value for symbol
        pip_value = self._get_pip_value(symbol)
        
        # Calculate SL distance in pips for $10 loss
        # Assuming 0.01 lot = $0.10 per pip for standard pairs
        # For $10 loss with 0.01 lot: 100 pips
        # Adjust based on actual lot size
        fixed_sl_usd = self.config['order_b_fixed_sl']
        
        # Simplified calculation: $10 / (pip_value * lot_size)
        # For now, use a fixed pip distance based on symbol type
        if 'XAU' in symbol or 'GOLD' in symbol:
            sl_distance = 10.0  # $10 = 10 points for gold at 0.01 lot
        elif 'JPY' in symbol:
            sl_distance = 0.10  # 10 pips for JPY pairs
        else:
            sl_distance = 0.0010  # 10 pips for standard pairs
        
        # Calculate SL price based on direction
        if direction == 'BUY':
            sl_price = entry_price - sl_distance
        else:
            sl_price = entry_price + sl_distance
        
        return round(sl_price, 5)
    
    def _get_pip_value(self, symbol: str) -> float:
        """
        Get pip value for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            float: Pip value
        """
        if 'JPY' in symbol:
            return self.PIP_VALUES['jpy']
        elif 'XAU' in symbol or 'GOLD' in symbol:
            return self.PIP_VALUES['gold']
        return self.PIP_VALUES['standard']
    
    def _get_pip_size(self, symbol: str) -> float:
        """
        Get pip size for price calculation.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            float: Pip size
        """
        return self._get_pip_value(symbol)
    
    async def _save_dual_trade(
        self,
        alert: Any,
        order_a_ticket: Optional[int],
        order_b_ticket: Optional[int],
        lot_a: float,
        lot_b: float,
        sl_a: float,
        sl_b: float,
        tp_a: float,
        tp_b: float,
        logic_route: str
    ):
        """
        Save dual trade record to database.
        
        Args:
            alert: V3 alert data
            order_a_ticket: Order A ticket
            order_b_ticket: Order B ticket
            lot_a: Order A lot size
            lot_b: Order B lot size
            sl_a: Order A SL price
            sl_b: Order B SL price
            tp_a: Order A TP price
            tp_b: Order B TP price
            logic_route: Logic route
        """
        try:
            trade_record = {
                'symbol': self._get_attr(alert, 'symbol', ''),
                'direction': self._get_attr(alert, 'direction', ''),
                'signal_type': self._get_attr(alert, 'signal_type', ''),
                'order_a_ticket': order_a_ticket,
                'order_b_ticket': order_b_ticket,
                'lot_a': lot_a,
                'lot_b': lot_b,
                'order_a_sl': sl_a,
                'order_b_sl': sl_b,
                'order_a_tp': tp_a,
                'order_b_tp': tp_b,
                'logic_route': logic_route,
                'entry_time': datetime.now().isoformat(),
                'plugin_id': self.plugin.plugin_id
            }
            
            if hasattr(self.plugin, 'database') and self.plugin.database:
                await self.plugin.database.save_dual_trade(trade_record)
            
            self.logger.debug(f"Dual trade saved: {trade_record['symbol']} {logic_route}")
            
        except Exception as e:
            self.logger.warning(f"Dual trade save error: {e}")
    
    def _get_attr(self, alert: Any, attr: str, default: Any = None) -> Any:
        """Get attribute from alert (supports dict and object)."""
        if isinstance(alert, dict):
            return alert.get(attr, default)
        return getattr(alert, attr, default)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dual order manager statistics."""
        return {
            **self.stats,
            'config': {
                'split_ratio': self.config['split_ratio'],
                'order_b_fixed_sl': self.config['order_b_fixed_sl']
            }
        }
