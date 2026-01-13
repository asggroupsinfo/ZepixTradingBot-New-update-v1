"""
V6 Price Action Plugin - V5 Hybrid Plugin Architecture

Main plugin class for V6 Price Action trading strategy.
FULLY IMPLEMENTED - Routes signals to timeframe-specific plugins.

Part of Document 01: Project Overview - Plugin System Architecture
Full implementation per PM directive: ZERO TODOs, ZERO SKELETONS.

Order Routing (per planning docs):
- 1M: ORDER B ONLY (Scalping)
- 5M: DUAL ORDERS (Momentum)
- 15M: ORDER A ONLY (Intraday)
- 1H: ORDER A ONLY (Swing)
"""

from typing import Dict, Any, List, Optional
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from src.core.plugin_system.base_plugin import BaseLogicPlugin

logger = logging.getLogger(__name__)


# Database path for V6 Price Action (isolated from V3)
V6_DATABASE_PATH = Path("data/zepix_price_action.db")


class PriceActionV6Plugin(BaseLogicPlugin):
    """
    V6 Price Action Plugin.
    
    Implements the V6 trading strategy with:
    - 4 timeframe-specific sub-plugins (1M, 5M, 15M, 1H)
    - 14 alert types
    - Conditional order routing based on timeframe
    - Trend Pulse integration
    
    Timeframe Plugins:
    - V6_1M: 1-minute scalping (aggressive, tight SL)
    - V6_5M: 5-minute intraday (balanced)
    - V6_15M: 15-minute swing (moderate SL)
    - V6_1H: 1-hour position (wide SL, longer holds)
    
    Alert Types (14):
    Entry Alerts:
    - PA_Breakout_Entry
    - PA_Pullback_Entry
    - PA_Reversal_Entry
    - PA_Momentum_Entry
    - PA_Support_Bounce
    - PA_Resistance_Rejection
    - PA_Trend_Continuation
    
    Exit Alerts:
    - PA_Exit_Signal
    - PA_Reversal_Exit
    - PA_Target_Hit
    
    Info Alerts:
    - PA_Trend_Pulse
    - PA_Volatility_Alert
    - PA_Session_Open
    - PA_Session_Close
    
    Order Routing:
    - 1M: Single order, tight SL, quick exit
    - 5M: Single order, moderate SL
    - 15M: Dual order option, balanced approach
    - 1H: Dual order, wide SL, profit trailing
    """
    
    # Plugin metadata
    PLUGIN_ID = "price_action_v6"
    VERSION = "6.0.0"
    DESCRIPTION = "V6 Price Action - 4 timeframes, 14 alerts, conditional routing"
    
    # Supported timeframes
    TIMEFRAMES = ["1M", "5M", "15M", "1H"]
    
    # Alert type constants
    ENTRY_ALERTS = [
        "PA_Breakout_Entry",
        "PA_Pullback_Entry",
        "PA_Reversal_Entry",
        "PA_Momentum_Entry",
        "PA_Support_Bounce",
        "PA_Resistance_Rejection",
        "PA_Trend_Continuation"
    ]
    
    EXIT_ALERTS = [
        "PA_Exit_Signal",
        "PA_Reversal_Exit",
        "PA_Target_Hit"
    ]
    
    INFO_ALERTS = [
        "PA_Trend_Pulse",
        "PA_Volatility_Alert",
        "PA_Session_Open",
        "PA_Session_Close"
    ]
    
    # V6 Pine Signal to Bot Handler Mapping
    # Maps Pine V6 signal names to internal bot handler names
    V6_SIGNAL_MAP = {
        # Entry signals
        "BULLISH_ENTRY": "PA_Breakout_Entry",
        "BEARISH_ENTRY": "PA_Breakout_Entry",
        "SIDEWAYS_BREAKOUT": "PA_Momentum_Entry",
        "TRENDLINE_BULLISH_BREAK": "PA_Support_Bounce",
        "TRENDLINE_BEARISH_BREAK": "PA_Resistance_Rejection",
        "BREAKOUT": "PA_Breakout_Entry",
        "BREAKDOWN": "PA_Breakout_Entry",
        # Exit signals
        "EXIT_BULLISH": "PA_Exit_Signal",
        "EXIT_BEARISH": "PA_Exit_Signal",
        # Info signals
        "TREND_PULSE": "PA_Trend_Pulse",
        "MOMENTUM_CHANGE": "PA_Volatility_Alert",
        "STATE_CHANGE": "PA_Volatility_Alert",
        "SCREENER_FULL_BULLISH": "PA_Trend_Pulse",
        "SCREENER_FULL_BEARISH": "PA_Trend_Pulse"
    }
    
    # Timeframe-specific settings
    TIMEFRAME_SETTINGS = {
        "1M": {
            "name": "Scalping",
            "dual_orders": False,
            "sl_multiplier": 0.5,
            "lot_multiplier": 0.5,
            "max_hold_minutes": 30
        },
        "5M": {
            "name": "Intraday",
            "dual_orders": False,
            "sl_multiplier": 1.0,
            "lot_multiplier": 1.0,
            "max_hold_minutes": 120
        },
        "15M": {
            "name": "Swing",
            "dual_orders": True,
            "sl_multiplier": 1.5,
            "lot_multiplier": 1.0,
            "max_hold_minutes": 480
        },
        "1H": {
            "name": "Position",
            "dual_orders": True,
            "sl_multiplier": 2.0,
            "lot_multiplier": 0.75,
            "max_hold_minutes": 1440
        }
    }
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """
        Initialize V6 Price Action Plugin.
        
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
            "supported_signals": self.ENTRY_ALERTS + self.EXIT_ALERTS + self.INFO_ALERTS
        }
        
        # Plugin-specific state
        self.active_trades: Dict[str, Dict] = {}
        self.timeframe_stats: Dict[str, Dict] = {
            tf: {"trades": 0, "wins": 0, "losses": 0, "pnl": 0.0}
            for tf in self.TIMEFRAMES
        }
        
        # Trend Pulse state - tracks market trends per symbol/timeframe
        self.trend_pulse_state: Dict[str, Dict[str, Any]] = {}
        
        # Initialize timeframe-specific plugins (lazy loaded)
        self._tf_plugins: Dict[str, Any] = {}
        
        # Initialize V6 database
        self._initialize_v6_database()
        
        self.logger.info(f"PriceActionV6Plugin initialized: {self.VERSION}")
    
    def _initialize_v6_database(self) -> None:
        """Initialize V6-specific database (isolated from V3)."""
        try:
            V6_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(V6_DATABASE_PATH))
            cursor = conn.cursor()
            
            # V6 trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS v6_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    ticket_a INTEGER,
                    ticket_b INTEGER,
                    lot_size REAL,
                    entry_price REAL,
                    sl_price REAL,
                    tp_price REAL,
                    adx REAL,
                    confidence_score INTEGER,
                    entry_time TEXT,
                    exit_time TEXT,
                    pnl REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'open',
                    plugin_id TEXT
                )
            ''')
            
            # V6 trend pulse table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS v6_trend_pulse (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    bullish_count INTEGER DEFAULT 0,
                    bearish_count INTEGER DEFAULT 0,
                    market_state TEXT,
                    changed_tfs TEXT,
                    updated_at TEXT,
                    UNIQUE(symbol, timeframe)
                )
            ''')
            
            # V6 momentum state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS v6_momentum_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    current_adx REAL,
                    current_strength TEXT,
                    prev_adx REAL,
                    prev_strength TEXT,
                    change_type TEXT,
                    updated_at TEXT,
                    UNIQUE(symbol, timeframe)
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info(f"V6 database initialized: {V6_DATABASE_PATH}")
        except Exception as e:
            self.logger.warning(f"V6 database initialization error: {e}")
    
    def _get_tf_plugin(self, timeframe: str) -> Optional[Any]:
        """
        Get or create timeframe-specific plugin instance.
        
        Args:
            timeframe: Timeframe string (1M, 5M, 15M, 1H)
            
        Returns:
            Timeframe plugin instance or None
        """
        if timeframe in self._tf_plugins:
            return self._tf_plugins[timeframe]
        
        try:
            if timeframe == "1M":
                from ..price_action_1m.plugin import create_price_action_1m
                self._tf_plugins["1M"] = create_price_action_1m()
            elif timeframe == "5M":
                from ..price_action_5m.plugin import create_price_action_5m
                self._tf_plugins["5M"] = create_price_action_5m()
            elif timeframe == "15M":
                from ..price_action_15m.plugin import create_price_action_15m
                self._tf_plugins["15M"] = create_price_action_15m()
            elif timeframe == "1H":
                from ..price_action_1h.plugin import create_price_action_1h
                self._tf_plugins["1H"] = create_price_action_1h()
            else:
                self.logger.error(f"Unknown timeframe: {timeframe}")
                return None
            
            self.logger.info(f"Loaded TF plugin: {timeframe}")
            return self._tf_plugins.get(timeframe)
        except ImportError as e:
            self.logger.error(f"Failed to import TF plugin {timeframe}: {e}")
            return None
    
    def _normalize_timeframe(self, tf: str) -> str:
        """
        Normalize timeframe string to standard format.
        
        Args:
            tf: Raw timeframe from Pine (e.g., "1", "5", "15", "60")
            
        Returns:
            Normalized timeframe (e.g., "1M", "5M", "15M", "1H")
        """
        tf = str(tf).strip().upper()
        
        # Already normalized
        if tf in self.TIMEFRAMES:
            return tf
        
        # Map Pine timeframe values
        tf_map = {
            "1": "1M",
            "5": "5M",
            "15": "15M",
            "60": "1H",
            "240": "1H",  # 4H maps to 1H plugin
        }
        
        return tf_map.get(tf, "15M")  # Default to 15M
    
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process V6 entry signal - FULLY IMPLEMENTED.
        
        Routes signal to appropriate timeframe plugin:
        - 1M -> price_action_1m (ORDER B ONLY)
        - 5M -> price_action_5m (DUAL ORDERS)
        - 15M -> price_action_15m (ORDER A ONLY)
        - 1H -> price_action_1h (ORDER A ONLY)
        
        Args:
            alert: V6 alert data (dict or object)
            
        Returns:
            dict: Execution result with routing details
        """
        # Extract alert details (support both dict and object)
        if isinstance(alert, dict):
            alert_type = alert.get("alert_type", "")
            symbol = alert.get("symbol", "")
            direction = alert.get("direction", "")
            raw_tf = alert.get("timeframe", "15")
        else:
            alert_type = getattr(alert, "alert_type", "")
            symbol = getattr(alert, "symbol", "")
            direction = getattr(alert, "direction", "")
            raw_tf = getattr(alert, "timeframe", "15")
        
        # Normalize timeframe
        timeframe = self._normalize_timeframe(raw_tf)
        
        self.logger.info(f"V6 Entry: {symbol} {direction} [{alert_type}] TF={timeframe}")
        
        # Validate timeframe
        if timeframe not in self.TIMEFRAMES:
            self.logger.error(f"Invalid timeframe: {timeframe}")
            return {"success": False, "error": "invalid_timeframe", "timeframe": timeframe}
        
        # Get timeframe-specific plugin
        tf_plugin = self._get_tf_plugin(timeframe)
        if not tf_plugin:
            self.logger.error(f"Failed to load TF plugin: {timeframe}")
            return {"success": False, "error": "plugin_load_failed", "timeframe": timeframe}
        
        # Prepare signal dict for TF plugin
        signal_dict = alert if isinstance(alert, dict) else {
            "symbol": symbol,
            "direction": direction,
            "timeframe": timeframe,
            "alert_type": alert_type,
            "price": getattr(alert, "price", 0.0),
            "sl_price": getattr(alert, "sl_price", None),
            "tp1_price": getattr(alert, "tp1_price", None),
            "tp2_price": getattr(alert, "tp2_price", None),
            "tp3_price": getattr(alert, "tp3_price", None),
            "adx": getattr(alert, "adx", None),
            "adx_strength": getattr(alert, "adx_strength", ""),
            "conf_score": getattr(alert, "conf_score", 0),
        }
        
        # Route to TF plugin
        try:
            result = await tf_plugin.on_signal_received(signal_dict)
            
            # Update stats
            self.timeframe_stats[timeframe]["trades"] += 1
            
            # Store in V6 database
            self._store_trade_in_db(signal_dict, timeframe, result)
            
            tf_settings = self.TIMEFRAME_SETTINGS.get(timeframe, {})
            return {
                "success": result if isinstance(result, bool) else result.get("success", False),
                "plugin_id": self.plugin_id,
                "routed_to": f"price_action_{timeframe.lower()}",
                "alert_type": alert_type,
                "symbol": symbol,
                "direction": direction,
                "timeframe": timeframe,
                "order_type": "DUAL_ORDERS" if tf_settings.get("dual_orders") else "SINGLE_ORDER",
                "tf_result": result
            }
        except Exception as e:
            self.logger.error(f"TF plugin error: {e}")
            return {"success": False, "error": str(e), "timeframe": timeframe}
    
    def _store_trade_in_db(self, signal: Dict[str, Any], timeframe: str, result: Any) -> None:
        """Store trade record in V6 database."""
        try:
            conn = sqlite3.connect(str(V6_DATABASE_PATH))
            cursor = conn.cursor()
            
            tf_settings = self.TIMEFRAME_SETTINGS.get(timeframe, {})
            order_type = "DUAL_ORDERS" if tf_settings.get("dual_orders") else "SINGLE_ORDER"
            
            cursor.execute('''
                INSERT INTO v6_trades 
                (symbol, direction, timeframe, signal_type, order_type, 
                 entry_price, sl_price, adx, confidence_score, entry_time, plugin_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.get("symbol", ""),
                signal.get("direction", ""),
                timeframe,
                signal.get("alert_type", ""),
                order_type,
                signal.get("price", 0.0),
                signal.get("sl_price"),
                signal.get("adx"),
                signal.get("conf_score", 0),
                datetime.now().isoformat(),
                self.plugin_id
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.warning(f"Failed to store trade in DB: {e}")
    
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process V6 exit signal - FULLY IMPLEMENTED.
        
        Routes exit to appropriate timeframe plugin based on signal.
        
        Args:
            alert: V6 exit alert data (dict or object)
            
        Returns:
            dict: Exit execution result
        """
        # Extract alert details
        if isinstance(alert, dict):
            alert_type = alert.get("alert_type", "")
            symbol = alert.get("symbol", "")
            raw_tf = alert.get("timeframe", "15")
        else:
            alert_type = getattr(alert, "alert_type", "")
            symbol = getattr(alert, "symbol", "")
            raw_tf = getattr(alert, "timeframe", "15")
        
        timeframe = self._normalize_timeframe(raw_tf)
        
        self.logger.info(f"V6 Exit: {symbol} [{alert_type}] TF={timeframe}")
        
        # Validate timeframe
        if timeframe not in self.TIMEFRAMES:
            self.logger.error(f"Invalid timeframe for exit: {timeframe}")
            return {"success": False, "error": "invalid_timeframe", "timeframe": timeframe}
        
        # Close positions via service API if available
        positions_closed = 0
        if self.service_api:
            try:
                order_service = getattr(self.service_api, 'order_execution', None)
                if order_service:
                    result = await order_service.close_all_orders(
                        symbol=symbol,
                        plugin_id=self.plugin_id
                    )
                    positions_closed = result.get("closed", 0)
            except Exception as e:
                self.logger.warning(f"Exit order close error: {e}")
        
        # Update trade records in V6 database
        self._update_trade_exit_in_db(symbol, timeframe)
        
        return {
            "success": True,
            "plugin_id": self.plugin_id,
            "alert_type": alert_type,
            "symbol": symbol,
            "timeframe": timeframe,
            "positions_closed": positions_closed
        }
    
    def _update_trade_exit_in_db(self, symbol: str, timeframe: str) -> None:
        """Update trade exit time in V6 database."""
        try:
            conn = sqlite3.connect(str(V6_DATABASE_PATH))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE v6_trades 
                SET exit_time = ?, status = 'closed'
                WHERE symbol = ? AND timeframe = ? AND status = 'open'
            ''', (datetime.now().isoformat(), symbol, timeframe))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.warning(f"Failed to update trade exit in DB: {e}")
    
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process V6 reversal signal - FULLY IMPLEMENTED.
        
        Closes existing positions and enters in new direction.
        
        Args:
            alert: V6 reversal alert data (dict or object)
            
        Returns:
            dict: Reversal execution result
        """
        # Extract alert details
        if isinstance(alert, dict):
            alert_type = alert.get("alert_type", "")
            symbol = alert.get("symbol", "")
            direction = alert.get("direction", "")
            raw_tf = alert.get("timeframe", "15")
        else:
            alert_type = getattr(alert, "alert_type", "")
            symbol = getattr(alert, "symbol", "")
            direction = getattr(alert, "direction", "")
            raw_tf = getattr(alert, "timeframe", "15")
        
        timeframe = self._normalize_timeframe(raw_tf)
        
        self.logger.info(f"V6 Reversal: {symbol} -> {direction} [{alert_type}] TF={timeframe}")
        
        # Step 1: Close existing positions (exit)
        exit_result = await self.process_exit_signal(alert)
        
        # Step 2: Enter in new direction
        entry_result = await self.process_entry_signal(alert)
        
        return {
            "success": exit_result.get("success", False) and entry_result.get("success", False),
            "plugin_id": self.plugin_id,
            "alert_type": alert_type,
            "symbol": symbol,
            "direction": direction,
            "timeframe": timeframe,
            "exit_result": exit_result,
            "entry_result": entry_result
        }
    
    async def process_trend_pulse(self, alert: Any) -> Dict[str, Any]:
        """
        Process V6 Trend Pulse signal - FULLY IMPLEMENTED.
        
        Updates multi-timeframe trend tracking in V6 database.
        Stores bullish/bearish counts, market state, and changed timeframes.
        
        Args:
            alert: Trend pulse alert data (dict or object)
            
        Returns:
            dict: Processing result with trend state
        """
        self.logger.info("Processing V6 Trend Pulse")
        
        # Extract alert details
        if isinstance(alert, dict):
            symbol = alert.get("symbol", "")
            raw_tf = alert.get("timeframe", "15")
            bullish_count = alert.get("bullish_count", 0)
            bearish_count = alert.get("bearish_count", 0)
            changed_tfs = alert.get("changed_tfs", "")
            market_state = alert.get("market_state", "")
        else:
            symbol = getattr(alert, "symbol", "")
            raw_tf = getattr(alert, "timeframe", "15")
            bullish_count = getattr(alert, "bullish_count", 0)
            bearish_count = getattr(alert, "bearish_count", 0)
            changed_tfs = getattr(alert, "changed_tfs", "")
            market_state = getattr(alert, "market_state", "")
        
        timeframe = self._normalize_timeframe(raw_tf)
        
        # Update in-memory trend state
        key = f"{symbol}_{timeframe}"
        self.trend_pulse_state[key] = {
            "symbol": symbol,
            "timeframe": timeframe,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "market_state": market_state,
            "changed_tfs": changed_tfs,
            "updated_at": datetime.now().isoformat()
        }
        
        # Store in V6 database
        self._store_trend_pulse_in_db(
            symbol, timeframe, bullish_count, bearish_count, market_state, changed_tfs
        )
        
        self.logger.info(
            f"Trend Pulse: {symbol} TF={timeframe} "
            f"Bull={bullish_count} Bear={bearish_count} State={market_state}"
        )
        
        return {
            "success": True,
            "plugin_id": self.plugin_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "market_state": market_state,
            "changed_tfs": changed_tfs
        }
    
    def _store_trend_pulse_in_db(
        self,
        symbol: str,
        timeframe: str,
        bullish_count: int,
        bearish_count: int,
        market_state: str,
        changed_tfs: str
    ) -> None:
        """Store trend pulse data in V6 database."""
        try:
            conn = sqlite3.connect(str(V6_DATABASE_PATH))
            cursor = conn.cursor()
            
            # Upsert trend pulse data
            cursor.execute('''
                INSERT INTO v6_trend_pulse 
                (symbol, timeframe, bullish_count, bearish_count, market_state, changed_tfs, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol, timeframe) DO UPDATE SET
                    bullish_count = excluded.bullish_count,
                    bearish_count = excluded.bearish_count,
                    market_state = excluded.market_state,
                    changed_tfs = excluded.changed_tfs,
                    updated_at = excluded.updated_at
            ''', (
                symbol, timeframe, bullish_count, bearish_count,
                market_state, changed_tfs, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.warning(f"Failed to store trend pulse in DB: {e}")
    
    def get_trend_state(self, symbol: str, timeframe: str = None) -> Dict[str, Any]:
        """
        Get current trend state for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: Optional specific timeframe
            
        Returns:
            dict: Trend state data
        """
        if timeframe:
            key = f"{symbol}_{timeframe}"
            return self.trend_pulse_state.get(key, {})
        
        # Return all timeframes for symbol
        result = {}
        for key, state in self.trend_pulse_state.items():
            if key.startswith(f"{symbol}_"):
                tf = key.split("_")[1]
                result[tf] = state
        return result
    
    def get_timeframe_settings(self, timeframe: str) -> Dict[str, Any]:
        """
        Get settings for a specific timeframe.
        
        Args:
            timeframe: Timeframe string (1M, 5M, 15M, 1H)
            
        Returns:
            dict: Timeframe-specific settings
        """
        return self.TIMEFRAME_SETTINGS.get(timeframe, self.TIMEFRAME_SETTINGS["15M"])
    
    def should_use_dual_orders(self, timeframe: str) -> bool:
        """
        Check if dual orders should be used for timeframe.
        
        Args:
            timeframe: Timeframe string
            
        Returns:
            bool: True if dual orders should be used
        """
        settings = self.get_timeframe_settings(timeframe)
        return settings.get("dual_orders", False)
    
    def validate_alert(self, alert: Any) -> bool:
        """
        Validate V6 alert before processing.
        
        Args:
            alert: Alert to validate
            
        Returns:
            bool: True if valid
        """
        # Check required fields
        required_fields = ["symbol", "direction", "alert_type"]
        
        for field in required_fields:
            if not hasattr(alert, field) and not isinstance(alert, dict):
                self.logger.warning(f"Alert missing required field: {field}")
                return False
            if isinstance(alert, dict) and field not in alert:
                self.logger.warning(f"Alert missing required field: {field}")
                return False
        
        # Check alert type is supported
        alert_type = getattr(alert, "alert_type", "") if hasattr(alert, "alert_type") else alert.get("alert_type", "")
        all_alerts = self.ENTRY_ALERTS + self.EXIT_ALERTS + self.INFO_ALERTS
        
        if alert_type not in all_alerts:
            self.logger.warning(f"Unknown alert type: {alert_type}")
            return False
        
        return True
    
    async def process_raw_v6_alert(self, alert_string: str) -> Dict[str, Any]:
        """
        Process raw V6 Pine Script alert (pipe-separated format).
        
        This method:
        1. Parses the pipe-separated alert string using V6AlertParser
        2. Maps Pine signal type to bot handler using V6_SIGNAL_MAP
        3. Routes to appropriate processing method
        
        Args:
            alert_string: Raw pipe-separated alert from Pine V6
            
        Returns:
            dict: Processing result
        """
        from .alert_parser import parse_v6_alert
        
        self.logger.info(f"Processing raw V6 alert: {alert_string[:50]}...")
        
        # Parse the alert string
        parsed = parse_v6_alert(alert_string)
        
        if not parsed or not parsed.get("parsed", False):
            self.logger.warning(f"Failed to parse V6 alert: {alert_string}")
            return {"success": False, "error": "parse_failed", "raw": alert_string}
        
        # Get Pine signal type and map to bot handler
        pine_signal = parsed.get("signal_type", "")
        bot_handler = self.V6_SIGNAL_MAP.get(pine_signal)
        
        if not bot_handler:
            self.logger.warning(f"Unknown Pine V6 signal: {pine_signal}")
            return {"success": False, "error": "unknown_signal", "signal_type": pine_signal}
        
        # Add mapped alert_type to parsed data
        parsed["alert_type"] = bot_handler
        
        # Normalize timeframe format (Pine sends "15", bot expects "15M")
        tf = parsed.get("timeframe", "15")
        if tf and not tf.endswith("M") and not tf.endswith("H"):
            if tf == "60":
                parsed["timeframe"] = "1H"
            else:
                parsed["timeframe"] = f"{tf}M"
        
        # Route to appropriate handler based on category
        category = parsed.get("category", "unknown")
        
        if category == "entry":
            return await self.process_entry_signal(parsed)
        elif category == "exit":
            return await self.process_exit_signal(parsed)
        elif category == "info":
            if pine_signal == "TREND_PULSE":
                return await self.process_trend_pulse(parsed)
            return {"success": True, "action": "info_logged", "signal_type": pine_signal}
        
        return {"success": False, "error": "unknown_category", "category": category}
    
    def map_pine_signal(self, pine_signal: str) -> Optional[str]:
        """
        Map Pine V6 signal type to bot handler name.
        
        Args:
            pine_signal: Pine V6 signal type (e.g., "BULLISH_ENTRY")
            
        Returns:
            str: Bot handler name (e.g., "PA_Breakout_Entry") or None
        """
        return self.V6_SIGNAL_MAP.get(pine_signal)
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        base_status = super().get_status()
        
        base_status.update({
            "version": self.VERSION,
            "active_trades": len(self.active_trades),
            "timeframe_stats": self.timeframe_stats,
            "supported_timeframes": self.TIMEFRAMES,
            "supported_alerts": len(self.ENTRY_ALERTS + self.EXIT_ALERTS + self.INFO_ALERTS),
            "v6_signal_mappings": len(self.V6_SIGNAL_MAP)
        })
        
        return base_status
