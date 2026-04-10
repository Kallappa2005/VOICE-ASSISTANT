"""
Frontend GUI - Visual Progress UI for Developer Assistant
=========================================================
Displays real-time progress, execution steps, and interactive project checklist.

Features:
  - Floating window that appears after wake-up
  - Real-time step progress display
  - Interactive project checklist (add/edit/delete/confirm)
  - Voice command integration for checklist modifications
  - Live command streaming output
  - Success/failure visual feedback
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from threading import Thread
import time
from pathlib import Path
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class FrontendGUI:
    """Visual Frontend UI for Developer Assistant"""

    def __init__(self, root=None):
        """
        Initialize Frontend GUI

        Args:
            root: Tkinter root window (creates new if None)
        """
        self.root = root or tk.Tk()
        self.root.title("🤖 Developer Assistant - Project Setup")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")

        # Make window stay on top
        self.root.attributes("-topmost", True)
        
        # Start hidden - will show after wake-up
        self.root.withdraw()

        # UI State
        self.current_step = 0
        self.total_steps = 0
        self.checklist_items = []
        self.project_info = {}
        self.is_executing = False

        # Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#4CAF50"
        self.warning_color = "#FFA500"
        self.error_color = "#FF6B6B"
        self.success_color = "#00FF00"

        # Build UI
        self._build_ui()
        logger.info("FrontendGUI initialized")

    # ─────────────────────────────────────────────────────────────────────────
    # UI Construction
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Build the main UI layout"""
        # ──── Header ────────────────────────────────────────────────────────
        header_frame = tk.Frame(self.root, bg=self.accent_color, height=60)
        header_frame.pack(fill=tk.X, pady=0)

        title_label = tk.Label(
            header_frame,
            text="🚀 Project Setup Assistant",
            font=("Arial", 16, "bold"),
            fg="white",
            bg=self.accent_color,
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # ──── Main Container (Horizontal Split) ────────────────────────────
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ────── Left Panel: Project Info + Checklist ──────────────────────
        left_panel = tk.Frame(container, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Project Info Section
        self._build_project_info_section(left_panel)

        # Checklist Section
        self._build_checklist_section(left_panel)

        # ────── Right Panel: Progress Steps + Output ──────────────────────
        right_panel = tk.Frame(container, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Execution Progress
        self._build_progress_section(right_panel)

        # Live Output Console
        self._build_console_section(right_panel)

        # ──── Footer ────────────────────────────────────────────────────────
        footer_frame = tk.Frame(self.root, bg="#2d2d2d", height=50)
        footer_frame.pack(fill=tk.X, pady=0)

        # Buttons
        btn_frame = tk.Frame(footer_frame, bg="#2d2d2d")
        btn_frame.pack(side=tk.LEFT, padx=20, pady=10)

        self.btn_start = tk.Button(
            btn_frame,
            text="▶ Start Execution",
            command=self._on_start_clicked,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_edit = tk.Button(
            btn_frame,
            text="✏️ Edit Checklist",
            command=self._on_edit_clicked,
            bg=self.warning_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
        )
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        self.btn_cancel = tk.Button(
            btn_frame,
            text="✕ Cancel",
            command=self._on_cancel_clicked,
            bg=self.error_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
        )
        self.btn_cancel.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(
            footer_frame,
            text="Ready to start...",
            fg=self.accent_color,
            bg="#2d2d2d",
            font=("Arial", 10),
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=10)

    def _build_project_info_section(self, parent):
        """Build project information display section"""
        header = tk.Label(
            parent,
            text="📋 Project Information",
            font=("Arial", 12, "bold"),
            fg=self.accent_color,
            bg=self.bg_color,
        )
        header.pack(anchor="w", pady=(0, 8))

        frame = tk.Frame(parent, bg="#2d2d2d", relief=tk.SUNKEN, bd=1)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Project Name
        tk.Label(
            frame,
            text="Project Name:",
            font=("Arial", 10, "bold"),
            fg=self.fg_color,
            bg="#2d2d2d",
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.label_project_name = tk.Label(
            frame,
            text="my-portfolio",
            font=("Arial", 10),
            fg=self.accent_color,
            bg="#2d2d2d",
        )
        self.label_project_name.pack(anchor="w", padx=20, pady=(0, 5))

        # Framework
        tk.Label(
            frame,
            text="Framework:",
            font=("Arial", 10, "bold"),
            fg=self.fg_color,
            bg="#2d2d2d",
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.label_framework = tk.Label(
            frame,
            text="React + Vite",
            font=("Arial", 10),
            fg=self.accent_color,
            bg="#2d2d2d",
        )
        self.label_framework.pack(anchor="w", padx=20, pady=(0, 5))

        # Location
        tk.Label(
            frame,
            text="Location:",
            font=("Arial", 10, "bold"),
            fg=self.fg_color,
            bg="#2d2d2d",
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.label_location = tk.Label(
            frame,
            text="C:\\Users\\Desktop\\Hackathon",
            font=("Arial", 9),
            fg=self.accent_color,
            bg="#2d2d2d",
            wraplength=300,
        )
        self.label_location.pack(anchor="w", padx=20, pady=(0, 10))

    def _build_checklist_section(self, parent):
        """Build interactive project checklist section"""
        header = tk.Label(
            parent,
            text="✅ Setup Checklist",
            font=("Arial", 12, "bold"),
            fg=self.accent_color,
            bg=self.bg_color,
        )
        header.pack(anchor="w", pady=(10, 8))

        # Scrollable checklist frame
        canvas = tk.Canvas(parent, bg="#2d2d2d", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2d2d2d")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.checklist_frame = scrollable_frame

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_progress_section(self, parent):
        """Build execution progress display section"""
        header = tk.Label(
            parent,
            text="⚙️ Execution Progress",
            font=("Arial", 12, "bold"),
            fg=self.accent_color,
            bg=self.bg_color,
        )
        header.pack(anchor="w", pady=(0, 8))

        # Progress container
        frame = tk.Frame(parent, bg="#2d2d2d", relief=tk.SUNKEN, bd=1)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            frame,
            variable=self.progress_var,
            maximum=100,
            length=300,
            mode="determinate",
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Progress text
        self.progress_text = tk.Label(
            frame,
            text="0/0 steps completed",
            font=("Arial", 9),
            fg=self.accent_color,
            bg="#2d2d2d",
        )
        self.progress_text.pack(anchor="w", padx=10, pady=(0, 10))

        # Steps container
        steps_frame = tk.Frame(parent, bg=self.bg_color)
        steps_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        tk.Label(
            steps_frame,
            text="📝 Steps:",
            font=("Arial", 10, "bold"),
            fg=self.accent_color,
            bg=self.bg_color,
        ).pack(anchor="w")

        # Scrollable steps list
        canvas = tk.Canvas(steps_frame, bg="#2d2d2d", highlightthickness=0, height=150)
        scrollbar = ttk.Scrollbar(steps_frame, orient="vertical", command=canvas.yview)
        steps_scrollable = tk.Frame(canvas, bg="#2d2d2d")

        steps_scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=steps_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.steps_frame = steps_scrollable

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_console_section(self, parent):
        """Build live output console section"""
        header = tk.Label(
            parent,
            text="💻 Live Output",
            font=("Arial", 12, "bold"),
            fg=self.accent_color,
            bg=self.bg_color,
        )
        header.pack(anchor="w", pady=(0, 8))

        # Console output
        self.console = scrolledtext.ScrolledText(
            parent,
            height=8,
            bg="#000000",
            fg="#00FF00",
            font=("Courier", 9),
            wrap=tk.WORD,
        )
        self.console.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colored output
        self.console.tag_configure("error", foreground="#FF6B6B")
        self.console.tag_configure("success", foreground="#00FF00")
        self.console.tag_configure("warning", foreground="#FFA500")
        self.console.tag_configure("info", foreground="#87CEEB")

    # ─────────────────────────────────────────────────────────────────────────
    # Public API to Update UI
    # ─────────────────────────────────────────────────────────────────────────

    def set_project_info(self, project_name: str, framework: str, location: str):
        """Set project information display"""
        self.project_info = {
            "name": project_name,
            "framework": framework,
            "location": location,
        }
        self.label_project_name.config(text=project_name)
        self.label_framework.config(text=framework)
        self.label_location.config(text=location)

    def set_checklist(self, items: list[str]):
        """
        Set checklist items

        Args:
            items: List of checklist item strings
        """
        # Clear existing items
        for widget in self.checklist_frame.winfo_children():
            widget.destroy()

        self.checklist_items = items

        # Add new items
        for i, item in enumerate(items):
            self._add_checklist_item(item)

    def _add_checklist_item(self, item: str):
        """Add single checklist item"""
        item_frame = tk.Frame(self.checklist_frame, bg="#2d2d2d")
        item_frame.pack(fill=tk.X, padx=5, pady=3)

        # Checkbox
        var = tk.BooleanVar()
        cb = tk.Checkbutton(
            item_frame,
            variable=var,
            bg="#2d2d2d",
            fg=self.accent_color,
            selectcolor="#2d2d2d",
        )
        cb.pack(side=tk.LEFT, padx=5)

        # Label
        label = tk.Label(
            item_frame,
            text=f"✓ {item}",
            font=("Arial", 9),
            fg=self.accent_color,
            bg="#2d2d2d",
        )
        label.pack(side=tk.LEFT, padx=5)

        # Edit button
        edit_btn = tk.Button(
            item_frame,
            text="✏️",
            font=("Arial", 8),
            bg="#444444",
            fg="white",
            command=lambda: self._on_edit_item(i, item),
            padx=3,
            pady=0,
        )
        edit_btn.pack(side=tk.RIGHT, padx=2)

        # Delete button
        del_btn = tk.Button(
            item_frame,
            text="✕",
            font=("Arial", 8),
            bg=self.error_color,
            fg="white",
            command=lambda: self._on_delete_item(i),
            padx=3,
            pady=0,
        )
        del_btn.pack(side=tk.RIGHT, padx=2)

    def update_progress(self, current_step: int, total_steps: int, message: str = ""):
        """Update execution progress display"""
        self.current_step = current_step
        self.total_steps = total_steps

        if total_steps > 0:
            progress_pct = (current_step / total_steps) * 100
            self.progress_var.set(progress_pct)

        self.progress_text.config(text=f"{current_step}/{total_steps} steps completed")
        if message:
            self.status_label.config(text=message)

    def add_step(self, step_name: str, status: str = "pending"):
        """
        Add step to progress display

        Args:
            step_name: Name of the step
            status: "pending", "running", "success", "failed"
        """
        step_frame = tk.Frame(self.steps_frame, bg="#2d2d2d")
        step_frame.pack(fill=tk.X, padx=5, pady=2)

        # Status icon
        icon_map = {
            "pending": "⏳",
            "running": "⚙️",
            "success": "✅",
            "failed": "❌",
        }
        icon = icon_map.get(status, "⏳")

        color_map = {
            "pending": self.fg_color,
            "running": self.warning_color,
            "success": self.success_color,
            "failed": self.error_color,
        }
        color = color_map.get(status, self.fg_color)

        tk.Label(
            step_frame,
            text=f"{icon} {step_name}",
            font=("Arial", 9),
            fg=color,
            bg="#2d2d2d",
        ).pack(anchor="w")

    def log_console(self, message: str, level: str = "info"):
        """
        Add message to console output

        Args:
            message: Message to log
            level: "info", "success", "warning", "error"
        """
        tag = level if level in ["error", "success", "warning", "info"] else "info"
        self.console.insert(tk.END, f"{message}\n", tag)
        self.console.see(tk.END)
        self.root.update()

    def show_checklist_edit_dialog(self):
        """Show dialog to edit checklist items"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Checklist")
        dialog.geometry("500x400")
        dialog.configure(bg=self.bg_color)

        tk.Label(
            dialog,
            text="Edit Checklist Items (one per line):",
            font=("Arial", 10, "bold"),
            fg=self.accent_color,
            bg=self.bg_color,
        ).pack(padx=10, pady=10)

        text_area = tk.Text(dialog, height=15, width=60, bg="#2d2d2d", fg=self.fg_color)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Populate current items
        current_text = "\n".join(self.checklist_items)
        text_area.insert(tk.END, current_text)

        def on_save():
            items = [line.strip() for line in text_area.get("1.0", tk.END).split("\n") if line.strip()]
            self.set_checklist(items)
            dialog.destroy()

        tk.Button(
            dialog,
            text="✓ Save",
            command=on_save,
            bg=self.accent_color,
            fg="white",
        ).pack(pady=10)

    def show_success(self, message: str):
        """Show success message"""
        self.status_label.config(text=f"✓ {message}", fg=self.success_color)
        self.log_console(f"✓ SUCCESS: {message}", "success")

    def show_error(self, message: str):
        """Show error message"""
        self.status_label.config(text=f"✗ {message}", fg=self.error_color)
        self.log_console(f"✗ ERROR: {message}", "error")

    def show_warning(self, message: str):
        """Show warning message"""
        self.status_label.config(text=f"⚠️ {message}", fg=self.warning_color)
        self.log_console(f"⚠️ WARNING: {message}", "warning")

    # ─────────────────────────────────────────────────────────────────────────
    # Button Callbacks
    # ─────────────────────────────────────────────────────────────────────────

    def _on_start_clicked(self):
        """Handle start execution button click"""
        logger.info("Start execution clicked")
        if hasattr(self, "on_start_callback"):
            self.on_start_callback()

    def _on_edit_clicked(self):
        """Handle edit checklist button click"""
        logger.info("Edit checklist clicked")
        self.show_checklist_edit_dialog()

    def _on_cancel_clicked(self):
        """Handle cancel button click"""
        if messagebox.askyesno("Confirm", "Cancel project setup?"):
            logger.info("Project setup cancelled")
            self.root.quit()

    def _on_edit_item(self, index: int, item: str):
        """Handle edit checklist item"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item")
        dialog.geometry("400x150")
        dialog.configure(bg=self.bg_color)

        tk.Label(
            dialog,
            text="Edit item:",
            font=("Arial", 10),
            fg=self.accent_color,
            bg=self.bg_color,
        ).pack(padx=10, pady=10)

        entry = tk.Entry(
            dialog,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg=self.fg_color,
            insertbackground=self.fg_color,
        )
        entry.pack(padx=10, pady=5, fill=tk.X)
        entry.insert(tk.END, item)

        def on_save_item():
            self.checklist_items[index] = entry.get()
            self.set_checklist(self.checklist_items)
            dialog.destroy()

        tk.Button(
            dialog,
            text="✓ Save",
            command=on_save_item,
            bg=self.accent_color,
            fg="white",
        ).pack(pady=10)

    def _on_delete_item(self, index: int):
        """Handle delete checklist item"""
        self.checklist_items.pop(index)
        self.set_checklist(self.checklist_items)

    # ─────────────────────────────────────────────────────────────────────────
    # UI Control
    # ─────────────────────────────────────────────────────────────────────────

    def show(self):
        """Display the GUI window"""
        try:
            self.root.deiconify()
            self.root.update()
            self.log_console("Frontend GUI ready", "info")
        except Exception as e:
            logger.error(f"Error showing GUI: {e}")

    def hide(self):
        """Hide the GUI window"""
        try:
            self.root.withdraw()
        except Exception as e:
            logger.error(f"Error hiding GUI: {e}")

    def run(self):
        """Start the GUI event loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in GUI mainloop: {e}")

    def close(self):
        """Close the GUI"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

    def update_ui(self, update_dict: dict) -> None:
        """
        Main update method - receives updates from pipeline
        Compatible with UIHandler callback interface

        Args:
            update_dict: {
                "type": "step_start" | "step_complete" | "plan" | "status" | "success" | "error" | "project_info",
                "step": current step (int),
                "total": total steps (int),
                "message": message text (str),
                "status": "success" | "failed" (str)
                "project_name": project name (for project_info)
                "framework": framework (for project_info)
                "location": location (for project_info)
            }
        """
        try:
            update_type = update_dict.get("type")
            step = update_dict.get("step")
            total = update_dict.get("total")
            message = update_dict.get("message", "")
            status = update_dict.get("status", "")

            # NEW: Handle project info update
            if update_type == "project_info":
                proj_name = update_dict.get("project_name", "my-app")
                framework = update_dict.get("framework", "Node.js")
                location = update_dict.get("location", "")
                
                self.set_project_info(proj_name, framework, location)
                self.log_console(f"📋 Project: {proj_name} ({framework})", "info")
                return

            if update_type == "step_start":
                self.add_step(message, "running")
                self.log_console(f"▶ Starting: {message}", "info")

            elif update_type == "step_complete":
                final_status = "success" if status == "success" else "failed"
                self.add_step(message, final_status)
                if status == "success":
                    self.log_console(f"✓ Completed: {message}", "success")
                else:
                    self.log_console(f"✗ Failed: {message}", "error")
                self.update_progress(step, total, message)

            elif update_type == "plan":
                # Parse plan string into checklist items
                if isinstance(message, str):
                    items = [line.strip() for line in message.split("\n") if line.strip()]
                else:
                    items = message
                self.set_checklist(items)
                self.log_console("📋 Execution plan generated", "info")

            elif update_type == "status":
                self.log_console(f"[STATUS] {message}", "info")

            elif update_type == "success":
                self.show_success(message)

            elif update_type == "error":
                self.show_error(message)

        except Exception as e:
            logger.error(f"GUI update error: {e}")
            self.log_console(f"Update error: {e}", "error")


# ─────────────────────────────────────────────────────────────────────────────
# Standalone Demo/Test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\hack\VOICE-ASSISTANT")

    root = tk.Tk()
    gui = FrontendGUI(root)

    # Demo data
    gui.set_project_info("my-portfolio", "React + Vite", "C:\\Users\\Desktop\\Hackathon")

    checklist = [
        "Check Node.js installation",
        "Create React project with Vite",
        "Install dependencies",
        "Start development server",
        "Open project in browser",
    ]
    gui.set_checklist(checklist)

    # Demo updates
    def demo():
        time.sleep(1)
        gui.log_console("🎯 Starting execution...", "info")
        gui.update_progress(1, 5, "Step 1 started")
        gui.add_step("Check Node.js installation", "running")

        time.sleep(2)
        gui.add_step("Check Node.js installation", "success")
        gui.log_console("✓ Node.js v22.12.0 found", "success")

        time.sleep(1)
        gui.update_progress(2, 5, "Step 2 started")
        gui.add_step("Create React project", "running")
        gui.log_console("📦 Running: npm create vite@latest my -- --template react", "info")

        time.sleep(3)
        gui.add_step("Create React project", "success")
        gui.log_console("✓ React project created successfully", "success")

        time.sleep(1)
        gui.show_success("All steps completed! Project ready at C:\\...\\my")

    Thread(target=demo, daemon=True).start()

    gui.show()
    gui.run()
