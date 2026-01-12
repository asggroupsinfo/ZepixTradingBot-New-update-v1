"""
Configuration Validation Schemas for V5 Hybrid Plugin Architecture.

Document 11: Configuration Templates - Validation Schemas
Provides strict validation for all configuration files using dataclasses.

Author: Devin AI
Date: 2026-01-12
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class PluginType(Enum):
    """Plugin type enumeration."""
    V3_COMBINED = "V3_COMBINED"
    V6_PRICE_ACTION = "V6_PRICE_ACTION"


class LogicRoute(Enum):
    """Logic route enumeration for V3."""
    LOGIC1 = "LOGIC1"
    LOGIC2 = "LOGIC2"
    LOGIC3 = "LOGIC3"


class OrderRouting(Enum):
    """Order routing types for V6."""
    ORDER_A_ONLY = "ORDER_A_ONLY"
    ORDER_B_ONLY = "ORDER_B_ONLY"
    DUAL_ORDERS = "DUAL_ORDERS"


class ADXStrength(Enum):
    """ADX strength levels."""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


@dataclass
class PluginSystemConfig:
    """Plugin system configuration."""
    enabled: bool = True
    plugin_directory: str = "src/logic_plugins"
    auto_discover: bool = True
    max_plugin_execution_time: float = 5.0
    dual_core_mode: bool = True
    
    def validate(self) -> bool:
        """Validate plugin system configuration."""
        if self.max_plugin_execution_time <= 0:
            raise ConfigValidationError("max_plugin_execution_time must be positive")
        return True


@dataclass
class PluginConfig:
    """Individual plugin configuration."""
    enabled: bool = True
    shadow_mode: bool = False
    type: str = "V3_COMBINED"
    database: str = ""
    
    def validate(self) -> bool:
        """Validate plugin configuration."""
        valid_types = ["V3_COMBINED", "V6_PRICE_ACTION"]
        if self.type not in valid_types:
            raise ConfigValidationError(f"Invalid plugin type: {self.type}")
        return True


@dataclass
class SymbolConfig:
    """Symbol configuration."""
    symbol_name: str = "XAUUSD"
    digits: int = 2
    pip_value_per_std_lot: float = 1.0
    min_lot: float = 0.01
    max_lot: float = 50.0
    max_spread_pips: float = 3.0
    
    def validate(self) -> bool:
        """Validate symbol configuration."""
        if self.digits < 0 or self.digits > 5:
            raise ConfigValidationError(f"Invalid digits: {self.digits}")
        if self.min_lot <= 0:
            raise ConfigValidationError("min_lot must be positive")
        if self.max_lot <= self.min_lot:
            raise ConfigValidationError("max_lot must be greater than min_lot")
        if self.max_spread_pips < 0:
            raise ConfigValidationError("max_spread_pips cannot be negative")
        return True


@dataclass
class BotConfig:
    """Bot configuration for logic routes."""
    enabled: bool = True
    lot_multiplier: float = 1.0
    risk_per_trade: float = 1.5
    max_daily_trades: int = 10
    logic_route: str = "LOGIC1"
    
    def validate(self) -> bool:
        """Validate bot configuration."""
        if self.lot_multiplier <= 0:
            raise ConfigValidationError("lot_multiplier must be positive")
        if self.risk_per_trade <= 0 or self.risk_per_trade > 10:
            raise ConfigValidationError("risk_per_trade must be between 0 and 10")
        if self.max_daily_trades <= 0:
            raise ConfigValidationError("max_daily_trades must be positive")
        valid_routes = ["LOGIC1", "LOGIC2", "LOGIC3"]
        if self.logic_route not in valid_routes:
            raise ConfigValidationError(f"Invalid logic_route: {self.logic_route}")
        return True


@dataclass
class MainConfig:
    """Main bot configuration schema."""
    telegram_controller_token: str = ""
    telegram_notification_token: str = ""
    telegram_analytics_token: str = ""
    telegram_token: str = ""
    telegram_chat_id: str = ""
    mt5_login: str = ""
    mt5_password: str = ""
    mt5_server: str = "MetaQuotesDemo-MT5"
    mt5_path: str = ""
    plugin_system: Dict[str, Any] = field(default_factory=dict)
    plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    symbol_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    bot_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate main configuration."""
        if not self.telegram_chat_id:
            raise ConfigValidationError("telegram_chat_id is required")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MainConfig':
        """Create MainConfig from dictionary."""
        return cls(
            telegram_controller_token=data.get("telegram_controller_token", ""),
            telegram_notification_token=data.get("telegram_notification_token", ""),
            telegram_analytics_token=data.get("telegram_analytics_token", ""),
            telegram_token=data.get("telegram_token", ""),
            telegram_chat_id=data.get("telegram_chat_id", ""),
            mt5_login=data.get("mt5_login", ""),
            mt5_password=data.get("mt5_password", ""),
            mt5_server=data.get("mt5_server", "MetaQuotesDemo-MT5"),
            mt5_path=data.get("mt5_path", ""),
            plugin_system=data.get("plugin_system", {}),
            plugins=data.get("plugins", {}),
            symbol_config=data.get("symbol_config", {}),
            bot_config=data.get("bot_config", {})
        )


