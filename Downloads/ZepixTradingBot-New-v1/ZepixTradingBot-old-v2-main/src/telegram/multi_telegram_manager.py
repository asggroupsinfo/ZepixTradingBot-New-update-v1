from typing import Dict, Any, Optional
import logging
from src.modules.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)

class MultiTelegramManager:
    """
    Manages multiple Telegram bots for specialized functions:
    1. Controller Bot: Commands and Admin
    2. Notification Bot: Trade Alerts
    3. Analytics Bot: Reports
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Load tokens
        self.main_token = config.get("telegram_token")
        self.controller_token = config.get("telegram_controller_token")
        self.notification_token = config.get("telegram_notification_token")
        self.analytics_token = config.get("telegram_analytics_token")
        
        self.chat_id = config.get("telegram_chat_id")
        
        # Initialize bots
        # Fallback to main bot if specific token logic is not ready or missing
        self.main_bot = TelegramBot(self.main_token) if self.main_token else None
        
        self.controller_bot = TelegramBot(self.controller_token) if self.controller_token else self.main_bot
        self.notification_bot = TelegramBot(self.notification_token) if self.notification_token else self.main_bot
        self.analytics_bot = TelegramBot(self.analytics_token) if self.analytics_token else self.main_bot
        
        logger.info("MultiTelegramManager initialized")
        
        # Log active configuration
        if self.controller_token:
            logger.info("✅ Controller Bot Active")
        else:
            logger.info("⚠️ Controller Bot using Main Token (Fallback)")
            
        if self.notification_token:
            logger.info("✅ Notification Bot Active")
        else:
            logger.info("⚠️ Notification Bot using Main Token (Fallback)")
            
        if self.analytics_token:
            logger.info("✅ Analytics Bot Active")
        else:
            logger.info("⚠️ Analytics Bot using Main Token (Fallback)")

    def route_message(self, message_type: str, content: str, parse_mode: str = "Markdown"):
        """
        Routes message to appropriate bot based on type.
        
        Args:
            message_type: 'command', 'alert', 'report', 'broadcast'
            content: Message text
        """
        if not content:
            return

        try:
            if message_type == "command":
                # Responses to commands go via Controller
                if self.controller_bot:
                    self.controller_bot.send_message(content)
                    
            elif message_type == "alert":
                # Trade alerts go via Notification bot
                if self.notification_bot:
                    self.notification_bot.send_message(content)
                    
            elif message_type == "report":
                # Analytics reports go via Analytics bot
                if self.analytics_bot:
                    self.analytics_bot.send_message(content)
                    
            elif message_type == "broadcast":
                # Send to ALL bots
                bots = [self.controller_bot, self.notification_bot, self.analytics_bot]
                # Filter None and duplicates
                unique_bots = list(set([b for b in bots if b]))
                
                for bot in unique_bots:
                    try:
                        bot.send_message(content)
                    except Exception as e:
                        logger.error(f"Broadcast failed for a bot: {e}")
                        
            else:
                # Default to main/controller
                if self.controller_bot:
                    self.controller_bot.send_message(content)
                    
        except Exception as e:
            logger.error(f"Failed to route message ({message_type}): {e}")
            # Emergency fallback: try main bot if different
            if self.main_bot and self.main_bot != self.controller_bot:
                try:
                    self.main_bot.send_message(f"⚠️ ROUTING ERROR: {content}")
                except:
                    pass

    def send_alert(self, message: str):
        """Helper for trade alerts"""
        self.route_message("alert", message)

    def send_report(self, message: str):
        """Helper for reports"""
        self.route_message("report", message)
        
    def send_admin_message(self, message: str):
        """Helper for admin/system messages"""
        self.route_message("command", message)
