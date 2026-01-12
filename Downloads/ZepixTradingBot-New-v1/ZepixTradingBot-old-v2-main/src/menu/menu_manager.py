"""
Menu Manager - Handles all menu display and navigation
"""
from typing import Dict, Any, Optional, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .context_manager import ContextManager
from .command_executor import CommandExecutor
from .menu_constants import (
    COMMAND_CATEGORIES, QUICK_ACTIONS, SYMBOLS, TIMEFRAMES, TRENDS,
    LOGICS, AMOUNT_PRESETS, PERCENTAGE_PRESETS, SL_SYSTEMS, PROFIT_SL_MODES,
    RISK_TIERS, INTERVAL_PRESETS, COOLDOWN_PRESETS, RECOVERY_PRESETS,
    MAX_LEVELS_PRESETS, SL_REDUCTION_PRESETS, SL_OFFSET_PRESETS, LOT_SIZE_PRESETS,
    DATE_PRESETS
)

class MenuManager:
    """
    Manages menu display, navigation, and parameter selection
    """
    
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.context = ContextManager()
        self.executor = CommandExecutor(telegram_bot, context_manager=self.context)
    
    def _get_tier_buttons_with_current(self, command: str) -> List[Dict[str, str]]:
        """
        Generate tier selection buttons with current tier highlighted
        Returns list of button dicts with text and callback_data
        """
        from .menu_constants import RISK_TIERS
        
        # Get current tier from config
        current_tier = None
        try:
            if hasattr(self.bot, 'config') and self.bot.config:
                current_tier = self.bot.config.get('default_risk_tier', None)
        except Exception as e:
            print(f"[TIER BUTTONS] Error getting current tier: {e}", flush=True)
        
        buttons = []
        for tier in RISK_TIERS:
            # Highlight current tier with ✅
            if current_tier and str(current_tier) == str(tier):
                button_text = f"✅ ${tier} (Current)"
            else:
                button_text = f"${tier}"
            
            buttons.append({
                "text": button_text,
                "callback_data": f"param_tier_{command}_{tier}"
            })
        
        return buttons
    
    def _get_smart_amount_presets(self, tier: str, param_type: str) -> List[str]:
        """
        Generate smart amount presets based on tier - shows CONFIGURED value + percentage options
        param_type: 'daily' or 'lifetime'
        Returns list of preset values as strings, with current value first
        """
        print(f"[SMART AMOUNT PRESETS] Generating for tier={tier}, type={param_type}", flush=True)
        
        try:
            tier_int = int(tier)
        except (ValueError, TypeError):
            print(f"[SMART AMOUNT PRESETS] Invalid tier value: {tier}", flush=True)
            # Fallback to generic presets
            return ["10", "20", "50", "100", "200", "500", "Custom Value"]
        
        # Get CONFIGURED value for this tier from config.json
        configured_value = None
        try:
            if hasattr(self.bot, 'config') and self.bot.config:
                risk_tiers = self.bot.config.get('risk_tiers', {})
                tier_config = risk_tiers.get(str(tier), {})
                if param_type == 'daily':
                    configured_value = tier_config.get('daily_loss_limit')
                else:  # lifetime
                    configured_value = tier_config.get('max_total_loss')
                    
                print(f"[SMART AMOUNT PRESETS] Configured {param_type} for ${tier}: ${configured_value}", flush=True)
        except Exception as e:
            print(f"[SMART PRESETS] Error getting configured value: {e}", flush=True)
        
        # If no configured value found, use defaults
        if not configured_value:
            print(f"[SMART AMOUNT PRESETS] No configured value found, using tier-based defaults", flush=True)
            if tier_int <= 5000:
                base_presets = ["50", "100", "200", "500", "Custom Value"]
            elif tier_int <= 10000:
                base_presets = ["200", "400", "800", "1000", "Custom Value"]
            elif tier_int <= 25000:
                base_presets = ["500", "1000", "2000", "2500", "Custom Value"]
            elif tier_int <= 50000:
                base_presets = ["1000", "2000", "4000", "5000", "Custom Value"]
            else:  # 100000+
                base_presets = ["2000", "4000", "8000", "10000", "Custom Value"]
            return base_presets
        
        # Generate smart presets based on CONFIGURED value
        # Show: Current value + 50%, 150%, 200% options + Custom
        current_val = int(configured_value)
        
        presets = []
        # Add current value first (will be highlighted)
        presets.append(f"{current_val} ✅")
        
        # Add percentage-based options
        half_val = int(current_val * 0.5)
        one_half_val = int(current_val * 1.5)
        double_val = int(current_val * 2.0)
        
        if half_val > 0 and half_val != current_val:
            presets.append(str(half_val))
        if one_half_val != current_val:
            presets.append(str(one_half_val))
        if double_val != current_val:
            presets.append(str(double_val))
        
        # Always add Custom Value option
        presets.append("Custom Value")
        
        print(f"[SMART AMOUNT PRESETS] Generated presets: {presets}", flush=True)
        return presets
    
    def _get_smart_lot_presets(self, tier: str) -> List[str]:
        """
        Generate smart lot size presets based on tier - shows CONFIGURED lot + percentage options
        Returns list of preset values as strings, with current lot size first
        """
        print(f"[SMART LOT PRESETS] Generating for tier={tier}", flush=True)
        
        try:
            tier_int = int(tier)
        except (ValueError, TypeError):
            print(f"[SMART LOT PRESETS] Invalid tier value: {tier}", flush=True)
            # Fallback to generic presets
            return ["0.01", "0.05", "0.1", "0.5", "1.0", "Custom Value"]
        
        # Get CONFIGURED lot size for this tier from config.json
        configured_lot = None
        try:
            if hasattr(self.bot, 'config') and self.bot.config:
                # Check manual overrides first (higher priority)
                manual_overrides = self.bot.config.get('manual_lot_overrides', {})
                if str(tier) in manual_overrides:
                    configured_lot = manual_overrides[str(tier)]
                    print(f"[SMART LOT PRESETS] Found manual override for ${tier}: {configured_lot}", flush=True)
                else:
                    # Check fixed lot sizes
                    fixed_lots = self.bot.config.get('fixed_lot_sizes', {})
                    configured_lot = fixed_lots.get(str(tier))
                    print(f"[SMART LOT PRESETS] Found fixed lot for ${tier}: {configured_lot}", flush=True)
        except Exception as e:
            print(f"[SMART LOT PRESETS] Error getting configured lot: {e}", flush=True)
        
        # If no configured lot found, use defaults
        if not configured_lot:
            print(f"[SMART LOT PRESETS] No configured lot found, using tier-based defaults", flush=True)
            if tier_int <= 5000:
                base_presets = ["0.01", "0.05", "0.1", "Custom Value"]
            elif tier_int <= 10000:
                base_presets = ["0.05", "0.1", "0.2", "Custom Value"]
            elif tier_int <= 25000:
                base_presets = ["0.5", "1.0", "2.0", "Custom Value"]
            elif tier_int <= 50000:
                base_presets = ["1.0", "2.5", "5.0", "Custom Value"]
            else:  # 100000+
                base_presets = ["2.0", "5.0", "10.0", "Custom Value"]
            return base_presets
        
        # Generate smart presets based on CONFIGURED lot size
        # Show: Current lot + 60%, 140%, 200% options + Custom
        current_lot = float(configured_lot)
        
        presets = []
        # Add current lot first (will be highlighted)
        presets.append(f"{current_lot} ✅")
        
        # Add percentage-based options
        sixty_percent = round(current_lot * 0.6, 2)
        one_forty_percent = round(current_lot * 1.4, 2)
        double_lot = round(current_lot * 2.0, 2)
        
        if sixty_percent > 0.01 and sixty_percent != current_lot:
            presets.append(str(sixty_percent))
        if one_forty_percent != current_lot:
            presets.append(str(one_forty_percent))
        if double_lot != current_lot and double_lot <= 10.0:
            presets.append(str(double_lot))
        
        # Always add Custom Value option
        presets.append("Custom Value")
        
        print(f"[SMART LOT PRESETS] Generated presets: {presets}", flush=True)
        return presets
    
    def show_main_menu(self, user_id: int, message_id: Optional[int] = None):
        """Display main menu with categories and quick actions"""
        text = (
            "🤖 *ZEPIX TRADING BOT v2.0*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎯 *QUICK ACTIONS*\n"
            "Instant access to most used commands\n\n"
            "📋 *MAIN CATEGORIES*\n"
            "Navigate to command categories\n\n"
            "💡 *Tip:* Use buttons to navigate - no typing required!"
        )
        
        keyboard = []
        
        # Quick Actions Row 1
        quick_row = []
        quick_row.append({"text": "📊 Dashboard", "callback_data": "action_dashboard"})
        quick_row.append({"text": "⏸️ Pause/Resume", "callback_data": "action_pause_resume"})
        keyboard.append(quick_row)
        
        # Quick Actions Row 2
        quick_row2 = []
        quick_row2.append({"text": "🎙️ Voice Test", "callback_data": "action_voice_test"})
        quick_row2.append({"text": "⏰ Clock", "callback_data": "action_clock"})
        keyboard.append(quick_row2)
        
        # Quick Actions Row 3
        quick_row3 = []
        quick_row3.append({"text": "📈 Trades", "callback_data": "action_trades"})
        quick_row3.append({"text": "💰 Performance", "callback_data": "action_performance"})
        keyboard.append(quick_row3)
        
        keyboard.append([])  # Empty row for spacing
        
        # Main Categories - Row 1
        cat_row1 = []
        cat_row1.append({"text": "🕒 Sessions", "callback_data": "session_dashboard"})
        cat_row1.append({"text": "💰 Trading", "callback_data": "menu_trading"})
        keyboard.append(cat_row1)
        
        # Main Categories - Row 2
        cat_row2 = []
        cat_row2.append({"text": "⏱️ Timeframe", "callback_data": "menu_timeframe"})
        cat_row2.append({"text": "⚡ Performance", "callback_data": "menu_performance"})
        keyboard.append(cat_row2)
        
        # Main Categories - Row 3
        cat_row3 = []
        cat_row3.append({"text": "🔄 Re-entry", "callback_data": "menu_reentry"})
        cat_row3.append({"text": "📍 Trends", "callback_data": "menu_trends"})
        keyboard.append(cat_row3)
        
        # Main Categories - Row 4
        cat_row4 = []
        cat_row4.append({"text": "🛡️ Risk",  "callback_data": "menu_risk"})
        cat_row4.append({"text": "⚙️ SL System", "callback_data": "menu_sl_system"})
        keyboard.append(cat_row4)
        
        # Main Categories - Row 5
        cat_row5 = []
        cat_row5.append({"text": "💎 Orders", "callback_data": "menu_orders"})
        cat_row5.append({"text": "📈 Profit", "callback_data": "menu_profit"})
        keyboard.append(cat_row5)
        
        # Main Categories - Row 6
        cat_row6 = []
        cat_row6.append({"text": "🔧 Settings", "callback_data": "menu_settings"})
        cat_row6.append({"text": "🔍 Diagnostics", "callback_data": "menu_diagnostics"})
        keyboard.append(cat_row6)
        
        # Main Categories - Row 7
        cat_row7 = []
        cat_row7.append({"text": "⚡ Fine-Tune", "callback_data": "menu_fine_tune"})
        keyboard.append(cat_row7)
        
        keyboard.append([])  # Empty row for spacing
        
        # Help and Refresh
        help_row = []
        help_row.append({"text": "🆘 Help", "callback_data": "action_help"})
        help_row.append({"text": "🔄 Refresh", "callback_data": "menu_main"})
        keyboard.append(help_row)
        
        reply_markup = {"inline_keyboard": keyboard}
        
        # Update context
        self.context.update_context(user_id, current_menu="menu_main")
        
        if message_id:
            # Edit existing message
            return self.bot.edit_message(text, message_id, reply_markup)
        else:
            # Send new message
            return self.bot.send_message_with_keyboard(text, reply_markup)

    def get_persistent_main_menu(self):
        return {
            "keyboard": [
                # Row 1: High Frequency
                ["📊 Dashboard", "⏸️ Pause/Resume", "🕒 Sessions"],
                # Row 2: Management
                ["📈 Active Trades", "🛡️ Risk", "🎙️ Voice"],
                # Row 3: Analysis
                ["🔄 Re-entry", "⚙️ SL System", "📍 Trends"],
                # Row 4: Info
                ["📈 Profit", "🆘 Help"],
                # Row 5: Safety (Full Width)
                ["🚨 PANIC CLOSE"]
            ],
            "resize_keyboard": True,  # KEEPS IT COMPACT
            "is_persistent": True,
            "one_time_keyboard": False  # Keep button available
        }
    
    def show_timeframe_menu(self, user_id: int, message_id: int):
        """Show timeframe configuration menu with dynamic status"""
        config = self.bot.config.get("timeframe_specific_config", {})
        enabled = config.get("enabled", False)
        
        # Dynamic toggle button text
        toggle_text = f"{'✅' if enabled else '❌'} Toggle System"
        
        # Build enhanced keyboard with advanced options
        keyboard = {
            "inline_keyboard": [
                [{"text": toggle_text, "callback_data": "action_toggle_timeframe"}],
                [{"text": "📊 View All Settings", "callback_data": "action_view_logic_settings"}],
                [{"text": "⚙️ Configure Logics", "callback_data": "tf_configure_menu"}],
                [{"text": "📖 Help & Guide", "callback_data": "tf_help_menu"}],
                [{"text": "🔄 Reset Defaults", "callback_data": "action_reset_timeframe_default"}],
                [{"text": "🔙 Back", "callback_data": "menu_main"}]
            ]
        }
        
        status_text = "ENABLED" if enabled else "DISABLED"
        text = (
            f"⏱️ <b>Timeframe Logic System</b>\n"
            f"Status: <b>{status_text}</b>\n\n"
            f"<b>Quick Overview:</b>\n"
            f"• combinedlogic-1 (5m): Aggressive 1.25x lot\n"
            f"• combinedlogic-2 (15m): Balanced, 1.5x SL\n"
            f"• combinedlogic-3 (1h): Conservative 0.625x lot, 2.5x SL\n\n"
            f"Use <b>Configure</b> to adjust individual settings.\n"
            f"Use <b>Help</b> to learn how it works."
        )
        
        if message_id:
            try:
                self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
            except Exception:
                self.bot.send_message_with_keyboard(text, keyboard)
        else:
            self.bot.send_message_with_keyboard(text, keyboard)
    
    def show_category_menu(self, user_id: int, category: str, message_id: int):
        """Display category sub-menu"""
        if category not in COMMAND_CATEGORIES:
            return None
        
        cat_info = COMMAND_CATEGORIES[category]
        cat_name = cat_info["name"]
        commands = cat_info["commands"]
        
        text = f"{cat_name}\n━━━━━━━━━━━━━━━━━━━━━━━━\n\nSelect a command:"
        
        keyboard = []
        
        # Group commands into rows of 2
        cmd_items = list(commands.items())
        for i in range(0, len(cmd_items), 2):
            row = []
            for j in range(2):
                if i + j < len(cmd_items):
                    cmd_key, cmd_data = cmd_items[i + j]
                    # Create button text from command key
                    button_text = cmd_key.replace("_", " ").title()
                    # Add emoji based on command type
                    if "status" in cmd_key:
                        button_text = f"📊 {button_text}"
                    elif "on" in cmd_key or "enable" in cmd_key:
                        button_text = f"✅ {button_text}"
                    elif "off" in cmd_key or "disable" in cmd_key:
                        button_text = f"❌ {button_text}"
                    elif "set" in cmd_key:
                        button_text = f"⚙️ {button_text}"
                    elif "reset" in cmd_key:
                        button_text = f"🔄 {button_text}"
                    else:
                        button_text = f"🔹 {button_text}"
                    
                    callback_data = f"cmd_{category}_{cmd_key}"
                    row.append({"text": button_text, "callback_data": callback_data})
            keyboard.append(row)
        
        # Back and Home buttons
        keyboard.append([])
        nav_row = []
        nav_row.append({"text": "🔙 Back", "callback_data": "nav_back"})
        nav_row.append({"text": "🏠 Home", "callback_data": "menu_main"})
        keyboard.append(nav_row)
        
        reply_markup = {"inline_keyboard": keyboard}
        
        # Update context
        self.context.push_menu(user_id, f"menu_{category}")
        
        return self.bot.edit_message(text, message_id, reply_markup)
    
    def show_parameter_selection(self, user_id: int, param_type: str, command: str, message_id: int, 
                                 custom_label: Optional[str] = None):
        """Show parameter selection buttons"""
        # Get context early for special parameter types
        context = self.context.get_context(user_id)
        
        # Handle special cases first
        if param_type == "chain_id" and command == "stop_profit_chain":
            # Dynamic parameter - handled separately
            return None
        
        # CRITICAL: Handle DYNAMIC presets for risk commands
        if param_type == "tier":
            # Use dynamic tier buttons with current tier highlighted
            tier_buttons = self._get_tier_buttons_with_current(command)
            
            # Get command info for progress display
            pending_cmd = context.get("pending_command", command)
            params = context.get("params", {})
            
            # Calculate step
            cmd_info = None
            for cat, cat_data in COMMAND_CATEGORIES.items():
                if pending_cmd in cat_data["commands"]:
                    cmd_info = cat_data["commands"][pending_cmd]
                    break
            
            if cmd_info:
                required_params = cmd_info.get("params", [])
                total_params = len(required_params) if isinstance(required_params, list) else 0
            else:
                total_params = 0
            
            if not params or len(params) == 0:
                current_step = 1
            else:
                current_step = len(params) + 1
            
            if total_params > 0 and current_step > total_params:
                current_step = total_params
            if current_step < 1:
                current_step = 1
            
            param_label = custom_label or "Tier"
            text = (
                f"⚙️ *{pending_cmd.replace('_', ' ').title()}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Step {current_step}/{total_params}: Select {param_label}\n\n"
                f"Choose your account balance tier:"
            )
            
            keyboard = [[button] for button in tier_buttons]  # One button per row
            keyboard.append([])
            keyboard.append([{"text": "🔙 Back", "callback_data": f"menu_{context.get('current_menu', 'menu_main').replace('menu_', '')}"}])
            
            reply_markup = {"inline_keyboard": keyboard}
            return self.bot.edit_message(text, message_id, reply_markup)
        
        elif param_type == "amount":
            # Check if this is a risk command needing dynamic amounts
            params = context.get("params", {})
            selected_tier = params.get("tier")
            
            if selected_tier and command in ["set_daily_cap", "set_lifetime_cap"]:
                # Use smart amount presets based on tier
                # Determine if this is daily or lifetime based on command
                amount_type = "daily" if "daily" in command else "lifetime"
                options = self._get_smart_amount_presets(selected_tier, amount_type)
            else:
                # Fallback to standard presets
                options = AMOUNT_PRESETS
        
        elif param_type == "daily" or param_type == "lifetime":
            # For set_risk_tier command
            params = context.get("params", {})
            selected_tier = params.get("balance")
            
            if selected_tier:
                # Use smart presets based on tier
                options = self._get_smart_amount_presets(selected_tier, param_type)
            else:
                # Fallback
                options = AMOUNT_PRESETS
        
        elif param_type == "lot_size":
            # Check if tier is selected for smart presets
            params = context.get("params", {})
            selected_tier = params.get("tier")
            
            if selected_tier:
                # Use smart lot presets based on tier
                options = self._get_smart_lot_presets(selected_tier)
            else:
                # Fallback to standard presets
                options = LOT_SIZE_PRESETS
        
        # Handle parameter types with custom keyboard generation
        elif param_type in ["date", "start_date", "end_date"]:
            # Date selection options for log export commands
            options = DATE_PRESETS
            keyboard = [
                [{"text": f"📅 {opt['display']}", "callback_data": f"param_{param_type}_{opt['value']}"}]
                for opt in options
            ]
            keyboard.append([{"text": "🔙 Back", "callback_data": f"menu_{context.get('current_menu', 'diagnostics').replace('menu_', '')}"}])
            
            param_label = custom_label or param_type.replace("_", " ").title()
            text = (
                f"⚙️ *{command.replace('_', ' ').title()}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Select {param_label}:\n\n"
                f"Choose a date from the last 7 days:"
            )
            reply_markup = {"inline_keyboard": keyboard}
            self.bot.edit_message(text, message_id, reply_markup)
            return True
        
        elif param_type == "lines":
            # Log export line count options
            options = ["100", "500", "1000"]
            keyboard = [
                [{"text": f"📄 {opt} lines", "callback_data": f"param_{param_type}_{opt}"}]
                for opt in options
            ]
            keyboard.append([{"text": "🔙 Back", "callback_data": f"menu_{context.get('current_menu', 'diagnostics').replace('menu_', '')}"}])
            
            param_label = custom_label or "Lines"
            text = (
                f"⚙️ *{command.replace('_', ' ').title()}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Select {param_label}:\n\n"
                f"Choose number of log lines to export:"
            )
            reply_markup = {"inline_keyboard": keyboard}
            self.bot.edit_message(text, message_id, reply_markup)
            return True
        
        elif param_type == "mode":
            # Trading debug mode options
            options = ["on", "off", "status"]
            emoji_map = {"on": "✅", "off": "❌", "status": "📊"}
            keyboard = [
                [{"text": f"{emoji_map[opt]} {opt.upper()}", "callback_data": f"param_{param_type}_{opt}"}]
                for opt in options
            ]
            keyboard.append([{"text": "🔙 Back", "callback_data": f"menu_{context.get('current_menu', 'diagnostics').replace('menu_', '')}"}])
            
            param_label = custom_label or "Mode"
            text = (
                f"⚙️ *{command.replace('_', ' ').title()}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Select {param_label}:\n\n"
                f"Choose debug mode:"
            )
            reply_markup = {"inline_keyboard": keyboard}
            self.bot.edit_message(text, message_id, reply_markup)
            return True
        
        elif param_type == "tier":
            # Tier selection for switch_tier command
            options = RISK_TIERS
            current_tier = self.bot.config.get('default_risk_tier', "5000")
            
            keyboard = []
            # Group options into rows of 2 for better visibility
            for i in range(0, len(options), 2):
                row = []
                for j in range(2):
                    if i + j < len(options):
                        option = options[i + j]
                        # Add active indicator
                        if str(option) == str(current_tier):
                            label = f"✅ ${option} (Active)"
                        else:
                            label = f"${option}"
                            
                        row.append({"text": label, "callback_data": f"param_tier_{option}"})
                keyboard.append(row)
            
            keyboard.append([{"text": "🔙 Back", "callback_data": f"menu_{context.get('current_menu', 'risk').replace('menu_', '')}"}])
            
            param_label = custom_label or "Risk Tier"
            text = (
                f"⚙️ *{command.replace('_', ' ').title()}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Select {param_label}:\n\n"
                f"Choose a risk tier to activate:"
            )
            reply_markup = {"inline_keyboard": keyboard}
            self.bot.edit_message(text, message_id, reply_markup)
            return True

        # Get parameter options based on type (for standard parameters)
        else:
            options = []
            if param_type == "symbol":
                options = SYMBOLS
            elif param_type == "timeframe":
                options = TIMEFRAMES
            elif param_type == "trend":
                options = TRENDS
            elif param_type == "logic":
                options = LOGICS
            elif param_type == "percent":
                options = PERCENTAGE_PRESETS
            elif param_type == "sl_system" or param_type == "system":
                options = SL_SYSTEMS
            elif param_type == "profit_sl_mode":
                options = PROFIT_SL_MODES
            elif param_type == "value":
                # Determine which preset to use based on command
                if command == "set_monitor_interval":
                    options = INTERVAL_PRESETS
                elif command == "set_cooldown":
                    options = COOLDOWN_PRESETS
                elif command == "set_recovery_time":
                    options = RECOVERY_PRESETS
                elif command == "set_max_levels":
                    options = MAX_LEVELS_PRESETS
                elif command == "set_sl_reduction":
                    options = SL_REDUCTION_PRESETS
                elif command == "set_sl_offset":
                    options = SL_OFFSET_PRESETS
                else:
                    options = INTERVAL_PRESETS  # Default
            elif param_type == "interval":
                options = INTERVAL_PRESETS
            elif param_type == "cooldown":
                options = COOLDOWN_PRESETS
            elif param_type == "recovery":
                options = RECOVERY_PRESETS
            elif param_type == "max_levels":
                options = MAX_LEVELS_PRESETS
            elif param_type == "sl_reduction":
                options = SL_REDUCTION_PRESETS
            elif param_type == "sl_offset":
                options = SL_OFFSET_PRESETS
            elif param_type == "balance":
                options = RISK_TIERS  # Use risk tiers as balance options
            elif param_type == "level":
                # Log level options for set_log_level command
                options = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            else:
                return None
        
        # If options is still empty, return None
        if not options:
            return None
        
        # Get command info to show progress
        context = self.context.get_context(user_id)
        pending_cmd = context.get("pending_command", command)
        params = context.get("params", {})
        
        # Count total params needed
        cmd_info = None
        for cat, cat_data in COMMAND_CATEGORIES.items():
            if pending_cmd in cat_data["commands"]:
                cmd_info = cat_data["commands"][pending_cmd]
                break
        
        # Get params list - handle both dict format and list format
        if cmd_info:
            required_params = cmd_info.get("params", [])
            if isinstance(required_params, list):
                total_params = len(required_params)
            else:
                total_params = 0
        else:
            total_params = 0
        
        # Current step calculation:
        # - If params is empty or None, we're showing the first parameter (step 1)
        # - If params has items, we're showing the next parameter (step = len(params) + 1)
        # - But ensure it doesn't exceed total_params
        if not params or len(params) == 0:
            current_step = 1
        else:
            current_step = len(params) + 1
        
        # Ensure current_step doesn't exceed total_params
        if total_params > 0 and current_step > total_params:
            current_step = total_params
        
        # Ensure current_step is at least 1
        if current_step < 1:
            current_step = 1
        
        param_label = custom_label or param_type.replace("_", " ").title()
        text = (
            f"⚙️ *{pending_cmd.replace('_', ' ').title()}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Step {current_step}/{total_params}: Select {param_label}\n\n"
            f"Choose an option:"
        )
        
        keyboard = []
        
        # Group options into rows of 3
        for i in range(0, len(options), 3):
            row = []
            for j in range(3):
                if i + j < len(options):
                    option = options[i + j]
                    # CRITICAL FIX: For lot_size param, use 'lot' in callback to avoid underscore parsing issues
                    # param_lot_size splits incorrectly, so we use param_lot instead
                    if param_type == "lot_size":
                        callback_data = f"param_lot_{option}"
                    elif param_type == "lot":
                        callback_data = f"param_lot_{option}"
                    else:
                        callback_data = f"param_{param_type}_{pending_cmd}_{option}"
                    row.append({"text": option, "callback_data": callback_data})
            keyboard.append(row)
        
        # Add Custom option for amounts and percentages
        if param_type in ["amount", "percentage", "interval", "cooldown", "recovery", 
                          "max_levels", "sl_reduction", "sl_offset", "lot_size", "lot", "daily", "lifetime"]:
            keyboard.append([])
            # CRITICAL FIX: For lot_size, use 'lot' in custom callback to avoid parsing issues
            if param_type == "lot_size" or param_type == "lot":
                keyboard.append([{"text": "✏️ Custom Value", "callback_data": f"param_custom_lot"}])
            else:
                keyboard.append([{"text": "✏️ Custom Value", "callback_data": f"param_custom_{param_type}_{pending_cmd}"}])
        
        # Back button
        keyboard.append([])
        keyboard.append([{"text": "🔙 Back", "callback_data": f"menu_{context.get('current_menu', 'menu_main').replace('menu_', '')}"}])
        
        reply_markup = {"inline_keyboard": keyboard}
        
        return self.bot.edit_message(text, message_id, reply_markup)
    
    def show_confirmation(self, user_id: int, command: str, message_id: int):
        """Show confirmation screen before executing command
        
        CRITICAL: This method ONLY displays the confirmation screen.
        It NEVER executes commands. Execution only happens when user clicks 'Confirm' button.
        """
        print(f"🛑 [CONFIRMATION] START - Showing confirmation for command: {command}", flush=True)
        
        context = self.context.get_context(user_id)
        params = context.get("params", {})
        
        # Ensure pending_command is set
        if not context.get("pending_command"):
            self.context.set_pending_command(user_id, command)
        
        # CRITICAL FIX: Verify params exist and try multiple recovery methods
        if not params or len(params) == 0:
            print(f"[CONFIRMATION ERROR] No params found for command {command}. Context: {context}", flush=True)
            # Try to recover
            recovered = self.context.recover_context(user_id)
            if recovered and recovered.get("params"):
                params = recovered.get("params", {})
                print(f"[CONFIRMATION] Recovered params: {params}", flush=True)
            
            # If still empty, try to get from get_all_params
            if not params or len(params) == 0:
                params = self.context.get_all_params(user_id)
                print(f"[CONFIRMATION] Got params from get_all_params: {params}", flush=True)
        
        print(f"[CONFIRMATION] Showing confirmation for {command} with params: {params}", flush=True)
        
        # Build command preview
        cmd_preview = f"/{command}"
        for param_name, param_value in params.items():
            cmd_preview += f" {param_value}"
        
        text = (
            f"✅ <b>Confirm Command</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Command: <code>{cmd_preview}</code>\n\n"
            f"Parameters:\n"
        )
        
        for param_name, param_value in params.items():
            text += f"• {param_name}: {param_value}\n"
        
        if not params:
            text += "⚠️ No parameters found - this may cause an error\n"
        
        text += "\nExecute this command?"
        
        keyboard = []
        confirm_row = []
        # CRITICAL: Confirm button MUST use execute_ prefix to trigger execution
        confirm_callback = f"execute_{command}"
        print(f"[CONFIRMATION] Confirm button callback: {confirm_callback}", flush=True)
        confirm_row.append({"text": "✅ Confirm", "callback_data": confirm_callback})
        confirm_row.append({"text": "❌ Cancel", "callback_data": f"menu_{context.get('current_menu', 'menu_main').replace('menu_', '')}"})
        keyboard.append(confirm_row)
        keyboard.append([{"text": "🔙 Back", "callback_data": f"cmd_{context.get('current_menu', '').replace('menu_', '')}_{command}"}])
        
        reply_markup = {"inline_keyboard": keyboard}
        
        print(f"[CONFIRMATION] About to display confirmation screen (NOT executing command)", flush=True)
        
        # CRITICAL FIX: If message_id is None (custom input flow), send new message instead of editing
        if message_id is None:
            print(f"[CONFIRMATION] No message_id - sending new message", flush=True)
            result = self.bot.send_message(text, reply_markup, parse_mode="HTML")
        else:
            # Use HTML parse mode to avoid Markdown errors with underscores in command names
            result = self.bot.edit_message(text, message_id, reply_markup, parse_mode="HTML")
        
        print(f"[CONFIRMATION] Confirmation screen displayed. Result: {result}", flush=True)
        print(f"✅ [CONFIRMATION] Confirmation screen shown successfully", flush=True)
        print(f"🛑 [CONFIRMATION] END - Waiting for user to click 'Confirm' button. NO EXECUTION YET.", flush=True)
        return result
    
    def get_next_parameter(self, user_id: int, command: str) -> Optional[str]:
        """Get next parameter needed for command"""
        from .command_mapping import COMMAND_PARAM_MAP
        
        context = self.context.get_context(user_id)
        params = context.get("params", {})
        
        # Get command definition from mapping
        if command in COMMAND_PARAM_MAP:
            cmd_info = COMMAND_PARAM_MAP[command]
            required_params = cmd_info.get("params", [])
        else:
            # Fallback to category mapping
            cmd_info = None
            for cat, cat_data in COMMAND_CATEGORIES.items():
                if command in cat_data["commands"]:
                    cmd_info = cat_data["commands"][command]
                    break
            
            if not cmd_info:
                return None
            
            required_params = cmd_info.get("params", [])
        
        # Find first missing parameter
        for param in required_params:
            if param not in params:
                return param
        
        return None  # All parameters collected
    
    def handle_parameter_selection(self, user_id: int, param_type: str, value: str, command: str, message_id: int):
        """Handle parameter selection and show next step
        
        CRITICAL: This method ONLY stores parameters and shows confirmation.
        It NEVER executes commands. Execution only happens via execute_ callback.
        """
        print(f"🛑 [PARAM SELECTION] START - param_type={param_type}, value={value}, command={command}", flush=True)
        
        # CRITICAL: Detect "Custom Value" button click
        if value == "Custom Value":
            print(f"🔧 [CUSTOM VALUE] User clicked Custom Value for {param_type}", flush=True)
            # Normalize param_type: 'lot' should be treated as 'lot_size'
            normalized_param_type = "lot_size" if param_type == "lot" else param_type
            # Show custom input prompt
            return self._show_custom_input_prompt(user_id, normalized_param_type, command, message_id)
        
        # CRITICAL: Strip checkmark from current value indicators (e.g., "100 ✅" -> "100")
        clean_value = value.replace(" ✅", "").strip()
        print(f"[PARAM SELECTION] Cleaned value: '{value}' -> '{clean_value}'", flush=True)
        
        # CRITICAL FIX: Get existing params first to preserve them
        context = self.context.get_context(user_id)
        existing_params = context.get("params", {}).copy()
        
        # Store parameter (use cleaned value)
        self.context.add_param(user_id, param_type, clean_value)
        
        # Ensure pending_command is set
        self.context.set_pending_command(user_id, command)
        
        # Verify param was stored
        new_context = self.context.get_context(user_id)
        stored_params = new_context.get("params", {})
        print(f"[PARAM SELECTION] Stored param: {param_type}={value}, All params: {stored_params}", flush=True)
        
        # CRITICAL FIX: Ensure all existing params are preserved
        for key, val in existing_params.items():
            if key not in stored_params:
                print(f"[PARAM SELECTION] Restoring lost param: {key}={val}", flush=True)
                self.context.add_param(user_id, key, val)
        
        # Re-verify after restoration
        final_stored_params = self.context.get_context(user_id).get("params", {})
        print(f"[PARAM SELECTION] Final stored params after preservation: {final_stored_params}", flush=True)
        
        # Check if more parameters needed
        next_param = self.get_next_parameter(user_id, command)
        
        if next_param:
            # Show next parameter selection
            print(f"🔄 [PARAM SELECTION] More parameters needed. Next param: {next_param}", flush=True)
            print(f"🔄 [PARAM SELECTION] Showing next parameter selection (NOT executing command)", flush=True)
            result = self.show_parameter_selection(user_id, next_param, command, message_id)
            print(f"✅ [PARAM SELECTION] Next parameter selection shown. Returning (NO EXECUTION)", flush=True)
            return result
        else:
            # All parameters collected, show confirmation
            # Verify params are still there before showing confirmation
            final_params = self.context.get_context(user_id).get("params", {})
            print(f"[PARAM SELECTION] All params collected. Final params: {final_params}, showing confirmation", flush=True)
            print(f"✅ [PARAM SELECTION] All parameters collected - SHOWING CONFIRMATION SCREEN", flush=True)
            print(f"🛑 [PARAM SELECTION] CRITICAL: About to show confirmation (NOT executing command)", flush=True)
            result = self.show_confirmation(user_id, command, message_id)
            print(f"✅ [PARAM SELECTION] Confirmation screen shown. Returning (NO EXECUTION)", flush=True)
            print(f"🛑 [PARAM SELECTION] END - Command will ONLY execute when user clicks 'Confirm' button", flush=True)
            return result
    
    def _show_custom_input_prompt(self, user_id: int, param_type: str, command: str, message_id: int):
        """Show custom input prompt for manual value entry"""
        print(f"[CUSTOM INPUT] Showing prompt for param_type={param_type}, command={command}", flush=True)
        
        # Set waiting_for_input state
        self.context.update_context(user_id, waiting_for_input=param_type)
        
        # Generate appropriate prompt based on parameter type
        prompts = {
            'amount': "💰 *Enter Custom Amount*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📝 Enter the amount (e.g., 250):\n\n💡 *Valid Range:* $10 - $10000\n\n❌ Type /cancel to cancel",
            'daily': "💰 *Enter Custom Daily Cap*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📝 Enter daily cap amount (e.g., 175):\n\n💡 *Valid Range:* $10 - $5000\n\n❌ Type /cancel to cancel",
            'lifetime': "💰 *Enter Custom Lifetime Cap*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📝 Enter lifetime cap amount (e.g., 1200):\n\n💡 *Valid Range:* $100 - $20000\n\n❌ Type /cancel to cancel",
            'lot_size': "📦 *Enter Custom Lot Size*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📝 Enter lot size (e.g., 0.07):\n\n💡 *Valid Range:* 0.01 - 10.0\n\n❌ Type /cancel to cancel",
        }
        
        prompt_text = prompts.get(param_type, f"📝 *Enter Custom Value*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\nEnter value for {param_type}:\n\n❌ Type /cancel to cancel")
        
        # Send prompt message
        try:
            self.bot.edit_message(prompt_text, message_id)
        except:
            self.bot.send_message(prompt_text)
        
        print(f"[CUSTOM INPUT] Prompt shown, waiting for user text input", flush=True)
        return None

