"""
Re-entry Menu Handler - Visual Toggles for Autonomous System
Provides zero-typing button-based control for all Re-entry features.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ReentryMenuHandler:
    """Telegram menu handler for Re-entry System with visual toggles"""
    
    def __init__(self, bot, autonomous_manager):
        """
        Initialize Re-entry menu handler
        
        Args:
            bot: TelegramBot instance
            autonomous_manager: AutonomousSystemManager instance
        """
        self.bot = bot
        self.autonomous_manager = autonomous_manager
        self.config = bot.config
    
    def _btn(self, text: str, callback_data: str):
        """Helper to create inline keyboard button dict"""
        return {"text": text, "callback_data": callback_data}
    
    def _create_keyboard(self, rows: list):
        """Helper to create inline keyboard dict"""
        return {"inline_keyboard": rows}
    
    def show_reentry_menu(self, user_id: int, message_id: Optional[int] = None):
        """
        Show Re-entry System menu with visual toggles
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (if updating existing message)
        """
        try:
            # Get current statuses from config
            re_entry_config = self.config.get("re_entry_config", {})
            autonomous_config = re_entry_config.get("autonomous_config", {})
            
            # Global autonomous mode
            autonomous_enabled = autonomous_config.get("enabled", False)
            
            # Individual feature statuses
            tp_cont_config = autonomous_config.get("tp_continuation", {})
            tp_cont_enabled = tp_cont_config.get("enabled", False)
            
            sl_hunt_config = autonomous_config.get("sl_hunt_recovery", {})
            sl_hunt_enabled = sl_hunt_config.get("enabled", False)
            
            exit_cont_config = autonomous_config.get("exit_continuation", {})
            exit_cont_enabled = exit_cont_config.get("enabled", False)
            
            # Reverse Shield v3.0 (Root Level Config)
            rev_shield_config = self.config.get("reverse_shield_config", {})
            rev_shield_enabled = rev_shield_config.get("enabled", False)
            
            # Build keyboard with 2-column layout
            keyboard = []
            
            # Master Autonomous Mode Toggle (full width)
            keyboard.append([self._toggle_button(
                "🤖 Autonomous Mode", 
                autonomous_enabled, 
                "toggle_autonomous"
            )])
            
            # Individual Feature Toggles (2-column layout)
            keyboard.append([
                self._toggle_button("🎯 TP Continuation", tp_cont_enabled, "toggle_tp_continuation"),
                self._toggle_button("🛡 SL Hunt", sl_hunt_enabled, "toggle_sl_hunt")
            ])
            
            # Reverse Shield & Exit Continuation
            keyboard.append([
                self._toggle_button("⚔️ Reverse Shield", rev_shield_enabled, "toggle_reverse_shield"),
                self._toggle_button("🔄 Exit Continuat.", exit_cont_enabled, "toggle_exit_continuation")
            ])
            
            # Additional Options (2-column layout)
            keyboard.append([
                self._btn("📊 View Status", "reentry_view_status"),
                self._btn("⚙ Advanced Settings", "reentry_advanced")
            ])
            keyboard.append([self._btn("🏠 Back to Main Menu", "menu_main")])
            
            # Build message
            status_icon = "🟢 ACTIVE" if autonomous_enabled else "🔴 INACTIVE"
            
            message = (
                f"🔄 <b>RE-ENTRY & SHIELD SYSTEM</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>Master Status:</b> {status_icon}\n\n"
                f"<b>Feature Status:</b>\n"
                f"• TP Continuation: {'ON ✅' if tp_cont_enabled else 'OFF ❌'}\n"
                f"• SL Hunt (Defense): {'ON ✅' if sl_hunt_enabled else 'OFF ❌'}\n"
                f"• Reverse Shield (Attack): {'ON ✅' if rev_shield_enabled else 'OFF ❌'}\n"
                f"• Exit Continuation: {'ON ✅' if exit_cont_enabled else 'OFF ❌'}\n\n"
                f"<b>💡 Tip:</b> Click buttons to toggle ON/OFF\n"
            )
            
            reply_markup = self._create_keyboard(keyboard)
            
            # Send or edit message
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
            logger.info(f"Re-entry menu shown to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error showing re-entry menu: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _toggle_button(self, label: str, is_enabled: bool, callback: str):
        """
        Create toggle button with visual indicator
        
        Args:
            label: Button label
            is_enabled: Current state
            callback: Callback data
        
        Returns:
            Button dict with visual ON/OFF indicator
        """
        status = "ON ✅" if is_enabled else "OFF ❌"
        return self._btn(f"{label} [{status}]", callback)
    
    def handle_toggle_callback(self, callback_data: str, user_id: int, message_id: int):
        """
        Handle toggle button clicks
        
        Args:
            callback_data: Callback data from button click
            user_id: Telegram user ID
            message_id: Message ID to update
        """
        try:
            logger.info(f"Handling toggle callback: {callback_data}")
            
            if callback_data == "toggle_autonomous":
                new_value = self.toggle_autonomous_mode()
                status = "ENABLED ✅" if new_value else "DISABLED ❌"
                self.bot.send_message(f"🤖 Autonomous Mode: {status}")
                
            elif callback_data == "toggle_tp_continuation":
                new_value = self.toggle_tp_continuation()
                status = "ENABLED ✅" if new_value else "DISABLED ❌"
                self.bot.send_message(f"🎯 TP Continuation: {status}")
                
            elif callback_data == "toggle_sl_hunt":
                new_value = self.toggle_sl_hunt()
                status = "ENABLED ✅" if new_value else "DISABLED ❌"
                self.bot.send_message(f"🛡 SL Hunt: {status}")
                
            elif callback_data == "toggle_exit_continuation":
                new_value = self.toggle_exit_continuation()
                status = "ENABLED ✅" if new_value else "DISABLED ❌"
                self.bot.send_message(f"🔄 Exit Continuation: {status}")
                
            elif callback_data == "toggle_reverse_shield":
                new_value = self.toggle_reverse_shield()
                status = "ENABLED ✅" if new_value else "DISABLED ❌"
                self.bot.send_message(f"⚔️ Reverse Shield: {status}")
            
            # Refresh menu to show updated states
            self.show_reentry_menu(user_id, message_id)
            
        except Exception as e:
            logger.error(f"Error handling toggle: {str(e)}")
            import traceback
            traceback.print_exc()
            self.bot.send_message(f"❌ Error toggling setting: {str(e)}")
    
    def toggle_autonomous_mode(self) -> bool:
        """
        Toggle master autonomous mode
        
        Returns:
            New value (True = enabled, False = disabled)
        """
        current = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("enabled", False)
        new_value = not current
        
        # Update config
        self.config.update_nested("re_entry_config.autonomous_config.enabled", new_value)
        
        # If disabling, disable all sub-features for safety
        if not new_value:
            logger.info("Disabling all sub-features (master autonomous mode disabled)")
            self.config.update_nested("re_entry_config.autonomous_config.tp_continuation.enabled", False)
            self.config.update_nested("re_entry_config.autonomous_config.sl_hunt_recovery.enabled", False)
            self.config.update_nested("re_entry_config.autonomous_config.exit_continuation.enabled", False)
        
        # Save config
        self.config.save()
        
        logger.info(f"Autonomous mode toggled: {current} → {new_value}")
        return new_value
    
    def toggle_tp_continuation(self) -> bool:
        """
        Toggle TP Continuation feature
        
        Returns:
            New value (True = enabled, False = disabled)
        """
        current = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("tp_continuation", {}).get("enabled", False)
        new_value = not current
        
        # Update config
        self.config.update_nested("re_entry_config.autonomous_config.tp_continuation.enabled", new_value)
        
        # Save config
        self.config.save()
        
        logger.info(f"TP Continuation toggled: {current} → {new_value}")
        return new_value
    
    def toggle_sl_hunt(self) -> bool:
        """
        Toggle SL Hunt Recovery feature
        
        Returns:
            New value (True = enabled, False = disabled)
        """
        current = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("sl_hunt_recovery", {}).get("enabled", False)
        new_value = not current
        
        # Update config
        self.config.update_nested("re_entry_config.autonomous_config.sl_hunt_recovery.enabled", new_value)
        
        # Save config
        self.config.save()
        
        logger.info(f"SL Hunt toggled: {current} → {new_value}")
        return new_value
    
    def toggle_exit_continuation(self) -> bool:
        """
        Toggle Exit Continuation feature
        
        Returns:
            New value (True = enabled, False = disabled)
        """
        current = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("exit_continuation", {}).get("enabled", False)
        new_value = not current
        
        # Update config
        self.config.update_nested("re_entry_config.autonomous_config.exit_continuation.enabled", new_value)
        
        # Save config
        self.config.save()
        
        logger.info(f"Exit Continuation toggled: {current} → {new_value}")
        return new_value
    
    def toggle_reverse_shield(self) -> bool:
        """
        Toggle Reverse Shield v3.0 (Attack Mode)
        
        Returns:
            New value (True = enabled, False = disabled)
        """
        # Note: Reverse Shield config is at ROOT level, not inside re_entry_config
        current = self.config.get("reverse_shield_config", {}).get("enabled", False)
        new_value = not current
        
        # Update config directly since it's root level
        # update_nested works for root keys too like 'reverse_shield_config.enabled'
        self.config.update_nested("reverse_shield_config.enabled", new_value)
        
        # Save config
        self.config.save()
        
        logger.info(f"Reverse Shield toggled: {current} → {new_value}")
        return new_value
    
    def show_reentry_status(self, user_id: int, message_id: Optional[int] = None):
        """Show detailed status of all Re-entry features"""
        try:
            autonomous_config = self.config.get("re_entry_config", {}).get("autonomous_config", {})
            
            # Gather all settings
            enabled = autonomous_config.get("enabled", False)
            
            tp_cont = autonomous_config.get("tp_continuation", {})
            tp_enabled = tp_cont.get("enabled", False)
            tp_cooldown = tp_cont.get("cooldown_seconds", 5)
            tp_max_levels = tp_cont.get("max_levels", 5)
            
            sl_hunt = autonomous_config.get("sl_hunt_recovery", {})
            sl_enabled = sl_hunt.get("enabled", False)
            sl_max_attempts = sl_hunt.get("max_attempts", 1)
            sl_min_pips = sl_hunt.get("min_recovery_pips", 2)
            
            exit_cont = autonomous_config.get("exit_continuation", {})
            exit_enabled = exit_cont.get("enabled", False)
            
            message = (
                "📊 <b>RE-ENTRY SYSTEM STATUS</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>🤖 Master Mode:</b> {'ON ✅' if enabled else 'OFF ❌'}\n\n"
                "<b>🎯 TP CONTINUATION</b>\n"
                f"• Status: {'ON ✅' if tp_enabled else 'OFF ❌'}\n"
                f"• Cooldown: {tp_cooldown}s\n"
                f"• Max Levels: {tp_max_levels}\n\n"
                "<b>🛡 SL HUNT RECOVERY</b>\n"
                f"• Status: {'ON ✅' if sl_enabled else 'OFF ❌'}\n"
                f"• Max Attempts: {sl_max_attempts}\n"
                f"• Min Recovery: {sl_min_pips} pips\n\n"
                "<b>🔄 EXIT CONTINUATION</b>\n"
                f"• Status: {'ON ✅' if exit_enabled else 'OFF ❌'}\n"
            )
            
            keyboard = [[self._btn("🏠 Back", "menu_reentry")]]
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Error showing re-entry status: {str(e)}")
    
    def show_advanced_settings(self, user_id: int, message_id: Optional[int] = None):
        """
        Show Advanced Re-entry Configuration submenu
        Provides access to all re-entry parameters
        """
        try:
            # Get current configuration
            re_entry_config = self.config.get("re_entry_config", {})
            
            # Build keyboard with 2-column layout for better UX
            keyboard = [
                # Configuration buttons in pairs
                [
                    self._btn("⏱ Monitor Interval", "adv_monitor_interval"),
                    self._btn("📏 SL Offset", "adv_sl_offset")
                ],
                [
                    self._btn("⏱ Cooldown Time", "adv_cooldown"),
                    self._btn("🔄 Recovery Window", "adv_recovery_window")
                ],
                [
                    self._btn("🔢 Max Chain Levels", "adv_max_levels"),
                    self._btn("📉 SL Reduction %", "adv_sl_reduction")
                ],
                # Standalone buttons
                [self._btn("🔄 Reset to Defaults", "adv_reset_config")],
                [self._btn("🔙 Back", "menu_reentry")]
            ]
            
            # Get current values for display
            monitor_interval = re_entry_config.get("monitor_interval", 5)
            sl_offset = re_entry_config.get("sl_hunt_offset_pips", 1.0)
            cooldown = re_entry_config.get("cooldown_seconds", 30)
            recovery_window = re_entry_config.get("recovery_window_minutes", 15)
            max_levels = re_entry_config.get("max_chain_levels", 5)
            sl_reduction = int(re_entry_config.get("sl_reduction_per_level", 0.3) * 100)
            
            message = f"""
