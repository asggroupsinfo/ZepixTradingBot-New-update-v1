"""
Forex Session Manager - V4 Logic Integration for V5 Sticky Header

Manages Forex session timings, symbol filtering, and trade permissions
based on IST timezone with dynamic configuration.

Sessions (IST):
- Asian: 05:30 - 14:30 (USDJPY, AUDUSD, EURJPY)
- London: 13:00 - 22:00 (GBPUSD, EURUSD, GBPJPY)
- Overlap: 18:00 - 20:30 (All Major Pairs)
- NY Late: 22:00 - 02:00 (USDCAD, EURUSD)
- Dead Zone: 02:00 - 05:30 (Trading Disabled)
"""

import json
import os
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import logging


class SessionType(Enum):
    """Forex session types."""
    ASIAN = "asian"
    LONDON = "london"
    OVERLAP = "overlap"
    NY_LATE = "ny_late"
    DEAD_ZONE = "dead_zone"
    NONE = "none"


class SessionStatus(Enum):
    """Session status indicators."""
    ACTIVE = "active"
    STARTING_SOON = "starting_soon"
    ENDING_SOON = "ending_soon"
    INACTIVE = "inactive"


@dataclass
class SessionConfig:
    """Configuration for a single trading session."""
    session_id: str
    name: str
    start_time: str
    end_time: str
    allowed_symbols: List[str]
    advance_alert_enabled: bool = True
    advance_alert_minutes: int = 30
    force_close_enabled: bool = False
    description: str = ""
    emoji: str = ""


@dataclass
class SessionInfo:
    """Current session information."""
    session_type: SessionType
    session_name: str
    start_time: str
    end_time: str
    allowed_symbols: List[str]
    time_remaining: timedelta
    status: SessionStatus
    is_trading_allowed: bool
    next_session: Optional[str] = None
    next_session_starts_in: Optional[timedelta] = None


@dataclass
class SessionAlert:
    """Alert for session transitions."""
    alert_id: str
    alert_type: str
    session_id: str
    message: str
    timestamp: datetime
    acknowledged: bool = False