@dataclass
class V3PluginMetadata:
    """V3 plugin metadata."""
    name: str = "V3 Combined Logic"
    description: str = ""
    author: str = "Zepix Team"
    created: str = "2026-01-12"
    category: str = "V3_COMBINED"
    logic_type: str = "LEGACY_V3"
    
    def validate(self) -> bool:
        """Validate metadata."""
        if not self.name:
            raise ConfigValidationError("Plugin name is required")
        return True


@dataclass
class SignalHandlingConfig:
    """Signal handling configuration for V3."""
    entry_signals: List[str] = field(default_factory=lambda: [
        "Institutional_Launchpad",
        "Liquidity_Trap",
        "Momentum_Ignition",
        "Mitigation_Block",
        "Golden_Pocket",
        "Screener",
        "entry_v3"
    ])
    exit_signals: List[str] = field(default_factory=lambda: ["Exit_Bullish", "Exit_Bearish"])
    info_signals: List[str] = field(default_factory=lambda: ["Volatility_Squeeze", "Trend_Pulse"])
    signal_12_enabled: bool = True
    signal_12_name: str = "Sideways_Breakout"
    
    def validate(self) -> bool:
        """Validate signal handling configuration."""
        if not self.entry_signals:
            raise ConfigValidationError("At least one entry signal is required")
        return True


@dataclass
class RoutingMatrixConfig:
    """Routing matrix configuration for V3."""
    priority_1_overrides: Dict[str, str] = field(default_factory=lambda: {
        "Screener": "LOGIC3",
        "Golden_Pocket_1H": "LOGIC3",
        "Golden_Pocket_4H": "LOGIC3"
    })
    priority_2_timeframe_routing: Dict[str, str] = field(default_factory=lambda: {
        "5": "LOGIC1",
        "15": "LOGIC2",
        "60": "LOGIC3",
        "240": "LOGIC3"
    })
    logic_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "LOGIC1": 1.25,
        "LOGIC2": 1.0,
        "LOGIC3": 0.625
    })
    
    def validate(self) -> bool:
        """Validate routing matrix."""
        for route, multiplier in self.logic_multipliers.items():
            if multiplier <= 0:
                raise ConfigValidationError(f"Invalid multiplier for {route}")
        return True


@dataclass
class OrderASettings:
    """Order A settings for V3 dual order system."""
    use_v3_smart_sl: bool = True
    target_level: str = "TP2"
    trailing_enabled: bool = True


@dataclass
class OrderBSettings:
    """Order B settings for V3 dual order system."""
    use_fixed_sl: bool = True
    fixed_sl_dollars: float = 10.0
    target_level: str = "TP1"
    trailing_enabled: bool = False
    
    def validate(self) -> bool:
        """Validate Order B settings."""
        if self.fixed_sl_dollars <= 0:
            raise ConfigValidationError("fixed_sl_dollars must be positive")
        return True


