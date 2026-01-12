"""
Pine Script Logic Engine - Core Translation
Translates ZEPIX Pine Script logic to Python for validation testing
"""

class OrderBlock:
    """Represents a Smart Money Order Block"""
    def __init__(self, top, btm, avg, loc, css=None):
        self.top = top
        self.btm = btm
        self.avg = avg
        self.loc = loc
        self.css = css
        self.isbb = False  # is broken/mitigated
        self.bbloc = 0     # broken location

class FVG:
    """Fair Value Gap structure"""
    def __init__(self, top, btm, loc):
        self.top = top
        self.btm = btm
        self.loc = loc
        self.isbb = False
        self.bbloc = 0

class TradeState:
    """Active trade state tracking"""
    def __init__(self):
        self.isActive = False
        self.isLong = False
        self.entryPrice = 0.0
        self.stopLoss = 0.0
        self.takeProfit1 = 0.0
        self.takeProfit2 = 0.0
        self.entryBar = 0

class MarketData:
    """Single bar of market data"""
    def __init__(self, bar_index, time, open, high, low, close, volume):
        self.bar_index = bar_index
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

class PineScriptEngine:
    """Main simulation engine - translates Pine Script execution"""
    
    def __init__(self):
        # Arrays
        self.bullOBs = []
        self.bearOBs = []
        self.bullFVGs = []
        self.bearFVGs = []
        
        # State
        self.tradeState = TradeState()
        self.marketTrend = 0  # 1=Bull, -1=Bear, 0=None
        self.structureTrend = 0
        self.consensusScore = 0
        self.prev_close = 0.0  # Track previous close for crossover detection
        
        # Signal 12 Specific - ADX Momentum Tracking
        self.zlTrend = 0                     # ZLEMA Trend
        self.prev_zlTrend = 0                # Previous ZLEMA Trend
        self.adxValue = 0.0                  # Current ADX for momentum check
        
        # Volume tracking
        
        # Volume tracking
        self.upVol_Fixed = 0.0
        self.dnVol_Fixed = 0.0
        
        # Flags
        self.priceInBullOB = False
        self.priceInBearOB = False
        self.priceInAnyBullOB = False
        self.priceInAnyBearOB = False
        
        # Config
        self.smcEnabled = True
        self.consensusEnabled = True
        self.breakoutEnabled = True
        self.volumeOK = True
        self.mtfAlignmentOK = True
        
    def reset(self):
        """Reset engine state for new test"""
        self.__init__()
        
    # ============================================
    # SECTION 6.6: Price in Order Block Check (LOOPING)
    # ============================================
    
    def check_price_in_ob(self, high, low):
        """
        Translates Pine Section 6.6 - Loop through ALL Order Blocks
        Lines 585-598 in FIXED version
        """
        self.priceInBullOB = False
        self.priceInBearOB = False
        
        if self.smcEnabled and len(self.bullOBs) > 0:
            for i in range(len(self.bullOBs)):
                ob = self.bullOBs[i]
                # if not ob.isbb and low <= ob.top and high >= ob.btm
                if not ob.isbb and low <= ob.top and high >= ob.btm:
                    self.priceInBullOB = True
                    break
        
        if self.smcEnabled and len(self.bearOBs) > 0:
            for i in range(len(self.bearOBs)):
                ob = self.bearOBs[i]
                if not ob.isbb and high >= ob.btm and low <= ob.top:
                    self.priceInBearOB = True
                    break
    
    def check_price_in_any_ob(self, high, low):
        """
        Dashboard version - checks even broken OBs for display context
        Lines 599-615 in FIXED version
        """
        self.priceInAnyBullOB = False
        self.priceInAnyBearOB = False
        
        if self.smcEnabled and len(self.bullOBs) > 0:
            for i in range(len(self.bullOBs)):
                ob = self.bullOBs[i]
                # Check even if broken - for dashboard context
                if low <= ob.top and high >= ob.btm:
                    self.priceInAnyBullOB = True
                    break
        
        if self.smcEnabled and len(self.bearOBs) > 0:
            for i in range(len(self.bearOBs)):
                ob = self.bearOBs[i]
                if high >= ob.btm and low <= ob.top:
                    self.priceInAnyBearOB = True
                    break
    
    # ============================================
    # SECTION 11: SIGNAL LOGIC (All 11 Signals)
    # ============================================
    
    def check_signal1_institutional_launchpad(self):
        """Signal 1: Institutional Launchpad"""
        # Bull
        bull = (self.smcEnabled and self.consensusEnabled and self.breakoutEnabled and 
                self.priceInBullOB and self.consensusScore >= 7 and 
                self.marketTrend == 1 and self.volumeOK)
        # Bear
        bear = (self.smcEnabled and self.consensusEnabled and self.breakoutEnabled and 
                self.priceInBearOB and self.consensusScore <= 2 and 
                self.marketTrend == -1 and self.volumeOK)
        return bull, bear
    
    def check_signal2_liquidity_trap(self, bullSweep=False, bearSweep=False):
        """Signal 2: Liquidity Trap Reversal"""
        bull = (self.smcEnabled and bullSweep and self.priceInBullOB and 
                self.volumeOK and self.marketTrend == 1)
        bear = (self.smcEnabled and bearSweep and self.priceInBearOB and 
                self.volumeOK and self.marketTrend == -1)
        return bull, bear
    
    def check_signal12_sideways_breakout(self, close, zlema):
        """Signal 12: Sideways Breakout (Hybrid Logic)
        
        Fires when:
        1. Trend JUST flipped (ZLEMA crossover)
        2. Market has CURRENT momentum (ADX > 20)
        3. Passes conflict resolution
        """
        # 1. Detect Trend Flip
        zlemaFlipBull = (self.zlTrend == 1 and self.prev_zlTrend != 1)
        priceCrossBull = (close > zlema and self.prev_close <= zlema)  # Crossover
        trendJustFlippedBull = zlemaFlipBull or priceCrossBull
        
        zlemaFlipBear = (self.zlTrend == -1 and self.prev_zlTrend != -1)
        priceCrossBear = (close < zlema and self.prev_close >= zlema)  # Crossunder
        trendJustFlippedBear = zlemaFlipBear or priceCrossBear
        
        # 2. Market Momentum Check (ADX > 20)
        marketHasMomentum = self.adxValue > 20
        
        # 3. Conflict Resolution
        bullishSignalAllowed = (self.marketTrend >= 0)  # Not in bear trend
        bearishSignalAllowed = (self.marketTrend <= 0)  # Not in bull trend
        
        # Signal Logic
        bull = (trendJustFlippedBull and marketHasMomentum and 
                self.volumeOK and bullishSignalAllowed)
        bear = (trendJustFlippedBear and marketHasMomentum and 
                self.volumeOK and bearishSignalAllowed)
        
        return bull, bear
    
    def check_signal3_momentum_breakout(self, trendLongBreak=False, trendShortBreak=False):
        """Signal 3: Momentum Breakout"""
        bull = (self.breakoutEnabled and self.consensusEnabled and trendLongBreak and 
                self.consensusScore >= 7 and self.volumeOK)
        bear = (self.breakoutEnabled and self.consensusEnabled and trendShortBreak and 
                self.consensusScore <= 2 and self.volumeOK)
        return bull, bear
    
    def check_signal4_mitigation_test(self, newBullOB=False, newBearOB=False, close_gt_open=False):
        """Signal 4: Mitigation Test Entry"""
        bull = (self.smcEnabled and self.priceInBullOB and not newBullOB and 
                close_gt_open and self.volumeOK and self.marketTrend == 1)
        bear = (self.smcEnabled and self.priceInBearOB and not newBearOB and 
                not close_gt_open and self.volumeOK and self.marketTrend == -1)
        return bull, bear
    
    def check_signal5_bullish_exit(self, high_val):
        """Signal 5: Bullish Exit"""
        return (self.tradeState.isActive and self.tradeState.isLong and 
                (high_val >= self.tradeState.takeProfit1 or self.priceInBearOB or self.consensusScore <= 3))
    
    def check_signal6_bearish_exit(self, low_val):
        """Signal 6: Bearish Exit"""
        return (self.tradeState.isActive and not self.tradeState.isLong and 
                (low_val <= self.tradeState.takeProfit1 or self.priceInBullOB or self.consensusScore >= 6))
    
    def check_signal7_golden_pocket(self, fibLevel=0.7, isCHOCH=False, isBOS=False):
        """Signal 7: Golden Pocket Flip"""
        bull = (self.smcEnabled and (isCHOCH or isBOS) and fibLevel >= 0.618 and 
                fibLevel <= 0.786 and self.priceInBullOB and self.volumeOK)
        bear = (self.smcEnabled and (isCHOCH or isBOS) and fibLevel >= 0.214 and 
                fibLevel <= 0.382 and self.priceInBearOB and self.volumeOK)
        return bull, bear
    
    def check_signal8_volatility_squeeze(self, volatilitySqueeze=False):
        """Signal 8: Volatility Squeeze Alert"""
        return (self.breakoutEnabled and volatilitySqueeze and 
                self.consensusScore >= 4 and self.consensusScore <= 5)
    
    def check_signal9_screener_full_bullish(self, volumeDeltaRatio=0):
        """Signal 9: Screener Full Bullish"""
        return (self.consensusEnabled and self.consensusScore == 9 and 
                self.mtfAlignmentOK and self.marketTrend == 1 and 
                volumeDeltaRatio > 2.0 and not self.priceInBearOB)
    
    def check_signal10_screener_full_bearish(self, volumeDeltaRatio=0):
        """Signal 10: Screener Full Bearish"""
        return (self.consensusEnabled and self.consensusScore == 0 and 
                self.mtfAlignmentOK and self.marketTrend == -1 and 
                volumeDeltaRatio < -2.0 and not self.priceInBullOB)
    
    def check_signal11_trend_pulse(self, trendPulseTriggered=False):
        """Signal 11: Trend Pulse"""
        return trendPulseTriggered
        
    def check_signal12_sideways_breakout(self, zlTrend, prev_zlTrend, close, zlema, volumeOK=True):
        """
        Signal 12: Sideways Breakout (Smart Trend Catcher)
        Logic: (wasInSqueeze OR wasNeutral) AND Resulting Trend Trigger
        """
        # 1. Setup Condition (Lookback 8 bars)
        wasInSqueeze = any(self.signal8_history[:8])
        wasNeutral = any(4 <= score <= 5 for score in self.consensus_history[:8])
        
        # 2. Trigger Condition
        # Green Flip
        zlemaFlipBull = zlTrend == 1 and prev_zlTrend != 1
        priceCrossBull = close > zlema and self.marketTrend != 1 # Simplify cross logic
        trendStartBull = zlemaFlipBull or priceCrossBull
        
        # Red Flip
        zlemaFlipBear = zlTrend == -1 and prev_zlTrend != -1
        priceCrossBear = close < zlema and self.marketTrend != -1
        trendStartBear = zlemaFlipBear or priceCrossBear
        
        # 3. Combined
        bull = (wasInSqueeze or wasNeutral) and trendStartBull and volumeOK
        bear = (wasInSqueeze or wasNeutral) and trendStartBear and volumeOK
        
        return bull, bear
    
    # ============================================
    # SECTION 14: Volume Table Calculation
    # ============================================
    
    def update_volume_table(self, close, open_p, high, low, volume):
        """
        Volume Table Logic - Intra-Bar Estimation
        Matches Pine Script v3.0 FINAL Fix
        """
        range_val = high - low
        
        if range_val > 0:
            estBuyVol = volume * ((close - low) / range_val)
            estSellVol = volume * ((high - close) / range_val)
        else:
            # Doji / Zero Range
            estBuyVol = volume * 0.5
            estSellVol = volume * 0.5
            
        return estBuyVol, estSellVol
    
    # ============================================
    # SIGNAL 12: SIDEWAYS BREAKOUT STRATEGY (REFINED LOGIC)
    # ============================================
    
    def check_signal12_sideways_breakout(self, zlTrend, prev_zlTrend, adx, consensus_score, volumeOK=True, bullishSignalAllowed=True, bearishSignalAllowed=True):
        """
        Signal 12 Refined Logic:
        1. Trigger: Trend Just Flipped (ZLEMA Cross)
        2. Filter: Momentum Exists (ADX > 20) -> Confirms Breakout
        3. Filter: Consensus Alignment (Bull >=4, Bear <=5) -> Prevents V-Shape Whipsaws
        """
        
        # 1. Trigger: Trend Just Flipped
        trendJustFlippedBull = (zlTrend == 1 and prev_zlTrend != 1)
        trendJustFlippedBear = (zlTrend == -1 and prev_zlTrend != -1)
        
        # 2. Filter: Market has Momentum (ADX check)
        # Using hardcoded 20 as per user's approved "Simpler Logic", although pine script has input.
        # Logic matches Pine Script default.
        marketHasMomentum = adx > 20
        
        # 3. Filter: Consensus Alignment
        # Bullish: >= 4 (Neutral or Bullish)
        # Bearish: <= 5 (Neutral or Bearish)
        consensusBull = consensus_score >= 4
        consensusBear = consensus_score <= 5
        
        # Final Signal Logic
        signal12_Bull = trendJustFlippedBull and marketHasMomentum and consensusBull and volumeOK and bullishSignalAllowed
        signal12_Bear = trendJustFlippedBear and marketHasMomentum and consensusBear and volumeOK and bearishSignalAllowed
        
        msg = f"Sig12 Check: FlipBull={trendJustFlippedBull}, FlipBear={trendJustFlippedBear}, ADX={adx}, ConScore={consensus_score} -> Bull={signal12_Bull}, Bear={signal12_Bear}"
        
        return signal12_Bull, signal12_Bear
    
    # ============================================
    # SECTION 16: Mitigation Logic (AFTER Signals)
    # ============================================
    
    def check_mitigation(self, high, low, close, open_p, time):
        """
        OB Mitigation Check - Runs AFTER signal detection
        Lines 1742-1773 in FIXED version
        """
        # Bull OBs
        if self.smcEnabled and len(self.bullOBs) > 0:
            for i in range(len(self.bullOBs) - 1, -1, -1):
                ob = self.bullOBs[i]
                if not ob.isbb:
                    # Using "Wick" method: low < ob.btm
                    mitigated = low < ob.btm
                    if mitigated:
                        ob.isbb = True
                        ob.bbloc = time
        
        # Bear OBs
        if self.smcEnabled and len(self.bearOBs) > 0:
            for i in range(len(self.bearOBs) - 1, -1, -1):
                ob = self.bearOBs[i]
                if not ob.isbb:
                    mitigated = high > ob.top
                    if mitigated:
                        ob.isbb = True
                        ob.bbloc = time
