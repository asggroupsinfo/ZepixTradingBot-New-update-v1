"""
Configuration Package for V5 Hybrid Plugin Architecture.

Document 11: Configuration Templates
Provides configuration schemas, defaults management, and environment variable support.

Author: Devin AI
Date: 2026-01-12
"""

from .schemas import (
    ConfigValidationError,
    PluginType,
    LogicRoute,
    OrderRouting,
    ADXStrength,
    PluginSystemConfig,
    PluginConfig,
    SymbolConfig,
    BotConfig,
    MainConfig,
    V3PluginMetadata,
    SignalHandlingConfig,
    RoutingMatrixConfig,
    OrderASettings,
    OrderBSettings,
    DualOrderSystemConfig,
    MTF4PillarConfig,
    PositionSizingConfig,
    TrendBypassConfig,
    RiskManagementConfig,
    NotificationsConfig,
    DatabaseConfig,
    V3PluginSettings,
    V3PluginConfig,
    V6EntryConditions,
    V6OrderConfiguration,
    TrendPulseIntegration,
    V6ExitRules,
    V6PluginMetadata,
    V6PluginSettings,
    V6PluginConfig,
    ShadowModeSettings,
    EnvironmentConfig,
    ConfigValidator
)

from .defaults import (
    DefaultsManager,
    EnvironmentVariableResolver,
    ConfigLoader,
    generate_env_template,
    generate_gitignore_additions
)

__all__ = [
    'ConfigValidationError',
    'PluginType',
    'LogicRoute',
    'OrderRouting',
    'ADXStrength',
    'PluginSystemConfig',
    'PluginConfig',
    'SymbolConfig',
    'BotConfig',
    'MainConfig',
    'V3PluginMetadata',
    'SignalHandlingConfig',
    'RoutingMatrixConfig',
    'OrderASettings',
    'OrderBSettings',
    'DualOrderSystemConfig',
    'MTF4PillarConfig',
    'PositionSizingConfig',
    'TrendBypassConfig',
    'RiskManagementConfig',
    'NotificationsConfig',
    'DatabaseConfig',
    'V3PluginSettings',
    'V3PluginConfig',
    'V6EntryConditions',
    'V6OrderConfiguration',
    'TrendPulseIntegration',
    'V6ExitRules',
    'V6PluginMetadata',
    'V6PluginSettings',
    'V6PluginConfig',
    'ShadowModeSettings',
    'EnvironmentConfig',
    'ConfigValidator',
    'DefaultsManager',
    'EnvironmentVariableResolver',
    'ConfigLoader',
    'generate_env_template',
    'generate_gitignore_additions'
]
