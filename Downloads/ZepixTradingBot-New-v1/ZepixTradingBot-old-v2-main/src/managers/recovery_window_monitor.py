"""
Recovery Window Monitor - Continuous Price Monitoring for SL Hunt Recovery
Monitors price movements in real-time and triggers immediate recovery actions
"""

import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
import MetaTrader5 as mt5
import logging

logger = logging.getLogger(__name__)


class RecoveryWindowMonitor:
    """
    Continuous price monitoring system for SL Hunt Recovery
    
    Features:
    - Real-time monitoring (1-second intervals)
    - Immediate action on price recovery
    - Symbol-specific recovery windows
    - Automatic timeout handling
    """
    
    # Symbol-specific recovery windows (in minutes)
    RECOVERY_WINDOWS = {
        # HIGH VOLATILITY - Short Windows (10-20 min)
        "XAUUSD": 15,      # Gold - Very fast moves
        "BTCUSD": 12,      # Bitcoin - Rapid price action
        "XAGUSD": 18,      # Silver - High volatility
        "ETHUSD": 15,      # Ethereum - Fast crypto
        
        # MEDIUM-HIGH VOLATILITY (20-25 min)
        "GBPJPY": 20,      # Very volatile pair
        "GBPUSD": 22,      # Cable - Active moves
        "AUDJPY": 20,      # Commodity currency
        "NZDJPY": 20,      # Similar to AUD
        
        # MEDIUM VOLATILITY (25-35 min)
        "EURUSD": 30,      # Most liquid, moderate
        "USDJPY": 28,      # Major pair, stable
        "AUDUSD": 30,      # Aussie - moderate
        "NZDUSD": 30,      # Kiwi - moderate
        "USDCAD": 28,      # Loonie - moderate
        "EURJPY": 25,      # EUR cross
        "EURGBP": 30,      # EUR cross
        
        # LOW VOLATILITY (35-50 min)
        "USDCHF": 35,      # Swissy - stable
        "EURCHF": 40,      # Very stable
        "AUDNZD": 40,      # Range-bound
        "AUDCAD": 35,      # Lower volatility
        "EURCAD": 35,      # Stable cross
        "GBPAUD": 30,      # Moderate cross
        "GBPNZD": 30,      # Moderate cross
        
        # EXOTIC PAIRS (45-60 min)
        "USDZAR": 50,      # South African Rand
        "USDTRY": 45,      # Turkish Lira
        "USDMXN": 50,      # Mexican Peso
        "USDSEK": 45,      # Swedish Krona
        "USDNOK": 45,      # Norwegian Krone
        "USDDKK": 50,      # Danish Krone
        "USDPLN": 45,      # Polish Zloty
        "USDHUF": 50,      # Hungarian Forint
    }
    
    DEFAULT_RECOVERY_WINDOW = 30  # Default 30 minutes
    MONITORING_INTERVAL = 1  # Check every 1 second
    
    def __init__(self, autonomous_manager):
        """
        Initialize Recovery Window Monitor
        
        Args:
            autonomous_manager: Reference to AutonomousSystemManager
        """
        self.autonomous_manager = autonomous_manager
        self.active_monitors: Dict[int, Dict[str, Any]] = {}
        self.monitor_tasks: Dict[int, asyncio.Task] = {}
        
        logger.info("✅ RecoveryWindowMonitor initialized")
    
    async def start_monitoring(
        self,
        order_id: int,
        symbol: str,
        direction: str,
        sl_price: float,
        original_order: Any,
        order_type: str = "A"
    ) -> None:
        """
        Start continuous monitoring for SL Hunt recovery
        
        Args:
            order_id: Original order ticket ID
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            sl_price: Stop loss price that was hit
            original_order: Original order object
            order_type: "A" (TP Trail) or "B" (Profit Booking)
        """
        
        # Get recovery window for this symbol
        recovery_window_minutes = self.get_recovery_window(symbol)
        
        # Get minimum recovery pips from config
        min_recovery_pips = self.autonomous_manager.config.get(
            "sl_hunt_recovery.min_recovery_pips",
            2
        )
        
        # Calculate recovery threshold price
        pip_value = self._get_pip_value(symbol)
        if direction == "BUY":
            recovery_price = sl_price + (min_recovery_pips * pip_value)
        else:  # SELL
            recovery_price = sl_price - (min_recovery_pips * pip_value)
        
        # Create monitor data
        monitor_data = {
            "order_id": order_id,
            "symbol": symbol,
            "direction": direction,
            "sl_price": sl_price,
            "recovery_price": recovery_price,
            "min_recovery_pips": min_recovery_pips,
            "start_time": datetime.now(),
            "max_duration_seconds": recovery_window_minutes * 60,
            "status": "MONITORING",
            "original_order": original_order,
            "order_type": order_type,
            "check_count": 0
        }
        
        self.active_monitors[order_id] = monitor_data
        
        logger.info(f"""
🔍 SL HUNT MONITORING STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order: #{order_id} (Order {order_type})
Symbol: {symbol}
Direction: {direction}
SL Price: {sl_price}
Recovery Threshold: {recovery_price}
Min Recovery: {min_recovery_pips} pips
Max Window: {recovery_window_minutes} minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Checking every {self.MONITORING_INTERVAL}s...
        """)
        
        # Start monitoring task
        task = asyncio.create_task(self._monitor_loop(order_id))
        self.monitor_tasks[order_id] = task
    
    async def start_monitoring_with_shield(
        self,
        order_id: int,
        symbol: str,
        direction: str,
        sl_price: float,
        original_order: Any,
        recovery_70_level: float,
        shield_ids: list,
        order_type: str = "A"
    ) -> None:
        """
        Start monitoring for Reverse Shield (Deep Monitor) - Path B
        Tracks 70% recovery level trigger for Kill Switch
        """
        # Determine max window based on symbol volatility
        window_minutes = self.RECOVERY_WINDOWS.get(symbol, self.DEFAULT_RECOVERY_WINDOW)
        max_duration = window_minutes * 60
        
        logger.info(f"🎯 STARTING DEEP MONITOR for Order #{order_id} ({symbol})")
        logger.info(f"   Recovery Level (70%): {recovery_70_level}")
        logger.info(f"   Active Shields: {shield_ids}")
        
        self.active_monitors[order_id] = {
            "order_id": order_id,
            "symbol": symbol,
            "direction": direction,
            "sl_price": sl_price,
            "recovery_price": recovery_70_level, # Target is 70% level
            "start_time": datetime.now(),
            "max_duration_seconds": max_duration,
            "original_order": original_order,
            "order_type": order_type,
            "status": "active",
            "check_count": 0,
            # Shield specific data
            "is_shield_mode": True,
            "shield_ids": shield_ids
        }
        
        # Start monitoring task
        self.monitor_tasks[order_id] = asyncio.create_task(
            self._monitor_loop(order_id)
        )
        
    async def _handle_shield_recovery(self, order_id: int, current_price: float, elapsed: float):
        """
        Handle Kill Switch Trigger (70% Recovery Reached)
        Closes shields and immediately restores original trade logic
        """
        logger.info(f"⚠️ KILL SWITCH TRIGGERED for Order #{order_id}")
        
        monitor_data = self.active_monitors.get(order_id)
        if not monitor_data: return
        
        # 1. Execute Kill Switch via Manager
        if hasattr(self.autonomous_manager, 'reverse_shield_manager') and self.autonomous_manager.reverse_shield_manager:
            shield_ids = monitor_data.get('shield_ids', [])
            original_order = monitor_data.get('original_order')
            
            await self.autonomous_manager.reverse_shield_manager.kill_switch(
                shield_ids, original_order, current_price, elapsed
            )
            
        # 2. Restore Original Trade (Immediate Recovery Entry)
        logger.info(f"🔄 Restoring Original Recovery Trade for #{order_id}")
        await self._place_recovery_order(monitor_data, current_price)
        
        # Cleanup
        self._cleanup_monitor(order_id)
    
    async def _monitor_loop(self, order_id: int) -> None:
        """
        Continuous monitoring loop - checks every second
        Updated for v3.0 Shield Support
        
        Args:
            order_id: Order ID to monitor
        """
        
        monitor_data = self.active_monitors.get(order_id)
        if not monitor_data:
            logger.error(f"Monitor data not found for order #{order_id}")
            return
        
        symbol = monitor_data["symbol"]
        direction = monitor_data["direction"]
        recovery_price = monitor_data["recovery_price"]
        start_time = monitor_data["start_time"]
        max_duration = monitor_data["max_duration_seconds"]
        
        try:
            while True:
                # Check if monitor still active
                if order_id not in self.active_monitors:
                    logger.debug(f"Monitor stopped for order #{order_id}")
                    break
                
                monitor_data["check_count"] += 1
                check_count = monitor_data["check_count"]
                
                # Check if window expired
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > max_duration:
                    await self._handle_timeout(order_id, elapsed)
                    break
                
                # Get current price
                current_price = self._get_current_price(symbol)
                if current_price is None:
                    logger.warning(f"Failed to get price for {symbol}, retrying...")
                    await asyncio.sleep(self.MONITORING_INTERVAL)
                    continue
                
                # Check recovery condition
                is_recovered = self._check_recovery(direction, current_price, recovery_price)
                
                # Log progress every 30 checks (30 seconds)
                if check_count % 30 == 0:
                    logger.info(
                        f"🔍 [{symbol}] Check #{check_count} | "
                        f"Price: {current_price} | Target: {recovery_price} | "
                        f"Elapsed: {elapsed:.0f}s"
                    )
                
                if is_recovered:
                    # ✅ IMMEDIATE ACTION - Price recovered!
                    
                    # Detect if Shield Mode (v3.0)
                    if monitor_data.get("is_shield_mode", False):
                         logger.info(f"⚠️ KILL SWITCH CONDITION MET for #{order_id}!")
                         await self._handle_shield_recovery(order_id, current_price, elapsed)
                    else:
                         # Standard Recovery
                         await self._handle_recovery(order_id, current_price, elapsed)
                    break
                
                # Wait for next check
                
                # Check Shield Status (if Shield Mode)
                if monitor_data.get("is_shield_mode", False) and check_count % 5 == 0:
                    try:
                        shield_ids = monitor_data.get("shield_ids", [])
                        if shield_ids:
                             shield_a_id = shield_ids[0]
                             # Check if closed
                             # Need access to mt5 client directly or via autonomous manager?
                             # autonomous_manager has mt5_client
                             # This is simpler if we assume mt5_client is available on self.autonomous_manager
                             if hasattr(self.autonomous_manager, 'mt5_client'):
                                 pos = self.autonomous_manager.mt5_client.get_position(shield_a_id)
                                 # If None, it's closed
                                 if pos is None:
                                     # Verify profit
                                     hist = self.autonomous_manager.mt5_client.get_order_history(shield_a_id)
                                     if hist and hist.get('profit', 0) > 0:
                                         if not monitor_data.get("victory_notified", False):
                                             logger.info(f"💰 Shield A #{shield_a_id} Closed in PROFIT!")
                                             # Notify
                                             if hasattr(self.autonomous_manager, 'rs_notification'):
                                                 await self.autonomous_manager.rs_notification.send_shield_profit_booked(
                                                     shield_order_ticket=shield_a_id,
                                                     symbol=symbol,
                                                     profit_amount=hist.get('profit', 0),
                                                     duration=f"{elapsed:.0f}s",
                                                     is_order_a=True
                                                 )
                                             monitor_data["victory_notified"] = True
                    except Exception as e:
                        logger.error(f"Error checking shield status: {e}")

                await asyncio.sleep(self.MONITORING_INTERVAL)
        
        except Exception as e:
            logger.error(f"Error in monitoring loop for #{order_id}: {e}", exc_info=True)
            self._cleanup_monitor(order_id)
    
    def _check_recovery(self, direction: str, current_price: float, recovery_price: float) -> bool:
        """
        Check if price has recovered
        
        Args:
            direction: "BUY" or "SELL"
            current_price: Current market price
            recovery_price: Target recovery price
        
        Returns:
            bool: True if recovered
        """
        if direction == "BUY":
            return current_price >= recovery_price
        else:  # SELL
            return current_price <= recovery_price
    
    async def _handle_recovery(self, order_id: int, recovery_price: float, elapsed_time: float) -> None:
        """
        Handle successful price recovery - place recovery order immediately
        
        Args:
            order_id: Original order ID
            recovery_price: Price at recovery
            elapsed_time: Time taken to recover (seconds)
        """
        
        monitor_data = self.active_monitors.get(order_id)
        if not monitor_data:
            return
        
        symbol = monitor_data["symbol"]
        check_count = monitor_data["check_count"]
        
        logger.success(f"""
✅ PRICE RECOVERED - IMMEDIATE ACTION!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order: #{order_id}
Symbol: {symbol}
Recovery Price: {monitor_data['recovery_price']}
Current Price: {recovery_price}
Recovery Time: {elapsed_time:.1f} seconds
Check Count: {check_count}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Placing Recovery Order NOW...
        """)
        
        # Clean up monitor
        self._cleanup_monitor(order_id)
        
        # Place recovery order
        await self._place_recovery_order(monitor_data, recovery_price)
    
    async def _handle_timeout(self, order_id: int, elapsed_time: float) -> None:
        """
        Handle recovery window timeout
        
        Args:
            order_id: Original order ID
            elapsed_time: Total elapsed time (seconds)
        """
        
        monitor_data = self.active_monitors.get(order_id)
        if not monitor_data:
            return
        
        max_duration = monitor_data["max_duration_seconds"]
        
        logger.warning(f"""
⏰ RECOVERY WINDOW TIMEOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order: #{order_id}
Elapsed: {elapsed_time/60:.1f} minutes
Max Window: {max_duration/60:.1f} minutes
Status: FAILED - No recovery detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        
        # Clean up monitor
        self._cleanup_monitor(order_id)
        
        # Update chain status to failed
        await self._mark_chain_failed(monitor_data)
    
    async def _place_recovery_order(self, monitor_data: Dict, entry_price: float) -> None:
        """
        Place SL Hunt recovery order
        
        Args:
            monitor_data: Monitor data dictionary
            entry_price: Entry price for recovery order
        """
        
        symbol = monitor_data["symbol"]
        direction = monitor_data["direction"]
        original_order = monitor_data["original_order"]
        order_type = monitor_data["order_type"]
        
        # Calculate recovery order parameters
        # Use tight SL (50% of original)
        original_sl_pips = getattr(original_order, 'sl_pips', 100)
        recovery_sl_pips = original_sl_pips * 0.5
        
        pip_value = self._get_pip_value(symbol)
        
        if direction == "BUY":
            sl_price = entry_price - (recovery_sl_pips * pip_value)
            tp_price = getattr(original_order, 'tp', entry_price + (100 * pip_value))
        else:  # SELL
            sl_price = entry_price + (recovery_sl_pips * pip_value)
            tp_price = getattr(original_order, 'tp', entry_price - (100 * pip_value))
        
        # Get lot size
        lot_size = getattr(original_order, 'volume', 0.01)
        
        try:
            # Place recovery order through autonomous manager
            recovery_order = await self.autonomous_manager.place_sl_hunt_recovery_order(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_price=tp_price,
                lot_size=lot_size,
                original_order_id=monitor_data["order_id"],
                order_type=order_type
            )
            
            if recovery_order:
                logger.success(f"""
🛡️ SL HUNT RECOVERY ORDER PLACED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recovery For: #{monitor_data['order_id']}
New Order: #{recovery_order.get('ticket', 'N/A')}
Entry: {entry_price}
SL: {sl_price} ({recovery_sl_pips:.1f} pips - Tight)
TP: {tp_price}
Lot: {lot_size}
Order Type: {order_type}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recovery attempt in progress...
                """)
            else:
                logger.error(f"❌ Failed to place recovery order for #{monitor_data['order_id']}")
        
        except Exception as e:
            logger.error(f"Error placing recovery order: {e}", exc_info=True)
    
    async def _mark_chain_failed(self, monitor_data: Dict) -> None:
        """
        Mark chain as failed after timeout
        
        Args:
            monitor_data: Monitor data dictionary
        """
        
        try:
            order_type = monitor_data["order_type"]
            order_id = monitor_data["order_id"]
            
            # Update chain status through autonomous manager
            await self.autonomous_manager.handle_recovery_timeout(
                order_id=order_id,
                order_type=order_type
            )
        
        except Exception as e:
            logger.error(f"Error marking chain as failed: {e}", exc_info=True)
    
    def _cleanup_monitor(self, order_id: int) -> None:
        """
        Clean up monitor resources
        
        Args:
            order_id: Order ID to clean up
        """
        
        if order_id in self.active_monitors:
            del self.active_monitors[order_id]
        
        if order_id in self.monitor_tasks:
            task = self.monitor_tasks[order_id]
            if not task.done():
                task.cancel()
            del self.monitor_tasks[order_id]
        
        logger.debug(f"Monitor cleaned up for order #{order_id}")
    
    def stop_monitoring(self, order_id: int) -> None:
        """
        Stop monitoring for a specific order
        
        Args:
            order_id: Order ID to stop monitoring
        """
        
        if order_id in self.active_monitors:
            logger.info(f"Stopping monitor for order #{order_id}")
            self._cleanup_monitor(order_id)
    
    def get_recovery_window(self, symbol: str) -> int:
        """
        Get recovery window for symbol (in minutes)
        
        Args:
            symbol: Trading symbol
        
        Returns:
            int: Recovery window in minutes
        """
        
        window = self.RECOVERY_WINDOWS.get(symbol, self.DEFAULT_RECOVERY_WINDOW)
        logger.debug(f"Recovery window for {symbol}: {window} minutes")
        return window
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Optional[float]: Current price or None if failed
        """
        
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
            
            # Use bid for SELL, ask for BUY (but for monitoring we use mid price)
            return (tick.bid + tick.ask) / 2
        
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def _get_pip_value(self, symbol: str) -> float:
        """
        Get pip value for symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            float: Pip value (0.0001 for most pairs, 0.01 for JPY pairs)
        """
        
        if "JPY" in symbol:
            return 0.01
        else:
            return 0.0001
    
    def get_active_monitors_count(self) -> int:
        """
        Get count of active monitors
        
        Returns:
            int: Number of active monitors
        """
        
        return len(self.active_monitors)
    
    def get_monitor_status(self, order_id: int) -> Optional[Dict]:
        """
        Get status of a specific monitor
        
        Args:
            order_id: Order ID
        
        Returns:
            Optional[Dict]: Monitor status or None if not found
        """
        
        monitor_data = self.active_monitors.get(order_id)
        if not monitor_data:
            return None
        
        elapsed = (datetime.now() - monitor_data["start_time"]).total_seconds()
        remaining = monitor_data["max_duration_seconds"] - elapsed
        
        return {
            "order_id": order_id,
            "symbol": monitor_data["symbol"],
            "direction": monitor_data["direction"],
            "elapsed_seconds": elapsed,
            "remaining_seconds": max(0, remaining),
            "check_count": monitor_data["check_count"],
            "status": monitor_data["status"]
        }
