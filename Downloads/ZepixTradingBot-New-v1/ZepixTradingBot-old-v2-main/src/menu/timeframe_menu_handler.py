def show_tf_configure_menu(self, user_id: int, message_id: int):
    """Show configure logics submenu"""
    config = self.bot.config.get("timeframe_specific_config", {})
    
    # Get current multipliers for display
    l1 = config.get("combinedlogic-1", {})
    l2 = config.get("combinedlogic-2", {})
    l3 = config.get("combinedlogic-3", {})
    
    keyboard = {
        "inline_keyboard": [

            [{"text": f"🔧 combinedlogic-1 (5m) - Lot: {l1.get('lot_multiplier', 1.0)}x, SL: {l1.get('sl_multiplier', 1.0)}x", 
              "callback_data": "tf_config_cl1"}],
            [{"text": f"🔧 combinedlogic-2 (15m) - Lot: {l2.get('lot_multiplier', 1.0)}x, SL: {l1.get('sl_multiplier', 1.0)}x", 
              "callback_data": "tf_config_cl2"}],
            [{"text": f"🔧 combinedlogic-3 (1h) - Lot: {l3.get('lot_multiplier', 1.0)}x, SL: {l3.get('sl_multiplier', 1.0)}x", 
              "callback_data": "tf_config_cl3"}],
            [{"text": "🔙 Back to Timeframe Menu", "callback_data": "menu_timeframe"}]
        ]
    }
    
    text = (
        "⚙️ <b>Configure Individual Logics</b>\n\n"
        "Select a logic to adjust its multipliers and recovery window:\n\n"
        "<b>Current Settings:</b>\n"
        f"combinedlogic-1: {l1.get('lot_multiplier', 1.0)}x lot, {l1.get('sl_multiplier', 1.0)}x SL, {l1.get('recovery_window_minutes', 30)}m window\n"
        f"combinedlogic-2: {l2.get('lot_multiplier', 1.0)}x lot, {l2.get('sl_multiplier', 1.0)}x SL, {l2.get('recovery_window_minutes', 45)}m window\n"
        f"combinedlogic-3: {l3.get('lot_multiplier', 1.0)}x lot, {l3.get('sl_multiplier', 1.0)}x SL, {l3.get('recovery_window_minutes', 120)}m window"
    )
    
    if message_id:
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
    else:
        self.bot.send_message_with_keyboard(text, keyboard)

def show_tf_logic_config(self, user_id: int, message_id: int, logic_name: str):
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
            [{"text": "🔙 Back to Configure", "callback_data": "tf_configure_menu"}]
        ]
    }
    
    text = (
        f"🔧 <b>{logic_name} Settings ({timeframe})</b>\n\n"
        f"<b>Current Configuration:</b>\n"
        f"• Lot Multiplier: {current_lot}x\n"
        f"• SL Multiplier: {current_sl}x\n"
        f"• Recovery Window: {current_window} minutes\n\n"
        f"<b>What These Mean:</b>\n"
        f"• <b>Lot Multiplier</b>: Adjusts position size\n"
        f"  Higher = More aggressive, larger lots\n"
        f"• <b>SL Multiplier</b>: Adjusts stop loss distance\n"
        f"  Higher = Wider SL, more breathing room\n"
        f"• <b>Recovery Window</b>: Time to wait for SL hunt recovery\n"
        f"  Longer = More patient re-entry\n\n"
        f"Click a setting to adjust it."
    )
    
    if message_id:
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
    else:
        self.bot.send_message_with_keyboard(text, keyboard)

def show_tf_adjustment_menu(self, user_id: int, message_id: int, logic_name: str, param_type: str):
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
        options = [15, 30, 45, 60, 90, 120, 180]
        title = "Recovery Window"
        unit = "m"
    
    # Build button grid (3 per row)
    buttons = []
    row = []
    for i, opt in enumerate(options):
        marker = "✅ " if abs(opt - current) < 0.01 else ""
        row.append({"text": f"{marker}{opt}{unit}", 
                   "callback_data": f"tf_set_{param_type}_{logic_name}_{opt}"})
        if len(row) == 3 or i == len(options) - 1:
            buttons.append(row)
            row = []
    
    buttons.append([{"text": "🔙 Back to Logic Settings", "callback_data": f"tf_config_{logic_name.lower()}"}])
    
    keyboard = {"inline_keyboard": buttons}
    
    text = (
        f"🎛 <b>Adjust {title} for {logic_name}</b>\n\n"
        f"Current Value: <b>{current}{unit}</b>\n\n"
        f"Select a new value from the options below:"
    )
    
    if message_id:
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
    else:
        self.bot.send_message_with_keyboard(text, keyboard)

