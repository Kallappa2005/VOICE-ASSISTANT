"""
Test script for speech module
Run from root: python -m tests.test_speech
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler

def test_speech_module():
    """Test the speech input/output module"""
    
    print("=" * 50)
    print("🎤 VOICE ASSISTANT - SPEECH MODULE TEST")
    print("=" * 50)
    
    # Initialize handlers
    tts = TextToSpeechHandler(rate=150)
    stt = SpeechRecognitionHandler()
    
    # Test microphone
    tts.speak("Testing microphone. Please wait.")
    if not stt.test_microphone():
        tts.speak("Microphone test failed. Please check your microphone.")
        return
    
    # Test conversation
    tts.speak("Hello! I am your voice assistant. Speech module is ready.")
    tts.speak("Please say something. I am listening.")
    
    # Listen for command
    command = stt.listen()
    
    if command:
        tts.speak(f"You said: {command}")
        tts.speak("Speech recognition is working perfectly!")
    else:
        tts.speak("I could not hear you properly. Please try again.")
    
    print("\n✅ Speech module test completed!")

if __name__ == "__main__":
    test_speech_module()