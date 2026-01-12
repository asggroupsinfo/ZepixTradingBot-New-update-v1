"""
Fine-Tune Menu Handler - Zero-Typing Telegram Controls
Provides complete button-based control for all Fine-Tune settings.
COMPATIBLE VERSION: Uses requests-based API matching TelegramBot.
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FineTuneMenuHandler:
    """
    Telegram menu handler for Fine-Tune Settings
    Compatible with Zepix Trading Bot v2 request-based architecture
    """
    
    def __init__(self, bot, profit_protection_mgr, sl_reduction_mgr):
        """
        Initialize menu handler
        
        Args:
            bot: TelegramBot instance (requests-based)
            profit_protection_mgr: ProfitProtectionManager instance
            sl_reduction_mgr: SLReductionOptimizer instance
        """
        self.bot = bot
        self.pp_mgr = profit_protection_mgr
        self.sl_mgr = sl_reduction_mgr
        
        logger.info("✅ FineTuneMenuHandler initialized (Compatible Mode)")
    
    def _btn(self, text: str, callback_data: str) -> Dict[str, str]:
        """Helper to create inline keyboard button dict"""
        return {"text": text, "callback_data": callback_data}
    
    def _create_keyboard(self, rows: list) -> Dict[str, list]:
        """Helper to create inline keyboard dict"""
        return {"inline_keyboard": rows}

    # ==================== MAIN MENU ====================
    
    def show_fine_tune_menu(self, user_id: int, message_id: Optional[int] = None) -> None:
        """Show main Fine-Tune settings menu"""
        
        keyboard_rows = [
            [self._btn("💰 Profit Protection", "ft_profit_protection")],
            [self._btn("📉 SL Reduction", "ft_sl_reduction")],
            [self._btn("🔍 Recovery Windows", "ft_recovery_windows_edit")],
            [self._btn("🤖 Autonomous Dashboard", "ft_autonomous_dashboard")],
            [self._btn("📊 View All Settings", "ft_view_all")],
            [self._btn("🏠 Back to Main Menu", "menu_main")]
        ]
        
        message = """
⚡ <b>FINE-TUNE SETTINGS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

Configure advanced trading parameters for optimal performance.

<b>Available Settings:</b>

💰 <b>Profit Protection</b>
   Control when SL Hunt recovery is allowed based on accumulated profits

📉 <b>SL Reduction</b>
   Optimize stop loss sizes across TP Continuation levels

🔍 <b>Recovery Windows</b>
   View symbol-specific recovery timeout settings

Select a setting to configure:
        """
        
        self._send_or_edit_message(
            message_id=message_id,
            text=message,
            keyboard=self._create_keyboard(keyboard_rows)
        )
    
    # ==================== PROFIT PROTECTION MENU ====================
    
    def show_profit_protection_menu(self, user_id: int, message_id: Optional[int] = None) -> None:
        """Show Profit Protection mode selection menu"""
        
        if not self.pp_mgr:
            self._send_error(user_id, "Profit Protection Manager not initialized")
            return

        current_settings = self.pp_mgr.get_current_settings()
        current_mode = current_settings.get("mode", "BALANCED")
        current_mult = current_settings.get("multiplier", 6.0)
        
        keyboard_rows = []
        
        # Mode selection buttons
        all_modes = current_settings.get("all_modes", {}) # Needs pp_mgr update or assumption
        # Fallback if all_modes not returned in settings
        if not all_modes:
             all_modes = self.pp_mgr.MODES if hasattr(self.pp_mgr, "MODES") else {}

        for mode_key, mode_data in all_modes.items():
            emoji = mode_data.get("emoji", "")
            mult = mode_data.get("multiplier", 0)
            
            # Add checkmark if current
            check = " ✓" if mode_key == current_mode else ""
            label = f"{emoji} {mode_key.title()} ({mult}x){check}"
            
            keyboard_rows.append([self._btn(label, f"pp_mode_{mode_key}")])
        
        # Order type toggles
        order_a_status = "ON ✅" if current_settings.get("order_a_enabled", True) else "OFF ❌"
        order_b_status = "ON ✅" if current_settings.get("order_b_enabled", True) else "OFF ❌"
        
        keyboard_rows.append([self._btn(f"📝 Order A Protection [{order_a_status}]", "pp_toggle_a")])
        keyboard_rows.append([self._btn(f"📝 Order B Protection [{order_b_status}]", "pp_toggle_b")])
        
        # Additional options
        keyboard_rows.append([self._btn("📊 View Current Stats", "pp_stats")])
        keyboard_rows.append([self._btn("📖 Detailed Guide", "pp_guide")])
        keyboard_rows.append([self._btn("🏠 Back", "fine_tune_menu")])
        
        message = f"""
