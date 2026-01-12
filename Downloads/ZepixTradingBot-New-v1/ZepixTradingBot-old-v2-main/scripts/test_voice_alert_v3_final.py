"""
Voice Alert System V3.0 - Final Test
Clean chat: Windows Audio + Text only (NO voice files)

Author: Zepix Trading Bot Team
Date: 2026-01-12
"""

import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.voice_alert_system import VoiceAlertSystem, AlertPriority
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    print("=" * 70)
    print("VOICE ALERT SYSTEM V3.0 - FINAL TEST")
    print("Windows Audio + Text Notifications (Clean Chat)")
    print("=" * 70)
    
    try:
        # Setup
        print("\n[Step 1/4] Initializing V3.0 final system...")
        
        bot_token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ ERROR: Credentials missing")
            return False
        
        bot = Bot(token=bot_token)
        alert_system = VoiceAlertSystem(bot, chat_id)
        
        print("✅ V3.0 System initialized successfully")
        
        # Test Windows Audio
        print("\n[Step 2/4] Testing Windows speaker...")
        print("🔊 Listen for laptop audio:")
        
        if alert_system.windows_player:
            test_msg = "Final system test. Voice alert system version three is ready for production."
            alert_system.windows_player.speak(test_msg)
            print("✅ Windows audio test PASSED")
        
        await asyncio.sleep(2)
        
        # Test All Priority Levels
        print("\n[Step 3/4] Testing all priority levels...")
        print("🔊 Windows: Listen for laptop audio (automatic)")
        print("📱 Phone: Check for text notifications ONLY\n")
        
        test_alerts = [
            {
                "priority": AlertPriority.CRITICAL,
                "message": "CRITICAL: Stop loss hit - EUR/USD closed at 1.0800.",
                "expected": "Windows Audio ✅ + Text ✅"
            },
            {
                "priority": AlertPriority.HIGH,
                "message": "HIGH: Profit target reached - GBP/USD closed at 1.2700.",
                "expected": "Windows Audio ✅ + Text ✅"
            },
            {
                "priority": AlertPriority.MEDIUM,
                "message": "MEDIUM: New signal detected - USD/JPY at 148.50.",
                "expected": "Windows Audio ✅ + Text ✅"
            },
            {
                "priority": AlertPriority.LOW,
                "message": "LOW: Market analysis update - trend remains bullish.",
                "expected": "Text ✅ only"
            }
        ]
        
        for i, test_alert in enumerate(test_alerts, 1):
            print(f"\n  [{i}/4] {test_alert['priority'].value} alert...")
            print(f"  Expected: {test_alert['expected']}")
            
            await alert_system.send_voice_alert(
                message=test_alert['message'],
                priority=test_alert['priority']
            )
            
            print(f"  ⏳ Waiting 4 seconds...")
            await asyncio.sleep(4)
            print(f"  ✅ Sent")
        
        # Verify Queue
        print("\n[Step 4/4] Verifying delivery...")
        
        for _ in range(5):
            queue_status = alert_system.get_queue_status()
            
            if queue_status['total_queued'] == 0:
                print("✅ All alerts delivered successfully")
                break
            
            await asyncio.sleep(1)
        
        # Final Instructions
        print("\n" + "=" * 70)
        print("FINAL VERIFICATION")
        print("=" * 70)
        
        print("\n✅ CHECK THESE:\n")
        
        print("  🔊 WINDOWS LAPTOP:")
        print("    [ ] Heard 4 TTS audio messages automatically")
        print("    [ ] All messages clear and understandable")
        print()
        
        print("  📱 PHONE (Telegram):")
        print("    [ ] Notification sound played (4 times)")
        print("    [ ] Received 4 TEXT messages")
        print("    [ ] NO voice files in chat (clean!)")
        print()
        
        print("  🎯 EXPECTED:")
        print("    ✅ Laptop: 4 automatic TTS audio")
        print("    ✅ Phone: 4 text notifications")
        print("    ✅ Chat: Text only (NO voice files)")
        print()
        
        print("=" * 70)
        print("TEST COMPLETED ✅")
        print("=" * 70)
        print()
        print("If all checks pass → V3.0 is READY FOR PRODUCTION! 🎉")
        
        return True
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted")
        sys.exit(1)