@dataclass
class DualOrderSystemConfig:
    """Dual order system configuration for V3."""
    enabled: bool = True
    order_split_ratio: float = 0.5
    order_a_settings: Dict[str, Any] = field(default_factory=dict)
    order_b_settings: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate dual order system configuration."""
        if self.order_split_ratio <= 0 or self.order_split_ratio > 1:
            raise ConfigValidationError("order_split_ratio must be between 0 and 1")
        return True


@dataclass
class MTF4PillarConfig:
    """MTF 4-pillar system configuration for V3."""
    enabled: bool = True
    pillars: List[str] = field(default_factory=lambda: ["15m", "1h", "4h", "1d"])
    extraction_indices: List[int] = field(default_factory=lambda: [2, 3, 4, 5])
    ignore_indices: List[int] = field(default_factory=lambda: [0, 1])
    min_aligned_for_entry: int = 3
    alignment_weight: Dict[str, float] = field(default_factory=lambda: {
        "15m": 1.0,
        "1h": 1.5,
        "4h": 2.0,
        "1d": 2.5
    })
    
    def validate(self) -> bool:
        """Validate MTF 4-pillar configuration."""
        if len(self.pillars) != 4:
            raise ConfigValidationError("MTF system requires exactly 4 pillars")
        if self.min_aligned_for_entry < 1 or self.min_aligned_for_entry > 4:
            raise ConfigValidationError("min_aligned_for_entry must be between 1 and 4")
        return True


@dataclass
class PositionSizingConfig:
    """Position sizing configuration."""
    base_risk_percentage: float = 1.5
    consensus_score_range: List[int] = field(default_factory=lambda: [0, 9])
    consensus_multiplier_range: List[float] = field(default_factory=lambda: [0.2, 1.0])
    apply_logic_multiplier: bool = True
    min_lot_size: float = 0.01
    max_lot_size: float = 1.0
    
    def validate(self) -> bool:
        """Validate position sizing configuration."""
        if self.base_risk_percentage <= 0 or self.base_risk_percentage > 10:
            raise ConfigValidationError("base_risk_percentage must be between 0 and 10")
        if self.min_lot_size <= 0:
            raise ConfigValidationError("min_lot_size must be positive")
        if self.max_lot_size <= self.min_lot_size:
            raise ConfigValidationError("max_lot_size must be greater than min_lot_size")
        return True


@dataclass
class TrendBypassConfig:
    """Trend bypass logic configuration for V3."""
    enabled: bool = True
    bypass_signals: List[str] = field(default_factory=lambda: ["entry_v3"])
    require_trend_signals: List[str] = field(default_factory=lambda: [
        "Institutional_Launchpad",
        "Liquidity_Trap",
        "Momentum_Ignition"
    ])


@dataclass
class RiskManagementConfig:
    """Risk management configuration."""
    max_open_trades: int = 5
    max_daily_trades: int = 10
    max_symbol_exposure: float = 0.30
    daily_loss_limit: float = 500.0
    risk_multiplier: float = 1.0
    base_risk_percentage: float = 1.5
    max_lot_size: float = 1.0
    
    def validate(self) -> bool:
        """Validate risk management configuration."""
        if self.max_open_trades <= 0:
            raise ConfigValidationError("max_open_trades must be positive")
        if self.max_daily_trades <= 0:
            raise ConfigValidationError("max_daily_trades must be positive")
        if self.daily_loss_limit <= 0:
            raise ConfigValidationError("daily_loss_limit must be positive")
        if self.max_symbol_exposure <= 0 or self.max_symbol_exposure > 1:
            raise ConfigValidationError("max_symbol_exposure must be between 0 and 1")
        return True


@dataclass
class NotificationsConfig:
    """Notifications configuration."""
    notify_on_entry: bool = True
    notify_on_exit: bool = True
    notify_on_routing: bool = True
    notify_on_error: bool = True
    use_voice_alerts: bool = False
    telegram_bot: str = "controller"
    
    def validate(self) -> bool:
        """Validate notifications configuration."""
        valid_bots = ["controller", "notification", "analytics"]
        if self.telegram_bot not in valid_bots:
            raise ConfigValidationError(f"Invalid telegram_bot: {self.telegram_bot}")
        return True


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: str = ""
    table_name: str = ""
    backup_enabled: bool = True
    backup_frequency: str = "daily"
    sync_to_central: bool = True
    sync_interval_minutes: int = 5
    
    def validate(self) -> bool:
        """Validate database configuration."""
        if not self.path:
            raise ConfigValidationError("Database path is required")
        if self.sync_interval_minutes <= 0:
            raise ConfigValidationError("sync_interval_minutes must be positive")
        return True


@dataclass
class V3PluginSettings:
    """V3 plugin settings."""
    supported_symbols: List[str] = field(default_factory=lambda: ["XAUUSD"])
    supported_timeframes: List[str] = field(default_factory=lambda: ["5", "15", "60", "240"])
    max_lot_size: float = 1.0
    daily_loss_limit: float = 500.0
    signal_handling: Dict[str, Any] = field(default_factory=dict)
    routing_matrix: Dict[str, Any] = field(default_factory=dict)
    dual_order_system: Dict[str, Any] = field(default_factory=dict)
    mtf_4_pillar_system: Dict[str, Any] = field(default_factory=dict)
    position_sizing: Dict[str, Any] = field(default_factory=dict)
    trend_bypass_logic: Dict[str, Any] = field(default_factory=dict)
    risk_management: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate V3 plugin settings."""
        if not self.supported_symbols:
            raise ConfigValidationError("At least one supported symbol is required")
        if self.max_lot_size <= 0:
            raise ConfigValidationError("max_lot_size must be positive")
        return True


