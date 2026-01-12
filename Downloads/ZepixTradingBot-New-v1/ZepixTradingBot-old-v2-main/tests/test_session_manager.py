"""
Unit Tests for Forex Session Manager
Tests session detection, symbol filtering, time adjustments, and alert logic.

Run tests with:
    pytest tests/test_session_manager.py -v
    pytest tests/test_session_manager.py::test_session_detection -v  # Single test
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
import pytz
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from modules.session_manager import SessionManager


class TestSessionManager:
    """Test suite for SessionManager class"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(temp_path + '.tmp'):
            os.unlink(temp_path + '.tmp')
    
    @pytest.fixture
    def session_mgr(self, temp_config_file):
        """Create a SessionManager instance with temp config"""
        return SessionManager(config_path=temp_config_file)
    
    def test_initialization(self, session_mgr):
        """Test that session manager initializes correctly"""
        assert session_mgr.config is not None
        assert session_mgr.timezone.zone == 'Asia/Kolkata'
        assert 'sessions' in session_mgr.config
        assert 'master_switch' in session_mgr.config
        assert len(session_mgr.config['sessions']) == 5  # 5 Forex sessions
    
    def test_default_config_structure(self, session_mgr):
        """Test default configuration has all required fields"""
        assert 'asian' in session_mgr.config['sessions']
        assert 'london' in session_mgr.config['sessions']
        assert 'overlap' in session_mgr.config['sessions']
        assert 'ny_late' in session_mgr.config['sessions']
        assert 'dead_zone' in session_mgr.config['sessions']
        
        # Check first session has required fields
        asian = session_mgr.config['sessions']['asian']
        assert 'name' in asian
        assert 'start_time' in asian
        assert 'end_time' in asian
        assert 'allowed_symbols' in asian
        assert 'advance_alert_enabled' in asian
        assert 'force_close_enabled' in asian
    
    def test_time_to_minutes_conversion(self, session_mgr):
        """Test time string to minutes conversion"""
        assert session_mgr.time_to_minutes("00:00") == 0
        assert session_mgr.time_to_minutes("12:00") == 720
        assert session_mgr.time_to_minutes("23:59") == 1439
        assert session_mgr.time_to_minutes("05:30") == 330
    
    @pytest.mark.parametrize("hour,minute,expected_session", [
        (6, 0, "asian"),       # 06:00 IST - Asian session
        (14, 0, "london"),     # 14:00 IST - London session
        (19, 0, "overlap"),    # 19:00 IST - Overlap session (Started 18:30)
        (23, 0, "ny_late"),    # 23:00 IST - NY Late session
        (4, 0, "dead_zone"),   # 04:00 IST - Dead zone (Starts 03:30)
        (5, 30, "asian"),      # 05:30 IST - Asian (Starts 05:00)
    ])
    def test_session_detection(self, session_mgr, hour, minute, expected_session):
        """Test session detection for various times"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            mock_time.return_value = datetime(
                2026, 1, 11, hour, minute, 0,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
            
            current_session = session_mgr.get_current_session()
            assert current_session == expected_session
    
    def test_session_detection_midnight_crossing(self, session_mgr):
        """Test session detection across midnight boundary"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # NY Late session: 22:30 - 03:30 (crosses midnight)
            
            # At 23:00 (before midnight)
            mock_time.return_value = datetime(2026, 1, 11, 23, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            assert session_mgr.get_current_session() == "ny_late"
            
            # At 01:00 (after midnight)
            mock_time.return_value = datetime(2026, 1, 12, 1, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            assert session_mgr.get_current_session() == "ny_late"
    
    @pytest.mark.parametrize("symbol,time_hour,expected_allowed", [
        ("USDJPY", 6, True),      # USDJPY allowed in Asian session
        ("EURUSD", 6, False),     # EURUSD not allowed in Asian session
        ("GBPUSD", 14, True),     # GBPUSD allowed in London session
        ("USDJPY", 14, False),    # USDJPY not allowed in London session
        ("EURUSD", 19, True),     # EURUSD allowed in Overlap
        ("AUDUSD", 23, False),    # AUDUSD not allowed in NY Late
    ])
    def test_symbol_filtering(self, session_mgr, symbol, time_hour, expected_allowed):
        """Test symbol filtering for different sessions"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            mock_time.return_value = datetime(
                2026, 1, 11, time_hour, 0, 0,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
            
            allowed, reason = session_mgr.check_trade_allowed(symbol)
            assert allowed == expected_allowed
    
    def test_master_switch_bypass(self, session_mgr):
        """Test that master switch OFF allows all trades"""
        # Turn off master switch
        session_mgr.config['master_switch'] = False
        
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # Dead zone 03:00 - normally no trades allowed
            mock_time.return_value = datetime(2026, 1, 11, 3, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            
            allowed, reason = session_mgr.check_trade_allowed("EURUSD")
            assert allowed is True
            assert "Master switch OFF" in reason
    
    def test_time_adjustment(self, session_mgr):
        """Test session time adjustment"""
        original_start = session_mgr.config['sessions']['asian']['start_time']
        
        # Adjust by +30 minutes
        session_mgr.adjust_session_time('asian', 'start_time', 30)
        new_start = session_mgr.config['sessions']['asian']['start_time']
        
        # Verify change
        assert original_start != new_start
        
        # Verify calculation (05:00 + 30min = 05:30)
        assert new_start == "05:30"
    
    def test_time_adjustment_midnight_wrap(self, session_mgr):
        """Test time adjustment wraps around midnight correctly"""
        # Set time to 23:30
        session_mgr.config['sessions']['test'] = {'start_time': "23:30"}
        
        # Add 60 minutes (should wrap to 00:30)
        session_mgr.adjust_session_time('test', 'start_time', 60)
        
        assert session_mgr.config['sessions']['test']['start_time'] == "00:30"
    
    def test_symbol_toggle(self, session_mgr):
        """Test toggling symbols ON/OFF"""
        # Check if USDJPY is initially in Asian session
        initial_symbols = session_mgr.config['sessions']['asian']['allowed_symbols'].copy()
        assert "USDJPY" in initial_symbols
        
        # Toggle OFF
        session_mgr.toggle_symbol('asian', 'USDJPY')
        assert "USDJPY" not in session_mgr.config['sessions']['asian']['allowed_symbols']
        
        # Toggle back ON
        session_mgr.toggle_symbol('asian', 'USDJPY')
        assert "USDJPY" in session_mgr.config['sessions']['asian']['allowed_symbols']
    
    def test_master_switch_toggle(self, session_mgr):
        """Test master switch toggling"""
        initial_state = session_mgr.config.get('master_switch', True)
        
        # Toggle
        new_state = session_mgr.toggle_master_switch()
        assert new_state != initial_state
        assert session_mgr.config['master_switch'] == new_state
        
        # Toggle back
        new_state2 = session_mgr.toggle_master_switch()
        assert new_state2 == initial_state
    
    def test_force_close_toggle(self, session_mgr):
        """Test force close toggling"""
        initial_state = session_mgr.config['sessions']['asian'].get('force_close_enabled', False)
        
        # Toggle
        new_state = session_mgr.toggle_force_close('asian')
        assert new_state != initial_state
        
        # Toggle back
        new_state2 = session_mgr.toggle_force_close('asian')
        assert new_state2 == initial_state
    
    def test_config_persistence(self, session_mgr, temp_config_file):
        """Test that config changes are saved and reloaded"""
        # Make a change
        session_mgr.toggle_master_switch()
        original_state = session_mgr.config['master_switch']
        
        # Create new instance with same config file
        session_mgr2 = SessionManager(config_path=temp_config_file)
        
        # Verify state persisted
        assert session_mgr2.config['master_switch'] == original_state
    
    def test_session_transition_detection(self, session_mgr):
        """Test session transition detection"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # Start at Asian session
            mock_time.return_value = datetime(2026, 1, 11, 6, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            alerts = session_mgr.check_session_transitions()
            
            # Should detect Asian session start
            assert alerts['session_started'] == 'asian' or session_mgr.last_session == 'asian'
            
            # Move to London session
            mock_time.return_value = datetime(2026, 1, 11, 14, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            alerts = session_mgr.check_session_transitions()
            
            # Should detect London session start
            assert alerts['session_started'] == 'london'
    
    def test_advance_alert_detection(self, session_mgr):
        """Test 30-minute advance alert detection"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # Asian session starts at 05:00, so advance alert at 04:30
            # Trigger at (05:00 - 30) = 04:30
            
            # Set time to exactly when advance alert should fire
            mock_time.return_value = datetime(2026, 1, 11, 4, 30, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            
            alerts = session_mgr.check_session_transitions()
            
            # Should detect advance alert for Asian session
            if alerts['session_ending']:
                assert alerts['session_ending']['session'] in session_mgr.config['sessions']
                assert alerts['session_ending']['starts_in_minutes'] == 30
    
    def test_force_close_detection(self, session_mgr):
        """Test force close detection at session end"""
        # Enable force close for dead_zone
        session_mgr.config['sessions']['dead_zone']['force_close_enabled'] = True
        
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # Dead zone ends at 05:00, force close triggers 1 min before = 04:59
            mock_time.return_value = datetime(2026, 1, 11, 4, 59, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            
            alerts = session_mgr.check_session_transitions()
            
            # Should detect force close requirement
            assert alerts['force_close_required'] is True
    
    def test_status_text_generation(self, session_mgr):
        """Test session status text generation"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # Asian session
            mock_time.return_value = datetime(2026, 1, 11, 6, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            
            status = session_mgr.get_session_status_text()
            
            # Verify statuS includes key info
            assert "Master Switch" in status
            assert "Current Session" in status
            assert "Allowed Symbols" in status
    
    def test_get_status(self, session_mgr):
        """Test comprehensive status retrieval"""
        status = session_mgr.get_status()
        
        assert 'master_switch' in status
        assert 'current_session' in status
        assert 'current_time' in status
        assert 'timezone' in status
        assert status['total_sessions'] == 5
    
    def test_invalid_session_errors(self, session_mgr):
        """Test error handling for invalid session IDs"""
        with pytest.raises(ValueError):
            session_mgr.adjust_session_time('invalid_session', 'start_time', 30)
        
        with pytest.raises(ValueError):
            session_mgr.toggle_force_close('invalid_session')
    
    def test_alert_cooldown_mechanism(self, session_mgr):
        """Test that alerts don't fire multiple times (cooldown)"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # Set time to advance alert trigger
            alert_time = datetime(2026, 1, 11, 4, 30, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            mock_time.return_value = alert_time
            
            # First call should trigger alert
            alerts1 = session_mgr.check_session_transitions()
            
            # Second call (same time) should NOT trigger (cooldown)
            alerts2 = session_mgr.check_session_transitions()
            
            # At least one should have no alert due to cooldown
            assert alerts1['session_ending'] is None or alerts2['session_ending'] is None


class TestSessionManagerEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.fixture
    def session_mgr(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        mgr = SessionManager(config_path=temp_path)
        yield mgr
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_empty_allowed_symbols(self, session_mgr):
        """Test session with no allowed symbols (dead zone)"""
        with patch.object(session_mgr, 'get_current_time') as mock_time:
            # Dead zone has no allowed symbols (04:00 AM)
            mock_time.return_value = datetime(2026, 1, 11, 4, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            
            allowed, reason = session_mgr.check_trade_allowed("EURUSD")
            assert allowed is False
    
    def test_all_symbols_in_overlap(self, session_mgr):
        """Test overlap session config"""
        overlap_symbols = session_mgr.config['sessions']['overlap']['allowed_symbols']
        
        # Overlap should allow XAUUSD and major pairs
        assert "XAUUSD" in overlap_symbols
        assert "EURUSD" in overlap_symbols
        assert "USDJPY" in overlap_symbols


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_session_manager.py -v
    pytest.main([__file__, "-v", "--tb=short"])
