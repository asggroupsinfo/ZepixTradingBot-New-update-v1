"""
Telegram Notification Diagnostic Test
Debug why phone is not making sound for notifications.
"""

import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    print("=" * 70)
    print("TELEGRAM NOTIFICATION DIAGNOSTIC TEST")
    print("=" * 70)
    
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ ERROR: Credentials missing")
        return
    
    bot = Bot(token=bot_token)
    
    print("\n🔍 TESTING DIFFERENT NOTIFICATION METHODS:\n")
    
    # Test 1: Basic message (default settings)
    print("[Test 1/5] Sending basic message (default settings)...")
    bot.send_message(
        chat_id=chat_id,
        text="🔔 Test 1: Basic message (default notification)"
    )
    print("✅ Sent. Check phone: Did it make sound?")
    await asyncio.sleep(3)
    
    # Test 2: Explicit notification enabled
    print("\n[Test 2/5] Sending message with explicit notification enabled...")
    bot.send_message(
        chat_id=chat_id,
        text="🔔 Test 2: Notification explicitly ENABLED (disable_notification=False)",
        disable_notification=False
    )
    print("✅ Sent. Check phone: Did it make sound?")
    await asyncio.sleep(3)
    
    # Test 3: Silent message (for comparison)
    print("\n[Test 3/5] Sending SILENT message (should NOT make sound)...")
    bot.send_message(
        chat_id=chat_id,
        text="🔕 Test 3: SILENT message (disable_notification=True)",
        disable_notification=True
    )
    print("✅ Sent. Check phone: Should be SILENT (no sound)")
    await asyncio.sleep(3)
    
    # Test 4: Message with sound emoji
    print("\n[Test 4/5] Sending message with sound-related formatting...")
    bot.send_message(
        chat_id=chat_id,
        text="🔊🚨 **URGENT ALERT** 🚨🔊\n\nTest 4: Does emoji/formatting help?",
        parse_mode='Markdown',
        disable_notification=False
    )
    print("✅ Sent. Check phone: Did it make sound?")
    await asyncio.sleep(3)
    
    # Test 5: Voice message (for comparison)
    print("\n[Test 5/5] Sending actual VOICE message (TTS audio)...")
    print("⚠️ This WILL create a voice file in chat (for testing only)")
    
    # Generate simple TTS
    try:
        import pyttsx3
        import io
        
        engine = pyttsx3.init()
        # Save to file temporarily
        test_audio_path = "test_notification.mp3"
        engine.save_to_file("Test five. This is a voice message test. You should hear this on your phone speakers.", test_audio_path)
        engine.runAndWait()
        
        # Send voice
        with open(test_audio_path, 'rb') as audio_file:
            bot.send_voice(
                chat_id=chat_id,
                voice=audio_file,
                caption="🎤 Test 5: Voice message (you should hear this on phone)"
            )
        
        # Cleanup
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
        
        print("✅ Sent. Check phone: Can you HEAR the voice message?")
    except Exception as e:
        print(f"⚠️ Voice test skipped: {e}")
    
    await asyncio.sleep(3)
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC TEST COMPLETE")
    print("=" * 70)
    
    print("\n📋 USER VERIFICATION REQUIRED:")
    print("\nPlease check your phone and answer:\n")
    print("Test 1 (Basic message): Did phone make sound? [YES/NO]")
    print("Test 2 (Explicit notification): Did phone make sound? [YES/NO]")
    print("Test 3 (Silent): Phone should be SILENT [Confirm: YES/NO]")
    print("Test 4 (Formatted): Did phone make sound? [YES/NO]")
    print("Test 5 (Voice message): Can you HEAR audio from speakers? [YES/NO]")
    
    print("\n⚠️ IMPORTANT:")
    print("If NONE of the tests made sound (except voice message),")
    print("the issue is with PHONE SETTINGS, not our code.")
    
    print("\n📱 Check these on your phone:")
    print("1. Telegram > Settings > Notifications > Enable sound")
    print("2. Phone Settings > Apps > Telegram > Notifications > Allow sound")
    print("3. Phone is NOT in Do Not Disturb mode")
    print("4. Phone volume is UP")
    print("\n⏳ Waiting for you to check all 5 tests on your phone...")
    print("Press Ctrl+C when done checking.")
    
    try:
        await asyncio.sleep(120)  # Wait 2 minutes for user to check
    except KeyboardInterrupt:
        print("\n\n✅ Test completed by user")

if __name__ == "__main__":
    asyncio.run(main())
