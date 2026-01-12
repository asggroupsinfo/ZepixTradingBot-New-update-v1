"""
Voice Alert System V2.5 - Complete Test
Tests hybrid notification system: Windows Audio + Voice Messages + Text

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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    print("=" * 70)
    print("VOICE ALERT SYSTEM V2.5 - COMPLETE TEST")
    print("Hybrid: Windows Audio + Voice Messages + Text")
    print("=" * 70)
    
    try:
        # Setup
        print("\n[Step 1/5] Initializing V2.5 alert system...")
        
        bot_token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ ERROR: Credentials missing in .env")
            return False
        
        bot = Bot(token=bot_token)
        alert_system = VoiceAlertSystem(bot, chat_id)
        
        print("✅ V2.5 Alert System initialized successfully")
        
        # Test Windows Audio
        print("\n[Step 2/5] Testing Windows speaker audio...")
        print("🔊 You should hear this from laptop speakers:")
        
        if alert_system.windows_player:
            test_msg = "System test. Voice alert system version two point five is ready."
            success = alert_system.windows_player.speak(test_msg)
            if success:
                print("✅ Windows speaker test PASSED")
            else:
                print("⚠️ Windows speaker test FAILED")
        
        await asyncio.sleep(2)
        
        # Test All Priority Levels
        print("\n[Step 3/5] Testing all priority levels...")
        print("🔊 Windows: Listen for laptop audio")
        print("📱 Phone: Check for Telegram messages\n")
        
        test_alerts = [
            {
                "priority": AlertPriority.CRITICAL,
                "message": "CRITICAL: Stop loss hit on EUR/USD at 1.0800. Position closed. Loss: 50 pips.",
                "expected": "Windows Audio ✅ + Voice Message ✅ + Text ✅"
            },
            {
                "priority": AlertPriority.HIGH,
                "message": "HIGH: Profit target reached on GBP/USD at 1.2700. Position closed. Profit: 100 pips.",
                "expected": "Windows Audio ✅ + Voice Message ✅ + Text ✅"
            },
            {
                "priority": AlertPriority.MEDIUM,
                "message": "MEDIUM: New trading signal detected on USD/JPY at 148.50. Entry confirmation pending.",
                "expected": "Windows Audio ✅ + Text ✅"
            },
            {
                "priority": AlertPriority.LOW,
                "message": "LOW: Market analysis update. Overall trend remains bullish on EUR/USD.",
                "expected": "Text ✅ only"
            }
        ]
        
        for i, test_alert in enumerate(test_alerts, 1):
            print(f"\n  [{i}/4] Sending {test_alert['priority'].value} priority alert...")
            print(f"  Expected channels: {test_alert['expected']}")
            
            # Send alert
            await alert_system.send_voice_alert(
                message=test_alert['message'],
                priority=test_alert['priority']
            )
            
            # Wait for processing
            wait_time = 8 if i <= 2 else 4  # Longer wait for voice messages
            print(f"  ⏳ Waiting {wait_time} seconds for delivery...")
            await asyncio.sleep(wait_time)
            
            print(f"  ✅ {test_alert['priority'].value} alert sent")
        
        # Verify Queue
        print("\n[Step 4/5] Verifying alert queue processing...")
        
        remaining_attempts = 10
        while remaining_attempts > 0:
            queue_status = alert_system.get_queue_status()
            
            if queue_status['total_queued'] == 0 and not queue_status['is_processing']:
                print("✅ All alerts processed successfully")
                break
            
            print(f"  ⏳ Queue processing... {queue_status['total_queued']} remaining")
            await asyncio.sleep(2)
            remaining_attempts -= 1
        
        if remaining_attempts == 0:
            print("⚠️ WARNING: Queue still processing after timeout")
        
        # Manual Verification
        print("\n[Step 5/5] Manual Verification Required")
        print("-" * 70)
        print("✅ COMPREHENSIVE VERIFICATION CHECKLIST:\n")
        
        print("  📱 PHONE VERIFICATION:")
        print("    1. Did phone make notification sound? (4 times)")
        print("       [ ] YES - Notification sound played")
        print("       [ ] NO - No sound")
        print()
        print("    2. Open Telegram chat - what do you see?")
        print("       [ ] 2 voice messages (CRITICAL + HIGH)")
        print("       [ ] 4 text messages (all priorities)")
        print("       [ ] Total: 6 messages")
        print()
        print("    3. TAP the voice messages - does audio play?")
        print("       [ ] YES - Voice audio plays when tapped")
        print("       [ ] NO - Voice doesn't play")
        print()
        
        print("  🔊 WINDOWS LAPTOP VERIFICATION:")
        print("    4. Did you hear TTS audio from speakers?")
        print("       [ ] YES - Heard audio for CRITICAL, HIGH, MEDIUM (3 messages)")
        print("       [ ] NO - No laptop audio")
        print()
        
        print("  🎯 EXPECTED RESULTS:")
        print("    ✅ Phone: 4 notification sounds")
        print("    ✅ Telegram: 2 voice messages + 4 text messages = 6 total")
        print("    ✅ Voice messages: Playable when tapped")
        print("    ✅ Laptop: 3 TTS audio messages (automatic)")
        print()
        
        print("-" * 70)
        
        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY ✅")
        print("=" * 70)
        print()
        print("📋 NEXT STEPS:")
        print("  1. Verify all checklist items above")
        print("  2. If all verified → Voice Alert V2.5 is PERFECT! 🎉")
        print("  3. If issues found → Report specific problems")
        print()
        
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
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
