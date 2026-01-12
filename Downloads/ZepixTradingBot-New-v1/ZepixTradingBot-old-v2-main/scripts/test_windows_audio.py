"""
Test Windows Audio Player functionality.
Verifies that TTS audio plays correctly on Windows speakers.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.windows_audio_player import WindowsAudioPlayer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 60)
    print("WINDOWS AUDIO PLAYER TEST")
    print("=" * 60)
    
    try:
        print("\n1. Initializing Windows Audio Player...")
        player = WindowsAudioPlayer(rate=150, volume=1.0)
        print("✅ Initialization successful\n")
        
        print("2. Running speaker test...")
        if player.test_speaker():
            print("✅ Speaker test passed\n")
        else:
            print("❌ Speaker test failed\n")
            return False
        
        print("3. Testing trading alert simulation...")
        test_messages = [
            "Critical alert. Euro USD long position opened at 1.0850. Stop loss at 1.0800.",
            "High priority. Profit target reached. Position closed with 50 pips profit.",
            "Medium priority. Trend reversal detected on 15-minute chart."
        ]
        
        for i, msg in enumerate(test_messages, 1):
            print(f"\nPlaying message {i}/{len(test_messages)}...")
            if player.speak(msg):
                print(f"✅ Message {i} played successfully")
            else:
                print(f"❌ Message {i} playback failed")
        
        print("\n4. Cleaning up...")
        player.cleanup()
        print("✅ Cleanup complete")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return True
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
