"""
V3 Combined Logic - Routing Logic Module

Implements 2-tier routing system for V3 signals:
1. Priority 1: Signal Type Override
2. Priority 2: Timeframe Routing

Part of Document 06: Phase 4 - V3 Plugin Migration
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class V3RoutingLogic:
    """
    2-Tier routing: Signal Override -> Timeframe Routing.
    
    Priority 1: Signal Type Override
    - Screener_Full_Bullish -> LOGIC3
    - Screener_Full_Bearish -> LOGIC3
    - Golden_Pocket_Flip_1H -> LOGIC3
    - Golden_Pocket_Flip_4H -> LOGIC3
    
    Priority 2: Timeframe Routing
    - 5m -> LOGIC1 (Scalping, 1.25x multiplier)
    - 15m -> LOGIC2 (Intraday, 1.0x multiplier)
    - 60m/240m -> LOGIC3 (Swing, 0.625x multiplier)
    
    Default: LOGIC2
    """
    
    # Signal type overrides (Priority 1)
    SIGNAL_OVERRIDES = {
        'Screener_Full_Bullish': 'LOGIC3',
        'Screener_Full_Bearish': 'LOGIC3',
        'Golden_Pocket_Flip_1H': 'LOGIC3',
        'Golden_Pocket_Flip_4H': 'LOGIC3'
    }
    
    # Timeframe routing (Priority 2)
    TIMEFRAME_ROUTING = {
        '1': 'LOGIC1',
        '5': 'LOGIC1',
        '1M': 'LOGIC1',
        '5M': 'LOGIC1',
        '15': 'LOGIC2',
        '15M': 'LOGIC2',
        '60': 'LOGIC3',
        '1H': 'LOGIC3',
        '240': 'LOGIC3',
        '4H': 'LOGIC3',
        'D1': 'LOGIC3',
        '1440': 'LOGIC3'
    }
    
    # Default logic route
    DEFAULT_LOGIC = 'LOGIC2'
    
    # Logic multipliers for lot sizing
    LOGIC_MULTIPLIERS = {
        'LOGIC1': 1.25,   # Scalping - larger lots, tighter SL
        'LOGIC2': 1.0,    # Intraday - balanced
        'LOGIC3': 0.625   # Swing - smaller lots, wider SL
    }
    
    # SL multipliers per logic type
    SL_MULTIPLIERS = {
        'LOGIC1': 1.0,    # Base SL
        'LOGIC2': 1.5,    # 1.5x base SL
        'LOGIC3': 2.0     # 2x base SL
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize V3 Routing Logic.
        
        Args:
            config: Plugin configuration (optional)
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.V3RoutingLogic")
        
        # Load overrides from config if provided
        if config:
            signal_routing = config.get('signal_routing', {})
            if signal_routing.get('signal_overrides'):
                self.SIGNAL_OVERRIDES.update(signal_routing['signal_overrides'])
            if signal_routing.get('timeframe_routing'):
                self.TIMEFRAME_ROUTING.update(signal_routing['timeframe_routing'])
            if signal_routing.get('default_logic'):
                self.DEFAULT_LOGIC = signal_routing['default_logic']
            
            logic_multipliers = config.get('logic_multipliers', {})
            if logic_multipliers:
                self.LOGIC_MULTIPLIERS.update(logic_multipliers)
        
        self.logger.info("V3RoutingLogic initialized")
    
    def determine_logic_route(
        self,
        alert: Any,
        signal_type: str
    ) -> str:
        """
        Determine logic route for signal.
        
        Uses 2-tier priority system:
        1. Check signal type override
        2. Check timeframe routing
        3. Fall back to default
        
        Args:
            alert: V3 alert data
            signal_type: Signal type string
            
        Returns:
            str: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
        """
        # Priority 1: Check signal type override
        if signal_type in self.SIGNAL_OVERRIDES:
            route = self.SIGNAL_OVERRIDES[signal_type]
            self.logger.debug(f"Signal override: {signal_type} -> {route}")
            return route
        
        # Priority 2: Check timeframe routing
        timeframe = self._get_timeframe(alert)
        if timeframe in self.TIMEFRAME_ROUTING:
            route = self.TIMEFRAME_ROUTING[timeframe]
            self.logger.debug(f"TF routing: {timeframe} -> {route}")
            return route
        
        # Default
        self.logger.debug(f"Default routing -> {self.DEFAULT_LOGIC}")
        return self.DEFAULT_LOGIC
    
    def get_logic_multiplier(self, logic_route: str) -> float:
        """
        Get lot size multiplier for given logic route.
        
        Args:
            logic_route: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
            
        Returns:
            float: Multiplier value
        """
        return self.LOGIC_MULTIPLIERS.get(logic_route, 1.0)
    
    def get_sl_multiplier(self, logic_route: str) -> float:
        """
        Get SL multiplier for given logic route.
        
        Args:
            logic_route: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
            
        Returns:
            float: SL multiplier value
        """
        return self.SL_MULTIPLIERS.get(logic_route, 1.0)
    
    def get_route_info(self, logic_route: str) -> Dict[str, Any]:
        """
        Get complete routing information for a logic route.
        
        Args:
            logic_route: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
            
        Returns:
            dict: Route information
        """
        route_names = {
            'LOGIC1': 'Scalping',
            'LOGIC2': 'Intraday',
            'LOGIC3': 'Swing'
        }
        
        return {
            'route': logic_route,
            'name': route_names.get(logic_route, 'Unknown'),
            'lot_multiplier': self.get_logic_multiplier(logic_route),
            'sl_multiplier': self.get_sl_multiplier(logic_route)
        }
    
    def is_signal_override(self, signal_type: str) -> bool:
        """
        Check if signal type has a routing override.
        
        Args:
            signal_type: Signal type string
            
        Returns:
            bool: True if override exists
        """
        return signal_type in self.SIGNAL_OVERRIDES
    
    def get_timeframe_logic(self, timeframe: str) -> str:
        """
        Get logic route for a specific timeframe.
        
        Args:
            timeframe: Timeframe string
            
        Returns:
            str: Logic route
        """
        return self.TIMEFRAME_ROUTING.get(timeframe, self.DEFAULT_LOGIC)
    
    def _get_timeframe(self, alert: Any) -> str:
        """
        Extract timeframe from alert.
        
        Args:
            alert: V3 alert data
            
        Returns:
            str: Timeframe string
        """
        if isinstance(alert, dict):
            return str(alert.get('tf', alert.get('timeframe', '15')))
        return str(getattr(alert, 'tf', getattr(alert, 'timeframe', '15')))
    
    def validate_route(self, logic_route: str) -> bool:
        """
        Validate that a logic route is valid.
        
        Args:
            logic_route: Route to validate
            
        Returns:
            bool: True if valid
        """
        return logic_route in ['LOGIC1', 'LOGIC2', 'LOGIC3']
    
    def get_all_routes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all logic routes.
        
        Returns:
            dict: All route information
        """
        return {
            'LOGIC1': self.get_route_info('LOGIC1'),
            'LOGIC2': self.get_route_info('LOGIC2'),
            'LOGIC3': self.get_route_info('LOGIC3')
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get routing configuration statistics.
        
        Returns:
            dict: Configuration stats
        """
        return {
            'signal_overrides': len(self.SIGNAL_OVERRIDES),
            'timeframe_routes': len(self.TIMEFRAME_ROUTING),
            'default_logic': self.DEFAULT_LOGIC,
            'logic_multipliers': self.LOGIC_MULTIPLIERS,
            'sl_multipliers': self.SL_MULTIPLIERS
        }
