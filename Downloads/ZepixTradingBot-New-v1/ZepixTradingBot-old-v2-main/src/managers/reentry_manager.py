from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from src.models import Trade, ReEntryChain
from src.utils.trend_analyzer import TrendAnalyzer
import uuid

class ReEntryManager:
    """Manage re-entry chains and SL hunting protection"""
    
    def __init__(self, config, mt5_client=None):
        self.config = config
        self.mt5_client = mt5_client
        self.active_chains = {}  # chain_id -> ReEntryChain
        self.recent_sl_hits = {}  # symbol -> list of recent SL hits
        self.completed_tps = {}  # symbol -> recent TP completions
        
        # Initialize TrendAnalyzer if client available
        self.trend_analyzer = None
        if self.mt5_client:
            self.trend_analyzer = TrendAnalyzer(self.mt5_client)
            
    def set_mt5_client(self, mt5_client):
        """Set MT5 client dependency"""
        self.mt5_client = mt5_client
        if not self.trend_analyzer:
            self.trend_analyzer = TrendAnalyzer(self.mt5_client)
        
    def create_chain(self, trade: Trade) -> ReEntryChain:
        """Create a new re-entry chain from initial trade"""
        
        chain_id = f"{trade.symbol}_{uuid.uuid4().hex[:8]}"
        
        # Handle simulation mode where trade_id might be None
        # Use negative timestamp-based ID for simulation trades
        trade_ids = []
        if trade.trade_id is not None:
            trade_ids = [trade.trade_id]
        else:
            # Create a pseudo-ID for simulation mode
            sim_id = int(datetime.now().timestamp() * 1000) % 1000000
            trade_ids = [sim_id]
            print(f"INFO: Simulation mode: Using pseudo trade ID {sim_id}")
        
        # Get active SL system and reduction info
        active_system = self.config.get("active_sl_system", "sl-1")
        symbol_reductions = self.config.get("symbol_sl_reductions", {})
        symbol_reduction = symbol_reductions.get(trade.symbol, 0)
        
        # Get ORIGINAL unreduced SL pips from dual system config
        # Determine account tier based on balance
        balance = self.config.get("account_balance", 10000)
        if balance < 7500:
            tier = "5000"
        elif balance < 17500:
            tier = "10000"
        elif balance < 37500:
            tier = "25000"
        elif balance < 75000:
            tier = "50000"
        else:
            tier = "100000"
        
        # Fetch original SL pips from the active system config
        original_sl_pips = self.config["sl_systems"][active_system]["symbols"][trade.symbol][tier]["sl_pips"]
        
        # Calculate applied SL pips (what was actually used on the trade)
        applied_sl_pips = original_sl_pips * (1 - symbol_reduction / 100) if symbol_reduction > 0 else original_sl_pips
        
        chain = ReEntryChain(
            chain_id=chain_id,
            symbol=trade.symbol,
            direction=trade.direction,
            original_entry=trade.entry,
            original_sl_distance=abs(trade.entry - trade.sl),
            current_level=1,
            max_level=self.config["re_entry_config"]["max_chain_levels"],
            trades=trade_ids,
            created_at=datetime.now().isoformat(),
            last_update=datetime.now().isoformat(),
           metadata={
                "sl_system_used": active_system,
                "sl_reduction_percent": symbol_reduction,
                "original_sl_pips": original_sl_pips,
                "applied_sl_pips": applied_sl_pips,
                "actual_lot_size": trade.lot_size,  # ✅ CRITICAL FIX: Store broker-adjusted lot for SL Hunt recovery
                "logic": trade.strategy  # Store strategy/logic for recovery
            }
        )
        
        self.active_chains[chain_id] = chain
        trade.chain_id = chain_id
        
        return chain
    
    def check_reentry_opportunity(self, symbol: str, signal: str, 
                                 price: float) -> Dict[str, Any]:
        """Check if new signal qualifies for re-entry"""
        
        result = {
            "is_reentry": False,
            "type": None,  # "tp_continuation" or "sl_recovery"
            "chain_id": None,
            "level": 1,
            "sl_adjustment": 1.0
        }
        
        # Check for TP continuation
        tp_opportunity = self._check_tp_continuation(symbol, signal, price)
        if tp_opportunity["eligible"]:
            result["is_reentry"] = True
            result["type"] = "tp_continuation"
            result["chain_id"] = tp_opportunity["chain_id"]
            result["level"] = tp_opportunity["level"]
            result["sl_adjustment"] = tp_opportunity["sl_adjustment"]
            return result
        
        # Check for SL recovery
        sl_opportunity = self._check_sl_recovery(symbol, signal, price)
        if sl_opportunity["eligible"]:
            result["is_reentry"] = True
            result["type"] = "sl_recovery"
            result["chain_id"] = sl_opportunity["chain_id"]  # Continue existing chain!
            result["level"] = sl_opportunity["level"]  # Use calculated level, not hardcoded!
            result["sl_adjustment"] = sl_opportunity["sl_adjustment"]  # Use progressive reduction!
            return result
        
        return result
    
    def _check_tp_continuation(self, symbol: str, signal: str, 
                              price: float) -> Dict[str, Any]:
        """Check if this is a continuation after TP hit"""
        
        result = {"eligible": False}
        
        if symbol not in self.completed_tps:
            return result
        
        recent_tps = self.completed_tps[symbol]
        current_time = datetime.now()
        
        for tp_event in recent_tps:
            time_since_tp = current_time - tp_event["time"]
            
            # Check if within continuation window
            if time_since_tp > timedelta(minutes=self.config["re_entry_config"]["recovery_window_minutes"]):
                continue
            
            # Check if same direction
            signal_direction = "buy" if signal in ["buy", "bull"] else "sell"
            if signal_direction != tp_event["direction"]:
                continue
            
            # Check if we haven't exceeded max levels
            chain = self.active_chains.get(tp_event["chain_id"])
            if chain and chain.current_level < chain.max_level:
                result["eligible"] = True
                result["chain_id"] = chain.chain_id
                result["level"] = chain.current_level + 1
                
                # Calculate SL adjustment
                reduction_per_level = self.config["re_entry_config"]["sl_reduction_per_level"]
                result["sl_adjustment"] = (1 - reduction_per_level) ** (result["level"] - 1)
                
                break
        
        return result
    
    def _check_sl_recovery(self, symbol: str, signal: str, 
                          price: float) -> Dict[str, Any]:
        """Check if this is a recovery after SL hit - continues existing chain"""
        
        result = {"eligible": False}
        
        if symbol not in self.recent_sl_hits:
            return result
        
        recent_sls = self.recent_sl_hits[symbol]
        current_time = datetime.now()
        
        for sl_event in recent_sls:
            time_since_sl = current_time - sl_event["time"]
            
            # Check if within recovery window
            if time_since_sl > timedelta(minutes=self.config["re_entry_config"]["recovery_window_minutes"]):
                continue
            
            # SAFETY CHECK #1: Enforce minimum time between re-entries (cooldown)
            min_time_seconds = self.config["re_entry_config"]["min_time_between_re_entries"]
            if time_since_sl < timedelta(seconds=min_time_seconds):
                print(f"WAIT: Re-entry cooldown active ({time_since_sl.seconds}s / {min_time_seconds}s)")
                continue
            
            # Check if same direction
            signal_direction = "buy" if signal in ["buy", "bull"] else "sell"
            if signal_direction != sl_event["direction"]:
                continue
            
            # Get chain info to continue it (not create new one!)
            chain_id = sl_event.get("chain_id")
            chain = self.active_chains.get(chain_id) if chain_id else None
            
            # Only allow re-entry if chain exists and hasn't hit max level
            if chain and chain.current_level < chain.max_level:
                # SAFETY CHECK #2: Verify price has recovered towards original entry
                # For BUY: new price should be higher than SL (recovering upwards)
                # For SELL: new price should be lower than SL (recovering downwards)
                price_recovered = False
                if signal_direction == "buy":
                    price_recovered = price > sl_event["sl_price"]
                else:
                    price_recovered = price < sl_event["sl_price"]
                
                if not price_recovered:
                    print(f"ERROR: Re-entry blocked: Price has not recovered from SL level")
                    continue
                
                result["eligible"] = True
                result["chain_id"] = chain.chain_id
                result["level"] = chain.current_level + 1
                
                # Calculate SL adjustment (progressive reduction)
                reduction_per_level = self.config["re_entry_config"]["sl_reduction_per_level"]
                result["sl_adjustment"] = (1 - reduction_per_level) ** (result["level"] - 1)
                
                # Reactivate chain
                chain.status = "active"
                
                print(f"SUCCESS: SL Recovery Re-Entry Eligible (Safe):")
                print(f"   Chain: {chain.chain_id}")
                print(f"   Level: {result['level']}/{chain.max_level}")
                print(f"   SL Adjustment: {result['sl_adjustment']:.2f}")
                print(f"   Time Since SL: {time_since_sl.seconds}s")
                print(f"   Price Recovered: {price_recovered}")
                
                break
        
        return result
    
    def record_tp_hit(self, trade: Trade, tp_price: float):
        """Record TP hit for continuation tracking"""
        
        if trade.symbol not in self.completed_tps:
            self.completed_tps[trade.symbol] = []
        
        # Keep only recent TPs (last 30 minutes)
        self._clean_old_events(self.completed_tps[trade.symbol])
        
        self.completed_tps[trade.symbol].append({
            "time": datetime.now(),
            "chain_id": trade.chain_id,
            "direction": trade.direction,
            "tp_price": tp_price,
            "original_entry": trade.original_entry or trade.entry
        })
        
        # Update chain status
        if trade.chain_id in self.active_chains:
            chain = self.active_chains[trade.chain_id]
            chain.total_profit += abs(tp_price - trade.entry) * trade.lot_size * 10000
            chain.last_update = datetime.now().isoformat()
    
    def record_sl_hit(self, trade: Trade):
        """Record SL hit for recovery tracking"""
        
        if trade.symbol not in self.recent_sl_hits:
            self.recent_sl_hits[trade.symbol] = []
        
        # Keep only recent SLs (last 30 minutes)
        self._clean_old_events(self.recent_sl_hits[trade.symbol])
        
        self.recent_sl_hits[trade.symbol].append({
            "time": datetime.now(),
            "direction": trade.direction,
            "sl_price": trade.sl,
            "original_entry": trade.original_entry or trade.entry,
            "chain_id": trade.chain_id  # Store chain_id to continue chain on re-entry,
        })
        
        # Update chain status based on Loss Capping Logic
        if trade.chain_id in self.active_chains:
            chain = self.active_chains[trade.chain_id]
            
            # Count recovery attempts
            if not hasattr(chain, 'recovery_attempts'):
                chain.recovery_attempts = 0
            
            # Allow MAX 1 recovery attempt (as per revised plan)
            MAX_RECOVERIES = 1
            
            if chain.recovery_attempts < MAX_RECOVERIES:
                chain.status = "recovery_mode"
                chain.recovery_attempts += 1
                
                # 🆕 ENHANCED: Store recovery metadata for SL Hunt monitoring
                chain.metadata["recovery_sl_price"] = trade.sl
                chain.metadata["recovery_started_at"] = datetime.now().isoformat()
                chain.metadata["recovery_original_level"] = chain.current_level
                
                print(f"🔄 RECOVERY MODE: Chain {trade.chain_id} SL Hit → Activating SL Hunt (Attempt {chain.recovery_attempts}/{MAX_RECOVERIES})")
            else:
                chain.status = "stopped"
                chain.metadata["stop_reason"] = "Max recovery attempts exceeded"
                print(f"🛑 HARD STOP: Chain {trade.chain_id} SL Hit → MAX RECOVERIES EXCEEDED → Chain Dead")
    
    def _clean_old_events(self, events: List[Dict]):
        """Remove events older than recovery window"""
        
        current_time = datetime.now()
        window = timedelta(minutes=self.config["re_entry_config"]["recovery_window_minutes"])
        
        events[:] = [e for e in events if current_time - e["time"] <= window]
    
    def update_chain_level(self, chain_id: str, new_trade_id: int):
        """Update chain when new re-entry is placed"""
        
        if chain_id in self.active_chains:
            chain = self.active_chains[chain_id]
            
            # Check if this was a recovery trade
            is_recovery = getattr(chain, 'status', '') == 'recovery_mode'
            
            if is_recovery:
                # On recovery, we DON'T increment level, we stay on same level but reset status
                chain.status = "active"
                print(f"INFO: Chain {chain_id} RE-ACTIVATED after recovery (Level {chain.current_level})")
            else:
                # Normal progression
                chain.current_level += 1
            
            # Handle None trade_id for simulation mode
            if new_trade_id is not None:
                chain.trades.append(new_trade_id)
            else:
                # Create pseudo-ID for simulation
                sim_id = int(datetime.now().timestamp() * 1000) % 1000000
                chain.trades.append(sim_id)
                print(f"INFO: Simulation mode: Using pseudo trade ID {sim_id} for re-entry")
            
            chain.last_update = datetime.now().isoformat()
            
            if chain.current_level >= chain.max_level:
                chain.status = "completed"
    
    def check_sl_hunt_recovery(self, chain, current_price: float) -> Dict[str, Any]:
        """
        🛡️ NEW: Check if SL hunt recovery conditions are met for chain in recovery_mode
        
        Monitors chains with status='recovery_mode' and checks:
        1. Recovery window not expired (symbol-specific)
        2. Price recovered beyond SL + min_pips
        3. Trend still aligned
        4. Optional: Volatility check
        
        Returns: {
            "eligible": bool,
            "entry_price": float,
            "tight_sl_price": float,
            "resume_to_next_level": bool,
            "current_level": int,
            "next_level_on_success": int
        }
        """
        result = {"eligible": False, "reason": ""}
        
        # Check chain in recovery mode
        if chain.status != "recovery_mode":
            result["reason"] = "Chain not in recovery mode"
            return result
        
        # Get recovery metadata
        recovery_sl = chain.metadata.get("recovery_sl_price")
        recovery_start = chain.metadata.get("recovery_started_at")
        
        if not recovery_sl or not recovery_start:
            result["reason"] = "Missing recovery metadata"
            return result
        
        # Get config
        hunt_config = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("sl_hunt_recovery", {})
        if not hunt_config.get("enabled", False):
            result["reason"] = "SL hunt recovery disabled in config"
            return result
        
        # Check recovery window timeout (symbol-specific)
        symbol_windows = hunt_config.get("recovery_windows_by_symbol", {})
        symbol_window = symbol_windows.get(chain.symbol, hunt_config.get("recovery_window_minutes", 30))
        
        time_elapsed = (datetime.now() - datetime.fromisoformat(recovery_start)).total_seconds() / 60
        
        if time_elapsed > symbol_window:
            result["reason"] = f"Recovery window expired ({time_elapsed:.1f} min > {symbol_window} min)"
            chain.status = "stopped"
            chain.metadata["stop_reason"] = "Recovery window timeout"
            print(f"⏰ TIMEOUT: Chain {chain.chain_id} recovery window expired → Chain stopped")
            return result
        
        # Price recovery check (70% of SL Distance Rule)
        # Old Logic: SL + 1 pip (Rejected)
        # New Logic: SL + (Original_SL_Dist * 0.70)
        
        
        # Ensure pip_size is available
        pip_size = self.config.get("symbol_config", {}).get(chain.symbol, {}).get("pip_size", 0.01)

        original_sl_dist = chain.original_sl_distance
        if not original_sl_dist:
            # Fallback if distance not stored
            original_sl_dist = chain.metadata.get("applied_sl_pips", 50) * pip_size
            
        recovery_threshold = original_sl_dist * 0.70
        
        price_recovered = False
        target_price = 0.0
        
        if chain.direction == "buy":
            target_price = recovery_sl + recovery_threshold
            price_recovered = current_price >= target_price
        else:
            target_price = recovery_sl - recovery_threshold
            price_recovered = current_price <= target_price
        
        if not price_recovered:
            result["reason"] = f"Price not recovered 70% (Current: {current_price:.5f}, Target: {target_price:.5f})"
            return result
        
        # Trend alignment check
        if self.trend_analyzer:
            try:
                trend = self.trend_analyzer.get_current_trend(chain.symbol)
                is_aligned = self.trend_analyzer.is_aligned(chain.direction, trend)
                
                if not is_aligned:
                    result["reason"] = f"Trend not aligned (Direction: {chain.direction}, Trend: {trend})"
                    return result
            except Exception as e:
                result["reason"] = f"Trend check failed: {str(e)}"
                return result
        
        # Volatility check (optional - Recommendation #1)
        if hunt_config.get("volatility_check", False):
            # Simplified volatility check for now
            # TODO: Implement full ATR-based check if needed
            pass
        
        # Calculate tight SL (50% of original)
        tight_sl_multiplier = hunt_config.get("tight_sl_multiplier", 0.5)
        original_sl_pips = chain.metadata.get("applied_sl_pips", 50)
        tight_sl_distance = (original_sl_pips * pip_size) * tight_sl_multiplier
        
        if chain.direction == "buy":
            tight_sl_price = current_price - tight_sl_distance
        else:
            tight_sl_price = current_price + tight_sl_distance
        
        # All checks passed! ✅
        result["eligible"] = True
        result["entry_price"] = current_price
        result["tight_sl_price"] = tight_sl_price
        result["tight_sl_pips"] = int(tight_sl_distance / pip_size)
        
        # KEY FEATURE: Resume to NEXT level on success
        resume_to_next = hunt_config.get("resume_to_next_level_on_success", True)
        result["resume_to_next_level"] = resume_to_next
        result["current_level"] = chain.current_level
        result["next_level_on_success"] = chain.current_level + 1 if resume_to_next else chain.current_level
        result["reason"] = "✅ Recovery eligible - price recovered, trend aligned"
        
        print(f"✅ SL HUNT RECOVERY READY: {chain.symbol} @ {current_price} (Tight SL: {result['tight_sl_pips']} pips)")
        
        return result
    
    def check_autonomous_tp_continuation(self, chain, current_price: float) -> Dict[str, Any]:
        """
        🚀 NEW: Autonomous TP continuation check WITHOUT waiting for signal
        
        Monitors active chains and checks if TP was hit autonomously:
        1. TP price crossed
        2. 5-second cooldown elapsed
        3. Trend still aligned (TrendAnalyzer)
        4. Max level not exceeded
        
        Returns: {
            "eligible": bool,
            "next_level": int,
            "sl_reduction": float,
            "trend": str,
            "reason": str
        }
        """
        result = {"eligible": False, "reason": ""}
        
        # Get config
        auto_config = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("tp_continuation", {})
        if not auto_config.get("enabled", False):
            result["reason"] = "TP Continuation disabled"
            return result
        
        # Check chain active
        if chain.status != "active":
            result["reason"] = f"Chain status '{chain.status}', not active"
            return result
        
        # Check max levels
        max_levels = auto_config.get("max_levels", 5)
        if chain.current_level >= max_levels:
            result["reason"] = f"Max level {max_levels} reached"
            return result
        
        # Get last TP price from metadata
        last_tp = chain.metadata.get("last_tp_price")
        if not last_tp:
            result["reason"] = "No TP price in metadata"
            return result
        
        # TP hit detection
        tp_hit = False
        if chain.direction == "buy":
            tp_hit = current_price >= last_tp
        else:
            tp_hit = current_price <= last_tp
        
        if not tp_hit:
            result["reason"] = f"TP not hit (Current: {current_price}, TP: {last_tp})"
            return result
        
        # Cooldown check
        last_tp_time = chain.metadata.get("last_tp_time")
        if last_tp_time:
            time_since_tp = (datetime.now() - datetime.fromisoformat(last_tp_time)).total_seconds()
            cooldown = auto_config.get("cooldown_seconds", 5)
            
            if time_since_tp < cooldown:
                result["reason"] = f"Cooldown active ({time_since_tp:.1f}s / {cooldown}s)"
                return result
        
        # Trend alignment check
        if not self.trend_analyzer:
            result["reason"] = "TrendAnalyzer not initialized"
            return result
        
        try:
            trend = self.trend_analyzer.get_current_trend(chain.symbol)
            is_aligned = self.trend_analyzer.is_aligned(chain.direction, trend)
            
            if not is_aligned:
                result["reason"] = f"Trend NOT aligned ({chain.direction} vs {trend})"
                return result
        except Exception as e:
            result["reason"] = f"Trend check error: {str(e)}"
            return result
        
        # All checks passed! ✅
        result["eligible"] = True
        result["next_level"] = chain.current_level + 1
        result["sl_reduction"] = auto_config.get("sl_reduction_per_level", 0.3)
        result["trend"] = trend
        result["reason"] = "✅ TP hit, cooldown complete, trend aligned"
        
        print(f"🚀 AUTONOMOUS TP CONTINUATION: {chain.symbol} Level {chain.current_level} → {result['next_level']}")
        
        return result