💰 <b>PROFIT PROTECTION</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current Mode:</b> {current_settings.get('emoji','')} {current_mode}
<b>Multiplier:</b> {current_mult}x
<b>Min Threshold:</b> ${current_settings.get('min_threshold',0)}

<b>How it works:</b>
Recovery allowed when:
<code>Chain Profit &gt; (Loss × Multiplier)</code>

<b>Example:</b> With {current_mult}x multiplier
• Chain has $120 profit
• SL loss would be $10
• Required: $10 × {current_mult} = ${current_mult * 10}
• Result: ✅ Recovery allowed

<b>Select Protection Mode:</b>
        """
        
        self._send_or_edit_message(
            message_id=message_id,
            text=message,
            keyboard=self._create_keyboard(keyboard_rows)
        )
    
    def show_profit_protection_stats(self, user_id: int, message_id: Optional[int] = None) -> None:
        """Show current profit protection statistics"""
        
        settings = self.pp_mgr.get_current_settings()
        all_modes = settings.get("all_modes", self.pp_mgr.MODES)
        
        comparison = []
        for mode_name, mode_data in all_modes.items():
            check = "✓" if mode_name == settings.get("mode") else " "
            comparison.append(
                f"{check} {mode_data.get('emoji','')} <b>{mode_name}</b>\n"
                f"   Multiplier: {mode_data.get('multiplier')}x\n"
                f"   Min Profit: ${mode_data.get('min_profit_threshold')}\n"
                f"   {mode_data.get('description','')}"
            )
        
        message = f"""
📊 <b>PROFIT PROTECTION STATS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current Settings:</b>
• Mode: {settings.get('emoji','')} {settings.get('mode')}
• Multiplier: {settings.get('multiplier')}x
• Min Threshold: ${settings.get('min_threshold')}
• Order A: {'ON ✅' if settings.get('order_a_enabled') else 'OFF ❌'}
• Order B: {'ON ✅' if settings.get('order_b_enabled') else 'OFF ❌'}

<b>All Modes:</b>
{chr(10).join(comparison)}
        """
        
        self._send_or_edit_message(
            message_id=message_id,
            text=message,
            keyboard=self._create_keyboard([[self._btn("🏠 Back", "profit_protection_menu")]])
        )
    
    def show_profit_protection_guide(self, user_id: int, message_id: Optional[int] = None) -> None:
         # ... guide text matches previous ...
         guide = """
📖 <b>PROFIT PROTECTION GUIDE</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Purpose:</b>
Prevent risking large accumulated profits for small recovery attempts.

<b>⚙️ How It Works:</b>
1. <b>Calculate Total Profit:</b> Sum of all closed + open profitable orders in chain
2. <b>Check Multiplier Rule:</b> Total Profit &gt; (Potential Loss × Multiplier)
3. <b>Decision:</b>
   • ✅ Allowed: Profit is safe, attempt recovery
   • ❌ Blocked: Profit too valuable, skip recovery

<b>💡 Mode Selection:</b>
⚡ <b>Aggressive (3.5x)</b>: More recoveries, higher risk
⚖️ <b>Balanced (6.0x)</b>: Recommended
🛡️ <b>Conservative (9.0x)</b>: Fewer recoveries, protect profit
🔒 <b>Very Conservative (15.0x)</b>: Maximum safety
         """
         self._send_or_edit_message(
            message_id=message_id,
            text=guide,
            keyboard=self._create_keyboard([[self._btn("🏠 Back to Menu", "profit_protection_menu")]])
        )

    # ==================== SL REDUCTION MENU ====================
    
    def show_sl_reduction_menu(self, user_id: int, message_id: Optional[int] = None) -> None:
        if not self.sl_mgr:
            self._send_error(user_id, "SL Reduction Manager not initialized")
            return

        current_settings = self.sl_mgr.get_current_settings()
        current_strategy = current_settings.get("strategy", "BALANCED")
        
        keyboard_rows = []
        
        all_strategies = current_settings.get("all_strategies", self.sl_mgr.STRATEGIES)
        for strategy_key, strategy_data in all_strategies.items():
            emoji = strategy_data.get("emoji", "")
            
            if strategy_key == "ADAPTIVE":
                label = f"{emoji} {strategy_key.title()}"
            else:
                percent = strategy_data.get("reduction_percent", 0)
                label = f"{emoji} {strategy_key.title()} ({percent}%)"
            
            if strategy_key == current_strategy:
                label += " ✓"
            
            keyboard_rows.append([self._btn(label, f"slr_strategy_{strategy_key}")])
        
        keyboard_rows.append([self._btn("📊 View Reduction Table", "slr_table")])
        keyboard_rows.append([self._btn("📖 Detailed Guide", "slr_guide")])
        keyboard_rows.append([self._btn("🏠 Back", "fine_tune_menu")])
        
        if current_strategy == "ADAPTIVE":
            percent_info = f"Symbol-Specific (Default: {current_settings.get('default_percent', 30)}%)"
        else:
            percent_info = f"{current_settings.get('reduction_percent', 30)}%"
        
        message = f"""
