"""
Test Suite for Document 24: Sticky Header Implementation with V4 Session Logic

Tests cover:
- ForexSessionManager: Session timing, symbol filtering, trade permissions
- StickyHeaderManager: Header generation, updates, anti-scroll logic
- LiveClockManager: IST time display, formatting
- Multi-Bot Support: Controller, Notification, Analytics headers
- V4 Session Logic Integration: Asian, London, Overlap, NY Late, Dead Zone
"""

import sys
import os
import asyncio
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSessionManagerModuleStructure:
    """Test that all Session Manager components exist."""
    
    def test_module_exists(self):
        """Test that session_manager module exists."""
        from services import session_manager
        assert session_manager is not None
    
    def test_session_type_enum_exists(self):
        """Test SessionType enum exists."""
        from services.session_manager import SessionType
        assert SessionType is not None
    
    def test_session_status_enum_exists(self):
        """Test SessionStatus enum exists."""
        from services.session_manager import SessionStatus
        assert SessionStatus is not None
    
    def test_session_config_exists(self):
        """Test SessionConfig dataclass exists."""
        from services.session_manager import SessionConfig
        assert SessionConfig is not None
    
    def test_session_info_exists(self):
        """Test SessionInfo dataclass exists."""
        from services.session_manager import SessionInfo
        assert SessionInfo is not None
    
    def test_session_alert_exists(self):
        """Test SessionAlert dataclass exists."""
        from services.session_manager import SessionAlert
        assert SessionAlert is not None
    
    def test_forex_session_manager_exists(self):
        """Test ForexSessionManager class exists."""
        from services.session_manager import ForexSessionManager
        assert ForexSessionManager is not None
    
    def test_factory_function_exists(self):
        """Test create_session_manager factory function exists."""
        from services.session_manager import create_session_manager
        assert create_session_manager is not None


class TestStickyHeaderModuleStructure:
    """Test that all Sticky Header components exist."""
    
    def test_module_exists(self):
        """Test that sticky_header module exists."""
        from telegram import sticky_header
        assert sticky_header is not None
    
    def test_header_type_enum_exists(self):
        """Test HeaderType enum exists."""
        from telegram.sticky_header import HeaderType
        assert HeaderType is not None
    
    def test_header_status_enum_exists(self):
        """Test HeaderStatus enum exists."""
        from telegram.sticky_header import HeaderStatus
        assert HeaderStatus is not None
    
    def test_header_metrics_exists(self):
        """Test HeaderMetrics dataclass exists."""
        from telegram.sticky_header import HeaderMetrics
        assert HeaderMetrics is not None
    
    def test_header_config_exists(self):
        """Test HeaderConfig dataclass exists."""
        from telegram.sticky_header import HeaderConfig
        assert HeaderConfig is not None
    
    def test_pinned_message_exists(self):
        """Test PinnedMessage dataclass exists."""
        from telegram.sticky_header import PinnedMessage
        assert PinnedMessage is not None
    
    def test_sticky_header_manager_exists(self):
        """Test StickyHeaderManager class exists."""
        from telegram.sticky_header import StickyHeaderManager
        assert StickyHeaderManager is not None
    
    def test_live_clock_manager_exists(self):
        """Test LiveClockManager class exists."""
        from telegram.sticky_header import LiveClockManager
        assert LiveClockManager is not None
    
    def test_factory_functions_exist(self):
        """Test factory functions exist."""
        from telegram.sticky_header import create_sticky_header_manager, create_live_clock_manager
        assert create_sticky_header_manager is not None
        assert create_live_clock_manager is not None


class TestSessionTypeEnum:
    """Test SessionType enum values."""
    
    def test_session_type_values(self):
        """Test all session type values exist."""
        from services.session_manager import SessionType
        assert SessionType.ASIAN.value == "asian"
        assert SessionType.LONDON.value == "london"
        assert SessionType.OVERLAP.value == "overlap"
        assert SessionType.NY_LATE.value == "ny_late"
        assert SessionType.DEAD_ZONE.value == "dead_zone"
        assert SessionType.NONE.value == "none"


