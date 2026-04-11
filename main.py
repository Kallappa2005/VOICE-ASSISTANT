# Main entry point of the application

"""
Voice Assistant - Main Application
Integrates all features: Speech, Browser, YouTube, Screenshots, Navigation, etc.
Run: python main.py
"""

import sys
import os
import time
import webbrowser
from threading import Thread

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.browser.browser_controller import BrowserController
from src.browser.navigation import Navigation
from src.browser.tab_manager import TabManager
from src.automation.scroll_handler import ScrollHandler
from src.automation.screenshot_handler import ScreenshotHandler
from src.automation.youtube_controller import YouTubeController
from src.automation.coding_mode import CodingMode
from src.automation.study_mode import StudyMode
from src.automation.project_setup import ProjectSetup
from src.commands.command_parser import CommandParser
from src.core.logger import setup_logger

# GUI imports (optional)
try:
    import tkinter as tk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

logger = setup_logger(__name__)

class VoiceAssistant:
    """Main Voice Assistant Application"""
    
    def __init__(self, gui=None):
        """
        Initialize all components
        
        Args:
            gui: Optional BasicAssistantGUI instance (passed from launcher)
        """
        print("\n" + "=" * 80)
        print(" " * 25 + "🎤 VOICE ASSISTANT")
        print("=" * 80)
        print("\n🔧 Initializing components...")
        
        # GUI (optional)
        self.gui = gui
        
        # Initialize speech handlers
        print("   ├── Speech Recognition...")
        self.tts = TextToSpeechHandler(rate=210)
        self.stt = SpeechRecognitionHandler()
        print("   ✅ Speech module ready")
        
        # Calibrate to room noise immediately after mic is ready
        print("   ├── Calibrating to room noise...")
        self.stt.calibrate(duration=2.0)
        print("   ✅ Noise calibration complete")
        
        # Initialize browser controller
        print("   ├── Browser Controller...")
        self.browser = BrowserController()
        print("   ✅ Browser controller ready")
        
        # Initialize command parser
        print("   ├── Command Parser...")
        self.parser = CommandParser()
        print("   ✅ Command parser ready")
        
        # Initialize Coding Mode (browser-independent — uses config.json)
        print("   ├── Coding Mode...")
        self.coding_mode = CodingMode()
        print("   ✅ Coding Mode ready")
        
        # Initialize Study Mode (browser-independent — uses config.json)
        print("   ├── Study Mode...")
        self.study_mode = StudyMode()
        print("   ✅ Study Mode ready")

        # Initialize Project Setup (browser-independent — uses config.json)
        print("   ├── Project Setup...")
        self.project_setup = ProjectSetup()
        print("   ✅ Project Setup ready")
        
        # Browser-dependent handlers (initialized after browser opens)
        self.nav = None
        self.tabs = None
        self.scroll = None
        self.screenshot = None
        self.youtube = None
        
        self.running = False
        
        # GUI availability
        if self.gui is None and GUI_AVAILABLE:
            try:
                from src.ui.basic_gui import BasicAssistantGUI
                self.gui = BasicAssistantGUI(assistant=self)
                print("   ├── GUI Interface...")
                print("   ✅ GUI ready")
            except Exception as e:
                print(f"   ⚠️ GUI not available: {e}")
                self.gui = None
        
        print("\n✅ Voice Assistant initialized successfully!")
        logger.info("Voice Assistant initialized")
    
    def start(self):
        """Start the voice assistant"""
        print("\n" + "=" * 80)
        print("🚀 STARTING VOICE ASSISTANT")
        print("=" * 80)
        
        # If GUI is available, start it in the main thread
        # This blocks until the GUI window closes
        if self.gui:
            print("\n📱 Starting GUI interface...")
            
            # Start assistant in daemon thread
            assistant_thread = Thread(target=self._run_assistant, daemon=True)
            assistant_thread.start()
            
            # Show GUI (blocks main thread)
            self.gui.show()
            self.gui.run()
            
            # GUI closed, stop assistant
            self.running = False
            print("\n👋 GUI closed, shutting down...")
            time.sleep(0.5)
            self.cleanup()
            
            return True
        
        # Otherwise run headless (traditional mode)
        print("\n🎧 Running in headless mode (no GUI)")
        return self._run_assistant()
    
    def _run_assistant(self):
        """Run the assistant loop (can run in separate thread)"""
        try:
            # Greet user
            self.tts.speak("Hello! I am your voice assistant.")
            time.sleep(0.5)
            
            # Note: Browser will open on first user command (navigate, search, youtube)
            # Don't open it automatically to allow users to just listen/speak
            
            # Initialize browser-dependent handlers
            print("\n🔧 Initializing browser features...")
            self.nav = Navigation(self.browser)
            self.tabs = TabManager(self.browser)
            self.scroll = ScrollHandler(self.browser)
            self.screenshot = ScreenshotHandler(self.browser)
            self.youtube = YouTubeController(self.browser)
            print("✅ All features initialized")
            
            # Ready message
            print("\n" + "=" * 80)
            print("✅ VOICE ASSISTANT IS READY!")
            print("=" * 80)
            
            self.tts.speak("I am ready! You can now give me commands.")
            time.sleep(0.5)
            self.tts.speak("Say help to hear available commands, or say exit to quit.")
            
            # Show command menu
            self._show_command_menu()
            
            # Start command loop
            self.running = True
            self.run_command_loop()
            
            return True
            
        except Exception as e:
            print(f"❌ Error in assistant: {e}")
            logger.error(f"Assistant error: {e}", exc_info=True)
            return False
    
    def _show_command_menu(self):
        """Display available commands"""
        print("\n" + "=" * 80)
        print("📋 AVAILABLE COMMANDS:")
        print("=" * 80)
        
        commands = {
            "🌐 Navigation": [
                "'open youtube' - Open YouTube",
                "'open google' / 'open wikipedia' - Open websites",
                "'search for [query]' - Search on Google",
            ],
            "📹 YouTube": [
                "'search youtube for [query]' - Search videos",
                "'play video 1' / 'play first video' - Play specific video",
                "'pause video' - Pause current video",
                "'play video' / 'resume video' - Resume playback",
                "'stop video' - Stop and reset video",
                "'skip ad' - Skip the current YouTube ad (once skip button appears)",
            ],
            "📜 Scrolling": [
                "'scroll down' / 'scroll up' - Scroll page",
                "'scroll to top' / 'scroll to bottom' - Jump to top/bottom",
            ],
            "📸 Screenshots": [
                "'take screenshot' - Capture current view",
                "'full page screenshot' - Capture entire page",
                "'list screenshots' - Count screenshots",
                "'delete screenshot' - Delete last screenshot",
            ],
            "🗂️ Tab Management": [
                "'switch tab' / 'next tab' - Switch to next tab",
                "'previous tab' - Switch to previous tab",
                "'new tab' - Open new tab",
                "'close tab' - Close current tab",
            ],
            "⚙️ System": [
                "'help' - Show this menu",
                "'exit' / 'goodbye' - Quit assistant",
            ],
            "💻 Coding Mode": [
                "'start coding'  - Launch full dev environment from config.json",
                "'coding mode'   - Same as above",
                "'begin coding'  - Same as above",
                "'launch project'- Open project in VS Code + terminal + browser",
                "  (edit config.json in project root to change settings)",
            ],
            "🛠️ Project Setup": [
                "'set up react project'  - Create React + Express starter project",
                "'set up flask project'  - Create React + Flask starter project",
                "  Voice assistant will ask for the main folder name first",
                "  Base Desktop folder is read from config.json",
            ],
            "📚 Study Mode": [
                "'study mode' [topic]        - Launch study environment",
                "'start studying' [topic]    - Same as above",
                "'focus mode' [topic]        - Same as above",
                "'study session' [topic]     - Same as above",
                "  Example: 'study mode React hooks', 'start studying Python'",
                "  (edit config.json to customize YouTube, docs, and note app)",
            ],
            "🔊 Noisy Room Tips": [
                "Speak clearly and slightly louder than normal",
                "Assistant retries 3× if it mishears — wait for the retry prompt",
                "Move closer to the microphone if possible",
            ]
        }
        
        for category, cmd_list in commands.items():
            print(f"\n{category}")
            print("  " + "─" * 70)
            for cmd in cmd_list:
                print(f"  {cmd}")
        
        print("\n" + "=" * 80)
    
    def _handle_help(self):
        """Handle help command - show available commands in console and GUI"""
        self.tts.speak("Here are the available commands")
        
        if self.gui:
            self.gui.log_console("\n" + "=" * 80, "info")
            self.gui.log_console("📋 AVAILABLE COMMANDS:", "info")
            self.gui.log_console("=" * 80, "info")
        
        commands = {
            "🌐 Navigation": [
                "'open youtube' - Open YouTube",
                "'open google' / 'open wikipedia' - Open websites",
                "'search for [query]' - Search on Google",
            ],
            "📹 YouTube": [
                "'search youtube for [query]' - Search videos",
                "'play video 1' / 'play first video' - Play specific video",
                "'pause video' - Pause current video",
                "'play video' / 'resume video' - Resume playback",
                "'stop video' - Stop and reset video",
                "'skip ad' - Skip the current YouTube ad (once skip button appears)",
            ],
            "📜 Scrolling": [
                "'scroll down' / 'scroll up' - Scroll page",
                "'scroll to top' / 'scroll to bottom' - Jump to top/bottom",
            ],
            "📸 Screenshots": [
                "'take screenshot' - Capture current view",
                "'full page screenshot' - Capture entire page",
                "'list screenshots' - Count screenshots",
                "'delete screenshot' - Delete last screenshot",
            ],
            "🗂️ Tab Management": [
                "'switch tab' / 'next tab' - Switch to next tab",
                "'previous tab' - Switch to previous tab",
                "'new tab' - Open new tab",
                "'close tab' - Close current tab",
            ],
            "⚙️ System": [
                "'help' - Show this menu",
                "'exit' / 'goodbye' - Quit assistant",
            ],
            "💻 Coding Mode": [
                "'start coding'  - Launch full dev environment from config.json",
                "'coding mode'   - Same as above",
                "'begin coding'  - Same as above",
                "'launch project'- Open project in VS Code + terminal + browser",
                "  (edit config.json in project root to change settings)",
            ],
            "🛠️ Project Setup": [
                "'set up react project'  - Create React + Express starter project",
                "'set up flask project'  - Create React + Flask starter project",
                "  Voice assistant will ask for the main folder name first",
                "  Base Desktop folder is read from config.json",
            ],
            "📚 Study Mode": [
                "'study mode' [topic]        - Launch study environment",
                "'start studying' [topic]    - Same as above",
                "'focus mode' [topic]        - Same as above",
                "'study session' [topic]     - Same as above",
                "  Example: 'study mode React hooks', 'start studying Python'",
                "  (edit config.json to customize YouTube, docs, and note app)",
            ],
            "🔊 Noisy Room Tips": [
                "Speak clearly and slightly louder than normal",
                "Assistant retries 3× if it mishears — wait for the retry prompt",
                "Move closer to the microphone if possible",
            ]
        }
        
        for category, cmd_list in commands.items():
            category_msg = f"\n{category}"
            separator = "  " + "─" * 70
            
            if self.gui:
                self.gui.log_console(category_msg, "success")
                self.gui.log_console(separator, "info")
            
            print(category_msg)
            print(separator)
            
            for cmd in cmd_list:
                cmd_msg = f"  {cmd}"
                if self.gui:
                    self.gui.log_console(cmd_msg, "info")
                print(cmd_msg)
        
        if self.gui:
            self.gui.log_console("\n" + "=" * 80, "info")
        
        print("\n" + "=" * 80)
        self.tts.speak("What would you like me to do?")
    
    def run_command_loop(self):
        """Main command processing loop"""
        command_count = 0
        
        if self.gui:
            self.gui.log_message("🎤 Listening... Say commands or 'help' for menu", level="info")
        
        while self.running:
            try:
                print("\n" + "━" * 80)
                print(f"🎤 LISTENING... (Command #{command_count + 1})")
                print("━" * 80)
                
                # Get context
                context = self._get_context()
                if context:
                    if context.get('on_video_page'):
                        status = "▶️ Playing" if context.get('video_playing') else "⏸️ Paused"
                        print(f"📍 Context: On YouTube video page ({status})")
                        
                        if self.gui:
                            self.gui.log_message(f"📍 On YouTube ({status})", level="info")
                    elif context.get('on_youtube'):
                        print(f"📍 Context: On YouTube")
                        
                        if self.gui:
                            self.gui.log_message("📍 On YouTube", level="info")
                    else:
                        current_url = self.browser.get_current_url()
                        if current_url:
                            print(f"📍 Current page: {current_url[:60]}...")
                            
                            if self.gui:
                                self.gui.log_message(f"📍 {current_url[:50]}...", level="info")
                
                # Listen for command
                print("\n🎤 Speak now...")
                command = self.stt.listen()
                
                if not command:
                    print("❓ No audio detected")
                    self.tts.speak("I didn't hear anything. Please try again.")
                    
                    if self.gui:
                        self.gui.log_message("❓ No audio detected", level="warning")
                    
                    continue
                
                print(f"\n📝 You said: '{command}'")
                logger.info(f"User command: {command}")
                
                if self.gui:
                    self.gui.log_message(f"👤 You: {command}", level="info")
                
                # Check for exit command
                if self._is_exit_command(command):
                    print("\n👋 Exiting...")
                    self.tts.speak("Goodbye! Thank you for using voice assistant.")
                    
                    if self.gui:
                        self.gui.log_message("👋 Goodbye!", level="success")
                    
                    break
                
                # Check for help command
                if 'help' in command.lower():
                    self.tts.speak("Here are the available commands")
                    self._show_command_menu()
                    self.tts.speak("What would you like me to do?")
                    
                    if self.gui:
                        self.gui.log_message("📋 Showing available commands", level="info")
                    
                    continue
                
                # Execute command
                self.execute_command(command, context)
                command_count += 1
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user (Ctrl+C)")
                logger.warning("Interrupted by user")
                self.tts.speak("Interrupted")
                
                if self.gui:
                    self.gui.log_message("⚠️ Interrupted by user", level="warning")
                
                break
                
            except Exception as e:
                print(f"\n❌ Error in command loop: {e}")
                logger.error(f"Command loop error: {e}")
                self.tts.speak("Sorry, I encountered an error. Please try again.")
                
                if self.gui:
                    self.gui.log_message(f"❌ Error: {e}", level="error")
        
        # Cleanup
        print(f"\n📊 Total commands executed: {command_count}")
        logger.info(f"Total commands: {command_count}")
        
        if self.gui:
            self.gui.log_message(f"📊 Session ended. Commands: {command_count}", level="success")
        
        self.cleanup()
    
    def _get_context(self):
        """Get current context information"""
        try:
            context = {}
            
            # Check if on YouTube
            if self.youtube and self.youtube.is_on_youtube():
                context['on_youtube'] = True
                
                # Check if on video page
                if self.youtube.is_on_video_page():
                    context['on_video_page'] = True
                    
                    # Check if video is playing
                    try:
                        if self.youtube.is_video_playing():
                            context['video_playing'] = True
                    except:
                        pass
            
            return context if context else None
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return None
    
    def _is_exit_command(self, command):
        """Check if command is an exit command"""
        exit_keywords = [
            'exit', 'quit', 'goodbye', 'bye', 'stop', 
            'close assistant', 'stop assistant', 'shut down'
        ]
        command_lower = command.lower().strip()
        
        # Exact matches
        if command_lower in exit_keywords:
            return True
        
        # Contains exit phrases
        exit_phrases = ['exit', 'quit', 'goodbye', 'shut down']
        return any(phrase in command_lower for phrase in exit_phrases)
    
    def execute_command(self, command, context=None):
        """Execute parsed command"""
        try:
            # Parse command with context
            parsed = self.parser.parse(command, context=context)
            intent = parsed['intent']
            params = parsed['params']
            
            print(f"🔍 Detected intent: {intent}")
            logger.info(f"Intent: {intent}, Params: {params}")
            
            return self.handle_command(intent, params, context=context)
        
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            logger.error(f"Command execution error: {e}", exc_info=True)
            self.tts.speak("Sorry, I encountered an error while executing that command.")
            return False
    
    def handle_command(self, intent, params, context=None):
        """Handle an already-parsed intent from voice input or GUI buttons."""
        try:
            params = params or {}

            if intent == 'navigate':
                self._handle_navigate(params)
                return True
            
            if intent == 'search':
                self._handle_search(params)
                return True
            
            if intent == 'open_youtube':
                self._handle_open_youtube()
                return True
            
            if intent == 'youtube_search':
                self._handle_youtube_search(params)
                return True
            
            if intent == 'play_video':
                self._handle_play_video(params)
                return True
            
            if intent == 'pause_video':
                self._handle_pause_video()
                return True
            
            if intent == 'resume_video':
                self._handle_resume_video()
                return True
            
            if intent == 'stop_video':
                self._handle_stop_video()
                return True
            
            if intent == 'skip_ad':
                self._handle_skip_ad()
                return True
            
            if intent == 'scroll_down':
                self._handle_scroll_down(params)
                return True
            
            if intent == 'scroll_up':
                self._handle_scroll_up(params)
                return True
            
            if intent == 'scroll_top':
                self._handle_scroll_top()
                return True
            
            if intent == 'scroll_bottom':
                self._handle_scroll_bottom()
                return True
            
            if intent == 'screenshot':
                self._handle_screenshot()
                return True
            
            if intent == 'fullpage_screenshot':
                self._handle_fullpage_screenshot()
                return True
            
            if intent == 'list_screenshots':
                self._handle_list_screenshots()
                return True
            
            if intent == 'delete_screenshot':
                self._handle_delete_screenshot()
                return True
            
            if intent == 'delete_all_screenshots':
                self._handle_delete_all_screenshots()
                return True
            
            if intent == 'switch_tab':
                self._handle_switch_tab()
                return True
            
            if intent == 'previous_tab':
                self._handle_previous_tab()
                return True
            
            if intent == 'close_tab':
                self._handle_close_tab()
                return True
            
            if intent == 'new_tab':
                self._handle_new_tab()
                return True
            
            if intent == 'close_browser':
                self._handle_close_browser()
                return True
            
            if intent == 'start_coding':
                self._handle_start_coding()
                return True

            if intent == 'setup_project':
                self._handle_setup_project(params)
                return True
            
            if intent == 'start_study':
                self._handle_start_study(params)
                return True
            
            if intent == 'help':
                self._handle_help()
                return True
            
            if intent == 'wake':
                self.tts.speak("Hello! I'm ready. How can I help you?")
                return True

            if intent == 'sleep':
                self.tts.speak("Going to sleep. Say wake up to wake me.")
                return True

            if intent == 'exit':
                self.tts.speak_goodbye()
                return False
            
            if intent == 'unknown':
                print("❌ Command not recognized")
                self.tts.speak("I'm not sure what you mean. Say help to see available commands.")
                return True
            
            print(f"⚠️ Intent '{intent}' not implemented yet")
            self.tts.speak(f"I understand {intent}, but this feature is not ready yet.")
            return True
        
        except Exception as e:
            print(f"❌ Error handling command: {e}")
            logger.error(f"Command handling error: {e}", exc_info=True)
            self.tts.speak("Sorry, I encountered an error while executing that command.")
            return True
    
    # ==================== BROWSER INITIALIZATION ====================
    
    def _ensure_browser_open(self):
        """Ensure browser is open before browser-dependent commands"""
        if not self.browser.is_open():
            print("\n📋 Opening Chrome browser...")
            self.tts.speak("Opening Chrome browser, please wait.")
            
            if not self.browser.open_chrome():
                print("❌ Failed to open browser")
                self.tts.speak("Failed to open browser. Please check your Chrome installation.")
                return False
            
            print("✅ Browser opened successfully")
            time.sleep(1)
            return True
        
        return True
    
    # ==================== COMMAND HANDLERS ====================
    
    def _handle_navigate(self, params):
        """Handle website navigation"""
        site = params.get('site', 'google')

        if not self._ensure_browser_open():
            return

        print(f"\n🌐 Opening {site}...")
        self.tts.speak(f"Opening {site}")

        success, url = self.nav.open_website(site)
        if success:
            time.sleep(2)
            print(f"✅ Opened: {url}")
            self.tts.speak(f"{site} is now open")
        else:
            print(f"❌ Failed to open {site}")
            self.tts.speak(f"Could not open {site}")

    def _handle_search(self, params):
        """Handle Google search"""
        query = params.get('query', '')
        if not query:
            self.tts.speak("What would you like to search for?")
            return

        if not self._ensure_browser_open():
            return

        print(f"\n🔍 Searching for: {query}")
        self.tts.speak(f"Searching for {query}")

        if self.nav.search_google(query):
            time.sleep(2)
            print("✅ Search completed")
            self.tts.speak("Search completed")
        else:
            print("❌ Search failed")
            self.tts.speak("Search failed")

    def _handle_open_youtube(self):
        """Handle open YouTube"""
        if not self._ensure_browser_open():
            return

        print("\n📺 Opening YouTube...")
        self.tts.speak("Opening YouTube")

        if self.youtube.open_youtube():
            time.sleep(2)
            print("✅ YouTube opened")
            self.tts.speak("YouTube is now open")
        else:
            print("❌ Failed to open YouTube")
            self.tts.speak("Failed to open YouTube")

    def _handle_youtube_search(self, params):
        """Handle YouTube search"""
        query = params.get('query', '')
        if not query:
            self.tts.speak("What would you like to search on YouTube?")
            return

        if not self._ensure_browser_open():
            return

        print(f"\n🔍 Searching YouTube: {query}")
        self.tts.speak(f"Searching YouTube for {query}")

        if self.youtube.search_video(query):
            time.sleep(2)
            count = self.youtube.get_search_results_count()
            print(f"✅ Found {count} videos")
            self.tts.speak(f"Found {count} videos. You can play any video by saying play video followed by a number.")
        else:
            print("❌ YouTube search failed")
            self.tts.speak("YouTube search failed")

    def _handle_play_video(self, params):
        """Handle play video by number"""
        video_num = params.get('video_number', 1)
        index = video_num - 1

        if not self._ensure_browser_open():
            return

        print(f"\n▶️ Playing video {video_num}...")

        # Get video title
        title = self.youtube.get_video_title_by_index(index)
        if not title:
            print(f"❌ Video {video_num} not found")
            self.tts.speak(f"Video {video_num} not found")
            return

        print(f"   Title: {title[:60]}...")
        self.tts.speak(f"Playing video {video_num}")

        if self.youtube.play_video_by_index(index):
            time.sleep(3)
            print("✅ Video started")
            self.tts.speak("Video is now playing")
        else:
            print("❌ Failed to play video")
            self.tts.speak("Failed to play video")

    def _handle_pause_video(self):
        """Handle pause video"""
        if not self._ensure_browser_open():
            return

        if not self.youtube.is_on_video_page():
            print("❌ No video is playing")
            self.tts.speak("No video is currently playing")
            return

        print("\n⏸️ Pausing video...")
        self.tts.speak("Pausing video")

        if self.youtube.pause_video():
            time.sleep(1)
            print("✅ Video paused")
            self.tts.speak("Video paused")
        else:
            print("❌ Failed to pause")
            self.tts.speak("Failed to pause video")

    def _handle_resume_video(self):
        """Handle resume video"""
        if not self._ensure_browser_open():
            return

        if not self.youtube.is_on_video_page():
            print("❌ No video loaded")
            self.tts.speak("No video is loaded")
            return

        print("\n▶️ Resuming video...")
        self.tts.speak("Resuming video")

        if self.youtube.play_video():
            time.sleep(1)
            print("✅ Video resumed")
            self.tts.speak("Video resumed")
        else:
            print("❌ Failed to resume")
            self.tts.speak("Failed to resume video")

    def _handle_stop_video(self):
        """Handle stop video"""
        if not self._ensure_browser_open():
            return

        if not self.youtube.is_on_video_page():
            print("❌ No video is playing")
            self.tts.speak("No video is playing")
            return

        print("\n⏹️ Stopping video...")
        self.tts.speak("Stopping video")

        if self.youtube.stop_video():
            time.sleep(1)
            print("✅ Video stopped and reset")
            self.tts.speak("Video stopped")
        else:
            print("❌ Failed to stop")
            self.tts.speak("Failed to stop video")

    def _handle_skip_ad(self):
        """Handle skip YouTube ad"""
        if not self._ensure_browser_open():
            return

        print("\n⏭️ Checking for ads...")

        # First, make sure we are on a video page at all
        if not self.youtube.is_on_video_page():
            print("❌ Not on a YouTube video page")
            self.tts.speak("You are not on a YouTube video page")
            return

        # Check if an ad is actually showing
        if not self.youtube.is_ad_playing():
            print("ℹ️ No ad is currently playing")
            self.tts.speak("No ad is currently playing")
            return

        print("📢 Ad detected! Waiting for skip button (up to 30 seconds)...")
        self.tts.speak("Ad detected. Waiting for the skip button.")

        result = self.youtube.skip_ad(wait_seconds=30)

        if result == 'skipped':
            print("✅ Ad skipped!")
            self.tts.speak("Ad skipped. Enjoy your video!")
        elif result == 'no_ad':
            print("ℹ️ Ad ended on its own before skip button appeared")
            self.tts.speak("Looks like the ad already finished")
        elif result == 'not_yet':
            print("⚠️ Ad is playing but skip button did not appear")
            self.tts.speak(
                "This ad cannot be skipped. It will end automatically, "
                "please wait a moment."
            )
        else:  # 'error'
            print("❌ Error while trying to skip ad")
            self.tts.speak("Sorry, something went wrong while trying to skip the ad.")

    def _handle_setup_project(self, params):
        """Handle project setup commands for React and Flask starter projects."""
        params = params or {}
        project_type = params.get('project_type', 'react').strip().lower()

        print(f"\n🛠️ Starting {project_type.title()} project setup...")
        self.tts.speak(
            f"Starting {project_type} project setup. What folder name should I use for the main project folder?"
        )

        folder_name = self.stt.listen()
        if not folder_name:
            fallback_name = params.get('project_name')
            if fallback_name:
                folder_name = fallback_name

        if not folder_name:
            print("❌ No folder name provided")
            self.tts.speak("I could not hear the folder name. Please try again.")
            return

        folder_name = folder_name.strip()
        print(f"📁 Folder name: {folder_name}")
        self.tts.speak(f"Setting up the project inside the folder named {folder_name}. Please wait.")

        result = self.project_setup.setup_project(project_type, folder_name)

        if result['success']:
            ok = sum(1 for s in result['steps'] if s.startswith('✅'))
            total = len(result['steps'])
            urls = result.get('urls', {})

            print(f"\n✅ {project_type.title()} project launched ({ok}/{total} steps succeeded)")
            print(f"📂 Project path: {result.get('project_path')}")

            if urls.get('backend'):
                if self.nav:
                    self.nav.goto_url(urls['backend'], new_tab=True)
                else:
                    webbrowser.open(urls['backend'], new=2)

            if urls.get('frontend'):
                time.sleep(1)
                if self.nav:
                    self.nav.goto_url(urls['frontend'], new_tab=True)
                else:
                    webbrowser.open(urls['frontend'], new=2)

            self.tts.speak(
                f"{project_type.title()} project setup is complete. I opened the frontend and backend in the browser."
            )
        else:
            err = result.get('error', 'Unknown error')
            print(f"\n❌ Project setup failed: {err}")
            self.tts.speak(f"Project setup failed. {err}")
    
    def _handle_start_study(self, params):
        """Handle 'study mode' voice command — launches focused study environment."""
        topic = params.get('topic') if params else None
        
        topic_label = f" ({topic})" if topic else " (default topic)"
        print(f"\n📚 Starting Study Mode{topic_label}...")
        
        if topic:
            self.tts.speak(f"Starting study mode. Opening YouTube, documentation, and notepad for {topic}. Please wait.")
        else:
            self.tts.speak("Starting study mode. Opening YouTube, documentation, and notepad. Please wait.")
        
        result = self.study_mode.start_study_mode(topic=topic)
        
        if result['success']:
            ok  = sum(1 for s in result['steps'] if s.startswith('✅'))
            total = len(result['steps'])
            
            print(f"\n✅ Study Mode launched ({ok}/{total} steps succeeded)")
            self.tts.speak(
                "Study mode is ready. YouTube, documentation, and notepad have been opened. Good luck studying!"
            )
        else:
            err = result.get('error', 'Unknown error')
            print(f"\n❌ Study Mode failed: {err}")
            
            if 'config.json not found' in err:
                self.tts.speak(
                    "Could not start study mode. "
                    "The config dot json file was not found. "
                    "Please create it at the project root."
                )
            elif 'Invalid JSON' in err:
                self.tts.speak(
                    "Could not start study mode. "
                    "The config dot json file contains invalid JSON. "
                    "Please fix it and try again."
                )
            else:
                self.tts.speak(f"Study mode failed: {err}")
    
    def _handle_start_coding(self):
        """Handle 'start coding' voice command — launches the full dev environment."""
        print("\n💻 Starting Coding Mode...")
        self.tts.speak(
            "Starting coding mode. Opening Visual Studio Code, terminal, "
            "and your browser links. Please wait."
        )
        
        result = self.coding_mode.start_coding_mode()
        
        if result['success']:
            # Count successful steps
            ok  = sum(1 for s in result['steps'] if s.startswith('✅'))
            total = len(result['steps'])
            
            print(f"\n✅ Coding Mode launched ({ok}/{total} steps succeeded)")
            self.tts.speak(
                f"Coding mode is ready. "
                f"Visual Studio Code, terminal, and browser tabs have been opened."
            )
        else:
            err = result.get('error', 'Unknown error')
            print(f"\n❌ Coding Mode failed: {err}")
            # Summarise the error for voice (keep it short)
            if 'config.json not found' in err:
                self.tts.speak(
                    "Could not start coding mode. "
                    "The config dot json file was not found. "
                    "Please create it at the project root."
                )
            elif 'Invalid JSON' in err:
                self.tts.speak(
                    "Could not start coding mode. "
                    "The config dot json file contains invalid JSON. "
                    "Please fix it and try again."
                )
            else:
                self.tts.speak(
                    "Could not start coding mode due to a configuration error. "
                    "Please check the terminal for details."
                )
    
    def _handle_scroll_down(self, params):
        """Handle scroll down"""
        amount = params.get('amount', 'medium') if params else 'medium'

        if not self._ensure_browser_open():
            return

        print(f"\n📜 Scrolling down ({amount})...")
        if self.scroll.scroll_down(amount):
            print("✅ Scrolled down")
            self.tts.speak("Scrolled down")
        else:
            print("❌ Failed to scroll")
            self.tts.speak("Failed to scroll")
    
    def _handle_scroll_up(self, params):
        """Handle scroll up"""
        amount = params.get('amount', 'medium') if params else 'medium'

        if not self._ensure_browser_open():
            return

        print(f"\n📜 Scrolling up ({amount})...")
        if self.scroll.scroll_up(amount):
            print("✅ Scrolled up")
            self.tts.speak("Scrolled up")
        else:
            print("❌ Failed to scroll")
            self.tts.speak("Failed to scroll")
    
    def _handle_scroll_top(self):
        """Handle scroll to top"""
        if not self._ensure_browser_open():
            return

        print("\n📜 Scrolling to top...")
        if self.scroll.scroll_to_top():
            print("✅ At top of page")
            self.tts.speak("At top of page")
        else:
            print("❌ Failed to scroll")
            self.tts.speak("Failed to scroll")
    
    def _handle_scroll_bottom(self):
        """Handle scroll to bottom"""
        if not self._ensure_browser_open():
            return

        print("\n📜 Scrolling to bottom...")
        if self.scroll.scroll_to_bottom():
            print("✅ At bottom of page")
            self.tts.speak("At bottom of page")
        else:
            print("❌ Failed to scroll")
            self.tts.speak("Failed to scroll")
    
    def _handle_screenshot(self):
        """Handle take screenshot"""
        if not self._ensure_browser_open():
            return

        print("\n📸 Taking screenshot...")
        self.tts.speak("Taking screenshot")

        success, filepath = self.screenshot.take_screenshot()
        if success:
            print(f"✅ Screenshot saved: {filepath}")
            self.tts.speak("Screenshot saved successfully")
        else:
            print("❌ Failed to take screenshot")
            self.tts.speak("Failed to take screenshot")
    
    def _handle_fullpage_screenshot(self):
        """Handle full page screenshot"""
        if not self._ensure_browser_open():
            return

        print("\n📸 Taking full page screenshot...")
        self.tts.speak("Taking full page screenshot. This may take a moment.")

        success, filepath = self.screenshot.take_full_page_screenshot()
        if success:
            print(f"✅ Full page screenshot saved: {filepath}")
            self.tts.speak("Full page screenshot saved successfully")
        else:
            print("❌ Failed to take full page screenshot")
            self.tts.speak("Failed to take full page screenshot")
    
    def _handle_list_screenshots(self):
        """Handle list screenshots"""
        if not self._ensure_browser_open():
            return

        print("\n📸 Counting screenshots...")
        count = self.screenshot.get_screenshot_count()
        print(f"✅ You have {count} screenshot(s)")
        self.tts.speak(f"You have {count} screenshot{'s' if count != 1 else ''}")
    
    def _handle_delete_screenshot(self):
        """Handle delete last screenshot"""
        if not self._ensure_browser_open():
            return

        print("\n🗑️ Deleting last screenshot...")

        screenshots = self.screenshot.list_screenshots()
        if not screenshots:
            print("❌ No screenshots found")
            self.tts.speak("No screenshots to delete")
            return
        
        if self.screenshot.delete_screenshot(screenshots[0]):
            remaining = self.screenshot.get_screenshot_count()
            print(f"✅ Screenshot deleted. {remaining} remaining")
            self.tts.speak(f"Screenshot deleted. {remaining} remaining")
        else:
            print("❌ Failed to delete screenshot")
            self.tts.speak("Failed to delete screenshot")
    
    def _handle_delete_all_screenshots(self):
        """Handle delete all screenshots"""
        if not self._ensure_browser_open():
            return

        count = self.screenshot.get_screenshot_count()
        
        if count == 0:
            print("❌ No screenshots to delete")
            self.tts.speak("No screenshots to delete")
            return
        
        print(f"\n⚠️ This will delete all {count} screenshot(s)")
        self.tts.speak(f"This will delete all {count} screenshots. Say yes to confirm.")
        
        confirmation = self.stt.listen()
        
        if confirmation and ('yes' in confirmation.lower() or 'confirm' in confirmation.lower()):
            print("🗑️ Deleting all screenshots...")
            deleted = self.screenshot.clear_all_screenshots()
            print(f"✅ Deleted {deleted} screenshot(s)")
            self.tts.speak(f"Deleted {deleted} screenshots")
        else:
            print("❌ Deletion cancelled")
            self.tts.speak("Deletion cancelled")
    
    def _handle_switch_tab(self):
        """Handle switch to next tab"""
        if not self._ensure_browser_open():
            return

        print("\n🗂️ Switching to next tab...")
        if self.tabs.switch_to_next_tab():
            time.sleep(1)
            title = self.browser.get_page_title()
            print(f"✅ Switched to: {title[:40]}...")
            self.tts.speak(f"Switched to {title[:30]}")
        else:
            print("❌ Only one tab open")
            self.tts.speak("Only one tab is open")
    
    def _handle_previous_tab(self):
        """Handle switch to previous tab"""
        if not self._ensure_browser_open():
            return

        print("\n🗂️ Switching to previous tab...")
        if self.tabs.switch_to_previous_tab():
            time.sleep(1)
            title = self.browser.get_page_title()
            print(f"✅ Switched to: {title[:40]}...")
            self.tts.speak(f"Switched to {title[:30]}")
        else:
            print("❌ Only one tab open")
            self.tts.speak("Only one tab is open")
    
    def _handle_close_tab(self):
        """Handle close current tab"""
        if not self._ensure_browser_open():
            return

        print("\n🗂️ Closing current tab...")
        if self.tabs.close_current_tab():
            remaining = self.tabs.get_tab_count()
            if remaining > 0:
                print(f"✅ Tab closed. {remaining} tab(s) remaining")
                self.tts.speak(f"{remaining} tabs remaining")
            else:
                print("✅ Last tab closed. Browser will close.")
                self.tts.speak("Browser closed")
                self.running = False
        else:
            print("❌ Failed to close tab")
            self.tts.speak("Failed to close tab")
    
    def _handle_new_tab(self):
        """Handle open new tab"""
        if not self._ensure_browser_open():
            return

        print("\n🗂️ Opening new tab...")
        if self.tabs.open_new_tab("https://www.google.com"):
            count = self.tabs.get_tab_count()
            print(f"✅ New tab opened. Total: {count} tab(s)")
            self.tts.speak(f"New tab opened. Total {count} tabs")
        else:
            print("❌ Failed to open new tab")
            self.tts.speak("Failed to open new tab")
    
    def _handle_close_browser(self):
        """Handle close browser"""
        if self.browser and self.browser.is_open():
            print("\n🌐 Closing browser...")
            self.browser.close_browser()
            self.tts.speak("Browser closed")
        else:
            self.tts.speak("Browser is already closed")
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n" + "=" * 80)
        print("🧹 CLEANING UP...")
        print("=" * 80)
        
        try:
            if self.browser and self.browser.is_open():
                print("   ├── Closing browser...")
                self.browser.close_browser()
                print("   ✅ Browser closed")
            
            print("\n✅ Voice Assistant stopped gracefully")
            logger.info("Voice Assistant stopped")
            
        except Exception as e:
            print(f"   ⚠️ Error during cleanup: {e}")
            logger.error(f"Cleanup error: {e}")
        
        print("=" * 80)

# ==================== ENTRY POINT ====================

def main():
    """Main entry point"""
    try:
        # Create assistant instance
        assistant = VoiceAssistant()
        
        # Start the assistant
        assistant.start()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user (Ctrl+C)")
        
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        
    finally:
        print("\n👋 Thank you for using Voice Assistant!")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    main()