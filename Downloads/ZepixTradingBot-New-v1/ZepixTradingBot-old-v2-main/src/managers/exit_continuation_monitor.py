"""
Exit Continuation Monitor - Smart Re-Entry System

Monitors trades closed due to:
1. Manual exit
2. Trend reversal
3. Other auto-close conditions

When price reverts to original direction and trend re-aligns within monitoring window,
automatically places re-entry order.

Similar to RecoveryWindowMonitor but for exit scenarios instead of SL hunts.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from src.models import Trade
from src.utils.optimized_logger import logger
import time


class ExitContinuationMonitor:
    """
    Monitor closed trades for potential re-entry opportunities
    
    Logic:
    - Trade closed (manual/reversal)
    - Monitor window: 60 seconds (configurable)
    - Check interval: 5 seconds
    - Conditions: Price moves back to original direction + Trend aligns
    - Action: Place re-entry order at same level
    """
    
    def __init__(self, autonomous_manager):
        """
        Initialize exit continuation monitor
        
        Args:
            autonomous_manager: Reference to AutonomousSystemManager for callbacks
        """
        self.manager = autonomous_manager
        self.config = autonomous_manager.config
        self.mt5_client = autonomous_manager.mt5_client
        self.telegram_bot = autonomous_manager.telegram_bot
        
        # Active monitors: {exit_id: monitor_data}
        self.active_monitors = {}
        
        # Get configuration
        exit_config = self.config["re_entry_config"]["autonomous_config"]["exit_continuation"]
        self.enabled = exit_config.get("enabled", True)
        self.monitor_duration = exit_config.get("monitor_duration_seconds", 60)
        self.check_interval = 5  # Check every 5 seconds
        self.min_reversion_pips = exit_config.get("min_reversion_pips", 2)
        self.trend_check_required = exit_config.get("trend_check_required", True)
        
        # Monitoring tasks
        self.monitoring_tasks = {}
        
        logger.info(
            f"✅ Exit Continuation Monitor initialized "
            f"(Window: {self.monitor_duration}s, Interval: {self.check_interval}s)"
        )
    
    def start_monitoring(self, trade: Trade, exit_reason: str, exit_price: float):
        """
        Start monitoring a closed trade for continuation opportunity
        
        Args:
            trade: Closed trade object
            exit_reason: Why trade was closed (MANUAL_EXIT, REVERSAL_EXIT, etc.)
            exit_price: Price at which trade was closed
        """
        if not self.enabled:
            logger.debug("Exit continuation disabled, skipping monitoring")
            return
        
        # Create unique exit ID
        exit_id = f"EXIT_{trade.symbol}_{trade.trade_id}_{int(time.time())}"
        
        # Store monitor data
        monitor_data = {
            "exit_id": exit_id,
            "trade": trade,
            "exit_reason": exit_reason,
            "exit_price": exit_price,
            "start_time": datetime.now(),
            "original_direction": trade.direction,
            "original_level": getattr(trade, 'profit_level', trade.chain_id if hasattr(trade, 'chain_id') else 1),
            "symbol": trade.symbol,
            "lot_size": trade.lot_size,
            "strategy": trade.strategy,
            "original_entry": trade.entry,
            "original_sl": trade.sl,
            "original_tp": trade.tp,
            "check_count": 0
        }
        
        self.active_monitors[exit_id] = monitor_data
        
        # Start monitoring task
        task = asyncio.create_task(self._monitor_loop(exit_id))
        self.monitoring_tasks[exit_id] = task
        
        # Send notification
        self._send_monitoring_start_notification(monitor_data)
        
        logger.info(
            f"🔄 Exit continuation monitoring started for {trade.symbol} "
            f"(Reason: {exit_reason}, Window: {self.monitor_duration}s)"
        )
    
    async def _monitor_loop(self, exit_id: str):
        """
        Continuous monitoring loop for exit continuation
        
        Checks every N seconds for:
        1. Window timeout
        2. Price reversion to original direction
        3. Trend alignment
        4. Valid entry opportunity
        
        Args:
            exit_id: Unique identifier for this monitoring session
        """
        try:
            monitor_data = self.active_monitors.get(exit_id)
            if not monitor_data:
                return
            
            logger.debug(
                f"🔄 Starting exit continuation monitor loop for {exit_id} "
                f"(Duration: {self.monitor_duration}s)"
            )
            
            while True:
                # Check if monitoring session still active
                if exit_id not in self.active_monitors:
                    logger.debug(f"Monitor {exit_id} no longer active, stopping")
                    break
                
                monitor_data["check_count"] += 1
                
                # Check timeout
                elapsed = (datetime.now() - monitor_data["start_time"]).total_seconds()
                if elapsed >= self.monitor_duration:
                    self._handle_timeout(exit_id, elapsed)
                    break
                
                # Get current price
                current_price = self.mt5_client.get_current_price(monitor_data["symbol"])
                if current_price == 0:
                    logger.debug(f"Failed to get price for {monitor_data['symbol']}, retrying...")
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # Check if conditions met for continuation
                continuation_eligible = await self._check_continuation_conditions(
                    monitor_data, current_price
                )
                
                if continuation_eligible:
                    # Price reverted and trend aligned - place re-entry!
                    await self._handle_continuation(exit_id, current_price, elapsed)
                    break
                
                # Wait before next check
                logger.debug(
                    f"Exit continuation check #{monitor_data['check_count']} for {exit_id}: "
                    f"Not eligible yet (Elapsed: {elapsed:.1f}s / {self.monitor_duration}s)"
                )
                await asyncio.sleep(self.check_interval)
            
        except Exception as e:
            logger.error(f"Error in exit continuation monitor loop for {exit_id}: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            if exit_id in self.active_monitors:
                del self.active_monitors[exit_id]
            if exit_id in self.monitoring_tasks:
                del self.monitoring_tasks[exit_id]
    
    async def _check_continuation_conditions(self, monitor_data: Dict[str, Any], 
                                            current_price: float) -> bool:
        """
        Check if continuation conditions are met
        
        Conditions:
        1. Price has reverted to original direction
        2. Trend is aligned (if trend_check_required)
        3. Sufficient price movement (min_reversion_pips)
        
        Args:
            monitor_data: Monitor session data
            current_price: Current market price
        
        Returns:
            True if continuation should be triggered, False otherwise
        """
        symbol = monitor_data["symbol"]
        direction = monitor_data["original_direction"]
        exit_price = monitor_data["exit_price"]
        
        # Get pip size for this symbol
        symbol_config = self.config.get("symbol_config", {}).get(symbol, {})
        pip_size = symbol_config.get("pip_size", 0.0001)
        
        # Calculate price movement in pips
        if direction == "buy":
            # For BUY: Price should have moved UP from exit
            price_diff_pips = (current_price - exit_price) / pip_size
            price_reverted = price_diff_pips >= self.min_reversion_pips
        else:
            # For SELL: Price should have moved DOWN from exit
            price_diff_pips = (exit_price - current_price) / pip_size
            price_reverted = price_diff_pips >= self.min_reversion_pips
        
        if not price_reverted:
            logger.debug(
                f"Price not reverted enough for {symbol}: "
                f"{price_diff_pips:.1f} pips (need {self.min_reversion_pips})"
            )
            return False
        
        # Check trend alignment if required
        if self.trend_check_required:
            try:
                # Use trend analyzer to check alignment
                trend_aligned = await self._check_trend_alignment(monitor_data, current_price)
                if not trend_aligned:
                    logger.debug(f"Trend not aligned for {symbol}, waiting...")
                    return False
            except Exception as e:
                logger.error(f"Error checking trend alignment: {str(e)}")
                return False
        
        # All conditions met!
        logger.info(
            f"✅ Exit continuation conditions MET for {symbol}: "
            f"Price reverted {price_diff_pips:.1f} pips, Trend aligned"
        )
        return True
    
    async def _check_trend_alignment(self, monitor_data: Dict[str, Any], 
                                     current_price: float) -> bool:
        """
        Check if trend is aligned with original direction
        
        Uses TrendAnalyzer integration similar to SL Hunt Recovery
        
        Args:
            monitor_data: Monitor session data
            current_price: Current price
        
        Returns:
            True if trend aligned, False otherwise
        """
        symbol = monitor_data["symbol"]
        direction = monitor_data["original_direction"]
        
        # Get reentry manager's trend analyzer
        if not hasattr(self.manager.reentry_manager, 'trend_analyzer'):
            logger.warning("TrendAnalyzer not available, skipping trend check")
            return True
        
        trend_analyzer = self.manager.reentry_manager.trend_analyzer
        
        try:
            # Get current trend
            trend = trend_analyzer.get_current_trend(symbol)
            is_aligned = trend_analyzer.is_aligned(direction, trend)
            
            logger.debug(f"Trend check for {symbol}: Direction={direction}, Trend={trend}, Aligned={is_aligned}")
            return is_aligned
            
        except Exception as e:
            logger.error(f"Trend alignment check error: {str(e)}")
            # On error, allow continuation (safety fallback)
            return True
    
    async def _handle_continuation(self, exit_id: str, entry_price: float, elapsed_time: float):
        """
        Handle successful continuation - place re-entry order
        
        Args:
            exit_id: Monitor session ID
            entry_price: Price to enter at
            elapsed_time: Seconds elapsed since exit
        """
        monitor_data = self.active_monitors.get(exit_id)
        if not monitor_data:
            return
        
        logger.info(
            f"✅ EXIT CONTINUATION TRIGGERED - {monitor_data['symbol']} "
            f"recovered in {elapsed_time:.1f}s"
        )
        
        # Place continuation order
        success = await self._place_continuation_order(monitor_data, entry_price)
        
        if success:
            # Send success notification
            self._send_continuation_success_notification(
                monitor_data, entry_price, elapsed_time
            )
        else:
            logger.error(f"Failed to place exit continuation order for {exit_id}")
        
        # Cleanup
        if exit_id in self.active_monitors:
            del self.active_monitors[exit_id]
    
    async def _place_continuation_order(self, monitor_data: Dict[str, Any], 
                                        entry_price: float) -> bool:
        """
        Place re-entry order for exit continuation
        
        Order specs:
        - Same direction as original
        - Same level as original
        - Updated SL/TP based on current price
        - Same lot size
        
        Args:
            monitor_data: Monitor session data
            entry_price: Entry price for new order
        
        Returns:
            True if order placed successfully, False otherwise
        """
        try:
            symbol = monitor_data["symbol"]
            direction = monitor_data["original_direction"]
            lot_size = monitor_data["lot_size"]
            strategy = monitor_data["strategy"]
            
            # Calculate SL and TP (same distance as original)
            original_trade = monitor_data["trade"]
            original_sl_distance = abs(original_trade.entry - original_trade.sl)
            original_tp_distance = abs(original_trade.tp - original_trade.entry)
            
            if direction == "buy":
                sl_price = entry_price - original_sl_distance
                tp_price = entry_price + original_tp_distance
            else:
                sl_price = entry_price + original_sl_distance
                tp_price = entry_price - original_tp_distance
            
            # Create new trade object
            from src.models import Trade
            new_trade = Trade(
                symbol=symbol,
                entry=entry_price,
                sl=sl_price,
                tp=tp_price,
                lot_size=lot_size,
                direction=direction,
                strategy=strategy,
                open_time=datetime.now().isoformat(),
                original_entry=entry_price,
                original_sl_distance=original_sl_distance,
                order_type="TP_TRAIL",  # Same as Order A
                # Preserve chain info if it exists
                chain_id=getattr(original_trade, 'chain_id', None),
                profit_level=getattr(original_trade, 'profit_level', None)
            )
            
            # Place order via MT5
            if not self.config.get("simulate_orders", False):
                trade_id = self.mt5_client.place_order(
                    symbol=symbol,
                    order_type=direction,
                    lot_size=lot_size,
                    price=entry_price,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"{strategy}_EXIT_CONT"
                )
                
                if trade_id:
                    new_trade.trade_id = trade_id
                    logger.success(
                        f"✅ Exit continuation order placed: {symbol} {direction.upper()} "
                        f"@ {entry_price} (ID: {trade_id})"
                    )
                    return True
                else:
                    logger.error(f"Failed to place exit continuation order for {symbol}")
                    return False
            else:
                # Simulation mode
                import random
                new_trade.trade_id = random.randint(100000, 999999)
                logger.info(f"[SIMULATION] Exit continuation order placed: {new_trade.trade_id}")
                return True
        
        except Exception as e:
            logger.error(f"Error placing exit continuation order: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _handle_timeout(self, exit_id: str, elapsed_time: float):
        """
        Handle monitoring window timeout
        
        Args:
            exit_id: Monitor session ID
            elapsed_time: Total elapsed time
        """
        monitor_data = self.active_monitors.get(exit_id)
        if not monitor_data:
            return
        
        logger.info(
            f"⏰ Exit continuation timeout for {monitor_data['symbol']} "
            f"({elapsed_time:.1f}s / {self.monitor_duration}s)"
        )
        
        # Send timeout notification
        self._send_timeout_notification(monitor_data, elapsed_time)
        
        # Cleanup
        if exit_id in self.active_monitors:
            del self.active_monitors[exit_id]
    
    # ==================== TELEGRAM NOTIFICATIONS ====================
    
    def _send_monitoring_start_notification(self, monitor_data: Dict[str, Any]):
        """Send notification when monitoring starts"""
        try:
            trade = monitor_data["trade"]
            message = f"""
