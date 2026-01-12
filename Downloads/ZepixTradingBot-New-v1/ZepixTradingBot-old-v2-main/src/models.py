from typing import Dict, Any, Optional, List
from pydantic import BaseModel, validator
from datetime import datetime
import json

class Alert(BaseModel):
    type: str  # "bias", "trend", "entry", "reversal", or "exit"
    symbol: str
    signal: str  # "buy", "sell", "bull", "bear", "reversal_bull", "reversal_bear"
    tf: str  # "1h", "15m", "5m", "1d" - REQUIRED FIELD (no default)
    price: Optional[float] = None
    strategy: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['bias', 'trend', 'entry', 'reversal', 'exit']:
            raise ValueError('Type must be bias, trend, entry, reversal, or exit')
        return v
    
    @validator('tf')
    def validate_tf(cls, v):
        if v not in ['1h', '15m', '5m', '1d']:
            raise ValueError('Timeframe must be 1h, 15m, 5m, or 1d')
        return v

class Trade(BaseModel):
    symbol: str
    entry: float
    
    @property
    def entry_price(self):
        return self.entry

    @property
    def sl_price(self):
        return self.sl

    sl: float
    tp: float  # Single TP now (1:1 RR)
    lot_size: float
    direction: str  # "buy" or "sell"
    strategy: str  # "combinedlogic-1", "combinedlogic-2", "combinedlogic-3"
    status: str = "open"  # open, closed
    trade_id: Optional[int] = None
    open_time: str
    close_time: Optional[str] = None
    pnl: Optional[float] = None
    
    # Re-entry tracking
    chain_id: Optional[str] = None
    chain_level: int = 1
    original_entry: Optional[float] = None
    original_sl_distance: Optional[float] = None
    is_re_entry: bool = False
    parent_trade_id: Optional[int] = None
    
    # Dual order system tracking
    order_type: Optional[str] = None  # "TP_TRAIL" or "PROFIT_TRAIL"
    profit_chain_id: Optional[str] = None  # Link to profit booking chain
    profit_level: int = 0  # Level in profit booking chain (0-4)
    session_id: Optional[str] = None  # Session ID this trade belongs to
    
    # Timeframe logic tracking (Phase 5 & 6)
    logic_type: Optional[str] = None  # combinedlogic-1, combinedlogic-2, combinedlogic-3
    base_lot_size: Optional[float] = None  # Original lot before multiplier
    final_lot_size: Optional[float] = None  # Lot after multiplier applied
    lot_multiplier: Optional[float] = 1.0  # Multiplier used
    sl_multiplier: Optional[float] = 1.0  # SL multiplier used

    class Config:
        extra = "allow"
        
    @property
    def ticket(self):
        return self.trade_id
        
    @ticket.setter
    def ticket(self, value):
        self.trade_id = value
        
    base_sl_pips: Optional[float] = None  # Original SL distance in pips
    final_sl_pips: Optional[float] = None  # Final SL distance after multiplier

    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "entry": self.entry,
            "sl": self.sl,
            "tp": self.tp,
            "lot_size": self.lot_size,
            "direction": self.direction,
            "strategy": self.strategy,
            "status": self.status,
            "trade_id": self.trade_id,
            "open_time": self.open_time,
            "close_time": self.close_time,
            "pnl": self.pnl,
            "chain_id": self.chain_id,
            "chain_level": self.chain_level,
            "is_re_entry": self.is_re_entry,
            "order_type": self.order_type,
            "profit_chain_id": self.profit_chain_id,
            "profit_level": self.profit_level,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ReEntryChain(BaseModel):
    chain_id: str
    symbol: str
    direction: str
    original_entry: float
    original_sl_distance: float
    current_level: int
    max_level: int
    total_profit: float = 0.0
    trades: List[int] = []  # Trade IDs
    status: str = "active"  # active, completed, stopped
    created_at: str
    last_update: str
    trend_at_creation: Dict[str, str] = {}
    recovery_attempts: int = 0
    metadata: Dict[str, Any] = {}  # Stores SL system info, reductions, etc

class ProfitBookingChain(BaseModel):
    """Profit Booking Chain for pyramid compounding system"""
    chain_id: str
    symbol: str
    direction: str
    base_lot: float
    current_level: int
    max_level: int
    total_profit: float = 0.0
    active_orders: List[int] = []  # Trade IDs for current level
    status: str = "ACTIVE"  # ACTIVE, COMPLETED, STOPPED
    created_at: str
    updated_at: str
    profit_targets: List[float] = [10, 20, 40, 80, 160]  # Profit targets per level
    multipliers: List[int] = [1, 2, 4, 8, 16]  # Order multipliers per level
    sl_reductions: List[float] = [0, 10, 25, 40, 50]  # SL reduction % per level
    metadata: Dict[str, Any] = {}  # Additional chain metadata