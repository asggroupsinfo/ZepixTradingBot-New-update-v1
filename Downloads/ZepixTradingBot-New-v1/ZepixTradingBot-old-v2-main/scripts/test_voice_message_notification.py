"""
Voice Message Notification Test
Test if voice messages trigger phone notification sound automatically.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram import Bot
from dotenv import load_dotenv
import pyttsx3

load_dotenv()

def create_voice_message(text: str, filename: str) -> str:
    """Create TTS voice message file."""
    print(f"🎤 Generating TTS audio: '{text}'...")
    
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    
    # Save to file
    engine.save_to_file(text, filename)
    engine.runAndWait()
    
    print(f"✅ Audio file created: {filename}")
    return filename

async def main():
    print("=" * 70)
    print("VOICE MESSAGE NOTIFICATION TEST")
    print("=" * 70)
    
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ ERROR: Credentials missing")
        return
    
    bot = Bot(token=bot_token)
    
    print("\n🔊 TESTING: Voice message notification sound\n")
    
    # Test messages
    test_messages = [
        {
            "text": "Critical alert. This is test number one. Euro USD stop loss hit at 1.0800.",
            "priority": "CRITICAL",
            "emoji": "🚨"
        },
        {
            "text": "High priority alert. This is test number two. Profit target reached on GBP USD.",
            "priority": "HIGH",
            "emoji": "🔴"
        },
        {
            "text": "Medium priority alert. This is test number three. New trading signal detected.",
            "priority": "MEDIUM",
            "emoji": "🟡"
        }
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n[Test {i}/3] Sending {msg['priority']} voice message...")
        
        # Generate audio file
        audio_filename = f"voice_alert_{msg['priority'].lower()}.mp3"
        create_voice_message(msg['text'], audio_filename)
        
        # Send voice message
        try:
            with open(audio_filename, 'rb') as audio_file:
                bot.send_voice(
                    chat_id=chat_id,
                    voice=audio_file,
                    caption=f"{msg['emoji']} **{msg['priority']} ALERT**\n\nVoice notification test {i}/3",
                    parse_mode='Markdown'
                )
            
            print(f"✅ Voice message sent successfully")
            print(f"📱 CHECK PHONE: Did notification sound play?")
            
            # Cleanup
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
            
            # Wait between messages
            if i < 3:
                print(f"⏳ Waiting 5 seconds before next message...")
                await asyncio.sleep(5)
        
        except Exception as e:
            print(f"❌ Error sending voice message: {e}")
    
    print("\n" + "=" * 70)
    print("VOICE MESSAGE TEST COMPLETED")
    print("=" * 70)
    
    print("\n📋 VERIFICATION CHECKLIST:\n")
    print("📱 Phone Check:")
    print("  1. Did you hear notification sound when messages arrived? [YES/NO]")
    print("  2. Can you see 3 voice messages in chat? [YES/NO]")
    print("  3. When you TAP a voice message, does it play audio? [YES/NO]")
    print("  4. Does voice message auto-play on notification? [YES/NO]")
    
    print("\n🔊 Expected Behavior:")
    print("  ✅ Notification sound when message arrives")
    print("  ✅ Voice message visible in chat (with play button)")
    print("  ✅ Audio plays when you tap the message")
    print("  ⚠️  Auto-play: Depends on phone settings")
    
    print("\n⏳ Check your phone and report results!")

if __name__ == "__main__":
    asyncio.run(main())