⚙️ <b>ADVANCED SETTINGS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current Configuration:</b>

⏱ <b>Monitor Interval:</b> {monitor_interval}s
   └ How often to check for re-entry opportunities

📏 <b>SL Hunt Offset:</b> {sl_offset} pips
   └ Price buffer for SL Hunt recovery

⏱ <b>Cooldown Time:</b> {cooldown}s
   └ Wait time between re-entry attempts

🔄 <b>Recovery Window:</b> {recovery_window} minutes
   └ Maximum time to monitor for recovery

🔢 <b>Max Chain Levels:</b> {max_levels}
   └ Maximum TP continuation levels

📉 <b>SL Reduction:</b> {sl_reduction}%
   └ SL size reduction per level

<b>💡 Tip:</b> Click any setting to modify
            """
            
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
            logger.info(f"Advanced settings shown to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error showing advanced settings: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # ==================== ADVANCED SETTINGS PARAMETER EDITORS ====================
    
    def show_monitor_interval_editor(self, user_id: int, message_id: Optional[int] = None):
        """Show monitor interval selection menu with presets"""
        try:
            current = self.config.get("re_entry_config", {}).get("monitor_interval", 5)
            
            keyboard = [
                [self._btn("3s", "set_monitor_3"), self._btn("5s ✅" if current == 5 else "5s", "set_monitor_5")],
                [self._btn("10s", "set_monitor_10"), self._btn("15s", "set_monitor_15")],
                [self._btn("30s", "set_monitor_30"), self._btn("60s", "set_monitor_60")],
                [self._btn("🔙 Back", "reentry_advanced")]
            ]
            
            message = f"""
