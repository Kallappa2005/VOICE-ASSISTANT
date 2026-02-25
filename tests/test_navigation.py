"""
Test script for navigation module with interactive voice control
Run from root: python -m tests.test_navigation
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.browser_controller import BrowserController
from src.browser.navigation import Navigation
from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.commands.command_parser import CommandParser

def test_interactive_navigation():
    """Test interactive navigation with voice commands"""
    
    print("=" * 70)
    print("🌐 VOICE ASSISTANT - INTERACTIVE NAVIGATION TEST (Step 5.2)")
    print("=" * 70)
    
    # Initialize components
    tts = TextToSpeechHandler(rate=150)
    stt = SpeechRecognitionHandler()
    browser = BrowserController()
    parser = CommandParser()
    
    # Open browser first
    print("\n📋 Opening Chrome Browser...")
    tts.speak("Opening Chrome browser. Please wait.")
    
    if not browser.open_chrome():
        tts.speak("Failed to open browser")
        return
    
    tts.speak("Chrome browser is now open")
    print("✅ Browser opened successfully")
    
    # Initialize navigation
    nav = Navigation(browser)
    
    # Interactive loop
    tts.speak("What would you like me to do? You can say open YouTube, go to any website, or search for something.")
    
    max_commands = 3  # Limit for testing
    command_count = 0
    
    while command_count < max_commands:
        print(f"\n{'='*70}")
        print(f"🎤 Command {command_count + 1}/{max_commands} - Listening...")
        print("💡 Try: 'open youtube', 'go to reva.edu.in', 'search for python'")
        print(f"{'='*70}")
        
        # Listen for command
        command = stt.listen()
        
        if not command:
            tts.speak("I didn't hear anything. Please try again.")
            continue
        
        # Stop commands
        if 'stop' in command or 'exit' in command or 'close browser' in command:
            tts.speak("Closing browser. Goodbye!")
            break
        
        # Parse command
        parsed = parser.parse(command)
        intent = parsed['intent']
        params = parsed['params']
        
        # Execute command
        if intent == 'navigate':
            site = params['site']
            tts.speak(f"Opening {site}. Please wait.")
            print(f"\n🌐 Navigating to: {site}")
            
            success, url = nav.open_website(site)
            
            if success:
                time.sleep(2)  # Wait for page to settle
                page_info = nav.get_page_info()
                print(f"✅ Opened: {page_info['title']}")
                tts.speak(f"{site} is now open. What's next?")
            else:
                print(f"❌ Failed to open: {site}")
                tts.speak(f"Sorry, I couldn't open {site}. Please try another website.")
        
        elif intent == 'search':
            query = params['query']
            tts.speak(f"Searching for {query}")
            print(f"\n🔍 Searching: {query}")
            
            if nav.search_google(query):
                time.sleep(2)
                print(f"✅ Search completed")
                tts.speak("Search results are ready. What would you like to do next?")
            else:
                print(f"❌ Search failed")
                tts.speak("Sorry, search failed. Please try again.")
        
        else:
            tts.speak("I didn't understand that command. Please try again.")
        
        command_count += 1
    
    # Close browser
    print(f"\n{'='*70}")
    print("🔚 Test session ending...")
    tts.speak("Test completed. Closing browser now.")
    time.sleep(2)
    browser.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ Interactive Navigation Test Completed (Step 5.2)")
    print("=" * 70)

if __name__ == "__main__":
    test_interactive_navigation()