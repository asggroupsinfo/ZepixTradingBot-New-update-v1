"""
Windows Audio Player Module
Direct TTS audio playback on Windows speakers using pyttsx3.

Features:
- Offline TTS (no internet required)
- Direct speaker output
- Works even if Telegram is closed
- Configurable voice rate and volume

Author: Zepix Trading Bot Team
Version: 1.0
Created: 2026-01-12
"""

import pyttsx3
import logging
from typing import Optional


class WindowsAudioPlayer:
    """Play TTS audio directly on Windows speakers."""
    
    def __init__(self, rate: int = 150, volume: float = 1.0):
        """
        Initialize Windows Audio Player configuration.
        
        Args:
            rate: Speech rate (words per minute), default 150
            volume: Volume level (0.0 to 1.0), default 1.0 (max)
        """
        self.logger = logging.getLogger(__name__)
        self.rate = rate
        self.volume = volume
        self.logger.info(f"WindowsAudioPlayer config | Rate: {rate} | Volume: {volume}")
    
    def speak(self, text: str) -> bool:
        """
        Play text as audio on Windows speakers.
        
        Creates a fresh engine instance for each call to ensure thread safety
        and prevent COM interface errors when called from async executors.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            self.logger.warning("Empty text provided, skipping")
            return False
        
        engine = None
        try:
            # Initialize engine locally for thread safety
            # pyttsx3.init() returns a reference to a singleton in some drivers,
            # but re-initializing in the new thread context is safer for COM.
            import pyttsx3
            engine = pyttsx3.init()
            
            # Configure engine
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)
            
            # Use default voice (usually Microsoft David/Zira)
            # We don't query voices here to save time and avoid stability issues
            
            self.logger.info(f"Playing audio: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # Queue and play
            engine.say(text)
            engine.runAndWait()
            
            self.logger.info("Audio playback completed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
            return False
        finally:
            # Cleanup
            if engine:
                try:
                    engine.stop()
                    del engine
                except:
                    pass
    
    def test_speaker(self) -> bool:
        """
        Test speaker with a simple message.
        
        Returns:
            True if test successful, False otherwise
        """
        test_message = "Windows audio system test. System is working."
        return self.speak(test_message)
    
    def cleanup(self):
        """No-op for V2 (engine is local)."""
        pass


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing WindowsAudioPlayer...")
    
    try:
        player = WindowsAudioPlayer(rate=160, volume=1.0)
        player.test_speaker()
        player.speak("This is a critical trading alert. Euro USD long position opened at 1.0850.")
        player.cleanup()
        print("✅ Test completed successfully")
    except Exception as e:
        print(f"❌ Test failed: {e}")