📉 <b>SL REDUCTION OPTIMIZER</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current Strategy:</b> {current_settings.get('emoji','')} {current_strategy}
<b>Reduction:</b> {percent_info}

<b>How it works:</b>
Each TP continuation level reduces SL by the configured percentage.

<b>Select Strategy:</b>
        """
        
        self._send_or_edit_message(
            message_id=message_id,
            text=message,
            keyboard=self._create_keyboard(keyboard_rows)
        )
    
    def show_adaptive_symbol_settings(self, user_id: int, page: int = 0, message_id: Optional[int] = None) -> None:
        current_settings = self.sl_mgr.get_current_settings()
        symbol_settings = current_settings.get("symbol_settings", {})
        
        symbols_per_page = 6
        all_symbols = sorted(symbol_settings.keys())
        total_pages = (len(all_symbols) + symbols_per_page - 1) // symbols_per_page
        start_idx = page * symbols_per_page
        end_idx = start_idx + symbols_per_page
        symbols_page = all_symbols[start_idx:end_idx]
        
        keyboard_rows = []
        for symbol in symbols_page:
            percent = symbol_settings[symbol].get("reduction_percent", 30)
            keyboard_rows.append([
                self._btn("⬇️", f"slr_dec_{symbol}_{page}"),
                self._btn(f"{symbol}: {percent}%", f"slr_info_{symbol}"),
                self._btn("⬆️", f"slr_inc_{symbol}_{page}")
            ])
            
        nav_buttons = []
        if page > 0:
            nav_buttons.append(self._btn("⬅️ Previous", f"slr_page_{page-1}"))
        if end_idx < len(all_symbols):
            nav_buttons.append(self._btn("Next ➡️", f"slr_page_{page+1}"))
        if nav_buttons:
            keyboard_rows.append(nav_buttons)
            
        keyboard_rows.append([self._btn("📖 Symbol Guide", "slr_symbol_guide")])
        keyboard_rows.append([self._btn("🏠 Back", "sl_reduction_menu")])
        
        message = f"""
🎯 <b>ADAPTIVE SYMBOL SETTINGS</b>
━━━━━━━━━━━━━━━━━━━━━━━━
<b>Page {page + 1} of {max(1, total_pages)}</b>

Use ⬇️⬆️ to adjust reduction percentage for each symbol.
Default: {current_settings.get('default_percent', 30)}%
Range: 10% - 50%
        """
        self._send_or_edit_message(message_id=message_id, text=message, keyboard=self._create_keyboard(keyboard_rows))

    def show_recovery_windows_info(self, user_id: int, message_id: Optional[int] = None) -> None:
        """Show recovery window information"""
        from src.managers.recovery_window_monitor import RecoveryWindowMonitor
        
        windows = getattr(RecoveryWindowMonitor, 'RECOVERY_WINDOWS', {})
        default = getattr(RecoveryWindowMonitor, 'DEFAULT_RECOVERY_WINDOW', 30)
        
        if not windows:
            # Fallback display if not importable
             message = "⚠️ Settings check currently unavailable"
        else:
            high_vol = [f"• {s}: {m}m" for s,m in windows.items() if m <= 20][:8]
            med_vol = [f"• {s}: {m}m" for s,m in windows.items() if 20 < m <= 35][:8]
            
            message = f"""
🔍 <b>RECOVERY WINDOWS</b>
━━━━━━━━━━━━━━━━━━━━━━━━
<b>⚡ High Volatility:</b>
{chr(10).join(high_vol) if high_vol else "None"}

