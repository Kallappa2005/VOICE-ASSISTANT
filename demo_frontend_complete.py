"""
COMPLETE DEMO - Frontend GUI Integration
=========================================
Demonstrates:
  1. Frontend GUI appearing after assistant wake-up
  2. Real-time progress updates from pipeline
  3. Interactive checklist (add/edit/delete)
  4. Live console output streaming
  5. Voice command integration

Usage:
    python demo_frontend_complete.py
    
    Say: "hey assistant"
    Say: "build react project my portfolio"
    
    The GUI will display:
    - Project information (name, framework, location)
    - Execution plan checklist
    - Real-time step progress (1/5, 2/5, etc.)
    - Live npm output in console
    - Success/failure messages
"""

import sys
import tkinter as tk
from pathlib import Path
import time
from threading import Thread

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.frontend_gui import FrontendGUI
from src.assistant import Assistant
from src.agent.intent_enhancer import IntentEnhancer
from src.agent.task_planner import TaskPlanner
from src.core.logger import setup_logger

logger = setup_logger(__name__)


def demo_basic_ui():
    """Demo 1: Basic GUI display and interaction"""
    print("\n" + "=" * 80)
    print("DEMO 1: Basic Frontend GUI Display")
    print("=" * 80)

    root = tk.Tk()
    gui = FrontendGUI(root)

    # Set project info
    gui.set_project_info(
        project_name="my-portfolio",
        framework="React + Vite",
        location="C:\\Users\\Desktop\\Hackathon",
    )

    # Set checklist
    checklist = [
        "✓ Check Node.js installation",
        "✓ Create React project with Vite",
        "✓ Install dependencies",
        "✓ Start development server",
        "✓ Open project in browser",
    ]
    gui.set_checklist(checklist)

    # Simulate background updates
    def simulate_execution():
        time.sleep(2)

        gui.log_console("🎯 Starting execution...", "info")
        gui.update_progress(0, 5, "Initializing...")

        # Step 1
        time.sleep(1)
        gui.add_step("Check Node.js installation", "running")
        gui.log_console("▶ Step 1: Checking Node.js...", "info")

        time.sleep(2)
        gui.add_step("Check Node.js installation", "success")
        gui.log_console("✓ Node.js v22.12.0 found", "success")
        gui.update_progress(1, 5, "Step 1 complete")

        # Step 2
        time.sleep(1)
        gui.add_step("Create React project with Vite", "running")
        gui.log_console("▶ Step 2: Creating React project...", "info")
        gui.log_console("📦 Running: npm create vite@latest my -- --template react", "info")

        time.sleep(3)
        gui.add_step("Create React project with Vite", "success")
        gui.log_console("✓ React project created", "success")
        gui.update_progress(2, 5, "Step 2 complete")

        # Step 3
        time.sleep(1)
        gui.add_step("Install dependencies", "running")
        gui.log_console("▶ Step 3: Installing dependencies...", "info")
        gui.log_console("npm install... (streaming live output)", "info")

        time.sleep(3)
        gui.add_step("Install dependencies", "success")
        gui.log_console("✓ Dependencies installed", "success")
        gui.update_progress(3, 5, "Step 3 complete")

        # Step 4
        time.sleep(1)
        gui.add_step("Start development server", "running")
        gui.log_console("▶ Step 4: Starting dev server...", "info")

        time.sleep(2)
        gui.add_step("Start development server", "success")
        gui.log_console("✓ Dev server started on port 5173", "success")
        gui.update_progress(4, 5, "Step 4 complete")

        # Step 5
        time.sleep(1)
        gui.add_step("Open project in browser", "running")
        gui.log_console("▶ Step 5: Opening browser...", "info")

        time.sleep(1)
        gui.add_step("Open project in browser", "success")
        gui.log_console("✓ Browser opened to http://localhost:5173", "success")
        gui.update_progress(5, 5, "All steps complete")

        time.sleep(1)
        gui.show_success("✓ Project setup complete! Your React project is ready at C:\\...\\Hackathon\\my")

    Thread(target=simulate_execution, daemon=True).start()

    gui.show()
    gui.run()


def demo_with_assistant_pipeline():
    """
    Demo 2: Complete pipeline with Assistant
    Shows Assistant → TaskPlanner → ExecutionManager → GUI updates
    """
    print("\n" + "=" * 80)
    print("DEMO 2: Complete Assistant Pipeline with GUI")
    print("=" * 80)

    # Create GUI
    root = tk.Tk()
    gui = FrontendGUI(root)

    # Create Assistant with GUI callback
    class MockTTS:
        def speak(self, text):
            gui.log_console(f"🔊 TTS: {text}", "info")

    tts = MockTTS()
    assistant = Assistant(tts=tts, ui_callback=gui.update_ui)

    gui.show()
    gui.log_console("Assistant initialized with GUI", "info")

    # Simulate a developer task
    def process_task():
        time.sleep(2)
        
        command = "build react project my portfolio"
        gui.log_console(f"🎤 Command: {command}", "info")
        
        # Run assistant task
        result = assistant.handle_developer_task(command)
        
        # Display result
        if result['success']:
            gui.show_success(
                f"Project created at {result.get('project_path', 'N/A')}"
            )
        else:
            gui.show_error(f"Error: {result.get('error', 'Unknown error')}")

    Thread(target=process_task, daemon=True).start()

    gui.run()