class ForexSessionManager:
    """
    Manages Forex trading sessions with IST timezone support.
    
    Integrates V4 session logic for the V5 Sticky Header system.
    """
    
    IST_OFFSET_HOURS = 5
    IST_OFFSET_MINUTES = 30
    
    DEFAULT_SESSIONS = {
        "asian": SessionConfig(
            session_id="asian",
            name="Asian Session",
            start_time="05:30",
            end_time="14:30",
            allowed_symbols=["USDJPY", "AUDUSD", "EURJPY"],
            advance_alert_enabled=True,
            advance_alert_minutes=30,
            force_close_enabled=False,
            description="Tokyo & Sydney overlap, low volatility",
            emoji=""
        ),
        "london": SessionConfig(
            session_id="london",
            name="London Session",
            start_time="13:00",
            end_time="22:00",
            allowed_symbols=["GBPUSD", "EURUSD", "GBPJPY"],
            advance_alert_enabled=True,
            advance_alert_minutes=30,
            force_close_enabled=False,
            description="European session, high liquidity",
            emoji=""
        ),
        "overlap": SessionConfig(
            session_id="overlap",
            name="London-NY Overlap",
            start_time="18:00",
            end_time="20:30",
            allowed_symbols=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "GBPJPY", "USDCAD", "XAUUSD"],
            advance_alert_enabled=True,
            advance_alert_minutes=30,
            force_close_enabled=False,
            description="Highest volume period, maximum volatility",
            emoji=""
        ),
        "ny_late": SessionConfig(
            session_id="ny_late",
            name="New York Late Session",
            start_time="22:00",
            end_time="02:00",
            allowed_symbols=["USDCAD", "EURUSD"],
            advance_alert_enabled=True,
            advance_alert_minutes=30,
            force_close_enabled=False,
            description="Late US session, consolidation phase",
            emoji=""
        ),
        "dead_zone": SessionConfig(
            session_id="dead_zone",
            name="Dead Zone",
            start_time="02:00",
            end_time="05:30",
            allowed_symbols=[],
            advance_alert_enabled=False,
            advance_alert_minutes=0,
            force_close_enabled=True,
            description="Low liquidity, trading not recommended",
            emoji=""
        )
    }
    
    ALL_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "GBPJPY", "USDCAD", "XAUUSD"]
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Forex Session Manager.
        
        Args:
            config_path: Optional path to session configuration JSON file
        """
        self.config_path = config_path or "data/session_settings.json"
        self.sessions: Dict[str, SessionConfig] = {}
        self.master_switch: bool = True
        self.last_session: Optional[str] = None
        self.alert_history: List[str] = []
        self.alerts: List[SessionAlert] = []
        self._alert_callback: Optional[Callable] = None
        self._running: bool = False
        self._monitor_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__)
        
        self.stats = {
            'session_changes': 0,
            'alerts_generated': 0,
            'trades_blocked': 0,
            'trades_allowed': 0
        }
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load session configuration from file or use defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.master_switch = data.get('master_switch', True)
                self.alert_history = data.get('alert_history', [])
                
                for session_id, session_data in data.get('sessions', {}).items():
                    self.sessions[session_id] = SessionConfig(
                        session_id=session_id,
                        name=session_data.get('name', session_id),
                        start_time=session_data.get('start_time', '00:00'),
                        end_time=session_data.get('end_time', '00:00'),
                        allowed_symbols=session_data.get('allowed_symbols', []),
                        advance_alert_enabled=session_data.get('advance_alert_enabled', True),
                        advance_alert_minutes=session_data.get('advance_alert_minutes', 30),
                        force_close_enabled=session_data.get('force_close_enabled', False),
                        description=session_data.get('description', ''),
                        emoji=session_data.get('emoji', '')
                    )
                
                self.logger.info(f"Loaded session config from {self.config_path}")
            except Exception as e:
                self.logger.error(f"Failed to load session config: {e}")
                self._use_defaults()
        else:
            self._use_defaults()
    
    def _use_defaults(self) -> None:
        """Use default session configuration."""
        self.sessions = self.DEFAULT_SESSIONS.copy()
        self.master_switch = True
        self.alert_history = []
        self.logger.info("Using default session configuration")
    
    def save_config(self) -> bool:
        """Save session configuration to file."""
        try:
            data = {
                'version': '1.0',
                'master_switch': self.master_switch,
                'timezone': 'Asia/Kolkata',
                'sessions': {},
                'all_symbols': self.ALL_SYMBOLS,
                'alert_history': self.alert_history[-100:]
            }
            
            for session_id, config in self.sessions.items():
                data['sessions'][session_id] = {
                    'name': config.name,
                    'start_time': config.start_time,
                    'end_time': config.end_time,
                    'allowed_symbols': config.allowed_symbols,
                    'advance_alert_enabled': config.advance_alert_enabled,
                    'advance_alert_minutes': config.advance_alert_minutes,
                    'force_close_enabled': config.force_close_enabled,
                    'description': config.description,
                    'emoji': config.emoji
                }
            
            os.makedirs(os.path.dirname(self.config_path) or '.', exist_ok=True)
            
            temp_path = self.config_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            os.replace(temp_path, self.config_path)
            self.logger.info("Session config saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session config: {e}")
            return False
    
    def get_current_ist_time(self) -> datetime:
        """Get current time in IST timezone."""
        utc_now = datetime.now(timezone.utc)
        ist_offset = timedelta(hours=self.IST_OFFSET_HOURS, minutes=self.IST_OFFSET_MINUTES)
        return utc_now + ist_offset
    
    def format_ist_time(self, dt: Optional[datetime] = None) -> str:
        """Format datetime as IST time string (HH:MM:SS IST)."""
        if dt is None:
            dt = self.get_current_ist_time()
        return dt.strftime("%H:%M:%S IST")
    
    def format_ist_date(self, dt: Optional[datetime] = None) -> str:
        """Format datetime as IST date string (DD Mon YYYY)."""
        if dt is None:
            dt = self.get_current_ist_time()
        return dt.strftime("%d %b %Y")
    
    def format_ist_datetime(self, dt: Optional[datetime] = None) -> Tuple[str, str]:
        """Format datetime as IST time and date strings."""
        if dt is None:
            dt = self.get_current_ist_time()
        return self.format_ist_time(dt), self.format_ist_date(dt)
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM string to minutes since midnight."""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except (ValueError, AttributeError):
            return 0
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to HH:MM string."""
        minutes = minutes % (24 * 60)
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def get_current_session(self, current_time: Optional[datetime] = None) -> SessionType:
        """
        Get the current active session type.
        
        Args:
            current_time: Optional datetime to check (defaults to current IST time)
            
        Returns:
            SessionType enum value
        """
        if current_time is None:
            current_time = self.get_current_ist_time()
        
        current_minutes = current_time.hour * 60 + current_time.minute
        
        for session_id, config in self.sessions.items():
            start_mins = self._time_to_minutes(config.start_time)
            end_mins = self._time_to_minutes(config.end_time)
            
            if start_mins > end_mins:
                if current_minutes >= start_mins or current_minutes < end_mins:
                    try:
                        return SessionType(session_id)
                    except ValueError:
                        return SessionType.NONE
            else:
                if start_mins <= current_minutes < end_mins:
                    try:
                        return SessionType(session_id)
                    except ValueError:
                        return SessionType.NONE
        
        return SessionType.NONE
    
    def get_session_info(self, current_time: Optional[datetime] = None) -> SessionInfo:
        """
        Get detailed information about the current session.
        
        Args:
            current_time: Optional datetime to check
            
        Returns:
            SessionInfo dataclass with current session details
        """
        if current_time is None:
            current_time = self.get_current_ist_time()
        
        session_type = self.get_current_session(current_time)
        current_minutes = current_time.hour * 60 + current_time.minute
        
        if session_type == SessionType.NONE:
            return SessionInfo(
                session_type=SessionType.NONE,
                session_name="No Active Session",
                start_time="--:--",
                end_time="--:--",
                allowed_symbols=[],
                time_remaining=timedelta(0),
                status=SessionStatus.INACTIVE,
                is_trading_allowed=False,
                next_session=self._get_next_session(current_minutes),
                next_session_starts_in=self._get_time_to_next_session(current_minutes)
            )
        
        config = self.sessions.get(session_type.value)
        if not config:
            return SessionInfo(
                session_type=session_type,
                session_name="Unknown",
                start_time="--:--",
                end_time="--:--",
                allowed_symbols=[],
                time_remaining=timedelta(0),
                status=SessionStatus.INACTIVE,
                is_trading_allowed=False
            )
        
        end_mins = self._time_to_minutes(config.end_time)
        start_mins = self._time_to_minutes(config.start_time)
        
        if start_mins > end_mins:
            if current_minutes >= start_mins:
                remaining_mins = (24 * 60 - current_minutes) + end_mins
            else:
                remaining_mins = end_mins - current_minutes
        else:
            remaining_mins = end_mins - current_minutes
        
        time_remaining = timedelta(minutes=max(0, remaining_mins))
        
        if remaining_mins <= 30:
            status = SessionStatus.ENDING_SOON
        else:
            status = SessionStatus.ACTIVE
        
        is_trading_allowed = (
            session_type != SessionType.DEAD_ZONE and
            len(config.allowed_symbols) > 0
        )
        
        return SessionInfo(
            session_type=session_type,
            session_name=config.name,
            start_time=config.start_time,
            end_time=config.end_time,
            allowed_symbols=config.allowed_symbols,
            time_remaining=time_remaining,
            status=status,
            is_trading_allowed=is_trading_allowed,
            next_session=self._get_next_session(current_minutes),
            next_session_starts_in=self._get_time_to_next_session(current_minutes)
        )
    
    def _get_next_session(self, current_minutes: int) -> Optional[str]:
        """Get the name of the next session."""
        session_order = ["asian", "london", "overlap", "ny_late", "dead_zone"]
        
        for session_id in session_order:
            config = self.sessions.get(session_id)
            if not config:
                continue
            
            start_mins = self._time_to_minutes(config.start_time)
            
            if start_mins > current_minutes:
                return config.name
        
        first_config = self.sessions.get(session_order[0])
        return first_config.name if first_config else None
    
    def _get_time_to_next_session(self, current_minutes: int) -> Optional[timedelta]:
        """Get time until the next session starts."""
        session_order = ["asian", "london", "overlap", "ny_late", "dead_zone"]
        
        for session_id in session_order:
            config = self.sessions.get(session_id)
            if not config:
                continue
            
            start_mins = self._time_to_minutes(config.start_time)
            
            if start_mins > current_minutes:
                return timedelta(minutes=start_mins - current_minutes)
        
        first_config = self.sessions.get(session_order[0])
        if first_config:
            start_mins = self._time_to_minutes(first_config.start_time)
            return timedelta(minutes=(24 * 60 - current_minutes) + start_mins)
        
        return None
    
    def check_trade_allowed(self, symbol: str, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Check if trading the symbol is allowed based on current session.
        
        Args:
            symbol: Trading symbol to check
            current_time: Optional datetime to check
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        if not self.master_switch:
            self.stats['trades_allowed'] += 1
            return True, "Master switch OFF - all trades allowed"
        
        if current_time is None:
            current_time = self.get_current_ist_time()
        
        session_type = self.get_current_session(current_time)
        
        if session_type == SessionType.NONE:
            self.stats['trades_blocked'] += 1
            return False, "No active session"
        
        if session_type == SessionType.DEAD_ZONE:
            self.stats['trades_blocked'] += 1
            return False, "Dead Zone - trading disabled"
        
        config = self.sessions.get(session_type.value)
        if not config:
            self.stats['trades_blocked'] += 1
            return False, "Session configuration not found"
        
        symbol_upper = symbol.upper()
        if symbol_upper in config.allowed_symbols:
            self.stats['trades_allowed'] += 1
            return True, f"Allowed in {config.name}"
        else:
            self.stats['trades_blocked'] += 1
            return False, f"{symbol} not allowed in {config.name}"
    
    def get_allowed_symbols(self, current_time: Optional[datetime] = None) -> List[str]:
        """Get list of symbols allowed for trading in current session."""
        if not self.master_switch:
            return self.ALL_SYMBOLS.copy()
        
        session_type = self.get_current_session(current_time)
        
        if session_type == SessionType.NONE or session_type == SessionType.DEAD_ZONE:
            return []
        
        config = self.sessions.get(session_type.value)
        return config.allowed_symbols.copy() if config else []
    
    def toggle_master_switch(self) -> bool:
        """Toggle master switch and return new state."""
        self.master_switch = not self.master_switch
        self.save_config()
        self.logger.info(f"Master switch toggled to: {self.master_switch}")
        return self.master_switch
    
    def adjust_session_time(self, session_id: str, field: str, delta_minutes: int) -> bool:
        """
        Adjust session start or end time.
        
        Args:
            session_id: Session identifier
            field: 'start_time' or 'end_time'
            delta_minutes: Minutes to adjust (+/-)
            
        Returns:
            True if successful
        """
        if session_id not in self.sessions:
            return False
        
        config = self.sessions[session_id]
        
        if field == 'start_time':
            current_mins = self._time_to_minutes(config.start_time)
            new_mins = (current_mins + delta_minutes) % (24 * 60)
            config.start_time = self._minutes_to_time(new_mins)
        elif field == 'end_time':
            current_mins = self._time_to_minutes(config.end_time)
            new_mins = (current_mins + delta_minutes) % (24 * 60)
            config.end_time = self._minutes_to_time(new_mins)
        else:
            return False
        
        self.save_config()
        return True
    
    def toggle_symbol(self, session_id: str, symbol: str) -> bool:
        """Toggle symbol ON/OFF for a session."""
        if session_id not in self.sessions:
            return False
        
        config = self.sessions[session_id]
        symbol_upper = symbol.upper()
        
        if symbol_upper in config.allowed_symbols:
            config.allowed_symbols.remove(symbol_upper)
        else:
            config.allowed_symbols.append(symbol_upper)
        
        self.save_config()
        return True
    
    def check_session_transitions(self) -> Dict[str, Any]:
        """
        Check for session transitions and return alerts.
        
        Returns:
            Dictionary with transition alerts
        """
        current_time = self.get_current_ist_time()
        current_session = self.get_current_session(current_time)
        current_minutes = current_time.hour * 60 + current_time.minute
        
        alerts = {
            'session_started': None,
            'session_ending': None,
            'force_close_required': False,
            'advance_alerts': []
        }
        
        if self.last_session != current_session.value:
            alerts['session_started'] = current_session.value
            self.last_session = current_session.value
            self.stats['session_changes'] += 1
            
            self._generate_alert(
                alert_type='session_change',
                session_id=current_session.value,
                message=f"Session changed to {current_session.value}"
            )
        
        for session_id, config in self.sessions.items():
            if not config.advance_alert_enabled:
                continue
            
            start_mins = self._time_to_minutes(config.start_time)
            alert_mins = config.advance_alert_minutes
            
            alert_trigger_mins = (start_mins - alert_mins) % (24 * 60)
            
            if abs(current_minutes - alert_trigger_mins) < 1:
                alert_key = f"{session_id}_{current_time.strftime('%Y%m%d')}"
                if alert_key not in self.alert_history:
                    alerts['advance_alerts'].append({
                        'session': session_id,
                        'starts_in_minutes': alert_mins
                    })
                    self.alert_history.append(alert_key)
                    
                    self._generate_alert(
                        alert_type='advance_alert',
                        session_id=session_id,
                        message=f"{config.name} starts in {alert_mins} minutes"
                    )
        
        if current_session != SessionType.NONE:
            config = self.sessions.get(current_session.value)
            if config and config.force_close_enabled:
                end_mins = self._time_to_minutes(config.end_time)
                
                if abs(current_minutes - (end_mins - 1)) < 1:
                    alerts['force_close_required'] = True
                    
                    self._generate_alert(
                        alert_type='force_close',
                        session_id=current_session.value,
                        message=f"Force close required - {config.name} ending"
                    )
        
        return alerts
    
    def _generate_alert(self, alert_type: str, session_id: str, message: str) -> SessionAlert:
        """Generate a session alert."""
        import uuid
        
        alert = SessionAlert(
            alert_id=str(uuid.uuid4())[:8],
            alert_type=alert_type,
            session_id=session_id,
            message=message,
            timestamp=self.get_current_ist_time()
        )
        
        self.alerts.append(alert)
        self.stats['alerts_generated'] += 1
        
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        if self._alert_callback:
            try:
                self._alert_callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
        
        return alert
    
    def set_alert_callback(self, callback: Callable) -> None:
        """Set callback function for session alerts."""
        self._alert_callback = callback
    
    def get_session_status_text(self) -> str:
        """Generate status text for Telegram display."""
        current_time = self.get_current_ist_time()
        session_info = self.get_session_info(current_time)
        
        time_str, date_str = self.format_ist_datetime(current_time)
        
        if session_info.session_type == SessionType.DEAD_ZONE:
            session_emoji = ""
            session_status = "DEAD ZONE"
        elif session_info.session_type == SessionType.NONE:
            session_emoji = ""
            session_status = "NO SESSION"
        else:
            session_emoji = ""
            session_status = session_info.session_name.upper()
        
        allowed_symbols = session_info.allowed_symbols
        if allowed_symbols:
            symbols_str = ", ".join(allowed_symbols[:5])
            if len(allowed_symbols) > 5:
                symbols_str += f" +{len(allowed_symbols) - 5} more"
        else:
            symbols_str = "None"
        
        status_text = (
            f"{time_str} | {date_str}\n"
            f"{session_emoji} {session_status} | Active Pairs: {symbols_str}"
        )
        
        return status_text
    
    def get_header_session_panel(self) -> Dict[str, str]:
        """
        Get session panel data for sticky header.
        
        Returns:
            Dictionary with formatted session panel data
        """
        current_time = self.get_current_ist_time()
        session_info = self.get_session_info(current_time)
        
        time_str = current_time.strftime("%H:%M:%S")
        date_str = current_time.strftime("%d %b %Y")
        
        if session_info.session_type == SessionType.DEAD_ZONE:
            session_line = " DEAD ZONE - Trading Disabled"
            status_color = "red"
        elif session_info.session_type == SessionType.NONE:
            session_line = " No Active Session"
            status_color = "yellow"
        else:
            session_line = f" {session_info.session_name.upper()}"
            status_color = "green"
        
        allowed_symbols = session_info.allowed_symbols
        if allowed_symbols:
            pairs_line = ", ".join(allowed_symbols)
        else:
            pairs_line = "No pairs available"
        
        remaining = session_info.time_remaining
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        time_remaining_str = f"{hours}h {minutes}m"
        
        return {
            'time': time_str,
            'date': date_str,
            'session': session_line,
            'status_color': status_color,
            'active_pairs': pairs_line,
            'time_remaining': time_remaining_str,
            'is_trading_allowed': session_info.is_trading_allowed,
            'next_session': session_info.next_session or "Unknown"
        }
    
    async def start_monitoring(self, check_interval: int = 60) -> None:
        """Start background session monitoring."""
        self._running = True
        self.logger.info("Starting session monitoring...")
        
        while self._running:
            try:
                self.check_session_transitions()
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Session monitoring error: {e}")
                await asyncio.sleep(check_interval)
    
    async def start(self) -> None:
        """Start the session manager."""
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self.start_monitoring())
            self.logger.info("Session manager started")
    
    async def stop(self) -> None:
        """Stop the session manager."""
        self._running = False
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Session manager stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session manager statistics."""
        return {
            **self.stats,
            'master_switch': self.master_switch,
            'active_sessions': len(self.sessions),
            'total_alerts': len(self.alerts),
            'current_session': self.get_current_session().value
        }


def create_session_manager(config_path: Optional[str] = None) -> ForexSessionManager:
    """Factory function to create a ForexSessionManager instance."""
    return ForexSessionManager(config_path=config_path)