<b>⚖️ Medium Volatility:</b>
{chr(10).join(med_vol) if med_vol else "None"}

<b>Default:</b> {default} minutes

<b>Note:</b> Bot monitors continuously and acts immediately. Window is timeout only.
            """
        
        self._send_or_edit_message(
            message_id=message_id,
            text=message,
            keyboard=self._create_keyboard([[self._btn("🏠 Back", "fine_tune_menu")]])
        )

    # Alias for method name compatibility
    show_recovery_windows = show_recovery_windows_info
    
    # ==================== RECOVERY WINDOWS EDIT ====================
    
    def show_recovery_windows_edit(self, user_id: int, page: int = 0, message_id: Optional[int] = None) -> None:
        """
        Show recovery windows with edit capability (⬇⬆ buttons)
        Similar to adaptive symbol settings interface
        """
        try:
            # Get recovery windows
            windows = self._get_recovery_windows()
            
            # Pagination
            symbols_per_page = 6
            all_symbols = sorted(windows.keys())
            total_pages = (len(all_symbols) + symbols_per_page - 1) // symbols_per_page
            start_idx = page * symbols_per_page
            end_idx = start_idx + symbols_per_page
            symbols_page = all_symbols[start_idx:end_idx]
            
            keyboard_rows = []
            
            # Symbol adjustment buttons
            for symbol in symbols_page:
                window_min = windows.get(symbol, 30)
                keyboard_rows.append([
                    self._btn("⬇", f"rw_dec_{symbol}_{page}"),
                    self._btn(f"{symbol}: {window_min}m", f"rw_info_{symbol}"),
                    self._btn("⬆", f"rw_inc_{symbol}_{page}")
                ])
            
            # Pagination buttons
            nav_buttons = []
            if page > 0:
                nav_buttons.append(self._btn("⬅ Previous", f"rw_page_{page-1}"))
            if end_idx < len(all_symbols):
                nav_buttons.append(self._btn("Next ➡", f"rw_page_{page+1}"))
            
            if nav_buttons:
                keyboard_rows.append(nav_buttons)
            
            # Additional options
            keyboard_rows.append([self._btn("📖 Window Guide", "rw_guide")])
            keyboard_rows.append([self._btn("🏠 Back", "fine_tune_menu")])
            
            message = f"""
🔍 <b>RECOVERY WINDOWS</b>
━━━━━━━━━━━━━━━━━━━━━━━━
<b>Page {page + 1} of {max(1, total_pages)}</b>

Adjust maximum wait time for SL Hunt recovery per symbol.

<b>How it works:</b>
Bot monitors price continuously. Window = timeout limit.

