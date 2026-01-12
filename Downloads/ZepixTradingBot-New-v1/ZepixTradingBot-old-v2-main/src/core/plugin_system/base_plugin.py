from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class BaseLogicPlugin(ABC):
    """
    Base class for all trading logic plugins.
    
    Plugins must implement:
    - process_entry_signal()
    - process_exit_signal()
    - process_reversal_signal()
    
    Document 07: Phase 5 - Dynamic Config & Per-Plugin Databases
    Added config hot-reload support with on_config_changed() method.
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """
        Initialize plugin instance.
        
        Args:
            plugin_id: Unique identifier for this plugin
            config: Plugin-specific configuration
            service_api: Access to shared services
        """
        self.plugin_id = plugin_id
        self.config = config
        self.service_api = service_api
        self.logger = logging.getLogger(f"plugin.{plugin_id}")
        
        # Plugin metadata
        self.metadata = self._load_metadata()
        
        # Plugin state
        self.enabled = config.get("enabled", True)
        
        # Database connection (plugin-specific)
        self.db_path = f"data/zepix_{plugin_id}.db"
        
        # Config manager reference (set by registry)
        self.config_manager = None
        
        # Configurable parameters (can be hot-reloaded)
        self.max_lot = config.get("max_lot_size", 1.0)
        self.risk_percent = config.get("risk_percent", 1.0)
        
        self.logger.info(f"Initialized plugin: {plugin_id}")
    
    @abstractmethod
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process entry signal and execute trade.
        
        Args:
            alert: Alert data (ZepixV3Alert or similar)
            
        Returns:
            dict: Execution result with trade details
        """
        pass
    
    @abstractmethod
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process exit signal and close trades.
        
        Args:
            alert: Exit alert data
            
        Returns:
            dict: Exit execution result
        """
        pass
    
    @abstractmethod
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process reversal signal (close + opposite entry).
        
        Args:
            alert: Reversal alert data
            
        Returns:
            dict: Reversal execution result
        """
        pass
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "Base plugin",
            "supported_signals": []
        }
    
    def validate_alert(self, alert: Any) -> bool:
        """
        Validate alert before processing.
        
        Override for custom validation logic.
        """
        return True
    
    def get_database_connection(self):
        """Get plugin's isolated database connection"""
        import sqlite3
        return sqlite3.connect(self.db_path)
    
    def enable(self):
        """Enable this plugin"""
        self.enabled = True
        self.logger.info(f"Plugin {self.plugin_id} enabled")
    
    def disable(self):
        """Disable this plugin"""
        self.enabled = False
        self.logger.info(f"Plugin {self.plugin_id} disabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        return {
            "plugin_id": self.plugin_id,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "database": self.db_path
        }
    
    # =========================================================================
    # Document 07: Config Hot-Reload Support
    # =========================================================================
    
    def on_config_changed(self, changes: List[str]) -> None:
        """
        Called when plugin config changes.
        Plugins can override to handle config updates.
        
        Document 07: Phase 5 - Dynamic Config & Per-Plugin Databases
        This method is called by ConfigManager when config file changes.
        
        Args:
            changes: List of changed configuration keys
        """
        self.logger.info(f"Plugin {self.plugin_id} config updated: {changes}")
        
        # Reload plugin-specific config from config manager
        if self.config_manager:
            self.config = self.config_manager.get_plugin_config(self.plugin_id)
        
        # Apply common config changes
        if "max_lot_size" in changes or f"plugins.{self.plugin_id}.max_lot_size" in changes:
            self.max_lot = self.config.get("max_lot_size", 1.0)
            self.logger.info(f"Updated max_lot to {self.max_lot}")
        
        if "risk_percent" in changes or f"plugins.{self.plugin_id}.risk_percent" in changes:
            self.risk_percent = self.config.get("risk_percent", 1.0)
            self.logger.info(f"Updated risk_percent to {self.risk_percent}")
        
        if "enabled" in changes or f"plugins.{self.plugin_id}.enabled" in changes:
            new_enabled = self.config.get("enabled", True)
            if new_enabled and not self.enabled:
                self.on_plugin_enabled()
            elif not new_enabled and self.enabled:
                self.on_plugin_disabled()
            self.enabled = new_enabled
    
    def on_plugin_enabled(self) -> None:
        """
        Called when plugin is enabled via config change.
        Override in subclass for custom enable logic.
        """
        self.logger.info(f"Plugin {self.plugin_id} enabled via config")
    
    def on_plugin_disabled(self) -> None:
        """
        Called when plugin is disabled via config change.
        Override in subclass for custom disable logic.
        """
        self.logger.info(f"Plugin {self.plugin_id} disabled via config")
    
    def set_config_manager(self, config_manager) -> None:
        """
        Set the config manager reference.
        Called by PluginRegistry when registering the plugin.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        
        # Register as observer for config changes
        if config_manager:
            config_manager.register_observer(self._handle_config_change)
    
    def _handle_config_change(self, changes: List[str]) -> None:
        """
        Internal handler for config changes.
        Filters changes relevant to this plugin and calls on_config_changed.
        
        Args:
            changes: List of all changed configuration keys
        """
        # Filter for changes relevant to this plugin
        plugin_prefix = f"plugins.{self.plugin_id}"
        relevant_changes = [c for c in changes if c.startswith(plugin_prefix) or c == "plugins"]
        
        if relevant_changes:
            self.on_config_changed(relevant_changes)
    
    def reload_config(self) -> None:
        """
        Manually reload configuration from config manager.
        Useful for forcing a config refresh.
        """
        if self.config_manager:
            self.config = self.config_manager.get_plugin_config(self.plugin_id)
            self.max_lot = self.config.get("max_lot_size", 1.0)
            self.risk_percent = self.config.get("risk_percent", 1.0)
            self.enabled = self.config.get("enabled", True)
            self.logger.info(f"Plugin {self.plugin_id} config reloaded")
