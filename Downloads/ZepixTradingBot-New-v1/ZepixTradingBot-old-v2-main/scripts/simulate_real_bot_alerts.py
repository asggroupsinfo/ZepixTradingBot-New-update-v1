"""
REAL BOT ALERT SIMULATION
-------------------------
Simulates the exact alert sequence a real trading session would generate.
Verifies that Windows Voice Alert System V3.0 picks up these alerts and speaks them.

Scenarios:
1. Bot Start
2. Market Analysis (Low Priority)
3. Pattern Detection (Medium)
4. Critical Entry (High)
5. Take Profit (High)
6. Stop Loss (Critical)
7. Session Summary (Low)
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.voice_alert_system import VoiceAlertSystem, AlertPriority
from telegram import Bot
from dotenv import load_dotenv

# Setup simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_simulation():
    load_dotenv()
    
    print("\n" + "="*60)
    print("🤖 ZEPIX BOT - REAL ALERT SIMULATION MODE")
    print("="*60)
    print("Testing: Windows Voice V3.0 + Telegram Text Integration")
    print("-" * 60)

    # 1. Initialize Real Alert System
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Credentials missing!")
        return

    try:
        bot = Bot(token=bot_token)
        alert_system = VoiceAlertSystem(bot, chat_id)
        print("✅ Alert System Initialized (Connected to Windows Speakers)")
    except Exception as e:
        print(f"❌ Init failed: {e}")
        return

    # 2. Simulate Trading Session
    events = [
        {
            "time": "09:30:00",
            "type": "BOT_START",
            "priority": AlertPriority.LOW,
            "msg": "🤖 Zepix Bot Started directly on Port 80. Waiting for signals..."
        },
        {
            "time": "09:30:05",
            "type": "MARKET_SCAN",
            "priority": AlertPriority.LOW,
            "msg": "📊 Market Scan: EUR/USD trend is BULLISH. Volatility is normal."
        },
        {
            "time": "09:35:00",
            "type": "PATTERN_DETECTED",
            "priority": AlertPriority.MEDIUM,
            "msg": "⚠️ Potential Setup: Double Bottom detected on GBP/USD M15 timeframe."
        },
        {
            "time": "09:35:10",
            "type": "TRADE_ENTRY",
            "priority": AlertPriority.HIGH,
            "msg": "🚀 ENTRY SIGNAL: LONG GBP/USD at 1.2550. SL: 1.2530, TP: 1.2580."
        },
        {
            "time": "09:45:00",
            "type": "TAKE_PROFIT",
            "priority": AlertPriority.CRITICAL,  # Critical because it's money!
            "msg": "💰 TAKE PROFIT HIT: GBP/USD closed at 1.2580. Profit: +30 pips. Great trade!"
        },
        {
            "time": "10:00:00",
            "type": "STOP_LOSS",
            "priority": AlertPriority.CRITICAL,
            "msg": "🛑 STOP LOSS HIT: EUR/JPY closed at 155.20. Loss: -20 pips. Managing risk."
        },
        {
            "time": "10:05:00",
            "type": "SESSION_END",
            "priority": AlertPriority.LOW,
            "msg": "🏁 Session Ended. Total Trades: 2. Net PnL: +10 pips. Shutting down."
        }
    ]

    print("\n🚀 STARTING SIMULATION SEQUENCE...\n")
    print("👂 Listen to your Windows Laptop Speakers!")
    print("📱 Check Telegram for Text Notifications\n")

    for event in events:
        print(f"⏰ {event['time']} | [{event['type']}] -> Sending Alert...")
        
        # This is exactly how the real bot sends alerts
        success = await alert_system.send_voice_alert(
            message=event['msg'],
            priority=event['priority']
        )
        
        if success:
            print(f"   ✅ Alert Sent: {event['msg'][:40]}...")
        else:
            print("   ❌ Alert Failed!")
            
        # Realistic pause between events to let audio finish
        await asyncio.sleep(6)  

    print("\n" + "="*60)
    print("✅ SIMULATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_simulation())