⏱ <b>MONITOR INTERVAL</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current:</b> {current}s

How often the bot checks for re-entry opportunities.

<b>Recommended:</b>
• 3-5s: High-frequency monitoring
• 10-15s: Balanced
• 30-60s: Conservative

<b>Select New Interval:</b>
            """
            
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Error showing monitor interval editor: {str(e)}")
    
    def show_sl_offset_editor(self, user_id: int, message_id: Optional[int] = None):
        """Show SL offset selection menu"""
        try:
            current = self.config.get("re_entry_config", {}).get("sl_hunt_offset_pips", 1.0)
            
            keyboard = [
                [self._btn("0.5 pips", "set_offset_0.5"), self._btn("1.0 pips ✅" if current == 1.0 else "1.0 pips", "set_offset_1.0")],
                [self._btn("1.5 pips", "set_offset_1.5"), self._btn("2.0 pips", "set_offset_2.0")],
                [self._btn("3.0 pips", "set_offset_3.0"), self._btn("5.0 pips", "set_offset_5.0")],
                [self._btn("🔙 Back", "reentry_advanced")]
            ]
            
            message = f"""
📏 <b>SL HUNT OFFSET</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current:</b> {current} pips

Price buffer above/below SL for hunt recovery entry.

<b>Lower offset:</b> More recoveries, tighter entries  
<b>Higher offset:</b> Safer entries, fewer recoveries

