"""
Forex Session Manager
Manages Forex trading session timings, symbol filtering, and session-based trade permissions.

Features:
- Dynamic session configuration via JSON (data/session_settings.json)
- 5 predefined Forex sessions: Asian, London, Overlap, NY Late, Dead Zone
- Per-session symbol filtering (enable/disable symbols per session)
- Master switch for global session filtering
- Session transition detection with advance alerts
- Force-close option at session end
- Time adjustment support (±30 minute increments)
- IST timezone (Asia/Kolkata) support

Author: Zepix Trading Bot Development Team
Version: 1.0
Created: 2026-01-11
"""

import json
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import logging


class SessionManager:
    """
    Manages Forex session-based trading restrictions.
    
    Provides dynamic configuration for session timings, symbol filtering,
    and automated alerts for session transitions.
    """
    
    def __init__(self, config_path: str = "data/session_settings.json"):
        """
        Initialize the Forex Session Manager.
        
        Args:
            config_path: Path to JSON configuration file (default: data/session_settings.json)
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)  # Initialize logger FIRST
        self.config = self.load_session_config()
        self.timezone = pytz.timezone(self.config.get('timezone', 'Asia/Kolkata'))
        self.last_session = None
        self.alert_cooldown = {}  # Prevents duplicate alerts
        
        self.logger.info(f"Forex SessionManager initialized with timezone: {self.timezone}")
    
    def load_session_config(self) -> dict:
        """
        Load session configuration from JSON file.
        
        Returns:
            dict: Session configuration with all settings
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Session config loaded from {self.config_path}")
                return config
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON config: {e}")
                return self._get_default_config()
        else:
            self.logger.warning(f"Config not found: {self.config_path}, using defaults")
            default_config = self._get_default_config()
            # Create default config file
            self.save_session_config(default_config)
            return default_config
    
    def save_session_config(self, config: Optional[dict] = None):
        """
        Save session configuration to JSON file (atomic write).
        
        Args:
            config: Configuration dict to save (defaults to self.config)
        """
        if config is None:
            config = self.config
        
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Atomic write: write to temp file first
            temp_path = self.config_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Rename temp to actual (atomic on most systems)
            os.replace(temp_path, self.config_path)
            self.logger.info("Session config saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save session config: {e}")
            raise
    
    def _get_default_config(self) -> dict:
        """
        Return default Forex session configuration.
        Strictly matches User's Session Table from Step 544.
        
        Returns:
            dict: Default configuration with 5 Forex sessions
        """
        from datetime import datetime
        
        return {
            "version": "4.0",
            "master_switch": True,
            "timezone": "Asia/Kolkata",
            "sessions": {
                "asian": {
                    "name": "Asian Session",
                    "start_time": "05:00",
                    "end_time": "13:30",
                    "allowed_symbols": ["USDJPY", "AUDJPY", "AUDUSD", "NZDUSD"],
                    "advance_alert_enabled": True,
                    "advance_alert_minutes": 30,
                    "force_close_enabled": False,
                    "description": "User Rule: USDJPY, AUDJPY, AUDUSD, NZDUSD Allowed. Blocked: EURUSD, GBPUSD, GBPJPY"
                },
                "london": {
                    "name": "London Session",
                    "start_time": "13:30",
                    "end_time": "18:30",
                    "allowed_symbols": ["EURUSD", "GBPUSD", "EURGBP", "GBPJPY", "EURJPY", "XAUUSD"],
                    "advance_alert_enabled": True,
                    "advance_alert_minutes": 30,
                    "force_close_enabled": False,
                    "description": "User Rule: EURUSD, GBPUSD, EURGBP, GBPJPY, EURJPY, XAUUSD Allowed"
                },
                "overlap": {
                    "name": "Overlap Session",
                    "start_time": "18:30",
                    "end_time": "22:30",
                    "allowed_symbols": ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY"],
                    "advance_alert_enabled": True,
                    "advance_alert_minutes": 30,
                    "force_close_enabled": False,
                    "description": "User Rule: EURUSD, GBPUSD, XAUUSD, USDJPY Allowed"
                },
                "ny_late": {
                    "name": "NY Late Session",
                    "start_time": "22:30",
                    "end_time": "03:30",
                    "allowed_symbols": ["USDJPY", "XAUUSD", "USDCAD"],
                    "advance_alert_enabled": True,
                    "advance_alert_minutes": 30,
                    "force_close_enabled": False,
                    "description": "User Rule: USDJPY, XAUUSD, USDCAD Allowed. Blocked: EURUSD, GBPUSD"
                },
                "dead_zone": {
                    "name": "Dead Zone",
                    "start_time": "03:30",
                    "end_time": "05:00",
                    "allowed_symbols": [],
                    "advance_alert_enabled": False,
                    "advance_alert_minutes": 0,
                    "force_close_enabled": True,
                    "description": "User Rule: NO TRADES. ALL BLOCKED"
                }
            },
            "all_symbols": [
                "USDJPY", "AUDJPY", "AUDUSD", "NZDUSD", 
                "EURUSD", "GBPUSD", "EURGBP", "GBPJPY", "EURJPY", "XAUUSD",
                "USDCAD"
            ],
            "alert_history": [],
            "metadata": {
                "created_at": "2026-01-12T00:30:00+05:30",
                "last_modified": "2026-01-12T00:30:00+05:30",
                "modified_by": "system_defaults",
                "notes": "Default Forex session configuration matching User Table."
            }
        }

    
    def get_current_time(self) -> datetime:
        """
        Get current time in configured timezone.
        
        Returns:
            datetime: Current time with timezone info
        """
        return datetime.now(self.timezone)
    
    def time_to_minutes(self, time_str: str) -> int:
        """
        Convert HH:MM string to minutes since midnight.
        
        Args:
            time_str: Time in HH:MM format (24-hour)
            
        Returns:
            int: Minutes since midnight (0-1439)
        """
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def get_current_session(self, current_time: Optional[datetime] = None) -> str:
        """
        Get the name of the current active session.
        
        When multiple sessions overlap, returns the session with the latest start time.
        This ensures priority for more recent sessions (e.g., London over Asian).
        
        Args:
            current_time: Optional datetime to check (defaults to now)
            
        Returns:
            str: Session ID (e.g., "asian", "london") or "none" if no active session
        """
        if current_time is None:
            current_time = self.get_current_time()
        
        current_minutes = current_time.hour * 60 + current_time.minute
        
        # Collect all active sessions
        active_sessions = []
        
        for session_id, session_data in self.config['sessions'].items():
            start_mins = self.time_to_minutes(session_data['start_time'])
            end_mins = self.time_to_minutes(session_data['end_time'])
            
            # Handle sessions that cross midnight (e.g., 22:00 to 02:00)
            if start_mins > end_mins:
                # Session spans midnight
                if current_minutes >= start_mins or current_minutes < end_mins:
                    active_sessions.append((session_id, start_mins))
            else:
                # Normal session within same day
                if start_mins <= current_minutes < end_mins:
                    active_sessions.append((session_id, start_mins))
        
        # If no active sessions, return "none"
        if not active_sessions:
            return "none"
        
        # If multiple sessions active (overlap), return the one with latest start time
        # This gives priority to London over Asian during 13:00-14:30 overlap
        active_sessions.sort(key=lambda x: x[1], reverse=True)
        return active_sessions[0][0]
    
    def check_trade_allowed(self, symbol: str, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Check if trading the symbol is allowed based on current session.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD", "GBPUSD")
            current_time: Optional datetime to check (defaults to now)
            
        Returns:
            Tuple[bool, str]: (allowed: bool, reason: str)
        """
        # Master switch check - if OFF, all trades allowed
        if not self.config.get('master_switch', True):
            return True, "Master switch OFF - all trades allowed"
        
        if current_time is None:
            current_time = self.get_current_time()
        
        current_session = self.get_current_session(current_time)
        
        if current_session == "none":
            return False, "No active session"
        
        session_data = self.config['sessions'][current_session]
        allowed_symbols = session_data.get('allowed_symbols', [])
        
        if symbol in allowed_symbols:
            return True, f"Allowed in {session_data['name']}"
        else:
            return False, f"{symbol} not allowed in {session_data['name']}"
    
    def adjust_session_time(self, session_id: str, field: str, delta_minutes: int):
        """
        Adjust session start or end time by delta minutes.
        
        Args:
            session_id: Session identifier (e.g., "asian", "london")
            field: 'start_time' or 'end_time'
            delta_minutes: Adjustment in minutes (+30 or -30)
            
        Raises:
            ValueError: If session_id is invalid
        """
        if session_id not in self.config['sessions']:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.config['sessions'][session_id]
        current_time_str = session[field]
        
        # Parse current time
        hours, minutes = map(int, current_time_str.split(':'))
        total_minutes = hours * 60 + minutes
        
        # Apply delta and wrap around 24 hours
        new_total_minutes = (total_minutes + delta_minutes) % (24 * 60)
        
        # Convert back to HH:MM
        new_hours = new_total_minutes // 60
        new_minutes = new_total_minutes % 60
        new_time_str = f"{new_hours:02d}:{new_minutes:02d}"
        
        # Update config
        self.config['sessions'][session_id][field] = new_time_str
        self.save_session_config()
        
        self.logger.info(f"Adjusted {session_id}.{field}: {current_time_str} → {new_time_str}")
    
    def toggle_symbol(self, session_id: str, symbol: str):
        """
        Toggle symbol ON/OFF for a specific session.
        
        Args:
            session_id: Session identifier
            symbol: Trading symbol to toggle
            
        Raises:
            ValueError: If session_id is invalid
        """
        if session_id not in self.config['sessions']:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.config['sessions'][session_id]
        allowed_symbols = session.get('allowed_symbols', [])
        
        if symbol in allowed_symbols:
            allowed_symbols.remove(symbol)
            action = "removed"
        else:
            allowed_symbols.append(symbol)
            action = "added"
        
        session['allowed_symbols'] = allowed_symbols
        self.save_session_config()
        
        self.logger.info(f"{symbol} {action} for {session_id}")
    
    def toggle_master_switch(self) -> bool:
        """
        Toggle master switch and return new state.
        
        Returns:
            bool: New master switch state
        """
        current_state = self.config.get('master_switch', True)
        new_state = not current_state
        self.config['master_switch'] = new_state
        self.save_session_config()
        
        self.logger.info(f"Master switch: {current_state} → {new_state}")
        return new_state
    
    def toggle_force_close(self, session_id: str) -> bool:
        """
        Toggle force close for a session and return new state.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: New force close state
            
        Raises:
            ValueError: If session_id is invalid
        """
        if session_id not in self.config['sessions']:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.config['sessions'][session_id]
        current_state = session.get('force_close_enabled', False)
        new_state = not current_state
        session['force_close_enabled'] = new_state
        self.save_session_config()
        
        self.logger.info(f"Force close for {session_id}: {current_state} → {new_state}")
        return new_state
    
    def check_session_transitions(self) -> Dict[str, any]:
        """
        Check for session transitions and return alerts.
        
        Should be called periodically (e.g., every minute) to detect:
        - Session starts
        - Session endings (advance alerts)
        - Force close triggers
        
        Returns:
            dict: Alerts with keys:
                - session_started: Session ID that just started (or None)
                - session_ending: Dict with session and minutes until start (or None)
                - force_close_required: bool indicating if force close needed
        """
        current_time = self.get_current_time()
        current_session = self.get_current_session(current_time)
        current_date_key = current_time.strftime("%Y-%m-%d")
        
        alerts = {
            'session_started': None,
            'session_ending': None,
            'force_close_required': False
        }
        
        # Check if session just started (different from last checked session)
        if self.last_session != current_session and current_session != "none":
            alerts['session_started'] = current_session
            self.last_session = current_session
            self.logger.info(f"Session transitioned to: {current_session}")
        
        # Check for advance alerts (X minutes before session starts)
        for session_id, session_data in self.config['sessions'].items():
            if not session_data.get('advance_alert_enabled', False):
                continue
            
            start_minutes = self.time_to_minutes(session_data['start_time'])
            alert_minutes = session_data.get('advance_alert_minutes', 30)
            
            # Calculate alert trigger time
            alert_trigger_minutes = (start_minutes - alert_minutes) % (24 * 60)
            current_minutes = current_time.hour * 60 + current_time.minute
            
            # Create cooldown key (unique per day per session)
            cooldown_key = f"{current_date_key}_{session_id}_advance"
            
            # Check if we're at the alert trigger point (within 1-minute window)
            if abs(current_minutes - alert_trigger_minutes) < 1:
                # Check cooldown to prevent duplicate alerts
                if cooldown_key not in self.alert_cooldown:
                    alerts['session_ending'] = {
                        'session': session_id,
                        'starts_in_minutes': alert_minutes,
                        'session_name': session_data['name']
                    }
                    # Set cooldown (expires in 2 minutes)
                    self.alert_cooldown[cooldown_key] = current_time + timedelta(minutes=2)
        
        # Clean expired cooldowns
        self.alert_cooldown = {
            k: v for k, v in self.alert_cooldown.items()
            if v > current_time
        }
        
        # Check if current session requires force close at end
        if current_session != "none":
            current_session_data = self.config['sessions'][current_session]
            if current_session_data.get('force_close_enabled', False):
                end_minutes = self.time_to_minutes(current_session_data['end_time'])
                current_minutes = current_time.hour * 60 + current_time.minute
                
                # Trigger force close 1 minute before session ends
                minutes_until_end = (end_minutes - current_minutes) % (24 * 60)
                if 0 <= minutes_until_end <= 1:
                    alerts['force_close_required'] = True
        
        return alerts
    
    def get_session_status_text(self) -> str:
        """
        Generate status text for Telegram display.
        
        Returns:
            str: Formatted status message with current session info
        """
        current_time = self.get_current_time()
        current_session = self.get_current_session(current_time)
        master_switch = self.config.get('master_switch', True)
        
        status = f"{'🟢' if master_switch else '🔴'} **Master Switch:** {'ON' if master_switch else 'OFF'}\n"
        
        if current_session == "none":
            status += "🕐 **Current Session:** None (Dead Zone)\n"
            status += "✅ **Allowed Symbols:** All (0 restrictions)\n"
        else:
            session_data = self.config['sessions'][current_session]
            allowed_symbols = session_data.get('allowed_symbols', [])
            status += f"🕐 **Current Session:** {session_data['name']}\n"
            status += f"✅ **Allowed Symbols:** {', '.join(allowed_symbols)} ({len(allowed_symbols)}/{len(self.config['all_symbols'])})\n"
        
        return status
    
    def get_status(self) -> dict:
        """
        Get comprehensive status information.
        
        Returns:
            dict: Status with current session, config, and runtime info
        """
        current_time = self.get_current_time()
        current_session = self.get_current_session(current_time)
        
        return {
            'master_switch': self.config.get('master_switch', True),
            'current_session': current_session,
            'current_time': current_time.isoformat(),
            'timezone': str(self.timezone),
            'total_sessions': len(self.config['sessions']),
            'config_path': self.config_path
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize session manager
    mgr = SessionManager()
    
    # Get current session
    current = mgr.get_current_session()
    print(f"Current session: {current}")
    
    # Check if symbol is allowed
    allowed, reason = mgr.check_trade_allowed("EURUSD")
    print(f"EURUSD allowed: {allowed} ({reason})")
    
    # Get status text
    status = mgr.get_session_status_text()
    print(status)