🔄 <b>EXIT CONTINUATION MONITORING</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>Trade:</b> #{trade.trade_id}
<b>Symbol:</b> {monitor_data['symbol']}
<b>Exit Reason:</b> {monitor_data['exit_reason']}
<b>Exit Price:</b> {monitor_data['exit_price']:.5f}

⏱️ <b>MONITORING WINDOW</b>
Duration: {self.monitor_duration} seconds
Checking every: {self.check_interval} seconds

🎯 <b>CONDITIONS</b>
• Price reversion to original direction ({monitor_data['original_direction'].upper()})
• Minimum {self.min_reversion_pips} pips movement
• Trend re-alignment
• Valid entry opportunity
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monitoring in progress...
            """
            self.telegram_bot.send_message(message.strip())
        except Exception as e:
            logger.error(f"Error sending monitoring start notification: {str(e)}")
    
    def _send_continuation_success_notification(self, monitor_data: Dict[str, Any], 
                                                entry_price: float, elapsed_time: float):
        """Send notification when continuation order is placed"""
        try:
            trade = monitor_data["trade"]
            message = f"""
✅ <b>EXIT CONTINUATION ORDER PLACED</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>Original Trade:</b> #{trade.trade_id}
<b>Symbol:</b> {monitor_data['symbol']}
<b>Direction:</b> {monitor_data['original_direction'].upper()}

