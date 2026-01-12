# Extended timeframe menu handlers
# Import this in menu_callback_handler.py to add advanced timeframe functionality

def _handle_tf_configure_menu(self, user_id: int, message_id: int):
    """Show configure logics submenu"""
    from menu.timeframe_menu_handler import show_tf_configure_menu
    return show_tf_configure_menu(self, self.bot, self.menu_manager, user_id, message_id)

def _handle_tf_logic_config(self, user_id: int, message_id: int, logic_name: str):
    """Show individual logic configuration menu"""
    from menu.timeframe_menu_handler import show_tf_logic_config
    return show_tf_logic_config(self, self.bot, self.menu_manager, user_id, message_id, logic_name)

def _handle_tf_adjustment_menu(self, user_id: int, message_id: int, logic_name: str, param_type: str):
    """Show adjustment buttons for a specific parameter"""
    from menu.timeframe_menu_handler import show_tf_adjustment_menu
    return show_tf_adjustment_menu(self, self.bot, self.menu_manager, user_id, message_id, logic_name, param_type)

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
    self.bot.send_message(f"✅ {logic_name} {param_name} updated to {value}")
    
    # Show logic config menu again
    from menu.timeframe_menu_handler import show_tf_logic_config
    return show_tf_logic_config(self, self.bot, self.menu_manager, user_id, message_id, logic_name)

def _handle_tf_help_menu(self, user_id: int, message_id: int):
    """Show help and guide for timeframe logic"""
    from menu.timeframe_menu_handler import show_tf_help_menu
    return show_tf_help_menu(self, self.bot, self.menu_manager, user_id, message_id)

def _handle_tf_help_content(self, user_id: int, message_id: int, help_type: str):
    """Show specific help content"""
    from menu.timeframe_menu_handler import show_tf_help_content
    return show_tf_help_content(self, self.bot, self.menu_manager, user_id, message_id, help_type)
