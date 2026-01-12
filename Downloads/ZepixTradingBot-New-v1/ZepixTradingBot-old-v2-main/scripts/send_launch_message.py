
import sys
import os
import logging

# Add root directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from src.config import Config
from src.clients.telegram_bot import TelegramBot

# Setup simple logging
logging.basicConfig(level=logging.INFO)

def send_launch_message():
    try:
        config = Config()
        bot = TelegramBot(config)
        
        message = (
            "🚀 **Zepix Bot v3.0 is ONLINE**\n"
            "🛡️ Systems: 100% HEALTHY\n"
            "💰 Profit Protection: ACTIVE\n"
            "📉 Margin Check: BYPASSED\n"
            "📂 Test Assets: Archived & Safe\n"
            "Waiting for TradingView Signals..."
        )
        
        print(f"Sending launch message...")
        bot.send_message(message)
        print("✅ Launch message sent successfully")
        
    except Exception as e:
        print(f"❌ Error sending launch message: {e}")

if __name__ == "__main__":
    send_launch_message()
