"""
Voice Assistant with AI Features
Main entry point for AI-powered voice assistant
"""

import sys
import os
import time

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

logger = setup_logger(__name__)

class AIVoiceAssistant:
    """AI-Powered Voice Assistant"""
    
    def __init__(self):
        """Initialize AI voice assistant"""
        print("\n" + "=" * 80)
        print(" " * 20 + "🤖 AI VOICE ASSISTANT")
        print("=" * 80)
        print("\n🔧 Initializing components...")
        
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
        
        print("\n✅ AI Voice Assistant initialized successfully!")
        logger.info("AI Voice Assistant initialized")
    
    def start(self):
        """Start the AI voice assistant"""
        print("\n" + "=" * 80)
        print("🚀 STARTING AI VOICE ASSISTANT")
        print("=" * 80)
        
        # Greet user
        self.tts.speak("Hello! I am your AI voice assistant.")
        time.sleep(0.5)
        
        # Open browser
        print("\n📋 Opening Chrome browser...")
        self.tts.speak("Opening Chrome browser, please wait.")
        
        if not self.browser.open_chrome():
            print("❌ Failed to open browser")
            self.tts.speak("Failed to open browser. Please check your Chrome installation.")
            return False
        
        print("✅ Browser opened successfully")
        time.sleep(1)
        
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
    
    def run_command_loop(self):
        """Main command processing loop"""
        command_count = 0
        
        print("\n🎤 Listening... (Say 'Hey assistant' to wake up)\n")
        
        while self.running:
            try:
                # Listen for command
                command = self.stt.listen()
                
                if not command:
                    continue
                
                print(f"\n👤 You said: '{command}'")
                logger.info(f"User command: {command}")
                
                # Parse command
                parsed = self.parser.parse(command, context=None)
                intent = parsed['intent']
                params = parsed['params']
                
                print(f"🔍 Detected intent: {intent}")
                
                # Handle command
                self.running = self.handle_command(intent, params)
                command_count += 1
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user (Ctrl+C)")
                self.speaker.speak("Interrupted")
                break
                
            except Exception as e:
                print(f"\n❌ Error in command loop: {e}")
                logger.error(f"Command loop error: {e}")
                self.speaker.speak("Sorry, I encountered an error. Please try again.")
        
        # Cleanup
        print(f"\n📊 Total commands executed: {command_count}")
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
                return True
            
            # Must be awake for other commands
            if not self.is_awake and intent not in ['wake', 'exit']:
                return True
            
            if intent == 'sleep':
                print("\n🤖 Assistant: Going to sleep. Say 'wake up' to wake me.\n")
                self.speaker.speak("Going to sleep. Say wake up to wake me.")
                self.is_awake = False
                return True
            
            if intent == 'exit':
                print("\n🤖 Assistant: Goodbye!\n")
                self.speaker.speak_goodbye()
                return False
            
            # ==================== AI WEBPAGE ANALYSIS ====================
            
            if intent == 'analyze_current_page':
                self.ai_handler.analyze_current_page()
                return True
            
            if intent == 'summarize_page':
                self.ai_handler.summarize_page()
                return True
            
            if intent == 'get_key_points':
                self.ai_handler.get_key_points()
                return True
            
            # ==================== AI CODE ANALYSIS ====================
            
            if intent == 'analyze_code_file':
                file_path = params.get('file_path', '') if params else ''
                # Always call analyze_code_file - it handles default file internally
                self.ai_handler.analyze_code_file(file_path)
                return True
            
            if intent == 'analyze_code_clipboard':
                self.ai_handler.analyze_code_clipboard()
                return True
            
            # ==================== NAVIGATION ====================
            
            if intent == 'navigate':
                site = params.get('site', 'google') if params else 'google'
                print(f"\n🌐 Opening {site}...")
                self.speaker.speak(f"Opening {site}")
                
                success, url = self.nav.open_website(site)
                if success:
                    time.sleep(2)
                    print(f"✅ Opened: {url}")
                    self.speaker.speak("Page opened. What would you like me to do?")
                else:
                    print(f"❌ Failed to open {site}")
                    self.speaker.speak(f"Could not open {site}")
                return True
            
            if intent == 'search':
                query = params.get('query', '') if params else ''
                if not query:
                    self.speaker.speak("What would you like to search for?")
                    return True
                
                print(f"\n🔍 Searching for: {query}")
                self.speaker.speak(f"Searching for {query}")
                
                if self.nav.search_google(query):
                    time.sleep(2)
                    print("✅ Search completed")
                    self.speaker.speak("Search completed")
                else:
                    print("❌ Search failed")
                    self.speaker.speak("Search failed")
                return True
            
            # ==================== HELP ====================
            
            if 'help' in intent or intent == 'unknown':
                self.speaker.speak("Here are the available commands")
                self._show_command_menu()
                self.speaker.speak("What would you like me to do?")
                return True
            
            # Unknown command
            print(f"⚠️ Intent '{intent}' not implemented yet")
            self.speaker.speak(f"I understand {intent}, but this feature is not ready yet.")
            return True
            
        except Exception as e:
            print(f"❌ Error handling command: {e}")
            logger.error(f"Command handling error: {e}", exc_info=True)
            self.speaker.speak("Sorry, I encountered an error.")
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