📍 <b>RE-ENTRY DETAILS</b>
Entry: {entry_price:.5f}
SL: {monitor_data['original_sl']:.5f}
TP: {monitor_data['original_tp']:.5f}
Lot: {monitor_data['lot_size']}
Strategy: {monitor_data['strategy']}

⏱️ <b>TIMING</b>
Exit → Re-entry: {elapsed_time:.1f} seconds
Checks performed: {monitor_data['check_count']}

🎯 <b>REASON</b>
Price reverted to original direction
Trend re-aligned
All conditions met ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order active and monitoring...
            """
            self.telegram_bot.send_message(message.strip())
        except Exception as e:
            logger.error(f"Error sending continuation success notification: {str(e)}")
    
    def _send_timeout_notification(self, monitor_data: Dict[str, Any], elapsed_time: float):
        """Send notification when monitoring window times out"""
        try:
            trade = monitor_data["trade"]
            message = f"""
⏰ <b>EXIT CONTINUATION TIMEOUT</b>
━━━━━━━━━━━━━━━━━━━━━━
<b>Trade:</b> #{trade.trade_id}
<b>Symbol:</b> {monitor_data['symbol']}
<b>Elapsed:</b> {elapsed_time:.1f} seconds
<b>Max Window:</b> {self.monitor_duration} seconds
<b>Status:</b> NO RE-ENTRY - Conditions not met
━━━━━━━━━━━━━━━━━━━━━━
Monitoring stopped.
            """
            self.telegram_bot.send_message(message.strip())
        except Exception as e:
            logger.error(f"Error sending timeout notification: {str(e)}")
    
    def stop_all_monitoring(self):
        """Stop all active monitoring sessions (for shutdown)"""
        logger.info(f"Stopping {len(self.monitoring_tasks)} exit continuation monitors...")
        for task in self.monitoring_tasks.values():
            if not task.done():
                task.cancel()
        self.active_monitors.clear()
        self.monitoring_tasks.clear()
        logger.info("✅ All exit continuation monitors stopped")