<b>Range:</b> 5 - 60 minutes
<b>⬇</b> Decrease by 5 min
<b>⬆</b> Increase by 5 min
            """
            
            self._send_or_edit_message(
                message_id=message_id,
                text=message,
                keyboard=self._create_keyboard(keyboard_rows)
            )
            
            logger.info(f"Recovery Windows Edit shown (Page {page+1})")
            
        except Exception as e:
            logger.error(f"Error showing recovery windows edit: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _get_recovery_windows(self) -> dict:
        """
        Get recovery windows from RecoveryWindowMonitor or config
        
        Returns:
            dict: {symbol: window_minutes}
        """
        try:
            # Try to get from autonomous system manager
            if hasattr(self.bot, 'autonomous_system_manager'):
                asm = self.bot.autonomous_system_manager
                if hasattr(asm, 'recovery_monitor') and asm.recovery_monitor:
                    monitor = asm.recovery_monitor
                    if hasattr(monitor, 'symbol_windows'):
                        return monitor.symbol_windows.copy()
            
            # Try from config
            if hasattr(self.bot, 'config'):
                recovery_windows = self.bot.config.get("recovery_windows", {})
                if recovery_windows:
                    return recovery_windows
            
            # Fallback to default windows
            return self._get_default_recovery_windows()
            
        except Exception as e:
            logger.error(f"Error getting recovery windows: {str(e)}")
            return self._get_default_recovery_windows()
    
    def _get_default_recovery_windows(self) -> dict:
        """Get default recovery windows for all major symbols"""
        return {
            # HIGH VOLATILITY - Short Windows (10-20 min)
            "XAUUSD": 15, "BTCUSD": 12, "XAGUSD": 18,
            "ETHUSD": 15,
            
            # MEDIUM-HIGH VOLATILITY (20-25 min)
            "GBPJPY": 20, "GBPUSD": 22, "AUDJPY": 20, "NZDJPY": 20,
            
            # MEDIUM VOLATILITY (25-35 min)
            "EURUSD": 30, "USDJPY": 28, "AUDUSD": 30,
            "NZDUSD": 30, "USDCAD": 28, "EURJPY": 25, "EURGBP": 30,
            
            # LOW VOLATILITY (35-50 min)
            "USDCHF": 35, "EURCHF": 40, "AUDNZD": 40,
            "AUDCAD": 35, "EURCAD": 35, "GBPAUD": 30, "GBPNZD": 30,
            
            # EXOTIC PAIRS (45-60 min)
            "USDZAR": 50, "USDTRY": 45, "USDMXN": 50,
            "USDSEK": 45, "USDNOK": 45, "USDDKK": 50,
            "USDPLN": 45, "USDHUF": 50
        }
    
    def _update_recovery_window(self, symbol: str, new_window: int) -> bool:
        """
        Update recovery window for a specific symbol
        
        Args:
            symbol: Trading symbol
            new_window: New window duration in minutes
        
        Returns:
            bool: True if successful
        """
        try:
            # Update in RecoveryWindowMonitor if available
            if hasattr(self.bot, 'autonomous_system_manager'):
                asm = self.bot.autonomous_system_manager
                if hasattr(asm, 'recovery_monitor') and asm.recovery_monitor:
                    monitor = asm.recovery_monitor
                    if hasattr(monitor, 'update_symbol_window'):
                        monitor.update_symbol_window(symbol, new_window)
                    elif hasattr(monitor, 'symbol_windows'):
                        # Direct update if method doesn't exist
                        monitor.symbol_windows[symbol] = new_window
            
            # Persist to config
            if hasattr(self.bot, 'config'):
                self.bot.config.update_nested(f"recovery_windows.{symbol}", new_window)
                self.bot.config.save()
            
            logger.info(f"✅ Recovery window updated: {symbol} → {new_window} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Error updating recovery window: {str(e)}")
            return False
    
    def show_recovery_window_guide(self, user_id: int, message_id: Optional[int] = None) -> None:
        """Show recovery window guide/help"""
        guide = """
📖 <b>RECOVERY WINDOWS GUIDE</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Purpose:</b>
Set maximum wait time for SL Hunt price recovery per symbol.

<b>⚙ How It Works:</b>
1. <b>SL Hit:</b> Trade hits stop loss
2. <b>Monitor Start:</b> Bot starts watching price
3. <b>Price Check:</b> Every 1 second, checks if price recovered
4. <b>Immediate Action:</b> If recovered, places order instantly
5. <b>Timeout:</b> If window expires, stops monitoring

<b>💡 Window Settings:</b>
⚡ <b>Short (10-20 min)</b>: Fast-moving pairs (XAUUSD, BTCUSD)
⚖ <b>Medium (25-35 min)</b>: Major forex pairs (EURUSD, USDJPY)
🛡 <b>Long (35-60 min)</b>: Stable pairs (USDCHF, Exotics)

<b>🔧 Adjustment Tips:</b>
• More volatile = shorter window
• Trending market = shorter window
• Choppy market = longer window