@dataclass
class V3PluginConfig:
    """V3 Combined Logic plugin configuration schema."""
    plugin_id: str = "combined_v3"
    version: str = "1.0.0"
    enabled: bool = True
    shadow_mode: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    database: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate V3 plugin configuration."""
        if not self.plugin_id:
            raise ConfigValidationError("plugin_id is required")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'V3PluginConfig':
        """Create V3PluginConfig from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", "combined_v3"),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            shadow_mode=data.get("shadow_mode", False),
            metadata=data.get("metadata", {}),
            settings=data.get("settings", {}),
            notifications=data.get("notifications", {}),
            database=data.get("database", {})
        )


@dataclass
class V6EntryConditions:
    """V6 entry conditions configuration."""
    adx_threshold: int = 20
    adx_strength_required: str = "MODERATE"
    confidence_threshold: int = 70
    max_spread_pips: float = 2.0
    require_market_state_alignment: bool = True
    require_15m_alignment: bool = False
    require_momentum_increasing: bool = False
    require_market_state_match: bool = False
    require_pulse_alignment: bool = True
    require_4h_alignment: bool = False
    require_1d_alignment: bool = False
    higher_tf_weight: float = 1.0
    
    def validate(self) -> bool:
        """Validate entry conditions."""
        if self.adx_threshold < 0 or self.adx_threshold > 100:
            raise ConfigValidationError("adx_threshold must be between 0 and 100")
        if self.confidence_threshold < 0 or self.confidence_threshold > 100:
            raise ConfigValidationError("confidence_threshold must be between 0 and 100")
        valid_strengths = ["WEAK", "MODERATE", "STRONG", "VERY_STRONG"]
        if self.adx_strength_required not in valid_strengths:
            raise ConfigValidationError(f"Invalid adx_strength_required: {self.adx_strength_required}")
        return True


@dataclass
class V6OrderConfiguration:
    """V6 order configuration."""
    use_order_a: bool = True
    use_order_b: bool = False
    target_level: str = "TP2"
    split_ratio: float = 0.5
    order_a_target: str = "TP2"
    order_b_target: str = "TP1"
    same_sl_for_both: bool = True
    quick_exit_enabled: bool = False
    extended_tp_enabled: bool = False
    
    def validate(self) -> bool:
        """Validate order configuration."""
        if self.split_ratio <= 0 or self.split_ratio > 1:
            raise ConfigValidationError("split_ratio must be between 0 and 1")
        valid_targets = ["TP1", "TP2", "TP3"]
        if self.target_level not in valid_targets:
            raise ConfigValidationError(f"Invalid target_level: {self.target_level}")
        return True


@dataclass
class TrendPulseIntegration:
    """Trend Pulse integration configuration for V6."""
    enabled: bool = True
    require_pulse_alignment: bool = True
    min_bull_count_for_buy: int = 3
    min_bear_count_for_sell: int = 3
    check_bull_bear_ratio: bool = False
    use_traditional_tf_trends: bool = False
    
    def validate(self) -> bool:
        """Validate Trend Pulse integration."""
        if self.min_bull_count_for_buy < 0 or self.min_bull_count_for_buy > 10:
            raise ConfigValidationError("min_bull_count_for_buy must be between 0 and 10")
        if self.min_bear_count_for_sell < 0 or self.min_bear_count_for_sell > 10:
            raise ConfigValidationError("min_bear_count_for_sell must be between 0 and 10")
        return True


