from src.core.plugin_system import BaseLogicPlugin
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TemplatePlugin(BaseLogicPlugin):
    """
    Template plugin - copy this to create new plugins.
    
    Steps to create a new plugin:
    1. Copy this template directory
    2. Rename to your plugin ID (e.g., `my_logic`)
    3. Update class name (e.g., `MyLogicPlugin`)
    4. Implement process_entry_signal, process_exit_signal, process_reversal_signal
    5. Update config.json with your plugin settings
    6. Register plugin in main config
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        super().__init__(plugin_id, config, service_api)
        
        # Plugin-specific initialization
        self.logger.info(f"Template Plugin '{plugin_id}' initialized")
    
    async def process_entry_signal(self, alert) -> Dict[str, Any]:
        """
        Process entry signal.
        
        Example implementation:
        1. Validate alert
        2. Calculate lot size using service_api.risk_management
        3. Place order using service_api.order_execution
        4. Record trade in database
        5. Send notification using service_api.telegram
        """
        self.logger.info(f"Processing entry signal for {getattr(alert, 'symbol', 'UNKNOWN')}")
        
        # TODO: Implement your entry logic
        
        return {
            "success": True,
            "message": "Entry processed (template)",
            "plugin_id": self.plugin_id
        }
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        """Process exit signal"""
        self.logger.info(f"Processing exit signal for {getattr(alert, 'symbol', 'UNKNOWN')}")
        
        # TODO: Implement your exit logic
        
        return {
            "success": True,
            "message": "Exit processed (template)",
            "plugin_id": self.plugin_id
        }
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        """Process reversal signal"""
        self.logger.info(f"Processing reversal signal for {getattr(alert, 'symbol', 'UNKNOWN')}")
        
        # TODO: Implement your reversal logic
        
        return {
            "success": True,
            "message": "Reversal processed (template)",
            "plugin_id": self.plugin_id
        }
