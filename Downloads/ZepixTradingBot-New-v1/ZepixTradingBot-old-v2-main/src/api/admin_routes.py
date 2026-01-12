"""
Admin Routes - FastAPI REST Endpoints for Plugin Management

Document 08: Phase 6 - UI Dashboard (Optional)
Provides REST API endpoints for plugin management and configuration.

Endpoints:
- GET /admin/plugins - List all plugins with status
- POST /admin/plugins/{plugin_id}/enable - Enable a plugin
- POST /admin/plugins/{plugin_id}/disable - Disable a plugin
- GET /admin/plugins/{plugin_id} - Get plugin details
- PUT /admin/plugins/{plugin_id}/config - Update plugin config
- GET /admin/config - Get system configuration
- PUT /admin/config - Update system configuration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PluginInfo:
    """Plugin information model for API responses."""
    
    def __init__(self, plugin_id: str, name: str, version: str, 
                 enabled: bool, status: str, stats: Dict[str, Any]):
        self.id = plugin_id
        self.name = name
        self.version = version
        self.enabled = enabled
        self.status = status
        self.stats = stats
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "status": self.status,
            "stats": self.stats
        }


class AdminRouter:
    """
    Admin router for plugin management endpoints.
    
    This class provides REST API endpoints for managing plugins
    without requiring FastAPI as a dependency. It can be integrated
    with FastAPI or used standalone.
    
    Usage with FastAPI:
        from fastapi import APIRouter, HTTPException
        from api.admin_routes import AdminRouter
        
        admin = AdminRouter(plugin_registry, config_manager)
        router = APIRouter(prefix="/admin")
        
        @router.get("/plugins")
        async def list_plugins():
            return admin.list_plugins()
    """
    
    def __init__(self, plugin_registry=None, config_manager=None):
        """
        Initialize AdminRouter.
        
        Args:
            plugin_registry: PluginRegistry instance for plugin management
            config_manager: ConfigManager instance for configuration
        """
        self.plugin_registry = plugin_registry
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
    
    def set_plugin_registry(self, registry) -> None:
        """Set the plugin registry."""
        self.plugin_registry = registry
    
    def set_config_manager(self, manager) -> None:
        """Set the config manager."""
        self.config_manager = manager
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        Returns all plugins with status.
        
        Endpoint: GET /admin/plugins
        
        Returns:
            List of plugin information dictionaries
        """
        if not self.plugin_registry:
            return []
        
        plugins = []
        
        try:
            all_plugins = self.plugin_registry.get_all_plugins()
            
            for plugin in all_plugins:
                plugin_info = {
                    "id": plugin.plugin_id,
                    "name": plugin.metadata.get("name", plugin.plugin_id),
                    "version": plugin.metadata.get("version", "1.0.0"),
                    "enabled": plugin.enabled,
                    "status": self._get_plugin_status(plugin),
                    "stats": self._get_plugin_stats(plugin)
                }
                plugins.append(plugin_info)
                
        except Exception as e:
            self.logger.error(f"Error listing plugins: {e}")
        
        return plugins
    
    def _get_plugin_status(self, plugin) -> str:
        """Get plugin status string."""
        if not plugin.enabled:
            return "stopped"
        
        try:
            status = plugin.get_status()
            if isinstance(status, dict):
                return status.get("status", "running")
            return "running"
        except:
            return "error"
    
    def _get_plugin_stats(self, plugin) -> Dict[str, Any]:
        """Get plugin statistics."""
        try:
            if hasattr(plugin, 'get_statistics'):
                return plugin.get_statistics()
            elif hasattr(plugin, 'stats'):
                return plugin.stats
            return {}
        except:
            return {}
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific plugin.
        
        Endpoint: GET /admin/plugins/{plugin_id}
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin information dictionary or None if not found
        """
        if not self.plugin_registry:
            return None
        
        try:
            plugin = self.plugin_registry.get_plugin(plugin_id)
            if plugin:
                return {
                    "id": plugin.plugin_id,
                    "name": plugin.metadata.get("name", plugin.plugin_id),
                    "version": plugin.metadata.get("version", "1.0.0"),
                    "description": plugin.metadata.get("description", ""),
                    "author": plugin.metadata.get("author", "Unknown"),
                    "enabled": plugin.enabled,
                    "status": self._get_plugin_status(plugin),
                    "stats": self._get_plugin_stats(plugin),
                    "config": self._get_plugin_config(plugin_id),
                    "database": plugin.db_path if hasattr(plugin, 'db_path') else None
                }
        except Exception as e:
            self.logger.error(f"Error getting plugin {plugin_id}: {e}")
        
        return None
    
    def _get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """Get plugin configuration."""
        if self.config_manager:
            return self.config_manager.get_plugin_config(plugin_id)
        return {}
    
    def enable_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """
        Enable a plugin.
        
        Endpoint: POST /admin/plugins/{plugin_id}/enable
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Result dictionary with success status and message
        """
        if not self.plugin_registry:
            return {"success": False, "message": "Plugin registry not available"}
        
        try:
            plugin = self.plugin_registry.get_plugin(plugin_id)
            if not plugin:
                return {"success": False, "message": f"Plugin {plugin_id} not found"}
            
            plugin.enable()
            
            # Update config if config manager available
            if self.config_manager:
                self.config_manager.set_plugin_enabled(plugin_id, True, persist=True)
            
            self.logger.info(f"Plugin {plugin_id} enabled via API")
            return {"success": True, "message": f"Plugin {plugin_id} enabled"}
            
        except Exception as e:
            self.logger.error(f"Error enabling plugin {plugin_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def disable_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """
        Disable a plugin.
        
        Endpoint: POST /admin/plugins/{plugin_id}/disable
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Result dictionary with success status and message
        """
        if not self.plugin_registry:
            return {"success": False, "message": "Plugin registry not available"}
        
        try:
            plugin = self.plugin_registry.get_plugin(plugin_id)
            if not plugin:
                return {"success": False, "message": f"Plugin {plugin_id} not found"}
            
            plugin.disable()
            
            # Update config if config manager available
            if self.config_manager:
                self.config_manager.set_plugin_enabled(plugin_id, False, persist=True)
            
            self.logger.info(f"Plugin {plugin_id} disabled via API")
            return {"success": True, "message": f"Plugin {plugin_id} disabled"}
            
        except Exception as e:
            self.logger.error(f"Error disabling plugin {plugin_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def update_plugin_config(self, plugin_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update plugin configuration.
        
        Endpoint: PUT /admin/plugins/{plugin_id}/config
        
        Args:
            plugin_id: Plugin identifier
            config: New configuration dictionary
            
        Returns:
            Result dictionary with success status and message
        """
        if not self.config_manager:
            return {"success": False, "message": "Config manager not available"}
        
        try:
            self.config_manager.set_plugin_config(plugin_id, config, persist=True)
            
            # Trigger config reload on plugin if available
            if self.plugin_registry:
                plugin = self.plugin_registry.get_plugin(plugin_id)
                if plugin and hasattr(plugin, 'reload_config'):
                    plugin.reload_config()
            
            self.logger.info(f"Plugin {plugin_id} config updated via API")
            return {"success": True, "message": f"Plugin {plugin_id} config updated"}
            
        except Exception as e:
            self.logger.error(f"Error updating plugin {plugin_id} config: {e}")
            return {"success": False, "message": str(e)}
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get system configuration.
        
        Endpoint: GET /admin/config
        
        Returns:
            System configuration dictionary
        """
        if not self.config_manager:
            return {}
        
        return self.config_manager.config
    
    def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update system configuration.
        
        Endpoint: PUT /admin/config
        
        Args:
            config: New configuration dictionary
            
        Returns:
            Result dictionary with success status and message
        """
        if not self.config_manager:
            return {"success": False, "message": "Config manager not available"}
        
        try:
            # Validate config
            errors = []
            if not isinstance(config, dict):
                errors.append("Config must be a dictionary")
            
            if errors:
                return {"success": False, "message": ", ".join(errors)}
            
            # Update config
            for key, value in config.items():
                self.config_manager.set(key, value)
            
            self.config_manager.save_config()
            
            self.logger.info("System config updated via API")
            return {"success": True, "message": "Configuration updated"}
            
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
            return {"success": False, "message": str(e)}
    
    def reload_config(self) -> Dict[str, Any]:
        """
        Reload configuration from file.
        
        Endpoint: POST /admin/config/reload
        
        Returns:
            Result dictionary with success status and changes
        """
        if not self.config_manager:
            return {"success": False, "message": "Config manager not available"}
        
        try:
            changes = self.config_manager.reload_config()
            
            self.logger.info(f"Config reloaded via API, changes: {changes}")
            return {
                "success": True,
                "message": "Configuration reloaded",
                "changes": changes
            }
            
        except Exception as e:
            self.logger.error(f"Error reloading config: {e}")
            return {"success": False, "message": str(e)}