@dataclass
class V6ExitRules:
    """V6 exit rules configuration."""
    tp1_pips: int = 10
    tp2_pips: int = 30
    sl_pips: int = 15
    use_trailing_stop: bool = False
    max_hold_time_minutes: int = 60
    move_to_breakeven_after_tp1: bool = False
    breakeven_buffer_pips: float = 2.0
    
    def validate(self) -> bool:
        """Validate exit rules."""
        if self.tp1_pips <= 0:
            raise ConfigValidationError("tp1_pips must be positive")
        if self.sl_pips <= 0:
            raise ConfigValidationError("sl_pips must be positive")
        if self.max_hold_time_minutes <= 0:
            raise ConfigValidationError("max_hold_time_minutes must be positive")
        return True


@dataclass
class V6PluginMetadata:
    """V6 plugin metadata."""
    name: str = ""
    description: str = ""
    author: str = "Zepix Team"
    created: str = "2026-01-12"
    category: str = "V6_PRICE_ACTION"
    timeframe: str = ""
    
    def validate(self) -> bool:
        """Validate metadata."""
        if not self.name:
            raise ConfigValidationError("Plugin name is required")
        return True


@dataclass
class V6PluginSettings:
    """V6 plugin settings."""
    supported_symbols: List[str] = field(default_factory=lambda: ["XAUUSD"])
    supported_timeframes: List[str] = field(default_factory=list)
    order_routing: str = "ORDER_A_ONLY"
    entry_conditions: Dict[str, Any] = field(default_factory=dict)
    order_configuration: Dict[str, Any] = field(default_factory=dict)
    risk_management: Dict[str, Any] = field(default_factory=dict)
    trend_pulse_integration: Dict[str, Any] = field(default_factory=dict)
    exit_rules: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate V6 plugin settings."""
        valid_routings = ["ORDER_A_ONLY", "ORDER_B_ONLY", "DUAL_ORDERS"]
        if self.order_routing not in valid_routings:
            raise ConfigValidationError(f"Invalid order_routing: {self.order_routing}")
        return True


@dataclass
class V6PluginConfig:
    """V6 Price Action plugin configuration schema."""
    plugin_id: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    shadow_mode: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    database: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate V6 plugin configuration."""
        if not self.plugin_id:
            raise ConfigValidationError("plugin_id is required")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'V6PluginConfig':
        """Create V6PluginConfig from dictionary."""
        return cls(
            plugin_id=data.get("plugin_id", ""),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            shadow_mode=data.get("shadow_mode", False),
            metadata=data.get("metadata", {}),
            settings=data.get("settings", {}),
            notifications=data.get("notifications", {}),
            database=data.get("database", {})
        )


@dataclass
class ShadowModeSettings:
    """Shadow mode settings for testing plugins."""
    log_all_signals: bool = True
    simulate_order_placement: bool = True
    track_hypothetical_pnl: bool = True
    shadow_duration_hours: int = 72
    
    def validate(self) -> bool:
        """Validate shadow mode settings."""
        if self.shadow_duration_hours <= 0:
            raise ConfigValidationError("shadow_duration_hours must be positive")
        return True


@dataclass
class EnvironmentConfig:
    """Environment configuration from .env file."""
    telegram_controller_token: str = ""
    telegram_notification_token: str = ""
    telegram_analytics_token: str = ""
    telegram_main_token: str = ""
    mt5_password: str = ""
    db_encryption_key: str = ""
    admin_chat_id: str = ""
    admin_password: str = ""
    environment: str = "development"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'EnvironmentConfig':
        """Load configuration from environment variables."""
        return cls(
            telegram_controller_token=os.environ.get("TELEGRAM_CONTROLLER_TOKEN", ""),
            telegram_notification_token=os.environ.get("TELEGRAM_NOTIFICATION_TOKEN", ""),
            telegram_analytics_token=os.environ.get("TELEGRAM_ANALYTICS_TOKEN", ""),
            telegram_main_token=os.environ.get("TELEGRAM_MAIN_TOKEN", ""),
            mt5_password=os.environ.get("MT5_PASSWORD", ""),
            db_encryption_key=os.environ.get("DB_ENCRYPTION_KEY", ""),
            admin_chat_id=os.environ.get("ADMIN_CHAT_ID", ""),
            admin_password=os.environ.get("ADMIN_PASSWORD", ""),
            environment=os.environ.get("ENVIRONMENT", "development"),
            debug_mode=os.environ.get("DEBUG_MODE", "false").lower() == "true",
            log_level=os.environ.get("LOG_LEVEL", "INFO")
        )
    
    def validate(self) -> bool:
        """Validate environment configuration."""
        valid_environments = ["development", "staging", "production"]
        if self.environment not in valid_environments:
            raise ConfigValidationError(f"Invalid environment: {self.environment}")
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ConfigValidationError(f"Invalid log_level: {self.log_level}")
        return True


