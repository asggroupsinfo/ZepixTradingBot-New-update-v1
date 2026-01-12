"""
Unit Tests for Session Menu Handler (Telegram UI)
Tests all button interactions, callback routing, and UI updates.

Run tests with:
    pytest tests/test_session_menu_handler.py -v
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, Message, User, Chat
from telegram.ext import ContextTypes
import tempfile
import os

# Import modules to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from modules.session_manager import SessionManager

# Import handler from src/telegram/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'telegram'))
from session_menu_handler import SessionMenuHandler


class TestSessionMenuHandler:
    """Test suite for SessionMenuHandler"""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def session_mgr(self, temp_config):
        """Create SessionManager with temp config"""
        return SessionManager(config_path=temp_config)
    
    @pytest.fixture
    def menu_handler(self, session_mgr):
        """Create SessionMenuHandler"""
        return SessionMenuHandler(session_mgr)
    
    @pytest.fixture
    def mock_update(self):
        """Create mock Update object for Telegram"""
        update = MagicMock(spec=Update)
        query = MagicMock(spec=CallbackQuery)
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        query.data = "test_data"
        update.callback_query = query
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock Context object"""
        return MagicMock()
    
    def test_initialization(self, menu_handler, session_mgr):
        """Test handler initializes correctly"""
        assert menu_handler.session_mgr == session_mgr
        assert menu_handler.logger is not None
    
    @pytest.mark.asyncio
    async def test_show_dashboard(self, menu_handler, mock_update, mock_context):
        """Test dashboard display"""
        await menu_handler.show_session_dashboard(mock_update, mock_context)
        
        # Verify callback query was answered
        mock_update.callback_query.answer.assert_called_once()
        
        # Verify message was edited
        mock_update.callback_query.edit_message_text.assert_called_once()
        
        # Check message content
        call_kwargs = mock_update.callback_query.edit_message_text.call_args.kwargs
        assert 'Session Manager Dashboard' in call_kwargs['text']
        assert 'Master Switch' in call_kwargs['text']
        assert call_kwargs['parse_mode'] == 'Markdown'
        
        # Verify keyboard has buttons
        reply_markup = call_kwargs['reply_markup']
        assert len(reply_markup.inline_keyboard) == 3  # Master, Edit, Back
    
    @pytest.mark.asyncio
    async def test_show_session_edit_menu(self, menu_handler, mock_update, mock_context):
        """Test session edit menu displays all sessions"""
        await menu_handler.show_session_edit_menu(mock_update, mock_context)
        
        mock_update.callback_query.answer.assert_called_once()
        mock_update.callback_query.edit_message_text.assert_called_once()
        
        call_kwargs = mock_update.callback_query.edit_message_text.call_args.kwargs
        reply_markup = call_kwargs['reply_markup']
        
        # Should have 5 sessions + 1 back button = 6 total
        assert len(reply_markup.inline_keyboard) == 6
    
    @pytest.mark.asyncio
    async def test_show_session_details(self, menu_handler, mock_update, mock_context):
        """Test detailed session edit screen"""
        await menu_handler.show_session_details(mock_update, mock_context, 'asian')
        
        mock_update.callback_query.answer.assert_called_once()
        
        call_kwargs = mock_update.callback_query.edit_message_text.call_args.kwargs
        message_text = call_kwargs['text']
        
        # Verify session info displayed
        assert 'Asian Session' in message_text
        assert 'Active:' in message_text
        assert 'Allowed Symbols:' in message_text
        
        reply_markup = call_kwargs['reply_markup']
        buttons = reply_markup.inline_keyboard
        
        # Should have symbol buttons + time buttons + force close + back
        # 7 symbols = 4 rows (2 per row), 2 time rows, 1 force close, 1 back = 8 rows min
        assert len(buttons) >= 8
    
    @pytest.mark.asyncio
    async def test_handle_symbol_toggle(self, menu_handler, mock_update, mock_context):
        """Test symbol toggle functionality"""
        # Set callback data
        mock_update.callback_query.data = "session_toggle_asian_USDJPY"
        
        # Check initial state
        initial_symbols = menu_handler.session_mgr.config['sessions']['asian']['allowed_symbols'].copy()
        initial_state = 'USDJPY' in initial_symbols
        
        # Toggle
        await menu_handler.handle_symbol_toggle(mock_update, mock_context)
        
        # Verify symbol state changed
        new_symbols = menu_handler.session_mgr.config['sessions']['asian']['allowed_symbols']
        new_state = 'USDJPY' in new_symbols
        
        assert new_state != initial_state
    
    @pytest.mark.asyncio
    async def test_handle_time_adjustment(self, menu_handler, mock_update, mock_context):
        """Test time adjustment functionality"""
        # Set callback data for +30 minute adjustment
        mock_update.callback_query.data = "session_time_asian_start_+30"
        
        original_time = menu_handler.session_mgr.config['sessions']['asian']['start_time']
        
        # Adjust
        await menu_handler.handle_time_adjustment(mock_update, mock_context)
        
        new_time = menu_handler.session_mgr.config['sessions']['asian']['start_time']
        
        # Verify time changed
        assert original_time != new_time
        
        # Verify it's 30 minutes later (05:30 + 30min = 06:00)
        assert new_time == "06:00"
    
    @pytest.mark.asyncio
    async def test_handle_master_switch(self, menu_handler, mock_update, mock_context):
        """Test master switch toggle"""
        initial_state = menu_handler.session_mgr.config.get('master_switch', True)
        
        await menu_handler.handle_master_switch(mock_update, mock_context)
        
        new_state = menu_handler.session_mgr.config.get('master_switch', True)
        
        # Verify state changed
        assert new_state != initial_state
    
    @pytest.mark.asyncio
    async def test_handle_force_close_toggle(self, menu_handler, mock_update, mock_context):
        """Test force close toggle"""
        mock_update.callback_query.data = "session_force_asian"
        
        initial_state = menu_handler.session_mgr.config['sessions']['asian'].get('force_close_enabled', False)
        
        await menu_handler.handle_force_close_toggle(mock_update, mock_context)
        
        new_state = menu_handler.session_mgr.config['sessions']['asian'].get('force_close_enabled', False)
        
        # Verify state changed
        assert new_state != initial_state
    
    @pytest.mark.asyncio
    async def test_callback_data_parsing_symbol_toggle(self, menu_handler, mock_update, mock_context):
        """Test correct parsing of symbol toggle callback data"""
        test_cases = [
            ("session_toggle_london_EURUSD", "london", "EURUSD"),
            ("session_toggle_overlap_GBPJPY", "overlap", "GBPJPY"),
            ("session_toggle_asian_AUDUSD", "asian", "AUDUSD"),
        ]
        
        for callback_data, expected_session, expected_symbol in test_cases:
            mock_update.callback_query.data = callback_data
            
            # Check symbol is in allowed list before toggle
            session_config = menu_handler.session_mgr.config['sessions'][expected_session]
            initial_allowed = expected_symbol in session_config['allowed_symbols']
            
            await menu_handler.handle_symbol_toggle(mock_update, mock_context)
            
            # Verify symbol state changed
            new_allowed = expected_symbol in session_config['allowed_symbols']
            assert new_allowed != initial_allowed
    
    @pytest.mark.asyncio
    async def test_callback_data_parsing_time_adjustment(self, menu_handler, mock_update, mock_context):
        """Test correct parsing of time adjustment callback data"""
        test_cases = [
            ("session_time_london_start_+30", "london", "start", 30),
            ("session_time_asian_end_-30", "asian", "end", -30),
        ]
        
        for callback_data, session_id, field, delta in test_cases:
            mock_update.callback_query.data = callback_data
            
            original_time = menu_handler.session_mgr.config['sessions'][session_id][f'{field}_time']
            
            await menu_handler.handle_time_adjustment(mock_update, mock_context)
            
            new_time = menu_handler.session_mgr.config['sessions'][session_id][f'{field}_time']
            
            # Verify time changed
            assert original_time != new_time
    
    @pytest.mark.asyncio
    async def test_ui_refresh_after_toggle(self, menu_handler, mock_update, mock_context):
        """Test that UI refreshes after each toggle action"""
        mock_update.callback_query.data = "session_toggle_asian_USDJPY"
        
        await menu_handler.handle_symbol_toggle(mock_update, mock_context)
        
        # Verify edit_message_text was called (UI refresh)
        assert mock_update.callback_query.edit_message_text.call_count >= 1
    
    def test_get_status(self, menu_handler):
        """Test status retrieval"""
        status = menu_handler.get_status()
        
        assert 'handler_active' in status
        assert status['handler_active'] is True
        assert 'session_manager_status' in status
    
    @pytest.mark.asyncio
    async def test_master_switch_button_state(self, menu_handler, mock_update, mock_context):
        """Test master switch button shows correct state"""
        # Set master switch ON
        menu_handler.session_mgr.config['master_switch'] = True
        
        await menu_handler.show_session_dashboard(mock_update, mock_context)
        
        call_kwargs = mock_update.callback_query.edit_message_text.call_args.kwargs
        reply_markup = call_kwargs['reply_markup']
        
        # First button should be master switch
        master_button = reply_markup.inline_keyboard[0][0]
        assert "🟢" in master_button.text
        assert "ON" in master_button.text
        
        # Toggle to OFF
        menu_handler.session_mgr.config['master_switch'] = False
        
        await menu_handler.show_session_dashboard(mock_update, mock_context)
        
        call_kwargs = mock_update.callback_query.edit_message_text.call_args.kwargs
        reply_markup = call_kwargs['reply_markup']
        master_button = reply_markup.inline_keyboard[0][0]
        
        assert "🔴" in master_button.text
        assert "OFF" in master_button.text
    
    @pytest.mark.asyncio
    async def test_symbol_button_state_updates(self, menu_handler, mock_update, mock_context):
        """Test symbol buttons show correct checkmark state"""
        # Add EURUSD to Asian session
        menu_handler.session_mgr.config['sessions']['asian']['allowed_symbols'].append('EURUSD')
        
        await menu_handler.show_session_details(mock_update, mock_context, 'asian')
        
        call_kwargs = mock_update.callback_query.edit_message_text.call_args.kwargs
        reply_markup = call_kwargs['reply_markup']
        
        # Find EURUSD button
        eurusd_button = None
        for row in reply_markup.inline_keyboard:
            for btn in row:
                if 'EURUSD' in btn.text:
                    eurusd_button = btn
                    break
        
        assert eurusd_button is not None
        assert "✅" in eurusd_button.text  # Should show checkmark


class TestSessionMenuEdgeCases:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    def menu_handler(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        mgr = SessionManager(config_path=temp_path)
        handler = SessionMenuHandler(mgr)
        yield handler
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_invalid_callback_data(self, menu_handler):
        """Test handling of malformed callback data"""
        mock_update = MagicMock(spec=Update)
        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.answer = AsyncMock()
        mock_query.data = "invalid_data_format"
        mock_update.callback_query = mock_query
        
        # Should not crash on invalid data
        try:
            await menu_handler.handle_symbol_toggle(mock_update, None)
        except Exception as e:
            pytest.fail(f"Handler crashed on invalid data: {e}")
    
    def test_all_sessions_present(self, menu_handler):
        """Test that all 5 Forex sessions are accessible"""
        sessions = menu_handler.session_mgr.config['sessions']
        
        expected_sessions = ['asian', 'london', 'overlap', 'ny_late', 'dead_zone']
        
        for session_id in expected_sessions:
            assert session_id in sessions


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_session_menu_handler.py -v
    pytest.main([__file__, "-v", "--tb=short"])
