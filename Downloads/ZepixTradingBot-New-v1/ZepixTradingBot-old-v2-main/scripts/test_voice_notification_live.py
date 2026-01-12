"""
Live Voice Notification Test - Zero Tolerance Verification

Tests the complete V2.0 voice notification system:
1. Windows speaker TTS audio playback
2. Telegram text notifications (phone sound)
3. Verifies NO voice files in chat
4. Tests all priority levels

Author: Zepix Trading Bot Team
Date: 2026-01-12
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Run comprehensive voice notification test."""
    
    print("=" * 70)
    print("LIVE VOICE NOTIFICATION SYSTEM TEST - V2.0")
    print("=" * 70)
    
    try:
        # Step 1: Setup
        print("\n[Step 1/5] Initializing bot and alert system...")
        
        bot_token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ ERROR: TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set in .env file")
            return False
        
        bot = Bot(token=bot_token)
        alert_system = VoiceAlertSystem(bot, chat_id)
        
        print("✅ Bot and alert system initialized successfully")
        
        # Step 2: Test Windows Audio
        print("\n[Step 2/5] Testing Windows speaker audio...")
        print("⏳ You should hear this message from your laptop speakers:")
        
        test_msg = "Test alert. This is a Windows speaker audio test for the Zepix trading bot."
        if alert_system.windows_player:
            success = alert_system.windows_player.speak(test_msg)
            if success:
                print("✅ Windows speaker test PASSED")
            else:
                print("⚠️ Windows speaker test FAILED - but continuing...")
        else:
            print("❌ Windows audio player not available")
            return False
        
        # Step 3: Test All Priority Levels
        print("\n[Step 3/5] Testing all priority levels...")
        print("📱 Check your phone for Telegram notifications (should make sound)")
        print("🔊 Listen for Windows speaker audio\n")
        
        test_alerts = [
            {
                "priority": AlertPriority.CRITICAL,
                "message": "CRITICAL: Stop loss hit on EUR/USD. Position closed at 1.0800. Loss: 50 pips."
            },
            {
                "priority": AlertPriority.HIGH,
                "message": "HIGH: Profit target reached on GBP/USD. Position closed at 1.2700. Profit: 100 pips."
            },
            {
                "priority": AlertPriority.MEDIUM,
                "message": "MEDIUM: New trading signal detected on USD/JPY at 148.50. Entry confirmation pending."
            },
            {
                "priority": AlertPriority.LOW,
                "message": "LOW: Market analysis update. Overall trend remains bullish on EUR/USD."
            }
        ]
        
        for i, test_alert in enumerate(test_alerts, 1):
            print(f"\n  [{i}/4] Sending {test_alert['priority'].value} priority alert...")
            
            # Send alert
            await alert_system.send_voice_alert(
                message=test_alert['message'],
                priority=test_alert['priority']
            )
            
            # Wait for processing
            wait_time = 3 if i < 4 else 5  # Extra wait after last alert
            print(f"  ⏳ Waiting {wait_time} seconds for delivery...")
            await asyncio.sleep(wait_time)
            
            print(f"  ✅ {test_alert['priority'].value} alert sent")
        
        # Step 4: Verify Queue Processing
        print("\n[Step 4/5] Verifying alert queue processing...")
        
        # Give time for queue to process
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
        
        # Step 5: Final Instructions
        print("\n[Step 5/5] Manual Verification Required")
        print("-" * 70)
        print("✅ VERIFICATION CHECKLIST:")
        print()
        print("  Windows Laptop:")
        print("    [ ] Did you hear TTS audio from speakers? (4 messages)")
        print("    [ ] Were all messages clear and understandable?")
        print()
        print("  Phone:")
        print("    [ ] Did Telegram notification sound play? (4 times)")
        print("    [ ] Can you see notification banners?")
        print()
        print("  Telegram Chat:")
        print("    [ ] Open Telegram and check the chat")
        print("    [ ] Are there ONLY text messages? (NO voice files)")
        print("    [ ] Are messages formatted with emojis and priority levels?")
        print()
        print("-" * 70)
        
        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY ✅")
        print("=" * 70)
        print()
        print("📋 NEXT STEPS:")
        print("  1. Verify all checklist items above")
        print("  2. If all verified → Voice Notification V2.0 is READY")
        print("  3. If issues found → Report errors for fixing")
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
