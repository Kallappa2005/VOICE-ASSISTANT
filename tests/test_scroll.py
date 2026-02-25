"""
Test script for scroll functionality with interactive voice control
Run from root: python -m tests.test_scroll
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.browser_controller import BrowserController
from src.browser.navigation import Navigation
from src.automation.scroll_handler import ScrollHandler
from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.commands.command_parser import CommandParser

def test_scroll_functionality():
    """Test scrolling with voice commands"""
    
    print("=" * 70)
    print("📜 VOICE ASSISTANT - SCROLL FUNCTIONALITY TEST (Step 5.3)")
    print("=" * 70)
    
    # Initialize components
    tts = TextToSpeechHandler(rate=150)
    stt = SpeechRecognitionHandler()
    browser = BrowserController()
    parser = CommandParser()
    
    # Open browser
    print("\n📋 Opening Chrome Browser...")
    tts.speak("Opening Chrome browser")
    
    if not browser.open_chrome(start_url="https://www.google.com"):
        tts.speak("Failed to open browser")
        return
    
    tts.speak("Chrome browser is open")
    
    # Initialize handlers
    nav = Navigation(browser)
    scroll = ScrollHandler(browser)
    
    # Open a long page for scrolling test
    tts.speak("Opening Wikipedia for scroll test")
    print("\n🌐 Opening Wikipedia...")
    nav.goto_url("https://en.wikipedia.org/wiki/Python_(programming_language)")
    time.sleep(3)
    
    tts.speak("Page loaded. You can now try scroll commands.")
    print("✅ Page loaded\n")
    
    # Interactive loop
    print("💡 Try these commands:")
    print("   - 'scroll down'")
    print("   - 'scroll up'")
    print("   - 'go to top'")
    print("   - 'go to bottom'")
    print("   - 'scroll down a lot'")
    print("   - 'stop' to exit\n")
    
    max_commands = 5  # Limit for testing
    command_count = 0
    
    while command_count < max_commands:
        print(f"\n{'='*70}")
        print(f"🎤 Command {command_count + 1}/{max_commands} - Listening...")
        print(f"{'='*70}")
        
        # Listen for command
        command = stt.listen()
        
        if not command:
            tts.speak("I didn't hear anything. Try again.")
            continue
        
        # Stop command
        if 'stop' in command or 'exit' in command:
            tts.speak("Stopping test")
            break
        
        # Parse command
        parsed = parser.parse(command)
        intent = parsed['intent']
        params = parsed['params']
        
        # Execute command
        if intent == 'scroll_down':
            amount = params.get('amount', 'medium') if params else 'medium'
            tts.speak(f"Scrolling down")
            print(f"📜 Scrolling down ({amount})...")
            if scroll.scroll_down(amount):
                print("✅ Scrolled down")
                tts.speak("Done")
            else:
                print("❌ Scroll failed")
                tts.speak("Scroll failed")
        
        elif intent == 'scroll_up':
            amount = params.get('amount', 'medium') if params else 'medium'
            tts.speak(f"Scrolling up")
            print(f"📜 Scrolling up ({amount})...")
            if scroll.scroll_up(amount):
                print("✅ Scrolled up")
                tts.speak("Done")
            else:
                print("❌ Scroll failed")
                tts.speak("Scroll failed")
        
        elif intent == 'scroll_top':
            tts.speak("Going to top")
            print("⬆️ Scrolling to top...")
            if scroll.scroll_to_top():
                print("✅ At top of page")
                tts.speak("Now at top of page")
            else:
                print("❌ Scroll failed")
                tts.speak("Failed")
        
        elif intent == 'scroll_bottom':
            tts.speak("Going to bottom")
            print("⬇️ Scrolling to bottom...")
            if scroll.scroll_to_bottom():
                print("✅ At bottom of page")
                tts.speak("Now at bottom of page")
            else:
                print("❌ Scroll failed")
                tts.speak("Failed")
        
        else:
            tts.speak("That's not a scroll command. Try scroll up or scroll down.")
        
        command_count += 1
    
    # Cleanup
    print(f"\n{'='*70}")
    tts.speak("Test completed. Closing browser.")
    time.sleep(2)
    browser.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ Scroll Functionality Test Completed (Step 5.3)")
    print("=" * 70)

if __name__ == "__main__":
    test_scroll_functionality()