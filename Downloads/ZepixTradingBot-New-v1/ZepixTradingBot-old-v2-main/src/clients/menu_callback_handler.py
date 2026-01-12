"""
Menu Callback Handler
Handles all menu navigation callbacks for Telegram bot
Separated for modularity and easier maintenance
"""

import logging

logger = logging.getLogger(__name__)

class MenuCallbackHandler:
    """Handles menu-related callback queries"""
    
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.menu_manager = telegram_bot.menu_manager
        self.fine_tune_handler = None
    
    def handle_menu_callback(self, callback_data, user_id, message_id):
        """
        Handle menu navigation callbacks
        
        Args:
            callback_data: The callback data from button click
            user_id: Telegram user ID
            message_id: Message ID to edit
            
        Returns:
            True if handled, False if not a menu callback
        """
        # Main menu
        if callback_data == "menu_main":
            self.menu_manager.show_main_menu(user_id, message_id)
            return True
        
        # Fine-Tune menu - Special handling (two variants)
        elif callback_data == "menu_fine_tune" or callback_data == "fine_tune_menu":
            return self._handle_fine_tune_menu(user_id, message_id)
        
        # Re-entry menu - New handler
        elif callback_data == "menu_reentry":
            return self._handle_reentry_menu(user_id, message_id)
        
        # Profit booking menu - New handler
        elif callback_data == "menu_profit":
            return self._handle_profit_booking_menu(user_id, message_id)
        
        # Profit booking toggles (FIX: these were incorrectly going to reentry handler)
        elif callback_data in ["toggle_profit_sl_hunt", "toggle_profit_protection"]:
            return self._handle_profit_booking_toggle(callback_data, user_id, message_id)
        
        # Voice and Clock action handlers
        elif callback_data == "action_voice_test":
            self.bot.handle_voice_test_command(message=None) # Pass None as message since it's a callback
            return True
        elif callback_data == "action_clock":
            self.bot.handle_clock_command(message=None)
            return True
            
        # Timeframe menu action handlers  
        elif callback_data == "action_toggle_timeframe":
            return self._handle_timeframe_toggle(user_id, message_id)
        elif callback_data == "action_view_logic_settings":
            return self._handle_view_logic_settings(user_id, message_id)
        elif callback_data == "action_reset_timeframe_default":
            return self._handle_reset_timeframe(user_id, message_id)
        
        # NEW: Timeframe configure/help menus
        elif callback_data == "tf_configure_menu":
            return self._handle_tf_configure_menu(user_id, message_id)
        elif callback_data == "tf_help_menu":
            return self._handle_tf_help_menu(user_id, message_id)
        
        # NEW: Individual logic configuration
        elif callback_data.startswith("tf_config_logic"):
            logic_name = callback_data.replace("tf_config_", "").upper()
            return self._handle_tf_logic_config(user_id, message_id, logic_name)
        
        # NEW: Parameter adjustment menus
        elif callback_data.startswith("tf_adj_"):
            parts = callback_data.split("_")
            param_type = parts[2]  # lot, sl, or window
            logic_name = parts[3]  # combinedlogic-1/2/3
            return self._handle_tf_adjustment_menu(user_id, message_id, logic_name, param_type)
        
        # NEW: Set parameter value
        elif callback_data.startswith("tf_set_"):
            return self._handle_tf_set_parameter(callback_data, user_id, message_id)
        
        # NEW: Help content pages
        elif callback_data.startswith("tf_help_"):
            help_type = callback_data.replace("tf_help_", "")
            if help_type != "menu":
                return self._handle_tf_help_content(user_id, message_id, help_type)
        
        # NEW: Detailed example scenarios
        elif callback_data.startswith("tf_ex_"):
            scenario = callback_data.replace("tf_ex_", "")
            return self._handle_tf_example_scenario(user_id, message_id, scenario)
        
        
        # Profit levels menu and toggles (CHECK BEFORE generic toggle_)
        elif callback_data == "profit_levels_menu":
            if hasattr(self.bot, 'profit_booking_menu_handler') and self.bot.profit_booking_menu_handler:
                self.bot.profit_booking_menu_handler.show_levels_menu(user_id, message_id)
            return True
        elif callback_data.startswith("toggle_level_"):
            if hasattr(self.bot, 'profit_booking_menu_handler') and self.bot.profit_booking_menu_handler:
                level = callback_data.split("_")[-1]  # Extract level number
                self.bot.profit_booking_menu_handler.toggle_level(level, user_id, message_id)
            return True
        
        # Re-entry toggles (MUST be after toggle_level_ check)
        elif callback_data.startswith("toggle_"):
            return self._handle_reentry_toggle(callback_data, user_id, message_id)
        
        # Profit SL mode selector
        elif callback_data.startswith("profit_sl_mode_"):
            return self._handle_profit_sl_mode(callback_data, user_id, message_id)
        
        # Recovery windows editing
        elif callback_data.startswith("rw_") or callback_data == "ft_recovery_windows_edit":
            return self._handle_recovery_windows(callback_data, user_id, message_id)
        
        # Re-entry status view
        elif callback_data == "reentry_view_status":
            return self._handle_reentry_status(user_id, message_id)
        
        # Re-entry advanced settings
        elif callback_data == "reentry_advanced":
            return self._handle_reentry_advanced(user_id, message_id)
        
        # Advanced settings parameter editors
        elif callback_data.startswith("adv_"):
            return self._handle_advanced_settings_callback(callback_data, user_id, message_id)
        
        # Parameter value setters
        elif callback_data.startswith("set_"):
            return self._handle_parameter_setter(callback_data, user_id, message_id)
        
        # All other category menus
        elif callback_data.startswith("menu_"):
            category = callback_data.replace("menu_", "")
            
            # Special handler for timeframe menu
            if category  == "timeframe":
                if hasattr(self.menu_manager, 'show_timeframe_menu'):
                    self.menu_manager.show_timeframe_menu(user_id, message_id)
                else:
                    print("WARNING: show_timeframe_menu not found", flush=True)
                return True
            
            # Generic category handler
            self.menu_manager.show_category_menu(user_id, category, message_id)
            return True
        
        return False

    
    def _handle_fine_tune_menu(self, user_id, message_id=None):
        """Handle Fine-Tune menu specifically"""
        # Get or initialize fine_tune_handler
        if not self.fine_tune_handler and hasattr(self.bot, 'fine_tune_handler'):
            self.fine_tune_handler = self.bot.fine_tune_handler
        
        # Initialize if needed
        if not self.fine_tune_handler:
            if hasattr(self.bot, '_initialize_fine_tune_handler'):
                self.bot._initialize_fine_tune_handler()
                self.fine_tune_handler = getattr(self.bot, 'fine_tune_handler', None)
        
        # Show menu
        if self.fine_tune_handler:
            self.fine_tune_handler.show_fine_tune_menu(user_id, message_id)
            return True
        else:
            self.bot.send_message("❌ Fine-Tune system not initialized. Please restart bot.")
            return True
    
    def handle_action_callback(self, callback_data, user_id, message_id):
        """
        Handle quick action callbacks
        
        Args:
            callback_data: The callback data from button click
            user_id: Telegram user ID  
            message_id: Message ID to edit
            
        Returns:
            True if handled, False if not an action callback
        """
        if callback_data == "action_trades":
            if hasattr(self.bot, 'handle_trades'):
                self.bot.handle_trades({"message_id": message_id})
            return True
        
        elif callback_data == "action_performance":
            if hasattr(self.bot, 'handle_performance'):
                self.bot.handle_performance({"message_id": message_id})
            return True
        
        elif callback_data == "action_pause_resume":
            if hasattr(self.bot, 'trading_engine') and self.bot.trading_engine:
                self.bot.trading_engine.is_paused = not self.bot.trading_engine.is_paused
                status = "PAUSED ⏸️" if self.bot.trading_engine.is_paused else "RESUMED ▶️"
                self.bot.send_message(f"✅ Trading {status}")
            return True
        
        elif callback_data == "action_dashboard":
            if hasattr(self.bot, 'handle_dashboard'):
                self.bot.handle_dashboard({"message_id": message_id})
            return True
        
        elif callback_data == "action_help":
            if hasattr(self.bot, '_show_help_menu'):
                self.bot._show_help_menu(user_id, message_id)
            return True
        
        return False
    
    # ==================== NEW HANDLER METHODS ====================
    
    def _handle_reentry_menu(self, user_id, message_id=None):
        """Handle Re-entry System menu"""
        if not hasattr(self.bot, 'reentry_menu_handler') or not self.bot.reentry_menu_handler:
            self.bot.send_message("❌ Re-entry menu not initialized. Please restart bot.")
            return True
        
        self.bot.reentry_menu_handler.show_reentry_menu(user_id, message_id)
        return True
    
    def _handle_profit_booking_menu(self, user_id, message_id=None):
        """Handle Profit Booking menu"""
        if not hasattr(self.bot, 'profit_booking_menu_handler') or not self.bot.profit_booking_menu_handler:
            self.bot.send_message("❌ Profit Booking menu not initialized. Please restart bot.")
            return True
        
        self.bot.profit_booking_menu_handler.show_profit_booking_menu(user_id, message_id)
        return True
    
    def _handle_reentry_toggle(self, callback_data, user_id, message_id):
        """Handle re-entry toggle callbacks"""
        if not hasattr(self.bot, 'reentry_menu_handler') or not self.bot.reentry_menu_handler:
            self.bot.send_message("❌ Re-entry menu not initialized.")
            return True
        
        self.bot.reentry_menu_handler.handle_toggle_callback(callback_data, user_id, message_id)
        return True
    
    def _handle_profit_sl_mode(self, callback_data, user_id, message_id):
        """Handle profit SL mode change"""
        if not hasattr(self.bot, 'profit_booking_menu_handler') or not self.bot.profit_booking_menu_handler:
            self.bot.send_message("❌ Profit Booking menu not initialized.")
            return True
        
        # Extract mode from callback_data
        mode = "SL-1.1" if "11" in callback_data else "SL-2.1"
        self.bot.profit_booking_menu_handler.handle_sl_mode_change(mode, user_id, message_id)
        return True
    
    def _handle_profit_booking_toggle(self, callback_data, user_id, message_id):
        """Handle profit booking toggle callbacks"""
        if not hasattr(self.bot, 'profit_booking_menu_handler') or not self.bot.profit_booking_menu_handler:
            self.bot.send_message("❌ Profit Booking menu not initialized.")
            return True
        
        # Route to correct method based on callback
        if callback_data == "toggle_profit_sl_hunt":
            self.bot.profit_booking_menu_handler.toggle_profit_sl_hunt(user_id, message_id)
        elif callback_data == "toggle_profit_protection":
            self.bot.profit_booking_menu_handler.toggle_profit_protection(user_id, message_id)
        return True
    
    def _handle_recovery_windows(self, callback_data, user_id, message_id):
        """Handle recovery windows editing callbacks"""
        if not hasattr(self.bot, 'fine_tune_handler') or not self.bot.fine_tune_handler:
            self.bot.send_message("❌ Fine-tune handler not initialized.")
            return True
        
        # Create callback_query dict for handler
        callback_query = {
            "data": callback_data,
            "from": {"id": user_id},
            "message": {"message_id": message_id}
        }
        
        # Route to recovery window handler
        if callback_data == "ft_recovery_windows_edit":
            self.bot.fine_tune_handler.show_recovery_windows_edit(user_id, 0, message_id)
        else:
            self.bot.fine_tune_handler.handle_recovery_window_callback(callback_query)
        
        return True
    
    def _handle_reentry_status(self, user_id, message_id):
        """Handle re-entry status view"""
        if not hasattr(self.bot, 'reentry_menu_handler') or not self.bot.reentry_menu_handler:
            self.bot.send_message("❌ Re-entry menu not initialized.")
            return True
        
        self.bot.reentry_menu_handler.show_reentry_status(user_id, message_id)
        return True
    
    def _handle_reentry_advanced(self, user_id, message_id):
        """Handle re-entry advanced settings submenu"""
        if not hasattr(self.bot, 'reentry_menu_handler') or not self.bot.reentry_menu_handler:
            self.bot.send_message("❌ Re-entry menu not initialized.")
            return True
        
        # Show advanced settings submenu
        if hasattr(self.bot.reentry_menu_handler, 'show_advanced_settings'):
            self.bot.reentry_menu_handler.show_advanced_settings(user_id, message_id)
        else:
            # Fallback: just show main reentry menu
            self.bot.reentry_menu_handler.show_reentry_menu(user_id, message_id)
        return True
    
    def _handle_advanced_settings_callback(self, callback_data, user_id, message_id):
        """Handle advanced settings parameter editor callbacks"""
        if not hasattr(self.bot, 'reentry_menu_handler') or not self.bot.reentry_menu_handler:
            self.bot.send_message("❌ Re-entry menu not initialized.")
            return True
        
        handler = self.bot.reentry_menu_handler
        
        # Route to appropriate editor
        if callback_data == "adv_monitor_interval":
            handler.show_monitor_interval_editor(user_id, message_id)
        elif callback_data == "adv_sl_offset":
            handler.show_sl_offset_editor(user_id, message_id)
        elif callback_data == "adv_cooldown":
            handler.show_cooldown_editor(user_id, message_id)
        elif callback_data == "adv_recovery_window":
            handler.show_recovery_window_editor(user_id, message_id)
        elif callback_data == "adv_max_levels":
            handler.show_max_levels_editor(user_id, message_id)
        elif callback_data == "adv_sl_reduction":
            handler.show_sl_reduction_editor(user_id, message_id)
        elif callback_data == "adv_reset_config":
            handler.reset_to_defaults(user_id, message_id)
        
        return True
    
    def _handle_parameter_setter(self, callback_data, user_id, message_id):
        """Handle parameter value setter callbacks"""
        if not hasattr(self.bot, 'reentry_menu_handler') or not self.bot.reentry_menu_handler:
            self.bot.send_message("❌ Re-entry menu not initialized.")
            return True
        
        handler = self.bot.reentry_menu_handler
        
        # Parse callback data to extract parameter and value
        # Format: set_<param>_<value>
        parts = callback_data.split("_")
        
        if len(parts) < 3:
            return True
        
        param_type = parts[1]  # monitor, offset, cooldown, window, levels, reduction
        value_str = parts[2]
        
        # Convert value to appropriate type and set parameter
        try:
            if param_type == "monitor":
                # set_monitor_5 → monitor_interval = 5
                value = int(value_str)
                handler.set_parameter("monitor_interval", value, user_id, message_id)
                
            elif param_type == "offset":
                # set_offset_1.0 → sl_hunt_offset_pips = 1.0
                value = float(value_str)
                handler.set_parameter("sl_hunt_offset_pips", value, user_id, message_id)
                
            elif param_type == "cooldown":
                # set_cooldown_30 → cooldown_seconds = 30
                value = int(value_str)
                handler.set_parameter("cooldown_seconds", value, user_id, message_id)
                
            elif param_type == "window":
                # set_window_15 → recovery_window_minutes = 15
                value = int(value_str)
                handler.set_parameter("recovery_window_minutes", value, user_id, message_id)
                
            elif param_type == "levels":
                # set_levels_5 → max_chain_levels = 5
                value = int(value_str)
                handler.set_parameter("max_chain_levels", value, user_id, message_id)
                
            elif param_type == "reduction":
                # set_reduction_30 → sl_reduction_per_level = 0.30
                value = int(value_str) / 100.0  # Convert percentage to decimal
                handler.set_parameter("sl_reduction_per_level", value, user_id, message_id)
                
        except Exception as e:
            logger.error(f"Error setting parameter from callback {callback_data}: {str(e)}")
            self.bot.send_message(f"❌ Error: {str(e)}")
        
        return True
    
    def _handle_timeframe_toggle(self, user_id: int, message_id: int):
        """Toggle timeframe-specific logic system ON/OFF"""
        config = self.bot.config.get("timeframe_specific_config", {})
        current = config.get("enabled", False)
        new_state = not current
        
        config["enabled"] = new_state
        self.bot.config.config["timeframe_specific_config"] = config
        self.bot.config.save_config()
        
        status = "✅ ENABLED" if new_state else "❌ DISABLED"
        self.bot.send_message(f"⏱️ Timeframe Logic: {status}")
        
        # Refresh menu
        self.menu_manager.show_timeframe_menu(user_id, message_id)
        return True
    
    def _handle_view_logic_settings(self, user_id: int, message_id: int):
        """Show detailed logic settings for each timeframe"""
        config = self.bot.config.get("timeframe_specific_config", {})
        
        text = "📊 <b>Timeframe Logic Settings</b>\n\n"
        
        for logic_name in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
            logic = config.get(logic_name, {})
            text += f"<b>{logic_name}</b> ({logic.get('timeframe', 'N/A')})\n"
            text += f"  Lot: {logic.get('lot_multiplier', 1.0)}x\n"
            text += f"  SL: {logic.get('sl_multiplier', 1.0)}x\n"
            text += f"  Window: {logic.get('recovery_window_minutes', 15)}m\n\n"
        
        keyboard = {
            "inline_keyboard": [[{"text": "🔙 Back", "callback_data": "menu_timeframe"}]]
        }
        
        if message_id:
            self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        else:
            self.bot.send_message_with_keyboard(text, keyboard)
        
        return True
    
    def _handle_reset_timeframe(self, user_id: int, message_id: int):
        """Reset timeframe config to defaults"""
        default_config = {
            "enabled": True,
            "enabled": True,
            "combinedlogic-1": {
                "timeframe": "5m",
                "lot_multiplier": 1.25,
                "sl_multiplier": 1.0,
                "recovery_window_minutes": 30,
                "description": "Aggressive - Fast moves"
            },
            "combinedlogic-2": {
                "timeframe": "15m",
                "lot_multiplier": 1.0,
                "sl_multiplier": 1.5,
                "recovery_window_minutes": 45,
                "description": "Balanced - Medium volatility"
            },
            "combinedlogic-3": {
                "timeframe": "1h",
                "lot_multiplier": 0.625,
                "sl_multiplier": 2.5,
                "recovery_window_minutes": 120,
                "description": "Conservative - Wide breathing room"
            }
        }
        
        self.bot.config.config["timeframe_specific_config"] = default_config
        self.bot.config.save_config()
        
        self.bot.send_message("✅ Timeframe config reset to defaults!")
        
        # Refresh menu
        self.menu_manager.show_timeframe_menu(user_id, message_id)
        return True
    
    # NEW: Advanced Timeframe Menu Handlers
    
    def _handle_tf_configure_menu(self, user_id: int, message_id: int):
        """Show configure logics submenu"""
        config = self.bot.config.get("timeframe_specific_config", {})
        
        # Get current multipliers for display
        l1 = config.get("combinedlogic-1", {})
        l2 = config.get("combinedlogic-2", {})
        l3 = config.get("combinedlogic-3", {})
        
        keyboard = {
            "inline_keyboard": [
                [{"text": f"🔧 combinedlogic-1 (5m) - Lot: {l1.get('lot_multiplier', 1.0)}x, SL: {l1.get('sl_multiplier', 1.0)}x", 
                  "callback_data": "tf_config_combinedlogic-1"}],
                [{"text": f"🔧 combinedlogic-2 (15m) - Lot: {l2.get('lot_multiplier', 1.0)}x, SL: {l2.get('sl_multiplier', 1.0)}x", 
                  "callback_data": "tf_config_combinedlogic-2"}],
                [{"text": f"🔧 combinedlogic-3 (1h) - Lot: {l3.get('lot_multiplier', 1.0)}x, SL: {l3.get('sl_multiplier', 1.0)}x", 
                  "callback_data": "tf_config_combinedlogic-3"}],
                [{"text": "🔙 Back to Timeframe Menu", "callback_data": "menu_timeframe"}]
            ]
        }
        
        text = (
            "⚙️ <b>Configure Individual Logics</b>\n\n"
            "Select a logic to adjust its multipliers:\n\n"
            f"combinedlogic-1: {l1.get('lot_multiplier', 1.0)}x lot, {l1.get('sl_multiplier', 1.0)}x SL\n"
            f"combinedlogic-2: {l2.get('lot_multiplier', 1.0)}x lot, {l2.get('sl_multiplier', 1.0)}x SL\n"
            f"combinedlogic-3: {l3.get('lot_multiplier', 1.0)}x lot, {l3.get('sl_multiplier', 1.0)}x SL"
        )
        
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        return True
    
    def _handle_tf_logic_config(self, user_id: int, message_id: int, logic_name: str):
        """Show individual logic configuration menu"""
        config = self.bot.config.get("timeframe_specific_config", {})
        logic = config.get(logic_name, {})
        
        timeframe = logic.get("timeframe", "N/A")
        current_lot = logic.get("lot_multiplier", 1.0)
        current_sl = logic.get("sl_multiplier", 1.0)
        current_window = logic.get("recovery_window_minutes", 30)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": f"📦 Lot Multiplier: {current_lot}x", "callback_data": f"tf_adj_lot_{logic_name}"}],
                [{"text": f"🎯 SL Multiplier: {current_sl}x", "callback_data": f"tf_adj_sl_{logic_name}"}],
                [{"text": f"⏱ Recovery Window: {current_window}m", "callback_data": f"tf_adj_window_{logic_name}"}],
                [{"text": "🔙 Back", "callback_data": "tf_configure_menu"}]
            ]
        }
        
        text = (
            f"🔧 <b>{logic_name} Settings ({timeframe})</b>\n\n"
            f"• Lot Multiplier: {current_lot}x\n"
            f"• SL Multiplier: {current_sl}x\n"
            f"• Recovery Window: {current_window}m\n\n"
            f"Click a setting to adjust it."
        )
        
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        return True
    
    def _handle_tf_adjustment_menu(self, user_id: int, message_id: int, logic_name: str, param_type: str):
        """Show adjustment buttons for a specific parameter"""
        config = self.bot.config.get("timeframe_specific_config", {})
        logic = config.get(logic_name, {})
        
        if param_type == "lot":
            current = logic.get("lot_multiplier", 1.0)
            options = [0.5, 0.625, 0.75, 1.0, 1.25, 1.5, 2.0]
            title = "Lot Multiplier"
            unit = "x"
        elif param_type == "sl":
            current = logic.get("sl_multiplier", 1.0)
            options = [0.75, 1.0, 1.5, 2.0, 2.5, 3.0]
            title = "SL Multiplier"
            unit = "x"
        else:  # window
            current = logic.get("recovery_window_minutes", 30)
            options = [15, 30, 45, 60, 90, 120]
            title = "Recovery Window"
            unit = "m"
        
        
        # Map logic name to short code
        logic_code_map = {
            "combinedlogic-1": "cl1",
            "combinedlogic-2": "cl2",
            "combinedlogic-3": "cl3"
        }
        logic_code = logic_code_map.get(logic_name, logic_name)
        
        # Build button grid (3 per row)
        buttons = []
        row = []
        for i, opt in enumerate(options):
            marker = "✅ " if abs(opt - current) < 0.01 else ""
            row.append({"text": f"{marker}{opt}{unit}", 
                       "callback_data": f"tf_set_{param_type}_{logic_code}_{opt}"})
            if len(row) == 3 or i == len(options) - 1:
                buttons.append(row)
                row = []
        
        buttons.append([{"text": "🔙 Back", "callback_data": f"tf_config_{logic_name}"}])
        
        keyboard = {"inline_keyboard": buttons}
        
        text = f"🎛 <b>Adjust {title} for {logic_name}</b>\n\nCurrent: <b>{current}{unit}</b>"
        
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        return True
    
    def _handle_tf_set_parameter(self, callback_data: str, user_id: int, message_id: int):
        """Set a parameter value from callback"""
        # Parse: tf_set_lot_cl1_1.25
        parts = callback_data.split("_")
        param_type = parts[2]  # lot, sl, window
        logic_code = parts[3]  # cl1/cl2/cl3
        value_str = parts[4]   # The value
        
        # Map code to full name
        logic_map = {
            "cl1": "combinedlogic-1",
            "cl2": "combinedlogic-2", 
            "cl3": "combinedlogic-3"
        }
        logic_name = logic_map.get(logic_code, logic_code)
        
        # Convert value
        try:
            value = float(value_str)
        except:
            value = int(value_str)
        
        # Update config
        config = self.bot.config.get("timeframe_specific_config", {})
        logic = config.get(logic_name, {})
        
        if param_type == "lot":
            logic["lot_multiplier"] = value
            param_name = "Lot Multiplier"
        elif param_type == "sl":
            logic["sl_multiplier"] = value
            param_name = "SL Multiplier"
        else:  # window
            logic["recovery_window_minutes"] = int(value)
            param_name = "Recovery Window"
        
        config[logic_name] = logic
        self.bot.config.config["timeframe_specific_config"] = config
        self.bot.config.save_config()
        
        # Send confirmation
        self.bot.send_message(f"✅ {logic_name} {param_name} → {value}")
        
        # Show logic config menu again
        return self._handle_tf_logic_config(user_id, message_id, logic_name)
    
    def _handle_tf_help_menu(self, user_id: int, message_id: int):
        """Show help and guide"""
        keyboard = {
            "inline_keyboard": [
                [{"text": "📘 What is Timeframe Logic?", "callback_data": "tf_help_what"}],
                [{"text": "🔢 How Multipliers Work", "callback_data": "tf_help_multipliers"}],
                [{"text": "💡 Examples & Tips", "callback_data": "tf_help_examples"}],
                [{"text": "🔙 Back", "callback_data": "menu_timeframe"}]
            ]
        }
        
        text = (
            "📖 <b>Timeframe Logic Help</b>\n\n"
            "Learn how the system works:\n\n"
            "• <b>What is it?</b> - Core concept\n"
            "• <b>How Multipliers Work</b> - Details\n"
            "• <b>Examples & Tips</b> - Best practices"
        )
        
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        return True
    
    def _handle_tf_help_content(self, user_id: int, message_id: int, help_type: str):
        """Show specific help content"""
        keyboard = {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "tf_help_menu"}]]}
        
        if help_type == "what":
            text = (
                "📘 <b>What is Timeframe Logic?</b>\n\n"
                "Adapts strategy per timeframe:\n\n"
                "• <b>combinedlogic-1 (5m)</b>: Fast moves\n"
                "  Aggressive, 1.25x lot, tight SL\n\n"
                "• <b>combinedlogic-2 (15m)</b>: Balanced\n"
                "  Standard lot, 1.5x SL\n\n"
                "• <b>combinedlogic-3 (1h)</b>: Slow moves\n"
                "  Conservative, 0.625x lot, wide SL\n\n"
                "<b>Benefit:</b> Each timeframe gets optimal risk!"
            )
        elif help_type == "multipliers":
            text = (
                "🔢 <b>How Multipliers Work</b>\n\n"
                "<b>Lot Multiplier:</b>\n"
                "Base lot × Multiplier = Final lot\n\n"
                "Example: Base 0.04 lots\n"
                "• 1.25x → 0.05 lots (bigger)\n"
                "• 0.625x → 0.025 lots (smaller)\n\n"
                "<b>SL Multiplier:</b>\n"
                "Base SL × Multiplier = Final SL\n\n"
                "Example: Base 100 pips\n"
                "• 1.5x → 150 pips (wider)\n"
                "• 2.5x → 250 pips (much wider)"
            )
        else:  # examples
            # Create submenu for different example scenarios
            keyboard = {
                "inline_keyboard": [
                    [{"text": "1️⃣ Conservative (Risk-Averse)", "callback_data": "tf_ex_conservative"}],
                    [{"text": "2️⃣ Balanced (Recommended)", "callback_data": "tf_ex_balanced"}],
                    [{"text": "3️⃣ Aggressive (High Risk)", "callback_data": "tf_ex_aggressive"}],
                    [{"text": "4️⃣ Scalping Focus (5m only)", "callback_data": "tf_ex_scalping"}],
                    [{"text": "5️⃣ Swing Trading (1h focus)", "callback_data": "tf_ex_swing"}],
                    [{"text": "6️⃣ Troubleshooting Tips", "callback_data": "tf_ex_troubleshoot"}],
                    [{"text": "🔙 Back", "callback_data": "tf_help_menu"}]
                ]
            }
            
            text = (
                "💡 <b>Practical Examples & Scenarios</b>\n\n"
                "Select a scenario to see detailed settings:\n\n"
                "1️⃣ <b>Conservative</b> - Minimize SL hits\n"
                "2️⃣ <b>Balanced</b> - Recommended for most\n"
                "3️⃣ <b>Aggressive</b> - Maximize profits\n"
                "4️⃣ <b>Scalping</b> - Fast 5m trading\n"
                "5️⃣ <b>Swing</b> - Patient 1h trading\n"
                "6️⃣ <b>Troubleshooting</b> - Common issues"
            )
        
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        return True
    
    def _handle_tf_example_scenario(self, user_id: int, message_id: int, scenario: str):
        """Show detailed example scenario with comprehensive guide"""
        keyboard = {"inline_keyboard": [[{"text": "🔙 Back to Examples", "callback_data": "tf_help_examples"}]]}
        
        if scenario == "conservative":
            text = (
                "1️⃣ <b>Conservative Setup (Risk-Averse)</b>\n\n"
                "<b>Goal:</b> Minimize SL hits, protect capital\n\n"
                "<b>Recommended Settings:</b>\n"
                "• combinedlogic-1 (5m): Lot 0.75x, SL 1.5x, Window 45m\n"
                "• combinedlogic-2 (15m): Lot 0.625x, SL 2.0x, Window 60m\n"
                "• combinedlogic-3 (1h): Lot 0.5x, SL 3.0x, Window 180m\n\n"
                "<b>Why This Works:</b>\n"
                "✅ Smaller lots = Less risk per trade\n"
                "✅ Wider SL = More room for price movement\n"
                "✅ Longer windows = Patient re-entry\n\n"
                "<b>Best For:</b>\n"
                "• Small account sizes ($5k-$10k)\n"
                "• New traders learning the system\n"
                "• Volatile market conditions\n"
                "• Preserving drawdowns\n\n"
                "<b>Expected Results:</b>\n"
                "• Low SL hit rate (~20-30%)\n"
                "• Slower profit accumulation\n"
                "• Very stable equity curve"
            )
        elif scenario == "balanced":
            text = (
                "2️⃣ <b>Balanced Setup (Recommended)</b>\n\n"
                "<b>Goal:</b> Optimal risk/reward balance\n\n"
                "<b>Recommended Settings:</b>\n"
                "• combinedlogic-1 (5m): Lot 1.25x, SL 1.0x, Window 30m\n"
                "• combinedlogic-2 (15m): Lot 1.0x, SL 1.5x, Window 45m\n"
                "• combinedlogic-3 (1h): Lot 0.625x, SL 2.5x, Window 120m\n\n"
                "<b>Why This Works:</b>\n"
                "✅ Default settings (proven effective)\n"
                "✅ Each timeframe optimized separately\n"
                "✅ Good balance of risk & opportunity\n\n"
                "<b>Best For:</b>\n"
                "• Medium accounts ($10k-$25k)\n"
                "• Experienced traders\n"
                "• Normal market conditions\n"
                "• Long-term consistent growth\n\n"
                "<b>Expected Results:</b>\n"
                "• Moderate SL hit rate (~35-45%)\n"
                "• Steady profit growth\n"
                "• Balanced equity curve\n\n"
                "<b>⭐ This is the DEFAULT setting!</b>"
            )
        elif scenario == "aggressive":
            text = (
                "3️⃣ <b>Aggressive Setup (High Risk)</b>\n\n"
                "<b>Goal:</b> Maximize profits, accept higher risk\n\n"
                "<b>Recommended Settings:</b>\n"
                "• combinedlogic-1 (5m): Lot 1.5x, SL 0.75x, Window 15m\n"
                "• combinedlogic-2 (15m): Lot 1.25x, SL 1.0x, Window 30m\n"
                "• combinedlogic-3 (1h): Lot 1.0x, SL 1.5x, Window 60m\n\n"
                "<b>Why This Works:</b>\n"
                "✅ Larger lots = Higher profit potential\n"
                "✅ Tighter SL = More trades executed\n"
                "✅ Faster re-entry = More opportunities\n\n"
                "<b>Best For:</b>\n"
                "• Large accounts ($25k+)\n"
                "• Expert traders\n"
                "• Strong trending markets\n"
                "• Quick profit targets\n\n"
                "<b>Expected Results:</b>\n"
                "• High SL hit rate (~50-60%)\n"
                "• Fast profit when right\n"
                "• Volatile equity curve\n\n"
                "<b>⚠️ WARNING:</b>\n"
                "Only use if you can handle 3-5\n"
                "consecutive losses!"
            )
        elif scenario == "scalping":
            text = (
                "4️⃣ <b>Scalping Focus (5m Timeframe)</b>\n\n"
                "<b>Goal:</b> Fast trades on 5m charts only\n\n"
                "<b>Recommended Settings:</b>\n"
                "• combinedlogic-1 (5m): Lot 1.5x, SL 0.75x, Window 20m\n"
                "• combinedlogic-2 (15m): Lot 0.5x, SL 1.0x, Window 30m\n"
                "• combinedlogic-3 (1h): Lot 0.25x, SL 1.0x, Window 60m\n\n"
                "<b>Strategy Explanation:</b>\n"
                "1. Focus on combinedlogic-1 (5m) signals\n"
                "2. Use tight SL for quick exits\n"
                "3. Bigger lot size on 5m only\n"
                "4. Reduce combinedlogic-2/3 to minimum\n\n"
                "<b>Advanced Tips:</b>\n"
                "• Trade only during peak hours\n"
                "• Watch 5m-15m correlation\n"
                "• Exit before major news events\n"
                "• Use TP1 more aggressively\n\n"
                "<b>Risk Management:</b>\n"
                "• Max 3 combinedlogic-1 trades/day\n"
                "• Stop after 2 consecutive losses\n"
                "• Don't chase missed entries\n\n"
                "<b>Expected Win Rate:</b> 45-55%"
            )
        elif scenario == "swing":
            text = (
                "5️⃣ <b>Swing Trading (1h Timeframe)</b>\n\n"
                "<b>Goal:</b> Patient, high-probability trades\n\n"
                "<b>Recommended Settings:</b>\n"
                "• combinedlogic-1 (5m): Lot 0.5x, SL 1.0x, Window 60m\n"
                "• combinedlogic-2 (15m): Lot 0.75x, SL 1.5x, Window 90m\n"
                "• combinedlogic-3 (1h): Lot 1.0x, SL 3.0x, Window 180m\n\n"
                "<b>Strategy Explanation:</b>\n"
                "1. Focus on combinedlogic-3 (1h) signals\n"
                "2. Give trades LOTS of room (3x SL!)\n"
                "3. Ignore 5m noise completely\n"
                "4. Hold for bigger moves\n\n"
                "<b>Advanced Tips:</b>\n"
                "• Check 4h trend alignment\n"
                "• Wait for 1h candle close\n"
                "• Target TP3 more often\n"
                "• Let profit run past TP\n\n"
                "<b>Risk Management:</b>\n"
                "• Max 1-2 combinedlogic-3 trades/day\n"
                "• 3-hour recovery windows\n"
                "• Don't micro-manage trades\n\n"
                "<b>Expected Win Rate:</b> 60-70%\n"
                "<b>Avg Trade Duration:</b> 4-8 hours"
            )
        else:  # troubleshoot
            text = (
                "6️⃣ <b>Troubleshooting Common Issues</b>\n\n"
                "<b>Problem 1: Too Many SL Hits</b>\n"
                "Solution:\n"
                "• Increase SL multiplier by 0.5x\n"
                "• Reduce lot multiplier to 0.75x\n"
                "• Increase recovery window +15m\n\n"
                "<b>Problem 2: Missing Profit Targets</b>\n"
                "Solution:\n"
                "• Check if SL too wide (reduce 0.25x)\n"
                "• Increase lot size for faster TP\n"
                "• Review symbol volatility settings\n\n"
                "<b>Problem 3: Not Enough Trades</b>\n"
                "Solution:\n"
                "• Reduce recovery windows\n"
                "• Enable all 3 logics\n"
                "• Check TradingView alerts active\n\n"
                "<b>Problem 4: Too Much Drawdown</b>\n"
                "Solution:\n"
                "• Switch to Conservative setup\n"
                "• Reduce ALL lot multipliers by 0.25x\n"
                "• Take break after -$100 day\n\n"
                "<b>Problem 5: Config Not Saving</b>\n"
                "Solution:\n"
                "• Click value, wait for ✅ message\n"
                "• Check config.json file updated\n"
                "• Restart bot if needed\n\n"
                "<b>General Best Practices:</b>\n"
                "✅ Change ONE setting at a time\n"
                "✅ Test for 1 week before adjusting\n"
                "✅ Keep notes on what works\n"
                "❌ Don't change during active trades"
            )
        
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        return True
