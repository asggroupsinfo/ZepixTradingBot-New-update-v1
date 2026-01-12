import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config
from src.clients.telegram_bot import TelegramBot
from src.modules.voice_alert_system import VoiceAlertSystem, AlertPriority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LiveVoiceTest")

async def main():
    logger.info("🚀 Starting Live Voice Alert Test...")
    
    # 1. Load Real Configuration
    try:
        config = Config()
        logger.info("✅ Configuration loaded.")
    except Exception as e:
        logger.error(f"❌ Failed to load config: {e}")
        return

    # 2. Initialize Telegram Bot
    try:
        bot = TelegramBot(config)
        logger.info("✅ TelegramBot initialized.")
    except Exception as e:
        logger.error(f"❌ Failed to init TelegramBot: {e}")
        return

    # 3. Initialize Voice System
    chat_id = bot.chat_id
    if not chat_id:
        logger.error("❌ No Chat ID found in config/env. Cannot send alert.")
        return
        
    logger.info(f"🎯 Target Chat ID: {chat_id}")
    voice_system = VoiceAlertSystem(bot, str(chat_id))

    # 4. Text Message First
    bot.send_message("🔔 **Zepix Bot:** Starting Live Voice Test...")

    # 5. Send Voice Alert
    message = "This is a live test of the Zepix Trading Bot Voice Alert System. Access granted."
    logger.info(f"🔊 Sending Voice Alert: '{message}'")
    
    try:
        await voice_system.send_voice_alert(message, priority=AlertPriority.CRITICAL)
        logger.info("✅ Voice alert QUEUED. Waiting for delivery...")
        
        # Wait for async queue processing (Voice generation takes time)
        await asyncio.sleep(15)
        
        bot.send_message("✅ **Test Complete:** You should have received a voice note.")
    except Exception as e:
        logger.error(f"❌ Failed to send voice alert: {e}")
        bot.send_message(f"❌ **Test Failed:** {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