<b>Select New Offset:</b>
            """
            
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Error showing SL offset editor: {str(e)}")
    
    def show_cooldown_editor(self, user_id: int, message_id: Optional[int] = None):
        """Show cooldown time selection menu"""
        try:
            current = self.config.get("re_entry_config", {}).get("cooldown_seconds", 30)
            
            keyboard = [
                [self._btn("10s", "set_cooldown_10"), self._btn("30s ✅" if current == 30 else "30s", "set_cooldown_30")],
                [self._btn("60s", "set_cooldown_60"), self._btn("120s", "set_cooldown_120")],
                [self._btn("300s", "set_cooldown_300"), self._btn("600s", "set_cooldown_600")],
                [self._btn("🔙 Back", "reentry_advanced")]
            ]
            
            message = f"""
⏱ <b>COOLDOWN TIME</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current:</b> {current}s

Wait time between consecutive re-entry attempts.

Prevents rapid-fire entries and overtrading.

<b>Select New Cooldown:</b>
            """
            
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Error showing cooldown editor: {str(e)}")
    
    def show_recovery_window_editor(self, user_id: int, message_id: Optional[int] = None):
        """Show recovery window selection menu"""
        try:
            current = self.config.get("re_entry_config", {}).get("recovery_window_minutes", 15)
            
            keyboard = [
                [self._btn("5 min", "set_window_5"), self._btn("10 min", "set_window_10")],
                [self._btn("15 min ✅" if current == 15 else "15 min", "set_window_15"), self._btn("20 min", "set_window_20")],
                [self._btn("30 min", "set_window_30"), self._btn("60 min", "set_window_60")],
                [self._btn("🔙 Back", "reentry_advanced")]
            ]
            
            message = f"""
🔄 <b>RECOVERY WINDOW</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current:</b> {current} minutes

Maximum time to monitor for SL Hunt recovery.

<b>Shorter:</b> Less waiting, miss some recoveries  
<b>Longer:</b> More chances, ties up monitoring

