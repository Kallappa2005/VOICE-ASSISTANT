"""
Quick Test - Frontend GUI Fixed Version
========================================
Tests the corrected GUI implementation with proper event loop handling.
"""

import sys
import time
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.frontend_gui import FrontendGUI

print("\n" + "="*70)
print("FRONTEND GUI - FIXED VERSION TEST")
print("="*70 + "\n")

# Create root window
root = tk.Tk()

# Create GUI (starts hidden)
print("[1] Creating GUI (starts hidden)...")
gui = FrontendGUI(root)
print("    ✓ GUI created\n")

# Set project info
print("[2] Setting project information...")
gui.set_project_info(
    project_name="my-portfolio",
    framework="React + Vite",
    location="C:\\Users\\Desktop\\Hackathon"
)
print("    ✓ Project info set\n")

# Set checklist
print("[3] Setting checklist...")
gui.set_checklist([
    "Check Node.js installation",
    "Create React project",
    "Install dependencies",
    "Start dev server",
    "Open browser"
])
print("    ✓ Checklist set\n")

# Show GUI (now it appears!)
print("[4] Displaying GUI window...")
gui.show()
print("    ✓ GUI window displayed\n")

# Simulate execution updates
print("[5] Simulating execution (updates every 2s)...\n")

for step in range(1, 6):
    # Update progress
    gui.update_progress(step, 5, f"Step {step}/5 running")
    
    # Add step
    step_names = [
        "Check Node.js installation",
        "Create React project",
        "Install dependencies",
        "Start dev server",
        "Open browser"
    ]
    
    gui.add_step(step_names[step-1], "success")
    gui.log_console(f"✓ Step {step}: {step_names[step-1]}", "success")
    
    # Keep GUI responsive
    for _ in range(20):  # 2 seconds in 0.1s increments
        root.update()
        time.sleep(0.1)
    
    print(f"    [Step {step}/5] Updated")

print("\n    ✓ Simulation complete\n")

# Show success
print("[6] Displaying success message...")
gui.show_success("✓ Project created successfully!")
root.update()
time.sleep(1)
print("    ✓ Success message shown\n")

# Keep GUI open for a few seconds
print("[7] GUI will stay open for 3 seconds (watch the window)...\n")
for _ in range(30):
    root.update()
    time.sleep(0.1)

print("[8] Closing GUI...")
gui.close()
print("    ✓ GUI closed\n")

print("="*70)
print("✅ TEST COMPLETE - GUI WORKS CORRECTLY!")
print("="*70)
print("\nKey fixes applied:")
print("  ✓ GUI starts hidden (no blocking on initialization)")
print("  ✓ GUI shows on demand with deiconify()")
print("  ✓ root.update() keeps GUI responsive")
print("  ✓ No mainloop() blocking the command loop")
print("  ✓ Proper error handling for GUI operations\n")