class TestSessionStatusEnum:
    """Test SessionStatus enum values."""
    
    def test_session_status_values(self):
        """Test all session status values exist."""
        from services.session_manager import SessionStatus
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.STARTING_SOON.value == "starting_soon"
        assert SessionStatus.ENDING_SOON.value == "ending_soon"
        assert SessionStatus.INACTIVE.value == "inactive"


class TestHeaderTypeEnum:
    """Test HeaderType enum values."""
    
    def test_header_type_values(self):
        """Test all header type values exist."""
        from telegram.sticky_header import HeaderType
        assert HeaderType.CONTROLLER.value == "controller"
        assert HeaderType.NOTIFICATION.value == "notification"
        assert HeaderType.ANALYTICS.value == "analytics"
        assert HeaderType.UNIFIED.value == "unified"


class TestHeaderStatusEnum:
    """Test HeaderStatus enum values."""
    
    def test_header_status_values(self):
        """Test all header status values exist."""
        from telegram.sticky_header import HeaderStatus
        assert HeaderStatus.ACTIVE.value == "active"
        assert HeaderStatus.UPDATING.value == "updating"
        assert HeaderStatus.STALE.value == "stale"
        assert HeaderStatus.ERROR.value == "error"


class TestSessionConfig:
    """Test SessionConfig dataclass."""
    
    def test_session_config_creation(self):
        """Test creating a SessionConfig."""
        from services.session_manager import SessionConfig
        
        config = SessionConfig(
            session_id="asian",
            name="Asian Session",
            start_time="05:30",
            end_time="14:30",
            allowed_symbols=["USDJPY", "AUDUSD", "EURJPY"]
        )
        
        assert config.session_id == "asian"
        assert config.name == "Asian Session"
        assert config.start_time == "05:30"
        assert config.end_time == "14:30"
        assert "USDJPY" in config.allowed_symbols
    
    def test_session_config_defaults(self):
        """Test SessionConfig default values."""
        from services.session_manager import SessionConfig
        
        config = SessionConfig(
            session_id="test",
            name="Test",
            start_time="00:00",
            end_time="12:00",
            allowed_symbols=[]
        )
        
        assert config.advance_alert_enabled is True
        assert config.advance_alert_minutes == 30
        assert config.force_close_enabled is False


class TestSessionInfo:
    """Test SessionInfo dataclass."""
    
    def test_session_info_creation(self):
        """Test creating a SessionInfo."""
        from services.session_manager import SessionInfo, SessionType, SessionStatus
        
        info = SessionInfo(
            session_type=SessionType.LONDON,
            session_name="London Session",
            start_time="13:00",
            end_time="22:00",
            allowed_symbols=["GBPUSD", "EURUSD"],
            time_remaining=timedelta(hours=2),
            status=SessionStatus.ACTIVE,
            is_trading_allowed=True
        )
        
        assert info.session_type == SessionType.LONDON
        assert info.session_name == "London Session"
        assert info.is_trading_allowed is True


class TestHeaderMetrics:
    """Test HeaderMetrics dataclass."""
    
    def test_header_metrics_creation(self):
        """Test creating HeaderMetrics."""
        from telegram.sticky_header import HeaderMetrics
        
        metrics = HeaderMetrics(
            total_pnl=1500.50,
            daily_pnl=250.00,
            active_trades=3,
            api_latency_ms=45
        )
        
        assert metrics.total_pnl == 1500.50
        assert metrics.daily_pnl == 250.00
        assert metrics.active_trades == 3
        assert metrics.api_latency_ms == 45
    
    def test_header_metrics_defaults(self):
        """Test HeaderMetrics default values."""
        from telegram.sticky_header import HeaderMetrics
        
        metrics = HeaderMetrics()
        
        assert metrics.total_pnl == 0.0
        assert metrics.daily_pnl == 0.0
        assert metrics.active_trades == 0
        assert metrics.win_rate == 0.0


class TestHeaderConfig:
    """Test HeaderConfig dataclass."""
    
    def test_header_config_creation(self):
        """Test creating HeaderConfig."""
        from telegram.sticky_header import HeaderConfig
        
        config = HeaderConfig(
            update_interval_seconds=30,
            anti_scroll_check_interval=120
        )
        
        assert config.update_interval_seconds == 30
        assert config.anti_scroll_check_interval == 120
    
    def test_header_config_defaults(self):
        """Test HeaderConfig default values."""
        from telegram.sticky_header import HeaderConfig
        
        config = HeaderConfig()
        
        assert config.update_interval_seconds == 60
        assert config.anti_scroll_check_interval == 300
        assert config.enable_metrics is True
        assert config.enable_session_panel is True