<b>Range:</b> 5 - 60 minutes
        """
        
        self._send_or_edit_message(
            message_id=message_id,
            text=guide,
            keyboard=self._create_keyboard([[self._btn("🏠 Back", "recovery_windows_edit")]])
        )
    
    def handle_recovery_window_callback(self, callback_query: dict) -> None:
        """Handle recovery window adjustment callbacks"""
        data = callback_query.get("data")
        user_id = callback_query.get("from", {}).get("id")
        message_id = callback_query.get("message", {}).get("message_id")
        
        if not data:
            return
        
        try:
            if data.startswith("rw_inc_") or data.startswith("rw_dec_"):
                # Parse callback data
                parts = data.split("_")
                action = parts[1]  # "inc" or "dec"
                symbol = parts[2]
                page = int(parts[3]) if len(parts) > 3 else 0
                
                # Get current window
                windows = self._get_recovery_windows()
                current = windows.get(symbol, 30)
                
                # Adjust by 5 minutes
                new_window = current + 5 if action == "inc" else current - 5
                
                # Validate range (5-60 minutes)
                if 5 <= new_window <= 60:
                    success = self._update_recovery_window(symbol, new_window)
                    if success:
                        # Send temporary notification (if bot supports answer_callback_query)
                        if hasattr(self.bot, 'answer_callback_query'):
                            self.bot.answer_callback_query(
                                callback_query.get("id"),
                                text=f"{symbol}: {current}m → {new_window}m"
                            )
                    # Refresh menu
                    self.show_recovery_windows_edit(user_id, page, message_id)
                else:
                    # Out of range
                    if hasattr(self.bot, 'answer_callback_query'):
                        self.bot.answer_callback_query(
                            callback_query.get("id"),
                            text=f"❌ Range limit: 5-60 minutes",
                            show_alert=True
                        )
            
            elif data.startswith("rw_page_"):
                page = int(data.replace("rw_page_", ""))
                self.show_recovery_windows_edit(user_id, page, message_id)
            
            elif data == "rw_guide":
                self.show_recovery_window_guide(user_id, message_id)
            
            elif data == "recovery_windows_edit":
                self.show_recovery_windows_edit(user_id, 0, message_id)
                
        except Exception as e:
            logger.error(f"Error handling recovery window callback: {str(e)}")
            import traceback
            traceback.print_exc()

    # ==================== HANDLERS ====================

    def handle_profit_protection_callback(self, callback_query: dict) -> None:
        data = callback_query.get("data")
        user_id = callback_query.get("from", {}).get("id")
        message_id = callback_query.get("message", {}).get("message_id")
        
        if not data: return

        if data.startswith("pp_mode_"):
            mode = data.replace("pp_mode_", "").upper()
            self.pp_mgr.switch_mode(mode)
            self.show_profit_protection_menu(user_id, message_id)
        
        elif data == "pp_toggle_a":
            self.pp_mgr.toggle_order_type("A")
            self.show_profit_protection_menu(user_id, message_id)
            
        elif data == "pp_toggle_b":
            self.pp_mgr.toggle_order_type("B")
            self.show_profit_protection_menu(user_id, message_id)
            
        elif data == "pp_stats":
            self.show_profit_protection_stats(user_id, message_id)
            
        elif data == "pp_guide":
            self.show_profit_protection_guide(user_id, message_id)

    def handle_sl_reduction_callback(self, callback_query: dict) -> None:
        data = callback_query.get("data")
        user_id = callback_query.get("from", {}).get("id")
        message_id = callback_query.get("message", {}).get("message_id")
        
        if not data: return

        if data.startswith("slr_strategy_"):
            strategy = data.replace("slr_strategy_", "").upper()
            success = self.sl_mgr.switch_strategy(strategy)
            if success and strategy == "ADAPTIVE":
                self.show_adaptive_symbol_settings(user_id, 0, message_id)
            else:
                self.show_sl_reduction_menu(user_id, message_id)
                
        elif data.startswith("slr_inc_") or data.startswith("slr_dec_"):
            parts = data.split("_")
            action = parts[1]
            symbol = parts[2]
            page = int(parts[3]) if len(parts) > 3 else 0
            
            settings = self.sl_mgr.get_current_settings()
            current = settings.get("symbol_settings", {}).get(symbol, {}).get("reduction_percent", 30)
            new_val = current + 1 if action == "inc" else current - 1
            
            if 10 <= new_val <= 50:
                self.sl_mgr.update_adaptive_symbol(symbol, new_val)
                self.show_adaptive_symbol_settings(user_id, page, message_id)
                
        elif data.startswith("slr_page_"):
            page = int(data.replace("slr_page_", ""))
            self.show_adaptive_symbol_settings(user_id, page, message_id)
            
        elif data == "slr_table":
            # Just show guide for now as table logic is complex for this patch
            self.show_sl_reduction_menu(user_id, message_id)
            
        elif data == "slr_guide":
            # Reuse similar guide logic
            guide = "📖 <b>SL REDUCTION GUIDE</b>\n\nOptimizes stop loss sizes.\nAggressive: 40%\nBalanced: 30%\nConservative: 20%"
            self._send_or_edit_message(message_id=message_id, text=guide, keyboard=self._create_keyboard([[self._btn("🏠 Back", "sl_reduction_menu")]]))

    # ==================== HELPER ====================
    
    def _send_or_edit_message(self, text: str, keyboard: dict, message_id: Optional[int] = None) -> None:
        try:
            if message_id:
                self.bot.edit_message(
                    text=text,
                    message_id=message_id,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                self.bot.send_message(
                    message=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Error sending/editing message: {e}")
            
    def _send_error(self, user_id, error_text):
        try:
            self.bot.send_message(message=f"❌ Error: {error_text}")
        except:
            pass
