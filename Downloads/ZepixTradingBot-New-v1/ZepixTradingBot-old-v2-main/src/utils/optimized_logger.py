"""
Optimized Logger for Zepix Trading Bot v2.0
Intelligent logging system with importance-based filtering and error deduplication
"""

import os
from datetime import datetime

# Import from same utils directory
try:
    from .logging_config import logging_config, LogLevel
except ImportError:
    # Fallback for direct execution
    from logging_config import logging_config, LogLevel


class OptimizedLogger:
    """
    Intelligent logger with advanced features:
    - Importance-based command logging (filter routine commands)
    - Error deduplication (prevent log spam)
    - Trading debug mode integration
    - Log rotation with size limits
    - Missing order tracking with repeat suppression
    """
    
    def __init__(self):
        # Important commands always logged (user-critical actions)
        self.important_commands = {
            'start', 'dashboard', 'pause', 'resume', 'status', 'performance',
            'set_trend', 'set_profit_sl', 'profit_sl_mode', 'profit_sl_status',
            'stop_all', 'emergency_stop', 'set_risk', 'account_status'
        }
        
        # Routine commands only logged in DEBUG mode
        self.routine_commands = {
            'trades', 'signal_status', 'simulation_mode', 'logic_status',
            'open_trades', 'chains', 'statistics'
        }
        
        # Error deduplication tracking
        self.trading_errors_count = {}
        self.max_error_repeats = 3
        
        # Missing order deduplication
        self.missing_order_checks = {}
    
    def log_command_execution(self, command: str, user_id: int, params: dict = None):
        """
        Log Telegram command execution with importance-based filtering
        
        Args:
            command: Command name (e.g., 'start', 'dashboard')
            user_id: Telegram user ID
            params: Optional command parameters
        """
        if command in self.important_commands:
            # Always log important commands
            param_str = f" | Params: {params}" if params else ""
            self._write_log(LogLevel.INFO, f"🎯 {command.upper()}{param_str} | User: {user_id}")
        
        elif command in self.routine_commands:
            # Only log routine commands in DEBUG mode
            if logging_config.should_log(LogLevel.DEBUG):
                self._write_log(LogLevel.DEBUG, f"🔹 {command} | User: {user_id}")
        
        else:
            # Other commands logged in DEBUG mode
            if logging_config.should_log(LogLevel.DEBUG):
                self._write_log(LogLevel.DEBUG, f"⚡ {command}")
    
    def log_trading_debug(self, alert, alignment: dict, signal_direction: str, logic: str):
        """
        Detailed trading decision debugging (only when trading_debug enabled)
        
        Args:
            alert: TradingView alert object
            alignment: Trend alignment check result
            signal_direction: BULLISH/BEARISH/PENDING
            logic: Trading logic (combinedlogic-1/combinedlogic-2/combinedlogic-3)
        """
        if logging_config.trading_debug:
            self._write_log(LogLevel.DEBUG, f"🔍 TRADING_DEBUG: Alert={alert.signal}, TF={alert.tf}, Symbol={alert.symbol}")
            self._write_log(LogLevel.DEBUG, f"🔍 TRADING_DEBUG: Alignment={alignment}")
            self._write_log(LogLevel.DEBUG, f"🔍 TRADING_DEBUG: SignalDir={signal_direction}, Logic={logic}")
    
    def log_trading_error(self, error_msg: str, alert=None):
        """
        Log trading errors with deduplication to prevent spam
        
        Args:
            error_msg: Error message to log
            alert: Optional alert object for context
        """
        # Check if this error has been logged before
        if error_msg in self.trading_errors_count:
            self.trading_errors_count[error_msg] += 1
            
            # Log only first 3 occurrences
            if self.trading_errors_count[error_msg] <= self.max_error_repeats:
                self._write_log(LogLevel.ERROR, f"❌ {error_msg}")
            
            # On 4th occurrence, log suppression notice
            elif self.trading_errors_count[error_msg] == self.max_error_repeats + 1:
                self._write_log(LogLevel.ERROR, f"❌ {error_msg} (suppressing further repeats)")
        
        else:
            # First occurrence - always log
            self.trading_errors_count[error_msg] = 1
            self._write_log(LogLevel.ERROR, f"❌ {error_msg}")
        
        # If alert provided, log debug context
        if alert and logging_config.trading_debug:
            self.log_trading_debug(alert, {"aligned": False, "direction": "UNKNOWN"}, "UNKNOWN", "UNKNOWN")
    
    def log_missing_order(self, chain_id: str, order_id: str):
        """
        Log missing order with deduplication (max 3 times per chain/order pair)
        
        Args:
            chain_id: Profit chain ID
            order_id: Missing order ticket ID
        """
        check_key = f"{chain_id}_{order_id}"
        
        if check_key in self.missing_order_checks:
            self.missing_order_checks[check_key] += 1
            
            # Log only first 3 occurrences
            if self.missing_order_checks[check_key] <= self.max_error_repeats:
                self._write_log(LogLevel.WARNING, f"⚠️ Chain {chain_id} has missing order: {order_id}")
        
        else:
            # First occurrence
            self.missing_order_checks[check_key] = 1
            self._write_log(LogLevel.WARNING, f"⚠️ Chain {chain_id} has missing order: {order_id}")
    
    def log_system_event(self, event_type: str, details: str = ""):
        """
        Log important system events
        
        Args:
            event_type: Event description
            details: Additional event details
        """
        detail_str = f" | {details}" if details else ""
        self._write_log(LogLevel.INFO, f"🔔 {event_type}{detail_str}")
    
    def info(self, message: str):
        """Standard info log"""
        self._write_log(LogLevel.INFO, message)
    
    def warning(self, message: str):
        """Standard warning log"""
        self._write_log(LogLevel.WARNING, f"⚠️ {message}")
    
    def error(self, message: str, exc_info: bool = False):
        """Standard error log"""
        self._write_log(LogLevel.ERROR, f"❌ {message}")
        if exc_info:
            import traceback
            self._write_log(LogLevel.ERROR, traceback.format_exc())
    
    def critical(self, message: str):
        """Critical error log"""
        self._write_log(LogLevel.CRITICAL, f"🚨 CRITICAL: {message}")
    
    def debug(self, message: str):
        """Debug log"""
        if logging_config.should_log(LogLevel.DEBUG):
            self._write_log(LogLevel.DEBUG, f"🔧 {message}")
    
    def _write_log(self, level: LogLevel, message: str):
        """
        Internal method to write log with timestamp
        
        Args:
            level: Log level
            message: Message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Console logging
        if logging_config.enable_console_logs and logging_config.should_log(level):
            print(formatted_message)
        
        # File logging
        if logging_config.enable_file_logs:
            self._write_to_file(formatted_message)
    
    def _write_to_file(self, message: str):
        """
        Write log to file with rotation support
        
        Args:
            message: Formatted message to write
        """
        try:
            # Check if rotation needed
            if os.path.exists(logging_config.log_file):
                file_size = os.path.getsize(logging_config.log_file)
                if file_size > logging_config.max_file_size:
                    self._rotate_log_file()
            
            # Append to log file
            with open(logging_config.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")
        
        except Exception as e:
            print(f"⚠️ Failed to write log file: {e}")
    
    def _rotate_log_file(self):
        """
        Rotate log files when max size exceeded
        Keeps backup_count number of old log files
        """
        try:
            # Shift existing backup files
            for i in range(logging_config.backup_count - 1, 0, -1):
                old_file = f"{logging_config.log_file}.{i}"
                new_file = f"{logging_config.log_file}.{i+1}"
                
                if os.path.exists(old_file):
                    if os.path.exists(new_file):
                        os.remove(new_file)
                    os.rename(old_file, new_file)
            
            # Rename current log to .1
            if os.path.exists(logging_config.log_file):
                backup_file = f"{logging_config.log_file}.1"
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(logging_config.log_file, backup_file)
        
        except Exception as e:
            print(f"⚠️ Log rotation failed: {e}")


# Global logger instance
logger = OptimizedLogger()