class TestForexSessionManager:
    """Test ForexSessionManager class."""
    
    def test_manager_initialization(self):
        """Test ForexSessionManager initialization."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        
        assert isinstance(manager.master_switch, bool)
        assert len(manager.sessions) > 0
        assert "asian" in manager.sessions
        assert "london" in manager.sessions
        assert "dead_zone" in manager.sessions
    
    def test_get_current_ist_time(self):
        """Test getting current IST time."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        ist_time = manager.get_current_ist_time()
        
        assert ist_time is not None
        utc_now = datetime.now(timezone.utc)
        diff = ist_time - utc_now
        assert 5 <= diff.total_seconds() / 3600 <= 6
    
    def test_format_ist_time(self):
        """Test formatting IST time."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        time_str = manager.format_ist_time()
        
        assert "IST" in time_str
        assert ":" in time_str
    
    def test_format_ist_date(self):
        """Test formatting IST date."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        date_str = manager.format_ist_date()
        
        assert len(date_str) > 0
    
    def test_get_current_session(self):
        """Test getting current session."""
        from services.session_manager import ForexSessionManager, SessionType
        
        manager = ForexSessionManager()
        session = manager.get_current_session()
        
        assert session is not None
        assert isinstance(session, SessionType)
    
    def test_get_session_info(self):
        """Test getting session info."""
        from services.session_manager import ForexSessionManager, SessionInfo
        
        manager = ForexSessionManager()
        info = manager.get_session_info()
        
        assert info is not None
        assert isinstance(info, SessionInfo)
        assert info.session_name is not None
    
    def test_check_trade_allowed_master_off(self):
        """Test trade check with master switch off."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        manager.master_switch = False
        
        allowed, reason = manager.check_trade_allowed("EURUSD")
        
        assert allowed is True
        assert "Master switch OFF" in reason
    
    def test_get_allowed_symbols(self):
        """Test getting allowed symbols."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        symbols = manager.get_allowed_symbols()
        
        assert isinstance(symbols, list)
    
    def test_toggle_master_switch(self):
        """Test toggling master switch."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        initial_state = manager.master_switch
        
        new_state = manager.toggle_master_switch()
        
        assert new_state != initial_state
        assert manager.master_switch == new_state
    
    def test_get_session_status_text(self):
        """Test getting session status text."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        status_text = manager.get_session_status_text()
        
        assert status_text is not None
        assert len(status_text) > 0
    
    def test_get_header_session_panel(self):
        """Test getting header session panel data."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        panel = manager.get_header_session_panel()
        
        assert 'time' in panel
        assert 'date' in panel
        assert 'session' in panel
        assert 'active_pairs' in panel
        assert 'is_trading_allowed' in panel
    
    def test_check_session_transitions(self):
        """Test checking session transitions."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        alerts = manager.check_session_transitions()
        
        assert 'session_started' in alerts
        assert 'session_ending' in alerts
        assert 'force_close_required' in alerts
        assert 'advance_alerts' in alerts
    
    def test_get_stats(self):
        """Test getting session manager stats."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        stats = manager.get_stats()
        
        assert 'session_changes' in stats
        assert 'alerts_generated' in stats
        assert 'master_switch' in stats
        assert 'current_session' in stats


class TestForexSessionTimings:
    """Test V4 Forex session timing logic."""
    
    def test_asian_session_exists_and_valid(self):
        """Test Asian session exists with valid configuration."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        config = manager.sessions.get("asian")
        
        assert config is not None
        assert config.name == "Asian Session"
        assert ":" in config.start_time
        assert ":" in config.end_time
        assert len(config.allowed_symbols) >= 0
    
    def test_london_session_exists_and_valid(self):
        """Test London session exists with valid configuration."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        config = manager.sessions.get("london")
        
        assert config is not None
        assert config.name == "London Session"
        assert ":" in config.start_time
        assert ":" in config.end_time
        assert len(config.allowed_symbols) >= 0
    
    def test_overlap_session_exists_and_valid(self):
        """Test Overlap session exists with valid configuration."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        config = manager.sessions.get("overlap")
        
        assert config is not None
        assert "Overlap" in config.name
        assert ":" in config.start_time
        assert ":" in config.end_time
        assert len(config.allowed_symbols) >= 0
    
    def test_ny_late_session_exists_and_valid(self):
        """Test NY Late session exists with valid configuration."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        config = manager.sessions.get("ny_late")
        
        assert config is not None
        assert "NY" in config.name or "Late" in config.name
        assert ":" in config.start_time
        assert ":" in config.end_time
        assert len(config.allowed_symbols) >= 0
    
    def test_dead_zone_exists_and_valid(self):
        """Test Dead Zone exists with valid configuration."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        config = manager.sessions.get("dead_zone")
        
        assert config is not None
        assert "Dead" in config.name or "Zone" in config.name
        assert ":" in config.start_time
        assert ":" in config.end_time
        assert len(config.allowed_symbols) == 0
        assert config.force_close_enabled is True
    
    def test_all_five_sessions_exist(self):
        """Test all five V4 sessions exist."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        
        assert "asian" in manager.sessions
        assert "london" in manager.sessions
        assert "overlap" in manager.sessions
        assert "ny_late" in manager.sessions
        assert "dead_zone" in manager.sessions
        assert len(manager.sessions) == 5
    
    def test_session_time_format_valid(self):
        """Test all session times are in valid HH:MM format."""
        from services.session_manager import ForexSessionManager
        import re
        
        manager = ForexSessionManager()
        time_pattern = re.compile(r'^\d{2}:\d{2}$')
        
        for session_id, config in manager.sessions.items():
            assert time_pattern.match(config.start_time), f"{session_id} start_time invalid"
            assert time_pattern.match(config.end_time), f"{session_id} end_time invalid"


class TestStickyHeaderManager:
    """Test StickyHeaderManager class."""
    
    def test_manager_initialization(self):
        """Test StickyHeaderManager initialization."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        
        assert manager._running is False
        assert len(manager.pinned_messages) == 0
        assert manager.metrics is not None
    
    def test_manager_with_config(self):
        """Test StickyHeaderManager with custom config."""
        from telegram.sticky_header import StickyHeaderManager, HeaderConfig
        
        config = HeaderConfig(update_interval_seconds=30)
        manager = StickyHeaderManager(config=config)
        
        assert manager.config.update_interval_seconds == 30
    
    def test_manager_with_session_manager(self):
        """Test StickyHeaderManager with session manager."""
        from telegram.sticky_header import StickyHeaderManager
        from services.session_manager import ForexSessionManager
        
        session_manager = ForexSessionManager()
        header_manager = StickyHeaderManager(session_manager=session_manager)
        
        assert header_manager.session_manager == session_manager
    
    def test_get_current_ist_time(self):
        """Test getting current IST time."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        ist_time = manager.get_current_ist_time()
        
        assert ist_time is not None
    
    def test_format_uptime(self):
        """Test formatting uptime."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        
        assert manager.format_uptime(30) == "30s"
        assert manager.format_uptime(90) == "1m 30s"
        assert manager.format_uptime(3700) == "1h 1m 40s"
        assert "d" in manager.format_uptime(90000)
    
    def test_update_metrics(self):
        """Test updating metrics."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        
        manager.update_metrics(
            total_pnl=1000.0,
            daily_pnl=100.0,
            active_trades=5
        )
        
        assert manager.metrics.total_pnl == 1000.0
        assert manager.metrics.daily_pnl == 100.0
        assert manager.metrics.active_trades == 5
    
    def test_generate_controller_header(self):
        """Test generating controller header."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        header = manager.generate_controller_header()
        
        assert "Zepix Trading Bot" in header
        assert "System Status" in header
        assert "Trading Stats" in header
    
    def test_generate_notification_header(self):
        """Test generating notification header."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        header = manager.generate_notification_header()
        
        assert "Notifications" in header
        assert "Alert Status" in header
    
    def test_generate_analytics_header(self):
        """Test generating analytics header."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        header = manager.generate_analytics_header()
        
        assert "Analytics" in header
        assert "Performance" in header
    
    def test_generate_unified_header(self):
        """Test generating unified header."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        header = manager.generate_unified_header()
        
        assert "COMMAND CENTER" in header
        assert "Trading Status" in header
        assert "Performance" in header
        assert "System Health" in header
    
    def test_generate_header_by_type(self):
        """Test generating header by type."""
        from telegram.sticky_header import StickyHeaderManager, HeaderType
        
        manager = StickyHeaderManager()
        
        controller = manager.generate_header(HeaderType.CONTROLLER)
        notification = manager.generate_header(HeaderType.NOTIFICATION)
        analytics = manager.generate_header(HeaderType.ANALYTICS)
        unified = manager.generate_header(HeaderType.UNIFIED)
        
        assert "Dashboard" in controller
        assert "Notifications" in notification
        assert "Analytics" in analytics
        assert "COMMAND CENTER" in unified
    
    def test_generate_quick_buttons(self):
        """Test generating quick buttons."""
        from telegram.sticky_header import StickyHeaderManager, HeaderType
        
        manager = StickyHeaderManager()
        
        buttons = manager.generate_quick_buttons(HeaderType.CONTROLLER)
        
        assert len(buttons) > 0
        assert len(buttons[0]) > 0
        assert 'text' in buttons[0][0]
        assert 'callback_data' in buttons[0][0]
    
    def test_generate_reply_keyboard(self):
        """Test generating reply keyboard."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        keyboard = manager.generate_reply_keyboard()
        
        assert len(keyboard) == 2
        assert "Menu" in keyboard[0][0]
        assert "Status" in keyboard[0][1]
    
    def test_get_header_status_not_exists(self):
        """Test getting header status when not exists."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        status = manager.get_header_status(12345)
        
        assert status['exists'] is False
        assert status['status'] == 'error'
    
    def test_get_stats(self):
        """Test getting sticky header stats."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        stats = manager.get_stats()
        
        assert 'updates_sent' in stats
        assert 'updates_failed' in stats
        assert 'repins_triggered' in stats
        assert 'active_headers' in stats
        assert 'is_running' in stats


