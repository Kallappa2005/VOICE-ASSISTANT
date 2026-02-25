# Handle voice output

"""
Text-to-Speech Handler
Converts text responses into voice output
"""

import pyttsx3
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class TextToSpeechHandler:
    """Handles text-to-speech conversion for voice feedback"""
    
    def __init__(self, rate=150, volume=1.0):
        """
        Initialize TTS engine
        
        Args:
            rate (int): Speech rate (words per minute)
            volume (float): Volume level (0.0 to 1.0)
        """
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Set voice (optional: change to female voice)
            voices = self.engine.getProperty('voices')
            # self.engine.setProperty('voice', voices[1].id)  # Uncomment for female voice
            
            logger.info("Text-to-Speech engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    
    def speak(self, text):
        """
        Convert text to speech
        
        Args:
            text (str): Text to speak
        """
        try:
            logger.info(f"Speaking: {text}")
            print(f"🔊 Assistant: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            print(f"❌ Failed to speak: {text}")
    
    def stop(self):
        """Stop current speech"""
        try:
            self.engine.stop()
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    def change_voice(self, voice_index=0):
        """
        Change voice
        
        Args:
            voice_index (int): Index of voice (0 for male, 1 for female typically)
        """
        try:
            voices = self.engine.getProperty('voices')
            if voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)
                logger.info(f"Voice changed to index {voice_index}")
        except Exception as e:
            logger.error(f"Error changing voice: {e}")
    
    def set_rate(self, rate):
        """
        Set speech rate
        
        Args:
            rate (int): Words per minute (default: 150)
        """
        try:
            self.engine.setProperty('rate', rate)
            logger.info(f"Speech rate set to {rate}")
        except Exception as e:
            logger.error(f"Error setting rate: {e}")