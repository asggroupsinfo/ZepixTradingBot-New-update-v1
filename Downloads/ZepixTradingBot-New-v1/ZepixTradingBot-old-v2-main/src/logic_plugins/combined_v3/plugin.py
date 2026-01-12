"""
V3 Combined Logic Plugin - V5 Hybrid Plugin Architecture

Main plugin class for V3 Combined Logic trading strategy.
Complete implementation as per Document 06: Phase 4 - V3 Plugin Migration.

Features:
- 12 signal types (7 entry, 2 exit, 2 info, 1 trend pulse)
- 3 logic routes (LOGIC1, LOGIC2, LOGIC3)
- Dual order system (Order A + Order B)
- Hybrid SL management (Smart SL + Fixed $10 SL)
- MTF 4-pillar trend validation
- 4-step position sizing
- 100% backward compatibility with V2 code
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from src.core.plugin_system.base_plugin import BaseLogicPlugin
from .signal_handlers import V3SignalHandlers
from .routing_logic import V3RoutingLogic
from .dual_order_manager import V3DualOrderManager
from .mtf_processor import V3MTFProcessor
from .position_sizer import V3PositionSizer
from .entry_logic import EntryLogic
from .exit_logic import ExitLogic

logger = logging.getLogger(__name__)


class CombinedV3Plugin(BaseLogicPlugin):
    """
    V3 Combined Logic Plugin.
    
    Implements the complete V3 trading strategy with:
    - 12 signal types
    - 3 logic routes (LOGIC1, LOGIC2, LOGIC3)
    - Dual order system (Order A + Order B)
    - Hybrid SL management
    - MTF 4-pillar trend validation
    - 4-step position sizing
    
    Signal Types:
    Entry Signals (7):
    1. Institutional_Launchpad
    2. Liquidity_Trap
    3. Momentum_Breakout
    4. Mitigation_Test
    5. Golden_Pocket_Flip
    6. Screener_Full_Bullish/Bearish (9/10)
    7. Sideways_Breakout (12 - BONUS)
    
    Exit Signals (2):
    - Bullish_Exit (Signal 7)
    - Bearish_Exit (Signal 8)
    
    Info Signals (2):
    - Volatility_Squeeze (Signal 6)
    - Trend_Pulse (Signal 11)
    
    Logic Routes:
    - LOGIC1: 5-minute scalping (SL multiplier: 1.0x)
    - LOGIC2: 15-minute intraday (SL multiplier: 1.5x)
    - LOGIC3: 1-hour swing (SL multiplier: 2.0x)
    
    Order Types:
    - Order A: TP Trail with V3 Smart SL from Pine Script
    - Order B: Profit Trail with Fixed $10 SL (2.0x Order A lot)
    """
    
    # Plugin metadata
    PLUGIN_ID = "combined_v3"
    VERSION = "3.1.0"  # Updated for Document 06 implementation
    DESCRIPTION = "V3 Combined Logic - 12 signals, 3 logics, dual orders, MTF 4-pillar"
    
    # Signal type constants (Document 06 specification)
    ENTRY_SIGNALS = [
        "Institutional_Launchpad",
        "Liquidity_Trap",
        "Momentum_Breakout",
        "Mitigation_Test",
        "Golden_Pocket_Flip",
        "Golden_Pocket_Flip_1H",
        "Golden_Pocket_Flip_4H",
        "Screener_Full_Bullish",
        "Screener_Full_Bearish",
        "Sideways_Breakout",
        # Legacy signal names for backward compatibility
        "Liquidity_Trap_Reversal",
        "Confluence_Entry",
        "Breakout_Entry",
        "Pullback_Entry"
    ]
    
    EXIT_SIGNALS = [
        "Bullish_Exit",
        "Bearish_Exit",
        # Legacy signal names for backward compatibility
        "Exit_Appeared",
        "Reversal_Exit"
    ]
    
    INFO_SIGNALS = [
        "Volatility_Squeeze",
        "Trend_Pulse",
        # Legacy signal names for backward compatibility
        "Squeeze_Alert"
    ]
    
    # Aggressive reversal signals (bypass trend check)
    AGGRESSIVE_REVERSAL_SIGNALS = [
        "Liquidity_Trap",
        "Liquidity_Trap_Reversal",
        "Golden_Pocket_Flip",
        "Golden_Pocket_Flip_1H",
        "Golden_Pocket_Flip_4H",
        "Screener_Full_Bullish",
        "Screener_Full_Bearish"
    ]
    
    # Logic type constants
    LOGIC_TYPES = ["LOGIC1", "LOGIC2", "LOGIC3"]
    
    # SL multipliers per logic type (Document 06 specification)
    SL_MULTIPLIERS = {
        "LOGIC1": 1.0,   # Base SL
        "LOGIC2": 1.5,   # 1.5x base SL
        "LOGIC3": 2.0    # 2x base SL
    }
    
    # Order B lot multiplier (relative to Order A)
    ORDER_B_MULTIPLIER = 2.0
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """
        Initialize V3 Combined Logic Plugin.
        
        Args:
            plugin_id: Plugin identifier
            config: Plugin configuration
            service_api: Shared services API
        """
        super().__init__(plugin_id, config, service_api)
        
        # Override metadata
        self.metadata = {
            "version": self.VERSION,
            "author": "Zepix Team",
            "description": self.DESCRIPTION,
            "signals": 12,
            "supported_signals": self.ENTRY_SIGNALS + self.EXIT_SIGNALS + self.INFO_SIGNALS
        }
        
        # Initialize V3 components (Document 06 modules)
        self.signal_handlers = V3SignalHandlers(self)
        self.routing = V3RoutingLogic(self.config)
        self.dual_orders = V3DualOrderManager(self, service_api)
        self.mtf_processor = V3MTFProcessor(self)
        self.position_sizer = V3PositionSizer(self.config)
        
        # Initialize legacy entry/exit logic for backward compatibility
        self.entry_logic = EntryLogic(self)
        self.exit_logic = ExitLogic(self)
        
        # Plugin-specific state
        self.active_sessions: Dict[str, Dict] = {}
        self.active_chains: Dict[str, Dict] = {}
        self.shadow_mode = self.config.get('shadow_mode', False)
        
        # Statistics tracking
        self.stats = {
            'entries_processed': 0,
            'exits_processed': 0,
            'reversals_processed': 0,
            'trend_pulses_processed': 0,
            'dual_orders_placed': 0,
            'errors': 0
        }
        
        # Initialize V3 database tables
        self._initialize_v3_database()
        
        self.logger.info(f"CombinedV3Plugin initialized: {self.VERSION} - 12 signals ready")
    
    def _initialize_v3_database(self):
        """Initialize V3-specific database tables."""
        try:
            db = self.get_database_connection()
            if db:
                # V3 dual trades table
                db.execute('''
                    CREATE TABLE IF NOT EXISTS v3_dual_trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        signal_type TEXT NOT NULL,
                        logic_route TEXT NOT NULL,
                        order_a_ticket INTEGER,
                        order_b_ticket INTEGER,
                        lot_a REAL,
                        lot_b REAL,
                        sl_a REAL,
                        sl_b REAL,
                        tp_a REAL,
                        tp_b REAL,
                        entry_time TEXT,
                        exit_time TEXT,
                        pnl_a REAL,
                        pnl_b REAL,
                        status TEXT DEFAULT 'open',
                        plugin_id TEXT
                    )
                ''')
                
                # V3 MTF trends table
                db.execute('''
                    CREATE TABLE IF NOT EXISTS v3_mtf_trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        updated_at TEXT,
                        UNIQUE(symbol, timeframe)
                    )
                ''')
                
                db.commit()
                self.logger.debug("V3 database tables initialized")
        except Exception as e:
            self.logger.warning(f"V3 database initialization error: {e}")
    
    async def on_signal_received(self, signal_data: Any) -> Optional[Dict[str, Any]]:
        """
        Main signal routing for V3.
        
        Routes signals to appropriate handlers based on signal type.
        
        Args:
            signal_data: V3 signal data
            
        Returns:
            dict: Processing result or None
        """
        signal_type = self._get_signal_type(signal_data)
        
        if not signal_type:
            self.logger.warning("Signal missing signal_type")
            return None
        
        # Route to signal handlers
        return await self.signal_handlers.route_signal(signal_data)
    
    async def process_v3_entry(
        self,
        alert: Any,
        signal_type: str
    ) -> Dict[str, Any]:
        """
        Main V3 entry processing pipeline.
        
        Steps:
        1. Determine logic route (2-tier: signal override -> TF routing)
        2. Check trend alignment (unless bypassed)
        3. Calculate lot size (4-step flow)
        4. Place dual orders (Order A + Order B)
        
        Args:
            alert: V3 alert data
            signal_type: Signal type string
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        
        self.logger.info(f"V3 Entry: {symbol} {direction} [{signal_type}]")
        
        try:
            # Step 1: Determine logic route (2-tier routing)
            logic_route = self.routing.determine_logic_route(alert, signal_type)
            logic_mult = self.routing.get_logic_multiplier(logic_route)
            sl_mult = self.routing.get_sl_multiplier(logic_route)
            
            self.logger.debug(f"Route: {logic_route} (lot_mult={logic_mult}, sl_mult={sl_mult})")
            
            # Step 2: Check trend alignment (unless bypassed)
            if not self._should_bypass_trend(alert, signal_type):
                trend_aligned = await self.mtf_processor.validate_trend_alignment(alert)
                if not trend_aligned:
                    self.logger.info(f"V3 Entry skipped: trend misalignment for {symbol}")
                    return {
                        "success": False,
                        "reason": "trend_misalignment",
                        "symbol": symbol,
                        "direction": direction,
                        "signal_type": signal_type
                    }
            
            # Step 3: Calculate lot size (4-step flow)
            final_lot = self.position_sizer.calculate_v3_lot_size(alert, logic_mult)
            
            # Step 4: Place dual orders
            order_a, order_b = await self.dual_orders.place_dual_orders_v3(
                alert, final_lot, logic_route
            )
            
            # Update statistics
            self.stats['entries_processed'] += 1
            if order_a and order_b:
                self.stats['dual_orders_placed'] += 1
            
            self.logger.info(
                f"V3 Entry complete: {symbol} {direction} [{signal_type}] -> {logic_route} "
                f"A#{order_a} B#{order_b}"
            )
            
            return {
                "success": True,
                "plugin_id": self.plugin_id,
                "symbol": symbol,
                "direction": direction,
                "signal_type": signal_type,
                "logic_route": logic_route,
                "order_a": order_a,
                "order_b": order_b,
                "lot_size": final_lot,
                "sl_multiplier": sl_mult
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"V3 Entry error: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol,
                "signal_type": signal_type
            }
    
    async def process_v3_exit(
        self,
        alert: Any,
        exit_type: str
    ) -> Dict[str, Any]:
        """
        Process V3 exit signal.
        
        Args:
            alert: V3 exit alert data
            exit_type: 'bullish' or 'bearish'
            
        Returns:
            dict: Exit result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        
        self.logger.info(f"V3 Exit: {symbol} [{exit_type}]")
        
        try:
            # Use exit logic module
            result = await self.exit_logic.process_exit(alert)
            
            self.stats['exits_processed'] += 1
            
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"V3 Exit error: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    def _get_signal_type(self, alert: Any) -> Optional[str]:
        """Get signal type from alert."""
        return self._get_attr(alert, 'signal_type', None)
    
    def _get_attr(self, alert: Any, attr: str, default: Any = None) -> Any:
        """Get attribute from alert (supports dict and object)."""
        if isinstance(alert, dict):
            return alert.get(attr, default)
        return getattr(alert, attr, default)
    
    def _should_bypass_trend(self, alert: Any, signal_type: str) -> bool:
        """
        Check if trend validation should be bypassed.
        
        V3 signals that bypass trend validation:
        - entry_v3 signals (fresh signals)
        - Aggressive reversal signals
        
        Args:
            alert: V3 alert data
            signal_type: Signal type string
            
        Returns:
            bool: True if trend check should be bypassed
        """
        # Check bypass config
        bypass_config = self.config.get('trend_bypass', {})
        
        # entry_v3 signals bypass trend
        signal_source = self._get_attr(alert, 'signal_source', '')
        if signal_source == 'entry_v3' and bypass_config.get('bypass_for_entry_v3', True):
            return True
        
        # Aggressive reversal signals bypass trend
        if signal_type in self.AGGRESSIVE_REVERSAL_SIGNALS:
            return True
        
        # SL hunt re-entry requires trend check
        if self._get_attr(alert, 'is_sl_hunt_reentry', False):
            return False
        
        return False
    
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process V3 entry signal (legacy interface).
        
        Routes to process_v3_entry for full implementation.
        
        Args:
            alert: V3 alert data (ZepixV3Alert)
            
        Returns:
            dict: Execution result
        """
        signal_type = self._get_signal_type(alert)
        
        if not signal_type:
            return {"success": False, "error": "missing_signal_type"}
        
        # Validate alert
        if not self.validate_alert(alert):
            return {"success": False, "error": "invalid_alert"}
        
        # Route to full V3 entry processing
        return await self.process_v3_entry(alert, signal_type)
    
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process V3 exit signal (legacy interface).
        
        Routes to process_v3_exit for full implementation.
        
        Args:
            alert: V3 exit alert data
            
        Returns:
            dict: Exit execution result
        """
        signal_type = self._get_signal_type(alert)
        exit_type = 'bullish' if signal_type and 'Bullish' in signal_type else 'bearish'
        
        return await self.process_v3_exit(alert, exit_type)
    
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process V3 reversal signal.
        
        Steps:
        1. Close opposite positions
        2. Enter in new direction
        
        Args:
            alert: V3 reversal alert data
            
        Returns:
            dict: Reversal execution result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        signal_type = self._get_signal_type(alert)
        
        self.logger.info(f"V3 Reversal: {symbol} -> {direction} [{signal_type}]")
        
        try:
            # Step 1: Close opposite positions
            exit_result = await self.exit_logic.process_reversal_exit(alert)
            
            # Step 2: Enter in new direction
            entry_result = await self.process_v3_entry(alert, signal_type)
            
            self.stats['reversals_processed'] += 1
            
            return {
                "success": True,
                "plugin_id": self.plugin_id,
                "symbol": symbol,
                "direction": direction,
                "signal_type": signal_type,
                "exit_result": exit_result,
                "entry_result": entry_result
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"V3 Reversal error: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    async def process_trend_pulse(self, alert: Any) -> Dict[str, Any]:
        """
        Process V3 Trend Pulse signal.
        
        Updates multi-timeframe trend database via MTF processor.
        
        Args:
            alert: Trend pulse alert data
            
        Returns:
            dict: Processing result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        
        self.logger.info(f"V3 Trend Pulse: {symbol}")
        
        try:
            # Update MTF trends via MTF processor
            await self.mtf_processor.update_trend_database(alert)
            
            self.stats['trend_pulses_processed'] += 1
            
            return {
                "success": True,
                "plugin_id": self.plugin_id,
                "symbol": symbol,
                "action": "trend_updated"
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"V3 Trend Pulse error: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    def _route_to_logic(self, alert: Any) -> str:
        """
        Route alert to appropriate logic type based on timeframe.
        
        Routing Rules:
        - 1M, 5M -> LOGIC1 (scalping)
        - 15M -> LOGIC2 (intraday)
        - 1H, 4H, D1 -> LOGIC3 (swing)
        
        Args:
            alert: Alert data with timeframe
            
        Returns:
            str: Logic type (LOGIC1, LOGIC2, or LOGIC3)
        """
        timeframe = getattr(alert, "tf", "15")
        
        if timeframe in ["1", "5", "1M", "5M"]:
            return "LOGIC1"
        elif timeframe in ["15", "15M"]:
            return "LOGIC2"
        else:  # 1H, 4H, D1
            return "LOGIC3"
    
    def _is_aggressive_reversal(self, signal_type: str) -> bool:
        """
        Check if signal is an aggressive reversal signal.
        
        Aggressive reversal signals bypass trend check.
        
        Args:
            signal_type: Signal type string
            
        Returns:
            bool: True if aggressive reversal
        """
        return signal_type in self.AGGRESSIVE_REVERSAL_SIGNALS
    
    def validate_alert(self, alert: Any) -> bool:
        """
        Validate V3 alert before processing.
        
        Args:
            alert: Alert to validate
            
        Returns:
            bool: True if valid
        """
        # Check required fields
        required_fields = ["symbol", "direction", "signal_type"]
        
        for field in required_fields:
            if not hasattr(alert, field) and not isinstance(alert, dict):
                self.logger.warning(f"Alert missing required field: {field}")
                return False
            if isinstance(alert, dict) and field not in alert:
                self.logger.warning(f"Alert missing required field: {field}")
                return False
        
        # Check signal type is supported
        signal_type = getattr(alert, "signal_type", "") if hasattr(alert, "signal_type") else alert.get("signal_type", "")
        all_signals = self.ENTRY_SIGNALS + self.EXIT_SIGNALS + self.INFO_SIGNALS
        
        if signal_type not in all_signals:
            self.logger.warning(f"Unknown signal type: {signal_type}")
            return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status with component statistics."""
        base_status = super().get_status()
        
        base_status.update({
            "version": self.VERSION,
            "active_sessions": len(self.active_sessions),
            "active_chains": len(self.active_chains),
            "supported_signals": len(self.ENTRY_SIGNALS + self.EXIT_SIGNALS + self.INFO_SIGNALS),
            "shadow_mode": self.shadow_mode,
            "stats": self.stats,
            "components": {
                "signal_handlers": self.signal_handlers.get_statistics(),
                "routing": self.routing.get_statistics(),
                "dual_orders": self.dual_orders.get_statistics(),
                "mtf_processor": self.mtf_processor.get_statistics(),
                "position_sizer": self.position_sizer.get_statistics()
            }
        })
        
        return base_status
    
    def get_sl_multiplier(self, logic_route: str) -> float:
        """
        Get SL multiplier for logic route.
        
        Args:
            logic_route: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
            
        Returns:
            float: SL multiplier
        """
        return self.SL_MULTIPLIERS.get(logic_route, 1.0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin statistics."""
        return {
            **self.stats,
            "plugin_id": self.plugin_id,
            "version": self.VERSION,
            "shadow_mode": self.shadow_mode
        }
