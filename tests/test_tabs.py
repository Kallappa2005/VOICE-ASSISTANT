"""
Test script for tab management with interactive voice control
Run from root: python -m tests.test_tabs
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.browser_controller import BrowserController
from src.browser.navigation import Navigation
from src.browser.tab_manager import TabManager
from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.commands.command_parser import CommandParser

def test_tab_management():
    """Test tab management with voice commands"""
    
    print("=" * 70)
    print("❌ VOICE ASSISTANT - TAB MANAGEMENT TEST (Step 5.4)")
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
    
    tts.speak("Chrome browser is open with Google")
    time.sleep(2)
    
    # Initialize handlers
    nav = Navigation(browser)
    tabs = TabManager(browser)
    
    # Open multiple tabs for testing using new_tab parameter
    print("\n📑 Setting up test tabs...")
    print("Tab 1: Google (already open)")
    
    tts.speak("Opening YouTube in new tab")
    print("Tab 2: Opening YouTube...")
    nav.open_website("youtube", new_tab=True)  # NEW TAB
    time.sleep(2)
    
    tts.speak("Opening Wikipedia in another new tab")
    print("Tab 3: Opening Wikipedia...")
    nav.open_website("wikipedia", new_tab=True)  # NEW TAB
    time.sleep(2)
    
    tab_count = tabs.get_tab_count()
    print(f"✅ Setup complete: {tab_count} tabs open")
    tts.speak(f"Setup complete. {tab_count} tabs are now open")
    
    # Show tab info
    print("\n📊 Current tabs:")
    titles = tabs.get_all_tab_titles()
    for i, title in enumerate(titles):
        print(f"   Tab {i+1}: {title[:50]}")
    
    # Interactive loop
    print("\n💡 Try these commands:")
    print("   - 'switch tab' / 'next tab'")
    print("   - 'previous tab'")
    print("   - 'close tab'")
    print("   - 'new tab'")
    print("   - 'close browser'")
    print("   - 'stop' to exit\n")
    
    tts.speak("You can now try tab commands. Say switch tab, close tab, or new tab.")
    
    max_commands = 8  # Increased for more testing
    command_count = 0
    
    while command_count < max_commands:
        print(f"\n{'='*70}")
        print(f"🎤 Command {command_count + 1}/{max_commands} - Listening...")
        current_index = tabs.get_current_tab_index()
        current_count = tabs.get_tab_count()
        current_title = browser.get_page_title()
        print(f"📊 Current: Tab {current_index + 1}/{current_count} - {current_title[:40]}")
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
        
        # Execute command
        if intent == 'close_browser':
            tts.speak("Closing browser and all tabs. Goodbye!")
            time.sleep(1)
            tabs.close_all_tabs()
            print("✅ Browser closed")
            return
        
        elif intent == 'close_tab':
            current_tabs = tabs.get_tab_count()
            tts.speak("Closing current tab")
            print(f"❌ Closing tab: {browser.get_page_title()[:40]}")
            
            if tabs.close_current_tab():
                remaining = tabs.get_tab_count()
                if remaining > 0:
                    print(f"✅ Tab closed ({remaining} tabs remaining)")
                    time.sleep(0.5)
                    new_title = browser.get_page_title()
                    print(f"📄 Now on: {new_title[:40]}")
                    tts.speak(f"{remaining} tabs remaining")
                else:
                    print("✅ Last tab closed - browser closed")
                    tts.speak("Browser closed")
                    return
            else:
                print("❌ Failed to close tab")
                tts.speak("Could not close tab")
        
        elif intent == 'new_tab':
            tts.speak("Opening new tab with Google")
            print("📑 Opening new tab...")
            
            if tabs.open_new_tab("https://www.google.com"):
                count = tabs.get_tab_count()
                time.sleep(1)
                print(f"✅ New tab opened (Total: {count})")
                tts.speak(f"New tab opened. Total {count} tabs")
            else:
                print("❌ Failed to open new tab")
                tts.speak("Could not open new tab")
        
        elif intent == 'switch_tab':
            before_title = browser.get_page_title()
            tts.speak("Switching to next tab")
            print(f"🔄 Switching from: {before_title[:40]}")
            
            if tabs.switch_to_next_tab():
                time.sleep(1)
                after_title = browser.get_page_title()
                print(f"✅ Switched to: {after_title[:40]}")
                tts.speak(f"Now on {after_title[:30]}")
            else:
                print("❌ Could not switch tab")
                tts.speak("Only one tab open")
        
        elif intent == 'previous_tab':
            before_title = browser.get_page_title()
            tts.speak("Switching to previous tab")
            print(f"🔄 Going back from: {before_title[:40]}")
            
            if tabs.switch_to_previous_tab():
                time.sleep(1)
                after_title = browser.get_page_title()
                print(f"✅ Switched to: {after_title[:40]}")
                tts.speak(f"Now on {after_title[:30]}")
            else:
                print("❌ Could not switch tab")
                tts.speak("Only one tab open")
        
        else:
            tts.speak("That's not a tab command. Try close tab or switch tab.")
        
        command_count += 1
    
    # Cleanup
    print(f"\n{'='*70}")
    tts.speak("Test completed. Closing browser.")
    time.sleep(2)
    browser.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ Tab Management Test Completed (Step 5.4)")
    print("=" * 70)

if __name__ == "__main__":
    test_tab_management()