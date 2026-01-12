import requests
import json
import threading
import time
import sys
import logging
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING
from src.config import Config
from src.managers.risk_manager import RiskManager
from src.services.analytics_engine import AnalyticsEngine
from src.managers.timeframe_trend_manager import TimeframeTrendManager
from src.clients.menu_callback_handler import MenuCallbackHandler
from src.menu.fine_tune_menu_handler import FineTuneMenuHandler
from src.menu.menu_constants import REPLY_MENU_MAP

if TYPE_CHECKING:
    from src.core.trading_engine import TradingEngine

class TelegramBot:
    def __init__(self, config: Config):
        self.config = config
        self.token = config["telegram_token"]
        self.chat_id = config["telegram_chat_id"]
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.logger = logging.getLogger(__name__)
        
        # Connection pooling for faster API requests
        self.session = requests.Session()
        
        self.trend_manager = None
        self.polling_stop_event = threading.Event()
        self.polling_thread = None
        self.http409_count = 0  # Track consecutive 409 errors
        self.polling_enabled = True  # ENABLED - polling now works with proper webhook cleanup and DEBUG logging
        
        self.command_handlers = {
            "/start": self.handle_start,
            "/status": self.handle_status,
            "/pause": self.handle_pause,
            "/resume": self.handle_resume,
            "/performance": self.handle_performance,
            "/stats": self.handle_stats,
            "/trades": self.handle_trades,
            "/logic1_on": self.handle_logic1_on,
            "/logic1_off": self.handle_logic1_off,
            "/logic2_on": self.handle_logic2_on,
            "/logic2_off": self.handle_logic2_off,
            "/logic3_on": self.handle_logic3_on,
            "/logic3_off": self.handle_logic3_off,
            "/logic_control": self.handle_logic_control,
            "/logic_status": self.handle_logic_status,
            "/performance_report": self.handle_performance,
            "/pair_report": self.handle_pair_report,
            "/strategy_report": self.handle_strategy_report,
            # Trend commands
            "/set_trend": self.handle_set_trend,
            "/set_auto": self.handle_set_auto,
            "/show_trends": self.handle_show_trends,
            "/trend_matrix": self.handle_trend_matrix,
            "/trend_mode": self.handle_trend_mode,
            "/lot_size_status": self.handle_lot_size_status,
            "/set_lot_size": self.handle_set_lot_size,
            "/chains": self.handle_chains_status,
            "/signal_status": self.handle_status,
            "/clear_loss_data": self.handle_clear_loss_data,
            "/clear_daily_loss": self.handle_clear_daily_loss,
            "/tp_system": self.handle_tp_system,
            "/sl_hunt": self.handle_sl_hunt,
            "/exit_continuation": self.handle_exit_continuation,
            "/tp_report": self.handle_tp_report,
            # New configuration commands
            "/simulation_mode": self.handle_simulation_mode,
            "/reentry_config": self.handle_reentry_config,
            "/set_monitor_interval": self.handle_set_monitor_interval,
            "/set_sl_offset": self.handle_set_sl_offset,
            "/set_cooldown": self.handle_set_cooldown,
            "/set_recovery_time": self.handle_set_recovery_time,
            "/set_max_levels": self.handle_set_max_levels,
            "/set_sl_reduction": self.handle_set_sl_reduction,
            "/reset_reentry_config": self.handle_reset_reentry_config,
            "/view_sl_config": self.handle_view_sl_config,
            "/set_symbol_sl": self.handle_set_symbol_sl,
            "/view_risk_caps": self.handle_view_risk_caps,
            "/sl_status": self.handle_sl_status,
            "/sl_system_change": self.handle_sl_system_change,
            "/sl_system_on": self.handle_sl_system_on,
            "/profit_stats": self.handle_profit_stats,
            "/toggle_profit_booking": self.handle_toggle_profit_booking,
            "/set_profit_targets": self.handle_set_profit_targets,
            "/profit_chains": self.handle_profit_chains,
            "/stop_profit_chain": self.handle_stop_profit_chain,
            "/stop_all_profit_chains": self.handle_stop_all_profit_chains,
            "/set_chain_multipliers": self.handle_set_chain_multipliers,
            "/set_sl_reductions": self.handle_set_sl_reductions,
            "/close_profit_chain": self.handle_stop_profit_chain,  # Alias for stop_profit_chain
            "/profit_config": self.handle_profit_config,
            # Profit Booking SL commands
            "/profit_sl_status": self.handle_profit_sl_status,
            "/profit_sl_mode": self.handle_profit_sl_mode,
            "/enable_profit_sl": self.handle_enable_profit_sl,
            "/disable_profit_sl": self.handle_disable_profit_sl,
            "/set_sl1_1": self.handle_set_sl1_1,
            "/set_sl2_1": self.handle_set_sl2_1,
            # Reverse Shield v3.0
            "/shield": self.handle_shield_command,
            "/set_profit_sl": self.handle_set_profit_sl,
            "/reset_profit_sl": self.handle_reset_profit_sl,
            # Dashboard command
            "/dashboard": self.handle_dashboard,
            
            # Fine-Tune System Commands
            "/fine_tune": self.handle_fine_tune,
            "/autonomous_dashboard": self.handle_autonomous_dashboard,
            "/profit_protection": self.handle_profit_protection,
            "/sl_reduction": self.handle_sl_reduction,
            "/recovery_windows": self.handle_recovery_windows,
            "/recovery_windows": self.handle_recovery_windows,
            "/autonomous_status": self.handle_autonomous_status,
            "/view_logic_settings": self.handle_view_logic_settings,
            "/reset_timeframe_default": self.handle_reset_timeframe_default,
        }
        






        
        self.risk_manager = None
        self.trading_engine = None
        self.analytics_engine = AnalyticsEngine()
        
        # Initialize menu system
        from src.menu import MenuManager
        self.menu_manager = MenuManager(self)
        
        # Initialize menu callback handler
        self.menu_callback_handler = MenuCallbackHandler(self)
        
        # CRITICAL: Clean up any existing webhooks on initialization
        print("[INIT] Cleaning up webhooks on bot initialization...")
        self._cleanup_webhook_before_polling()
        print("[INIT] Webhook cleanup complete")

    def set_dependencies(self, risk_manager: RiskManager, trading_engine: 'TradingEngine'):
        """Set dependent modules"""
        self.risk_manager = risk_manager
        self.trading_engine = trading_engine
        # Store references for dashboard
        if trading_engine:
            self.mt5_client = trading_engine.mt5_client
            self.pip_calculator = trading_engine.pip_calculator
            self.dual_order_manager = trading_engine.dual_order_manager
            self.profit_booking_manager = trading_engine.profit_booking_manager
            self.reentry_manager = trading_engine.reentry_manager
            self.db = trading_engine.db

            # Initialize Fine-Tune Menu Handler
            if hasattr(trading_engine, "autonomous_manager") and trading_engine.autonomous_manager:
                am = trading_engine.autonomous_manager
                if hasattr(am, "profit_protection") and hasattr(am, "sl_optimizer"):
                    self.fine_tune_handler = FineTuneMenuHandler(self, am.profit_protection, am.sl_optimizer)
                    print("✅ TelegramBot: Fine-Tune Menu Handler initialized")
                else:
                    print("⚠️ TelegramBot: Autonomous Manager missing sub-managers")
                    self.fine_tune_handler = None
                
                # Initialize Re-entry Menu Handler
                try:
                    from src.menu.reentry_menu_handler import ReentryMenuHandler
                    self.reentry_menu_handler = ReentryMenuHandler(self, am)
                    print("✅ TelegramBot: Re-entry Menu Handler initialized")
                except ImportError as e:
                    print(f"⚠️ TelegramBot: Could not import ReentryMenuHandler: {e}")
                    self.reentry_menu_handler = None
                
            else:
                print("⚠️ TelegramBot: Trading Engine missing autonomous_manager")
                self.fine_tune_handler = None
                self.reentry_menu_handler = None
            
            # Initialize Profit Booking Menu Handler
            try:
                from src.menu.profit_booking_menu_handler import ProfitBookingMenuHandler
                self.profit_booking_menu_handler = ProfitBookingMenuHandler(self)
                print("✅ TelegramBot: Profit Booking Menu Handler initialized")
            except ImportError as e:
                print(f"⚠️ TelegramBot: Could not import ProfitBookingMenuHandler: {e}")
                self.profit_booking_menu_handler = None

    
    def _ensure_dependencies(self):
        """Ensure dependencies are available - try to get from trading_engine if not set"""
        # If trading_engine is not set, try to get from global references
        if not self.trading_engine:
            # Try to get from global references set in main.py
            if hasattr(self, '_global_trading_engine') and self._global_trading_engine:
                self.trading_engine = self._global_trading_engine
                print("DEBUG: Retrieved trading_engine from global reference")
            if hasattr(self, '_global_risk_manager') and self._global_risk_manager:
                self.risk_manager = self._global_risk_manager
                print("DEBUG: Retrieved risk_manager from global reference")
            
            # Also try to get from main module
            if not self.trading_engine:
                try:
                    import sys
                    main_module = sys.modules.get('src.main')
                    if main_module and hasattr(main_module, 'trading_engine'):
                        self.trading_engine = main_module.trading_engine
                        print("DEBUG: Retrieved trading_engine from main module")
                    if main_module and hasattr(main_module, 'risk_manager'):
                        self.risk_manager = main_module.risk_manager
                        print("DEBUG: Retrieved risk_manager from main module")
                except Exception as e:
                    print(f"DEBUG: Could not retrieve from main: {e}")
        
        # If still no trading_engine, we can't get dependencies
        if not self.trading_engine:
            return False
        
        # If risk_manager not set, try to get from trading_engine
        if not self.risk_manager and hasattr(self.trading_engine, 'risk_manager'):
            self.risk_manager = self.trading_engine.risk_manager
        
        # Ensure all sub-managers are set from trading_engine
        if self.trading_engine:
            if hasattr(self.trading_engine, 'mt5_client') and self.trading_engine.mt5_client:
                if not hasattr(self, 'mt5_client') or not self.mt5_client:
                    self.mt5_client = self.trading_engine.mt5_client
            if hasattr(self.trading_engine, 'pip_calculator') and self.trading_engine.pip_calculator:
                if not hasattr(self, 'pip_calculator') or not self.pip_calculator:
                    self.pip_calculator = self.trading_engine.pip_calculator
            if hasattr(self.trading_engine, 'dual_order_manager') and self.trading_engine.dual_order_manager:
                if not hasattr(self, 'dual_order_manager') or not self.dual_order_manager:
                    self.dual_order_manager = self.trading_engine.dual_order_manager
            if hasattr(self.trading_engine, 'profit_booking_manager') and self.trading_engine.profit_booking_manager:
                if not hasattr(self, 'profit_booking_manager') or not self.profit_booking_manager:
                    self.profit_booking_manager = self.trading_engine.profit_booking_manager
            if hasattr(self.trading_engine, 'reentry_manager') and self.trading_engine.reentry_manager:
                if not hasattr(self, 'reentry_manager') or not self.reentry_manager:
                    self.reentry_manager = self.trading_engine.reentry_manager
            if hasattr(self.trading_engine, 'db') and self.trading_engine.db:
                if not hasattr(self, 'db') or not self.db:
                    self.db = self.trading_engine.db
        
        return True

    def _initialize_fine_tune_handler(self):
        """Helper to initialize fine tune handler (called by menu system)"""
        if self.trading_engine and hasattr(self.trading_engine, "autonomous_manager") and self.trading_engine.autonomous_manager:
            am = self.trading_engine.autonomous_manager
            if hasattr(am, "profit_protection") and hasattr(am, "sl_optimizer"):
                from src.menu.fine_tune_menu_handler import FineTuneMenuHandler
                self.fine_tune_handler = FineTuneMenuHandler(self, am.profit_protection, am.sl_optimizer)
                print("✅ TelegramBot: Fine-Tune Menu Handler initialized (Lazy Load)")

    def handle_autonomous_status(self, message):
        """Show full status of the autonomous system"""
        if self.reentry_menu_handler:
            self.reentry_menu_handler.show_reentry_status(message.get("from", {}).get("id"))
        else:
            self.send_message("❌ Re-entry handler not available")

    def handle_panic_close(self, message_or_callback):
        """
        Emergency handler to close all open positions.
        Requires confirmation to prevent accidental activation.
        """
        # Step 1: Show confirmation
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ YES - CLOSE ALL", "callback_data": "confirm_panic_close"},
                    {"text": "❌ CANCEL", "callback_data": "menu_main"}
                ]
            ]
        }
        
        warning = (
            "🚨 *PANIC CLOSE CONFIRMATION* 🚨\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ This will close ALL open trades *IMMEDIATELY*:\n\n"
            "• All positions will be closed at market price\n"
            "• No recovery attempts will be made\n"
            "• This action cannot be undone\n\n"
            "*Are you absolutely sure?*"
        )
        
        # Check if called from callback or dictionary
        if isinstance(message_or_callback, dict):
            # It's a message dict or callback dict
            self.send_message_with_keyboard(warning, keyboard)
        else:
            # It might be a callback query object or message object
            self.send_message_with_keyboard(warning, keyboard)

    def handle_confirm_panic_close(self, callback_query):
        """Execute panic close after confirmation"""
        try:
            user_id = callback_query.get("from", {}).get("id")
            self.logger.warning(f"🚨 PANIC CLOSE INITIATED BY USER {user_id}")
            
            if not self.trading_engine:
                self.logger.error("❌ Panic close failed: Trading engine not available")
                self.send_message("❌ Trading engine not available")
                return
            
            # Get all open trades
            open_trades = self.db.get_open_trades()
            
            if not open_trades:
                self.send_message("ℹ️ No open trades to close")
                return
            
            # Close all positions
            closed_count = 0
            failed_count = 0
            
            self.send_message("⏳ Executing EMERGENCY CLOSE on all positions...")
            
            for trade in open_trades:
                try:
                    # Direct close via MT5 client
                    result = self.mt5_client.close_order(trade.ticket)
                    if result:
                        closed_count += 1
                        self.logger.info(f"🚨 Panic Close: Trade {trade.ticket} closed successfully")
                    else:
                        failed_count += 1
                        self.logger.error(f"🚨 Panic Close: Failed to close {trade.ticket}")
                except Exception as e:
                    self.logger.error(f"Failed to close {trade.ticket}: {e}")
                    failed_count += 1
            
            # Report results
            report = (
                f"🚨 *PANIC CLOSE EXECUTED*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Closed: {closed_count} trades\n"
                f"❌ Failed: {failed_count} trades\n\n"
                f"All emergency actions completed.\n"
                f"Bot is now in PAUSED state."
            )
            
            # Auto-pause the bot for safety
            self.trading_engine.is_paused = True
            
            self.send_message(report)
            
        except Exception as e:
            self.logger.error(f"Panic close critical error: {e}")
            self.send_message(f"❌ Panic close critical error: {str(e)}")

    def set_trend_manager(self, trend_manager: TimeframeTrendManager):
        """Set trend manager"""
        self.trend_manager = trend_manager
        self.logger.info("SUCCESS: Trend manager set in Telegram bot")
    


    def send_message(self, message: str, reply_markup: dict = None, add_menu_button: bool = True, parse_mode: str = "HTML"):
        """Send message to Telegram with optional menu button and custom keyboard
        
        Args:
            message: Message text
            reply_markup: Custom inline keyboard (if provided, overrides add_menu_button)
            add_menu_button: Add default menu button if no custom keyboard
            parse_mode: Formatting mode - "HTML", "Markdown", or None
        """
        if not self.token or not self.chat_id:
            print("WARNING: Telegram credentials not configured - message not sent")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            # Use custom keyboard if provided, otherwise add menu button if requested
            if reply_markup:
                payload["reply_markup"] = reply_markup
            elif add_menu_button:
                keyboard = [[{"text": "🏠 MAIN MENU", "callback_data": "menu_main"}]]
                payload["reply_markup"] = {"inline_keyboard": keyboard}
            
            response = requests.post(url, json=payload, timeout=2)
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {}).get("message_id") if result.get("ok") else True
            elif response.status_code == 400:
                print(f"WARNING: Parse mode '{parse_mode}' error, retrying without formatting...")
                payload.pop("parse_mode", None)
                retry_response = requests.post(url, json=payload, timeout=2)
                if retry_response.status_code == 200:
                    result = retry_response.json()
                    return result.get("result", {}).get("message_id") if result.get("ok") else True
                else:
                    print(f"WARNING: Telegram API error (Retry): Status {retry_response.status_code}, Response: {retry_response.text}")
                    return False
            else:
                print(f"WARNING: Telegram API error: Status {response.status_code}, Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Telegram API request failed: {str(e)}")
            return False
        except Exception as e:
            print(f"WARNING: Telegram send_message error: {str(e)}")
            return False
    
    def send_document(self, document, filename=None, caption=None):
        """Send a document to the user"""
        if not self.token or not self.chat_id:
            print("WARNING: Telegram credentials not configured - document not sent")
            return False
            
        try:
            url = f"{self.base_url}/sendDocument"
            # Handle file-like objects or file paths
            if hasattr(document, 'read'):
                files = {'document': (filename, document)} if filename else {'document': document}
            else:
                # Assume it's a file path - open and read it
                with open(document, 'rb') as f:
                    files = {'document': (filename or document, f)}
                    data = {'chat_id': self.chat_id}
                    if caption:
                        data['caption'] = caption
                    response = requests.post(url, data=data, files=files, timeout=30)
                    
                    if response.status_code == 200:
                        return True
                    else:
                        print(f"WARNING: Telegram API error sending document: {response.text}")
                        return False
                        
            # For file-like objects
            data = {'chat_id': self.chat_id}
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.status_code == 200:
                return True
            else:
                print(f"WARNING: Telegram API error sending document: {response.text}")
                return False
        except Exception as e:
            print(f"WARNING: Error sending document: {str(e)}")
            return False

    def send_message_with_keyboard(self, message: str, reply_markup: dict):
        """Send message with inline keyboard"""
        if not self.token or not self.chat_id:
            print("WARNING: Telegram credentials not configured - message not sent")
            return None
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "reply_markup": reply_markup,
                "parse_mode": "HTML"  # Use HTML to support <b> tags
            }
            response = requests.post(url, json=payload, timeout=2)
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    return result.get("result", {}).get("message_id")
            elif response.status_code == 400:
                # Retry without parse_mode if unsupported
                print("WARNING: Parse mode error, retrying without formatting...")
                payload.pop("parse_mode", None)
                response = requests.post(url, json=payload, timeout=2)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        return result.get("result", {}).get("message_id")
            else:
                print(f"WARNING: Telegram API error: Status {response.status_code}, Response: {response.text}")
            return None
        except Exception as e:
            print(f"WARNING: Telegram send_message_with_keyboard error: {str(e)}")
            return None
    
    def send_profit_recovery_notification(self, symbol, chain_id, level, current_price, sl_price, pnl=0.0):
        """Send notification for profit recovery trade (Fix #6)"""
        if not self.token or not self.chat_id:
            return
        
        emoji = "🔄"
        try:
             message = (
                f"{emoji} <b>PROFIT RECOVERY TRIGGERED</b>\n"
                f"Symbol: {symbol}\n"
                f"Chain ID: {chain_id[:8]}... (Level {level})\n"
                f"Current Price: {current_price}\n"
                f"Recovery SL: {sl_price}\n"
                f"Previous PnL: ${pnl:.2f}\n"
                f"Strategy: PROFIT_RECOVERY"
            )
             self.send_message(message)
        except Exception as e:
            print(f"Error sending profit recovery notification: {e}")

    def send_profit_hunt_notification(self, symbol, chain_id, level, pnl, distance_pips):
        """Send notification for profit hunting (Fix #6)"""
        if not self.token or not self.chat_id:
            return

        try:
             message = (
                f"🎯 <b>PROFIT HUNT STOP HIT</b>\n"
                f"Symbol: {symbol}\n"
                f"Chain ID: {chain_id[:8]}... (Level {level})\n"
                f"PnL Locked: ${pnl:.2f}\n"
                f"Distance: {distance_pips:.1f} pips\n"
                f"Status: Waiting for Recovery..."
            )
             self.send_message(message)
        except Exception as e:
            print(f"Error sending profit hunt notification: {e}")

    def send_autonomous_reentry_notification(self, trade_stub, level, current_price, sl_approx, tp_approx, trend_aligned):
        """Send notification for autonomous re-entry (Fix #6)"""
        if not self.token or not self.chat_id:
            return
            
        try:
             emoji = "🚀" if trend_aligned else "⚠️"
             message = (
                f"{emoji} <b>AUTONOMOUS RE-ENTRY</b>\n"
                f"Symbol: {trade_stub.symbol}\n"
                f"Direction: {trade_stub.direction.upper()}\n"
                f"Level: {level}\n"
                f"Entry: {current_price:.5f}\n"
                f"SL: ~{sl_approx:.5f}\n"
                f"TP: ~{tp_approx:.5f}\n"
                f"Trend Aligned: {'✅ YES' if trend_aligned else '❌ NO'}"
            )
             self.send_message(message)
        except Exception as e:
             print(f"Error sending autonomous notification: {e}")

    def edit_message(self, text: str, message_id: int, reply_markup: dict = None, parse_mode: str = "HTML"):
        """Edit existing message - defaults to HTML parse mode"""
        if not self.token or not self.chat_id:
            print("WARNING: Telegram credentials not configured - message not sent")
            return False
        
        if not message_id:
            # If no message_id, send new message instead
            if reply_markup:
                self.send_message_with_keyboard(text, reply_markup)
            else:
                self.send_message(text)
            return False
        
        try:
            url = f"{self.base_url}/editMessageText"
            payload = {
                "chat_id": self.chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": parse_mode
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup
            
            response = requests.post(url, json=payload, timeout=2)
            if response.status_code == 200:
                return True
            elif response.status_code == 400:
                error_text = response.json().get("description", "")
                # If message not found, send new message instead of failing
                if "message to edit not found" in error_text.lower() or "message is not modified" in error_text.lower():
                    print(f"INFO: Message {message_id} not found or not modified, sending new message instead")
                    if reply_markup:
                        self.send_message_with_keyboard(text, reply_markup)
                    else:
                        self.send_message(text)
                    return False
                # REMOVED RETRY - was causing extra 10s delay
                # Just fall back to new message immediately
                print(f"WARNING: Edit failed, sending new message")
                if reply_markup:
                    self.send_message_with_keyboard(text, reply_markup)
                else:
                    self.send_message(text)
                return False
            else:
                print(f"WARNING: Telegram API error: Status {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print(f"WARNING: Telegram edit_message error: {str(e)}")
            return False

    def handle_start(self, message):
        # LOCAL IMPORTS to prevent NameErrors
        import json
        import requests
        import traceback
        
        # Safe ID extraction
        try:
            user_id = message["from"]["id"]
        except:
            user_id = self.chat_id

        try:
            # 1. VISUAL PROOF OF UPDATE
            # Manually send to user_id to ensure delivery
            diag_url = f"{self.base_url}/sendMessage"
            diag_payload = {
                "chat_id": user_id,
                "text": "🔍 **DIAGNOSTIC: Code v3.0 Loaded**\nAttempting to inject keyboard...",
                "parse_mode": "Markdown"
            }
            requests.post(diag_url, data=diag_payload, timeout=5)

            # 2. DEFINE KEYBOARD (Compact 3-Column)
            keyboard_payload = {
                "keyboard": [
                    [{"text": "📊 Dashboard"}, {"text": "⏸️ Pause/Resume"}, {"text": "📈 Active Trades"}],
                    [{"text": "🛡️ Risk"}, {"text": "🔄 Re-entry"}, {"text": "⚙️ SL System"}],
                    [{"text": "📍 Trends"}, {"text": "📈 Profit"}, {"text": "🆘 Help"}],
                    [{"text": "🚨 PANIC CLOSE"}]
                ],
                "resize_keyboard": True,
                "is_persistent": True,
                "video_chat_allowed": False, # Explicitly disable
                "input_field_placeholder": "v3.0 Control Panel"
            }

            # 3. FORCE SEND
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": "👇 **Control Panel Updated (v3.0)**",
                "parse_mode": "Markdown",
                "reply_markup": json.dumps(keyboard_payload)
            }
            
            # 4. EXECUTE REQUEST
            response = requests.post(url, data=payload, timeout=5)
            
            # 5. REPORT STATUS
            if response.status_code != 200:
                print(f"❌ API Error: {response.text}")
                # Try sending error to user
                requests.post(diag_url, data={"chat_id": user_id, "text": f"❌ API Error: {response.text}"})
            else:
                print(f"[SUCCESS] Menu v3.0 sent to {user_id}")

        except Exception as e:
            # 6. CRASH REPORT TO USER
            error_msg = f"❌ CRASH IN HANDLE_START:\n{str(e)}"
            print(error_msg)
            try:
                requests.post(f"{self.base_url}/sendMessage", data={"chat_id": user_id, "text": error_msg})
            except:
                pass
            
            # If menu failed to send, try fallback with buttons
            if result is None:
                print("WARNING: Menu system returned None, trying fallback with buttons")
                self._send_start_fallback_with_buttons(user_id)
                
        except Exception as e:
            # Fallback to menu with buttons if menu system fails
            print(f"Menu system error: {e}")
            import traceback
            traceback.print_exc()
            try:
                user_id = message.get("from", {}).get("id") if isinstance(message, dict) else self.chat_id
                self._send_start_fallback_with_buttons(user_id)
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
                # Last resort: send text message
                rr_ratio = self.config.get("rr_ratio", 1.0)
                welcome_msg = (
                    "🤖 <b>Zepix Trading Bot v2.0</b>\n"
                    "✅ Bot is active with enhanced features\n"
                    f"📊 1:{rr_ratio} Risk-Reward System Active\n\n"
                    "<b>📋 TOTAL COMMANDS: 72</b>\n\n"
                    "Use /dashboard for interactive controls.\n"
                    "Type /help to see all commands.\n\n"
                    "<b>🆕 NEW: Zero-Typing Menu System</b>\n"
                    "Use buttons above to navigate - no typing required!"
                )
                self.send_message(welcome_msg, add_menu_button=True)
    
    def _send_start_fallback_with_buttons(self, user_id: int):
        """Send fallback start message with menu buttons"""
        rr_ratio = self.config.get("rr_ratio", 1.0)
        welcome_msg = (
            "🤖 <b>ZEPIX TRADING BOT v2.0</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ Bot is active with enhanced features\n"
            f"📊 1:{rr_ratio} Risk-Reward System Active\n\n"
            "<b>📋 TOTAL COMMANDS: 72</b>\n\n"
            "🆕 <b>Zero-Typing Menu System</b>\n"
            "Use buttons below to navigate - no typing required!"
        )
        
        # Create menu buttons
        keyboard = []
        keyboard.append([{"text": "📊 Dashboard", "callback_data": "action_dashboard"}])
        keyboard.append([{"text": "💰 Trading", "callback_data": "menu_trading"}])
        keyboard.append([{"text": "⚡ Performance", "callback_data": "menu_performance"}])
        keyboard.append([{"text": "🔄 Re-entry", "callback_data": "menu_reentry"}])
        keyboard.append([{"text": "📍 Trends", "callback_data": "menu_trends"}])
        keyboard.append([{"text": "🛡️ Risk", "callback_data": "menu_risk"}])
        keyboard.append([{"text": "⚙️ SL System", "callback_data": "menu_sl_system"}])
        keyboard.append([{"text": "💎 Orders", "callback_data": "menu_orders"}])
        keyboard.append([{"text": "📈 Profit", "callback_data": "menu_profit"}])
        
        reply_markup = {"inline_keyboard": keyboard}
        self.send_message_with_keyboard(welcome_msg, reply_markup)

    def handle_status(self, message):
        """Handle /status command with enhanced display"""
        # Try to get dependencies if not available
        if not self.trading_engine:
            if hasattr(self, 'trading_engine') and self.trading_engine:
                pass  # Already set
            else:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
        
        if not self.risk_manager:
            if self.trading_engine and hasattr(self.trading_engine, 'risk_manager'):
                self.risk_manager = self.trading_engine.risk_manager
            else:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
        
        stats = self.risk_manager.get_stats()
        
        # Get current trends for major symbol
        xau_trends = self.trend_manager.get_all_trends("XAUUSD") if self.trend_manager else {}
        
        # Check logic alignments
        logic_alignments = {}
        if self.trend_manager:
            for logic in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
                alignment = self.trend_manager.check_logic_alignment("XAUUSD", logic)
                logic_alignments[logic] = alignment["direction"]
        
        status_msg = (
            "📊 <b>Bot Status</b>\n\n"
            f"🔸 Trading: {'⏸️ PAUSED' if self.trading_engine.is_paused else '✅ ACTIVE'}\n"
            f"🔸 Simulation: {'✅ ON' if self.config['simulate_orders'] else '❌ OFF'}\n"
            f"🔸 MT5: {'✅ Connected' if self.trading_engine.mt5_client.initialized else '❌ Disconnected'}\n"
            f"🔸 Balance: ${stats.get('account_balance', 0):.2f}\n"
            f"🔸 Lot Size: {stats.get('current_lot_size', 0.05)}\n\n"
            "<b>Current Modes (XAUUSD):</b>\n"
            f"combinedlogic-1: {logic_alignments.get('combinedlogic-1', 'NEUTRAL')}\n"
            f"combinedlogic-2: {logic_alignments.get('combinedlogic-2', 'NEUTRAL')}\n"
            f"combinedlogic-3: {logic_alignments.get('combinedlogic-3', 'NEUTRAL')}\n\n"
            "<b>Live Signals (XAUUSD):</b>\n"
            f"15min: {xau_trends.get('15m', 'NA')}\n"
            f"1H: {xau_trends.get('1h', 'NA')}\n"
            f"1D: {xau_trends.get('1d', 'NA')}"
        )
        self.send_message(status_msg)

    # NEW COMMAND: Set Auto Mode
    def handle_set_auto(self, message):
        """Set trend back to AUTO mode"""
        if not self.trend_manager:
            self.send_message("❌ Trend manager not initialized")
            return
            
        try:
            parts = message['text'].split()
            
            if len(parts) < 3:
                self.send_message(
                    "📝 <b>Usage:</b> /set_auto SYMBOL TIMEFRAME\n\n"
                    "<b>Symbols:</b> XAUUSD, EURUSD, GBPUSD, etc.\n"
                    "<b>Timeframes:</b> 5m, 15m, 1h, 1d\n\n"
                    "<b>Example:</b> /set_auto XAUUSD 1h\n"
                    "This allows TradingView signals to auto-update this trend"
                )
                return
            
            symbol = parts[1].upper()
            timeframe = parts[2].lower()
            
            valid_timeframes = ['15m', '1h', '1d']  # Removed 5m - not used by any logic
            if timeframe not in valid_timeframes:
                self.send_message(f"❌ Invalid timeframe. Use: {', '.join(valid_timeframes)}")
                return
            
            self.trend_manager.set_auto_trend(symbol, timeframe)
            current_trend = self.trend_manager.get_trend(symbol, timeframe)
            current_mode = self.trend_manager.get_mode(symbol, timeframe)
            
            self.send_message(f"🔄 <b>Auto Mode Enabled</b>\n"
                            f"{symbol} {timeframe} → {current_trend} ({current_mode})\n"
                            f"📡 Now accepting TradingView signals")
            
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    # NEW COMMAND: Check Trend Mode
    def handle_trend_mode(self, message):
        """Check current trend mode"""
        if not self.trend_manager:
            self.send_message("❌ Trend manager not initialized")
            return
            
        try:
            parts = message['text'].split()
            
            if len(parts) < 3:
                self.send_message(
                    "📝 <b>Usage:</b> /trend_mode SYMBOL TIMEFRAME\n\n"
                    "<b>Example:</b> /trend_mode XAUUSD 1h"
                )
                return
            
            symbol = parts[1].upper()
            timeframe = parts[2].lower()
            
            current_trend = self.trend_manager.get_trend(symbol, timeframe)
            current_mode = self.trend_manager.get_mode(symbol, timeframe)
            
            mode_info = "🔄 AUTO (TradingView updates)" if current_mode == "AUTO" else "🔒 MANUAL (Locked)"
            
            self.send_message(f"📊 <b>Trend Mode</b>\n"
                            f"Symbol: {symbol}\n"
                            f"Timeframe: {timeframe}\n"
                            f"Trend: {current_trend}\n"
                            f"Mode: {mode_info}")
            
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_trend(self, message):
        """Handle /set_trend command - SETS MANUAL MODE"""
        if not self.trend_manager:
            self.send_message("❌ Trend manager not initialized")
            return
            
        try:
            parts = message['text'].split()
            
            if len(parts) < 4:
                self.send_message(
                    "📝 <b>Usage:</b> /set_trend SYMBOL TIMEFRAME TREND\n\n"
                    "<b>Symbols:</b> XAUUSD, EURUSD, GBPUSD, etc.\n"
                    "<b>Timeframes:</b> 15m, 1h, 1d\n"
                    "<b>Trends:</b> BULLISH, BEARISH, NEUTRAL\n\n"
                    "⚠️ <b>This sets MANUAL mode</b> - TradingView signals won't auto-update\n"
                    "Use /set_auto to allow auto updates\n\n"
                    "<b>Example:</b> /set_trend XAUUSD 1h BULLISH"
                )
                return
            
            symbol = parts[1].upper()
            timeframe = parts[2].lower()
            trend = parts[3].upper()
            
            valid_timeframes = ['15m', '1h', '1d']  # Removed 5m
            if timeframe not in valid_timeframes:
                self.send_message(f"❌ Invalid timeframe. Use: {', '.join(valid_timeframes)}")
                return
            
            if trend not in ["BULLISH", "BEARISH", "NEUTRAL"]:
                self.send_message("❌ Trend must be BULLISH, BEARISH, or NEUTRAL")
                return
            
            self.trend_manager.set_manual_trend(symbol, timeframe, trend)
            
            # Verify the trend was set
            current_trend = self.trend_manager.get_trend(symbol, timeframe)
            current_mode = self.trend_manager.get_mode(symbol, timeframe)
            
            self.send_message(f"🔒 <b>Manual Trend Set</b>\n"
                            f"{symbol} {timeframe} → {current_trend} ({current_mode})\n"
                            f"⚠️ TradingView signals won't auto-update this\n"
                            f"Use /set_auto {symbol} {timeframe} to allow auto updates")
            
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_show_trends(self, message):
        """Handle /show_trends command"""
        if not self.trend_manager:
            self.send_message("❌ Trend manager not initialized")
            return
        
        symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD"]
        
        msg = "📊 <b>Current Trends</b>\n\n"
        for symbol in symbols:
            trends = self.trend_manager.get_all_trends_with_mode(symbol)
            has_non_neutral = any(trend_data["trend"] != "NEUTRAL" for trend_data in trends.values())
            
            if has_non_neutral:
                msg += f"<b>{symbol}:</b>\n"
                for tf in ["15m", "1h", "1d"]:  # Removed 5m - not used by any logic
                    if tf in trends:
                        trend_data = trends[tf]
                        if trend_data["trend"] != "NEUTRAL":
                            mode_icon = "🔒" if trend_data["mode"] == "MANUAL" else "🔄"
                            msg += f"  {tf}: {trend_data['trend']} {mode_icon}\n"
                msg += "─────────────\n"
        
        self.send_message(msg)

    def handle_trend_matrix(self, message):
        """Show complete trend matrix for all symbols"""
        if not self.trend_manager:
            self.send_message("❌ Trend manager not initialized")
            return
        
        # FIX #1: Force reload trends from file for real-time data
        self.trend_manager.load_trends()
        
        # FIX #2: Load ALL active symbols from config instead of hardcoded list
        from src.menu.menu_constants import SYMBOLS
        symbols = SYMBOLS  # This pulls all 10 symbols: XAUUSD, EURUSD, GBPUSD, USDJPY, USDCAD, AUDUSD, NZDUSD, EURJPY, GBPJPY, AUDJPY
        
        # Build complete matrix
        msg = "🎯 <b>Complete Trend Matrix</b>\n\n"
        
        for symbol in symbols:
            msg += f"<b>{symbol}</b>\n"
            trends = self.trend_manager.get_all_trends_with_mode(symbol)
            
            # Show individual timeframes with mode (only those used by logic)
            for tf in ["15m", "1h", "1d"]:  # Removed 5m - not used by any logic
                trend_data = trends.get(tf, {"trend": "NEUTRAL", "mode": "AUTO"})
                trend = trend_data["trend"]
                mode = trend_data["mode"]
                
                emoji = "🟢" if trend == "BULLISH" else "🔴" if trend == "BEARISH" else "⚪"
                mode_icon = "🔒" if mode == "MANUAL" else "🔄"
                
                msg += f"  {tf}: {emoji} {trend} {mode_icon}\n"
            
            # Show logic alignments
            for logic in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
                alignment = self.trend_manager.check_logic_alignment(symbol, logic)
                if alignment["aligned"]:
                    msg += f"  ✅ {logic}: {alignment['direction']}\n"
            
            msg += "─────────────\n"
        
        msg += "\n<b>Legend:</b> 🟢BULLISH 🔴BEARISH ⚪NEUTRAL 🔒MANUAL 🔄AUTO"
        
        # FIX #3: Handle Telegram's 4096 character limit
        # If message is too long, split into multiple messages
        if len(msg) > 4000:  # Leave buffer for safety
            # Split by finding midpoint symbol
            lines = msg.split('\n')
            mid_point = len(symbols) // 2
            
            # Build first message (Majors)
            msg1 = "🎯 <b>Trend Matrix - Part 1 (Majors)</b>\n\n"
            current_symbol_count = 0
            for line in lines[2:]:  # Skip header
                if '<b>' in line and '</b>' in line:  # Symbol header
                    current_symbol_count += 1
                if current_symbol_count <= mid_point:
                    msg1 += line + '\n'
                else:
                    break
            msg1 += "\n<b>Legend:</b> 🟢BULLISH 🔴BEARISH ⚪NEUTRAL 🔒MANUAL 🔄AUTO"
            
            # Build second message (Minors + Crosses)
            msg2 = "🎯 <b>Trend Matrix - Part 2 (Minors & Crosses)</b>\n\n"
            for line in lines[2:]:
                if '<b>' in line and '</b>' in line:
                    current_symbol_count += 1
                if current_symbol_count > mid_point:
                    msg2 += line + '\n'
            msg2 += "\n<b>Legend:</b> 🟢BULLISH 🔴BEARISH ⚪NEUTRAL 🔒MANUAL 🔄AUTO"
            
            # Send both messages
            self.send_message(msg1)
            self.send_message(msg2)
        else:
            # Single message is fine
            self.send_message(msg)

    # Trading Control Commands
    def handle_pause(self, message):
        """Handle /pause command"""
        self._ensure_dependencies()
        if not self.trading_engine:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        self.trading_engine.is_paused = True
        self.send_message("⏸️ <b>Trading PAUSED</b>\nNo new trades will be executed")

    def handle_resume(self, message):
        """Handle /resume command"""
        self._ensure_dependencies()
        if not self.trading_engine:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        self.trading_engine.is_paused = False
        self.send_message("✅ <b>Trading RESUMED</b>\nReady to execute new trades")

    def handle_performance(self, message):
        """Handle /performance command"""
        self._ensure_dependencies()
        if not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
            
        stats = self.risk_manager.get_stats()
        performance_msg = (
            "📈 <b>Trading Performance</b>\n\n"
            f"🔸 Total Trades: {stats['total_trades']}\n"
            f"🔸 Winning Trades: {stats['winning_trades']}\n"
            f"🔸 Win Rate: {stats['win_rate']:.1f}%\n\n"
            f"💰 Today's PnL: ${stats['daily_profit'] - stats['daily_loss']:.2f}\n"
            f"📊 Daily Profit: ${stats['daily_profit']:.2f}\n"
            f"📉 Daily Loss: ${stats['daily_loss']:.2f}\n"
            f"🔻 Lifetime Loss: ${stats['lifetime_loss']:.2f}"
        )
        self.send_message(performance_msg)
            
    def handle_sessions(self, message):
        """Handle /sessions command - List today's sessions"""
        self._ensure_dependencies()
        if not self.trading_engine or not hasattr(self.trading_engine, 'session_manager'):
            self.send_message("❌ Session manager not initialized yet.")
            return

        sessions = self.trading_engine.session_manager.get_today_sessions()
        
        if not sessions:
            self.send_message("📅 <b>TODAY'S SESSIONS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\nNo sessions recorded today.")
            return

        response = f"📅 <b>TODAY'S SESSIONS ({datetime.now().strftime('%d %b %Y')})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, session in enumerate(sessions, 1):
            s_id = session.get('session_id')
            symbol = session.get('symbol')
            direction = session.get('direction', '').upper()
            pnl = session.get('total_pnl', 0)
            trades = session.get('total_trades', 0)
            status = session.get('status')
            
            # Format time
            start_dt = datetime.fromisoformat(session.get('start_time'))
            start_str = start_dt.strftime('%H:%M')
            end_str = "Active"
            if session.get('end_time'):
                end_dt = datetime.fromisoformat(session.get('end_time'))
                end_str = end_dt.strftime('%H:%M')
            
            icon = "💰" if pnl > 0 else "❌"
            if status == 'ACTIVE':
                icon = "🟢"
            
            response += (
                f"{i}️⃣ <b>Session #{s_id.split('_')[-1]}</b> ({status})\n"
                f"   🕐 {start_str} - {end_str}\n"
                f"   📊 {symbol} {direction}\n"
                f"   {icon} <b>${pnl:.2f}</b> ({trades} trades)\n"
                f"   /session_report_{s_id}\n\n"
            )
            
        self.send_message(response)

    def handle_session_report(self, message):
        """Handle /session_report_<id> command"""
        text = message.get('text', '')
        parts = text.split('_')
        
        if len(parts) < 3:  # /session_report_SES_ID
            self.send_message("❌ Invalid session ID format.")
            return
            
        session_id = "_".join(parts[2:])  # Reconstruct ID part if it had underscores
        # Actually expected format: /session_report_SES_2025...
        # Let's support both /session_report <id> and /session_report_<id>
        
        if text.startswith('/session_report '):
            session_id = text.replace('/session_report ', '').strip()
        elif text.startswith('/session_report_'):
            session_id = text.replace('/session_report_', '').strip()
            
        self._ensure_dependencies()
        if not self.trading_engine or not hasattr(self.trading_engine, 'session_manager'):
            self.send_message("❌ Session manager not initialized.")
            return
            
        # Update stats first if active
        active_id = self.trading_engine.session_manager.get_active_session()
        if active_id == session_id:
            self.trading_engine.session_manager.update_session()
            
        report = self.trading_engine.session_manager.get_session_report(session_id)
        if not report:
            self.send_message(f"❌ Session not found: {session_id}")
            return
            
        # Construct Report
        symbol = report.get('symbol')
        direction = report.get('direction', '').upper()
        pnl = report.get('total_pnl', 0)
        trades_count = report.get('total_trades', 0)
        start_time = datetime.fromisoformat(report.get('start_time')).strftime('%H:%M')
        
        end_time = "Ongoing"
        duration = "..."
        if report.get('end_time'):
            end_dt = datetime.fromisoformat(report.get('end_time'))
            end_time = end_dt.strftime('%H:%M')
            duration_mins = int((end_dt - datetime.fromisoformat(report.get('start_time'))).total_seconds() / 60)
            duration = f"{duration_mins} min"
            
        breakdown = report.get('breakdown', {})
        wins = breakdown.get('wins', 0)
        losses = breakdown.get('losses', 0)
        win_rate = (wins / trades_count * 100) if trades_count > 0 else 0
        
        msg = (
            f"📊 <b>SESSION REPORT</b>\n"
            f"ID: <code>{session_id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 <b>{symbol} {direction}</b>\n"
            f"⏰ {start_time} - {end_time} ({duration})\n\n"
            f"🎯 <b>SUMMARY:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Profit: ${breakdown.get('total_profit', 0):.2f}\n"
            f"❌ Loss: ${breakdown.get('total_loss', 0):.2f}\n"
            f"📊 <b>Net P&L: ${pnl:.2f}</b>\n"
            f"🎯 Win Rate: {win_rate:.1f}% ({wins}W / {losses}L)\n\n"
            f"📋 <b>ACTIVITY:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔸 Dual Orders: {breakdown.get('dual_orders', 0)}\n"
            f"🔸 Profit Chains: {breakdown.get('profit_chains', 0)}\n"
            f"🔸 Re-entries: {breakdown.get('reentries', 0)}\n\n"
            f"✅ Entry: {report.get('entry_signal', 'Unknown')}\n"
            f"🏁 Exit: {report.get('exit_reason', 'Active')}\n"
        )
        
        self.send_message(msg)


    def handle_stats(self, message):
        """Handle /stats command - shows current active tier settings"""
        self._ensure_dependencies()
        if not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
            
        # Get active tier from config (not from old stats)
        active_tier = self.config.get("default_risk_tier", "10000")
        tier_config = self.config.get("risk_tiers", {}).get(active_tier, {})
        
        stats = self.risk_manager.get_stats()
        risk_msg = (
            "⚠️ <b>Risk Management</b>\n\n"
            f"🔸 Risk Tier: ${active_tier}\n"
            f"🔸 Daily Loss Limit: ${tier_config.get('daily_loss_limit', stats['risk_parameters']['daily_loss_limit'])}\n"
            f"🔸 Max Total Loss: ${tier_config.get('max_total_loss', stats['risk_parameters']['max_total_loss'])}\n\n"
            f"📊 Daily Loss: ${stats['daily_loss']:.2f}/{tier_config.get('daily_loss_limit', stats['risk_parameters']['daily_loss_limit'])}\n"
            f"🔻 Lifetime Loss: ${stats['lifetime_loss']:.2f}/{tier_config.get('max_total_loss', stats['risk_parameters']['max_total_loss'])}\n\n"
            f"📦 Current Lot Size: {tier_config.get('lot_size', stats['current_lot_size'])}"
        )
        self.send_message(risk_msg)

    def handle_trades(self, message):
        """Handle /trades command"""
        self._ensure_dependencies()
        if not self.trading_engine:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
            
        if not self.trading_engine.open_trades:
            self.send_message("📭 <b>No Open Trades</b>")
            return
        
        rr_ratio = self.config.get("rr_ratio", 1.0)
        trades_msg = "📊 <b>Open Trades</b>\n\n"
        for i, trade in enumerate(self.trading_engine.open_trades, 1):
            if trade.status != "closed":
                chain_info = f" [RE-{trade.chain_level}]" if trade.is_re_entry else ""
                trades_msg += (
                    f"<b>Trade #{i}{chain_info}</b>\n"
                    f"Symbol: {trade.symbol} | {trade.direction.upper()}\n"
                    f"Strategy: {trade.strategy}\n"
                    f"Entry: {trade.entry:.5f} | SL: {trade.sl:.5f}\n"
                    f"TP: {trade.tp:.5f} | RR: 1:{rr_ratio}\n"
                    f"Lot: {trade.lot_size:.2f}\n"
                    "────────────────────\n"
                )
        
        self.send_message(trades_msg)

    def handle_chains_status(self, message):
        """Show active re-entry chains"""
        self._ensure_dependencies()
        if not self.trading_engine:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        chains = self.trading_engine.reentry_manager.active_chains
        
        if not chains:
            self.send_message("🔗 <b>No Active Re-entry Chains</b>")
            return
        
        msg = "🔗 <b>Active Re-entry Chains</b>\n\n"
        for chain_id, chain in chains.items():
            msg += (
                f"<b>{chain.symbol} - {chain.direction.upper()}</b>\n"
                f"Level: {chain.current_level}/{chain.max_level}\n"
                f"Total Profit: ${chain.total_profit:.2f}\n"
                f"Status: {chain.status}\n"
                "────────────────────\n"
            )
        
        self.send_message(msg)

    def handle_pair_report(self, message):
        """Show detailed performance by symbol pair"""
        self._ensure_dependencies()
        if not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        stats = self.risk_manager.get_stats()
        pair_stats = stats.get('pair_performance', {})
        
        if not pair_stats:
            self.send_message("📊 <b>Symbol Performance Report</b>\n\n❌ No trading data available yet.")
            return
        
        msg = "📊 <b>Symbol Performance Report</b>\n\n"
        for symbol, data in pair_stats.items():
            win_rate = (data.get('wins', 0) / data.get('total', 1)) * 100 if data.get('total', 0) > 0 else 0
            msg += (
                f"<b>{symbol}</b>\n"
                f"📈 Trades: {data.get('total', 0)} | Win Rate: {win_rate:.1f}%\n"
                f"💰 PnL: ${data.get('profit', 0) - data.get('loss', 0):.2f}\n"
                "────────────────────\n"
            )
        
        self.send_message(msg)

    def handle_strategy_report(self, message):
        """Show performance breakdown by strategy logic"""
        self._ensure_dependencies()
        if not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        stats = self.risk_manager.get_stats()
        strategy_stats = stats.get('strategy_performance', {})
        
        if not strategy_stats:
            self.send_message("⚙️ <b>Strategy Performance Report</b>\n\n❌ No trading data available yet.")
            return
        
        msg = "⚙️ <b>Strategy Performance Report</b>\n\n"
        for strategy, data in strategy_stats.items():
            win_rate = (data.get('wins', 0) / data.get('total', 1)) * 100 if data.get('total', 0) > 0 else 0
            msg += (
                f"<b>{strategy.upper()}</b>\n"
                f"📈 Trades: {data.get('total', 0)} | Win Rate: {win_rate:.1f}%\n"
                f"💰 PnL: ${data.get('profit', 0) - data.get('loss', 0):.2f}\n"
                "────────────────────\n"
            )
        
        self.send_message(msg)

    # Logic control handlers
    def handle_combinedlogic1_on(self, message):
        if not self._ensure_dependencies() or not self.trading_engine:
            msg = "❌ Trading Engine not available"
            self.send_message(msg)
            return msg
        self.trading_engine.enable_logic(1)
        msg = "✅ combinedlogic-1 TRADING ENABLED"
        self.send_message(msg)
        return msg

    def handle_combinedlogic1_off(self, message):
        if not self._ensure_dependencies() or not self.trading_engine:
            msg = "❌ Trading Engine not available"
            self.send_message(msg)
            return msg
        self.trading_engine.disable_logic(1)
        msg = "⛔ combinedlogic-1 TRADING DISABLED"
        self.send_message(msg)
        return msg

    def handle_combinedlogic2_on(self, message):
        if not self._ensure_dependencies() or not self.trading_engine:
            msg = "❌ Trading Engine not available"
            self.send_message(msg)
            return msg
        self.trading_engine.enable_logic(2)
        msg = "✅ combinedlogic-2 TRADING ENABLED"
        self.send_message(msg)
        return msg

    def handle_combinedlogic2_off(self, message):
        if not self._ensure_dependencies() or not self.trading_engine:
            msg = "❌ Trading Engine not available"
            self.send_message(msg)
            return msg
        self.trading_engine.disable_logic(2)
        msg = "⛔ combinedlogic-2 TRADING DISABLED"
        self.send_message(msg)
        return msg

    def handle_combinedlogic3_on(self, message):
        if not self._ensure_dependencies() or not self.trading_engine:
            msg = "❌ Trading Engine not available"
            self.send_message(msg)
            return msg
        self.trading_engine.enable_logic(3)
        msg = "✅ combinedlogic-3 TRADING ENABLED"
        self.send_message(msg)
        return msg

    def handle_combinedlogic3_off(self, message):
        if not self._ensure_dependencies() or not self.trading_engine:
            msg = "❌ Trading Engine not available"
            self.send_message(msg)
            return msg
        self.trading_engine.disable_logic(3)
        msg = "⛔ combinedlogic-3 TRADING DISABLED"
        self.send_message(msg)
        return msg

    def handle_logic_control(self, message):
        """Show logic control submenu"""
        # Always send a new message instead of trying to edit
        user_id = message.get("from", {}).get("id")
        self._show_logic_control_menu(user_id, None)

    def _show_logic_control_menu(self, user_id, message_id):
        text = "⚙️ <b>Logic Control</b>\n\nSelect a logic strategy to toggle:"
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Enable combinedlogic-1", "callback_data": "cmd_strategy_combinedlogic1_on"},
                    {"text": "⛔ Disable combinedlogic-1", "callback_data": "cmd_strategy_combinedlogic1_off"}
                ],
                [
                    {"text": "✅ Enable combinedlogic-2", "callback_data": "cmd_strategy_combinedlogic2_on"},
                    {"text": "⛔ Disable combinedlogic-2", "callback_data": "cmd_strategy_combinedlogic2_off"}
                ],
                [
                    {"text": "✅ Enable combinedlogic-3", "callback_data": "cmd_strategy_combinedlogic3_on"},
                    {"text": "⛔ Disable combinedlogic-3", "callback_data": "cmd_strategy_combinedlogic3_off"}
                ],
                [{"text": "🔙 Back", "callback_data": "menu_trading"}]
            ]
        }
        # Always send new message to avoid "message to edit not found" error
        self.send_message_with_keyboard(text, keyboard)

    def handle_logic_status(self, message):
        if not self._ensure_dependencies() or not self.trading_engine:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
            
        status = self.trading_engine.get_logic_status()
        status_msg = (
            "🤖 <b>LOGIC STATUS:</b>\n\n"
            f"combinedlogic-1 (1H+15M→5M): {'✅ ENABLED' if status['combinedlogic-1'] else '❌ DISABLED'}\n"
            f"combinedlogic-2 (1H+15M→15M): {'✅ ENABLED' if status['combinedlogic-2'] else '❌ DISABLED'}\n"
            f"combinedlogic-3 (1D+1H→1H): {'✅ ENABLED' if status['combinedlogic-3'] else '❌ DISABLED'}\n\n"
            "Use /combinedlogic1_on, /combinedlogic1_off, etc. to control"
        )
        self.send_message(status_msg)

    def handle_lot_size_status(self, message):
        """Show current lot size settings"""
        if not self._ensure_dependencies() or not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        balance = self.risk_manager.mt5_client.get_account_balance()
        current_lot = self.risk_manager.get_fixed_lot_size(balance)
        tier = self.risk_manager.get_risk_tier(balance)
        
        msg = (
            "📦 <b>Lot Size Configuration</b>\n\n"
            f"Account Balance: ${balance:.2f}\n"
            f"Current Tier: ${tier}\n"
            f"Current Lot Size: {current_lot:.2f}\n\n"
            "<b>Tier Settings:</b>\n"
            "$5,000 → 0.05 lots\n"
            "$10,000 → 0.10 lots\n"
            "$25,000 → 1.00 lots\n"
            "$100,000 → 5.00 lots\n\n"
            "Use /set_lot_size TIER LOT to override"
        )
        self.send_message(msg)

    def handle_reset_risk_settings(self, message):
        """Reset all risk settings to defaults"""
        self._ensure_dependencies()
        try:
            # Reset to defaults
            default_tiers = {
                "5000": {"daily_loss_limit": 100.0, "max_total_loss": 500.0, "lot_size": 0.01},
                "10000": {"daily_loss_limit": 200.0, "max_total_loss": 1000.0, "lot_size": 0.05},
                "25000": {"daily_loss_limit": 500.0, "max_total_loss": 2500.0, "lot_size": 0.1},
                "50000": {"daily_loss_limit": 1000.0, "max_total_loss": 5000.0, "lot_size": 0.2},
                "100000": {"daily_loss_limit": 2000.0, "max_total_loss": 10000.0, "lot_size": 0.5}
            }
            
            self.config.update('risk_tiers', default_tiers)
            self.config.update('default_risk_tier', "5000")
            
            # Force reload in risk manager
            if self.risk_manager:
                self.risk_manager.load_config()
            
            self.send_message("✅ <b>Risk Settings Reset</b>\n\nAll risk tiers and limits have been reset to default values.")
            
        except Exception as e:
            self.send_message(f"❌ Error resetting risk settings: {str(e)}")
        """Handle manual lot size override"""
        if not self._ensure_dependencies() or not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        try:
            parts = message['text'].split()
            
            if len(parts) < 3:
                self.send_message(
                    "📝 <b>Usage:</b> /set_lot_size TIER LOT\n\n"
                    "<b>Example:</b> /set_lot_size 10000 0.15\n"
                    "This sets 0.15 lots for $10,000 tier"
                )
                return
            
            tier = int(parts[1])
            lot_size = float(parts[2])
            
            valid_tiers = [5000, 10000, 25000, 100000]
            if tier not in valid_tiers:
                self.send_message(f"❌ Invalid tier. Use: {', '.join(map(str, valid_tiers))}")
                return
            
            if lot_size <= 0 or lot_size > 10:
                self.send_message("❌ Lot size must be between 0.01 and 10.00")
                return
            
            self.risk_manager.set_manual_lot_size(tier, lot_size)
            
            # Send success message
            success_msg = (
                f"✅ <b>LOT SIZE UPDATED</b>\n\n"
                f"🎯 Tier: ${tier:,}\n"
                f"📊 Lot Size: {lot_size:.2f}\n\n"
                f"✅ Configuration saved successfully!"
            )
            self.send_message(success_msg)
            
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_switch_tier(self, message):
        """Switch active risk tier - applies preset daily/lifetime caps and lot size"""
        try:
            # Extract tier from message
            if isinstance(message, dict) and 'tier' in message:
                new_tier = message['tier']
            else:
                # Try to parse from text
                parts = message.get('text', '').split()
                if len(parts) >= 2:
                    new_tier = parts[1]
                else:
                    self.send_message("❌ Usage: /switch_tier TIER\nExample: /switch_tier 10000")
                    return
            
            # Validate tier exists
            if new_tier not in ["5000", "10000", "25000", "50000", "100000"]:
                self.send_message(f"❌ Invalid tier: {new_tier}\nValid tiers: 5000, 10000, 25000, 50000, 100000")
                return
            
            # Check account balance
            if self.mt5_client:
                balance = self.mt5_client.get_account_balance()
                tier_value = int(new_tier)
                
                warning_msg = ""
                if tier_value > balance:
                    warning_msg = f"⚠️ <b>Warning:</b> Tier ${new_tier} exceeds account balance ${balance:.2f}\n\n"
            else:
                warning_msg = ""
            
            # Get preset values for this tier
            risk_tiers = self.config.get('risk_tiers', {})
            fixed_lots = self.config.get('fixed_lot_sizes', {})
            
            tier_config = risk_tiers.get(new_tier, {})
            daily_cap = tier_config.get('daily_loss_limit', 0)
            lifetime_cap = tier_config.get('max_total_loss', 0)
            lot_size = fixed_lots.get(new_tier, 0)
            
            # Update active tier in config
            self.config.update('default_risk_tier', new_tier)
            
            # Send detailed success message
            success_msg = (
                f"{warning_msg}"
                f"✅ <b>ACTIVE TIER SWITCHED</b>\n\n"
                f"🎯 <b>New Active Tier: ${new_tier}</b>\n\n"
                f"<b>📋 Preset Settings Applied:</b>\n"
                f"├─ 📉 Daily Loss Cap: ${daily_cap:.2f}\n"
                f"├─ 🔴 Lifetime Loss Cap: ${lifetime_cap:.2f}\n"
                f"└─ 📊 Lot Size: {lot_size:.2f}\n\n"
                f"✅ All trades will now use ${new_tier} tier settings!"
            )
            self.send_message(success_msg)
            
            self.logger.info(f"[SWITCH TIER] User switched active tier to ${new_tier}")
            
        except Exception as e:
            self.logger.error(f"[SWITCH TIER ERROR] {str(e)}")
            self.send_message(f"❌ Error switching tier: {str(e)}")

    def handle_view_risk_status(self, message):
        """View comprehensive risk status"""
        try:
            risk_tiers = self.config.get('risk_tiers', {})
            fixed_lots = self.config.get('fixed_lot_sizes', {})
            current_tier = self.config.get('default_risk_tier', "5000")
            
            # Get current loss data
            daily_loss = 0.0
            lifetime_loss = 0.0
            if self.risk_manager:
                daily_loss = self.risk_manager.daily_loss
                lifetime_loss = self.risk_manager.lifetime_loss
            
            status_msg = (
                "📊 <b>COMPLETE RISK SETTINGS STATUS</b>\n\n"
                f"⭐️ <b>Current Active Tier: ${current_tier}</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "<b>📋 ALL TIER CONFIGURATIONS:</b>\n\n"
            )
            
            for balance in ["5000", "10000", "25000", "50000", "100000"]:
                tier_data = risk_tiers.get(balance, {})
                daily = tier_data.get('daily_loss_limit', 0)
                lifetime = tier_data.get('max_total_loss', 0)
                lot = fixed_lots.get(balance, 0)
                
                active_marker = "✅ " if str(balance) == str(current_tier) else ""
                status_msg += (
                    f"{active_marker}<b>${balance} Tier:</b>\n"
                    f"📉 Daily Cap: ${daily:.1f}\n"
                    f"🔴 Lifetime Cap: ${lifetime:.1f}\n"
                    f"📊 Lot Size: {lot}\n\n"
                )
            
            status_msg += (
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "<b>💰 CURRENT LOSS STATUS:</b>\n"
                f"📉 Daily Loss: ${daily_loss:.2f}\n"
                f"🔴 Lifetime Loss: ${lifetime_loss:.2f}"
            )
            
            self.send_message(status_msg)
            
        except Exception as e:
            self.logger.error(f"[RISK STATUS ERROR] {str(e)}")
            self.send_message(f"❌ Error viewing status: {str(e)}")

    def handle_reset_risk_settings(self, message):
        """Reset all risk settings to defaults"""
        try:
            # Reset to defaults
            default_tiers = {
                "5000": {"daily_loss_limit": 100.0, "max_total_loss": 500.0},
                "10000": {"daily_loss_limit": 200.0, "max_total_loss": 1000.0},
                "25000": {"daily_loss_limit": 500.0, "max_total_loss": 2500.0},
                "50000": {"daily_loss_limit": 1000.0, "max_total_loss": 5000.0},
                "100000": {"daily_loss_limit": 2000.0, "max_total_loss": 10000.0}
            }
            default_lots = {
                "5000": 0.01,
                "10000": 0.05,
                "25000": 0.1,
                "50000": 0.2,
                "100000": 0.5
            }
            
            self.config.update('risk_tiers', default_tiers)
            self.config.update('fixed_lot_sizes', default_lots)
            self.config.update('default_risk_tier', "5000")
            
            msg = (
                "🔄 <b>RISK SETTINGS RESET</b>\n\n"
                "✅ All risk settings restored to factory defaults:\n\n"
                "<b>$5000 Tier (Active):</b>\n"
                "• Daily Cap: $100\n"
                "• Lifetime Cap: $500\n"
                "• Lot Size: 0.01\n\n"
                "<b>$10000 Tier:</b>\n"
                "• Daily Cap: $200\n"
                "• Lifetime Cap: $1000\n"
                "• Lot Size: 0.05\n\n"
                "<b>$25000 Tier:</b>\n"
                "• Daily Cap: $500\n"
                "• Lifetime Cap: $2500\n"
                "• Lot Size: 0.1\n\n"
                "<b>$50000 Tier:</b>\n"
                "• Daily Cap: $1000\n"
                "• Lifetime Cap: $5000\n"
                "• Lot Size: 0.2\n\n"
                "<b>$100000 Tier:</b>\n"
                "• Daily Cap: $2000\n"
                "• Lifetime Cap: $10000\n"
                "• Lot Size: 0.5"
            )
            self.send_message(msg)
            self.logger.info("[RISK RESET] All risk settings reset to defaults")
            
        except Exception as e:
            self.logger.error(f"[RISK RESET ERROR] {str(e)}")
            self.send_message(f"❌ Error resetting settings: {str(e)}")
    
    def handle_clear_loss_data(self, message):
        """Clear lifetime loss data"""
        if not self._ensure_dependencies() or not self.risk_manager or not self.trading_engine:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        try:
            self.risk_manager.reset_lifetime_loss()
            self.trading_engine.db.clear_lifetime_losses()
            self.send_message("✅ Lifetime loss data cleared successfully")
        except Exception as e:
            self.send_message(f"❌ Error clearing loss data: {str(e)}")
    
    def handle_clear_daily_loss(self, message):
        """Clear daily loss data with verification"""
        if not self._ensure_dependencies() or not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        try:
            # Get current values before reset
            old_loss = self.risk_manager.daily_loss
            old_profit = self.risk_manager.daily_profit
            
            # Reset and verify
            success = self.risk_manager.reset_daily_loss()
            
            if success:
                # Read file to triple-verify
                import json
                import os
                stats_file = self.risk_manager.stats_file
                
                if os.path.exists(stats_file):
                    with open(stats_file, 'r') as f:
                        data = json.load(f)
                    
                    file_daily_loss = data.get('daily_loss', -1)
                    
                    msg = (
                        f"✅ Daily loss cleared successfully\n\n"
                        f"Previous Values:\n"
                        f"├─ Daily Loss: ${old_loss:.2f}\n"
                        f"├─ Daily Profit: ${old_profit:.2f}\n\n"
                        f"Current Values:\n"
                        f"├─ Daily Loss: ${self.risk_manager.daily_loss:.2f}\n"
                        f"├─ Daily Profit: ${self.risk_manager.daily_profit:.2f}\n\n"
                        f"📁 Verified in file: {os.path.basename(stats_file)}\n"
                        f"   File daily_loss: ${file_daily_loss:.2f}\n\n"
                        f"✅ Bot can now accept new trades"
                    )
                else:
                    msg = "⚠️ Stats cleared in memory but file not found. Restart bot recommended."
                
                self.send_message(msg)
            else:
                self.send_message(
                    f"❌ CRITICAL ERROR: Failed to clear daily loss\n\n"
                    f"Memory was cleared but file write failed.\n"
                    f"File: {self.risk_manager.stats_file}\n\n"
                    f"Action required: Restart bot or run manual reset script"
                )
                
        except Exception as e:
            self.logger.error(f"Error in handle_clear_daily_loss: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.send_message(f"❌ Error clearing daily loss: {str(e)}")
    
    def handle_tp_system(self, message):
        """Control TP re-entry system: /tp_system [on/off/status]"""
        try:
            parts = message["text"].strip().split()
            
            re_entry_config = self.config.get("re_entry_config", {})
            
            # Check if mode parameter provided directly (from menu)
            mode = message.get("mode", "").lower() if isinstance(message.get("mode"), str) else ""
            
            # Or extract from text
            if not mode and len(parts) >= 2:
                mode = parts[1].lower()
            
            if mode == "on":
                re_entry_config["tp_reentry_enabled"] = True
                self.config["re_entry_config"] = re_entry_config
                self.send_message("✅ *TP Re-entry System ENABLED*\n\nTP re-entries will now be monitored.")
                return
            elif mode == "off":
                re_entry_config["tp_reentry_enabled"] = False
                self.config["re_entry_config"] = re_entry_config
                self.send_message("❌ *TP Re-entry System DISABLED*\n\nTP re-entries stopped.")
                return
            
            # Default to status
            enabled = re_entry_config.get("tp_reentry_enabled", False)
            status_emoji = "✅" if enabled else "❌"
            msg = (
                f"{status_emoji} *TP Re-entry System*\n\n"
                f"Status: {'ENABLED' if enabled else 'DISABLED'}\n"
                f"Chain Levels: {re_entry_config.get('max_reentry_levels', 3)}\n"
                f"SL Reduction: {re_entry_config.get('sl_reduction_per_level', 0.5)*100:.0f}% per level\n\n"
                "*Usage:*\n"
                "/tp_system on - Enable TP re-entry\n"
                "/tp_system off - Disable TP re-entry\n"
                "/tp_system status - Show this status"
            )
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_profit_sl_mode(self, message):
        """Set Profit SL Mode (SL-1.1, SL-2.1, etc.)"""
        try:
            # Extract mode from message
            if isinstance(message, dict) and 'profit_sl_mode' in message:
                mode = message['profit_sl_mode']
            else:
                parts = message.get('text', '').split()
                if len(parts) >= 2:
                    mode = parts[1]
                else:
                    self.send_message("❌ Usage: /profit_sl_mode MODE\nExample: /profit_sl_mode SL-1.1")
                    return

            # Validate mode
            valid_modes = ["SL-1.1", "SL-2.1"]
            if mode not in valid_modes:
                self.send_message(f"❌ Invalid mode. Valid modes: {', '.join(valid_modes)}")
                return

            # Update config
            pb_config = self.config.get('profit_booking_config', {})
            pb_config['sl_system'] = mode
            self.config.update('profit_booking_config', pb_config)
            
            # Send success message
            self.send_message(f"✅ <b>PROFIT SL MODE UPDATED</b>\n\nActive Mode: <b>{mode}</b>")
            self.logger.info(f"[PROFIT SL] Mode updated to {mode}")

        except Exception as e:
            self.logger.error(f"[PROFIT SL ERROR] {str(e)}")
            self.send_message(f"❌ Error setting Profit SL Mode: {str(e)}")

    def handle_set_profit_sl(self, message):
        """Set Profit SL value for a specific logic or fixed mode"""
        try:
            # Extract params
            logic = None
            value = None
            
            if isinstance(message, dict):
                # From menu
                logic = message.get('logic')
                value = message.get('value') or message.get('amount')
            else:
                # From text: /set_profit_sl LOGIC VALUE or /set_profit_sl VALUE
                parts = message.get('text', '').split()
                if len(parts) == 3:
                    logic = parts[1]
                    value = parts[2]
                elif len(parts) == 2:
                    value = parts[1]
                else:
                    self.send_message("❌ Usage: /set_profit_sl [LOGIC] VALUE\nExample: /set_profit_sl combinedlogic-1 20")
                    return

            if not value:
                self.send_message("❌ Missing value parameter")
                return

            try:
                sl_value = float(value)
            except ValueError:
                self.send_message("❌ Value must be a number")
                return

            # Get current config
            pb_config = self.config.get('profit_booking_config', {})
            current_mode = pb_config.get('sl_system', 'SL-1.1')
            
            if current_mode == 'SL-1.1':
                # Logic-specific settings
                if not logic:
                    self.send_message("❌ SL-1.1 mode requires LOGIC parameter (combinedlogic-1, combinedlogic-2, combinedlogic-3)")
                    return
                
                logic = logic.upper()
                if logic not in ['combinedlogic-1', 'combinedlogic-2', 'combinedlogic-3']:
                    self.send_message("❌ Invalid logic. Use combinedlogic-1, combinedlogic-2, or combinedlogic-3")
                    return
                
                sl_1_1 = pb_config.get('sl_1_1_settings', {})
                sl_1_1[logic] = sl_value
                pb_config['sl_1_1_settings'] = sl_1_1
                
                msg = f"✅ <b>PROFIT SL UPDATED (SL-1.1)</b>\n\nLogic: {logic}\nNew Value: ${sl_value:.2f}"
                
            elif current_mode == 'SL-2.1':
                # Fixed setting
                sl_2_1 = pb_config.get('sl_2_1_settings', {})
                sl_2_1['fixed_sl'] = sl_value
                pb_config['sl_2_1_settings'] = sl_2_1
                
                msg = f"✅ <b>PROFIT SL UPDATED (SL-2.1)</b>\n\nMode: Fixed\nNew Value: ${sl_value:.2f}"
            
            else:
                self.send_message(f"❌ Unknown SL mode: {current_mode}")
                return

            # Save config
            self.config.update('profit_booking_config', pb_config)
            self.send_message(msg)
            self.logger.info(f"[PROFIT SL] Updated {current_mode} settings")

        except Exception as e:
            self.logger.error(f"[SET PROFIT SL ERROR] {str(e)}")
            self.send_message(f"❌ Error setting Profit SL value: {str(e)}")
    
    def handle_sl_hunt(self, message):
        """Control SL Hunt re-entry system: /sl_hunt [on/off/status]"""
        try:
            parts = message["text"].strip().split()
            
            re_entry_config = self.config.get("re_entry_config", {})
            
            # Check if mode parameter provided directly (from menu)
            mode = message.get("mode", "").lower() if isinstance(message.get("mode"), str) else ""
            
            # Or extract from text
            if not mode and len(parts) >= 2:
                mode = parts[1].lower()
            
            if mode == "on":
                re_entry_config["sl_hunt_reentry_enabled"] = True
                self.config["re_entry_config"] = re_entry_config
                self.send_message("✅ *SL Hunt Re-entry System ENABLED*\n\nSL hunt monitoring started.")
                return
            elif mode == "off":
                re_entry_config["sl_hunt_reentry_enabled"] = False
                self.config["re_entry_config"] = re_entry_config
                self.send_message("❌ *SL Hunt Re-entry System DISABLED*\n\nSL hunt stopped.")
                return
            
            # Default to status
            enabled = re_entry_config.get("sl_hunt_reentry_enabled", False)
            status_emoji = "✅" if enabled else "❌"
            msg = (
                f"{status_emoji} *SL Hunt Re-entry System*\n\n"
                f"Status: {'ENABLED' if enabled else 'DISABLED'}\n"
                f"Offset: {re_entry_config.get('sl_hunt_offset_pips', 2)} pips\n"
                f"Cooldown: {re_entry_config.get('sl_hunt_cooldown_seconds', 60)}s\n\n"
                "*Usage:*\n"
                "/sl_hunt on - Enable SL hunt\n"
                "/sl_hunt off - Disable SL hunt\n"
                "/sl_hunt status - Show this status"
            )
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_exit_continuation(self, message):
        """Control Exit Continuation re-entry system: /exit_continuation [on/off/status]"""
        try:
            parts = message["text"].strip().split()
            
            re_entry_config = self.config.get("re_entry_config", {})
            
            # Check if mode parameter provided directly (from menu)
            mode = message.get("mode", "").lower() if isinstance(message.get("mode"), str) else ""
            
            # Or extract from text
            if not mode and len(parts) >= 2:
                mode = parts[1].lower()
            
            if mode == "on":
                re_entry_config["exit_continuation_enabled"] = True
                self.config["re_entry_config"] = re_entry_config
                self.send_message("✅ *Exit Continuation System ENABLED*\n\nExit continuation monitoring started.")
                return
            elif mode == "off":
                re_entry_config["exit_continuation_enabled"] = False
                self.config["re_entry_config"] = re_entry_config
                self.send_message("❌ *Exit Continuation System DISABLED*\n\nExit continuation stopped.")
                return
            
            # Default to status
            enabled = re_entry_config.get("exit_continuation_enabled", False)
            status_emoji = "✅" if enabled else "❌"
            msg = (
                f"{status_emoji} *Exit Continuation System*\n\n"
                f"Status: {'ENABLED' if enabled else 'DISABLED'}\n"
                f"Gap: {re_entry_config.get('exit_continuation_gap_pips', 3)} pips\n"
                f"Cooldown: {re_entry_config.get('exit_continuation_cooldown', 120)}s\n\n"
                "*Usage:*\n"
                "/exit_continuation on - Enable exit continuation\n"
                "/exit_continuation off - Disable exit continuation\n"
                "/exit_continuation status - Show this status"
            )
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_tp_report(self, message):
        """Show TP re-entry statistics and performance"""
        if not self._ensure_dependencies() or not self.trading_engine:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        try:
            tp_stats = self.trading_engine.db.get_tp_reentry_stats()
            sl_stats = self.trading_engine.db.get_sl_hunt_reentry_stats()
            reversal_stats = self.trading_engine.reversal_handler.get_reversal_exit_stats()
            
            msg = "📊 <b>Advanced Re-entry Report (30 Days)</b>\n\n"
            
            msg += "<b>TP Re-entry System:</b>\n"
            msg += f"Total TP Re-entries: {tp_stats.get('total_tp_reentries', 0)}\n"
            msg += f"Profitable: {tp_stats.get('profitable_tp_reentries', 0)}\n"
            msg += f"Total PnL: ${tp_stats.get('total_tp_reentry_pnl', 0):.2f}\n"
            msg += f"Avg PnL: ${tp_stats.get('avg_tp_reentry_pnl', 0):.2f}\n\n"
            
            msg += "<b>SL Hunt Re-entry System:</b>\n"
            msg += f"SL Hunt Attempts: {sl_stats.get('sl_hunt_attempts', 0)}\n"
            msg += f"Successful Re-entries: {sl_stats.get('total_sl_hunt_reentries', 0)}\n\n"
            
            msg += "<b>Reversal Exit System:</b>\n"
            msg += f"Total Reversal Exits: {reversal_stats.get('total_reversal_exits', 0)}\n"
            msg += f"Profitable Exits: {reversal_stats.get('profitable_exits', 0)}\n"
            msg += f"Total PnL: ${reversal_stats.get('total_reversal_pnl', 0):.2f}\n"
            msg += f"Avg PnL: ${reversal_stats.get('avg_reversal_pnl', 0):.2f}"
            
            self.send_message(msg)
            
        except Exception as e:
            self.send_message(f"❌ Error generating report: {str(e)}")

    def handle_simulation_mode(self, message):
        """Toggle simulation mode on/off or show status"""
        try:
            parts = message['text'].split()
            mode = parts[1].lower() if len(parts) > 1 else 'status'
            
            # Support 'status' to show current mode
            if mode == 'status':
                current_mode = "SIMULATION" if self.config.get('simulate_orders', False) else "LIVE TRADING"
                status_msg = (
                    f"📊 **Current Trading Mode:**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Mode: **{current_mode}**\n\n"
                    f"Simulation: {'✅ ON' if self.config.get('simulate_orders', False) else '❌ OFF'}\n\n"
                    f"💡 Use '/simulation_mode on' or '/simulation_mode off' to change"
                )
                self.send_message(status_msg)
                return
            
            if mode not in ['on', 'off']:
                self.send_message("❌ Invalid mode. Use 'status', 'on' or 'off'")
                return
            
            simulate = (mode == 'on')
            self.config.update('simulate_orders', simulate)
            
            status = "ENABLED ✅" if simulate else "DISABLED ❌"
            self.send_message(f"🔄 Simulation Mode: {status}\n\n{'⚠️ Orders will be simulated (not live)' if simulate else '✅ Live trading mode active'}")
        
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_reentry_config(self, message):
        """Display all re-entry configuration settings"""
        re_cfg = self.config.get('re_entry_config', {})
        
        msg = "⚙️ <b>Re-entry System Configuration</b>\n\n"
        msg += f"<b>System Status:</b>\n"
        msg += f"TP Re-entry: {'✅ ON' if re_cfg.get('tp_reentry_enabled', True) else '❌ OFF'}\n"
        msg += f"SL Hunt Re-entry: {'✅ ON' if re_cfg.get('sl_hunt_reentry_enabled', True) else '❌ OFF'}\n"
        msg += f"Reversal Exit: {'✅ ON' if re_cfg.get('reversal_exit_enabled', True) else '❌ OFF'}\n"
        msg += f"Exit Continuation: {'✅ ON' if re_cfg.get('exit_continuation_enabled', True) else '❌ OFF'}\n\n"
        
        msg += f"<b>Timing Settings:</b>\n"
        msg += f"Monitor Interval: {re_cfg.get('price_monitor_interval_seconds', 30)}s\n"
        msg += f"SL Hunt Cooldown: {re_cfg.get('sl_hunt_cooldown_seconds', 60)}s\n"
        msg += f"Recovery Window: {re_cfg.get('price_recovery_check_minutes', 2)} min\n\n"
        
        msg += f"<b>Re-entry Rules:</b>\n"
        msg += f"SL Hunt Offset: {re_cfg.get('sl_hunt_offset_pips', 1.0)} pips\n"
        msg += f"Max Chain Levels: {re_cfg.get('max_chain_levels', 2)}\n"
        msg += f"SL Reduction: {int(re_cfg.get('sl_reduction_per_level', 0.5) * 100)}%"
        
        self.send_message(msg)

    def handle_set_monitor_interval(self, message):
        """Set price monitor interval (30-300 seconds)"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message("❌ Usage: /set_monitor_interval [30-300]")
                return
            
            interval = int(parts[1])
            if not (30 <= interval <= 300):
                self.send_message("❌ Interval must be between 30-300 seconds")
                return
            
            re_cfg = self.config.get('re_entry_config', {})
            re_cfg['price_monitor_interval_seconds'] = interval
            self.config.update('re_entry_config', re_cfg)
            
            self.send_message(f"✅ Price monitor interval set to {interval}s")
        
        except ValueError:
            self.send_message("❌ Invalid number. Use: /set_monitor_interval [30-300]")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_sl_offset(self, message):
        """Set SL hunt offset pips (1-5)"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message("❌ Usage: /set_sl_offset [1-5]")
                return
            
            offset = float(parts[1])
            if not (1 <= offset <= 5):
                self.send_message("❌ Offset must be between 1-5 pips")
                return
            
            re_cfg = self.config.get('re_entry_config', {})
            re_cfg['sl_hunt_offset_pips'] = offset
            self.config.update('re_entry_config', re_cfg)
            
            self.send_message(f"✅ SL hunt offset set to {offset} pips")
        
        except ValueError:
            self.send_message("❌ Invalid number. Use: /set_sl_offset [1-5]")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_cooldown(self, message):
        """Set SL hunt cooldown (30-300 seconds)"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message("❌ Usage: /set_cooldown [30-300]")
                return
            
            cooldown = int(parts[1])
            if not (30 <= cooldown <= 300):
                self.send_message("❌ Cooldown must be between 30-300 seconds")
                return
            
            re_cfg = self.config.get('re_entry_config', {})
            re_cfg['sl_hunt_cooldown_seconds'] = cooldown
            self.config.update('re_entry_config', re_cfg)
            
            self.send_message(f"✅ SL hunt cooldown set to {cooldown}s")
        
        except ValueError:
            self.send_message("❌ Invalid number. Use: /set_cooldown [30-300]")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_recovery_time(self, message):
        """Set price recovery window (1-10 minutes)"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message("❌ Usage: /set_recovery_time [1-10]")
                return
            
            minutes = int(parts[1])
            if not (1 <= minutes <= 10):
                self.send_message("❌ Recovery time must be between 1-10 minutes")
                return
            
            re_cfg = self.config.get('re_entry_config', {})
            re_cfg['price_recovery_check_minutes'] = minutes
            self.config.update('re_entry_config', re_cfg)
            
            self.send_message(f"✅ Price recovery window set to {minutes} minutes")
        
        except ValueError:
            self.send_message("❌ Invalid number. Use: /set_recovery_time [1-10]")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_max_levels(self, message):
        """Set max re-entry chain levels (1-5)"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message("❌ Usage: /set_max_levels [1-5]")
                return
            
            levels = int(parts[1])
            if not (1 <= levels <= 5):
                self.send_message("❌ Max levels must be between 1-5")
                return
            
            re_cfg = self.config.get('re_entry_config', {})
            re_cfg['max_chain_levels'] = levels
            self.config.update('re_entry_config', re_cfg)
            
            self.send_message(f"✅ Max re-entry levels set to {levels}")
        
        except ValueError:
            self.send_message("❌ Invalid number. Use: /set_max_levels [1-5]")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_sl_reduction(self, message):
        """Set SL reduction percentage (0.3-0.7 = 30%-70%)"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message("❌ Usage: /set_sl_reduction [0.3-0.7]")
                return
            
            reduction = float(parts[1])
            if not (0.3 <= reduction <= 0.7):
                self.send_message("❌ Reduction must be between 0.3-0.7 (30%-70%)")
                return
            
            re_cfg = self.config.get('re_entry_config', {})
            re_cfg['sl_reduction_per_level'] = reduction
            self.config.update('re_entry_config', re_cfg)
            
            self.send_message(f"✅ SL reduction set to {int(reduction * 100)}% per level")
        
        except ValueError:
            self.send_message("❌ Invalid number. Use: /set_sl_reduction [0.3-0.7]")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_reset_reentry_config(self, message):
        """Reset all re-entry settings to defaults"""
        default_re_cfg = {
            "max_chain_levels": 2,
            "sl_reduction_per_level": 0.5,
            "recovery_window_minutes": 30,
            "min_time_between_re_entries": 60,
            "sl_hunt_offset_pips": 1.0,
            "tp_reentry_enabled": True,
            "sl_hunt_reentry_enabled": True,
            "reversal_exit_enabled": True,
            "price_monitor_interval_seconds": 30,
            "tp_continuation_price_gap_pips": 2.0,
            "sl_hunt_cooldown_seconds": 60,
            "price_recovery_check_minutes": 2
        }
        
        self.config.update('re_entry_config', default_re_cfg)
        self.send_message("✅ Re-entry config reset to defaults:\n\n"
                         "Monitor Interval: 30s\n"
                         "SL Offset: 1 pip\n"
                         "Cooldown: 60s\n"
                         "Recovery: 2 min\n"
                         "Max Levels: 2\n"
                         "SL Reduction: 50%")

    def handle_view_sl_config(self, message):
        """Display all symbol SL configurations with dual SL system info"""
        active_system = self.config.get('active_sl_system', 'sl-1')
        sl_enabled = self.config.get('sl_system_enabled', True)
        sl_systems = self.config.get('sl_systems', {})
        sl_reductions = self.config.get('symbol_sl_reductions', {})
        symbol_config = self.config.get('symbol_config', {})
        current_tier = self.config.get('default_risk_tier', '5000')
        
        system_info = sl_systems.get(active_system, {})
        system_name = system_info.get('name', active_system.upper())
        
        msg = f"📊 <b>SL Configuration</b>\n\n"
        msg += f"<b>Active System:</b> {system_name}\n"
        msg += f"<b>Status:</b> {'✅ ENABLED' if sl_enabled else '❌ DISABLED'}\n"
        msg += f"<b>Account Tier:</b> ${current_tier}\n\n"
        
        all_symbols = list(symbol_config.keys())
        
        for symbol in all_symbols:
            volatility = symbol_config.get(symbol, {}).get('volatility', 'MEDIUM')
            
            system_symbols = system_info.get('symbols', {})
            if symbol in system_symbols and current_tier in system_symbols[symbol]:
                original_pips = system_symbols[symbol][current_tier]['sl_pips']
            else:
                original_pips = 0
            
            reduction_percent = sl_reductions.get(symbol, 0)
            
            if reduction_percent > 0:
                current_pips = int(original_pips * (1 - reduction_percent / 100))
                msg += f"<b>{symbol} ({volatility}):</b>\n"
                msg += f"  Original: {original_pips} pips | Reduced: {reduction_percent}% | Current: {current_pips} pips\n\n"
            else:
                msg += f"<b>{symbol} ({volatility}):</b>\n"
                msg += f"  SL: {original_pips} pips (No reduction)\n\n"
        
        self.send_message(msg)

    def handle_set_symbol_sl(self, message):
        """Reduce symbol SL by percentage - /set_symbol_sl SYMBOL PERCENT"""
        try:
            parts = message['text'].split()
            if len(parts) != 3:
                self.send_message(
                    "❌ <b>Usage:</b> /set_symbol_sl SYMBOL PERCENT\n\n"
                    "<b>Example:</b> /set_symbol_sl XAUUSD 20\n"
                    "This reduces Gold SL by 20%\n\n"
                    "<b>Percent Range:</b> 5-50%"
                )
                return
            
            symbol = parts[1].upper()
            percent = float(parts[2])
            
            if not (5 <= percent <= 50):
                self.send_message("❌ Percentage must be between 5-50%")
                return
            
            symbol_config = self.config.get('symbol_config', {})
            if symbol not in symbol_config:
                self.send_message(f"❌ Symbol {symbol} not found in config")
                return
            
            active_system = self.config.get('active_sl_system', 'sl-1')
            sl_systems = self.config.get('sl_systems', {})
            current_tier = self.config.get('default_risk_tier', '5000')
            
            system_info = sl_systems.get(active_system, {})
            system_symbols = system_info.get('symbols', {})
            
            if symbol not in system_symbols or current_tier not in system_symbols[symbol]:
                self.send_message(f"❌ {symbol} not configured in {active_system}")
                return
            
            original_pips = system_symbols[symbol][current_tier]['sl_pips']
            current_pips = int(original_pips * (1 - percent / 100))
            
            sl_reductions = self.config.get('symbol_sl_reductions', {})
            sl_reductions[symbol] = percent
            self.config.update('symbol_sl_reductions', sl_reductions)
            
            self.send_message(
                f"✅ <b>{symbol} SL Reduced</b>\n\n"
                f"Original: {original_pips} pips\n"
                f"Reduction: {percent}%\n"
                f"Current: {current_pips} pips"
            )
        
        except ValueError:
            self.send_message("❌ Invalid percentage. Use numbers only (5-50)")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_sl_status(self, message):
        """Show current active SL system, enabled status, all symbol reductions"""
        active_system = self.config.get('active_sl_system', 'sl-1')
        sl_enabled = self.config.get('sl_system_enabled', True)
        sl_systems = self.config.get('sl_systems', {})
        sl_reductions = self.config.get('symbol_sl_reductions', {})
        
        system_info = sl_systems.get(active_system, {})
        system_name = system_info.get('name', active_system.upper())
        system_desc = system_info.get('description', '')
        
        msg = "⚙️ <b>SL SYSTEM STATUS</b>\n\n"
        msg += f"<b>Active System:</b> {system_name}\n"
        msg += f"<b>Description:</b> {system_desc}\n"
        msg += f"<b>Status:</b> {'✅ ENABLED' if sl_enabled else '❌ DISABLED'}\n\n"
        
        if sl_reductions:
            msg += "<b>Symbol SL Reductions:</b>\n"
            for symbol, percent in sl_reductions.items():
                msg += f"  {symbol}: {percent}% reduction\n"
        else:
            msg += "<b>Symbol SL Reductions:</b> None\n"
        
        self.send_message(msg)
    
    def handle_sl_system_change(self, message):
        """Switch between SL systems - /sl_system_change [sl-1/sl-2]"""
        try:
            # Try getting from direct param first (Menu System)
            new_system = message.get('system')
            
            # Fallback to text parsing (Command Line)
            if not new_system:
                parts = message['text'].split()
                if len(parts) == 2:
                    new_system = parts[1].lower()
            
            if not new_system:
                self.send_message(
                    "❌ <b>Usage:</b> /sl_system_change [sl-1/sl-2]\n\n"
                    "<b>Example:</b> /sl_system_change sl-2\n"
                    "Switches to SL-2 system"
                )
                return
            
            if new_system not in ['sl-1', 'sl-2']:
                self.send_message("❌ System must be sl-1 or sl-2")
                return
            
            sl_systems = self.config.get('sl_systems', {})
            if new_system not in sl_systems:
                self.send_message(f"❌ System {new_system} not found in config")
                return
            
            self.config.update('active_sl_system', new_system)
            
            system_info = sl_systems[new_system]
            system_name = system_info.get('name', new_system.upper())
            
            self.send_message(
                f"✅ <b>SL System Changed</b>\n\n"
                f"Now using: {system_name}\n"
                f"Description: {system_info.get('description', '')}"
            )
        
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_sl_system_on(self, message):
        """Enable specific SL system - /sl_system_on [sl-1/sl-2]"""
        try:
            # Try getting from direct param first (Menu System)
            system = message.get('system')
            
            # Fallback to text parsing (Command Line)
            if not system:
                parts = message['text'].split()
                if len(parts) == 2:
                    system = parts[1].lower()
            
            if not system:
                self.send_message(
                    "❌ <b>Usage:</b> /sl_system_on [sl-1/sl-2]\n\n"
                    "<b>Example:</b> /sl_system_on sl-1\n"
                    "Enables SL-1 system"
                )
                return
            
            if system not in ['sl-1', 'sl-2']:
                self.send_message("❌ System must be sl-1 or sl-2")
                return
            
            sl_systems = self.config.get('sl_systems', {})
            if system not in sl_systems:
                self.send_message(f"❌ System {system} not found in config")
                return
            
            self.config.update('active_sl_system', system)
            self.config.update('sl_system_enabled', True)
            
            system_info = sl_systems[system]
            system_name = system_info.get('name', system.upper())
            
            self.send_message(
                f"✅ <b>SL System Enabled</b>\n\n"
                f"Active: {system_name}\n"
                f"Status: ✅ ENABLED"
            )
        
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_complete_sl_system_off(self, message):
        """Disable all SL systems"""
        self.config.update('sl_system_enabled', False)
        
        self.send_message(
            "⚠️ <b>ALL SL SYSTEMS DISABLED</b>\n\n"
            "All SL systems are now turned off.\n"
            "Use /sl_system_on [sl-1/sl-2] to enable."
        )
    
    def handle_reset_symbol_sl(self, message):
        """Reset one symbol to original SL - /reset_symbol_sl SYMBOL"""
        try:
            parts = message['text'].split()
            if len(parts) != 2:
                self.send_message(
                    "❌ <b>Usage:</b> /reset_symbol_sl SYMBOL\n\n"
                    "<b>Example:</b> /reset_symbol_sl XAUUSD\n"
                    "Resets Gold to original SL"
                )
                return
            
            symbol = parts[1].upper()
            
            sl_reductions = self.config.get('symbol_sl_reductions', {})
            
            if symbol not in sl_reductions:
                self.send_message(f"❌ {symbol} has no SL reduction to reset")
                return
            
            del sl_reductions[symbol]
            self.config.update('symbol_sl_reductions', sl_reductions)
            
            self.send_message(
                f"✅ <b>{symbol} SL Reset</b>\n\n"
                f"{symbol} has been reset to original SL values"
            )
        
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_reset_all_sl(self, message):
        """Reset all symbols to original SL - clear all reductions"""
        sl_reductions = self.config.get('symbol_sl_reductions', {})
        
        if not sl_reductions:
            self.send_message("❌ No SL reductions to reset")
            return
        
        count = len(sl_reductions)
        self.config.update('symbol_sl_reductions', {})
        
        self.send_message(
            f"✅ <b>All SL Reductions Reset</b>\n\n"
            f"Reset {count} symbol(s) to original SL values"
        )

    def handle_view_risk_caps(self, message):
        """Display risk caps and current loss status"""
        if not self._ensure_dependencies() or not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return
        
        tiers = self.config.get('risk_tiers', {})
        current_tier = self.config.get('default_risk_tier', '5000')
        
        daily_loss = self.risk_manager.daily_loss
        lifetime_loss = self.risk_manager.lifetime_loss
        
        msg = "💰 <b>Risk Caps &amp; Loss Status</b>\n\n"
        msg += f"<b>Current Tier: ${current_tier}</b>\n\n"
        
        msg += f"<b>Current Loss:</b>\n"
        msg += f"Daily: ${abs(daily_loss):.2f}\n"
        msg += f"Lifetime: ${abs(lifetime_loss):.2f}\n\n"
        
        msg += f"<b>All Risk Tiers:</b>\n"
        for balance, caps in sorted(tiers.items(), key=lambda x: int(x[0])):
            daily_cap = caps.get('daily_loss_limit', 0)
            lifetime_cap = caps.get('max_total_loss', 0)
            msg += f"${balance}: Daily ${daily_cap} | Lifetime ${lifetime_cap}\n"
        
        self.send_message(msg)

    def handle_set_daily_cap(self, message):
        """Set daily loss limit for specific tier"""
        try:
            parts = message['text'].split()
            if len(parts) != 3:
                self.send_message("❌ Usage: /set_daily_cap TIER AMOUNT\nExample: /set_daily_cap 10000 500")
                return
            
            tier = parts[1]
            amount = float(parts[2])
            
            if amount <= 0:
                self.send_message("❌ Amount must be positive")
                return
            
            tiers = self.config.get('risk_tiers', {})
            
            # Create tier if doesn't exist
            if tier not in tiers:
                tiers[tier] = {}
            
            tiers[tier]['daily_loss_limit'] = amount
            self.config.update('risk_tiers', tiers)
            
            # Send detailed success message
            success_msg = (
                f"✅ <b>DAILY LOSS LIMIT UPDATED</b>\n\n"
                f"🎯 Tier: ${tier}\n"
                f"📉 Daily Limit: ${amount:.2f}\n\n"
                f"✅ Configuration saved successfully!"
            )
            self.send_message(success_msg)
        
        except ValueError:
            self.send_message("❌ Invalid amount. Use numbers only")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_lifetime_cap(self, message):
        """Set lifetime loss limit for specific tier"""
        try:
            parts = message['text'].split()
            if len(parts) != 3:
                self.send_message("❌ Usage: /set_lifetime_cap TIER AMOUNT\nExample: /set_lifetime_cap 10000 2000")
                return
            
            tier = parts[1]
            amount = float(parts[2])
            
            if amount <= 0:
                self.send_message("❌ Amount must be positive")
                return
            
            tiers = self.config.get('risk_tiers', {})
            
            # Create tier if doesn't exist
            if tier not in tiers:
                tiers[tier] = {}
            
            tiers[tier]['max_total_loss'] = amount
            self.config.update('risk_tiers', tiers)
            
            # Send detailed success message
            success_msg = (
                f"✅ <b>LIFETIME LOSS LIMIT UPDATED</b>\n\n"
                f"🎯 Tier: ${tier}\n"
                f"🔴 Lifetime Limit: ${amount:.2f}\n\n"
                f"✅ Configuration saved successfully!"
            )
            self.send_message(success_msg)
        
        except ValueError:
            self.send_message("❌ Invalid amount. Use numbers only")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_risk_tier(self, message):
        """Set complete risk tier - /set_risk_tier BALANCE DAILY LIFETIME"""
        try:
            # Support both parameter-based and text-based input
            if isinstance(message, dict) and 'tier' in message:
                # Parameter-based (from menu)
                balance = message.get('tier')
                daily_limit = message.get('daily', 0)
                lifetime_limit = message.get('lifetime', 0)
                
                # Validate all parameters provided
                if not balance or daily_limit == 0 or lifetime_limit == 0:
                    self.send_message(f"❌ Missing parameters. Balance: {balance}, Daily: {daily_limit}, Lifetime: {lifetime_limit}")
                    return
            else:
                # Text-based (from direct command)
                parts = message.get('text', '').split()
                if len(parts) != 4:
                    self.send_message("❌ Usage: /set_risk_tier BALANCE DAILY LIFETIME\nExample: /set_risk_tier 10000 500 2000")
                    return
                
                balance = parts[1]
                daily_limit = float(parts[2])
                lifetime_limit = float(parts[3])
            
            # Convert to float
            daily_limit = float(daily_limit)
            lifetime_limit = float(lifetime_limit)
            
            if daily_limit <= 0 or lifetime_limit <= 0:
                self.send_message("❌ Limits must be positive")
                return
            
            tiers = self.config.get('risk_tiers', {})
            tiers[balance] = {
                'daily_loss_limit': daily_limit,
                'max_total_loss': lifetime_limit
            }
            self.config.update('risk_tiers', tiers)
            
            # Send detailed success message
            success_msg = (
                f"✅ <b>RISK TIER CONFIGURED</b>\n\n"
                f"🎯 Balance Tier: ${balance}\n"
                f"📉 Daily Loss Limit: ${daily_limit:.2f}\n"
                f"🔴 Lifetime Loss Limit: ${lifetime_limit:.2f}\n\n"
                f"✅ Configuration saved successfully!"
            )
            self.send_message(success_msg)
        
        except ValueError:
            self.send_message("❌ Invalid values. Use: /set_risk_tier BALANCE DAILY LIFETIME")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    # Dual Order Commands
    def handle_reset_risk_settings(self, message):
        """Reset all risk settings to defaults"""
        self._ensure_dependencies()
        try:
            # Reset to defaults
            default_tiers = {
                "5000": {"daily_loss_limit": 100.0, "max_total_loss": 500.0, "lot_size": 0.01},
                "10000": {"daily_loss_limit": 200.0, "max_total_loss": 1000.0, "lot_size": 0.05},
                "25000": {"daily_loss_limit": 500.0, "max_total_loss": 2500.0, "lot_size": 0.1},
                "50000": {"daily_loss_limit": 1000.0, "max_total_loss": 5000.0, "lot_size": 0.2},
                "100000": {"daily_loss_limit": 2000.0, "max_total_loss": 10000.0, "lot_size": 0.5}
            }
            
            self.config.update('risk_tiers', default_tiers)
            self.config.update('default_risk_tier', "5000")
            
            # Force reload in risk manager
            if self.risk_manager:
                self.risk_manager.load_config()
            
            self.send_message("✅ <b>Risk Settings Reset</b>\n\nAll risk tiers and limits have been reset to default values.")
            
        except Exception as e:
            self.send_message(f"❌ Error resetting risk settings: {str(e)}")

    def handle_set_lot_size(self, message):
        """Handle manual lot size override"""
        if not self._ensure_dependencies() or not self.risk_manager:
            self.send_message("❌ Bot still initializing. Please wait a moment.")
            return

        try:
            parts = message['text'].split()
            if len(parts) < 3:
                self.send_message("📝 Usage: /set_lot_size TIER LOT_SIZE\nExample: /set_lot_size 10000 0.05")
                return

            tier = parts[1]
            try:
                lot_size = float(parts[2])
            except ValueError:
                self.send_message("❌ Invalid lot size. Must be a number.")
                return

            # Validate tier
            valid_tiers = ["5000", "10000", "25000", "50000", "100000"]
            if tier not in valid_tiers:
                self.send_message(f"❌ Invalid tier. Use: {', '.join(valid_tiers)}")
                return

            # Update config
            fixed_lots = self.config.get('fixed_lot_sizes', {})
            fixed_lots[tier] = lot_size
            self.config.update('fixed_lot_sizes', fixed_lots)
            
            # Force reload in risk manager
            self.risk_manager.load_config()
            
            self.send_message(f"✅ <b>Lot Size Updated</b>\n\nTier: ${tier}\nNew Lot Size: {lot_size}")
            
        except Exception as e:
            self.send_message(f"❌ Error setting lot size: {str(e)}")

    def handle_lot_size_status(self, message):
        """Show current lot size status for all tiers"""
        try:
            fixed_lots = self.config.get('fixed_lot_sizes', {})
            current_tier = self.config.get('default_risk_tier', '5000')
            
            msg = "📊 <b>LOT SIZE CONFIGURATION</b>\n\n"
            msg += f"🎯 <b>Active Tier:</b> ${current_tier}\n\n"
            msg += "<b>Fixed Lot Sizes:</b>\n"
            
            for tier, lot in fixed_lots.items():
                marker = "✅" if tier == current_tier else "•"
                msg += f"{marker} ${tier}: {lot} lots\n"
                
            msg += "\n💡 Use /set_lot_size TIER SIZE to override"
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error showing lot sizes: {str(e)}")

    # Dual Order Commands
    def handle_dual_order_status(self, message):
        """Show dual order system status"""
        try:
            dual_config = self.config.get("dual_order_config", {})
            enabled = dual_config.get("enabled", True)
            
            status_msg = (
                f"📊 DUAL ORDER SYSTEM STATUS\n\n"
                f"Status: {'✅ ENABLED' if enabled else '❌ DISABLED'}\n"
                f"Mode: Both orders use same lot size (no split)\n"
                f"Order A: TP Trail (existing system)\n"
                f"Order B: Profit Trail (pyramid system)\n"
                f"Note: Orders work independently - no rollback"
            )
            self.send_message(status_msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_toggle_dual_orders(self, message):
        """Toggle dual order system on/off"""
        try:
            dual_config = self.config.get("dual_order_config", {})
            current = dual_config.get("enabled", True)
            new_status = not current
            
            dual_config["enabled"] = new_status
            self.config.update("dual_order_config", dual_config)
            
            status = "✅ ENABLED" if new_status else "❌ DISABLED"
            self.send_message(f"✅ Dual order system: {status}")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    # Profit Booking Commands
    def handle_profit_status(self, message):
        """Show profit booking system status"""
        self._ensure_dependencies()
        try:
            profit_config = self.config.get("profit_booking_config", {})
            enabled = profit_config.get("enabled", True)
            max_level = profit_config.get("max_level", 4)
            profit_targets = profit_config.get("profit_targets", [10, 20, 40, 80, 160])
            multipliers = profit_config.get("multipliers", [1, 2, 4, 8, 16])
            
            status_msg = (
                f"💰 PROFIT BOOKING SYSTEM STATUS\n\n"
                f"Status: {'✅ ENABLED' if enabled else '❌ DISABLED'}\n"
                f"Max Level: {max_level}\n\n"
                f"Profit Targets:\n"
            )
            
            for i, target in enumerate(profit_targets[:max_level+1]):
                mult = multipliers[i] if i < len(multipliers) else 1
                status_msg += f"  Level {i}: ${target} ({mult}x orders)\n"
            
            self.send_message(status_msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_profit_stats(self, message):
        """Show profit booking statistics"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            profit_manager = getattr(self.trading_engine, 'profit_booking_manager', None)
            if not profit_manager:
                self.send_message("❌ Profit booking manager not available")
                return
            
            # Get stats from database
            db = getattr(self.trading_engine, 'db', None)
            if db:
                stats = db.get_profit_chain_stats()
                
                stats_msg = (
                    f"📊 PROFIT BOOKING STATISTICS\n\n"
                    f"Total Chains: {stats.get('total_chains', 0)}\n"
                    f"Active Chains: {stats.get('active_chains', 0)}\n"
                    f"Completed Chains: {stats.get('completed_chains', 0)}\n"
                    f"Average Level: {stats.get('avg_level', 0):.1f}\n"
                    f"Total Profit: ${stats.get('total_profit', 0):.2f}\n"
                    f"Avg Profit/Chain: ${stats.get('avg_profit_per_chain', 0):.2f}"
                )
                self.send_message(stats_msg)
            else:
                # Fallback: count active chains
                active_chains = profit_manager.get_all_chains()
                stats_msg = (
                    f"📊 PROFIT BOOKING STATISTICS\n\n"
                    f"Active Chains: {len(active_chains)}\n"
                )
                self.send_message(stats_msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_toggle_profit_booking(self, message):
        """Toggle profit booking system on/off"""
        self._ensure_dependencies()
        try:
            profit_config = self.config.get("profit_booking_config", {})
            current = profit_config.get("enabled", True)
            new_status = not current
            
            profit_config["enabled"] = new_status
            self.config.update("profit_booking_config", profit_config)
            
            status = "✅ ENABLED" if new_status else "❌ DISABLED"
            self.send_message(f"✅ Profit booking system: {status}")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_set_profit_targets(self, message):
        """Set profit targets - /set_profit_targets 10 20 40 80 160"""
        try:
            parts = message['text'].split()
            if len(parts) < 2:
                self.send_message("❌ Usage: /set_profit_targets TARGET1 TARGET2 ...\nExample: /set_profit_targets 10 20 40 80 160")
                return
            
            targets = [float(t) for t in parts[1:]]
            if any(t <= 0 for t in targets):
                self.send_message("❌ All targets must be positive")
                return
            
            profit_config = self.config.get("profit_booking_config", {})
            profit_config["profit_targets"] = targets
            profit_config["max_level"] = len(targets) - 1
            self.config.update("profit_booking_config", profit_config)
            
            self.send_message(f"✅ Profit targets updated: {targets}")
        except ValueError:
            self.send_message("❌ Invalid values. Use numbers only.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_profit_chains(self, message):
        """Show all active profit booking chains"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            profit_manager = getattr(self.trading_engine, 'profit_booking_manager', None)
            if not profit_manager:
                self.send_message("❌ Profit booking manager not available")
                return
            
            active_chains = profit_manager.get_all_chains()
            if not active_chains:
                self.send_message("📊 No active profit booking chains")
                return
            
            chains_msg = "📊 ACTIVE PROFIT BOOKING CHAINS\n\n"
            for chain_id, chain in list(active_chains.items())[:10]:  # Limit to 10
                chains_msg += (
                    f"Chain: {chain_id[:8]}...\n"
                    f"Symbol: {chain.symbol} {chain.direction.upper()}\n"
                    f"Level: {chain.current_level}/{chain.max_level}\n"
                    f"Profit: ${chain.total_profit:.2f}\n"
                    f"Orders: {len(chain.active_orders)}\n\n"
                )
            
            if len(active_chains) > 10:
                chains_msg += f"... and {len(active_chains) - 10} more chains"
            
            self.send_message(chains_msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_stop_profit_chain(self, message):
        """Stop a specific profit booking chain - /stop_profit_chain CHAIN_ID"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            parts = message['text'].split()
            if len(parts) < 2:
                self.send_message("❌ Usage: /stop_profit_chain CHAIN_ID")
                return
            
            chain_id = parts[1]
            
            profit_manager = getattr(self.trading_engine, 'profit_booking_manager', None)
            if not profit_manager:
                self.send_message("❌ Profit booking manager not available")
                return
            
            chain = profit_manager.get_chain(chain_id)
            if not chain:
                self.send_message(f"❌ Chain {chain_id} not found")
                return
            
            profit_manager.stop_chain(chain_id, "Manual stop via Telegram")
            self.send_message(f"✅ Chain {chain_id[:8]}... stopped")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_stop_all_profit_chains(self, message):
        """Stop all active profit booking chains"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            profit_manager = getattr(self.trading_engine, 'profit_booking_manager', None)
            if not profit_manager:
                self.send_message("❌ Profit booking manager not available")
                return
            
            active_chains = profit_manager.get_all_chains()
            if not active_chains:
                self.send_message("📊 No active chains to stop")
                return
            
            profit_manager.stop_all_chains("Manual stop all via Telegram")
            self.send_message(f"✅ Stopped {len(active_chains)} profit booking chains")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_set_chain_multipliers(self, message):
        """Set chain multipliers - /set_chain_multipliers 1 2 4 8 16"""
        try:
            parts = message['text'].split()
            if len(parts) < 2:
                self.send_message("❌ Usage: /set_chain_multipliers MULT1 MULT2 ...\nExample: /set_chain_multipliers 1 2 4 8 16")
                return
            
            multipliers = [int(m) for m in parts[1:]]
            if any(m <= 0 for m in multipliers):
                self.send_message("❌ All multipliers must be positive integers")
                return
            
            profit_config = self.config.get("profit_booking_config", {})
            profit_config["multipliers"] = multipliers
            profit_config["max_level"] = len(multipliers) - 1
            self.config.update("profit_booking_config", profit_config)
            
            self.send_message(f"✅ Chain multipliers updated: {multipliers}")
        except ValueError:
            self.send_message("❌ Invalid values. Use integers only.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_set_sl_reductions(self, message):
        """Set SL reductions - /set_sl_reductions 0 10 25 40 50"""
        try:
            parts = message['text'].split()
            if len(parts) < 2:
                self.send_message("❌ Usage: /set_sl_reductions RED1 RED2 ...\nExample: /set_sl_reductions 0 10 25 40 50")
                return
            
            reductions = [float(r) for r in parts[1:]]
            if any(r < 0 or r > 100 for r in reductions):
                self.send_message("❌ All reductions must be between 0 and 100")
                return
            
            profit_config = self.config.get("profit_booking_config", {})
            profit_config["sl_reductions"] = reductions
            self.config.update("profit_booking_config", profit_config)
            
            self.send_message(f"✅ SL reductions updated: {reductions}")
        except ValueError:
            self.send_message("❌ Invalid values. Use numbers only.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_profit_config(self, message):
        """Show profit booking configuration"""
        try:
            profit_config = self.config.get("profit_booking_config", {})
            enabled = profit_config.get("enabled", True)
            max_level = profit_config.get("max_level", 4)
            profit_targets = profit_config.get("profit_targets", [10, 20, 40, 80, 160])
            multipliers = profit_config.get("multipliers", [1, 2, 4, 8, 16])
            sl_reductions = profit_config.get("sl_reductions", [0, 10, 25, 40, 50])
            
            config_msg = (
                f"💰 PROFIT BOOKING CONFIGURATION\n\n"
                f"Status: {'✅ ENABLED' if enabled else '❌ DISABLED'}\n"
                f"Max Level: {max_level}\n\n"
                f"Profit Targets:\n"
            )
            
            for i, target in enumerate(profit_targets[:max_level+1]):
                mult = multipliers[i] if i < len(multipliers) else 1
                sl_red = sl_reductions[i] if i < len(sl_reductions) else 0
                config_msg += f"  Level {i}: ${target} ({mult}x orders, SL -{sl_red}%)\n"
            
            config_msg += f"\nMultipliers: {multipliers}\n"
            config_msg += f"SL Reductions: {sl_reductions}%"
            
            self.send_message(config_msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_profit_sl_status(self, message):
        """Show profit booking SL system status"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not self.profit_booking_manager:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            # Get current settings
            mode = calculator.current_mode
            enabled = calculator.enabled
            sl_1_1 = calculator.sl_1_1_settings
            sl_2_1 = calculator.sl_2_1_settings
            
            status_msg = (
                f"💰 *PROFIT BOOKING SL STATUS*\n\n"
                f"• System: {'✅ ENABLED' if enabled else '❌ DISABLED'}\n"
                f"• Mode: *{mode}*\n\n"
            )
            
            if mode == "SL-1.1":
                status_msg += "*Current Settings (Logic-Specific):*\n"
                status_msg += f"  • combinedlogic-1: ${sl_1_1.get('combinedlogic-1', 20.0):.2f} SL\n"
                status_msg += f"  • combinedlogic-2: ${sl_1_1.get('combinedlogic-2', 40.0):.2f} SL\n"
                status_msg += f"  • combinedlogic-3: ${sl_1_1.get('combinedlogic-3', 50.0):.2f} SL\n"
            else:
                status_msg += "*Current Settings (Universal Fixed):*\n"
                status_msg += f"  • All Logics: ${sl_2_1.get('fixed_sl', 10.0):.2f} SL\n"
            
            status_msg += "\nUse /profit_sl_mode to switch systems"
            
            self.send_message(status_msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_profit_sl_mode(self, message):
        """Switch between SL-1.1 and SL-2.1 modes"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not self.profit_booking_manager:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            # Parse command
            parts = message.get('text', '').split()
            if len(parts) < 2:
                self.send_message(
                    "❌ Usage: /profit_sl_mode SL-1.1 or /profit_sl_mode SL-2.1\n\n"
                    "• SL-1.1: Logic-Specific SL ($20/$40/$50)\n"
                    "• SL-2.1: Universal Fixed SL ($10 for all)"
                )
                return
            
            new_mode = parts[1].upper()
            if new_mode not in ["SL-1.1", "SL-2.1"]:
                self.send_message("❌ Invalid mode. Use SL-1.1 or SL-2.1")
                return
            
            old_mode = calculator.current_mode
            if calculator.switch_mode(new_mode):
                mode_desc = "Logic-Specific SL ($20/$40/$50)" if new_mode == "SL-1.1" else "Universal Fixed SL ($10 for all)"
                self.send_message(
                    f"✅ *Profit Booking SL Mode Changed*\n\n"
                    f"• {old_mode} → {new_mode}\n"
                    f"• Now using: {mode_desc}"
                )
            else:
                self.send_message("❌ Failed to switch mode. Please try again.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_enable_profit_sl(self, message):
        """Enable profit booking SL system"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not self.profit_booking_manager:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            if calculator.enable():
                self.send_message("✅ Profit Booking SL System ENABLED")
            else:
                self.send_message("⚠️ System already enabled")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_disable_profit_sl(self, message):
        """Disable profit booking SL system"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not self.profit_booking_manager:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            if calculator.disable():
                self.send_message("❌ Profit Booking SL System DISABLED")
            else:
                self.send_message("⚠️ System already disabled")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_set_profit_sl(self, message):
        """Set custom profit SL value"""
        self._ensure_dependencies()
        try:
            # Parse params
            logic = None
            value = None
            
            if isinstance(message, dict):
                logic = message.get('logic')
                value = message.get('value') or message.get('amount')
            else:
                parts = message.get('text', '').split()
                if len(parts) >= 2:
                    # Check if first arg is logic or value
                    if parts[1].lower() in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
                        logic = parts[1].lower()
                        if len(parts) >= 3:
                            value = parts[2]
                    else:
                        value = parts[1]
            
            if not value:
                self.send_message("❌ Usage: /set_profit_sl [LOGIC] VALUE")
                return
                
            try:
                value = float(value)
            except ValueError:
                self.send_message("❌ Value must be a number")
                return

            if not self.profit_booking_manager or not self.profit_booking_manager.profit_sl_calculator:
                 self.send_message("❌ Profit SL system not initialized")
                 return
                 
            calculator = self.profit_booking_manager.profit_sl_calculator
            
            if calculator.current_mode == "SL-1.1":
                if not logic:
                     self.send_message("❌ Mode SL-1.1 requires specifying LOGIC (combinedlogic-1/combinedlogic-2/combinedlogic-3)")
                     return
                calculator.update_sl_1_1(logic, value)
                self.send_message(f"✅ Profit SL for {logic} set to ${value:.2f}")
            else:
                calculator.update_sl_2_1(value)
                self.send_message(f"✅ Universal Profit SL set to ${value:.2f}")
                
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_reset_profit_sl(self, message):
        """Reset profit SL settings to defaults"""
        self._ensure_dependencies()
        try:
            if not self.profit_booking_manager or not self.profit_booking_manager.profit_sl_calculator:
                 self.send_message("❌ Profit SL system not initialized")
                 return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            calculator.sl_1_1_settings = {"combinedlogic-1": 20.0, "combinedlogic-2": 40.0, "combinedlogic-3": 50.0}
            calculator.sl_2_1_settings = {"fixed_sl": 10.0}
            calculator.save_config()
            
            self.send_message("✅ Profit SL settings reset to defaults")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_signal_status(self, message):
        """Show current signals for all symbols"""
        self._ensure_dependencies()
        try:
            if not self.trend_manager:
                self.send_message("❌ Trend manager not available")
                return
            
            symbols = self.config.get('symbol_config', {}).keys()
            if not symbols:
                symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD"]
                
            report = "📡 *SIGNAL STATUS REPORT*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for symbol in symbols:
                trends = self.trend_manager.get_all_trends(symbol)
                report += f"*{symbol}*\n"
                for tf, trend in trends.items():
                    icon = "🟢" if trend == "BULLISH" else "🔴" if trend == "BEARISH" else "⚪"
                    report += f"  {tf}: {icon} {trend}\n"
                report += "\n"
                
            self.send_message(report)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_performance_report(self, message):
        """Show 30-day performance report"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not hasattr(self.trading_engine, 'analytics_engine'):
                self.send_message("❌ Analytics engine not available")
                return
                
            report = self.trading_engine.analytics_engine.get_performance_report()
            
            msg = (
                "📊 *30-DAY PERFORMANCE REPORT*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Total Trades: {report.get('total_trades', 0)}\n"
                f"Win Rate: {report.get('win_rate', 0):.1f}%\n"
                f"Total PnL: ${report.get('total_pnl', 0):.2f}\n\n"
                f"✅ Winning Trades: {report.get('winning_trades', 0)}\n"
                f"❌ Losing Trades: {report.get('losing_trades', 0)}\n"
                f"💰 Avg Win: ${report.get('average_win', 0):.2f}\n"
                f"💸 Avg Loss: ${report.get('average_loss', 0):.2f}"
            )
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_pair_report(self, message):
        """Show performance by symbol pair"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not hasattr(self.trading_engine, 'analytics_engine'):
                self.send_message("❌ Analytics engine not available")
                return
                
            stats = self.trading_engine.analytics_engine.get_pair_performance()
            
            if not stats:
                self.send_message("📊 No trading data available for pair report")
                return
                
            msg = "📈 *PAIR PERFORMANCE REPORT*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for symbol, data in stats.items():
                win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
                icon = "🟢" if data['pnl'] >= 0 else "🔴"
                msg += (
                    f"*{symbol}* {icon}\n"
                    f"  PnL: ${data['pnl']:.2f}\n"
                    f"  Trades: {data['trades']} (WR: {win_rate:.0f}%)\n\n"
                )
            
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_strategy_report(self, message):
        """Show performance by strategy logic"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not hasattr(self.trading_engine, 'analytics_engine'):
                self.send_message("❌ Analytics engine not available")
                return
                
            stats = self.trading_engine.analytics_engine.get_strategy_performance()
            
            if not stats:
                self.send_message("📊 No trading data available for strategy report")
                return
                
            msg = "🤖 *STRATEGY PERFORMANCE REPORT*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for strategy, data in stats.items():
                win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
                icon = "🟢" if data['pnl'] >= 0 else "🔴"
                msg += (
                    f"*{strategy}* {icon}\n"
                    f"  PnL: ${data['pnl']:.2f}\n"
                    f"  Trades: {data['trades']} (WR: {win_rate:.0f}%)\n\n"
                )
            
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def handle_tp_report(self, message):
        """Show TP Re-entry system report"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not hasattr(self.trading_engine, 'reentry_manager'):
                self.send_message("❌ Re-entry manager not available")
                return
            
            reentry = self.trading_engine.reentry_manager
            active_chains = len(reentry.active_chains)
            
            # Note: Detailed stats might need DB support, showing basic info for now
            msg = (
                "🎯 *TP RE-ENTRY REPORT*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Active Chains: {active_chains}\n"
                f"System Status: {'✅ Active' if self.config.get('reentry_enabled', True) else '❌ Disabled'}\n\n"
                "ℹ️ *Configuration:*\n"
                f"• Monitor Interval: {self.config.get('reentry_monitor_interval', 60)}s\n"
                f"• Max Levels: {self.config.get('reentry_max_levels', 3)}\n"
                f"• SL Reduction: {self.config.get('reentry_sl_reduction', 0.5)*100:.0f}%"
            )
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            if calculator.set_enabled(True):
                self.send_message("✅ *Profit Booking SL Enabled*\n\nSL system is now active for new orders")
            else:
                self.send_message("❌ Failed to enable SL system. Please try again.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_disable_profit_sl(self, message):
        """Disable profit booking SL system"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not self.profit_booking_manager:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            if calculator.set_enabled(False):
                self.send_message("✅ *Profit Booking SL Disabled*\n\nNo SL will be set for profit booking orders")
            else:
                self.send_message("❌ Failed to disable SL system. Please try again.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_set_profit_sl(self, message):
        """Set custom SL for specific logic (SL-1.1 only)"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not self.profit_booking_manager:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            # Check if in SL-1.1 mode
            if calculator.current_mode != "SL-1.1":
                self.send_message(
                    "❌ Custom SL settings only available in SL-1.1 mode\n\n"
                    "Use /profit_sl_mode SL-1.1 to switch"
                )
                return
            
            # Parse command
            parts = message.get('text', '').split()
            if len(parts) < 3:
                self.send_message(
                    "❌ Usage: /set_profit_sl LOGIC AMOUNT\n\n"
                    "Example: /set_profit_sl combinedlogic-1 25\n"
                    "Valid logics: combinedlogic-1, combinedlogic-2, combinedlogic-3"
                )
                return
            
            logic = parts[1].upper()
            if logic not in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
                self.send_message("❌ Invalid logic. Use combinedlogic-1, combinedlogic-2, or combinedlogic-3")
                return
            
            try:
                amount = float(parts[2])
                if amount <= 0:
                    self.send_message("❌ Amount must be greater than 0")
                    return
            except ValueError:
                self.send_message("❌ Invalid amount. Use a number (e.g., 25)")
                return
            
            # Get old value
            old_value = calculator.sl_1_1_settings.get(logic, 20.0)
            
            if calculator.update_logic_sl(logic, amount):
                self.send_message(
                    f"✅ *Profit Booking SL Updated (SL-1.1)*\n\n"
                    f"• {logic}: ${old_value:.2f} → ${amount:.2f}"
                )
            else:
                self.send_message("❌ Failed to update SL. Please try again.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def handle_reset_profit_sl(self, message):
        """Reset profit booking SL settings to defaults"""
        self._ensure_dependencies()
        try:
            if not self.trading_engine or not self.profit_booking_manager:
                self.send_message("❌ Bot still initializing. Please wait a moment.")
                return
            
            calculator = self.profit_booking_manager.profit_sl_calculator
            if not calculator:
                self.send_message("❌ Profit booking SL calculator not available")
                return
            
            if calculator.reset_to_defaults():
                self.send_message(
                    "✅ *Profit Booking SL Reset*\n\n"
                    "All settings restored to defaults:\n"
                    "• Mode: SL-1.1\n"
                    "• Status: Enabled\n"
                    "• combinedlogic-1: $20.00\n"
                    "• combinedlogic-2: $40.00\n"
                    "• combinedlogic-3: $50.00\n"
                    "• SL-2.1 Fixed: $10.00"
                )
            else:
                self.send_message("❌ Failed to reset settings. Please try again.")
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    # ------------------------------------------------------------------
    # FINE-TUNE & AUTONOMOUS COMMANDS
    # ------------------------------------------------------------------
    
    def handle_fine_tune(self, message):
        """Show Fine-Tune Menu"""
        if self.fine_tune_handler:
            chat_id = message["chat"]["id"] if isinstance(message, dict) and "chat" in message else self.chat_id
            self.fine_tune_handler.show_fine_tune_menu(chat_id)
        else:
            self.send_message("⚠️ Fine-Tune System not initialized.")

    def handle_profit_protection(self, message):
        """Show Profit Protection Menu"""
        if self.fine_tune_handler:
            chat_id = message["chat"]["id"] if isinstance(message, dict) and "chat" in message else self.chat_id
            self.fine_tune_handler.show_profit_protection_menu(chat_id)
        else:
            self.send_message("⚠️ Fine-Tune System not initialized.")

    def handle_sl_reduction(self, message):
        """Show SL Reduction Menu"""
        if self.fine_tune_handler:
            chat_id = message["chat"]["id"] if isinstance(message, dict) and "chat" in message else self.chat_id
            self.fine_tune_handler.show_sl_reduction_menu(chat_id)
        else:
            self.send_message("⚠️ Fine-Tune System not initialized.")

    def handle_recovery_windows(self, message):
        """Show Recovery Windows Info"""
        if self.fine_tune_handler:
            chat_id = message["chat"]["id"] if isinstance(message, dict) and "chat" in message else self.chat_id
            self.fine_tune_handler.show_recovery_windows_info(chat_id)
        else:
            self.send_message("⚠️ Fine-Tune System not initialized.")

    def handle_autonomous_status(self, message):
        """Show Autonomous Dashboard Status"""
        self.handle_autonomous_dashboard(message)

    def handle_autonomous_dashboard(self, message):
        """Show proper Autonomous Dashboard"""
        if not hasattr(self.trading_engine, "autonomous_manager") or not self.trading_engine.autonomous_manager:
            self.send_message("⚠️ Autonomous System not active or initializing.")
            return

        am = self.trading_engine.autonomous_manager
        
        # Gather stats safely
        daily_recoveries = getattr(am, 'daily_recovery_count', 0)
        active_recoveries = 0
        if hasattr(am, 'active_recovery_monitors'):
            active_recoveries = len(am.active_recovery_monitors) 
        elif hasattr(am, 'recovery_window_monitor') and hasattr(am.recovery_window_monitor, 'active_monitors'):
            active_recoveries = len(am.recovery_window_monitor.active_monitors)
        
        # Check sub-managers
        pp_status = "✅ Active" if hasattr(am, "profit_protection") and am.profit_protection.enabled else "❌ Disabled"
        sl_status = "✅ Active" if hasattr(am, "sl_optimizer") and am.sl_optimizer.enabled else "❌ Disabled"
        
        msg = (
            "🤖 <b>AUTONOMOUS DASHBOARD</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Status:</b> ✅ RUNNING\n"
            f"<b>Daily Recoveries:</b> {daily_recoveries}/10\n"
            f"<b>Active Monitors:</b> {active_recoveries}\n"
            
            "<b>🔍 Sub-Systems:</b>\n"
            f"• Profit Protection: {pp_status}\n"
            f"• SL Optimizer: {sl_status}\n"
            f"• Recovery Windows: ✅ Active\n"
            
            "<b>⚙ Active Configuration:</b>\n"
            "• TP Continuation: ON\n"
            "• SL Hunt Recovery: ON\n"
            "• Exit Continuation: ON"
        )
        
        # Add keyboard with shortcuts
        keyboard = [
            [{"text": "⚡ Fine-Tune Menu", "callback_data": "menu_fine_tune"}, 
             {"text": "🔄 Refresh", "callback_data": "ft_autonomous_dashboard"}],
            [{"text": "📊 View Trends", "callback_data": "menu_trends"}, 
             {"text": "🛡 Profit Protection", "callback_data": "ft_profit_protection"}],
            [{"text": "🏠 Main Menu", "callback_data": "menu_main"}]
        ]

        self.send_message(msg, reply_markup={"inline_keyboard": keyboard})

    def handle_dashboard(self, message):
        """Display interactive dashboard with live PnL"""
        try:
            print(f"DEBUG: handle_dashboard called with message: {message}")
            
            # ALWAYS try to get dependencies from trading_engine if not set
            if not self.risk_manager and self.trading_engine:
                if hasattr(self.trading_engine, 'risk_manager') and self.trading_engine.risk_manager:
                    self.risk_manager = self.trading_engine.risk_manager
                    print("DEBUG: RiskManager retrieved from trading_engine")
            
            if not self.trading_engine:
                error_msg = (
                    "❌ *Bot Still Initializing*\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "TradingEngine not initialized yet.\n"
                    "Please wait a few seconds and try again.\n\n"
                    "The bot is starting up..."
                )
                keyboard = []
                keyboard.append([{"text": "🏠 Main Menu", "callback_data": "menu_main"}])
                reply_markup = {"inline_keyboard": keyboard}
                self.send_message_with_keyboard(error_msg, reply_markup)
                print("DEBUG: TradingEngine not available")
                return
            
            # If still no risk_manager, try one more time
            if not self.risk_manager:
                if hasattr(self.trading_engine, 'risk_manager') and self.trading_engine.risk_manager:
                    self.risk_manager = self.trading_engine.risk_manager
                else:
                    # Use fallback values - don't block dashboard
                    print("WARNING: RiskManager not available, using fallback values")
                    self.risk_manager = None  # Will be handled in _send_dashboard
            
            # Get message_id if available (for updating existing message)
            message_id = message.get("message_id") if isinstance(message, dict) else None
            print(f"DEBUG: Sending dashboard, message_id={message_id}")
            
            # Send dashboard (always send new message for /dashboard command)
            result = self._send_dashboard(None)  # Always send new message, not update
            
            if result is None:
                # If sending failed, try to send error message
                print("DEBUG: Dashboard send failed, sending error message")
                self.send_message("❌ Error: Could not display dashboard. Please check bot logs.")
            else:
                print(f"DEBUG: Dashboard sent successfully with message_id={result}")

        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")

    def _send_dashboard(self, message_id=None):
        """Send or update dashboard message"""
        try:
            print(f"DEBUG: _send_dashboard called, message_id={message_id}")
            
            # ALWAYS try to get dependencies from trading_engine if not set
            if not self.risk_manager and self.trading_engine:
                if hasattr(self.trading_engine, 'risk_manager') and self.trading_engine.risk_manager:
                    self.risk_manager = self.trading_engine.risk_manager
                    print("DEBUG: RiskManager retrieved in _send_dashboard")
            
            if not self.trading_engine:
                print("DEBUG: TradingEngine not available in _send_dashboard")
                return None
            
            # If still no risk_manager, use fallback - don't block dashboard
            if not self.risk_manager:
                print("WARNING: RiskManager not available, using fallback values")
            
            # Get live data with safe fallbacks
            try:
                account_balance = self.mt5_client.get_account_balance() if self.mt5_client else 0.0
            except Exception as e:
                print(f"DEBUG: Error getting account balance: {e}")
                account_balance = 0.0
            
            try:
                trading_enabled = self.trading_engine.trading_enabled if self.trading_engine else False
            except Exception as e:
                print(f"DEBUG: Error getting trading_enabled: {e}")
                trading_enabled = False
            
            # Get PnL data with safe fallbacks
            try:
                if all([self.risk_manager, self.trading_engine, self.mt5_client, self.pip_calculator]):
                    live_pnl_data = self.risk_manager.get_live_open_trades_pnl(
                        self.trading_engine, self.mt5_client, self.pip_calculator
                    )
                else:
                    print("DEBUG: Missing dependencies for live PnL calculation")
                    live_pnl_data = {'total_live_pnl': 0.0, 'trade_details': []}
            except Exception as e:
                print(f"DEBUG: Error calculating live PnL: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                live_pnl_data = {'total_live_pnl': 0.0, 'trade_details': []}
            
            # Get today's performance with safe fallbacks
            try:
                if self.risk_manager and self.db:
                    today_data = self.risk_manager.get_todays_performance(self.db)
                else:
                    print("DEBUG: Missing RiskManager or DB for today's performance")
                    today_data = {'profit': 0.0, 'loss': 0.0, 'net': 0.0, 'trade_count': 0}
            except Exception as e:
                print(f"DEBUG: Error getting today's performance: {e}")
                today_data = {'profit': 0.0, 'loss': 0.0, 'net': 0.0, 'trade_count': 0}
            
            # Format PnL values safely - handle missing risk_manager
            try:
                if self.risk_manager:
                    live_pnl_text = self.risk_manager.format_pnl_value(live_pnl_data['total_live_pnl'])
                else:
                    live_pnl_text = f"${live_pnl_data['total_live_pnl']:.2f}"
            except Exception as e:
                print(f"DEBUG: Error formatting live PnL: {e}")
                live_pnl_text = f"${live_pnl_data['total_live_pnl']:.2f}"
            
            try:
                if self.risk_manager:
                    net_pnl_text = self.risk_manager.format_pnl_value(today_data['net'])
                else:
                    net_pnl_text = f"${today_data['net']:.2f}"
            except Exception as e:
                print(f"DEBUG: Error formatting net PnL: {e}")
                net_pnl_text = f"${today_data['net']:.2f}"
            
            # Check system status safely
            try:
                dual_orders_status = '🟢 ON' if (self.dual_order_manager and hasattr(self.dual_order_manager, 'is_enabled') and self.dual_order_manager.is_enabled()) else '🔴 OFF'
            except Exception as e:
                print(f"DEBUG: Error checking dual orders: {e}")
                dual_orders_status = '🔴 OFF'
            
            try:
                profit_booking_status = '🟢 ON' if (self.profit_booking_manager and hasattr(self.profit_booking_manager, 'is_enabled') and self.profit_booking_manager.is_enabled()) else '🔴 OFF'
            except Exception as e:
                print(f"DEBUG: Error checking profit booking: {e}")
                profit_booking_status = '🔴 OFF'
            
            try:
                reentry_status = '🟢 ON' if (self.reentry_manager and self.config.get('re_entry_config', {}).get('sl_hunt_reentry_enabled', False)) else '🔴 OFF'
            except Exception as e:
                print(f"DEBUG: Error checking re-entry: {e}")
                reentry_status = '🔴 OFF'
            
            # Format dashboard text (HTML)
            dashboard_text = f"""🤖 <b>ZEPIX TRADING BOT DASHBOARD</b>

══════════════════════════════

<b>📊 LIVE STATUS</b>

• Bot: {'🟢 RUNNING' if trading_enabled else '🔴 PAUSED'}
• Balance: ${account_balance:.2f}
• Open Trades: {len(live_pnl_data.get('trade_details', []))}
• Live PnL: {live_pnl_text}

<b>💰 TODAY'S PERFORMANCE</b>

• Today's Profit: 🟢 +${today_data.get('profit', 0.0):.2f}
• Today's Loss: 🔴 -${abs(today_data.get('loss', 0.0)):.2f}
• Net PnL: {net_pnl_text}
• Trades Today: {today_data.get('trade_count', 0)}

<b>🎯 TRADING SYSTEMS</b>

• Dual Orders: {dual_orders_status}
• Profit Booking: {profit_booking_status}
• Re-entry: {reentry_status}

"""
            
            # Add individual trades if any
            trade_details = live_pnl_data.get('trade_details', [])
            if trade_details:
                dashboard_text += "\n<b>⚡ LIVE TRADES</b>\n"
                for trade in trade_details:
                    try:
                        pnl_text = self.risk_manager.format_pnl_value(trade.get('live_pnl', 0.0)) if self.risk_manager else f"${trade.get('live_pnl', 0.0):.2f}"
                        symbol = trade.get('symbol', 'N/A')
                        direction = trade.get('direction', 'N/A')
                        sl_price = trade.get('sl_price', 0.0)
                        tp_price = trade.get('tp_price', 0.0)
                        dashboard_text += f"• {symbol} {direction} | {pnl_text} | "
                        dashboard_text += f"SL: {sl_price:.5f} | TP: {tp_price:.5f}\n"
                    except Exception as e:
                        print(f"DEBUG: Error formatting trade: {e}")
                        continue
            else:
                dashboard_text += "\n<b>⚡ LIVE TRADES</b>\n• No open positions\n"
            
            dashboard_text += f"\n<i>Last updated: {datetime.now().strftime('%H:%M:%S')}</i>"
            
            # Create inline keyboard
            keyboard = [
                [
                    {"text": "⏸️ PAUSE", "callback_data": "dashboard_pause"},
                    {"text": "📊 STATUS", "callback_data": "dashboard_status"},
                    {"text": "📈 TRADES", "callback_data": "dashboard_trades"}
                ],
                [
                    {"text": "💰 PERFORMANCE", "callback_data": "dashboard_performance"},
                    {"text": "⚡ RISK", "callback_data": "dashboard_risk"},
                    {"text": "📉 TRENDS", "callback_data": "dashboard_trends"}
                ],
                [
                    {"text": "🔄 REFRESH", "callback_data": "dashboard_refresh"},
                    {"text": "❓ HELP", "callback_data": "dashboard_help"}
                ],
                [
                    {"text": "🏠 MAIN MENU", "callback_data": "menu_main"}
                ]
            ]
            
            reply_markup = {"inline_keyboard": keyboard}
            
            # Send or update message
            if message_id:
                # Update existing message
                url = f"{self.base_url}/editMessageText"
                payload = {
                    "chat_id": self.chat_id,
                    "message_id": message_id,
                    "text": dashboard_text,
                    "reply_markup": reply_markup,
                    "text": dashboard_text,
                    "reply_markup": reply_markup,
                    "parse_mode": "HTML"
                }
                requests.post(url, json=payload, timeout=10)
            else:
                # Send new message
                url = f"{self.base_url}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": dashboard_text,
                    "reply_markup": reply_markup,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        message_id = result.get("result", {}).get("message_id")
                        print(f"DEBUG: Dashboard sent successfully, message_id={message_id}")
                        return message_id
                    else:
                        print(f"DEBUG: Telegram API error: {result}")
                        return None
                else:
                    print(f"DEBUG: HTTP error {response.status_code}: {response.text}")
                    return None
            
        except Exception as e:
            import traceback
            print(f"Error sending dashboard: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _process_custom_input(self, user_id: int, param_type: str, value_text: str):
        """Process custom value input from user"""
        try:
            self.logger.info(f"[CUSTOM INPUT] Processing {param_type} = {value_text}")
            
            # Handle /cancel command
            if value_text.startswith('/cancel'):
                self.menu_manager.context.update_context(user_id, waiting_for_input=None)
                self.send_message("❌ Custom input cancelled. Please use /start to return to main menu.")
                return
            
            # Validate input based on parameter type
            self.logger.info(f"[CUSTOM INPUT DEBUG] About to validate {param_type}")
            is_valid, validated_value, error_msg = self._validate_custom_input(param_type, value_text)
            self.logger.info(f"[CUSTOM INPUT DEBUG] Validation result: valid={is_valid}, value={validated_value}, error={error_msg}")
            
            if not is_valid:
                # Send error message
                self.send_message(f"❌ Invalid value: {error_msg}\n\nPlease try again or type /cancel to cancel.")
                return
            
            # Input is valid - store it
            self.logger.info(f"[CUSTOM INPUT DEBUG] Validated value: {validated_value}")

            
            self.logger.info(f"[CUSTOM INPUT DEBUG] Getting context for user {user_id}")
            context = self.menu_manager.context.get_context(user_id)
            self.logger.info(f"[CUSTOM INPUT DEBUG] Context type: {type(context)}, Context: {context}")
            
            pending_command = context.get('pending_command')
            self.logger.info(f"[CUSTOM INPUT DEBUG] Pending command: {pending_command}")
            
            # Store the parameter value DIRECTLY in context
            self.logger.info(f"[CUSTOM INPUT] Storing {param_type} = {validated_value} for command {pending_command}")
            self.menu_manager.context.add_param(user_id, param_type, str(validated_value))
            
            # Clear waiting state
            self.menu_manager.context.update_context(user_id, waiting_for_input=None)
            
            # Check if more parameters are needed
            if pending_command and self.menu_manager:
                next_param = self.menu_manager.get_next_parameter(user_id, pending_command)
                
                if next_param:
                    # Show next parameter selection
                    self.logger.info(f"[CUSTOM INPUT] More params needed. Showing next: {next_param}")
                    # Send new message with parameter selection (can't edit previous one)
                    self.menu_manager.show_parameter_selection(user_id, next_param, pending_command, None)
                else:
                    # All parameters collected - show confirmation
                    self.logger.info(f"[CUSTOM INPUT] All params collected. Showing confirmation")
                    self.menu_manager.show_confirmation(user_id, pending_command, None)
            else:
                self.send_message("✅ Value saved. Please use /start to continue.")
                
        except Exception as e:
            self.logger.error(f"[CUSTOM INPUT] Error processing input: {e}")
            import traceback
            self.logger.error(f"[CUSTOM INPUT] Full traceback:\n{traceback.format_exc()}")
            traceback.print_exc()
            self.send_message("❌ Error processing your input. Please try again or use /start.")
    
    # NOTE: _validate_custom_input method moved to line ~3038 with tuple return type
    # This duplicate was causing "tuple indices must be integers or slices, not str" error
    
    def handle_callback_query(self, callback_query):
        """Handle callback queries - Menu navigation, parameter selection, and command execution"""
        try:
            callback_data = callback_query.get("data", "")
            message = callback_query.get("message", {})
            message_id = message.get("message_id")
            user_id = callback_query.get("from", {}).get("id")
            
            # Always answer callback query first to prevent loading spinner
            callback_id = callback_query.get("id")
            if callback_id:
                try:
                    url = f"{self.base_url}/answerCallbackQuery"
                    requests.post(url, json={"callback_query_id": callback_id}, timeout=5)
                except:
                    pass  # Ignore errors in answering callback
            
            # Permission check
            allowed_user = self.config.get("allowed_telegram_user")
            if allowed_user and user_id != allowed_user:
                return
            
            # Ensure menu_manager is available
            if not self.menu_manager:
                error_text = (
                    "❌ *Menu System Not Ready*\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Menu system is still initializing.\n"
                    "Please wait a moment and try again."
                )
                try:
                    self.edit_message(error_text, message_id)
                except:
                    self.send_message(error_text)
                return
            
            # Check context expiration
            if hasattr(self.menu_manager, 'context') and self.menu_manager.context._is_expired(user_id):
                self.menu_manager.context.clear_context(user_id)
                text = "⏱️ Your session has expired. Returning to main menu..."
                try:
                    self.edit_message(text, message_id)
                    self.menu_manager.show_main_menu(user_id, message_id)
                except:
                    self.send_message(text)
                return
            
            # ZERO-TYPING / PANIC HANDLERS
            if callback_data == "panic_close":
                self.handle_panic_close(callback_query)
                return
            elif callback_data == "confirm_panic_close":
                self.handle_confirm_panic_close(callback_query)
                return
            elif callback_data == "action_panic_close":
                # Route from persistent keyboard (Zero-Typing UI)
                self.handle_panic_close(callback_query)
                return

            # Handle dashboard callbacks (existing functionality)
            if callback_data.startswith("dashboard_"):
                if callback_data == "dashboard_refresh":
                    self._send_dashboard(message_id)
                elif callback_data == "dashboard_pause":
                    if self.trading_engine:
                        self.trading_engine.is_paused = not self.trading_engine.is_paused
                        status = "PAUSED" if self.trading_engine.is_paused else "RESUMED"
                        self.send_message(f"✅ Trading {status}\n\nRefreshing dashboard...")
                        self._send_dashboard(message_id)
                elif callback_data == "dashboard_status":
                    status_text = self.get_detailed_status()
                    self.edit_message(status_text, message_id)
                elif callback_data == "dashboard_trades":
                    self.show_open_trades_dashboard(message_id)
                elif callback_data == "dashboard_performance":
                    if hasattr(self, 'handle_performance'):
                        self.handle_performance({"message_id": message_id})
                elif callback_data == "dashboard_risk":
                    if hasattr(self, 'handle_view_risk_caps'):
                        self.handle_view_risk_caps({"message_id": message_id})
                elif callback_data == "dashboard_trends":
                    if hasattr(self, 'handle_show_trends'):
                        self.handle_show_trends({"message_id": message_id})
                elif callback_data == "dashboard_help":
                    help_text = """🤖 *DASHBOARD HELP*

*📊 Live Status* - Real-time bot status and PnL
*💰 Today's Performance* - Daily profit/loss breakdown  
*⚡ Live Trades* - Current open positions with real-time PnL

*BUTTONS:*
• ⏸️ PAUSE - Toggle trading on/off
• 📊 STATUS - Detailed system status
• 📈 TRADES - Open positions
• 💰 PERFORMANCE - Detailed PnL analytics
• ⚡ RISK - Risk management settings
• 📉 TRENDS - Market trend matrix
• 🔄 REFRESH - Update dashboard data

Use /dashboard to return to main view"""
                    self.edit_message(help_text, message_id)
                return
            
            # Delegate menu navigation to MenuCallbackHandler
            if self.menu_callback_handler.handle_menu_callback(callback_data, user_id, message_id):
                return
            
            # Delegate action callbacks to MenuCallbackHandler
            if self.menu_callback_handler.handle_action_callback(callback_data, user_id, message_id):
               return
            
            # Handle Fine-Tune Callbacks (ft_, pp_, slr_)
            if callback_data.startswith("ft_") or callback_data.startswith("pp_") or callback_data.startswith("slr_"):
                if hasattr(self, "fine_tune_handler") and self.fine_tune_handler:
                    if callback_data.startswith("pp_"):
                        self.fine_tune_handler.handle_profit_protection_callback(callback_query)
                    elif callback_data.startswith("slr_"):
                        self.fine_tune_handler.handle_sl_reduction_callback(callback_query)
                    else:
                        # ft_ or specific menu navigation
                        if callback_data == "ft_profit_protection":
                            self.fine_tune_handler.show_profit_protection_menu(user_id, message_id)
                        elif callback_data == "ft_sl_reduction":
                            self.fine_tune_handler.show_sl_reduction_menu(user_id, message_id)
                        elif callback_data == "ft_recovery_windows":
                             # Show window info
                             self.fine_tune_handler.show_recovery_windows(user_id, message_id)
                        elif callback_data == "ft_autonomous_dashboard":
                             # Show dashboard via main bot handler
                             self.handle_autonomous_dashboard(callback_query.get("message", {}))
                        elif callback_data == "ft_view_all":
                             self.fine_tune_handler.show_fine_tune_menu(user_id, message_id)
                        elif callback_data == "fine_tune_menu":
                             self.fine_tune_handler.show_fine_tune_menu(user_id, message_id)
                        else:
                             self.fine_tune_handler.show_fine_tune_menu(user_id, message_id)
                    return
                else:
                    self.send_message("❌ Fine-Tune system not initialized. Please restart bot.")
                    return
            
            elif callback_data == "action_dashboard":
                self.handle_dashboard({"message_id": message_id})
            
            elif callback_data == "action_pause_resume":
                if self.trading_engine:
                    if self.trading_engine.is_paused:
                        self.handle_resume({"message_id": message_id})
                    else:
                        self.handle_pause({"message_id": message_id})
            
            elif callback_data == "action_trades":
                self.handle_trades({"message_id": message_id})
            
            elif callback_data == "action_performance":
                self.handle_performance({"message_id": message_id})
            
            elif callback_data == "action_help":
                # Show help with command list
                self._show_help_menu(user_id, message_id)
            
            # Handle command selection from category menu
            elif callback_data.startswith("cmd_"):
                # Format: cmd_category_command_name
                # Note: Category names can have underscores (e.g., "sl_system")
                # So we need to match against known categories first
                from src.menu.menu_constants import COMMAND_CATEGORIES
                
                # Remove "cmd_" prefix
                remainder = callback_data[4:]  # Skip "cmd_"
                
                # Try to match against known categories
                category = None
                command = None
                for cat_key in COMMAND_CATEGORIES.keys():
                    if remainder.startswith(f"{cat_key}_"):
                        category = cat_key
                        command = remainder[len(cat_key) + 1:]  # Skip category + "_"
                        break
                
                if category and command:
                    self._handle_command_selection(user_id, category, command, message_id)
                else:
                    # Fallback to old logic for backward compatibility
                    parts = callback_data.split("_", 2)
                    if len(parts) >= 3:
                        category = parts[1]
                        command = parts[2]
                        self._handle_command_selection(user_id, category, command, message_id)
            
            # Handle parameter selection
            elif callback_data.startswith("param_"):
                # Format: param_paramtype_command_value
                # Example: param_symbol_set_trend_XAUUSD
                # Problem: command name may contain underscores (e.g., set_trend)
                # Solution: Get command from context, then parse
                context = self.menu_manager.context.get_context(user_id)
                pending_command = context.get("pending_command")
                
                if not pending_command:
                    # Try to extract from callback_data as fallback
                    parts = callback_data.split("_", 3)
                    if len(parts) >= 4:
                        if parts[1] == "custom":
                            # Delegate to menu_manager
                            self.menu_manager._handle_custom_parameter(user_id, parts[2], parts[3], message_id)
                            return
                        # Can't parse without command - show error
                        self.send_message("❌ Error: Command context lost. Please start over with /start")
                        return
                
                # We have the command from context, now parse properly
                # Improved parsing for parameter types with underscores
                remainder = callback_data[6:] # Skip "param_"
                
                # Check for custom parameter request first
                if remainder.startswith("custom_"):
                    # Format: param_custom_paramtype_command
                    custom_parts = remainder.split("_", 2)
                    if len(custom_parts) >= 3:
                        param_type = custom_parts[1]
                        # Normalize 'lot' to 'lot_size'
                        if param_type == "lot":
                            param_type = "lot_size"
                        
                        self.menu_manager._handle_custom_parameter(user_id, param_type, pending_command, message_id)
                        return
                    elif len(custom_parts) == 2 and custom_parts[1] == "lot":
                         # Special case for param_custom_lot
                         self.menu_manager._handle_custom_parameter(user_id, "lot_size", pending_command, message_id)
                         return
                
                # Check for known complex types first
                complex_types = ["profit_sl_mode", "lot_size", "sl_system", "sl_reduction", "max_levels", "start_date", "end_date", "chain_id"]
                param_type = None
                
                for pt in complex_types:
                    if remainder.startswith(pt + "_"):
                        param_type = pt
                        break
                
                if not param_type:
                    # Fallback to simple split
                    param_type = remainder.split("_", 1)[0]
                
                # Handle chain_id specially (dynamic)
                if param_type == "chain_id":
                    self._handle_dynamic_chain_selection(user_id, message_id)
                    return
                
                # Extract value
                # Format: param_{param_type}_{command}_{value} OR param_{param_type}_{value} (legacy/simple)
                
                # Special handling for 'lot' type
                if param_type == "lot":
                    param_type = "lot_size"
                
                prefix = f"{param_type}_"
                value_part = remainder[len(prefix):]
                
                # Check if command name is included in callback
                command_prefix = f"{pending_command}_"
                if value_part.startswith(command_prefix):
                    value = value_part[len(command_prefix):]
                else:
                    # Fallback: value is just the rest
                    value = value_part
                
                print(f"DEBUG: Parsed param - type: {param_type}, command: {pending_command}, value: {value}")
                self.menu_manager.handle_parameter_selection(user_id, param_type, value, pending_command, message_id)
            
            # Handle command execution
            elif callback_data.startswith("execute_"):
                command = callback_data.replace("execute_", "")
                self._execute_command_from_context(user_id, command, message_id)
            
            # Handle navigation
            elif callback_data == "nav_back":
                previous_menu = self.menu_manager.context.pop_menu(user_id)
                if previous_menu == "menu_main":
                    self.menu_manager.show_main_menu(user_id, message_id)
                else:
                    category = previous_menu.replace("menu_", "")
                    self.menu_manager.show_category_menu(user_id, category, message_id)
            
            else:
                # Unknown callback - try to handle as dashboard callback
                if callback_data.startswith("dashboard_"):
                    pass  # Already handled above
                else:
                    print(f"Unknown callback_data: {callback_data}")
                    # Send helpful message
                    error_text = (
                        "❓ *Unknown Action*\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        "This action is not recognized.\n\n"
                        "Please use /start to return to main menu."
                    )
                    keyboard = []
                    keyboard.append([{"text": "🏠 Main Menu", "callback_data": "menu_main"}])
                    reply_markup = {"inline_keyboard": keyboard}
                    try:
                        self.edit_message(error_text, message_id, reply_markup)
                    except:
                        self.send_message_with_keyboard(error_text, reply_markup)
            
        except Exception as e:
            print(f"Callback query handler error: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error message to user with menu button
            try:
                error_text = (
                    "❌ *Error*\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "An error occurred while processing your request.\n\n"
                    f"Error: {str(e)[:100]}\n\n"
                    "Please try again or use /start to return to main menu."
                )
                keyboard = []
                keyboard.append([{"text": "🏠 Main Menu", "callback_data": "menu_main"}])
                reply_markup = {"inline_keyboard": keyboard}
                try:
                    self.edit_message(error_text, message_id, reply_markup)
                except:
                    self.send_message_with_keyboard(error_text, reply_markup)
            except Exception as e2:
                print(f"Failed to send error message: {e2}")
                # Last resort - try to send simple message
                try:
                    self.send_message("❌ An error occurred. Please use /start to return to main menu.")
                except:
                    pass
    
    def _handle_command_selection(self, user_id: int, category: str, command: str, message_id: int):
        """Handle command selection from category menu"""
        try:
            from src.menu.menu_constants import COMMAND_CATEGORIES
            from src.menu.command_mapping import COMMAND_PARAM_MAP
            
            # Set pending command
            self.menu_manager.context.set_pending_command(user_id, command)
            self.menu_manager.context.clear_params(user_id)
            
            # First check menu_constants for command type (takes precedence)
            cmd_info = None
            if category in COMMAND_CATEGORIES:
                cmd_info = COMMAND_CATEGORIES[category]["commands"].get(command)
            
            # Get command type from either menu_constants or COMMAND_PARAM_MAP
            cmd_type = None
            if cmd_info and "type" in cmd_info:
                cmd_type = cmd_info.get("type")
            elif command in COMMAND_PARAM_MAP:
                cmd_type = COMMAND_PARAM_MAP[command].get("type", "direct")
            else:
                cmd_type = "direct"
            
            # Handle special command types
            if cmd_type == "submenu":
                # Submenu commands should execute directly without showing success message
                # They will display their own submenu
                success = self.menu_manager.executor.execute_command(user_id, command, {})
                # Don't show success message - the submenu is the response
                return
            elif cmd_type == "multi_targets":
                # Multi-target commands need special input
                self._handle_multi_target_command(user_id, command, message_id)
                return
            elif cmd_type == "dynamic":
                # Dynamic commands (like stop_profit_chain)
                if command == "stop_profit_chain":
                    self._handle_dynamic_chain_selection(user_id, message_id)
                return
            elif cmd_type == "direct":
                # No parameters - execute directly with success message
                self._execute_command_from_context(user_id, command, message_id)
                return
            
            # Check if command needs parameters
            if cmd_info and cmd_info.get("params"):
                # Show first parameter selection
                first_param = cmd_info["params"][0]
                result = self.menu_manager.show_parameter_selection(user_id, first_param, command, message_id)
                if result is None and first_param == "chain_id":
                    # Dynamic parameter - handled separately
                    self._handle_dynamic_chain_selection(user_id, message_id)
            else:
                # No parameters - execute directly
                self._execute_command_from_context(user_id, command, message_id)
        except Exception as e:
            print(f"Error handling command selection: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_multi_target_command(self, user_id: int, command: str, message_id: int):
        """Handle multi-target commands (set_profit_targets, set_chain_multipliers)"""
        try:
            from src.menu.dynamic_handlers import DynamicHandlers
            dynamic = DynamicHandlers(self)
            
            text, reply_markup = dynamic.format_multi_target_input(command)
            self.edit_message(text, message_id, reply_markup)
            
            # Store that we're waiting for multi-target input
            self.menu_manager.context.update_context(user_id, waiting_for_multi_target=command)
        except Exception as e:
            print(f"Error handling multi-target command: {e}")
            self.send_message(f"❌ Error: {str(e)}")
    
    def _handle_custom_parameter(self, user_id: int, param_type: str, command: str, message_id: int):
        """Handle custom parameter input request"""
        try:
            # Determine validation rules based on param_type
            validation_hints = {
                "amount": "Enter a dollar amount (e.g., 150, 500, 1000)",
                "daily": "Enter daily loss limit amount (e.g., 100, 500)",
                "lifetime": "Enter lifetime loss limit amount (e.g., 500, 2000)",
                "lot_size": "Enter lot size (e.g., 0.05, 0.1, 1.0)",
                "percent": "Enter percentage (e.g., 10, 25, 50)",
                "value": "Enter numeric value"
            }
            
            hint = validation_hints.get(param_type, f"Enter value for {param_type}")
            
            text = (
                f"⚙️ *Custom {param_type.replace('_', ' ').title()}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📝 {hint}\n\n"
                f"💡 **Examples:**\n"
            )
            
            # Add specific examples based on param_type
            if param_type in ["amount", "daily", "lifetime"]:
                text += "• 100\n• 500\n• 1000\n• 2500\n"
            elif param_type == "lot_size":
                text += "• 0.01\n• 0.05\n• 0.1\n• 1.0\n"
            elif param_type == "percent":
                text += "• 10\n• 25\n• 50\n"
            else:
                text += "• Enter a numeric value\n"
            
            text += "\n❌ Type /cancel to cancel this operation."
            
            # Store that we're waiting for custom input
            self.menu_manager.context.update_context(user_id, waiting_for_custom_param=param_type, waiting_for_command=command)
            
            keyboard = []
            keyboard.append([{"text": "❌ Cancel", "callback_data": f"menu_{self.menu_manager.context.get_context(user_id).get('current_menu', 'menu_main').replace('menu_', '')}"}])
            reply_markup = {"inline_keyboard": keyboard}
            
            self.edit_message(text, message_id, reply_markup)
        except Exception as e:
            print(f"Error handling custom parameter: {e}")
    
    def _validate_custom_input(self, param_type: str, value_str: str, command: str = None) -> tuple:
        """
        Validate custom parameter input
        Returns: (is_valid: bool, validated_value: Any, error_message: str)
        """
        try:
            if param_type in ["amount", "daily", "lifetime"]:
                # Amount validation
                value = float(value_str)
                if value <= 0:
                    return (False, None, "Amount must be positive")
                if value > 1000000:
                    return (False, None, "Amount too large (max: $1,000,000)")
                return (True, str(int(value)), None)
            
            elif param_type == "lot_size":
                # Lot size validation
                value = float(value_str)
                if value <= 0:
                    return (False, None, "Lot size must be positive")
                if value < 0.01:
                    return (False, None, "Lot size too small (min: 0.01)")
                if value > 10.0:
                    return (False, None, "Lot size too large (max: 10.0)")
                return (True, str(value), None)
            
            elif param_type == "percent":
                # Percentage validation
                value = float(value_str)
                if value < 5:
                    return (False, None, "Percentage too small (min: 5%)")
                if value > 50:
                    return (False, None, "Percentage too large (max: 50%)")
                return (True, str(int(value)), None)
            
            elif param_type == "value":
                # Generic value validation
                value = float(value_str)
                if value < 0:
                    return (False, None, "Value must be non-negative")
                return (True, str(value), None)
            
            else:
                # Default: accept as string
                return (True, value_str, None)
        
        except ValueError:
            return (False, None, f"Invalid number format. Please enter a valid number.")
    
    def _execute_command_from_context(self, user_id: int, command: str, message_id: int):
        """Execute command with parameters from user context"""
        try:
            context = self.menu_manager.context.get_context(user_id)
            params = context.get("params", {})
            
            # Execute command
            success = self.menu_manager.executor.execute_command(user_id, command, params)
            
            if success:
                # Clear context
                self.menu_manager.context.clear_context(user_id)
                
                # Commands that send their own messages - don't show success screen
                self_messaging_commands = [
                    "logic1_on", "logic1_off", "logic2_on", "logic2_off", 
                    "logic3_on", "logic3_off", "pause", "resume", 
                    "status", "trades", "performance", "stats"
                ]
                
                if command in self_messaging_commands:
                    # These commands handle their own messaging
                    # ANTI-SPAM: User has persistent keyboard, no need to re-show menu
                    return
                
                # Get execution stats for confirmation
                stats = self.menu_manager.executor.get_execution_stats()
                
                # Format params for display
                params_display = ""
                if params:
                    params_list = []
                    for key, value in params.items():
                        if isinstance(value, list):
                            params_list.append(f"{key}: {', '.join(str(v) for v in value)}")
                        else:
                            params_list.append(f"{key}: {value}")
                    params_display = "\n".join(f"• {p}" for p in params_list)
                
                # Show enhanced success message
                text = (
                    f"✅ *Command Executed Successfully*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"*Command:* `/{command}`\n"
                )
                
                if params_display:
                    text += f"\n*Parameters:*\n{params_display}\n"
                
                text += (
                    f"\n✅ Command executed from menu system.\n"
                    f"Check the response above for command output.\n\n"
                    f"*Execution Stats:*\n"
                    f"• Total: {stats.get('total', 0)}\n"
                    f"• Success Rate: {stats.get('success_rate', 0.0)}%"
                )
                
                keyboard = []
                keyboard.append([{"text": "🏠 Main Menu", "callback_data": "menu_main"}])
                reply_markup = {"inline_keyboard": keyboard}
                
                self.edit_message(text, message_id, reply_markup)
                
                # Success message already shown
                # ANTI-SPAM: User has persistent keyboard for navigation
            else:
                # Show error message
                text = (
                    f"❌ *Command Failed*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Command: `/{command}`\n\n"
                    f"❌ Failed to execute command.\n"
                    f"Please check bot logs for details."
                )
                
                keyboard = []
                keyboard.append([{"text": "🔙 Back", "callback_data": "nav_back"}])
                keyboard.append([{"text": "🏠 Main Menu", "callback_data": "menu_main"}])
                reply_markup = {"inline_keyboard": keyboard}
                
                self.edit_message(text, message_id, reply_markup)
        except Exception as e:
            print(f"Error executing command from context: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_help_menu(self, user_id: int, message_id: int):
        """Show help menu with command list"""
        try:
            text = (
                "🆘 *HELP & COMMAND LIST*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "📋 *Total Commands: 72*\n\n"
                "💡 *How to Use:*\n"
                "• Use buttons to navigate - no typing required!\n"
                "• Select category → Select command → Select parameters → Confirm\n"
                "• All commands can also be typed directly\n\n"
                "🎯 *Quick Actions:*\n"
                "• Dashboard - Live PnL & controls\n"
                "• Pause/Resume - Toggle trading\n"
                "• Trades - View open positions\n"
                "• Performance - Trading metrics\n\n"
                "📋 *Categories:*\n"
                "• 💰 Trading Control (6 commands)\n"
                "• ⚡ Performance & Analytics (7 commands)\n"
                "• ⚙️ Strategy Control (7 commands)\n"
                "• 🔄 Re-entry System (12 commands)\n"
                "• 📍 Trend Management (5 commands)\n"
                "• 🛡️ Risk & Lot Management (8 commands)\n"
                "• ⚙️ SL System Control (8 commands)\n"
                "• 💎 Dual Orders (2 commands)\n"
                "• 📈 Profit Booking (16 commands)\n"
                "• 🔧 System Settings (1 command)\n\n"
                "💡 *Tip:* Use /start to return to main menu anytime!"
            )
            
            keyboard = []
            keyboard.append([{"text": "🏠 Main Menu", "callback_data": "menu_main"}])
            reply_markup = {"inline_keyboard": keyboard}
            
            self.edit_message(text, message_id, reply_markup)
        except Exception as e:
            print(f"Error showing help menu: {e}")
    
    def _show_logic_control_menu(self, user_id: int, message_id: int):
        """Show logic control submenu"""
        try:
            text = (
                "⚙️ *LOGIC CONTROL*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Select a logic to enable/disable:\n\n"
                "• combinedlogic-1: 1H+15M→5M\n"
                "• combinedlogic-2: 1H+15M→15M\n"
                "• combinedlogic-3: D+1H→1H"
            )
            
            keyboard = []
            # Logic status
            keyboard.append([{"text": "📊 Logic Status", "callback_data": "cmd_strategy_logic_status"}])
            keyboard.append([])
            # Logic 1
            keyboard.append([{"text": "✅ Enable combinedlogic-1", "callback_data": "cmd_strategy_combinedlogic1_on"},
                            {"text": "⛔ Disable combinedlogic-1", "callback_data": "cmd_strategy_combinedlogic1_off"}])
            # Logic 2
            keyboard.append([{"text": "✅ Enable combinedlogic-2", "callback_data": "cmd_strategy_combinedlogic2_on"},
                            {"text": "⛔ Disable combinedlogic-2", "callback_data": "cmd_strategy_combinedlogic2_off"}])
            # Logic 3
            keyboard.append([{"text": "✅ Enable combinedlogic-3", "callback_data": "cmd_strategy_combinedlogic3_on"},
                            {"text": "⛔ Disable combinedlogic-3", "callback_data": "cmd_strategy_combinedlogic3_off"}])
            keyboard.append([])
            # Navigation
            keyboard.append([{"text": "🔙 Back", "callback_data": "nav_back"},
                            {"text": "🏠 Home", "callback_data": "menu_main"}])
            
            reply_markup = {"inline_keyboard": keyboard}
            self.edit_message(text, message_id, reply_markup)
        except Exception as e:
            print(f"Error showing logic control menu: {e}")
    
    def _handle_dynamic_chain_selection(self, user_id: int, message_id: int):
        """Handle dynamic chain selection for stop_profit_chain"""
        try:
            from src.menu.dynamic_handlers import DynamicHandlers
            dynamic = DynamicHandlers(self)
            
            chains = dynamic.get_active_chain_ids()
            if not chains:
                text = (
                    "📭 *No Active Chains*\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "No active profit booking chains found.\n\n"
                    "Cannot stop any chains."
                )
                keyboard = []
                keyboard.append([{"text": "🔙 Back", "callback_data": "nav_back"}])
                reply_markup = {"inline_keyboard": keyboard}
                self.edit_message(text, message_id, reply_markup)
                return
            
            text, reply_markup = dynamic.format_chain_selection(chains)
            self.edit_message(text, message_id, reply_markup)
        except Exception as e:
            print(f"Error handling dynamic chain selection: {e}")
            self.send_message(f"❌ Error loading chains: {str(e)}")
    
    def _handle_multi_target_input(self, user_id: int, command: str, input_text: str, message_data: dict):
        """Handle multi-target input from user (for set_profit_targets, set_chain_multipliers)"""
        try:
            # Parse input (space-separated values)
            if input_text.lower() in ["/cancel", "cancel"]:
                self.menu_manager.context.update_context(user_id, waiting_for_multi_target=None)
                self.send_message("❌ Cancelled")
                self.menu_manager.show_main_menu(user_id)
                return
            
            values = input_text.split()
            try:
                # Convert to floats
                float_values = [float(v) for v in values]
                
                # Validate all positive
                if any(v <= 0 for v in float_values):
                    self.send_message("❌ All values must be positive numbers")
                    return
                
                # Store in context
                if command == "set_profit_targets":
                    self.menu_manager.context.add_param(user_id, "targets", float_values)
                elif command == "set_chain_multipliers":
                    self.menu_manager.context.add_param(user_id, "multipliers", float_values)
                
                # Clear waiting flag
                self.menu_manager.context.update_context(user_id, waiting_for_multi_target=None)
                
                # Show confirmation
                self.menu_manager.show_confirmation(user_id, command, message_data.get("message_id"))
                
            except ValueError:
                self.send_message("❌ Invalid input. Please enter space-separated numbers (e.g., 10 20 40 80 160)")
        except Exception as e:
            print(f"Error handling multi-target input: {e}")
            self.send_message(f"❌ Error: {str(e)}")
    
    def get_detailed_status(self):
        """Get detailed system status for dashboard"""
        try:
            account_balance = self.mt5_client.get_account_balance() if self.mt5_client else 0.0
            open_trades = self.trading_engine.get_open_trades() if self.trading_engine else []
            
            status_text = f"""🔍 *DETAILED SYSTEM STATUS*

══════════════════════════

*🤖 BOT STATUS*

• Trading: {'🟢 ENABLED' if (self.trading_engine and self.trading_engine.trading_enabled) else '🔴 PAUSED'}
• Balance: ${account_balance:.2f}
• Open Trades: {len(open_trades)}

*📊 SYSTEM HEALTH*

• MT5 Connection: {'🟢 CONNECTED' if (self.mt5_client and self.mt5_client.initialized) else '🔴 DISCONNECTED'}
• Database: {'🟢 OK' if (self.db and self.db.test_connection()) else '🔴 ERROR'}
• Telegram: {'🟢 ACTIVE' if self.token else '🔴 INACTIVE'}

*🎯 TRADING SYSTEMS*

• Dual Orders: {'🟢 ON' if (self.dual_order_manager and self.dual_order_manager.is_enabled()) else '🔴 OFF'}
• Profit Booking: {'🟢 ON' if (self.profit_booking_manager and self.profit_booking_manager.is_enabled()) else '🔴 OFF'}
• Re-entry Systems: {'🟢 ON' if (self.reentry_manager and self.config.get('re_entry_config', {}).get('sl_hunt_reentry_enabled', False)) else '🔴 OFF'}

*📈 PERFORMANCE*

• Daily Profit: +${self.risk_manager.daily_profit if self.risk_manager else 0.0:.2f}
• Daily Loss: -${abs(self.risk_manager.daily_loss) if self.risk_manager else 0.0:.2f}
• Win Rate: {self.risk_manager.get_win_rate() if self.risk_manager else 0.0:.1f}%

_Use /dashboard to return to main view_"""
            
            return status_text
            
        except Exception as e:
            return f"❌ Error getting status: {str(e)}"
    
    def show_open_trades_dashboard(self, message_id):
        """Show open trades with live PnL"""
        try:
            open_trades = self.trading_engine.get_open_trades() if self.trading_engine else []
            
            if not open_trades:
                text = "📭 <b>NO OPEN TRADES</b>\n\nNo active positions found."
                url = f"{self.base_url}/editMessageText"
                payload = {
                    "chat_id": self.chat_id,
                    "message_id": message_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
                requests.post(url, json=payload, timeout=10)
                return
            
            # Get live PnL data
            live_pnl_data = self.risk_manager.get_live_open_trades_pnl(
                self.trading_engine, self.mt5_client, self.pip_calculator
            ) if all([self.risk_manager, self.trading_engine, self.mt5_client, self.pip_calculator]) else {'trade_details': []}
            
            text = "📈 <b>OPEN TRADES</b>\n═══════════════\n\n"
            keyboard = []
            
            for trade in open_trades:
                # Find matching trade in live data
                trade_pnl = 0.0
                for td in live_pnl_data.get('trade_details', []):
                    if td.get('symbol') == trade.symbol and td.get('direction', '').upper() == trade.direction.upper():
                        trade_pnl = td.get('live_pnl', 0.0)
                        break
                
                pnl_text = self.risk_manager.format_pnl_value(trade_pnl) if self.risk_manager else f"${trade_pnl:.2f}"
                
                text += f"• {trade.symbol} {trade.direction.upper()}\n"
                text += f"  Entry: {trade.entry:.5f} | PnL: {pnl_text}\n"
                text += f"  SL: {trade.sl:.5f} | TP: {trade.tp:.5f}\n\n"
            
            # Add back to dashboard button
            keyboard.append([{"text": "🔙 BACK TO DASHBOARD", "callback_data": "dashboard_refresh"}])
            
            reply_markup = {"inline_keyboard": keyboard}
            
            url = f"{self.base_url}/editMessageText"
            payload = {
                "chat_id": self.chat_id,
                "message_id": message_id,
                "text": text,
                "reply_markup": reply_markup,
                "parse_mode": "HTML"
            }
            requests.post(url, json=payload, timeout=10)
            
        except Exception as e:
            self.logger.error(f"[OPEN-TRADES] Error showing open trades: {e}")



    def start_polling(self):
        """Start polling for Telegram commands"""
        if not self.polling_enabled:
            self.logger.warning("[POLLING] DISABLED - Polling is disabled due to Telegram webhook conflicts")
            self.logger.info("[POLLING] Bot is running in MANUAL COMMAND MODE - use /start to interact")
            return
        # Clear the stop event to allow polling
        self.polling_stop_event.clear()
        
        def poll_commands():
            offset = 0
            self.logger.debug(f"[POLLING-DEBUG] poll_commands() started, stop_event={self.polling_stop_event.is_set()}")
            self.logger.info("[POLLING] Starting polling loop...")
            cycle = 0
            error_count = 0  # FIX #5: Init error counter
            while not self.polling_stop_event.is_set():
                cycle += 1
                self.logger.debug(f"[POLLING-DEBUG] Cycle {cycle} starting...")
                try:
                    url = f"{self.base_url}/getUpdates?offset={offset}&timeout=30"
                    self.logger.debug(f"[POLLING-DEBUG] Making request to: {url[:80]}...")
                    self.logger.debug(f"[POLLING-CYCLE-{cycle}] Making request to Telegram...")
                    response = self.session.get(url, timeout=35)
                    self.logger.debug(f"[POLLING-DEBUG] Got response status={response.status_code}")
                    self.logger.debug(f"[POLLING-CYCLE-{cycle}] Got response: status={response.status_code}")
                    
                    # Handle non-200 responses first
                    if response.status_code == 409:
                        self.http409_count += 1
                        # Conflict - webhook is still active on Telegram server
                        self.logger.warning(f"[POLLING] HTTP 409 #{self.http409_count}: Webhook conflict - attempting recovery")
                        
                        # If too many 409s, disable polling and exit
                        if self.http409_count >= 5:
                            self.logger.error(f"[POLLING] ❌ HTTP 409 limit exceeded (5+ failures) - bot webhook is permanently conflicted")
                            self.logger.error(f"[POLLING] 📌 Solution: Contact @BotFather on Telegram, delete bot, create NEW bot")
                            self.logger.error(f"[POLLING] 📌 Update TELEGRAM_TOKEN in .env with new token")
                            self.polling_stop_event.set()
                            return
                        
                        try:
                            # Use POST to delete webhook with proper JSON parameter
                            delete_url = f"{self.base_url}/deleteWebhook"
                            resp = requests.post(delete_url, 
                                               json={"drop_pending_updates": True}, 
                                               timeout=10)
                            result = resp.json()
                            
                            if result.get("ok"):
                                self.logger.info(f"[POLLING] HTTP 409 Recovery: Webhook cleared")
                                self.http409_count = 0  # Reset counter on success
                            else:
                                self.logger.warning(f"[POLLING] HTTP 409 Recovery failed: {result.get('description', 'Unknown error')}")
                            
                            # Wait for propagation - 30 seconds for Telegram to process
                            self.logger.debug(f"[POLLING] Waiting 30 seconds for Telegram to clear webhook...")
                            time.sleep(30)
                        except Exception as e:
                            self.logger.error(f"[POLLING] HTTP 409 Recovery error: {e}")
                            time.sleep(30)
                        continue
                    elif response.status_code != 200:
                        self.logger.warning(f"[POLLING] Unexpected status code: {response.status_code}")
                        time.sleep(10)
                        continue
                    
                    # Process 200 response
                    error_count = 0  # FIX #5: Reset error count on success
                    data = response.json()
                    if not data.get("ok"):
                        self.logger.warning(f"[POLLING] Telegram API error: {data}")
                        time.sleep(10)
                        continue
                    
                    # Get updates and process them
                    updates = data.get("result", [])
                    
                    # CRITICAL DEBUG: Log how many updates received
                    if len(updates) > 0:
                        self.logger.info(f"[POLLING-UPDATES] 🔔 Received {len(updates)} update(s) in cycle {cycle}")
                    else:
                        self.logger.debug(f"[POLLING-CYCLE-{cycle}] No new updates (updates array empty)")
                    
                    for update in updates:
                        offset = update["update_id"] + 1
                        
                        # CRITICAL DEBUG: Log what type of update
                        self.logger.info(f"[POLLING-UPDATE] Processing update_id={update.get('update_id')}, keys={list(update.keys())}")
                        
                        # Handle callback queries (inline keyboard buttons)
                        if "callback_query" in update:
                            callback_query = update["callback_query"]
                            user_id = callback_query["from"]["id"]
                            callback_data = callback_query.get("data", "")
                            
                            # CRITICAL DEBUG: Log callback details
                            self.logger.info(f"[CALLBACK] 🔘 Button clicked! user_id={user_id}, data='{callback_data}'")
                            self.logger.info(f"[CALLBACK] Allowed user: {self.config['allowed_telegram_user']}, Match: {user_id == self.config['allowed_telegram_user']}")
                            
                            if user_id == self.config["allowed_telegram_user"]:
                                try:
                                    start_time = time.time()
                                    self.logger.info(f"[CALLBACK] ✅ Processing authorized callback: {callback_data}")
                                    
                                    self.handle_callback_query(callback_query)
                                    
                                    elapsed = time.time() - start_time
                                    self.logger.info(f"[CALLBACK] ✅ Completed in {elapsed:.2f}s")
                                    # NOTE: handle_callback_query already answers the callback - no redundant call needed
                                except Exception as e:
                                    self.logger.error(f"[CALLBACK] ❌ Error: {e}")
                                    print(f"Callback query error: {e}")
                                    import traceback
                                    traceback.print_exc()
                            else:
                                self.logger.warning(f"[CALLBACK] ❌ UNAUTHORIZED user {user_id} tried to use button")
                            continue
                        
                        if "message" in update and "text" in update["message"]:
                            message_data = update["message"]
                            user_id = message_data["from"]["id"]
                            text = message_data["text"].strip()
                            
                            self.logger.info(f"[TELEGRAM] 📨 Received message from user {user_id}: {text}")
                            sys.stdout.flush()
                            
                            if user_id == self.config["allowed_telegram_user"]:
                                # CRITICAL: Check if waiting for custom input
                                if self.menu_manager and hasattr(self.menu_manager, 'context'):
                                    try:
                                        context = self.menu_manager.context.get_context(user_id)
                                        self.logger.debug(f"[POLLING CUSTOM INPUT CHECK] Context type: {type(context)}, Context: {context}")
                                        waiting_for = context.get('waiting_for_input')
                                        self.logger.debug(f"[POLLING CUSTOM INPUT CHECK] Waiting for: {waiting_for}")
                                    except TypeError as te:
                                        self.logger.error(f"[POLLING] TypeError getting context: {te}")
                                        import traceback
                                        self.logger.error(f"[POLLING] Traceback:\n{traceback.format_exc()}")
                                        context = {}
                                        waiting_for = None
                                    
                                    if waiting_for:
                                        # Process custom input
                                        self.logger.info(f"[CUSTOM INPUT] Received value for {waiting_for}: {text}")
                                        self._process_custom_input(user_id, waiting_for, text)
                                        continue
                                    
                                    # [ZERO-TYPING UI] Interceptor
                                    # Check if text matches a Reply Keyboard button
                                    if text in REPLY_MENU_MAP:
                                        self.logger.info(f"[INTERCEPTOR] 🔄 Translating text '{text}' to callback")
                                        callback_data = REPLY_MENU_MAP[text]
                                        
                                        # Create synthetic callback query
                                        synthetic_callback = {
                                            "id": f"synthetic_{int(time.time()*1000)}",
                                            "from": message_data["from"],
                                            "message": message_data,
                                            "data": callback_data,
                                            "chat_instance": str(message_data["chat"]["id"]) if "chat" in message_data else "0"
                                        }
                                        
                                        self.handle_callback_query(synthetic_callback)
                                        continue
                                
                                command_parts = text.split()
                                if command_parts:
                                    command = command_parts[0]
                                    
                                    self.logger.debug(f"[TELEGRAM] ✅ Processing command: {command}")
                                    sys.stdout.flush()
                                    
                                    if command in self.command_handlers:
                                        try:
                                            self.logger.debug(f"[TELEGRAM] 🔄 Executing handler for: {command}")
                                            sys.stdout.flush()
                                            self.command_handlers[command](message_data)
                                            self.logger.info(f"[TELEGRAM] ✅ Command {command} executed successfully")
                                            sys.stdout.flush()
                                        except Exception as e:
                                            error_msg = f"❌ Error executing {command}: {str(e)}"
                                            self.send_message(error_msg)
                                            self.logger.error(f"[TELEGRAM] ❌ Command error: {e}")
                                            sys.stdout.flush()
                                    else:
                                        self.logger.debug(f"[TELEGRAM] ⚠️ Unknown command: {command}")
                                        sys.stdout.flush()
                            else:
                                self.logger.warning(f"[TELEGRAM] ❌ Unauthorized user: {user_id}")
                                sys.stdout.flush()
                
                except Exception as e:
                    self.logger.debug(f"[POLLING-DEBUG] EXCEPTION in cycle {cycle}: {type(e).__name__}: {str(e)}")
                    self.logger.error(f"[POLLING-ERROR-CYCLE-{cycle}] Telegram polling error: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    # FIX #5: Exponential backoff
                    error_count += 1
                    backoff = min(300, 5 * (2 ** (error_count - 1)))
                    self.logger.warning(f"[POLLING] Error count: {error_count}, retrying in {backoff}s...")
                    time.sleep(backoff)
            
            self.logger.debug(f"[POLLING-DEBUG] Loop exited, stop_event={self.polling_stop_event.is_set()}")
        
        try:
            thread = threading.Thread(target=poll_commands, daemon=True)
            thread.start()
            self.polling_thread = thread
            self.logger.info("SUCCESS: Telegram bot polling started")
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to start polling thread: {e}")
            import traceback
            traceback.print_exc()

    def stop_polling(self):
        """Stop the polling thread gracefully"""
        if self.polling_thread is not None:
            self.logger.info("[POLLING] Stopping polling thread...")
            self.polling_stop_event.set()
            # Wait for thread to finish (max 5 seconds)
            self.polling_thread.join(timeout=5)
            self.logger.info("[POLLING] Polling thread stopped")
            self.polling_thread = None

    def _cleanup_webhook_before_polling(self):
        """Ensure any existing webhook is deleted before polling starts"""
        try:
            self.logger.info("[POLLING-INIT] Cleaning up any existing webhooks...")
            
            # Step 1: Get current webhook info
            try:
                webhook_info_url = f"{self.base_url}/getWebhookInfo"
                response = requests.post(webhook_info_url, timeout=10)
                webhook_data = response.json()
                
                if webhook_data.get("ok"):
                    webhook_url = webhook_data.get("result", {}).get("url")
                    if webhook_url:
                        self.logger.warning(f"[POLLING-INIT] Found existing webhook: {webhook_url}")
                    else:
                        self.logger.info("[POLLING-INIT] No webhook found on Telegram servers")
            except Exception as e:
                self.logger.debug(f"[POLLING-INIT] Could not get webhook info: {e}")
            
            # Step 2: Delete any webhook
            try:
                delete_url = f"{self.base_url}/deleteWebhook"
                resp = requests.post(delete_url, 
                                   json={"drop_pending_updates": True}, 
                                   timeout=10)
                result = resp.json()
                if result.get("ok"):
                    self.logger.info("[POLLING-INIT] Webhook deleted successfully")
                else:
                    self.logger.warning(f"[POLLING-INIT] deleteWebhook API response: {result}")
            except Exception as e:
                self.logger.warning(f"[POLLING-INIT] Error deleting webhook: {e}")
            
            # Step 3: Wait for deletion to propagate
            self.logger.debug("[POLLING-INIT] Waiting 3 seconds for webhook deletion to propagate...")
            time.sleep(3)
            
            # Step 4: Verify deletion
            try:
                response = requests.post(webhook_info_url, timeout=10)
                webhook_data = response.json()
                if webhook_data.get("ok"):
                    webhook_url = webhook_data.get("result", {}).get("url")
                    if not webhook_url:
                        self.logger.info("[POLLING-INIT] ✅ Webhook cleanup verified - ready for polling")
                    else:
                        self.logger.warning(f"[POLLING-INIT] ⚠️ Webhook still exists after deletion: {webhook_url}")
            except Exception as e:
                self.logger.debug(f"[POLLING-INIT] Could not verify webhook deletion: {e}")
                
        except Exception as e:
            self.logger.error(f"[POLLING-INIT] Unexpected error in cleanup: {e}")

    # Timeframe Specific Logic Handlers
    def handle_toggle_timeframe(self, message):
        """Toggle timeframe specific logic"""
        try:
             # Logic to toggle
             # Handle dict message from menu system
             if isinstance(message, dict):
                 # Check if 'enabled' param is provided directly
                 if 'enabled' in message:
                     new_state = str(message['enabled']).lower() == 'true'
                 else:
                     # Toggle if no param
                     current = self.config.get("timeframe_specific_config", {}).get("enabled", False)
                     new_state = not current
             else:
                 # Standard toggle
                 current = self.config.get("timeframe_specific_config", {}).get("enabled", False)
                 new_state = not current
             
             if "timeframe_specific_config" not in self.config:
                 self.config["timeframe_specific_config"] = {}
             
             self.config["timeframe_specific_config"]["enabled"] = new_state
             self.config.save_config()
             
             state_str = "✅ ENABLED" if new_state else "❌ DISABLED"
             self.send_message(f"<b>Timeframe Specific Logic</b>\nStatus: {state_str}")
        except Exception as e:
             self.send_message(f"❌ Error toggling timeframe logic: {str(e)}")
             import traceback
             traceback.print_exc()

    def handle_view_logic_settings(self, message):
        """View logic settings"""
        try:
            config = self.config.get("timeframe_specific_config", {})
            enabled = config.get("enabled", False)
            msg = f"📊 <b>Timeframe Specific Logic</b>\nStatus: {'✅ ENABLED' if enabled else '❌ DISABLED'}\n\n"
            
            for logic in ["combinedlogic-1", "combinedlogic-2", "combinedlogic-3"]:
                logic_config = config.get(logic, {})
                lot_mult = logic_config.get("lot_multiplier", 1.0)
                sl_mult = logic_config.get("sl_multiplier", 1.0)
                window = logic_config.get("recovery_window_minutes", 30)
                
                msg += f"<b>{logic}</b>\n"
                msg += f"🔸 Lot Multiplier: {lot_mult}x\n"
                msg += f"🔸 SL Multiplier: {sl_mult}x\n"
                msg += f"🔸 Recovery Window: {window}m\n\n"
            
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Error viewing logic settings: {str(e)}")

    def handle_reset_timeframe_default(self, message):
        """Reset timeframe specific logic to defaults"""
        try:
            default_config = {
                "enabled": False,
                "combinedlogic-1": {"lot_multiplier": 1.0, "sl_multiplier": 1.0, "recovery_window_minutes": 30},
                "combinedlogic-2": {"lot_multiplier": 1.0, "sl_multiplier": 1.0, "recovery_window_minutes": 60},
                "combinedlogic-3": {"lot_multiplier": 1.5, "sl_multiplier": 1.2, "recovery_window_minutes": 120}
            }
            
            self.config["timeframe_specific_config"] = default_config
            self.config.save_config()
            
            self.send_message(f"✅ <b>Timeframe Logic Reset</b>\nSettings have been reset to default values.")
            
            # Show new settings
            self.handle_view_logic_settings(message)
            
        except Exception as e:
             self.send_message(f"❌ Error resetting timeframe logic: {str(e)}")

    def update_timeframe_logic_config(self, logic: str, param: str, value: float):
        """Update a specific parameter for a logic (for Fine Tune menu)"""
        try:
            if "timeframe_specific_config" not in self.config:
                self.config["timeframe_specific_config"] = {}
                
            if logic not in self.config["timeframe_specific_config"]:
                self.config["timeframe_specific_config"][logic] = {}
                
            self.config["timeframe_specific_config"][logic][param] = float(value)
            self.config.save_config()
            self.send_message(f"✅ Config updated: {logic} {param} = {value}")
            return True
        except Exception as e:
            print(f"Error updating timeframe config: {e}")
            return False

    def handle_set_sl1_1(self, update: Any, context: Any) -> None:
        """Placeholder for SL-1.1 Setup"""
        # Feature not fully requested in this task, but handler prevents crash
        self.send_message("Feature coming soon: SL-1.1 Setup")

    def handle_set_sl2_1(self, update: Any, context: Any) -> None:
        """Placeholder for SL-2.1 Setup"""
        self.send_message("Feature coming soon: SL-2.1 Setup")

    def handle_shield_command(self, update: Any, context: Any) -> None:
        """Handle /shield command for Reverse Shield v3.0 control"""
        if not self.check_auth(update): return
        
        args = context.args
        if not args:
            # Show Status
            rs_config = self.config.config.get("reverse_shield_config", {})
            status = "✅ ENABLED" if rs_config.get("enabled", False) else "❌ DISABLED"
            
            msg = f"🛡️ <b>REVERSE SHIELD SYSTEM (v3.0)</b>\n"
            msg += f"Status: <b>{status}</b>\n\n"
            
            try:
                msg += f"Recovery Level: {rs_config.get('recovery_threshold_percent', 0.70)*100}%\n"
                msg += f"Lot Multiplier: {rs_config.get('shield_lot_size_multiplier', 0.5)}x\n"
                msg += f"Smart Risk: {'ON' if rs_config.get('risk_integration', {}).get('enable_smart_adjustment') else 'OFF'}\n\n"
            except:
                pass

            msg += "<b>Commands:</b>\n"
            msg += "/shield on - Enable Shield System\n"
            msg += "/shield off - Disable Shield System\n"
            msg += "/shield status - detailed status"
            
            self.send_message(msg, parse_mode='HTML')
            return

        action = args[0].lower()
        
        if action == "on":
            self.config.config.setdefault("reverse_shield_config", {})["enabled"] = True
            self.config.save_config()
            self.send_message("🛡️ <b>Reverse Shield ENABLED</b>", parse_mode='HTML')
            
        elif action == "off":
            self.config.config.setdefault("reverse_shield_config", {})["enabled"] = False
            self.config.save_config()
            self.send_message("🛡️ <b>Reverse Shield DISABLED</b>\n(Active shields will continue until closed)", parse_mode='HTML')
        
        elif action == "status":
             self.handle_shield_command(update, context)
             
        else:
            self.send_message("Invalid command. Use /shield on|off")
