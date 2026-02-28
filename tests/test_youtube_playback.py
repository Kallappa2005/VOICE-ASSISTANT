"""
Test script for YouTube video selection and playback control
Run from root: python -m tests.test_youtube_playback
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

def test_youtube_playback():
    """Test YouTube video selection and playback control"""
    
    print("=" * 70)
    print("🎬 VOICE ASSISTANT - YOUTUBE PLAYBACK TEST (Step 6.2)")
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
    
    time.sleep(1)
    
    # Initialize YouTube controller
    youtube = YouTubeController(browser)
    
    # Open YouTube and search
    print("\n🎬 Opening YouTube...")
    tts.speak("Opening YouTube")
    
    if not youtube.open_youtube():
        tts.speak("Failed to open YouTube")
        browser.close_browser()
        return
    
    time.sleep(2)
    
    # Do a search first
    print("\n🔍 Searching for demo videos...")
    tts.speak("Searching for cat videos")
    
    if youtube.search_video("funny cats"):
        time.sleep(2)
        count = youtube.get_search_results_count()
        print(f"✅ Found {count} videos")
        tts.speak(f"Found {count} videos. You can play any video by number.")
        
        # Show first few titles
        print("\n📹 Available videos:")
        for i in range(min(5, count)):
            title = youtube.get_video_title_by_index(i)
            if title:
                print(f"   {i+1}. {title[:60]}...")
    else:
        tts.speak("Search failed")
        browser.close_browser()
        return
    
    # Interactive control
    print("\n🎤 Interactive Playback Control")
    print("=" * 70)
    print("💡 Try these commands:")
    print("   - 'play video 1' / 'play first video'")
    print("   - 'pause video'")
    print("   - 'play video' (resumes)")
    print("   - 'stop video' (pause + reset)")
    print("   - 'exit test' to quit\n")
    
    max_commands = 10
    command_count = 0
    
    while command_count < max_commands:
        print(f"\n{'='*70}")
        print(f"🎤 Command {command_count + 1}/{max_commands} - Listening...")
        
        # Show context
        on_video_page = youtube.is_on_video_page()
        
        if on_video_page:
            current_video = youtube.get_current_video_title()
            if current_video:
                print(f"📹 Currently: {current_video[:50]}...")
            is_playing = youtube.is_video_playing()
            print(f"▶️ Status: {'Playing ▶️' if is_playing else 'Paused ⏸️'}")
        else:
            print(f"📍 Context: On search results page")
        
        print(f"{'='*70}")
        
        # Listen for command
        command = stt.listen()
        
        if not command:
            tts.speak("I didn't hear anything. Try again.")
            continue
        
        print(f"📝 You said: '{command}'")
        
        # Stop TEST command - check for "exit test" ONLY
        if 'exit test' in command or 'quit test' in command or command.strip() == 'stop':
            tts.speak("Stopping test")
            break
        
        # Build context for parser
        context = {
            'on_video_page': on_video_page
        }
        
        # Parse command WITH CONTEXT
        parsed = parser.parse(command, context=context)
        intent = parsed['intent']
        params = parsed['params']
        
        print(f"🔍 Detected intent: {intent}")
        
        # Handle commands
        if intent == 'play_video':
            video_num = params['video_number']
            index = video_num - 1
            
            count = youtube.get_search_results_count()
            
            if index < 0 or index >= count:
                print(f"❌ Invalid video number. Only {count} videos available.")
                tts.speak(f"Only {count} videos available.")
            else:
                title = youtube.get_video_title_by_index(index)
                print(f"\n▶️ Playing video {video_num}: {title[:50]}...")
                tts.speak(f"Playing video {video_num}")
                
                if youtube.play_video_by_index(index):
                    time.sleep(3)
                    print(f"✅ Video started")
                    tts.speak("Video is now playing")
                else:
                    print(f"❌ Failed to play video")
                    tts.speak("Failed to play video")
        
        elif intent == 'pause_video':
            if not on_video_page:
                print("❌ No video is playing")
                tts.speak("No video is currently playing")
            else:
                print("\n⏸️ Pausing video...")
                tts.speak("Pausing")
                
                if youtube.pause_video():
                    time.sleep(1)
                    is_paused = not youtube.is_video_playing()
                    if is_paused:
                        print("✅ Video paused")
                        tts.speak("Video paused")
                    else:
                        print("⚠️ Pause command sent")
                        tts.speak("Pause command sent")
                else:
                    print("❌ Failed to pause")
                    tts.speak("Failed to pause")
        
        elif intent == 'resume_video':
            if not on_video_page:
                print("❌ No video is loaded")
                tts.speak("No video is loaded")
            else:
                print("\n▶️ Resuming video...")
                tts.speak("Resuming")
                
                if youtube.play_video():
                    time.sleep(1)
                    is_playing = youtube.is_video_playing()
                    if is_playing:
                        print("✅ Video resumed")
                        tts.speak("Video resumed")
                    else:
                        print("⚠️ Play command sent")
                        tts.speak("Play command sent")
                else:
                    print("❌ Failed to resume")
                    tts.speak("Failed to resume")
        
        elif intent == 'stop_video':
            if not on_video_page:
                print("❌ No video is playing")
                tts.speak("No video is playing")
            else:
                print("\n⏹️ Stopping video...")
                tts.speak("Stopping video")
                
                if youtube.stop_video():
                    print("✅ Video stopped and reset")
                    tts.speak("Video stopped")
                else:
                    print("❌ Failed to stop")
                    tts.speak("Failed to stop")
        
        elif intent == 'youtube_search':
            query = params['query']
            print(f"\n🔍 Searching: {query}")
            tts.speak(f"Searching for {query}")
            
            if youtube.search_video(query):
                time.sleep(2)
                count = youtube.get_search_results_count()
                print(f"✅ Found {count} videos")
                tts.speak(f"Found {count} videos")
        
        else:
            print("❌ Command not recognized")
            tts.speak("Try play video, pause, or resume")
        
        command_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"🎬 Commands executed: {command_count}")
    
    if youtube.is_on_video_page():
        current = youtube.get_current_video_title()
        if current:
            print(f"📹 Final video: {current}")
    
    tts.speak("Test completed. Closing browser.")
    time.sleep(2)
    browser.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ YouTube Playback Test Completed (Step 6.2)")
    print("=" * 70)

if __name__ == "__main__":
    test_youtube_playback()