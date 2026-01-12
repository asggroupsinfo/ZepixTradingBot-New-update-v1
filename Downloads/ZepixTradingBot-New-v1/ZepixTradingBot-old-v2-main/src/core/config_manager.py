"""
ConfigManager - Dynamic Configuration Loading and Hot-Reload System

Document 07: Phase 5 - Dynamic Config & Per-Plugin Databases
Implements zero-downtime configuration updates with file watching.

Features:
- JSON configuration loading
- File system watching for auto-reload
- Observer pattern for change notifications
- Plugin-specific configuration access
- Configuration diffing and change detection
"""

import json
import os
import logging
import threading
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigFileHandler:
    """
    File system event handler for configuration file changes.
    Triggers config reload when the config file is modified.
    """
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.last_modified = 0
        self.debounce_seconds = 1.0  # Prevent multiple reloads
    
    def on_modified(self, event):
        """Handle file modification event."""
        if event.is_directory:
            return
        
        # Check if it's our config file
        if os.path.basename(event.src_path) == os.path.basename(self.config_manager.config_path):
            current_time = datetime.now().timestamp()
            
            # Debounce to prevent multiple rapid reloads
            if current_time - self.last_modified > self.debounce_seconds:
                self.last_modified = current_time
                logger.info(f"Config file modified: {event.src_path}")
                self.config_manager.reload_config()


