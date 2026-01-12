from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceAPI:
    """
    Exposes core bot functionality to plugins in a safe, controlled manner.
    Acts as a facade over TradingEngine and Managers.
    """
    
    def __init__(self, trading_engine):
        self._engine = trading_engine
        self._config = trading_engine.config
        self._mt5 = trading_engine.mt5_client
        self._risk = trading_engine.risk_manager
        self._telegram = trading_engine.telegram_bot
        self._logger = logger

    # --- Market Data ---

    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        tick = self._mt5.get_symbol_tick(symbol)
        if tick:
            return tick['bid'] # Return bid by default or maybe close?
        return 0.0

    def get_symbol_info(self, symbol: str) -> Dict:
        """Get symbol validation info"""
        return self._mt5.get_symbol_info(symbol)

    # --- Account Info ---

    def get_balance(self) -> float:
        """Get current account balance"""
        return self._mt5.get_account_balance()
    
    def get_equity(self) -> float:
        """Get current account equity"""
        return self._mt5.get_account_equity()

    # --- Order Management ---

    def place_order(self, symbol: str, direction: str, lot_size: float, 
                   sl_price: float = 0.0, tp_price: float = 0.0, 
                   comment: str = "") -> Optional[int]:
        """
        Place a new order.
        direction: "BUY" or "SELL"
        """
        if not self._engine.trading_enabled:
            self._logger.warning("Trading is paused. Order rejected.")
            return None

        return self._mt5.place_order(
            symbol=symbol,
            order_type=direction.upper(),
            lot_size=lot_size,
            price=0.0, # Market order usually 0.0 or current Ask/Bid
            sl=sl_price,
            tp=tp_price,
            comment=comment
        )

    def close_trade(self, trade_id: int) -> bool:
        """Close an existing trade"""
        return self._mt5.close_position(trade_id)

    def modify_order(self, trade_id: int, sl: float = 0.0, tp: float = 0.0) -> bool:
        """Modify SL/TP of a trade"""
        return self._mt5.modify_position(trade_id, sl, tp)
    
    def get_open_trades(self) -> List[Any]:
        """Get list of ALL open trades"""
        return self._engine.get_open_trades()

    # --- Risk Management ---

    def calculate_lot_size(self, symbol: str, stop_loss_pips: float = 0.0) -> float:
        """Calculate recommended lot size based on risk settings"""
        balance = self.get_balance()
        # If the risk manager has a method for this, use it.
        # Check risk_manager.py: get_fixed_lot_size or calculate_lot_size
        if hasattr(self._risk, 'calculate_lot_size') and stop_loss_pips > 0:
             return self._risk.calculate_lot_size(balance, stop_loss_pips)
        return self._risk.get_fixed_lot_size(balance)

    # --- Communication ---

    def send_notification(self, message: str):
        """Send message via Telegram"""
        self._telegram.send_message(message)

    def log(self, message: str, level: str = "info"):
        """Log message"""
        if level.lower() == "error":
            self._logger.error(message)
        elif level.lower() == "warning":
            self._logger.warning(message)
        elif level.lower() == "debug":
            self._logger.debug(message)
        else:
            self._logger.info(message)
    
    # --- Configuration ---
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)
