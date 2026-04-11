"""
Voice Assistant with AI Features
Main entry point for AI-powered voice assistant
Implements strict linear pipeline: Voice → Text → Intent → Plan → Execute → UI + Voice Output
"""

import sys
import os
import time
import tkinter as tk
from threading import Thread
from pathlib import Path

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

# NEW: Pipeline components
from src.voice.voice import VoiceInput
from src.assistant import Assistant
from src.ui.simple_ui import UIHandler
from src.ui.production_gui import ProductionGUI  # NEW: Production-Grade Visual Frontend

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
        self.tts = TextToSpeechHandler(rate=160)
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
        self.speaker = VoiceOutput()
        print("   ✅ AI voice output ready")
        
        # Browser-dependent handlers
        self.nav = None
        self.ai_handler = None
        
        # State
        self.is_awake  = False
        self.running   = False

        # ── NEW: Pipeline Components ──────────────────────────────────────────
        print("   ├── Voice Input Handler...")
        self.voice_input = VoiceInput()
        print("   ✅ Voice input ready")
        
        print("   ├── UI Handler (Console)...")
        self.ui_handler = UIHandler()
        print("   ✅ Console UI handler ready")

        print("   ├── Frontend GUI (Visual)...")
        self.gui_root = tk.Tk()
        self.frontend_gui = ProductionGUI(root=self.gui_root)
        print("   ✅ Production GUI ready")

        # ── Agent system (developer automation) ───────────────────────────────
        print("   |-- Agent System...")
        try:
            from src.agent.intent_enhancer import IntentEnhancer
            from src.agent.task_planner    import TaskPlanner
            from src.agent.execution_manager import ExecutionManager
            self.intent_enhancer   = IntentEnhancer()
            self.task_planner      = TaskPlanner()
            self.execution_manager = ExecutionManager(tts=self.tts)
            print("   [OK] Agent system ready")
            
            # NEW: Create Assistant orchestrator - Pass FRONTEND GUI as callback
            # Frontend GUI will receive all real-time updates
            self.assistant = Assistant(
                tts=self.tts,
                ui_callback=self.frontend_gui.update_ui,  # ← Visual updates!
            )
            print("   [OK] Assistant pipeline ready")
        except Exception as _agent_exc:
            logger.warning(f"Agent system unavailable: {_agent_exc}")
            self.intent_enhancer   = None
            self.task_planner      = None
            self.execution_manager = None
            self.assistant         = None
        
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
            "[AGENT] Developer Automation": [
                "'build react project'          - Scaffold React + Vite + run",
                "'build react project my-app'   - Named React project",
                "'create node app with express' - Node.js + Express server",
                "'create node app my-api'       - Named Node project",
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
                # ─── GUI UPDATE: Keep window responsive ──────────────────────
                try:
                    if self.gui_root and self.is_awake:
                        self.gui_root.update()
                except:
                    pass
                
                # ─── STEP 1: Voice Input ─────────────────────────────────────
                # Use new VoiceInput handler instead of self.stt.listen()
                command = self.voice_input.listen()
                
                if not command:
                    continue
                
                print(f"\n[You said]: '{command}'")
                logger.info(f"User command: {command}")

                # ─── Add to chat display ──────────────────────────────────────
                if self.frontend_gui:
                    self.frontend_gui.add_chat_message(command, "user")

                # ─── STEP 2: Check if developer task ──────────────────────────
                if self.is_awake and self.assistant:
                    if self.assistant.is_developer_task(command):
                        # ─── Switch to project mode ──────────────────────────────
                        if self.frontend_gui:
                            self.frontend_gui.add_chat_info("🚀 Developer task detected - switching to project setup...")
                            self.frontend_gui.update_ui({"type": "mode_switch", "mode": "project"})
                            self.gui_root.update()
                        
                        # ─── STEP 3-7: Developer task flow (from assistant.py) ──
                        result = self.assistant.handle_developer_task(command)
                        command_count += 1
                        
                        # Sleep mode: wait before returning to listening
                        if result['success']:
                            time.sleep(8)
                        else:
                            # On error, go back to chat mode
                            if self.frontend_gui:
                                self.frontend_gui.update_ui({"type": "mode_switch", "mode": "chat"})
                                self.gui_root.update()
                        
                        continue

                # ─── STEP 5: Non-developer commands (existing flow) ───────────
                # Pass to existing CommandParser and handlers
                parsed = self.parser.parse(command, context=None)
                intent = parsed['intent']
                params = parsed['params']
                
                print(f"🔍 Detected intent: {intent}")
                
                # Handle command (existing code)
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
                    
                    # ─── NEW: Show Frontend GUI after wake-up ──────────────────
                    self._show_frontend_gui()
                    
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
            print(f"[WARN] Intent '{intent}' not implemented yet")
            self.speaker.speak(f"I understand {intent}, but this feature is not ready yet.")
            return True

        except Exception as e:
            print(f"[ERR] Error handling command: {e}")
            logger.error(f"Command handling error: {e}", exc_info=True)
            self.speaker.speak("Sorry, I encountered an error.")
            return True

    def _handle_developer_task_agent(self, command: str):
        """
        Full agent pipeline for a developer automation task.
        Called when IntentEnhancer detects a developer task in the voice command.

        Pipeline
        --------
        command -> IntentEnhancer.enhance() -> TaskPlanner.plan()
               -> ExecutionManager.show_plan() -> confirm -> execute()
        """
        try:
            print("\n[AGENT] Developer task detected")
            self.speaker.speak("Developer task detected. Analyzing command.")

            # 1. Enhance
            enhanced  = self.intent_enhancer.enhance(command)
            goal      = enhanced.get('goal', 'unknown')
            proj_name = enhanced.get('name') or 'auto-generated'
            framework = enhanced.get('framework')

            print(f"[AGENT] Goal      : {goal}")
            print(f"[AGENT] Project   : {proj_name}")
            if framework:
                print(f"[AGENT] Framework : {framework}")

            # 2. Plan
            steps = self.task_planner.plan(enhanced)
            if not steps:
                print("[WARN] Could not create a plan for this command")
                self.speaker.speak("Sorry, I could not create a plan for that task.")
                return

            # 3. Show plan
            self.execution_manager.show_plan(steps)

            # 4. Voice summary
            self.speaker.speak(
                f"I have a {len(steps)}-step plan to {goal.replace('_', ' ')}. "
                "Please check the terminal and confirm."
            )

            # 5. Confirm
            if not self.execution_manager.confirm():
                self.speaker.speak("Execution cancelled.")
                return

            # 6. Execute
            self.speaker.speak("Starting execution. This may take a few minutes.")
            result = self.execution_manager.execute(steps)

            if result['success']:
                proj = result.get('project_path', '')
                print(f"[DONE] Project ready: {proj}")
                self.speaker.speak("Your project is ready and running.")
            else:
                err = result.get('error', 'Unknown error')
                print(f"[FAIL] {err}")
                self.speaker.speak(
                    f"Execution stopped after {result['completed_steps']} steps. "
                    "Check the terminal for details."
                )

        except Exception as exc:
            logger.error(f"Developer task error: {exc}", exc_info=True)
            print(f"[ERR] Developer task error: {exc}")
            self.speaker.speak("Sorry, I encountered an error with the developer task.")

    # ─────────────────────────────────────────────────────────────────────────
    # NEW: Frontend GUI Management
    # ─────────────────────────────────────────────────────────────────────────

    def _show_frontend_gui(self):
        """Display frontend GUI in chat mode (shows window, doesn't block)"""
        try:
            self.frontend_gui.show()
            self.frontend_gui.show_chat_mode()  # Ensure we show chat mode first
            self.frontend_gui.add_chat_info("👋 Assistant is ready! Try commands like: 'build react project', 'search google python', etc.")
            self.gui_root.update()
            logger.info("Production GUI displayed in chat mode")
        except Exception as e:
            logger.error(f"GUI display error: {e}")

    def _update_gui_for_developer_task(self, enhanced: dict):
        """Update GUI with developer task information"""
        proj_name = enhanced.get("name", "my-app")
        goal = enhanced.get("goal", "unknown")
        framework = "React + Vite" if "react" in goal.lower() else "Node.js"
        
        location = str(Path.home() / "Desktop" / "Hackathon")
        
        self.frontend_gui.set_project_info(
            project_name=proj_name,
            framework=framework,
            location=location
        )
        
        # Default checklist
        checklist = [
            "✓ Check Node.js installation",
            "✓ Create project with Vite",
            "✓ Install dependencies",
            "✓ Start development server",
            "✓ Open project in browser",
        ]
        self.frontend_gui.set_checklist(checklist)
        self.frontend_gui.log_console(f"📋 Project setup plan ready", "info")

    def handle_checklist_command(self, command: str):
        """
        Handle voice commands for checklist modification
        
        Examples:
            "add install typescript"
            "remove start development server"
            "edit create project"
        """
        command_lower = command.lower().strip()
        
        # Add item
        if command_lower.startswith("add "):
            item = command_lower.replace("add ", "").strip()
            self.frontend_gui.checklist_items.append(f"✓ {item}")
            self.frontend_gui.set_checklist(self.frontend_gui.checklist_items)
            self.frontend_gui.log_console(f"✓ Added: {item}", "success")
            self.speaker.speak(f"Added {item} to checklist")
            return True
        
        # Remove item
        elif command_lower.startswith("remove "):
            item_text = command_lower.replace("remove ", "").strip()
            # Find and remove matching item
            for i, item in enumerate(self.frontend_gui.checklist_items):
                if item_text.lower() in item.lower():
                    removed = self.frontend_gui.checklist_items.pop(i)
                    self.frontend_gui.set_checklist(self.frontend_gui.checklist_items)
                    self.frontend_gui.log_console(f"✗ Removed: {removed}", "warning")
                    self.speaker.speak(f"Removed {item_text}")
                    return True
            self.speaker.speak(f"Could not find {item_text} in checklist")
            return False
        
        # Clear all
        elif "clear" in command_lower:
            self.frontend_gui.set_checklist([])
            self.frontend_gui.log_console("Checklist cleared", "warning")
            self.speaker.speak("Checklist cleared")
            return True
        
        # Show checklist
        elif "show" in command_lower or "list" in command_lower:
            self.frontend_gui.log_console("Current checklist:", "info")
            for item in self.frontend_gui.checklist_items:
                self.frontend_gui.log_console(f"  {item}", "info")
            self.speaker.speak("Checklist displayed on screen")
            return True
        
        return False

    def cleanup(self):
        """Cleanup resources"""
        print("\n" + "=" * 80)
        print("🧹 CLEANING UP...")
        print("=" * 80)
        
        try:
            print("   ├── Closing GUI...")
            if hasattr(self, 'frontend_gui') and self.frontend_gui:
                self.frontend_gui.close()
            if hasattr(self, 'gui_root') and self.gui_root:
                self.gui_root.quit()
            print("   ✅ GUI closed")
            
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