class ConfigManager:
    """
    Manages dynamic configuration loading and hot-reload.
    
    Features:
    - Load configuration from JSON file
    - Watch for file changes and auto-reload
    - Notify observers of configuration changes
    - Plugin-specific configuration access
    - Zero-downtime configuration updates
    
    Usage:
        config_manager = ConfigManager("config/config.json")
        config_manager.register_observer(my_callback)
        
        # Get full config
        config = config_manager.config
        
        # Get plugin-specific config
        plugin_config = config_manager.get_plugin_config("combined_v3")
    """
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.observers: List[Callable[[List[str]], None]] = []
        self._lock = threading.Lock()
        self._observer = None
        self._watching = False
        
        # Load initial configuration
        self.load_config()
        
        # Start file watching if watchdog is available
        self._try_start_watching()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Loads configuration from JSON file.
        
        Returns:
            The loaded configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        with self._lock:
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Config loaded from {self.config_path}")
                return self.config
            except FileNotFoundError:
                logger.error(f"Config file not found: {self.config_path}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
                raise
    
    def reload_config(self) -> List[str]:
        """
        Reloads config without restart.
        
        Returns:
            List of changed configuration keys
        """
        with self._lock:
            old_config = self.config.copy()
        
        try:
            self.load_config()
        except Exception as e:
            logger.error(f"Failed to reload config: {e}")
            return []
        
        # Detect changes
        changes = self._diff_config(old_config, self.config)
        
        if changes:
            logger.info(f"Config changes detected: {changes}")
            self._notify_observers(changes)
        else:
            logger.info("Config reloaded, no changes detected")
        
        return changes
    
    def _diff_config(self, old: Dict[str, Any], new: Dict[str, Any], prefix: str = "") -> List[str]:
        """
        Returns list of changed keys (supports nested dicts).
        
        Args:
            old: Old configuration dictionary
            new: New configuration dictionary
            prefix: Key prefix for nested keys
            
        Returns:
            List of changed key paths
        """
        changes = []
        
        # Check for new or modified keys
        for key in new:
            full_key = f"{prefix}.{key}" if prefix else key
            
            if key not in old:
                changes.append(full_key)
            elif isinstance(new[key], dict) and isinstance(old.get(key), dict):
                # Recursively check nested dicts
                changes.extend(self._diff_config(old[key], new[key], full_key))
            elif old[key] != new[key]:
                changes.append(full_key)
        
        # Check for removed keys
        for key in old:
            full_key = f"{prefix}.{key}" if prefix else key
            if key not in new:
                changes.append(full_key)
        
        return changes
    
    def register_observer(self, callback: Callable[[List[str]], None]) -> None:
        """
        Register callback for config changes.
        
        Args:
            callback: Function to call when config changes.
                     Receives list of changed keys as argument.
        """
        if callback not in self.observers:
            self.observers.append(callback)
            callback_name = getattr(callback, '__name__', str(callback))
            logger.debug(f"Registered config observer: {callback_name}")
    
    def unregister_observer(self, callback: Callable[[List[str]], None]) -> None:
        """
        Unregister a config change callback.
        
        Args:
            callback: The callback to remove
        """
        if callback in self.observers:
            self.observers.remove(callback)
            callback_name = getattr(callback, '__name__', str(callback))
            logger.debug(f"Unregistered config observer: {callback_name}")
    
    def _notify_observers(self, changes: List[str]) -> None:
        """
        Notify all observers of changes.
        
        Args:
            changes: List of changed configuration keys
        """
        for callback in self.observers:
            try:
                callback(changes)
            except Exception as e:
                logger.error(f"Error in config observer {callback.__name__}: {e}")
    
    def _try_start_watching(self) -> None:
        """
        Try to start watching config file for changes.
        Uses watchdog if available, otherwise logs a warning.
        """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class WatchdogHandler(FileSystemEventHandler):
                def __init__(self, config_handler):
                    self.config_handler = config_handler
                
                def on_modified(self, event):
                    self.config_handler.on_modified(event)
            
            event_handler = WatchdogHandler(ConfigFileHandler(self))
            self._observer = Observer()
            config_dir = os.path.dirname(os.path.abspath(self.config_path))
            self._observer.schedule(event_handler, config_dir, recursive=False)
            self._observer.start()
            self._watching = True
            logger.info(f"Started watching config file: {self.config_path}")
        except ImportError:
            logger.warning("watchdog not installed, config hot-reload disabled. Install with: pip install watchdog")
            self._watching = False
    
    def start_watching(self) -> bool:
        """
        Start watching config file for changes.
        
        Returns:
            True if watching started successfully, False otherwise
        """
        if not self._watching:
            self._try_start_watching()
        return self._watching
    
    def stop_watching(self) -> None:
        """Stop watching config file for changes."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            self._watching = False
            logger.info("Stopped watching config file")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        Supports dot notation for nested keys.
        
        Args:
            key: Configuration key (e.g., "plugins.combined_v3.enabled")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        with self._lock:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    def set(self, key: str, value: Any, persist: bool = False) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            persist: If True, save to config file
        """
        with self._lock:
            keys = key.split('.')
            config = self.config
            
            # Navigate to parent
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set value
            old_value = config.get(keys[-1])
            config[keys[-1]] = value
            
            if old_value != value:
                self._notify_observers([key])
        
        if persist:
            self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        with self._lock:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Config saved to {self.config_path}")
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin configuration dictionary or empty dict
        """
        return self.get(f"plugins.{plugin_id}", {})
    
    def set_plugin_config(self, plugin_id: str, config: Dict[str, Any], persist: bool = False) -> None:
        """
        Set configuration for a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            config: Plugin configuration dictionary
            persist: If True, save to config file
        """
        self.set(f"plugins.{plugin_id}", config, persist)
    
    def get_plugin_enabled(self, plugin_id: str) -> bool:
        """
        Check if a plugin is enabled.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if plugin is enabled, False otherwise
        """
        return self.get(f"plugins.{plugin_id}.enabled", False)
    
    def set_plugin_enabled(self, plugin_id: str, enabled: bool, persist: bool = False) -> None:
        """
        Enable or disable a plugin.
        
        Args:
            plugin_id: Plugin identifier
            enabled: Whether to enable the plugin
            persist: If True, save to config file
        """
        self.set(f"plugins.{plugin_id}.enabled", enabled, persist)
    
    @property
    def is_watching(self) -> bool:
        """Check if config file watching is active."""
        return self._watching
    
    def get_all_plugin_ids(self) -> List[str]:
        """
        Get list of all configured plugin IDs.
        
        Returns:
            List of plugin identifiers
        """
        plugins = self.get("plugins", {})
        return list(plugins.keys()) if isinstance(plugins, dict) else []
    
    def validate_config(self) -> List[str]:
        """
        Validate the current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required top-level keys
        required_keys = ["trading", "telegram"]
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Missing required key: {key}")
        
        # Validate plugin configurations
        plugins = self.get("plugins", {})
        for plugin_id, plugin_config in plugins.items():
            if not isinstance(plugin_config, dict):
                errors.append(f"Invalid plugin config for {plugin_id}: must be a dictionary")
        
        return errors
    
    def __repr__(self) -> str:
        return f"ConfigManager(path={self.config_path}, watching={self._watching})"
