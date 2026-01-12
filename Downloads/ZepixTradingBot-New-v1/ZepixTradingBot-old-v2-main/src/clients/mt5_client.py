try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("WARNING: MetaTrader5 not available (Windows only). Running in simulation mode.")

import time
import logging
from typing import Dict, Any, Optional, List
from src.config import Config
from src.models import Trade
from src.utils.optimized_logger import logger as opt_logger

logger = logging.getLogger(__name__)

class MT5Client:
    def __init__(self, config: Config):
        self.config = config
        self.initialized = False
        # Load symbol mapping from config for broker compatibility
        self.symbol_mapping = config.get("symbol_mapping", {})
        # Cache for symbol mappings to avoid repeated lookups and debug logs
        self.symbol_cache = {}
        
        # Connection health monitoring
        self.connection_errors = 0
        self.max_connection_errors = 5
        self.telegram_bot = None  # Will be set externally after initialization

    def _map_symbol(self, symbol: str) -> str:
        """
        Map TradingView symbol to broker's MT5 symbol
        Example: XAUUSD (TradingView) -> GOLD (XM Broker)
        Uses caching to prevent repeated lookups and debug logs
        """
        # Check cache first
        if symbol in self.symbol_cache:
            return self.symbol_cache[symbol]
        
        # Perform mapping (existing logic)
        mapped = self.symbol_mapping.get(symbol, symbol)
        
        # Cache the result
        self.symbol_cache[symbol] = mapped
        
        # Log only if mapping changed (existing debug log)
        if mapped != symbol:
            # Use logger.debug instead of print to avoid spam
            logger.debug(f"Symbol mapping: {symbol} -> {mapped}")
        
        return mapped

    def initialize(self) -> bool:
        """Initialize MT5 connection with retry logic"""
        if not MT5_AVAILABLE:
            print("WARNING: Running in simulation mode (MT5 not available on this platform)")
            self.initialized = True
            return True
            
        for i in range(self.config["mt5_retries"]):
            try:
                if not mt5.initialize():
                    print(f"MT5 initialization failed, retry {i+1}/{self.config['mt5_retries']}")
                    time.sleep(self.config["mt5_wait"])
                    continue
                
                login = self.config.get("mt5_login", 0)
                password = self.config.get("mt5_password", "")
                server = self.config.get("mt5_server", "")
                
                if not login or not password or not server:
                    print(f"ERROR: MT5 credentials missing - Login: {login}, Server: {server}")
                    print("WARNING: Please check .env file for MT5_LOGIN, MT5_PASSWORD, MT5_SERVER")
                    time.sleep(self.config["mt5_wait"])
                    continue
                
                authorized = mt5.login(login, password, server)
                
                if authorized:
                    self.initialized = True
                    print("SUCCESS: MT5 connection established")
                    account_info = mt5.account_info()
                    if account_info:
                        print(f"Account Balance: ${account_info.balance:.2f}")
                        print(f"Account: {account_info.login} | Server: {account_info.server}")
                    return True
                else:
                    error = mt5.last_error()
                    print(f"MT5 login failed, retry {i+1}/{self.config['mt5_retries']}")
                    print(f"ERROR: MT5 login error: {error}")
                    time.sleep(self.config["mt5_wait"])
                    
            except Exception as e:
                print(f"MT5 connection error: {str(e)}")
                time.sleep(self.config["mt5_wait"])
        
        print("ERROR: Failed to connect to MT5 after retries")
        print("WARNING: Check the following:")
        print("  1. MT5 terminal is installed and running")
        print("  2. MT5 terminal is logged in with correct account")
        print("  3. .env file contains correct MT5_LOGIN, MT5_PASSWORD, MT5_SERVER")
        print("  4. MT5 server name matches exactly (case-sensitive)")
        
        # Check if simulation mode is enabled/should be enabled
        if self.config.get("simulate_orders", False):
            print("WARNING: MT5 connection failed but simulation mode enabled - continuing")
            self.initialized = True  # Safe to set for simulation
            return True
        
        return False

    async def check_connection_health(self) -> bool:
        """
        Check MT5 connection health and attempt reconnect if needed
        Returns True if connection is healthy, False otherwise
        """
        # Skip health check in simulation mode
        if not MT5_AVAILABLE or self.config.get("simulate_orders", False):
            return True
        
        try:
            # Check if MT5 is still initialized
            if not mt5.initialize():
                self.connection_errors += 1
                opt_logger.error(f"MT5 connection lost - attempt #{self.connection_errors}")
                
                # Attempt reconnection
                success = self.initialize()
                if success:
                    opt_logger.info("✅ MT5 reconnection successful")
                    self.connection_errors = 0
                    return True
                else:
                    if self.connection_errors >= self.max_connection_errors:
                        opt_logger.critical("🚨 MT5 connection permanently lost")
                        if self.telegram_bot:
                            try:
                                self.telegram_bot.send_message("🚨 CRITICAL: MT5 connection lost - Trading stopped!")
                            except Exception as e:
                                opt_logger.error(f"Failed to send Telegram alert: {e}")
                    return False
            
            # Connection is healthy
            return True
            
        except Exception as e:
            opt_logger.error(f"MT5 health check error: {str(e)}", exc_info=True)
            return False

    def validate_order_parameters(self, symbol: str, order_type: str, 
                                  price: float, sl_price: float, 
                                  tp_price: Optional[float] = None) -> tuple:
        """
        Validate order parameters against MT5 broker constraints
        Returns: (is_valid: bool, error_message: str)
        """
        # Debug logging at start
        logger.info(
            f"VALIDATION DEBUG: Symbol={symbol}, OrderType={order_type}, "
            f"Price={price}, SL={sl_price}, TP={tp_price}"
        )
        
        # Skip validation in simulation mode
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            logger.info("VALIDATION: Skipped (simulation mode)")
            return True, "Validation passed (simulation mode)"
        
        # Map symbol for broker compatibility
        mt5_symbol = self._map_symbol(symbol)
        if mt5_symbol != symbol:
            logger.info(f"VALIDATION: Symbol mapped {symbol} -> {mt5_symbol}")
        
        try:
            # Get symbol info from MT5
            symbol_info = mt5.symbol_info(mt5_symbol)
            if symbol_info is None:
                error_msg = f"Symbol {mt5_symbol} not found in MT5"
                logger.error(f"VALIDATION FAILED: {error_msg}")
                return False, error_msg
            
            logger.info(
                f"VALIDATION: Symbol info retrieved for {mt5_symbol} - "
                f"Visible={symbol_info.visible}, Digits={symbol_info.digits}"
            )
            
            # Get minimum stops level (minimum distance from price)
            stops_level = symbol_info.trade_stops_level
            point = symbol_info.point
            
            # Calculate minimum distance required
            if stops_level > 0:
                min_distance = stops_level * point
            else:
                # Default to 10 points if stops_level is 0
                min_distance = 10 * point
            
            logger.info(
                f"VALIDATION: StopsLevel={stops_level}, Point={point}, "
                f"MinDistance={min_distance:.5f}"
            )
            
            # Determine order direction
            if order_type == "buy" or order_type == mt5.ORDER_TYPE_BUY:
                # BUY order: SL should be below entry, TP above entry
                if sl_price >= price:
                    error_msg = f"BUY order SL {sl_price} must be below entry {price}"
                    logger.error(f"VALIDATION FAILED: {error_msg} (SL={sl_price}, Entry={price})")
                    return False, error_msg
                
                if tp_price is not None and tp_price <= price:
                    error_msg = f"BUY order TP {tp_price} must be above entry {price}"
                    logger.error(f"VALIDATION FAILED: {error_msg} (TP={tp_price}, Entry={price})")
                    return False, error_msg
                
                # Check minimum distance from current price
                sl_distance = abs(price - sl_price)
                logger.info(f"VALIDATION: BUY order SL distance={sl_distance:.5f}, MinRequired={min_distance:.5f}")
                if sl_distance < min_distance:
                    error_msg = f"SL distance {sl_distance:.5f} less than minimum {min_distance:.5f} points"
                    logger.error(f"VALIDATION FAILED: {error_msg}")
                    return False, error_msg
                
                if tp_price is not None:
                    tp_distance = abs(tp_price - price)
                    logger.info(f"VALIDATION: BUY order TP distance={tp_distance:.5f}, MinRequired={min_distance:.5f}")
                    if tp_distance < min_distance:
                        error_msg = f"TP distance {tp_distance:.5f} less than minimum {min_distance:.5f} points"
                        logger.error(f"VALIDATION FAILED: {error_msg}")
                        return False, error_msg
                    
            elif order_type == "sell" or order_type == mt5.ORDER_TYPE_SELL:
                # SELL order: SL should be above entry, TP below entry
                if sl_price <= price:
                    error_msg = f"SELL order SL {sl_price} must be above entry {price}"
                    logger.error(f"VALIDATION FAILED: {error_msg} (SL={sl_price}, Entry={price})")
                    return False, error_msg
                
                if tp_price is not None and tp_price >= price:
                    error_msg = f"SELL order TP {tp_price} must be below entry {price}"
                    logger.error(f"VALIDATION FAILED: {error_msg} (TP={tp_price}, Entry={price})")
                    return False, error_msg
                
                # Check minimum distance from current price
                sl_distance = abs(sl_price - price)
                logger.info(f"VALIDATION: SELL order SL distance={sl_distance:.5f}, MinRequired={min_distance:.5f}")
                if sl_distance < min_distance:
                    error_msg = f"SL distance {sl_distance:.5f} less than minimum {min_distance:.5f} points"
                    logger.error(f"VALIDATION FAILED: {error_msg}")
                    return False, error_msg
                
                if tp_price is not None:
                    tp_distance = abs(price - tp_price)
                    logger.info(f"VALIDATION: SELL order TP distance={tp_distance:.5f}, MinRequired={min_distance:.5f}")
                    if tp_distance < min_distance:
                        error_msg = f"TP distance {tp_distance:.5f} less than minimum {min_distance:.5f} points"
                        logger.error(f"VALIDATION FAILED: {error_msg}")
                        return False, error_msg
            
            logger.info(f"VALIDATION PASSED: All checks passed for {symbol} ({mt5_symbol})")
            return True, "Validation passed"
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(f"VALIDATION FAILED: {error_msg}")
            import traceback
            logger.error(f"VALIDATION EXCEPTION TRACEBACK: {traceback.format_exc()}")
            return False, error_msg

    def place_order(self, symbol: str, order_type: str, lot_size: float, 
                   price: float, sl: float, tp: float = None, 
                   comment: str = "") -> Optional[int]:
        """
        Place a new order with TP support and automatic symbol mapping
        This function translates TradingView symbols to broker-specific symbols
        """
        if not self.initialized:
            if not self.initialize():
                return None
        
        # Simulation mode
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            import random
            simulated_ticket = random.randint(100000, 999999)
            print(f"SIMULATED ORDER: {order_type.upper()} {lot_size} lots {symbol} @ {price}, SL={sl}, TP={tp} (Ticket #{simulated_ticket})")
            return simulated_ticket
        
        # Map symbol for broker compatibility - CRITICAL FOR XM BROKER
        mt5_symbol = self._map_symbol(symbol)
        
        try:
            # Get symbol info using the mapped broker symbol
            symbol_info = mt5.symbol_info(mt5_symbol)
            if symbol_info is None:
                print(f"ERROR: Symbol {mt5_symbol} not found in MT5")
                return None
                
            if not symbol_info.visible:
                print(f"Symbol {mt5_symbol} is not visible, attempting to enable")
                if not mt5.symbol_select(mt5_symbol, True):
                    print(f"ERROR: Failed to enable symbol {mt5_symbol}")
                    return None
            
            # Determine order type and get current price
            if order_type == "buy":
                order_type_mt5 = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(mt5_symbol).ask
            else:
                order_type_mt5 = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(mt5_symbol).bid
            
            # Round prices to symbol's digit precision
            digits = symbol_info.digits
            price = round(price, digits)
            sl = round(sl, digits)
            if tp:
                tp = round(tp, digits)
            
            # Validate order parameters after getting actual current price
            is_valid, error_msg = self.validate_order_parameters(symbol, order_type, price, sl, tp)
            if not is_valid:
                print(f"ERROR: Order validation failed: {error_msg}")
                print(f"Request details: Symbol={mt5_symbol}, Lot={lot_size}, Price={price}, SL={sl}, TP={tp}")
                return None
            
            # Prepare order request with mapped symbol
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": mt5_symbol,  # Use broker's symbol name
                "volume": lot_size,
                "type": order_type_mt5,
                "price": price,
                "sl": sl,
                "deviation": 20,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add TP if provided
            if tp:
                request["tp"] = tp
            
            # Send order to MT5
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"ERROR: Order failed: {result.comment} (Error code: {result.retcode})")
                print(f"Request details: Symbol={mt5_symbol}, Lot={lot_size}, Price={price}, SL={sl}, TP={tp}")
                return None
            
            print(f"SUCCESS: Order placed successfully: Ticket #{result.order}")
            return result.order
            
        except Exception as e:
            print(f"ERROR: Order placement error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def close_position(self, position_id: int, percentage: float = 100):
        """Close a position completely"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        # Simulation mode - always return success
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            print(f"SIMULATED CLOSE: Position #{position_id}")
            return True
        
        try:
            # Get position by ticket
            positions = mt5.positions_get(ticket=position_id)
            
            # Check if it's an API error vs position not found
            if positions is None:
                error = mt5.last_error()
                print(f"ERROR: MT5 API error when getting position {position_id}: {error}")
                return False  # API error - don't mark as closed
            
            if len(positions) == 0:
                print(f"SUCCESS: Position {position_id} already closed (not found in MT5)")
                return True  # Position genuinely doesn't exist - already closed
                
            position = positions[0]
            
            # Prepare close request
            symbol_info = mt5.symbol_info(position.symbol)
            
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": position_id,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": f"Close_{percentage}%",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"SUCCESS: Position {position_id} closed successfully")
                return True
            else:
                print(f"Failed to close position: {result.comment}")
                return False
                
        except Exception as e:
            print(f"Position close error: {str(e)}")
            return False

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol with automatic mapping support
        Handles both TradingView symbols and broker symbols
        Returns None if price cannot be fetched
        """
        if not self.initialized:
            if not self.initialize():
                return None
        
        # Simulation mode - return dummy prices
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            dummy_prices = {
                "XAUUSD": 2650.0, "GOLD": 2650.0,
                "EURUSD": 1.0850, "GBPUSD": 1.2650,
                "USDJPY": 149.50, "USDCAD": 1.3550
            }
            return dummy_prices.get(symbol, 1.0)
        
        # Map symbol to broker's format
        mt5_symbol = self._map_symbol(symbol)
        
        try:
            tick = mt5.symbol_info_tick(mt5_symbol)
            if tick:
                return (tick.ask + tick.bid) / 2
            return None
        except:
            return None

    def get_account_balance(self) -> float:
        """Get current account balance"""
        if not self.initialized:
            if not self.initialize():
                return 0.0
        
        # Simulation mode - return dummy balance
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            return 10000.0
        
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.balance
            return 0.0
        except:
            return 0.0

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all positions from MT5, optionally filtered by symbol
        Returns list of position dictionaries with ticket, volume, price_open, sl, tp, profit, comment
        """
        if not self.initialized:
            if not self.initialize():
                return []
        
        # Simulation mode - return empty list
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            return []
        
        try:
            # Map symbol if provided
            mt5_symbol = self._map_symbol(symbol) if symbol else None
            
            # Get positions from MT5
            if mt5_symbol:
                positions = mt5.positions_get(symbol=mt5_symbol)
            else:
                positions = mt5.positions_get()
            
            if positions is None:
                return []
            
            # Convert to list of dictionaries
            result = []
            for position in positions:
                result.append({
                    'ticket': position.ticket,
                    'volume': position.volume,
                    'price_open': position.price_open,
                    'sl': position.sl,
                    'tp': position.tp,
                    'profit': position.profit,
                    'comment': position.comment,
                    'symbol': position.symbol,
                    'type': position.type
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []

    def get_position(self, ticket: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific position by ticket number
        Returns position dict if found, None otherwise
        """
        if not self.initialized:
            if not self.initialize():
                return None
        
        # Simulation mode - return None
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            return None
        
        try:
            positions = mt5.positions_get(ticket=ticket)
            
            if positions is None or len(positions) == 0:
                return None
            
            position = positions[0]
            return {
                'ticket': position.ticket,
                'volume': position.volume,
                'price_open': position.price_open,
                'sl': position.sl,
                'tp': position.tp,
                'profit': position.profit,
                'comment': position.comment,
                'symbol': position.symbol,
                'type': position.type
            }
            
        except Exception as e:
            logger.error(f"Error getting position {ticket}: {str(e)}")
            return None

    def get_account_info_detailed(self) -> Dict[str, float]:
        """Get detailed account info including margins and equity"""
        if not self.initialized:
            if not self.initialize():
                return {}
        
        # Simulation mode - return dummy values
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            return {
                "balance": 10000.0,
                "equity": 10000.0,
                "free_margin": 9000.0,
                "margin": 1000.0,
                "margin_level": 1000.0  # percentage
            }
        
        try:
            account_info = mt5.account_info()
            if account_info:
                return {
                    "balance": account_info.balance,
                    "equity": account_info.equity,
                    "free_margin": account_info.margin_free,
                    "margin": account_info.margin,
                    "margin_level": account_info.margin_level  # percentage (free_margin/margin * 100)
                }
            return {}
        except Exception as e:
            print(f"ERROR: Unable to get account info: {str(e)}")
            return {}

    def get_free_margin(self) -> float:
        """Get current free margin available for trading"""
        info = self.get_account_info_detailed()
        return info.get("free_margin", 0.0)

    def get_margin_level(self) -> float:
        """
        Get margin level percentage
        Formula: (equity / margin) * 100
        > 100% = Safe zone
        < 100% = Margin call territory
        < 50% = Auto-liquidation likely
        """
        info = self.get_account_info_detailed()
        return info.get("margin_level", 0.0)

    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """
        Modify Stop Loss and Take Profit for an existing position
        """
        if not self.initialized:
            if not self.initialize():
                return False
        
        # Simulation mode
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            print(f"SIMULATED MODIFY: Ticket {ticket} -> SL={sl}, TP={tp}")
            return True
            
        try:
            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "symbol": self.get_position(ticket)['symbol'], # Helper get_position needed or use existing
                "sl": sl,
                "tp": tp,
                "magic": 234000
            }
            # Handle get_position usage explicitly if needed or rely on robust implementation below
            # Re-fetch symbol if needed
            pos_info = self.get_position(ticket)
            if not pos_info:
                print(f"ERROR: Cannot modify position {ticket} - not found")
                return False
            
            request["symbol"] = pos_info["symbol"]
            
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"SUCCESS: Position {ticket} modified. SL={sl}, TP={tp}")
                return True
            else:
                logger.error(f"Failed to modify position {ticket}: {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Modify position error: {str(e)}")
            return False

    def get_required_margin_for_order(self, symbol: str, lot_size: float) -> float:
        """
        Calculate required margin for a position
        Formula: pip_value × stop_loss_pips × lot_size / leverage
        """
        if not self.initialized:
            if not self.initialize():
                return 0.0
        
        # Simulation mode
        if not MT5_AVAILABLE or self.config.get("simulate_orders", True):
            # Dummy calculation
            return lot_size * 100 * 10  # Rough estimate
        
        try:
            # Map symbol if needed
            mt5_symbol = self._map_symbol(symbol)
            
            # Get symbol info to get pip value and leverage
            symbol_info = mt5.symbol_info(mt5_symbol)
            if not symbol_info:
                print(f"WARNING: Could not get symbol info for {mt5_symbol}")
                return 0.0
            
            # Get account leverage
            account_info = mt5.account_info()
            if not account_info:
                return 0.0
            
            leverage = account_info.leverage if hasattr(account_info, 'leverage') else 1
            
            # Approximate required margin per lot based on pip value
            # This is a simplified calculation - actual margin may vary
            tick = mt5.symbol_info_tick(mt5_symbol)
            if tick:
                pip_value = symbol_info.point * 10  # 1 pip in currency value per 1 lot
                required_margin = (pip_value * lot_size * 100) / leverage  # Rough estimate
                return required_margin
            
            return 0.0
            
        except Exception as e:
            print(f"ERROR: Could not calculate required margin: {str(e)}")
            return 0.0

    def is_margin_safe(self, min_margin_level: float = 100.0) -> bool:
        """
        Check if account has safe margin level
        min_margin_level: minimum safe margin level percentage (default 100%)
        Returns: True if safe, False if risky
        """
        margin_level = self.get_margin_level()
        free_margin = self.get_free_margin()
        
        is_safe = margin_level >= min_margin_level and free_margin > 0
        
        if not is_safe:
            print(f"WARNING: Margin not safe! Level: {margin_level:.2f}% (min: {min_margin_level:.2f}%), Free: ${free_margin:.2f}")
        
        return is_safe

    def shutdown(self):
        """Shutdown MT5 connection gracefully"""
        if self.initialized:
            mt5.shutdown()
            self.initialized = False
            print("MT5 connection closed")

    def get_closed_trade_profit(self, ticket_id: int) -> Optional[float]:
        """
        Fetch ACTUAL profit from MT5 history for a closed position.
        This is the REAL profit including commission, swap, and correct contract size.
        
        Args:
            ticket_id: MT5 position ticket ID
            
        Returns:
            Actual profit/loss in account currency (e.g., USD), or None if not found
        """
        if not self.initialized or not MT5_AVAILABLE:
            logger.warning(f"Cannot fetch profit for ticket {ticket_id}: MT5 not initialized")
            return None
        
        try:
            # Request trade history for this specific position
            # We need to look in deals (not positions, since it's closed)
            deals = mt5.history_deals_get(position=ticket_id)
            
            if not deals:
                logger.warning(f"No history found for ticket {ticket_id}")
                return None
            
            # Sum up all deal profits for this position
            # (Usually 2 deals: entry + exit, but could be partial closes)
            total_profit = sum(deal.profit for deal in deals)
            
            logger.debug(f"Fetched actual profit for ticket {ticket_id}: ${total_profit:.2f}")
            return total_profit
            
        except Exception as e:
            logger.error(f"Error fetching profit for ticket {ticket_id}: {e}")
            return None