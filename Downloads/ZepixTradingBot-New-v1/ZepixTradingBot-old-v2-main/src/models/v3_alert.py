"""
V3 Alert Data Models for ZEPIX_ULTIMATE_BOT_v3.pine Integration

This module defines Pydantic models for the enhanced v3 alert payload
from the TradingView Pine Script indicator.
"""

from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from datetime import datetime


class ZepixV3Alert(BaseModel):
    """
    V3 Enhanced Alert from ZEPIX_ULTIMATE_BOT_v3.pine
    
    Represents one of 11 signal types with full context:
    - 8 Entry signals (Institutional Launchpad, Liquidity Trap, etc.)
    - 2 Exit signals (Bullish Exit, Bearish Exit)
    - 1 Warning signal (Volatility Squeeze)
    - 1 Info signal (Trend Pulse)
    """
    
    # Core identification
    type: Literal["entry_v3", "exit_v3", "squeeze_v3", "trend_pulse_v3"]
    signal_type: str  # e.g., "Institutional_Launchpad", "Liquidity_Trap_Reversal"
    symbol: str
    direction: Literal["buy", "sell", "neutral"]  # neutral for squeeze/pulse
    tf: str  # "5", "15", "60", "240", etc.
    price: float
    
    # Consensus Engine (0-9 scale from 9-indicator voting)
    consensus_score: int
    
    # Optional SL/TP from indicator (Order Block based)
    sl_price: Optional[float] = None
    tp1_price: Optional[float] = None  # Closer target
    tp2_price: Optional[float] = None  # Extended target
    
    # MTF Trends String Format: "1,1,-1,1,1,1"
    # Indices: [0]=1m, [1]=5m, [2]=15m, [3]=1H, [4]=4H, [5]=1D
    # Bot will extract ONLY indices [2,3,4,5]
    mtf_trends: Optional[str] = None
    
    # Market Context
    market_trend: int  # 1=bull, -1=bear, 0=neutral
    volume_delta_ratio: Optional[float] = None
    price_in_ob: Optional[bool] = None  # Price in Order Block
    
    # Position Sizing (from Pine's consensus-based calculation)
    position_multiplier: Optional[float] = 1.0
    
    # Trend Pulse specific fields
    current_trends: Optional[str] = None  # Current MTF state
    previous_trends: Optional[str] = None  # Previous MTF state
    changed_timeframes: Optional[str] = None  # Which TFs changed
    change_details: Optional[str] = None  # Details of changes
    
    # Additional metadata
    timestamp: Optional[str] = None
    raw_data: Optional[dict] = None
    
    @validator('consensus_score')
    def validate_consensus_score(cls, v):
        """Ensure consensus score is within valid range"""
        if not 0 <= v <= 9:
            raise ValueError(f"Consensus score must be 0-9, got {v}")
        return v
    
    @validator('position_multiplier')
    def validate_position_multiplier(cls, v):
        """Ensure position multiplier is reasonable"""
        if v is not None and not 0.1 <= v <= 2.0:
            raise ValueError(f"Position multiplier must be 0.1-2.0, got {v}")
        return v
    
    @validator('mtf_trends')
    def validate_mtf_trends(cls, v):
        """Validate MTF trends string format"""
        if v is not None:
            parts = v.split(',')
            if len(parts) != 6:
                raise ValueError(f"MTF trends must have 6 values (1m,5m,15m,1H,4H,1D), got {len(parts)}")
            
            # Validate each value is 1, -1, or 0
            for part in parts:
                try:
                    val = int(part.strip())
                    if val not in [-1, 0, 1]:
                        raise ValueError(f"MTF trend values must be -1, 0, or 1, got {val}")
                except ValueError:
                    raise ValueError(f"Invalid MTF trend value: {part}")
        
        return v
    
    def get_mtf_pillars(self) -> dict:
        """
        Extract ONLY the 4 stable pillars from MTF trends string
        
        Returns:
            dict: {"15m": 1, "1h": 1, "4h": -1, "1d": 1}
        """
        if not self.mtf_trends:
            return {}
        
        trends = [int(t.strip()) for t in self.mtf_trends.split(',')]
        
        # Extract ONLY indices [2,3,4,5] - ignore [0,1] (1m, 5m noise)
        return {
            "15m": trends[2],  # Index 2
            "1h": trends[3],   # Index 3
            "4h": trends[4],   # Index 4
            "1d": trends[5]    # Index 5
        }
    
    def is_aggressive_reversal_signal(self) -> bool:
        """Check if this signal should trigger aggressive reversal (close + reverse)"""
        AGGRESSIVE_SIGNALS = [
            "Liquidity_Trap_Reversal",
            "Golden_Pocket_Flip",
            "Screener_Full_Bullish",
            "Screener_Full_Bearish"
        ]
        return self.signal_type in AGGRESSIVE_SIGNALS or self.consensus_score >= 7
    
    def is_conservative_exit_signal(self) -> bool:
        """Check if this is a conservative exit (close only, no reverse)"""
        CONSERVATIVE_SIGNALS = ["Bullish_Exit", "Bearish_Exit"]
        return self.signal_type in CONSERVATIVE_SIGNALS
    
    def should_bypass_trend_check(self) -> bool:
        """
        V3 fresh entries BYPASS trend check (5-layer pre-validation trusted)
        Re-entries and autonomous actions still REQUIRE trend check
        """
        return self.type == "entry_v3"
    
    class Config:
        # Allow extra fields for future compatibility
        extra = "allow"
        # Use enum values
        use_enum_values = True


class V3AlertResponse(BaseModel):
    """Response after processing a v3 alert"""
    status: Literal["success", "error", "skipped", "ignored"]
    message: Optional[str] = None
    logic_used: Optional[str] = None  # combinedlogic-1, combinedlogic-2, combinedlogic-3
    order_a_id: Optional[str] = None
    order_b_id: Optional[str] = None
    total_lot: Optional[float] = None
    action_taken: Optional[str] = None  # "entry", "exit", "reverse", "alert_only"
    closed_positions: Optional[int] = 0
    
    class Config:
        use_enum_values = True
