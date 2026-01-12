from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseLogicPlugin(ABC):
    """
    Base class for all trading logic plugins.
    
    Plugins must implement:
    - process_entry_signal()
    - process_exit_signal()
    - process_reversal_signal()
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
