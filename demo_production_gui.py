"""
Production GUI Demo - Interactive Showcase
===========================================
Demonstrates all features of the modern production-grade GUI with dual modes.

MODES:
  1. CHAT MODE: For normal voice commands and chat-like interaction
  2. PROJECT MODE: For developer tasks with setup checklist and progress tracking
"""

import sys
import time
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.production_gui import ProductionGUI
from src.core.logger import setup_logger

logger = setup_logger(__name__)


def demo_1_chat_interface():
    """Demo 1: Chat Bot Interface"""
    print("\n" + "="*80)
    print("DEMO 1: CHAT BOT INTERFACE")
    print("="*80)
    print("This shows the modern chat interface for normal voice commands\n")
    
    root = tk.Tk()
    gui = ProductionGUI(root)
    gui.show()
    
    def chat_sequence():
        time.sleep(1)
        gui.add_chat_message("hello assistant", "user")
        gui.add_chat_info("👋 Assistant woken up")
        
        time.sleep(1.5)
        gui.add_chat_message("Good morning! I'm ready to help. What would you like to do?", "assistant")
        
        time.sleep(2)
        gui.add_chat_message("search google machine learning", "user")
        
        time.sleep(1)
        gui.add_chat_message("Searching Google for 'machine learning'\n\nFound 15 relevant articles...", "assistant")
        
        time.sleep(2)
        gui.add_chat_message("summarize this page", "user")
        
        time.sleep(1)
        gui.add_chat_message("Summary:\n- Machine learning is a subset of AI\n- Uses algorithms to learn from data\n- Applications: recommendations, predictions", "assistant")
        
        time.sleep(2)
        gui.add_chat_info("💬 Chat interface supports natural conversation flow")
        
    from threading import Thread
    Thread(target=chat_sequence, daemon=True).start()
    
    root.mainloop()


def demo_2_project_setup():
    """Demo 2: Developer Task Detection & Project Mode"""
    print("\n" + "="*80)
    print("DEMO 2: DEVELOPER TASK DETECTION & PROJECT SETUP")
    print("="*80)
    print("This shows automatic mode switching when developer task is detected\n")
    
    root = tk.Tk()
    gui = ProductionGUI(root)
    gui.show()
    gui.show_chat_mode()
    
    def project_sequence():
        time.sleep(1)
        gui.add_chat_message("hey assistant", "user")
        gui.add_chat_info("👋 Assistant woken up")
        
        time.sleep(1)
        gui.add_chat_message("build a react portfolio project", "user")
        
        time.sleep(1)
        gui.add_chat_info("🚀 Developer task detected - switching to project setup...")
        gui.update_ui({"type": "mode_switch", "mode": "project"})
        gui.root.update()
        
        time.sleep(1.5)
        gui.set_project_info(
            project_name="my-portfolio",
            framework="React + Vite",
            location="C:\\Users\\Desktop\\Hackathon\\my-portfolio"
        )
        
        checklist = [
            "Check Node.js installation",
            "Create app with create-vite",
            "Install dependencies (npm install)",
            "Start development server",
            "Open project in browser"
        ]
        gui.set_checklist(checklist)
        gui.log_console("📋 Project setup plan initialized", "info")
        
        time.sleep(2)
        gui.add_step("Check Node.js installation", "running")
        gui.log_console("Checking Node.js installation...", "info")
        
        time.sleep(1.5)
        gui.add_step("Check Node.js installation", "success")
        gui.log_console("✓ Node.js v18.17.0 found", "success")
        gui.update_progress(1, 5)
        
        time.sleep(1)
        gui.add_step("Create app with create-vite", "running")
        gui.log_console("Creating React app with Vite...", "info")
        gui.log_console("npx create-vite my-portfolio --template react", "info")
        
        time.sleep(2)
        gui.add_step("Create app with create-vite", "success")
        gui.log_console("✓ Project created successfully", "success")
        gui.update_progress(2, 5)
        
        time.sleep(1)
        gui.add_step("Install dependencies", "running")
        gui.log_console("Installing npm packages...", "info")
        gui.log_console("npm install", "info")
        
        time.sleep(1.5)
        gui.log_console("⠙ Installing react@18.2.0...", "warning")
        gui.log_console("⠹ Installing react-dom@18.2.0...", "warning")
        gui.log_console("⠸ Installing vite@5.0.11...", "warning")
        
        time.sleep(1)
        gui.add_step("Install dependencies", "success")
        gui.log_console("✓ All dependencies installed (45 packages)", "success")
        gui.update_progress(3, 5)
        
        time.sleep(1)
        gui.add_step("Start development server", "running")
        gui.log_console("Starting dev server...", "info")
        gui.log_console("npm run dev", "info")
        
        time.sleep(1)
        gui.log_console("Local:   http://localhost:5173/", "info")
        gui.log_console("Network: http://192.168.1.100:5173/", "info")
        gui.add_step("Start development server", "success")
        gui.log_console("✓ Dev server running on http://localhost:5173/", "success")
        gui.update_progress(4, 5)
        
        time.sleep(1)
        gui.add_step("Open project in browser", "running")
        gui.log_console("Opening browser...", "info")
        
        time.sleep(1)
        gui.add_step("Open project in browser", "success")
        gui.log_console("✓ Project loaded in browser", "success")
        gui.update_progress(5, 5)
        
        time.sleep(1)
        gui.show_success("🎉 Project setup completed successfully!")
        gui.log_console("All steps completed! Your React portfolio is ready to develop.", "success")
        
    from threading import Thread
    Thread(target=project_sequence, daemon=True).start()
    
    root.mainloop()


