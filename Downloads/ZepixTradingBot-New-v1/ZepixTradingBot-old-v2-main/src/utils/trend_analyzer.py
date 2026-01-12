import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

class TrendAnalyzer:
    """
    Autonomous trend detection for re-entry decisions.
    Uses Price Action (High/Low analysis) and simple Momentum.
    """
    
    def __init__(self, mt5_client):
        self.mt5_client = mt5_client
        self.logger = logging.getLogger(__name__)
        
    def get_current_trend(self, symbol, timeframe="15m"):
        """
        Determines the current trend for a symbol.
        Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        try:
            # Get last 20 candles
            candles = self.mt5_client.get_candles(symbol, timeframe, 20)
            if not candles:
                self.logger.warning(f"TrendAnalyzer: No candles found for {symbol}")
                return "NEUTRAL"
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(candles)
            
            # 1. Price Momentum Check (Last 3 candles)
            close = df['close'].values
            momentum_bullish = close[-1] > close [-2]
            momentum_bearish = close[-1] < close [-2]
            
            # 2. Moving Average Check (Simple SMA 7 vs SMA 14)
            sma_7 = np.mean(close[-7:])
            sma_14 = np.mean(close[-14:])
            
            ma_bullish = sma_7 > sma_14
            ma_bearish = sma_7 < sma_14
            
            # 3. Simple High/Low Check (Price Action)
            # Recent high higher than previous high?
            highs = df['high'].values
            lows = df['low'].values
            
            hh_bullish = highs[-1] >= np.max(highs[-5:-1])
            ll_bearish = lows[-1] <= np.min(lows[-5:-1])
            
            # SCORING SYSTEM
            score = 0
            if ma_bullish: score += 1
            if momentum_bullish: score += 1
            if hh_bullish: score += 1
            
            if ma_bearish: score -= 1
            if momentum_bearish: score -= 1
            if ll_bearish: score -= 1
            
            # Determine Trend
            if score >= 2:
                return "BULLISH"
            elif score <= -2:
                return "BEARISH"
            else:
                return "NEUTRAL"
                
        except Exception as e:
            self.logger.error(f"Error in TrendAnalyzer.get_current_trend: {e}")
            return "NEUTRAL"

    def is_aligned(self, trade_direction, trend):
        """
        Checks if trade direction matches the detected trend.
        """
        if trade_direction.lower() == "buy" and trend == "BULLISH":
            return True
        if trade_direction.lower() == "sell" and trend == "BEARISH":
            return True
        return False