# Create default router instance
router = AdminRouter()


# FastAPI integration helper
def create_fastapi_router(plugin_registry=None, config_manager=None):
    """
    Create FastAPI router with admin endpoints.
    
    Usage:
        from fastapi import FastAPI
        from api.admin_routes import create_fastapi_router
        
        app = FastAPI()
        admin_router = create_fastapi_router(plugin_registry, config_manager)
        app.include_router(admin_router, prefix="/admin")
    """
    try:
        from fastapi import APIRouter, HTTPException
        
        admin = AdminRouter(plugin_registry, config_manager)
        api_router = APIRouter()
        
        @api_router.get("/plugins")
        async def list_plugins():
            return admin.list_plugins()
        
        @api_router.get("/plugins/{plugin_id}")
        async def get_plugin(plugin_id: str):
            result = admin.get_plugin(plugin_id)
            if not result:
                raise HTTPException(404, f"Plugin {plugin_id} not found")
            return result
        
        @api_router.post("/plugins/{plugin_id}/enable")
        async def enable_plugin(plugin_id: str):
            result = admin.enable_plugin(plugin_id)
            if not result["success"]:
                raise HTTPException(400, result["message"])
            return result
        
        @api_router.post("/plugins/{plugin_id}/disable")
        async def disable_plugin(plugin_id: str):
            result = admin.disable_plugin(plugin_id)
            if not result["success"]:
                raise HTTPException(400, result["message"])
            return result
        
        @api_router.get("/config")
        async def get_config():
            return admin.get_config()
        
        @api_router.post("/config/reload")
        async def reload_config():
            result = admin.reload_config()
            if not result["success"]:
                raise HTTPException(400, result["message"])
            return result
        
        return api_router
        
    except ImportError:
        logger.warning("FastAPI not installed, cannot create FastAPI router")
        return None