<b>Select New Window:</b>
            """
            
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Error showing recovery window editor: {str(e)}")
    
    def show_max_levels_editor(self, user_id: int, message_id: Optional[int] = None):
        """Show max chain levels selection menu"""
        try:
            current = self.config.get("re_entry_config", {}).get("max_chain_levels", 5)
            
            keyboard = [
                [self._btn("1 level", "set_levels_1"), self._btn("2 levels", "set_levels_2")],
                [self._btn("3 levels", "set_levels_3"), self._btn("4 levels", "set_levels_4")],
                [self._btn("5 levels ✅" if current == 5 else "5 levels", "set_levels_5"), self._btn("10 levels", "set_levels_10")],
                [self._btn("🔙 Back", "reentry_advanced")]
            ]
            
            message = f"""
🔢 <b>MAX CHAIN LEVELS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current:</b> {current} levels

Maximum TP continuation progression levels.

Each level takes partial profit and reduces SL.

<b>Fewer levels:</b> Simpler, less management  
<b>More levels:</b> Better profit optimization

<b>Select New Max:</b>
            """
            
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Error showing max levels editor: {str(e)}")
    
    def show_sl_reduction_editor(self, user_id: int, message_id: Optional[int] = None):
        """Show SL reduction percentage selection menu"""
        try:
            current = int(self.config.get("re_entry_config", {}).get("sl_reduction_per_level", 0.3) * 100)
            
            keyboard = [
                [self._btn("20%", "set_reduction_20"), self._btn("30% ✅" if current == 30 else "30%", "set_reduction_30")],
                [self._btn("40%", "set_reduction_40"), self._btn("50%", "set_reduction_50")],
                [self._btn("60%", "set_reduction_60"), self._btn("70%", "set_reduction_70")],
                [self._btn("🔙 Back", "reentry_advanced")]
            ]
            
            message = f"""
📉 <b>SL REDUCTION %</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current:</b> {current}%

Percentage to reduce SL at each TP level.

<b>Example with 30%:</b>
• Level 1: $100 SL
• Level 2: $70 SL (30% reduction)
• Level 3: $49 SL (30% reduction)

<b>Lower:</b> Slower progression, more conservative  
<b>Higher:</b> Faster progression, more aggressive

<b>Select New Percentage:</b>
            """
            
            reply_markup = self._create_keyboard(keyboard)
            
            if message_id:
                self.bot.edit_message(message, message_id, reply_markup, parse_mode="HTML")
            else:
                self.bot.send_message_with_keyboard(message, reply_markup, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Error showing SL reduction editor: {str(e)}")
    
    # ==================== PARAMETER VALUE SETTERS ====================
    
    def set_parameter(self, param_name: str, value: any, user_id: int, message_id: int):
        """
        Generic parameter setter
        
        Args:
            param_name: Config key name
            value: New value
            user_id: Telegram user ID
            message_id: Message ID to update
        """
        try:
            # Update config
            self.config.update_nested(f"re_entry_config.{param_name}", value)
            self.config.save()
            
            logger.info(f"Parameter {param_name} updated to {value}")
            
            # Send confirmation
            self.bot.send_message(f"✅ Setting updated: {param_name} = {value}")
            
            # Return to advanced settings menu
            self.show_advanced_settings(user_id, message_id)
            
        except Exception as e:
            logger.error(f"Error setting parameter {param_name}: {str(e)}")
            self.bot.send_message(f"❌ Error: {str(e)}")
    
    def reset_to_defaults(self, user_id: int, message_id: int):
        """Reset all advanced settings to factory defaults"""
        try:
            # Default values
            defaults = {
                "monitor_interval": 5,
                "sl_hunt_offset_pips": 1.0,
                "cooldown_seconds": 30,
                "recovery_window_minutes": 15,
                "max_chain_levels": 5,
                "sl_reduction_per_level": 0.3
            }
            
            # Update all values
            for key, value in defaults.items():
                self.config.update_nested(f"re_entry_config.{key}", value)
            
            self.config.save()
            
            logger.info("Advanced settings reset to defaults")
            
            # Send confirmation
            self.bot.send_message(
                "✅ <b>Reset Complete</b>\n\n"
                "All advanced settings restored to factory defaults:\n"
                "• Monitor Interval: 5s\n"
                "• SL Offset: 1.0 pips\n"
                "• Cooldown: 30s\n"
                "• Recovery Window: 15 min\n"
                "• Max Levels: 5\n"
                "• SL Reduction: 30%",
                parse_mode="HTML"
            )
            
            # Return to advanced settings menu
            self.show_advanced_settings(user_id, message_id)
            
        except Exception as e:
            logger.error(f"Error resetting to defaults: {str(e)}")
            self.bot.send_message(f"❌ Error: {str(e)}")
