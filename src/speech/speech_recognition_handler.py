"""
Speech Recognition Handler
Listens to user voice commands and converts to text
"""

import speech_recognition as sr
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class SpeechRecognitionHandler:
    """Handles speech recognition for voice input"""
    
    def __init__(self, language='en-IN', timeout=5, phrase_time_limit=10):
        """
        Initialize speech recognizer
        
        Args:
            language (str): Recognition language (en-IN for Indian English)
            timeout (int): Seconds to wait for speech to start
            phrase_time_limit (int): Maximum seconds for phrase
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        
        # Adjust for ambient noise
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
        logger.info("Speech Recognition Handler initialized")
    
    def listen(self):
        """
        Listen to microphone and convert speech to text
        
        Returns:
            str: Recognized text or None if failed
        """
        try:
            with sr.Microphone() as source:
                print("🎤 Listening...")
                logger.info("Listening for user input")
                
                # Adjust for ambient noise (only first time)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen to audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                print("🔄 Processing...")
                logger.info("Audio captured, processing...")
                
                # Recognize speech using Google
                text = self.recognizer.recognize_google(audio, language=self.language)
                
                logger.info(f"Recognized: {text}")
                print(f"👤 You said: {text}")
                
                return text.lower()
                
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            print("⏱️ No speech detected. Timeout.")
            return None
            
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            print("❓ Sorry, I didn't understand that.")
            return None
            
        except sr.RequestError as e:
            logger.error(f"API request error: {e}")
            print(f"❌ Speech recognition service error: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"❌ Error: {e}")
            return None
    
    def test_microphone(self):
        """Test if microphone is working"""
        try:
            with sr.Microphone() as source:
                print("🎤 Testing microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microphone is working!")
                logger.info("Microphone test successful")
                return True
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            logger.error(f"Microphone test failed: {e}")
            return False