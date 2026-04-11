"""
Voice Output Module
Handles text-to-speech for AI responses
"""

import pyttsx3
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class VoiceOutput:
    """Text-to-speech output for AI assistant"""
    
    def __init__(self, rate=210):
        """Initialize text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice
            voices = self.engine.getProperty('voices')
            # Use female voice if available (usually index 1)
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
            
            # Set speech rate (default is usually around 200)
            self.engine.setProperty('rate', rate)
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.9)
            
            logger.info(f"Voice output initialized (rate={rate})")
            
        except Exception as e:
            logger.error(f"Error initializing voice output: {e}")
            self.engine = None
    
    def speak(self, text):
        """
        Speak text out loud
        
        Args:
            text: Text to speak
        """
        if not self.engine:
            logger.warning("Voice engine not available")
            return
        
        try:
            # Clean text for speech (remove markdown, special chars)
            clean_text = self._clean_for_speech(text)
            
            logger.info(f"Speaking: {clean_text[:50]}...")
            
            self.engine.say(clean_text)
            self.engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error speaking: {e}")
    
    def _clean_for_speech(self, text):
        """
        Clean text for better speech output
        
        Args:
            text: Raw text
        
        Returns:
            str: Cleaned text
        """
        # Remove markdown
        text = text.replace('**', '')
        text = text.replace('__', '')
        text = text.replace('`', '')
        
        # Remove emojis
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Limit length for speech (don't speak too long)
        if len(text) > 500:
            text = text[:500] + "... Check the terminal for full details."
        
        return text
    
    def speak_greeting(self):
        """Speak greeting message"""
        self.speak("Hello! I'm ready. How can I help you?")
    
    def speak_goodbye(self):
        """Speak goodbye message"""
        self.speak("Goodbye! Have a great day!")