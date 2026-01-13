"""
V3 Combined Logic - Signal Handlers Module

Handles all 12 V3 signal types with proper routing and processing.

Part of Document 06: Phase 4 - V3 Plugin Migration
Implements exact same logic as old V3 in TradingEngine.

Signal Types:
Entry Signals (7):
1. Institutional Launchpad
2. Liquidity Trap
3. Momentum Breakout
4. Mitigation Test
5. Golden Pocket Flip
6. Screener Full Bullish/Bearish (9/10)
7. Sideways Breakout (12 - BONUS)

Exit Signals (2):
- Signal 7: Bullish Exit
- Signal 8: Bearish Exit

Info Signals (2):
- Signal 6: Volatility Squeeze
- Signal 11: Trend Pulse
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class V3SignalHandlers:
    """
    Handles all 12 V3 signal types.
    
    Routes signals to appropriate processing pipelines:
    - Entry signals -> process_entry_signal
    - Exit signals -> process_exit_signal
    - Info signals -> process_info_signal
    """
    
    # Signal aliases for Pine V3 compatibility
    # Maps Pine signal names to internal handler names
    SIGNAL_ALIASES = {
        'Liquidity_Trap_Reversal': 'Liquidity_Trap',
        'Mitigation_Test_Entry': 'Mitigation_Test'
    }
    
    # Signal type to handler mapping
    SIGNAL_HANDLERS = {
        # Entry signals (7)
        'Institutional_Launchpad': 'handle_institutional_launchpad',
        'Liquidity_Trap': 'handle_liquidity_trap',
        'Liquidity_Trap_Reversal': 'handle_liquidity_trap',  # Pine V3 alias
        'Momentum_Breakout': 'handle_momentum_breakout',
        'Mitigation_Test': 'handle_mitigation_test',
        'Mitigation_Test_Entry': 'handle_mitigation_test',  # Pine V3 alias
        'Golden_Pocket_Flip': 'handle_golden_pocket_flip',
        'Golden_Pocket_Flip_1H': 'handle_golden_pocket_flip',
        'Golden_Pocket_Flip_4H': 'handle_golden_pocket_flip',
        'Screener_Full_Bullish': 'handle_screener_full',
        'Screener_Full_Bearish': 'handle_screener_full',
        'Sideways_Breakout': 'handle_sideways_breakout',
        # Exit signals (2)
        'Bullish_Exit': 'handle_bullish_exit',
        'Bearish_Exit': 'handle_bearish_exit',
        # Info signals (2)
        'Volatility_Squeeze': 'handle_volatility_squeeze',
        'Trend_Pulse': 'handle_trend_pulse'
    }
    
    # Entry signal types
    ENTRY_SIGNALS = [
        'Institutional_Launchpad',
        'Liquidity_Trap',
        'Momentum_Breakout',
        'Mitigation_Test',
        'Golden_Pocket_Flip',
        'Golden_Pocket_Flip_1H',
        'Golden_Pocket_Flip_4H',
        'Screener_Full_Bullish',
        'Screener_Full_Bearish',
        'Sideways_Breakout'
    ]
    
    # Exit signal types
    EXIT_SIGNALS = [
        'Bullish_Exit',
        'Bearish_Exit'
    ]
    
    # Info signal types (no trade placement)
    INFO_SIGNALS = [
        'Volatility_Squeeze',
        'Trend_Pulse'
    ]
    
    def __init__(self, plugin):
        """
        Initialize V3 Signal Handlers.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"{__name__}.V3SignalHandlers")
        
        # Statistics tracking
        self.stats = {
            'signals_received': 0,
            'entries_processed': 0,
            'exits_processed': 0,
            'info_processed': 0,
            'errors': 0
        }
        
        self.logger.info("V3SignalHandlers initialized - 12 signals ready")
    
    async def route_signal(self, alert: Any) -> Optional[Dict[str, Any]]:
        """
        Route signal to appropriate handler.
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Processing result or None
        """
        signal_type = self._get_signal_type(alert)
        
        if not signal_type:
            self.logger.warning("Alert missing signal_type")
            return None
        
        self.stats['signals_received'] += 1
        
        handler_name = self.SIGNAL_HANDLERS.get(signal_type)
        if not handler_name:
            self.logger.warning(f"Unknown signal type: {signal_type}")
            return None
        
        handler = getattr(self, handler_name, None)
        if not handler:
            self.logger.error(f"Handler not found: {handler_name}")
            return None
        
        try:
            result = await handler(alert)
            return result
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Signal handler error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== ENTRY SIGNAL HANDLERS ====================
    
    async def handle_institutional_launchpad(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 1: Institutional Launchpad Entry.
        
        High-probability entry based on institutional order flow.
        Routes through standard entry pipeline.
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        
        self.logger.info(f"Signal 1: Institutional Launchpad - {symbol} {direction}")
        
        result = await self._process_entry_signal(alert, signal_type='Institutional_Launchpad')
        self.stats['entries_processed'] += 1
        
        return result
    
    async def handle_liquidity_trap(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 2: Liquidity Trap Entry.
        
        Entry after liquidity sweep/trap pattern detected.
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        
        self.logger.info(f"Signal 2: Liquidity Trap - {symbol} {direction}")
        
        result = await self._process_entry_signal(alert, signal_type='Liquidity_Trap')
        self.stats['entries_processed'] += 1
        
        return result
    
    async def handle_momentum_breakout(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 3: Momentum Breakout Entry.
        
        Entry on strong momentum breakout.
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        
        self.logger.info(f"Signal 3: Momentum Breakout - {symbol} {direction}")
        
        result = await self._process_entry_signal(alert, signal_type='Momentum_Breakout')
        self.stats['entries_processed'] += 1
        
        return result
    
    async def handle_mitigation_test(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 4: Mitigation Test Entry.
        
        Entry after price tests and mitigates a key level.
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        
        self.logger.info(f"Signal 4: Mitigation Test - {symbol} {direction}")
        
        result = await self._process_entry_signal(alert, signal_type='Mitigation_Test')
        self.stats['entries_processed'] += 1
        
        return result
    
    async def handle_golden_pocket_flip(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 5: Golden Pocket Flip Entry.
        
        Entry at golden pocket (61.8% Fib) with flip confirmation.
        This signal has TF-based routing override (1H/4H -> LOGIC3).
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        timeframe = self._get_attr(alert, 'tf', '15')
        
        self.logger.info(f"Signal 5: Golden Pocket Flip - {symbol} {direction} [{timeframe}]")
        
        result = await self._process_entry_signal(alert, signal_type='Golden_Pocket_Flip')
        self.stats['entries_processed'] += 1
        
        return result
    
    async def handle_screener_full(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 9/10: Screener Full Bullish/Bearish Entry.
        
        Entry when full screener alignment detected.
        ALWAYS routes to LOGIC3 (override).
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        signal_type = self._get_signal_type(alert)
        
        self.logger.info(f"Signal 9/10: Screener Full - {symbol} {direction} [{signal_type}]")
        
        result = await self._process_entry_signal(alert, signal_type=signal_type)
        self.stats['entries_processed'] += 1
        
        return result
    
    async def handle_sideways_breakout(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 12: Sideways Breakout Entry (BONUS).
        
        Entry after breakout from sideways consolidation.
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        direction = self._get_attr(alert, 'direction', '')
        
        self.logger.info(f"Signal 12: Sideways Breakout - {symbol} {direction}")
        
        result = await self._process_entry_signal(alert, signal_type='Sideways_Breakout')
        self.stats['entries_processed'] += 1
        
        return result
    
    # ==================== EXIT SIGNAL HANDLERS ====================
    
    async def handle_bullish_exit(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 7: Bullish Exit.
        
        Exit signal for bullish positions (close BUY positions).
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Exit result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        
        self.logger.info(f"Signal 7: Bullish Exit - {symbol}")
        
        result = await self._process_exit_signal(alert, exit_type='bullish')
        self.stats['exits_processed'] += 1
        
        return result
    
    async def handle_bearish_exit(self, alert: Any) -> Dict[str, Any]:
        """
        Signal 8: Bearish Exit.
        
        Exit signal for bearish positions (close SELL positions).
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Exit result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        
        self.logger.info(f"Signal 8: Bearish Exit - {symbol}")
        
        result = await self._process_exit_signal(alert, exit_type='bearish')
        self.stats['exits_processed'] += 1
        
        return result
    
    # ==================== INFO SIGNAL HANDLERS ====================
    
    async def handle_volatility_squeeze(self, alert: Any) -> Optional[Dict[str, Any]]:
        """
        Signal 6: Volatility Squeeze (Info only).
        
        Informational signal - no trade placement.
        Updates volatility state for the symbol.
        
        Args:
            alert: V3 alert data
            
        Returns:
            None (info signal)
        """
        symbol = self._get_attr(alert, 'symbol', '')
        squeeze_state = self._get_attr(alert, 'squeeze_state', 'unknown')
        
        self.logger.info(f"Signal 6: Volatility Squeeze - {symbol} [{squeeze_state}]")
        
        # Update volatility state in database
        await self._update_volatility_state(alert)
        
        self.stats['info_processed'] += 1
        
        return {
            "success": True,
            "signal_type": "Volatility_Squeeze",
            "symbol": symbol,
            "squeeze_state": squeeze_state,
            "action": "info_only"
        }
    
    async def handle_trend_pulse(self, alert: Any) -> Optional[Dict[str, Any]]:
        """
        Signal 11: Trend Pulse (DB Update).
        
        Updates multi-timeframe trend database.
        No trade placement - info signal only.
        
        Args:
            alert: V3 alert data
            
        Returns:
            dict: Update result
        """
        symbol = self._get_attr(alert, 'symbol', '')
        mtf_trends = self._get_attr(alert, 'mtf_trends', '')
        
        self.logger.info(f"Signal 11: Trend Pulse - {symbol}")
        
        # Update MTF trends via MTF processor
        if hasattr(self.plugin, 'mtf_processor'):
            await self.plugin.mtf_processor.update_trend_database(alert)
        
        self.stats['info_processed'] += 1
        
        return {
            "success": True,
            "signal_type": "Trend_Pulse",
            "symbol": symbol,
            "mtf_trends": mtf_trends,
            "action": "db_update"
        }
    
    # ==================== COMMON PROCESSING METHODS ====================
    
    async def _process_entry_signal(
        self,
        alert: Any,
        signal_type: str
    ) -> Dict[str, Any]:
        """
        Common entry processing pipeline.
        
        Routes through plugin's entry pipeline:
        1. Determine logic route
        2. Validate trend (unless bypassed)
        3. Calculate lot size
        4. Place dual orders
        
        Args:
            alert: V3 alert data
            signal_type: Signal type string
            
        Returns:
            dict: Entry result
        """
        return await self.plugin.process_v3_entry(alert, signal_type)
    
    async def _process_exit_signal(
        self,
        alert: Any,
        exit_type: str
    ) -> Dict[str, Any]:
        """
        Common exit processing pipeline.
        
        Args:
            alert: V3 alert data
            exit_type: 'bullish' or 'bearish'
            
        Returns:
            dict: Exit result
        """
        return await self.plugin.process_v3_exit(alert, exit_type)
    
    async def _update_volatility_state(self, alert: Any):
        """
        Update volatility state in database.
        
        Args:
            alert: Volatility squeeze alert
        """
        try:
            symbol = self._get_attr(alert, 'symbol', '')
            squeeze_state = self._get_attr(alert, 'squeeze_state', 'unknown')
            
            # Store in plugin database
            if hasattr(self.plugin, 'database'):
                await self.plugin.database.update_volatility_state(
                    symbol=symbol,
                    state=squeeze_state,
                    timestamp=datetime.now()
                )
        except Exception as e:
            self.logger.warning(f"Volatility state update error: {e}")
    
    # ==================== UTILITY METHODS ====================
    
    def _get_signal_type(self, alert: Any) -> Optional[str]:
        """Get signal type from alert."""
        return self._get_attr(alert, 'signal_type', None)
    
    def _get_attr(self, alert: Any, attr: str, default: Any = None) -> Any:
        """Get attribute from alert (supports dict and object)."""
        if isinstance(alert, dict):
            return alert.get(attr, default)
        return getattr(alert, attr, default)
    
    def is_entry_signal(self, signal_type: str) -> bool:
        """Check if signal type is an entry signal."""
        return signal_type in self.ENTRY_SIGNALS
    
    def is_exit_signal(self, signal_type: str) -> bool:
        """Check if signal type is an exit signal."""
        return signal_type in self.EXIT_SIGNALS
    
    def is_info_signal(self, signal_type: str) -> bool:
        """Check if signal type is an info signal."""
        return signal_type in self.INFO_SIGNALS
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get signal handler statistics."""
        return {
            **self.stats,
            'supported_signals': len(self.SIGNAL_HANDLERS),
            'entry_signals': len(self.ENTRY_SIGNALS),
            'exit_signals': len(self.EXIT_SIGNALS),
            'info_signals': len(self.INFO_SIGNALS)
        }
