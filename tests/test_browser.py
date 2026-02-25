"""
Test script for browser module
Run from root: python -m tests.test_browser
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.browser_controller import BrowserController
from src.speech.text_to_speech_handler import TextToSpeechHandler

def test_open_chrome():
    """Test opening Chrome browser with voice feedback"""
    
    print("=" * 60)
    print("🌐 VOICE ASSISTANT - BROWSER MODULE TEST (Step 5.1)")
    print("=" * 60)
    
    # Initialize handlers
    tts = TextToSpeechHandler(rate=150)
    browser = BrowserController()
    
    # Test 1: Open Chrome
    print("\n📋 Test 1: Opening Chrome Browser")
    tts.speak("Opening Chrome browser. Please wait.")
    
    success = browser.open_chrome()
    
    if success:
        print("✅ Chrome browser opened successfully!")
        tts.speak("Chrome browser is now open")
        
        # Keep browser open for 5 seconds
        print("⏳ Browser will remain open for 5 seconds...")
        time.sleep(5)
        
        # Test 2: Check if browser is open
        print("\n📋 Test 2: Checking browser status")
        if browser.is_open():
            print(f"✅ Browser status: OPEN")
            print(f"📄 Current URL: {browser.get_current_url()}")
            tts.speak("Browser status check passed")
        
        # Test 3: Close browser
        print("\n📋 Test 3: Closing browser")
        tts.speak("Now closing the browser")
        
        if browser.close_browser():
            print("✅ Browser closed successfully!")
            tts.speak("Browser closed successfully")
        else:
            print("❌ Failed to close browser")
            tts.speak("Failed to close browser")
    else:
        print("❌ Failed to open Chrome browser")
        tts.speak("Failed to open Chrome browser. Please check if Chrome is installed.")
    
    print("\n" + "=" * 60)
    print("✅ Browser Module Test Completed (Step 5.1)")
    print("=" * 60)

if __name__ == "__main__":
    test_open_chrome()