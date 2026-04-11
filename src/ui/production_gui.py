"""
Production-Ready Frontend GUI - Modern Chat & Project Setup Interface
=====================================================================
Professional dual-mode interface:
  - MODE 1: Chat Bot Interface (normal commands)
  - MODE 2: Project Setup Mode (developer tasks)
  
Features:
  - Smooth transitions between modes
  - Modern design with professional styling
  - Real-time message display
  - Rich project setup visualization
  - Production-quality UX
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import time
from datetime import datetime
from pathlib import Path
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class ProductionGUI:
    """Production-Ready Frontend with Chat & Project Setup Modes"""

    # Mode constants
    MODE_CHAT = "chat"
    MODE_PROJECT = "project"

    def __init__(self, root=None):
        """Initialize production GUI"""
        self.root = root or tk.Tk()
        self.root.title("🤖 Developer Assistant")
        self.root.geometry("1000x650")
        self.root.configure(bg="#0f0f0f")
        
        # Modern window styling
        self.root.attributes("-topmost", True)
        self.root.withdraw()  # Start hidden

        # State
        self.mode = self.MODE_CHAT
        self.current_step = 0
        self.total_steps = 0
        self.checklist_items = []
        self.project_info = {}
        self.chat_history = []

        # Modern color palette (dark theme, professional)
        self.colors = {
            "bg": "#0f0f0f",
            "bg_secondary": "#1a1a1a",
            "bg_tertiary": "#252525",
            "fg": "#ffffff",
            "fg_secondary": "#b0b0b0",
            "accent": "#00d4ff",      # Cyan
            "accent_alt": "#4CAF50",   # Green
            "success": "#4CAF50",
            "warning": "#ff9800",
            "error": "#ff4444",
            "user_msg": "#2d5a7b",     # Dark blue for user
            "assistant_msg": "#1a3a2a", # Dark green for assistant
        }

        # Build UI
        self._setup_styles()
        self._build_ui()
        logger.info("ProductionGUI initialized")

    def _setup_styles(self):
        """Setup modern TTK styles"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure colors
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TButton", background=self.colors["bg_secondary"], foreground=self.colors["fg"])
        style.map("TButton", background=[("active", self.colors["accent"])])

    def _build_ui(self):
        """Build main UI layout"""
        # Header with gradient effect
        self._build_header()
        
        # Main container (will switch between modes)
        self.main_container = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Initialize both modes but show chat first
        self._build_chat_mode()
        self._build_project_mode()
        
        # Show chat mode initially
        self.show_chat_mode()

    def _build_header(self):
        """Build professional header"""
        header = tk.Frame(self.root, bg=self.colors["accent"], height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # Logo section
        logo_frame = tk.Frame(header, bg=self.colors["accent"])
        logo_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        title = tk.Label(
            logo_frame,
            text="🤖 Developer Assistant",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg=self.colors["accent"]
        )
        title.pack()

        # Status indicator
        self.status_label = tk.Label(
            header,
            text="Ready",
            font=("Segoe UI", 10),
            fg="white",
            bg=self.colors["accent"]
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=10)

    def _build_chat_mode(self):
        """Build chat bot interface"""
        self.chat_frame = tk.Frame(self.main_container, bg=self.colors["bg"])
        
        # Chat history display
        history_frame = tk.Frame(self.chat_frame, bg=self.colors["bg"])
        history_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Title
        title = tk.Label(
            history_frame,
            text="💬 Chat",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["bg"]
        )
        title.pack(anchor="w", pady=(0, 10))

        # Messages container
        self.chat_display = scrolledtext.ScrolledText(
            history_frame,
            height=15,
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Configure tags for message styling
        self.chat_display.tag_configure("user", foreground=self.colors["accent"], font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground=self.colors["accent_alt"], font=("Segoe UI", 10))
        self.chat_display.tag_configure("timestamp", foreground=self.colors["fg_secondary"], font=("Segoe UI", 8))
        self.chat_display.tag_configure("info", foreground=self.colors["fg_secondary"], font=("Segoe UI", 9, "italic"))
        self.chat_display.config(state=tk.DISABLED)

        # Input area
        input_frame = tk.Frame(history_frame, bg=self.colors["bg"])
        input_frame.pack(fill=tk.X, pady=(0, 10))

        status = tk.Label(
            input_frame,
            text="🎤 Listening for commands... (Say 'hey assistant' to activate)",
            font=("Segoe UI", 9),
            fg=self.colors["fg_secondary"],
            bg=self.colors["bg"]
        )
        status.pack(anchor="w", pady=(0, 8))

        # Quick info
        info_frame = tk.Frame(history_frame, bg=self.colors["bg_secondary"], relief=tk.FLAT, bd=1)
        info_frame.pack(fill=tk.X, pady=(10, 0))

        info_text = tk.Label(
            info_frame,
            text="Try: 'build react project my-app' or 'search google python'",
            font=("Segoe UI", 9),
            fg=self.colors["fg_secondary"],
            bg=self.colors["bg_secondary"]
        )
        info_text.pack(padx=12, pady=8)

    def _build_project_mode(self):
        """Build project setup interface"""
        self.project_frame = tk.Frame(self.main_container, bg=self.colors["bg"])

        # Two-column layout
        left_panel = tk.Frame(self.project_frame, bg=self.colors["bg"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        right_panel = tk.Frame(self.project_frame, bg=self.colors["bg"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # LEFT PANEL: Project Info & Checklist
        self._build_project_info_panel(left_panel)
        self._build_checklist_panel(left_panel)

        # RIGHT PANEL: Progress & Output
        self._build_progress_panel(right_panel)
        self._build_console_panel(right_panel)

        # FOOTER: Action buttons
        self._build_project_footer()

    def _build_project_info_panel(self, parent):
        """Build project information section"""
        section = tk.LabelFrame(
            parent,
            text="📋 Project Information",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            relief=tk.FLAT,
            bd=2
        )
        section.pack(fill=tk.X, pady=(0, 12))

        # Content frame
        content = tk.Frame(section, bg=self.colors["bg_secondary"], relief=tk.FLAT)
        content.pack(fill=tk.X, padx=10, pady=10)

        # Project name
        tk.Label(content, text="Project:", font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["bg_secondary"]).pack(anchor="w", padx=10, pady=(8, 2))
        self.label_project_name = tk.Label(content, text="my-app", font=("Segoe UI", 10), fg=self.colors["fg"], bg=self.colors["bg_secondary"])
        self.label_project_name.pack(anchor="w", padx=20, pady=(0, 8))

        # Framework
        tk.Label(content, text="Framework:", font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["bg_secondary"]).pack(anchor="w", padx=10, pady=(2, 2))
        self.label_framework = tk.Label(content, text="React + Vite", font=("Segoe UI", 10), fg=self.colors["fg"], bg=self.colors["bg_secondary"])
        self.label_framework.pack(anchor="w", padx=20, pady=(0, 8))

        # Location
        tk.Label(content, text="Location:", font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["bg_secondary"]).pack(anchor="w", padx=10, pady=(2, 2))
        self.label_location = tk.Label(content, text="C:\\Users\\Desktop\\Hackathon", font=("Segoe UI", 9), fg=self.colors["fg_secondary"], bg=self.colors["bg_secondary"], wraplength=250, justify=tk.LEFT)
        self.label_location.pack(anchor="w", padx=20, pady=(0, 8))

    def _build_checklist_panel(self, parent):
        """Build checklist section"""
        section = tk.LabelFrame(
            parent,
            text="✅ Setup Checklist",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            relief=tk.FLAT,
            bd=2
        )
        section.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        # Scrollable checklist
        canvas = tk.Canvas(section, bg=self.colors["bg_secondary"], highlightthickness=0, relief=tk.FLAT)
        scrollbar = ttk.Scrollbar(section, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_secondary"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.checklist_frame = scrollable_frame

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

    def _build_progress_panel(self, parent):
        """Build progress display section"""
        section = tk.LabelFrame(
            parent,
            text="⚙️ Execution Progress",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            relief=tk.FLAT,
            bd=2
        )
        section.pack(fill=tk.X, pady=(0, 12))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            section,
            variable=self.progress_var,
            maximum=100,
            length=300,
            mode="determinate"
        )
        progress_bar.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Progress text
        self.progress_text = tk.Label(
            section,
            text="0/0 steps completed",
            font=("Segoe UI", 9),
            fg=self.colors["accent"],
            bg=self.colors["bg"]
        )
        self.progress_text.pack(anchor="w", padx=10, pady=(0, 10))

        # Steps list
        tk.Label(section, text="Steps:", font=("Segoe UI", 10, "bold"), fg=self.colors["accent"], bg=self.colors["bg"]).pack(anchor="w", padx=10, pady=(5, 5))

        canvas = tk.Canvas(section, bg=self.colors["bg_secondary"], highlightthickness=0, relief=tk.FLAT, height=150)
        scrollbar = ttk.Scrollbar(section, orient="vertical", command=canvas.yview)
        steps_frame = tk.Frame(canvas, bg=self.colors["bg_secondary"])

        steps_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=steps_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.steps_frame = steps_frame

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(0, 10))

    def _build_console_panel(self, parent):
        """Build live console output section"""
        section = tk.LabelFrame(
            parent,
            text="💻 Live Output",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            relief=tk.FLAT,
            bd=2
        )
        section.pack(fill=tk.BOTH, expand=True)

        self.console = scrolledtext.ScrolledText(
            section,
            height=10,
            bg="#000000",
            fg="#00dd00",
            font=("Consolas", 9),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure tags
        self.console.tag_configure("error", foreground="#ff4444")
        self.console.tag_configure("success", foreground="#00dd00")
        self.console.tag_configure("warning", foreground="#ffaa00")
        self.console.tag_configure("info", foreground="#00ccff")

    def _build_project_footer(self):
        """Build project mode footer with controls"""
        footer = tk.Frame(self.root, bg=self.colors["bg_secondary"], height=60)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        # Status
        self.footer_status = tk.Label(
            footer,
            text="Ready to start project setup",
            font=("Segoe UI", 10),
            fg=self.colors["accent"],
            bg=self.colors["bg_secondary"]
        )
        self.footer_status.pack(side=tk.LEFT, padx=20, pady=15)

        # Buttons
        btn_frame = tk.Frame(footer, bg=self.colors["bg_secondary"])
        btn_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        tk.Button(
            btn_frame,
            text="▶ Start",
            command=lambda: None,
            bg=self.colors["accent"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="✏️ Edit",
            command=lambda: None,
            bg=self.colors["warning"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="✕ Cancel",
            command=lambda: None,
            bg=self.colors["error"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

    # ─────────────────────────────────────────────────────────────────────────
    # Mode Switching
    # ─────────────────────────────────────────────────────────────────────────

    def show_chat_mode(self):
        """Switch to chat mode"""
        self.mode = self.MODE_CHAT
        self.project_frame.pack_forget() if hasattr(self, 'project_frame') else None
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.status_label.config(text="💬 Chat Mode")

    def show_project_mode(self):
        """Switch to project setup mode"""
        self.mode = self.MODE_PROJECT
        self.chat_frame.pack_forget() if hasattr(self, 'chat_frame') else None
        self.project_frame.pack(fill=tk.BOTH, expand=True)
        self.status_label.config(text="🚀 Project Setup")

    # ─────────────────────────────────────────────────────────────────────────
    # Chat Mode Methods
    # ─────────────────────────────────────────────────────────────────────────

    def add_chat_message(self, text: str, sender: str = "assistant", timestamp: bool = True):
        """
        Add message to chat display

        Args:
            text: Message text
            sender: "user" or "assistant"
            timestamp: Show timestamp
        """
        self.chat_display.config(state=tk.NORMAL)
        
        if timestamp:
            ts = datetime.now().strftime("%H:%M:%S")
            self.chat_display.insert(tk.END, f"[{ts}] ", "timestamp")
        
        tag = "user" if sender == "user" else "assistant"
        prefix = "👤 You: " if sender == "user" else "🤖 Assistant: "
        
        self.chat_display.insert(tk.END, prefix, tag)
        self.chat_display.insert(tk.END, f"{text}\n\n", tag)
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def add_chat_info(self, text: str):
        """Add info message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"ℹ️ {text}\n", "info")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    # ─────────────────────────────────────────────────────────────────────────
    # Project Mode Methods
    # ─────────────────────────────────────────────────────────────────────────

    def set_project_info(self, project_name: str, framework: str, location: str):
        """Set project information"""
        self.label_project_name.config(text=project_name)
        self.label_framework.config(text=framework)
        self.label_location.config(text=location)

    def set_checklist(self, items: list):
        """Set checklist items"""
        for widget in self.checklist_frame.winfo_children():
            widget.destroy()

        for i, item in enumerate(items):
            item_frame = tk.Frame(self.checklist_frame, bg=self.colors["bg_secondary"])
            item_frame.pack(fill=tk.X, padx=8, pady=3)

            var = tk.BooleanVar()
            tk.Checkbutton(
                item_frame,
                variable=var,
                bg=self.colors["bg_secondary"],
                fg=self.colors["accent"],
                selectcolor=self.colors["bg_secondary"],
                activebackground=self.colors["bg_secondary"]
            ).pack(side=tk.LEFT)

            tk.Label(
                item_frame,
                text=f"✓ {item}",
                font=("Segoe UI", 9),
                fg=self.colors["fg"],
                bg=self.colors["bg_secondary"]
            ).pack(side=tk.LEFT, padx=5)

    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress display"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        self.progress_text.config(text=f"{current}/{total} steps completed")

    def add_step(self, step_name: str, status: str = "pending"):
        """Add step to progress list"""
        icons = {
            "pending": "⏳",
            "running": "⚙️",
            "success": "✅",
            "failed": "❌"
        }
        colors = {
            "pending": self.colors["fg_secondary"],
            "running": self.colors["warning"],
            "success": self.colors["success"],
            "failed": self.colors["error"]
        }
        icon = icons.get(status, "⏳")
        color = colors.get(status, self.colors["fg"])

        step_frame = tk.Frame(self.steps_frame, bg=self.colors["bg_secondary"])
        step_frame.pack(fill=tk.X, padx=8, pady=2)

        tk.Label(
            step_frame,
            text=f"{icon} {step_name}",
            font=("Segoe UI", 9),
            fg=color,
            bg=self.colors["bg_secondary"]
        ).pack(anchor="w")

    def log_console(self, message: str, level: str = "info"):
        """Add message to console output"""
        tag = level if level in ["error", "success", "warning", "info"] else "info"
        self.console.insert(tk.END, f"{message}\n", tag)
        self.console.see(tk.END)
        self.root.update()

    def show_success(self, message: str):
        """Display success message"""
        self.footer_status.config(text=f"✓ {message}", fg=self.colors["success"])
        self.log_console(f"✓ SUCCESS: {message}", "success")

    def show_error(self, message: str):
        """Display error message"""
        self.footer_status.config(text=f"✗ {message}", fg=self.colors["error"])
        self.log_console(f"✗ ERROR: {message}", "error")

    def show_warning(self, message: str):
        """Display warning message"""
        self.footer_status.config(text=f"⚠️ {message}", fg=self.colors["warning"])
        self.log_console(f"⚠️ WARNING: {message}", "warning")

    # ─────────────────────────────────────────────────────────────────────────
    # Control Methods
    # ─────────────────────────────────────────────────────────────────────────

    def show(self):
        """Display the window"""
        try:
            self.root.deiconify()
            self.root.update()
        except Exception as e:
            logger.error(f"Error showing GUI: {e}")

    def hide(self):
        """Hide the window"""
        try:
            self.root.withdraw()
        except Exception as e:
            logger.error(f"Error hiding GUI: {e}")

    def close(self):
        """Close the GUI"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

    def update_ui(self, update_dict: dict) -> None:
        """Main callback for pipeline updates"""
        try:
            update_type = update_dict.get("type")
            message = update_dict.get("message", "")

            # Mode switch indicators
            if update_type == "mode_switch":
                mode = update_dict.get("mode")
                if mode == "project":
                    self.show_project_mode()
                elif mode == "chat":
                    self.show_chat_mode()
                return

            # Chat mode updates
            if self.mode == self.MODE_CHAT:
                if update_type == "user_input":
                    self.add_chat_message(message, "user")
                elif update_type == "assistant_response":
                    self.add_chat_message(message, "assistant")
                elif update_type == "status":
                    self.add_chat_info(message)

            # Project mode updates
            elif self.mode == self.MODE_PROJECT:
                if update_type == "project_info":
                    self.set_project_info(
                        update_dict.get("project_name", ""),
                        update_dict.get("framework", ""),
                        update_dict.get("location", "")
                    )
                elif update_type == "plan":
                    items = message.split("\n") if isinstance(message, str) else message
                    self.set_checklist(items)
                elif update_type == "step_start":
                    self.add_step(message, "running")
                    self.log_console(f"▶ {message}", "info")
                elif update_type == "step_complete":
                    status = "success" if update_dict.get("status") == "success" else "failed"
                    self.add_step(message, status)
                    level = "success" if status == "success" else "error"
                    self.log_console(f"{'✓' if status == 'success' else '✗'} {message}", level)
                    step = update_dict.get("step", 0)
                    total = update_dict.get("total", 0)
                    self.update_progress(step, total, message)
                elif update_type == "success":
                    self.show_success(message)
                elif update_type == "error":
                    self.show_error(message)

        except Exception as e:
            logger.error(f"GUI update error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Demo/Testing
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    root = tk.Tk()
    gui = ProductionGUI(root)
    gui.show()

    # Demo chat
    def demo():
        time.sleep(1)
        gui.add_chat_message("build react project", "user")
        gui.add_chat_info("Detected: Developer task - switching to project setup...")
        
        time.sleep(2)
        gui.update_ui({"type": "mode_switch", "mode": "project"})
        
        time.sleep(1)
        gui.set_project_info("my-portfolio", "React + Vite", "C:\\Users\\Desktop\\Hackathon")
        gui.set_checklist(["Check Node.js", "Create app", "Install deps", "Start server", "Open browser"])
        
        time.sleep(2)
        gui.add_step("Check Node.js", "running")
        gui.log_console("Checking Node.js installation...", "info")
        
        time.sleep(1)
        gui.add_step("Check Node.js", "success")
        gui.log_console("✓ Node.js v22.12.0 found", "success")
        gui.update_progress(1, 5)
        
        time.sleep(1)
        gui.show_success("Project creation complete!")

    from threading import Thread
    Thread(target=demo, daemon=True).start()

    gui.root.mainloop()