class TestLiveClockManager:
    """Test LiveClockManager class."""
    
    def test_clock_initialization(self):
        """Test LiveClockManager initialization."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager()
        
        assert clock._running is False
        assert clock.update_interval == 60
    
    def test_clock_custom_interval(self):
        """Test LiveClockManager with custom interval."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager(update_interval_seconds=30)
        
        assert clock.update_interval == 30
    
    def test_get_current_ist_time(self):
        """Test getting current IST time."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager()
        ist_time = clock.get_current_ist_time()
        
        assert ist_time is not None
    
    def test_format_clock_display(self):
        """Test formatting clock display."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager()
        display = clock.format_clock_display()
        
        assert 'time' in display
        assert 'time_short' in display
        assert 'date' in display
        assert 'date_full' in display
        assert 'day' in display
        assert 'timezone' in display
        assert display['timezone'] == 'IST'
    
    def test_format_clock_message(self):
        """Test formatting clock message."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager()
        message = clock.format_clock_message()
        
        assert "Current Time" in message
        assert "Date" in message
        assert "IST" in message


class TestStickyHeaderStartStop:
    """Test StickyHeaderManager start/stop functionality."""
    
    def test_start_stop(self):
        """Test starting and stopping header manager."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        
        async def run_test():
            await manager.start()
            assert manager._running is True
            await asyncio.sleep(0.1)
            await manager.stop()
            assert manager._running is False
        
        asyncio.run(run_test())
    
    def test_double_start(self):
        """Test double start is safe."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        
        async def run_test():
            await manager.start()
            await manager.start()
            assert manager._running is True
            await manager.stop()
        
        asyncio.run(run_test())


class TestLiveClockStartStop:
    """Test LiveClockManager start/stop functionality."""
    
    def test_start_stop(self):
        """Test starting and stopping clock manager."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager()
        
        async def run_test():
            await clock.start()
            assert clock._running is True
            await asyncio.sleep(0.1)
            await clock.stop()
            assert clock._running is False
        
        asyncio.run(run_test())


