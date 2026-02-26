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
    
    tts.speak("Page loaded. You can now take or manage screenshots.")
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
    print("   - 'list screenshots'")
    print("   - 'delete screenshot' (deletes last one)")
    print("   - 'delete all screenshots'")
    print("   - 'go to youtube' (then take screenshot)")
    print("   - 'stop' to exit\n")
    
    max_commands = 8
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
        
        print(f"🔍 Detected intent: {intent}")  # DEBUG OUTPUT
        
        # ====== HANDLE SCREENSHOT COMMANDS FIRST ======
        
        if intent == 'delete_all_screenshots':
            count = screenshot.get_screenshot_count()
            
            if count == 0:
                print("❌ No screenshots to delete")
                tts.speak("No screenshots found")
            else:
                print(f"\n🗑️ Want to delete all {count} screenshots...")
                tts.speak(f"This will delete all {count} screenshots. Say yes to confirm or no to cancel.")
                
                # Wait for confirmation
                print("🎤 Waiting for confirmation (yes/no)...")
                confirmation = stt.listen()
                
                print(f"📝 Heard: '{confirmation}'")
                
                if confirmation:
                    confirmation_lower = confirmation.lower().strip()
                    
                    if 'yes' in confirmation_lower or 'yeah' in confirmation_lower or 'confirm' in confirmation_lower or 'sure' in confirmation_lower or 'ok' in confirmation_lower or 'okay' in confirmation_lower:
                        print("✅ Confirmation received: YES")
                        tts.speak("Deleting all screenshots now")
                        deleted = screenshot.clear_all_screenshots()
                        print(f"✅ Deleted {deleted} screenshots")
                        tts.speak(f"All screenshots deleted. {deleted} files removed.")
                    elif 'no' in confirmation_lower or 'cancel' in confirmation_lower or 'stop' in confirmation_lower:
                        print("❌ Deletion cancelled by user")
                        tts.speak("Deletion cancelled")
                    else:
                        print(f"❌ Unclear response: '{confirmation}'")
                        tts.speak("I didn't understand. Deletion cancelled for safety.")
                else:
                    print("❌ No confirmation heard")
                    tts.speak("No response heard. Deletion cancelled")
        
        elif intent == 'list_screenshots':
            count = screenshot.get_screenshot_count()
            print(f"\n📊 Total screenshots: {count}")
            tts.speak(f"You have {count} screenshots")
            
            if count > 0:
                print("📁 Screenshots:")
                screenshots_list = screenshot.list_screenshots()
                
                # Show first 5
                for i, filename in enumerate(screenshots_list[:5], 1):
                    filepath = os.path.join(screenshot.screenshots_dir, filename)
                    size = os.path.getsize(filepath) / 1024  # KB
                    print(f"   {i}. {filename} ({size:.1f} KB)")
                
                if count > 5:
                    print(f"   ... and {count - 5} more")
            else:
                print("📁 No screenshots found")
        
        elif intent == 'delete_screenshot':
            screenshots_list = screenshot.list_screenshots()
            
            if not screenshots_list:
                print("❌ No screenshots to delete")
                tts.speak("No screenshots found to delete")
            else:
                last_screenshot = screenshots_list[0]  # Most recent
                print(f"\n🗑️ Deleting: {last_screenshot}")
                tts.speak("Deleting last screenshot")
                
                if screenshot.delete_screenshot(last_screenshot):
                    print(f"✅ Deleted: {last_screenshot}")
                    remaining = screenshot.get_screenshot_count()
                    tts.speak(f"Screenshot deleted. {remaining} remaining")
                else:
                    print("❌ Failed to delete screenshot")
                    tts.speak("Failed to delete screenshot")
        
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
        
        elif intent == 'screenshot':
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
        
        # ====== OTHER COMMANDS ======
        
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
        
        elif intent == 'search':
            query = params['query']
            tts.speak(f"Searching for {query}")
            print(f"\n🔍 Searching: {query}")
            
            success = nav.search_google(query)
            
            if success:
                time.sleep(2)
                print(f"✅ Search completed")
                tts.speak("Search completed")
            else:
                print(f"❌ Search failed")
                tts.speak("Search failed")
        
        else:
            tts.speak("Try saying take screenshot, list screenshots, or delete screenshot.")
        
        command_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"📸 Screenshots taken this session: {screenshots_taken}")
    
    total_count = screenshot.get_screenshot_count()
    print(f"📁 Total screenshots remaining: {total_count}")
    
    if total_count > 0:
        print("\n📁 Current screenshots:")
        recent = screenshot.list_screenshots()
        for i, filename in enumerate(recent, 1):
            filepath = os.path.join(screenshot.screenshots_dir, filename)
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"   {i}. {filename} ({size:.1f} KB)")
    
    tts.speak(f"Test completed. Closing browser.")
    time.sleep(2)
    browser.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ Screenshot Functionality Test Completed (Step 5.5)")
    print("=" * 70)

if __name__ == "__main__":
    test_screenshot_functionality()