def demo_3_error_recovery():
    """Demo 3: Error Handling & Recovery"""
    print("\n" + "="*80)
    print("DEMO 3: ERROR HANDLING & RECOVERY")
    print("="*80)
    print("This shows how errors are displayed and recovered\n")
    
    root = tk.Tk()
    gui = ProductionGUI(root)
    gui.show()
    gui.show_project_mode()
    
    def error_sequence():
        time.sleep(1)
        gui.set_project_info(
            project_name="test-app",
            framework="Node.js Express",
            location="C:\\Users\\Desktop\\Hackathon\\test-app"
        )
        
        checklist = ["Check Prerequisites", "Install Dependencies", "Configure Database"]
        gui.set_checklist(checklist)
        gui.log_console("📋 Project setup initialized", "info")
        
        time.sleep(1)
        gui.add_step("Check Prerequisites", "running")
        gui.log_console("Checking Node.js...")
        time.sleep(1)
        gui.add_step("Check Prerequisites", "success")
        gui.log_console("✓ Node.js v18.17.0 found", "success")
        gui.update_progress(1, 3)
        
        time.sleep(1)
        gui.add_step("Install Dependencies", "running")
        gui.log_console("Running npm install...", "info")
        time.sleep(1.5)
        gui.log_console("npm ERR! code ERESOLVE", "error")
        gui.log_console("npm ERR! ERESOLVE unable to resolve dependency tree", "error")
        gui.log_console("npm ERR! Found: express@4.18.0", "error")
        
        time.sleep(1)
        gui.show_warning("⚠️ Dependency conflict detected - attempting to resolve...")
        gui.log_console("Attempting to resolve with legacy peer deps...", "warning")
        gui.log_console("npm install --legacy-peer-deps", "info")
        
        time.sleep(2)
        gui.add_step("Install Dependencies", "success")
        gui.log_console("✓ Dependencies installed successfully", "success")
        gui.update_progress(2, 3)
        
        time.sleep(1)
        gui.add_step("Configure Database", "running")
        gui.log_console("Connecting to MongoDB...", "info")
        time.sleep(1)
        gui.log_console("CONNECTION ERROR: Unable to connect to localhost:27017", "error")
        
        time.sleep(1)
        gui.show_error("❌ Database Connection Failed - Please check MongoDB service")
        gui.log_console("Error: MongoDB service not running on port 27017", "error")
        
    from threading import Thread
    Thread(target=error_sequence, daemon=True).start()
    
    root.mainloop()