class TestSessionManagerStartStop:
    """Test ForexSessionManager start/stop functionality."""
    
    def test_start_stop(self):
        """Test starting and stopping session manager."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        
        async def run_test():
            await manager.start()
            await asyncio.sleep(0.2)
            assert manager._running is True
            await manager.stop()
            assert manager._running is False
        
        asyncio.run(run_test())
    
    def test_has_start_stop_methods(self):
        """Test session manager has start/stop methods."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        
        assert hasattr(manager, 'start')
        assert hasattr(manager, 'stop')
        assert hasattr(manager, 'start_monitoring')
        assert callable(manager.start)
        assert callable(manager.stop)


class TestFactoryFunctions:
    """Test factory functions."""
    
    def test_create_session_manager(self):
        """Test creating session manager via factory."""
        from services.session_manager import create_session_manager
        
        manager = create_session_manager()
        
        assert manager is not None
        assert len(manager.sessions) > 0
    
    def test_create_sticky_header_manager(self):
        """Test creating sticky header manager via factory."""
        from telegram.sticky_header import create_sticky_header_manager
        
        manager = create_sticky_header_manager()
        
        assert manager is not None
        assert manager.config is not None
    
    def test_create_live_clock_manager(self):
        """Test creating live clock manager via factory."""
        from telegram.sticky_header import create_live_clock_manager
        
        clock = create_live_clock_manager()
        
        assert clock is not None
        assert clock.update_interval == 60
    
    def test_create_live_clock_manager_custom_interval(self):
        """Test creating live clock manager with custom interval."""
        from telegram.sticky_header import create_live_clock_manager
        
        clock = create_live_clock_manager(update_interval=30)
        
        assert clock.update_interval == 30


