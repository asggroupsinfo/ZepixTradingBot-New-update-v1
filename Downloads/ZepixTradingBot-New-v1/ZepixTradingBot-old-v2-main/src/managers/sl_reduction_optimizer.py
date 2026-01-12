"""
SL Reduction Optimizer - Dynamic Stop Loss Management
Optimizes SL reduction percentages across TP Continuation levels
"""

from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SLReductionOptimizer:
    """
    Manages SL reduction strategies for TP Continuation re-entries
    
    Features:
    - 4 strategies (Aggressive, Balanced, Conservative, Adaptive)
    - Symbol-specific optimization (Adaptive mode)
    - Dynamic SL calculation per level
    - Real-time configuration updates
    """
    
    # Strategy Configurations
    STRATEGIES = {
        "AGGRESSIVE": {
            "reduction_percent": 40,
            "description": "Tight stops, trending markets",
            "emoji": "⚡",
            "best_for": "Strong momentum, clear trends"
        },
        "BALANCED": {
            "reduction_percent": 30,
            "description": "Recommended for most conditions",
            "emoji": "⚖️",
            "best_for": "Mixed market conditions"
        },
        "CONSERVATIVE": {
            "reduction_percent": 20,
            "description": "Wide stops, choppy markets",
            "emoji": "🛡️",
            "best_for": "Ranging, uncertain conditions"
        },
        "ADAPTIVE": {
            "description": "Symbol-specific optimization",
            "emoji": "🎯",
            "best_for": "Optimized for each symbol's characteristics",
            "symbol_settings": {
                "XAUUSD": {"reduction_percent": 35, "reason": "Gold volatile but trending"},
                "EURUSD": {"reduction_percent": 25, "reason": "Forex stable, needs room"},
                "GBPJPY": {"reduction_percent": 38, "reason": "High volatility pair"},
                "BTCUSD": {"reduction_percent": 40, "reason": "Crypto fast moves"},
                "USDJPY": {"reduction_percent": 22, "reason": "Stable major pair"},
                "AUDUSD": {"reduction_percent": 28, "reason": "Commodity currency"},
                "NZDUSD": {"reduction_percent": 28, "reason": "Similar to AUD"},
                "USDCAD": {"reduction_percent": 26, "reason": "Oil-correlated"},
                "XAGUSD": {"reduction_percent": 36, "reason": "Silver volatile"},
                "GBPUSD": {"reduction_percent": 32, "reason": "Cable active"},
                "EURGBP": {"reduction_percent": 27, "reason": "EUR cross stable"},
                "EURJPY": {"reduction_percent": 30, "reason": "EUR cross moderate"},
                "AUDJPY": {"reduction_percent": 33, "reason": "Volatile commodity pair"},
                "NZDJPY": {"reduction_percent": 33, "reason": "Similar to AUDJPY"},
                "USDCHF": {"reduction_percent": 24, "reason": "Swissy stable"},
                "EURCHF": {"reduction_percent": 22, "reason": "Very stable pair"},
                "GBPAUD": {"reduction_percent": 31, "reason": "Moderate cross"},
                "GBPNZD": {"reduction_percent": 31, "reason": "Moderate cross"},
                "AUDCAD": {"reduction_percent": 27, "reason": "Lower volatility"},
                "AUDNZD": {"reduction_percent": 23, "reason": "Range-bound"},
            },
            "default_percent": 30
        }
    }
    
    # Minimum SL constraint (pips)
    MIN_SL_PIPS = 10
    
    def __init__(self, config_manager):
        """
        Initialize SL Reduction Optimizer
        
        Args:
            config_manager: Reference to configuration manager
        """
        self.config = config_manager
        self.load_settings()
        
        logger.info("✅ SLReductionOptimizer initialized")
    
    def load_settings(self) -> None:
        """Load current SL reduction settings from config"""
        
        sl_config = self.config.get("sl_reduction_optimization", {})
        
        self.enabled = sl_config.get("enabled", True)
        self.current_strategy = sl_config.get("current_strategy", "BALANCED")
        
        # Validate current strategy
        if self.current_strategy not in self.STRATEGIES:
            logger.warning(f"Invalid strategy '{self.current_strategy}', defaulting to BALANCED")
            self.current_strategy = "BALANCED"
        
        strategy_info = self.STRATEGIES[self.current_strategy]
        
        if self.current_strategy == "ADAPTIVE":
            logger.info(f"""
SL Reduction Settings Loaded:
├─ Enabled: {self.enabled}
├─ Strategy: {strategy_info['emoji']} {self.current_strategy}
├─ Default: {strategy_info.get('default_percent', 30)}%
└─ Symbols: {len(strategy_info.get('symbol_settings', {}))} configured
            """)
        else:
            logger.info(f"""
SL Reduction Settings Loaded:
├─ Enabled: {self.enabled}
├─ Strategy: {strategy_info['emoji']} {self.current_strategy}
├─ Reduction: {strategy_info['reduction_percent']}%
└─ Description: {strategy_info['description']}
            """)
    
    def calculate_next_level_sl(
        self,
        symbol: str,
        current_level: int,
        base_sl_pips: float
    ) -> float:
        """
        Calculate SL pips for next TP Continuation level
        
        Args:
            symbol: Trading symbol
            current_level: Current chain level (1-5)
            base_sl_pips: Base SL in pips (Level 1SL)
        
        Returns:
            float: SL pips for next level
        """
        
        if not self.enabled:
            logger.debug("SL Reduction disabled, using base SL")
            return base_sl_pips
        
        next_level = current_level + 1
        
        # Maximum level constraint
        if next_level > 5:
            min_sl = base_sl_pips * 0.2  # Minimum 20% for level 6+
            logger.debug(f"Level {next_level} exceeds max, using minimum: {min_sl:.1f} pips")
            return max(min_sl, self.MIN_SL_PIPS)
        
        # Get reduction percentage
        strategy = self.STRATEGIES.get(self.current_strategy)
        
        if self.current_strategy == "ADAPTIVE":
            reduction_percent = self._get_adaptive_reduction(symbol)
        else:
            reduction_percent = strategy.get("reduction_percent", 30)
        
        # Calculate progressive reduction
        reduction_factor = 1.0 - (reduction_percent / 100.0)
        
        next_sl_pips = base_sl_pips
        for level in range(2, next_level + 1):
            next_sl_pips = next_sl_pips * reduction_factor
        
        # Apply minimum SL constraint
        next_sl_pips = max(next_sl_pips, self.MIN_SL_PIPS)
        
        logger.debug(f"""
SL Calculation for Next Level:
├─ Symbol: {symbol}
├─ Current Level: {current_level}
├─ Next Level: {next_level}
├─ Base SL: {base_sl_pips} pips
├─ Strategy: {self.current_strategy}
├─ Reduction: {reduction_percent}%
└─ Next SL: {next_sl_pips:.1f} pips
        """)
        
        return next_sl_pips
    
    def get_level_progression(
        self,
        symbol: str,
        base_sl_pips: float,
        max_level: int = 5
    ) -> Dict[int, float]:
        """
        Get SL progression for all levels
        
        Args:
            symbol: Trading symbol
            base_sl_pips: Base SL for level 1
            max_level: Maximum level to calculate
        
        Returns:
            Dict[int, float]: Level to SL pips mapping
        """
        
        progression = {1: base_sl_pips}
        
        for level in range(1, max_level):
            next_sl = self.calculate_next_level_sl(symbol, level, base_sl_pips)
            progression[level + 1] = next_sl
        
        return progression
    
    def _get_adaptive_reduction(self, symbol: str) -> float:
        """
        Get symbol-specific reduction percentage for Adaptive strategy
        
        Args:
            symbol: Trading symbol
        
        Returns:
            float: Reduction percentage for symbol
        """
        
        strategy = self.STRATEGIES.get("ADAPTIVE", {})
        symbol_settings = strategy.get("symbol_settings", {})
        
        if symbol in symbol_settings:
            percent = symbol_settings[symbol]["reduction_percent"]
            logger.debug(f"Adaptive reduction for {symbol}: {percent}%")
            return percent
        else:
            default = strategy.get("default_percent", 30)
            logger.debug(f"Using default reduction for {symbol}: {default}%")
            return default
    
    def switch_strategy(self, new_strategy: str) -> bool:
        """
        Switch to a different SL reduction strategy
        
        Args:
            new_strategy: Strategy name
        
        Returns:
            bool: True if successful
        """
        
        new_strategy = new_strategy.upper()
        
        if new_strategy not in self.STRATEGIES:
            logger.error(f"Invalid strategy: {new_strategy}. Valid: {list(self.STRATEGIES.keys())}")
            return False
        
        old_strategy = self.current_strategy
        old_info = self.STRATEGIES[old_strategy]
        new_info = self.STRATEGIES[new_strategy]
        
        # Update strategy
        self.current_strategy = new_strategy
        
        # Save to config
        self.config.update("sl_reduction_optimization.current_strategy", new_strategy)
        
        logger.info(f"""
🔄 SL REDUCTION STRATEGY CHANGED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Old Strategy: {old_info.get('emoji', '')} {old_strategy}
New Strategy: {new_info.get('emoji', '')} {new_strategy}
Description: {new_info.get('description', '')}
Best For: {new_info.get('best_for', '')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        
        return True
    
    def update_adaptive_symbol(self, symbol: str, reduction_percent: float) -> bool:
        """
        Update reduction percentage for a specific symbol in Adaptive mode
        
        Args:
            symbol: Trading symbol
            reduction_percent: New reduction percentage (10-50%)
        
        Returns:
            bool: True if successful
        """
        
        if self.current_strategy != "ADAPTIVE":
            logger.warning(f"Not in ADAPTIVE mode (current: {self.current_strategy}), update skipped")
            return False
        
        # Validate range
        if not (10 <= reduction_percent <= 50):
            logger.error(f"Invalid reduction percent: {reduction_percent}%. Must be 10-50%")
            return False
        
        # Get current value for logging
        strategy = self.STRATEGIES["ADAPTIVE"]
        symbol_settings = strategy.get("symbol_settings", {})
        old_percent = symbol_settings.get(symbol, {}).get("reduction_percent", strategy.get("default_percent", 30))
        
        # Update in-memory
        if symbol not in symbol_settings:
            symbol_settings[symbol] = {"reduction_percent": reduction_percent, "reason": "Custom"}
        else:
            symbol_settings[symbol]["reduction_percent"] = reduction_percent
        
        # Update config
        path = f"sl_reduction_optimization.strategies.ADAPTIVE.symbol_settings.{symbol}.reduction_percent"
        self.config.update(path, reduction_percent)
        
        logger.info(f"""
✅ SYMBOL REDUCTION UPDATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symbol: {symbol}
Old: {old_percent}%
New: {reduction_percent}%
Change: {reduction_percent - old_percent:+.0f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        
        return True
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current SL reduction settings for display
        
        Returns:
            Dict: Current settings
        """
        
        strategy_info = self.STRATEGIES.get(self.current_strategy, self.STRATEGIES["BALANCED"])
        
        settings = {
            "enabled": self.enabled,
            "strategy": self.current_strategy,
            "emoji": strategy_info.get("emoji", ""),
            "description": strategy_info.get("description", ""),
            "best_for": strategy_info.get("best_for", "")
        }
        
        if self.current_strategy == "ADAPTIVE":
            settings["symbol_settings"] = strategy_info.get("symbol_settings", {})
            settings["default_percent"] = strategy_info.get("default_percent", 30)
        else:
            settings["reduction_percent"] = strategy_info.get("reduction_percent", 30)
        
        settings["all_strategies"] = self.STRATEGIES
        
        return settings
    
    def get_strategy_info(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific strategy
        
        Args:
            strategy_name: Strategy name
        
        Returns:
            Optional[Dict]: Strategy settings or None if invalid
        """
        
        return self.STRATEGIES.get(strategy_name.upper())
    
    def toggle_enabled(self) -> bool:
        """
        Toggle SL reduction optimization on/off
        
        Returns:
            bool: New status (True = enabled, False = disabled)
        """
        
        self.enabled = not self.enabled
        self.config.update("sl_reduction_optimization.enabled", self.enabled)
        
        status = "ENABLED ✅" if self.enabled else "DISABLED ❌"
        logger.info(f"SL Reduction Optimization: {status}")
        
        return self.enabled
    
    def get_status_summary(self) -> str:
        """
        Get formatted status summary
        
        Returns:
            str: Status summary string
        """
        
        strategy_info = self.STRATEGIES[self.current_strategy]
        
        if self.current_strategy == "ADAPTIVE":
            detail = f"Default: {strategy_info.get('default_percent', 30)}%"
        else:
            detail = f"Reduction: {strategy_info['reduction_percent']}%"
        
        status = f"""
📉 SL REDUCTION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enabled: {'YES ✅' if self.enabled else 'NO ❌'}
Strategy: {strategy_info['emoji']} {self.current_strategy}
{detail}
Description: {strategy_info['description']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        return status