def demo_checklist_voice_commands():
    """
    Demo 3: Interactive checklist with voice-style commands
    Shows how to modify checklist via commands
    """
    print("\n" + "=" * 80)
    print("DEMO 3: Interactive Checklist Modifications")
    print("=" * 80)

    root = tk.Tk()
    gui = FrontendGUI(root)

    gui.set_project_info(
        project_name="my-app",
        framework="Node.js + Express",
        location="C:\\Users\\Desktop\\Hackathon",
    )

    initial_items = [
        "✓ Check Node.js installation",
        "✓ Create project folder",
        "✓ Initialize npm project",
        "✓ Install Express",
        "✓ Create server.js",
    ]
    gui.set_checklist(initial_items)

    gui.show()

    # Simulate voice commands to modify checklist
    def modify_checklist():
        time.sleep(2)

        # Add item
        gui.log_console("🎤 Voice: add install typescript", "info")
        gui.checklist_items.append("✓ install TypeScript")
        gui.set_checklist(gui.checklist_items)
        gui.log_console("✓ Added: install TypeScript", "success")

        time.sleep(2)

        # Remove item
        gui.log_console("🎤 Voice: remove Create server.js", "info")
        gui.checklist_items = [
            i for i in gui.checklist_items if "Create server" not in i
        ]
        gui.set_checklist(gui.checklist_items)
        gui.log_console("✗ Removed: Create server.js", "warning")

        time.sleep(2)

        # Show list
        gui.log_console("🎤 Voice: show checklist", "info")
        gui.log_console("📋 Current checklist:", "info")
        for item in gui.checklist_items:
            gui.log_console(f"  {item}", "info")

    Thread(target=modify_checklist, daemon=True).start()

    gui.run()


def demo_error_recovery():
    """Demo 4: Error handling and recovery scenarios"""
    print("\n" + "=" * 80)
    print("DEMO 4: Error Handling & Recovery")
    print("=" * 80)

    root = tk.Tk()
    gui = FrontendGUI(root)

    gui.set_project_info(
        project_name="demo-project",
        framework="React + Vite",
        location="C:\\Users\\Desktop\\Hackathon",
    )

    gui.set_checklist(
        [
            "✓ Check Node.js",
            "✓ Create project",
            "✓ Install dependencies",
            "✓ Start dev server",
            "✓ Open browser",
        ]
    )

    gui.show()

    def simulate_failure():
        time.sleep(2)

        gui.add_step("Check Node.js", "success")
        gui.log_console("✓ Node.js found", "success")
        gui.update_progress(1, 5)

        time.sleep(1)

        gui.add_step("Create project", "running")
        gui.log_console("▶ Creating project...", "info")

        time.sleep(2)

        gui.show_error("Network error: npm registry timeout")
        gui.log_console("✗ ERROR: npm registry timeout", "error")
        gui.log_console("[RETRY] Retrying in 2 seconds...", "warning")
        gui.add_step("Create project", "running")

        time.sleep(2)

        gui.log_console("✓ Retry successful!", "success")
        gui.add_step("Create project", "success")
        gui.update_progress(2, 5)

        time.sleep(1)

        gui.show_success("Project recovered and creation completed successfully!")

    Thread(target=simulate_failure, daemon=True).start()

    gui.run()


def print_menu():
    """Print demo menu"""
    print("\n" + "=" * 80)
    print("🎨 FRONTEND GUI - COMPLETE DEMO SUITE")
    print("=" * 80)
    print("\nAvailable Demos:")
    print("  1. Basic UI Display & Interaction")
    print("  2. Complete Assistant Pipeline (Intent → Plan → Execute)")
    print("  3. Interactive Checklist Voice Commands")
    print("  4. Error Handling & Recovery")
    print("  5. Run All Demos Sequentially")
    print("  0. Exit")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    while True:
        print_menu()
        choice = input("Enter choice (0-5): ").strip()

        if choice == "1":
            demo_basic_ui()
        elif choice == "2":
            try:
                demo_with_assistant_pipeline()
            except Exception as e:
                print(f"Error: {e}")
                logger.error(f"Demo 2 error: {e}", exc_info=True)
        elif choice == "3":
            demo_checklist_voice_commands()
        elif choice == "4":
            demo_error_recovery()
        elif choice == "5":
            print("\n📺 Running all demos...\n")
            demo_basic_ui()
            demo_checklist_voice_commands()
            demo_error_recovery()
            print("\n✅ All demos completed!")
            break
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
