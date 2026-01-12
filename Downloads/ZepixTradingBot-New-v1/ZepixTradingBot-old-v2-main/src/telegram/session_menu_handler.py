"""
Session Manager Telegram Menu Handler
Zero-typing button-based UI for Forex session configuration.

Features:
- Dashboard view with current session status
- Edit menu for all 5 Forex sessions
- Symbol toggle buttons (7 major pairs)
- Time adjustment controls (±30 minutes)
- Master switch toggle (global ON/OFF)
- Force-close toggle per session
- Real-time config updates

Author: Zepix Trading Bot Development Team
Version: 1.0
Created: 2026-01-11
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Optional
import logging
import sys
import os

# Import SessionManager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from modules.session_manager import SessionManager


class SessionMenuHandler:
    """
    Handles Telegram inline keyboard interactions for Session Manager.
    
    Provides a zero-typing interface where all session configuration
    is done via button clicks.
    """
    
    def __init__(self, session_manager, bot=None):
        """
        Initialize Session Menu Handler.
        
        Args:
            session_manager: Instance of SessionManager
            bot: Instance of TelegramBot (optional, for sending messages)
        """
        self.session_mgr = session_manager
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("SessionMenuHandler initialized")
    
    def show_session_dashboard(self, update: Update, context):
        """
        Display Session Manager dashboard with current status.
        
        Shows:
        - Master switch state
        - Current active session
        - Allowed symbols for current session
        """
        query = update.callback_query
        # self.session_mgr.bot is likely the TelegramBot wrapper, or the raw bot. 
        # If it's the wrapper, it uses 'send_message' etc. using requests.
        # If it's PTB Bot, it might be async.
        # Given TelegramBot uses requests, we assume we need to use its methods or requests directly.
        # But here we are passed 'update' which might be a PTB object OR a dict if manually parsed.
        # The mock in handle_callback_query creates a pseudo object.
        
        # Safe answer (catch errors if method missing)
        try:
            query.answer()
        except:
            pass
        
        # Get current status
        status_text = self.session_mgr.get_session_status_text()
        master_switch = self.session_mgr.config.get('master_switch', True)
        
        # Build keyboard
        keyboard = [
            [InlineKeyboardButton(
                f"{'🟢 Master: ON' if master_switch else '🔴 Master: OFF'}",
                callback_data="session_toggle_master"
            )],
            [InlineKeyboardButton("📝 Edit Sessions", callback_data="session_edit_menu")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"**📊 Session Manager Dashboard**\n\n{status_text}"
        
        try:
            query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            self.logger.error(f"Failed to edit message: {e}")
        
        self.logger.info("Dashboard displayed")
    
    def show_session_edit_menu(self, update: Update, context):
        """
        Show list of all 5 Forex sessions to edit.
        """
        query = update.callback_query
        try:
            query.answer()
        except:
            pass
        
        keyboard = []
        
        # Add button for each session
        for session_id, session_data in self.session_mgr.config['sessions'].items():
            button_text = f"{session_data['name']}"
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"session_edit_{session_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back to Dashboard", callback_data="session_dashboard")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            query.edit_message_text(
                text="**Select Session to Edit:**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            self.logger.error(f"Failed to show edit menu: {e}")
        
        self.logger.info("Session edit menu displayed")
    
    def show_session_details(self, update: Update, context, session_id: str):
        """
        Show detailed edit screen for a specific session.
        """
        query = update.callback_query
        try:
            query.answer()
        except:
            pass
        
        session_data = self.session_mgr.config['sessions'][session_id]
        all_symbols = self.session_mgr.config['all_symbols']
        allowed_symbols = session_data.get('allowed_symbols', [])
        
        # Build symbol toggle buttons (2 per row)
        symbol_keyboard = []
        for i in range(0, len(all_symbols), 2):
            row = []
            for j in range(2):
                if i + j < len(all_symbols):
                    symbol = all_symbols[i + j]
                    is_allowed = symbol in allowed_symbols
                    button_text = f"{'✅' if is_allowed else '❌'} {symbol}"
                    row.append(InlineKeyboardButton(
                        button_text,
                        callback_data=f"session_toggle_{session_id}_{symbol}"
                    ))
            symbol_keyboard.append(row)
        
        # Time adjustment buttons
        time_keyboard = [
            [
                InlineKeyboardButton("Start:", callback_data="noop"),
                InlineKeyboardButton(session_data['start_time'], callback_data="noop"),
                InlineKeyboardButton("−30m", callback_data=f"session_time_{session_id}_start_-30"),
                InlineKeyboardButton("+30m", callback_data=f"session_time_{session_id}_start_+30")
            ],
            [
                InlineKeyboardButton("End:", callback_data="noop"),
                InlineKeyboardButton(session_data['end_time'], callback_data="noop"),
                InlineKeyboardButton("−30m", callback_data=f"session_time_{session_id}_end_-30"),
                InlineKeyboardButton("+30m", callback_data=f"session_time_{session_id}_end_+30")
            ]
        ]
        
        # Force close toggle
        force_close = session_data.get('force_close_enabled', False)
        toggle_keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if force_close else '❌'} Force Close at End",
                callback_data=f"session_force_{session_id}"
            )]
        ]
        
        # Combine all keyboards
        keyboard = symbol_keyboard + time_keyboard + toggle_keyboard
        keyboard.append([InlineKeyboardButton("« Back to Sessions", callback_data="session_edit_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"**Editing: {session_data['name']}**\n\n"
            f"📝 {session_data.get('description', 'N/A')}\n"
            f"⏰ Active: {session_data['start_time']} - {session_data['end_time']}\n"
            f"📊 Allowed Symbols: {len(allowed_symbols)}/{len(all_symbols)}\n\n"
            f"**Toggle symbols, adjust times, or configure options below:**"
        )
        
        try:
            query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            self.logger.error(f"Failed to show session details: {e}")
        
        self.logger.info(f"Session edit screen displayed for: {session_id}")
    
    def handle_symbol_toggle(self, update: Update, context):
        """
        Handle symbol ON/OFF toggle.
        """
        query = update.callback_query
        try:
            query.answer("Toggling symbol...")
        except:
            pass
        
        # Parse callback data: session_toggle_{session_id}_{symbol}
        parts = query.data.split('_', 3)
        if len(parts) != 4:
            self.logger.error(f"Invalid callback data: {query.data}")
            return
        
        _, _, session_id, symbol = parts
        
        self.session_mgr.toggle_symbol(session_id, symbol)
        
        # Refresh the edit menu
        self.show_session_details(update, context, session_id)
        
        self.logger.info(f"Toggled symbol {symbol} for session {session_id}")
    
    def handle_time_adjustment(self, update: Update, context):
        """
        Handle session time adjustment.
        """
        query = update.callback_query
        try:
            query.answer("Adjusting time...")
        except:
            pass
        
        # Parse callback data: session_time_{session_id}_{field}_{delta}
        parts = query.data.split('_', 4)
        if len(parts) != 5:
            self.logger.error(f"Invalid callback data: {query.data}")
            return
        
        _, _, session_id, field, delta_str = parts
        delta_minutes = int(delta_str)
        
        self.session_mgr.adjust_session_time(session_id, f"{field}_time", delta_minutes)
        
        # Refresh the edit menu
        self.show_session_details(update, context, session_id)
        
        self.logger.info(f"Adjusted {field}_time for {session_id} by {delta_minutes} minutes")
    
    def handle_master_switch(self, update: Update, context):
        """
        Toggle master switch.
        """
        query = update.callback_query
        
        new_state = self.session_mgr.toggle_master_switch()
        
        try:
            query.answer(f"Master switch: {'ON' if new_state else 'OFF'}")
        except:
            pass
        
        # Refresh dashboard
        self.show_session_dashboard(update, context)
        
        self.logger.info(f"Master switch toggled to: {new_state}")
    
    def handle_force_close_toggle(self, update: Update, context):
        """
        Toggle force close for a session.
        """
        query = update.callback_query
        try:
            query.answer("Toggling force close...")
        except:
            pass
        
        # Parse callback data: session_force_{session_id}
        parts = query.data.split('_', 2)
        if len(parts) != 3:
            self.logger.error(f"Invalid callback data: {query.data}")
            return
        
        _, _, session_id = parts
        
        new_state = self.session_mgr.toggle_force_close(session_id)
        
        # Refresh the edit menu
        self.show_session_details(update, context, session_id)
        
    def handle_callback_query(self, callback_data: str, chat_id: int, message_id: int):
        """
        Main dispatcher for session-related callbacks.
        
        Args:
            callback_data: Callback data string
            chat_id: Telegram chat ID
            message_id: Message ID to edit
        """
        # Create a mock update object since we have the data directly
        # This allows reusing existing methods that expect an Update object
        mock_update = type('obj', (object,), {
            'callback_query': type('obj', (object,), {
                'data': callback_data,
                'message': type('obj', (object,), {'chat': type('obj', (object,), {'id': chat_id}), 'message_id': message_id}),
                'answer': lambda text=None: None, # Dummy answer function
                'edit_message_text': self.bot.edit_message_text if self.bot else None
            })
        })
        
        # Dispatch based on callback data prefix (SYNC CALLS)
        if callback_data == "session_dashboard":
            self.show_session_dashboard(mock_update, None)
            
        elif callback_data == "session_edit_menu":
            self.show_session_edit_menu(mock_update, None)
            
        elif callback_data.startswith("session_edit_"):
            session_id = callback_data.replace("session_edit_", "")
            self.show_session_details(mock_update, None, session_id)
            
        elif callback_data.startswith("session_toggle_master"):
            self.handle_master_switch(mock_update, None)
            
        elif callback_data.startswith("session_toggle_"):
            self.handle_symbol_toggle(mock_update, None)
            
        elif callback_data.startswith("session_time_"):
            self.handle_time_adjustment(mock_update, None)
            
        elif callback_data.startswith("session_force_"):
            self.handle_force_close_toggle(mock_update, None)
            
        else:
            self.logger.warning(f"Unknown session callback: {callback_data}")
    
    def get_status(self) -> dict:
        """
        Get handler status information.
        
        Returns:
            dict: Status including session manager state
        """
        return {
            'handler_active': True,
            'session_manager_status': self.session_mgr.get_status()
        }


# Example usage (for testing)
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # This would normally be initialized in telegram_bot.py
    from modules.session_manager import SessionManager
    
    session_mgr = SessionManager()
    handler = SessionMenuHandler(session_mgr)
    
    print("SessionMenuHandler initialized successfully")
    print(f"Status: {handler.get_status()}")
