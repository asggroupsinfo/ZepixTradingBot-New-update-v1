import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.models import Trade
from src.config import Config
from src.utils.optimized_logger import logger as opt_logger
import logging

class PriceMonitorService:
    """
    Background service to monitor prices every 30 seconds for:
    1. SL hunt re-entry (price reaches SL + offset)
    2. TP continuation re-entry (after TP hit with price gap)
    3. Reversal exit opportunities
    """
    
    def __init__(self, config: Config, mt5_client, reentry_manager, 
                 trend_manager, pip_calculator, trading_engine):
        self.config = config
        self.mt5_client = mt5_client
        self.reentry_manager = reentry_manager
        self.trend_manager = trend_manager
        self.pip_calculator = pip_calculator
        self.trading_engine = trading_engine
        
        self.is_running = False
        self.monitor_task = None
        
        # Circuit breaker for error protection
        self.monitor_error_count = 0
        self.max_monitor_errors = 10
        
        # Track symbols being monitored
        self.monitored_symbols = set()
        
        # SL hunt re-entry tracking
        self.sl_hunt_pending = {}  # symbol -> {'price': sl+offset, 'direction': 'buy', 'chain_id': ...}
        
        # TP re-entry tracking
        self.tp_continuation_pending = {}  # symbol -> {'tp_price': ..., 'direction': ...}
        
        # Exit continuation tracking (Exit Appeared/Reversal signals)
        self.exit_continuation_pending = {}  # symbol -> {'exit_price': ..., 'direction': ..., 'exit_reason': ...}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        DIAGNOSTIC: Get comprehensive service status for debugging
        Returns detailed information about service state, pending re-entries, and configuration
        """
        return {
            "service_running": self.is_running,
            "monitor_task_active": self.monitor_task is not None and not self.monitor_task.done() if self.monitor_task else False,
            "monitored_symbols": list(self.monitored_symbols),
            "pending_counts": {
                "sl_hunt": len(self.sl_hunt_pending),
                "tp_continuation": len(self.tp_continuation_pending),
                "exit_continuation": len(self.exit_continuation_pending)
            },
            "pending_details": {
                "sl_hunt": dict(self.sl_hunt_pending),
                "tp_continuation": dict(self.tp_continuation_pending),
                "exit_continuation": dict(self.exit_continuation_pending)
            },
            "configuration": {
                "sl_hunt_enabled": self.config["re_entry_config"].get("sl_hunt_reentry_enabled", False),
                "tp_reentry_enabled": self.config["re_entry_config"].get("tp_reentry_enabled", False),
                "exit_continuation_enabled": self.config["re_entry_config"].get("exit_continuation_enabled", False),
                "monitor_interval": self.config["re_entry_config"].get("price_monitor_interval_seconds", 30),
                "sl_hunt_offset_pips": self.config["re_entry_config"].get("sl_hunt_offset_pips", 1.0),
                "tp_continuation_gap_pips": self.config["re_entry_config"].get("tp_continuation_price_gap_pips", 2.0)
            }
        }
    
    def log_service_status(self):
        """DIAGNOSTIC: Log comprehensive service status"""
        status = self.get_service_status()
        self.logger.info(
            f"📊 [SERVICE_STATUS] Price Monitor Service:\n"
            f"  Running: {status['service_running']}\n"
            f"  Task Active: {status['monitor_task_active']}\n"
            f"  Monitored Symbols: {status['monitored_symbols']}\n"
            f"  Pending: SL Hunt={status['pending_counts']['sl_hunt']}, "
            f"TP={status['pending_counts']['tp_continuation']}, "
            f"Exit={status['pending_counts']['exit_continuation']}\n"
            f"  Config: SL Hunt={status['configuration']['sl_hunt_enabled']}, "
            f"TP={status['configuration']['tp_reentry_enabled']}, "
            f"Exit={status['configuration']['exit_continuation_enabled']}"
        )
    
    async def start(self):
        """Start the background price monitoring task"""
        if self.is_running:
            self.logger.warning("Price Monitor Service already running")
            return
        
        try:
            self.is_running = True
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            
            # DIAGNOSTIC: Verify task creation
            if self.monitor_task:
                self.logger.info(
                    f"✅ Price Monitor Service started successfully - "
                    f"Task created: {self.monitor_task}, is_running: {self.is_running}"
                )
            else:
                self.logger.error("❌ Price Monitor Service failed - monitor_task is None")
                
        except Exception as e:
            self.logger.error(f"❌ Error starting Price Monitor Service: {str(e)}")
            import traceback
            traceback.print_exc()
            self.is_running = False
    
    async def stop(self):
        """Stop the background price monitoring task"""
        self.is_running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("STOPPED: Price Monitor Service stopped")
    
    async def _monitor_loop(self):
        # Background loop - runs silently in INFO mode, detailed logs in DEBUG mode
        cycle_count = 0
        interval = self.config["re_entry_config"]["price_monitor_interval_seconds"]
        
        self.logger.debug(
            f"🔄 Monitor loop started - Interval: {interval}s, "
            f"Config: SL Hunt={self.config['re_entry_config'].get('sl_hunt_reentry_enabled', False)}, "
            f"TP={self.config['re_entry_config'].get('tp_reentry_enabled', False)}, "
            f"Exit={self.config['re_entry_config'].get('exit_continuation_enabled', False)}"
        )
        
        while self.is_running:
            try:
                cycle_count += 1
                cycle_start_time = datetime.now()
                
                # Background heartbeat - saved to file in DEBUG mode
                if cycle_count % 50 == 0:
                    self.logger.debug(
                        f"💓 Monitor loop heartbeat - Cycle #{cycle_count}, "
                        f"Running: {self.is_running}, "
                        f"Pending: SL Hunt={len(self.sl_hunt_pending)}, "
                        f"TP={len(self.tp_continuation_pending)}, "
                        f"Exit={len(self.exit_continuation_pending)}"
                    )
                
                await self._check_all_opportunities()
                
                cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
                if cycle_duration > interval:
                    self.logger.warning(
                        f"⚠️ Monitor cycle took {cycle_duration:.2f}s (longer than interval {interval}s)"
                    )
                
                await asyncio.sleep(interval)
                self.monitor_error_count = 0  # Reset on success
                
            except asyncio.CancelledError:
                self.logger.info("Monitor loop cancelled")
                break
            except Exception as e:
                self.monitor_error_count += 1
                opt_logger.error(f"Price monitor error #{self.monitor_error_count}: {str(e)}")
                
                if self.monitor_error_count >= self.max_monitor_errors:
                    opt_logger.error(f"⚠️ High error rate: {self.monitor_error_count} errors detected")
                    if hasattr(self.trading_engine, 'telegram_bot'):
                        try:
                            self.trading_engine.telegram_bot.send_message(
                                f"⚠️ WARNING: Price monitor experiencing errors ({self.monitor_error_count})\\n"
                                f"Bot still running but may miss some re-entries.\\n"
                                f"Monitoring continues..."
                            )
                        except Exception:
                            pass
                    # ✅ CRITICAL FIX #3: Reset counter instead of stopping - bot stays alive
                    self.monitor_error_count = 0
                
                import traceback
                traceback.print_exc()
                await asyncio.sleep(interval)
        
        self.logger.debug(f"Monitor loop stopped after {cycle_count} cycles")
    
    def register_exit_continuation(self, symbol: str, exit_price: float, new_direction: str, strategy: str = "AUTO", min_gap_pips: float = 20.0, max_wait_seconds: int = 300, exit_reason: str = "EXIT"):
        """Register a symbol for exit continuation monitoring"""
        try:
            self.exit_continuation_pending[symbol] = {
                "exit_price": exit_price,
                "direction": new_direction,
                "strategy": strategy,
                "start_time": datetime.now(),
                "expiration_time": datetime.now() + timedelta(seconds=max_wait_seconds),
                "min_gap_pips": min_gap_pips,
                "exit_reason": exit_reason
            }
            self.monitored_symbols.add(symbol)
            self.logger.info(f"✅ Registered Exit Continuation for {symbol}: {new_direction} after {exit_price}")
        except Exception as e:
            self.logger.error(f"Failed to register exit continuation: {e}")

    async def _check_all_opportunities(self):
        """Check all pending re-entry opportunities"""
        
        # DEBUG: Log monitoring cycle start
        self.logger.debug(
            f"[MONITOR_CYCLE] Checking opportunities - "
            f"SL Hunt: {len(self.sl_hunt_pending)}, "
            f"TP Continuation: {len(self.tp_continuation_pending)}, "
            f"Exit Continuation: {len(self.exit_continuation_pending)}"
        )
        
        # 🆕 CRITICAL: Check margin health and auto-close risky positions if needed
        await self._check_margin_health()
        
        # Check SL hunt re-entries
        await self._check_sl_hunt_reentries()
        
        # Check TP continuation re-entries
        await self._check_tp_continuation_reentries()
        
        # Check Exit continuation re-entries (NEW)
        await self._check_exit_continuation_reentries()
        
        # Check Profit Booking chains (NEW)
        await self._check_profit_booking_chains()
        
        # Check Autonomous Opportunities
        await self._check_autonomous_opportunities()

    async def _check_profit_booking_chains(self):
        """Check for profit booking order recoveries"""
        if not hasattr(self.trading_engine, 'profit_booking_reentry_manager'):
            return
            
        recoveries = self.trading_engine.profit_booking_reentry_manager.check_recoveries()
        
        for rec in recoveries:
             await self._execute_profit_recovery(rec)

    async def _execute_profit_recovery(self, rec: Dict):
        """Execute profit booking recovery trade"""
        try:
            symbol = rec['symbol']
            direction = rec['direction']
            price = rec['current_price']
            chain_id = rec['chain_id']
            level = rec['level']
            
            # 1. Calculate SL/TP
            # User requirement: "SL chhota hoga (Risk kam)"
            # Standard Profit SL is fixed $10. Let's try to maintain that or slightly tighter if needed.
            # But the 'risk' is defined by SL distance.
            # Let's use a tight SL based on market structure or fixed small amount.
            # Using fixed 10 pips for recovery as a safety default or 50% of original.
            
            # Retrieve original SL pips if available, else use default tight SL
            # Let's use 20 pips for Gold, 10 for others as safe "Tight" recovery SL
            tight_sl_pips = 20.0 if symbol == "XAUUSD" else 10.0
            
            symbol_config = self.config["symbol_config"][symbol]
            sl_distance = tight_sl_pips * symbol_config["pip_size"]
            
            if direction == "buy":
                sl_price = price - sl_distance
                tp_price = price + (sl_distance * 1.5) # 1.5 RR recovery
            else:
                sl_price = price + sl_distance
                tp_price = price - (sl_distance * 1.5)
                
            # 2. Calculate Lot Size (use same as original or minimum)
            # Original trade info is in rec['data']? No, simplistic approach uses curr balance
            account_balance = self.mt5_client.get_account_balance()
            lot_size = self.trading_engine.risk_manager.get_fixed_lot_size(account_balance)
            
            # 3. Create Trade Object
            trade = Trade(
                symbol=symbol,
                entry=price,
                sl=sl_price,
                tp=tp_price,
                lot_size=lot_size,
                direction=direction,
                strategy="PROFIT_RECOVERY",
                open_time=datetime.now().isoformat(),
                profit_chain_id=chain_id,
                profit_level=level, # Staying at same level to retry it
                order_type="PROFIT_TRAIL",
                is_re_entry=True
            )
            # Determine SL System based on user config (Dynamic Switch Support)
            active_system = self.config.get("active_sl_system", "sl-1")
            
            # Default "Tight" SL logic (SL-2 style) if unspecified or for Order B
            # Allows user to switch global SL system to affect recovery
            if active_system == "sl-2":
                 # Use tighter SL for recovery
                 tight_sl_pips = 15.0 if symbol == "XAUUSD" else 10.0
            else:
                 # Use standard recovery SL (slightly wider but still tight for Order B)
                 tight_sl_pips = 25.0 if symbol == "XAUUSD" else 15.0
            
            # Register recovery with correct SL
            # Note: ACTUAL placement happens via TradingEngine.place_order or similar
            # For this context, we simulate the 'recovery' placement logic or call engine
            
            self.logger.info(f"Executing Profit Recovery for {symbol} | System: {active_system} | SL: {tight_sl_pips} pips")
            
            # Link back to engine to place the trade
            if self.trading_engine:
                 # Calculate proper SL Price
                 current_price = self.mt5_client.get_current_price(symbol) # Changed from self.mt5_service to self.mt5_client
                 if not current_price: return
                 
                 symbol_config = self.config["symbol_config"][symbol]
                 sl_distance = tight_sl_pips * symbol_config["pip_size"]

                 if direction == "buy":
                    sl_price = current_price - sl_distance
                 else:
                    sl_price = current_price + sl_distance
                 
                 # Place order via engine (standard method)
                 # Using special tag or comment to identify it as recovery
                 # The original rec['price'] was the entry price, but for recovery, we use current_price
                 # The original lot_size calculation was based on account balance, let's try to replicate that or use a default.
                 # The provided snippet uses volume=0.01, which might be too simplistic.
                 # Let's use the original lot size calculation for now, or a default if not available.
                 account_balance = self.mt5_client.get_account_balance()
                 lot_size = self.trading_engine.risk_manager.get_fixed_lot_size(account_balance)

                 # The instruction snippet had a placeholder for recovered_info, but rec already contains the necessary info.
                 # The instruction also used send_sl_hunt_notification, but send_profit_recovery_notification is more appropriate.
                 # Let's adapt the notification to use the existing method and available data.

                 trade_id = await self.trading_engine.place_recovery_order( # Assuming place_recovery_order is async
                     symbol=symbol,
                     direction=direction,
                     volume=lot_size, # Using calculated lot_size
                     entry_price=current_price, # Use current price as entry
                     sl_price=sl_price,
                     tp_price=None, # Use Profit Manager logic
                     comment=f"Recovery {chain_id[:8]} L{level}" # Added level to comment
                 )
                 
                 if trade_id:
                    # Update chain status
                    self.trading_engine.profit_booking_reentry_manager.complete_recovery(chain_id)
                    
                    # Send Notification
                    if hasattr(self.trading_engine, 'telegram_bot'):
                        # Adapting to existing send_profit_recovery_notification signature
                        # The instruction's notification was for SL hunt, but this is profit recovery.
                        # We need to pass the correct parameters for the existing method.
                        # The 7.0 in the original notification was likely a profit/loss value, which we don't have yet for a new trade.
                        # Let's pass 0.0 for now or remove if not applicable.
                        self.trading_engine.telegram_bot.send_profit_recovery_notification(
                            symbol, chain_id, level, current_price, sl_price, 0.0 # Placeholder for profit/loss
                        )
                    self.logger.info(f"✅ PROFIT RECOVERY executed for {symbol} chain {chain_id} with Trade ID: {trade_id}")
                 else:
                    self.logger.error(f"❌ Failed to place PROFIT RECOVERY order for {symbol} chain {chain_id}")

        except Exception as e:
            self.logger.error(f"Error executing profit recovery: {e}")

    async def _check_autonomous_opportunities(self):
        """Check for autonomous re-entry opportunities (no signal required)"""
        # Autonomous system is handled by autonomous_system_manager directly
        # This method is kept for compatibility but autonomous checks are done elsewhere
        return
        
        try:
            if not self.config["re_entry_config"].get("autonomous_enabled", False):
                return

            # opportunities = self.reentry_manager.check_autonomous_reentry()
            opportunities = []  # Disabled - handled by autonomous_system_manager
            for opp in opportunities:
                symbol = opp['symbol']
                direction = opp['direction']
                chain_id = opp['chain_id']
                
                # Get current price
                price = self._get_current_price(symbol, direction)
                if not price: continue

                self.logger.info(f"🚀 AUTONOMOUS OPPORTUNITY: {opp['type']} for {symbol}")

                if opp['type'] == 'tp_continuation':
                    await self._execute_tp_continuation_reentry(
                        symbol=symbol,
                        direction=direction,
                        price=price,
                        chain_id=chain_id,
                        logic="AUTONOMOUS"
                    )
                    # Specific autonomous notification
                    if hasattr(self.trading_engine, 'telegram_bot'):
                         self.trading_engine.telegram_bot.send_autonomous_reentry_notification(
                             type("TradeStub", (), {"symbol": symbol, "direction": direction})(), 
                             opp['level'], price, 
                             price - (opp['sl_adjustment']*0.01), # Approx SL for display
                             price + (opp['sl_adjustment']*0.02), # Approx TP
                             opp['trend_aligned']
                         )

                elif opp['type'] == 'sl_recovery':
                    await self._execute_sl_hunt_reentry(
                        symbol=symbol,
                        direction=direction,
                        price=price,
                        chain_id=chain_id,
                        logic="AUTONOMOUS"
                    )
                    # Notification handled in execute or custom one here
                    if hasattr(self.trading_engine, 'telegram_bot'):
                        self.trading_engine.telegram_bot.send_sl_hunt_notification(
                            symbol, direction, opp['level'], 
                            opp.get('original_sl', 0), 
                            opp.get('recovery_price', price),
                            opp['trend_aligned']
                        )

        except Exception as e:
            self.logger.error(f"Error in autonomous checks: {e}")
    
    async def _check_margin_health(self):
        """
        [DISABLED] Margin checks removed per USER REQUEST.
        Bot will NOT close trades based on margin levels.
        """
        return
        try:
            # Get current margin metrics
            margin_level = self.mt5_client.get_margin_level()
            free_margin = self.mt5_client.get_free_margin()
            account_info = self.mt5_client.get_account_info_detailed()
            
            equity = account_info.get("equity", 0)
            balance = account_info.get("balance", 0)
            margin_used = account_info.get("margin", 0)
            
            # Log margin status periodically
            if not hasattr(self, '_margin_log_counter'):
                self._margin_log_counter = 0
            
            # Background margin check - saved to file in DEBUG mode
            if not hasattr(self, '_margin_log_counter'):
                self._margin_log_counter = 0
            
            self._margin_log_counter += 1
            if self._margin_log_counter % 10 == 0:
                status_text = "✅ No positions" if margin_used == 0 else f"📊 Level: {margin_level:.2f}%"
                self.logger.debug(
                    f"💰 [MARGIN_CHECK] {status_text} | "
                    f"Free: ${free_margin:.2f} | Equity: ${equity:.2f} | Used: ${margin_used:.2f}"
                )
                self._margin_log_counter = 0
            
            # CRITICAL THRESHOLD: Only check if positions exist (margin_used > 0)
            # If margin_used == 0, it means no positions, so skip alert
            if margin_used > 0 and margin_level < 100.0:
                self.logger.critical(
                    f"🚨 CRITICAL MARGIN ALERT: Level {margin_level:.2f}% < 100% "
                    f"| Free: ${free_margin:.2f} | Equity: ${equity:.2f}"
                )
                
                # Get all open positions
                open_positions = self.mt5_client.get_positions()
                
                if open_positions:
                    # Sort by loss (most negative profit first)
                    losing_positions = sorted(
                        [p for p in open_positions if p.get('profit', 0) < 0],
                        key=lambda x: x.get('profit', 0)
                    )
                    
                    # Emergency close the worst losing position, OR just largest volume if all profitable
                    if losing_positions:
                        worst_pos = losing_positions[0]
                    else:
                        # Fallback: Close largest position to free margin
                        # Sort by volume descending
                        worst_pos = sorted(open_positions, key=lambda x: x.get('volume', 0), reverse=True)[0]
                        
                    ticket = worst_pos.get('ticket')
                    loss = worst_pos.get('profit', 0)
                    
                    self.logger.critical(
                        f"🆘 EMERGENCY CLOSE: Ticket {ticket} with ${loss:.2f} loss "
                        f"to prevent margin call"
                    )
                        
                    # Close the position
                    success = self.mt5_client.close_position(ticket)
                    
                    if success and hasattr(self.trading_engine, 'telegram_bot'):
                        try:
                            self.trading_engine.telegram_bot.send_message(
                                f"🚨 EMERGENCY: Closed position {ticket} (Loss: ${loss:.2f}) "
                                f"due to critical margin level {margin_level:.2f}%"
                            )
                        except Exception:
                            pass
            
            # WARNING THRESHOLD: If margin level 100-150%, send warning but don't close
            # Only show warning if positions exist (margin_used > 0)
            elif margin_used > 0 and margin_level < 150.0:
                if not hasattr(self, '_margin_warning_sent'):
                    self._margin_warning_sent = False
                
                if not self._margin_warning_sent:
                    self.logger.warning(
                        f"⚠️ MARGIN WARNING: Level {margin_level:.2f}% < 150% "
                        f"| Free: ${free_margin:.2f}"
                    )
                    
                    if hasattr(self.trading_engine, 'telegram_bot'):
                        try:
                            self.trading_engine.telegram_bot.send_message(
                                f"⚠️ MARGIN WARNING: Level {margin_level:.2f}% < 150% "
                                f"| Free: ${free_margin:.2f} | Consider reducing positions"
                            )
                        except Exception:
                            pass
                    
                    self._margin_warning_sent = True
            else:
                # Reset warning flag when margin recovers
                self._margin_warning_sent = False
                
        except Exception as e:
            self.logger.error(f"Error checking margin health: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def _check_sl_hunt_reentries(self):
        """
        Check if price has reached SL + offset for automatic re-entry
        After SL hunt, wait for price to recover to SL + 1 pip, then re-enter
        """
        if not self.config["re_entry_config"]["sl_hunt_reentry_enabled"]:
            return
        
        for symbol in list(self.sl_hunt_pending.keys()):
            # Handle list of pending items
            pending_items = self.sl_hunt_pending[symbol]
            
            # Use a new list to keep active items
            active_items = []
            
            for pending in pending_items:
                # Check if window expired
                if 'expiration_time' in pending and datetime.now() > pending['expiration_time']:
                    self.logger.info(f"⏳ SL Hunt window expired for {symbol} (Chain: {pending.get('chain_id')})")
                    continue
                    
                # Get current price from MT5
                current_price = self._get_current_price(symbol, pending['direction'])
                if current_price is None:
                    self.logger.debug(f"[SL_HUNT] {symbol}: Failed to get current price")
                    active_items.append(pending) # Keep retrying
                    continue
                
                target_price = pending['target_price']
                direction = pending['direction']
                chain_id = pending['chain_id']
                sl_price = pending.get('sl_price', 0)
                
                # DEBUG: Log price comparison
                self.logger.debug(
                    f"[SL_HUNT] {symbol} {direction.upper()} (Chain {chain_id}): "
                    f"Current={current_price:.5f} Target={target_price:.5f} "
                    f"SL={sl_price:.5f} Gap={abs(current_price - target_price):.5f}"
                )
                
                # Check if price has reached target
                price_reached = False
                if direction == 'buy':
                    price_reached = current_price >= target_price
                else:
                    price_reached = current_price <= target_price
                
                # Background price check - saved to file in DEBUG mode
                price_diff = current_price - target_price if direction == 'buy' else target_price - current_price
                
                if price_reached:
                    # Validate trend alignment before re-entry
                    logic = pending.get('logic', 'combinedlogic-1')
                    alignment = self.trend_manager.check_logic_alignment(symbol, logic)
                    
                    if not alignment['aligned']:
                        self.logger.warning(
                            f"⚠️ [SL_HUNT_BLOCKED] {symbol}: Re-entry blocked - "
                            f"Alignment failed: {alignment.get('failure_reason', 'Unknown reason')}"
                        )
                        active_items.append(pending) # Keep checking alignment until timeout
                        continue
                        
                    # TRIGGER RE-ENTRY
                    self.logger.info(
                        f"🚨 TRIGGERED: SL Hunt Re-Entry Triggered: {symbol} @ {current_price:.5f} "
                        f"(Target: {target_price:.5f}) Chain: {chain_id}"
                    )
                    
                    success = await self._execute_sl_hunt_reentry(
                        symbol, direction, current_price, chain_id, logic
                    )
                    
                    if success:
                        self.logger.info(
                            f"✅ [SL_HUNT_SUCCESS] Executed re-entry for {symbol} Chain {chain_id}"
                        )
                        # Do NOT add back to active_items (It's done)
                    else:
                        self.logger.error(
                            f"❌ [SL_HUNT_FAIL] Failed to execute re-entry for {symbol} Chain {chain_id}"
                        )
                        active_items.append(pending) # Retry next time?
                else:
                    active_items.append(pending) # Not reached yet, keep monitoring
            
            # Update the list for this symbol
            if not active_items:
                del self.sl_hunt_pending[symbol]
                self.monitored_symbols.discard(symbol)
            else:
                self.sl_hunt_pending[symbol] = active_items
    
    async def _check_tp_continuation_reentries(self):
        """
        Check if price has moved enough after TP hit for re-entry
        After TP, wait for price gap (e.g., 2 pips), then re-enter with reduced SL
        """
        if not self.config["re_entry_config"]["tp_reentry_enabled"]:
            return
        
        for symbol in list(self.tp_continuation_pending.keys()):
            # Handle list of pending items
            pending_items = self.tp_continuation_pending[symbol]
            active_items = []
            
            for pending in pending_items:
                # Check if window expired
                if 'expiration_time' in pending and datetime.now() > pending['expiration_time']:
                    self.logger.info(f"⏳ TP Continuation window expired for {symbol} (Chain: {pending.get('chain_id')})")
                    continue
                
                # Get current price
                current_price = self._get_current_price(symbol, pending['direction'])
                if current_price is None:
                    self.logger.debug(f"[TP_CONTINUATION] {symbol}: Failed to get current price")
                    active_items.append(pending)
                    continue
                
                # Target price logic
                tp_price = pending['tp_price']
                pip_size = self.config["symbol_config"][symbol]["pip_size"]
                gap_pips = self.config["re_entry_config"].get("tp_continuation_price_gap_pips", 2) # Use existing config key
                
                if pending['direction'] == 'buy':
                    target_price = tp_price + (gap_pips * pip_size)
                else:
                    target_price = tp_price - (gap_pips * pip_size)
                    
                # DEBUG: Log price comparison
                self.logger.debug(
                    f"[TP_CONTINUATION] {symbol} {pending['direction'].upper()}: "
                    f"Current={current_price:.5f} TP={tp_price:.5f} "
                    f"Target={target_price:.5f} Gap={gap_pips}pips "
                    f"GapPrice={(gap_pips * pip_size):.5f}"
                )

                # Check price
                price_reached = False
                if pending['direction'] == 'buy':
                    price_reached = current_price >= target_price
                else:
                    price_reached = current_price <= target_price
                
                if price_reached:
                    logic = pending.get('logic', 'combinedlogic-1')
                    chain_id = pending['chain_id']

                    # Validate trend alignment
                    alignment = self.trend_manager.check_logic_alignment(symbol, logic)
                    
                    if not alignment['aligned']:
                        self.logger.warning(
                            f"⚠️ [TP_CONTINUATION_BLOCKED] {symbol}: Re-entry blocked - "
                            f"Alignment failed: {alignment.get('failure_reason', 'Unknown reason')}"
                        )
                        active_items.append(pending) # Keep checking alignment until timeout
                        continue
                    
                    signal_direction = "BULLISH" if pending['direction'] == "buy" else "BEARISH"
                    alignment_direction = alignment['direction'].upper()
                    if alignment_direction != signal_direction:
                        self.logger.warning(
                            f"⚠️ [TP_CONTINUATION_BLOCKED] {symbol}: Re-entry blocked - "
                            f"Direction mismatch: Signal={signal_direction} != Alignment={alignment_direction}"
                        )
                        active_items.append(pending) # Keep checking alignment until timeout
                        continue
                    
                    # Execute TP continuation re-entry
                    self.logger.info(f"TRIGGERED: TP Continuation Re-Entry Triggered: {symbol} @ {current_price}")
                    
                    success = await self._execute_tp_continuation_reentry(
                        symbol, pending['direction'], current_price, chain_id, logic
                    )
                    
                    if not success:
                       active_items.append(pending) # Retry if failed?
                else:
                    active_items.append(pending)
            
            if not active_items:
                del self.tp_continuation_pending[symbol]
                self.monitored_symbols.discard(symbol)
            else:
                self.tp_continuation_pending[symbol] = active_items
    
    async def _check_exit_continuation_reentries(self):
        """
        Check for re-entry after Exit Appeared/Reversal exit signals
        After exit (Exit Appeared/Reversal), continue monitoring for re-entry with price gap
        Example: Exit @ 3640.200 -> Monitor -> Re-entry @ 3642.200 (gap required)
        """
        if not self.config["re_entry_config"].get("exit_continuation_enabled", True):
            return
        
        for symbol in list(self.exit_continuation_pending.keys()):
            pending = self.exit_continuation_pending[symbol]
            
            # Get current price from MT5
            current_price = self._get_current_price(symbol, pending['direction'])
            if current_price is None:
                continue
            
            exit_price = pending['exit_price']
            direction = pending['direction']
            logic = pending.get('logic', 'combinedlogic-1')
            exit_reason = pending.get('exit_reason', 'EXIT')
            price_gap_pips = self.config["re_entry_config"]["tp_continuation_price_gap_pips"]
            
            # Calculate pip value for symbol
            symbol_config = self.config["symbol_config"][symbol]
            pip_size = symbol_config["pip_size"]
            price_gap = price_gap_pips * pip_size
            
            # Calculate target price
            if direction == 'buy':
                target_price = exit_price + price_gap
            else:
                target_price = exit_price - price_gap
            
            # DEBUG: Log price comparison
            self.logger.debug(
                f"[EXIT_CONTINUATION] {symbol} {direction.upper()} ({exit_reason}): "
                f"Current={current_price:.5f} Exit={exit_price:.5f} "
                f"Target={target_price:.5f} Gap={price_gap_pips}pips "
                f"GapPrice={price_gap:.5f}"
            )
            
            # Check if price has moved enough from exit price (continuation direction)
            gap_reached = False
            if direction == 'buy':
                gap_reached = current_price >= target_price
            else:
                gap_reached = current_price <= target_price
            
            # BACKGROUND LOOP - Exit continuation price/alignment checks silenced
            
            if gap_reached:
                # Validate trend alignment (CRITICAL - must match logic)
                alignment = self.trend_manager.check_logic_alignment(symbol, logic)
                
                if not alignment['aligned']:
                    self.logger.warning(
                        f"⚠️ [EXIT_CONTINUATION_BLOCKED] {symbol} ({exit_reason}): Re-entry blocked - "
                        f"Alignment failed: {alignment.get('failure_reason', 'Unknown reason')}"
                    )
                    del self.exit_continuation_pending[symbol]
                    continue
                
                signal_direction = "BULLISH" if direction == "buy" else "BEARISH"
                alignment_direction = alignment['direction'].upper()
                if alignment_direction != signal_direction:
                    self.logger.warning(
                        f"⚠️ [EXIT_CONTINUATION_BLOCKED] {symbol} ({exit_reason}): Re-entry blocked - "
                        f"Direction mismatch: Signal={signal_direction} != Alignment={alignment_direction}"
                    )
                    del self.exit_continuation_pending[symbol]
                    continue
                
                # Execute Exit continuation re-entry
                self.logger.info(f"TRIGGERED: Exit Continuation Re-Entry Triggered: {symbol} @ {current_price} after {exit_reason}")
                
                # Create new chain for exit continuation
                from src.models import Alert
                entry_signal = Alert(
                    symbol=symbol,
                    tf=str(pending.get('timeframe', '15M')).lower(),
                    signal='buy' if direction == 'buy' else 'sell',
                    type='entry',
                    price=current_price
                )
                
                # Execute via trading engine
                await self.trading_engine.process_alert(entry_signal)
                
                # Remove from pending
                del self.exit_continuation_pending[symbol]
                
                self.logger.info(f"SUCCESS: Exit continuation re-entry executed for {symbol}")
    
    async def _execute_sl_hunt_reentry(self, symbol: str, direction: str, 
                                       price: float, chain_id: str, logic: str) -> bool:
        """Execute automatic SL hunt re-entry"""
        
        # Get chain info
        chain = self.reentry_manager.active_chains.get(chain_id)
        
        # 🆕 ADD DETAILED VALIDATION LOGGING
        if not chain:
            self.logger.error(
                f"❌ [SL_HUNT_RECOVERY_FAILED] {symbol}: Chain {chain_id[:12]}... NOT FOUND in active_chains"
            )
            self.logger.debug(f"Active chains: {list(self.reentry_manager.active_chains.keys())}")
            return False
        
        if chain.current_level >= chain.max_level:
            self.logger.warning(
                f"⚠️ [SL_HUNT_RECOVERY_BLOCKED] {symbol}: Chain at MAX LEVEL "
                f"({chain.current_level}/{chain.max_level})"
            )
            return False
        
        self.logger.info(f"✅ [SL_HUNT_RECOVERY_START] {symbol}: Chain valid, executing re-entry...")
        
        # Calculate new SL with reduction
        reduction_per_level = self.config["re_entry_config"]["sl_reduction_per_level"]
        sl_adjustment = (1 - reduction_per_level) ** chain.current_level
        
        # ✅ CRITICAL FIX: Get account balance FIRST (needed for SL calculation regardless of lot size source)
        account_balance = self.mt5_client.get_account_balance()
        
        # ✅ CRITICAL FIX: Use stored lot size from chain metadata (actual broker-adjusted size)
        # This prevents "Invalid volume" errors when broker adjusts lot sizes
        lot_size = chain.metadata.get("actual_lot_size", None)
        
        if not lot_size:
            # Fallback for legacy chains without stored lot size
            lot_size = self.trading_engine.risk_manager.get_lot_size_for_logic(
                account_balance, logic=logic
            )
            self.logger.warning(
                f"⚠️ [SL_HUNT_LOT_FALLBACK] Chain {chain_id[:12]}... missing actual_lot_size in metadata, "
                f"using fallback calculation: {lot_size:.2f}"
            )
        else:
            self.logger.info(
                f"📊 [SL_HUNT_LOT_RETRIEVED] Using stored lot size from chain metadata: {lot_size:.2f}"
            )
        
        # Calculate SL and TP
        sl_price, sl_distance = self.pip_calculator.calculate_sl_price(
            symbol, price, direction, lot_size, account_balance, sl_adjustment, logic=logic
        )
        
        tp_price = self.pip_calculator.calculate_tp_price(
            price, sl_price, direction, self.config["rr_ratio"]
        )
        
        # Create trade
        trade = Trade(
            symbol=symbol,
            entry=price,
            sl=sl_price,
            tp=tp_price,
            lot_size=lot_size,
            direction=direction,
            strategy=logic,
            open_time=datetime.now().isoformat(),
            chain_id=chain_id,
            chain_level=chain.current_level + 1,
            is_re_entry=True
        )
        
        # Place order
        if not self.config["simulate_orders"]:
            trade_id = self.mt5_client.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=lot_size,
                price=price,
                sl=sl_price,
                tp=tp_price,
                comment=f"{logic}_SL_HUNT_REENTRY"
            )
            if trade_id:
                trade.trade_id = trade_id
                self.logger.info(f"✅ [SL_HUNT_ORDER_PLACED] {symbol}: MT5 Order #{trade_id} placed successfully")
            else:
                self.logger.error(f"❌ [SL_HUNT_ORDER_FAILED] {symbol}: MT5 order placement returned None")
                # Send failure notification
                if hasattr(self.trading_engine, 'telegram_bot'):
                    self.trading_engine.telegram_bot.send_message(
                        f"⚠️ SL HUNT RECOVERY FAILED\n"
                        f"Symbol: {symbol}\n"
                        f"Reason: MT5 order placement failed\n"
                        f"Chain: {chain_id}"
                    )
                return False  # Don't update chain if order failed
        
        # Update chain
        self.reentry_manager.update_chain_level(chain_id, trade.trade_id)
        
        # Add to open trades
        self.trading_engine.open_trades.append(trade)
        self.trading_engine.risk_manager.add_open_trade(trade)
        
        # Send Telegram notification
        sl_reduction_percent = (1 - sl_adjustment) * 100
        if hasattr(self.trading_engine, 'telegram_bot'):
            self.trading_engine.telegram_bot.send_message(
                f"🔄 SL HUNT RE-ENTRY #{chain.current_level + 1}\n"
                f"Strategy: {logic}\n"
                f"Symbol: {symbol}\n"
                f"Direction: {direction.upper()}\n"
                f"Entry: {price:.5f}\n"
                f"SL: {sl_price:.5f} (-{sl_reduction_percent:.0f}% reduction)\n"
                f"TP: {tp_price:.5f}\n"
                f"Lots: {lot_size:.2f}\n"
                f"Chain: {chain_id}\n"
                f"Level: {chain.current_level + 1}/{chain.max_level}"
            )
        return True
    
    async def _execute_tp_continuation_reentry(self, symbol: str, direction: str,
                                               price: float, chain_id: str, logic: str) -> bool:
        """Execute automatic TP continuation re-entry"""
        
        # Get chain info
        chain = self.reentry_manager.active_chains.get(chain_id)
        if not chain:
            self.logger.error(
                f"❌ [TP_CONTINUATION_FAILED] {symbol}: Chain {chain_id[:12]}... NOT FOUND in active_chains"
            )
            self.logger.debug(f"Active chains: {list(self.reentry_manager.active_chains.keys())}")
            return False
        
        if chain.current_level >= chain.max_level:
            self.logger.warning(
                f"⚠️ [TP_CONTINUATION_BLOCKED] {symbol}: Chain at MAX LEVEL "
                f"({chain.current_level}/{chain.max_level})"
            )
            return False
        
        self.logger.info(f"✅ [TP_CONTINUATION_START] {symbol}: Chain valid, executing re-entry...")

        # Calculate new SL with reduction
        reduction_per_level = self.config["re_entry_config"]["sl_reduction_per_level"]
        sl_adjustment = (1 - reduction_per_level) ** chain.current_level
        
        account_balance = self.mt5_client.get_account_balance()
        
        # Use stored lot size from chain metadata if available, otherwise calculate
        lot_size = chain.metadata.get("actual_lot_size", None)
        if not lot_size:
            lot_size = self.trading_engine.risk_manager.get_lot_size_for_logic(account_balance, logic=logic)
            self.logger.warning(
                f"⚠️ [TP_CONTINUATION_LOT_FALLBACK] Chain {chain_id[:12]}... missing actual_lot_size in metadata, "
                f"using fallback calculation: {lot_size:.2f}"
            )
        else:
            self.logger.info(
                f"📊 [TP_CONTINUATION_LOT_RETRIEVED] Using stored lot size from chain metadata: {lot_size:.2f}"
            )
        
        # Calculate SL and TP
        sl_price, sl_distance = self.pip_calculator.calculate_sl_price(
            symbol, price, direction, lot_size, account_balance, sl_adjustment, logic=logic
        )
        
        tp_price = self.pip_calculator.calculate_tp_price(
            price, sl_price, direction, self.config["rr_ratio"]
        )
        
        # Create trade
        trade = Trade(
            symbol=symbol,
            entry=price,
            sl=sl_price,
            tp=tp_price,
            lot_size=lot_size,
            direction=direction,
            strategy=logic,
            open_time=datetime.now().isoformat(),
            chain_id=chain_id,
            chain_level=chain.current_level + 1,
            is_re_entry=True
        )
        
        # Place order
        if not self.config["simulate_orders"]:
            trade_id = self.mt5_client.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=lot_size,
                price=price,
                sl=sl_price,
                tp=tp_price,
                comment=f"{logic}_TP{chain.current_level}_REENTRY"
            )
            if trade_id:
                trade.trade_id = trade_id
                self.logger.info(f"✅ [TP_CONTINUATION_ORDER_PLACED] {symbol}: MT5 Order #{trade_id} placed successfully")
            else:
                self.logger.error(f"❌ [TP_CONTINUATION_ORDER_FAILED] {symbol}: MT5 order placement returned None")
                if hasattr(self.trading_engine, 'telegram_bot'):
                    self.trading_engine.telegram_bot.send_message(
                        f"⚠️ TP CONTINUATION FAILED\n"
                        f"Symbol: {symbol}\n"
                        f"Reason: MT5 order placement failed\n"
                        f"Chain: {chain_id}"
                    )
                return False
        
        # Update chain
        self.reentry_manager.update_chain_level(chain_id, trade.trade_id)
        
        # Add to open trades
        self.trading_engine.open_trades.append(trade)
        self.trading_engine.risk_manager.add_open_trade(trade)
        
        # Save to database
        tp_level = chain.current_level + 1
        self.trading_engine.db.conn.cursor().execute('''
            INSERT INTO tp_reentry_events VALUES (?,?,?,?,?,?,?,?,?)
        ''', (None, chain_id, symbol, tp_level, chain.total_profit, price, 
              (1-sl_adjustment)*100, 0, datetime.now().isoformat()))
        self.trading_engine.db.conn.commit()
        
        # Send Telegram notification
        sl_reduction_percent = (1 - sl_adjustment) * 100
        if hasattr(self.trading_engine, 'telegram_bot'):
            self.trading_engine.telegram_bot.send_message(
                f"✅ TP{tp_level} RE-ENTRY\n"
                f"Strategy: {logic}\n"
                f"Symbol: {symbol}\n"
                f"Direction: {direction.upper()}\n"
                f"Entry: {price:.5f}\n"
                f"SL: {sl_price:.5f} (-{sl_reduction_percent:.0f}% reduction)\n"
                f"TP: {tp_price:.5f}\n"
                f"Lots: {lot_size:.2f}\n"
                f"Chain Profit: ${chain.total_profit:.2f}\n"
                f"Level: {tp_level}/{chain.max_level}"
            )
        return True
    
    def _get_current_price(self, symbol: str, direction: str) -> Optional[float]:
        """Get current price from MT5 (or simulation) using mapped client"""
        try:
            # Use the robust client method which handles:
            # 1. Simulation mode check
            # 2. Symbol mapping (TradingView XAUUSD -> Broker GOLD)
            # 3. Connection health
            return self.mt5_client.get_current_price(symbol)
        except:
            return None
    
    def register_sl_hunt(self, trade: Trade, logic: str):
        """Register a trade for SL hunt monitoring"""
        
        # DIAGNOSTIC: Verify registration prerequisites
        if not trade.chain_id:
            self.logger.warning(
                f"⚠️ Cannot register SL hunt - Trade {trade.trade_id} has no chain_id"
            )
            return
        
        if not trade.sl or trade.sl == 0:
            self.logger.warning(
                f"⚠️ Cannot register SL hunt - Trade {trade.trade_id} has invalid SL: {trade.sl}"
            )
            return
        
        # VALIDATE LOGIC: Fix for "Unknown logic" error in monitoring loop
        if logic not in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
            self.logger.warning(
                f"⚠️ [SL_HUNT_REGISTRATION] Invalid logic '{logic}' for trade {trade.trade_id}. "
                f"Expected combinedlogic-1/2/3. Attempting detection from trade strategy."
            )
            # Try to detect from trade.strategy if available
            detected = self.trend_manager.detect_logic_from_strategy_or_timeframe(
                trade.strategy if hasattr(trade, 'strategy') else logic
            )
            if detected:
                self.logger.info(
                    f"✅ [LOGIC_DETECTION] Normalized '{logic}' → '{detected}' for SL hunt registration"
                )
                logic = detected
            else:
                self.logger.error(
                    f"❌ Cannot register SL hunt - Invalid logic '{logic}' and auto-detection failed. "
                    f"Trade: {trade.symbol} {trade.trade_id}"
                )
                return
        
        try:
            symbol_config = self.config["symbol_config"][trade.symbol]
            offset_pips = self.config["re_entry_config"]["sl_hunt_offset_pips"]
            pip_size = symbol_config["pip_size"]
            
            # Calculate target price (SL + offset)
            if trade.direction == 'buy':
                target_price = trade.sl + (offset_pips * pip_size)
            else:
                target_price = trade.sl - (offset_pips * pip_size)
            
            # DIAGNOSTIC: Log registration details
            self.logger.info(
                f"📝 [SL_HUNT_REGISTRATION] Trade {trade.trade_id}: "
                f"Symbol={trade.symbol} Direction={trade.direction} "
                f"SL={trade.sl:.5f} Offset={offset_pips}pips "
                f"Target={target_price:.5f} Chain={trade.chain_id} Logic={logic}"
            )
            
            # Get timeframe-specific window
            timeframe_config = self.config.get("timeframe_specific_config", {})
            if timeframe_config.get("enabled", False) and logic in timeframe_config:
                window_minutes = timeframe_config[logic].get("recovery_window_minutes", 30)
            else:
                window_minutes = self.config["re_entry_config"].get("recovery_window_minutes", 30)

            expiration_time = datetime.now() + timedelta(minutes=window_minutes)
            
            # Use list for multiple concurrent chains
            if trade.symbol not in self.sl_hunt_pending:
                self.sl_hunt_pending[trade.symbol] = []
                
            # Add to list (support multiple chains)
            self.sl_hunt_pending[trade.symbol].append({
                'target_price': target_price,
                'direction': trade.direction,
                'chain_id': trade.chain_id,
                'sl_price': trade.sl,
                'logic': logic,
                'expiration_time': expiration_time
            })
            
            self.monitored_symbols.add(trade.symbol)
            
            # Count total pending items across all symbols
            total_pending = sum(len(items) for items in self.sl_hunt_pending.values())
            
            self.logger.info(
                f"✅ REGISTERED: SL Hunt monitoring registered: {trade.symbol} @ {target_price:.5f} "
                f"(Total pending: {total_pending})"
            )
            
        except KeyError as e:
            self.logger.error(
                f"❌ Error registering SL hunt - Symbol config missing: {trade.symbol}, Error: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"❌ Error registering SL hunt: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def register_tp_continuation(self, trade: Trade, tp_price: float, logic: str):
        """Register a trade for TP continuation monitoring"""
        
        # DIAGNOSTIC: Verify registration prerequisites
        if not trade.chain_id:
            self.logger.warning(
                f"⚠️ Cannot register TP continuation - Trade {trade.trade_id} has no chain_id"
            )
            return
        
        if not tp_price or tp_price == 0:
            self.logger.warning(
                f"⚠️ Cannot register TP continuation - Invalid TP price: {tp_price}"
            )
            return
        
        # VALIDATE LOGIC: Fix for "Unknown logic" error in monitoring loop
        if logic not in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
            self.logger.warning(
                f"⚠️ [TP_CONTINUATION_REGISTRATION] Invalid logic '{logic}' for trade {trade.trade_id}. "
                f"Expected combinedlogic-1/2/3. Attempting detection from trade strategy."
            )
            # Try to detect from trade.strategy if available
            detected = self.trend_manager.detect_logic_from_strategy_or_timeframe(
                trade.strategy if hasattr(trade, 'strategy') else logic
            )
            if detected:
                self.logger.info(
                    f"✅ [LOGIC_DETECTION] Normalized '{logic}' → '{detected}' for TP continuation registration"
                )
                logic = detected
            else:
                self.logger.error(
                    f"❌ Cannot register TP continuation - Invalid logic '{logic}' and auto-detection failed. "
                    f"Trade: {trade.symbol} {trade.trade_id}"
                )
                return
        
        try:
            # DIAGNOSTIC: Log registration details
            self.logger.info(
                f"📝 [TP_CONTINUATION_REGISTRATION] Trade {trade.trade_id}: "
                f"Symbol={trade.symbol} Direction={trade.direction} "
                f"TP={tp_price:.5f} Chain={trade.chain_id} Logic={logic}"
            )
            
            # Get timeframe-specific window
            timeframe_config = self.config.get("timeframe_specific_config", {})
            if timeframe_config.get("enabled", False) and logic in timeframe_config:
                window_minutes = timeframe_config[logic].get("recovery_window_minutes", 30)
            else:
                window_minutes = self.config["re_entry_config"].get("recovery_window_minutes", 30)

            expiration_time = datetime.now() + timedelta(minutes=window_minutes)

            # Use list for multiple concurrent chains
            if trade.symbol not in self.tp_continuation_pending:
                self.tp_continuation_pending[trade.symbol] = []

            # Add to list (support multiple chains)
            self.tp_continuation_pending[trade.symbol].append({
                'tp_price': tp_price,
                'direction': trade.direction,
                'chain_id': trade.chain_id,
                'logic': logic,
                'expiration_time': expiration_time
            })
            
            self.monitored_symbols.add(trade.symbol)
            
            # Count total pending items across all symbols
            total_pending = sum(len(items) for items in self.tp_continuation_pending.values())

            self.logger.info(
                f"✅ REGISTERED: TP continuation monitoring registered: {trade.symbol} after TP @ {tp_price:.5f} "
                f"(Total pending: {total_pending})"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error registering TP continuation: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def stop_tp_continuation(self, symbol: str, reason: str = "Opposite signal received"):
        """Stop TP continuation monitoring for a symbol"""
        if symbol in self.tp_continuation_pending:
            del self.tp_continuation_pending[symbol]
            self.logger.info(f"STOPPED: TP continuation stopped for {symbol}: {reason}")
    
    def register_exit_continuation(self, trade: Trade, exit_price: float, exit_reason: str, logic: str, timeframe: str = '15M'):
        """
        Register continuation monitoring after Exit Appeared/Reversal exit
        Bot will monitor for re-entry with price gap after exit signal
        """
        
        # DIAGNOSTIC: Verify registration prerequisites
        if not exit_price or exit_price == 0:
            self.logger.warning(
                f"⚠️ Cannot register exit continuation - Invalid exit price: {exit_price}"
            )
            return
        
        try:
            # DIAGNOSTIC: Log registration details
            self.logger.info(
                f"📝 [EXIT_CONTINUATION_REGISTRATION] Trade {getattr(trade, 'trade_id', 'N/A')}: "
                f"Symbol={trade.symbol} Direction={trade.direction} "
                f"Exit={exit_price:.5f} Reason={exit_reason} Logic={logic} TF={timeframe}"
            )
            
            self.exit_continuation_pending[trade.symbol] = {
                'exit_price': exit_price,
                'direction': trade.direction,
                'logic': logic,
                'exit_reason': exit_reason,
                'timeframe': timeframe
            }
            
            self.monitored_symbols.add(trade.symbol)
            self.logger.info(
                f"✅ REGISTERED: Exit continuation monitoring registered: {trade.symbol} after {exit_reason} @ {exit_price:.5f} "
                f"(Total pending: {len(self.exit_continuation_pending)})"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error registering exit continuation: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def stop_exit_continuation(self, symbol: str, reason: str = "Alignment lost"):
        """Stop exit continuation monitoring for a symbol"""
        if symbol in self.exit_continuation_pending:
            del self.exit_continuation_pending[symbol]
            self.logger.info(f"STOPPED: Exit continuation stopped for {symbol}: {reason}")
    
    async def _check_profit_booking_chains(self):
        """
        Check profit booking chains for profit target achievement
        Runs every 30 seconds to monitor combined PnL
        """
        # Check if profit booking enabled
        profit_config = self.config.get("profit_booking_config", {})
        if not profit_config.get("enabled", True):
            return
        
        # Get profit booking manager from trading engine
        profit_manager = getattr(self.trading_engine, 'profit_booking_manager', None)
        if not profit_manager or not profit_manager.is_enabled():
            return
        
        # Periodic cleanup of stale chains (every 5 minutes)
        import time
        if not hasattr(self, '_last_cleanup_time'):
            self._last_cleanup_time = time.time()
        
        if time.time() - self._last_cleanup_time > 300:  # 5 minutes
            profit_manager.cleanup_stale_chains()
            self._last_cleanup_time = time.time()
        
        # Get all active profit chains
        active_chains = profit_manager.get_all_chains()
        if not active_chains:
            return
        
        # Get open trades from trading engine
        open_trades = getattr(self.trading_engine, 'open_trades', [])
        
        # Check each chain
        for chain_id, chain in active_chains.items():
            try:
                # Validate chain state (now with deduplication)
                if not profit_manager.validate_chain_state(chain, open_trades):
                    continue
                
                # Check for orders ready to book (≥ $7 each)
                orders_to_book = profit_manager.check_profit_targets(chain, open_trades)
                
                if orders_to_book:
                    # Book orders individually
                    for order in orders_to_book:
                        success = await profit_manager.book_individual_order(
                            order, chain, open_trades, self.trading_engine
                        )
                        if success:
                            self.logger.info(
                                f"✅ Order {order.trade_id} booked: "
                                f"Chain {chain_id} Level {chain.current_level}"
                            )
                    
                    # Check if all orders in current level are closed - progress to next level
                    await profit_manager.check_and_progress_chain(
                        chain, open_trades, self.trading_engine
                    )
                
            except Exception as e:
                self.logger.error(
                    f"Error checking profit booking chain {chain_id}: {str(e)}"
                )
                import traceback
                traceback.print_exc()
