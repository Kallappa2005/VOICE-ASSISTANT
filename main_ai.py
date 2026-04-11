"""
Voice Assistant with AI Features
Main entry point for AI-powered voice assistant

Supports:
- Command line usage: python main_ai.py
- Launcher with GUI: python launcher.py --mode ai
"""

import sys
import os
import time
from threading import Thread

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.speech.text_to_speech_handler import TextToSpeechHandler
from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.browser.browser_controller import BrowserController
from src.browser.navigation import Navigation
from src.commands.command_parser import CommandParser
from src.core.logger import setup_logger

# AI imports
from src.ai.voice_output import VoiceOutput
from src.ai.ai_commands import AICommandHandler

# GUI imports (optional)
try:
    import tkinter as tk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

logger = setup_logger(__name__)

class AIVoiceAssistant:
    """AI-Powered Voice Assistant"""
    
    def __init__(self, gui=None):
        """
        Initialize AI voice assistant
        
        Args:
            gui: Optional AIAssistantGUI instance (passed from launcher)
        """
        print("\n" + "=" * 80)
        print(" " * 20 + "🤖 AI VOICE ASSISTANT")
        print("=" * 80)
        print("\n🔧 Initializing components...")
        
        # GUI (optional)
        self.gui = gui
        
        # Core components
        print("   ├── Speech Recognition...")
        self.tts = TextToSpeechHandler(rate=210)
        self.stt = SpeechRecognitionHandler()
        print("   ✅ Speech module ready")
        
        print("   ├── Browser Controller...")
        self.browser = BrowserController()
        print("   ✅ Browser controller ready")
        
        print("   ├── Command Parser...")
        self.parser = CommandParser()
        print("   ✅ Command parser ready")
        
        # AI components
        print("   ├── AI Voice Output...")
        self.speaker = VoiceOutput(rate=210)
        print("   ✅ AI voice output ready")
        
        # Browser-dependent handlers
        self.nav = None
        self.ai_handler = None
        
        # State
        self.is_awake = False
        self.running = False
        
        # GUI availability
        if self.gui is None and GUI_AVAILABLE:
            try:
                from src.ui.ai_gui import AIAssistantGUI
                self.gui = AIAssistantGUI(assistant=self)
                print("   ├── GUI Interface...")
                print("   ✅ GUI ready")
            except Exception as e:
                print(f"   ⚠️ GUI not available: {e}")
                self.gui = None
        
        print("\n✅ AI Voice Assistant initialized successfully!")
        logger.info("AI Voice Assistant initialized")
    
    def start(self):
        """Start the AI voice assistant"""
        print("\n" + "=" * 80)
        print("🚀 STARTING AI VOICE ASSISTANT")
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
            self.tts.speak("Hello! I am your AI voice assistant.")
            time.sleep(0.5)
            
            # Note: Browser will open on first browser-related command.
            # Do not open it automatically on startup.
            
            # Initialize browser-dependent handlers
            print("\n🔧 Initializing AI features...")
            self.nav = Navigation(self.browser)
            self.ai_handler = AICommandHandler(self.browser)
            print("✅ AI features initialized")
            
            # Ready message
            print("\n" + "=" * 80)
            print("✅ AI VOICE ASSISTANT IS READY!")
            print("=" * 80)
            
            self.speaker.speak("I am ready! Say hey assistant to wake me up.")
            
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
            "🎤 Wake/Sleep": [
                "'hey assistant' / 'wake up' - Wake assistant",
                "'sleep' - Put assistant to sleep",
                "'exit' / 'goodbye' - Quit assistant",
            ],
            "🌐 Navigation": [
                "'open wikipedia artificial intelligence' - Open website",
                "'search for [query]' - Search on Google",
            ],
            "🤖 AI Webpage Analysis": [
                "'analyze this page' - Full page analysis",
                "'summarize this page' - Quick summary",
                "'give me key points' - Extract key points",
            ],
            "💻 AI Code Analysis": [
                "'analyze code from file' - Analyze test_code.py (SQL, XSS, complexity)",
                "'check code clipboard' - Analyze code from clipboard",
            ],
            "⚙️ System": [
                "'help' - Show this menu",
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
        self.speaker.speak("Here are the available commands")
        
        if self.gui:
            self.gui.log_console("\n" + "=" * 80, "info")
            self.gui.log_console("📋 AVAILABLE COMMANDS:", "info")
            self.gui.log_console("=" * 80, "info")
        
        commands = {
            "🎤 Wake/Sleep": [
                "'hey assistant' / 'wake up' - Wake assistant",
                "'sleep' - Put assistant to sleep",
                "'exit' / 'goodbye' - Quit assistant",
            ],
            "🌐 Navigation": [
                "'open wikipedia artificial intelligence' - Open website",
                "'search for [query]' - Search on Google",
            ],
            "🤖 AI Webpage Analysis": [
                "'analyze this page' - Full page analysis",
                "'summarize this page' - Quick summary",
                "'give me key points' - Extract key points",
            ],
            "💻 AI Code Analysis": [
                "'analyze code from file' - Analyze test_code.py (SQL, XSS, complexity)",
                "'check code clipboard' - Analyze code from clipboard",
            ],
            "⚙️ System": [
                "'help' - Show this menu",
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
        self.speaker.speak("What would you like me to do?")
    
    def run_command_loop(self):
        """Main command processing loop"""
        command_count = 0
        
        print("\n🎤 Listening... (Say 'Hey assistant' to wake up)\n")
        
        if self.gui:
            self.gui.log_message("🎤 Listening... Say 'Hey assistant' to wake up", level="info")
        
        while self.running:
            try:
                # Listen for command
                command = self.stt.listen()
                
                if not command:
                    continue
                
                print(f"\n👤 You said: '{command}'")
                logger.info(f"User command: {command}")
                
                if self.gui:
                    self.gui.log_message(f"👤 You: {command}", level="info")
                
                # Parse command
                parsed = self.parser.parse(command, context=None)
                intent = parsed['intent']
                params = parsed['params']
                
                print(f"🔍 Detected intent: {intent}")
                logger.info(f"Detected intent: {intent}")
                
                if self.gui:
                    self.gui.log_message(f"🔍 Intent: {intent}", level="info")
                
                # Handle command
                self.running = self.handle_command(intent, params)
                command_count += 1
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user (Ctrl+C)")
                logger.warning("Interrupted by user")
                self.speaker.speak("Interrupted")
                
                if self.gui:
                    self.gui.log_message("⚠️ Interrupted by user", level="warning")
                
                break
                
            except Exception as e:
                print(f"\n❌ Error in command loop: {e}")
                logger.error(f"Command loop error: {e}")
                self.speaker.speak("Sorry, I encountered an error. Please try again.")
                
                if self.gui:
                    self.gui.log_message(f"❌ Error: {e}", level="error")
        
        # Cleanup
        print(f"\n📊 Total commands executed: {command_count}")
        logger.info(f"Total commands: {command_count}")
        
        if self.gui:
            self.gui.log_message(f"📊 Total commands: {command_count}", level="success")
        
        self.cleanup()
    
    def handle_command(self, intent, params):
        """
        Handle parsed command
        
        Args:
            intent: Command intent
            params: Command parameters
        
        Returns:
            bool: Continue running?
        """
        try:
            # ==================== WAKE/SLEEP/EXIT ====================
            
            if intent == 'wake':
                if not self.is_awake:
                    self.is_awake = True
                    print("\n🤖 Assistant: Hello! I'm ready. How can I help you?\n")
                    self.speaker.speak_greeting()
                    
                    if self.gui:
                        self.gui.log_message("🤖 Assistant: Waking up...", level="success")
                        self.gui._update_status_awake()
                
                return True
            
            # Must be awake for other commands
            if not self.is_awake and intent not in ['wake', 'exit']:
                if self.gui:
                    self.gui.log_message("⚠️ Assistant is sleeping. Say 'wake up' to wake me.", level="warning")
                return True
            
            if intent == 'sleep':
                print("\n🤖 Assistant: Going to sleep. Say 'wake up' to wake me.\n")
                self.speaker.speak("Going to sleep. Say wake up to wake me.")
                self.is_awake = False
                
                if self.gui:
                    self.gui.log_message("😴 Assistant: Going to sleep...", level="info")
                    self.gui._update_status_sleeping()
                
                return True
            
            if intent == 'exit':
                print("\n🤖 Assistant: Goodbye!\n")
                self.speaker.speak_goodbye()
                
                if self.gui:
                    self.gui.log_message("👋 Assistant: Goodbye!", level="success")
                
                return False
            
            # ==================== AI WEBPAGE ANALYSIS ====================
            
            if intent == 'analyze_current_page':
                if not self._ensure_browser_open():
                    return True
                if self.gui:
                    self.gui.log_message("🔍 Analyzing page...", level="info")
                self.ai_handler.analyze_current_page()
                return True
            
            if intent == 'summarize_page':
                if not self._ensure_browser_open():
                    return True
                if self.gui:
                    self.gui.log_message("📝 Summarizing page...", level="info")
                self.ai_handler.summarize_page()
                return True
            
            if intent == 'get_key_points':
                if not self._ensure_browser_open():
                    return True
                if self.gui:
                    self.gui.log_message("✨ Extracting key points...", level="info")
                self.ai_handler.get_key_points()
                return True
            
            # ==================== AI CODE ANALYSIS ====================
            
            if intent == 'analyze_code_file':
                file_path = params.get('file_path', '') if params else ''
                if self.gui:
                    self.gui.log_message("💻 Analyzing code file...", level="info")
                # Always call analyze_code_file - it handles default file internally
                self.ai_handler.analyze_code_file(file_path)
                return True
            
            if intent == 'analyze_code_clipboard':
                if self.gui:
                    self.gui.log_message("💻 Analyzing code from clipboard...", level="info")
                self.ai_handler.analyze_code_clipboard()
                return True
            
            # ==================== NAVIGATION ====================
            
            if intent == 'navigate':
                if not self._ensure_browser_open():
                    return True
                site = params.get('site', 'google') if params else 'google'
                print(f"\n🌐 Opening {site}...")
                self.speaker.speak(f"Opening {site}")
                
                if self.gui:
                    self.gui.log_message(f"🌐 Opening {site}...", level="info")
                
                success, url = self.nav.open_website(site)
                if success:
                    time.sleep(2)
                    print(f"✅ Opened: {url}")
                    self.speaker.speak("Page opened. What would you like me to do?")
                    
                    if self.gui:
                        self.gui.log_message(f"✅ Opened: {url}", level="success")
                else:
                    print(f"❌ Failed to open {site}")
                    self.speaker.speak(f"Could not open {site}")
                    
                    if self.gui:
                        self.gui.log_message(f"❌ Failed to open {site}", level="error")
                
                return True
            
            if intent == 'search':
                query = params.get('query', '') if params else ''
                if not query:
                    self.speaker.speak("What would you like to search for?")
                    
                    if self.gui:
                        self.gui.log_message("🔍 What would you like to search for?", level="info")
                    
                    return True

                if not self._ensure_browser_open():
                    return True
                
                print(f"\n🔍 Searching for: {query}")
                self.speaker.speak(f"Searching for {query}")
                
                if self.gui:
                    self.gui.log_message(f"🔍 Searching for: {query}", level="info")
                
                if self.nav.search_google(query):
                    time.sleep(2)
                    print("✅ Search completed")
                    self.speaker.speak("Search completed")
                    
                    if self.gui:
                        self.gui.log_message("✅ Search completed", level="success")
                else:
                    print("❌ Search failed")
                    self.speaker.speak("Search failed")
                    
                    if self.gui:
                        self.gui.log_message("❌ Search failed", level="error")
                
                return True
            
            # ==================== HELP ====================
            
            if intent == 'help':
                self._handle_help()
                return True
            
            # Unknown command
            print(f"⚠️ Intent '{intent}' not implemented yet")
            self.speaker.speak(f"I understand {intent}, but this feature is not ready yet.")
            
            if self.gui:
                self.gui.log_message(f"⚠️ Intent '{intent}' not implemented", level="warning")
            
            return True
            
        except Exception as e:
            print(f"❌ Error handling command: {e}")
            logger.error(f"Command handling error: {e}", exc_info=True)
            self.speaker.speak("Sorry, I encountered an error.")
            
            if self.gui:
                self.gui.log_message(f"❌ Error: {e}", level="error")
            
            return True

    def _ensure_browser_open(self):
        """Ensure browser is open before browser-dependent commands."""
        if self.browser.is_open():
            return True

        print("\n📋 Opening Chrome browser...")
        self.speaker.speak("Opening Chrome browser, please wait.")

        if not self.browser.open_chrome():
            print("❌ Failed to open browser")
            self.speaker.speak("Failed to open browser. Please check your Chrome installation.")
            if self.gui:
                self.gui.log_message("❌ Failed to open browser", level="error")
            return False

        print("✅ Browser opened successfully")
        time.sleep(1)
        return True
    
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
            
            print("\n✅ AI Voice Assistant stopped gracefully")
            logger.info("AI Voice Assistant stopped")
            
        except Exception as e:
            print(f"   ⚠️ Error during cleanup: {e}")
            logger.error(f"Cleanup error: {e}")
        
        print("=" * 80)

# ==================== ENTRY POINT ====================

def main():
    """Main entry point"""
    try:
        # Create assistant instance
        assistant = AIVoiceAssistant()
        
        # Start the assistant
        assistant.start()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user (Ctrl+C)")
        
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        
    finally:
        print("\n👋 Thank you for using AI Voice Assistant!")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    main()