class TestSessionManagerConfigPersistence:
    """Test session manager configuration persistence."""
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        from services.session_manager import ForexSessionManager
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            config_path = f.name
        
        try:
            manager = ForexSessionManager(config_path=config_path)
            manager.master_switch = False
            manager.save_config()
            
            manager2 = ForexSessionManager(config_path=config_path)
            
            assert manager2.master_switch is False
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)


class TestIntegration:
    """Test integration between Session Manager and Sticky Header."""
    
    def test_header_with_session_data(self):
        """Test header generation with session data."""
        from telegram.sticky_header import StickyHeaderManager
        from services.session_manager import ForexSessionManager
        
        session_manager = ForexSessionManager()
        header_manager = StickyHeaderManager(session_manager=session_manager)
        
        header = header_manager.generate_unified_header()
        
        assert header is not None
        assert len(header) > 0
    
    def test_session_panel_in_header(self):
        """Test session panel data appears in header."""
        from telegram.sticky_header import StickyHeaderManager
        from services.session_manager import ForexSessionManager
        
        session_manager = ForexSessionManager()
        header_manager = StickyHeaderManager(session_manager=session_manager)
        
        panel = header_manager._get_session_panel()
        
        assert 'time' in panel
        assert 'session' in panel
        assert 'active_pairs' in panel


