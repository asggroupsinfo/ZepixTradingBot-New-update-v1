"""
Centralized Logging Configuration for Zepix Trading Bot v2.0
Provides LogLevel enum and LoggingConfig class for intelligent logging control
"""

import logging
import os
from enum import Enum
from datetime import datetime


class LogLevel(Enum):
    """Log level enumeration for filtering messages"""
    DEBUG = 1
    INFO = 2  
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class LoggingConfig:
    """
    Centralized logging configuration with trading debug mode support.
    
    Features:
    - Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Console and file logging control
    - Trading debug mode for detailed trend-signal analysis
    - Log rotation with size limits
    """
    
    def __init__(self):
        # Core logging settings
        self.current_level = LogLevel.INFO
        self.enable_console_logs = True
        self.enable_file_logs = True
        
        # File logging configuration
        self.log_file = "logs/bot_activity.log"
        self.max_file_size = 10 * 1024 * 1024  # 10MB max file size
        self.backup_count = 5  # Keep 5 backup files
        
        # TRADING DEBUG MODE - For detailed trend-signal analysis
        # When enabled, logs all trading decisions with full context
        self.trading_debug = True
        
        # Create logs directory if not exists
        os.makedirs("logs", exist_ok=True)
        
        # Load saved log level from config (PERSISTENCE across restarts)
        self._load_log_level_from_config()
        
    def set_level(self, level: LogLevel):
        """Change the current logging level"""
        self.current_level = level
        
    def should_log(self, message_level: LogLevel) -> bool:
        """Check if a message with given level should be logged"""
        return message_level.value >= self.current_level.value
    
    def enable_trading_debug(self):
        """Enable detailed trading debug logging"""
        self.trading_debug = True
        
    def disable_trading_debug(self):
        """Disable trading debug logging"""
        self.trading_debug = False
    
    def _load_log_level_from_config(self):
        """Load saved log level from config file (if exists)"""
        try:
            import json
            config_file = "config/logging_settings.json"
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    level_name = settings.get("log_level", "INFO")
                    
                    # Map string to LogLevel enum
                    level_map = {
                        "DEBUG": LogLevel.DEBUG,
                        "INFO": LogLevel.INFO,
                        "WARNING": LogLevel.WARNING,
                        "ERROR": LogLevel.ERROR,
                        "CRITICAL": LogLevel.CRITICAL
                    }
                    
                    if level_name in level_map:
                        self.current_level = level_map[level_name]
                        print(f"[LOGGING CONFIG] Loaded saved log level: {level_name}")
                        # Load trading_debug setting
                        trading_debug = settings.get("trading_debug", False)
                        self.trading_debug = trading_debug
                        print(f"[LOGGING CONFIG] Loaded trading_debug: {trading_debug}")
                    else:
                        print(f"[LOGGING CONFIG] Invalid saved level '{level_name}', using default INFO")
            else:
                print("[LOGGING CONFIG] No saved log level, using default INFO")
        except Exception as e:
            print(f"[LOGGING CONFIG] Could not load log level from config: {e}, using default INFO")


# Global logging configuration instance
logging_config = LoggingConfig()
