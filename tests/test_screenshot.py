"""
Test script for screenshot functionality with interactive voice control
Run from root: python -m tests.test_screenshot
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.browser_controller import BrowserController
from src.browser.navigation import Navigation
from src.automation.screenshot_handler import ScreenshotHandler
from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.commands.command_parser import CommandParser

def test_screenshot_functionality():
    """Test screenshot capture with voice commands"""
    
    print("=" * 70)
    print("📸 VOICE ASSISTANT - SCREENSHOT FUNCTIONALITY TEST (Step 5.5)")
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
    time.sleep(2)
    
    # Initialize handlers
    nav = Navigation(browser)
    screenshot = ScreenshotHandler(browser)
    
    # Open a nice page for screenshot
    print("\n🌐 Opening Wikipedia for screenshot test...")
    tts.speak("Opening Wikipedia")
    nav.goto_url("https://en.wikipedia.org/wiki/Python_(programming_language)")
    time.sleep(3)
    
    tts.speak("Page loaded. You can now take screenshots.")
    print("✅ Page loaded")
    
    # Show existing screenshots
    existing_count = screenshot.get_screenshot_count()
    print(f"\n📊 Existing screenshots: {existing_count}")
    
    if existing_count > 0:
        print("📁 Recent screenshots:")
        recent = screenshot.list_screenshots()[:3]
        for i, filename in enumerate(recent, 1):
            print(f"   {i}. {filename}")
    
    # Interactive loop
    print("\n💡 Try these commands:")
    print("   - 'take screenshot'")
    print("   - 'capture screen'")
    print("   - 'full page screenshot'")
    print("   - 'go to youtube' (then take screenshot)")
    print("   - 'stop' to exit\n")
    
    max_commands = 5
    command_count = 0
    screenshots_taken = 0
    
    while command_count < max_commands:
        print(f"\n{'='*70}")
        print(f"🎤 Command {command_count + 1}/{max_commands} - Listening...")
        current_title = browser.get_page_title()
        print(f"📄 Current page: {current_title[:50]}")
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
        if intent == 'screenshot':
            tts.speak("Taking screenshot. Please wait.")
            print("📸 Capturing screenshot...")
            
            success, filepath = screenshot.take_screenshot()
            
            if success:
                screenshots_taken += 1
                filename = os.path.basename(filepath)
                print(f"✅ Screenshot saved: {filename}")
                print(f"📁 Location: {filepath}")
                tts.speak("Screenshot saved successfully")
            else:
                print("❌ Failed to take screenshot")
                tts.speak("Failed to take screenshot")
        
        elif intent == 'fullpage_screenshot':
            tts.speak("Taking full page screenshot. This may take a moment.")
            print("📸 Capturing full page screenshot...")
            
            success, filepath = screenshot.take_full_page_screenshot()
            
            if success:
                screenshots_taken += 1
                filename = os.path.basename(filepath)
                print(f"✅ Full page screenshot saved: {filename}")
                print(f"📁 Location: {filepath}")
                tts.speak("Full page screenshot saved successfully")
            else:
                print("❌ Failed to take full page screenshot")
                tts.speak("Failed to take full page screenshot")
        
        elif intent == 'navigate':
            site = params['site']
            tts.speak(f"Opening {site}")
            print(f"\n🌐 Navigating to: {site}")
            
            success, url = nav.open_website(site)
            
            if success:
                time.sleep(2)
                page_info = nav.get_page_info()
                print(f"✅ Opened: {page_info['title']}")
                tts.speak(f"{site} is now open. You can take a screenshot.")
            else:
                print(f"❌ Failed to open: {site}")
                tts.speak(f"Could not open {site}")
        
        else:
            tts.speak("Try saying take screenshot or go to a website.")
        
        command_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"📸 Screenshots taken this session: {screenshots_taken}")
    
    total_count = screenshot.get_screenshot_count()
    print(f"📁 Total screenshots saved: {total_count}")
    
    if screenshots_taken > 0:
        print("\n📁 New screenshots:")
        recent = screenshot.list_screenshots()[:screenshots_taken]
        for i, filename in enumerate(recent, 1):
            filepath = os.path.join(screenshot.screenshots_dir, filename)
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"   {i}. {filename} ({size:.1f} KB)")
    
    tts.speak(f"Test completed. {screenshots_taken} screenshots taken. Closing browser.")
    time.sleep(2)
    browser.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ Screenshot Functionality Test Completed (Step 5.5)")
    print("=" * 70)

if __name__ == "__main__":
    test_screenshot_functionality()