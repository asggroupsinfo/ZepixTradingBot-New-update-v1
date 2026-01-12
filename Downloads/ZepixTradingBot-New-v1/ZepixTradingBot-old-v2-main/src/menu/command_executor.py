"""
Command Executor - Executes commands from user context
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from .parameter_validator import ParameterValidator
from .command_mapping import COMMAND_DEPENDENCIES, COMMAND_PARAM_MAP
from .dynamic_handlers import DynamicHandlers

logger = logging.getLogger(__name__)

class CommandExecutor:
    """
    Executes commands with parameters from user context
    """
    
    def __init__(self, telegram_bot, context_manager=None):
        self.bot = telegram_bot
        self.validator = ParameterValidator()
        self.dynamic_handlers = DynamicHandlers(telegram_bot)
        self.execution_log: List[Dict[str, Any]] = []  # Store execution history
        self.context_manager = context_manager  # Store reference to context manager
    
    def _create_message_dict(self, command: str, params: Dict[str, Any]) -> dict:
        """
        Create message dict compatible with all handlers
        Handlers use both message['text'] and message.get('text', '')
        Also includes params as direct keys for menu system compatibility
        """
        # Build command string
        parts = [f"/{command}"]
        for param_name, param_value in params.items():
            if isinstance(param_value, list):
                parts.extend(str(v) for v in param_value)
            else:
                parts.append(str(param_value))
        
        # Create message dict with both text and direct param keys
        message_dict = {
            "text": " ".join(parts),
            "message_id": None,
            "from": {"id": self.bot.chat_id} if self.bot.chat_id else {},
            "chat": {"id": self.bot.chat_id} if self.bot.chat_id else {}
        }
        
        # Add params as direct keys for menu system compatibility
        for param_name, param_value in params.items():
            message_dict[param_name] = param_value
        
        logger.debug(f"📨 MESSAGE CREATED: {message_dict}")
        return message_dict
    
    def execute_command(self, user_id: int, command: str, params: Dict[str, Any]) -> bool:
        """
        Execute command with parameters
        Returns True if successful, False otherwise
        """
        # CRITICAL FIX: Recover params if empty
        if not params or len(params) == 0:
            print(f"[MENU EXECUTION] Empty params detected, attempting recovery...", flush=True)
            # Try to get from context manager
            if self.context_manager:
                context = self.context_manager.get_context(user_id)
                recovered_params = context.get("params", {})
                if recovered_params:
                    params = recovered_params
                    logger.warning(f"Recovered params from context: {params}")
                    print(f"[MENU EXECUTION] Recovered params: {params}", flush=True)
            # Also try to get from menu_manager if available
            if (not params or len(params) == 0) and hasattr(self.bot, 'menu_manager'):
                context = self.bot.menu_manager.context.get_context(user_id)
                recovered_params = context.get("params", {})
                if recovered_params:
                    params = recovered_params
                    logger.warning(f"Recovered params from menu_manager context: {params}")
                    print(f"[MENU EXECUTION] Recovered params from menu_manager: {params}", flush=True)
        
        # Create execution record for logging
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "command": command,
            "params": params.copy() if params else {},
            "status": "attempting",
            "error": None
        }
        self.execution_log.append(execution_record)
        
        # Log execution attempt
        logger.info(f"EXECUTING: {command} with params {params} for user {user_id}")
        logger.debug(f"🚨 DEBUG EXECUTE: Command={command}, Params={params}, User={user_id}")
        logger.debug(f"[MENU EXECUTION] User {user_id} executing command: {command} with params: {params}")
        
        # Execution flow tracking
        execution_steps = {
            "validation": False,
            "handler_call": False,
            "handler_complete": False,
            "success": False
        }
        
        try:
            # Validate required params BEFORE execution
            required_params = self._get_required_params(command)
            missing = [p for p in required_params if p not in params or params[p] is None]
            if missing:
                execution_record["status"] = "failed"
                execution_record["error"] = f"Missing required parameters: {', '.join(missing)}"
                error_msg = (
                    f"❌ *Missing Required Parameters*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Command: `{command}`\n\n"
                    f"Missing: {', '.join(missing)}\n\n"
                    f"Please select all required parameters and try again."
                )
                self.bot.send_message(error_msg)
                logger.warning(f"EXECUTION FAILED: {command} - Missing required parameters: {missing}")
                return False
            
            execution_steps["validation"] = True
            logger.debug(f"📊 EXECUTION STEPS: {execution_steps}")
            
            # Validate dependencies
            if not self._validate_dependencies(command):
                execution_record["status"] = "failed"
                execution_record["error"] = "Dependencies not available"
                error_msg = (
                    f"❌ *Command Unavailable*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Required dependencies not available for `{command}`.\n\n"
                    f"Bot may still be initializing. Please try again in a moment."
                )
                self.bot.send_message(error_msg)
                logger.warning(f"EXECUTION FAILED: {command} - Dependencies not available")
                return False
            
            # Validate parameters
            is_valid, error_msg = self.validator.validate_command_params(command, params)
            if not is_valid:
                execution_record["status"] = "failed"
                execution_record["error"] = f"Parameter validation failed: {error_msg}"
                error_msg = (
                    f"❌ *Parameter Validation Failed*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Command: `{command}`\n"
                    f"Error: {error_msg}\n\n"
                    f"Please check your input and try again."
                )
                self.bot.send_message(error_msg)
                logger.warning(f"EXECUTION FAILED: {command} - Parameter validation failed: {error_msg}")
                return False
            
            # Format parameters
            formatted_params = {}
            for param_name, param_value in params.items():
                try:
                    formatted_params[param_name] = self.validator.format_parameter(param_name, param_value)
                except Exception as e:
                    execution_record["status"] = "failed"
                    execution_record["error"] = f"Parameter format error for {param_name}: {str(e)}"
                    error_msg = (
                        f"❌ *Parameter Format Error*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"Could not format parameter `{param_name}`: {str(e)}\n\n"
                        f"Please try again with valid input."
                    )
                    self.bot.send_message(error_msg)
                    logger.warning(f"EXECUTION FAILED: {command} - Parameter format error: {str(e)}")
                    return False
            
            # Handle special command types
            if command in COMMAND_PARAM_MAP:
                cmd_def = COMMAND_PARAM_MAP[command]
                if cmd_def.get("type") == "dynamic":
                    return self._execute_dynamic_command(command, formatted_params)
            
            # Map command names to handler methods
            command_map = {
                # Trading commands
                "pause": lambda p: self.bot.handle_pause({"message_id": None}),
                "resume": lambda p: self.bot.handle_resume({"message_id": None}),
                "status": lambda p: self.bot.handle_status({"message_id": None}),
                "trades": lambda p: self.bot.handle_trades({"message_id": None}),
                "signal_status": lambda p: self.bot.handle_signal_status({"message_id": None}),
                "simulation_mode": self._execute_simulation_mode,
                
                # Performance commands
                "performance": lambda p: self.bot.handle_performance({"message_id": None}),
                "stats": lambda p: self.bot.handle_stats({"message_id": None}),
                "performance_report": lambda p: self.bot.handle_performance_report({"message_id": None}),
                "sessions": lambda p: self.bot.handle_sessions({"message_id": None}),
                "pair_report": lambda p: self.bot.handle_pair_report({"message_id": None}),
                "strategy_report": lambda p: self.bot.handle_strategy_report({"message_id": None}),
                
                # Strategy commands
                "logic_status": lambda p: self.bot.handle_logic_status({"message_id": None}),
                "logic_control": lambda p: self.bot.handle_logic_control(self._create_message_dict("logic_control", {})),
                "logic1_on": lambda p: self.bot.handle_logic1_on({"message_id": None}),
                "logic1_off": lambda p: self.bot.handle_logic1_off({"message_id": None}),
                "logic2_on": lambda p: self.bot.handle_logic2_on({"message_id": None}),
                "logic2_off": lambda p: self.bot.handle_logic2_off({"message_id": None}),
                "logic3_on": lambda p: self.bot.handle_logic3_on({"message_id": None}),
                "logic3_off": lambda p: self.bot.handle_logic3_off({"message_id": None}),
                
                # Re-entry commands
                "tp_system": self._execute_tp_system,
                "sl_hunt": self._execute_sl_hunt,
                "exit_continuation": self._execute_exit_continuation,
                "tp_report": lambda p: self.bot.handle_tp_report({"message_id": None}),
                "reentry_config": lambda p: self.bot.handle_reentry_config({"message_id": None}),
                "set_monitor_interval": self._execute_set_monitor_interval,
                "set_sl_offset": self._execute_set_sl_offset,
                "set_cooldown": self._execute_set_cooldown,
                "set_recovery_time": self._execute_set_recovery_time,
                "set_max_levels": self._execute_set_max_levels,
                "set_sl_reduction": self._execute_set_sl_reduction,
                "reset_reentry_config": lambda p: self.bot.handle_reset_reentry_config({"message_id": None}),
                
                # Timeframe Logic Commands
                "menu_timeframe": lambda p: self.bot.menu_manager.show_timeframe_menu(p.get("user_id"), p.get("message_id")),
                "toggle_timeframe": lambda p: self.bot.handle_toggle_timeframe({"message_id": None}),
                "view_logic_settings": lambda p: self.bot.handle_view_logic_settings({"message_id": None}),
                "reset_timeframe_default": lambda p: self.bot.handle_reset_timeframe_default({"message_id": None}),
                
                # Trend commands
                "show_trends": lambda p: self.bot.handle_show_trends({"message_id": None}),
                "trend_matrix": lambda p: self.bot.handle_trend_matrix({"message_id": None}),
                "set_trend": self._execute_set_trend,
                "set_auto": self._execute_set_auto,
                "trend_mode": self._execute_trend_mode,
                
                # Risk commands
                "view_risk_caps": lambda p: self.bot.handle_view_risk_caps({"message_id": None}),
                "view_risk_status": lambda p: self.bot.handle_view_risk_status({"message_id": None}),
                "set_daily_cap": self._execute_set_daily_cap,
                "set_lifetime_cap": self._execute_set_lifetime_cap,
                "set_risk_tier": self._execute_set_risk_tier,
                "switch_tier": self._execute_switch_tier,
                "clear_loss_data": lambda p: self.bot.handle_clear_loss_data({"message_id": None}),
                "clear_daily_loss": lambda p: self.bot.handle_clear_daily_loss({"message_id": None}),
                "lot_size_status": lambda p: self.bot.handle_lot_size_status({"message_id": None}),
                "reset_all_sl": lambda p: self.bot.handle_reset_all_sl(self._create_message_dict("reset_all_sl", {})),
                
                # SL System commands
                "sl_status": lambda p: self.bot.handle_sl_status({"message_id": None}),
                "sl_system_change": self._execute_sl_system_change,
                "sl_system_on": self._execute_sl_system_on,
                "complete_sl_system_off": lambda p: self.bot.handle_complete_sl_system_off({"message_id": None}),
                "view_sl_config": lambda p: self.bot.handle_view_sl_config({"message_id": None}),
                "set_symbol_sl": self._execute_set_symbol_sl,
                "reset_symbol_sl": self._execute_reset_symbol_sl,
                
                # Dual Order commands
                "dual_order_status": lambda p: self.bot.handle_dual_order_status({"message_id": None}),
                "toggle_dual_orders": lambda p: self.bot.handle_toggle_dual_orders({"message_id": None}),
                
                # Profit Booking commands
                "profit_status": lambda p: self.bot.handle_profit_status(self._create_message_dict("profit_status", {})),
                "profit_stats": lambda p: self.bot.handle_profit_stats(self._create_message_dict("profit_stats", {})),
                "toggle_profit_booking": lambda p: self.bot.handle_toggle_profit_booking(self._create_message_dict("toggle_profit_booking", {})),
                "set_profit_targets": self._execute_set_profit_targets,
                "profit_chains": lambda p: self.bot.handle_profit_chains(self._create_message_dict("profit_chains", {})),
                "stop_profit_chain": self._execute_stop_profit_chain,
                "stop_all_profit_chains": lambda p: self.bot.handle_stop_all_profit_chains(self._create_message_dict("stop_all_profit_chains", {})),
                "set_chain_multipliers": self._execute_set_chain_multipliers,
                "profit_config": lambda p: self.bot.handle_profit_config(self._create_message_dict("profit_config", {})),
                "profit_sl_status": lambda p: self.bot.handle_profit_sl_status(self._create_message_dict("profit_sl_status", {})),
                "profit_sl_mode": self._execute_profit_sl_mode,
                "enable_profit_sl": lambda p: self.bot.handle_enable_profit_sl(self._create_message_dict("enable_profit_sl", {})),
                "disable_profit_sl": lambda p: self.bot.handle_disable_profit_sl(self._create_message_dict("disable_profit_sl", {})),
                "set_profit_sl": self._execute_set_profit_sl,
                "reset_profit_sl": lambda p: self.bot.handle_reset_profit_sl(self._create_message_dict("reset_profit_sl", {})),
                
                # Autonomous Control
                "autonomous_dashboard": lambda p: self.bot.handle_autonomous_dashboard({"message_id": None}),
                "autonomous_mode": self._execute_autonomous_mode,
                "autonomous_status": lambda p: self.bot.handle_autonomous_status({"message_id": None}),
                "profit_sl_hunt": self._execute_profit_sl_hunt,
                
                # Settings commands
                "chains": lambda p: self.bot.handle_chains_status({"message_id": None}),
                
                # Diagnostic commands (15 total - 12 existing + 3 new export commands)
                "health_status": self._execute_health_status,
                "set_log_level": self._execute_set_log_level,
                "get_log_level": self._execute_get_log_level,
                "reset_log_level": self._execute_reset_log_level,
                "error_stats": self._execute_error_stats,
                "reset_errors": self._execute_reset_errors,
                "reset_health": self._execute_reset_health,
                "export_logs": self._execute_export_logs,
                "log_file_size": self._execute_log_file_size,
                "clear_old_logs": self._execute_clear_old_logs,
                "export_current_session": self._execute_export_current_session,
                "export_by_date": self._execute_export_by_date,
                "export_date_range": self._execute_export_date_range,
                "trading_debug_mode": self._execute_trading_debug_mode,
                "system_resources": self._execute_system_resources,
                
                # Deprecated/alias commands
                "set_sl_reductions": self._execute_set_sl_reduction,  # Deprecated but kept for compatibility
                "close_profit_chain": self._execute_stop_profit_chain,  # Alias for stop_profit_chain
            }
            
            if command not in command_map:
                error_msg = (
                    f"❌ *Unknown Command*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Command `{command}` is not recognized.\n\n"
                    f"Use /start to see all available commands."
                )
                self.bot.send_message(error_msg)
                return False
            
            # Execute command
            try:
                logger.info(f"CALLING HANDLER: {command} with formatted params: {formatted_params}")
                logger.debug(f"[MENU EXECUTION] User {user_id} executing command: {command} with params: {formatted_params}")
                
                # Verify handler exists before calling
                if command not in command_map:
                    raise AttributeError(f"Command '{command}' not found in command map")
                
                handler_func = command_map[command]
                if handler_func is None:
                    raise AttributeError(f"Handler function is None for command: {command}")
                
                # Verify handler is callable
                if not callable(handler_func):
                    raise AttributeError(f"Handler function is not callable: {handler_func}")
                
                logger.debug(f"✅ HANDLER FOUND: {handler_func}")
                logger.debug(f"✅ HANDLER VERIFIED: {handler_func} is callable")
                
                # Call the handler with proper error handling
                try:
                    logger.debug(f"[MENU EXECUTION] About to call handler for {command}")
                    logger.debug(f"[MENU EXECUTION] Handler function: {handler_func}")
                    logger.debug(f"[MENU EXECUTION] Formatted params: {formatted_params}")
                    logger.debug(f"📨 CALLING HANDLER with formatted_params: {formatted_params}")
                    
                    execution_steps["handler_call"] = True
                    logger.debug(f"📊 EXECUTION STEPS: {execution_steps}")
                    
                    # Execute handler directly (synchronous) and track result
                    result = handler_func(formatted_params)
                    logger.debug(f"🎯 HANDLER RESULT: {result}")
                    
                    logger.debug(f"[MENU EXECUTION] Handler {command} returned (no exception)")
                    logger.debug(f"🎯 HANDLER RETURNED: Command {command} completed")
                    
                    execution_steps["handler_complete"] = True
                    logger.debug(f"📊 EXECUTION STEPS: {execution_steps}")
                    
                    # Mark as successful IMMEDIATELY after handler returns
                    execution_record["status"] = "success"
                    execution_steps["success"] = True
                    logger.info(f"EXECUTION SUCCESS: {command} executed successfully for user {user_id}")
                    logger.debug(f"[MENU EXECUTION] [OK] Command {command} executed successfully")
                    logger.debug(f"✅ EXECUTION SUCCESS: {command}")
                    logger.debug(f"📊 FINAL EXECUTION STEPS: {execution_steps}")
                    logger.debug(f"[MENU EXECUTION] Marking execution as SUCCESS for {command}")
                    logger.debug(f"[MENU EXECUTION] Returning True for {command}")
                    return True
                except Exception as handler_error:
                    # Handler execution failed
                    execution_record["status"] = "failed"
                    execution_record["error"] = f"Handler execution error: {str(handler_error)}"
                    logger.debug(f"[MENU EXECUTION] [ERROR] Handler {command} threw exception: {handler_error}")
                    logger.debug(f"💥 EXECUTION ERROR: {str(handler_error)}")
                    import traceback
                    traceback.print_exc()
                    error_msg = (
                        f"❌ *Command Execution Failed*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"Command: `{command}`\n"
                        f"Error: {str(handler_error)[:200]}\n\n"
                        f"Please try again or contact support if the issue persists."
                    )
                    try:
                        self.bot.send_message(error_msg)
                    except:
                        pass
                    logger.error(f"EXECUTION FAILED: {command} - Handler error: {str(handler_error)}")
                    logger.debug(f"[MENU EXECUTION] Marking execution as FAILED for {command}")
                    return False
                
            except AttributeError as e:
                execution_record["status"] = "failed"
                execution_record["error"] = f"Handler missing: {str(e)}"
                # Handler method doesn't exist
                error_msg = (
                    f"❌ *Command Handler Missing*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Handler for `{command}` is not available.\n\n"
                    f"This may be a configuration issue. Please contact support."
                )
                self.bot.send_message(error_msg)
                logger.error(f"EXECUTION FAILED: {command} - Handler missing: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            except Exception as e:
                # Command execution failed
                execution_record["status"] = "failed"
                execution_record["error"] = str(e)
                error_msg = (
                    f"❌ *Command Execution Failed*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Command: `{command}`\n"
                    f"Error: {str(e)}\n\n"
                    f"Please check the command parameters and try again."
                )
                self.bot.send_message(error_msg)
                logger.error(f"EXECUTION FAILED: {command} - Execution error: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
        except Exception as e:
            execution_record["status"] = "failed"
            execution_record["error"] = f"Unexpected error: {str(e)}"
            error_msg = (
                f"❌ *Unexpected Error*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"An unexpected error occurred while executing `{command}`:\n"
                f"{str(e)}\n\n"
                f"Please try again or use /start to return to main menu."
            )
            self.bot.send_message(error_msg)
            logger.error(f"EXECUTION FAILED: {command} - Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_execution_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent execution log entries"""
        return self.execution_log[-limit:] if len(self.execution_log) > limit else self.execution_log
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_log:
            return {"total": 0, "success": 0, "failed": 0, "success_rate": 0.0}
        
        total = len(self.execution_log)
        success = sum(1 for record in self.execution_log if record.get("status") == "success")
        failed = total - success
        success_rate = (success / total * 100) if total > 0 else 0.0
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success_rate, 2)
        }
    
    # Helper methods for commands with parameters
    def _execute_pause_resume(self, params: Dict[str, Any]):
        """Execute pause/resume toggle"""
        if self.bot.trading_engine:
            if self.bot.trading_engine.is_paused:
                self.bot.handle_resume({"message_id": None})
            else:
                self.bot.handle_pause({"message_id": None})
    
    def _execute_simulation_mode(self, params: Dict[str, Any]):
        """Execute simulation mode command"""
        mode = params.get("mode", "status")
        msg = self._create_message_dict("simulation_mode", {"mode": mode})
        self.bot.handle_simulation_mode(msg)
    
    def _execute_tp_system(self, params: Dict[str, Any]):
        """Execute TP system command"""
        mode = params.get("mode", "status")
        msg = self._create_message_dict("tp_system", {"mode": mode})
        self.bot.handle_tp_system(msg)
    
    def _execute_sl_hunt(self, params: Dict[str, Any]):
        """Execute SL hunt command"""
        mode = params.get("mode", "status")
        msg = self._create_message_dict("sl_hunt", {"mode": mode})
        self.bot.handle_sl_hunt(msg)
    
    def _execute_exit_continuation(self, params: Dict[str, Any]):
        """Execute exit continuation command"""
        mode = params.get("mode", "status")
        msg = self._create_message_dict("exit_continuation", {"mode": mode})
        self.bot.handle_exit_continuation(msg)
    
    def _execute_set_monitor_interval(self, params: Dict[str, Any]):
        """Execute set monitor interval"""
        value = params.get("value")
        if value:
            msg = self._create_message_dict("set_monitor_interval", {"value": value})
            self.bot.handle_set_monitor_interval(msg)
    
    def _execute_set_sl_offset(self, params: Dict[str, Any]):
        """Execute set SL offset"""
        value = params.get("value")
        if value:
            msg = self._create_message_dict("set_sl_offset", {"value": value})
            self.bot.handle_set_sl_offset(msg)
    
    def _execute_set_cooldown(self, params: Dict[str, Any]):
        """Execute set cooldown"""
        value = params.get("value")
        if value:
            msg = self._create_message_dict("set_cooldown", {"value": value})
            self.bot.handle_set_cooldown(msg)
    
    def _execute_set_recovery_time(self, params: Dict[str, Any]):
        """Execute set recovery time"""
        value = params.get("value")
        if value:
            msg = self._create_message_dict("set_recovery_time", {"value": value})
            self.bot.handle_set_recovery_time(msg)
    
    def _execute_set_max_levels(self, params: Dict[str, Any]):
        """Execute set max levels"""
        value = params.get("value")
        if value:
            msg = self._create_message_dict("set_max_levels", {"value": value})
            self.bot.handle_set_max_levels(msg)
    
    def _execute_set_sl_reduction(self, params: Dict[str, Any]):
        """Execute set SL reduction"""
        value = params.get("value")
        if value:
            msg = self._create_message_dict("set_sl_reduction", {"value": value})
            self.bot.handle_set_sl_reduction(msg)
    
    def _execute_set_trend(self, params: Dict[str, Any]):
        """Execute set trend"""
        symbol = params.get("symbol")
        timeframe = params.get("timeframe")
        trend = params.get("trend")
        if symbol and timeframe and trend:
            msg = self._create_message_dict("set_trend", {"symbol": symbol, "timeframe": timeframe, "trend": trend})
            self.bot.handle_set_trend(msg)
    
    def _execute_set_auto(self, params: Dict[str, Any]):
        """Execute set auto"""
        symbol = params.get("symbol")
        timeframe = params.get("timeframe")
        if symbol and timeframe:
            msg = self._create_message_dict("set_auto", {"symbol": symbol, "timeframe": timeframe})
            self.bot.handle_set_auto(msg)
    
    def _execute_trend_mode(self, params: Dict[str, Any]):
        """Execute trend mode"""
        symbol = params.get("symbol")
        timeframe = params.get("timeframe")
        if symbol and timeframe:
            msg = self._create_message_dict("trend_mode", {"symbol": symbol, "timeframe": timeframe})
            self.bot.handle_trend_mode(msg)
    
    def _execute_set_lot_size(self, params: Dict[str, Any]):
        """Execute set lot size with tier parameter"""
        logger.debug(f"[EXECUTE SET_LOT_SIZE] Received params: {params}")
        tier = params.get("tier")
        lot = params.get("lot_size") or params.get("lot")  # Support both param names
        
        if not tier or not lot:
            error_msg = f"❌ Missing parameters. Tier: {tier}, Lot: {lot}"
            logger.error(f"[EXECUTE SET_LOT_SIZE ERROR] {error_msg}")
            self.bot.send_message(error_msg)
            return
        
        logger.debug(f"[EXECUTE SET_LOT_SIZE] Calling handler with tier={tier}, lot_size={lot}")
        msg = self._create_message_dict("set_lot_size", {"tier": tier, "lot_size": lot})
        self.bot.handle_set_lot_size(msg)
    
    def _execute_set_daily_cap(self, params: Dict[str, Any]):
        """Execute set daily cap with tier parameter"""
        logger.debug(f"[EXECUTE SET_DAILY_CAP] Received params: {params}")
        tier = params.get("tier")
        amount = params.get("amount")
        
        if not tier or not amount:
            error_msg = f"❌ Missing parameters. Tier: {tier}, Amount: {amount}"
            logger.error(f"[EXECUTE SET_DAILY_CAP ERROR] {error_msg}")
            self.bot.send_message(error_msg)
            return
        
        logger.debug(f"[EXECUTE SET_DAILY_CAP] Calling handler with tier={tier}, amount={amount}")
        msg = self._create_message_dict("set_daily_cap", {"tier": tier, "amount": amount})
        self.bot.handle_set_daily_cap(msg)
    
    def _execute_set_lifetime_cap(self, params: Dict[str, Any]):
        """Execute set lifetime cap with tier parameter"""
        logger.debug(f"[EXECUTE SET_LIFETIME_CAP] Received params: {params}")
        tier = params.get("tier")
        amount = params.get("amount")
        
        if not tier or not amount:
            error_msg = f"❌ Missing parameters. Tier: {tier}, Amount: {amount}"
            logger.error(f"[EXECUTE SET_LIFETIME_CAP ERROR] {error_msg}")
            self.bot.send_message(error_msg)
            return
        
        logger.debug(f"[EXECUTE SET_LIFETIME_CAP] Calling handler with tier={tier}, amount={amount}")
        msg = self._create_message_dict("set_lifetime_cap", {"tier": tier, "amount": amount})
        self.bot.handle_set_lifetime_cap(msg)
    
    def _execute_set_risk_tier(self, params: Dict[str, Any]):
        """Execute set risk tier with full validation"""
        logger.debug(f"[EXECUTE SET_RISK_TIER] Received params: {params}")
        tier = params.get("tier")  # Changed from balance to tier
        daily = params.get("daily")
        lifetime = params.get("lifetime")
        
        if not tier or not daily or not lifetime:
            error_msg = f"❌ Missing parameters. Tier: {tier}, Daily: {daily}, Lifetime: {lifetime}"
            logger.error(f"[EXECUTE SET_RISK_TIER ERROR] {error_msg}")
            self.bot.send_message(error_msg)
            return
        
        logger.debug(f"[EXECUTE SET_RISK_TIER] Calling handler with tier={tier}, daily={daily}, lifetime={lifetime}")
        msg = self._create_message_dict("set_risk_tier", {"tier": tier, "daily": daily, "lifetime": lifetime})
        self.bot.handle_set_risk_tier(msg)
    
    def _execute_sl_system_change(self, params: Dict[str, Any]):
        """Execute SL system change"""
        system = params.get("system")
        logger.debug(f"[EXECUTE SL_SYSTEM_CHANGE] Params: {params}, system: {system}")
        if system:
            msg = self._create_message_dict("sl_system_change", {"system": system})
            logger.debug(f"[EXECUTE SL_SYSTEM_CHANGE] Message dict: {msg}")
            self.bot.handle_sl_system_change(msg)
        else:
            logger.debug(f"[EXECUTE SL_SYSTEM_CHANGE ERROR] System parameter missing")
            self.bot.send_message("❌ Error: System parameter is required. Please try again.")
    
    def _execute_sl_system_on(self, params: Dict[str, Any]):
        """Execute SL system on"""
        system = params.get("system")
        if system:
            msg = self._create_message_dict("sl_system_on", {"system": system})
            self.bot.handle_sl_system_on(msg)
    
    def _execute_set_symbol_sl(self, params: Dict[str, Any]):
        """Execute set symbol SL"""
        symbol = params.get("symbol")
        percent = params.get("percent") or params.get("percentage")  # Support both
        if symbol and percent:
            msg = self._create_message_dict("set_symbol_sl", {"symbol": symbol, "percent": percent})
            self.bot.handle_set_symbol_sl(msg)
    
    def _execute_reset_symbol_sl(self, params: Dict[str, Any]):
        """Execute reset symbol SL"""
        symbol = params.get("symbol")
        if symbol:
            msg = self._create_message_dict("reset_symbol_sl", {"symbol": symbol})
            self.bot.handle_reset_symbol_sl(msg)
    
    def _execute_set_profit_targets(self, params: Dict[str, Any]):
        """Execute set profit targets - now using button presets"""
        from .menu_constants import PROFIT_TARGET_PRESETS
        
        preset = params.get("preset")
        if preset and preset in PROFIT_TARGET_PRESETS:
            # Convert preset name to actual target values
            targets = PROFIT_TARGET_PRESETS[preset]
            msg = self._create_message_dict("set_profit_targets", {"targets": targets})
            self.bot.handle_set_profit_targets(msg)
        else:
            logger.error(f"Invalid profit target preset: {preset}")
            self.bot.send_message(f"❌ Invalid preset: {preset}")
    
    def _execute_stop_profit_chain(self, params: Dict[str, Any]):
        """Execute stop profit chain"""
        chain_id = params.get("chain_id")
        if chain_id:
            msg = self._create_message_dict("stop_profit_chain", {"chain_id": chain_id})
            self.bot.handle_stop_profit_chain(msg)
    
    def _execute_set_chain_multipliers(self, params: Dict[str, Any]):
        """Execute set chain multipliers - now using button presets"""
        from .menu_constants import MULTIPLIER_PRESETS
        
        preset = params.get("preset")
        if preset and preset in MULTIPLIER_PRESETS:
            # Convert preset name to actual multiplier values
            multipliers = MULTIPLIER_PRESETS[preset]
            msg = self._create_message_dict("set_chain_multipliers", {"multipliers": multipliers})
            self.bot.handle_set_chain_multipliers(msg)
        else:
            logger.error(f"Invalid chain multiplier preset: {preset}")
            self.bot.send_message(f"❌ Invalid preset: {preset}")
    
    def _execute_profit_sl_mode(self, params: Dict[str, Any]):
        """Execute profit SL mode"""
        logger.debug(f"[EXECUTE PROFIT_SL_MODE] START - Params: {params}")
        try:
            mode = params.get("profit_sl_mode") or params.get("mode")  # Support both for backward compatibility
            logger.debug(f"[EXECUTE PROFIT_SL_MODE] Extracted mode: {mode}")
            if mode:
                logger.debug(f"[EXECUTE PROFIT_SL_MODE] Creating message dict...")
                msg = self._create_message_dict("profit_sl_mode", {"profit_sl_mode": mode})
                logger.debug(f"[EXECUTE PROFIT_SL_MODE] Message dict created: {msg}")
                logger.debug(f"[EXECUTE PROFIT_SL_MODE] About to call handle_profit_sl_mode...")
                try:
                    result = self.bot.handle_profit_sl_mode(msg)
                    logger.debug(f"[EXECUTE PROFIT_SL_MODE] handle_profit_sl_mode returned: {result}")
                    logger.debug(f"🎯 HANDLER RETURNED: {result}")
                    
                    # CRITICAL: Check if handler returned properly
                    if result is True:
                        logger.debug(f"✅ HANDLER COMPLETED SUCCESSFULLY")
                        logger.debug(f"✅ EXECUTION SUCCESS: profit_sl_mode completed successfully")
                        logger.debug(f"🎉 FINAL SUCCESS: Command profit_sl_mode executed completely")
                    elif result is False:
                        logger.debug(f"❌ HANDLER RETURNED FALSE")
                        logger.debug(f"❌ EXECUTION FAILED: Handler returned False")
                    else:
                        logger.debug(f"⚠️ HANDLER RETURNED: {result} (unexpected)")
                except Exception as handler_error:
                    logger.debug(f"[EXECUTE PROFIT_SL_MODE] handle_profit_sl_mode threw exception: {handler_error}")
                    logger.debug(f"💥 EXECUTION ERROR: {handler_error}")
                    import traceback
                    traceback.print_exc()
                    raise
            else:
                logger.debug(f"[EXECUTE PROFIT_SL_MODE ERROR] Mode parameter missing")
                self.bot.send_message("❌ Error: Mode parameter is required. Please try again.")
            logger.debug(f"[EXECUTE PROFIT_SL_MODE] END - Success")
        except Exception as e:
            logger.debug(f"[EXECUTE PROFIT_SL_MODE] END - Exception: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _execute_switch_tier(self, params: Dict[str, Any]):
        """Execute tier switch with validation"""
        logger.debug(f"[EXECUTE SWITCH_TIER] Received params: {params}")
        tier = params.get("tier")
        
        if not tier:
            error_msg = f"❌ Missing tier parameter"
            logger.error(f"[EXECUTE SWITCH_TIER ERROR] {error_msg}")
            self.bot.send_message(error_msg)
            return
        
        logger.debug(f"[EXECUTE SWITCH_TIER] Switching to tier: {tier}")
        msg = self._create_message_dict("switch_tier", {"tier": tier})
        self.bot.handle_switch_tier(msg)
    
    def _execute_set_profit_sl(self, params: Dict[str, Any]):
        """Execute set profit SL"""
        logic = params.get("logic")
        amount = params.get("amount")
        if logic and amount:
            msg = self._create_message_dict("set_profit_sl", {"logic": logic, "amount": amount})
            self.bot.handle_set_profit_sl(msg)
    
    def _get_required_params(self, command: str) -> List[str]:
        """Get required parameters for a command from COMMAND_PARAM_MAP"""
        if command in COMMAND_PARAM_MAP:
            return COMMAND_PARAM_MAP[command].get("params", [])
        return []
    
    def _validate_dependencies(self, command: str) -> bool:
        """Check if all required dependencies for a command are available"""
        required_deps = COMMAND_DEPENDENCIES.get(command, [])
        for dep in required_deps:
            if not hasattr(self.bot, dep):
                print(f"Missing dependency '{dep}' for command '{command}'")
                return False
            
            dep_value = getattr(self.bot, dep, None)
            if dep_value is None:
                print(f"Dependency '{dep}' is None for command '{command}'")
                return False
            
            # Special check for trading_engine's sub-managers
            if dep == "trading_engine":
                if command in ["stop_profit_chain", "profit_chains", "stop_all_profit_chains"]:
                    if not hasattr(self.bot.trading_engine, 'profit_booking_manager'):
                        print(f"Missing profit_booking_manager in trading_engine for command '{command}'")
                        return False
                    if self.bot.trading_engine.profit_booking_manager is None:
                        print(f"profit_booking_manager is None for command '{command}'")
                        return False
        return True
    
        return True
    
    def _execute_reset_reentry_config(self, params: Dict[str, Any]):
        """Execute reset reentry config"""
        msg = self._create_message_dict("reset_reentry_config", {})
        self.bot.handle_reset_reentry_config(msg)

    def _execute_autonomous_mode(self, params: Dict[str, Any]):
        """Execute autonomous mode command"""
        mode = params.get("mode", "status")
        msg = self._create_message_dict("autonomous_mode", {"mode": mode})
        self.bot.handle_autonomous_mode(msg)
    
    def _execute_autonomous_status(self, params: Dict[str, Any]):
        """Execute autonomous status command"""
        msg = self._create_message_dict("autonomous_status", {})
        self.bot.handle_autonomous_status(msg)
        
    def _execute_profit_sl_hunt(self, params: Dict[str, Any]):
        """Execute profit sl hunt command"""
        mode = params.get("mode", "status")
        msg = self._create_message_dict("profit_sl_hunt", {"mode": mode})
        self.bot.handle_profit_sl_hunt(msg)
    
    # ========== NEW DIAGNOSTIC COMMANDS ==========
    
    def _execute_health_status(self, params: Dict[str, Any]):
        """Show comprehensive system health dashboard"""
        try:
            import time
            import os
            
            # Get MT5 status
            mt5_status = "✅ Connected" if self.bot.trading_engine.mt5_client.initialized else "❌ Disconnected"
            mt5_errors = self.bot.trading_engine.mt5_client.connection_errors
            mt5_max_errors = self.bot.trading_engine.mt5_client.max_connection_errors
            
            # Get circuit breaker status
            trading_monitor_errors = self.bot.trading_engine.monitor_error_count
            trading_max_errors = self.bot.trading_engine.max_monitor_errors
            trading_status = "✅ Healthy" if trading_monitor_errors < 5 else "⚠️ Degraded"
            
            price_monitor_errors = self.bot.trading_engine.price_monitor.monitor_error_count
            price_max_errors = self.bot.trading_engine.price_monitor.max_monitor_errors
            price_status = "✅ Healthy" if price_monitor_errors < 5 else "⚠️ Degraded"
            
            # Get uptime (use creation time if start_time not available)
            if hasattr(self.bot.trading_engine, 'start_time'):
                uptime_seconds = time.time() - self.bot.trading_engine.start_time
            else:
                # Fallback: use current time (will show 0 uptime, but won't crash)
                uptime_seconds = 0
            uptime_hours = uptime_seconds / 3600
            
            # Get log file size
            log_size = 0
            # FIX: Check REAL bot logs from standard Python logging (bot.log)
            if os.path.exists("logs/bot.log"):
                log_size = os.path.getsize("logs/bot.log") / (1024 * 1024)  # MB
            
            # Get MT5 account info
            mt5_login = self.bot.config.get('mt5_login', 'N/A')
            mt5_server = self.bot.config.get('mt5_server', 'N/A')
            
            # Get trading mode
            is_simulation = self.bot.config.get('simulate_orders', False)
            trading_mode = "SIMULATION" if is_simulation else "LIVE TRADING"
            
            # Get paused status
            is_paused = self.bot.trading_engine.is_paused
            
            text = (
                "🏥 *SYSTEM HEALTH DASHBOARD*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "📡 *MT5 Connection:*\n"
                f"• Status: {mt5_status}\n"
                f"• Errors: {mt5_errors}/{mt5_max_errors}\n"
                f"• Account: {mt5_login}\n"
                f"• Server: {mt5_server}\n\n"
                "⚙️ *Trading Engine:*\n"
                f"• Status: {trading_status}\n"
                f"• Monitor Errors: {trading_monitor_errors}/{trading_max_errors}\n"
                f"• Paused: {'Yes' if is_paused else 'No'}\n\n"
                "📊 *Price Monitor:*\n"
                f"• Status: {price_status}\n"
                f"• Monitor Errors: {price_monitor_errors}/{price_max_errors}\n\n"
                "📈 *System Info:*\n"
                f"• Uptime: {uptime_hours:.1f} hours\n"
                f"• Log Size: {log_size:.2f} MB / 10 MB\n"
                f"• Trading Mode: {trading_mode}\n\n"
                "💡 *Tip:* Use /reset_health to clear error counts"
            )
            
            self.bot.send_message(text)
            return True
            
        except Exception as e:
            logger.error(f"Health status error: {e}")
            self.bot.send_message(f"❌ Error retrieving health status: {str(e)}")
            return False
    
    def _save_log_level_to_config(self, level: str):
        """Save log level to config file for persistence across restarts"""
        try:
            import json
            import os
            
            config_path = "config/logging_settings.json"
            
            # Create config directory if it doesn't exist
            os.makedirs("config", exist_ok=True)
            
            # Load existing config or create new
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {}
            
            # Update log level
            config['log_level'] = level
            
            # Save back to file
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved log level '{level}' to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save log level to config: {e}")
            return False
    
    def _execute_set_log_level(self, params: Dict[str, Any]):
        """Change logging level dynamically with REAL verification"""
        try:
            from src.utils.logging_config import logging_config, LogLevel
            import logging as std_logging
            
            level_name = params.get("level", "INFO").upper()
            
            # Map to LogLevel enum
            level_map = {
                "DEBUG": LogLevel.DEBUG,
                "INFO": LogLevel.INFO,
                "WARNING": LogLevel.WARNING,
                "ERROR": LogLevel.ERROR,
                "CRITICAL": LogLevel.CRITICAL
            }
            
            if level_name not in level_map:
                self.bot.send_message(
                    f"❌ Invalid level: {level_name}\n\n"
                    f"Valid levels: DEBUG, INFO, WARNING, ERROR, CRITICAL"
                )
                return False
            
            # Get previous level
            old_level = logging_config.current_level.name
            
            # Set new level in our custom logger
            logging_config.set_level(level_map[level_name])
            
            # ALSO set Python's standard logging level for complete effect
            std_level_map = {
                "DEBUG": std_logging.DEBUG,
                "INFO": std_logging.INFO,
                "WARNING": std_logging.WARNING,
                "ERROR": std_logging.ERROR,
                "CRITICAL": std_logging.CRITICAL
            }
            
            # Update root logger (this affects what gets logged)
            root_logger = std_logging.getLogger()
            # Keep root at DEBUG, let handlers filter
            
            # Update ALL handlers to use new level (this is critical!)
            for handler in root_logger.handlers:
                handler.setLevel(std_level_map[level_name])
                logger.debug(f"Updated handler {handler.__class__.__name__} to {level_name}")
            
            # Save to config for persistence across restarts
            self._save_log_level_to_config(level_name)
            
            # Verify the change worked
            new_level = logging_config.current_level.name
            verified = (new_level == level_name)
            
            text = (
                "✅ *Log Level Changed Successfully*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"• Previous: `{old_level}`\n"
                f"• New: `{level_name}`\n"
                f"• Verified: {'✅ YES' if verified else '❌ NO'}\n\n"
                "📊 *Impact on Logging:*\n"
            )
            
            if level_name == "DEBUG":
                text += (
                    "🔍 *DEBUG MODE ACTIVE*\n"
                    "• All logs visible (max detail)\n"
                    "• Trading decisions fully logged\n"
                    "• Signal analysis details shown\n"
                    "• Parameter validations logged\n"
                    "• Performance may be slower\n"
                    "• Log file will grow faster\n\n"
                    "⚠️ Use for troubleshooting only!"
                )
            elif level_name == "INFO":
                text += (
                    "ℹ️ *INFO MODE (RECOMMENDED)*\n"
                    "• Important events logged\n"
                    "• Trading actions recorded\n"
                    "• Routine commands suppressed\n"
                    "• Optimal for production\n"
                    "• Balanced detail vs performance"
                )
            elif level_name == "WARNING":
                text += (
                    "⚠️ *WARNING MODE*\n"
                    "• Only warnings and errors\n"
                    "• Minimal log output\n"
                    "• Good for low-noise monitoring\n"
                    "• May miss important events"
                )
            elif level_name == "ERROR":
                text += (
                    "❌ *ERROR MODE*\n"
                    "• Only errors logged\n"
                    "• Very minimal output\n"
                    "• Use when debugging errors only"
                )
            else:  # CRITICAL
                text += (
                    "🚨 *CRITICAL MODE*\n"
                    "• Only critical failures logged\n"
                    "• Almost no output\n"
                    "• Not recommended for trading"
                )
            
            # FIX: Reference correct log file
            text += f"\n\n💡 Check logs/bot.log to see effect"
            
            self.bot.send_message(text)
            
            # Display change in console immediately
            print(f"═══════════════════════════════════════")
            print(f"📊 LOGGING LEVEL CHANGED: {old_level} → {level_name}")
            print(f"═══════════════════════════════════════")
            
            logger.info(f"Log level changed: {old_level} → {level_name} (verified: {verified})")
            
            # Test the new log level immediately
            logger.debug(f"TEST: This is a DEBUG message (level={level_name})")
            logger.info(f"TEST: This is an INFO message (level={level_name})")
            
            return True
            
        except Exception as e:
            logger.error(f"Set log level error: {e}")
            import traceback
            self.bot.send_message(f"❌ Error changing log level: {str(e)}\n\nCheck terminal for details")
            traceback.print_exc()
            return False
    

    def _execute_get_log_level(self, params: Dict[str, Any]):
        """Show current log level with descriptions"""
        try:
            from src.utils.logging_config import logging_config
            
            current = logging_config.current_level.name
            
            text = (
                "📊 *CURRENT LOG LEVEL*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎯 *Active Level:* `{current}`\n\n"
            )
            
            # Description based on current level
            if current == "DEBUG":
                text += (
                    "🔍 *DEBUG MODE*\n"
                    "• Maximum verbosity\n"
                    "• All details logged\n"
                    "• Slower performance\n"
                    "• Large log files\n"
                )
            elif current == "INFO":
                text += (
                    "ℹ️ *INFO MODE (Recommended)*\n"
                    "• Important events only\n"
                    "• Balanced detail\n"
                    "• Optimal for production\n"
                    "• Moderate log size\n"
                )
            elif current == "WARNING":
                text += (
                    "⚠️ *WARNING MODE*\n"
                    "• Warnings & errors only\n"
                    "• Minimal output\n"
                    "• May miss info events\n"
                )
            elif current == "ERROR":
                text += (
                    "❌ *ERROR MODE*\n"
                    "• Errors only\n"
                    "• Very quiet\n"
                )
            else:  # CRITICAL
                text += (
                    "🚨 *CRITICAL MODE*\n"
                    "• Critical failures only\n"
                    "• Almost silent\n"
                )
            
            text += "\n\n📋 *Available Levels:*\n"
            levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            for lvl in levels:
                emoji = "✅" if lvl == current else "  "
                text += f"{emoji} {lvl}\n"
            
            text += "\n💡 Use /set_log_level to change"
            
            self.bot.send_message(text)
            logger.info(f"Displayed current log level: {current}")
            return True
            
        except Exception as e:
            logger.error(f"Get log level error: {e}")
            self.bot.send_message(f"❌ Error checking log level: {str(e)}")
            return False
    
    def _execute_reset_log_level(self, params: Dict[str, Any]):
        """Reset log level to default INFO"""
        try:
            from src.utils.logging_config import logging_config, LogLevel
            import logging as std_logging
            
            old_level = logging_config.current_level.name
            
            # Reset to INFO
            logging_config.set_level(LogLevel.INFO)
            std_logging.getLogger().setLevel(std_logging.INFO)
            
            # Save to config
            self._save_log_level_to_config("INFO")
            
            # Verify
            new_level = logging_config.current_level.name
            verified = (new_level == "INFO")
            
            text = (
                "✅ *Log Level Reset to Default*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"• Previous: `{old_level}`\n"
                f"• Reset to: `INFO` (default)\n"
                f"• Verified: {'✅ YES' if verified else '❌ NO'}\n\n"
                "ℹ️ *INFO Level Features:*\n"
                "• Important events logged\n"
                "• Trading actions recorded\n"
                "• Optimal for production\n"
                "• Balanced performance\n\n"
                "💡 This setting persists across restarts"
            )
            
            self.bot.send_message(text)
            logger.info(f"Reset log level from {old_level} to INFO")
            return True
            
        except Exception as e:
            logger.error(f"Reset log level error: {e}")
            self.bot.send_message(f"❌ Error resetting log level: {str(e)}")
            return False

    def _execute_error_stats(self, params: Dict[str, Any]):
        """Show detailed error statistics with REAL error data from logs + DEBUG INFO"""
        try:
            from collections import Counter
            from src.utils.optimized_logger import logger as opt_logger
            import os
            
            # Get trading errors from optimized logger
            trading_errors = opt_logger.trading_errors_count
            total_trading_errors = sum(trading_errors.values())
            
            # Get top 5 errors
            top_errors = Counter(trading_errors).most_common(5)
            
            # Read ACTUAL errors from log file (last 100 lines) - WITH DETAILED DEBUG
            recent_errors = []
            # FIX: Read REAL bot logs from standard Python logging (bot.log)
            log_file = "logs/bot.log"
            log_file_exists = os.path.exists(log_file)
            log_file_size = 0
            total_lines_read = 0
            lines_checked = 0
            
            if log_file_exists:
                try:
                    log_file_size = os.path.getsize(log_file) / 1024  # KB
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines_read = len(lines)
                        
                        # Get last 100 lines and filter for errors
                        last_100 = lines[-100:] if len(lines) >= 100 else lines
                        lines_checked = len(last_100)
                        
                        for line in last_100:
                            if "❌" in line or "ERROR" in line or "CRITICAL" in line or "⚠️" in line:
                                # Extract timestamp and error
                                if "]" in line:
                                    timestamp = line.split("]")[0].strip("[")
                                    error_msg = line.split("]")[1].strip()
                                    recent_errors.append((timestamp, error_msg[:100]))
                except Exception as e:
                    logger.error(f"Failed to read log file: {e}")
            
            # Circuit breaker info
            trading_breaker_status = "🟢 OK" if self.bot.trading_engine.monitor_error_count < 10 else "🔴 TRIGGERED"
            price_breaker_status = "🟢 OK" if self.bot.trading_engine.price_monitor.monitor_error_count < 10 else "🔴 TRIGGERED"
            
            # MT5 reconnections
            mt5_reconnects = self.bot.trading_engine.mt5_client.connection_errors
            mt5_status_emoji = "✅" if mt5_reconnects == 0 else "⚠️" if mt5_reconnects < 3 else "🚨"
            
            text = (
                "📊 *ERROR STATISTICS*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "📈 *Summary:*\n"
                f"• Total Trading Errors: {total_trading_errors}\n"
                f"• Unique Error Types: {len(trading_errors)}\n"
                f"• MT5 Reconnects: {mt5_status_emoji} {mt5_reconnects}\n"
                f"• Recent Log Errors: {len(recent_errors)}\n\n"
                "🔍 *Log File Analysis:*\n"
                f"• File Exists: {'✅ YES' if log_file_exists else '❌ NO'}\n"
                f"• File Size: {log_file_size:.1f} KB\n"
                f"• Total Lines: {total_lines_read}\n"
                f"• Lines Checked: {lines_checked} (last 100)\n"
                f"• Errors Found: {len(recent_errors)}\n\n"
            )
            
            if top_errors:
                text += "🔝 *Top Errors (Last Session):*\n"
                for i, (error_msg, count) in enumerate(top_errors, 1):
                    # Truncate long messages
                    short_msg = error_msg[:50] + "..." if len(error_msg) > 50 else error_msg
                    text += f"{i}. `{short_msg}` ({count}x)\n"
                text += "\n"
            
            # Show recent actual errors from logs
            if recent_errors:
                text += "🕐 *Recent Errors from Logs:*\n"
                # Show last 3 errors
                for timestamp, error_msg in recent_errors[-3:]:
                    text += f"• {timestamp}: {error_msg[:60]}...\n"
                text += "\n"
            else:
                text += "✅ *No Errors Found in Logs!*\n"
                if log_file_exists and lines_checked > 0:
                    text += f"• Checked {lines_checked} recent log lines\n"
                    text += "• No ERROR/CRITICAL/❌ patterns found\n"
                    text += "• Bot is running clean! 🎉\n\n"
                else:
                    text += "• Log file may be empty or missing\n\n"
            
            text += (
                "🛡️ *Circuit Breakers:*\n"
                f"• Trading Monitor: {trading_breaker_status} "
                f"({self.bot.trading_engine.monitor_error_count}/{self.bot.trading_engine.max_monitor_errors})\n"
                f"• Price Monitor: {price_breaker_status} "
                f"({self.bot.trading_engine.price_monitor.monitor_error_count}/{self.bot.trading_engine.price_monitor.max_monitor_errors})\n\n"
                "💡 *Actions:*\n"
                "• Use /reset_errors to clear counters\n"
                "• Use /health_status for full system check\n"
                "• Check logs/bot.log for full details"
            )
            
            self.bot.send_message(text)
            return True
            
        except Exception as e:
            logger.error(f"Error stats error: {e}")
            self.bot.send_message(f"❌ Error retrieving error stats: {str(e)}")
            return False
    
    def _execute_reset_errors(self, params: Dict[str, Any]):
        """Reset error counters"""
        try:
            from src.utils.optimized_logger import logger as opt_logger
            
            # Clear trading errors
            old_error_count = sum(opt_logger.trading_errors_count.values())
            opt_logger.trading_errors_count.clear()
            
            # Clear missing order checks
            opt_logger.missing_order_checks.clear()
            
            text = (
                "✅ *Error Counters Reset*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"• Previous Total Errors: {old_error_count}\n"
                f"• All error counters cleared\n"
                f"• Missing order checks cleared\n\n"
                "💡 Fresh start for error tracking!"
            )
            
            self.bot.send_message(text)
            logger.info("Error counters reset by user command")
            return True
            
        except Exception as e:
            logger.error(f"Reset errors error: {e}")
            self.bot.send_message(f"❌ Error resetting errors: {str(e)}")
            return False
    
    def _execute_reset_health(self, params: Dict[str, Any]):
        """Reset health counters"""
        try:
            # Reset circuit breaker counters
            old_trading_errors = self.bot.trading_engine.monitor_error_count
            old_price_errors = self.bot.trading_engine.price_monitor.monitor_error_count
            old_mt5_errors = self.bot.trading_engine.mt5_client.connection_errors
            
            self.bot.trading_engine.monitor_error_count = 0
            self.bot.trading_engine.price_monitor.monitor_error_count = 0
            self.bot.trading_engine.mt5_client.connection_errors = 0
            
            text = (
                "✅ *Health Counters Reset*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "📊 *Previous Error Counts:*\n"
                f"• Trading Monitor: {old_trading_errors}\n"
                f"• Price Monitor: {old_price_errors}\n"
                f"• MT5 Connection: {old_mt5_errors}\n\n"
                "🟢 All health counters reset to 0\n\n"
                "💡 Circuit breakers are now reset!"
            )
            
            self.bot.send_message(text)
            logger.info("Health counters reset by user command")
            return True
            
        except Exception as e:
            logger.error(f"Reset health error: {e}")
            self.bot.send_message(f"❌ Error resetting health: {str(e)}")
            return False
    
    def _execute_export_logs(self, params: Dict[str, Any]):
        """Export last N lines of log file"""
        try:
            import os
            import gzip
            from datetime import datetime
            
            lines = int(params.get("lines", 100))
            # FIX: Read REAL bot logs from standard Python logging (bot.log)
            log_file = "logs/bot.log"
            
            if not os.path.exists(log_file):
                self.bot.send_message("❌ Log file not found!")
                return False
            
            # Create export directory
            export_dir = "logs/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Read last N lines
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                export_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Create export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"bot_logs_{timestamp}_{lines}lines.txt"
            export_path = os.path.join(export_dir, export_filename)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.writelines(export_lines)
            
            file_size_kb = os.path.getsize(export_path) / 1024
            
            # Compress if > 1MB
            if file_size_kb > 1024:
                gz_path = export_path + ".gz"
                with open(export_path, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(export_path)
                export_path = gz_path
                export_filename = export_filename + ".gz"
                file_size_kb = os.path.getsize(export_path) / 1024
            
            text = f"""✅ *Logs Exported Successfully*
━━━━━━━━━━━━━━━━━━━━━━━━

📄 *File:* `{export_filename}`
📊 *Lines Exported:* {len(export_lines)}
💾 *File Size:* {file_size_kb:.2f} KB
📁 *Location:* `{export_path}`

💡 File ready for download!"""
            
            self.bot.send_message(text)
            
            # Try to send file via Telegram
            try:
                if hasattr(self.bot, 'send_document'):
                    self.bot.send_document(export_path, filename=export_filename, caption=f"Bot logs export - {lines} lines")
                    logger.info(f"Logs exported and sent to Telegram: {export_filename}")
                else:
                    logger.warning("send_document method not available in telegram_bot")
            except Exception as e:
                logger.warning(f"Could not send file via Telegram: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Export logs error: {e}")
            self.bot.send_message(f"❌ Error exporting logs: {str(e)}")
            return False
    
    def _filter_logs_by_date(self, log_file: str, start_date: str, end_date: str = None):
        """
        Filter log lines by date range
        
        Args:
            log_file: Path to log file
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (optional, defaults to start_date)
        
        Returns:
            Tuple of (filtered_lines, first_timestamp, last_timestamp)
        """
        from datetime import datetime
        
        if end_date is None:
            end_date = start_date
        
        # Parse date strings
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Set end date to end of day
        end_dt = end_dt.replace(hour=23, minute=59, second=59)
        
        filtered_lines = []
        first_timestamp = None
        last_timestamp = None
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Extract timestamp from log line (format: YYYY-MM-DD HH:MM:SS)
                if len(line) >= 19 and line[4] == '-' and line[7] == '-' and line[10] == ' ':
                    try:
                        timestamp_str = line[:19]  # "2025-11-23 01:06:11"
                        log_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        
                        # Check if within date range
                        if start_dt <= log_dt <= end_dt:
                            filtered_lines.append(line)
                            if first_timestamp is None:
                                first_timestamp = timestamp_str
                            last_timestamp = timestamp_str
                    except ValueError:
                        # If timestamp parsing fails, skip line
                        continue
        
        return filtered_lines, first_timestamp, last_timestamp
    
    def _execute_export_current_session(self, params: Dict[str, Any]):
        """Export logs from current bot session only (today's live data)"""
        try:
            import os
            import gzip
            from datetime import datetime
            
            log_file = "logs/bot.log"
            
            if not os.path.exists(log_file):
                self.bot.send_message("❌ Log file not found!")
                return False
            
            # Get today's date
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Filter logs for today
            filtered_lines, first_ts, last_ts = self._filter_logs_by_date(log_file, today)
            
            if not filtered_lines:
                self.bot.send_message(f"❌ No logs found for current session ({today})")
                return False
            
            # Create export directory
            export_dir = "logs/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Create export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"current_session_{timestamp}.txt"
            export_path = os.path.join(export_dir, export_filename)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            
            file_size_kb = os.path.getsize(export_path) / 1024
            
            # Compress if > 1MB
            if file_size_kb > 1024:
                gz_path = export_path + ".gz"
                with open(export_path, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(export_path)
                export_path = gz_path
                export_filename = export_filename + ".gz"
                file_size_kb = os.path.getsize(export_path) / 1024
            
            text = f"""✅ *Current Session Logs Exported*
━━━━━━━━━━━━━━━━━━━━━━━━

📅 *Date:* {today}
⏰ *Session Period:*
   From: {first_ts}
   To: {last_ts}

📄 *File:* `{export_filename}`
📊 *Lines Exported:* {len(filtered_lines)}
💾 *File Size:* {file_size_kb:.2f} KB
📁 *Location:* `{export_path}`

💡 File contains only today's logs!"""
            
            self.bot.send_message(text)
            
            # Try to send file via Telegram
            try:
                if hasattr(self.bot, 'send_document'):
                    self.bot.send_document(export_path, filename=export_filename, caption=f"Current session logs - {today}")
                    logger.info(f"Current session logs exported: {export_filename}")
                else:
                    logger.warning("send_document method not available in telegram_bot")
            except Exception as e:
                logger.warning(f"Could not send file via Telegram: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Export current session error: {e}")
            self.bot.send_message(f"❌ Error exporting current session: {str(e)}")
            return False
    
    def _execute_export_by_date(self, params: Dict[str, Any]):
        """Export logs from a specific date"""
        try:
            import os
            import gzip
            from datetime import datetime
            
            date = params.get("date")
            if not date:
                self.bot.send_message("❌ Date parameter required!")
                return False
            
            log_file = "logs/bot.log"
            
            if not os.path.exists(log_file):
                self.bot.send_message("❌ Log file not found!")
                return False
            
            # Filter logs for specific date
            filtered_lines, first_ts, last_ts = self._filter_logs_by_date(log_file, date)
            
            if not filtered_lines:
                # Format date for display (DD-MM-YYYY)
                display_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
                self.bot.send_message(f"❌ No logs found for date: {display_date}")
                return False
            
            # Create export directory
            export_dir = "logs/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Create export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"logs_{date}_{timestamp}.txt"
            export_path = os.path.join(export_dir, export_filename)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            
            file_size_kb = os.path.getsize(export_path) / 1024
            
            # Compress if > 1MB
            if file_size_kb > 1024:
                gz_path = export_path + ".gz"
                with open(export_path, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(export_path)
                export_path = gz_path
                export_filename = export_filename + ".gz"
                file_size_kb = os.path.getsize(export_path) / 1024
            
            # Format date for display
            display_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
            
            text = f"""✅ *Date-Specific Logs Exported*
━━━━━━━━━━━━━━━━━━━━━━━━

📅 *Date:* {display_date}
⏰ *Time Range:*
   From: {first_ts}
   To: {last_ts}

📄 *File:* `{export_filename}`
📊 *Lines Exported:* {len(filtered_lines)}
💾 *File Size:* {file_size_kb:.2f} KB
📁 *Location:* `{export_path}`

💡 File contains logs for {display_date} only!"""
            
            self.bot.send_message(text)
            
            # Try to send file via Telegram
            try:
                if hasattr(self.bot, 'send_document'):
                    self.bot.send_document(export_path, filename=export_filename, caption=f"Logs for {display_date}")
                    logger.info(f"Date-specific logs exported: {export_filename}")
                else:
                    logger.warning("send_document method not available in telegram_bot")
            except Exception as e:
                logger.warning(f"Could not send file via Telegram: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Export by date error: {e}")
            self.bot.send_message(f"❌ Error exporting logs by date: {str(e)}")
            return False
    
    def _execute_export_date_range(self, params: Dict[str, Any]):
        """Export logs between two dates"""
        try:
            import os
            import gzip
            from datetime import datetime
            
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            
            if not start_date or not end_date:
                self.bot.send_message("❌ Both start_date and end_date required!")
                return False
            
            # Validate date range
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start_dt > end_dt:
                self.bot.send_message("❌ Start date must be before or equal to end date!")
                return False
            
            log_file = "logs/bot.log"
            
            if not os.path.exists(log_file):
                self.bot.send_message("❌ Log file not found!")
                return False
            
            # Filter logs for date range
            filtered_lines, first_ts, last_ts = self._filter_logs_by_date(log_file, start_date, end_date)
            
            if not filtered_lines:
                display_start = start_dt.strftime("%d-%m-%Y")
                display_end = end_dt.strftime("%d-%m-%Y")
                self.bot.send_message(f"❌ No logs found for range: {display_start} to {display_end}")
                return False
            
            # Create export directory
            export_dir = "logs/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Create export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"logs_{start_date}_to_{end_date}_{timestamp}.txt"
            export_path = os.path.join(export_dir, export_filename)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            
            file_size_kb = os.path.getsize(export_path) / 1024
            
            # Compress if > 1MB
            if file_size_kb > 1024:
                gz_path = export_path + ".gz"
                with open(export_path, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(export_path)
                export_path = gz_path
                export_filename = export_filename + ".gz"
                file_size_kb = os.path.getsize(export_path) / 1024
            
            # Format dates for display
            display_start = start_dt.strftime("%d-%m-%Y")
            display_end = end_dt.strftime("%d-%m-%Y")
            
            # Calculate days in range
            days_diff = (end_dt - start_dt).days + 1
            
            text = f"""✅ *Date Range Logs Exported*
━━━━━━━━━━━━━━━━━━━━━━━━

📅 *Date Range:* {display_start} → {display_end}
📆 *Days Covered:* {days_diff} day(s)

⏰ *Time Range:*
   From: {first_ts}
   To: {last_ts}

📄 *File:* `{export_filename}`
📊 *Lines Exported:* {len(filtered_lines)}
💾 *File Size:* {file_size_kb:.2f} KB
📁 *Location:* `{export_path}`

💡 File contains logs for entire date range!"""
            
            self.bot.send_message(text)
            
            # Try to send file via Telegram
            try:
                if hasattr(self.bot, 'send_document'):
                    self.bot.send_document(export_path, filename=export_filename, caption=f"Logs: {display_start} to {display_end}")
                    logger.info(f"Date range logs exported: {export_filename}")
                else:
                    logger.warning("send_document method not available in telegram_bot")
            except Exception as e:
                logger.warning(f"Could not send file via Telegram: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Export date range error: {e}")
            self.bot.send_message(f"❌ Error exporting date range: {str(e)}")
            return False
    
    def _execute_log_file_size(self, params: Dict[str, Any]):
        """Show enhanced log file statistics with date breakdown"""
        try:
            import os
            from datetime import datetime
            
            log_file = "logs/bot.log"
            
            if not os.path.exists(log_file):
                self.bot.send_message("❌ Log file not found!")
                return False
            
            # Main log file stats
            size_bytes = os.path.getsize(log_file)
            size_mb = size_bytes / (1024 * 1024)
            modified_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            
            # Count total lines and get date range
            total_lines = 0
            today_lines = 0
            first_date = None
            last_date = None
            today = datetime.now().strftime("%Y-%m-%d")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    total_lines += 1
                    # Extract date from timestamp
                    if len(line) >= 10 and line[4] == '-' and line[7] == '-':
                        try:
                            date_str = line[:10]  # "2025-11-23"
                            if first_date is None:
                                first_date = date_str
                            last_date = date_str
                            
                            # Count today's lines
                            if date_str == today:
                                today_lines += 1
                        except:
                            continue
            
            # Check for backup files
            backup_files = []
            log_dir = os.path.dirname(log_file) or "logs"
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    if filename.startswith("bot.log") and filename != "bot.log":
                        backup_path = os.path.join(log_dir, filename)
                        backup_size = os.path.getsize(backup_path) / (1024 * 1024)
                        backup_files.append((filename, backup_size))
            
            total_size_mb = size_mb + sum(size for _, size in backup_files)
            
            # Format dates for display
            if first_date and last_date:
                try:
                    first_display = datetime.strptime(first_date, "%Y-%m-%d").strftime("%d-%m-%Y")
                    last_display = datetime.strptime(last_date, "%Y-%m-%d").strftime("%d-%m-%Y")
                    date_range = f"{first_display} → {last_display}"
                except:
                    date_range = f"{first_date} → {last_date}"
            else:
                date_range = "Unknown"
            
            text = f"""📊 *LOG FILE STATISTICS*
━━━━━━━━━━━━━━━━━━━━━━━━

📄 *Main Log File:*
• File: `bot.log`
• Size: {size_mb:.2f} MB ({size_bytes:,} bytes)
• Total Lines: {total_lines:,}
• Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}

📅 *Date Coverage:*
• Date Range: {date_range}
• Today's Lines: {today_lines:,}
• Historical Lines: {total_lines - today_lines:,}

💾 *Storage Info:*
• Max Size: 10 MB
• Usage: {(size_mb/10)*100:.1f}%
"""
            
            if backup_files:
                text += f"• Backup Files: {len(backup_files)}\n\n"
                text += "🔄 *Backup Files:*\n"
                for filename, backup_size in backup_files:
                    text += f"• {filename}: {backup_size:.2f} MB\n"
                text += f"\n📦 *Total Size (All):* {total_size_mb:.2f} MB\n\n"
            else:
                text += f"• Backup Files: 0\n\n"
                text += f"📦 *Total Size:* {total_size_mb:.2f} MB\n\n"
            
            # Rotation status
            if size_mb > 9:
                text += "⚠️ *Warning:* Log file near rotation limit!\n\n"
            else:
                text += "✅ *Status:* Healthy\n\n"
            
            text += "💡 *Export Options:*\n"
            text += "• `/export_logs` - Last N lines\n"
            text += "• `/export_current_session` - Today only\n"
            text += "• `/export_by_date` - Specific date\n"
            text += "• `/export_date_range` - Date range"
            
            self.bot.send_message(text)
            return True
            
        except Exception as e:
            logger.error(f"Log file size error: {e}")
            self.bot.send_message(f"❌ Error checking log size: {str(e)}")
            return False
    
    def _execute_clear_old_logs(self, params: Dict[str, Any]):
        """Clear old backup log files"""
        try:
            import os
            from datetime import datetime, timedelta
            
            # FIX: Remove admin check - owner can manage their own logs
            # User is the configured admin/owner (chat_id: 2139792302)
            
            log_dir = "logs"
            retention_days = 30
            keep_min_backups = 2
            
            # Find backup files
            backup_files = []
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    # FIX: Check for bot.log backups (bot.log.1, bot.log.2, etc.)
                    if filename.startswith("bot.log") and filename != "bot.log":
                        filepath = os.path.join(log_dir, filename)
                        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        age_days = (datetime.now() - modified_time).days
                        size_mb = os.path.getsize(filepath) / (1024 * 1024)
                        backup_files.append((filename, filepath, age_days, size_mb))
            
            # Sort by age (oldest first)
            backup_files.sort(key=lambda x: x[2], reverse=True)
            
            # Determine which to delete
            to_delete = []
            for filename, filepath, age_days, size_mb in backup_files:
                # Keep at least 2 recent backups
                if len(backup_files) - len(to_delete) <= keep_min_backups:
                    break
                # Delete if older than 30 days
                if age_days > retention_days:
                    to_delete.append((filename, filepath, age_days, size_mb))
            
            if not to_delete:
                text = f"""ℹ️ *No Old Logs to Clear*
━━━━━━━━━━━━━━━━━━━━━━━━

• Backup Files: {len(backup_files)}
• Retention Policy: {retention_days} days
• Minimum Backups: {keep_min_backups}

✅ All backups are within retention period"""
                self.bot.send_message(text)
                return True
            
            # Delete old files
            deleted_count = 0
            freed_mb = 0.0
            for filename, filepath, age_days, size_mb in to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    freed_mb += size_mb
                    logger.info(f"Deleted old log: {filename} (age: {age_days} days)")
                except Exception as e:
                    logger.error(f"Failed to delete {filename}: {e}")
            
            text = f"""✅ *Old Logs Cleared*
━━━━━━━━━━━━━━━━━━━━━━━━

🗑️ *Deleted Files:* {deleted_count}
💾 *Space Freed:* {freed_mb:.2f} MB
📦 *Remaining Backups:* {len(backup_files) - deleted_count}

📅 *Retention Policy:* {retention_days} days
🔒 *Safety:* Kept {keep_min_backups} recent backups

💡 Current logs are unaffected"""
            
            self.bot.send_message(text)
            return True
            
        except Exception as e:
            logger.error(f"Clear old logs error: {e}")
            self.bot.send_message(f"❌ Error clearing logs: {str(e)}")
            return False
    
    def _execute_trading_debug_mode(self, params: Dict[str, Any]):
        """Enable/disable trading debug mode"""
        try:
            from src.utils.logging_config import logging_config
            
            mode = params.get("mode", "status").lower()
            
            if mode == "status":
                # Show current status
                status = "✅ ON" if getattr(logging_config, 'trading_debug', False) else "❌ OFF"
                text = f"""📊 *TRADING DEBUG MODE STATUS*
━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *Current Status:* {status}

"""
                
                if getattr(logging_config, 'trading_debug', False):
                    text += """🔍 *When Enabled:*
• Full trend analysis logged
• Signal decisions with reasons
• Entry/exit logic details
• Price action analysis
• Risk calculations shown

💡 Use /trading_debug_mode off to disable"""
                else:
                    text += """ℹ️ *When Disabled:*
• Only final trading actions
• Minimal log output
• Better performance

💡 Use /trading_debug_mode on to enable"""
                
                self.bot.send_message(text)
                return True
            
            elif mode == "on":
                old_status = getattr(logging_config, 'trading_debug', False)
                logging_config.trading_debug = True
                
                # Save to config for persistence
                self._save_trading_debug_to_config(True)
                
                text = f"""✅ *Trading Debug Mode ENABLED*
━━━━━━━━━━━━━━━━━━━━━━━━

• Previous: {'ON' if old_status else 'OFF'}
• New: ON

🔍 *What Will Be Logged:*
• Full trend analysis
• Signal decisions with reasons
• Entry/exit logic details
• Price action analysis
• Risk calculations

⚠️ *Impact:*
• Larger log files
• More detailed debugging
• Slightly slower execution

💡 Survives bot restart!"""
                
                self.bot.send_message(text)
                logger.info("Trading debug mode enabled")
                return True
            
            elif mode == "off":
                old_status = getattr(logging_config, 'trading_debug', False)
                logging_config.trading_debug = False
                
                # Save to config for persistence
                self._save_trading_debug_to_config(False)
                
                text = f"""✅ *Trading Debug Mode DISABLED*
━━━━━━━━━━━━━━━━━━━━━━━━

• Previous: {'ON' if old_status else 'OFF'}
• New: OFF

ℹ️ *What Will Be Logged:*
• Only final trading actions
• Order placement/closure
• Critical events only

✅ *Benefits:*
• Smaller log files
• Better performance
• Clean production logs

💡 Survives bot restart!"""
                
                self.bot.send_message(text)
                logger.info("Trading debug mode disabled")
                return True
            
            else:
                self.bot.send_message(f"❌ Invalid mode: {mode}\\nUse: on, off, or status")
                return False
                
        except Exception as e:
            logger.error(f"Trading debug mode error: {e}")
            self.bot.send_message(f"❌ Error changing debug mode: {str(e)}")
            return False
    
    def _execute_system_resources(self, params: Dict[str, Any]):
        """Show system resource usage"""
        try:
            import psutil
            import os
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            mem_total_gb = memory.total / (1024 ** 3)
            mem_used_gb = memory.used / (1024 ** 3)
            mem_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage(os.getcwd())
            disk_total_gb = disk.total / (1024 ** 3)
            disk_used_gb = disk.used / (1024 ** 3)
            disk_percent = disk.percent
            
            # Process info
            process = psutil.Process(os.getpid())
            bot_mem_mb = process.memory_info().rss / (1024 ** 2)
            bot_cpu_percent = process.cpu_percent(interval=1)
            
            # Load average
            try:
                load_avg = os.getloadavg()
                load_str = f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
            except:
                load_str = "N/A (Windows)"
            
            # Status emojis
            cpu_emoji = "🟢" if cpu_percent < 70 else "🟡" if cpu_percent < 90 else "🔴"
            mem_emoji = "🟢" if mem_percent < 70 else "🟡" if mem_percent < 90 else "🔴"
            disk_emoji = "🟢" if disk_percent < 70 else "🟡" if disk_percent < 90 else "🔴"
            
            text = f"""💻 *SYSTEM RESOURCES*
━━━━━━━━━━━━━━━━━━━━━━━━

{cpu_emoji} *CPU Usage:*
• Overall: {cpu_percent}%
• Cores: {cpu_count}
• Load Average: {load_str}

{mem_emoji} *Memory (RAM):*
• Used: {mem_used_gb:.2f} GB / {mem_total_gb:.2f} GB
• Usage: {mem_percent}%
• Available: {memory.available / (1024**3):.2f} GB

{disk_emoji} *Disk Space:*
• Used: {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB
• Usage: {disk_percent}%
• Free: {disk.free / (1024**3):.1f} GB

🤖 *Bot Process:*
• Memory: {bot_mem_mb:.1f} MB
• CPU: {bot_cpu_percent}%
• PID: {os.getpid()}

"""
            
            # Health summary
            if cpu_percent > 90 or mem_percent > 90 or disk_percent > 90:
                text += "⚠️ *Warning:* High resource usage detected!"
            elif cpu_percent > 70 or mem_percent > 70 or disk_percent > 70:
                text += "💡 *Status:* Moderate resource usage"
            else:
                text += "✅ *Status:* Healthy"
            
            self.bot.send_message(text)
            return True
            
        except ImportError:
            self.bot.send_message("❌ psutil not installed!\nRun: pip install psutil")
            return False
        except Exception as e:
            logger.error(f"System resources error: {e}")
            self.bot.send_message(f"❌ Error checking resources: {str(e)}")
            return False
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        try:
            # Check if user_id matches configured admin
            if hasattr(self.bot, 'chat_id') and user_id == self.bot.chat_id:
                return True
            # Additional admin check from config
            if hasattr(self.bot, 'config'):
                admin_id = self.bot.config.get('telegram_chat_id', 0)
                return user_id == admin_id
            return False
        except:
            return False
    
    def _save_trading_debug_to_config(self, enabled: bool):
        """Save trading debug mode to config"""
        try:
            import json
            import os
            
            config_file = "config/logging_settings.json"
            os.makedirs("config", exist_ok=True)
            
            # Load existing settings
            settings = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    settings = json.load(f)
            
            # Update trading_debug
            settings["trading_debug"] = enabled
            
            # Save
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"Trading debug mode saved to config: {enabled}")
        except Exception as e:
            logger.warning(f"Could not save trading debug to config: {e}")


    def _execute_dynamic_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Handle execution for dynamic commands"""
        if command == "stop_profit_chain":
            return self._execute_stop_profit_chain(params) is not None
        return False

