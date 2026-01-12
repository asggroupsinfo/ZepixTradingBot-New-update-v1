import importlib
import asyncio
import os
from typing import Dict, Optional, List, Any
import logging

from .base_plugin import BaseLogicPlugin

logger = logging.getLogger(__name__)

class PluginRegistry:
    """
    Central registry for all trading logic plugins.
    
    Responsibilities:
    - Discover plugins from plugin directory
    - Load and initialize plugins
    - Route alerts to correct plugin
    - Manage plugin lifecycle
    """
    
    def __init__(self, config: Dict, service_api):
        """
        Initialize plugin registry.
        
        Args:
            config: Bot configuration
            service_api: Shared services API
        """
        self.config = config
        self.service_api = service_api
        self.plugins: Dict[str, BaseLogicPlugin] = {}
        
        self.plugin_dir = config.get("plugin_system", {}).get("plugin_dir", "src/logic_plugins")
        
        logger.info("Plugin registry initialized")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directory.
        
        Returns:
            list: Plugin directory names
        """
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return []
        
        plugins = []
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            # Check if it's a valid plugin directory
            if os.path.isdir(plugin_path) and not item.startswith("_"):
                if os.path.exists(os.path.join(plugin_path, "plugin.py")):
                    plugins.append(item)
        
        logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins
    
    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load and register a single plugin.
        
        Args:
            plugin_id: Plugin identifier (directory name)
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            # Import plugin module
            # plugin_dir could be relative, e.g. "src/logic_plugins"
            # We need to turn this into a package path: "src.logic_plugins"
            package_path = self.plugin_dir.replace('/', '.').replace('\\', '.')
            module_path = f"{package_path}.{plugin_id}.plugin"
            
            plugin_module = importlib.import_module(module_path)
            
            # Get plugin class
            # Construct expected class name: "my_plugin" -> "MyPluginPlugin"
            class_name = f"{plugin_id.title().replace('_', '')}Plugin"
            plugin_class = getattr(plugin_module, class_name)
            
            # Load plugin config
            plugin_config = self.config.get("plugins", {}).get(plugin_id, {})
            
            # Instantiate plugin
            plugin_instance = plugin_class(
                plugin_id=plugin_id,
                config=plugin_config,
                service_api=self.service_api
            )
            
            # Register
            self.plugins[plugin_id] = plugin_instance
            
            logger.info(f"Loaded plugin: {plugin_id}")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import plugin module {plugin_id}: {e}")
            return False
        except AttributeError as e:
            logger.error(f"Plugin class not found in {plugin_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    def load_all_plugins(self):
        """Discover and load all available plugins"""
        plugins = self.discover_plugins()
        
        for plugin_id in plugins:
            self.load_plugin(plugin_id)
        
        logger.info(f"Loaded {len(self.plugins)} plugins")
    
    def get_plugin(self, plugin_id: str) -> Optional[BaseLogicPlugin]:
        """
        Get plugin instance by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            BaseLogicPlugin or None
        """
        return self.plugins.get(plugin_id)
    
    async def route_alert_to_plugin(self, alert, plugin_id: str) -> Dict[str, Any]:
        """
        Route alert to specified plugin.
        
        Args:
            alert: Alert data
            plugin_id: Target plugin ID
            
        Returns:
            dict: Execution result from plugin
        """
        plugin = self.get_plugin(plugin_id)
        
        if not plugin:
            # Instead of raising, return error dict to avoid crashing caller
            logger.error(f"Plugin not found: {plugin_id}")
            return {"error": "plugin_not_found"}
        
        if not plugin.enabled:
            logger.warning(f"Plugin {plugin_id} is disabled, skipping alert")
            return {"skipped": True, "reason": "plugin_disabled"}
        
        # Route based on alert type - assume alert object has signal_type
        signal_type = getattr(alert, "signal_type", None)
        if not signal_type and isinstance(alert, dict):
             signal_type = alert.get("signal_type")

        if not signal_type:
             logger.warning("Alert missing signal_type")
             return {"error": "missing_signal_type"}

        if "entry" in signal_type.lower():
            return await plugin.process_entry_signal(alert)
        elif "exit" in signal_type.lower():
            return await plugin.process_exit_signal(alert)
        elif "reversal" in signal_type.lower():
            return await plugin.process_reversal_signal(alert)
        else:
            logger.warning(f"Unknown signal type: {signal_type}")
            return {"error": "unknown_signal_type"}
    
    async def execute_hook(self, hook_name: str, data: Any) -> Any:
        """
        Execute a hook across all enabled plugins.
        
        Args:
            hook_name: Name of hook event (e.g., 'signal_received')
            data: Data to pass to hook
            
        Returns:
            Modified data (pipe-and-filter style) or original if no modifications
        """
        result = data
        
        for plugin_id, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            
            # Check if plugin has hook handler
            handler_name = f"on_{hook_name}"
            if hasattr(plugin, handler_name):
                try:
                    handler = getattr(plugin, handler_name)
                    
                    # Support both sync and async hooks
                    if importlib.util.find_spec("asyncio") and asyncio.iscoroutinefunction(handler):
                        modified = await handler(result)
                    else:
                        modified = handler(result)
                        
                    if modified is not None:
                        result = modified
                        
                    # If result explicitly set to None/False by plugin?
                    # We assume handler returns modified data object.
                    
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_id} hook {hook_name}: {e}")
        
        return result
    
    def get_all_plugins(self) -> Dict[str, BaseLogicPlugin]:
        """Get all registered plugins"""
        return self.plugins
    
    def get_plugin_status(self, plugin_id: str) -> Optional[Dict]:
        """Get status of specific plugin"""
        plugin = self.get_plugin(plugin_id)
        return plugin.get_status() if plugin else None