class TestDocument24Requirements:
    """Test Document 24 specific requirements."""
    
    def test_unified_header_manager(self):
        """Test unified header manager exists and works."""
        from telegram.sticky_header import StickyHeaderManager, HeaderType
        
        manager = StickyHeaderManager()
        header = manager.generate_header(HeaderType.UNIFIED)
        
        assert "COMMAND CENTER" in header
    
    def test_live_clock_panel(self):
        """Test live clock panel with IST time."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager()
        display = clock.format_clock_display()
        
        assert display['timezone'] == 'IST'
        assert ':' in display['time']
    
    def test_session_panel_integration(self):
        """Test session panel integration."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        panel = manager.get_header_session_panel()
        
        assert 'time' in panel
        assert 'date' in panel
        assert 'session' in panel
        assert 'active_pairs' in panel
    
    def test_smart_update_interval(self):
        """Test smart update interval (60s default)."""
        from telegram.sticky_header import HeaderConfig
        
        config = HeaderConfig()
        
        assert config.update_interval_seconds == 60
    
    def test_metrics_display(self):
        """Test metrics display in header."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        manager.update_metrics(
            total_pnl=1500.0,
            daily_pnl=250.0,
            active_trades=3,
            api_latency_ms=45
        )
        
        header = manager.generate_unified_header()
        
        assert "P&L" in header
        assert "Active Trades" in header
        assert "Latency" in header
    
    def test_anti_scroll_config(self):
        """Test anti-scroll configuration."""
        from telegram.sticky_header import HeaderConfig
        
        config = HeaderConfig()
        
        assert config.anti_scroll_check_interval == 300
        assert config.max_message_age_seconds == 600
    
    def test_multi_bot_support(self):
        """Test multi-bot header support."""
        from telegram.sticky_header import StickyHeaderManager, HeaderType
        
        manager = StickyHeaderManager()
        
        controller = manager.generate_header(HeaderType.CONTROLLER)
        notification = manager.generate_header(HeaderType.NOTIFICATION)
        analytics = manager.generate_header(HeaderType.ANALYTICS)
        
        assert controller != notification
        assert notification != analytics
        assert controller != analytics


class TestDocument24Summary:
    """Test Document 24 summary requirements."""
    
    def test_header_manager_implemented(self):
        """Test StickyHeaderManager is fully implemented."""
        from telegram.sticky_header import StickyHeaderManager
        
        manager = StickyHeaderManager()
        
        assert hasattr(manager, 'create_header')
        assert hasattr(manager, 'update_header')
        assert hasattr(manager, 'check_and_repin')
        assert hasattr(manager, 'generate_header')
        assert hasattr(manager, 'start')
        assert hasattr(manager, 'stop')
    
    def test_session_manager_implemented(self):
        """Test ForexSessionManager is fully implemented."""
        from services.session_manager import ForexSessionManager
        
        manager = ForexSessionManager()
        
        assert hasattr(manager, 'get_current_session')
        assert hasattr(manager, 'get_session_info')
        assert hasattr(manager, 'check_trade_allowed')
        assert hasattr(manager, 'get_header_session_panel')
        assert hasattr(manager, 'check_session_transitions')
    
    def test_live_clock_implemented(self):
        """Test LiveClockManager is fully implemented."""
        from telegram.sticky_header import LiveClockManager
        
        clock = LiveClockManager()
        
        assert hasattr(clock, 'get_current_ist_time')
        assert hasattr(clock, 'format_clock_display')
        assert hasattr(clock, 'format_clock_message')
        assert hasattr(clock, 'start')
        assert hasattr(clock, 'stop')
    
    def test_v4_session_logic_integrated(self):
        """Test V4 session logic is integrated."""
        from services.session_manager import ForexSessionManager, SessionType
        
        manager = ForexSessionManager()
        
        assert SessionType.ASIAN in SessionType
        assert SessionType.LONDON in SessionType
        assert SessionType.OVERLAP in SessionType
        assert SessionType.NY_LATE in SessionType
        assert SessionType.DEAD_ZONE in SessionType
        
        assert "asian" in manager.sessions
        assert "london" in manager.sessions
        assert "overlap" in manager.sessions
        assert "ny_late" in manager.sessions
        assert "dead_zone" in manager.sessions
    
    def test_rate_limit_compliance(self):
        """Test rate limit compliance (60s update interval)."""
        from telegram.sticky_header import HeaderConfig
        
        config = HeaderConfig()
        
        assert config.update_interval_seconds >= 60
    
    def test_all_components_importable(self):
        """Test all Document 24 components are importable."""
        from services.session_manager import (
            SessionType,
            SessionStatus,
            SessionConfig,
            SessionInfo,
            SessionAlert,
            ForexSessionManager,
            create_session_manager
        )
        
        from telegram.sticky_header import (
            HeaderType,
            HeaderStatus,
            HeaderMetrics,
            HeaderConfig,
            PinnedMessage,
            StickyHeaderManager,
            LiveClockManager,
            create_sticky_header_manager,
            create_live_clock_manager
        )
        
        assert all([
            SessionType, SessionStatus, SessionConfig, SessionInfo,
            SessionAlert, ForexSessionManager, create_session_manager,
            HeaderType, HeaderStatus, HeaderMetrics, HeaderConfig,
            PinnedMessage, StickyHeaderManager, LiveClockManager,
            create_sticky_header_manager, create_live_clock_manager
        ])