def show_tf_help_menu(self, user_id: int, message_id: int):
    """Show help and guide for timeframe logic"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📘 What is Timeframe Logic?", "callback_data": "tf_help_what"}],
            [{"text": "🔢 How Multipliers Work", "callback_data": "tf_help_multipliers"}],
            [{"text": "💡 Examples & Best Practices", "callback_data": "tf_help_examples"}],
            [{"text": "🔙 Back to Timeframe Menu", "callback_data": "menu_timeframe"}]
        ]
    }
    
    text = (
        "📖 <b>Timeframe Logic Help & Guide</b>\n\n"
        "Learn how the timeframe-specific trading system works:\n\n"
        "<b>Available Topics:</b>\n"
        "• <b>What is Timeframe Logic?</b>\n"
        "  Understand the core concept\n\n"
        "• <b>How Multipliers Work</b>\n"
        "  Learn about lot and SL multipliers\n\n"
        "• <b>Examples & Best Practices</b>\n"
        "  Real-world scenarios and tips"
    )
    
    if message_id:
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
    else:
        self.bot.send_message_with_keyboard(text, keyboard)

def show_tf_help_content(self, user_id: int, message_id: int, help_type: str):
    """Show specific help content"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Back to Help Menu", "callback_data": "tf_help_menu"}]
        ]
    }
    
    if help_type == "what":
        text = (
            "📘 <b>What is Timeframe Logic?</b>\n\n"
            "The Timeframe Logic System adapts your trading strategy "
            "based on the timeframe (5m, 15m, 1h) of each signal.\n\n"
            "<b>Why It Matters:</b>\n"
            "• 5m signals move fast → Need tight SL, higher lot\n"
            "• 15m signals are balanced → Standard settings\n"
            "• 1h signals need room → Wider SL, smaller lot\n\n"
            "<b>Three Logics:</b>\n"
            "• <b>combinedlogic-1 (5m)</b>: Aggressive (V3 Scalping), 1.25x lot, 1.0x SL\n"
            "• <b>combinedlogic-2 (15m)</b>: Balanced (V3 Intraday), 1.0x lot, 1.5x SL\n"
            "• <b>combinedlogic-3 (1h)</b>: Conservative (V3 Swing), 0.625x lot, 2.5x SL\n\n"
            "<b>Key Benefit:</b>\n"
            "Each timeframe gets optimal risk settings automatically!"
        )
    elif help_type == "multipliers":
        text = (
            "🔢 <b>How Multipliers Work</b>\n\n"
            "<b>Lot Multiplier:</b>\n"
            "Base lot size × Multiplier = Final lot\n\n"
            "Example ($10k account, EURUSD):\n"
            "• Base: 0.04 lots\n"
            "• combinedlogic-1 (1.25x): 0.04 × 1.25 = 0.05 lots\n"
            "• combinedlogic-2 (1.0x): 0.04 × 1.0 = 0.04 lots\n"
            "• combinedlogic-3 (0.625x): 0.04 × 0.625 = 0.025 lots\n\n"
            "<b>SL Multiplier:</b>\n"
            "Base SL distance × Multiplier = Final SL\n\n"
            "Example (EURUSD, SL-1 = 100 pips base):\n"
            "• combinedlogic-1 (1.0x): 100 × 1.0 = 100 pips\n"
            "• combinedlogic-2 (1.5x): 100 × 1.5 = 150 pips\n"
            "• combinedlogic-3 (2.5x): 100 × 2.5 = 250 pips\n\n"
            "<b>Recovery Window:</b>\n"
            "Time to wait before re-entering after SL hunt:\n"
            "• combinedlogic-1: 30 min (6 × 5m candles)\n"
            "• combinedlogic-2: 45 min (3 × 15m candles)\n"
            "• combinedlogic-3: 120 min (2 × 1h candles)"
        )
    else:  # examples
        text = (
            "💡 <b>Examples & Best Practices</b>\n\n"
            "<b>Example 1: Conservative Trading</b>\n"
            "Goal: Minimize SL hits, accept smaller positions\n"
            "Settings:\n"
            "• combinedlogic-1: Lot 1.0x, SL 1.5x\n"
            "• combinedlogic-2: Lot 0.75x, SL 2.0x\n"
            "• combinedlogic-3: Lot 0.5x, SL 3.0x\n\n"
            "<b>Example 2: Aggressive Trading</b>\n"
            "Goal: Maximize profits, tight SL\n"
            "Settings:\n"
            "• combinedlogic-1: Lot 1.5x, SL 0.75x\n"
            "• combinedlogic-2: Lot 1.25x, SL 1.0x\n"
            "• combinedlogic-3: Lot 1.0x, SL 1.5x\n\n"
            "<b>Best Practices:</b>\n"
            "✅ Keep combinedlogic-3 SL higher (2x+)\n"
            "✅ Use smaller lots for higher SL\n"
            "✅ Test one logic at a time\n"
            "✅ Track which logic performs best\n"
            "❌ Don't use same settings for all\n"
            "❌ Don't make SL too tight on 1h"
        )
    
    if message_id:
        self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
    else:
        self.bot.send_message_with_keyboard(text, keyboard)
