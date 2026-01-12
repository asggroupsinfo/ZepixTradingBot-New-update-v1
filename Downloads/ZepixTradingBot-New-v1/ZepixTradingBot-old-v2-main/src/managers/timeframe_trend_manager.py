import json
import os
import pathlib
from datetime import datetime
from typing import Dict, Any, Optional

class TimeframeTrendManager:
    """Manage trends per timeframe instead of per logic"""
    
    def __init__(self, config_file: str = "config/timeframe_trends.json"):
        # Resolve absolute path to ensure persistence works regardless of CWD
        # Assume this file is in src/managers/
        # Root is 2 levels up from src/managers -> src -> root
        current_dir = pathlib.Path(__file__).parent.absolute()
        project_root = current_dir.parent.parent
        
        # If config_file is relative, make it absolute relative to project root
        if not os.path.isabs(config_file):
            self.config_file = str(project_root / config_file)
        else:
            self.config_file = config_file
            
        print(f"DEBUG: TimeframeTrendManager using config file: {self.config_file}")
        
        self.trends = self.load_trends()
        
    def load_trends(self) -> Dict[str, Any]:
        """Load trends from file with error handling"""
        try:
            if os.path.exists(self.config_file) and os.path.getsize(self.config_file) > 0:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    print(f"SUCCESS: Loaded trends from {self.config_file}")
                    # Debug: Print summary of loaded manual trends
                    manual_count = 0
                    
                    # CLEANUP: Filter out 5m trends if present (they are unused)
                    if "symbols" in data:
                        for sym in data["symbols"]:
                            if "5m" in data["symbols"][sym]:
                                del data["symbols"][sym]["5m"]
                                
                    for sym, tfs in data.get("symbols", {}).items():
                        for tf, details in tfs.items():
                            if details.get("mode") == "MANUAL":
                                manual_count += 1
                                print(f"DEBUG: Loaded MANUAL trend for {sym} {tf}: {details.get('trend')}")
                    print(f"DEBUG: Total manual trends loaded: {manual_count}")
                    return data
            else:
                print(f"WARNING: Trends file not found or empty at {self.config_file}, using defaults")
                # Return default structure if file doesn't exist or is empty
                return {
                    "symbols": {},
                    "default_mode": "AUTO"
                }
        except (json.JSONDecodeError, Exception) as e:
            print(f"WARNING: Trends file corrupted at {self.config_file}, using defaults: {str(e)}")
            return {
                "symbols": {},
                "default_mode": "AUTO"
            }
    
    def save_trends(self):
        """Save trends to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.trends, f, indent=4)
            # print(f"DEBUG: Saved trends to {self.config_file}") 
        except Exception as e:
            print(f"ERROR: Error saving trends to {self.config_file}: {str(e)}")
    
    def update_trend(self, symbol: str, timeframe: str, signal: str, mode: str = "AUTO"):
        """Update trend for a specific symbol and timeframe"""
        
        # 5m trends are NOT used for logic alignment (combinedlogic-1 uses 1H+15M)
        # We ignore 5m trend updates to keep data clean
        if timeframe.lower() in ["5m", "5min"]:
            # print(f"DEBUG: Ignoring 5m trend update for {symbol} (Unused by logic)")
            return False

        if symbol not in self.trends["symbols"]:
            self.trends["symbols"][symbol] = {}
        
        if timeframe not in self.trends["symbols"][symbol]:
            self.trends["symbols"][symbol][timeframe] = {}
        
        # Check if manually locked
        current = self.trends["symbols"][symbol][timeframe]
        if current.get("mode") == "MANUAL" and mode == "AUTO":
            print(f"WARNING: Manual trend locked for {symbol} {timeframe}, not updating")
            return  # Don't override manual settings
        
        # Convert signal to trend - FIXED BUG HERE
        signal_lower = signal.lower()
        if signal_lower in ["bull", "buy", "bullish"]:
            trend = "BULLISH"
        elif signal_lower in ["bear", "sell", "bearish"]:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"
            
        # Check if trend is already the same
        current_trend = current.get("trend")
        current_mode = current.get("mode")
        
        if current_trend == trend and current_mode == mode:
            print(f"INFO: Trend already {trend} ({mode}) for {symbol} {timeframe}, ignoring update")
            return False
        
        self.trends["symbols"][symbol][timeframe] = {
            "trend": trend,
            "mode": mode,
            "last_update": datetime.now().isoformat()
        }
        self.save_trends()
        print(f"SUCCESS: Trend updated: {symbol} {timeframe} -> {trend} ({mode})")
        return True
    
    def get_trend(self, symbol: str, timeframe: str) -> Optional[str]:
        """Get trend for a specific symbol and timeframe"""
        try:
            return self.trends["symbols"].get(symbol, {}).get(timeframe, {}).get("trend", "NEUTRAL")
        except:
            return "NEUTRAL"
    
    def get_mode(self, symbol: str, timeframe: str) -> str:
        """Get mode for a specific symbol and timeframe"""
        try:
            return self.trends["symbols"].get(symbol, {}).get(timeframe, {}).get("mode", "AUTO")
        except:
            return "AUTO"
    
    def detect_logic_from_strategy_or_timeframe(self, strategy: str, timeframe: Optional[str] = None) -> Optional[str]:
        """
        Detect logic type from strategy name or timeframe.
        
        This method normalizes strategy/logic identifiers to standard combinedlogic-1/2/3 format.
        Critical for fixing "Unknown logic" errors when TradingView sends "ZepixPremium".
        
        Args:
            strategy: Strategy name (may be "ZepixPremium", "combinedlogic-1", etc.)
            timeframe: Optional timeframe (5m, 15m, 1h) for detection
        
        Returns:
            "combinedlogic-1", "combinedlogic-2", "combinedlogic-3", or None if cannot detect
            
        Logic Mapping:
            - combinedlogic-1: 5m timeframe entries (requires 1h + 15m trend alignment)
            - combinedlogic-2: 15m timeframe entries (requires 1h + 15m trend alignment)
            - combinedlogic-3: 1h timeframe entries (requires 1d + 1h trend alignment)
        """
        # Already normalized - return as is
        if strategy in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
            return strategy
        
        # ✅ FIX: Map TradingView strategy names to internal combinedlogic identifiers
        strategy_lower = strategy.lower()
        if strategy_lower in ["zepixpremium", "zepix", "premium", "zepix_premium"]:
            # ZepixPremium can be any logic - use timeframe to determine
            if timeframe:
                tf_lower = timeframe.lower()
                if tf_lower in ["5m", "5min"]:
                    return "combinedlogic-1"
                elif tf_lower in ["15m", "15min"]:
                    return "combinedlogic-2"
                elif tf_lower in ["1h", "1hour", "1hr"]:
                    return "combinedlogic-3"
            # If no timeframe provided, default to combinedlogic-1
            return "combinedlogic-1"
        
        # Detect from timeframe if provided
        if timeframe:
            tf_lower = timeframe.lower()
            if tf_lower == "5m":
                return "combinedlogic-1"
            elif tf_lower == "15m":
                return "combinedlogic-2"
            elif tf_lower == "1h":
                return "combinedlogic-3"
        
        # Try to extract from strategy name (e.g., "combinedlogic-1_FRESH", "ZepixPremium_combinedlogic-2")
        import re
        match = re.search(r'(combinedlogic-[123])', strategy, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        
        # Cannot detect
        return None
    
    def check_logic_alignment(self, symbol: str, logic: str) -> Dict[str, Any]:
        """Check if trends align for a specific trading logic"""
        
        import logging
        logger = logging.getLogger(__name__)
        
        result = {
            "aligned": False,
            "direction": "NEUTRAL",
            "details": {},
            "failure_reason": None
        }
        
        # VALIDATE AND NORMALIZE LOGIC: Fix for "Unknown logic" error
        original_logic = logic
        if logic not in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
            # Try to detect from strategy name
            detected = self.detect_logic_from_strategy_or_timeframe(logic)
            if detected:
                logger.debug(
                    f"🔍 [LOGIC_DETECTION] Normalized '{original_logic}' → '{detected}' for {symbol}"
                )
                logic = detected
            else:
                result["failure_reason"] = f"Unknown logic: {logic} (could not auto-detect)"
                logger.warning(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ Unknown logic (no detection possible). "
                    f"Expected: combinedlogic-1/2/3, Got: {original_logic}"
                )
                return result
        
        # DIAGNOSTIC: Check if symbol exists in trends
        if symbol not in self.trends["symbols"]:
            result["failure_reason"] = f"Symbol {symbol} not found in trends dictionary"
            logger.debug(
                f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ Symbol not in trends. "
                f"Available symbols: {list(self.trends['symbols'].keys())}"
            )
            return result
        
        symbol_trends = self.trends["symbols"][symbol]
        
        if logic == "combinedlogic-1":  # 1H bias + 15M trend for 5M entries
            h1_trend = symbol_trends.get("1h", {}).get("trend", "NEUTRAL")
            m15_trend = symbol_trends.get("15m", {}).get("trend", "NEUTRAL")
            
            result["details"] = {"1h": h1_trend, "15m": m15_trend}
            
            # DIAGNOSTIC: Log alignment check details
            if h1_trend == "NEUTRAL":
                result["failure_reason"] = "1H trend is NEUTRAL"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ 1H trend is NEUTRAL "
                    f"(1H={h1_trend}, 15M={m15_trend})"
                )
            elif m15_trend == "NEUTRAL":
                result["failure_reason"] = "15M trend is NEUTRAL"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ 15M trend is NEUTRAL "
                    f"(1H={h1_trend}, 15M={m15_trend})"
                )
            elif h1_trend != m15_trend:
                result["failure_reason"] = f"Trends don't match: 1H={h1_trend} != 15M={m15_trend}"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ Trends don't match "
                    f"(1H={h1_trend}, 15M={m15_trend})"
                )
            else:
                result["aligned"] = True
                result["direction"] = h1_trend
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ✅ ALIGNED "
                    f"(1H={h1_trend}, 15M={m15_trend}, Direction={h1_trend})"
                )
                
        elif logic == "combinedlogic-2":  # 1H bias + 15M trend for 15M entries
            h1_trend = symbol_trends.get("1h", {}).get("trend", "NEUTRAL")
            m15_trend = symbol_trends.get("15m", {}).get("trend", "NEUTRAL")
            
            result["details"] = {"1h": h1_trend, "15m": m15_trend}
            
            # DIAGNOSTIC: Log alignment check details
            if h1_trend == "NEUTRAL":
                result["failure_reason"] = "1H trend is NEUTRAL"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ 1H trend is NEUTRAL "
                    f"(1H={h1_trend}, 15M={m15_trend})"
                )
            elif m15_trend == "NEUTRAL":
                result["failure_reason"] = "15M trend is NEUTRAL"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ 15M trend is NEUTRAL "
                    f"(1H={h1_trend}, 15M={m15_trend})"
                )
            elif h1_trend != m15_trend:
                result["failure_reason"] = f"Trends don't match: 1H={h1_trend} != 15M={m15_trend}"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ Trends don't match "
                    f"(1H={h1_trend}, 15M={m15_trend})"
                )
            else:
                result["aligned"] = True
                result["direction"] = h1_trend
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ✅ ALIGNED "
                    f"(1H={h1_trend}, 15M={m15_trend}, Direction={h1_trend})"
                )
                
        elif logic == "combinedlogic-3":  # 1D bias + 1H trend for 1H entries
            d1_trend = symbol_trends.get("1d", {}).get("trend", "NEUTRAL")
            h1_trend = symbol_trends.get("1h", {}).get("trend", "NEUTRAL")
            
            result["details"] = {"1d": d1_trend, "1h": h1_trend}
            
            # DIAGNOSTIC: Log alignment check details
            if d1_trend == "NEUTRAL":
                result["failure_reason"] = "1D trend is NEUTRAL"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ 1D trend is NEUTRAL "
                    f"(1D={d1_trend}, 1H={h1_trend})"
                )
            elif h1_trend == "NEUTRAL":
                result["failure_reason"] = "1H trend is NEUTRAL"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ 1H trend is NEUTRAL "
                    f"(1D={d1_trend}, 1H={h1_trend})"
                )
            elif d1_trend != h1_trend:
                result["failure_reason"] = f"Trends don't match: 1D={d1_trend} != 1H={h1_trend}"
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ Trends don't match "
                    f"(1D={d1_trend}, 1H={h1_trend})"
                )
            else:
                result["aligned"] = True
                result["direction"] = d1_trend
                logger.debug(
                    f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ✅ ALIGNED "
                    f"(1D={d1_trend}, 1H={h1_trend}, Direction={d1_trend})"
                )
        else:
            result["failure_reason"] = f"Unknown logic: {logic}"
            logger.warning(f"🔍 [ALIGNMENT_CHECK] {symbol} {logic}: ❌ Unknown logic")
        
        return result
    
    def set_manual_trend(self, symbol: str, timeframe: str, trend: str):
        """Manually set a trend that won't be overridden by signals"""
        # Convert BULLISH/BEARISH to bull/bear for signal
        if trend.upper() == "BULLISH":
            signal = "bull"
        elif trend.upper() == "BEARISH":
            signal = "bear"
        else:
            signal = "neutral"
            
        self.update_trend(symbol, timeframe, signal, "MANUAL")
    
    def set_auto_trend(self, symbol: str, timeframe: str):
        """Set trend back to AUTO mode (will be updated by TradingView signals)"""
        if symbol in self.trends["symbols"] and timeframe in self.trends["symbols"][symbol]:
            self.trends["symbols"][symbol][timeframe]["mode"] = "AUTO"
            self.save_trends()
            print(f"SUCCESS: Mode set to AUTO for {symbol} {timeframe}")
    
    def get_all_trends(self, symbol: str) -> Dict[str, str]:
        """Get all timeframe trends for a symbol"""
        if symbol not in self.trends["symbols"]:
            return {"15m": "NEUTRAL", "1h": "NEUTRAL", "1d": "NEUTRAL"}
        
        result = {}
        for tf in ["15m", "1h", "1d"]:
            result[tf] = self.trends["symbols"][symbol].get(tf, {}).get("trend", "NEUTRAL")
        
        return result
    
    def get_all_trends_with_mode(self, symbol: str) -> Dict[str, Dict[str, str]]:
        """Get all timeframe trends with mode information"""
        if symbol not in self.trends["symbols"]:
            return {
                "15m": {"trend": "NEUTRAL", "mode": "AUTO"},
                "1h": {"trend": "NEUTRAL", "mode": "AUTO"},
                "1d": {"trend": "NEUTRAL", "mode": "AUTO"}
            }
        
        result = {}
        for tf in ["15m", "1h", "1d"]:
            trend_data = self.trends["symbols"][symbol].get(tf, {})
            result[tf] = {
                "trend": trend_data.get("trend", "NEUTRAL"),
                "mode": trend_data.get("mode", "AUTO")
            }
        
        return result