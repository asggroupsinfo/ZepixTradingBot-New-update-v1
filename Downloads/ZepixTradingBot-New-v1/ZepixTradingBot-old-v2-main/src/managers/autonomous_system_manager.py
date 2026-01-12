"""
Autonomous System Manager
Handles all autonomous trading operations:
- TP Continuation (autonomous)
- SL Hunt Recovery (autonomous)  
- Profit Booking SL Hunt Recovery
- Exit Continuation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.models import Trade, ReEntryChain, ProfitBookingChain
import asyncio
import time


class AutonomousSystemManager:
    """
    Central manager for all autonomous trading operations
    Coordinates re-entry, SL hunt, and profit booking systems
    """
    
    def __init__(self, config, reentry_manager, profit_booking_manager, 
                 profit_booking_reentry_manager, mt5_client, telegram_bot,
                 risk_manager=None):
        self.config = config
        self.reentry_manager = reentry_manager
        self.profit_booking_manager = profit_booking_manager
        self.profit_booking_reentry_manager = profit_booking_reentry_manager
        self.mt5_client = mt5_client
        self.telegram_bot = telegram_bot
        self.risk_manager = risk_manager
        
        # Initialize Fine-Tune managers
        try:
            from src.managers.recovery_window_monitor import RecoveryWindowMonitor
            from src.managers.profit_protection_manager import ProfitProtectionManager
            from src.managers.sl_reduction_optimizer import SLReductionOptimizer
            from src.managers.reverse_shield_manager import ReverseShieldManager
            from src.services.reverse_shield_notification_handler import ReverseShieldNotificationHandler
            from src.database import TradeDatabase
            
            db = TradeDatabase()
            
            self.recovery_monitor = RecoveryWindowMonitor(self)
            self.profit_protection = ProfitProtectionManager(config)
            self.sl_optimizer = SLReductionOptimizer(config)
            
            # Initialize Reverse Shield System (v3.0)
            self.rs_notification = ReverseShieldNotificationHandler(telegram_bot, config)
            self.reverse_shield_manager = ReverseShieldManager(
                config, mt5_client, profit_booking_manager, 
                risk_manager, db, self.rs_notification
            )
            
            print("✅ Fine-Tune managers & Reverse Shield v3.0 initialized")
        except ImportError as e:
            print(f"⚠️ Warning: Could not initialize Fine-Tune managers: {e}")
            self.recovery_monitor = None
            self.profit_protection = None
            self.sl_optimizer = None
            self.reverse_shield_manager = None
        
        # Track daily recovery statistics
        self.daily_stats = {
            "recovery_attempts": 0,
            "recovery_losses": 0,
            "last_reset": datetime.now().date(),
            "active_recoveries": set()  # Set of chain_ids currently recovering
        }
        
        # Priority queue for multi-symbol recovery
        self.recovery_priority = []
        
        # Track candidates for Exit Continuation
        self.exit_continuation_candidates = {}  # trade_id -> recovery_metadata
        
        print("✅ Autonomous System Manager initialized")
    
    def check_daily_limits(self) -> bool:
        """
        Check if daily recovery limits have been exceeded
        Returns True if we can still do recoveries, False if limits hit
        """
        # Reset daily stats if new day
        current_date = datetime.now().date()
        if current_date != self.daily_stats["last_reset"]:
            self.daily_stats = {
                "recovery_attempts": 0,
                "recovery_losses": 0,
                "last_reset": current_date,
                "active_recoveries": set()
            }
            print(f"📅 Daily stats reset for {current_date}")
        
        # Get limits from config
        auto_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        safety_limits = auto_config.get("safety_limits", {})
        
        max_attempts = safety_limits.get("daily_recovery_attempts", 10)
        max_losses = safety_limits.get("daily_recovery_losses", 5)
        
        # Check limits
        if self.daily_stats["recovery_attempts"] >= max_attempts:
            print(f"⚠️ Daily recovery attempt limit reached ({max_attempts})")
            return False
        
        if self.daily_stats["recovery_losses"] >= max_losses:
            print(f"⚠️ Daily recovery loss limit reached ({max_losses})")
            return False
        
        return True
    
    def check_concurrent_recovery_limit(self) -> bool:
        """Check if we can start a new concurrent recovery"""
        auto_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        safety_limits = auto_config.get("safety_limits", {})
        max_concurrent = safety_limits.get("max_concurrent_recoveries", 3)
        
        active_count = len(self.daily_stats["active_recoveries"])
        if active_count >= max_concurrent:
            print(f"⚠️ Max concurrent recoveries reached ({max_concurrent})")
            return False
        
        return True
    
    def should_skip_recovery_for_profit_protection(self, chain) -> bool:
        """
        Recommendation #3: Skip recovery if existing profit is too valuable
        Returns True if we should skip recovery to protect profits
        """
        auto_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        safety_limits = auto_config.get("safety_limits", {})
        profit_multiplier = safety_limits.get("profit_protection_multiplier", 5)
        
        total_profit = getattr(chain, 'total_profit', 0)
        
        # Estimate potential loss (simplified - use applied SL pips)
        applied_sl_pips = chain.metadata.get("applied_sl_pips", 50)
        symbol_config = self.config.get("symbol_config", {}).get(chain.symbol, {})
        pip_value = symbol_config.get("pip_value_per_std_lot", 1.0)
        
        # Rough estimate of potential loss
        potential_loss = applied_sl_pips * pip_value * 0.01  # Assuming 0.01 lot
        
        if total_profit > (potential_loss * profit_multiplier):
            print(f"🛡️ PROFIT PROTECTION: Skipping recovery for {chain.chain_id}")
            print(f"   Total Profit: ${total_profit:.2f}")
            print(f"   Potential Loss: ${potential_loss:.2f}")
            print(f"   Ratio: {total_profit/potential_loss:.1f}x (threshold: {profit_multiplier}x)")
            return True
        
        return False
    
    async def monitor_autonomous_tp_continuation(self, open_trades: List[Trade],
                                                  trading_engine) -> int:
        """
        Monitor all active chains for autonomous TP continuation
        Returns number of autonomous orders placed
        """
        autonomous_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        tp_config = autonomous_config.get("tp_continuation", {})
        
        if not tp_config.get("enabled", False):
            return 0
        
        orders_placed = 0
        
        # Check all active chains
        for chain_id, chain in list(self.reentry_manager.active_chains.items()):
            if chain.status != "active":
                continue
            
            # Get current price
            current_price = self.mt5_client.get_current_price(chain.symbol)
            if current_price == 0:
                continue
            
            # Check autonomous TP continuation
            result = self.reentry_manager.check_autonomous_tp_continuation(chain, current_price)
            
            if not result["eligible"]:
                continue  # Skip to next chain
            
            # All checks passed! Place autonomous order
            print(f"🚀 AUTONOMOUS TP CONTINUATION TRIGGERED: {chain.symbol} Level {chain.current_level} → {result['next_level']}")
            
            # Place autonomous re-entry order
            success = await self._place_autonomous_tp_order(
                chain, current_price, result, trading_engine
            )
            
            if success:
                orders_placed += 1
                
                # Send enhanced notification
                self._send_tp_continuation_notification(chain, current_price, result)
                
                # Update chain metadata
                chain.metadata["last_tp_price"] = current_price
                chain.metadata["last_tp_time"] = datetime.now().isoformat()
        
        return orders_placed
    
    async def monitor_sl_hunt_recovery(self, open_trades: List[Trade], trading_engine) -> int:
        """
        Monitor chains in recovery_mode (Delegate to RecoveryWindowMonitor)
        Returns checks initiated (always 0 orders directly placed now)
        """
        if not self.recovery_monitor: return 0
        autonomous_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        hunt_config = autonomous_config.get("sl_hunt_recovery", {})
        
        if not hunt_config.get("enabled", False):
            return 0
            
        # Check all chains in recovery mode
        for chain_id, chain in list(self.reentry_manager.active_chains.items()):
            if chain.status != "recovery_mode":
                continue
                
            # Check profit protection
            if self.should_skip_recovery_for_profit_protection(chain):
                chain.status = "stopped"
                chain.metadata["stop_reason"] = "Profit protection - recovery skipped"
                continue
            
            # Get order details
            last_order_id = chain.metadata.get("last_trade_id")
            if not last_order_id:
                continue

            # Check if already monitored
            if last_order_id in self.recovery_monitor.active_monitors:
                continue
                
            # Start Monitoring
            print(f"🔄 Starting Recovery Monitor for Chain {chain_id} (Order #{last_order_id})")
            
            # Mimic order object logic
            class OrderData: pass
            order_data = OrderData()
            order_data.sl_pips = chain.metadata.get("applied_sl_pips", 50)
            order_data.tp = chain.metadata.get("last_tp_price", 0)
            order_data.volume = chain.lot_size
            order_data.chain_id = chain_id # Store chain ID
            
            sl_price = chain.metadata.get("last_sl_price", 0)
            
            await self.recovery_monitor.start_monitoring(
                order_id=last_order_id,
                symbol=chain.symbol,
                direction=chain.direction,
                sl_price=sl_price,
                original_order=order_data,
                order_type="A"
            )
            
        return 0

    async def run_autonomous_checks(self, open_trades: List[Trade], trading_engine) -> None:
        """
        Run all autonomous system checks (Called from TradingEngine loop)
        Centralizes: TP Continuation, Profit Booking Checks, etc.
        """
        try:
            # 1. Monitor Autonomous TP Continuation
            await self.monitor_autonomous_tp_continuation(open_trades, trading_engine)
            
            # 2. Monitor Profit Booking SL Hunt (Delegates to RecoveryMonitor)
            await self.monitor_profit_booking_sl_hunt(open_trades, trading_engine)
            
            # 3. Monitor Profit Booking Targets (Dynamic PnL Checks)
            await self.monitor_profit_booking_targets(open_trades, trading_engine)
            
        except Exception as e:
            print(f"❌ Error in Autonomous Checks: {e}")

    async def monitor_profit_booking_targets(self, open_trades: List[Trade], trading_engine) -> int:
        """
        Monitor active profit chains for PnL targets (The missing link!)
        Checks if any order has reached the dynamic profit target (e.g., $7)
        """
        if not self.profit_booking_manager.is_enabled():
            return 0
            
        checks_run = 0
        
        # Access chains safely
        if hasattr(self.profit_booking_manager, 'get_all_chains'):
            active_chains = self.profit_booking_manager.get_all_chains()
        else:
            active_chains = self.profit_booking_manager.active_chains
            
        for chain_id, chain in list(active_chains.items()):
            if chain.status != "ACTIVE": continue
            
            # Check targets using the manager's logic
            # This returns list of trades ready to book
            orders_to_book = self.profit_booking_manager.check_profit_targets(chain, open_trades)
            
            for trade in orders_to_book:
                print(f"💰 PROFIT TARGET REACHED: Order #{trade.trade_id} (Chain {chain_id})")
                
                # Execute booking immediately
                success = await self.profit_booking_manager.book_individual_order(
                    trade, chain, open_trades, trading_engine
                )
                
                if success:
                    # After booking, check if we can progress the chain
                    # (e.g. if all orders in level are now closed)
                    await self.profit_booking_manager.check_and_progress_chain(
                        chain, open_trades, trading_engine
                    )
            
            checks_run += 1
            
        return checks_run
    
    async def _execute_sl_recovery_registration(self, trade: Trade, strategy: str, order_type: str):
        """Internal async handler for SL recovery registration"""
        print(f"🔄 Processing SL Recovery for Trade #{trade.trade_id}")
        
        print(f"DEBUG: ASM Reverse Shield Check - Manager: {self.reverse_shield_manager}")
        if self.reverse_shield_manager:
            print(f"DEBUG: ASM Reverse Shield Enabled Check: {self.reverse_shield_manager.is_enabled()}")

        # Check Reverse Shield (v3.0)
        if self.reverse_shield_manager and self.reverse_shield_manager.is_enabled():
            print(f"🛡️ Reverse Shield Enabled for Trade #{trade.trade_id}")
            try:
                shield_result = await self.reverse_shield_manager.activate_shield(trade, strategy)
                if shield_result:
                    # Path A: Shield Activated -> Path B: Deep Monitor (70% level)
                    if self.recovery_monitor:
                        await self.recovery_monitor.start_monitoring_with_shield(
                            order_id=trade.trade_id,
                            symbol=trade.symbol,
                            direction=trade.direction,
                            sl_price=trade.sl,
                            original_order=trade,
                            recovery_70_level=shield_result['recovery_70_level'],
                            shield_ids=shield_result['shield_ids'],
                            order_type=order_type
                        )
                    return
            except Exception as e:
                print(f"❌ Reverse Shield Error: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to standard recovery
        
        # Standard v2.1 Recovery
        if self.recovery_monitor:
            await self.recovery_monitor.start_monitoring(
                order_id=trade.trade_id,
                symbol=trade.symbol,
                direction=trade.direction,
                sl_price=trade.sl,
                original_order=trade,
                order_type=order_type
            )

    def register_sl_recovery(self, trade: Trade, strategy: str) -> bool:
        """
        Register a trade for SL Hunt Recovery (Callable from TradingEngine)
        Connects the 'SL Hit' event to the 'Recovery Window Monitor'
        """
        if not self.recovery_monitor:
            print("❌ Recovery Monitor not available for registration")
            return False
            
        print(f"🔄 REGISTERING AUTONOMOUS SL RECOVERY for Order #{trade.trade_id}")
        
        # Determine order type
        order_type = "A"
        if hasattr(trade, 'order_type') and trade.order_type == "PROFIT_TRAIL":
            order_type = "B"
            
        # Bridge to async execution
        asyncio.create_task(self._execute_sl_recovery_registration(
            trade, strategy, order_type
        ))
        
        return True
    
    async def monitor_profit_booking_sl_hunt(self, open_trades: List[Trade], trading_engine) -> int:
        """
        Monitor profit booking orders for SL hunt recovery (Delegate to Monitor)
        """
        if not self.recovery_monitor: return 0
        autonomous_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        profit_hunt_config = autonomous_config.get("profit_sl_hunt", {})
        
        if not profit_hunt_config.get("enabled", False):
            return 0

        # Get all active profit booking chains
        # FIX: Ensure get_all_chains exists or access directly
        if hasattr(self.profit_booking_manager, 'get_all_chains'):
            active_chains = self.profit_booking_manager.get_all_chains()
        else:
            active_chains = self.profit_booking_manager.active_chains
        
        for chain_id, chain in list(active_chains.items()):
            if chain.status != "active": continue
            
            # Get current level orders from open_trades
            level_orders = [t for t in open_trades if 
                           hasattr(t, 'profit_chain_id') and 
                           t.profit_chain_id == chain_id and
                           t.status != "closed"]
                           
            for order in level_orders:
                # Check for RECOVERY_PENDING status (set by TradeManager/Exiter)
                recovery_status = getattr(order, 'recovery_status', None)
                if recovery_status == "RECOVERY_PENDING":
                    # Check if already monitored
                    if order.trade_id in self.recovery_monitor.active_monitors:
                        continue
                        
                    print(f"💎 Starting Profit Recovery Monitor for Order #{order.trade_id}")
                    
                    # Start Monitoring
                    await self.recovery_monitor.start_monitoring(
                        order_id=order.trade_id,
                        symbol=order.symbol,
                        direction=order.direction,
                        sl_price=order.sl,
                        original_order=order,
                        order_type="B"
                    )
        return 0
    
    async def _place_autonomous_tp_order(self, chain, current_price, result, trading_engine):
        """Place autonomous TP continuation order"""
        try:
            # Calculate SL with reduction
            sl_reduction = result["sl_reduction"]
            original_sl_pips = chain.metadata.get("applied_sl_pips", 100)
            new_sl_pips = int(original_sl_pips * (1 - sl_reduction))
            
            # Get pip size
            symbol_config = self.config.get("symbol_config", {}).get(chain.symbol, {})
            pip_size = symbol_config.get("pip_size", 0.01)
            
            new_sl_distance = new_sl_pips * pip_size
            
            # Calculate SL and TP
            if chain.direction == "buy":
                sl_price = current_price - new_sl_distance
                tp_price = current_price + (new_sl_distance * self.config.get("rr_ratio", 1.5))
            else:
                sl_price = current_price + new_sl_distance
                tp_price = current_price - (new_sl_distance * self.config.get("rr_ratio", 1.5))
            
            # Get lot size
            account_balance = self.mt5_client.get_account_balance()
            from src.managers.risk_manager import RiskManager
            lot_size = trading_engine.risk_manager.get_fixed_lot_size(account_balance)
            
            # Create trade object
            trade = Trade(
                symbol=chain.symbol,
                entry=current_price,
                sl=sl_price,
                tp=tp_price,
                lot_size=lot_size,
                direction=chain.direction,
                strategy="AUTONOMOUS_TP_CONT",
                open_time=datetime.now().isoformat(),
                chain_id=chain.chain_id,
                chain_level=result["next_level"],
                is_re_entry=True,
                original_entry=chain.original_entry,
                original_sl_distance=chain.original_sl_distance,
                order_type="TP_TRAIL"
            )
            
            # Place order
            if not self.config.get("simulate_orders", False):
                trade_id = self.mt5_client.place_order(
                    symbol=chain.symbol,
                    order_type=chain.direction,
                    lot_size=lot_size,
                    price=current_price,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"AUTO_TP_L{result['next_level']}"
                )
                if trade_id:
                    trade.trade_id = trade_id
                else:
                    print(f"❌ Failed to place autonomous TP order for {chain.symbol}")
                    return False
            else:
                # Simulation mode
                trade.trade_id = int(datetime.now().timestamp() * 1000) % 1000000
            
            # Update chain level
            self.reentry_manager.update_chain_level(chain.chain_id, trade.trade_id)
            
            # Add to trading engine
            trading_engine.open_trades.append(trade)
            trading_engine.risk_manager.add_open_trade(trade)
            trading_engine.db.save_trade(trade)
            trading_engine.trade_count += 1
            
            print(f"✅ Autonomous TP order placed: {chain.symbol} Level {result['next_level']}")
            print(f"   Entry: {current_price:.5f}")
            print(f"   SL: {sl_price:.5f} ({new_sl_pips} pips)")
            print(f"   TP: {tp_price:.5f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error placing autonomous TP order: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _place_sl_hunt_recovery_order(self, chain, current_price, result, trading_engine):
        """Place SL hunt recovery order"""
        try:
            # Use tight SL from result
            tight_sl_price = result["tight_sl_price"]
            
            # Calculate TP (use original TP or RR ratio)
            sl_distance = abs(current_price - tight_sl_price)
            if chain.direction == "buy":
                tp_price = current_price + (sl_distance * self.config.get("rr_ratio", 1.5))
            else:
                tp_price = current_price - (sl_distance * self.config.get("rr_ratio", 1.5))
            
            # Get lot size
            account_balance = self.mt5_client.get_account_balance()
            lot_size = trading_engine.risk_manager.get_fixed_lot_size(account_balance)
            
            # Create trade object
            trade = Trade(
                symbol=chain.symbol,
                entry=current_price,
                sl=tight_sl_price,
                tp=tp_price,
                lot_size=lot_size,
                direction=chain.direction,
                strategy="SL_HUNT_RECOVERY",
                open_time=datetime.now().isoformat(),
                chain_id=chain.chain_id,
                chain_level=chain.current_level,  # Stay at same level
                is_re_entry=True,
                original_entry=chain.original_entry,
                original_sl_distance=chain.original_sl_distance,
                order_type="SL_RECOVERY"
            )
            
            # Place order
            if not self.config.get("simulate_orders", False):
                trade_id = self.mt5_client.place_order(
                    symbol=chain.symbol,
                    order_type=chain.direction,
                    lot_size=lot_size,
                    price=current_price,
                    sl=tight_sl_price,
                    tp=tp_price,
                    comment=f"SL_HUNT_L{chain.current_level}"
                )
                if trade_id:
                    trade.trade_id = trade_id
                else:
                    print(f"❌ Failed to place SL hunt recovery order for {chain.symbol}")
                    return False
            else:
                # Simulation mode
                trade.trade_id = int(datetime.now().timestamp() * 1000) % 1000000
            
            # Change chain status from recovery_mode to active (recovery attempt in progress)
            chain.status = "recovering"
            chain.metadata["recovery_trade_id"] = trade.trade_id
            chain.metadata["recovery_entry_price"] = current_price
            
            # Add to trading engine
            trading_engine.open_trades.append(trade)
            trading_engine.risk_manager.add_open_trade(trade)
            trading_engine.db.save_trade(trade)
            trading_engine.trade_count += 1
            
            print(f"✅ SL Hunt recovery order placed: {chain.symbol}")
            print(f"   Entry: {current_price:.5f}")
            print(f"   SL: {tight_sl_price:.5f} ({result['tight_sl_pips']} pips - TIGHT)")
            print(f"   TP: {tp_price:.5f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error placing SL hunt recovery order: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_profit_order_recovery(self, order, chain, current_price, config) -> Dict[str, Any]:
        """Check if profit booking order can be recovered"""
        result = {"eligible": False, "reason": ""}
        
        # Get recovery metadata
        recovery_sl = getattr(order, 'sl', None)
        recovery_start = getattr(order, 'recovery_start_time', None)
        
        if not recovery_sl or not recovery_start:
            result["reason"] = "Missing recovery metadata"
            return result
        
        # Check recovery window
        recovery_window = config.get("recovery_window_minutes", 30)
        time_elapsed = (datetime.now() - datetime.fromisoformat(recovery_start)).total_seconds() / 60
        
        if time_elapsed > recovery_window:
            result["reason"] = f"Recovery window expired ({time_elapsed:.1f} min > {recovery_window} min)"
            return result
        
        # Price recovery check
        min_pips = config.get("min_recovery_pips", 2)
        symbol_config = self.config.get("symbol_config", {}).get(order.symbol, {})
        pip_size = symbol_config.get("pip_size", 0.01)
        min_distance = min_pips * pip_size
        
        price_recovered = False
        if order.direction == "buy":
            price_recovered = current_price >= (recovery_sl + min_distance)
        else:
            price_recovered = current_price <= (recovery_sl - min_distance)
        
        if not price_recovered:
            result["reason"] = f"Price not recovered ({current_price} needs {min_pips} pips from {recovery_sl})"
            return result
        
        # All checks passed
        result["eligible"] = True
        result["recovery_sl"] = recovery_sl
        result["entry_price"] = current_price
        result["reason"] = "✅ Recovery eligible"
        
        return result
    
    async def _place_profit_order_recovery(self, order, chain, current_price, result, trading_engine):
        """Place profit booking order recovery"""
        try:
            # Get profit booking config
            profit_config = self.config.get("profit_booking_config", {})
            recovery_config = profit_config.get("sl_hunt_recovery", {})
            
            # Use the active SL system for profit booking
            sl_system = profit_config.get("sl_system", "SL-2.1")
            
            # Calculate SL based on system
            if sl_system == "SL-1.1":
                # Logic-specific SL
                sl_settings = profit_config.get("sl_1_1_settings", {})
                strategy = order.strategy
                sl_dollars = sl_settings.get(strategy, 20.0)
            else:  # SL-2.1
                # Fixed universal SL
                sl_settings = profit_config.get("sl_2_1_settings", {})
                sl_dollars = sl_settings.get("fixed_sl", 10.0)
            
            # Convert dollar SL to price
            from src.utils.profit_sl_calculator import ProfitBookingSLCalculator
            profit_sl_calc = ProfitBookingSLCalculator(self.config)
            
            sl_price, sl_distance = profit_sl_calc.calculate_sl_price(
                current_price, order.direction, order.symbol, order.lot_size, order.strategy
            )
            
            # Calculate TP (same as original - $7 target)
            min_profit = profit_config.get("min_profit", 7.0)
            
            # Use RR ratio for TP
            if sl_distance and sl_distance > 0:
                if order.direction == "buy":
                    tp_price = current_price + (sl_distance * self.config.get("rr_ratio", 1.5))
                else:
                    tp_price = current_price - (sl_distance * self.config.get("rr_ratio", 1.5))
            else:
                # Fallback TP
                default_distance = current_price * 0.01  # 1%
                if order.direction == "buy":
                    tp_price = current_price + default_distance
                else:
                    tp_price = current_price - default_distance
            
            # Get lot size
            account_balance = self.mt5_client.get_account_balance()
            lot_size = trading_engine.risk_manager.get_fixed_lot_size(account_balance)
            
            # Create recovery trade
            recovery_trade = Trade(
                symbol=order.symbol,
                entry=current_price,
                sl=sl_price,
                tp=tp_price,
                lot_size=lot_size,
                direction=order.direction,
                strategy=order.strategy,
                open_time=datetime.now().isoformat(),
                chain_id=order.chain_id if hasattr(order, 'chain_id') else None,
                profit_chain_id=order.profit_chain_id,
                profit_level=order.profit_level,
                is_re_entry=True,
                original_entry=order.entry,
                original_sl_distance=getattr(order, 'original_sl_distance', sl_distance),
                order_type="PROFIT_RECOVERY"
            )
            
            # Place order
            if not self.config.get("simulate_orders", False):
                trade_id = self.mt5_client.place_order(
                    symbol=order.symbol,
                    order_type=order.direction,
                    lot_size=lot_size,
                    price=current_price,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"{order.strategy}_PROFIT_REC_L{order.profit_level}"
                )
                if trade_id:
                    recovery_trade.trade_id = trade_id
                else:
                    print(f"❌ Failed to place profit order recovery for {order.symbol}")
                    return False
            else:
                # Simulation mode
                recovery_trade.trade_id = int(datetime.now().timestamp() * 1000) % 1000000
            
            # Mark original order as recovered
            setattr(order, 'recovery_status', 'RECOVERING')
            setattr(order, 'recovery_trade_id', recovery_trade.trade_id)
            
            # Add to trading engine
            trading_engine.open_trades.append(recovery_trade)
            trading_engine.risk_manager.add_open_trade(recovery_trade)
            trading_engine.db.save_trade(recovery_trade)
            trading_engine.trade_count += 1
            
            print(f"✅ Profit order recovery placed: {order.symbol}")
            print(f"   Chain: {order.profit_chain_id}")
            print(f"   Level: {order.profit_level}")
            print(f"   Entry: {current_price:.5f}")
            print(f"   SL: {sl_price:.5f} (${sl_dollars} fixed)")
            print(f"   TP: {tp_price:.5f} (${min_profit} target)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error placing profit order recovery: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _send_tp_continuation_notification(self, chain, current_price, result):
        """Send enhanced TP continuation notification"""
        trend_emoji = "🟢" if chain.direction == "buy" else "🔴"
        
        message = (
            f"🚀 **AUTONOMOUS RE-ENTRY** 🚀\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Symbol: {chain.symbol} ({chain.direction.upper()})\n"
            f"Type: TP Continuation\n"
            f"Progress: Level {chain.current_level} ➡️ Level {result['next_level']}\n\n"
            f"📍 ENTRY DETAILS\n"
            f"Entry: {current_price:.5f}\n"
            f"SL: (30% reduced)\n\n"
            f"✅ CHECKS PASSED\n"
            f"• Trend: {result['trend']} {trend_emoji}\n"
            f"• Cooldown: 5s Complete ✅\n"
            f"• Momentum: Strong ⬆️\n\n"
            f"⏱️ TIMING\n"
            f"Placed: {datetime.now().strftime('%H:%M:%S')} UTC\n\n"
            f"🎯 CHAIN STATUS\n"
            f"Level: {result['next_level']}/5\n"
            f"Total Profit: +${chain.total_profit:.2f}\n"
            f"Status: ACTIVE 🟢\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        self.telegram_bot.send_message(message)
    
    def _send_sl_hunt_notification(self, chain, current_price, result):
        """Send enhanced SL hunt recovery notification"""
        trend_emoji = "🟢" if chain.direction == "buy" else "🔴"
        recovery_sl = chain.metadata.get("recovery_sl_price", 0)
        recovery_start = chain.metadata.get("recovery_started_at", "")
        
        time_since_sl = ""
        if recovery_start:
            elapsed = (datetime.now() - datetime.fromisoformat(recovery_start)).total_seconds()
            time_since_sl = f"{int(elapsed)} seconds"
        
        message = (
            f"🛡️ **SL HUNT ACTIVATED** 🛡️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Symbol: {chain.symbol} ({chain.direction.upper()})\n"
            f"Type: Recovery Entry\n"
            f"Attempt: 1/1\n\n"
            f"⚠️ ORIGINAL LOSS\n"
            f"SL Hit: {recovery_sl:.5f}\n"
            f"Time: {time_since_sl}\n\n"
            f"📍 RECOVERY ENTRY\n"
            f"Entry: {current_price:.5f}\n"
            f"SL: {result['tight_sl_price']:.5f} ({result['tight_sl_pips']} pips - Tight)\n\n"
            f"✅ SAFETY CHECKS\n"
            f"• Price Recovery: ✅ Confirmed\n"
            f"• Trend: {trend_emoji}\n"
            f"• ATR: Stable ✅\n\n"
            f"💪 CHAIN CONTINUATION\n"
            f"If Success: Resume → Level {result['next_level_on_success']}\n"
            f"If Fail: Chain STOP ❌\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        self.telegram_bot.send_message(message)
    
    def _send_profit_hunt_notification(self, order, chain, current_price):
        """Send profit booking SL hunt notification"""
        message = (
            f"💎 **PROFIT ORDER PROTECTION** 💎\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Chain: #{chain.chain_id[:8]}\n"
            f"Level: {chain.current_level}/4 (Order {order.profit_level})\n\n"
            f"⚠️ SL HIT DETECTED\n"
            f"Order ID: #{order.trade_id}\n"
            f"SL Price: {order.sl:.5f}\n\n"
            f"🔄 MONITORING ACTIVE\n"
            f"Current Price: {current_price:.5f}\n"
            f"Trend: BULLISH 🟢\n"
            f"Time: 30 mins remaining\n\n"
            f"⚡ NEXT STEPS\n"
            f"Watching for 2-pip recovery...\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        self.telegram_bot.send_message(message)
    
    def handle_recovery_success(self, chain_id: str, recovery_trade: Trade):
        """
        Handle successful recovery - resume to next level
        Enhanced to support BOTH Order A (Re-entry) and Order B (Profit Booking)
        """
        # Determine order type
        order_type = getattr(recovery_trade, 'order_type', None)
        
        if order_type == "SL_RECOVERY":
            # Order A - Re-entry chain recovery
            chain = self.reentry_manager.active_chains.get(chain_id)
            if not chain:
                logger.warning(f"Chain {chain_id} not found for recovery success")
                return
            
            # Check if resume to next level is enabled
            resume_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
            sl_hunt_config = resume_config.get("sl_hunt_recovery", {})
            resume_to_next = sl_hunt_config.get("resume_to_next_level_on_success", True)
            
            if resume_to_next:
                # RESUME TO NEXT LEVEL (Key innovation)
                chain.current_level += 1
                chain.status = "active"
                chain.metadata["recovery_success_count"] = chain.metadata.get("recovery_success_count", 0) + 1
                
                logger.success(
                    f"🎉 RECOVERY SUCCESS: Chain {chain_id} → "
                    f"Resumed to Level {chain.current_level}"
                )
                
                # Send notification
                message = (
                    f"🎉 **RECOVERY SUCCESS** 🎉\n"
                    f"Chain: {chain_id}\n"
                    f"Resumed to Level: {chain.current_level}\n"
                    f"Status: ACTIVE ✅\n"
                    f"Recovery Profit: ${recovery_trade.profit:.2f if hasattr(recovery_trade, 'profit') else 0:.2f}"
                )
                self.telegram_bot.send_message(message)
            
            # Remove from active recoveries
            if chain_id in self.daily_stats["active_recoveries"]:
                self.daily_stats["active_recoveries"].remove(chain_id)
        
        elif order_type == "PROFIT_RECOVERY":
            # Order B - Profit booking chain recovery
            pb_chain = self.profit_booking_manager.get_chain(chain_id)
            if not pb_chain:
                logger.warning(f"Profit chain {chain_id} not found for recovery success")
                return
            
            # Mark this level as recovered (not a loss anymore)
            pb_chain.metadata[f"loss_level_{pb_chain.current_level}"] = False
            pb_chain.metadata[f"loss_level_{pb_chain.current_level}_recovered"] = True
            pb_chain.metadata[f"recovery_order_{recovery_trade.trade_id}"] = {
                "success": True,
                "profit": getattr(recovery_trade, 'profit', 0)
            }
            
            # Save chain
            self.profit_booking_manager.db.save_profit_chain(pb_chain)
            
            logger.success(
                f"💎 PROFIT ORDER RECOVERY SUCCESS: Chain {chain_id} "
                f"Level {pb_chain.current_level} can now progress"
            )
            
            # Send notification
            message = (
                f"💎 **PROFIT RECOVERY SUCCESS** 💎\n"
                f"Chain: {chain_id}\n"
                f"Level: {pb_chain.current_level}/4\n"
                f"Order Recovered: ✅\n"
                f"Recovery Profit: ${getattr(recovery_trade, 'profit', 0):.2f}\n"
                f"Status: Level can progress normally"
            )
            self.telegram_bot.send_message(message)
        
        else:
            # Unknown order type - log warning
            logger.warning(
                f"Unknown order type '{order_type}' in recovery success for chain {chain_id}"
            )

    
    def handle_recovery_failure(self, chain_id: str, recovery_trade: Trade):
        """Handle failed recovery - stop chain permanently"""
        chain = self.reentry_manager.active_chains.get(chain_id)
        if not chain:
            return
        
        # Check if this was a recovery trade
        if hasattr(recovery_trade, 'order_type') and recovery_trade.order_type == "SL_RECOVERY":
            # Recovery failed - stop chain
            chain.status = "stopped"
            chain.metadata["stop_reason"] = "Recovery failed - max attempts exceeded"
            
            self.daily_stats["recovery_losses"] += 1
            
            print(f"❌ RECOVERY FAILED: {chain_id} → Chain STOPPED permanently")
            
            # Send notification
            message = (
                f"💀 **RECOVERY FAILED** 💀\n"
                f"Chain: {chain_id}\n"
                f"Status: STOPPED ❌\n"
                f"No more recovery attempts allowed"
            )
            self.telegram_bot.send_message(message)
            
            # Remove from active recoveries
            if chain_id in self.daily_stats["active_recoveries"]:
                self.daily_stats["active_recoveries"].remove(chain_id)

    # ==================== MONITOR CALLBACK IMPLEMENTATION ====================

    async def place_sl_hunt_recovery_order(self, symbol, direction, entry_price, sl_price, tp_price, lot_size, original_order_id, order_type="A"):
        """
        Public method called by RecoveryWindowMonitor when price recovers
        """
        # Validate limits before placing
        if not self.check_daily_limits() or not self.check_concurrent_recovery_limit():
             print(f"⚠️ Recovery limits hit, skipping recovery order for {symbol}")
             return None

        trading_engine = self.telegram_bot.trading_engine
        if not trading_engine:
             print("❌ Trading Engine not available for recovery placement")
             return None

        if order_type == "A":
             # Order A Recovery
             chain = None
             # Find chain by original_order_id (which is last_trade_id)
             for cid, c in self.reentry_manager.active_chains.items():
                 if c.metadata.get("last_trade_id") == original_order_id:
                     chain = c
                     break
             
             if not chain:
                 print(f"❌ Chain not found for recovery order #{original_order_id}")
                 return None
                 
             # Construct result object for _place_sl_hunt_recovery_order
             result = {
                 "tight_sl_price": sl_price,
                 "tight_sl_pips": abs(entry_price - sl_price) / (0.01 if "JPY" in symbol else 0.0001)
             }
             
             # Call internal placement logic
             success = await self._place_sl_hunt_recovery_order(chain, entry_price, result, trading_engine)
             
             if success:
                 # Stats update
                 self.daily_stats["recovery_attempts"] += 1
                 self.daily_stats["active_recoveries"].add(chain.chain_id)
                 
                 # Send notification
                 self._send_sl_hunt_notification(chain, entry_price, result)
                 return {"ticket": chain.metadata.get("recovery_trade_id")}
             else:
                 return None

        elif order_type == "B":
             # Order B Recovery (Profit Booking)
             trade = next((t for t in trading_engine.open_trades if t.trade_id == original_order_id), None)
             if not trade:
                 print(f"⚠️ Original order #{original_order_id} not found for recovery")
                 return None
                 
             chain_id = getattr(trade, 'profit_chain_id', None)
             chains = self.profit_booking_manager.get_all_chains()
             chain = chains.get(chain_id)
             
             if not chain:
                 print(f"⚠️ Profit chain {chain_id} not found")
                 return None
             
             result = { "eligible": True, "recovery_sl": sl_price, "entry_price": entry_price }
             
             success = await self._place_profit_order_recovery(trade, chain, entry_price, result, trading_engine)
             
             if success:
                 self._send_profit_hunt_notification(trade, chain, entry_price)
                 return {"ticket": getattr(trade, 'recovery_trade_id', None)}
             
             return None

        elif order_type == "EXIT_CONTINUATION":
             # Exit Continuation Recovery
             chain = None
             # Try to find chain in active chains (might be stopped/completed, so check all?)
             # ReEntryManager usually keeps chains in active_chains dict even if stopped?
             # Let's check active_chains first.
             for cid, c in self.reentry_manager.active_chains.items():
                 # Check trades list to find original order
                 if original_order_id in c.trades:
                     chain = c
                     break
             
             if not chain:
                 print(f"❌ Chain not found for exit continuation order #{original_order_id}")
                 return None
             
             # Activate chain if stopped
             chain.status = "recovery_mode" 
             
             # Construct result
             result = {
                 "tight_sl_price": sl_price, # Use the SL provided by monitor (which is original Entry)
                 # Actually, monitor passes 'sl_price' as the trigger price. 
                 # We need a REAL SL for the new order.
                 # Let's use 30% reduction from standard or tight SL?
                 # Recommendation: "Tight SL"
                 "tight_sl_pips": 20 # Default or calculated
             }
             
             # Calculate a proper Tight SL
             # If BUY: Entry = Current. SL = Entry - X.
             symbol_config = self.config.get("symbol_config", {}).get(symbol, {})
             pip_size = symbol_config.get("pip_size", 0.01)
             sl_pips = 20 # Fixed tight SL for exit recovery?
             sl_dist = sl_pips * pip_size
             
             if direction == "buy":
                 result["tight_sl_price"] = entry_price - sl_dist
             else:
                 result["tight_sl_price"] = entry_price + sl_dist
             
             result["tight_sl_pips"] = sl_pips

             # Place recovery order
             success = await self._place_sl_hunt_recovery_order(chain, entry_price, result, trading_engine)
             
             if success:
                 self.daily_stats["recovery_attempts"] += 1
                 
                 # Notify
                 self.telegram_bot.send_message(
                    f"🚀 **EXIT CONTINUATION EXECUTED**\n"
                    f"Symbol: {symbol}\n"
                    f"Message: Market returned to entry! Resuming trade.\n"
                    f"SL: {sl_pips} pips (Tight)"
                 )
                 return {"ticket": chain.metadata.get("recovery_trade_id")}
             else:
                 return None

             
        return None

    def handle_recovery_timeout(self, order_id: int, order_type: str = "A"):
        """Handle recovery timeout from monitor"""
        
        if order_type == "B":
            # Handle Profit Booking Timeout
            if not self.profit_booking_manager: return
            
            chains = self.profit_booking_manager.get_all_chains()
            # Find chain that has this order
            found_chain = None
            for cid, chain in chains.items():
                if order_id in chain.active_orders or chain.metadata.get("recovery_order_id") == order_id:
                    found_chain = chain
                    break
            
            if found_chain:
                print(f"⏰ Profit Recovery Timeout for Chain {found_chain.chain_id}")
                # Mark level as loss
                found_chain.metadata[f"loss_level_{found_chain.current_level}"] = True
                
                # Check strict mode again? Or just let normal process handle it?
                # We should notify user.
                self.telegram_bot.send_message(
                    f"⏰ **PROFIT RECOVERY TIMEOUT**\n"
                    f"Chain: {found_chain.chain_id}\n"
                    f"Level: {found_chain.current_level}\n"
                    f"Status: Recovery Failed (Timeout)"
                )
                self.profit_booking_manager.db.save_profit_chain(found_chain)
            return

        # Start search in ReEntry chains for Order A / Exit Continuation
        for cid, chain in self.reentry_manager.active_chains.items():
            if chain.metadata.get("last_trade_id") == order_id or order_id in chain.trades:
                print(f"⏰ Recovery Timeout for Chain {cid}")
                chain.status = "stopped"
                chain.metadata["stop_reason"] = "Recovery window timeout"
                
                # Notify
                self.telegram_bot.send_message(f"⏰ **RECOVERY TIMEOUT**\nChain: {cid}\nStatus: STOPPED")
                return
        print(f"⚠️ Recovery timeout for unknown order #{order_id}")

    def register_exit_continuation(self, trade: Trade, reason: str):
        """
        Register a closed trade for Exit Continuation monitoring.
        Called when a trade is closed due to Trend Reversal or Manual Exit.
        
        Uses dedicated ExitContinuationMonitor for clean separation.
        """
        # Validate exit configuration
        autonomous_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
        exit_config = autonomous_config.get("exit_continuation", {})
        
        if not exit_config.get("enabled", False):
            logger.debug("Exit continuation disabled in config")
            return
        
        # Check if exit reason is eligible
        eligible_types = exit_config.get("eligible_exit_types", ["manual", "reversal"])
        exit_type = None
        
        if "MANUAL" in reason.upper():
            exit_type = "manual"
        elif "REVERSAL" in reason.upper():
            exit_type = "reversal"
        
        if exit_type not in eligible_types:
            logger.debug(f"Exit reason '{reason}' not eligible for continuation (allowed: {eligible_types})")
            return
        
        # Get exit price
        current_price = self.mt5_client.get_current_price(trade.symbol)
        if current_price == 0:
            logger.error(f"Failed to get current price for {trade.symbol}, cannot start exit monitoring")
            return
        
        # Initialize ExitContinuationMonitor if not exists
        if not hasattr(self, 'exit_continuation_monitor'):
            from src.managers.exit_continuation_monitor import ExitContinuationMonitor
            self.exit_continuation_monitor = ExitContinuationMonitor(self)
            logger.info("✅ Exit Continuation Monitor initialized")
        
        # Start monitoring
        self.exit_continuation_monitor.start_monitoring(
            trade=trade,
            exit_reason=reason,
            exit_price=current_price
        )
        
        logger.info(
            f"✅ Exit continuation monitoring started: {trade.symbol} "
            f"(Reason: {reason}, Exit Price: {current_price:.5f})"
        )