class ConfigValidator:
    """Configuration validator utility class."""
    
    @staticmethod
    def validate_main_config(config: Dict[str, Any]) -> bool:
        """Validate main configuration dictionary."""
        main = MainConfig.from_dict(config)
        main.validate()
        
        if "plugin_system" in config:
            ps = PluginSystemConfig(**config["plugin_system"])
            ps.validate()
        
        if "plugins" in config:
            for name, plugin_config in config["plugins"].items():
                pc = PluginConfig(**plugin_config)
                pc.validate()
        
        if "symbol_config" in config:
            for symbol, sym_config in config["symbol_config"].items():
                sc = SymbolConfig(**sym_config)
                sc.validate()
        
        if "bot_config" in config:
            for bot, bot_cfg in config["bot_config"].items():
                bc = BotConfig(**bot_cfg)
                bc.validate()
        
        return True
    
    @staticmethod
    def validate_v3_config(config: Dict[str, Any]) -> bool:
        """Validate V3 plugin configuration dictionary."""
        v3 = V3PluginConfig.from_dict(config)
        v3.validate()
        
        if "settings" in config:
            settings = config["settings"]
            
            if "signal_handling" in settings:
                sh = SignalHandlingConfig(**settings["signal_handling"])
                sh.validate()
            
            if "routing_matrix" in settings:
                rm = RoutingMatrixConfig(**settings["routing_matrix"])
                rm.validate()
            
            if "dual_order_system" in settings:
                dos = DualOrderSystemConfig(**settings["dual_order_system"])
                dos.validate()
            
            if "mtf_4_pillar_system" in settings:
                mtf = MTF4PillarConfig(**settings["mtf_4_pillar_system"])
                mtf.validate()
            
            if "position_sizing" in settings:
                ps = PositionSizingConfig(**settings["position_sizing"])
                ps.validate()
            
            if "risk_management" in settings:
                rm = RiskManagementConfig(**settings["risk_management"])
                rm.validate()
        
        if "notifications" in config:
            nc = NotificationsConfig(**config["notifications"])
            nc.validate()
        
        if "database" in config:
            db = DatabaseConfig(**config["database"])
            db.validate()
        
        return True
    
    @staticmethod
    def validate_v6_config(config: Dict[str, Any]) -> bool:
        """Validate V6 plugin configuration dictionary."""
        v6 = V6PluginConfig.from_dict(config)
        v6.validate()
        
        if "settings" in config:
            settings = config["settings"]
            
            valid_routings = ["ORDER_A_ONLY", "ORDER_B_ONLY", "DUAL_ORDERS"]
            if "order_routing" in settings:
                if settings["order_routing"] not in valid_routings:
                    raise ConfigValidationError(f"Invalid order_routing: {settings['order_routing']}")
            
            if "entry_conditions" in settings:
                ec = V6EntryConditions(**settings["entry_conditions"])
                ec.validate()
            
            if "order_configuration" in settings:
                oc = V6OrderConfiguration(**settings["order_configuration"])
                oc.validate()
            
            if "risk_management" in settings:
                rm = RiskManagementConfig(**settings["risk_management"])
                rm.validate()
            
            if "trend_pulse_integration" in settings:
                tpi = TrendPulseIntegration(**settings["trend_pulse_integration"])
                tpi.validate()
            
            if "exit_rules" in settings:
                er = V6ExitRules(**settings["exit_rules"])
                er.validate()
        
        if "database" in config:
            db = DatabaseConfig(**config["database"])
            db.validate()
        
        return True
    
    @staticmethod
    def load_and_validate_json(file_path: str, config_type: str = "main") -> Dict[str, Any]:
        """Load JSON file and validate based on type."""
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        if config_type == "main":
            ConfigValidator.validate_main_config(config)
        elif config_type == "v3":
            ConfigValidator.validate_v3_config(config)
        elif config_type == "v6":
            ConfigValidator.validate_v6_config(config)
        else:
            raise ConfigValidationError(f"Unknown config type: {config_type}")
        
        return config
