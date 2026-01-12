from typing import Dict, Any, List, Optional
from datetime import datetime
from src.models import Trade, ProfitBookingChain
from src.config import Config
from src.database import TradeDatabase
from src.clients.mt5_client import MT5Client
from src.utils.pip_calculator import PipCalculator
from src.managers.risk_manager import RiskManager
from src.utils.optimized_logger import logger
import uuid
import logging
import time

class ProfitBookingManager:
    """
    Manages profit booking chains for pyramid compounding system
    - Level 0: 1 order → $10 profit target → Level 1
    - Level 1: 2 orders → $20 profit target → Level 2
    - Level 2: 4 orders → $40 profit target → Level 3
    - Level 3: 8 orders → $80 profit target → Level 4
    - Level 4: 16 orders → $160 profit target → Max level
    """
    
    def __init__(self, config: Config, mt5_client: MT5Client, 
                 pip_calculator: PipCalculator, risk_manager: RiskManager,
                 db: TradeDatabase):
        self.config = config
        self.mt5_client = mt5_client
        self.pip_calculator = pip_calculator
        self.risk_manager = risk_manager
        self.db = db
        
        # Active profit booking chains
        self.active_chains: Dict[str, ProfitBookingChain] = {}
        
        # Get configuration
        self.profit_config = config.get("profit_booking_config", {})
        self.enabled = self.profit_config.get("enabled", True)
        # NEW: Fixed $7 minimum profit for all levels (replaces progressive targets)
        self.min_profit = self.profit_config.get("min_profit", 7.0)  # $7 minimum per order
        self.multipliers = self.profit_config.get("multipliers", [1, 2, 4, 8, 16])
        self.max_level = self.profit_config.get("max_level", 4)
        
        # Import profit booking SL calculator
        from src.utils.profit_sl_calculator import ProfitBookingSLCalculator
        self.profit_sl_calculator = ProfitBookingSLCalculator(config)
        
        # Keep old logger for backward compatibility with existing diagnostic logs
        self.logger = logging.getLogger(__name__)
        
        # Error deduplication: Track missing order checks to prevent spam
        self.checked_missing_orders: Dict[str, int] = {}  # order_id -> check_count
        self.last_error_log_time: Dict[str, float] = {}  # order_id -> last_log_timestamp
        self.stale_chains: set = set()  # Chains marked as stale
    
    def is_enabled(self) -> bool:
        """Check if profit booking system is enabled"""
        return self.enabled
    
    def create_profit_chain(self, trade: Trade) -> Optional[ProfitBookingChain]:
        """
        Create a new profit booking chain from Order B (PROFIT_TRAIL)
        Returns chain if created successfully, None otherwise
        """
        if not self.is_enabled():
            return None
        
        if trade.order_type != "PROFIT_TRAIL":
            return None  # Only create chains for Profit Trail orders
        
        try:
            chain_id = f"PROFIT_{trade.symbol}_{uuid.uuid4().hex[:8]}"
            
            chain = ProfitBookingChain(
                chain_id=chain_id,
                symbol=trade.symbol,
                direction=trade.direction,
                base_lot=trade.lot_size,
                current_level=0,
                max_level=self.max_level,
                total_profit=0.0,
                active_orders=[trade.trade_id] if trade.trade_id else [],
                status="ACTIVE",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                profit_targets=[self.min_profit] * (self.max_level + 1),  # All levels use $7 minimum
                multipliers=self.multipliers.copy(),
                sl_reductions=[0] * (self.max_level + 1),  # No SL reduction (uses fixed $10 SL)
                metadata={
                    "strategy": trade.strategy,
                    "original_entry": trade.entry,
                    "original_sl": trade.sl,
                    "original_tp": trade.tp
                }
            )
            
            self.active_chains[chain_id] = chain
            trade.profit_chain_id = chain_id
            trade.profit_level = 0
            
            # Save to database
            self.db.save_profit_chain(chain)
            
            # Sync chain state with MT5 immediately after creation
            # This ensures chain state is synced from the start
            if trade.trade_id:
                # Verify the order exists in MT5 and update chain state
                mt5_position = self.mt5_client.get_position(trade.trade_id)
                if mt5_position:
                    # Order exists in MT5, chain is properly synced
                    self.logger.debug(
                        f"Chain {chain_id} synced with MT5: Order {trade.trade_id} verified"
                    )
                else:
                    # Order not found in MT5 yet (might be pending)
                    self.logger.debug(
                        f"Chain {chain_id} created but order {trade.trade_id} not yet in MT5"
                    )
                
                # Save profit booking order to database
                self.db.save_profit_booking_order(
                    str(trade.trade_id),
                    chain_id,
                    0,
                    self.min_profit,  # $7 minimum
                    0,  # No SL reduction (uses fixed $10 SL)
                    "OPEN"
                )
            
            self.logger.info(f"SUCCESS: Profit booking chain created: {chain_id} for {trade.symbol}")
            return chain
            
        except Exception as e:
            self.logger.error(f"Error creating profit chain: {str(e)}")
            return None
    
    def get_profit_target(self, level: int) -> float:
        """Get profit target for a specific level (DEPRECATED - kept for compatibility)"""
        # Always return min_profit for all levels
        return self.min_profit
    
    def get_order_multiplier(self, level: int) -> int:
        """Get order multiplier for a specific level"""
        if 0 <= level < len(self.multipliers):
            return self.multipliers[level]
        return 1
    
    def get_sl_reduction(self, level: int) -> float:
        """Get SL reduction percentage for a specific level (DEPRECATED - always returns 0 for fixed $10 SL)"""
        # Always return 0 - profit booking uses fixed $10 SL, no reductions
        return 0.0
    
    def calculate_combined_pnl(self, chain: ProfitBookingChain, 
                               open_trades: List[Trade]) -> float:
        """
        Calculate combined unrealized PnL for all orders in current level
        Returns total PnL in dollars
        """
        try:
            # Get all trades for this chain at current level
            chain_trades = [
                t for t in open_trades
                if t.profit_chain_id == chain.chain_id 
                and t.profit_level == chain.current_level
                and t.status == "open"
            ]
            
            if not chain_trades:
                return 0.0
            
            # Get current price
            current_price = self.mt5_client.get_current_price(chain.symbol)
            if current_price == 0:
                return 0.0
            
            # Calculate PnL for each trade and sum
            total_pnl = 0.0
            
            for trade in chain_trades:
                symbol_config = self.config["symbol_config"][trade.symbol]
                pip_size = symbol_config["pip_size"]
                pip_value_per_std_lot = symbol_config["pip_value_per_std_lot"]
                
                # Calculate price difference in pips
                if trade.direction == "buy":
                    price_diff = current_price - trade.entry
                else:
                    price_diff = trade.entry - current_price
                
                pips_moved = price_diff / pip_size
                
                # Calculate PnL: pips × pip_value × lot_size
                pip_value = pip_value_per_std_lot * trade.lot_size
                trade_pnl = pips_moved * pip_value
                
                total_pnl += trade_pnl
            
            return total_pnl
            
        except Exception as e:
            self.logger.error(f"Error calculating combined PnL: {str(e)}")
            return 0.0
    
    def calculate_individual_pnl(self, trade: Trade, current_price: float) -> float:
        """
        Calculate individual order PnL (for profit booking)
        Returns PnL in dollars for a single order
        """
        try:
            if current_price == 0:
                current_price = self.mt5_client.get_current_price(trade.symbol)
                if current_price == 0:
                    return 0.0
            
            symbol_config = self.config["symbol_config"][trade.symbol]
            pip_size = symbol_config["pip_size"]
            pip_value_per_std_lot = symbol_config["pip_value_per_std_lot"]
            
            # Calculate price difference in pips
            if trade.direction == "buy":
                price_diff = current_price - trade.entry
            else:
                price_diff = trade.entry - current_price
            
            pips_moved = price_diff / pip_size
            
            # Calculate PnL: pips × pip_value × lot_size
            pip_value = pip_value_per_std_lot * trade.lot_size
            trade_pnl = pips_moved * pip_value
            
            return trade_pnl
            
        except Exception as e:
            self.logger.error(f"Error calculating individual PnL for trade {trade.trade_id}: {str(e)}")
            return 0.0
    
    def should_book_order(self, trade: Trade, current_price: float) -> bool:
        """
        Check if order should be booked (≥ $7 profit)
        Returns True if profit >= min_profit, False otherwise
        """
        pnl = self.calculate_individual_pnl(trade, current_price)
        should_book = pnl >= self.min_profit
        
        if should_book:
            self.logger.debug(
                f"[PROFIT_BOOKING] Order {trade.trade_id} should be booked: "
                f"PnL=${pnl:.2f} >= ${self.min_profit:.2f}"
            )
        
        return should_book
    
    def check_profit_targets(self, chain: ProfitBookingChain, 
                            open_trades: List[Trade]) -> List[Trade]:
        """
        NEW: Check individual orders for profit booking (≥ $7 per order)
        Returns list of orders that should be booked immediately
        Changed from combined PnL check to individual order check
        """
        orders_to_book = []
        
        if chain.status != "ACTIVE":
            return orders_to_book
        
        if chain.current_level >= chain.max_level:
            return orders_to_book
        
        # Get all trades for this chain at current level
        chain_trades = [
            t for t in open_trades
            if t.profit_chain_id == chain.chain_id 
            and t.profit_level == chain.current_level
            and t.status == "open"
        ]
        
        # If no trades found in open_trades, check if orders exist in MT5
        # This handles cases where orders were auto-closed or not tracked
        if not chain_trades:
            # Check if chain has active_orders (trade_ids) that might be in MT5
            if chain.active_orders:
                # Try to recover chain from MT5
                recovered = self.recover_chain_from_mt5(chain.chain_id)
                if recovered:
                    # After recovery, re-check for trades
                    chain_trades = [
                        t for t in open_trades
                        if t.profit_chain_id == chain.chain_id 
                        and t.profit_level == chain.current_level
                        and t.status == "open"
                    ]
            
            if not chain_trades:
                return orders_to_book
        
        # Get current price once
        current_price = self.mt5_client.get_current_price(chain.symbol)
        if current_price == 0:
            return orders_to_book
        
        # Check each order individually
        for trade in chain_trades:
            if self.should_book_order(trade, current_price):
                orders_to_book.append(trade)
                self.logger.info(
                    f"✅ Order {trade.trade_id} ready to book: "
                    f"Chain {chain.chain_id} Level {chain.current_level} - "
                    f"PnL=${self.calculate_individual_pnl(trade, current_price):.2f} >= ${self.min_profit:.2f}"
                )
        
        return orders_to_book
    
    async def book_individual_order(self, trade: Trade, chain: ProfitBookingChain,
                                   open_trades: List[Trade], trading_engine) -> bool:
        """
        Book a single order immediately when it reaches ≥ $7 profit
        Returns True if successfully booked, False otherwise
        """
        try:
            # Get current price
            current_price = self.mt5_client.get_current_price(trade.symbol)
            if current_price == 0:
                self.logger.error(f"Failed to get current price for {trade.symbol}")
                return False
            
            # Calculate profit for this order
            profit_booked = self.calculate_individual_pnl(trade, current_price)
            
            # Close the order
            await trading_engine.close_trade(trade, "PROFIT_BOOKING", current_price)
            
            # Update chain profit
            chain.total_profit += profit_booked
            chain.updated_at = datetime.now().isoformat()
            self.db.save_profit_chain(chain)
            
            # Save profit booking event
            self.db.save_profit_booking_event(
                chain.chain_id,
                chain.current_level,
                profit_booked,
                1,  # 1 order closed
                0   # 0 orders placed (will be placed when level progresses)
            )
            
            self.logger.info(
                f"✅ Individual order booked: Trade {trade.trade_id} "
                f"Chain {chain.chain_id} Level {chain.current_level} "
                f"Profit: ${profit_booked:.2f}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error booking individual order {trade.trade_id}: {str(e)}")
            return False
    
    async def check_and_progress_chain(self, chain: ProfitBookingChain,
                                      open_trades: List[Trade], trading_engine) -> bool:
        """
        Check if all orders in current level are closed, then progress to next level
        Returns True if progressed, False otherwise
        """
        try:
            if chain.status != "ACTIVE":
                return False
            
            if chain.current_level >= chain.max_level:
                # Max level reached - complete chain
                chain.status = "COMPLETED"
                chain.updated_at = datetime.now().isoformat()
                self.db.save_profit_chain(chain)
                self.logger.info(f"SUCCESS: Chain {chain.chain_id} completed - max level reached")
                return True
            
            # Check if all orders in current level are closed
            current_level_trades = [
                t for t in open_trades
                if t.profit_chain_id == chain.chain_id 
                and t.profit_level == chain.current_level
                and t.status == "open"
            ]
            
            # If there are still open orders, don't progress yet
            if current_level_trades:
                self.logger.debug(
                    f"Chain {chain.chain_id} Level {chain.current_level}: "
                    f"{len(current_level_trades)} orders still open, waiting for all to close"
                )
                return False
            
            # All orders closed - progress to next level
            
            # --- STRICT SUCCESS CHECK (Enhanced with Recovery Consideration) ---
            has_loss = chain.metadata.get(f"loss_level_{chain.current_level}", False)
            was_recovered = chain.metadata.get(f"loss_level_{chain.current_level}_recovered", False)
            profit_config = self.config.get("profit_booking_config", {})
            allow_partial = profit_config.get("allow_partial_progression", False)
            
            if has_loss and not allow_partial:
                if was_recovered:
                    # Loss happened but was RECOVERED successfully - allow progression
                    self.logger.info(
                        f"✅ Level {chain.current_level} had loss but was RECOVERED - "
                        f"Continuing to next level"
                    )
                    # Chain progresses normally (no stop)
                else:
                    # Loss not recovered - stop chain (strict mode)
                    self.logger.warning(
                        f"⛔ STRICT MODE: Chain {chain.chain_id} stopped due to "
                        f"unrecovered loss in Level {chain.current_level}"
                    )
                    chain.status = "STOPPED"
                    chain.metadata["stop_reason"] = "Strict Mode: Level Loss (Not Recovered)"
                    chain.updated_at = datetime.now().isoformat()
                    self.db.save_profit_chain(chain)
                    
                    trading_engine.telegram_bot.send_message(
                        f"⛔ **CHAIN STOPPED (STRICT)**\n"
                        f"Chain: {chain.chain_id}\n"
                        f"Level: {chain.current_level}\n"
                        f"Reason: Loss detected in strict mode (not recovered)"
                    )
                    return False
            # -----------------------------

            self.logger.info(
                f"✅ All orders closed in Level {chain.current_level}, "
                f"progressing to Level {chain.current_level + 1}"
            )
            
            # Progress to next level
            next_level = chain.current_level + 1
            
            # CHECK: Is this level enabled?
            enabled_levels = self.profit_config.get("enabled_levels", {})
            if not enabled_levels.get(str(next_level), True):
                self.logger.info(
                    f"⏹ Level {next_level} is DISABLED - stopping chain {chain.chain_id}"
                )
                chain.status = "STOPPED"
                chain.metadata["stop_reason"] = f"Level {next_level} disabled by user"
                chain.updated_at = datetime.now().isoformat()
                self.db.save_profit_chain(chain)
                
                trading_engine.telegram_bot.send_message(
                    f"⏹ **CHAIN STOPPED**\n"
                    f"Chain: {chain.chain_id}\n"
                    f"Reason: Level {next_level} is disabled\n"
                    f"Total Profit: ${chain.total_profit:.2f}"
                )
                return False
            
            next_order_count = self.get_order_multiplier(next_level)
            
            # Get strategy from chain metadata
            strategy = chain.metadata.get("strategy", "combinedlogic-1")

            # Place new orders for next level
            account_balance = self.mt5_client.get_account_balance()
            lot_size = self.risk_manager.get_lot_size_for_logic(account_balance, logic=strategy)
            
            # Get current price
            current_price = self.mt5_client.get_current_price(chain.symbol)
            if current_price == 0:
                self.logger.error(f"Failed to get current price for {chain.symbol}")
                return False
            
            # Use logic-based SL for profit booking orders
            sl_price, sl_distance = self.profit_sl_calculator.calculate_sl_price(
                current_price, chain.direction, chain.symbol, lot_size, strategy
            )
            
            # Calculate TP (using RR ratio)
            # If SL is disabled (None), use a default distance for TP calculation
            if sl_price is None:
                # Use a default SL distance for TP calculation when SL is disabled
                default_sl_distance = current_price * 0.01  # 1% default
                if chain.direction == "buy":
                    default_sl_price = current_price - default_sl_distance
                else:
                    default_sl_price = current_price + default_sl_distance
                tp_price = self.pip_calculator.calculate_tp_price(
                    current_price, default_sl_price, chain.direction, self.config.get("rr_ratio", 1.0)
                )
            else:
                tp_price = self.pip_calculator.calculate_tp_price(
                    current_price, sl_price, chain.direction, self.config.get("rr_ratio", 1.0)
                )
            
            # Place multiple orders for next level
            new_trade_ids = []
            orders_placed = 0
            
            for i in range(next_order_count):
                # Create trade object
                new_trade = Trade(
                    symbol=chain.symbol,
                    entry=current_price,
                    sl=sl_price,
                    tp=tp_price,
                    lot_size=lot_size,
                    direction=chain.direction,
                    strategy=chain.metadata.get("strategy", "combinedlogic-1"),
                    open_time=datetime.now().isoformat(),
                    original_entry=chain.metadata.get("original_entry", current_price),
                    original_sl_distance=sl_distance if sl_distance is not None else 0.0,
                    order_type="PROFIT_TRAIL",
                    profit_chain_id=chain.chain_id,
                    profit_level=next_level
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
                        comment=f"{chain.metadata.get('strategy', 'combinedlogic-1')}_PROFIT_L{next_level}"
                    )
                    if trade_id:
                        new_trade.trade_id = trade_id
                        new_trade_ids.append(trade_id)
                else:
                    # Simulation mode
                    import random
                    trade_id = random.randint(100000, 999999)
                    new_trade.trade_id = trade_id
                    new_trade_ids.append(trade_id)
                
                # Add to open trades
                trading_engine.open_trades.append(new_trade)
                trading_engine.risk_manager.add_open_trade(new_trade)
                
                # Save to database
                if new_trade.trade_id:
                    self.db.save_profit_booking_order(
                        str(new_trade.trade_id),
                        chain.chain_id,
                        next_level,
                        self.min_profit,  # $7 minimum
                        0,  # No SL reduction for profit booking (uses fixed $10 SL)
                        "OPEN"
                    )
                
                orders_placed += 1
            
            # Update chain
            chain.current_level = next_level
            chain.active_orders = new_trade_ids
            chain.updated_at = datetime.now().isoformat()
            self.db.save_profit_chain(chain)
            
            # Send Telegram notification
            trading_engine.telegram_bot.send_message(
                f"🔁 PROFIT BOOKING LEVEL UP!\n"
                f"Chain: {chain.chain_id}\n"
                f"Level: {chain.current_level - 1} → {chain.current_level}\n"
                f"Orders Placed: {orders_placed}\n"
                f"Next Target: ${self.min_profit:.2f} per order\n"
                f"SL: $10 fixed per order"
            )
            
            self.logger.info(
                f"✅ Chain progressed: {chain.chain_id} "
                f"Level {chain.current_level - 1} → {chain.current_level}, "
                f"Orders placed: {orders_placed}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking and progressing chain {chain.chain_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def execute_profit_booking(self, chain: ProfitBookingChain, 
                                    open_trades: List[Trade],
                                    trading_engine) -> bool:
        """
        Execute profit booking: close current level orders and place next level orders
        Returns True if successful, False otherwise
        """
        try:
            if chain.status != "ACTIVE":
                return False
            
            if chain.current_level >= chain.max_level:
                # Max level reached - complete chain
                chain.status = "COMPLETED"
                chain.updated_at = datetime.now().isoformat()
                self.db.save_profit_chain(chain)
                self.logger.info(f"SUCCESS: Chain {chain.chain_id} completed - max level reached")
                return True
            
            # Get all trades for current level
            current_level_trades = [
                t for t in open_trades
                if t.profit_chain_id == chain.chain_id 
                and t.profit_level == chain.current_level
                and t.status == "open"
            ]
            
            if not current_level_trades:
                self.logger.warning(f"No open trades found for chain {chain.chain_id} level {chain.current_level}")
                return False
            
            # Calculate profit booked (combined PnL)
            profit_booked = self.calculate_combined_pnl(chain, open_trades)
            
            # Close all orders in current level
            orders_closed = 0
            for trade in current_level_trades:
                current_price = self.mt5_client.get_current_price(trade.symbol)
                if current_price > 0:
                    await trading_engine.close_trade(trade, "PROFIT_BOOKING", current_price)
                    orders_closed += 1
            
            # Update chain profit
            chain.total_profit += profit_booked
            
            # Progress to next level
            next_level = chain.current_level + 1
            next_order_count = self.get_order_multiplier(next_level)
            next_profit_target = self.get_profit_target(next_level)
            
            # Get strategy from chain metadata
            strategy = chain.metadata.get("strategy", "combinedlogic-1")

            # Place new orders for next level
            orders_placed = 0
            account_balance = self.mt5_client.get_account_balance()
            lot_size = self.risk_manager.get_lot_size_for_logic(account_balance, logic=strategy)
            
            # Get current price
            current_price = self.mt5_client.get_current_price(chain.symbol)
            if current_price == 0:
                self.logger.error(f"Failed to get current price for {chain.symbol}")
                return False
            
            # Use logic-based SL for profit booking orders (not TP Trail SL system)
            sl_price, sl_distance = self.profit_sl_calculator.calculate_sl_price(
                current_price, chain.direction, chain.symbol, lot_size, strategy
            )
            
            # Calculate TP (using RR ratio)
            # If SL is disabled (None), use a default distance for TP calculation
            if sl_price is None:
                # Use a default SL distance for TP calculation when SL is disabled
                default_sl_distance = current_price * 0.01  # 1% default
                if chain.direction == "buy":
                    default_sl_price = current_price - default_sl_distance
                else:
                    default_sl_price = current_price + default_sl_distance
                tp_price = self.pip_calculator.calculate_tp_price(
                    current_price, default_sl_price, chain.direction, self.config.get("rr_ratio", 1.0)
                )
            else:
                tp_price = self.pip_calculator.calculate_tp_price(
                    current_price, sl_price, chain.direction, self.config.get("rr_ratio", 1.0)
                )
            
            # Place multiple orders for next level
            new_trade_ids = []
            for i in range(next_order_count):
                # Create trade object
                new_trade = Trade(
                    symbol=chain.symbol,
                    entry=current_price,
                    sl=sl_price,
                    tp=tp_price,
                    lot_size=lot_size,
                    direction=chain.direction,
                    strategy=chain.metadata.get("strategy", "combinedlogic-1"),
                    open_time=datetime.now().isoformat(),
                    original_entry=chain.metadata.get("original_entry", current_price),
                    original_sl_distance=sl_distance if sl_distance is not None else 0.0,
                    order_type="PROFIT_TRAIL",
                    profit_chain_id=chain.chain_id,
                    profit_level=next_level
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
                        comment=f"{chain.metadata.get('strategy', 'combinedlogic-1')}_PROFIT_L{next_level}"
                    )
                    if trade_id:
                        new_trade.trade_id = trade_id
                        new_trade_ids.append(trade_id)
                else:
                    # Simulation mode
                    import random
                    trade_id = random.randint(100000, 999999)
                    new_trade.trade_id = trade_id
                    new_trade_ids.append(trade_id)
                
                # Add to open trades
                trading_engine.open_trades.append(new_trade)
                trading_engine.risk_manager.add_open_trade(new_trade)
                
                # Save to database
                if new_trade.trade_id:
                    self.db.save_profit_booking_order(
                        str(new_trade.trade_id),
                        chain.chain_id,
                        next_level,
                        self.min_profit,  # $7 minimum
                        0,  # No SL reduction (uses fixed $10 SL)
                        "OPEN"
                    )
                
                orders_placed += 1
            
            # Update chain
            chain.current_level = next_level
            chain.active_orders = new_trade_ids
            chain.updated_at = datetime.now().isoformat()
            self.db.save_profit_chain(chain)
            
            # Save profit booking event
            self.db.save_profit_booking_event(
                chain.chain_id,
                chain.current_level - 1,  # Previous level
                profit_booked,
                orders_closed,
                orders_placed
            )
            
            # Send Telegram notification
            trading_engine.telegram_bot.send_message(
                f"🔁 PROFIT BOOKING LEVEL UP!\n"
                f"Chain: {chain.chain_id}\n"
                f"Level: {chain.current_level - 1} → {chain.current_level}\n"
                f"Profit Booked: ${profit_booked:.2f}\n"
                f"Orders Closed: {orders_closed}\n"
                f"Orders Placed: {orders_placed}\n"
                f"Next Target: ${self.min_profit:.2f} per order\n"
                f"SL: $10 fixed per order"
            )
            
            self.logger.info(
                f"✅ Profit booking executed: Chain {chain.chain_id} "
                f"Level {chain.current_level - 1} → {chain.current_level}, "
                f"Profit: ${profit_booked:.2f}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing profit booking: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_chain(self, chain_id: str, reason: str = "Manual stop"):
        """Stop a profit booking chain"""
        if chain_id in self.active_chains:
            chain = self.active_chains[chain_id]
            chain.status = "STOPPED"
            chain.updated_at = datetime.now().isoformat()
            self.db.save_profit_chain(chain)
            self.logger.info(f"STOPPED: Chain {chain_id} stopped: {reason}")
    
    def stop_all_chains(self, reason: str = "Manual stop all"):
        """Stop all active profit booking chains"""
        for chain_id in list(self.active_chains.keys()):
            self.stop_chain(chain_id, reason)
    
    def recover_chains_from_database(self, open_trades: List[Trade]):
        """
        Recover active profit booking chains from database on bot restart
        """
        try:
            active_chains_data = self.db.get_active_profit_chains()
            
            for chain_data in active_chains_data:
                try:
                    chain = ProfitBookingChain(
                        chain_id=chain_data["chain_id"],
                        symbol=chain_data["symbol"],
                        direction=chain_data["direction"],
                        base_lot=chain_data["base_lot"],
                        current_level=chain_data["current_level"],
                        max_level=self.max_level,
                        total_profit=chain_data.get("total_profit", 0.0),
                        active_orders=[],  # Will be populated from open_trades
                        status=chain_data.get("status", "ACTIVE"),
                        created_at=chain_data.get("created_at", datetime.now().isoformat()),
                        updated_at=chain_data.get("updated_at", datetime.now().isoformat()),
                        profit_targets=[self.min_profit] * (self.max_level + 1),  # All levels use $7 minimum
                        multipliers=self.multipliers.copy(),
                        sl_reductions=[0] * (self.max_level + 1),  # No SL reduction (uses fixed $10 SL)
                        metadata={}
                    )
                    
                    # Find active orders for this chain
                    chain_orders = [
                        t.trade_id for t in open_trades
                        if t.profit_chain_id == chain.chain_id
                        and t.status == "open"
                    ]
                    chain.active_orders = chain_orders
                    
                    self.active_chains[chain.chain_id] = chain
                    self.logger.info(f"SUCCESS: Recovered chain: {chain.chain_id} with {len(chain_orders)} orders")
                    
                except Exception as e:
                    self.logger.error(f"Error recovering chain {chain_data.get('chain_id', 'unknown')}: {str(e)}")
            
            self.logger.info(f"SUCCESS: Recovered {len(self.active_chains)} profit booking chains from database")
            
        except Exception as e:
            self.logger.error(f"Error recovering chains from database: {str(e)}")
    
    def get_chain(self, chain_id: str) -> Optional[ProfitBookingChain]:
        """Get profit booking chain by ID"""
        return self.active_chains.get(chain_id)
    
    def get_all_chains(self) -> Dict[str, ProfitBookingChain]:
        """Get all active profit booking chains"""
        return self.active_chains.copy()
    
    def recover_chain_from_mt5(self, chain_id: str) -> bool:
        """
        Attempt to recover chain state from MT5 positions
        Returns True if recovered, False otherwise
        """
        try:
            chain = self.get_chain(chain_id)
            if not chain:
                self.logger.warning(f"Chain {chain_id} not found for recovery")
                return False
            
            # Get all positions from MT5 for this symbol
            positions = self.mt5_client.get_positions(symbol=chain.symbol)
            
            chain_orders = []
            for position in positions:
                # Check if position comment contains chain_id
                if position.get('comment') and chain_id in position.get('comment', ''):
                    # This position belongs to our chain
                    chain_orders.append({
                        'ticket': position['ticket'],
                        'volume': position['volume'],
                        'price_open': position['price_open'],
                        'sl_price': position['sl'],
                        'tp_price': position['tp'],
                        'profit': position['profit'],
                        'comment': position['comment']
                    })
            
            if chain_orders:
                # Update chain with found orders
                # Note: active_orders in chain stores trade_ids, not position dicts
                # We'll update the chain status to indicate recovery
                chain.status = 'ACTIVE'
                chain.updated_at = datetime.now().isoformat()
                self.db.save_profit_chain(chain)
                self.logger.info(
                    f"Recovered chain {chain_id} with {len(chain_orders)} orders from MT5"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Chain recovery failed for {chain_id}: {str(e)}")
            return False
    
    def validate_chain_state(self, chain: ProfitBookingChain, 
                            open_trades: List[Trade]) -> bool:
        """
        Validate chain state integrity
        Returns True if valid, False otherwise
        Implements error deduplication to prevent log spam
        """
        try:
            # Check if chain exists
            if chain.chain_id not in self.active_chains:
                return False
            
            # Skip validation for stale chains
            if chain.chain_id in self.stale_chains:
                return False
            
            # Track missing orders for this chain
            missing_orders = []
            valid_orders = []
            
            # Check if all active orders still exist
            for order_id in chain.active_orders:
                order_exists = any(
                    t.trade_id == order_id and t.status == "open"
                    for t in open_trades
                )
                
                if not order_exists:
                    missing_orders.append(order_id)
                    
                    # Track check count for this order
                    order_key = f"{chain.chain_id}:{order_id}"
                    check_count = self.checked_missing_orders.get(order_key, 0)
                    
                    # Stop checking after 3 attempts
                    if check_count >= 3:
                        continue  # Skip logging, already checked 3 times
                    
                    # Increment check count
                    self.checked_missing_orders[order_key] = check_count + 1
                    
                    # Log error only once per 5 minutes per order
                    current_time = time.time()
                    last_log = self.last_error_log_time.get(order_key, 0)
                    
                    if current_time - last_log > 300:  # 5 minutes
                        self.logger.warning(
                            f"Chain {chain.chain_id} has missing order: {order_id} "
                            f"(check {check_count + 1}/3)"
                        )
                        self.last_error_log_time[order_key] = current_time
                else:
                    valid_orders.append(order_id)
            
            # If all orders are missing and checked 3+ times, mark chain as stale
            if len(missing_orders) == len(chain.active_orders) and len(valid_orders) == 0:
                all_checked = all(
                    self.checked_missing_orders.get(f"{chain.chain_id}:{order_id}", 0) >= 3
                    for order_id in missing_orders
                )
                
                if all_checked and chain.chain_id not in self.stale_chains:
                    self.logger.warning(
                        f"Marking chain {chain.chain_id} as STALE - all orders missing after 3 checks"
                    )
                    self.stale_chains.add(chain.chain_id)
                    # Optionally stop the chain
                    self.stop_chain(chain.chain_id, "All orders missing - marked stale")
                    return False
            
            # Return True if at least some orders exist
            return len(valid_orders) > 0
            
        except Exception as e:
            self.logger.error(f"Error validating chain state: {str(e)}")
            return False
    
    def handle_orphaned_orders(self, open_trades: List[Trade]):
        """
        Handle orders that have profit_chain_id but chain doesn't exist
        """
        try:
            for trade in open_trades:
                if trade.profit_chain_id and trade.profit_chain_id not in self.active_chains:
                    # Orphaned order - clear profit_chain_id
                    trade.profit_chain_id = None
                    trade.profit_level = 0
                    self.logger.warning(
                        f"Cleared orphaned order: {trade.trade_id} "
                        f"from missing chain: {trade.profit_chain_id}"
                    )
        except Exception as e:
            self.logger.error(f"Error handling orphaned orders: {str(e)}")
    
    def cleanup_stale_chains(self):
        """
        Clean up stale chains that have all missing orders
        Specifically removes the problematic chain PROFIT_XAUUSD_aacf09c3
        """
        try:
            chains_to_remove = []
            
            # Check for the specific problematic chain
            if "PROFIT_XAUUSD_aacf09c3" in self.active_chains:
                chains_to_remove.append("PROFIT_XAUUSD_aacf09c3")
                self.logger.info("Removing stale chain: PROFIT_XAUUSD_aacf09c3")
            
            # Also check other stale chains
            for chain_id in self.stale_chains:
                if chain_id in self.active_chains and chain_id not in chains_to_remove:
                    chains_to_remove.append(chain_id)
            
            # Remove stale chains
            for chain_id in chains_to_remove:
                if chain_id in self.active_chains:
                    chain = self.active_chains[chain_id]
                    chain.status = "STALE"
                    chain.updated_at = datetime.now().isoformat()
                    self.db.save_profit_chain(chain)
                    del self.active_chains[chain_id]
                    self.logger.info(f"Removed stale chain: {chain_id}")
            
            # Clean up tracking dictionaries for removed chains
            keys_to_remove = [
                key for key in self.checked_missing_orders.keys()
                if any(key.startswith(f"{chain_id}:") for chain_id in chains_to_remove)
            ]
            for key in keys_to_remove:
                del self.checked_missing_orders[key]
                if key in self.last_error_log_time:
                    del self.last_error_log_time[key]
            
            # Remove from stale_chains set
            self.stale_chains -= set(chains_to_remove)
            
            if chains_to_remove:
                self.logger.info(f"Cleaned up {len(chains_to_remove)} stale chain(s)")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up stale chains: {str(e)}")

    async def handle_trade_close(self, trade: Trade, open_trades: List[Trade], trading_engine):
        """
        Public method called by TradingEngine when a profit booking trade closes.
        Tracks losses for strict mode and triggers level progression check.
        """
        try:
            chain_id = trade.profit_chain_id
            if not chain_id: return
            
            chain = self.get_chain(chain_id)
            if not chain: return
            
            # 1. Track Outcome (for Strict Mode)
            if hasattr(trade, 'pnl') and trade.pnl < 0:
                # Loss detected!
                # Check if it was a SL Hunt Recovery trade?
                if getattr(trade, 'order_type', '') == "PROFIT_RECOVERY":
                    # Recovery failed -> Loss confirmed
                    self.logger.info(f"Loss confirmed on recovery trade for chain {chain_id}")
                    chain.metadata[f"loss_level_{chain.current_level}"] = True
                else:
                    # Normal trade loss -> Recovery might run?
                    # If recovery is enabled, we wait for recovery outcome before marking loss?
                    # BUT TradingEngine closes normal trade as "SL_HIT".
                    # And then starts "PROFIT_RECOVERY".
                    # So the level is NOT done yet.
                    # check_and_progress_chain waits for ALL orders to close.
                    # The Recovery Order is NEW.
                    # It should be added to the level tracking if not already?
                    # AutonomousManager places it.
                    # Does it set profit_chain_id? Yes.
                    # So it belongs to the level.
                    # So check_and_progress_chain will WAIT for it.
                    # Great!
                    
                    # But we shouldn't mark "loss_level" yet if recovery is pending.
                    # How do we know?
                    # AutonomousManager starts recovery monitoring.
                    pass
                
                # If valid loss (no recovery or recovery failed), mark it.
                # Simplification: If PnL < 0, check if recovery is possible.
                # If recovery enabled, don't mark loss yet.
                # If recovery disabled, mark loss.
                
                pass # Logic handled by waiting for recovery trades
                
                # However, if RECOVERY FAILS (Closed with Loss), we MUST mark it.
                if getattr(trade, 'order_type', '') == "PROFIT_RECOVERY" and trade.pnl < 0:
                     chain.metadata[f"loss_level_{chain.current_level}"] = True
                
                # If Normal Order B fails and Recovery Disabled:
                config = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("profit_sl_hunt", {})
                if not config.get("enabled", False) and trade.pnl < 0:
                     chain.metadata[f"loss_level_{chain.current_level}"] = True

            self.db.save_profit_chain(chain)
            
            # 2. Trigger Progression Check
            # Use asyncio.create_task to run in background
            import asyncio
            asyncio.create_task(self.check_and_progress_chain(chain, open_trades, trading_engine))
            
        except Exception as e:
            self.logger.error(f"Error handling trade close for chain {trade.profit_chain_id}: {str(e)}")