def demo_4_realtime_updates():
    """Demo 4: Real-time Updates & Live Output"""
    print("\n" + "="*80)
    print("DEMO 4: REAL-TIME UPDATES & LIVE OUTPUT")
    print("="*80)
    print("This shows real-time console streaming and progress tracking\n")
    
    root = tk.Tk()
    gui = ProductionGUI(root)
    gui.show()
    gui.show_project_mode()
    
    def realtime_sequence():
        time.sleep(1)
        gui.set_project_info(
            project_name="ai-chatbot",
            framework="Python + Flask",
            location="C:\\Users\\Desktop\\Hackathon\\ai-chatbot"
        )
        
        checklist = ["Clone Repository", "Setup Virtual Env", "Install Requirements", "Run Tests", "Start Server"]
        gui.set_checklist(checklist)
        
        time.sleep(1)
        gui.add_step("Clone Repository", "running")
        output_lines = [
            "Cloning from https://github.com/example/ai-chatbot.git",
            "remote: Counting objects: 1523, done.",
            "remote: Compressing objects: 100% (892)",
            "Receiving objects: 45% (685/1523)",
            "Receiving objects: 90% (1370/1523)",
            "Receiving objects: 100% (1523/1523)",
        ]
        for line in output_lines:
            gui.log_console(line, "info")
            time.sleep(0.3)
        
        gui.add_step("Clone Repository", "success")
        gui.log_console("✓ Repository cloned", "success")
        gui.update_progress(1, 5)
        
        time.sleep(1)
        gui.add_step("Setup Virtual Env", "running")
        gui.log_console("Creating virtual environment...", "info")
        gui.log_console("python -m venv venv", "info")
        time.sleep(1)
        gui.log_console("✓ Virtual environment created", "success")
        gui.log_console("Activating virtual environment...", "info")
        time.sleep(0.5)
        gui.add_step("Setup Virtual Env", "success")
        gui.log_console("✓ Virtual environment activated", "success")
        gui.update_progress(2, 5)
        
        time.sleep(1)
        gui.add_step("Install Requirements", "running")
        req_lines = [
            "Installing from requirements.txt...",
            "Collecting flask==2.3.2",
            "Collecting torch==2.0.1",
            "  Downloading torch-2.0.1-cp311-cp311-win_amd64.whl (2.4 GB)",
            "⠙ Downloading torch...",
            "⠹ Downloading torch...",
            "Collecting transformers==4.30.2",
            "✓ torch-2.0.1 installed",
            "✓ transformers-4.30.2 installed",
        ]
        for line in req_lines:
            gui.log_console(line, "info" if "Downloading" in line or "⠹" in line else "success" if "✓" in line else "info")
            time.sleep(0.4)
        
        gui.add_step("Install Requirements", "success")
        gui.log_console("✓ All requirements installed", "success")
        gui.update_progress(3, 5)
        
        time.sleep(1)
        gui.add_step("Run Tests", "running")
        test_lines = [
            "Running pytest...",
            "test_main.py::TestGemini::test_api_connection PASSED",
            "test_main.py::TestGemini::test_response_format PASSED",
            "test_main.py::TestChat::test_memory PASSED",
            "test_main.py::TestChat::test_error_handling PASSED",
            "==================== 4 passed in 2.34s ====================",
        ]
        for line in test_lines:
            gui.log_console(line, "success" if "PASSED" in line or "passed" in line else "info")
            time.sleep(0.3)
        
        gui.add_step("Run Tests", "success")
        gui.log_console("✓ All tests passed", "success")
        gui.update_progress(4, 5)
        
        time.sleep(1)
        gui.add_step("Start Server", "running")
        server_lines = [
            "Starting Flask server...",
            "python app.py",
            " * Running on http://127.0.0.1:5000",
            " * WARNING: This is a development server",
            "✓ Server started successfully",
        ]
        for line in server_lines:
            gui.log_console(line, "info")
            time.sleep(0.5)
        
        gui.add_step("Start Server", "success")
        gui.log_console("✓ Server running on http://127.0.0.1:5000", "success")
        gui.update_progress(5, 5)
        
        time.sleep(1)
        gui.show_success("🚀 AI Chatbot is running and ready for testing!")
        
    from threading import Thread
    Thread(target=realtime_sequence, daemon=True).start()
    
    root.mainloop()


def main():
    """Interactive demo menu"""
    print("\n" + "="*80)
    print("🎨 PRODUCTION GUI - INTERACTIVE DEMOS")
    print("="*80)
    print("\nChoose a demo to see the production GUI in action:\n")
    print("  1. Chat Bot Interface (Normal commands)")
    print("  2. Developer Task Detection & Project Setup")
    print("  3. Error Handling & Recovery")
    print("  4. Real-time Updates & Live Output")
    print("  5. Exit\n")
    
    while True:
        choice = input("Select demo (1-5): ").strip()
        
        if choice == "1":
            demo_1_chat_interface()
        elif choice == "2":
            demo_2_project_setup()
        elif choice == "3":
            demo_3_error_recovery()
        elif choice == "4":
            demo_4_realtime_updates()
        elif choice == "5":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.\n")


if __name__ == "__main__":
    main()
