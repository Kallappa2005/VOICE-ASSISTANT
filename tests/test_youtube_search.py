"""
Test script for YouTube search functionality
Run from root: python -m tests.test_youtube_search
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.browser_controller import BrowserController
from src.automation.youtube_controller import YouTubeController
from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.commands.command_parser import CommandParser

def test_youtube_search():
    """Test YouTube search with voice commands"""
    
    print("=" * 70)
    print("🎬 VOICE ASSISTANT - YOUTUBE SEARCH TEST (Step 6.1)")
    print("=" * 70)
    
    # Initialize components
    tts = TextToSpeechHandler(rate=150)
    stt = SpeechRecognitionHandler()
    browser = BrowserController()
    parser = CommandParser()
    
    # Open browser
    print("\n📋 Opening Chrome Browser...")
    tts.speak("Opening Chrome browser")
    
    if not browser.open_chrome():
        tts.speak("Failed to open browser")
        return
    
    tts.speak("Chrome browser is open")
    time.sleep(1)
    
    # Initialize YouTube controller
    youtube = YouTubeController(browser)
    
    # Test 1: Open YouTube
    print("\n🎬 Test 1: Opening YouTube...")
    tts.speak("Opening YouTube")
    
    if youtube.open_youtube():
        print("✅ YouTube opened successfully")
        tts.speak("YouTube is now open. You can search by just saying what you want to find.")
        time.sleep(2)
    else:
        print("❌ Failed to open YouTube")
        tts.speak("Failed to open YouTube")
        browser.close_browser()
        return
    
    # Test 2: Voice command search with context awareness
    print("\n🎤 Test 2: Context-Aware Search")
    print("=" * 70)
    print("💡 Since you're on YouTube, you can say:")
    print("   - 'search music' → Searches YouTube")
    print("   - 'cat videos' → Searches YouTube")
    print("   - 'python tutorial' → Searches YouTube")
    print("   - 'youtube search bike races' → Also works")
    print("   - 'open youtube' → Goes to homepage")
    print("   - 'stop' to exit\n")
    
    max_searches = 5
    search_count = 0
    
    while search_count < max_searches:
        print(f"\n{'='*70}")
        print(f"🎤 Search {search_count + 1}/{max_searches} - Listening...")
        
        # Show current context
        if youtube.is_on_youtube():
            print(f"📍 Context: ON YOUTUBE (searches will go to YouTube)")
        else:
            print(f"📍 Context: NOT on YouTube")
        
        print(f"{'='*70}")
        
        # Listen for command
        command = stt.listen()
        
        if not command:
            tts.speak("I didn't hear anything. Try again.")
            continue
        
        print(f"📝 You said: '{command}'")
        
        # Stop command
        if 'stop' in command or 'exit' in command:
            tts.speak("Stopping test")
            break
        
        # Parse command
        parsed = parser.parse(command)
        intent = parsed['intent']
        params = parsed['params']
        
        print(f"🔍 Detected intent: {intent}")
        
        # ===== CONTEXT-AWARE LOGIC =====
        
        # If explicit YouTube search command
        if intent == 'youtube_search':
            query = params['query']
            print(f"\n🔍 YouTube Search: '{query}'")
            tts.speak(f"Searching YouTube for {query}")
            
            if youtube.search_video(query):
                time.sleep(2)
                count = youtube.get_search_results_count()
                print(f"✅ Search successful! Found {count} results")
                
                first_video = youtube.get_first_video_title()
                if first_video:
                    print(f"📹 First result: {first_video[:50]}...")
                    tts.speak(f"Found {count} videos.")
                else:
                    tts.speak("Search completed")
                
                search_count += 1
            else:
                print("❌ Search failed")
                tts.speak("Search failed. Try again.")
        
        # If general search/navigate BUT we're on YouTube → Search YouTube
        elif (intent == 'search' or intent == 'navigate') and youtube.is_on_youtube():
            # Extract query
            if intent == 'search':
                query = params['query']
            else:
                query = params['site']
            
            print(f"\n🎯 Context-Aware: You're on YouTube, searching there")
            print(f"🔍 YouTube Search: '{query}'")
            tts.speak(f"Searching YouTube for {query}")
            
            if youtube.search_video(query):
                time.sleep(2)
                count = youtube.get_search_results_count()
                print(f"✅ Search successful! Found {count} results")
                
                first_video = youtube.get_first_video_title()
                if first_video:
                    print(f"📹 First result: {first_video[:50]}...")
                    tts.speak(f"Found {count} videos.")
                else:
                    tts.speak("Search completed")
                
                search_count += 1
            else:
                print("❌ Search failed")
                tts.speak("Search failed. Try again.")
        
        # Open YouTube command
        elif intent == 'open_youtube':
            print("\n🎬 Opening YouTube homepage...")
            tts.speak("Going to YouTube homepage")
            
            if youtube.open_youtube():
                print("✅ YouTube homepage loaded")
                tts.speak("YouTube homepage loaded")
            else:
                print("❌ Failed to load YouTube")
                tts.speak("Failed to load YouTube")
        
        # If navigate but NOT on YouTube
        elif intent == 'navigate' and not youtube.is_on_youtube():
            site = params['site']
            print(f"\n🌐 Not on YouTube, navigating to: {site}")
            tts.speak(f"Opening {site}")
            # This would use navigation handler if available
            print("⚠️ Navigation to other sites - using browser default")
        
        else:
            print(f"❌ Command not recognized in this context")
            tts.speak("Try saying what you want to search, or say open YouTube")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"🔍 Searches performed: {search_count}")
    print(f"🎬 Current page: {browser.get_page_title()}")
    
    tts.speak(f"Test completed. {search_count} searches performed. Closing browser.")
    time.sleep(2)
    browser.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ YouTube Search Test Completed (Step 6.1)")
    print("=" * 70)

if __name__ == "__main__":
    test_youtube_search()